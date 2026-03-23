# OpenRX-900 Bill of Materials

> Audit note: do not lock the LR1121 footprint or schematic pin mapping from this file alone. Treat `LR1121IMLTRT` as `QFN-32 4x4mm` and reconcile the full radio section against the official Semtech datasheet before drawing the real schematic.

Target BOM cost: EUR 4-5 (at JLCPCB assembly quantities)

## Active Components

| Ref | Description | MPN | LCSC | Package | Qty | Unit Price | Notes |
|-----|-------------|-----|------|---------|-----|------------|-------|
| U1  | LR1121 sub-GHz/2.4GHz transceiver | LR1121IMLTRT | C7498014 | QFN-32 4x4mm | 1 | ~$2.50 | Main RF transceiver |
| U2  | ESP32-C3FH4 MCU (4MB flash) | ESP32-C3FH4 | C2858491 | QFN-32 5x5mm | 1 | ~$1.20 | RISC-V MCU, WiFi+BLE |
| U3  | ME6211C33M5G-N 3.3V LDO | ME6211C33M5G-N | C82942 | SOT-23-5 | 1 | ~$0.04 | 500mA, 3.3V output |
| Y2  | 32MHz TCXO (peak-shaving sine) | OW2EL89CENUXFMYLC-32M | C22434888 | SMD3225-4P | 1 | ~$0.46 | For LR1121 clock |
| Y1  | 40MHz crystal (10pF load) | 7M40000005 | C90924 | SMD3225-4P | 1 | ~$0.08 | For ESP32-C3 clock |
| D1  | WS2812B-2020 RGB LED | WS2812B-2020 | C965555 | 2020 | 1 | ~$0.04 | Addressable LED |
| J1  | U.FL antenna connector | U.FL-R-SMT-1(80) | C88374 | SMD | 1 | ~$0.08 | 50 ohm, HRS/Hirose |

**Active subtotal: ~$4.40**

## Passive Components — Capacitors

| Ref | Value | Package | Qty | LCSC | Notes |
|-----|-------|---------|-----|------|-------|
| C1  | 10uF 10V X5R | 0402 | 1 | C15525 | LDO input |
| C2  | 100nF 16V X7R | 0402 | 1 | C1525 | LDO input bypass |
| C3  | 22uF 10V X5R | 0603 | 1 | C59461 | LDO output |
| C4  | 100nF 16V X7R | 0402 | 1 | C1525 | LDO output bypass |
| C5  | 10pF 50V C0G | 0402 | 1 | C32949 | XTAL_P load cap |
| C6  | 10pF 50V C0G | 0402 | 1 | C32949 | XTAL_N load cap |
| C7  | 1uF 16V X5R | 0402 | 1 | C52923 | ESP32 EN delay |
| C8  | 100nF 16V X7R | 0402 | 1 | C1525 | LR1121 VTCXO bypass |
| C9  | 100nF 16V X7R | 0402 | 1 | C1525 | LR1121 VBAT_RF bypass |
| C10 | 100nF 16V X7R | 0402 | 1 | C1525 | LR1121 VBAT bypass |
| C11 | 4.7uF 10V X5R | 0402 | 1 | C23733 | LR1121 VR_PA |
| C12 | 100nF 16V X7R | 0402 | 1 | C1525 | LR1121 VR_PA bypass |
| C13 | 10uF 10V X5R | 0402 | 1 | C15525 | LR1121 VREG |
| C14 | 100nF 16V X7R | 0402 | 1 | C1525 | LR1121 VREG bypass |
| C15 | 100nF 16V X7R | 0402 | 1 | C1525 | ESP32 VDD3P3 bypass |
| C16 | 100nF 16V X7R | 0402 | 1 | C1525 | ESP32 VDD3P3_RTC bypass |
| C17 | 1uF 16V X5R | 0402 | 1 | C52923 | ESP32 VDDA |
| C18 | 100nF 16V X7R | 0402 | 1 | C1525 | ESP32 VDDA bypass |
| C19 | 100nF 16V X7R | 0402 | 1 | C1525 | WS2812B bypass |

**Capacitor summary: 19 caps total**
- 100nF 0402 x11 (C1525 — LCSC basic part)
- 10uF 0402 x2 (C15525 — LCSC basic part)
- 22uF 0603 x1 (C59461 — LCSC basic part)
- 1uF 0402 x2 (C52923 — LCSC basic part)
- 4.7uF 0402 x1 (C23733 — LCSC basic part)
- 10pF 0402 x2 (C32949 — LCSC basic part)

## Passive Components — Resistors

