# OpenRX Core BOM — Shared Components Across All 6 Receivers

All receivers share a common component pool to minimize unique LCSC part numbers, simplify procurement, reduce JLCPCB extended part setup fees, and enable bulk pricing.

## Audit Corrections

- Treat this file as the target procurement baseline, not a statement that every per-project `BOM.md` already matches it.
- `RFX2401C` is already used in `OpenRX-Nano`. `OpenRX-Dual`, `OpenRX-PWM`, and `OpenRX-Gemini` still document `SE2431L` and need pin-control / RF rework before a full unification.
- `LR1121IMLTRT` is a `QFN-32 4x4mm` device. Any `5x5mm` references elsewhere in the repo are stale and should not be used for footprint selection.
- `OpenRX-Gemini` currently targets `ESP32-C3FH4`, not `ESP32-S3`.
- Datasheet coverage is partly local already and is being normalized separately from the BOM lock.

## Design Rules
1. **One LCSC part number per function** — no duplicate selections across receivers
2. **JLCPCB basic parts for all passives** — zero setup fees on caps/resistors
3. **0402 passives everywhere** (except bulk caps where 0603/0805 needed for capacitance)
4. **Prefer one part per function once validated** — do not force BOM unification ahead of firmware or RF validation

## Component Standardization Issues Found

The 6 design agents made inconsistent choices. Standardized selections below:

| Component | Agent Choices | Current Direction | Reason |
|-----------|--------------|-------------------|--------|
| Front-end IC | SE2431L-R (C2649471) vs RFX2401C (C19213) | **RFX2401C preferred for new work** | $0.90 vs $1.89, 57k stock, QFN-16 3x3mm (smaller). Nano already uses it; Dual/PWM/Gemini still need rework. |
| 100nF 0402 | C1525 vs C307331 | **C1525** | JLCPCB basic, highest stock |
| 40MHz crystal | C2875272 vs C426988 vs C90924 vs C14346 | **C90924** | 3225 package, 10pF load, wide availability |
| UFL connector | C22418213 vs C88374 vs C88373 | **C88374** | Hirose U.FL-R-SMT-1(80), well-stocked |
| LDO | ME6211 (C82942) vs AMS1117 (C6186) vs AP2112K (C51118) | **ME6211 (C82942)** default, **AMS1117 (C6186)** for PWM only (needs >6V input) |
| LED | WS2812B-2020 (C965555) | **C965555** | All receivers |
| 22uF cap | C45783 vs C59461 vs C159842 vs C159770 | **C59461** | 0603, 10V X5R, JLCPCB basic |

---

## Shared Core Components

These components are shared across most of the family or form the intended default baseline:

| Function | MPN | LCSC | Package | Price | Used In |
|----------|-----|------|---------|-------|---------|
| MCU | ESP32-C3FH4 | **C2858491** | QFN-32 5x5mm | ~$1.50 | ALL |
| LDO (default) | ME6211C33M5G-N | **C82942** | SOT-23-5 | ~$0.04 | Lite, Nano, 900, Dual |
| 40MHz crystal | 7M40000005 | **C90924** | SMD3225 | ~$0.08 | ALL |
| Status LED | WS2812B-2020 | **C965555** | 2020 | ~$0.04 | Project-dependent |

### Universal Passives

| Value | Package | LCSC | JLCPCB | Used For | Min Qty/Board |
|-------|---------|------|--------|----------|---------------|
| 100nF X7R 16V | 0402 | **C1525** | Basic | Decoupling everywhere | 6-15 |
| 10uF X5R 10V | 0402 | **C15525** | Basic | LDO input bulk | 1 |
| 22uF X5R 10V | 0603 | **C59461** | Basic | LDO output bulk | 1 |
| 1uF X5R 16V | 0402 | **C52923** | Basic | EN RC delay, various | 1-4 |
| 10pF C0G 50V | 0402 | **C32949** | Basic | Crystal load caps | 2 |
| 10k 1% | 0402 | **C25744** | Basic | Pull-ups (EN, NSS, NRESET, BOOT) | 3-5 |
| 100R 1% | 0402 | **C25076** | Basic | LED series, PWM protection | 1-6 |

---

## SX1281 Family (Lite, Nano, PWM)

Additional shared components for 2.4GHz SX1281-based receivers:

| Function | MPN | LCSC | Package | Price | Used In |
|----------|-----|------|---------|-------|---------|
| RF transceiver | SX1281IMLTRT | **C2151551** | QFN-24 4x4mm | ~$2.26 | Lite, Nano, PWM |
| 52MHz TCXO | OW7EL89CENUNFAYLC-52M | **C22434896** | SMD2016 | ~$0.42 | Lite, Nano, PWM |

### SX1281-Specific Passives

