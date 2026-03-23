Lite and Mono BOMs were exported from KiCad and checked against live LCSC product pages on 2026-03-23.

Files:
- `OpenRX-Lite.csv`
- `OpenRX-Mono.csv`
- `lcsc-live-check.tsv`

Status summary:

- `OpenRX-Lite`: all fitted LCSC-coded parts resolve to the expected MPNs and are currently in stock.
- `OpenRX-Mono`: most fitted LCSC-coded parts resolve correctly, but two fitted parts are currently out of stock:
  - `R6` `220R 0201` -> `C274342`
  - `T1` `0900PC16J0042001E` -> `C19842466`

Important caveats:

- `OpenRX-Lite` still has an annotation warning in KiCad. The inductor is referenced as `L`, not a fully annotated reference like `L1`.
- `OpenRX-Lite` exported BOM is not a purely ceramic-only antenna design in its current schematic. It includes:
  - `AE1` `2450AT18A100E`
  - `AE2` `47948-0001`
- `OpenRX-Mono` still reflects inherited former-Dual hardware choices in the current schematic/BOM:
  - `JP1, JP2` two `U.FL` connectors
  - `T1` sub-GHz balun

Live 1-piece fitted subtotals from LCSC page pricing:

- `OpenRX-Lite`: `$5.6344`
- `OpenRX-Mono`: `$6.9507`

This audit verifies procurement mapping and current LCSC availability. It does not by itself prove RF or production readiness.
