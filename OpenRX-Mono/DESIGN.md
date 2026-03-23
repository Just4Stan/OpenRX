# OpenRX-Mono — Schematic Design Document

> Release-plan note: `OpenRX-Mono` is the active mainstream single-`LR1121` release project. It was transferred from the former `OpenRX-Dual` concept so the schematic content is preserved while the product stack is simplified.
>
> Audit note: the intended ELRS-compatible architecture for this board is `LR1121 DIO9 -> radio_dio1` and `LR1121 RFSW -> RFX2401C TXEN/RXEN control`. The FEM is driven entirely by LR1121 RFSW pins via `SetDioAsRfSwitch()` — no ESP32 GPIOs are used for FEM control.
>
> BOM note: use [verification/bom/OpenRX-Mono-lcsc.csv](/Users/stan/Library/Mobile%20Documents/com~apple~CloudDocs/OpenRX/verification/bom/OpenRX-Mono-lcsc.csv) for the current fitted part numbers. The preferred Johanson sub-GHz IPD is still the schematic baseline, but its direct LCSC page currently shows `Out of Stock`.

Single-radio multi-band ExpressLRS receiver with optional PA+LNA path.
One `LR1121` covers `868/915MHz` and `2.4GHz` on a single mainstream hardware platform.

## Block Diagram

```
                          +------------------+
                          |   ESP32-C3FH4    |
                          |                  |
  FC UART TX ──────── GPIO20 (RX)            |
  FC UART RX ──────── GPIO21 (TX)            |
                          |    SPI Bus       |
                          | GPIO4  (SCK)  ───────────┐
                          | GPIO7  (MOSI) ───────────┤
                          | GPIO6  (MISO) ───────────┤
                          | GPIO8  (NSS)  ───────────┤
                          | GPIO2  (NRESET) ─────────┤
                          | GPIO3  (BUSY)  ──────────┤
                          | GPIO5  (DIO9)  ──────────┤
                          | GPIO10 (LED)  ── WS2812B |
                          | GPIO9  (BOOT) ── Button  |
                          | GPIO18/19 ── USB pads    |
                          | XTAL_P/N ── 40MHz XTAL   |
                          +------------------+
                                             │
                          +------------------+
                          |     LR1121       |
                          |                  |
                          |  SCK ────────────┘ (shared SPI)
                          |  MOSI ───────────┘
                          |  MISO ───────────┘
                          |  NSS  ───────────┘
                          |  NRESET ─────────┘
                          |  BUSY  ──────────┘
                          |  DIO9  ──────────┘
                          |                  |
                          |  RFSW_0..3 ──┐   |   (internal DIO5-DIO8)
                          |              │   |
                          |  RFI_HF ─────┼── 2.4GHz path ── RFX2401C ── 0.3pF ── UFL
                          |              │                                      │
                          |  RFI_N ──────┼── sub-GHz path ── Balun ──────────── UFL
                          |  RFI_P ──────┘
                          |                  |
                          |  XTA ── 32MHz TCXO (powered from VTCXO pin)
                          +------------------+
```

---

## 1. Power Supply

### 1.1 LDO Regulator — TLV75533PDQNR (LCSC C2861882)

Converts 3.3–5V input from flight controller to clean 3.3V rail.

| Pin | Name | Connection |
|-----|------|------------|
| 1   | VIN  | FC 5V input |
| 2   | GND  | Ground |
| 3   | EN   | Tied to VIN (always enabled) |
| 4   | BP   | 1uF ceramic to GND (noise bypass) |
| 5   | VOUT | 3.3V output rail |

**Decoupling:**
- VIN: 10uF X5R 0402 + 100nF X7R 0402 to GND
- VOUT: 22uF X5R 0603 + 100nF X7R 0402 to GND
- BP: 1uF X7R 0402 to GND

**Notes:**
- 500mA max output, sufficient for ESP32-C3 (~80mA active) + LR1121 (~120mA TX) + RFX2401C (~140mA TX)
- Total worst-case current ~330mA during 2.4GHz TX with PA active
- Thermal pad on X2SON-4 1x1mm connects to GND pour

---

## 2. ESP32-C3FH4 (LCSC C2858491)

QFN-32, 5x5mm. 4MB flash internal. RISC-V single-core 160MHz.

### 2.1 Pin Assignment Table

