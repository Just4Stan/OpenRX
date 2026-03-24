# OpenRX-Gemini

Final active flagship dual-radio receiver schematic based on `ESP32-C3 + 2x LR1121`.

## Current Schematic

- Main sheet: `OpenRX-Gemini/esp32c3_lr1121_gemini.kicad_sch`
- Radio chain A:
  - `LR1121 -> 0900PC16J0042001E -> SKY13588`
  - `LR1121 RFIO_HF -> DEA102700LT-6307A2 -> RFX2401C -> 0.3 pF shunt -> SKY13588`
  - `SKY13588 RFC -> JP1 U.FL`
- Radio chain B mirrors chain A and exits through `JP2`
- Wi-Fi / service antenna: `AE1 2450AT18A100E`

## Firmware Basis

- ExpressLRS env basis: `Unified_ESP32C3_LR1121_RX_via_UART`
- OTA basis: `Unified_ESP32C3_LR1121_RX_via_WIFI`
- Upstream target basis: `Generic C3 LR1121 True Diversity`

Important firmware note:

- Gemini needs an OpenRX-specific true-diversity / Gemini target entry in the ELRS targets repo
- Gemini needs the final dual-radio pin layout and matching `radio_rfsw_ctrl` definitions

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

Local shared datasheets used by Gemini are present under `datasheets/common/`, including:

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

- Active fitted Gemini schematic has no blank `LCSC` fields
- The main likely `JLCPCB Global Sourcing` parts are:
  - `C2151906` `SKY13588-460LF`
  - `C19842466` `0900PC16J0042001E`
  - `C7498014` `LR1121IMLTRT`

## Release To-Do

- Finish PCB routing / DRC
- Add OpenRX Gemini target entry in the ELRS targets repo
- Verify both radios on the shared SPI bus during bring-up
- Validate symmetric RF performance across both chains
- Run Gemini / Xrossband pre-scan and link validation
