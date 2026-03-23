# OpenRX-900 Schematic Design

> Audit note: this brief still contains unresolved `LR1121` package and pin-mapping contradictions. Do not start schematic capture from it until the LR1121 section is reconciled against the official Semtech datasheet and the intended ELRS target wiring.

Sub-GHz (868/915MHz) ExpressLRS receiver using ESP32-C3FH4 + LR1121.

## Block Diagram

```
                    3.3-5V IN
                       │
                   ┌───┴───┐
                   │ME6211C│ LDO
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

## Power Supply — ME6211C33M5G-N (U3)

500mA 3.3V LDO, SOT-23-5. LCSC C82942.

| Pin | Name | Connection |
|-----|------|------------|
| 1   | VIN  | 5V input + C1 (10uF ceramic) + C2 (100nF ceramic) to GND |
| 2   | GND  | Ground |
| 3   | EN   | Tied to VIN (always enabled) |
| 4   | NC   | No connect |
| 5   | VOUT | 3.3V rail + C3 (22uF ceramic) + C4 (100nF ceramic) to GND |

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

Note: For sub-GHz only without external PA/LNA, RFSW pins are driven by LR1121 firmware to select internal RF paths (HP PA, LP PA, or RX). No external RF switch needed. The ELRS firmware configures these via `radio_dcdc: true` in the target JSON.

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

### Alternative: Johanson IPD Balun

Instead of discrete components, use **Johanson 0900FM15K0039** (0805 package):
- Integrates balun, matching, and filtering in a single 0805 component
- Replaces 12 discrete components
- Optimized for SX1261/SX1262 (compatible with LR1121 sub-GHz port)
- Insertion loss: 1.1dB TX typical, 1.5dB RX typical
- **Note:** This part may not be available on LCSC. Check DigiKey/Mouser.

For this budget design, the discrete matching network is recommended for cost reasons.


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


## WS2812B-2020 RGB LED (D1)

Addressable RGB LED, 2.0x2.0mm. LCSC C965555.

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
    "power_high": 3,
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
