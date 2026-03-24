# OpenRX

Open-source ExpressLRS receiver family built around three active boards:

- `OpenRX-Lite`: compact `2.4 GHz` SX1281 receiver with ceramic ELRS antenna
- `OpenRX-Mono`: single-`LR1121` multi-band receiver with `1x U.FL`
- `OpenRX-Gemini`: dual-`LR1121` Gemini/Xrossband receiver with `2x U.FL`

The active schematics are:

| Model | Band | RF | Front-End | Antenna | Target Price | ELRS Target |
|-------|------|-----|-----------|---------|-------------|-------------|
| **Lite** | 2.4 GHz | SX1281 | DEA LPF only | Ceramic (Molex tower) | €8-15 | Generic C3 2400 |
| **Mono** | Multi-band | LR1121 | RFX2401C + SKY13588 + Johanson IPD | 1× UFL, dual-band | €15-25 | Generic C3 LR1121 |
| **Gemini** | Xrossband | 2× LR1121 | 2× (RFX2401C + SKY13588 + Johanson IPD) | 2× UFL, dual-band | €25-35 | Generic C3 LR1121 True Diversity |

- `OpenRX-Lite/esp32c3_sx1281_lite.kicad_sch`
- `OpenRX-Mono/esp32c3_lr1121_mono.kicad_sch`
- `OpenRX-Gemini/esp32c3_lr1121_gemini.kicad_sch`

These are the current source of truth for the hardware. Older Nano / 900 / Dual / PWM concepts live under `archive/legacy-projects/`.

## Documentation

The active documentation is intentionally reduced to:

- this `README.md`
- `OpenRX-Lite/DESIGN.md`
- `OpenRX-Mono/DESIGN.md`
- `OpenRX-Gemini/DESIGN.md`

## Active Board Summary

| Board | Role | ExpressLRS env basis | First-flash path | Main release work |
|------|------|-----------------------|------------------|-------------------|
| Lite | `2.4 GHz` SX1281 RX | `Unified_ESP32C3_2400_RX_via_UART` / `_via_WIFI` | UART pads + temporary `CHIP_BOOT` access | PCB finish, target entry, RF validation |
| Mono | single-`LR1121` multi-band RX | `Unified_ESP32C3_LR1121_RX_via_UART` / `_via_WIFI` | UART pads + onboard `BUTTON` | PCB finish, target entry, `radio_rfsw_ctrl`, RF validation |
| Gemini | dual-`LR1121` Gemini RX | `Unified_ESP32C3_LR1121_RX_via_UART` / `_via_WIFI` | UART pads + onboard `BUTTON` | PCB finish, target entry, dual-radio validation |

OpenRX-specific `hardware.json` / layout entries still need to be created in the ExpressLRS targets repo.

## Flashing Interface

All three boards expose:

- `TP1` = `RX`
- `TP2` = `TX`
- `TP3` = `5V`
- `TP4` = `GND`

Current boot entry:

- Lite: `GPIO9` exists as `CHIP_BOOT`, but there is no dedicated BOOT pad or button
- Mono: `BUTTON` pulls `GPIO9` low for manual UART download mode
- Gemini: `BUTTON` pulls `GPIO9` low for manual UART download mode

## Datasheets

The shared local cache is `datasheets/common/`.

All active IC / RF datasheets needed for Lite, Mono, and Gemini are present locally there except for the official `DEA102700LT-6307A2` PDF, which still needs to be mirrored into the repo. Use the official TDK product page as the current source of truth for that part.

## Sourcing

As of `2026-03-24`, the active schematics have no blank `LCSC` fields.

Current low-stock / likely `JLCPCB Global Sourcing` candidates:

- `C2151906` `SKY13588-460LF`
- `C19842466` `0900PC16J0042001E`
- `C7498014` `LR1121IMLTRT`
- `C2151551` `SX1281IMLTRT` for a full `1000 pcs` Lite build
