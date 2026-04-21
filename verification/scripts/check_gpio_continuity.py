#!/usr/bin/env python3
"""
Verify schematic ↔ hardware.json continuity for each OpenRX board.

Source of truth: kicad-cli-exported netlist.xml next to each schematic.
Strategy:
  - Build ESP32-C3 pin-function → GPIO number table from the datasheet.
  - For the ESP32 component in the netlist, map each pinfunction to a GPIO.
  - Compare the GPIO numbers against the ELRS target JSON's declared pins.

Run after regenerating netlists:
  for d in OpenRX-Lite OpenRX-Lite-UFL OpenRX-Mono OpenRX-Gemini; do
    kicad-cli sch export netlist --format kicadxml \
        -o $d/netlist.xml $d/*core*.kicad_sch $d/esp32c3*.kicad_sch 2>/dev/null
  done
"""
from __future__ import annotations

import json
import os
import re
import sys
import xml.etree.ElementTree as ET

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ELRS = os.path.join(BASE, "shared", "elrs-targets")

# ── ESP32-C3 (QFN32) pinfunction → GPIO# ───────────────────────────────
# Taken from the ESP32-C3 datasheet Table 3-2.
ESP32C3_PIN_TO_GPIO: dict[str, int] = {
    "XTAL_32K_P":  0,
    "XTAL_32K_N":  1,
    "GPIO2":       2,
    "GPIO3":       3,
    "MTMS":        4,
    "MTDI":        5,
    "MTCK":        6,
    "MTDO":        7,
    "GPIO8":       8,
    "GPIO9":       9,
    "GPIO10":      10,
    "VDD_SPI":     11,
    "SPIHD":       12,
    "SPIWP":       13,
    "SPICS0":      14,
    "SPICLK":      15,
    "SPID":        16,
    "SPIQ":        17,
    "GPIO18":      18,
    "GPIO19":      19,
    "U0RXD":       20,
    "U0TXD":       21,
}

# Net-name in schematic → ELRS JSON field. Uses a regex so the schematics
# are free to number signals per-radio (BUSY1, BUSY2, etc.) and we still
# find them.
NET_TO_FIELD_COMMON: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^RX$"),           "serial_rx"),
    (re.compile(r"^TX$"),           "serial_tx"),
    (re.compile(r"^MOSI$"),         "radio_mosi"),
    (re.compile(r"^MISO$"),         "radio_miso"),
    (re.compile(r"^SCK$"),          "radio_sck"),
    (re.compile(r"^BUSY1?$"),       "radio_busy"),
    (re.compile(r"^IRQ1?$"),        "radio_dio1"),
    (re.compile(r"^NSS1?$"),        "radio_nss"),
    (re.compile(r"^RST1?$"),        "radio_rst"),
    (re.compile(r"^LED$"),          "led"),
    (re.compile(r"^LED$"),          "led_rgb"),  # Gemini uses RGB LED
    (re.compile(r"^BUTTON$|^BTN$"), "button"),
]

NET_TO_FIELD_RADIO_B: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^BUSY2$"), "radio_busy_2"),
    (re.compile(r"^IRQ2$"),  "radio_dio1_2"),
    (re.compile(r"^NSS2$"),  "radio_nss_2"),
    (re.compile(r"^RST2$"),  "radio_rst_2"),
]


def parse_pinfunction(pinfunc: str) -> int | None:
    """Accept either 'GPIO3' or 'GPIO3_8' (<name>_<pin>) or 'MTDI_10'."""
    if not pinfunc:
        return None
    base = pinfunc.split("_")[0]
    # Some library variants expand: 'GPIO3' pin is GPIO3 directly
    if base in ESP32C3_PIN_TO_GPIO:
        return ESP32C3_PIN_TO_GPIO[base]
    # Handle 'XTAL_32K_P_4' style where base split was too aggressive
    m = re.match(r"(XTAL_32K_[PN])", pinfunc)
    if m:
        return ESP32C3_PIN_TO_GPIO[m.group(1)]
    return None


