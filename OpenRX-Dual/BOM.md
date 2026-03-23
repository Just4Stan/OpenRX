# OpenRX-Dual — Bill of Materials

> Audit note: this BOM still assumes `SE2431L`. Decide `SE2431L` vs `RFX2401C` before schematic capture; `CORE_BOM.md` now treats `RFX2401C` as the cost-optimized target, but that change is not yet propagated or validated here.

Target BOM cost: EUR 7-9 at production quantities (100+ units).
All parts sourced from LCSC for JLCPCB assembly compatibility.

## Active Components

| Ref | Part | MPN | LCSC | Package | Qty | Unit Price (USD) | Notes |
|-----|------|-----|------|---------|-----|-----------------|-------|
| U1 | MCU | ESP32-C3FH4 | C2858491 | QFN-32 (5x5mm) | 1 | ~$1.50 | RISC-V, 4MB flash internal |
| U2 | RF Transceiver | LR1121IMLTRT | C7498014 | QFN-32 (4x4mm) | 1 | ~$3.20 | Sub-GHz + 2.4GHz LoRa |
| U3 | 2.4GHz FEM | SE2431L-R | C2649471 | QFN-24-EP (3x4mm) | 1 | ~$1.89 | LNA+PA, Skyworks |
| U4 | LDO 3.3V | ME6211C33M5G-N | C82942 | SOT-23-5 | 1 | ~$0.04 | 500mA, 3.3V output |
| D1 | LED | WS2812B-2020 | C965555 | 2020 (2x2mm) | 1 | ~$0.04 | Addressable RGB |

## RF / Frequency Components

| Ref | Part | MPN | LCSC | Package | Qty | Unit Price (USD) | Notes |
|-----|------|-----|------|---------|-----|-----------------|-------|
| Y1 | 40MHz Crystal | — | C14346 | 3.2x2.5mm | 1 | ~$0.08 | 10pF load, for ESP32-C3 |
| Y2 | 32MHz TCXO | OW2EL89CENUXFMYLC-32M (YXC) | C22434888 | 3.2x2.5mm | 1 | ~$0.90 | Peak-shaving sine, 3.3V, +/-2.5ppm. Set VTCXO=3.3V in firmware |
| FL1 | 2.4GHz SAW Filter | NDFH024-2442SA | C312144 | SMD | 1 | ~$0.15 | 2403-2480MHz bandpass |
| T1 | Sub-GHz Balun | 0900BM15A0001 | — | 0805 | 1 | ~$0.50 | 868/915MHz balun. Source from DigiKey/Mouser if not on LCSC |

**Balun Alternatives (LCSC):**
- Search LCSC for 868/915MHz balun in 0805 or 0603 package
- Johanson 0900BM15A0001 may need DigiKey sourcing (~$0.45 @ 100+)
- Alternative: discrete LC balun (3x inductors + 2x caps) saves cost but needs tuning

## Connectors

| Ref | Part | MPN | LCSC | Package | Qty | Unit Price (USD) | Notes |
|-----|------|-----|------|---------|-----|-----------------|-------|
| J1 | UFL Connector (sub-GHz) | U.FL-R-SMT-1(10) | C88373 | SMD | 1 | ~$0.20 | Hirose, 50-ohm, IPEX-1 |
| J2 | UFL Connector (2.4GHz) | U.FL-R-SMT-1(10) | C88373 | SMD | 1 | ~$0.20 | Hirose, 50-ohm, IPEX-1 |

## Passive Components — Capacitors

All ceramic, X7R or X5R dielectric unless noted. 0402 (1005 metric) default.

| Ref | Value | Voltage | Package | Qty | LCSC | Notes |
|-----|-------|---------|---------|-----|------|-------|
| C1 | 10uF | 10V X5R | 0402 | 1 | C15525 | LDO VIN bypass |
| C2 | 100nF | 16V X7R | 0402 | 12 | C1525 | General decoupling (LDO VIN, VOUT, ESP32 VDD x3, LR1121 VDD_PERI, VDD_IN, VDD, VTCXO, SE2431L VDD_PA, VDD_LNA, WS2812B) |
| C3 | 22uF | 10V X5R | 0603 | 1 | C59461 | LDO VOUT bulk |
| C4 | 1uF | 16V X7R | 0402 | 3 | C52923 | LDO BP, EN RC delay, SE2431L VDD_PA bulk |
| C5 | 4.7uF | 10V X7R | 0402 | 1 | C368816 | LR1121 VR_PA bypass |
| C6 | 10pF | 50V C0G/NP0 | 0402 | 2 | C32949 | Crystal load caps (ESP32-C3) |
| C7 | 0.5pF | 50V C0G/NP0 | 0402 | 2 | — | Sub-GHz matching (may not be needed with integrated balun) |
| C8 | 1pF | 50V C0G/NP0 | 0402 | 1 | — | 2.4GHz matching (pi-network, if needed) |
| C9 | 100pF | 50V C0G/NP0 | 0402 | 1 | C1546 | DC blocking cap (RFIO_HF to SE2431L, optional) |

**Total capacitor count:** ~24 (some values share BOM lines)

## Passive Components — Resistors

