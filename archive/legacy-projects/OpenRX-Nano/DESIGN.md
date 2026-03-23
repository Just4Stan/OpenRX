# OpenRX-Nano Schematic Design Document

> Release-plan note: `OpenRX-Nano` is not part of the current release stack. Keep this document only as a legacy `SX1281 + FEM` reference concept.
>
> Audit note: for current ExpressLRS unified RX targets, the front-end control keys are `power_rxen` and `power_txen`, not `rx_en` and `tx_en`.
>
> Procurement note: `AE1` / `2450AT18A100E` is the ESP32-C3 Wi-Fi update antenna in the current schematic. The ELRS RF path goes out through `JP1` / `U.FL-R-SMT-1(80)`.

2.4GHz ExpressLRS receiver with PA+LNA front-end.
PCB: 20x13mm, 2-layer, 1.0mm thickness.

## Block Diagram

```
                          +-------------------+
                          |                   |
   FC 5V ──► TLV755 LDO ─┤─► 3.3V Rail       |
                          |                   |
                          |   ┌───────────┐   |
                          |   │ ESP32-C3  │   |
                          |   │  FH4      │   |
              40MHz XTAL──┤───┤           │   |
                          |   │  SPI Bus  │   |
                          |   │  GPIO     │   |
                          |   └─┬─┬─┬─┬─┬─┘   |
                          |     │ │ │ │ │     |
                          |   ┌─┴─┴─┴─┴─┴─┐   |
                          |   │  SX1281   │   |
              52MHz TCXO──┤───┤           │   |
                          |   │  RFIO     │   |
                          |   └─────┬─────┘   |
                          |         │         |
                          |   ┌─────┴─────┐   |
                          |   │ RFX2401C  │   |
                          |   │  PA+LNA   │   |
                          |   └─────┬─────┘   |
                          |         │         |
                          |   DEA LPF Filter  |
                          |         │         |
                          |    UFL Connector  |
                          +-------------------+
                                │   │
                              TX/RX to FC
                              (CRSF UART)
```

## RF Signal Path

```
Antenna ◄──► UFL/IPEX ◄──► [C15: 0.3pF shunt] ◄──► RFX2401C ANT (pin 10) ◄──► [internal switch] ◄──► TXRX (pin 4) ◄──► DEA102700LT-6307A2 ◄──► SX1281 RFIO (pin 15)
                             (MANDATORY, 5th harm.)                                                                       (LPF, LCSC C574024)
```

Between SX1281 RFIO (pin 15) and RFX2401C TXRX (pin 4): a single DEA102700LT-6307A2
(LCSC C574024, 0402 integrated LPF) is the current fitted low-pass element in the
schematic. It should not be described as a Semtech-specific one-part SX1281 match. This
single component replaces
what earlier revisions called a "SAW filter" in this path. Both ports are 50 ohm; the
RFX2401C TXRX is DC shorted to GND internally, providing the DC path required by SX1281
RFIO. No external DC blocking cap needed.

**MANDATORY**: C15 (0.3pF C0G 0402) shunt cap to GND on RFX2401C ANT pin (pin 10).
This is the 5th harmonic filter required for CE compliance per the RFX2401C eval board
design. Do not omit. See note in BOM section for sourcing.

---

## 1. Power Supply — TLV75533PDQNR (U1)

LCSC: C2861882 | Package: X2SON-4 (1.0x1.0mm) | 3.3V 500mA LDO (TI)

```
        VIN (5V from FC)
         │
         ├──┤C_bulk: 10uF 0603├──GND
         │
         ├──┤C1: 1uF 0402├──GND
         │
    ┌────┴────┐
    │ 1: IN   │
    │ 2: GND  ├──── GND (exposed pad)
    │ 3: EN   ├──── IN (tied to input)
    │ 4: OUT  ├──── 3.3V Rail
    └────┬────┘
         │
         ├──┤C3: 1uF 0402├──GND
         │
         ├──┤C_bulk: 10uF 0603├──GND
         │
        3.3V
```

### TLV75533PDQNR Pin Table

| Pin | Name | Connection | Notes |
|-----|------|------------|-------|
| 1   | IN   | 5V input from FC | C1 (1uF 0402) local + 10uF bulk to GND |
| 2   | GND  | Ground | Exposed pad |
| 3   | EN   | IN (tied high) | Active high enable |
| 4   | OUT  | 3.3V output | C3 (1uF 0402) local + 10uF bulk to GND |