def gather_esp32_nets(netlist_xml: str) -> tuple[str, dict[str, int]]:
    """Return (esp_ref, {net_name_stripped: gpio#}) for the ESP32 on this netlist."""
    tree = ET.parse(netlist_xml)
    root = tree.getroot()

    esp_ref = None
    for comp in root.iter("comp"):
        if "ESP32" in comp.findtext("value", ""):
            esp_ref = comp.get("ref")
            break
    if not esp_ref:
        return "", {}

    out: dict[str, int] = {}
    for net in root.iter("net"):
        raw = net.get("name", "")
        name = raw.strip("/").split("/")[-1].upper()
        for node in net.iter("node"):
            if node.get("ref") != esp_ref:
                continue
            pinfunc = node.get("pinfunction") or ""
            gpio = parse_pinfunction(pinfunc)
            if gpio is not None:
                # Only record the first assignment for a given net (they
                # should all agree since a net→ESP32 is usually 1 pin).
                out.setdefault(name, gpio)
    return esp_ref, out


def check_board(name: str, netlist: str, json_name: str, dual_radio: bool) -> int:
    print(f"\n── {name} ──")
    if not os.path.exists(netlist):
        print(f"  ERROR: netlist missing: {netlist}"); return 1
    json_path = os.path.join(ELRS, json_name)
    if not os.path.exists(json_path):
        print(f"  ERROR: json missing: {json_path}"); return 1

    esp_ref, pins = gather_esp32_nets(netlist)
    if not pins:
        print(f"  ERROR: no ESP32 pins resolved"); return 1

    with open(json_path) as f:
        conf = json.load(f)

    rules = list(NET_TO_FIELD_COMMON)
    if dual_radio:
        rules += NET_TO_FIELD_RADIO_B

    errors = 0
    seen_fields: set[str] = set()
    for net_name, gpio in sorted(pins.items()):
        matched = False
        for rx, field in rules:
            if not rx.match(net_name):
                continue
            if field not in conf:
                continue
            want = conf[field]
            seen_fields.add(field)
            if gpio == want:
                print(f"  OK    {field:16s} net={net_name:9s} GPIO{gpio}")
            else:
                print(f"  FAIL  {field:16s} net={net_name:9s} schematic=GPIO{gpio}  json={want}")
                errors += 1
            matched = True
            break
        if not matched:
            # Not tied to a JSON field — still print for visibility
            pass

    # Any configured JSON pins for which we saw no matching net?
    expected_fields = {f for _, f in rules if f in conf}
    missing = expected_fields - seen_fields
    for m in sorted(missing):
        # led_rgb and led are aliases — tolerate one missing if the other was seen
        if m == "led_rgb" and "led" in seen_fields:
            continue
        if m == "led" and "led_rgb" in seen_fields:
            continue
        print(f"  MISS  {m:16s} expected GPIO{conf[m]} — no net mapped")
        errors += 1

    print(f"  ESP32 ref: {esp_ref}, nets resolved: {len(pins)}, errors: {errors}")
    return errors


def main() -> int:
    rc = 0
    rc += check_board(
        "OpenRX-Lite",
        os.path.join(BASE, "OpenRX-Lite", "netlist.xml"),
        "OpenRX Lite 2400.json",
        dual_radio=False,
    )
    rc += check_board(
        "OpenRX-Lite-UFL",
        os.path.join(BASE, "OpenRX-Lite-UFL", "netlist.xml"),
        "OpenRX Lite 2400.json",
        dual_radio=False,
    )
    rc += check_board(
        "OpenRX-Mono",
        os.path.join(BASE, "OpenRX-Mono", "netlist.xml"),
        "OpenRX Mono LR1121.json",
        dual_radio=False,
    )
    rc += check_board(
        "OpenRX-Gemini",
        os.path.join(BASE, "OpenRX-Gemini", "netlist.xml"),
        "OpenRX Gemini LR1121.json",
        dual_radio=True,
    )
    print(f"\nTotal errors: {rc}")
    return 0 if rc == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
