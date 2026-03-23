# OpenRX-PWM Schematic Design

6-channel PWM ExpressLRS 2.4GHz receiver for fixed wing, helicopters, and surface vehicles.

- Band: 2.4GHz (SX1281)
- MCU: ESP32-C3FH4 (QFN-32)
- RF Front-end: SE2431L-R (LNA+PA, 100mW telemetry)
- PWM Outputs: 5 or 6 channels (50-400Hz servo/ESC)
- PCB: 30x20mm, 4-layer, 1.0mm
- Input: 4.5-10V (BEC or receiver battery)

## GPIO Allocation

The ESP32-C3FH4 has 15 usable GPIOs: GPIO0-10, GPIO18-21. This is the hardest constraint in the design. Every GPIO assignment is a trade-off.

### Fixed allocations (non-negotiable for ELRS SX1281 operation)

| GPIO | Function | Notes |
|------|----------|-------|
| GPIO4 | SX1281 SCK | SPI clock |
| GPIO6 | SX1281 MISO | SPI data in |
| GPIO7 | SX1281 MOSI | SPI data out |
| GPIO8 | SX1281 NSS | SPI chip select |
| GPIO2 | SX1281 NRESET | Radio reset, 10k pull-up |
| GPIO3 | SX1281 BUSY | Radio busy flag |
| GPIO5 | SX1281 DIO1 | Radio interrupt |
| GPIO20 | UART RX | CRSF input (binding, config) |
| GPIO21 | UART TX | CRSF telemetry output |

That is 9 GPIOs consumed. 6 remain: GPIO0, GPIO1, GPIO9, GPIO10, GPIO18, GPIO19.

### The SE2431L control problem

The SE2431L front-end requires two control signals: TXEN and RXEN. ELRS firmware uses `GPIO_PIN_TX_ENABLE` and `GPIO_PIN_RX_ENABLE` for these.

Dedicating 2 GPIOs to SE2431L control leaves only 4 GPIOs for PWM -- not enough for 6 channels.

### Option A: 5-channel PWM with dedicated SE2431L control (recommended)

| GPIO | Function | Notes |
|------|----------|-------|
| GPIO0 | PWM CH1 | Servo output |
| GPIO1 | PWM CH2 | Servo output |
| GPIO9 | PWM CH3 | Boot strapping pin, 10k pull-up required. After boot, usable as PWM. No physical boot button -- enter bootloader via WiFi or UART |
| GPIO18 | PWM CH4 | Sacrifices USB D- test pad |
| GPIO19 | PWM CH5 | Sacrifices USB D+ test pad |
| GPIO10 | SE2431L TXEN | TX enable for PA |
| (hardwire) | SE2431L RXEN | Tied HIGH via 10k pull-up. LNA always on in RX, PA overrides when TXEN asserted |

Trade-offs:
- 5 PWM channels (sufficient for most fixed wing: aileron, elevator, rudder, throttle, flap/gear)
- USB test pads sacrificed (WiFi OTA is primary update method anyway)
- No boot button (bridge pads or use WiFi/UART for bootloader entry)
- No WS2812B LED (acceptable for PWM receiver, use simple LED on 3.3V rail)
- RXEN hardwired HIGH means LNA is always enabled in RX mode, slight extra current draw during TX but SE2431L datasheet confirms this is safe

### Option B: 6-channel PWM with DIO2-based antenna switching

| GPIO | Function | Notes |
|------|----------|-------|
| GPIO0 | PWM CH1 | Servo output |
| GPIO1 | PWM CH2 | Servo output |
| GPIO9 | PWM CH3 | Boot strapping pin with pull-up |
| GPIO10 | PWM CH4 | Sacrifices LED |
| GPIO18 | PWM CH5 | Sacrifices USB D- |
| GPIO19 | PWM CH6 | Sacrifices USB D+ |

SE2431L control via SX1281 DIO2:
- SX1281 DIO2 can be configured to output TX/RX state automatically
- DIO2 directly drives TXEN on SE2431L
- RXEN hardwired HIGH via 10k pull-up
- DIO2 directly drives TXEN (active high during TX, low during RX)

