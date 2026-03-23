# OpenRX-Nano Schematic Design Document

> Audit note: for current ExpressLRS unified RX targets, the front-end control keys are `power_rxen` and `power_txen`, not `rx_en` and `tx_en`.

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
(LCSC C574024, 0402 integrated LPF) provides impedance matching and low-pass filtering.
No discrete matching network or separate SAW filter needed — this single component replaces
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

Crystal: SMD3225, 40MHz, 10pF load, +/-10ppm (e.g. JGHC S3240000101040, LCSC C426988)

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

LCSC: C426988 | JGHC S3240000101040 | Package: SMD3225 | 40MHz, 10pF, +/-10ppm

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

Placed between SX1281 RFIO (pin 15) and RFX2401C TXRX (pin 4). Provides impedance
matching and low-pass filtering in a single component. No discrete matching network
needed.

```
    SX1281 RFIO (pin 15) ── FL1 ── RFX2401C TXRX (pin 4)
```

This replaces what earlier revisions called a "SAW filter" in the transceiver-to-FEM
path. The antenna-side harmonic filtering is handled by C15 (0.3pF shunt on ANT pin).

---

## 8. UFL/IPEX Connector (J1)

LCSC: C22418213 | Package: SMD | UFL receptacle

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

> Audit note: this is the current preferred 2.4GHz baseline. Uses RFX2401C with DEA102700LT-6307A2 LPF (replaces earlier SAW filter). Connector choices still need to be reconciled with `CORE_BOM.md` before freezing procurement.

Target BOM cost: EUR 5-6 at quantity 100+

## Active Components

| Ref | Description | MPN | Package | LCSC | Qty | Unit Price (USD) | Notes |
|-----|-------------|-----|---------|------|-----|-------------------|-------|
| U1  | 3.3V 500mA LDO | TLV75533PDQNR | X2SON-4 1x1mm | C2861882 | 1 | $0.15 | TI, Extended |
| U2  | MCU, 4MB flash | ESP32-C3FH4 | QFN-32 5x5mm | C2858491 | 1 | $1.15 | Extended |
| U3  | 2.4GHz LoRa transceiver | SX1281IMLTRT | QFN-24 4x4mm | C2151551 | 1 | $1.80 | Extended |
| U4  | 2.4GHz PA+LNA+Switch | RFX2401C | QFN-16 3x3mm | C19213 | 1 | $0.90 | Extended |
| Y1  | 40MHz crystal, 10pF | S3240000101040 | SMD3225 | C426988 | 1 | $0.06 | Extended |
| Y2  | 52MHz TCXO, 3.3V, ±0.5ppm | OW7EL89CENUNFAYLC-52M | SMD2016 | C22434896 | 1 | $0.42 | Extended |
| FL1 | 2.4GHz LPF | DEA102700LT-6307A2 | 0402 | C574024 | 1 | $0.10 | Extended |
| J1  | UFL/IPEX connector | CONUFL001-SMD-T | SMD | C22418213 | 1 | $0.56 | Extended |
| LED1 | Addressable RGB LED | XL-1010RGBC-WS2812B | 1010 (1x1mm) | C5349953 | 1 | $0.04 | Extended |
| SW1 | Tactile switch (boot) | — | 3x4mm SMD | — | 1 | $0.02 | Any 3x4 tact |

### Active Component Subtotal: ~$5.17

## Passive Components — Capacitors

| Ref | Value | Package | Spec | LCSC | Qty | Notes |
|-----|-------|---------|------|------|-----|-------|
| C1  | 1uF   | 0402 | X5R 10V ±10% | C52923 | 1 | LDO input local (TLV755), basic |
| C2  | 10uF  | 0603 | X5R 10V ±10% | C15525 | 1 | 5V rail bulk, basic |
| C3  | 1uF   | 0402 | X5R 10V ±10% | C52923 | 1 | LDO output local (TLV755), basic |
| C4  | 10uF  | 0603 | X5R 10V ±10% | C15525 | 1 | 3.3V rail bulk, basic |
| C5  | 1uF   | 0402 | X7R 16V ±10% | C52923 | 1 | EN RC delay, basic |
| C6  | 100nF | 0402 | X7R 16V ±10% | C1525 | 1 | ESP32 VDD3P3, basic |
| C7  | 100nF | 0402 | X7R 16V ±10% | C1525 | 1 | ESP32 VDD_SPI, basic |
| C8  | 100nF | 0402 | X7R 16V ±10% | C1525 | 1 | ESP32 VDD3P3_RTC, basic |
| C9  | 100nF | 0402 | X7R 16V ±10% | C1525 | 1 | SX1281 pin 1 VDD, basic |
| C10 | 100nF | 0402 | X7R 16V ±10% | C1525 | 1 | SX1281 pin 2 VDD_IN, basic |
| C11 | 470nF | 0402 | X7R 16V ±10% | C1543 | 1 | SX1281 VR_PA (LDO mode), basic |
| C12 | 100nF | 0402 | X7R 16V ±10% | C1525 | 1 | SX1281 pin 11 VDD, basic |
| C13 | 1uF   | 0402 | X5R 16V ±10% | C52923 | 1 | RFX2401C VDD, basic |
| C14 | 220pF | 0402 | C0G/NP0 50V ±5% | C1604 | 1 | RFX2401C VDD HF, basic |
| C15 | 0.3pF | 0402 | C0G/NP0 50V | — | 1 | 5th harmonic filter, see note |
| C16 | 100nF | 0402 | X7R 16V ±10% | C1525 | 1 | TCXO VCC, basic |
| C17 | 100nF | 0402 | X7R 16V ±10% | C1525 | 1 | WS2812B VDD, basic |
| CX1 | 10pF  | 0402 | C0G/NP0 50V ±5% | C32949 | 1 | 40MHz crystal load, basic |
| CX2 | 10pF  | 0402 | C0G/NP0 50V ±5% | C32949 | 1 | 40MHz crystal load, basic |

