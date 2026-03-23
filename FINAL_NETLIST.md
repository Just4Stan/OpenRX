# OpenRX Final Netlist — Mono & Gemini

## Topology Overview

### Mono (1× LR1121, 1 UFL, 1 dual-band antenna)

```
                          ┌─ DIO7 (V1) ──────────────────────┐
                          ├─ DIO8 (V2) ──────────────────────┤
ESP32-C3 ←SPI→ LR1121 ──┤                                   │
                          ├─ RFI_N/P ──→ Johanson IPD ──→ SKY13588 J1 (RX)
                          ├─ RFO_HP_LF ─────────────────→ SKY13588 J2 (TX)
                          ├─ RFO_LP_LF ─────────────────→ (NC or J3)
                          │                                   │
                          │                    SKY13588 RFC ──┼──→ UFL → dual-band antenna
                          │                                   │
                          ├─ RFIO_HF ──→ DEA LPF ────────────┘
                          │              (2.4GHz joins at antenna)
                          ├─ DIO5 (2.4GHz RX enable) ─→ controls HF path
                          └─ DIO6 (2.4GHz TX enable) ─→ controls HF path
```

The sub-GHz path goes through the SKY13588. The 2.4GHz path bypasses the switch and joins at the antenna. The LR1121 RFSW DIO pins control both the switch AND the 2.4GHz path enable.

### Gemini (2× LR1121, 2 UFL, 2 dual-band antennas)

Two identical Mono RF chains sharing one ESP32-C3 via SPI bus.

---

## Mono GPIO Map (matches `Generic C3 LR1121.json`)

| GPIO | ESP32-C3 Pin # | Symbol Label | Function | ELRS Key |
|------|---------------|--------------|----------|----------|
| 0 | 4 | XTAL_32K_P | — (NC on Mono) | — |
| 1 | 5 | XTAL_32K_N | LR1121 DIO9 (IRQ) | `radio_dio1` |
| 2 | 6 | GPIO2 | LR1121 NRESET | `radio_rst` |
| 3 | 8 | GPIO3 | LR1121 BUSY | `radio_busy` |
| 4 | 9 | MTMS | SPI MOSI | `radio_mosi` |
| 5 | 10 | MTDI | SPI MISO | `radio_miso` |
| 6 | 12 | MTCK | SPI SCK | `radio_sck` |
| 7 | 13 | MTDO | LR1121 NSS | `radio_nss` |
| 8 | 14 | GPIO8 | LED (WS2812B) | `led_rgb` |
| 9 | 15 | GPIO9 | Button | `button` |
| 10 | 16 | GPIO10 | — (available) | — |
| 18 | 25 | GPIO18 | Serial1 RX (optional) | `serial1_rx` |
| 19 | 26 | GPIO19 | Serial1 TX (optional) | `serial1_tx` |
| 20 | 27 | U0RXD | CRSF RX | `serial_rx` |
| 21 | 28 | U0TXD | CRSF TX | `serial_tx` |
| — | 1 | LNA_IN | WiFi antenna (2450AT18A100E) | — |

**NOTE:** This is DIFFERENT from our current Mono schematic. Major changes:
- NSS moved from GPIO8 → GPIO7
- IRQ moved from GPIO5 → GPIO1 (XTAL_32K_N)
- MOSI moved from GPIO7 → GPIO4
- MISO moved from GPIO6 → GPIO5
- SCK moved from GPIO4 → GPIO6
- LED moved from GPIO10 → GPIO8

## Gemini GPIO Map (matches `Generic C3 LR1121 True Diversity.json`)

| GPIO | ESP32-C3 Pin # | Function | ELRS Key |
|------|---------------|----------|----------|
| 0 | 4 | Radio 1 NSS | `radio_nss` |
| 1 | 5 | Radio 1 IRQ (DIO9) | `radio_dio1` |
| 2 | 6 | Radio 1 RST | `radio_rst` |
| 3 | 8 | Radio 1 BUSY | `radio_busy` |
| 4 | 9 | SPI MOSI (shared) | `radio_mosi` |
| 5 | 10 | SPI MISO (shared) | `radio_miso` |
| 6 | 12 | SPI SCK (shared) | `radio_sck` |
| 7 | 13 | Radio 2 NSS | `radio_nss_2` |
| 8 | 14 | Radio 2 BUSY | `radio_busy_2` |
| 9 | 15 | Button | `button` |
| 10 | 16 | Radio 2 RST | `radio_rst_2` |
| 18 | 25 | Radio 2 IRQ (DIO9) | `radio_dio1_2` |
| 19 | 26 | LED (WS2812B) | `led_rgb` |
| 20 | 27 | CRSF RX | `serial_rx` |
| 21 | 28 | CRSF TX | `serial_tx` |