| Value | Package | LCSC | Used For |
|-------|---------|------|----------|
| 470nF X7R 10V | 0402 | **C1543** | SX1281 VR_PA (LDO mode) |

---

## LR1121 Family (900, Dual, Gemini)

Additional shared components for LR1121-based receivers:

| Function | MPN | LCSC | Package | Price | Used In |
|----------|-----|------|---------|-------|---------|
| RF transceiver | LR1121IMLTRT | **C7498014** | QFN-32 4x4mm | ~$2.50 | 900, Dual, Gemini (x2) |
| 32MHz TCXO | OW2EL89CENUXFMYLC-32M | **C22434888** | SMD3225 | ~$0.46 | 900, Dual, Gemini (x2) |

### LR1121-Specific Passives

| Value | Package | LCSC | Used For |
|-------|---------|------|----------|
| 4.7uF X5R 10V | 0402 | **C23733** | LR1121 VR_PA |
| 10uH 300mA | 0603 | **C1035** | LR1121 DC-DC inductor |
| 100k 1% | 0402 | **C25741** | RFSW pull-downs |

---

## PA+LNA Family (Nano, Dual, PWM, Gemini)

Additional shared components for receivers with RF front-end:

| Function | MPN | LCSC | Package | Price | Used In |
|----------|-----|------|---------|-------|---------|
| 2.4GHz PA+LNA+Switch | RFX2401C | **C19213** | QFN-16 3x3mm | ~$0.90 | Nano today, target standard for Dual/PWM/Gemini |
| 2.4GHz SAW filter | NDFH024-2442SA | **C312144** | 1.1x0.9mm | ~$0.10 | Nano, Dual, PWM, Gemini |
| UFL connector | U.FL-R-SMT-1(80) | **C88374** | SMD | ~$0.08 | Nano, 900, Dual(x2), PWM, Gemini(x2) |

---

## Antenna Components

| Function | MPN | LCSC | Package | Price | Used In |
|----------|-----|------|---------|-------|---------|
| 2.4GHz ceramic antenna | 2450AT18A100E | **C89334** | 3.2x1.6mm | ~$0.25 | Lite only |
| UFL connector | U.FL-R-SMT-1(80) | **C88374** | SMD | ~$0.08 | All except Lite |
| Sub-GHz balun 868/915MHz | 0900BM15A0001 | **TBD** | 0805 | ~$0.50 | 900, Dual, Gemini |

**Sub-GHz balun sourcing problem:** Johanson 0900BM15A0001 is NOT on LCSC. Options:
1. Consign from DigiKey/Mouser to JLCPCB
2. Discrete LC balun (3 inductors + 2 caps, needs VNA tuning)
3. Find LCSC-stocked alternative — search needed

---

## Receiver-Specific Components

| Component | Used In | LCSC | Notes |
|-----------|---------|------|-------|
| AMS1117-3.3 (SOT-223 LDO) | PWM only | C6186 | Higher VIN range for BEC/battery input (up to 15V) |
| AP2112K-3.3TRG1 (SOT-23-5 LDO) | Gemini only | C51118 | 600mA for dual radios (ME6211 is 500mA) |
| Pin headers 1x3 2.54mm | PWM only | C2337 | Servo connectors, through-hole |

---

## Complete LCSC Master Part List

**Total unique LCSC part numbers across all 6 receivers: 23 active + ~12 passive = ~35 total**

### Active Components (order in bulk)

| # | LCSC | MPN | Function | Total Qty (6 designs) |
|---|------|-----|----------|----------------------|
| 1 | C2858491 | ESP32-C3FH4 | MCU | 6 (one per RX) |
| 2 | C2151551 | SX1281IMLTRT | 2.4GHz RF | 3 (Lite, Nano, PWM) |
| 3 | C7498014 | LR1121IMLTRT | Dual-band RF | 4 (900x1, Dualx1, Geminix2) |
| 4 | C19213 | RFX2401C | PA+LNA 2.4GHz | 4 (Nano, Dual, PWM, Gemini) |
| 5 | C82942 | ME6211C33M5G-N | 3.3V LDO | 5 (all except PWM) |
| 6 | C6186 | AMS1117-3.3 | 3.3V LDO high-VIN | 1 (PWM) |
| 7 | C51118 | AP2112K-3.3TRG1 | 3.3V LDO 600mA | 1 (Gemini) |
| 8 | C22434896 | 52MHz TCXO (YXC) | SX1281 clock | 3 (Lite, Nano, PWM) |
| 9 | C22434888 | 32MHz TCXO (YXC) | LR1121 clock | 4 (900x1, Dualx1, Geminix2) |
| 10 | C90924 | 40MHz crystal | ESP32-C3 clock | 6 (all) |
| 11 | C965555 | WS2812B-2020 | Status LED | 6 (all) |
| 12 | C312144 | NDFH024-2442SA | 2.4GHz SAW | 4 (Nano, Dual, PWM, Gemini) |
| 13 | C89334 | 2450AT18A100E | Ceramic antenna | 1 (Lite) |
| 14 | C88374 | U.FL-R-SMT-1(80) | UFL connector | 9 (Nano, 900, Dualx2, PWM, Geminix2+) |

