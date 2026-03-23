# OpenRX-PWM Bill of Materials

> Audit note: this BOM still assumes `SE2431L`. Keep it as a working concept only until you decide whether to preserve the current GPIO/control scheme or rework the design around `RFX2401C`.

Target BOM cost: EUR 6-8 (at production quantities of 100+)

All parts sourced from LCSC for JLCPCB assembly compatibility. Basic parts preferred to avoid extended part setup fees.

## Active Components

| Ref | Description | MPN | LCSC | Package | Qty | Unit Price (USD) | Notes |
|-----|-------------|-----|------|---------|-----|------------------|-------|
| U1 | MCU | ESP32-C3FH4 | C2858491 | QFN-32 5x5mm | 1 | $1.56 | Internal 4MB flash, WiFi+BLE |
| U2 | 2.4GHz RF transceiver | SX1281IMLTRT | C2151551 | QFN-24 4x4mm | 1 | $2.26 | LDO mode, 2.4-2.5GHz |
| U3 | 2.4GHz front-end (LNA+PA) | SE2431L-R | C2649471 | QFN-24 3x4mm | 1 | $1.89 | Skyworks, 100mW PA + LNA |
| U4 | 3.3V LDO regulator | AMS1117-3.3 | C6186 | SOT-223 | 1 | $0.12 | 1A, VIN max 15V, 1.1V dropout |

## Oscillator

| Ref | Description | MPN | LCSC | Package | Qty | Unit Price (USD) | Notes |
|-----|-------------|-----|------|---------|-----|------------------|-------|
| Y1 | 52MHz TCXO | OW7EL89CENUNFAYLC-52M | C22434896 | SMD2016-4P (2.0x1.6mm) | 1 | $0.42 | YXC, 3.3V, +/-0.5ppm, sine wave |

## RF / Filter

| Ref | Description | MPN | LCSC | Package | Qty | Unit Price (USD) | Notes |
|-----|-------------|-----|------|---------|-----|------------------|-------|
| FL1 | 2.4GHz SAW bandpass filter | NDFH024-2442SA | C312144 | SMD 0.9x1.1mm | 1 | ~$0.10 | HUAYING, 2.4-2.5GHz passband |

## Connectors

| Ref | Description | MPN | LCSC | Package | Qty | Unit Price (USD) | Notes |
|-----|-------------|-----|------|---------|-----|------------------|-------|
| J1 | UFL/IPEX antenna connector | U.FL-R-SMT-1(80) | C88374 | SMD | 1 | $0.08 | Hirose, 50 ohm, MHF1 compatible |
| J2-J7 | 3-pin servo header (2.54mm) | - | - | 1x3 2.54mm | 6 | ~$0.03 ea | Signal, +V, GND. Standard pin header |

Note: Servo headers are typically hand-soldered or use through-hole 1x3 pin headers. Not placed by JLCPCB SMT assembly. Use standard 2.54mm male pin headers from LCSC (e.g., C2337, 1x40 pin header, cut to length).

## Capacitors

All 0402 unless otherwise noted. X5R or X7R dielectric. LCSC basic parts.

| Ref | Value | Voltage | Package | Qty | LCSC | Notes |
|-----|-------|---------|---------|-----|------|-------|
| C1 | 22uF | 16V | 0805 | 1 | C159842 | VIN input decoupling |
| C2 | 100nF | 16V | 0402 | 1 | C307331 | VIN input HF decoupling |
| C3 | 22uF | 10V | 0805 | 1 | C159842 | 3.3V output decoupling |
| C4 | 100nF | 16V | 0402 | 1 | C307331 | 3.3V output HF decoupling |
| C5 | 100nF | 16V | 0402 | 1 | C307331 | SX1281 VDD (pin 1) |
| C6 | 100nF | 16V | 0402 | 1 | C307331 | SX1281 VDD_IN (pin 2) |
| C7 | 470nF | 10V | 0402 | 1 | C368813 | SX1281 VR_PA (pins 9/10) |
| C8 | 100nF | 16V | 0402 | 1 | C307331 | TCXO VCC decoupling |
| C9 | 100nF | 16V | 0402 | 1 | C307331 | SE2431L VDD (pin 1) |
| C10 | 10nF | 16V | 0402 | 1 | C15195 | SE2431L BYPASS (pin 10) |
| C11 | 100nF | 16V | 0402 | 1 | C307331 | SE2431L VDD (pin 11) |
| C12 | 100nF | 16V | 0402 | 1 | C307331 | VBat ADC anti-alias |
| C13 | 1uF | 10V | 0402 | 1 | C52923 | ESP32-C3 CHIP_EN RC delay |
| C14 | 100pF | 50V | 0402 | 1 | C1554 | RF DC block (SX1281 RFIO to SE2431L) |

**Capacitor totals:** 8x 100nF 0402, 2x 22uF 0805, 1x 470nF 0402, 1x 10nF 0402, 1x 1uF 0402, 1x 100pF 0402 = 14 capacitors

## Resistors

All 0402, 1% tolerance. LCSC basic parts.

