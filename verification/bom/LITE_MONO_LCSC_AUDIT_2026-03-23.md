Active receiver BOMs were exported from KiCad and checked against LCSC on 2026-03-23.

Files:
- `OpenRX-Lite-lcsc.csv`
- `OpenRX-Mono-lcsc.csv`
- `OpenRX-Gemini-lcsc.csv`
- `lcsc-live-check.tsv`

Status summary:

- `OpenRX-Lite`: all fitted LCSC-coded parts resolve to the expected MPNs and are currently in stock.
- `OpenRX-Mono`: all fitted parts resolve correctly, but one fitted sourcing blocker remains:
  - `T1` `0900PC16J0042001E` -> `C19842466` currently shows `Out of Stock` on the direct LCSC product page.
- `OpenRX-Gemini`: same current sourcing blocker as Mono:
  - `T1` `0900PC16J0042001E` -> `C19842466` currently shows `Out of Stock` on the direct LCSC product page.

Direct re-checks made after the earlier BOM pass:

- `C274342` (`220R 0201`) now shows `In Stock` again on the direct LCSC product page, so it is no longer an active blocker for `Mono` or `Gemini`.
- `C19842466` still resolves to the correct Johanson part, but the direct product page currently shows `Out of Stock` despite older indexed snippets still showing stock.

Important caveats:

- `OpenRX-Lite` still has an annotation warning in KiCad. The inductor is referenced as `L`, not a fully annotated reference like `L1`.
- `OpenRX-Lite` is still a ceramic-only ELRS antenna design in the current schematic:
  - `AE1` `2450AT18A100E` is the ESP32-C3 Wi-Fi antenna.
  - `AE2` `47948-0001` is the ELRS antenna/feed part on the main SX1281 path.
- `OpenRX-Mono` still reflects inherited former-Dual hardware choices in the current schematic/BOM:
  - `JP1, JP2` two `U.FL` connectors
  - `T1` sub-GHz balun
- `OpenRX-Gemini` now has the same grouped LCSC BOM export as Lite and Mono, but its design brief still contains some older package/BOM discussion that should not override the schematic or the verification exports.

Live 1-piece fitted subtotals from LCSC page pricing:

- `OpenRX-Lite`: `$5.6344`
- `OpenRX-Mono`: `$6.9507`

This audit verifies procurement mapping and current LCSC availability. It does not by itself prove RF or production readiness.
