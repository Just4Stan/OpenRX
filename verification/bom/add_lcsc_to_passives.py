#!/usr/bin/env python3
"""
Add/update LCSC Part numbers on passive components (Device:C, Device:R, Device:L)
in OpenRX KiCad schematics using kicad-skip.

These passives use generic KiCad library symbols that lack the "LCSC Part"
property needed for JLCPCB BOM matching. This script:
  1. Opens each sub-sheet schematic (where components live)
  2. Finds all Device:C, Device:R, Device:L symbols
  3. Matches by value + footprint to a verified LCSC part number
  4. Adds "LCSC Part" property (cloned from existing property)
  5. Updates the "LCSC" property if the value was wrong/missing
  6. Saves the schematic

All LCSC part numbers verified via jlcsearch API 2026-04-06.
Preference: JLCPCB basic parts where available, adequate voltage ratings,
C0G/NP0 for RF and crystal caps, X5R for bulk/bypass.

Run:  python3 add_lcsc_to_passives.py
"""
from __future__ import annotations

import os
import sys

try:
    import skip
except ImportError:
    print("ERROR: kicad-skip not installed. Run: pip3 install kicad-skip", file=sys.stderr)
    sys.exit(1)


# ── LCSC mapping: (value, footprint_suffix) → LCSC part number ──────────
# footprint_suffix is the unique part after the last ':', e.g. "C_0201_0603Metric"
LCSC_MAP: dict[tuple[str, str], str] = {
    # ── Capacitors ──
    # 100nF 0201, Murata GRM033R61E104KE14D, 25V X5R — decoupling
    ("100nF", "C_0201_0603Metric"):   "C76939",
    # 1uF 0201, Murata GRM033R61A105ME44D, 10V X5R — bypass
    ("1uF",   "C_0201_0603Metric"):   "C76935",
    # 10uF 0402, Samsung CL05A106MQ5NUNC, 6.3V X5R — BASIC — bulk
    ("10uF",  "C_0402_1005Metric"):   "C15525",
    # 18pF 0201, FH 0201CG180J500NT, 50V C0G — crystal load caps
    ("18pF",  "C_0201_0603Metric"):   "C62164",
    # 4.7uF 0402, Samsung CL05A475MP5NRNC, 10V X5R — BASIC — LDO output
    ("4.7uF", "C_0402_1005Metric"):   "C23733",
    # 220pF 0201, FH 0201B221K500NT, 50V C0G — RF matching
    ("220pF", "C_0201_0603Metric"):   "C62548",
    # 0.3pF 0201, Murata GRM0335C1HR30BA01D, 50V C0G — RF coupling
    ("0.3pF", "C_0201_0603Metric"):   "C76927",
    # 10pF 0201, Murata GRM0335C1H100JA01D, 50V C0G — RF matching
    ("10pF",  "C_0201_0603Metric"):   "C76921",
    # 470nF 0201, Murata GRM033R60J474KE90D, 6.3V X5R — SX1281 decoupling
    ("470nF", "C_0201_0603Metric"):   "C85926",
    # 1nF 0201, FH 0201B102K500NT, 50V — SX1281 decoupling
    ("1nF",   "C_0201_0603Metric"):   "C66942",

    # ── Resistors ──
    # 10k 0201, Yageo RC0201FR-0710KL, 1% — pull-ups
    ("10k",   "R_0201_0603Metric"):   "C106225",
    # 220R 0201, Yageo RC0201FR-07220RL, 1% — LED series
    ("220R",  "R_0201_0603Metric"):   "C274342",

    # ── Inductors ──
    # 24nH 0201, Murata LQP03TN24NH02D — RF matching
    ("24nH",  "L_0201_0603Metric"):   "C206441",
    # 10uH 0603, Sunlord SDFL1608S100KTF — BASIC — RF choke / DC feed
    ("10uH",  "L_0603_1608Metric"):   "C1035",
}

# Which lib_id prefixes are considered "passive / generic"
PASSIVE_LIBS = {"Device:C", "Device:R", "Device:L"}

# ── Schematic sub-sheets containing actual components ────────────────────
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHEETS: list[str] = [
    os.path.join(BASE, "OpenRX-Lite",   "esp32c3_sx1281_lite.kicad_sch"),
    os.path.join(BASE, "OpenRX-Mono",   "esp32c3_lr1121_mono.kicad_sch"),
    os.path.join(BASE, "OpenRX-Gemini", "esp32c3_lr1121_gemini.kicad_sch"),
]


def footprint_suffix(fp: str) -> str:
    """Extract 'C_0201_0603Metric' from 'Capacitor_SMD:C_0201_0603Metric'."""
    return fp.rsplit(":", 1)[-1] if ":" in fp else fp


def normalize_prop_name(name: str) -> str:
    """Normalize property name for comparison.
    kicad-skip converts spaces to underscores internally, so
    'LCSC Part' and 'LCSC_Part' should match."""
    return name.replace(" ", "_")


