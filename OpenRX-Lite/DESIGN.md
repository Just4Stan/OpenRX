# OpenRX-Lite Schematic Documentation

Active release SKU. Tiny `2.4GHz` ExpressLRS receiver with ceramic main antenna.

> Release-plan note: Lite stays in the release stack. Its intended product form is a ceramic-antenna-only micro / whoop receiver. Any Molex / alternate-main-antenna references below should be treated as historical schematic detail, not the product decision.
>
> BOM note: use [verification/bom/OpenRX-Lite-lcsc.csv](/Users/stan/Library/Mobile%20Documents/com~apple~CloudDocs/OpenRX/verification/bom/OpenRX-Lite-lcsc.csv) for the current fitted part numbers exported from the active schematic.

- PCB: 16x12mm target, 2-layer, 1.0mm thickness
- Procurement snapshot: the current schematic prices closer to `$8.8` from LCSC before VAT/shipping. The old `EUR 3-4` target is not realistic for the current fitted parts.
- Input: 3.3-5V from flight controller

## Block Diagram

```
                                    +3.3V
                                      |
  +-----+    +--------+    +---------+----------+
  | FC   |    |TLV755  |    |                    |
  | 5V---|----| LDO    |----|  ESP32-C3FH4       |
  | GND--|--+-| 3.3V   |    |  (QFN-32, 5x5mm)  |
  | TX---|--|-|--------|----| GPIO1/RX           |
  | RX---|--|-|--------|----| GPIO0/TX           |
  +-----+  | |        |    |                    |    SPI Bus
            | +--------+    |  GPIO4/SCK  -------+--------+
            |               |  GPIO7/MOSI -------+-----+  |
            |               |  GPIO6/MISO -------+--+  |  |
            |               |  GPIO8/NSS  -------+-+|  |  |
            |               |  GPIO5/DIO1 ------+| ||  |  |
            |               |  GPIO3/BUSY -----+|| ||  |  |
            |               |  GPIO2/NRST ----+||| ||  |  |
            |               |                 |||| ||  |  |
            |     40MHz     |  XTAL_P/N       |||| ||  |  |
            |    +-----+    |    |  |          |||| ||  |  |
            |    | XTAL|----+----+--+          |||| ||  |  |
            |    +-----+    |                  |||| ||  |  |
            |               | GPIO10 ---> WS2812B (opt)    |
            |               | GPIO9  ---> BOOT btn         |
            |               | GPIO18 ---> USB D- (TP)      |
            |               | GPIO19 ---> USB D+ (TP)      |
            |               +----------+   |||| ||  |  |
            |                              |||| ||  |  |
            |               +----------+   |||| ||  |  |
            |    52MHz      |SX1281    |   |||| ||  |  |
            |   +------+    |IMLTRT   |   |||| ||  |  |
            |   | TCXO |----|XTA      |   |||| ||  |  |
            |   +------+    |         |   |||| ||  |  |
            |               |NRESET---+---+||| ||  |  |
            |               |BUSY  --------+|| ||  |  |
            |               |DIO1  ---------+| ||  |  |
            |               |NSS   ----------+ ||  |  |
            |               |MISO  -------------+  |  |
            |               |MOSI  ----------------+  |
            |               |SCK   -------------------+
            |               |         |
            |               |  RFIO   |
            |               +----+----+
            |                    |
            |              DEA102700LT-6307A2
            |                  (LPF)
            |                    |
            |               +----------+
            |               | Ceramic  |
            |               | Antenna  |
            |               | 2450AT   |
            |               +----------+
            |
            +--- GND plane
```

## Power Supply (U3: TLV75533PDQNR)

X2SON-4 (1.0x1.0mm), 500mA, LDO 3.3V regulator. LCSC C2861882. TI.

```
         5V IN
          |
          +--[C1 1uF]--+--GND
          |             |
     +----+----+
     |   IN    |
     |         |
     | TLV755  |
     |         |
     |   OUT---+--[C3 1uF]--+--GND
     |         |             |
     |   EN    |             +--- 3.3V RAIL
     |  (=IN)  |
     |   GND   |
     +---------+
```

