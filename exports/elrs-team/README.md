# ELRS Review Package

Files:

- `OpenRX-Lite-schematic.pdf`
- `OpenRX-Mono-schematic.pdf`
- `OpenRX-Gemini-schematic.pdf`

## LR1121 DIO Table Source

The Discord screenshot table is coming from Semtech's LR1121 documentation, not from ExpressLRS:

- [LR1121_datasheet.pdf](/Users/stan/Library/Mobile%20Documents/com~apple~CloudDocs/OpenRX/datasheets/common/LR1121_datasheet.pdf)
  - `Table 4-1: LR1121 DIO Mapping`
  - local PDF title: `LR1121_H2_DS_v2_0.pdf`
  - local file metadata shows `35` pages
  - the table maps:
    - `DIO9 -> IRQ`
    - `DIO4 -> SPI MISO`
    - `DIO3 -> SPI MOSI`
    - `DIO2 -> SPI SCK`
    - `DIO1 -> SPI NSS`
    - `DIO0/BUSY -> BUSY`

- [LR1121_user_manual.pdf](/Users/stan/Library/Mobile%20Documents/com~apple~CloudDocs/OpenRX/datasheets/common/LR1121_user_manual.pdf)
  - `Table 4-1: Digital I/Os`
  - local PDF title: `UserManual_LR1121_v1_2.pdf`
  - local file metadata shows `129` pages
  - it states:
    - `DIO1 to DIO4` are the SPI interface signals
    - `DIO9` is dedicated to LR1121 interrupts
    - `DIO11` can be another interrupt pin if the 32.768kHz crystal is not used

## Why This Looks Confusing In ExpressLRS

ExpressLRS uses the hardware key name `radio_dio1`, but for `LR1121` this is just the interrupt line name expected by the firmware, not the physical Semtech `DIO1` pin.

For LR1121 hardware, the correct mapping is:

- ELRS `radio_dio1` -> physical `LR1121 DIO9`
- ELRS `radio_busy` -> physical `LR1121 DIO0/BUSY`
- ELRS `radio_nss` -> physical `LR1121 DIO1`

Relevant local ELRS code:

- [Unified_ESP_RX.h](/Users/stan/Documents/GitHub/ExpressLRS/src/include/target/Unified_ESP_RX.h)
- [LR1121_hal.cpp](/Users/stan/Documents/GitHub/ExpressLRS/src/lib/LR1121Driver/LR1121_hal.cpp)

That matches the Discord explanation from `PK`: the ELRS JSON `DIO1` field is legacy naming for the interrupt signal, so on LR1121 it should be wired to `DIO9/IRQ`, not to the physical `DIO1` pin.