Note: TLV755 max VIN is 5.5V. Input from FC 5V rail only, not raw battery.

---

## 2. MCU — ESP32-C3FH4 (U2)

LCSC: C2858491 | Package: QFN-32, 5x5mm | 4MB internal flash

### Crystal Circuit

40MHz crystal (Y1) with load capacitors:

```
    XTAL_P (pin 7) ──── Y1 ──── XTAL_N (pin 8)
         │               40MHz          │
         ├──┤CX1: 10pF├──┐    ┌──┤CX2: 10pF├──┤
         │                │    │                │
        GND              GND  GND              GND
```

Crystal: current schematic uses `CJ17-400001010B20`, LCSC `C2875272`, 40MHz, 10pF load.

### Reset Circuit

```
    3.3V ──┤R1: 10k├── EN (pin 4)
                        │
                       ┤C5: 1uF├── GND
```

### Boot Button

```
    3.3V ──┤R2: 10k├── GPIO9 (pin 18)
                        │
                       [SW1] ── GND
```

### USB Test Pads

```
    GPIO18 (pin 27) ── TP_USB_DN (test pad)
    GPIO19 (pin 28) ── TP_USB_DP (test pad)
    GND             ── TP_GND    (test pad)
```

5.1k pull-down resistors on D+/D- not required for test pads (only for USB-C receptacle).

### ESP32-C3FH4 Complete Pin Table

| Pin | Name     | Connection | Notes |
|-----|----------|------------|-------|
| 1   | GND      | GND | |
| 2   | GND      | GND | |
| 3   | ADC2/GPIO3 | SX1281 BUSY | Direct |
| 4   | EN       | 10k to 3.3V + 1uF to GND | RC reset delay |
| 5   | ADC1/GPIO2 | SX1281 NRESET | Direct |
| 6   | GPIO1    | RFX2401C TXEN (pin 5) via 10k series R | TX enable |
| 7   | XTAL_P   | 40MHz crystal + 10pF cap | |
| 8   | XTAL_N   | 40MHz crystal + 10pF cap | |
| 9   | GPIO0    | RFX2401C RXEN (pin 6) via 10k series R | RX enable |
| 10  | VDD3P3   | 3.3V + 100nF | Power supply |
| 11  | VDD3P3   | 3.3V | Connected to pin 10 supply |
| 12  | GPIO10   | WS2812B DIN | Status LED data |
| 13  | VDD_SPI  | 3.3V + 100nF | Internal flash supply |
| 14  | GPIO6/FSPICLK | SX1281 MISO (pin 16) | SPI |
| 15  | GPIO7/FSPID | SX1281 MOSI (pin 17) | SPI |
| 16  | GPIO4    | SX1281 SCK (pin 18) | SPI clock |
| 17  | GPIO5    | SX1281 DIO1 (pin 5) | Interrupt |
| 18  | GPIO9    | Boot button + 10k pull-up | Boot mode select |
| 19  | GPIO8/FSPICS0 | SX1281 NSS (pin 19) + 10k pull-up | SPI chip select |
| 20  | GPIO19   | USB D+ test pad | USB |
| 21  | GPIO18   | USB D- test pad | USB |
| 22  | VDD3P3_RTC | 3.3V + 100nF | RTC domain supply |
| 23  | CHIP_PU  | NC (internal connection to EN) | Do not connect externally |
| 24  | GPIO20/U0RXD | UART RX from FC (CRSF) | RCSIGNAL_RX |
| 25  | GPIO21/U0TXD | UART TX to FC (CRSF) | RCSIGNAL_TX |
| 26  | VDD3P3   | 3.3V | Power supply |
| 27  | GPIO18   | USB D- test pad | Same as pin 21 |
| 28  | GPIO19   | USB D+ test pad | Same as pin 20 |
| 29  | GND      | GND | |
| 30  | GND      | GND | |
| 31  | GND      | GND | |
| 32  | GND      | GND | |
| PAD | GND      | GND | Exposed pad, multiple vias |