def has_property(sym, name: str) -> bool:
    """Check if a symbol already has a property with the given name.
    Handles kicad-skip's space→underscore normalization."""
    target = normalize_prop_name(name)
    for p in sym.property:
        if normalize_prop_name(p.name) == target:
            return True
    return False


def get_property(sym, name: str):
    """Get a property object by name, or None.
    Handles kicad-skip's space→underscore normalization."""
    target = normalize_prop_name(name)
    for p in sym.property:
        if normalize_prop_name(p.name) == target:
            return p
    return None


def process_sheet(path: str) -> dict:
    """Process a single schematic sheet, returns stats dict."""
    stats = {"file": path, "updated": 0, "added_lcsc_part": 0,
             "fixed_lcsc": 0, "skipped_no_match": [], "skipped_not_passive": 0}

    if not os.path.exists(path):
        print(f"  SKIP: file not found: {path}")
        return stats

    print(f"\n  Opening: {os.path.basename(path)}")
    sch = skip.Schematic(path)
    symbols = list(sch.symbol)
    print(f"  Found {len(symbols)} symbols total")

    for sym in symbols:
        ref = sym.property.Reference.value
        # Skip power symbols and other non-component refs
        if ref.startswith("#"):
            continue

        lib_id = sym.lib_id.value if hasattr(sym, "lib_id") else ""
        if lib_id not in PASSIVE_LIBS:
            stats["skipped_not_passive"] += 1
            continue

        value = sym.property.Value.value
        fp = sym.property.Footprint.value
        fp_key = footprint_suffix(fp)
        key = (value, fp_key)

        if key not in LCSC_MAP:
            stats["skipped_no_match"].append(f"{ref} ({value}, {fp_key})")
            continue

        target_lcsc = LCSC_MAP[key]
        changed = False

        # 1. Update or verify LCSC property
        lcsc_prop = get_property(sym, "LCSC")
        if lcsc_prop is not None:
            if lcsc_prop.value != target_lcsc:
                old = lcsc_prop.value
                lcsc_prop.value = target_lcsc
                print(f"    {ref}: LCSC {old} → {target_lcsc}")
                stats["fixed_lcsc"] += 1
                changed = True
        # If no LCSC property exists at all, we'd need to create one from scratch.
        # With kicad-skip, we can't easily create properties from nothing — skip this edge case.

        # 2. Add "LCSC Part" property if missing
        if not has_property(sym, "LCSC Part"):
            # Clone an existing property to create the new one
            # Prefer cloning LCSC since it has the right value already
            source_prop = get_property(sym, "LCSC") or get_property(sym, "Description")
            if source_prop is not None:
                new_prop = source_prop.clone()
                new_prop.name = "LCSC Part"
                new_prop.value = target_lcsc
                print(f"    {ref}: added 'LCSC Part' = {target_lcsc}")
                stats["added_lcsc_part"] += 1
                changed = True
        else:
            # LCSC Part already exists, verify/update its value
            existing = get_property(sym, "LCSC Part")
            if existing.value != target_lcsc:
                old = existing.value
                existing.value = target_lcsc
                print(f"    {ref}: LCSC Part {old} → {target_lcsc}")
                changed = True

        if changed:
            stats["updated"] += 1

    if stats["updated"] > 0 or stats["added_lcsc_part"] > 0:
        sch.write(path)
        print(f"  SAVED: {stats['updated']} components updated, "
              f"{stats['added_lcsc_part']} 'LCSC Part' added, "
              f"{stats['fixed_lcsc']} LCSC values corrected")
    else:
        print(f"  No changes needed")

    if stats["skipped_no_match"]:
        print(f"  WARNING: {len(stats['skipped_no_match'])} passives had no mapping:")
        for item in stats["skipped_no_match"]:
            print(f"    - {item}")

    return stats


def main() -> int:
    print("=" * 60)
    print("OpenRX — Add LCSC Part numbers to passive components")
    print("=" * 60)
    print(f"\nLCSC mapping has {len(LCSC_MAP)} value+footprint entries")
    print(f"Processing {len(SHEETS)} schematic sheets\n")

    all_stats = []
    for sheet in SHEETS:
        stats = process_sheet(sheet)
        all_stats.append(stats)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total_updated = sum(s["updated"] for s in all_stats)
    total_added = sum(s["added_lcsc_part"] for s in all_stats)
    total_fixed = sum(s["fixed_lcsc"] for s in all_stats)
    total_unmatched = sum(len(s["skipped_no_match"]) for s in all_stats)
    print(f"  Components updated:      {total_updated}")
    print(f"  'LCSC Part' added:       {total_added}")
    print(f"  LCSC values corrected:   {total_fixed}")
    print(f"  Passives without match:  {total_unmatched}")

    if total_unmatched > 0:
        print("\n  Unmatched passives need manual LCSC assignment.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
