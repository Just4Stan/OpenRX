#!/usr/bin/env python3
"""
One-shot fixes for OpenRX-Gemini schematic (ELRS review prep):

1. Filter symbols:
     lib_id     DEA102700LT-6307A2 → 2450FM07D0034T
     footprint  FILTER-SMD_4P-L1.0-W0.5-L_DEA102700LT-XXX → FILTER-SMD_4P-L1.0-W0.5-L
2. Rename filter references:
     USB2 (Radio A, x≈390) → FL1
     USB1 (Radio B, x≈136) → FL2
3. Add/update LCSC Part + MPN + Manufacturer + Description on the filters.

Uses kicad-skip. Run from anywhere.
"""
from __future__ import annotations

import os
import sys

import skip

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GEMINI_SCH = os.path.join(BASE, "OpenRX-Gemini", "esp32c3_lr1121_gemini.kicad_sch")

OLD_LIB_ID = "OpenRX-Shared:DEA102700LT-6307A2"
NEW_LIB_ID = "OpenRX-Shared:2450FM07D0034T"
OLD_FP = "OpenRX-Shared:FILTER-SMD_4P-L1.0-W0.5-L_DEA102700LT-XXX"
NEW_FP = "OpenRX-Shared:FILTER-SMD_4P-L1.0-W0.5-L"

# Rename: old ref → (new ref, approx x to confirm location)
RENAME = {
    "USB2": ("FL1", 390.0),   # Radio A, right side
    "USB1": ("FL2", 136.0),   # Radio B, left side
}


def norm(name: str) -> str:
    return name.replace(" ", "_")


def find_prop(sym, name: str):
    target = norm(name)
    for p in sym.property:
        if norm(p.name) == target:
            return p
    return None


def set_or_clone(sym, name: str, value: str):
    prop = find_prop(sym, name)
    if prop is not None:
        if prop.value != value:
            prop.value = value
            return True
        return False
    source = find_prop(sym, "Description") or find_prop(sym, "Datasheet")
    if source is None:
        return False
    new_prop = source.clone()
    new_prop.name = name
    new_prop.value = value
    return True


def main() -> int:
    if not os.path.exists(GEMINI_SCH):
        print(f"ERROR: not found: {GEMINI_SCH}", file=sys.stderr)
        return 1

    sch = skip.Schematic(GEMINI_SCH)
    touched = 0
    renamed = 0

    for sym in list(sch.symbol):
        ref = sym.property.Reference.value
        lib_id = sym.lib_id.value

        if lib_id != OLD_LIB_ID and ref not in RENAME:
            continue

        # Swap lib_id on old DEA instances
        if lib_id == OLD_LIB_ID:
            sym.lib_id.value = NEW_LIB_ID
            print(f"  {ref}: lib_id → {NEW_LIB_ID}")
            touched += 1

            # Fix footprint
            fp_prop = find_prop(sym, "Footprint")
            if fp_prop is not None and fp_prop.value == OLD_FP:
                fp_prop.value = NEW_FP
                print(f"  {ref}: footprint → {NEW_FP}")

            # Ensure metadata reflects Johanson 2450FM07D0034T
            changed = False
            changed |= set_or_clone(sym, "Value", "2450FM07D0034T")
            changed |= set_or_clone(sym, "Manufacturer", "JOHANSON")
            changed |= set_or_clone(sym, "MPN", "2450FM07D0034T")
            changed |= set_or_clone(sym, "LCSC Part", "C2651081")
            changed |= set_or_clone(sym, "LCSC Part_1", "C2651081")
            changed |= set_or_clone(
                sym,
                "Datasheet",
                "https://www.lcsc.com/datasheet/C2651081.pdf",
            )

        # Rename refs
        if ref in RENAME:
            new_ref, expected_x = RENAME[ref]
            ref_prop = sym.property.Reference
            ref_prop.value = new_ref
            print(f"  {ref} → {new_ref} (at x≈{expected_x})")
            renamed += 1

    sch.write(GEMINI_SCH)
    print(f"\nSaved. Filter symbols migrated: {touched}, refs renamed: {renamed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