**NOTE on pin numbering**: The ESP32-C3FH4 QFN-32 pin numbering follows the Espressif
datasheet. Verify exact pin locations against the datasheet before layout. The GPIO numbers
above are the logical GPIO numbers, not physical pin numbers. Cross-reference with the
ESP32-C3 datasheet Table "QFN32 Pin Description".

### Decoupling Capacitors for ESP32-C3

| Capacitor | Value | Package | Rail | Placement |
|-----------|-------|---------|------|-----------|
| C6 | 100nF | 0402 | VDD3P3 (pin 10) | Adjacent to pin |
| C7 | 100nF | 0402 | VDD_SPI (pin 13) | Adjacent to pin |
| C8 | 100nF | 0402 | VDD3P3_RTC (pin 22) | Adjacent to pin |

---

## 3. RF Transceiver — SX1281IMLTRT (U3)

LCSC: C2151551 | Package: QFN-24, 4x4mm | LDO Mode

### SX1281 Pin Table

| Pin | Name    | Connection | Notes |
|-----|---------|------------|-------|
| 1   | VDD     | 3.3V + C9 (100nF 0402) | Supply |
| 2   | VDD_IN  | 3.3V + C10 (100nF 0402) | Supply |
| 3   | NRESETn | ESP32-C3 GPIO2 + R3 (10k) to 3.3V | Active low reset |
| 4   | BUSY    | ESP32-C3 GPIO3 | Busy indicator |
| 5   | DIO1    | ESP32-C3 GPIO5 | Interrupt output |
| 6   | DIO2    | NC | Not used |
| 7   | DIO3    | NC | Not used |
| 8   | GND     | GND | |
| 9   | GND     | GND | |
| 10  | VR_PA   | C11 (470nF 0402) to GND | LDO mode: cap only, no inductor |
| 11  | VDD     | 3.3V + C12 (100nF 0402) | Supply |
| 12  | XTA     | 52MHz TCXO output | Clock input |
| 13  | XTB     | NC (floating) | Not used with TCXO |
| 14  | GND     | GND | |
| 15  | RFIO    | DEA102700LT-6307A2 (FL1) to RFX2401C TXRX (pin 4) | RF I/O, 50 ohm, via LPF |
| 16  | MISO    | ESP32-C3 GPIO6 | SPI data out |
| 17  | MOSI    | ESP32-C3 GPIO7 | SPI data in |
| 18  | SCK     | ESP32-C3 GPIO4 | SPI clock |
| 19  | NSS     | ESP32-C3 GPIO8 + R4 (10k) to 3.3V | SPI chip select, active low |
| 20  | GND     | GND | |
| 21  | GND     | GND | |
| 22  | GND     | GND | |
| 23  | GND     | GND | |
| 24  | GND     | GND | |
| PAD | GND     | GND | Exposed pad, multiple vias |

### SX1281 LDO Mode Configuration

In LDO mode, VR_PA (pin 10) gets a 470nF decoupling cap to GND. No external inductor.
This is simpler than DC-DC mode but slightly less efficient at high TX power. Acceptable
for an ELRS receiver where TX duty cycle is low (telemetry only).

### SX1281 Decoupling Summary

| Capacitor | Value | Package | Pin | Placement |
|-----------|-------|---------|-----|-----------|
| C9  | 100nF | 0402 | Pin 1 (VDD) | Adjacent |
| C10 | 100nF | 0402 | Pin 2 (VDD_IN) | Adjacent |
| C11 | 470nF | 0402 | Pin 10 (VR_PA) | Adjacent |
| C12 | 100nF | 0402 | Pin 11 (VDD) | Adjacent |

---

## 4. Front-End Module — RFX2401C (U4)

LCSC: C19213 | Package: QFN-16, 3x3x0.55mm | 2.4GHz PA+LNA+Switch

**NOTE**: The user spec originally called for SE2431L-R (LCSC C2649471, QFN-24 3x4mm).
That part is discontinued and out of stock at LCSC. The RFX2401C is pin-compatible in
function (same manufacturer, same feature set), is QFN-16 3x3mm, is in stock at LCSC
(C19213, ~57k units, $0.90), and is what most ELRS receivers actually use.

### RFX2401C Pin Table

