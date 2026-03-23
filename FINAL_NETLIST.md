# OpenRX Final Netlist

Based on RadioMaster XR4 teardown analysis and ELRS firmware targets.

---

# Part 1: OpenRX-Mono

One ESP32-C3 + one LR1121 + one RFX2401C + one SKY13588 + one Johanson IPD + one DEA LPF → one UFL → one dual-band antenna.

## Signal Flow

```
Sub-GHz path (direct-tie):
  LR1121 RFI_N/P (pins 29-30) ──┐
  LR1121 RFO_LP_LF (pin 31)  ──┤──→ Johanson IPD (all outputs tied together) ──→ SKY13588 J1
  LR1121 RFO_HP_LF (pin 32)  ──┘

2.4GHz path:
  LR1121 RFIO_HF (pin 26) ──→ DEA102700LT LPF ──→ RFX2401C ──→ SKY13588 J2

Band selection (SKY13588):
  J1 (sub-GHz) ──┐
  J2 (2.4GHz)  ──┤──→ RFC ──→ DC block / matching ──→ UFL ──→ dual-band antenna
  J3 (unused)  ──┘
```

The SKY13588 acts as the **final LF/HF band-select switch** between the sub-GHz branch and the 2.4GHz branch. It does NOT handle sub-GHz RX/TX selection — that is handled by the direct-tie arrangement at the Johanson IPD. Only one band is active at a time. The LR1121 RFSW DIO pins control which port is connected to RFC.

The Johanson IPD is used here in an **inferred XR4-style direct-tie mode** — all three antenna-side ports (RX pin 6, TX_LP pin 8, TX_HP pin 9) are tied together and feed as one single-ended sub-GHz node into SKY13588 J1. **This is a deliberate cost/size tradeoff: direct-tie results in ~2-3 dB RX sensitivity loss on sub-GHz compared to a fully switched implementation.** The LR1121 was designed for use with an external switch on the sub-GHz path; direct-tie is a valid but performance-compromised alternative and should be validated with RF measurement on prototypes.

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
| 9 | 15 | GPIO9 | Button (C2976675) + 10k pull-up | `button` |
| 20 | 27 | U0RXD | CRSF RX solder pad | `serial_rx` |
| 21 | 28 | U0TXD | CRSF TX solder pad | `serial_tx` |
| — | 1 | LNA_IN | WiFi antenna (2450AT18A100E) | — |
| — | 30 | XTAL_P | 40MHz crystal via 24nH inductor | — |
| — | 29 | XTAL_N | 40MHz crystal | — |
| — | 7 | CHIP_EN | 10k pull-up + 1uF to GND | — |
| — | 31,32 | VDDA | 3.3V + 1uF decoupling | — |

GPIO 0, 10, 18, 19 are NC on Mono.

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
| 10 | DIO8 | SKY13588 V2 (pin 5) — band/path select |
| 11 | DIO7 | SKY13588 V1 (pin 4) — band/path select |
| 12 | VREG | 100nF to GND only (output, NOT to 3.3V) |
| 13 | GND | GND |
| 14 | DCC_SW | 10uH inductor to pin 15 (VBAT) |
| 15 | VBAT | 3.3V + 100nF |
| 16-18 | DNC | NC |
| 19 | DIO6 | 100k pull-down to GND |
| 20 | DIO5 | 100k pull-down to GND |
| 21 | DIO4 | ESP32 GPIO5 (MISO) |
| 22 | DIO3 | ESP32 GPIO4 (MOSI) |
| 23 | DIO2 | ESP32 GPIO6 (SCK) |
| 24 | DIO1 | ESP32 GPIO7 (NSS) + 10k pull-up |
| 25 | DIO0/BUSY | ESP32 GPIO3 |
| 26 | RFIO_HF | DEA102700LT-6307A2 IN |
| 27-28 | DNC | NC |
| 29 | RFI_N_LF0 | Johanson IPD pin 4 |
| 30 | RFI_P_LF0 | Johanson IPD pin 3 |
| 31 | RFO_LP_LF | Johanson IPD pin 2 |
| 32 | RFO_HP_LF | Johanson IPD pin 1 |
| 33 | EP | GND |

## Johanson IPD (0900PC16J0042001E) — Direct-Tie Mode

