# OpenRX-Gemini Schematic Design Document

Date: 2026-03-23
Status: Design phase
Target: Xrossband dual-band simultaneous ExpressLRS receiver

## Overview

The OpenRX-Gemini is a dual-LR1121 receiver for ExpressLRS 4.x Xrossband (simultaneous 868/915MHz + 2.4GHz) and True Diversity modes. It uses an ESP32-C3FH4 MCU with two LR1121 radios on a shared SPI bus, a SE2431L front-end on the 2.4GHz path, and direct balun output on the sub-GHz path.

ELRS firmware target: `Unified_ESP32C3_LR1121_RX`

PCB: 24x18mm, 4-layer, 1.0mm thickness
Target BOM: EUR 12-15

## Block Diagram

```
                           +------------------+
                           |   ESP32-C3FH4    |
                           |                  |
  FC UART RX <-- GPIO20 ---|  SPI Bus:        |
  FC UART TX --> GPIO21 ---|  SCK  = GPIO4    |--- SCK ----+--------+
                           |  MOSI = GPIO7    |--- MOSI ---+--------+
                           |  MISO = GPIO6    |--- MISO ---+--------+
                           |                  |            |        |
                           |  GPIO8  NSS1  ---|--- NSS ----+        |
                           |  GPIO2  NRESET---|--- NRST ---+        |
                           |  GPIO3  BUSY1 ---|--- BUSY ---+        |
                           |  GPIO5  DIO9_1---|--- DIO9 ---+        |
                           |                  |        LR1121 #1    |
                           |  GPIO10 NSS2  ---|--- NSS  ---+        |
                           |  GPIO0  NRST2 ---|--- NRST ---+        |
                           |  GPIO1  BUSY2 ---|--- BUSY ---+        |
                           |  GPIO9  DIO9_2---|--- DIO9 ---+        |
                           |                  |        LR1121 #2    |
                           |  GPIO18 TXEN  ---|---+                 |
                           |  GPIO19 RXEN  ---|---+---> SE2431L     |
                           +------------------+         |           |
                                                        v           |
                                                   2.4GHz UFL    Sub-GHz UFL
```

## Power Supply

### Input
- 3.3V to 5V from FC via solder pads
- Reverse polarity: no protection (standard for ELRS receivers, FC provides regulated supply)

### LDO: AP2112K-3.3TRG1 (LCSC C51118, SOT-23-5)
Selected over RT9080 for better availability and proven ELRS use. 600mA output, dropout 250mV at 600mA.

Dual LR1121 + ESP32-C3 + SE2431L peak current estimate:
- ESP32-C3: ~80mA (WiFi off, SPI active)
- LR1121 x2: ~50mA each in RX, ~120mA each in TX (telemetry)
- SE2431L: ~25mA in RX mode, ~120mA in TX mode
- Total worst case (both radios TX + SE2431L TX): ~490mA
- Typical operation (both RX): ~230mA

600mA LDO provides adequate margin for typical operation.

| Pin | Connection | Notes |
|-----|-----------|-------|
| VIN | 5V input | Via ferrite bead (optional) |
| GND | Ground | Thermal pad to ground pour |
| EN | VIN | Always enabled |
| VOUT | 3.3V rail | |
| NC | - | |

### Decoupling
- VIN: 22uF 0402 ceramic + 100nF 0402 ceramic
- VOUT: 22uF 0402 ceramic x2 + 100nF 0402 ceramic (extra bulk for dual radio transients)

All capacitors X5R or X7R, 10V minimum rating for input, 6.3V minimum for output.

## ESP32-C3FH4 (U1)

### Package
QFN-32, 5x5mm, 0.4mm pitch
LCSC: C2858491

The ESP32-C3FH4 has 4MB flash integrated. No external flash required.

### Complete Pin Table

