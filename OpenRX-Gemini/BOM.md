# OpenRX-Gemini Bill of Materials

> Audit note: this is an `ESP32-C3 + 2x LR1121` concept BOM. The 2.4GHz front-end is still documented as `SE2431L`; do not treat the front-end choice as locked until the common BOM strategy is reconciled.

Date: 2026-03-23
Status: Design phase
Target unit BOM cost: EUR 12-15 (at qty 100)

## Active Components

| Ref | Qty | Description | MPN | LCSC | Package | Unit Price (USD) | Notes |
|-----|-----|-------------|-----|------|---------|-----------------|-------|
| U1 | 1 | MCU, ESP32-C3FH4, 4MB flash integrated | ESP32-C3FH4 | C2858491 | QFN-32 5x5mm | ~$1.80 | WiFi+BLE, RISC-V, 160MHz |
| U2 | 1 | Sub-GHz Radio, LR1121 | LR1121IMLTRT | C7498014 | QFN-32 4x4mm | ~$2.50 | Sub-GHz primary (868/915MHz) |
| U3 | 1 | 2.4GHz Radio, LR1121 | LR1121IMLTRT | C7498014 | QFN-32 4x4mm | ~$2.50 | 2.4GHz primary |
| U4 | 1 | 2.4GHz Front-End (PA+LNA+Switch) | SE2431L-R | C2649471 | QFN-24 3x4mm | ~$1.89 | Skyworks, RX gain +11dB, TX +22dBm |
| U5 | 1 | LDO 3.3V 600mA | AP2112K-3.3TRG1 | C51118 | SOT-23-5 | ~$0.07 | Diodes Inc, 250mV dropout |

## Oscillators

| Ref | Qty | Description | MPN | LCSC | Package | Unit Price (USD) | Notes |
|-----|-----|-------------|-----|------|---------|-----------------|-------|
| Y1 | 1 | 32MHz TCXO for Radio 1 | OW2EL89CENUXFMYLC-32M | C22434888 | SMD3225-4P | ~$0.46 | YXC, 3.3V, +/-2.5ppm, clipped sine. LR1121 VDD_TCXO set to 3.3V. |
| Y2 | 1 | 32MHz TCXO for Radio 2 | OW2EL89CENUXFMYLC-32M | C22434888 | SMD3225-4P | ~$0.46 | Same as Y1. One per radio. |

### TCXO Notes
- The LR1121 VDD_TCXO output is programmable from 1.6V to 3.3V. Configure firmware to output 3.3V to match TCXO supply.
- 3225 package (3.2x2.5mm) is the smallest readily available 32MHz TCXO on LCSC. 2016 (2.0x1.6mm) options exist but are out of stock or expensive.
- If a 1.8V TCXO in 2016 package becomes available on LCSC, switch to it to save board area. The 3225 footprint fits the 24x18mm board but is tight.
- Alternative: Seiko Epson TG2016SBN series (1.8V, 2016 package) available from Mouser/DigiKey but not LCSC. Consider consignment if size is critical.

## RF / Antenna Components

| Ref | Qty | Description | MPN | LCSC | Package | Unit Price (USD) | Notes |
|-----|-----|-------------|-----|------|---------|-----------------|-------|
| FL1 | 1 | 2.4GHz SAW bandpass filter | SAFFB2G45MA0F0AR1X | C910680 | 1.1x0.9mm | ~$0.05 | Murata, 2.4-2.5GHz ISM band |
| BL1 | 1 | Sub-GHz balun 868/915MHz | 0896BM15A0001E | TBD | 0805 | ~$0.50 | Johanson, 50-ohm differential to single-ended. Not confirmed on LCSC -- may need consignment or alternative. |
| J1 | 1 | IPEX MHF4 connector (sub-GHz) | KH-IPEX4-2020 | C530666 | SMD | ~$0.09 | Kinghelm, 50-ohm, 3GHz rated |
| J2 | 1 | IPEX MHF4 connector (2.4GHz) | KH-IPEX4-2020 | C530666 | SMD | ~$0.09 | Same part |

### Sub-GHz Balun Alternatives
The Johanson 0896BM15A0001E may not be available on LCSC. Alternatives:
1. Discrete L-C balun using 0402 inductors and capacitors (cheapest, requires tuning)
2. Anaren B0310J50100AHF (LCSC C502721) -- 315MHz, too low
3. Check LCSC balun category for 868/915MHz options
4. Consign from Mouser/DigiKey if no LCSC equivalent

If using discrete balun, add 3-4 passive components (inductors + capacitors) instead of BL1.

## Capacitors (0402, X5R/X7R unless noted)