Trade-offs:
- 6 PWM channels
- Depends on SX1281 DIO2 auto-TX/RX indication feature
- ELRS firmware must support DIO2-based antenna switching (verify in target config)
- If DIO2 mode is not supported in ELRS for this use case, this option fails
- No status LED at all

### Option C: External PWM expander (PCA9685)

- PCA9685 (I2C, 16-channel PWM) on GPIO0 (SDA) + GPIO1 (SCL)
- Provides 16 PWM channels, only need 6
- Adds BOM cost (~$1), board area, I2C latency (~1ms)
- ELRS firmware does NOT natively support PCA9685 output
- Would require custom firmware -- not viable for a standard ELRS receiver

**Verdict: Option A (5-channel) is the safe choice. Option B (6-channel) is viable if DIO2 antenna switching is confirmed in ELRS firmware. Document both on the schematic with 0-ohm resistor selection.**

### Recommended implementation: Dual-option with 0R selection

Place 0-ohm resistors to allow factory selection:
- R_OPT1: GPIO10 to SE2431L TXEN (Option A, populate for 5ch)
- R_OPT2: GPIO10 to PWM CH4 header (Option B, populate for 6ch)
- R_OPT3: SX1281 DIO2 to SE2431L TXEN (Option B, populate for 6ch)

Default populate for Option A (5-channel with dedicated SE2431L control).

## Power Supply

### Input stage

Input voltage: 4.5-10V from BEC or receiver battery (2S-3S LiPo compatible).

```
VIN ──┬── C1 22uF/16V ──┬── GND
      │                  │
      ├── C2 100nF/16V ──┘
      │
      ├── D1 (reverse polarity, Schottky SS14 or equivalent, optional)
      │
      └── LDO VIN
```

### Voltage regulator

Primary: AMS1117-3.3 (LCSC C6186, SOT-223)
- VIN max: 15V (sufficient for 3S LiPo)
- Output: 3.3V, 1A
- Dropout: 1.1V at 1A
- Minimum input for regulation: 4.4V (3.3V + 1.1V dropout)

Alternative: AP2112K-3.3TRG1 (LCSC C51118, SOT-23-5)
- VIN max: 6V (NOT suitable for direct 2S/3S without additional regulation)
- Output: 3.3V, 600mA
- Dropout: 250mV
- Better for efficiency but limited input voltage range

**Use AMS1117-3.3 for this design.** The higher input voltage range is critical for fixed wing where power comes from BEC (typically 5-8.4V) or direct battery.

```
VIN ──── AMS1117 VIN (pin 3)
         AMS1117 VOUT (pin 2) ──┬── C3 22uF/10V ──┬── GND
                                │                  │
                                ├── C4 100nF ──────┘
                                │
                                └── 3.3V rail
         AMS1117 GND (pin 1) ──── GND
         AMS1117 TAB (pin 4) ──── GND
```

### Power budget (3.3V rail)

| Component | Typical | Peak |
|-----------|---------|------|
| ESP32-C3 (WiFi off) | 30mA | 80mA |
| ESP32-C3 (WiFi active) | 120mA | 350mA |
| SX1281 (RX mode) | 7mA | 10mA |
| SX1281 (TX 12.5dBm) | 40mA | 45mA |
| SE2431L (RX, LNA) | 5mA | 8mA |
| SE2431L (TX, PA) | 110mA | 140mA |
| TCXO | 1.5mA | 2mA |
| **Total (normal RX)** | **~45mA** | **~100mA** |
| **Total (WiFi config)** | **~160mA** | **~450mA** |
| **Total (TX telemetry)** | **~185mA** | **~500mA** |

AMS1117 at 1A is sufficient with margin. At 10V input, worst case dissipation: (10V - 3.3V) * 0.5A = 3.35W. This is too high for sustained WiFi+TX operation at high input voltage. In practice, TX telemetry is brief bursts and WiFi config is rare. Thermal pad on SOT-223 helps.

## SX1281 Radio (LDO Mode)

QFN-24, 4x4mm. LDO mode (simpler, no external inductor needed).