All 0402, 1% tolerance.

| Ref | Value | Package | Qty | LCSC | Notes |
|-----|-------|---------|-----|------|-------|
| R1 | 10k | 0402 | 4 | C25744 | Pull-ups: ESP32 EN, LR1121 NRESET, LR1121 NSS, GPIO9 boot |
| R2 | 330R | 0402 | 1 | C25100 | Series resistor for WS2812B DIN |

## Passive Components — Inductors (RF Matching)

| Ref | Value | Package | Qty | LCSC | Notes |
|-----|-------|---------|-----|------|-------|
| L1 | 1.2nH | 0402 | 1 | — | 2.4GHz pi-match (if needed) |

**Note:** RF matching inductors may not be needed if using integrated balun and direct 50-ohm connections. Populate during RF tuning on prototype. Reserve pads in layout.

## Mechanical

| Ref | Part | Qty | Notes |
|-----|------|-----|-------|
| SW1 | Tactile Button | 1 | Boot button, 3x4mm SMD or smaller |
| — | PCB | 1 | 22x15mm, 4-layer, 1.0mm, ENIG finish |
| — | Sub-GHz antenna pigtail | 1 | UFL to SMA or dipole (not on BOM, user-supplied) |
| — | 2.4GHz antenna pigtail | 1 | UFL to SMA or T-antenna (not on BOM, user-supplied) |

---

## BOM Cost Estimate (per unit, 100+ qty)

| Category | Estimated Cost (USD) |
|----------|---------------------|
| ESP32-C3FH4 | $1.50 |
| LR1121IMLTRT | $3.20 |
| SE2431L-R | $1.89 |
| ME6211C33M5G-N (LDO) | $0.04 |
| 32MHz TCXO | $0.90 |
| 40MHz Crystal | $0.08 |
| SAW Filter | $0.15 |
| Sub-GHz Balun | $0.50 |
| UFL Connectors (x2) | $0.40 |
| WS2812B LED | $0.04 |
| Passives (caps, resistors) | $0.30 |
| Boot Button | $0.05 |
| **Component Total** | **~$9.05** |
| PCB (JLCPCB, qty 100) | ~$0.50/board |
| JLCPCB Assembly | ~$2-3/board |
| **Total Landed Cost** | **~$11-12.50** |

### Cost Notes

- LR1121 is the most expensive component at ~$3.20. Volume pricing (1000+) may bring this to ~$2.50.
- SE2431L at ~$1.89 is the second biggest cost driver. Could be replaced with a cheaper Chinese FEM if one exists for 2.4GHz with similar specs.
- Target EUR 7-9 BOM is achievable at 1000+ quantity with aggressive LCSC pricing.
- Competition: RadioMaster XR3 retails at $29.99. At ~$12 landed cost, we achieve ~60% cost reduction.

---

## LCSC Part Availability Notes

| Component | LCSC Status | Alternative |
|-----------|-------------|-------------|
| ESP32-C3FH4 (C2858491) | In stock | ESP32-C3 (C2838500) — needs external flash |
| LR1121IMLTRT (C7498014) | Verify stock | Source from Mouser/DigiKey if needed |
| SE2431L-R (C2649471) | In stock (~1272 pcs) | No direct LCSC alternative |
| ME6211C33M5G-N (C82942) | In stock (basic part) | AP2112K-3.3 or similar |
| WS2812B-2020 (C965555) | In stock | SK6805-EC20 (better 3.3V compat) |
| 32MHz TCXO (C22434888) | Verify stock | Any 32MHz TCXO, match VTCXO voltage |
| SAW Filter (C312144) | Verify stock | Other 2.4GHz SAW from LCSC catalog |
| UFL Connector (C88373) | In stock | C434812 or generic IPEX-1 |
| Sub-GHz Balun | NOT on LCSC | Johanson 0900BM15A0001 from DigiKey; or discrete LC |

---

## JLCPCB Assembly Classification

| Part | JLCPCB Type | Setup Fee |
|------|-------------|-----------|
| ME6211C33M5G-N | Basic | None |
| 0402 Resistors | Basic | None |
| 0402 Capacitors | Basic | None |
| ESP32-C3FH4 | Extended | $3/part type |
| LR1121IMLTRT | Extended | $3/part type |
| SE2431L-R | Extended | $3/part type |
| WS2812B-2020 | Extended | $3/part type |
| 32MHz TCXO | Extended | $3/part type |
| SAW Filter | Extended | $3/part type |
| UFL Connectors | Extended | $3/part type |

Extended parts: 7 types x $3 = $21 setup fee (one-time per order, amortized across quantity).
At 100 boards: $0.21/board setup overhead.

---

## easyeda2kicad Import List

Components to import into project-local library:

```
C2858491  # ESP32-C3FH4
C7498014  # LR1121IMLTRT
C2649471  # SE2431L-R
C82942    # ME6211C33M5G-N
C965555   # WS2812B-2020
C22434888 # 32MHz TCXO (YXC OW2EL89CENUXFMYLC-32M)
C312144   # SAW Filter NDFH024-2442SA
C88373    # U.FL-R-SMT-1(10)
```
