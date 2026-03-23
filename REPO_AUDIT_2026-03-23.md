# OpenRX Repository Audit — 2026-03-23

## Verified State

- All six receiver directories exist with KiCad project files, `SCHEMATIC.md`, `BOM.md`, local imported libraries, and some local datasheets.
- The KiCad projects are starter shells only:
  - each `.kicad_sch` is effectively empty
  - each `.kicad_pcb` is effectively empty
  - no receiver has been captured in KiCad yet
- The actual design intent currently lives in the markdown design briefs and imported local part libraries.

## Repairs Applied

- Added `sym-lib-table` and `fp-lib-table` to every receiver project so the imported libraries resolve locally for anyone cloning the repo.
- Updated each `.kicad_pro` to pin its project-local symbol and footprint library and to use the correct project filename instead of `placeholder.kicad_pro`.
- Rewrote imported footprint 3D model paths to `${KIPRJMOD}` so they are no longer tied to one workstation.
- Normalized the top-level docs so they no longer describe the repo as six already-instantiated receiver schematics.
- Added a shared `datasheets/common/` cache and backfilled the obvious missing per-project datasheets from local copies plus direct downloads.

## BOM / Architecture Corrections

- `OpenRX-Gemini` is currently an `ESP32-C3 + 2x LR1121` concept, not an `ESP32-S3` design.
- `OpenRX-Gemini` has one 2.4GHz front-end on the 2.4GHz path, not two front-ends and not four RF connectors.
- `OpenRX-Nano` already uses `RFX2401C`; the other front-end designs still document `SE2431L` and should not be considered standardized yet.
- `LR1121IMLTRT` should be treated as a `QFN-32 4x4mm` part. Any `5x5mm` references elsewhere in the repo are stale.

## Remaining Technical Risks

- `OpenRX-900` still contains contradictory LR1121 pinout / package notes across its docs and needs a dedicated cleanup pass before schematic entry.
- `OpenRX-Dual`, `OpenRX-PWM`, and `OpenRX-Gemini` still need a deliberate decision on `SE2431L` vs `RFX2401C` before schematic capture starts.
- The sub-GHz balun remains an external sourcing problem for the LR1121-based boards if you want a pure LCSC/JLCPCB flow.
- Datasheet coverage is much better than the initial drop, but a few connector / alternate-part PDFs are still not exact-per-project matches.

## Recommended Next Step

Capture one receiver first, then fan out:

1. `OpenRX-Lite` as the simplest SX1281 baseline.
2. `OpenRX-Nano` as the preferred mainstream 2.4GHz product.
3. `OpenRX-900` only after the LR1121 package / pinout pass is reconciled.