| Pin | Name     | Function           | Connection                          |
|-----|----------|--------------------|-------------------------------------|
| 1   | GND      | Ground             | GND plane                           |
| 2   | GND      | Ground             | GND plane                           |
| 3   | XTAL_P   | Crystal in         | 40MHz crystal pin 1                 |
| 4   | XTAL_N   | Crystal out        | 40MHz crystal pin 3                 |
| 5   | GPIO2    | Digital I/O        | LR1121 NRESET + 10k pull-up to 3.3V |
| 6   | GPIO3    | Digital I/O        | LR1121 BUSY                         |
| 7   | CHIP_EN  | Enable             | 10k pull-up to 3.3V + 1uF to GND (RC delay) |
| 8   | GPIO0    | Digital I/O        | UART0 TX (debug)                    |
| 9   | GPIO1    | Digital I/O        | UART0 RX (debug)                    |
| 10  | GND      | Ground             | GND plane                           |
| 11  | VDD3P3   | Power              | 3.3V + 100nF                        |
| 12  | VDD3P3   | Power              | 3.3V + 100nF                        |
| 13  | GPIO10   | Digital I/O        | WS2812B LED data in                 |
| 14  | VDD_SPI  | SPI flash power    | 3.3V + 100nF (internal flash)       |
| 15  | GPIO4    | Digital I/O / SPI  | LR1121 SCK                          |
| 16  | GPIO5    | Digital I/O        | LR1121 DIO9 (IRQ)                   |
| 17  | GPIO6    | Digital I/O / SPI  | LR1121 MISO                         |
| 18  | GPIO7    | Digital I/O / SPI  | LR1121 MOSI                         |
| 19  | GPIO8    | Digital I/O / SPI  | LR1121 NSS + 10k pull-up to 3.3V    |
| 20  | GPIO9    | Boot mode          | Boot button to GND + 10k pull-up    |
| 21  | GPIO18   | USB D-             | USB test pad (D-)                   |
| 22  | GPIO19   | USB D+             | USB test pad (D+)                   |
| 23  | GPIO20   | UART1 RX           | FC UART TX                          |
| 24  | GPIO21   | UART1 TX           | FC UART RX                          |
| 25  | GND      | Ground             | GND plane                           |
| 26  | GND      | Ground             | GND plane                           |
| 27  | GND      | Ground             | GND plane                           |
| 28  | GND      | Ground             | GND plane                           |
| 29  | GND      | Ground             | GND plane                           |
| 30  | GND      | Ground             | GND plane                           |
| 31  | GND      | Ground             | GND plane                           |
| 32  | GND      | Ground             | GND plane                           |
| EP  | GND      | Exposed pad        | GND plane (thermal)                 |

### 2.2 Crystal — 40MHz (LCSC C14346 or equivalent)

| Connection | Detail |
|------------|--------|
| XTAL_P (pin 3) | Crystal pin 1 + 10pF load cap to GND |
| XTAL_N (pin 4) | Crystal pin 3 + 10pF load cap to GND |
| Crystal pin 2,4 | GND |

- 3.2x2.5mm SMD crystal, 10pF load, +/-10ppm
- Place within 5mm of ESP32-C3
- Guard ring around crystal connected to GND

### 2.3 Boot & Reset

- **EN (pin 7):** 10k pull-up to 3.3V + 1uF cap to GND. RC time constant ~10ms provides stable power-on reset delay.
- **GPIO9 (pin 20):** Boot button (momentary, NC) to GND. 10k pull-up to 3.3V. Hold LOW during reset to enter download mode.

### 2.4 USB Interface (Test Pads Only)

- GPIO18 → USB D- test pad
- GPIO19 → USB D+ test pad
- No USB connector populated — firmware update via UART or WiFi OTA
- Optional: add 5.1k pull-down on each USB line for USB-C compatibility

### 2.5 UART to Flight Controller

- GPIO20 (RX) ← FC TX (CRSF protocol)
- GPIO21 (TX) → FC RX (CRSF protocol)
- 4-pin connector pad: GND, 5V, TX, RX
- CRSF protocol at 420000 baud (ELRS default)

---

## 3. LR1121IMLTRT Transceiver (LCSC C7498014)

QFN-32, 4x4mm. Multi-band LoRa transceiver: sub-GHz (150-960MHz) + 2.4GHz ISM + S-band.

### 3.1 Pin Assignment Table

| Pin | Name      | Type | Connection                                         |
|-----|-----------|------|------------------------------------------------------|
| 1   | VDD_PERI  | P    | 3.3V + 100nF to GND                                 |
| 2   | VR_PA     | P    | 4.7uF + 100nF to GND (internal PA DC-DC output)     |
| 3   | VDD_IN    | P    | 3.3V + 100nF to GND (main power input)              |
| 4   | GND       | G    | Ground                                               |
| 5   | DIO10     | I/O  | NC (or RFSW_4 if needed, see sec 3.4)               |
| 6   | DIO6      | I/O  | RFSW_1 — RF switch control (see truth table)         |
| 7   | DIO5      | I/O  | RFSW_0 — RF switch control (see truth table)         |
| 8   | DIO8      | I/O  | RFSW_3 — RF switch control (see truth table)         |
| 9   | GND       | G    | Ground                                               |
| 10  | RFIO_HF   | RF   | 2.4GHz RF port → DEA102700LT-6307A2 balun → RFX2401C TXRX |
| 11  | DIO7      | I/O  | RFSW_2 — RF switch control (see truth table)         |
| 12  | RFI_N     | RF   | Sub-GHz differential RF (negative)                   |
| 13  | RFI_P     | RF   | Sub-GHz differential RF (positive)                   |
| 14  | GND       | G    | Ground                                               |
| 15  | RFO_LP_LF | RF   | Sub-GHz low-power PA output (+15dBm) — NC (unused)  |
| 16  | NRESET    | I    | ESP32-C3 GPIO2 + 10k pull-up to 3.3V                |
| 17  | BUSY      | O    | ESP32-C3 GPIO3                                       |
| 18  | GND       | G    | Ground                                               |
| 19  | DIO0      | I/O  | NC                                                   |
| 20  | DIO1      | I/O  | NC                                                   |
| 21  | DIO2      | I/O  | NC                                                   |
| 22  | DIO3      | I/O  | NC                                                   |
| 23  | DIO9      | I/O  | ESP32-C3 GPIO5 (interrupt line)                      |
| 24  | DIO4      | I/O  | NC                                                   |
| 25  | MISO      | O    | ESP32-C3 GPIO6                                       |
| 26  | MOSI      | I    | ESP32-C3 GPIO7                                       |
| 27  | SCK       | I    | ESP32-C3 GPIO4                                       |
| 28  | NSS       | I    | ESP32-C3 GPIO8 + 10k pull-up to 3.3V                |
| 29  | VTCXO     | P    | Internal TCXO regulator output → TCXO VCC pin       |
| 30  | XTA       | I    | 32MHz TCXO output (clipped sine)                     |
| 31  | XTB       | O    | Float (unused when TCXO mode)                        |
| 32  | VDD       | P    | 3.3V + 100nF to GND                                 |
| EP  | GND       | G    | Exposed pad — GND plane (critical thermal path)      |

