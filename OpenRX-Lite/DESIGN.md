# OpenRX-Lite

Final active `2.4 GHz` receiver schematic based on `ESP32-C3 + SX1281`.

## Current Schematic

- Main sheet: `OpenRX-Lite/esp32c3_sx1281_lite.kicad_sch`
- RF chain: `SX1281 -> DEA102700LT-6307A2 -> AE1 2450AT18A100E`
- Main ELRS antenna: `AE1` ceramic antenna, fitted
- Alternate antenna footprint: `AE2 47948-0001`, present as `DNP`

## Firmware Basis

- ExpressLRS env basis: `Unified_ESP32C3_2400_RX_via_UART`
- OTA basis: `Unified_ESP32C3_2400_RX_via_WIFI`
- Upstream target basis: `Generic C3 2400`

## Flash Interface

- `TP1` = `RX`
- `TP2` = `TX`
- `TP3` = `5V`
- `TP4` = `GND`
- `GPIO9` boot strap exists on net `CHIP_BOOT`, but there is no dedicated BOOT test pad in the current schematic

First flash:

- hold `CHIP_BOOT` low during power-up
- flash over `TP1/TP2/TP3/TP4`
- use Wi-Fi OTA after the first successful flash

## Datasheets

Local shared datasheets used by Lite are present under `datasheets/common/`, including:

- `ESP32-C3FH4_datasheet.pdf`
- `SX1281IMLTRT_datasheet.pdf`
- `TLV755P_datasheet.pdf`
- `YXC_OW7EL89CENUNFAYLC-52M_C22434896.pdf`
- `2450AT18A100E_antenna.pdf`
- `CJ17-400001010B20_datasheet.pdf`
- `XL-1010RGBC-WS2812B_datasheet.pdf`

The official `DEA102700LT-6307A2` PDF is still not mirrored locally.

## Sourcing

- Active fitted Lite schematic has no blank `LCSC` fields
- `AE2 / C152351` remains in the schematic as `DNP`
- `C2151551` `SX1281IMLTRT` is the main part to watch for a `1000 pcs` run

## Release To-Do

- Finish PCB routing / DRC
- Add OpenRX Lite target entry in the ELRS targets repo
- Validate SX1281 RF path and ceramic antenna tune on hardware
- Run CE / RED pre-scan for the `2.4 GHz` design