```
Pin 1  VDD      → 3.3V + C5 100nF
Pin 2  VDD_IN   → 3.3V + C6 100nF
Pin 3  NRESETn  → ESP32-C3 GPIO2 + R1 10k pull-up to 3.3V
Pin 4  BUSY     → ESP32-C3 GPIO3
Pin 5  DIO1     → ESP32-C3 GPIO5
Pin 6  DIO2     → SE2431L TXEN (Option B) or NC (Option A)
Pin 7  DIO3     → NC
Pin 8  GND_RFI  → GND (RF ground, short via to ground plane)
Pin 9  VR_PA    → C7 470nF to GND (PA regulator decoupling)
Pin 10 VR_PA    → C7 (same cap as pin 9, pins are internally connected)
Pin 11 GND      → GND
Pin 12 XTA      → TCXO output (52MHz)
Pin 13 XTB      → NC (floating, TCXO mode)
Pin 14 GND      → GND
Pin 15 RFIO     → SE2431L RF_IN (via DC block + matching)
Pin 16 MISO     → ESP32-C3 GPIO6
Pin 17 MOSI     → ESP32-C3 GPIO7
Pin 18 SCK      → ESP32-C3 GPIO4
Pin 19 NSS      → ESP32-C3 GPIO8 + R2 10k pull-up to 3.3V
Pin 20-24 GND   → GND
Pad    GND      → GND (exposed pad, solid ground plane connection)
```

### SX1281 decoupling

- C5: 100nF, 0402, close to pin 1
- C6: 100nF, 0402, close to pin 2
- C7: 470nF, 0402, close to pins 9/10

### TCXO

52MHz TCXO, 2.0x1.6mm or 2.5x2.0mm package.

Recommended: TXC 7X-52.000MBB-T or equivalent LCSC basic part.

```
TCXO VCC  → 3.3V + C8 100nF
TCXO OUT  → SX1281 XTA (Pin 12)
TCXO GND  → GND
TCXO EN   → 3.3V (always on) or NC if no enable pin
```

## SE2431L Front-End

QFN-16, 3x3mm. Integrated LNA + PA for 2.4GHz.

```
Pin 1  VDD      → 3.3V + C9 100nF
Pin 2  RXEN     → 10k pull-up to 3.3V (hardwired HIGH) [Option A]
                   or ESP32-C3 GPIO (if GPIOs allow)
Pin 3  TXEN     → ESP32-C3 GPIO10 [Option A]
                   or SX1281 DIO2 [Option B]
Pin 4  ANTSEL   → GND (single antenna)
Pin 5  ANT      → SAW filter → UFL connector
Pin 6  GND      → GND
Pin 7  GND      → GND
Pin 8  RF_IN    → SX1281 RFIO (Pin 15) via DC block cap + matching
Pin 9  GND      → GND
Pin 10 BYPASS   → C10 10nF to GND (internal regulator bypass)
Pin 11 VDD      → 3.3V + C11 100nF
Pin 12 GND      → GND
Pad    GND      → GND (exposed pad)
```

### RF matching: SX1281 RFIO to SE2431L RF_IN

```
SX1281 RFIO ── C_DC 100pF ── L_MATCH ── SE2431L RF_IN
                                │
                             C_MATCH to GND
```

Values depend on PCB stackup. Start with Semtech reference: C_DC = 100pF, L_MATCH = 1.2nH, C_MATCH = open (DNP). Tune on VNA.

### RF output: SE2431L ANT to antenna connector

```
SE2431L ANT ── SAW filter (2.4GHz BPF) ── UFL/IPEX connector
```

SAW filter: 2.4GHz bandpass, e.g., Johanson 2450BP07A0100T or LCSC equivalent.

## Battery Voltage Sensing

Voltage divider from VIN to ESP32-C3 ADC.

```
VIN ── R3 100k ──┬── R4 10k ── GND
                 │
                 └── ESP32-C3 ADC (GPIO1 in Option A, or GPIO0)
                     + C12 100nF (anti-alias filter)
```

- Divider ratio: 10k / (100k + 10k) = 1/11
- For 2S LiPo (6.0-8.4V): ADC sees 0.55-0.76V
- For 3S LiPo (9.0-12.6V): ADC sees 0.82-1.15V
- ESP32-C3 ADC with 11dB attenuation: 0-2.5V range, sufficient