### Pin-by-pin: TLV75533PDQNR (X2SON-4, 1.0x1.0mm)

| Pin | Name | Connection |
|-----|------|------------|
| 1 | IN | 5V input rail. C1 (1uF 0402 X5R) to GND |
| 2 | GND | Ground (exposed pad) |
| 3 | EN | Tied to IN (always on) |
| 4 | OUT | 3.3V output rail. C3 (1uF 0402 X5R) to GND |

Note: TLV755 max VIN is 5.5V. Input must come from FC 5V rail, not raw battery. 10uF bulk cap on 5V entry, 10uF bulk on 3.3V rail near ESP32-C3.

## ESP32-C3FH4 (U1, QFN-32, 5x5mm)

LCSC C2858491. RISC-V single core, 160MHz, 4MB internal flash, WiFi+BLE.

### Pin-by-pin: ESP32-C3FH4 (QFN-32)

| Pin | Name | Connection | Notes |
|-----|------|------------|-------|
| 1 | GND | GND | |
| 2 | GND | GND | |
| 3 | 3V3 | 3.3V rail, 100nF (C5) to GND | Main power |
| 4 | EN (CHIP_EN) | 10k (R1) pull-up to 3.3V + 1uF (C6) to GND | RC delay per Espressif spec. Provides stable power-on reset. |
| 5 | GPIO4 | SX1281 SCK (pin 18) | SPI clock |
| 6 | GPIO5 | SX1281 DIO1 (pin 5) | Radio interrupt (active high) |
| 7 | GPIO6 | SX1281 MISO (pin 16) | SPI data from radio |
| 8 | GPIO7 | SX1281 MOSI (pin 17) | SPI data to radio |
| 9 | GPIO8 | SX1281 NSS (pin 19) + 10k (R2) pull-up to 3.3V | SPI chip select (active low). Pull-up keeps radio deselected during ESP boot. |
| 10 | GPIO9 | BOOT button (SW1) to GND + 10k (R3) pull-up to 3.3V | Hold low during reset to enter USB/UART bootloader. Internal pull-up exists but external recommended. |
| 11 | GPIO10 | WS2812B LED data (D1) | Optional status LED. Series 100R (R4) recommended. |
| 12 | GND | GND | |
| 13 | GPIO18 (USB_D-) | Test pad TP1 | Native USB for flashing. Optional -- can use UART instead. |
| 14 | GPIO19 (USB_D+) | Test pad TP2 | Native USB for flashing. Optional. |
| 15 | GPIO3 | SX1281 BUSY (pin 4) | Radio busy status (active high). Poll before SPI commands. |
| 16 | GPIO2 | SX1281 NRESETn (pin 3) | Radio hardware reset (active low). ESP drives low to reset SX1281. |
| 17 | GPIO1 (RX) | FC connector pad TX (CRSF from FC) | UART RX. FC TX connects to ESP RX. 3.3V logic. |
| 18 | GPIO0 (TX) | FC connector pad RX (CRSF to FC) | UART TX. ESP TX connects to FC RX. |
| 19 | GND | GND | |
| 20 | XTAL_P | 40MHz crystal (Y1) pin 1 + 10pF (C7) to GND | Crystal load cap. Place crystal close to pins 20/21. |
| 21 | XTAL_N | 40MHz crystal (Y1) pin 3 + 10pF (C8) to GND | Crystal load cap. |
| 22-30 | GND/NC | GND or NC per datasheet | Unused GPIO and supply pins tied to GND |
| 31 | GND | GND | |
| 32 | GND | GND | |
| EP | Exposed pad | GND | Thermal pad, multiple vias to ground plane |

**Critical notes for ESP32-C3FH4:**
- Pin 4 (EN) RC time constant: 10k * 1uF = 10ms. This ensures clean power-on reset.
- GPIO9 is the boot mode strapping pin. HIGH = normal boot from flash. LOW during reset = download mode.
- GPIO8 is also a strapping pin. Must be HIGH during boot (pull-up on NSS line handles this).
- GPIO2 is a strapping pin. Defaults to HIGH (floating). OK since SX1281 NRESET is active low.
- The ESP32-C3FH4 has 4MB flash internal -- no external flash needed.
- 40MHz crystal is mandatory. Cannot use internal RC oscillator for WiFi/BLE.
- Thermal pad MUST be soldered to GND with thermal vias.

