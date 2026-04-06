# OpenRX-Gemini

Dual-LR1121 Gemini/Xrossband receiver. ESP32-C3 + 2x LR1121 + 2x RFX2401C + 2x SKY13414 + 2x Johanson IPD.

## Schematic

- Main sheet: `esp32c3_lr1121_gemini.kicad_sch`
- Radio chain A: `LR1121 → IPD → SKY13414 → JP1 U.FL`
- Radio chain B: mirrors chain A → `JP2 U.FL`
- 2.4 GHz paths: `LR1121 RFIO_HF → 2450FM07D0034 → RFX2401C → 0.3pF → SKY13414 RF3`
- RF switch control (both chains): `DIO7 → V3, DIO8 → V2, V1 → GND`
- RFX2401C control: `DIO5 → RXEN, DIO6 → TXEN`
- Wiring SHOULD be symmetrical — ELRS sends SetDioAsRfSwitch to both radios simultaneously

### KNOWN BUGS (not ordered for fabrication yet)

1. **DIO7-2/DIO8-2 wiring bug:** Both SKY13414 switches (U6, U11) are controlled by Radio A's DIO7-1/DIO8-1. Radio B's DIO7-2/DIO8-2 are single-pin nets (go nowhere). Fix: U11 V3→DIO7-2, U11 V2→DIO8-2.

2. **Schematic still has old components:** index.json shows SKY13588-460LF (U6) and DEA102700LT-6307A2 (USB1) in the schematic — not yet updated to SKY13414 and 2450FM07D0034.

## Firmware

- ELRS target: `Unified_ESP32C3_LR1121_RX` (same binary as Mono)
- Hardware JSON: `/shared/elrs-targets/OpenRX Gemini LR1121.json`
- `radio_nss_2` enables dual-radio mode
- `radio_rfsw_ctrl: [15, 0, 0, 12, 4, 10, 0, 9]` — same as Mono, see Mono DESIGN.md for decode table

## Flash Interface

- Pads: `5V`, `GND`, `RX`, `TX`
- `BOOT` pad + tactile button on GPIO9
- Hold BOOT/button during power-up for UART download mode
- Use Wi-Fi OTA after first flash

## Sourcing

- `C255353` SKY13414-485LF (x2)
- `C19842466` 0900PC16J0042001E (x2, consign from DigiKey)
- `C7498014` LR1121IMLTRT (x2)
- `C2651081` 2450FM07D0034 (x2)
- `C19213` RFX2401C (x2)

## Release To-Do

- **Fix DIO7-2/DIO8-2 wiring** — Radio B switch has no control signals
- **Update schematic components** — replace SKY13588 with SKY13414, DEA102700 with 2450FM07D0034
- Rename USB1/USB2 ref designators to FL1/FL2
- Finish PCB routing / DRC
- Validate symmetric RF performance across both chains
- Run Gemini / Xrossband link validation
- CE / RED pre-scan for dual-band operation
