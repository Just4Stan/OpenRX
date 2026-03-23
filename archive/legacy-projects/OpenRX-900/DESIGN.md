# OpenRX-900 Schematic Design

> Release-plan note: `OpenRX-900` is not a standalone release SKU anymore. Keep it as a legacy single-band `LR1121` reference that feeds the future `Mono` receiver.

Sub-GHz (868/915MHz) ExpressLRS receiver using ESP32-C3FH4 + LR1121.

## Block Diagram

```
                    3.3-5V IN
                       │
                   ┌───┴───┐
                   │TLV755 │ LDO
                   │ 33M5G │
                   └───┬───┘
                     3.3V
            ┌──────────┼──────────┐
            │          │          │
       ┌────┴────┐ ┌───┴───┐  ┌──┴──┐
       │ESP32-C3 │ │LR1121 │  │TCXO │
       │  FH4    │ │       │  │32MHz│
       └────┬────┘ └───┬───┘  └─────┘
            │    SPI    │
            ├──────────┘
        UART│
        TX/RX          Sub-GHz RF
            │               │
         To FC         Matching
                       Network
                           │
                        U.FL
                           │
                       Antenna
```

## Power Supply — TLV75533PDQNR (U3)

500mA 3.3V LDO, X2SON-4 (1.0x1.0mm). LCSC C2861882. TI. Max VIN 5.5V.

| Pin | Name | Connection |
|-----|------|------------|
| 1   | IN   | 5V input + C1 (1uF 0402) local + 10uF bulk to GND |
| 2   | GND  | Ground (exposed pad) |
| 3   | EN   | Tied to IN (always enabled) |
| 4   | OUT  | 3.3V rail + C3 (1uF 0402) local + 10uF bulk to GND |

Notes:
- Input voltage range: 3.3V-5V from FC
- Output: 3.3V regulated, 500mA max
- Quiescent current: ~40uA typical
- Input caps placed close to VIN pin
- Output caps placed close to VOUT pin


## LR1121IMLTRT — RF Transceiver (U1)

QFN-32, 4x4mm. LCSC C7498014.

**CRITICAL: The pin assignments below are verified against the LR1121 Datasheet Rev 1.1 (Table 2-1). The LR1121 uses a different pinout from the SX1261/SX1262 and from what was initially specified in the design brief.**

### Complete Pinout (QFN-32, 4x4mm)

| Pin | Name        | Type | Connection | Notes |
|-----|-------------|------|------------|-------|
| 0   | GND (EP)    | -    | GND        | Exposed ground pad — solder to ground plane with thermal vias |
| 1   | VR_PA       | O    | 4.7uF + 100nF to GND | Regulated PA supply output. Internal DC-DC generates voltage for PA. Decouple close to pin. |
| 2   | VBAT_RF     | I    | 3.3V + 100nF to GND | Battery/main supply for RF section |
| 3   | VTCXO       | O    | TCXO VCC input + 100nF to GND | Internal TCXO regulator output. Powers external TCXO. |
| 4   | XTA         | -    | TCXO output | 32MHz TCXO clock input |
| 5   | XTB         | -    | NC (float)  | Not connected when using TCXO (used for crystal in XTAL mode) |
| 6   | NRESET      | I    | ESP32-C3 GPIO2 + 10k pull-up to 3.3V | Active-low reset. Hold low >100us to reset. |
| 7   | 32k_P/DIO11 | I/O  | NC          | 32.768kHz crystal or DIO. Not used (internal RC for RTC). |
| 8   | 32k_N/DIO10 | I/O  | NC          | 32.768kHz crystal or RFSW4. Not used. |
| 9   | DIO9        | I/O  | ESP32-C3 GPIO1 | **IRQ line** — main interrupt to host MCU |
| 10  | DIO8        | I/O  | 100k pull-down to GND | RFSW3 — RF switch control. Pull down when unused. |
| 11  | DIO7        | I/O  | 100k pull-down to GND | RFSW2 — RF switch control. Pull down when unused. |
| 12  | VREG        | O    | 10uF + 100nF to GND | Internal regulator output (LDO/DC-DC). Decouple close to pin. |
| 13  | GND         | -    | GND        | Ground |
| 14  | DCC_SW      | -    | 10uH inductor to VBAT (pin 15) | DC-DC switcher output. Connect inductor for DC-DC mode (recommended for efficiency). |
| 15  | VBAT        | I    | 3.3V + 100nF to GND | Main battery supply. Connected to DCC_SW via 10uH inductor. |
| 16  | DNC         | -    | NC         | Do not connect |
| 17  | DNC         | -    | NC         | Do not connect |
| 18  | DNC         | -    | NC         | Do not connect |
| 19  | DIO6        | I/O  | 100k pull-down to GND | RFSW1 — RF switch control. Pull down when unused. |
| 20  | DIO5        | I/O  | 100k pull-down to GND | RFSW0 — RF switch control. Pull down when unused. |
| 21  | DIO4        | I/O  | ESP32-C3 GPIO5 | **SPI MISO** (via DIO switch matrix) |
| 22  | DIO3        | I/O  | ESP32-C3 GPIO4 | **SPI MOSI** (via DIO switch matrix) |
| 23  | DIO2        | I/O  | ESP32-C3 GPIO6 | **SPI SCK** (via DIO switch matrix) |
| 24  | DIO1        | I/O  | ESP32-C3 GPIO7 + 10k pull-up to 3.3V | **SPI NSS** (via DIO switch matrix). Pull-up keeps chip deselected at boot. |
| 25  | DIO0/BUSY   | I/O  | ESP32-C3 GPIO3 | **BUSY** indicator — high when MCU cannot receive commands |
| 26  | RFIO_HF     | I/O  | NC or 50 ohm to GND | 2.4GHz/S-band RF port. Not used in sub-GHz only mode. Terminate or leave open for future use. |
| 27  | DNC         | -    | NC         | Do not connect |
| 28  | DNC         | -    | NC         | Do not connect |
| 29  | RFI_N_LF0   | I    | Sub-GHz matching network (differential -) | RF LF receiver input, negative |
| 30  | RFI_P_LF0   | I    | Sub-GHz matching network (differential +) | RF LF receiver input, positive |
| 31  | RFO_LP_LF   | O    | Sub-GHz matching network (LP PA output) | Low-power PA output, +15dBm max sub-GHz |
| 32  | RFO_HP_LF   | O    | Sub-GHz matching network (HP PA output) | High-power PA output, +22dBm max sub-GHz |