| Pin | Name | Connection | Notes |
|-----|------|------------|-------|
| 1   | N/C  | GND or float | Not connected internally |
| 2   | GND  | GND | |
| 3   | GND  | GND | |
| 4   | TXRX | DEA102700LT-6307A2 (FL1) to SX1281 RFIO (pin 15) | RF to/from transceiver via LPF, 50 ohm, DC shorted to GND |
| 5   | TXEN | ESP32-C3 GPIO1 via R5 (10k series) | TX enable, active high. CMOS 1.2V logic. |
| 6   | RXEN | ESP32-C3 GPIO0 via R6 (10k series) | RX enable, active high |
| 7   | N/C  | GND or float | Not connected internally |
| 8   | GND  | GND | |
| 9   | GND  | GND | |
| 10  | ANT  | C15 (0.3pF shunt to GND) then UFL connector | 50 ohm antenna port, DC shorted to GND. C15 is MANDATORY for CE. |
| 11  | GND  | GND | |
| 12  | N/C  | GND or float | Not connected internally |
| 13  | DNC  | Do not connect | Leave floating |
| 14  | VDD  | 3.3V (alternate supply, internally connected to pin 16) | Optional |
| 15  | N/C  | GND or float | Not connected internally |
| 16  | VDD  | 3.3V | Primary supply |
| 17 (PAD) | GND | GND | Exposed ground pad, multiple thermal vias required |

### RFX2401C Control Logic

| Mode     | TXEN | RXEN |
|----------|------|------|
| TX       | 1    | X    |
| RX       | 0    | 1    |
| Shutdown | 0    | 0    |

In ELRS firmware, these are configured as GPIO_PIN_TX_ENABLE and GPIO_PIN_RX_ENABLE
in the hardware target definition (hardware.json).

### RFX2401C Decoupling

| Capacitor | Value | Package | Pin | Placement |
|-----------|-------|---------|-----|-----------|
| C13 | 1uF   | 0402 | Pin 16 (VDD) | Adjacent to VDD |
| C14 | 220pF | 0402 | Pin 16 (VDD) | Adjacent, high-freq bypass |

Both capacitors placed as close as possible to VDD pin with short ground returns via the
exposed pad.

### RFX2401C Harmonic Filter

**MANDATORY**: C15 (0.3pF C0G 0402) shunt cap to GND on ANT pin (pin 10). This is the
5th harmonic filter required for CE compliance per the RFX2401C eval board design.
Do not omit.

```
    RFX2401C ANT (pin 10) ── C15 (0.3pF 0402) ── GND
                     │
                UFL Connector
```

The DEA102700LT-6307A2 LPF between SX1281 RFIO and RFX2401C TXRX handles in-band
filtering and impedance matching. The 0.3pF shunt on ANT handles remaining harmonic
suppression on the antenna side. No additional SAW or LC filter network is needed.

---

## 5. TCXO — 52MHz (Y2)

LCSC: C22434896 | YXC OW7EL89CENUNFAYLC-52M | Package: SMD2016 (2.0x1.6mm) | 3.3V, +/-0.5ppm

```
    ┌────────────┐
    │ 1: VCC     ├── 3.3V + C16 (100nF 0402)
    │ 2: GND     ├── GND
    │ 3: OUT     ├── SX1281 XTA (pin 12)
    │ 4: EN/NC   ├── 3.3V (or NC, check datasheet)
    └────────────┘
```

### TCXO Pin Table

| Pin | Name | Connection | Notes |
|-----|------|------------|-------|
| 1   | VCC  | 3.3V + C16 (100nF) | Power supply |
| 2   | GND  | GND | |
| 3   | OUT  | SX1281 XTA (pin 12) | 52MHz clock output |
| 4   | EN   | 3.3V or NC | Enable (active high) or NC |

---

## 6. 40MHz Crystal (Y1)

For ESP32-C3FH4 main clock.

LCSC: C2875272 | CJ17-400001010B20 | Package: SMD1612-4P | 40MHz, 10pF, +/-10ppm

### Crystal Circuit

| Component | Value | Package | Connection |
|-----------|-------|---------|------------|
| Y1 | 40MHz | SMD3225 | XTAL_P to XTAL_N |
| CX1 | 10pF | 0402 | XTAL_P to GND |
| CX2 | 10pF | 0402 | XTAL_N to GND |