| Pin | Name | Connection | Net Name | Notes |
|-----|------|-----------|----------|-------|
| 1 | LNA_IN | NC | - | WiFi antenna pin. NC for receiver (no WiFi antenna). WiFi used only for OTA firmware update over UART-connected WiFi. Leave unconnected with ESD protection. |
| 2 | VDD3P3 | 3.3V | VCC_3V3 | Main power, 100nF to GND |
| 3 | VDD3P3 | 3.3V | VCC_3V3 | Main power, 100nF to GND |
| 4 | GPIO2 | LR1121 #1 + #2 NRESET | RADIO_NRST | Shared reset. See trade-off analysis. |
| 5 | GPIO3 | LR1121 #1 BUSY | RADIO1_BUSY | |
| 6 | MTMS/GPIO4 | SPI SCK (shared) | SPI_SCK | |
| 7 | MTDI/GPIO5 | LR1121 #1 DIO9 | RADIO1_DIO9 | IRQ from radio 1 |
| 8 | MTCK/GPIO6 | SPI MISO (shared) | SPI_MISO | |
| 9 | MTDO/GPIO7 | SPI MOSI (shared) | SPI_MOSI | |
| 10 | GPIO8 | LR1121 #1 NSS | RADIO1_NSS | Active low chip select |
| 11 | GPIO9 | LR1121 #2 DIO9 | RADIO2_DIO9 | Boot strapping pin! 10k pull-up to 3.3V required. See boot analysis. |
| 12 | GPIO10 | LR1121 #2 NSS | RADIO2_NSS | Active low chip select |
| 13 | VDD3P3_RTC | 3.3V | VCC_3V3 | 100nF to GND |
| 14 | GPIO0 | LR1121 #2 NRESET | RADIO2_NRST | See alternative: shared NRESET |
| 15 | GPIO1 | LR1121 #2 BUSY | RADIO2_BUSY | |
| 16 | VDD_SPI | 3.3V | VCC_3V3 | Internal flash power. 100nF to GND |
| 17 | SPIHD/GPIO17 | NC | - | Internal flash |
| 18 | SPIWP/GPIO16 | NC | - | Internal flash |
| 19 | SPICS0/GPIO14 | NC | - | Internal flash |
| 20 | SPICLK/GPIO15 | NC | - | Internal flash |
| 21 | SPID/GPIO13 | NC | - | Internal flash |
| 22 | SPIQ/GPIO12 | NC | - | Internal flash |
| 23 | GPIO18 | SE2431L TXEN | FE_TXEN | Front-end TX enable |
| 24 | GPIO19 | SE2431L RXEN | FE_RXEN | Front-end RX enable (also USB_D+ alt) |
| 25 | GPIO20 | UART RX from FC | UART_RX | CRSF input from flight controller |
| 26 | GPIO21 | UART TX to FC | UART_TX | CRSF output to flight controller |
| 27 | VDD3P3 | 3.3V | VCC_3V3 | 100nF to GND |
| 28 | GPIO11 | NC | - | Internal flash VDD_SPI. Do NOT use. |
| 29 | XTAL_P | NC | - | Internal oscillator used (FH4 variant) |
| 30 | XTAL_N | NC | - | Internal oscillator used (FH4 variant) |
| 31 | CHIP_EN | EN circuit | CHIP_EN | 10k pull-up + 1uF to GND (RC delay per Espressif guidelines) |
| 32 | GND | Ground | GND | Exposed pad also GND |
| EP | GND | Ground | GND | Thermal pad |

### CHIP_EN Reset Circuit
Per Espressif ESP32-C3 hardware design guidelines:
- R: 10k to VCC_3V3
- C: 1uF to GND
- Time constant: ~10ms, ensures clean power-on reset

### Boot Strapping
- GPIO8: Pulled high via LR1121 #1 NSS (has 10k pull-up for SPI). Selects SPI boot = normal flash boot. OK.
- GPIO9: 10k pull-up to VCC_3V3. Must be HIGH at boot for normal operation. LR1121 DIO9 is output, default low after reset, does not conflict. OK.
- GPIO2: Connected to NRESET. MCU drives this, not an issue for boot strap (GPIO2 is not a boot pin on ESP32-C3). OK.

### WiFi OTA
The ESP32-C3FH4 has WiFi capability. ELRS uses WiFi for OTA firmware updates. The LNA_IN pin (pin 1) is not connected to an external antenna. WiFi OTA relies on the internal trace/pad acting as a rudimentary antenna -- sufficient for close-range OTA updates (< 1m). This is standard practice for ELRS receivers without a dedicated WiFi antenna.

No USB test pads are provided. Firmware update is WiFi OTA only (triggered via ELRS Lua script or by holding bind button timing). For initial factory flash, UART boot mode via FC passthrough.

## GPIO Allocation Analysis

### Final Allocation (Separate NRESET variant -- RECOMMENDED)