### 3.2 Power Supply Decoupling

Place all capacitors as close as possible to the LR1121 pins. Use 0402 package.

| Pin | Supply    | Decoupling          | Notes                              |
|-----|-----------|---------------------|------------------------------------|
| 1   | VDD_PERI  | 100nF X7R           | Peripheral digital supply          |
| 2   | VR_PA     | 4.7uF + 100nF X7R   | PA DC-DC output, do NOT connect to 3.3V |
| 3   | VDD_IN    | 100nF X7R           | Main power input                   |
| 32  | VDD       | 100nF X7R           | Core digital supply                |

**CRITICAL:** VR_PA (pin 2) is an OUTPUT from the internal DC-DC converter. Do NOT connect to the 3.3V rail. Connect only bypass capacitors (4.7uF + 100nF) to GND.

### 3.3 TCXO Connection — 32MHz

The LR1121 has an internal TCXO voltage regulator on pin 29 (VTCXO). This powers the external TCXO directly — no separate supply needed.

```
    VTCXO (pin 29) ──── 100nF ──── GND
         │
         └──── TCXO VCC pin
                  │
              32MHz TCXO
              (TYETBCSANF-32.000000 or equivalent)
                  │
              TCXO OUT ──── XTA (pin 30)
                  │
              TCXO GND ──── GND

    XTB (pin 31) ──── Float (no connection)
```

- TCXO voltage: programmable via SetTcxoMode command (1.6V, 1.7V, 1.8V, 2.2V, 2.4V, 2.7V, 3.0V, 3.3V)
- ELRS firmware sets this to 1.8V by default for most designs
- Use TCXO with 1.8V operating voltage, +/-1ppm stability
- Part: TAITIEN TYETBCSANF-32.000000 (LCSC C6732076), 2.8-3.3V — BUT check if 1.8V variant exists
- Alternative: use any 32MHz TCXO with 1.8V VCC, clipped sine output

**IMPORTANT:** If using a 3.3V TCXO, set firmware TCXO voltage to 3.3V. If using a 1.8V TCXO, set to 1.8V. The VTCXO pin voltage must match the TCXO's VCC requirement.

### 3.4 RF Switch Architecture (RFSW) — CRITICAL SECTION

The LR1121 has 5 DIO pins configurable as RF switch control outputs via the `SetDioAsRfSwitch` SPI command (opcode 0x0112). These pins automatically change state based on the radio's operating mode.

**DIO-to-RFSW Mapping (LR1121 QFN-32):**

| LR1121 Pin | DIO Name | RFSW Function | Bit Position |
|------------|----------|---------------|--------------|
| Pin 7      | DIO5     | RFSW_0        | Bit 0        |
| Pin 6      | DIO6     | RFSW_1        | Bit 1        |
| Pin 11     | DIO7     | RFSW_2        | Bit 2        |
| Pin 8      | DIO8     | RFSW_3        | Bit 3        |
| Pin 5      | DIO10    | RFSW_4        | Bit 4        |

**SetDioAsRfSwitch Command (8 bytes):**

```
Byte 0: RfswEnable    — bitmask of which DIO pins to enable as RFSW
Byte 1: RfSwStbyCfg   — pin states in STANDBY mode
Byte 2: RfSwRxCfg     — pin states in RX mode (sub-GHz RX)
Byte 3: RfSwTxCfg     — pin states in TX_LP mode (sub-GHz low power)
Byte 4: RfSwTxHPCfg   — pin states in TX_HP mode (sub-GHz high power)
Byte 5: RfSwTxHfCfg   — pin states in TX_HF mode (2.4GHz TX)
Byte 6: Reserved       — unused (set to 0)
Byte 7: RfSwWifiCfg   — pin states in WIFI/RX_HF mode (2.4GHz RX)
```

Each byte is a bitmask where bit N corresponds to RFSW_N (DIO5+N).

**ELRS Default Configuration:**

```
switchbuf[0] = 0b00001111  // Enable RFSW_0..3 (DIO5,6,7,8)
switchbuf[1] = 0b00000000  // STANDBY: all low
switchbuf[2] = 0b00000100  // RX (sub-GHz): RFSW_2=HIGH
switchbuf[3] = 0b00001000  // TX_LP:  RFSW_3=HIGH
switchbuf[4] = 0b00001000  // TX_HP:  RFSW_3=HIGH
switchbuf[5] = 0b00000010  // TX_HF:  RFSW_1=HIGH (2.4GHz TX)
switchbuf[6] = 0b00000000  // Reserved
switchbuf[7] = 0b00000001  // WIFI/RX_HF: RFSW_0=HIGH (2.4GHz RX)
```

