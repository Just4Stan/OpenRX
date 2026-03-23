# OpenRX-Dual — Schematic Design Document

Dual-band switchable ExpressLRS receiver with PA+LNA.
868/915MHz AND 2.4GHz via single LR1121 transceiver, firmware-selectable band.

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
                          |  RFI_HF ─────┼── 2.4GHz path ── SE2431L ── SAW ── UFL
                          |              │                                      │
                          |  RFI_N ──────┼── sub-GHz path ── Balun ──────────── UFL
                          |  RFI_P ──────┘
                          |                  |
                          |  XTA ── 32MHz TCXO (powered from VTCXO pin)
                          +------------------+
```

---

## 1. Power Supply

### 1.1 LDO Regulator — ME6211C33M5G-N (LCSC C82942)

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
- 500mA max output, sufficient for ESP32-C3 (~80mA active) + LR1121 (~120mA TX) + SE2431L (~130mA TX)
- Total worst-case current ~330mA during 2.4GHz TX with PA active
- Thermal pad on SOT-23-5 connects to GND pour

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
| 8   | GPIO0    | Digital I/O        | UART0 TX (debug / SE2431L RXEN)     |
| 9   | GPIO1    | Digital I/O        | UART0 RX (debug / SE2431L TXEN)     |
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
| 10  | RFIO_HF   | RF   | 2.4GHz RF port → matching network → SE2431L RF_IN   |
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
| 2.4GHz TX      | 0 | 1 | 0 | 0 | RFIO_HF → SE2431L TX |
| 2.4GHz RX      | 1 | 0 | 0 | 0 | SE2431L RX → RFIO_HF |

**Custom RFSW Config (radio_rfsw_ctrl in targets.json):**

ELRS targets can override defaults via `radio_rfsw_ctrl` array (8 elements matching the 8-byte command). Example from BAYCKRC: `[31,0,4,8,8,18,0,17]`.

For this design, connect RFSW pins to SE2431L as follows:

### 3.5 SE2431L Control via RFSW

The SE2431L has two control inputs: TXEN and RXEN. These need to be driven from the LR1121 RFSW outputs to switch the 2.4GHz FEM between TX, RX, and bypass/sleep modes.

**SE2431L Control Truth Table:**

| TXEN | RXEN | Mode         | Current |
|:----:|:----:|--------------|---------|
| 0    | 0    | Sleep/bypass | ~2uA    |
| 0    | 1    | RX (LNA on)  | ~5mA    |
| 1    | 0    | TX (PA on)   | ~130mA  |
| 1    | 1    | Invalid      | —       |

**RFSW-to-SE2431L Mapping for this design:**

```
LR1121 DIO6 (pin 6, RFSW_1) ──── SE2431L TXEN (pin 4)
LR1121 DIO5 (pin 7, RFSW_0) ──── SE2431L RXEN (pin 5)
```

This works with the ELRS default configuration:
- 2.4GHz TX: RFSW_1=HIGH → TXEN=HIGH, RFSW_0=LOW → RXEN=LOW → PA mode
- 2.4GHz RX: RFSW_0=HIGH → RXEN=HIGH, RFSW_1=LOW → TXEN=LOW → LNA mode
- Sub-GHz modes: RFSW_0=LOW, RFSW_1=LOW → SE2431L in sleep (saves power)
- Standby: RFSW_0=LOW, RFSW_1=LOW → SE2431L in sleep

**No extra ESP32-C3 GPIOs needed for SE2431L control.** The LR1121 handles it automatically via RFSW.

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

1. **Johanson 0900BM15A0001 (preferred):** Integrated balun for 868/915MHz, 0805 package. Converts differential to 50-ohm single-ended. No external matching components needed.

2. **Discrete balun:** Use 3-element LC matching network (requires tuning). Not recommended for production.

**Matching Network (if using discrete components):**

Follow Semtech AN1200.40 (LR11xx RF matching application note). Typical values:
- Series C: 0.5pF (0402 NP0)
- Shunt L: 6.8nH (0402)
- Series L: 3.3nH (0402)

**No external LNA on sub-GHz path** — cost optimization. The LR1121 internal LNA is sufficient for ELRS at close/medium range. The RX sensitivity is approximately -140dBm for LoRa, which is already excellent.

### 3.7 2.4GHz RF Path

```
LR1121 RFIO_HF (pin 10) ── π-match ── SE2431L RF_IN (pin 7)
                                              │
                                       SE2431L ANT (pin 1) ── SAW filter ── UFL (2.4GHz)
```

**RFIO_HF Matching Network:**

Pi-network between LR1121 RFIO_HF and SE2431L RF_IN:

```
RFIO_HF ── Series C (1pF) ── node ── Series L (1.2nH) ── RF_IN
                               │
                          Shunt C (0.5pF)
                               │
                              GND
