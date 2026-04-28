# JLC Panel BOM Quote — 2026-04-28 (1000 units, 4-SKU panel)

Quote pulled from JLC SMT estimator for `AllOpenRXV0.1` panel, 1200-piece run (1000 + ~17% overage).
Panel contains 1× of each SKU: Lite (ceramic) + Lite-UFL + Mono + Gemini.

## Refdes-suffix → SKU mapping
JLC's panelizer adds a numeric suffix only when refdes collides between SKUs. The suffix tracks the panel position (`_2`, `_3`, `_4` are duplicates of the bare refdes from another SKU). After mapping the JLC list against each schematic netlist:
- bare (no suffix) → first occurrence in panel order, often **Mono** or **Gemini** (Gemini has unique refdes like U9, U15, U17, U18 because of its higher count)
- `_2`, `_3`, `_4` → copies in other SKUs

## JLC unit prices (panel buy at 1000 units)

| LCSC | Part | JLC qty stocked | $/unit | Status |
|------|------|----------------|--------|--------|
| C152351 | 47948-0001 SMD UFL | 1200 | 0.7051 | InStock |
| C76939 | 100nF 0201 | 51667 | 0.00180 | InStock |
| C62548 | 220pF 0201 | 3610 | 0.000500 | InStock |
| C76927 | 0.3pF 0201 | 3610 | 0.00380 | InStock |
| C23733 | 4.7uF 0402 | 3610 | 0.00420 | Basic |
| C76921 | 10pF 0201 | 3620 | 0.00130 | InStock |
| C76935 | 1uF 0201 | 21624 | 0.00190 | InStock |
| C66942 | 1nF 0201 | 2410 | 0.000600 | InStock |
| C62164 | 18pF 0201 | 9620 | 0.000600 | InStock |
| C85926 | 470nF 0201 | 2412 | 0.00280 | InStock |
| C15525 | 10uF 0402 | 9620 | 0.00400 | Basic |
| C5349953 | XL-1010RGBC WS2812B | 4805 | 0.04130 | InStock |
| C88374 | U.FL receptacle | 4804 | 0.07120 | InStock |
| C1035 | 10uH 0603 | 3610 | 0.01350 | Basic |
| C206441 | 24nH 0201 | 4820 | 0.00530 | InStock |
| C22434896 | 52MHz XO (SX1281) | 2400 | 0.4237 | InStock |
| C274876 | 680R 0201 | 2420 | 0.000900 | InStock |
| C106225 | 10k 0201 | 24032 | 0.000600 | InStock |
| C274342 | 220R 0201 | 3620 | 0.000700 | InStock |
| C2976675 | tact button TS2306A | 2402 | 0.0581 | InStock |
| C19213 | RFX2401C | 3602 | 0.4877 | InStock |
| C255353 | SKY13414-485LF | 3601 | 0.5229 | InStock |
| C22381772 | 32MHz TCXO (LR1121) | 2400 | 0.4541 | InStock |
| C7498014 | LR1121IMLTRT | 3601 | 2.8779 | InStock |
| C89334 | 2450AT18A100E ceramic ant | 1351 (3449 short) | ~0.35 | **Partial** |
| C2858491 | ESP32-C3FH4 | 988 (3812 short) | ~1.61 | **Partial** |
| C2151551 | SX1281IMLTRT | 193 (2207 short) | ~2.50 | **Partial** |
| C2861882 | TLV75533PDQNR LDO | 2244 (2561 short) | ~0.11 | **Partial** |
| C2875272 | CJ17 40MHz crystal | 462 (4338 short) | ~0.25 | **Partial** |
| C2651081 | 2450FM07D0034T (Johanson 2.4G filter) | 0 | ~0.40 | **Consigned (Johanson)** |
| C19842466 | 0900PC16J0042001E (Johanson IPD) | 0 | ~0.49 | **Consigned (DigiKey)** |

Partial-stock parts: short qty must be sourced separately (LCSC bulk, DigiKey, or Johanson direct). Unit prices above blend JLC stocked rate + secondary source.

## Per-SKU BOM cost (1000 units)

### OpenRX-Lite (ceramic)
| Block | Cost ($) |
|---|---|
| AE1 ceramic 2450AT18A100E | 0.35 |
| AE2 Molex UFL 47948-0001 | 0.71 |
| U1 ESP32-C3FH4 | 1.61 |
| U2 LDO TLV75533 | 0.11 |
| U3 SX1281IMLTRT | 2.50 |
| OSC1 52MHz XO | 0.42 |
| X1 40MHz crystal + 2× 18pF | 0.25 |
| FL1 2450FM07D0034T (Johanson, consigned) | 0.40 |
| L1 24nH | 0.01 |
| D1 WS2812B LED | 0.04 |
| 10× 100nF + 4× 1uF + 2× 10uF + 1× 470nF + 1× 1nF | 0.04 |
| 4× 10k pullups | <0.01 |
| **Lite (ceramic) BOM total** | **≈ $6.44 / unit** |