| Pin # | Name | Connect To |
|-------|------|------------|
| 1 | RFO_HP_LF | LR1121 pin 32 |
| 2 | RFO_LP_LF | LR1121 pin 31 |
| 3 | RFI_P_LF0 | LR1121 pin 30 |
| 4 | RFI_N_LF0 | LR1121 pin 29 |
| 5 | GND | GND |
| 6 | RX | **Tied together** → SKY13588 J1 (pin 1) |
| 7 | GND | GND |
| 8 | TX_LP | **Tied together** → SKY13588 J1 (pin 1) |
| 9 | TX_HP | **Tied together** → SKY13588 J1 (pin 1) |
| 10 | GND | GND |

Pins 6, 8, 9 all connect to the same net going to SKY13588 J1. This is the direct-tie topology.

## RFX2401C (2.4GHz PA+LNA)

| Pin | Name | Connect To |
|-----|------|------------|
| 4 | TXRX | DEA102700LT-6307A2 OUT (from LR1121 RFIO_HF) |
| 10 | ANT | **0.3pF shunt to GND** (mandatory, 5th harmonic) + 50Ω trace → SKY13588 J2 (pin 9) |
| 5 | TXEN | LR1121 DIO6 (pin 19) |
| 6 | RXEN | LR1121 DIO5 (pin 20) |
| 14,16 | VDD | 3.3V + 1uF + 220pF |
| 1,2,3,7,8,9,11,12,15,17 | GND/EP | GND |

The 0.3pF C0G cap on ANT is **mandatory per Skyworks datasheet** — filters the 5th harmonic (~12GHz). Place as close to pin 10 as possible. Use a real stuffed capacitor as the baseline; leave room to tune around that value during RF validation if needed.

**RFSW firmware config:** The default ELRS `radio_rfsw_ctrl` does NOT match this topology. You must provide a **custom `radio_rfsw_ctrl` array** in hardware.json that:
- Sets DIO8 HIGH (V2) for sub-GHz → RFC↔J1
- Sets DIO7 HIGH (V1) for 2.4GHz → RFC↔J2
- Sets DIO5 HIGH for RFX2401C RXEN during 2.4GHz RX
- Sets DIO6 HIGH for RFX2401C TXEN during 2.4GHz TX
- All DIO LOW for standby

Custom `radio_rfsw_ctrl` for this exact topology using `SKY13588-460LF`:
```json
"radio_rfsw_ctrl": [15, 0, 8, 8, 8, 6, 0, 5]
```
Decoded (bit0=DIO5, bit1=DIO6, bit2=DIO7, bit3=DIO8):
- `15` = enable DIO5,6,7,8
- `0` = standby: all LOW
- `8` = sub-GHz RX: DIO8 HIGH (0b1000) → V1=0,V2=1 → RFC↔J1, FEM off
- `8` = sub-GHz TX LP: same sub-GHz selection
- `8` = sub-GHz TX HP: same sub-GHz selection
- `6` = 2.4GHz TX: DIO6 + DIO7 HIGH (0b0110) → TXEN=1, V1=1,V2=0 → RFC↔J2
- `5` = 2.4GHz RX / WiFi: DIO5 + DIO7 HIGH (0b0101) → RXEN=1, V1=1,V2=0 → RFC↔J2

If the final RF switch is **not** `SKY13588-460LF`, or if the control pins are reassigned, the array must be recalculated.

## DEA102700LT-6307A2 (2.4GHz LPF)

| Pin # | Name | Connect To |
|-------|------|------------|
| 1 | IN | LR1121 RFIO_HF (pin 26) |
| 2 | GND | GND |
| 3 | OUT | RFX2401C TXRX (pin 4) |
| 4 | GND | GND |

## SKY13588-460LF (SP3T Band Select Switch)

| Pin # | Name | Connect To |
|-------|------|------------|
| 1 | J1 | Johanson IPD direct-tie output (pins 6+8+9 joined) — sub-GHz |
| 2 | GND | GND |
| 3 | J3 | NC (unused third throw) |
| 4 | V1 | LR1121 DIO7 (pin 11) |
| 5 | V2 | LR1121 DIO8 (pin 10) |
| 6 | VDD | 3.3V + 100nF |
| 7 | GND | GND |
| 8 | GND | GND |
| 9 | J2 | RFX2401C ANT (pin 10) — 2.4GHz |
| 10 | GND | GND |
| 11 | RFC | DC block cap → UFL → dual-band antenna |
| 12 | GND | GND |
| 13 | EP | GND |