Place crystal and load caps as close as possible to ESP32-C3 XTAL pins. Guard ring
the crystal traces with ground.

---

## 7. LPF — DEA102700LT-6307A2 (FL1)

LCSC: C574024 | Package: 0402 | 2.4GHz integrated low-pass filter

Placed between SX1281 RFIO (pin 15) and RFX2401C TXRX (pin 4). In the current
schematic it is the fitted low-pass element, but it should not be described as a
Semtech-specific one-part SX1281 matching solution.

```
    SX1281 RFIO (pin 15) ── FL1 ── RFX2401C TXRX (pin 4)
```

This replaces what earlier revisions called a "SAW filter" in the transceiver-to-FEM
path. The antenna-side harmonic filtering is handled by C15 (0.3pF shunt on ANT pin).

---

## 8. UFL/IPEX Connector (J1)

LCSC: C88374 | Package: SMD | U.FL receptacle

```
    Signal pin ── RFX2401C ANT (via C15 shunt)
    GND pins ── GND (multiple pads)
```

Standard UFL/IPEX1 footprint. Signal trace from RFX2401C ANT pin to connector must be
50 ohm controlled impedance. On 2-layer 1.0mm FR4, this is approximately 0.5mm
trace width over ground plane (verify with impedance calculator for actual stackup).

---

## 9. XL-1010RGBC-WS2812B RGB LED (LED1)

LCSC: C5349953 | Package: 1010 (1.0x1.0mm)

```
    ┌────────────┐
    │ 1: VDD     ├── 5V (XL-1010RGBC needs 3.5-5.3V supply)
    │ 2: DOUT    ├── NC (single LED, no chain)
    │ 3: GND     ├── GND
    │ 4: DIN     ├── ESP32-C3 GPIO10
    └────────────┘
```

**IMPORTANT**: XL-1010RGBC-WS2812B VDD range is 3.5-5.3V. At 3.3V it is out of spec and may
not work reliably. Options:
1. Power from 5V rail (before LDO) — requires 5V always present
2. Use WS2812C-2020 variant which works down to 3.3V
3. Use a level shifter on DIN (unnecessary complexity)

Recommended: Power LED1 VDD from 5V (input rail), use a 100nF decoupling cap (C17).
The ESP32-C3 GPIO10 output (3.3V logic) is within the WS2812B input threshold when
VDD=5V (VIH = 0.7*VDD = 3.5V, marginal). Consider R7 (470 ohm) series resistor on DIN.

| Component | Value | Package | Connection |
|-----------|-------|---------|------------|
| C17 | 100nF | 0402 | LED1 VDD to GND |
| R7  | 470R  | 0402 | GPIO10 to LED1 DIN |

---

## 10. Solder Pads (J2)

1.27mm pitch edge pads for FC connection:

```
    Pad 1: 5V   (VIN to LDO)
    Pad 2: GND
    Pad 3: TX   (ESP32-C3 GPIO21, UART TX to FC)
    Pad 4: RX   (ESP32-C3 GPIO20, UART RX from FC)
```

---

## 11. SPI Bus Connections Summary

```
    ESP32-C3          SX1281
    ────────          ──────
    GPIO4  (SCK)  ──► Pin 18 (SCK)
    GPIO6  (MISO) ◄── Pin 16 (MISO)
    GPIO7  (MOSI) ──► Pin 17 (MOSI)
    GPIO8  (NSS)  ──► Pin 19 (NSS)   + R4 (10k) pull-up to 3.3V
    GPIO5  (IRQ)  ◄── Pin 5  (DIO1)
    GPIO2  (RST)  ──► Pin 3  (NRESETn) + R3 (10k) pull-up to 3.3V
    GPIO3  (BUSY) ◄── Pin 4  (BUSY)
```

---

## 12. Control Signals Summary

```
    ESP32-C3          RFX2401C
    ────────          ────────
    GPIO1  (TXEN) ──► Pin 5  (TXEN)  via R5 (10k series)
    GPIO0  (RXEN) ──► Pin 6  (RXEN)  via R6 (10k series)
```

Note: R5/R6 are series current-limiting resistors per Skyworks recommendation.
The RFX2401C control pins are CMOS inputs with VIH >= 1.2V, VIL <= 0.3V.
ESP32-C3 GPIO output is 3.3V, well within spec.

---

