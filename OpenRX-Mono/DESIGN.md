# OpenRX-Mono

Final active mainstream multi-band receiver schematic based on `ESP32-C3 + LR1121`.

## Current Schematic

- Main sheet: `OpenRX-Mono/esp32c3_lr1121_mono.kicad_sch`
- Sub-GHz path: `LR1121 -> 0900PC16J0042001E -> SKY13588`
- `2.4 GHz` path: `LR1121 RFIO_HF -> DEA102700LT-6307A2 -> RFX2401C -> 0.3 pF shunt -> SKY13588`
- Antenna output: `SKY13588 RFC -> JP1 U.FL`
- Wi-Fi / service antenna: `AE1 2450AT18A100E`

## Firmware Basis

- ExpressLRS env basis: `Unified_ESP32C3_LR1121_RX_via_UART`
- OTA basis: `Unified_ESP32C3_LR1121_RX_via_WIFI`
- Upstream target basis: `Generic C3 LR1121`

Important firmware note:

- Mono needs an OpenRX-specific `hardware.json` / layout entry
- Mono also needs the custom `radio_rfsw_ctrl` table that matches the current `LR1121 + RFX2401C + SKY13588` topology

## Flash Interface

- `TP1` = `RX`
- `TP2` = `TX`
- `TP3` = `5V`
- `TP4` = `GND`
- `SW1` / `BUTTON` pulls `GPIO9` low for manual UART download mode

First flash:

- hold the onboard `BUTTON`
- power the board through `TP3`
- flash over `TP1/TP2/TP3/TP4`
- use Wi-Fi OTA after the first successful flash

## Datasheets

Local shared datasheets used by Mono are present under `datasheets/common/`, including:

- `ESP32-C3FH4_datasheet.pdf`
- `LR1121_datasheet.pdf`
- `LR1121_user_manual.pdf`
- `RFX2401C_datasheet.pdf`
- `SKY13588-460LF_datasheet.pdf`
- `0900PC16J0042001E_datasheet.pdf`
- `OW7EL89CENUYO3YLC-32M_datasheet.pdf`
- `TLV755P_datasheet.pdf`
- `Hirose_U.FL-R-SMT-1_80_C88374.pdf`
- `2450AT18A100E_antenna.pdf`
- `CJ17-400001010B20_datasheet.pdf`

The official `DEA102700LT-6307A2` PDF is still not mirrored locally.

## Sourcing

- Active fitted Mono schematic has no blank `LCSC` fields
- The main likely `JLCPCB Global Sourcing` parts are:
  - `C2151906` `SKY13588-460LF`
  - `C19842466` `0900PC16J0042001E`
  - `C7498014` `LR1121IMLTRT`

## Release To-Do

- Finish PCB routing / DRC
- Add OpenRX Mono target entry in the ELRS targets repo
- Verify `radio_rfsw_ctrl` on first bring-up
- Validate LF / HF path switching and LR1121 band behavior on hardware
- Run CE / RED pre-scan for both `2.4 GHz` and sub-GHz operation