| Ref | Qty | Value | Voltage | LCSC | Unit Price (USD) | Notes |
|-----|-----|-------|---------|------|-----------------|-------|
| C1 | 1 | 22uF | 10V | C159770 | ~$0.02 | LDO input bulk. 0805 package (22uF unavailable in 0402). |
| C2 | 1 | 100nF | 10V | C307331 | ~$0.003 | LDO input decoupling |
| C3, C4 | 2 | 22uF | 6.3V | C159770 | ~$0.02 | LDO output bulk. 0805 package. |
| C5 | 1 | 100nF | 6.3V | C307331 | ~$0.003 | LDO output decoupling |
| C6-C9 | 4 | 100nF | 6.3V | C307331 | ~$0.003 | ESP32-C3 VDD pins |
| C10 | 1 | 100nF | 6.3V | C307331 | ~$0.003 | Radio 1 VDD_IN |
| C11 | 1 | 1uF | 6.3V | C52923 | ~$0.003 | Radio 1 VDD_IN bulk |
| C12 | 1 | 100nF | 6.3V | C307331 | ~$0.003 | Radio 1 LDO_OUT |
| C13 | 1 | 100nF | 6.3V | C307331 | ~$0.003 | Radio 1 VR_PA |
| C14 | 1 | 4.7uF | 6.3V | C368816 | ~$0.005 | Radio 1 VBAT_SW |
| C15 | 1 | 100nF | 6.3V | C307331 | ~$0.003 | Radio 1 VDD_TCXO |
| C16 | 1 | 100nF | 6.3V | C307331 | ~$0.003 | Radio 2 VDD_IN |
| C17 | 1 | 1uF | 6.3V | C52923 | ~$0.003 | Radio 2 VDD_IN bulk |
| C18 | 1 | 100nF | 6.3V | C307331 | ~$0.003 | Radio 2 LDO_OUT |
| C19 | 1 | 100nF | 6.3V | C307331 | ~$0.003 | Radio 2 VR_PA |
| C20 | 1 | 4.7uF | 6.3V | C368816 | ~$0.005 | Radio 2 VBAT_SW |
| C21 | 1 | 100nF | 6.3V | C307331 | ~$0.003 | Radio 2 VDD_TCXO |
| C22 | 1 | 100nF | 6.3V | C307331 | ~$0.003 | SE2431L VDD_LNA |
| C23 | 1 | 100nF | 6.3V | C307331 | ~$0.003 | SE2431L VDD_PA |
| C24 | 1 | 1uF | 6.3V | C52923 | ~$0.003 | SE2431L VDD_PA bulk |
| C25 | 1 | 1uF | 6.3V | C52923 | ~$0.003 | CHIP_EN RC delay |
| C26 | 1 | 100nF | 6.3V | C307331 | ~$0.003 | Radio 1 NRESET debounce |
| C27 | 1 | 100nF | 6.3V | C307331 | ~$0.003 | Radio 2 NRESET debounce |

Capacitor subtotals: 14x 100nF, 4x 1uF, 2x 4.7uF, 3x 22uF (0805)

### Capacitor LCSC Notes
- C307331: Murata GRM155R71C104KA88D, 100nF 0402 X7R 16V. JLCPCB basic part.
- C52923: Samsung CL05A105KA5NQNC, 1uF 0402 X5R 25V. JLCPCB basic part.
- C368816: Samsung CL05A475KP5NRNC, 4.7uF 0402 X5R 10V.
- C159770: Samsung CL21A226MAQNNNE, 22uF 0805 X5R 25V. Verify availability; alternative C5672399.

## Resistors (0402)

| Ref | Qty | Value | LCSC | Unit Price (USD) | Notes |
|-----|-----|-------|------|-----------------|-------|
| R1 | 1 | 10k | C25744 | ~$0.002 | CHIP_EN pull-up |
| R2 | 1 | 10k | C25744 | ~$0.002 | Radio 1 NSS pull-up |
| R3 | 1 | 10k | C25744 | ~$0.002 | Radio 2 NSS pull-up |
| R4 | 1 | 10k | C25744 | ~$0.002 | GPIO9 boot strap pull-up |
| R5 | 1 | 10k | C25744 | ~$0.002 | Radio 1 NRESET pull-up |
| R6 | 1 | 10k | C25744 | ~$0.002 | Radio 2 NRESET pull-up |
| R7 | 1 | 100k | C25741 | ~$0.002 | SE2431L TXEN pull-down |
| R8 | 1 | 100k | C25741 | ~$0.002 | SE2431L RXEN pull-down |

Resistor subtotals: 6x 10k, 2x 100k

### Resistor LCSC Notes
- C25744: UniOhm 0402WGF1002TCE, 10k 0402 1%. JLCPCB basic part.
- C25741: UniOhm 0402WGF1003TCE, 100k 0402 1%. JLCPCB basic part.

## Ferrite Beads (0402)

| Ref | Qty | Value | LCSC | Unit Price (USD) | Notes |
|-----|-----|-------|------|-----------------|-------|
| FB1 | 1 | 600R@100MHz | C76662 | ~$0.005 | Radio 1 VBAT_SW supply filter |
| FB2 | 1 | 600R@100MHz | C76662 | ~$0.005 | Radio 2 VBAT_SW supply filter |

### Ferrite Bead LCSC Notes
- C76662: Murata BLM15AG601SN1D, 600R@100MHz 0402. JLCPCB basic part.