### IMPORTANT Corrections from Design Brief

The initial design brief listed incorrect pin assignments based on assumptions about the LR1121 pinout. Key differences from the datasheet:

1. **Pin 1 is VR_PA** (not VDD) — regulated PA supply output, needs 4.7uF + 100nF
2. **Pin 2 is VBAT_RF** (not VR_PA) — RF section supply input
3. **Pin 3 is VTCXO** (not VDD_IN) — internal regulator output that powers external TCXO
4. **Pins 4/5 are XTA/XTB** — crystal/TCXO connections
5. **SPI is on DIO1-DIO4 (pins 21-24)**, not on dedicated SPI pins — the LR1121 uses a DIO switch matrix
6. **BUSY is DIO0 (pin 25)**, not a separate BUSY pin
7. **The LR1121 has 4 sub-GHz RF ports**: RFI_N_LF0 (pin 29), RFI_P_LF0 (pin 30), RFO_LP_LF (pin 31), RFO_HP_LF (pin 32)
8. **RFSW pins are DIO5-DIO8 (pins 10-11, 19-20)**, not separate RFSW pins
9. **Package is QFN-32 4x4mm**. Any older 5x5mm note is stale.

### LR1121 DIO Switch Matrix Configuration

The LR1121 uses a DIO Switch Matrix (SWM) to assign functions to DIOs. For ELRS operation:

| DIO Pin | LR1121 Pin | SWM Function | ESP32-C3 GPIO |
|---------|------------|--------------|---------------|
| DIO0    | 25         | BUSY         | GPIO3         |
| DIO1    | 24         | SPI NSS      | GPIO7         |
| DIO2    | 23         | SPI SCK      | GPIO6         |
| DIO3    | 22         | SPI MOSI     | GPIO4         |
| DIO4    | 21         | SPI MISO     | GPIO5         |
| DIO5    | 20         | RFSW0        | Not connected (100k pull-down) |
| DIO6    | 19         | RFSW1        | Not connected (100k pull-down) |
| DIO7    | 11         | RFSW2        | Not connected (100k pull-down) |
| DIO8    | 10         | RFSW3        | Not connected (100k pull-down) |
| DIO9    | 9          | IRQ          | GPIO1         |
| DIO10   | 8          | 32k_N/RFSW4  | Not connected |
| DIO11   | 7          | 32k_P/NC     | Not connected |

