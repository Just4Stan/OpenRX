# OpenRX-Gemini

Dual-LR1121 Gemini/Xrossband receiver. ESP32-C3 + 2x LR1121 + 2x RFX2401C + 2x SKY13414 + 2x Johanson IPD.

## Schematic

- Main sheet: `esp32c3_lr1121_gemini.kicad_sch`
- Radio A (U9 LR1121, U10 RFX2401C, U11 SKY13414): RF chain → `JP1` U.FL
- Radio B (U2 LR1121, U5 RFX2401C, U7 SKY13414): mirrors Radio A → `JP2` U.FL
- 2.4 GHz path per radio: `LR1121 RFIO_HF → 2450FM07D0034 (FL1/FL2) → RFX2401C → 0.3pF → SKY13414 RF4 → U.FL`
- Sub-GHz path per radio: `LR1121 → Johanson IPD (T1/T2) → SKY13414 RF1 (RX) / RF3 (TX HP) → U.FL`
- RF switch control (each radio controls its own switch): `DIO7 → V3, DIO8 → V2, V1 → GND`
- RFX2401C control (each radio controls its own FE): `DIO5 → RXEN, DIO6 → TXEN`
- ELRS sends `SetDioAsRfSwitch` to both radios simultaneously — wiring is symmetric so `radio_rfsw_ctrl` applies to both.

### SKY13414 Port Mapping (V1=GND, per switch)

| DIO7 (V3) | DIO8 (V2) | Port | Path |
|---|---|---|---|
| 0 | 0 | RF1 | Sub-GHz RX (IPD pin 6) |
| 1 | 0 | RF2 | NC |
| 0 | 1 | RF3 | Sub-GHz TX HP (IPD pin 9) |
| 1 | 1 | RF4 | 2.4GHz TX/RX (RFX2401C ANT) |

IPD TX_LP (pin 8) is disconnected — ELRS never uses LP PA on these boards.

### Status (2026-04-19, ELRS review)

All pre-fabrication schematic blockers resolved. Previously tracked bugs:

1. **DIO7-2 / DIO8-2 wiring:** FIXED — U7 (Radio B) V3/V2 tied to DIO7-2/DIO8-2, U11 (Radio A) V3/V2 tied to DIO7-1/DIO8-1. Each radio drives its own switch.
2. **Component swap:** DONE — filters migrated from `DEA102700LT-6307A2` to `2450FM07D0034T` (FL1 on Radio A, FL2 on Radio B), switches migrated from `SKY13588-460LF` to `SKY13414-485LF` (U7/U11).
3. **Ref designators:** filters renamed USB2→FL1 (Radio A) and USB1→FL2 (Radio B).

PCB routing, DRC, and on-hardware RF validation remain — see Release To-Do.

## Firmware

- ELRS target: `Unified_ESP32C3_LR1121_RX` (same binary as Mono)
- Hardware JSON: `/shared/elrs-targets/OpenRX Gemini LR1121.json`
- `radio_nss_2` enables dual-radio mode
- `radio_rfsw_ctrl: [15, 0, 0, 8, 8, 14, 0, 13]` — same as Mono, see Mono `DESIGN.md` for decode table (DIO5=RXEN, DIO6=TXEN, DIO7=V3, DIO8=V2)

## Flash Interface

- Pads: `5V`, `GND`, `RX`, `TX`
- `BOOT` pad + tactile button on GPIO9
- Hold BOOT/button during power-up for UART download mode
- Use Wi-Fi OTA after first flash

## Sourcing

- `C255353` SKY13414-485LF (x2)
- `C19842466` 0900PC16J0042001E (x2, consign from DigiKey)
- `C7498014` LR1121IMLTRT (x2)
- `C2651081` 2450FM07D0034T (x2)
- `C19213` RFX2401C (x2)

## Release To-Do

- Finish PCB routing / DRC
- Validate symmetric RF performance across both chains (NanoVNA)
- Run Gemini / Xrossband link validation on two LR1121-equipped TXs
- CE / RED pre-scan for dual-band operation
