# OpenRX-Nano Bill of Materials

> Audit note: this is the current preferred 2.4GHz baseline because it already uses `RFX2401C`. The SAW filter and connector choices still need to be reconciled with `CORE_BOM.md` before freezing procurement.

Target BOM cost: EUR 5-6 at quantity 100+

## Active Components

| Ref | Description | MPN | Package | LCSC | Qty | Unit Price (USD) | Notes |
|-----|-------------|-----|---------|------|-----|-------------------|-------|
| U1  | 3.3V 500mA LDO | ME6211C33M5G-N | SOT-23-5 | C82942 | 1 | $0.07 | Basic part |
| U2  | MCU, 4MB flash | ESP32-C3FH4 | QFN-32 5x5mm | C2858491 | 1 | $1.15 | Extended |
| U3  | 2.4GHz LoRa transceiver | SX1281IMLTRT | QFN-24 4x4mm | C2151551 | 1 | $1.80 | Extended |
| U4  | 2.4GHz PA+LNA+Switch | RFX2401C | QFN-16 3x3mm | C19213 | 1 | $0.90 | Extended |
| Y1  | 40MHz crystal, 10pF | S3240000101040 | SMD3225 | C426988 | 1 | $0.06 | Extended |
| Y2  | 52MHz TCXO, 3.3V, ±0.5ppm | OW7EL89CENUNFAYLC-52M | SMD2016 | C22434896 | 1 | $0.42 | Extended |
| FL1 | 2.4GHz SAW filter | 2450FM07D0034T | 0402-4pad | C2651081 | 1 | $0.15 | Extended |
| J1  | UFL/IPEX connector | CONUFL001-SMD-T | SMD | C22418213 | 1 | $0.56 | Extended |
| LED1 | WS2812B RGB LED | WS2812B-2020 | 2020 | C965555 | 1 | $0.04 | Extended |
| SW1 | Tactile switch (boot) | — | 3x4mm SMD | — | 1 | $0.02 | Any 3x4 tact |

### Active Component Subtotal: ~$5.17

## Passive Components — Capacitors

| Ref | Value | Package | Spec | LCSC | Qty | Notes |
|-----|-------|---------|------|------|-----|-------|
| C1  | 10uF  | 0805 | X5R 25V ±10% | C15850 | 1 | LDO input, basic |
| C2  | 100nF | 0402 | X7R 16V ±10% | C1525 | 1 | LDO input bypass, basic |
| C3  | 22uF  | 0805 | X5R 25V ±10% | C45783 | 1 | LDO output, basic |
| C4  | 100nF | 0402 | X7R 16V ±10% | C1525 | 1 | LDO output bypass, basic |
| C5  | 1uF   | 0402 | X7R 16V ±10% | C52923 | 1 | EN RC delay, basic |
| C6  | 100nF | 0402 | X7R 16V ±10% | C1525 | 1 | ESP32 VDD3P3, basic |
| C7  | 100nF | 0402 | X7R 16V ±10% | C1525 | 1 | ESP32 VDD_SPI, basic |
| C8  | 100nF | 0402 | X7R 16V ±10% | C1525 | 1 | ESP32 VDD3P3_RTC, basic |
| C9  | 100nF | 0402 | X7R 16V ±10% | C1525 | 1 | SX1281 pin 1 VDD, basic |
| C10 | 100nF | 0402 | X7R 16V ±10% | C1525 | 1 | SX1281 pin 2 VDD_IN, basic |
| C11 | 470nF | 0402 | X7R 16V ±10% | C1543 | 1 | SX1281 VR_PA (LDO mode), basic |
| C12 | 100nF | 0402 | X7R 16V ±10% | C1525 | 1 | SX1281 pin 11 VDD, basic |
| C13 | 1uF   | 0402 | X5R 16V ±10% | C52923 | 1 | RFX2401C VDD, basic |
| C14 | 220pF | 0402 | C0G/NP0 50V ±5% | C1604 | 1 | RFX2401C VDD HF, basic |
| C15 | 0.3pF | 0402 | C0G/NP0 50V | — | 1 | 5th harmonic filter, see note |
| C16 | 100nF | 0402 | X7R 16V ±10% | C1525 | 1 | TCXO VCC, basic |
| C17 | 100nF | 0402 | X7R 16V ±10% | C1525 | 1 | WS2812B VDD, basic |
| CX1 | 10pF  | 0402 | C0G/NP0 50V ±5% | C32949 | 1 | 40MHz crystal load, basic |
| CX2 | 10pF  | 0402 | C0G/NP0 50V ±5% | C32949 | 1 | 40MHz crystal load, basic |