Note: For sub-GHz only without external PA/LNA, RFSW pins are driven by LR1121 firmware via `SetDioAsRfSwitch()` to select internal RF paths (HP PA, LP PA, or RX). No external RF switch IC needed. The ELRS firmware configures this through the `radio_rfsw_ctrl` mechanism in the target definition, not via MCU GPIOs.

### LR1121 Power Supply Network

```
3.3V ──┬── 100nF ── GND    (VBAT_RF, pin 2)
       │
       ├── 100nF ── GND    (VBAT, pin 15)
       │
       └── 10uH inductor ── DCC_SW (pin 14)
                             │
                          VREG (pin 12) ── 10uF + 100nF ── GND

VR_PA (pin 1) ── 4.7uF + 100nF ── GND    (output, do not drive)

VTCXO (pin 3) ── to TCXO VCC ── 100nF ── GND    (output, powers TCXO)
```

### LR1121 Sub-GHz RF Impedance

From the datasheet, the differential impedance across RFI_N_LF0 / RFI_P_LF0:
- 868MHz: 9.4 - j141 ohm
- 920MHz: 9.5 - j131 ohm

This needs a matching network (balun + impedance match) to convert to 50 ohm single-ended for the UFL connector.


## Sub-GHz RF Matching Network

The LR1121 has 4 sub-GHz RF pins:
- **RFI_P_LF0 (pin 30)** — RX input, differential positive
- **RFI_N_LF0 (pin 29)** — RX input, differential negative
- **RFO_LP_LF (pin 31)** — Low-power PA TX output (+15dBm)
- **RFO_HP_LF (pin 32)** — High-power PA TX output (+22dBm)

### Matching Network Approach

For a budget sub-GHz receiver, use a discrete matching network with the following topology based on the Semtech reference design:

```
                    ┌─── C_HP ─── RFO_HP_LF (pin 32)
                    │
UFL ── C_DC ──┬── L_MATCH ──┬─── C_LP ─── RFO_LP_LF (pin 31)
              │              │
              │         C_MATCH
              │              │
              │             GND
              │
              ├── L1 ── RFI_P_LF0 (pin 30)
              │
              ├── L2 ── RFI_N_LF0 (pin 29)
              │
              └── C_BAL ── GND
```

### Recommended Component Values (868/915MHz Multi-band)

Based on Semtech reference design AN1200.76 and SX1261/SX1262 matching guidelines (LR1121 shares the same sub-GHz RF architecture):

**RX Matching (differential to single-ended):**
- L1: 15nH (0402) — RFI_P match
- L2: 15nH (0402) — RFI_N match
- C_BAL: 1.5pF (0402) — balun capacitor
- C_MATCH: 3.3pF (0402) — impedance match

**TX Path:**
- C_HP: 100pF (0402) — DC block for HP PA
- C_LP: 100pF (0402) — DC block for LP PA

**Common:**
- C_DC: 100pF (0402) — DC blocking cap to antenna
- L_MATCH: 6.8nH (0402) — series matching inductor

**IMPORTANT:** These values are approximate and require VNA tuning on the actual PCB. The impedance match depends heavily on PCB layout, trace impedance, and via placement. Semtech's IPD reference design (AN1200.76) uses an integrated passive device that replaces the discrete network.

### Preferred Integrated RF Front End

Use **Johanson 0900PC16J0042001E** (`LCSC C19842466`) as the preferred sub-GHz RF front end:
- Designed specifically for the **Semtech LR1110 / LR1120 / LR1121** family
- Covers **863-870MHz** and **902-928MHz**
- Integrates the **impedance transformation balun** and **harmonic filtering**
- Provides separate **RX**, **TX_LP**, and **TX_HP** ports that map directly to `RFI_P/N_LF0`, `RFO_LP_LF`, and `RFO_HP_LF`
- Johanson states it provides the attenuation needed to help meet **FCC / ETSI** requirements
- Typical loss is **1.0dB TX** and **1.7dB RX**

For OpenRX, this is the best baseline because it removes most of the uncertain hand-tuned 868/915MHz matching work. The discrete network above should be treated as a fallback only if `C19842466` becomes unavailable or if you want a lower-BOM-cost prototype that will still need RF tuning.


## ESP32-C3FH4 (U2)

QFN-32, 5x5mm. LCSC C2858491.
- 4MB internal flash (no external flash needed)
- Requires external 40MHz crystal
- WiFi + BLE 5.0 (used for firmware updates via WiFi/Betaflight passthrough)
- RISC-V single-core 160MHz

### Pin Assignments

Pin assignments follow the **ExpressLRS Generic C3 LR1121** target definition.