**Note on C15 (0.3pF)**: MANDATORY -- do not omit. Required for 5th harmonic suppression
and CE compliance per RFX2401C eval board. 0.3pF C0G 0402 caps exist as standard parts
(check LCSC/Murata GJM series). If unavailable, 0.5pF C0G 0402 (e.g. LCSC C1550) is the
closest standard substitute. RadioMaster Ranger Nano uses 0.3pF.

### Capacitor Subtotal: ~$0.10 (all basic parts, negligible cost)

## Passive Components — Resistors

| Ref | Value | Package | Spec | LCSC | Qty | Notes |
|-----|-------|---------|------|------|-----|-------|
| R1  | 10k | 0402 | ±1% 1/16W | C25744 | 1 | ESP32 EN pull-up, basic |
| R2  | 10k | 0402 | ±1% 1/16W | C25744 | 1 | GPIO9 boot pull-up, basic |
| R3  | 10k | 0402 | ±1% 1/16W | C25744 | 1 | SX1281 NRESET pull-up, basic |
| R4  | 10k | 0402 | ±1% 1/16W | C25744 | 1 | SX1281 NSS pull-up, basic |
| R5  | 10k | 0402 | ±1% 1/16W | C25744 | 1 | TXEN series, basic |
| R6  | 10k | 0402 | ±1% 1/16W | C25744 | 1 | RXEN series, basic |
| R7  | 470R | 0402 | ±1% 1/16W | C25117 | 1 | LED DIN series, basic |

### Resistor Subtotal: ~$0.01

## Connectors / Mechanical

| Ref | Description | Package | LCSC | Qty | Notes |
|-----|-------------|---------|------|-----|-------|
| J1  | UFL/IPEX connector | SMD | C22418213 | 1 | Listed in actives above |
| J2  | Solder pads 4x (5V, GND, TX, RX) | 1.27mm pitch | — | 1 | Copper pads on PCB edge |
| TP1-3 | Test pads (USB D+, D-, GND) | 1.0mm round | — | 3 | Copper pads |

## BOM Cost Summary (USD, qty 100)

| Category | Cost |
|----------|------|
| Active components | $5.17 |
| Passive components | $0.15 |
| **Total BOM** | **~$5.32** |

At current exchange rates (~1 USD = 0.92 EUR), BOM is approximately **EUR 4.90**.
Within the EUR 5-6 target.

## JLCPCB Assembly Notes

- 9 unique active component types (all SMD)
- 19 unique passive component types (mostly 0402, basic parts)
- Total component count: ~30 parts
- Basic parts: TLV755, all 0402 caps and resistors (no setup fee)
- Extended parts: ESP32-C3, SX1281, RFX2401C, crystal, TCXO, DEA LPF, UFL, WS2812B
  (setup fee per unique extended part, ~$3 each)
- Setup fees at qty 100: ~$27 total ($0.27/board)
- PCB cost (20x13mm, 2-layer, 1.0mm, qty 100): ~$0.50/board
- Assembly cost: ~$0.50/board
- **Total per-board cost at qty 100: ~EUR 6.10** (BOM + PCB + assembly + setup)

## Alternate Parts

| Original | Alternative | LCSC | Notes |
|----------|-------------|------|-------|
| RFX2401C (C19213) | SE2431L-R | C2649471 | **Not recommended** -- EOL, low stock, no restock expected |
| DEA102700LT-6307A2 (C574024) | 2450FM07D0034 | C2651081 | Johanson SAW/BPF alternative (functionally equivalent) |
| OW7EL89CENUNFAYLC-52M | ABDFTCXO-52MHz | C568568 | Abracon TCXO, larger package |
| S3240000101040 (C426988) | Any 40MHz 10pF 3225 | C90924 | TXC Corp alternative |
| C22418213 (UFL) | Any IPEX1/UFL receptacle | — | Standard footprint |
| XL-1010RGBC-WS2812B (C5349953) | WS2812C-2020 | — | Works at 3.3V natively |