**Truth Table (Default ELRS Config):**

| Radio Mode     | RFSW_0 (DIO5) | RFSW_1 (DIO6) | RFSW_2 (DIO7) | RFSW_3 (DIO8) | RF Path Active      |
|----------------|:-:|:-:|:-:|:-:|---------------------|
| Standby        | 0 | 0 | 0 | 0 | None                |
| Sub-GHz RX     | 0 | 0 | 1 | 0 | RFI_N/P → antenna   |
| Sub-GHz TX LP  | 0 | 0 | 0 | 1 | RFO_LP → antenna    |
| Sub-GHz TX HP  | 0 | 0 | 0 | 1 | RFO_HP → antenna    |
| 2.4GHz TX      | 0 | 1 | 0 | 0 | RFIO_HF → RFX2401C TX |
| 2.4GHz RX      | 1 | 0 | 0 | 0 | RFX2401C RX → RFIO_HF |

**Custom RFSW Config (radio_rfsw_ctrl in targets.json):**

ELRS targets can override defaults via `radio_rfsw_ctrl` array (8 elements matching the 8-byte command). Example from BAYCKRC: `[31,0,4,8,8,18,0,17]`.

For this design, connect RFSW pins to RFX2401C as follows:

### 3.5 RFX2401C Control via RFSW

The RFX2401C has two control inputs: TXEN and RXEN. These are driven from the LR1121 RFSW outputs via `SetDioAsRfSwitch()` to switch the 2.4GHz FEM between TX, RX, and sleep modes automatically based on radio state.

**RFX2401C Control Truth Table:**

| TXEN | RXEN | Mode         | Current |
|:----:|:----:|--------------|---------|
| 0    | 0    | Sleep        | ~2uA    |
| 0    | 1    | RX (LNA on)  | ~7mA    |
| 1    | 0    | TX (PA on)   | ~140mA  |
| 1    | 1    | Invalid      | —       |

**RFSW-to-RFX2401C Mapping for this design:**

```
LR1121 DIO6 (pin 6, RFSW_1) ──── RFX2401C TXEN
LR1121 DIO5 (pin 7, RFSW_0) ──── RFX2401C RXEN
```

This works with the ELRS default configuration:
- 2.4GHz TX: RFSW_1=HIGH → TXEN=HIGH, RFSW_0=LOW → RXEN=LOW → PA mode
- 2.4GHz RX: RFSW_0=HIGH → RXEN=HIGH, RFSW_1=LOW → TXEN=LOW → LNA mode
- Sub-GHz modes: RFSW_0=LOW, RFSW_1=LOW → RFX2401C in sleep (saves power)
- Standby: RFSW_0=LOW, RFSW_1=LOW → RFX2401C in sleep

**No ESP32-C3 GPIOs used for FEM control.** The LR1121 handles it entirely via RFSW pins and `SetDioAsRfSwitch()`.

### 3.6 Sub-GHz RF Path (868/915MHz)

The LR1121 outputs a differential signal on RFI_N (pin 12) and RFI_P (pin 13). This needs a balun to convert to 50-ohm single-ended for the antenna connector.

```
LR1121 RFI_P (pin 13) ──┬── C_MATCH (0.5pF) ──┐
                         │                      ├── Balun ── 50Ω ── UFL (sub-GHz)
LR1121 RFI_N (pin 12) ──┴── C_MATCH (0.5pF) ──┘
                                                    │
                                              GND ──┘
```

**Balun Options:**

1. **Johanson 0900PC16J0042001E (preferred):** LR11xx-specific integrated passive device for 863-870MHz and 902-928MHz. It exposes dedicated `RX`, `TX_LP`, and `TX_HP` ports and directly matches the LR1121 `RFI_P/N_LF0`, `RFO_LP_LF`, and `RFO_HP_LF` pins. This is the cleanest CE-oriented choice.

2. **Discrete balun / match:** Use a Semtech-style LC network only as a fallback if the Johanson IPD is unavailable. It will require tuning on the real PCB.

**Matching Network (if using discrete components):**

Follow Semtech AN1200.40 (LR11xx RF matching application note). Typical values:
- Series C: 0.5pF (0402 NP0)
- Shunt L: 6.8nH (0402)
- Series L: 3.3nH (0402)

**No external LNA on sub-GHz path** — cost optimization. The LR1121 internal LNA is sufficient for ELRS at close/medium range. The RX sensitivity is approximately -140dBm for LoRa, which is already excellent.

### 3.7 2.4GHz RF Path

```
LR1121 RFIO_HF (pin 10) ── DEA102700LT-6307A2 (C574024) ── RFX2401C TXRX
                                                                    │
                                                             RFX2401C ANT ── 0.3pF shunt to GND ── UFL (2.4GHz)
```

**RFIO_HF to RFX2401C:**

The DEA102700LT-6307A2 (LCSC C574024) is a 2.4GHz balun/matching network between the LR1121 RFIO_HF output and the RFX2401C TXRX pin. Both ports are nominally 50-ohm.

**Mandatory 0.3pF shunt cap on ANT output:**

A 0.3pF cap to GND on the RFX2401C ANT pin is mandatory per the RFX2401C datasheet. This provides 5th harmonic rejection and is required for regulatory compliance.