## SX1281IMLTRT (U2, QFN-24, 4x4mm)

LCSC C2151551. 2.4GHz LoRa/FLRC/FSK transceiver. Used in LDO mode (no external inductor).

### Pin-by-pin: SX1281IMLTRT (QFN-24)

| Pin | Name | Connection | Notes |
|-----|------|------------|-------|
| 1 | VDD | 3.3V through 100nF (C9) to GND | Digital supply |
| 2 | VDD_IN | 3.3V through 100nF (C10) to GND | CRITICAL: Must be connected. Main power input for internal LDO/DC-DC. |
| 3 | NRESETn | ESP32-C3 GPIO2 (pin 16) + 10k (R5) pull-up to 3.3V + 100nF (C11) to GND | Active low reset. RC provides power-on reset. ESP can drive low for hard reset. |
| 4 | BUSY | ESP32-C3 GPIO3 (pin 15) | Active high when radio is processing a command. Poll before SPI transactions. |
| 5 | DIO1 | ESP32-C3 GPIO5 (pin 6) | Main interrupt output. Directly connected. |
| 6 | DIO2 | NC | Not used in this design. Can be used for RF switch control in designs with PA/LNA. |
| 7 | DIO3 | NC | Not used. Can output 32MHz clock for TCXO enable but we use always-on TCXO. |
| 8 | GND | GND | |
| 9 | GND | GND | |
| 10 | VR_PA | 470nF (C12) to GND | LDO mode: This is the PA regulator output. 470nF decoupling required. NO inductor (inductor only needed in DC-DC mode). |
| 11 | VDD | 3.3V through 100nF (C13) to GND | RF/analog supply |
| 12 | XTA | 52MHz TCXO output (Y2 pin 3) | TCXO clock input. AC coupling cap may be needed (10pF, C14) depending on TCXO output type. If TCXO is clipped sine output, direct connection OK. |
| 13 | XTB | NC (floating) | Only used in crystal mode. Leave floating for TCXO mode. |
| 14 | GND | GND | |
| 15 | RFIO | DEA102700LT-6307A2 (FL1) to antenna | See RF Path section below |
| 16 | MISO | ESP32-C3 GPIO6 (pin 7) | SPI data output |
| 17 | MOSI | ESP32-C3 GPIO7 (pin 8) | SPI data input |
| 18 | SCK | ESP32-C3 GPIO4 (pin 5) | SPI clock input |
| 19 | NSS | ESP32-C3 GPIO8 (pin 9) + 10k (R2) pull-up to 3.3V | SPI chip select, active low. Shared pull-up with ESP side. |
| 20 | GND | GND | |
| 21 | GND | GND | |
| 22 | GND | GND | |
| 23 | GND | GND | |
| 24 | GND | GND | |
| EP | Exposed pad | GND | Thermal pad. Multiple vias to GND plane. |

**Critical notes for SX1281:**
- LDO mode selected: VR_PA (pin 10) gets 470nF cap only. No inductor.
- DC-DC mode would require 15nH inductor on VR_PA but adds layout complexity on 2-layer board. Not worth it for a receiver.
- VDD_IN (pin 2) MUST be connected to 3.3V. Common mistake to leave it floating.
- TCXO mode: Set register UseRegulatorMode and configure TCXO in firmware. DIO3 can control TCXO power but we run TCXO always-on from 3.3V for simplicity.
- Max SPI clock: 16MHz. ESP32-C3 SPI peripheral should be configured accordingly.
- BUSY must be polled before every SPI transaction. Do not rely on timing.

## 52MHz TCXO (Y2: OW7EL89CENUNFAYLC-52M)

LCSC C22434896. SMD 2016-4P (2.0x1.6mm). YXC, 3.3V, +/-0.5ppm.

### Pin-by-pin: TCXO (SMD2016-4P)

| Pin | Name | Connection |
|-----|------|------------|
| 1 | VDD | 3.3V through 100nF (C15) to GND |
| 2 | GND | GND |
| 3 | OUTPUT | SX1281 XTA (pin 12). Direct connection if clipped sine output. Add 10pF AC coupling cap (C14) if DC blocking needed. |
| 4 | GND | GND |