| GPIO | Function | ELRS hardware.json key | Direction | Notes |
|------|----------|----------------------|-----------|-------|
| 0 | Radio 2 NRESET | radio_rst_2 | Output | |
| 1 | Radio 2 BUSY | radio_busy_2 | Input | |
| 2 | Radio 1 NRESET | radio_rst | Output | |
| 3 | Radio 1 BUSY | radio_busy | Input | |
| 4 | SPI SCK | radio_sck | Output | Shared bus |
| 5 | Radio 1 DIO9 | radio_dio0 | Input | IRQ |
| 6 | SPI MISO | radio_miso | Input | Shared bus |
| 7 | SPI MOSI | radio_mosi | Output | Shared bus |
| 8 | Radio 1 NSS | radio_nss | Output | Active low |
| 9 | Radio 2 DIO9 | radio_dio0_2 | Input | IRQ. Boot pin, needs 10k pull-up. |
| 10 | Radio 2 NSS | radio_nss_2 | Output | Active low |
| 18 | SE2431L TXEN | power_txen | Output | 2.4GHz FE TX enable |
| 19 | SE2431L RXEN | power_rxen | Output | 2.4GHz FE RX enable |
| 20 | UART RX (from FC) | serial_rx | Input | CRSF/MAVLink |
| 21 | UART TX (to FC) | serial_tx | Output | CRSF/MAVLink |

Total GPIOs used: 16 out of 16 usable (GPIO0-10, 18-21). Zero remaining.

### What We Cannot Fit

| Feature | Why Not | Mitigation |
|---------|---------|-----------|
| WS2812B RGB LED | No GPIO available | Use simple LED on 3.3V rail with current limit (always on when powered). Or omit entirely. |
| Boot button | No GPIO for dedicated button | WiFi OTA for updates. Factory flash via UART passthrough. Bind via ELRS 3-click on power cycle. |
| USB D-/D+ | GPIO18/19 used for SE2431L | UART-only interface. WiFi OTA for updates. |
| Bind button | No GPIO | ELRS auto-bind on first power-up, or 3-click power cycle method. |
| Second UART | No GPIO | Single UART to FC only. |

### Alternative: Shared NRESET (Frees GPIO0)

Tying both LR1121 NRESET pins to GPIO2 (shared) frees GPIO0 for another function. Trade-offs:

Advantages:
- Frees GPIO0 for WS2812B LED, boot button, or bind button
- Simpler routing (one net instead of two)

Disadvantages:
- Cannot independently reset one radio without affecting the other
- If one radio hangs, resetting it also resets the working radio
- Minor: reset timing may need to satisfy both radios simultaneously (not a real issue, both are LR1121)

RECOMMENDATION: Use separate NRESET lines (GPIO0 and GPIO2). Independent reset is important for a dual-radio design where one radio might need recovery without disrupting the other. The cost is losing LED/button capability, which is acceptable for a premium miniature receiver.

If a LED is absolutely required for user feedback, use the shared NRESET variant and put a WS2812B on GPIO0.

### GPIO9 Boot Strap Safety Analysis

GPIO9 must be HIGH during boot for normal SPI flash boot mode.

LR1121 DIO9 behavior:
- After power-on or NRESET assertion: DIO9 is LOW (default state)
- DIO9 goes HIGH only when an IRQ fires AND the host has configured DIO9 as IRQ output
- During ESP32-C3 boot, the LR1121 has not been initialized, so DIO9 remains LOW

With a 10k pull-up on GPIO9:
- LR1121 DIO9 is high-impedance or low during boot = pull-up wins = GPIO9 = HIGH = normal boot
- During operation, LR1121 drives DIO9 actively when IRQ fires = overrides pull-up = correct IRQ behavior

This is safe. The pull-up ensures correct boot, and the LR1121's active drive easily overrides 10k during operation.

## LR1121 #1 -- Sub-GHz Radio (U2)

### Package
QFN-32, 4x4mm, 0.5mm pitch
LCSC: C7498014

### Function
Primary sub-GHz radio for 868MHz (EU) / 915MHz (US) operation.
In Xrossband mode: always on sub-GHz band.
In True Diversity mode: can operate on same band as Radio 2.

### Complete Pin Table

