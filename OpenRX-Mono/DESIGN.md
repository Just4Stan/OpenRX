# OpenRX-Mono

Single-LR1121 multi-band receiver. ESP32-C3 + LR1121 + RFX2401C + SKY13414 + Johanson IPD.

## Schematic

- Main sheet: `esp32c3_lr1121_mono.kicad_sch`
- Sub-GHz RX: `LR1121 pins 29-30 → IPD (T1) RX → SKY13414 RF1 → ANT → JP1 U.FL`
- Sub-GHz TX HP: `LR1121 pin 32 → IPD (T1) TX_HP → SKY13414 RF3 → ANT → JP1 U.FL`
- Sub-GHz TX LP: disconnected (IPD TX_LP pin 8 = NC, ELRS never uses LP PA)
- 2.4 GHz path: `LR1121 RFIO_HF → 2450FM07D0034 (USB2) → RFX2401C TXRX → PA/LNA → RFX2401C ANT → C16 0.3pF → SKY13414 RF4 → ANT → JP1 U.FL`
- RF switch control: `DIO7 → V3, DIO8 → V2, V1 → GND`
- RFX2401C control: `DIO5 → RXEN, DIO6 → TXEN`

### SKY13414 Port Mapping (V1=GND)

| DIO7 (V3) | DIO8 (V2) | Port | Path |
|---|---|---|---|
| 0 | 0 | RF1 | Sub-GHz RX (IPD pin 6) |
| 1 | 0 | RF2 | NC |
| 0 | 1 | RF3 | Sub-GHz TX HP (IPD pin 9) |
| 1 | 1 | RF4 | 2.4GHz TX/RX (RFX2401C ANT) |

IPD TX_LP (pin 8) is disconnected — ELRS never uses LP PA on these boards.

### 2450FM07D0034 Impedance Note

Filter pin 1 (chipset side) is 40 ohm, designed for SX1280/SX1281. LR1121 RFIO_HF is 50 ohm. Mismatch gives ~19 dB return loss (VSWR 1.25), only 0.05 dB mismatch loss — negligible. The filter's own internal return loss (14 dB typ) dominates. Keep as-is.

## Firmware

- ELRS target: `Unified_ESP32C3_LR1121_RX`
- Hardware JSON: `/shared/elrs-targets/OpenRX Mono LR1121.json`
- `radio_rfsw_ctrl: [15, 0, 0, 8, 8, 14, 0, 13]` — DIO5=RXEN, DIO6=TXEN, DIO7=V3, DIO8=V2

### rfsw_ctrl Decode

| Index | Mode | Value | Binary | DIO5 | DIO6 | DIO7 | DIO8 |
|---|---|---|---|---|---|---|---|
| 0 | Enable | 15 | 1111 | on | on | on | on |
| 1 | Standby | 0 | 0000 | 0 | 0 | 0 | 0 |
| 2 | SubGHz RX | 0 | 0000 | 0 | 0 | 0 | 0 |
| 3 | SubGHz TX LP | 8 | 1000 | 0 | 0 | 0 | 1 |
| 4 | SubGHz TX HP | 8 | 1000 | 0 | 0 | 0 | 1 |
| 5 | 2.4GHz TX | 14 | 1110 | 0 | 1 | 1 | 1 |
| 6 | unused | 0 | - | - | - | - | - |
| 7 | 2.4GHz RX | 13 | 1101 | 1 | 0 | 1 | 1 |

### GPIO Map

| GPIO | Function | LR1121 Pin |
|---|---|---|
| 1 | IRQ (DIO1) | 24 |
| 2 | RST | 6 |
| 3 | BUSY (DIO0) | 25 |
| 4 | MOSI | via SPI |
| 5 | MISO | via SPI |
| 6 | SCK | via SPI |
| 7 | NSS | via SPI |
| 8 | LED | - |
| 9 | Button | - |

## Flash Interface

- Pads: `5V`, `GND`, `RX`, `TX`
- `BOOT` pad + tactile button on GPIO9
- Hold BOOT/button during power-up for UART download mode
- Use Wi-Fi OTA after first flash

## Sourcing

- `C255353` SKY13414-485LF — 28K LCSC stock
- `C19842466` 0900PC16J0042001E — consign from DigiKey (~$0.49), 0 LCSC stock
- `C7498014` LR1121IMLTRT
- `C2651081` 2450FM07D0034
- `C19213` RFX2401C

## Release To-Do

- Rename USB2 ref designator to FL1
- Finish PCB routing / DRC
- Validate RF path switching and rfsw_ctrl on hardware
- Run CE / RED pre-scan for 2.4 GHz and sub-GHz operation