**Notes:**
- TCXO provides temperature-stable 52MHz reference. Prevents frequency drift disconnections that plague crystal-based ELRS receivers.
- +/-0.5ppm stability is excellent. SX1281 datasheet requires better than +/-5ppm for reliable FLRC mode.
- Always-on (powered from 3.3V rail directly). No DIO3 control needed.
- Place close to SX1281 XTA pin. Keep trace short and away from digital signals.

## 40MHz Crystal (Y1: CJ17-400001010B20)

LCSC C2875272. SMD 1612-4P (1.6x1.2mm). Changjing, 10pF load, +/-10ppm.

### Pin-by-pin: Crystal (SMD1612-4P)

| Pin | Name | Connection |
|-----|------|------------|
| 1 | XIN | ESP32-C3 XTAL_P (pin 20) + 10pF (C7) to GND |
| 2 | GND | GND |
| 3 | XOUT | ESP32-C3 XTAL_N (pin 21) + 10pF (C8) to GND |
| 4 | GND | GND |

**Notes:**
- 10pF load caps match crystal specification. Actual capacitance seen by crystal = (C_load1 * C_load2) / (C_load1 + C_load2) + C_stray. With 10pF caps and ~2-3pF stray, effective load is ~7-8pF. May need to adjust to 12pF caps if frequency is off.
- Place as close to ESP32-C3 XTAL pins as possible. Route traces as short differential pair.
- Guard ring on GND plane around crystal traces recommended.
- Keep copper pour away from crystal on the other layer.

## RF Path (Low-Pass Filter)

No PA/LNA. In the current KiCad sheet, the ELRS RF path runs from SX1281 RFIO through `DEA102700LT-6307A2` into the Molex `47948-0001` antenna/feed part. The separate `2450AT18A100E` chip antenna is reserved for ESP32-C3 Wi-Fi update mode.

```
SX1281                  LPF                    ELRS Antenna / Feed
RFIO  ---[FL1 DEA102700LT-6307A2]---[feed]--- 47948-0001
(pin 15)   (TDK, 0402-4pin)                   (Molex)
```

### Filter:
- FL1: DEA102700LT-6307A2 (TDK), LCSC C574024, 0402 4-pin multilayer LPF
- 50 ohm input/output, low-pass filtering
- This is the current schematic implementation, but it should not be treated as a Semtech-specific one-part SX1281 match. CE sign-off on the Lite RF path is still pending RF validation.

### Ceramic Antenna: 2450AT18A100E (ANT1)

LCSC C89334. Johanson, 3.2x1.6mm chip antenna.

**Notes:**
- Antenna MUST be placed at PCB edge with ground plane keepout per Johanson application note.
- Minimum 1mm clearance from antenna feed to GND pour on top layer.
- Ground plane on bottom layer should extend under antenna for return path.
- No copper (signal or ground) on the same layer as antenna within keepout zone.
- Performance will be significantly worse than external antenna. Expected range: 200-500m line of sight with ELRS 500Hz mode. Adequate for typical FPV use (proximity/indoor/whoops).

## WS2812B LED (D1, Optional)

Standard addressable RGB LED for status indication.

| Connection | Detail |
|------------|--------|
| VDD | 3.3V (WS2812B works at 3.3V, some variants need 5V -- check datasheet) |
| DIN | ESP32-C3 GPIO10 (pin 11) through 100R series resistor (R4) |
| DOUT | NC |
| GND | GND |
| Decoupling | 100nF (C16) close to VDD pin |

Note: WS2812B is optional. Omit to save BOM cost and board space. ELRS firmware can function without LED.

## Boot Button (SW1)

Tactile switch, normally open.

| Connection | Detail |
|------------|--------|
| One side | ESP32-C3 GPIO9 (pin 10) |
| Other side | GND |
| Pull-up | 10k (R3) from GPIO9 to 3.3V |

Hold button during power-on or reset to enter bootloader (USB or UART download mode).

Note: For production, this can be replaced with solder pads or omitted entirely if UART flashing via FC connection is sufficient. ELRS uses its own bootloader passthrough via UART.

