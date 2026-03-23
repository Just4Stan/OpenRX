# OpenRX — Open Source ExpressLRS Receiver Family

Part of the [OpenDrone](https://github.com/Just4Stan) ecosystem. This repository currently contains six ELRS 4.0 receiver product briefs, imported local KiCad libraries, and starter KiCad projects for schematic capture.

**Repository state:** the `.kicad_sch` and `.kicad_pcb` files are still starter shells. The actual design intent currently lives in `SCHEMATIC.md`, `BOM.md`, and the local imported part libraries.

**License:** CERN-OHL-S v2 (hardware), MIT (firmware/tools)

## The Lineup

| Model | Band | MCU | RF | Current 2.4GHz Front-End | Form Factor | Target BOM | Retail | Use Case |
|-------|------|-----|-----|---------------------------|------------|------------|--------|----------|
| **OpenRX-Lite** | 2.4 GHz | ESP32-C3 | SX1281 | None | 16x12mm, ceramic ant | €3-4 | €8-10 | Whoops, micro quads, racing |
| **OpenRX-Nano** | 2.4 GHz | ESP32-C3 | SX1281 | RFX2401C | 20x13mm, UFL | €5-6 | €12-15 | Standard 5" quads, all-rounder |
| **OpenRX-900** | 868/915 MHz | ESP32-C3 | LR1121 | None | 18x13mm, UFL | €4-5 | €10-13 | Long range, penetration |
| **OpenRX-Dual** | Dual-band switchable | ESP32-C3 | LR1121 | SE2431L in current docs | 22x15mm, 2x UFL | €7-9 | €15-18 | One receiver for 2.4GHz or sub-GHz |
| **OpenRX-PWM** | 2.4 GHz | ESP32-C3 | SX1281 | SE2431L in current docs | 30x20mm, UFL | €6-8 | €15-18 | Fixed wing, heli, cars, boats |
| **OpenRX-Gemini** | Xrossband simultaneous | ESP32-C3 | 2x LR1121 | SE2431L on 2.4GHz path | 24x18mm, 2x UFL | €12-15 | €25-30 | Flagship, simultaneous dual-band |

`RFX2401C` is already adopted in the Nano design docs. Rolling it into Dual/PWM/Gemini is still a follow-up task, not a finished repo-wide change.

## Which One Should I Buy?

```
Do you fly tiny whoops / micro quads?
  → OpenRX-Lite (smallest, lightest, cheapest)

Do you fly 3-5" FPV quads?
  → OpenRX-Nano (best balance of range, size, price)
  → OpenRX-Dual (if you want dual-band flexibility)

Do you need maximum range?
  → OpenRX-900 (sub-GHz penetration, cheap)
  → OpenRX-Dual (switchable bands, one receiver for everything)

Do you fly fixed wing, helicopters, or RC cars/boats?
  → OpenRX-PWM (6 direct servo/ESC outputs, no flight controller needed)

Do you want the absolute best link reliability?
  → OpenRX-Gemini (simultaneous 2.4GHz + 900MHz, dual redundancy)
```

## Architecture

All receivers share common design principles:

- **ELRS 4.0 unified firmware** — no custom targets, works with stock ELRS builds
- **ESP32-C3** MCU across the current lineup, including Gemini
- **LDO mode** on SX1281 (simpler, adequate for RX power levels)
- **TCXO** on all designs (prevents frequency drift disconnections)
- **2-layer PCB** for Lite/Nano/900, **4-layer** for Dual/PWM/Gemini
- **JLCPCB assembly** with LCSC basic parts preferred
- **Project-local KiCad libraries** with per-project `sym-lib-table` and `fp-lib-table`

### RF Chip Families

| Chip | Bands | Max Rate | Used In |
|------|-------|----------|---------|
| SX1281 | 2.4 GHz | 1000Hz FLRC | Lite, Nano, PWM |
| LR1121 | 868/915 MHz + 2.4 GHz | 1000Hz FSK | 900, Dual, Gemini |

### CE/FCC Certification Strategy

Two RF core designs enable family certification:
- **SX1281 family** (Lite, Nano, PWM): test worst-case variant (PWM), delta-test others
- **LR1121 family** (900, Dual, Gemini): test worst-case variant (Gemini), delta-test others

Budget: ~€20-30K for full family vs €60-90K for individual certification.

Standards: EN 300 328 (2.4GHz), EN 300 220 (sub-GHz), EN 301 489 (EMC), EN 62368-1 (safety).

## Repository Structure

```
OpenRX/
├── README.md                    ← You are here
├── CORE_BOM.md                  ← Shared procurement guidance + audit notes
├── REPO_AUDIT_2026-03-23.md     ← What is real vs still placeholder
├── OpenRX-Lite/
│   ├── OpenRX-Lite.kicad_pro    ← Starter project shell
│   ├── OpenRX-Lite.kicad_sch    ← Empty schematic shell
│   ├── OpenRX-Lite.kicad_pcb    ← Empty board shell
│   ├── SCHEMATIC.md             ← Design brief / pin mapping
│   ├── BOM.md                   ← Procurement draft
│   ├── datasheets/
│   ├── sym-lib-table            ← Local symbol library table
│   └── fp-lib-table             ← Local footprint library table
├── OpenRX-Nano/                 ← Standard 2.4GHz with PA+LNA
├── OpenRX-900/                  ← Budget sub-GHz long range
├── OpenRX-Dual/                 ← Dual-band switchable
├── OpenRX-PWM/                  ← PWM receiver concept
└── OpenRX-Gemini/               ← Flagship Xrossband
```

## Competing With RadioMaster

| Segment | RadioMaster | OpenRX | Our Advantage |
|---------|------------|--------|---------------|
| Budget 2.4GHz | XR2 (€10) | Lite (€8-10) | Open source, same price |
| Mid 2.4GHz | XR1 (€14) | Nano (€12-15) | Open source, PA+LNA |
| Sub-GHz | — | 900 (€10-13) | No cheap RadioMaster 900MHz option |
| Dual-band | XR3 (€30) | Dual (€15-18) | 40-50% cheaper |
| PWM | ER5C (€20) | PWM (€15-18) | Open source, better value |
| Gemini | XR4 (€40) | Gemini (€25-30) | 25-35% cheaper, open source |

## Integration With OpenDrone Ecosystem

- **OpenFC** flight controller has a breakaway ELRS module using the same ESP32-C3 + SX1281 platform
- **OpenRX-Nano** is a direct replacement/upgrade for the OpenFC breakaway module
- All receivers use CRSF protocol for seamless FC integration
- Shared KiCad libraries and component choices across the ecosystem

## Status

- [x] Project shells created for all 6 receivers
- [x] Local imported symbol / footprint / 3D libraries added
- [x] Per-project KiCad library tables added for clone-safe opening
- [ ] Schematic capture in KiCad
- [ ] Layout / RF placement
- [ ] Bring-up / firmware validation