| Pin | Name | Connection | Net Name | Notes |
|-----|------|-----------|----------|-------|
| 1 | VDD_IN | 3.3V | VCC_3V3 | Main supply, 100nF + 1uF to GND |
| 2 | LDO_OUT | 100nF to GND | R1_LDO | Internal LDO output. Decouple only, do not load. |
| 3 | VSS_RF | GND | GND | RF ground |
| 4 | RFI_P | Balun | R1_RFI_P | Sub-GHz differential RF+ |
| 5 | RFI_N | Balun | R1_RFI_N | Sub-GHz differential RF- |
| 6 | VR_PA | 100nF to GND | R1_VR_PA | Internal PA regulator output |
| 7 | VSS | GND | GND | |
| 8 | RFO_P | NC | - | Sub-GHz TX output, not used (telemetry via RFI) |
| 9 | RFO_N | NC | - | Sub-GHz TX output, not used |
| 10 | VBAT_SW | 3.3V via ferrite + 4.7uF | R1_VBAT_SW | Switched battery supply for PA. Required even at 3.3V. |
| 11 | RFSW_0 | NC or GND | - | RF switch DIO. Directly controlled by firmware via SetDioAsRfSwitch. No external switch on sub-GHz path. |
| 12 | RFSW_1 | NC or GND | - | RF switch DIO |
| 13 | RFSW_2 | NC or GND | - | RF switch DIO |
| 14 | RFSW_3 | NC or GND | - | RF switch DIO |
| 15 | BUSY | GPIO3 | RADIO1_BUSY | High when radio processing command |
| 16 | DIO9 | GPIO5 | RADIO1_DIO9 | Configurable IRQ output |
| 17 | NSS | GPIO8 | RADIO1_NSS | SPI chip select, active low. 10k pull-up to VCC_3V3. |
| 18 | MISO | GPIO6 | SPI_MISO | SPI data out |
| 19 | MOSI | GPIO7 | SPI_MOSI | SPI data in |
| 20 | SCK | GPIO4 | SPI_SCK | SPI clock |
| 21 | NRESET | GPIO2 | RADIO1_NRST | Active low reset. 100nF to GND for debounce. 10k pull-up. |
| 22 | XTA | 32MHz TCXO #1 | R1_TCXO_OUT | TCXO clock input |
| 23 | XTB | NC | - | Not used when TCXO on XTA |
| 24 | VDD_TCXO | 1.8V TCXO supply | R1_VDD_TCXO | LR1121 provides regulated TCXO supply. Enable via firmware. 100nF decoupling. |
| 25 | DIO5 | NC | - | Unused DIO |
| 26 | DIO6 | NC | - | Unused DIO |
| 27 | DIO7 | NC | - | Unused DIO |
| 28 | DIO8 | NC | - | Unused DIO |
| 29 | DIO10 | NC | - | Unused DIO |
| 30 | DIO11 | NC | - | Unused DIO |
| 31 | RFI_HF | NC | - | 2.4GHz RF input. NOT USED on sub-GHz radio. Terminate with 100nF to GND or leave NC. |
| 32 | VSS | GND | GND | |
| EP | GND | Ground | GND | Exposed pad. Critical thermal connection. |

### Sub-GHz RF Path

```
LR1121 #1                    Balun                    UFL
RFI_P ----+              +----------+
          |-- Matching -->| 868/915  |---> 50 ohm ---> UFL #1
RFI_N ----+              | Balun    |     microstrip   (sub-GHz)
                         +----------+
```

Balun: 0868BM15A0001E (Johanson Technology) or equivalent LTCC balun for 868/915MHz.
Alternative: discrete L-C balun using 0402 components (lower cost, requires tuning).

Matching network: Per LR1121 reference design. Typically 2-3 component pi or L network between LR1121 differential outputs and balun input.

No PA/LNA on sub-GHz path. The LR1121 internal PA provides up to +22dBm on sub-GHz which is sufficient for a receiver (telemetry TX power). The LR1121 has good RX sensitivity (-148dBm on sub-GHz) without external LNA.

### TCXO #1
32MHz TCXO, 1.8V supply from LR1121 VDD_TCXO pin.
Tolerance: +/- 1ppm or better (required for LR1121 FHSS operation).
Package: 1610 (1.6x1.0mm) preferred for size.

Recommended: SIT1532AI-J4-DCC-32.000E (SiTime) or equivalent.
LCSC options: search for 32MHz TCXO 1.6x1.0mm 1.8V.

## LR1121 #2 -- 2.4GHz Radio (U3)

### Package
QFN-32, 4x4mm, 0.5mm pitch
LCSC: C7498014 (same part as Radio 1)

### Function
Primary 2.4GHz radio.
In Xrossband mode: always on 2.4GHz band.
In True Diversity mode: can operate on same band as Radio 1.

### Complete Pin Table