---

## LR1121 → SKY13588 → Johanson IPD Wiring (per radio)

### LR1121 Sub-GHz Pins → SKY13588

| LR1121 Pin # | LR1121 Name | → | SKY13588 Pin # | SKY13588 Name | Notes |
|---|---|---|---|---|---|
| 29 | RFI_N_LF0 | → | — | — | Goes to Johanson IPD pin 4 |
| 30 | RFI_P_LF0 | → | — | — | Goes to Johanson IPD pin 3 |
| 31 | RFO_LP_LF | → | — | — | NC (use HP only, or connect to J3) |
| 32 | RFO_HP_LF | → | 9 | J2 | TX HP path through switch |

Wait — the sub-GHz RX path is differential (RFI_N/RFI_P) and needs the Johanson IPD balun BEFORE it can go through the single-ended SKY13588. The correct topology:

### Corrected Signal Flow

```
Sub-GHz RX path:
  Antenna → UFL → SKY13588 RFC (pin 11) → SKY13588 J1 (pin 1) → Johanson IPD ANT side
  Johanson IPD differential side → LR1121 RFI_P (pin 30) + RFI_N (pin 29)

Sub-GHz TX path:
  LR1121 RFO_HP_LF (pin 32) → Johanson IPD → SKY13588 J2 (pin 9) → SKY13588 RFC → UFL → Antenna
```

Actually this doesn't work — the Johanson IPD has separate ports for RX, TX_LP, TX_HP. The IPD itself combines/splits the paths. The switch goes BETWEEN the IPD and the antenna, not between the LR1121 and the IPD.

### CORRECT Signal Flow (IPD → Switch → Antenna)

```
LR1121 RFI_N/P (pins 29-30) → Johanson IPD RFI ports (pins 3-4)
LR1121 RFO_LP_LF (pin 31)  → Johanson IPD RFO_LP port (pin 2)
LR1121 RFO_HP_LF (pin 32)  → Johanson IPD RFO_HP port (pin 1)

Johanson IPD RX output (pin 6)     → SKY13588 J1 (pin 1)
Johanson IPD TX_LP output (pin 8)  → SKY13588 J2 (pin 9)  [or NC if not using LP]
Johanson IPD TX_HP output (pin 9)  → SKY13588 J3 (pin 3)

SKY13588 RFC (pin 11) → combines with 2.4GHz path → UFL → dual-band antenna
```

### 2.4GHz Path (bypasses SKY13588)

```
LR1121 RFIO_HF (pin 26) → DEA102700LT-6307A2 (LPF) → joins at antenna trace before UFL
```

The 2.4GHz path connects to the same antenna trace/UFL as the SKY13588 RFC output. Since the LR1121 only activates one band at a time, there's no collision. When 2.4GHz is active, the switch is in standby (all OFF), presenting high impedance on the sub-GHz path.

### SKY13588 Control (from LR1121 RFSW DIOs)

| LR1121 DIO | Pin # | → | SKY13588 Pin # | SKY13588 Name |
|---|---|---|---|---|
| DIO7 | 11 (DIO7/VREG) | → | 4 | V1 |
| DIO8 | 10 (DIO8) | → | 5 | V2 |

**WAIT — DIO7 is pin 11 which is VREG (internal LDO output).** This conflicts. Let me re-check the LR1121 pinout...

Actually, looking at the LR1121 symbol from our schematic: pin 11 is labeled "DIO7" on the imported symbol. The VREG is pin 12. So DIO7 = pin 11, VREG = pin 12. The naming in different datasheets varies. Using our imported symbol's pin numbering:

| LR1121 Pin # | Our Symbol Label | → | SKY13588 Pin # | Function |
|---|---|---|---|---|
| 11 | DIO7 | → | 4 | V1 (switch control) |
| 10 | DIO8 | → | 5 | V2 (switch control) |

### SKY13588 Truth Table (with RFSW mapping)

| Mode | DIO7 (V1) | DIO8 (V2) | SKY13588 Path | RF Function |
|---|---|---|---|---|
| Standby | 0 | 0 | All OFF | Sub-GHz isolated |
| Sub-GHz RX | 1 | 0 | RFC ↔ J1 | Antenna → Johanson RX → LR1121 RFI |
| Sub-GHz TX | 0 | 1 | RFC ↔ J2 | LR1121 RFO_LP → Johanson TX_LP → Antenna |
| Sub-GHz TX HP | 1 | 1 | RFC ↔ J3 | LR1121 RFO_HP → Johanson TX_HP → Antenna |

When 2.4GHz is active (TX_HF or WiFi/HF_RX modes), DIO7 and DIO8 are both LOW (switch off), and DIO5/DIO6 control the 2.4GHz path. The 2.4GHz signal goes through the DEA LPF directly to the antenna.