| ESP32-C3 Pin | Function | Connection | Notes |
|-------------|----------|------------|-------|
| GPIO0       | (reserved) | NC or test pad | Strapping pin — leave floating or pull-up |
| GPIO1       | radio_dio1 (IRQ) | LR1121 DIO9 (pin 9) | Interrupt from LR1121 |
| GPIO2       | radio_rst | LR1121 NRESET (pin 6) + 10k pull-up | Active-low reset |
| GPIO3       | radio_busy | LR1121 DIO0/BUSY (pin 25) | BUSY status from LR1121 |
| GPIO4       | radio_mosi | LR1121 DIO3 (pin 22) | SPI MOSI |
| GPIO5       | radio_miso | LR1121 DIO4 (pin 21) | SPI MISO |
| GPIO6       | radio_sck | LR1121 DIO2 (pin 23) | SPI clock |
| GPIO7       | radio_nss | LR1121 DIO1 (pin 24) + 10k pull-up | SPI chip select |
| GPIO8       | led_rgb | WS2812B DIN | Addressable RGB LED (GRB format) |
| GPIO9       | button | Boot/bind button + 10k pull-up | Strapping pin — also used for boot mode |
| GPIO10      | NC | NC | Available for future use |
| GPIO18      | USB D- | Test pad | USB for development/debug |
| GPIO19      | USB D+ | Test pad | USB for development/debug |
| GPIO20      | serial_rx | UART RX from FC (CRSF) | FC sends CRSF data to receiver |
| GPIO21      | serial_tx | UART TX to FC (CRSF) | Receiver sends CRSF data to FC |
| EN          | Enable | 10k pull-up to 3.3V + 1uF to GND | RC delay for stable boot |
| XTAL_P      | Crystal | 40MHz crystal pin 1 + 10pF load cap | |
| XTAL_N      | Crystal | 40MHz crystal pin 2 + 10pF load cap | |
| VDD3P3      | Power | 3.3V + 100nF | Main digital supply |
| VDD3P3_RTC  | Power | 3.3V + 100nF | RTC domain supply |
| VDDA        | Power | 3.3V + 100nF + 1uF | Analog supply (RF) |
| GND/EP      | Ground | GND plane | Exposed pad — thermal vias to ground |

### ESP32-C3 Crystal Circuit

```
              ┌────────────────────────┐
              │      40MHz Crystal     │
XTAL_P ──┬── ┤ 1                    2 ├──┬── XTAL_N
          │   └────────────────────────┘  │
         C5                              C6
        10pF                            10pF
          │                               │
         GND                             GND
```

Optional: 24nH series inductor on XTAL_P trace to reduce harmonic interference with RF.

### ESP32-C3 Boot / EN Circuit

```
3.3V ── R1 (10k) ── EN ── C7 (1uF) ── GND

3.3V ── R2 (10k) ── GPIO9 ── Boot Button ── GND
```

GPIO9 is a strapping pin:
- HIGH at boot = normal SPI boot (from internal flash)
- LOW at boot = download mode (UART/USB)


## TCXO — 32MHz (Y2)

32MHz TCXO for LR1121 clock reference.

**Selected: YXC OW2EL89CENUXFMYLC-32M** — LCSC C22434888
- Package: SMD3225-4P (3.2x2.5mm)
- Frequency: 32MHz
- Output: Peak-shaving sine wave (clipped sine)
- Supply: 3.3V (powered by LR1121 VTCXO pin 3)
- Stability: +/-2.5ppm
- Temperature range: -40 to +85C

Note: The 3225 package is slightly larger than ideal for this board. If a 2520 or 2016 TCXO becomes available on LCSC, prefer that. The TAITIEN TYETBCSANF-32.000000 (C6732076, SMD2520) is an alternative but was out of stock at time of design.

### TCXO Connection

```
LR1121 VTCXO (pin 3) ── C8 (100nF) ── GND
                    │
                    └── TCXO VCC (pin 4)
                         TCXO OUT (pin 3) ── LR1121 XTA (pin 4)
                         TCXO GND (pin 2) ── GND
                         TCXO NC  (pin 1) ── NC

LR1121 XTB (pin 5) ── NC (floating, TCXO mode)
```


## 40MHz Crystal (Y1)

For ESP32-C3FH4. Standard 40MHz SMD crystal.

**Selected: TXC 7M40000005** — LCSC C90924
- Package: SMD3225-4P (3.2x2.5mm)
- Frequency: 40MHz
- Load capacitance: 10pF
- Frequency tolerance: +/-10ppm
- ESR: 25 ohm max

