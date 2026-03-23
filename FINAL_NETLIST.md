# OpenRX Final Netlist

---

# Part 1: OpenRX-Mono

One ESP32-C3 + one LR1121 + one SKY13588 + one Johanson IPD + one DEA LPF → one UFL → one dual-band antenna.

## Signal Flow

```
                    Sub-GHz:
LR1121 RFI_N (29) ──┐
LR1121 RFI_P (30) ──┤──→ Johanson IPD (balun) ──→ IPD RX out (pin 6)  → SKY13588 J1 (pin 1)
LR1121 RFO_LP (31) ─┤──→ Johanson IPD ──────────→ IPD TX_LP out (pin 8)→ SKY13588 J2 (pin 9)
LR1121 RFO_HP (32) ─┘──→ Johanson IPD ──────────→ IPD TX_HP out (pin 9)→ SKY13588 J3 (pin 3)
                                                                              │
                                                              SKY13588 RFC (pin 11) ──→ UFL
                    2.4GHz:                                                   │
LR1121 RFIO_HF (26) ──→ DEA102700LT-6307A2 (LPF) ───────────────────────────┘
                                                         (joins at antenna trace)
```

The LR1121 only uses one band at a time. When sub-GHz is active, the SKY13588 routes the correct path (RX/TX_LP/TX_HP). When 2.4GHz is active, the switch is OFF (high impedance) and the signal goes through the DEA LPF directly.

## ESP32-C3 GPIO Map (matches `Generic C3 LR1121.json`)

| GPIO | ESP32 Pin # | Symbol Label | Connect To | ELRS Key |
|------|------------|--------------|------------|----------|
| 1 | 5 | XTAL_32K_N | LR1121 DIO9 (pin 9) | `radio_dio1` |
| 2 | 6 | GPIO2 | LR1121 NRESET (pin 6) + 10k pull-up | `radio_rst` |
| 3 | 8 | GPIO3 | LR1121 DIO0/BUSY (pin 25) | `radio_busy` |
| 4 | 9 | MTMS | LR1121 DIO3/MOSI (pin 22) | `radio_mosi` |
| 5 | 10 | MTDI | LR1121 DIO4/MISO (pin 21) | `radio_miso` |
| 6 | 12 | MTCK | LR1121 DIO2/SCK (pin 23) | `radio_sck` |
| 7 | 13 | MTDO | LR1121 DIO1/NSS (pin 24) + 10k pull-up | `radio_nss` |
| 8 | 14 | GPIO8 | WS2812B LED data | `led_rgb` |
| 9 | 15 | GPIO9 | Button + 10k pull-up | `button` |
| 20 | 27 | U0RXD | CRSF RX solder pad | `serial_rx` |
| 21 | 28 | U0TXD | CRSF TX solder pad | `serial_tx` |
| — | 1 | LNA_IN | WiFi antenna (2450AT18A100E) | — |
| — | 30 | XTAL_P | 40MHz crystal via 24nH inductor | — |
| — | 29 | XTAL_N | 40MHz crystal | — |
| — | 7 | CHIP_EN | 10k pull-up + 1uF to GND | — |
| — | 31,32 | VDDA | 3.3V + 1uF decoupling | — |

GPIO 0, 10, 18, 19 are unused on Mono.

## LR1121 Pin-by-Pin

| Pin # | Name | Connect To |
|-------|------|------------|
| 1 | VR_PA | 4.7uF to GND |
| 2 | VBAT_RF | 3.3V + 100nF |
| 3 | VTCXO | 100nF to GND + powers TCXO VDD |
| 4 | XTA | 32MHz TCXO output via 10pF + 220R |
| 5 | XTB | Float |
| 6 | NRESET | ESP32 GPIO2 + 10k pull-up |
| 7 | 32k_P/DIO11 | NC |
| 8 | 32k_N/DIO10 | NC |
| 9 | DIO9 | ESP32 GPIO1 (IRQ) |
| 10 | DIO8 | SKY13588 V2 (pin 5) |
| 11 | DIO7 | SKY13588 V1 (pin 4) |
| 12 | VREG | 100nF to GND only (output, NOT 3.3V) |
| 13 | GND | GND |
| 14 | DCC_SW | 10uH inductor to pin 15 (VBAT) |
| 15 | VBAT | 3.3V + 100nF |
| 16 | DNC | NC |
| 17 | DNC | NC |
| 18 | DNC | NC |
| 19 | DIO6 | 100k pull-down to GND |
| 20 | DIO5 | 100k pull-down to GND |
| 21 | DIO4 | ESP32 GPIO5 (MISO) |
| 22 | DIO3 | ESP32 GPIO4 (MOSI) |
| 23 | DIO2 | ESP32 GPIO6 (SCK) |
| 24 | DIO1 | ESP32 GPIO7 (NSS) + 10k pull-up |
| 25 | DIO0/BUSY | ESP32 GPIO3 |
| 26 | RFIO_HF | DEA102700LT-6307A2 IN |
| 27 | DNC | NC |
| 28 | DNC | NC |
| 29 | RFI_N_LF0 | Johanson IPD pin 4 |
| 30 | RFI_P_LF0 | Johanson IPD pin 3 |
| 31 | RFO_LP_LF | Johanson IPD pin 2 |
| 32 | RFO_HP_LF | Johanson IPD pin 1 |
| 33 | EP | GND |