Note: If using Option A (5-channel), GPIO1 is used for PWM CH2. Use GPIO0 for ADC and reduce to 4 PWM channels, OR add the voltage divider to the UART TX pin (GPIO21) and read it only during startup before UART is initialized. The cleanest solution is to sacrifice one PWM channel for battery sensing.

**Revised Option A with battery sensing:**

| GPIO | Function |
|------|----------|
| GPIO0 | PWM CH1 |
| GPIO1 | VBat ADC (voltage divider) |
| GPIO9 | PWM CH2 |
| GPIO10 | SE2431L TXEN |
| GPIO18 | PWM CH3 |
| GPIO19 | PWM CH4 |

This gives 4 PWM + battery sensing + SE2431L control. For 5 PWM without battery sensing, move GPIO1 back to PWM CH2.

**Alternatively, if battery sensing is critical (it is for telemetry), accept 4 PWM channels as the default configuration with SE2431L control:**

| GPIO | Function | Notes |
|------|----------|-------|
| GPIO0 | PWM CH1 | |
| GPIO1 | VBat ADC | Voltage divider, battery telemetry |
| GPIO9 | PWM CH2 | Boot pin with pull-up |
| GPIO10 | SE2431L TXEN | PA control |
| GPIO18 | PWM CH3 | |
| GPIO19 | PWM CH4 | |

4 channels covers: aileron, elevator, throttle, rudder. Most fixed wing is fine with 4.

## PWM Output Protection

Each PWM output pin:

```
ESP32-C3 GPIO ── R 100R ── servo header signal pin
                    │
                 D_TVS (ESD, optional) ── GND
```

- R: 100 ohm, 0402. Limits current if servo wire is shorted or ESD event.
- D_TVS: Optional ESD protection diode (PESD5V0S1BSF or similar). Only needed if long servo leads are expected (>30cm).

## Servo Connectors

6x 3-pin headers (2.54mm pitch), one per channel.

Each header:
```
Pin 1: Signal (from PWM GPIO via 100R series resistor)
Pin 2: +V (VIN pass-through, NOT 3.3V)
Pin 3: GND
```

All +V pins connected to VIN input (battery/BEC pass-through). Servos run on input voltage, not 3.3V.

All GND pins connected to main ground plane.

Header arrangement: Single row of 6 headers along one edge of the 30x20mm board, or dual rows of 3. Single row preferred for fixed wing installations.

## ESP32-C3FH4 Supporting Circuits

### CHIP_EN (Enable)

```
3.3V ── R5 10k ──┬── C13 1uF ── GND
                 │
                 └── ESP32-C3 CHIP_EN
```

RC delay per Espressif hardware design guidelines. Ensures clean power-on reset.

### Boot mode (GPIO9)

GPIO9 is a strapping pin. Must be HIGH during boot for normal SPI flash boot.

```
3.3V ── R6 10k ── GPIO9
```

If GPIO9 is used for PWM output (Options A/B), the pull-up ensures normal boot. Servo load will not pull GPIO9 low enough to trigger download mode (servo input impedance >> 10k).

For firmware flashing: use WiFi OTA (primary) or UART bootloader (hold GPIO9 low during reset via test pads).

### Boot/flash test pads

Place test pads (no headers, just exposed pads) for:
- GPIO9 (boot mode control)
- UART TX (GPIO21)
- UART RX (GPIO20)
- GND
- 3.3V
- CHIP_EN (for manual reset)

### USB (optional test pads only)

GPIO18/GPIO19 are used for PWM. USB is not available in normal operation.

If needed for debug, place test pads for USB D-/D+ (GPIO18/GPIO19) that can be temporarily connected. In production, these are PWM outputs.

### Status LED

With GPIO10 used for SE2431L TXEN (Option A) or PWM CH4 (Option B), there is no spare GPIO for a WS2812B LED.

Use a simple LED on the 3.3V power rail:
```
3.3V ── R7 1k ── LED (green, 0402) ── GND
```

This indicates power-on only, no firmware-controlled blinking. Acceptable for a PWM receiver where the user cares about servo movement, not LED patterns.

## Antenna

UFL/IPEX MHF1 connector.