### OpenRX-Lite-UFL
Same as Lite (ceramic) **minus AE2 Molex UFL ($0.71)** **plus JP1 Hirose U.FL ($0.07)**:
- **Lite-UFL BOM total ≈ $5.80 / unit**

### OpenRX-Mono
| Block | Cost ($) |
|---|---|
| AE1 ceramic ant (WiFi) | 0.35 |
| JP1 Hirose U.FL | 0.07 |
| U1 ESP32-C3FH4 | 1.61 |
| U2 LDO TLV75533 | 0.11 |
| U3 tact button | 0.06 |
| U4 LR1121IMLTRT | 2.88 |
| U5 32MHz TCXO ±1.5ppm | 0.45 |
| U7 RFX2401C 2.4G FE | 0.49 |
| U8 SKY13414-485LF SP4T | 0.52 |
| T1 Johanson IPD 0900PC16J (consigned) | 0.49 |
| FL1 2450FM07D0034T (consigned) | 0.40 |
| X1 40MHz crystal + 2× 18pF | 0.25 |
| L1 10uH (DC-DC choke) | 0.01 |
| L2 24nH (XTAL_P harmonic) | 0.01 |
| D1 WS2812B LED | 0.04 |
| Caps: 10× 100nF + 4× 1uF + 2× 10uF + 1× 4.7uF + 1× 10pF + 1× 220pF + 1× 0.3pF | 0.04 |
| Resistors: 5× 10k + 1× 220R | <0.01 |
| **Mono BOM total** | **≈ $7.78 / unit** |

### OpenRX-Gemini
| Block | Cost ($) |
|---|---|
| AE1 ceramic ant (WiFi) | 0.35 |
| 2× JP4/JP5 Hirose U.FL | 0.14 |
| U3 ESP32-C3FH4 | 1.61 |
| U6 LDO TLV75533 (consider 1A LDO instead) | 0.11 |
| U4 tact button | 0.06 |
| 2× LR1121IMLTRT (U2 + U9) | 5.76 |
| U1 32MHz TCXO ±1.5ppm (shared) | 0.45 |
| 2× RFX2401C (U15 + U17) | 0.98 |
| 2× SKY13414-485LF (U16 + U18) | 1.05 |
| 2× Johanson IPD T4/T5 (consigned) | 0.98 |
| 2× 2450FM07D0034T FL4/FL5 (consigned) | 0.80 |
| X1 40MHz crystal + 2× 18pF | 0.25 |
| L1 24nH + 2× L2/L3 10uH | 0.03 |
| D1 WS2812B LED | 0.04 |
| Caps: 14× 100nF + 6× 1uF + 2× 10uF + 2× 4.7uF + 2× 10pF + 2× 220pF + 2× 0.3pF + 2× 18pF | 0.07 |
| Resistors: 7× 10k + 2× 220R + 2× 680R | <0.01 |
| **Gemini BOM total** | **≈ $12.68 / unit** |

## Summary (1000-unit pricing)

| SKU | $/unit (BOM only) | €/unit (≈0.92 EUR/USD) |
|---|---|---|
| Lite (ceramic) | **$6.44** | €5.92 |
| Lite-UFL | **$5.80** | €5.34 |
| Mono | **$7.78** | €7.16 |
| Gemini | **$12.68** | €11.66 |

**Excludes:** PCB fab cost (panel split 4-ways), SMT assembly fee per board (typically $0.001/joint × ~80–250 joints/SKU), stencil, consignment handling fee from JLC, shipping/duties, Johanson part procurement.

**Compared to memory snapshot (Apr 4, qty 200 quote):** Lite €6.09, Mono €7.96, Gemini €13.65 — current 1000-unit pricing trends ~5–15% lower per unit as expected with volume.

## Sourcing risks before order

1. **ESP32-C3FH4** short by 3812 units — confirm LCSC bulk + DigiKey/Mouser combined can cover. Alt: ESP8685H4 (smaller pkg, FW-compatible per ELRS guide v1.12) if availability worsens.
2. **SX1281IMLTRT** short by 2207 — DigiKey/Mouser inventory needs check.
3. **40MHz crystal CJ17-400001010B20** short by 4338 units, JLC has only 462 — substantial sourcing problem. Alternates: any 40MHz ±10ppm 10pF SMD1612-4P crystal would work for ESP32-C3 (this is the ESP MCU clock, not the SX1281).
4. **2450AT18A100E ceramic ant** short by 3449 — Johanson; can be consigned with the rest of Johanson kit.
5. **TLV75533** short by 2561 — LCSC alt or AP2127K-3.3 substitute.

## Open question on the panel
- Confirm JLC accepts mixed-design panel without step-and-repeat (yes — order form has the option, but consigned-parts handling fee applies once for the whole panel).
- Submit Johanson kit (2× T1/T4/T5, 1× FL1/FL4/FL5, optionally 1× 2450AT18A100E) consigned together.