## RF Matching Components (0402, values TBD)

| Ref | Qty | Description | Package | Notes |
|-----|-----|-------------|---------|-------|
| L_RF1-L_RF2 | 2 | Sub-GHz matching inductors | 0402 | Values from LR1121 ref design, typically 3.9nH-12nH |
| C_RF1-C_RF3 | 3 | Sub-GHz matching capacitors | 0402 | Values from LR1121 ref design, NP0/C0G |
| L_RF3-L_RF4 | 2 | 2.4GHz matching inductors | 0402 | SE2431L input/output matching |
| C_RF4-C_RF6 | 3 | 2.4GHz matching capacitors | 0402 | SE2431L input/output matching, NP0/C0G |

RF matching component values are determined during layout based on PCB stackup and trace impedance. Budget ~$0.10 total for RF passives.

Use NP0/C0G dielectric for all RF capacitors (not X5R/X7R).
Use wire-wound or thin-film inductors for RF (not multilayer ferrite).

## BOM Cost Estimate (per unit at qty 100)

| Category | Est. Cost (USD) |
|----------|----------------|
| ESP32-C3FH4 | $1.80 |
| LR1121 x2 | $5.00 |
| SE2431L | $1.89 |
| AP2112K LDO | $0.07 |
| TCXOs x2 | $0.92 |
| SAW filter | $0.05 |
| Sub-GHz balun | $0.50 |
| IPEX connectors x2 | $0.18 |
| Capacitors (27 pcs) | $0.30 |
| Resistors (8 pcs) | $0.02 |
| Ferrite beads (2 pcs) | $0.01 |
| RF matching (~10 pcs) | $0.10 |
| **Total BOM** | **~$10.84** |

EUR equivalent at 1.08 rate: ~EUR 11.70

### Cost Notes
- LR1121 is the dominant cost driver at ~46% of BOM
- Target EUR 12-15 is achievable at these prices
- JLCPCB assembly adds ~$0.50/board for basic parts, ~$3-5/board for extended parts
- SE2431L is extended part on JLCPCB (extra setup fee ~$3 per unique extended part)
- LR1121 is extended part
- PCB fabrication at qty 100: ~$1-2/board for 4-layer 24x18mm

### Cost Comparison vs Competition
- RadioMaster XR4: $39.99 retail
- RadioMaster DBR4: $28.99 retail
- OpenRX-Gemini target: $20-25 retail (open source, community pricing)
- BOM at ~$11 leaves margin for PCB, assembly, packaging, and distribution

## Component Sourcing Risk

| Component | Risk | Stock (as of 2026-03) | Mitigation |
|-----------|------|----------------------|-----------|
| ESP32-C3FH4 (C2858491) | Low | Good LCSC stock | Widely available |
| LR1121 (C7498014) | HIGH | Low/variable LCSC stock | Order early. Check Mouser/DigiKey. Consider consignment. |
| SE2431L-R (C2649471) | Medium | ~1272 units | Adequate for prototype. Monitor for production. |
| AP2112K (C51118) | Low | 162k+ units | Very common, JLCPCB basic |
| YXC TCXO (C22434888) | Medium | ~2782 units | Adequate. Check alternative: Taitien TYETBCSANF-32.000000 (C6732076) when back in stock. |
| SAW filter (C910680) | Low | Good stock | Murata, widely available |
| IPEX MHF4 (C530666) | Low | 13k+ units | Kinghelm, good stock |
| 0402 passives | Low | Basic parts, millions in stock | JLCPCB basic parts |

## JLCPCB Assembly Classification

### Basic Parts (no setup fee)
- AP2112K-3.3TRG1 (C51118)
- All 0402 resistors (C25744, C25741)
- All 0402 capacitors 100nF (C307331)
- All 0402 capacitors 1uF (C52923)
- Ferrite beads (C76662)

### Extended Parts (setup fee per unique part)
- ESP32-C3FH4 (C2858491)
- LR1121IMLTRT (C7498014) -- x2 but same part number = one setup fee
- SE2431L-R (C2649471)
- YXC TCXO (C22434888) -- x2 but same part number = one setup fee
- SAFFB2G45MA0F0AR1X (C910680)
- KH-IPEX4-2020 (C530666) -- x2 but same part number = one setup fee
- 22uF 0805 capacitors
- 4.7uF 0402 capacitors

Estimated unique extended parts: ~7 = ~$21 total extended part fees (amortized over batch).

## Mechanical

| Item | Description | Notes |
|------|-------------|-------|
| PCB | 24x18mm, 4-layer, 1.0mm, ENIG | JLCPCB JLC04161H-7628 stackup |
| Solder pads | 4 castellated or edge pads: 5V, GND, TX, RX | Standard ELRS receiver pinout |
| Boot pads | Optional solder bridge for GPIO9-to-GND | Factory flash / recovery |
| Heatshrink | 30mm clear heatshrink tube | Packaging, standard for ELRS receivers |