| Pin | Name | Connection | Net Name | Notes |
|-----|------|-----------|----------|-------|
| 1 | VDD_IN | 3.3V | VCC_3V3 | Main supply, 100nF + 1uF to GND |
| 2 | LDO_OUT | 100nF to GND | R2_LDO | Internal LDO output decoupling |
| 3 | VSS_RF | GND | GND | |
| 4 | RFI_P | NC | - | Sub-GHz differential. NOT USED on 2.4GHz radio. NC. |
| 5 | RFI_N | NC | - | Sub-GHz differential. NOT USED. NC. |
| 6 | VR_PA | 100nF to GND | R2_VR_PA | Internal PA regulator |
| 7 | VSS | GND | GND | |
| 8 | RFO_P | NC | - | Not used |
| 9 | RFO_N | NC | - | Not used |
| 10 | VBAT_SW | 3.3V via ferrite + 4.7uF | R2_VBAT_SW | Switched PA supply |
| 11 | RFSW_0 | NC or to SE2431L logic | - | RF switch DIO for front-end control. See RF switch discussion. |
| 12 | RFSW_1 | NC | - | |
| 13 | RFSW_2 | NC | - | |
| 14 | RFSW_3 | NC | - | |
| 15 | BUSY | GPIO1 | RADIO2_BUSY | |
| 16 | DIO9 | GPIO9 | RADIO2_DIO9 | ESP32-C3 boot pin. 10k pull-up on GPIO9. |
| 17 | NSS | GPIO10 | RADIO2_NSS | SPI chip select. 10k pull-up to VCC_3V3. |
| 18 | MISO | GPIO6 | SPI_MISO | Shared SPI bus |
| 19 | MOSI | GPIO7 | SPI_MOSI | Shared SPI bus |
| 20 | SCK | GPIO4 | SPI_SCK | Shared SPI bus |
| 21 | NRESET | GPIO0 | RADIO2_NRST | Active low reset. 100nF + 10k pull-up. |
| 22 | XTA | 32MHz TCXO #2 | R2_TCXO_OUT | TCXO clock input |
| 23 | XTB | NC | - | |
| 24 | VDD_TCXO | 1.8V TCXO supply | R2_VDD_TCXO | 100nF decoupling |
| 25 | DIO5 | NC | - | |
| 26 | DIO6 | NC | - | |
| 27 | DIO7 | NC | - | |
| 28 | DIO8 | NC | - | |
| 29 | DIO10 | NC | - | |
| 30 | DIO11 | NC | - | |
| 31 | RFI_HF | Matching network to SE2431L | R2_RFI_HF | 2.4GHz single-ended RF port |
| 32 | VSS | GND | GND | |
| EP | GND | Ground | GND | Exposed pad |

### 2.4GHz RF Path

```
LR1121 #2     Matching      SE2431L          SAW         UFL
RFI_HF ----> Pi network --> RF_IN/RF_OUT --> Filter ---> UFL #2
                            TXEN <-- GPIO18              (2.4GHz)
                            RXEN <-- GPIO19
```

### TCXO #2
Separate 32MHz TCXO for Radio 2. Same specifications as TCXO #1.

Why two separate TCXOs instead of shared clock:
- Each LR1121 XTA pin expects a specific drive level and loading
- Clock buffer/fanout adds a component and PCB area
- Two 1610 TCXOs cost ~$0.60-1.00 total vs one TCXO + buffer ~$0.80 + complexity
- Independent clocks eliminate cross-coupling risk between radios
- Simpler layout with each TCXO placed adjacent to its radio

## SE2431L 2.4GHz Front-End (U4)

### Package
QFN-20, 3x3mm, 0.4mm pitch
LCSC: search for SE2431L-R (Skyworks)

### Function
2.4GHz PA + LNA + TX/RX switch for Radio 2 (2.4GHz path).
- RX mode: LNA provides ~11dB gain, improving sensitivity
- TX mode: PA provides up to +22dBm output (for telemetry)
- Integrated T/R switch eliminates external switch

### Complete Pin Table

| Pin | Name | Connection | Net Name | Notes |
|-----|------|-----------|----------|-------|
| 1 | RF_IN | LR1121 #2 RFI_HF via matching | FE_RF_IN | From radio matching network |
| 2 | GND | GND | GND | |
| 3 | VDD_LNA | 3.3V | VCC_3V3 | 100nF to GND |
| 4 | GND | GND | GND | |
| 5 | ANT | SAW filter input | FE_ANT | To antenna via SAW |
| 6 | GND | GND | GND | |
| 7 | VDD_PA | 3.3V | VCC_3V3 | 100nF + 1uF to GND. Main PA supply. |
| 8 | VDD_PA | 3.3V | VCC_3V3 | Tied to pin 7 |
| 9 | GND | GND | GND | |
| 10 | NC | - | - | |
| 11 | TXEN | GPIO18 | FE_TXEN | High = TX mode. 100k pull-down. |
| 12 | RXEN | GPIO19 | FE_RXEN | High = RX mode. 100k pull-down. |
| 13 | NC | - | - | |
| 14-20 | GND | GND | GND | Multiple ground pins |
| EP | GND | GND | GND | Exposed pad |

### SE2431L Control Truth Table