```
RFX2401C ANT ── 0.3pF (C0G/NP0, 0402) ── GND
      │
   50Ω trace ── UFL connector (2.4GHz)
```

---

## 4. RFX2401C Front-End Module (LCSC C19213)

QFN-16, 3x3mm. 2.4GHz LNA+PA integrated front-end module. Simpler than SE2431L — fewer pins, TXEN/RXEN control, single ANT pin.

### 4.1 Pin Assignment Table

| Pin | Name    | Connection                                              |
|-----|---------|----------------------------------------------------------|
| 1   | VDD     | 3.3V + 1uF + 100nF to GND                               |
| 2   | GND     | Ground                                                    |
| 3   | TXRX    | DEA102700LT-6307A2 balun → LR1121 RFIO_HF (pin 10)     |
| 4   | GND     | Ground                                                    |
| 5   | ANT     | 0.3pF shunt to GND → 50Ω trace → 2.4GHz UFL connector  |
| 6   | GND     | Ground                                                    |
| 7   | GND     | Ground                                                    |
| 8   | GND     | Ground                                                    |
| 9   | GND     | Ground                                                    |
| 10  | GND     | Ground                                                    |
| 11  | RXEN    | LR1121 DIO5 (pin 7, RFSW_0)                              |
| 12  | TXEN    | LR1121 DIO6 (pin 6, RFSW_1)                              |
| 13  | GND     | Ground                                                    |
| 14  | GND     | Ground                                                    |
| 15  | GND     | Ground                                                    |
| 16  | GND     | Ground                                                    |
| EP  | GND     | Exposed pad — GND plane (critical for RF ground)          |

### 4.2 RFX2401C Performance

| Parameter        | Value       |
|------------------|-------------|
| TX output power  | +22dBm typ  |
| TX current       | ~140mA      |
| RX gain (LNA)    | +11dB typ   |
| RX noise figure  | 2.5dB typ   |
| RX current (LNA) | ~7mA        |
| Frequency range  | 2.4-2.5GHz  |
| Supply voltage   | 3.0-3.6V    |

### 4.3 Mandatory 0.3pF Harmonic Filter (After RFX2401C ANT pin)

A 0.3pF shunt capacitor to GND is mandatory on the RFX2401C ANT output per the datasheet. This provides 5th harmonic rejection required for regulatory compliance. No external SAW filter is needed.

```
RFX2401C ANT (pin 5) ── 0.3pF (C0G/NP0, 0402) to GND ── 50Ω trace ── UFL connector
```

---

## 5. Antenna Connectors

Two UFL/IPEX-1 connectors, one for each band.

### 5.1 Sub-GHz Antenna (868/915MHz)
- UFL connector: Hirose U.FL-R-SMT-1(10) (LCSC C88373) or equivalent
- Connected to balun output (50-ohm single-ended)
- Place at board edge

### 5.2 2.4GHz Antenna
- UFL connector: Hirose U.FL-R-SMT-1(10) (LCSC C88373) or equivalent
- Connected to RFX2401C ANT output via 0.3pF shunt cap (50-ohm)
- Place at board edge, opposite side from sub-GHz connector

**RF Trace Requirements:**
- 50-ohm controlled impedance microstrip
- 4-layer stackup: Signal-GND-GND-Signal (or Signal-GND-Power-Signal)
- JLCPCB 4-layer 1.0mm: ~0.22mm trace width for 50-ohm on top layer over ground
- Keep RF traces short, no vias in RF path, ground stitching vias alongside traces

---

## 6. WS2812B Status LED (LCSC C5349953)

XL-1010RGBC-WS2812B (2x2mm addressable RGB LED).

| Pin | Name | Connection |
|-----|------|------------|
| 1   | VDD  | 5V from FC input (before LDO) OR 3.3V with reduced brightness |
| 2   | DOUT | NC (single LED, no chain) |
| 3   | GND  | Ground |
| 4   | DIN  | ESP32-C3 GPIO10 via 330R series resistor |

**Decoupling:** 100nF ceramic cap across VDD-GND, placed adjacent to LED.

**Note:** WS2812B nominally requires 5V VDD but works at 3.3V with reduced brightness. For reliable operation from 3.3V logic, the series resistor on DIN helps with signal integrity. If VDD is 5V, the 3.3V GPIO output is marginal for logic HIGH (need VIH > 0.7*VDD = 3.5V). Options:
1. Power LED from 3.3V (simplest, reduced brightness is acceptable for status LED)
2. Add level shifter (adds cost/complexity)
3. Use SK6805-EC20 which works reliably at 3.3V

---

## 7. Boot Button

Momentary push button on GPIO9.

```
GPIO9 ── 10k pull-up to 3.3V
  │
  └── Button (NO) ── GND
```

Hold during power-on/reset to enter ESP32-C3 download mode for firmware flashing.

---

## 8. FC Connection Pads

4 pads for soldering to flight controller:

| Pad | Signal | Notes |
|-----|--------|-------|
| 1   | GND    | Ground reference |
| 2   | 5V     | Power input (3.3-5V accepted) |
| 3   | TX     | ESP32-C3 GPIO21 → FC RX (CRSF) |
| 4   | RX     | ESP32-C3 GPIO20 ← FC TX (CRSF) |

---

## 9. SPI Bus (ESP32-C3 ↔ LR1121)