```

Component values are approximate — tune on VNA during prototyping. Both LR1121 RFIO_HF and SE2431L RF_IN are nominally 50-ohm, so minimal matching may be needed. Start with direct connection + series DC block cap (100pF).

---

## 4. SE2431L-R Front-End Module (LCSC C2649471)

QFN-24-EP, 3x4mm. 2.4GHz LNA+PA integrated front-end module.

### 4.1 Pin Assignment Table

| Pin | Name    | Connection                                       |
|-----|---------|--------------------------------------------------|
| 1   | ANT     | 50Ω trace → SAW filter → 2.4GHz UFL connector   |
| 2   | GND     | Ground                                            |
| 3   | VDD_PA  | 3.3V + 1uF + 100nF to GND                        |
| 4   | TXEN    | LR1121 DIO6 (pin 6, RFSW_1)                      |
| 5   | RXEN    | LR1121 DIO5 (pin 7, RFSW_0)                      |
| 6   | CSD     | NC (chip shutdown, internal pull-up — active HIGH)|
| 7   | RF_IN   | LR1121 RFIO_HF (pin 10) via matching network     |
| 8   | GND     | Ground                                            |
| 9   | VDD_LNA | 3.3V + 100nF to GND                              |
| 10  | GND     | Ground                                            |
| 11  | GND     | Ground                                            |
| 12  | GND     | Ground                                            |
| 13  | GND     | Ground                                            |
| 14  | GND     | Ground                                            |
| 15  | GND     | Ground                                            |
| 16  | GND     | Ground                                            |
| 17  | GND     | Ground                                            |
| 18  | GND     | Ground                                            |
| 19  | GND     | Ground                                            |
| 20  | GND     | Ground                                            |
| 21  | GND     | Ground                                            |
| 22  | GND     | Ground                                            |
| 23  | GND     | Ground                                            |
| 24  | GND     | Ground                                            |
| EP  | GND     | Exposed pad — GND plane (critical for RF ground)  |

### 4.2 SE2431L Performance

| Parameter        | Value       |
|------------------|-------------|
| TX output power  | +22dBm typ  |
| TX current       | ~130mA      |
| RX gain (LNA)    | +11dB typ   |
| RX noise figure  | 2.5dB typ   |
| RX current (LNA) | ~5mA        |
| Frequency range  | 2.4-2.5GHz  |
| Supply voltage   | 1.8-3.6V    |

### 4.3 SAW Filter (After SE2431L ANT pin)

Place a 2.4GHz bandpass SAW filter between SE2431L ANT output and the UFL connector. This rejects out-of-band interference and harmonics.

**Part:** HUAYING NDFH024-2442SA (LCSC C312144)
- Center frequency: 2442MHz
- Bandwidth: 2403-2480MHz (77MHz BW)
- Insertion loss: 1.2-2.2dB typical
- Package: small SMD

```
SE2431L ANT (pin 1) ── 50Ω trace ── SAW filter ── 50Ω trace ── UFL connector
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
- Connected to SAW filter output (50-ohm)
- Place at board edge, opposite side from sub-GHz connector

**RF Trace Requirements:**
- 50-ohm controlled impedance microstrip
- 4-layer stackup: Signal-GND-GND-Signal (or Signal-GND-Power-Signal)
- JLCPCB 4-layer 1.0mm: ~0.22mm trace width for 50-ohm on top layer over ground
- Keep RF traces short, no vias in RF path, ground stitching vias alongside traces

---

## 6. WS2812B Status LED (LCSC C965555)

WS2812B-2020 (2x2mm addressable RGB LED).

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
4. **Component placement priority:** LR1121 center, SE2431L adjacent, UFL connectors at edges
5. **Decoupling caps** within 1mm of IC power pins
6. **Keep ESP32-C3 crystal** away from RF traces and LR1121
7. **Thermal relief** on LR1121 and SE2431L exposed pads — multiple vias to L2 GND

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
- **2.4GHz RX:** RFSW_0=HIGH → SE2431L RXEN=HIGH → LNA active
- **2.4GHz TX:** RFSW_1=HIGH → SE2431L TXEN=HIGH → PA active
- **Sub-GHz RX:** RFSW_2=HIGH → sub-GHz antenna path to RFI_N/P
- **Sub-GHz TX:** RFSW_3=HIGH → sub-GHz antenna path from RFO

---

## 12. Schematic Checklist

- [ ] All LR1121 GND pins (4, 9, 14, 18, EP) connected to ground plane
- [ ] VR_PA decoupled but NOT connected to 3.3V rail
- [ ] TCXO powered from VTCXO pin, output to XTA, XTB floating
- [ ] SE2431L TXEN/RXEN driven by LR1121 RFSW (no extra GPIOs)
- [ ] SAW filter on 2.4GHz path between SE2431L ANT and UFL
- [ ] Sub-GHz balun between LR1121 differential and UFL
- [ ] ESP32-C3 EN pin RC delay (10k + 1uF)
- [ ] Boot button on GPIO9 with pull-up
- [ ] NSS and NRESET pull-ups (10k each)
- [ ] All power pins decoupled with 100nF minimum
- [ ] USB test pads on GPIO18/19
- [ ] FC UART on GPIO20/21
- [ ] WS2812B on GPIO10 with series resistor
