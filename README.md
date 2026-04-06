# OpenRX

Open-source ExpressLRS receiver family — four active boards:

- `OpenRX-Lite`: compact 2.4 GHz SX1281 receiver with ceramic antenna
- `OpenRX-Lite-UFL`: same as Lite with U.FL antenna connector
- `OpenRX-Mono`: single-LR1121 multi-band receiver with 1x U.FL
- `OpenRX-Gemini`: dual-LR1121 Gemini/Xrossband receiver with 2x U.FL

| Model | Band | RF | Front-End | Antenna | ELRS Target |
|-------|------|-----|-----------|---------|-------------|
| **Lite** | 2.4 GHz | SX1281 | 2450FM07D0034 BPF | Ceramic | `Unified_ESP32C3_2400_RX` |
| **Lite UFL** | 2.4 GHz | SX1281 | 2450FM07D0034 BPF | U.FL | `Unified_ESP32C3_2400_RX` |
| **Mono** | Multi-band | LR1121 | RFX2401C + SKY13414 + Johanson IPD | 1x U.FL | `Unified_ESP32C3_LR1121_RX` |
| **Gemini** | Xrossband | 2x LR1121 | 2x (RFX2401C + SKY13414 + Johanson IPD) | 2x U.FL | `Unified_ESP32C3_LR1121_RX` |

Mono and Gemini use the same firmware binary — `radio_nss_2` in hardware.json activates dual-radio mode.

## Active Schematics

- `OpenRX-Lite/esp32c3_sx1281_lite.kicad_sch`
- `OpenRX-Lite-UFL/esp32c3_sx1281_lite.kicad_sch`
- `OpenRX-Mono/esp32c3_lr1121_mono.kicad_sch`
- `OpenRX-Gemini/esp32c3_lr1121_gemini.kicad_sch`

## Documentation

- `OpenRX-Lite/DESIGN.md`
- `OpenRX-Lite-UFL/DESIGN.md`
- `OpenRX-Mono/DESIGN.md`
- `OpenRX-Gemini/DESIGN.md`

## Flashing

All boards expose `5V`, `GND`, `RX`, `TX` pads and a `BOOT` pad (GPIO9 to GND) for initial UART flashing. Mono and Gemini also have a tactile button on GPIO9. After first flash, use Wi-Fi OTA or Betaflight passthrough.

## ELRS Firmware Targets

Hardware JSON files are in `/shared/elrs-targets/`:

- `OpenRX Lite 2400.json`
- `OpenRX Mono LR1121.json`
- `OpenRX Gemini LR1121.json`
- `targets_entries.json`

## KiCad Libraries

All projects use KiCad 9 with project-local libraries only — no global library dependencies.

`shared/libs/` contains:

| Library | Contents |
|---------|----------|
| `OpenRX-Shared.kicad_sym` | Symbols: ESP32-C3, LR1121, SX1281, RFX2401C, SKY13414, TLV75533, Johanson IPD, 2450FM07D0034, antennas, LED, connectors |
| `OpenRX-Shared.pretty` | Footprints: QFN-14/16/24/32, X2SON, antenna, filter, LED, switch, solder pads |
| `OpenRX-Shared.3dshapes` | 3D models (.step + .wrl) |

All symbols include an `LCSC Part` property for JLCPCB BOM export.

## Datasheets

Shared local cache in `datasheets/common/`. All active IC/RF datasheets are present locally.

## Sourcing

Current low-stock / JLCPCB Global Sourcing candidates:

- `C255353` SKY13414-485LF
- `C19842466` 0900PC16J0042001E (consign from DigiKey)
- `C7498014` LR1121IMLTRT
- `C2151551` SX1281IMLTRT (for 1000 pcs Lite build)
- `C2651081` 2450FM07D0034

## License

**CERN Open Hardware Licence Version 2 - Strongly Reciprocal** ([CERN-OHL-S-2.0](https://ohwr.org/cern_ohl_s_v2.txt)). See [LICENSE](LICENSE).