### SKY13588 Power

| Pin # | Name | Connect To |
|---|---|---|
| 6 | VDD | 3.3V + 100nF decoupling |
| 2, 7, 8, 10, 12, 13 | GND / EP | GND |

### LR1121 RFSW DIO Connections Summary

| LR1121 DIO | Pin # | Connection | Function |
|---|---|---|---|
| DIO5 | 20 | Controls 2.4GHz RX path enable | Pull-down when unused |
| DIO6 | 19 | Controls 2.4GHz TX path enable | Pull-down when unused |
| DIO7 | 11 | SKY13588 V1 | Sub-GHz switch control |
| DIO8 | 10 | SKY13588 V2 | Sub-GHz switch control |

DIO5/DIO6 may go to nothing physical for now (the 2.4GHz path is passive — DEA LPF only). They could control an optional FEM if added later. Keep 100k pull-downs on DIO5 and DIO6.

---

## Complete Mono BOM (RF section)

| Ref | Part | LCSC | Package | Price | Function |
|---|---|---|---|---|---|
| U4 | LR1121IMLTRT | C7498014 | QFN-32 5×5 | ~$2.50 | Multi-band transceiver |
| SW1 | SKY13588-460LF | C2151906 | QFN-12 2×2 | ~$0.89 | SP3T RF switch |
| T1 | 0900PC16J0042001E | C19842466 | 10-pad 2.0×1.6 | ~$0.96 | Sub-GHz IPD (balun+filter) |
| FL1 | DEA102700LT-6307A2 | C574024 | 0402 4-pin | ~$0.10 | 2.4GHz LPF (harmonics) |
| U5 | OW7EL89CENUYO3YLC-32M | C22381772 | SMD2016 | ~$0.40 | 32MHz TCXO |
| JP1 | U.FL-R-SMT-1(80) | C88374 | SMD | ~$0.08 | Antenna connector |
| R_TCXO | 220R | C274342 | 0201 | ~$0.01 | TCXO series resistor |
| C_TCXO | 10pF | C20069240 | 0201 | ~$0.01 | TCXO DC-cut cap |
| C_SW | 100nF | C76939 | 0201 | ~$0.01 | SKY13588 VDD decoupling |
| C_VR_PA | 4.7uF | C23733 | 0402 | ~$0.01 | LR1121 VR_PA |
| L_DC | 10uH | C6808014 | 0603 | ~$0.02 | LR1121 DC-DC inductor |
| + | 4× 100nF | C76939 | 0201 | — | LR1121 VBAT_RF, VTCXO, VREG, VBAT |
| + | 2× 100k | C270364 | 0201 | — | DIO5, DIO6 pull-downs |
| + | 1× 100k | C270364 | 0201 | — | DIO7 or DIO8 pull-down (if not using LP path) |

**Mono RF subtotal: ~$4.99**

---

## Gemini BOM (RF section = 2× Mono RF)

Same as above ×2, plus the Gemini-specific GPIO differences (no serial1, LED on GPIO19 instead of GPIO8).

**Gemini RF subtotal: ~$9.98**

---

## Routing Notes (put on schematic)

1. **SKY13588 RFC → UFL trace**: 50Ω controlled impedance, as short as possible. Ground vias on both sides.
2. **2.4GHz path (RFIO_HF → DEA → antenna junction)**: 50Ω microstrip, keep under 5mm. This joins the sub-GHz trace at the UFL pad.
3. **Sub-GHz differential (RFI_N/RFI_P)**: Matched-length differential pair from LR1121 to Johanson IPD. Keep within 0.5mm of each other.
4. **Johanson IPD placement**: As close to LR1121 as possible. The differential traces are very short-range sensitive.
5. **SKY13588 placement**: Between Johanson IPD and UFL connector. Keep all RF traces on one layer (top).
6. **DEA LPF placement**: Between LR1121 RFIO_HF and the antenna junction point. Place near the junction, not near the LR1121.
7. **32MHz TCXO**: Place close to LR1121 XTA. 220R + 10pF in series on the signal path.
8. **10uH inductor (DC-DC)**: Place close to LR1121 DCC_SW pin. Short loop area with VBAT.
9. **Ground pour**: Solid ground on bottom layer. Via stitch around all RF components. No signal routing under RF ICs.
10. **Band junction**: Where 2.4GHz and sub-GHz traces meet before the UFL, keep the junction as small as possible. The inactive path presents high impedance, but minimizing stub length reduces parasitic effects.
11. **WiFi antenna (2450AT18A100E)**: Board edge, separate from ELRS RF section. Minimum 5mm keepout.
12. **Crystal (40MHz)**: Close to ESP32-C3 XTAL pins. 24nH series inductor on XTAL_P. No routing under crystal.