| Signal  | ESP32-C3 | LR1121   | Notes                    |
|---------|----------|----------|--------------------------|
| SCK     | GPIO4    | Pin 27   | SPI clock                |
| MOSI    | GPIO7    | Pin 26   | Master out, slave in     |
| MISO    | GPIO6    | Pin 25   | Master in, slave out     |
| NSS     | GPIO8    | Pin 28   | Chip select, active LOW  |
| NRESET  | GPIO2    | Pin 16   | Reset, active LOW        |
| BUSY    | GPIO3    | Pin 17   | Radio busy indicator     |
| DIO9    | GPIO5    | Pin 23   | Interrupt (packet ready) |

- NSS: 10k pull-up to 3.3V (keeps LR1121 deselected during ESP32 boot)
- NRESET: 10k pull-up to 3.3V (prevents spurious reset)
- SPI clock: up to 16MHz
- Place bypass caps on all LR1121 power pins before routing SPI

---

## 10. PCB Design Notes

### 10.1 Layer Stackup (JLCPCB 4-layer, 1.0mm)

| Layer | Function | Thickness |
|-------|----------|-----------|
| L1    | Signal + RF traces | 0.035mm Cu |
| L2    | GND plane (continuous) | 0.035mm Cu |
| L3    | Power plane (3.3V) | 0.035mm Cu |
| L4    | Signal + component pads | 0.035mm Cu |

Prepreg/core: ~0.2mm / 0.4mm / 0.2mm (JLCPCB JLC04161H-1080 stackup)

### 10.2 Critical Layout Rules

1. **Continuous GND plane on L2** — no splits, no routing on L2
2. **50-ohm RF traces** on L1 only, calculated for stackup (~0.22mm width)
3. **Ground stitching vias** along RF traces, spaced < lambda/20 (~3mm for 2.4GHz)
4. **Component placement priority:** LR1121 center, RFX2401C adjacent, UFL connectors at edges
5. **Decoupling caps** within 1mm of IC power pins
6. **Keep ESP32-C3 crystal** away from RF traces and LR1121
7. **Thermal relief** on LR1121 and RFX2401C exposed pads — multiple vias to L2 GND

### 10.3 Board Dimensions

- 22mm x 15mm, 1.0mm thickness
- Weight target: < 1g
- Mounting: solder pads for direct FC mounting

---

## 11. ELRS Firmware Configuration

### 11.1 Target JSON (for ExpressLRS/targets repo)

```json
{
  "firmware": "LR1121",
  "platform": "esp32-c3",
  "radio_chip": "lr1121",
  "radio_dcdc": true,
  "radio_miso": 6,
  "radio_mosi": 7,
  "radio_sck": 4,
  "radio_nss": 8,
  "radio_rst": 2,
  "radio_busy": 3,
  "radio_dio1": 5,
  "radio_rfsw_ctrl": [15, 0, 4, 8, 8, 2, 0, 1],
  "power_values": [12, 16, 19, 22],
  "power_values_dual": [-12, -9, -6, -2],
  "power_lna_gain": 12,
  "button": 9,
  "led_rgb": 10,
  "led_rgb_isgrb": true,
  "serial_rx": 20,
  "serial_tx": 21
}
```

### 11.2 radio_rfsw_ctrl Breakdown

```
[15, 0, 4, 8, 8, 2, 0, 1]
  │   │  │  │  │  │  │  └── Byte 7: RfSwWifiCfg (2.4GHz RX) = 0b00000001 → RFSW_0=HIGH
  │   │  │  │  │  │  └───── Byte 6: Reserved = 0
  │   │  │  │  │  └──────── Byte 5: RfSwTxHfCfg (2.4GHz TX) = 0b00000010 → RFSW_1=HIGH
  │   │  │  │  └─────────── Byte 4: RfSwTxHPCfg (sub-GHz TX HP) = 0b00001000 → RFSW_3=HIGH
  │   │  │  └──────────────  Byte 3: RfSwTxCfg (sub-GHz TX LP) = 0b00001000 → RFSW_3=HIGH
  │   │  └───────────────── Byte 2: RfSwRxCfg (sub-GHz RX) = 0b00000100 → RFSW_2=HIGH
  │   └──────────────────── Byte 1: RfSwStbyCfg = 0b00000000 → all LOW
  └─────────────────────── Byte 0: RfswEnable = 0b00001111 → RFSW_0..3 enabled
```

This maps to:
- **2.4GHz RX:** RFSW_0=HIGH → RFX2401C RXEN=HIGH → LNA active
- **2.4GHz TX:** RFSW_1=HIGH → RFX2401C TXEN=HIGH → PA active
- **Sub-GHz RX:** RFSW_2=HIGH → sub-GHz antenna path to RFI_N/P
- **Sub-GHz TX:** RFSW_3=HIGH → sub-GHz antenna path from RFO

---

## 12. Schematic Checklist

- [ ] All LR1121 GND pins (4, 9, 14, 18, EP) connected to ground plane
- [ ] VR_PA decoupled but NOT connected to 3.3V rail
- [ ] TCXO powered from VTCXO pin, output to XTA, XTB floating
- [ ] RFX2401C TXEN/RXEN driven by LR1121 RFSW (no extra GPIOs)
- [ ] 0.3pF shunt cap on RFX2401C ANT pin (mandatory 5th harmonic rejection)
- [ ] Sub-GHz balun between LR1121 differential and UFL
- [ ] ESP32-C3 EN pin RC delay (10k + 1uF)
- [ ] Boot button on GPIO9 with pull-up
- [ ] NSS and NRESET pull-ups (10k each)
- [ ] All power pins decoupled with 100nF minimum
- [ ] USB test pads on GPIO18/19
- [ ] FC UART on GPIO20/21
- [ ] WS2812B on GPIO10 with series resistor

