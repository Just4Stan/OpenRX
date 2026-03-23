# Datasheet Layout

## `common/`

Shared local datasheet cache for the core parts used across the OpenRX family. This is the best single place to start during schematic capture and BOM cleanup.

Included here now:

- ESP32-C3FH4
- SX1281
- LR1121 datasheet + user manual
- ME6211
- AMS1117
- AP2112K
- RFX2401C
- SE2431L
- NDFH024-2442SA
- WS2812B-2020
- Johanson 2450AT18A100E antenna
- YXC 52MHz TCXO `OW7EL89CENUNFAYLC-52M`
- YXC 32MHz TCXO `OW2EL89CENUXFMYLC-32M`
- TXC `7M40000005` / `7M` crystal family
- Hirose `U.FL-R-SMT-1(80)`

## Per-project `datasheets/`

Each receiver directory also keeps a working set of local PDFs close to its own BOM and design brief. Those folders are no longer as sparse as the original drop, but they are still convenience copies rather than a perfect one-to-one part lock.

## Remaining Gaps

- `OpenRX-Gemini` still does not have an exact local `KH-IPEX4-2020` connector datasheet in the repo.
- Some project BOMs still reference alternate SAW / connector / front-end parts that do not yet match the current common baseline.