## Connector Pads (J1)

4 castellated or solder pads, 1.27mm pitch, at PCB edge.

| Pad | Signal | Notes |
|-----|--------|-------|
| 1 | 5V | Power input from FC. 3.3-5V range (LDO input). |
| 2 | GND | Ground |
| 3 | TX | ESP32-C3 GPIO0/TX. CRSF data TO flight controller. Connect to FC RX pad. |
| 4 | RX | ESP32-C3 GPIO1/RX. CRSF data FROM flight controller. Connect to FC TX pad. |

## Test Pads

| Pad | Signal | Notes |
|-----|--------|-------|
| TP1 | USB D- | ESP32-C3 GPIO18. For USB flashing during development. |
| TP2 | USB D+ | ESP32-C3 GPIO19. For USB flashing during development. |

## Complete Decoupling Capacitor Summary

| Designator | Value | Package | Location | IC/Pin |
|------------|-------|---------|----------|--------|
| C1 | 10uF | 0603 X5R 10V | LDO input | U3 VIN |
| C2 | 100nF | 0402 X7R 16V | LDO input | U3 VIN |
| C3 | 22uF | 0603 X5R 10V | LDO output | U3 VOUT |
| C4 | 100nF | 0402 X7R 16V | LDO output | U3 VOUT |
| C5 | 100nF | 0402 X7R 16V | ESP32 3V3 | U1 pin 3 |
| C6 | 1uF | 0402 X5R 10V | ESP32 EN | U1 pin 4 (with R1) |
| C7 | 10pF | 0402 C0G 50V | Crystal load | U1 XTAL_P (pin 20) |
| C8 | 10pF | 0402 C0G 50V | Crystal load | U1 XTAL_N (pin 21) |
| C9 | 100nF | 0402 X7R 16V | SX1281 VDD | U2 pin 1 |
| C10 | 100nF | 0402 X7R 16V | SX1281 VDD_IN | U2 pin 2 |
| C11 | 100nF | 0402 X7R 16V | SX1281 NRESET | U2 pin 3 (with R5) |
| C12 | 470nF | 0402 X5R 10V | SX1281 VR_PA | U2 pin 10 (LDO mode) |
| C13 | 100nF | 0402 X7R 16V | SX1281 VDD | U2 pin 11 |
| C14 | 10pF | 0402 C0G 50V | TCXO AC coupling | Y2 out to U2 XTA (optional) |
| C15 | 100nF | 0402 X7R 16V | TCXO VDD | Y2 pin 1 |
| C16 | 100nF | 0402 X7R 16V | WS2812B VDD | D1 (optional) |

## Complete Resistor Summary

| Designator | Value | Package | Location |
|------------|-------|---------|----------|
| R1 | 10k | 0402 | ESP32 EN pull-up |
| R2 | 10k | 0402 | SPI NSS pull-up (shared ESP/SX1281) |
| R3 | 10k | 0402 | BOOT button pull-up |
| R4 | 100R | 0402 | WS2812B data series resistor (optional) |
| R5 | 10k | 0402 | SX1281 NRESET pull-up |

## RF Filter

| Designator | Value | Package | LCSC | Location |
|------------|-------|---------|------|----------|
| FL1 | DEA102700LT-6307A2 | 0402-4pin | C574024 | LPF between SX1281 RFIO and antenna |

## Design Notes and Considerations

### Power Budget
- ESP32-C3 active (WiFi off, CPU running): ~30mA
- SX1281 RX mode: ~7mA
- SX1281 TX mode (no PA): ~25mA at +12.5dBm
- TCXO: ~1.5mA
- WS2812B: ~1mA idle, ~20mA full white
- Total typical (RX mode): ~40mA
- TLV755 500mA capacity provides ample margin