---

# OpenRX-Mono — Bill of Materials

> BOM uses RFX2401C (C19213, $0.51) as the 2.4GHz FEM. Saves $1.38/unit vs SE2431L.

Target BOM cost: EUR 7-9 at production quantities (100+ units).
All parts sourced from LCSC for JLCPCB assembly compatibility.

## Active Components

| Ref | Part | MPN | LCSC | Package | Qty | Unit Price (USD) | Notes |
|-----|------|-----|------|---------|-----|-----------------|-------|
| U1 | MCU | ESP32-C3FH4 | C2858491 | QFN-32 (5x5mm) | 1 | ~$1.50 | RISC-V, 4MB flash internal |
| U2 | RF Transceiver | LR1121IMLTRT | C7498014 | QFN-32 (4x4mm) | 1 | ~$3.20 | Sub-GHz + 2.4GHz LoRa |
| U3 | 2.4GHz FEM | RFX2401C | C19213 | QFN-16 (3x3mm) | 1 | ~$0.51 | LNA+PA, TXEN/RXEN control |
| U4 | LDO 3.3V | TLV75533PDQNR | C2861882 | X2SON-4 1x1mm | 1 | ~$0.04 | 500mA, 3.3V output |
| D1 | LED | XL-1010RGBC-WS2812B | C5349953 | 1010 (1x1mm) | 1 | ~$0.04 | Addressable RGB |

## RF / Frequency Components

| Ref | Part | MPN | LCSC | Package | Qty | Unit Price (USD) | Notes |
|-----|------|-----|------|---------|-----|-----------------|-------|
| Y1 | 40MHz Crystal | — | C14346 | 3.2x2.5mm | 1 | ~$0.08 | 10pF load, for ESP32-C3 |
| Y2 | 32MHz TCXO | OW2EL89CENUXFMYLC-32M (YXC) | C22434888 | 3.2x2.5mm | 1 | ~$0.90 | Peak-shaving sine, 3.3V, +/-2.5ppm. Set VTCXO=3.3V in firmware |
| B1 | 2.4GHz Balun | DEA102700LT-6307A2 | C574024 | SMD | 1 | ~$0.10 | RFIO_HF to RFX2401C TXRX matching |
| T1 | Sub-GHz LR11xx IPD | 0900PC16J0042001E | C19842466 | 2.0x1.6mm 10-pad | 1 | ~$0.96 | Johanson LR1110/LR1120/LR1121 integrated balun + filter. Preferred OpenRX baseline. |

**Balun Alternatives (LCSC):**
- Preferred: `0900PC16J0042001E / C19842466`
- Current direct-page status: `C19842466` is showing `Out of Stock` on LCSC as of 2026-03-23
- If that part goes out of stock, use the discrete Semtech-style RF network rather than a random wideband 50:100 balun
- Older generic 868/915MHz Johanson baluns are not as attractive here because they are not LR11xx-specific and LCSC stock is worse

## Connectors

| Ref | Part | MPN | LCSC | Package | Qty | Unit Price (USD) | Notes |
|-----|------|-----|------|---------|-----|-----------------|-------|
| J1 | UFL Connector (sub-GHz) | U.FL-R-SMT-1(10) | C88373 | SMD | 1 | ~$0.20 | Hirose, 50-ohm, IPEX-1 |
| J2 | UFL Connector (2.4GHz) | U.FL-R-SMT-1(10) | C88373 | SMD | 1 | ~$0.20 | Hirose, 50-ohm, IPEX-1 |

## Passive Components — Capacitors

All ceramic, X7R or X5R dielectric unless noted. 0402 (1005 metric) default.

| Ref | Value | Voltage | Package | Qty | LCSC | Notes |
|-----|-------|---------|---------|-----|------|-------|
| C1 | 10uF | 10V X5R | 0402 | 1 | C15525 | LDO VIN bypass |
| C2 | 100nF | 16V X7R | 0402 | 11 | C1525 | General decoupling (LDO VIN, VOUT, ESP32 VDD x3, LR1121 VDD_PERI, VDD_IN, VDD, VTCXO, RFX2401C VDD, WS2812B) |
| C3 | 22uF | 10V X5R | 0603 | 1 | C59461 | LDO VOUT bulk |
| C4 | 1uF | 16V X7R | 0402 | 3 | C52923 | LDO BP, EN RC delay, RFX2401C VDD bulk |
| C5 | 4.7uF | 10V X7R | 0402 | 1 | C368816 | LR1121 VR_PA bypass |
| C6 | 10pF | 50V C0G/NP0 | 0402 | 2 | C32949 | Crystal load caps (ESP32-C3) |
| C7 | 0.5pF | 50V C0G/NP0 | 0402 | 2 | — | Sub-GHz matching (may not be needed with integrated balun) |
| C8 | 1pF | 50V C0G/NP0 | 0402 | 1 | — | 2.4GHz matching (pi-network, if needed) |
| C9 | 0.3pF | 50V C0G/NP0 | 0402 | 1 | — | RFX2401C ANT shunt to GND (mandatory 5th harmonic rejection) |

