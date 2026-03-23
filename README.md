# OpenRX — Open Source ExpressLRS Receiver Family

Part of the [OpenDrone](https://github.com/Just4Stan) ecosystem. Current release plan is a three-SKU ELRS 4.0 receiver stack: `Lite`, `Mono`, and `Gemini`.

**License:** CERN-OHL-S v2 (hardware), MIT (firmware/tools)

**Status:** Repo structure and KiCad project naming now match the reduced release stack. Active top-level projects are `OpenRX-Lite`, `OpenRX-Mono`, and `OpenRX-Gemini`. Older concepts were moved under `archive/legacy-projects/`.

**Current portfolio recommendation:** see [PRODUCT_LINEUP_REDUCTION_2026-03-23.md](PRODUCT_LINEUP_REDUCTION_2026-03-23.md). The commercial ELRS market is converging on a smaller ladder than the current six-project concept.

**Mono/Gemini topology research:** see [MONO_GEMINI_TOPOLOGY_RESEARCH_2026-03-23.md](MONO_GEMINI_TOPOLOGY_RESEARCH_2026-03-23.md) for the current competitor and ExpressLRS target deep-dive.

## Release Stack

| Model | Band | MCU | RF | Front-End | Size | BOM | Retail | Use Case |
|-------|------|-----|-----|-----------|------|-----|--------|----------|
| **Lite** | 2.4 GHz | ESP32-C3 | SX1281 | — | 16x12mm target | compact / low-cost target | entry | Ceramic-antenna micro / whoop RX |
| **Mono** | Multi-band | ESP32-C3 | LR1121 | optional matched output path | TBD | mainstream target | mainstream | Single-radio all-rounder, one U.FL |
| **Gemini** | Xrossband | ESP32-C3 | 2x LR1121 | premium RF path | TBD | premium target | premium | Flagship simultaneous 2.4 + 868/915 |

`Lite` remains the only current small 2.4-only product, and its intended release form is ceramic-antenna-only. `Mono` absorbs the old `900` and `Dual` market position. `Gemini` remains the premium later-phase product.

## Which One Do I Need?

- **Tiny whoops / micro quads** → Lite
- **Most FPV builds / one-board-for-most-users** → Mono
- **Best possible link / flagship** → Gemini

## Architecture

Two active RF platforms, one MCU family:

| Component | Part | LCSC | Used In |
|-----------|------|------|---------|
| MCU | ESP32-C3FH4 | C2858491 | Lite, Mono, Gemini |
| 2.4GHz RF | SX1281IMLTRT | C2151551 | Lite |
| Multi-band RF | LR1121IMLTRT | C7498014 | Mono, Gemini |
| Shared LDO | TLV75533PDQNR | C2861882 | Lite, Mono |
| 52MHz TCXO | YXC OW7EL89 | C22434896 | Lite |
| 32MHz TCXO | YXC OW2EL89 | C22434888 | Mono, Gemini |
| 40MHz crystal | CJ17-400001010B20 | C2875272 | Lite, Mono |
| RGB LED | XL-1010RGBC-WS2812B | C5349953 | Optional status LED on Lite, Mono |

Passive sourcing is still under review at the schematic level. Treat the current `DESIGN.md` files for legacy concepts as reference notes, not launch BOM commitments.

Shared-package policy: default active packages are `QFN/DFN/X2SON/WSON`; larger packages are exceptions only when RF, voltage, or thermal margin requires them.

## CE/FCC Certification

Two active RF families:
- **Lite / SX1281**
- **Mono + Gemini / LR1121**

Certification should be planned around the reduced stack, not the older six-concept family.

## Repository Structure

```
OpenRX/
├── README.md               ← This file
├── KICAD_WORKFLOW.md        ← How to capture schematics (read first)
├── shared/                  ← Shared KiCad libs and schematic sheets
│   ├── libs/                ← OpenRX-Shared symbols + footprints + 3D models
│   └── sheets/              ← Reusable schematic blocks
├── datasheets/common/       ← Shared datasheet cache
├── OpenRX-Lite/             ← Active release SKU: tiny 2.4GHz ceramic-ant board
│   ├── *.kicad_pro/sch/pcb  ← KiCad project
│   ├── DESIGN.md            ← Pin-level schematic + BOM
│   ├── datasheets/          ← Local datasheets
│   └── libs/                ← Project-local symbols + footprints for receiver-specific parts only
├── OpenRX-Mono/             ← Active mainstream single-LR1121 project
├── OpenRX-Gemini/           ← Active later-phase flagship concept
└── archive/legacy-projects/ ← Archived Nano / 900 / PWM / placeholder projects
```

## Market Position

| Segment | Market pattern | OpenRX plan |
|---------|----------------|-------------|
| Tiny 2.4GHz | RadioMaster XR2 | Lite |
| Mainstream multi-band | RadioMaster XR1 / BETAFPV SuperX Mono style | Mono |
| Premium GemX / Gemini | RadioMaster XR4 / BETAFPV SuperX Nano | Gemini |

See [PRODUCT_LINEUP_REDUCTION_2026-03-23.md](/Users/stan/Library/Mobile%20Documents/com~apple~CloudDocs/OpenRX/PRODUCT_LINEUP_REDUCTION_2026-03-23.md) for the reasoning behind the cut.