## 13. ELRS Firmware Hardware Definition

For ExpressLRS `hardware.json`:

```json
{
    "serial_rx": 20,
    "serial_tx": 21,
    "radio_busy": 3,
    "radio_dio1": 5,
    "radio_miso": 6,
    "radio_mosi": 7,
    "radio_nss": 8,
    "radio_rst": 2,
    "radio_sck": 4,
    "power_rxen": 0,
    "power_txen": 1,
    "led": 10
}
```

---

## 14. Complete Passive Component List

| Ref | Value | Package | Description | Location |
|-----|-------|---------|-------------|----------|
| C1  | 1uF   | 0402 | X5R 10V, LDO input local | TLV755 IN |
| C2  | 10uF  | 0603 | X5R 10V, 5V rail bulk | 5V entry |
| C3  | 1uF   | 0402 | X5R 10V, LDO output local | TLV755 OUT |
| C4  | 10uF  | 0603 | X5R 10V, 3.3V rail bulk | Near ESP32 |
| C5  | 1uF   | 0402 | X7R 16V, EN RC delay | ESP32-C3 EN |
| C6  | 100nF | 0402 | X7R 16V, MCU decoupling | ESP32-C3 VDD3P3 |
| C7  | 100nF | 0402 | X7R 16V, MCU decoupling | ESP32-C3 VDD_SPI |
| C8  | 100nF | 0402 | X7R 16V, MCU decoupling | ESP32-C3 VDD3P3_RTC |
| C9  | 100nF | 0402 | X7R 16V, SX1281 decoupling | SX1281 pin 1 VDD |
| C10 | 100nF | 0402 | X7R 16V, SX1281 decoupling | SX1281 pin 2 VDD_IN |
| C11 | 470nF | 0402 | X7R 16V, SX1281 LDO mode | SX1281 pin 10 VR_PA |
| C12 | 100nF | 0402 | X7R 16V, SX1281 decoupling | SX1281 pin 11 VDD |
| C13 | 1uF   | 0402 | X5R 16V, FEM decoupling | RFX2401C pin 16 VDD |
| C14 | 220pF | 0402 | C0G/NP0 16V, FEM HF bypass | RFX2401C pin 16 VDD |
| C15 | 0.3pF | 0402 | C0G/NP0, 5th harmonic | RFX2401C ANT pin 10 |
| C16 | 100nF | 0402 | X7R 16V, TCXO decoupling | TCXO VCC |
| C17 | 100nF | 0402 | X7R 16V, LED decoupling | WS2812B VDD |
| CX1 | 10pF  | 0402 | C0G/NP0 50V, crystal load | ESP32-C3 XTAL_P |
| CX2 | 10pF  | 0402 | C0G/NP0 50V, crystal load | ESP32-C3 XTAL_N |
| R1  | 10k   | 0402 | 1%, EN pull-up | ESP32-C3 EN to 3.3V |
| R2  | 10k   | 0402 | 1%, boot pull-up | ESP32-C3 GPIO9 to 3.3V |
| R3  | 10k   | 0402 | 1%, reset pull-up | SX1281 NRESET to 3.3V |
| R4  | 10k   | 0402 | 1%, NSS pull-up | SX1281 NSS to 3.3V |
| R5  | 10k   | 0402 | 1%, TXEN series | GPIO1 to RFX2401C TXEN |
| R6  | 10k   | 0402 | 1%, RXEN series | GPIO0 to RFX2401C RXEN |
| R7  | 470R  | 0402 | 1%, LED series | GPIO10 to WS2812B DIN |

---

## 15. Power Budget Estimate

| Block | Current (typ) | Current (max) | Notes |
|-------|---------------|---------------|-------|
| ESP32-C3 (active) | 30mA | 80mA | WiFi off, UART+SPI active |
| SX1281 (RX) | 8mA | 10mA | Continuous RX |
| SX1281 (TX) | 30mA | 50mA | Telemetry TX, low duty |
| RFX2401C (RX) | 8mA | 10mA | LNA active |
| RFX2401C (TX) | 90mA | 120mA | PA active, +20dBm |
| TCXO | 2mA | 3mA | Continuous |
| WS2812B | 1mA | 20mA | Depends on color |
| LDO quiescent | 0.04mA | 0.1mA | |
| **Total (RX mode)** | **~49mA** | **~103mA** | Normal operation |
| **Total (TX burst)** | **~161mA** | **~273mA** | Telemetry TX burst |