| TXEN | RXEN | Mode | Current |
|------|------|------|---------|
| 0 | 0 | Shutdown | < 1uA |
| 0 | 1 | RX (LNA active) | ~5mA |
| 1 | 0 | TX (PA active) | ~120mA |
| 1 | 1 | Invalid | Do not use |

Default state at boot (GPIOs floating/low): both TXEN and RXEN low = shutdown. Safe.

### SAW Filter
2.4GHz SAW/BAW filter between SE2431L ANT pin and UFL connector.
Purpose: reject out-of-band interference, especially from co-located sub-GHz transmissions.

Recommended: SAFFB2G41FA0F0A (Murata) or equivalent 2.4-2.5GHz bandpass filter.
Package: 1210 or 0805 SMD.

### SE2431L Matching
RF_IN and ANT pins require matching networks per SE2431L reference design.
Typically 2-element L-match on each port. Values depend on PCB stackup and trace impedance.

## SPI Bus Architecture

### Shared Bus with Independent Chip Selects

Both LR1121 chips share MOSI, MISO, and SCK. Each has its own NSS (chip select).

```
ESP32-C3          LR1121 #1        LR1121 #2
GPIO4 (SCK)  --+-- SCK             SCK --+
GPIO7 (MOSI) --+-- MOSI            MOSI --+
GPIO6 (MISO) --+-- MISO            MISO --+
GPIO8 (NSS1) ----- NSS
GPIO10 (NSS2) -------------------- NSS
```

### SPI Bus Rules
1. Only one NSS may be asserted (LOW) at a time
2. MISO is high-impedance when NSS is HIGH (LR1121 spec)
3. NSS pull-ups (10k) ensure radios are deselected during boot/reset
4. Maximum SPI clock: 16MHz (LR1121 limit)
5. CPOL=0, CPHA=0 (SPI Mode 0) per LR1121 datasheet

### SPI Transaction Sequence
The ELRS firmware handles dual-radio SPI arbitration:
1. Assert NSS for target radio
2. Check BUSY pin -- wait if radio is processing
3. Send command/data
4. Deassert NSS
5. Wait for DIO9 IRQ or poll BUSY for completion

### Bus Contention Risk
Minimal. The ELRS firmware is single-threaded on ESP32-C3 and serializes all SPI transactions. No hardware mutex needed.

## TCXO Specifications

Two identical 32MHz TCXOs, one per radio.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Frequency | 32.000 MHz | LR1121 reference clock |
| Supply | 1.8V | From LR1121 VDD_TCXO pin |
| Stability | +/- 1 ppm | Over -40 to +85C |
| Output | Clipped sine or CMOS | Connected to LR1121 XTA |
| Package | 1610 (1.6x1.0mm) | Minimize board area |
| Startup | < 1ms | Fast lock required for FHSS |

Each TCXO powered from its respective LR1121 VDD_TCXO output (pin 24). The LR1121 firmware enables this supply when configuring the radio for TCXO mode.

Decoupling: 100nF on VDD_TCXO pin, placed adjacent to TCXO.

## RF Switch Architecture (LR1121 RFSW Control)

The LR1121 has internal RFSW_0 through RFSW_3 pins that are programmatically controlled via the SetDioAsRfSwitch command. The firmware sends an 8-byte configuration that defines the RFSW pin states for each radio operating mode.

### Sub-GHz Radio (Radio 1) RF Switch Configuration
No external RF switch on sub-GHz path. The LR1121 internal T/R switch handles RX/TX switching on the RFI_P/RFI_N differential port.

RFSW pins are either NC or used as general status outputs. For OpenRX-Gemini, leave NC.

### 2.4GHz Radio (Radio 2) RF Switch Configuration
The SE2431L TXEN/RXEN are controlled by ESP32-C3 GPIO18/GPIO19, NOT by LR1121 RFSW pins. This is because:
1. RFSW pins have no connection to Radio 2 GPIOs on the ESP32-C3
2. The ELRS firmware uses power_txen/power_rxen hardware.json fields for front-end control
3. GPIO-based control gives the firmware direct, deterministic timing control

### ELRS hardware.json RFSW Configuration
For the OpenRX-Gemini, the radio_rfsw_ctrl array configures the LR1121 internal switch states:

```json
"radio_rfsw_ctrl": [31, 0, 20, 24, 24, 2, 0, 1]
```

These values configure:
- RfswEnable: which RFSW DIOs are active
- RfSwStbyCfg: RFSW state in standby
- RfSwRxCfg: RFSW state in sub-GHz RX
- RfSwTxCfg: RFSW state in sub-GHz TX (low power)
- RfSwTxHPCfg: RFSW state in sub-GHz TX (high power)
- RfSwTxHfCfg: RFSW state in 2.4GHz TX
- Unused
- RfSwWifiCfg: RFSW state in 2.4GHz RX / WiFi scan