### Switch Truth Table (controlled by LR1121 RFSW)

| V1 (DIO7) | V2 (DIO8) | RFC connects to | Mode |
|------------|-----------|-----------------|------|
| 0 | 0 | All OFF | Standby |
| 1 | 0 | J2 | 2.4GHz active |
| 0 | 1 | J1 | Sub-GHz active |
| 1 | 1 | J3 | Unused |

**The default ELRS `radio_rfsw_ctrl` does NOT match this topology.** For the exact `SKY13588 + RFX2401C + DIO5..DIO8` mapping documented here, use:
```json
"radio_rfsw_ctrl": [15, 0, 8, 8, 8, 6, 0, 5]
```
Validate the actual DIO-to-switch-pin mapping on your prototype — the exact truth table depends on which DIO connects to which switch control pin and how the RFX2401C TXEN/RXEN respond.

## 32MHz TCXO Wiring

```
TCXO VDD (pin 4) ← LR1121 VTCXO (pin 3) + 100nF to GND
TCXO OUT (pin 3) → 10pF cap → 220R resistor → LR1121 XTA (pin 4)
TCXO GND (pins 1,2) → GND
LR1121 XTB (pin 5) → float
```

## Mono BOM (RF section)

| Ref | Part | LCSC | Package | Price | Function |
|-----|------|------|---------|-------|----------|
| U4 | LR1121IMLTRT | C7498014 | QFN-32 5×5 | ~$2.50 | Multi-band transceiver |
| U6 | SKY13588-460LF | C2151906 | QFN-12 2×2 | ~$0.89 | SP3T band select switch |
| U3 | RFX2401C | C19213 | QFN-16 3×3 | ~$0.51 | 2.4GHz PA+LNA (100mW) |
| T1 | 0900PC16J0042001E | C19842466 | 10-pad 2.0×1.6 | ~$0.96 | Sub-GHz IPD (direct-tie) |
| FL1 | DEA102700LT-6307A2 | C574024 | 0402 4-pin | ~$0.10 | 2.4GHz LPF |
| U5 | OW7EL89CENUYO3YLC-32M | C22381772 | SMD2016 | ~$0.40 | 32MHz TCXO |
| JP1 | U.FL-R-SMT-1(80) | C88374 | SMD | ~$0.08 | Antenna connector |
| — | 220R | C274342 | 0201 | ~$0.01 | TCXO series resistor |
| — | 10pF | C20069240 | 0201 | ~$0.01 | TCXO DC-cut cap |
| — | 100nF ×5 | C76939 | 0201 | — | SKY VDD + LR1121 decoupling |
| — | 4.7uF | C23733 | 0402 | — | LR1121 VR_PA |
| — | 10uH | C6808014 | 0603 | — | LR1121 DC-DC |
| — | 1uF + 220pF | C76935 + C62548 | 0201 | — | RFX2401C VDD |
| — | 0.3pF nominal | — | 0402 pad | — | RFX2401C ANT 5th harmonic (mandatory, tune only after measurement) |
| — | 100k ×2 | C270364 | 0201 | — | DIO5, DIO6 pull-downs |

**Mono RF subtotal: ~$5.46**

---

# Part 2: OpenRX-Gemini

Two identical Mono RF sections sharing one ESP32-C3.

## How to Build

1. Start with the corrected Mono schematic
2. Copy the entire RF section: LR1121 + TCXO + 220R + 10pF + power caps + 10uH + 4.7uF + Johanson IPD + SKY13588 + DEA LPF + RFX2401C + 1uF + 220pF + UFL
3. This becomes Radio 2
4. Rewire ESP32 GPIOs per the Gemini table below

## Gemini ESP32-C3 GPIO Map (matches `Generic C3 LR1121 True Diversity.json`)