### Load Capacitor Calculation

CL = 10pF (from crystal datasheet)
Cstray ~ 2-3pF (PCB parasitic)

C_load = 2 * (CL - Cstray) = 2 * (10 - 2.5) = 15pF

Use 10pF caps as a starting point (Espressif recommendation). Adjust based on frequency measurement.


## XL-1010RGBC-WS2812B RGB LED (D1)

Addressable RGB LED, 1.0x1.0mm. LCSC C5349953.

| Pin | Name | Connection |
|-----|------|------------|
| 1   | VDD  | 3.3V + 100nF bypass |
| 2   | DOUT | NC (single LED, no chain) |
| 3   | GND  | GND |
| 4   | DIN  | ESP32-C3 GPIO8 |

Note: ELRS target specifies `led_rgb_isgrb: true` — the WS2812B uses GRB byte order, which matches.


## UFL Antenna Connector (J1)

**Selected: HRS U.FL-R-SMT-1(80)** — LCSC C88374
- 50 ohm impedance
- Frequency range: DC to 6GHz
- Mating height: ~1.0mm

Connected to the 50-ohm output of the sub-GHz matching network.


## UART / CRSF Interface (J2)

4-pin connection to flight controller:
| Pad | Signal | Notes |
|-----|--------|-------|
| 1   | GND    | Ground |
| 2   | 5V     | Power input from FC (to LDO VIN) |
| 3   | TX     | ESP32-C3 GPIO21 → FC RX (CRSF telemetry) |
| 4   | RX     | FC TX → ESP32-C3 GPIO20 (CRSF commands) |

Standard ELRS CRSF pinout. Half-duplex capable via ELRS firmware.


## USB Debug Pads (J3)

Test pads for USB programming (optional, not populated):
| Pad | Signal | Notes |
|-----|--------|-------|
| 1   | D-     | ESP32-C3 GPIO18 |
| 2   | D+     | ESP32-C3 GPIO19 |
| 3   | GND    | Ground |


## Complete Net List Summary

### Power Nets
- **5V**: FC input → LDO VIN
- **3.3V**: LDO VOUT → ESP32-C3 (VDD3P3, VDD3P3_RTC, VDDA) → LR1121 (VBAT_RF pin 2, VBAT pin 15) → WS2812B VDD → pull-up resistors
- **VTCXO**: LR1121 pin 3 output → TCXO VCC (internally regulated, ~1.6V)
- **VR_PA**: LR1121 pin 1 output → decoupling caps only (internal PA supply)
- **VREG**: LR1121 pin 12 output → decoupling caps only (internal regulator)

### SPI Bus
| Signal | ESP32-C3 | LR1121 |
|--------|----------|--------|
| SCK    | GPIO6    | DIO2 (pin 23) |
| MOSI   | GPIO4    | DIO3 (pin 22) |
| MISO   | GPIO5    | DIO4 (pin 21) |
| NSS    | GPIO7    | DIO1 (pin 24) |

### Control
| Signal | ESP32-C3 | LR1121 |
|--------|----------|--------|
| BUSY   | GPIO3    | DIO0 (pin 25) |
| IRQ    | GPIO1    | DIO9 (pin 9) |
| NRESET | GPIO2    | NRESET (pin 6) |

### UART (CRSF)
| Signal | ESP32-C3 | Direction |
|--------|----------|-----------|
| TX     | GPIO21   | To FC |
| RX     | GPIO20   | From FC |


## Decoupling Capacitor Summary

| Component | Value | Package | Location |
|-----------|-------|---------|----------|
| C1        | 10uF  | 0402/0603 | LDO VIN |
| C2        | 100nF | 0402    | LDO VIN |
| C3        | 22uF  | 0603    | LDO VOUT |
| C4        | 100nF | 0402    | LDO VOUT |
| C5        | 10pF  | 0402    | XTAL_P to GND |
| C6        | 10pF  | 0402    | XTAL_N to GND |
| C7        | 1uF   | 0402    | EN to GND |
| C8        | 100nF | 0402    | VTCXO (LR1121 pin 3) to GND |
| C9        | 100nF | 0402    | VBAT_RF (LR1121 pin 2) to GND |
| C10       | 100nF | 0402    | VBAT (LR1121 pin 15) to GND |
| C11       | 4.7uF | 0402    | VR_PA (LR1121 pin 1) to GND |
| C12       | 100nF | 0402    | VR_PA (LR1121 pin 1) to GND |
| C13       | 10uF  | 0402    | VREG (LR1121 pin 12) to GND |
| C14       | 100nF | 0402    | VREG (LR1121 pin 12) to GND |
| C15       | 100nF | 0402    | ESP32-C3 VDD3P3 to GND |
| C16       | 100nF | 0402    | ESP32-C3 VDD3P3_RTC to GND |
| C17       | 1uF   | 0402    | ESP32-C3 VDDA to GND |
| C18       | 100nF | 0402    | ESP32-C3 VDDA to GND |
| C19       | 100nF | 0402    | WS2812B VDD to GND |


