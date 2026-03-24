# OpenRX — Open Source ExpressLRS Receiver Family

Part of the [OpenDrone](https://github.com/Just4Stan) ecosystem. Three ELRS 4.0 receivers: Lite, Mono, and Gemini.

**License:** CERN-OHL-S v2 (hardware), MIT (firmware/tools)

## Receivers

| Model | Band | RF | Front-End | Antenna | Target Price | ELRS Target |
|-------|------|-----|-----------|---------|-------------|-------------|
| **Lite** | 2.4 GHz | SX1281 | DEA LPF only | Ceramic (Molex tower) | €8-10 | Generic C3 2400 |
| **Mono** | Multi-band | LR1121 | RFX2401C + SKY13588 + Johanson IPD | 1× UFL, dual-band | €15-18 | Generic C3 LR1121 |
| **Gemini** | Xrossband | 2× LR1121 | 2× (RFX2401C + SKY13588 + Johanson IPD) | 2× UFL, dual-band | €25-30 | Generic C3 LR1121 True Diversity |

## Architecture

All receivers share ESP32-C3FH4 MCU + TLV75533PDQNR LDO + 40MHz crystal + 2450AT18A100E WiFi antenna.

### Mono/Gemini RF Chain (per radio)

```
Sub-GHz:  LR1121 → Johanson IPD (direct-tie, 100pF series caps on TX) → SKY13588 J1
2.4GHz:   LR1121 RFIO_HF → DEA LPF → RFX2401C (100mW PA+LNA) → SKY13588 J2
Band select: SKY13588 RFC → UFL → dual-band antenna
```

Gemini = two complete Mono RF chains sharing one ESP32-C3 via SPI bus.

## Status

- [x] Lite schematic complete, ERC clean
- [x] Mono schematic complete, ERC clean, RF chain verified
- [x] Gemini schematic complete, ERC clean
- [x] Initial PCB layout for all 3 receivers
- [ ] Final routing and DRC clean
- [ ] JLCPCB production files
- [ ] CE/RED pre-assessment
- [ ] Prototype build and bring-up

## Repository Structure

```
OpenRX/
├── README.md
├── LICENSE                     ← CERN-OHL-S v2
├── KICAD_WORKFLOW.md           ← Schematic capture guide + ELRS pin contracts
├── FINAL_NETLIST.md            ← Definitive RF topology + wiring tables
├── shared/                     ← Shared KiCad libs (symbols, footprints, 3D)
├── datasheets/common/          ← IC datasheets
├── OpenRX-Lite/                ← 2.4GHz ceramic-antenna receiver
├── OpenRX-Mono/                ← Multi-band single-radio receiver
├── OpenRX-Gemini/              ← Xrossband dual-radio receiver
├── archive/legacy-projects/    ← Old Nano/900/Dual/PWM concepts
├── exports/                    ← Schematic PDFs for review
└── verification/               ← BOM audits and LCSC checks
```

## Key Components

| Component | LCSC | Used In |
|-----------|------|---------|
| ESP32-C3FH4 | C2858491 | All |
| SX1281IMLTRT | C2151551 | Lite |
| LR1121IMLTRT | C7498014 | Mono, Gemini |
| RFX2401C | C19213 | Mono, Gemini |
| SKY13588-460LF | C2151906 | Mono, Gemini |
| 0900PC16J0042001E | C19842466 | Mono, Gemini |
| DEA102700LT-6307A2 | C574024 | All |
| TLV75533PDQNR | C2861882 | All |

## CE/RED Certification

Two RF families:
- **SX1281** (Lite): EN 300 328 (2.4GHz)
- **LR1121** (Mono + Gemini): EN 300 328 + EN 300 220 (sub-GHz)

Both require EN 301 489 (EMC) and EN 62368-1 (safety).

Design considerations for compliance:
- DEA LPF provides 2.4GHz harmonic filtering for EN 300 328
- RFX2401C 0.3pF ANT shunt for 5th harmonic
- Johanson IPD provides sub-GHz filtering for EN 300 220
- SKY13588 provides band isolation
- Direct-tie sub-GHz with 100pF DC blocking caps per Semtech §9.4.3
- Custom `radio_rfsw_ctrl` firmware config required
- WiFi antenna path fully separate from ELRS RF

Family certification: test Gemini (worst-case LR1121), delta-test Mono. Test Lite separately. Budget ~€20-30K total.

## Contributing

Open source hardware — CERN-OHL-S v2. See `KICAD_WORKFLOW.md` for design guidelines.