Exact values must be determined during bring-up based on PCB routing and antenna configuration.

## Antenna Connectors

Two UFL/IPEX MHF4 connectors:

| Connector | Band | Radio | Net |
|-----------|------|-------|-----|
| J1 | Sub-GHz (868/915MHz) | LR1121 #1 | ANT_SUBGHZ |
| J2 | 2.4GHz | LR1121 #2 via SE2431L | ANT_2G4 |

IPEX MHF4 (1.4mm height) recommended for minimal profile.
Footprint: standard IPEX MHF4 with ground pads and anchor.

Signal integrity: 50-ohm controlled impedance microstrip from SE2431L/balun to connector. Keep traces short (< 10mm).

## Passive Components Summary

### Decoupling Capacitors (0402 package)

| Designator | Value | Net | Location |
|-----------|-------|-----|----------|
| C1 | 22uF X5R 10V | VIN | LDO input |
| C2 | 100nF X5R 10V | VIN | LDO input |
| C3 | 22uF X5R 6.3V | VCC_3V3 | LDO output |
| C4 | 22uF X5R 6.3V | VCC_3V3 | LDO output (extra bulk) |
| C5 | 100nF X5R 6.3V | VCC_3V3 | LDO output |
| C6-C9 | 100nF X5R 6.3V | VCC_3V3 | ESP32-C3 VDD pins (x4) |
| C10 | 100nF X5R 6.3V | VCC_3V3 | Radio 1 VDD_IN |
| C11 | 1uF X5R 6.3V | VCC_3V3 | Radio 1 VDD_IN |
| C12 | 100nF X5R 6.3V | R1_LDO | Radio 1 LDO_OUT |
| C13 | 100nF X5R 6.3V | R1_VR_PA | Radio 1 VR_PA |
| C14 | 4.7uF X5R 6.3V | R1_VBAT_SW | Radio 1 VBAT_SW |
| C15 | 100nF X5R 6.3V | R1_VDD_TCXO | Radio 1 TCXO supply |
| C16 | 100nF X5R 6.3V | VCC_3V3 | Radio 2 VDD_IN |
| C17 | 1uF X5R 6.3V | VCC_3V3 | Radio 2 VDD_IN |
| C18 | 100nF X5R 6.3V | R2_LDO | Radio 2 LDO_OUT |
| C19 | 100nF X5R 6.3V | R2_VR_PA | Radio 2 VR_PA |
| C20 | 4.7uF X5R 6.3V | R2_VBAT_SW | Radio 2 VBAT_SW |
| C21 | 100nF X5R 6.3V | R2_VDD_TCXO | Radio 2 TCXO supply |
| C22 | 100nF X5R 6.3V | VCC_3V3 | SE2431L VDD_LNA |
| C23 | 100nF X5R 6.3V | VCC_3V3 | SE2431L VDD_PA |
| C24 | 1uF X5R 6.3V | VCC_3V3 | SE2431L VDD_PA bulk |
| C25 | 1uF X5R 6.3V | CHIP_EN | ESP32-C3 EN RC delay |
| C26 | 100nF X5R 6.3V | RADIO1_NRST | Radio 1 NRESET debounce |
| C27 | 100nF X5R 6.3V | RADIO2_NRST | Radio 2 NRESET debounce |

### Resistors (0402 package)

| Designator | Value | Net | Function |
|-----------|-------|-----|----------|
| R1 | 10k | CHIP_EN | ESP32-C3 EN pull-up |
| R2 | 10k | RADIO1_NSS | NSS1 pull-up (also GPIO8 boot strap) |
| R3 | 10k | RADIO2_NSS | NSS2 pull-up |
| R4 | 10k | GPIO9 | GPIO9 boot strap pull-up |
| R5 | 10k | RADIO1_NRST | NRESET1 pull-up |
| R6 | 10k | RADIO2_NRST | NRESET2 pull-up |
| R7 | 100k | FE_TXEN | SE2431L TXEN pull-down (safe boot) |
| R8 | 100k | FE_RXEN | SE2431L RXEN pull-down (safe boot) |

### Ferrite Beads (0402 package)

| Designator | Value | Net | Function |
|-----------|-------|-----|----------|
| FB1 | 600R@100MHz | R1_VBAT_SW | Radio 1 PA supply filtering |
| FB2 | 600R@100MHz | R2_VBAT_SW | Radio 2 PA supply filtering |