```
SE2431L ANT ── SAW filter ── 50R trace ── UFL connector
```

- 50 ohm matched trace from SAW filter to UFL
- Trace impedance controlled by 4-layer stackup (signal-gnd-gnd-signal or signal-gnd-pwr-signal)
- Keep trace as short as possible (<10mm)
- Ground plane continuous under RF trace, no splits

## Decoupling Summary

| Ref | Value | Package | Location |
|-----|-------|---------|----------|
| C1 | 22uF/16V | 0805 | VIN input, near LDO |
| C2 | 100nF/16V | 0402 | VIN input, near LDO |
| C3 | 22uF/10V | 0805 | 3.3V output, near LDO |
| C4 | 100nF | 0402 | 3.3V output, near LDO |
| C5 | 100nF | 0402 | SX1281 VDD (pin 1) |
| C6 | 100nF | 0402 | SX1281 VDD_IN (pin 2) |
| C7 | 470nF | 0402 | SX1281 VR_PA (pins 9/10) |
| C8 | 100nF | 0402 | TCXO VCC |
| C9 | 100nF | 0402 | SE2431L VDD (pin 1) |
| C10 | 10nF | 0402 | SE2431L BYPASS (pin 10) |
| C11 | 100nF | 0402 | SE2431L VDD (pin 11) |
| C12 | 100nF | 0402 | VBat ADC anti-alias |
| C13 | 1uF | 0402 | ESP32-C3 CHIP_EN RC delay |

## Net List Summary

| Net Name | Description |
|----------|-------------|
| VIN | Battery/BEC input, 4.5-10V |
| +3V3 | Regulated 3.3V rail |
| GND | Ground |
| SPI_SCK | SX1281 SPI clock |
| SPI_MISO | SX1281 SPI data out |
| SPI_MOSI | SX1281 SPI data in |
| SPI_NSS | SX1281 SPI chip select |
| RADIO_NRST | SX1281 reset |
| RADIO_BUSY | SX1281 busy |
| RADIO_DIO1 | SX1281 interrupt |
| RADIO_DIO2 | SX1281 DIO2 (Option B: TXEN) |
| TXEN | SE2431L TX enable |
| RXEN | SE2431L RX enable (hardwired HIGH) |
| RFIO | SX1281 to SE2431L RF path |
| ANT | SE2431L to antenna |
| CRSF_RX | UART RX from TX module |
| CRSF_TX | UART TX telemetry |
| VBAT_SENSE | Voltage divider output to ADC |
| PWM_CH1-6 | PWM output nets |

## PCB Stackup (4-layer, 1.0mm, JLCPCB JLC04161H-7628)

| Layer | Function | Thickness |
|-------|----------|-----------|
| F.Cu | Signal + RF | 0.035mm |
| Prepreg | 7628 | 0.2104mm |
| In1.Cu | GND plane | 0.035mm |
| Core | | 0.45mm |
| In2.Cu | Power (3.3V, VIN) | 0.035mm |
| Prepreg | 7628 | 0.2104mm |
| B.Cu | Signal + servo headers | 0.035mm |

Total: ~1.0mm

RF traces on F.Cu with continuous GND plane on In1.Cu directly beneath. This gives controlled impedance for 50 ohm traces.

## Design Checklist

- [ ] ESP32-C3 CHIP_EN RC delay (10k + 1uF)
- [ ] GPIO9 pull-up (10k) for normal boot
- [ ] SX1281 NSS pull-up (10k) for defined state during ESP32 boot
- [ ] SX1281 NRESET pull-up (10k)
- [ ] SX1281 VR_PA decoupling (470nF)
- [ ] SE2431L RXEN pull-up (10k) if hardwired
- [ ] All GND pads/pins connected to ground plane with multiple vias
- [ ] RF trace impedance matched (50 ohm)
- [ ] No ground plane splits under RF traces
- [ ] Decoupling caps placed within 1mm of IC power pins
- [ ] Servo header +V connected to VIN, not 3.3V
- [ ] PWM outputs have 100R series protection resistors
- [ ] VBat voltage divider sized for 2S-3S range within ADC input range
- [ ] Test pads for UART, boot, reset, power
- [ ] Thermal relief on LDO ground pad
