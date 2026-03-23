# OpenRX — Open Source ExpressLRS Receiver Family

Part of the [OpenDrone](https://github.com/Just4Stan) ecosystem. Six ELRS 4.0 receivers from budget nano to Xrossband Gemini.

**License:** CERN-OHL-S v2 (hardware), MIT (firmware/tools)

**Status:** Design briefs complete (`DESIGN.md` per receiver). KiCad schematic capture in progress — see `KICAD_WORKFLOW.md` for the working procedure.

## The Lineup

| Model | Band | MCU | RF | Front-End | Size | BOM | Retail | Use Case |
|-------|------|-----|-----|-----------|------|-----|--------|----------|
| **Lite** | 2.4 GHz | ESP32-C3 | SX1281 | — | 16x12mm | ~$8.8 provisional | €8-10 | Whoops, micro quads |
| **Nano** | 2.4 GHz | ESP32-C3 | SX1281 | RFX2401C | 20x13mm | ~$8.7 provisional | €12-15 | Standard 5" quads |
| **900** | 868/915 MHz | ESP32-C3 | LR1121 | — | 18x13mm | ~€5 | €10-13 | Long range |
| **Dual** | Dual-band | ESP32-C3 | LR1121 | RFX2401C | 22x15mm | ~€6 | €15-18 | Switchable bands |
| **PWM** | 2.4 GHz | ESP32-C3 | SX1281 | RFX2401C | 30x20mm | ~€6 | €15-18 | Fixed wing, servos |
| **Gemini** | Xrossband | ESP32-C3 | 2x LR1121 | RFX2401C | 24x18mm | ~€9 | €25-30 | Flagship simultaneous |

Lite and Nano pricing above is a March 23, 2026 LCSC snapshot from the current KiCad netlists, excluding VAT/shipping and treating passives as provisional because several passive `LCSC` fields in the schematics are currently wrong. The other four receivers still carry planning estimates.

## Which One Do I Need?

- **Tiny whoops / micro quads** → Lite
- **3-5" FPV quads** → Nano (best value) or Dual (dual-band flexibility)
- **Maximum range** → 900 (cheap) or Dual (switchable)
- **Fixed wing / heli / cars / boats** → PWM (direct servo outputs)
- **Best possible link** → Gemini (simultaneous 2.4GHz + 900MHz)

## Architecture

Two RF platforms, one MCU, one front-end across all receivers:

| Component | Part | LCSC | Used In |
|-----------|------|------|---------|
| MCU | ESP32-C3FH4 | C2858491 | All 6 |
| 2.4GHz RF | SX1281IMLTRT | C2151551 | Lite, Nano, PWM |
| Dual-band RF | LR1121IMLTRT | C7498014 | 900, Dual, Gemini |
| 2.4GHz PA+LNA | RFX2401C | C19213 | Nano, Dual, PWM, Gemini |
| Shared LDO | TLV75533PDQNR | C2861882 | Lite, Nano, 900, Dual |
| 52MHz TCXO | YXC OW7EL89 | C22434896 | SX1281 family |
| 32MHz TCXO | YXC OW2EL89 | C22434888 | LR1121 family |
| 40MHz crystal | CJ17-400001010B20 | C2875272 | Lite, Nano |
| RGB LED | XL-1010RGBC-WS2812B | C5349953 | Optional status LED on Lite, Nano, 900, Dual |

Passive sourcing is under audit. Do not trust the current Lite/Nano schematic `LCSC` fields for every capacitor/resistor until the passive mapping cleanup is complete. Current pricing snapshots live in each receiver `DESIGN.md`.

Shared-package policy: default active packages are `QFN/DFN/X2SON/WSON`; `SOT-23-5`, `SOT-223`, and larger LEDs are exceptions only when input-voltage or current margin requires them. `PWM` remains a high-VIN exception, and `Gemini` remains a higher-current power exception.

## CE/FCC Certification

Two RF cores = two test families:
- **SX1281 family** (Lite, Nano, PWM): full test on PWM, delta-test others
- **LR1121 family** (900, Dual, Gemini): full test on Gemini, delta-test others

Budget: ~€20-30K for all 6 via family approach.

## Repository Structure

```
OpenRX/
├── README.md               ← This file
├── KICAD_WORKFLOW.md        ← How to capture schematics (read first)
├── shared/                  ← Shared KiCad libs and schematic sheets
│   ├── libs/                ← OpenRX-Shared symbols + footprints + 3D models
│   └── sheets/              ← Reusable schematic blocks
├── datasheets/common/       ← Shared datasheet cache
├── OpenRX-Lite/             ← Budget 2.4GHz
│   ├── *.kicad_pro/sch/pcb  ← KiCad project
│   ├── DESIGN.md            ← Pin-level schematic + BOM
│   ├── datasheets/          ← Local datasheets
│   └── libs/                ← Project-local symbols + footprints for receiver-specific parts only
├── OpenRX-Nano/             ← Standard 2.4GHz + PA/LNA
├── OpenRX-900/              ← Budget sub-GHz
├── OpenRX-Dual/             ← Dual-band switchable
├── OpenRX-PWM/              ← 6ch PWM for fixed wing
└── OpenRX-Gemini/           ← Flagship Xrossband
```

## Competing With RadioMaster

| Segment | RadioMaster | OpenRX | Advantage |
|---------|------------|--------|-----------|
| Budget 2.4GHz | XR2 (€10) | Lite (€8-10) | Open source |
| Mid 2.4GHz | XR1 (€14) | Nano (€12-15) | Open source, PA+LNA |
| Sub-GHz | — | 900 (€10-13) | No cheap RM 900MHz |
| Dual-band | XR3 (€30) | Dual (€15-18) | 40-50% cheaper |
| PWM | ER5C (€20) | PWM (€15-18) | Open source |
| Gemini | XR4 (€40) | Gemini (€25-30) | 25-35% cheaper |