### RF Matching Components
Values TBD during layout. Placeholder for:
- 3x components for sub-GHz balun matching (Radio 1 RFI_P/RFI_N to balun)
- 2x components for 2.4GHz matching (Radio 2 RFI_HF to SE2431L)
- 2x components for SE2431L ANT to SAW filter matching

All RF matching components: 0402 or 0201 NP0/C0G capacitors and wire-wound inductors.

## PCB Connection Pads

Solder pads on PCB edge for FC connection:

| Pad | Function | Notes |
|-----|----------|-------|
| 5V | Power input | From FC 5V regulated |
| GND | Ground | |
| TX | UART TX (GPIO21) | To FC UART RX |
| RX | UART RX (GPIO20) | From FC UART TX |

Optional boot pads (solder bridge):
| Pad | Function | Notes |
|-----|----------|-------|
| BOOT | GPIO9 to GND | Bridge to enter UART boot mode for factory flash |

## ELRS Firmware Configuration (hardware.json)

```json
{
  "hardware": {
    "serial_rx": 20,
    "serial_tx": 21,
    "radio_busy": 3,
    "radio_busy_2": 1,
    "radio_dio0": 5,
    "radio_dio0_2": 9,
    "radio_miso": 6,
    "radio_mosi": 7,
    "radio_nss": 8,
    "radio_nss_2": 10,
    "radio_rst": 2,
    "radio_rst_2": 0,
    "radio_sck": 4,
    "radio_dcdc": true,
    "radio_rfsw_ctrl": [31, 0, 20, 24, 24, 2, 0, 1],
    "radio_rfsw_ctrl_count": 8,
    "power_txen": 18,
    "power_rxen": 19,
    "power_min": 0,
    "power_max": 6,
    "power_default": 2,
    "power_values": [-18, -15, -12, -9, -5, 0, 7],
    "power_values2": [-17, -15, -12, -9, -5, 0, 7],
    "power_values_dual": [-18, -18, -15, -10, -6, -2, 2],
    "power_values_dual_count": 7
  }
}
```

Notes:
- `radio_rfsw_ctrl` values are placeholder, must be tuned during bring-up
- `power_values` are sub-GHz power table (dBm settings for LR1121)
- `power_values2` are 2.4GHz power table
- `power_values_dual` are Xrossband power table (reduced per-radio power)
- `radio_dcdc` enables LR1121 DC-DC converter mode for efficiency

## Layout Guidelines

1. Ground plane: unbroken under all RF components. 4-layer stack with solid GND on layer 2.
2. RF traces: 50-ohm controlled impedance microstrip on layer 1. Calculate width for JLCPCB JLC04161H-7628 stackup (~0.3mm for 50-ohm on 1.0mm 4-layer).
3. Component placement:
   - ESP32-C3 center of board
   - LR1121 #1 near sub-GHz UFL connector (minimize trace length)
   - LR1121 #2 near SE2431L and 2.4GHz UFL connector
   - TCXOs immediately adjacent to their respective LR1121
   - LDO near power input pads
4. Decoupling: place capacitors as close as possible to IC power pins. Via directly to ground plane.
5. RF isolation: keep sub-GHz and 2.4GHz paths on opposite sides of the board if possible.
6. Thermal: exposed pads on LR1121 and ESP32-C3 must have thermal vias to inner ground plane.
7. Antenna keepout: minimum 2mm clearance around UFL connectors, no copper pour in antenna launch area.

## Design Risk Register

| Risk | Severity | Mitigation |
|------|----------|-----------|
| GPIO9 boot conflict with LR1121 DIO9 | Medium | 10k pull-up ensures HIGH at boot. LR1121 DIO9 default LOW after reset. Tested safe in theory, verify on first proto. |
| SPI bus noise with two radios | Low | NSS pull-ups prevent bus contention. ELRS firmware serializes transactions. Short SPI traces. |
| LR1121 LCSC stock | High | C7498014 showed low stock historically. Order early, consider alternative distributors. |
| Thermal on 24x18mm board | Medium | Dual radios + SE2431L generate heat. Thermal vias mandatory. Max TX duty cycle limited by ELRS protocol (short telemetry bursts). |
| No LED for user feedback | Low | Acceptable for premium miniature receiver. User relies on Lua/OTA for status. Consider shared NRESET variant if LED required. |
| SE2431L 2.4GHz only | None | Correct. SE2431L is only on 2.4GHz path. Sub-GHz path has no front-end (LR1121 internal PA/LNA sufficient). |
| WiFi OTA range without antenna | Low | Sufficient for close-range updates. Standard ELRS practice. |