### Layout Priorities (2-layer board)
1. SX1281 ground pad: Maximize thermal vias to bottom GND plane
2. ESP32-C3 ground pad: Same treatment
3. Crystal placement: As close to ESP XTAL pins as physically possible
4. TCXO placement: As close to SX1281 XTA as possible
5. Antenna: At PCB edge, ground plane keepout per Johanson app note
6. Decoupling caps: Each cap within 1mm of its associated IC pin
7. SPI traces: Keep short, matched length not critical at 16MHz max
8. RF trace (RFIO to antenna): 50 ohm controlled impedance if possible. On 2-layer 1.0mm FR4, approximately 1.8mm trace width for 50 ohm microstrip. Short trace length minimizes mismatch impact.

### 2-Layer Stackup (JLCPCB 1.0mm)
- Top: Components, signal routing, RF trace
- Bottom: Continuous GND plane (maximise pour). Route signals on top only where possible.

### Firmware Considerations
- ExpressLRS firmware must be configured for:
  - SX1281 (not SX1280 -- SX1281 has LNA built in)
  - TCXO mode (not crystal)
  - LDO mode (not DC-DC)
  - No PA/LNA control pins
  - GPIO mappings matching this schematic
- CRSF protocol on UART at 420000 baud (ELRS default)
- Binding phrase set in firmware build

### Known Limitations
- No diversity (single antenna, single radio)
- No PA: TX power limited to SX1281 native +12.5dBm max
- No LNA: RX sensitivity limited to SX1281 native (~-105dBm for LoRa, ~-98dBm for FLRC)
- Range estimate: 200-500m LOS at 500Hz, 1-2km at 50Hz. Adequate for proximity/indoor/whoop flying.
- 2-layer RF: impedance control is less precise than a 4-layer board
- Current Lite sheet uses the Molex antenna/feed part, so the older ceramic-antenna range assumptions in this document are stale

---

# OpenRX-Lite Bill of Materials

## 2026-03-23 LCSC Pricing Snapshot

The previous BOM estimate in this document was stale. The table below is based on the current KiCad netlist plus current LCSC search results, using the first listed purchasable price tier. Prices exclude VAT, shipping, PCB, and assembly.

| Ref | Part | LCSC | Current LCSC Price | Availability Note |
|-----|------|------|--------------------|-------------------|
| U1 | ESP32-C3FH4 | C2858491 | $2.2891 | In stock on the most recent LCSC crawl |
| U2 | TLV75533PDQNR | C2861882 | $0.1290 | In stock on the most recent LCSC crawl |
| U3 | SX1281IMLTRT | C2151551 | $3.6011 | Most recent LCSC crawl showed out of stock |
| X1 | CJ17-400001010B20 | C2875272 | $0.2035 | In stock, but not deep stock |
| OSC1 | OW7EL89CENUNFAYLC-52M | C22434896 | $0.7907 | In stock on the most recent LCSC crawl |
| USB1 | DEA102700LT-6307A2 | C574024 | $0.0952 | In stock on the most recent LCSC crawl |
| AE1 | 2450AT18A100E | C89334 | $0.5293 | Wi-Fi update antenna only in the current sheet |
| AE2 | 47948-0001 | C152351 | $1.0869 | Current ELRS antenna/feed part in the sheet |
| D1 | XL-1010RGBC-WS2812B | C5349953 | $0.0732 | Optional |

### Lite Cost Summary

- Base fitted RF/logic subtotal from the current schematic, without optional LED and without passives: `$8.7248`
- With optional LED stuffed: `$8.7980`
- The passive `LCSC` fields in the schematic have now been corrected, but live JLC/LCSC pricing should still be re-quoted before ordering.

### Passive Procurement Status

The Lite schematic passive `LCSC` fields have been corrected. Important current mappings include:

- `100nF 0201` -> `C76939`
- `1uF 0201` -> `C76935`
- `18pF 0201` -> `C62164`
- `1nF 0201` -> `C66942`
- `470nF 0201` -> `C85926`
- `10k 0201` -> `C106225`

### Current Procurement Verdict

- The current Lite is not a `EUR 3-4` receiver. With the fitted parts now in the sheet, it is roughly an `$8.8` class BOM before PCB and assembly.
- Lite is also not currently cheaper than Nano because the present Lite sheet uses the Molex `47948-0001` antenna/feed part, which is materially more expensive than Nano’s `U.FL` path.
- The most important availability blocker is `SX1281IMLTRT`, because the most recent LCSC crawl showed it out of stock.