**Note on C15 (0.3pF)**: This is a non-standard value. Options:
- Use 0.5pF (LCSC C1550 or similar) as closest standard value
- Omit if the SAW filter provides adequate harmonic rejection
- Use copper pour pad to create parasitic capacitance (~0.3pF)

### Capacitor Subtotal: ~$0.10 (all basic parts, negligible cost)

## Passive Components — Resistors

| Ref | Value | Package | Spec | LCSC | Qty | Notes |
|-----|-------|---------|------|------|-----|-------|
| R1  | 10k | 0402 | ±1% 1/16W | C25744 | 1 | ESP32 EN pull-up, basic |
| R2  | 10k | 0402 | ±1% 1/16W | C25744 | 1 | GPIO9 boot pull-up, basic |
| R3  | 10k | 0402 | ±1% 1/16W | C25744 | 1 | SX1281 NRESET pull-up, basic |
| R4  | 10k | 0402 | ±1% 1/16W | C25744 | 1 | SX1281 NSS pull-up, basic |
| R5  | 10k | 0402 | ±1% 1/16W | C25744 | 1 | TXEN series, basic |
| R6  | 10k | 0402 | ±1% 1/16W | C25744 | 1 | RXEN series, basic |
| R7  | 470R | 0402 | ±1% 1/16W | C25117 | 1 | LED DIN series, basic |

### Resistor Subtotal: ~$0.01

## Connectors / Mechanical

| Ref | Description | Package | LCSC | Qty | Notes |
|-----|-------------|---------|------|-----|-------|
| J1  | UFL/IPEX connector | SMD | C22418213 | 1 | Listed in actives above |
| J2  | Solder pads 4x (5V, GND, TX, RX) | 1.27mm pitch | — | 1 | Copper pads on PCB edge |
| TP1-3 | Test pads (USB D+, D-, GND) | 1.0mm round | — | 3 | Copper pads |

## BOM Cost Summary (USD, qty 100)

| Category | Cost |
|----------|------|
| Active components | $5.17 |
| Passive components | $0.15 |
| **Total BOM** | **~$5.32** |

At current exchange rates (~1 USD = 0.92 EUR), BOM is approximately **EUR 4.90**.
Within the EUR 5-6 target.

## JLCPCB Assembly Notes

- 9 unique active component types (all SMD)
- 19 unique passive component types (mostly 0402, basic parts)
- Total component count: ~30 parts
- Basic parts: ME6211, all 0402 caps and resistors (no setup fee)
- Extended parts: ESP32-C3, SX1281, RFX2401C, crystal, TCXO, SAW, UFL, WS2812B
  (setup fee per unique extended part, ~$3 each)
- Setup fees at qty 100: ~$27 total ($0.27/board)
- PCB cost (20x13mm, 2-layer, 1.0mm, qty 100): ~$0.50/board
- Assembly cost: ~$0.50/board
- **Total per-board cost at qty 100: ~EUR 6.10** (BOM + PCB + assembly + setup)

## Alternate Parts

| Original | Alternative | LCSC | Notes |
|----------|-------------|------|-------|
| RFX2401C (C19213) | SE2431L-R | C2649471 | Discontinued, check stock |
| 2450FM07D0034 (C2651081) | 2450LP14A100T | — | Johanson LP filter alternative |
| OW7EL89CENUNFAYLC-52M | ABDFTCXO-52MHz | C568568 | Abracon TCXO, larger package |
| S3240000101040 (C426988) | Any 40MHz 10pF 3225 | C90924 | TXC Corp alternative |
| C22418213 (UFL) | Any IPEX1/UFL receptacle | — | Standard footprint |
| WS2812B-2020 (C965555) | WS2812C-2020 | — | Works at 3.3V natively |