| GPIO | ESP32 Pin # | Function | ELRS Key |
|------|------------|----------|----------|
| 0 | 4 | Radio 1 NSS + 10k pull-up | `radio_nss` |
| 1 | 5 | Radio 1 IRQ (DIO9) | `radio_dio1` |
| 2 | 6 | Radio 1 RST + 10k pull-up | `radio_rst` |
| 3 | 8 | Radio 1 BUSY | `radio_busy` |
| 4 | 9 | SPI MOSI (shared) | `radio_mosi` |
| 5 | 10 | SPI MISO (shared) | `radio_miso` |
| 6 | 12 | SPI SCK (shared) | `radio_sck` |
| 7 | 13 | Radio 2 NSS + 10k pull-up | `radio_nss_2` |
| 8 | 14 | Radio 2 BUSY | `radio_busy_2` |
| 9 | 15 | Button + 10k pull-up | `button` |
| 10 | 16 | Radio 2 RST | `radio_rst_2` |
| 18 | 25 | Radio 2 IRQ (DIO9) | `radio_dio1_2` |
| 19 | 26 | LED (WS2812B) | `led_rgb` |
| 20 | 27 | CRSF RX | `serial_rx` |
| 21 | 28 | CRSF TX | `serial_tx` |

## Differences from Mono → Gemini

| GPIO | Mono | Gemini | Change |
|------|------|--------|--------|
| 0 | NC | **Radio 1 NSS** | Wire to R1 DIO1 (pin 24) + pull-up |
| 7 | Radio 1 NSS | **Radio 2 NSS** | Rewire to R2 DIO1 (pin 24) + pull-up |
| 8 | LED | **Radio 2 BUSY** | Remove LED, wire to R2 DIO0 (pin 25) |
| 10 | NC | **Radio 2 RST** | Wire to R2 NRESET (pin 6) |
| 18 | NC | **Radio 2 IRQ** | Wire to R2 DIO9 (pin 9) |
| 19 | NC | **LED** | Wire to WS2812B |

## Radio 2 Wiring

Identical to Radio 1 except for ESP32 connections:

| LR1121 Pin | Radio 1 → ESP32 | Radio 2 → ESP32 |
|------------|-----------------|-----------------|
| DIO9 (9) IRQ | GPIO1 | **GPIO18** |
| DIO1 (24) NSS | GPIO0 | **GPIO7** |
| DIO0 (25) BUSY | GPIO3 | **GPIO8** |
| NRESET (6) | GPIO2 | **GPIO10** |
| DIO3 (22) MOSI | GPIO4 (shared) | GPIO4 (shared) |
| DIO4 (21) MISO | GPIO5 (shared) | GPIO5 (shared) |
| DIO2 (23) SCK | GPIO6 (shared) | GPIO6 (shared) |

Radio 2's SKY13588 V1/V2 are controlled by Radio 2's own LR1121 DIO7/DIO8 — no ESP32 GPIOs involved. Same for RFX2401C TXEN/RXEN via Radio 2's DIO5/DIO6.

Each radio has its own complete RF chain → its own UFL → its own dual-band antenna. 2 UFL total.

---

## Routing Notes

1. **SKY13588 RFC → UFL**: 50Ω controlled impedance, DC block cap in series, as short as possible
2. **Johanson IPD → SKY13588 J1**: short 50Ω trace, this carries the direct-tie sub-GHz signal
3. **RFX2401C ANT → SKY13588 J2**: short 50Ω trace, this carries the amplified 2.4GHz signal
4. **LR1121 RFIO_HF → DEA → RFX2401C TXRX**: 50Ω, keep DEA close to RFIO_HF
5. **LR1121 RFI_N/RFI_P → IPD**: matched-length differential pair, as short as possible
6. **Place order on PCB**: LR1121 → (IPD + DEA/RFX2401C side by side) → SKY13588 → UFL at board edge
7. **SKY13588 VDD**: 100nF decoupling right at pin 6
8. **RFX2401C VDD**: 1uF + 220pF close to VDD pins
9. **Ground pour**: solid bottom layer, via stitch around all RF components
10. **No routing under RF ICs** on opposite layer
11. **TCXO**: close to LR1121 XTA, 220R + 10pF in signal path
12. **10uH inductor**: close to LR1121 DCC_SW, tight loop to VBAT
13. **WiFi antenna**: board edge, separate from ELRS RF, 5mm keepout
14. **40MHz crystal**: close to ESP32 XTAL pins, 24nH on XTAL_P, 18pF load caps
15. **For Gemini**: mirror the two RF sections symmetrically for consistent performance