## Resistor Summary

| Component | Value | Package | Location |
|-----------|-------|---------|----------|
| R1        | 10k   | 0402    | EN pull-up to 3.3V |
| R2        | 10k   | 0402    | GPIO9 boot pull-up to 3.3V |
| R3        | 10k   | 0402    | LR1121 NRESET pull-up to 3.3V |
| R4        | 10k   | 0402    | LR1121 NSS (DIO1) pull-up to 3.3V |
| R5        | 100k  | 0402    | LR1121 DIO5 (RFSW0) pull-down to GND |
| R6        | 100k  | 0402    | LR1121 DIO6 (RFSW1) pull-down to GND |
| R7        | 100k  | 0402    | LR1121 DIO7 (RFSW2) pull-down to GND |
| R8        | 100k  | 0402    | LR1121 DIO8 (RFSW3) pull-down to GND |


## Inductor Summary

| Component | Value | Package | Location |
|-----------|-------|---------|----------|
| L1        | 10uH  | 0402/0603 | LR1121 DC-DC: VBAT (pin 15) to DCC_SW (pin 14) |


## PCB Layout Notes

- **Board size:** 18x13mm, 2-layer, 1.0mm thickness
- **Ground plane:** Continuous on bottom layer, maximum copper pour on top layer
- **LR1121 thermal pad:** Connected to ground plane with minimum 9 thermal vias (0.2mm drill)
- **ESP32-C3 thermal pad:** Connected to ground plane with thermal vias
- **RF trace:** 50-ohm controlled impedance from matching network to UFL connector
- **SPI traces:** Keep short, group together, avoid crossing RF traces
- **Decoupling caps:** Place as close as possible to IC power pins
- **Crystal placement:** Close to ESP32-C3, minimize trace length
- **TCXO placement:** Close to LR1121 XTA pin, minimize trace length
- **Antenna connector:** Place at board edge for clean RF path


## Firmware Target

ExpressLRS target: **Generic C3 LR1121** (`RX/Generic C3 LR1121.json`)

```json
{
    "serial_rx": 20,
    "serial_tx": 21,
    "radio_miso": 5,
    "radio_mosi": 4,
    "radio_sck": 6,
    "radio_busy": 3,
    "radio_dio1": 1,
    "radio_nss": 7,
    "radio_rst": 2,
    "power_min": 0,
    "power_max": 3,
    "power_default": 0,
    "power_control": 0,
    "power_values": [12, 16, 19, 22],
    "power_values_dual": [-12, -9, -6, -2],
    "power_lna_gain": 12,
    "led_rgb": 8,
    "led_rgb_isgrb": true,
    "radio_dcdc": true,
    "button": 9
}
```

Note: `radio_dcdc: true` enables the LR1121 internal DC-DC converter via the DCC_SW/VBAT inductor circuit, improving power efficiency.

---

# OpenRX-900 Bill of Materials

Target BOM cost: EUR 4-5 (at JLCPCB assembly quantities)

## Active Components

| Ref | Description | MPN | LCSC | Package | Qty | Unit Price | Notes |
|-----|-------------|-----|------|---------|-----|------------|-------|
| U1  | LR1121 sub-GHz/2.4GHz transceiver | LR1121IMLTRT | C7498014 | QFN-32 4x4mm | 1 | ~$2.50 | Main RF transceiver |
| U2  | ESP32-C3FH4 MCU (4MB flash) | ESP32-C3FH4 | C2858491 | QFN-32 5x5mm | 1 | ~$1.20 | RISC-V MCU, WiFi+BLE |
| U3  | TLV75533PDQNR 3.3V LDO | TLV75533PDQNR | C2861882 | X2SON-4 1x1mm | 1 | ~$0.15 | TI, 500mA, max 5.5V input |
| Y2  | 32MHz TCXO (peak-shaving sine) | OW2EL89CENUXFMYLC-32M | C22434888 | SMD3225-4P | 1 | ~$0.46 | For LR1121 clock |
| Y1  | 40MHz crystal (10pF load) | 7M40000005 | C90924 | SMD3225-4P | 1 | ~$0.08 | For ESP32-C3 clock |
| D1  | XL-1010RGBC-WS2812B | XL-1010RGBC-WS2812B | C5349953 | 1010 (1x1mm) | 1 | ~$0.04 | Addressable LED |
| J1  | U.FL antenna connector | U.FL-R-SMT-1(80) | C88374 | SMD | 1 | ~$0.08 | 50 ohm, HRS/Hirose |