**Total capacitor count:** ~24 (some values share BOM lines)

## Passive Components — Resistors

All 0402, 1% tolerance.

| Ref | Value | Package | Qty | LCSC | Notes |
|-----|-------|---------|-----|------|-------|
| R1 | 10k | 0402 | 4 | C25744 | Pull-ups: ESP32 EN, LR1121 NRESET, LR1121 NSS, GPIO9 boot |
| R2 | 330R | 0402 | 1 | C25100 | Series resistor for WS2812B DIN |

## Passive Components — Inductors (RF Matching)

| Ref | Value | Package | Qty | LCSC | Notes |
|-----|-------|---------|-----|------|-------|
| L1 | 1.2nH | 0402 | 1 | — | 2.4GHz pi-match (if needed) |

**Note:** RF matching inductors may not be needed if using integrated balun and direct 50-ohm connections. Populate during RF tuning on prototype. Reserve pads in layout.

## Mechanical

| Ref | Part | Qty | Notes |
|-----|------|-----|-------|
| SW1 | Tactile Button | 1 | Boot button, 3x4mm SMD or smaller |
| — | PCB | 1 | 22x15mm, 4-layer, 1.0mm, ENIG finish |
| — | Sub-GHz antenna pigtail | 1 | UFL to SMA or dipole (not on BOM, user-supplied) |
| — | 2.4GHz antenna pigtail | 1 | UFL to SMA or T-antenna (not on BOM, user-supplied) |

---

## BOM Cost Estimate (per unit, 100+ qty)

| Category | Estimated Cost (USD) |
|----------|---------------------|
| ESP32-C3FH4 | $1.50 |
| LR1121IMLTRT | $3.20 |
| RFX2401C | $0.51 |
| TLV75533PDQNR (LDO) | $0.04 |
| 32MHz TCXO | $0.90 |
| 40MHz Crystal | $0.08 |
| 2.4GHz Balun (DEA) | $0.10 |
| Sub-GHz Balun | $0.50 |
| UFL Connectors (x2) | $0.40 |
| WS2812B LED | $0.04 |
| Passives (caps, resistors) | $0.30 |
| Boot Button | $0.05 |
| **Component Total** | **~$7.62** |
| PCB (JLCPCB, qty 100) | ~$0.50/board |
| JLCPCB Assembly | ~$2-3/board |
| **Total Landed Cost** | **~$10-11** |

### Cost Notes

- LR1121 is the most expensive component at ~$3.20. Volume pricing (1000+) may bring this to ~$2.50.
- RFX2401C at ~$0.51 saves $1.38/unit vs SE2431L ($1.89). Simpler QFN-16 package, fewer pins, same RF performance.
- Target EUR 7-9 BOM is achievable at 1000+ quantity with aggressive LCSC pricing.
- Competition: RadioMaster XR3 retails at $29.99. At ~$10-11 landed cost, we achieve ~65% cost reduction.

---

## LCSC Part Availability Notes

| Component | LCSC Status | Alternative |
|-----------|-------------|-------------|
| ESP32-C3FH4 (C2858491) | In stock | ESP32-C3 (C2838500) — needs external flash |
| LR1121IMLTRT (C7498014) | Verify stock | Source from Mouser/DigiKey if needed |
| RFX2401C (C19213) | In stock | QFN-16 3x3mm, $0.51 |
| TLV75533PDQNR (C2861882) | In stock (basic part) | AP2112K-3.3 or similar |
| XL-1010RGBC-WS2812B (C5349953) | In stock | SK6805-EC20 (better 3.3V compat) |
| 32MHz TCXO (C22434888) | Verify stock | Any 32MHz TCXO, match VTCXO voltage |
| DEA102700LT-6307A2 (C574024) | Verify stock | 2.4GHz balun for RFIO_HF to RFX2401C |
| UFL Connector (C88373) | In stock | C434812 or generic IPEX-1 |
| Sub-GHz Balun | NOT on LCSC | Johanson 0900BM15A0001 from DigiKey; or discrete LC |

---

## JLCPCB Assembly Classification

| Part | JLCPCB Type | Setup Fee |
|------|-------------|-----------|
| TLV75533PDQNR | Basic | None |
| 0402 Resistors | Basic | None |
| 0402 Capacitors | Basic | None |
| ESP32-C3FH4 | Extended | $3/part type |
| LR1121IMLTRT | Extended | $3/part type |
| RFX2401C | Extended | $3/part type |
| XL-1010RGBC-WS2812B | Extended | $3/part type |
| 32MHz TCXO | Extended | $3/part type |
| DEA102700LT-6307A2 | Extended | $3/part type |
| UFL Connectors | Extended | $3/part type |

Extended parts: 7 types x $3 = $21 setup fee (one-time per order, amortized across quantity).
At 100 boards: $0.21/board setup overhead.

---

## easyeda2kicad Import List

Components to import into project-local library:

```
C2858491  # ESP32-C3FH4
C7498014  # LR1121IMLTRT
C19213    # RFX2401C
C2861882    # TLV75533PDQNR
C5349953   # XL-1010RGBC-WS2812B
C22434888 # 32MHz TCXO (YXC OW2EL89CENUXFMYLC-32M)
C574024   # DEA102700LT-6307A2 (2.4GHz balun)
C88373    # U.FL-R-SMT-1(10)
```