TLV755 rated 500mA — adequate for all operating modes.

---

## 16. Layout Notes

1. **Ground plane**: Unbroken ground plane on bottom layer. All QFN exposed pads need
   multiple vias (minimum 4 per IC).
2. **RF traces**: 50 ohm controlled impedance from SX1281 RFIO through RFX2401C to
   UFL connector. Keep as short as possible. No sharp bends.
3. **Component placement**: SX1281, DEA LPF (FL1), RFX2401C, and UFL connector should be
   in a straight line to minimize RF trace length.
4. **Decoupling caps**: Place all decoupling caps as close as possible to their respective
   IC power pins with short ground returns.
5. **Crystal**: Guard XTAL traces with ground. Keep traces short and symmetric.
6. **TCXO**: Place close to SX1281 XTA pin. Keep clock trace short.
7. **Power**: Wide traces for 5V and 3.3V rails. Star or solid plane distribution.
8. **50 ohm trace**: On 2-layer 1.0mm FR4 (Er=4.5), approximately 0.5mm trace width
   for 50 ohm microstrip. Verify with JLCPCB impedance calculator.

---

# OpenRX-Nano Bill of Materials

## 2026-03-23 LCSC Pricing Snapshot

The previous Nano BOM section was stale and did not match the current KiCad sheet. The table below is based on the current schematic netlist plus current LCSC search results, using the first listed purchasable price tier. Prices exclude VAT, shipping, PCB, and assembly.

| Ref | Part | LCSC | Current LCSC Price | Availability Note |
|-----|------|------|--------------------|-------------------|
| U1 | TLV75533PDQNR | C2861882 | $0.1290 | In stock on the most recent LCSC crawl |
| U2 | ESP32-C3FH4 | C2858491 | $2.2891 | In stock on the most recent LCSC crawl |
| U3 | SX1281IMLTRT | C2151551 | $3.6011 | Most recent LCSC crawl showed out of stock |
| U4 | RFX2401C | C19213 | $0.8604 | In stock on the most recent LCSC crawl |
| X1 | CJ17-400001010B20 | C2875272 | $0.2035 | In stock, but not deep stock |
| OSC1 | OW7EL89CENUNFAYLC-52M | C22434896 | $0.7907 | In stock on the most recent LCSC crawl |
| USB1 | DEA102700LT-6307A2 | C574024 | $0.0952 | In stock on the most recent LCSC crawl |
| JP1 | U.FL-R-SMT-1(80) | C88374 | $0.1286 | In stock on the most recent LCSC crawl |
| AE1 | 2450AT18A100E | C89334 | $0.5293 | Wi-Fi update antenna only in the current sheet |
| D1 | XL-1010RGBC-WS2812B | C5349953 | $0.0732 | Optional |

### Nano Cost Summary

- Base fitted RF/logic subtotal from the current schematic, without optional LED and without passives: `$8.6269`
- With optional LED stuffed: `$8.7001`
- Corrected passives should only add a few cents, but the current passive `LCSC` fields in the schematic are not trustworthy enough for an auto-BOM total yet

### Passive Procurement Status

The Nano schematic passive `LCSC` fields have been corrected. Important current mappings include:

- `100nF 0201` -> `C76939`
- `1uF 0201` -> `C76935`
- `18pF 0201` -> `C62164`
- `1nF 0201` -> `C66942`
- `470nF 0201` -> `C85926`
- `10k 0201` -> `C106225`
- `220pF 0201` -> `C62548`

The remaining Nano RF issue is no longer procurement but topology: the current schematic still does not implement the full explicit `RFX2401C` output harmonic filter from the Skyworks reference design.

### Current Procurement Verdict

- The current Nano is not a `EUR 5-6` receiver. With the fitted parts now in the sheet, it is roughly an `$8.7` class BOM before PCB and assembly.
- Nano is currently slightly cheaper than Lite because Lite still carries the more expensive Molex antenna/feed part, while Nano uses a cheaper `U.FL` output.
- The most important availability blocker is still `SX1281IMLTRT`, because the most recent LCSC crawl showed it out of stock.