**Active subtotal: ~$4.40**

## Passive Components — Capacitors

| Ref | Value | Package | Qty | LCSC | Notes |
|-----|-------|---------|-----|------|-------|
| C1  | 10uF 10V X5R | 0402 | 1 | C15525 | LDO input |
| C2  | 100nF 16V X7R | 0402 | 1 | C1525 | LDO input bypass |
| C3  | 22uF 10V X5R | 0603 | 1 | C59461 | LDO output |
| C4  | 100nF 16V X7R | 0402 | 1 | C1525 | LDO output bypass |
| C5  | 10pF 50V C0G | 0402 | 1 | C32949 | XTAL_P load cap |
| C6  | 10pF 50V C0G | 0402 | 1 | C32949 | XTAL_N load cap |
| C7  | 1uF 16V X5R | 0402 | 1 | C52923 | ESP32 EN delay |
| C8  | 100nF 16V X7R | 0402 | 1 | C1525 | LR1121 VTCXO bypass |
| C9  | 100nF 16V X7R | 0402 | 1 | C1525 | LR1121 VBAT_RF bypass |
| C10 | 100nF 16V X7R | 0402 | 1 | C1525 | LR1121 VBAT bypass |
| C11 | 4.7uF 10V X5R | 0402 | 1 | C23733 | LR1121 VR_PA |
| C12 | 100nF 16V X7R | 0402 | 1 | C1525 | LR1121 VR_PA bypass |
| C13 | 10uF 10V X5R | 0402 | 1 | C15525 | LR1121 VREG |
| C14 | 100nF 16V X7R | 0402 | 1 | C1525 | LR1121 VREG bypass |
| C15 | 100nF 16V X7R | 0402 | 1 | C1525 | ESP32 VDD3P3 bypass |
| C16 | 100nF 16V X7R | 0402 | 1 | C1525 | ESP32 VDD3P3_RTC bypass |
| C17 | 1uF 16V X5R | 0402 | 1 | C52923 | ESP32 VDDA |
| C18 | 100nF 16V X7R | 0402 | 1 | C1525 | ESP32 VDDA bypass |
| C19 | 100nF 16V X7R | 0402 | 1 | C1525 | WS2812B bypass |

**Capacitor summary: 19 caps total**
- 100nF 0402 x11 (C1525 — LCSC basic part)
- 10uF 0402 x2 (C15525 — LCSC basic part)
- 22uF 0603 x1 (C59461 — LCSC basic part)
- 1uF 0402 x2 (C52923 — LCSC basic part)
- 4.7uF 0402 x1 (C23733 — LCSC basic part)
- 10pF 0402 x2 (C32949 — LCSC basic part)

## Passive Components — Resistors

| Ref | Value | Package | Qty | LCSC | Notes |
|-----|-------|---------|-----|------|-------|
| R1  | 10k 1% | 0402 | 1 | C25744 | ESP32 EN pull-up |
| R2  | 10k 1% | 0402 | 1 | C25744 | ESP32 GPIO9 boot pull-up |
| R3  | 10k 1% | 0402 | 1 | C25744 | LR1121 NRESET pull-up |
| R4  | 10k 1% | 0402 | 1 | C25744 | LR1121 NSS pull-up |
| R5  | 100k 1% | 0402 | 1 | C25741 | LR1121 RFSW0 pull-down |
| R6  | 100k 1% | 0402 | 1 | C25741 | LR1121 RFSW1 pull-down |
| R7  | 100k 1% | 0402 | 1 | C25741 | LR1121 RFSW2 pull-down |
| R8  | 100k 1% | 0402 | 1 | C25741 | LR1121 RFSW3 pull-down |

**Resistor summary: 8 resistors total**
- 10k 0402 x4 (C25744 — LCSC basic part)
- 100k 0402 x4 (C25741 — LCSC basic part)

## Passive Components — Inductors

| Ref | Value | Package | Qty | LCSC | Notes |
|-----|-------|---------|-----|------|-------|
| L1  | 10uH 300mA | 0603 | 1 | C1035 | LR1121 DC-DC inductor. Low DCR preferred. |