| Ref | Value | Package | Qty | LCSC | Notes |
|-----|-------|---------|-----|------|-------|
| R1 | 10k | 0402 | 1 | C25744 | SX1281 NRESET pull-up |
| R2 | 10k | 0402 | 1 | C25744 | SX1281 NSS pull-up |
| R3 | 100k | 0402 | 1 | C25741 | VBat divider upper |
| R4 | 10k | 0402 | 1 | C25744 | VBat divider lower |
| R5 | 10k | 0402 | 1 | C25744 | ESP32-C3 CHIP_EN pull-up |
| R6 | 10k | 0402 | 1 | C25744 | GPIO9 boot pull-up |
| R7 | 1k | 0402 | 1 | C11702 | Power LED current limit |
| R8 | 10k | 0402 | 1 | C25744 | SE2431L RXEN pull-up (Option A) |
| R9-R14 | 100R | 0402 | 6 | C25076 | PWM output protection (one per channel) |

**Resistor totals:** 6x 10k, 1x 100k, 1x 1k, 6x 100R = 14 resistors (Option A with 5 PWM: 5x 100R = 13 resistors)

## Inductors / Matching

| Ref | Value | Package | Qty | LCSC | Notes |
|-----|-------|---------|-----|------|-------|
| L1 | 1.2nH | 0402 | 1 | C76857 | RF matching (SX1281 to SE2431L). Value TBD, tune on VNA |

## LED

| Ref | Description | Package | Qty | LCSC | Notes |
|-----|-------------|---------|-----|------|-------|
| D1 | Green LED | 0402 | 1 | C2286 | Power indicator, always on |

## Optional / DNP

| Ref | Description | MPN | LCSC | Package | Qty | Notes |
|-----|-------------|-----|------|---------|-----|-------|
| R_OPT1 | 0R jumper | - | C25077 | 0402 | 1 | GPIO10 to TXEN (Option A, default populate) |
| R_OPT2 | 0R jumper | - | C25077 | 0402 | 1 | GPIO10 to PWM CH4 (Option B, DNP default) |
| R_OPT3 | 0R jumper | - | C25077 | 0402 | 1 | DIO2 to TXEN (Option B, DNP default) |
| D2-D7 | TVS diode | PESD5V0S1BSF | - | SOD-323F | 6 | ESD protection on PWM outputs. DNP unless long servo leads |

## BOM Cost Estimate (Production Qty 100+)

| Category | Cost (USD) |
|----------|------------|
| ESP32-C3FH4 | $1.56 |
| SX1281IMLTRT | $2.26 |
| SE2431L-R | $1.89 |
| AMS1117-3.3 | $0.12 |
| TCXO 52MHz | $0.42 |
| SAW filter | $0.10 |
| UFL connector | $0.08 |
| Capacitors (14x) | $0.15 |
| Resistors (14x) | $0.10 |
| Inductor | $0.02 |
| LED | $0.02 |
| Pin headers (6x 1x3) | $0.18 |
| **Total components** | **$6.90** |

PCB (4-layer, 30x20mm, JLCPCB): ~$0.50/board at qty 100

**Total BOM + PCB: ~$7.40 USD (~EUR 6.80)**

Within the EUR 6-8 target.

## JLCPCB Assembly Notes

- SMT assembly: All components except servo headers (J2-J7)
- Servo headers: through-hole, hand-solder or wave solder
- All active ICs have LCSC part numbers and are available for JLCPCB placement
- Capacitors and resistors are LCSC basic parts where possible (no extended part fee)
- SE2431L-R and SX1281IMLTRT are extended parts (JLCPCB charges ~$3 setup per extended part type)
- Consider consigning ESP32-C3FH4 if LCSC stock is low

## LCSC Part Number Summary (for easyeda2kicad import)

```
C2858491  - ESP32-C3FH4
C2151551  - SX1281IMLTRT
C2649471  - SE2431L-R
C6186     - AMS1117-3.3
C22434896 - YXC 52MHz TCXO
C312144   - HUAYING SAW filter 2.4GHz
C88374    - Hirose U.FL connector
C25744    - 10k 0402 resistor
C25741    - 100k 0402 resistor
C11702    - 1k 0402 resistor
C25076    - 100R 0402 resistor
C25077    - 0R 0402 jumper
C307331   - 100nF 0402 X7R 16V capacitor
C159842   - 22uF 0805 capacitor
C368813   - 470nF 0402 capacitor
C15195    - 10nF 0402 capacitor
C52923    - 1uF 0402 capacitor
C1554     - 100pF 0402 capacitor
C76857    - 1.2nH 0402 inductor
C2286     - Green LED 0402
```

## Competitive Comparison

| | OpenRX-PWM | RadioMaster ER5C | RadioMaster ER6G |
|---|---|---|---|
| Price | ~$7.40 (BOM) | $19.99 (retail) | $29.99 (retail) |
| Channels | 4-6 PWM | 5 PWM | 6 PWM |
| PA/LNA | SE2431L (yes) | No | Yes |
| MCU | ESP32-C3 | ESP32-C3 | ESP32-C3 |
| RF | SX1281 | SX1281 | SX1281 |
| Battery sensing | Yes | No | Yes |
| Size | 30x20mm | ~25x15mm | ~35x25mm |
| Open source | Yes (CERN-OHL-S) | No | No |