| Ref | Value | Package | Qty | LCSC | Notes |
|-----|-------|---------|-----|------|-------|
| R1  | 10k 1% | 0402 | 1 | C25744 | ESP32 EN pull-up |
| R2  | 10k 1% | 0402 | 1 | C25744 | ESP32 GPIO9 boot pull-up |
| R3  | 10k 1% | 0402 | 1 | C25744 | LR1121 NRESET pull-up |
| R4  | 10k 1% | 0402 | 1 | C25744 | LR1121 NSS pull-up |
| R5  | 100k 1% | 0402 | 1 | C25741 | LR1121 RFSW0 pull-down |
| R6  | 100k 1% | 0402 | 1 | C25741 | LR1121 RFSW1 pull-down |
| R7  | 100k 1% | 0402 | 1 | C25741 | LR1121 RFSW2 pull-down |
| R8  | 100k 1% | 0402 | 1 | C25741 | LR1121 RFSW3 pull-down |

**Resistor summary: 8 resistors total**
- 10k 0402 x4 (C25744 — LCSC basic part)
- 100k 0402 x4 (C25741 — LCSC basic part)

## Passive Components — Inductors

| Ref | Value | Package | Qty | LCSC | Notes |
|-----|-------|---------|-----|------|-------|
| L1  | 10uH 300mA | 0603 | 1 | C1035 | LR1121 DC-DC inductor. Low DCR preferred. |

**Inductor summary: 1 inductor**
- 10uH 0603 x1 (C1035 — LCSC basic part)

## RF Matching Network Components

These values are for the discrete sub-GHz matching network. Exact values require VNA tuning on the final PCB.

| Ref | Value | Package | Qty | LCSC | Notes |
|-----|-------|---------|-----|------|-------|
| C20 | 100pF C0G | 0402 | 1 | C1553 | DC block, antenna side |
| C21 | 100pF C0G | 0402 | 1 | C1553 | DC block, HP PA |
| C22 | 100pF C0G | 0402 | 1 | C1553 | DC block, LP PA |
| C23 | 1.5pF C0G | 0402 | 1 | C1546 | Balun cap |
| C24 | 3.3pF C0G | 0402 | 1 | C1548 | Impedance match cap |
| L2  | 15nH | 0402 | 1 | TBD | RFI_P match |
| L3  | 15nH | 0402 | 1 | TBD | RFI_N match |
| L4  | 6.8nH | 0402 | 1 | TBD | Series match |

Note: RF inductor LCSC part numbers need to be selected based on Q-factor and SRF at 868/915MHz. Search LCSC for "15nH 0402" and "6.8nH 0402" RF inductors. Murata LQW15AN or similar recommended.

## Mechanical

| Item | Description | Notes |
|------|-------------|-------|
| PCB  | 18x13mm, 2-layer, 1.0mm, ENIG | JLCPCB standard 2-layer |
| Boot button | 3x4mm SMD tactile switch | Optional, for entering boot/bind mode |

## BOM Cost Estimate

| Category | Est. Cost (1pc) |
|----------|----------------|
| Active ICs (U1, U2, U3) | ~$3.74 |
| TCXO + Crystal (Y1, Y2) | ~$0.54 |
| LED (D1) | ~$0.04 |
| Connector (J1) | ~$0.08 |
| Capacitors (x19+5) | ~$0.15 |
| Resistors (x8) | ~$0.03 |
| Inductors (x1+3) | ~$0.10 |
| **Total BOM** | **~$4.68** |

At JLCPCB assembly quantities (100+), expect ~$3.50-4.00 per board.

## LCSC Part Availability Notes

- All capacitors and resistors use LCSC basic parts (no extended library fee)
- ME6211C33M5G-N (C82942) is an LCSC basic part
- ESP32-C3FH4 (C2858491) and LR1121 (C7498014) are extended parts (extra assembly fee)
- WS2812B-2020 (C965555) is an extended part
- U.FL connector (C88374) is an extended part
- 40MHz crystal (C90924) is an extended part
- 32MHz TCXO (C22434888) is an extended part

## Components Requiring LCSC Verification

Before ordering, verify these components are in stock on LCSC:

1. **LR1121IMLTRT (C7498014)** — Newer part, may have limited stock
2. **32MHz TCXO (C22434888)** — Had ~2,782 units at time of design. Alternative: TAITIEN TYETBCSANF-32.000000 (C6732076, SMD2520) when in stock
3. **RF inductors (L2-L4)** — Part numbers TBD, select from LCSC RF inductor category
4. **Tactile switch** — Select SMD 3x4mm or 2x3mm switch from LCSC

## Import List for easyeda2kicad

```bash
# Main ICs
easyeda2kicad --full --lcsc_id=C2858491 --output=libs  # ESP32-C3FH4
easyeda2kicad --full --lcsc_id=C7498014 --output=libs  # LR1121IMLTRT
easyeda2kicad --full --lcsc_id=C82942 --output=libs    # ME6211C33M5G-N

# TCXO and Crystal
easyeda2kicad --full --lcsc_id=C22434888 --output=libs # 32MHz TCXO
easyeda2kicad --full --lcsc_id=C90924 --output=libs    # 40MHz crystal

# LED and Connector
easyeda2kicad --full --lcsc_id=C965555 --output=libs   # WS2812B-2020
easyeda2kicad --full --lcsc_id=C88374 --output=libs    # U.FL connector
```
