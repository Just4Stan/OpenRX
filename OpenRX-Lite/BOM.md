# OpenRX-Lite Bill of Materials

Target BOM cost: EUR 3-4 at quantity 100+

## ICs

| Designator | Value | Package | LCSC | Description | Qty | Est. Price (USD) |
|------------|-------|---------|------|-------------|-----|-----------------|
| U1 | ESP32-C3FH4 | QFN-32 (5x5mm) | C2858491 | RISC-V MCU, 160MHz, 4MB flash, WiFi+BLE | 1 | $1.69 |
| U2 | SX1281IMLTRT | QFN-24 (4x4mm) | C2151551 | 2.4GHz LoRa/FLRC/FSK transceiver | 1 | $2.50 |
| U3 | ME6211C33M5G-N | SOT-23-5 | C82942 | 3.3V 500mA LDO regulator | 1 | $0.07 |

## Crystals and Oscillators

| Designator | Value | Package | LCSC | Description | Qty | Est. Price (USD) |
|------------|-------|---------|------|-------------|-----|-----------------|
| Y1 | 40MHz | SMD1612-4P (1.6x1.2mm) | C2875272 | Crystal, 10pF load, +/-10ppm (CJ17-400001010B20) | 1 | $0.08 |
| Y2 | 52MHz TCXO | SMD2016-4P (2.0x1.6mm) | C22434896 | TCXO, 3.3V, +/-0.5ppm (OW7EL89CENUNFAYLC-52M) | 1 | $0.45 |

## Antenna

| Designator | Value | Package | LCSC | Description | Qty | Est. Price (USD) |
|------------|-------|---------|------|-------------|-----|-----------------|
| ANT1 | 2450AT18A100E | 3.2x1.6mm | C89334 | 2.4GHz ceramic chip antenna (Johanson) | 1 | $0.25 |

## Optional Components

| Designator | Value | Package | LCSC | Description | Qty | Est. Price (USD) |
|------------|-------|---------|------|-------------|-----|-----------------|
| D1 | WS2812B | 3.5x3.5mm | C2761795 | Addressable RGB LED (status indicator) | 0-1 | $0.05 |
| SW1 | Tactile switch | 3x4mm or 2x3mm | -- | Boot button (can substitute solder pads) | 0-1 | $0.02 |

## Passives (not imported -- add manually in KiCad)

### Capacitors

| Designator | Value | Package | Dielectric | Voltage | Qty | Notes |
|------------|-------|---------|------------|---------|-----|-------|
| C1 | 10uF | 0603 | X5R | 10V | 1 | LDO input bulk |
| C2 | 100nF | 0402 | X7R | 16V | 1 | LDO input decoupling |
| C3 | 22uF | 0603 | X5R | 10V | 1 | LDO output bulk |
| C4 | 100nF | 0402 | X7R | 16V | 1 | LDO output decoupling |
| C5 | 100nF | 0402 | X7R | 16V | 1 | ESP32-C3 3V3 decoupling |
| C6 | 1uF | 0402 | X5R | 10V | 1 | ESP32-C3 EN RC filter |
| C7 | 10pF | 0402 | C0G | 50V | 1 | Crystal load cap (XTAL_P) |
| C8 | 10pF | 0402 | C0G | 50V | 1 | Crystal load cap (XTAL_N) |
| C9 | 100nF | 0402 | X7R | 16V | 1 | SX1281 VDD (pin 1) |
| C10 | 100nF | 0402 | X7R | 16V | 1 | SX1281 VDD_IN (pin 2) |
| C11 | 100nF | 0402 | X7R | 16V | 1 | SX1281 NRESET RC filter |
| C12 | 470nF | 0402 | X5R | 10V | 1 | SX1281 VR_PA (LDO mode) |
| C13 | 100nF | 0402 | X7R | 16V | 1 | SX1281 VDD (pin 11) |
| C14 | 10pF | 0402 | C0G | 50V | 1 | TCXO AC coupling (optional) |
| C15 | 100nF | 0402 | X7R | 16V | 1 | TCXO VDD decoupling |
| C16 | 1.0pF | 0402 | C0G | 50V | 1 | Antenna match shunt cap |
| C17 | 100nF | 0402 | X7R | 16V | 1 | WS2812B decoupling (optional) |

**Capacitor totals:** 100nF x9, 10pF x3, 10uF x1, 22uF x1, 1uF x1, 470nF x1, 1pF x1

### Resistors

| Designator | Value | Package | Qty | Notes |
|------------|-------|---------|-----|-------|
| R1 | 10k | 0402 | 1 | ESP32-C3 EN pull-up |
| R2 | 10k | 0402 | 1 | SPI NSS pull-up |
| R3 | 10k | 0402 | 1 | BOOT GPIO9 pull-up |
| R4 | 100R | 0402 | 1 | WS2812B data series (optional) |
| R5 | 10k | 0402 | 1 | SX1281 NRESET pull-up |

**Resistor totals:** 10k x4, 100R x1

### Inductors

| Designator | Value | Package | Qty | Notes |
|------------|-------|---------|-----|-------|
| L1 | 2.2nH | 0402 | 1 | Antenna L-match series. High-Q (>30 at 2.4GHz). |

## Imported Components (easyeda2kicad)

The following components have been imported into `libs/OpenRX-Lite.*`:

| LCSC | Part | Symbol | Footprint |
|------|------|--------|-----------|
| C2858491 | ESP32-C3FH4 | ESP32-C3FH4 | QFN-32_L5.0-W5.0-P0.50-TL-EP3.7 |
| C2151551 | SX1281IMLTRT | SX1281IMLTRT | QFN-24_L4.0-W4.0-P0.50-TL-EP2.6 |
| C89334 | 2450AT18A100E | 2450AT18A100E | ANT-SMD_L3.2-W1.6 |
| C82942 | ME6211C33M5G-N | ME6211C33M5G-N | SOT-23-5_L3.0-W1.7-P0.95-LS2.8-BL |
| C22434896 | 52MHz TCXO | OW7EL89CENUNFAYLC-52M | OSC-SMD_4P-L2.0-W1.6-BL_TXC_7Z |
| C2875272 | 40MHz Crystal | CJ17-400001010B20 | CRYSTAL-SMD_4P-L1.6-W1.2-BL |

Library path: `libs/OpenRX-Lite.kicad_sym` (symbols), `libs/OpenRX-Lite.pretty/` (footprints), `libs/OpenRX-Lite.3dshapes/` (3D models)

## BOM Cost Estimate (qty 100, LCSC pricing)

| Category | Est. Cost |
|----------|-----------|
| ESP32-C3FH4 | $1.69 |
| SX1281IMLTRT | $2.50 |
| ME6211C33M5G-N | $0.07 |
| 52MHz TCXO | $0.45 |
| 40MHz Crystal | $0.08 |
| Ceramic Antenna | $0.25 |
| All passives (~17 caps, 5 resistors, 1 inductor) | ~$0.15 |
| WS2812B (optional) | $0.05 |
| **Total (without PCB/assembly)** | **~$5.24** |

**Note:** The SX1281 is the cost driver at $2.50. At qty 1000+ the price drops to ~$1.80, bringing total BOM closer to $4.50. The EUR 3-4 target is aggressive and may require either volume pricing or substituting a cheaper transceiver (SX1280 if available cheaper). PCB fabrication and assembly at JLCPCB adds approximately $1-2 per unit at qty 100.