## Johanson IPD (0900PC16J0042001E) Pin-by-Pin

| Pin # | Name | Connect To |
|-------|------|------------|
| 1 | RFO_HP_LF | LR1121 pin 32 |
| 2 | RFO_LP_LF | LR1121 pin 31 |
| 3 | RFI_P_LF0 | LR1121 pin 30 |
| 4 | RFI_N_LF0 | LR1121 pin 29 |
| 5 | GND | GND |
| 6 | RX | SKY13588 J1 (pin 1) |
| 7 | GND | GND |
| 8 | TX_LP | SKY13588 J2 (pin 9) |
| 9 | TX_HP | SKY13588 J3 (pin 3) |
| 10 | GND | GND |

## SKY13588-460LF Pin-by-Pin

| Pin # | Name | Connect To |
|-------|------|------------|
| 1 | J1 | Johanson IPD RX (pin 6) — sub-GHz receive path |
| 2 | GND | GND |
| 3 | J3 | Johanson IPD TX_HP (pin 9) — sub-GHz high-power TX |
| 4 | V1 | LR1121 DIO7 (pin 11) — switch control |
| 5 | V2 | LR1121 DIO8 (pin 10) — switch control |
| 6 | VDD | 3.3V + 100nF decoupling |
| 7 | GND | GND |
| 8 | GND | GND |
| 9 | J2 | Johanson IPD TX_LP (pin 8) — sub-GHz low-power TX |
| 10 | GND | GND |
| 11 | RFC | Antenna trace → joins DEA LPF output → UFL |
| 12 | GND | GND |
| 13 | EP | GND |

### Switch Truth Table

| V1 (DIO7) | V2 (DIO8) | Active Path | When |
|------------|-----------|-------------|------|
| 0 | 0 | All OFF | Standby or 2.4GHz active |
| 1 | 0 | RFC ↔ J1 | Sub-GHz RX |
| 0 | 1 | RFC ↔ J2 | Sub-GHz TX (low power) |
| 1 | 1 | RFC ↔ J3 | Sub-GHz TX (high power) |

## DEA102700LT-6307A2 (2.4GHz LPF)

| Pin # | Name | Connect To |
|-------|------|------------|
| 1 | IN | LR1121 RFIO_HF (pin 26) |
| 2 | GND | GND |
| 3 | OUT | Antenna trace (same net as SKY13588 RFC) |
| 4 | GND | GND |

## Antenna Junction

SKY13588 RFC (pin 11) and DEA LPF OUT (pin 3) connect to the **same trace** going to the UFL connector. Keep this junction point as small as possible. Only one path is active at a time — no collision.

## 32MHz TCXO Wiring

```
TCXO VDD (pin 4) ← LR1121 VTCXO (pin 3) + 100nF to GND
TCXO OUT (pin 3) → 10pF cap → 220R resistor → LR1121 XTA (pin 4)
TCXO GND (pins 1,2) → GND
LR1121 XTB (pin 5) → float
```

## Mono BOM (new parts vs current schematic)

**Remove:**
- RFX2401C (U3) and caps C25, C26
- One UFL connector (keep JP1, remove JP2)

**Add:**
- SKY13588-460LF (C2151906) + 100nF VDD decoupling
- Rewire DIO7 → V1, DIO8 → V2

**Rewire all ESP32-C3 GPIOs** per the GPIO table above.

---

# Part 2: OpenRX-Gemini

Two identical Mono RF sections sharing one ESP32-C3.

## How to Build

1. Start with the corrected Mono schematic
2. Copy the entire RF section (LR1121 + TCXO + 220R + 10pF + power caps + 10uH inductor + 4.7uF + Johanson IPD + SKY13588 + DEA LPF + UFL)
3. This becomes Radio 2
4. Delete the LED from Radio 1's GPIO (GPIO8 becomes Radio 2 BUSY)
5. Rewire ESP32 GPIOs to match the Gemini target

## What's Different From Mono

| Item | Mono | Gemini |
|------|------|--------|
| LR1121 count | 1 | 2 |
| TCXO count | 1 | 2 |
| SKY13588 count | 1 | 2 |
| Johanson IPD count | 1 | 2 |
| DEA LPF count | 1 | 2 |
| 10uH inductor count | 1 | 2 |
| UFL count | 1 | 2 |
| LED | GPIO8 | **GPIO19** |
| Button | GPIO9 | GPIO9 (same) |
| Radio 1 NSS | GPIO7 | **GPIO0** |
| Radio 2 | — | Added |