### Passive Components (all JLCPCB basic — zero setup fee)

| # | LCSC | Value | Package | Used Across |
|---|------|-------|---------|-------------|
| 15 | C1525 | 100nF X7R 16V | 0402 | ALL |
| 16 | C15525 | 10uF X5R 10V | 0402 | ALL |
| 17 | C59461 | 22uF X5R 10V | 0603 | ALL |
| 18 | C52923 | 1uF X5R 16V | 0402 | ALL |
| 19 | C32949 | 10pF C0G 50V | 0402 | ALL |
| 20 | C23733 | 4.7uF X5R 10V | 0402 | LR1121 family |
| 21 | C1543 | 470nF X7R 10V | 0402 | SX1281 family |
| 22 | C25744 | 10k 1% | 0402 | ALL |
| 23 | C25076 | 100R 1% | 0402 | ALL |
| 24 | C25741 | 100k 1% | 0402 | LR1121 family |
| 25 | C1035 | 10uH 300mA | 0603 | LR1121 family |
| 26 | C1553 | 100pF C0G 50V | 0402 | RF DC block |

---

## Cost Summary Per Receiver (Standardized BOM, qty 100)

| Receiver | MCU | RF | FE | LDO | TCXO | Xtal | Filter | Conn | LED | Passives | **Total** |
|----------|-----|-----|-----|------|------|------|--------|------|-----|----------|-----------|
| **Lite** | $1.50 | $2.26 | — | $0.04 | $0.42 | $0.08 | — | $0.25¹ | $0.04 | ~$0.15 | **~$4.74** |
| **Nano** | $1.50 | $2.26 | $0.90 | $0.04 | $0.42 | $0.08 | $0.10 | $0.08 | $0.04 | ~$0.15 | **~$5.57** |
| **900** | $1.50 | $2.50 | — | $0.04 | $0.46 | $0.08 | — | $0.08 | $0.04 | ~$0.20 | **~$4.90** |
| **Dual** | $1.50 | $2.50 | $0.90 | $0.04 | $0.46 | $0.08 | $0.10 | $0.16² | $0.04 | ~$0.25 | **~$6.03** |
| **PWM** | $1.50 | $2.26 | $0.90 | $0.12 | $0.42 | $0.08 | $0.10 | $0.08 | $0.04 | ~$0.40 | **~$5.90** |
| **Gemini** | $1.50 | $5.00³ | $0.90 | $0.07 | $0.92⁴ | $0.08 | $0.10 | $0.16² | $0.04 | ~$0.35 | **~$9.12** |

¹ Ceramic antenna, no UFL
² 2x UFL connectors
³ 2x LR1121
⁴ 2x 32MHz TCXO

**Add ~$1.50-2.50 for PCB + JLCPCB assembly per board.**

---

## Bulk Ordering Strategy

For a production run of 100 units of each receiver (600 boards total):

| Component | Total Qty Needed | Bulk Price Break |
|-----------|-----------------|-----------------|
| ESP32-C3FH4 | 600 | ~$1.20/ea at 500+ |
| SX1281IMLTRT | 300 | ~$1.80/ea at 300+ |
| LR1121IMLTRT | 400 | ~$2.00/ea at 300+ |
| RFX2401C | 400 | ~$0.70/ea at 300+ |
| 52MHz TCXO | 300 | ~$0.35/ea at 300+ |
| 32MHz TCXO | 400 | ~$0.38/ea at 300+ |

At 500+ qty pricing, total BOM drops approximately 15-20%.

---

## Supply Risk Assessment

| Component | Risk | Stock (LCSC) | Mitigation |
|-----------|------|-------------|------------|
| ESP32-C3FH4 | LOW | >50k units | Well-stocked |
| SX1281IMLTRT | MEDIUM | ~5-10k | Monitor, order early |
| LR1121IMLTRT | **HIGH** | ~1-3k, variable | Order early, consider Mouser/DigiKey consignment |
| RFX2401C | LOW | 57k units | Well-stocked |
| ME6211C33M5G-N | LOW | >100k | JLCPCB basic part |
| Sub-GHz balun | **HIGH** | Not on LCSC | Must source externally or design discrete |
| 32MHz TCXO | MEDIUM | ~3k | Alternative TCXOs exist |