**Inductor summary: 1 inductor**
- 10uH 0603 x1 (C1035 — LCSC basic part)

## RF Matching Network Components

These values are for the discrete sub-GHz matching network. Exact values require VNA tuning on the final PCB.

| Ref | Value | Package | Qty | LCSC | Notes |
|-----|-------|---------|-----|------|-------|
| C20 | 100pF C0G | 0402 | 1 | C1553 | DC block, antenna side |
| C21 | 100pF C0G | 0402 | 1 | C1553 | DC block, HP PA |
| C22 | 100pF C0G | 0402 | 1 | C1553 | DC block, LP PA |
| C23 | 1.5pF C0G | 0402 | 1 | C1546 | Balun cap |
| C24 | 3.3pF C0G | 0402 | 1 | C1548 | Impedance match cap |
| L2  | 15nH | 0402 | 1 | TBD | RFI_P match |
| L3  | 15nH | 0402 | 1 | TBD | RFI_N match |
| L4  | 6.8nH | 0402 | 1 | TBD | Series match |

Preferred alternative to the discrete network:

| Ref | Value / Part | Package | Qty | LCSC | Notes |
|-----|--------------|---------|-----|------|-------|
| IPD1 | Johanson 0900PC16J0042001E | 2.0x1.6mm 10-pad | 1 | C19842466 | LR11xx-specific 868/915MHz integrated passive device. Replaces the discrete sub-GHz balun/match/filter network above. |

As of March 23, 2026, recent LCSC indexing showed `C19842466` with immediate stock and pricing around `$0.96 @ 1`, `$0.78 @ 10`, `$0.60 @ 100`. If `IPD1` is used, the discrete RF network above should not be populated.

## Mechanical

| Item | Description | Notes |
|------|-------------|-------|
| PCB  | 18x13mm, 2-layer, 1.0mm, ENIG | JLCPCB standard 2-layer |
| Boot button | 3x4mm SMD tactile switch | Optional, for entering boot/bind mode |

## BOM Cost Estimate

| Category | Est. Cost (1pc) |
|----------|----------------|
| Active ICs (U1, U2, U3) | ~$3.74 |
| TCXO + Crystal (Y1, Y2) | ~$0.54 |
| LED (D1) | ~$0.04 |
| Connector (J1) | ~$0.08 |
| Capacitors (x19+5) | ~$0.15 |
| Resistors (x8) | ~$0.03 |
| Inductors (x1+3) | ~$0.10 |
| **Total BOM** | **~$4.68** |

At JLCPCB assembly quantities (100+), expect ~$3.50-4.00 per board.

## LCSC Part Availability Notes

- All capacitors and resistors use LCSC basic parts (no extended library fee)
- TLV75533PDQNR (C2861882) is an LCSC extended part
- ESP32-C3FH4 (C2858491) and LR1121 (C7498014) are extended parts (extra assembly fee)
- XL-1010RGBC-WS2812B (C5349953) is an extended part
- U.FL connector (C88374) is an extended part
- 40MHz crystal (C90924) is an extended part
- 32MHz TCXO (C22434888) is an extended part

## Components Requiring LCSC Verification

Before ordering, verify these components are in stock on LCSC:

1. **LR1121IMLTRT (C7498014)** — Newer part, may have limited stock
2. **32MHz TCXO (C22434888)** — Had ~2,782 units at time of design. Alternative: TAITIEN TYETBCSANF-32.000000 (C6732076, SMD2520) when in stock
3. **RF inductors (L2-L4)** — Part numbers TBD, select from LCSC RF inductor category
4. **Tactile switch** — Select SMD 3x4mm or 2x3mm switch from LCSC

## Import List for easyeda2kicad

```bash
# Main ICs
easyeda2kicad --full --lcsc_id=C2858491 --output=libs  # ESP32-C3FH4
easyeda2kicad --full --lcsc_id=C7498014 --output=libs  # LR1121IMLTRT
easyeda2kicad --full --lcsc_id=C2861882 --output=libs  # TLV75533PDQNR

# TCXO and Crystal
easyeda2kicad --full --lcsc_id=C22434888 --output=libs # 32MHz TCXO
easyeda2kicad --full --lcsc_id=C90924 --output=libs    # 40MHz crystal

# LED and Connector
easyeda2kicad --full --lcsc_id=C5349953 --output=libs  # XL-1010RGBC-WS2812B
easyeda2kicad --full --lcsc_id=C88374 --output=libs    # U.FL connector
```