## Gemini ESP32-C3 GPIO Rewiring

Starting from Mono, change these connections:

| GPIO | Mono Function | Gemini Function | Action |
|------|---------------|-----------------|--------|
| 0 | NC | **Radio 1 NSS** | Wire to Radio 1 DIO1 (pin 24) + 10k pull-up |
| 7 | Radio 1 NSS | **Radio 2 NSS** | Rewire from Radio 1 to Radio 2 DIO1 (pin 24) + 10k pull-up |
| 8 | LED | **Radio 2 BUSY** | Remove LED, wire to Radio 2 DIO0/BUSY (pin 25) |
| 10 | NC | **Radio 2 RST** | Wire to Radio 2 NRESET (pin 6) |
| 18 | Serial1 RX / NC | **Radio 2 IRQ** | Wire to Radio 2 DIO9 (pin 9) |
| 19 | Serial1 TX / NC | **LED** | Wire to WS2812B |

Keep unchanged:
- GPIO 1 → Radio 1 DIO9 (IRQ)
- GPIO 2 → Radio 1 NRESET
- GPIO 3 → Radio 1 BUSY
- GPIO 4 → SPI MOSI (shared to both radios)
- GPIO 5 → SPI MISO (shared to both radios)
- GPIO 6 → SPI SCK (shared to both radios)
- GPIO 9 → Button
- GPIO 20 → CRSF RX
- GPIO 21 → CRSF TX

## Radio 2 LR1121 Wiring

Identical to Radio 1 (see Part 1 LR1121 pin table), except:

| Pin | Radio 1 connects to | Radio 2 connects to |
|-----|---------------------|---------------------|
| 9 (DIO9/IRQ) | ESP32 GPIO1 | ESP32 **GPIO18** |
| 24 (DIO1/NSS) | ESP32 GPIO7 → **GPIO0** | ESP32 **GPIO7** |
| 25 (DIO0/BUSY) | ESP32 GPIO3 | ESP32 **GPIO8** |
| 6 (NRESET) | ESP32 GPIO2 | ESP32 **GPIO10** |

All other LR1121 pins (power, TCXO, RF) are identical to Radio 1 but with their own dedicated components.

## Radio 2 RF Section

Exact copy of Radio 1:
- Own LR1121 + own TCXO + own power caps + own 10uH inductor
- Own SKY13588 (DIO7→V1, DIO8→V2 from Radio 2's LR1121)
- Own Johanson IPD
- Own DEA LPF on RFIO_HF
- Own UFL connector

Radio 2's sub-GHz and 2.4GHz paths combine at its own UFL, same as Radio 1.

## Gemini Shared SPI Bus

Three wires connect to both radios:

```
ESP32 GPIO4 (MOSI) → Radio 1 DIO3 (pin 22) AND Radio 2 DIO3 (pin 22)
ESP32 GPIO5 (MISO) → Radio 1 DIO4 (pin 21) AND Radio 2 DIO4 (pin 21)
ESP32 GPIO6 (SCK)  → Radio 1 DIO2 (pin 23) AND Radio 2 DIO2 (pin 23)
```

NSS lines are separate — the ESP32 selects which radio to talk to by pulling the correct NSS LOW.

---

## Routing Notes

1. **50Ω traces** on all RF paths (SKY13588 RFC → UFL, DEA OUT → junction, RFIO_HF → DEA IN)
2. **Differential pair** for LR1121 RFI_N/RFI_P → Johanson IPD (matched length, tight coupling)
3. **Place Johanson IPD adjacent to LR1121** — differential traces must be short
4. **Place SKY13588 between IPD and UFL** — minimize trace length on switched paths
5. **Place DEA LPF near the antenna junction** — short 2.4GHz trace to UFL
6. **Antenna junction** where sub-GHz (RFC) and 2.4GHz (DEA OUT) meet: keep stub as short as possible
7. **Solid ground pour** on bottom layer, via stitch around all RF components
8. **No routing under LR1121, SKY13588, or Johanson IPD** on the opposite layer
9. **TCXO close to LR1121 XTA** with 220R+10pF in the signal path
10. **10uH inductor close to LR1121 DCC_SW** — tight DC-DC loop to VBAT
11. **WiFi antenna (2450AT18A100E) at board edge** — separate from ELRS RF section, min 5mm keepout
12. **Crystal 40MHz close to ESP32 XTAL pins** — 24nH inductor on XTAL_P side, 18pF load caps
13. **For Gemini: keep both RF sections symmetric** — mirror layout if possible for consistent RF performance
