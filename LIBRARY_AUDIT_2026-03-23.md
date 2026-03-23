# Library Audit

Date: 2026-03-23

## Verified

- All receiver projects now point to a single custom local symbol library:
  - `shared/libs/OpenRX-Shared.kicad_sym`
- All receiver projects now point to a single custom local footprint library:
  - `shared/libs/OpenRX-Shared.pretty`
- All custom footprint 3D models now resolve locally from:
  - `shared/libs/OpenRX-Shared.3dshapes`
- The stale `OpenRX-Lite` library entries were removed from all project `sym-lib-table` and `fp-lib-table` files.

## Custom Library Coverage

- Shared custom symbols present: `14`
- Shared custom footprints present: `16`
- Used custom symbols referenced by current receiver schematics: `14`
- Used custom footprints referenced by current receiver schematics: `15`
- Missing used custom symbols: `0`
- Missing used custom footprints: `0`
- Footprints without a local 3D model: `0`
- Footprints with broken local 3D references: `0`

## KiCad Validation

The following top-level schematics successfully exported a netlist using KiCad CLI after the library-table cleanup:

- `OpenRX-Lite/OpenRX-Lite.kicad_sch`
- `OpenRX-Nano/OpenRX-Nano.kicad_sch`
- `OpenRX-900/OpenRX-900.kicad_sch`
- `OpenRX-Dual/OpenRX-Dual.kicad_sch`
- `OpenRX-Gemini/OpenRX-Gemini.kicad_sch`

## Important Caveat

This audit covers the custom imported OpenRX parts and project-local library linking.

The schematics still use standard built-in KiCad libraries for generic symbols and footprints such as:

- `Device`
- `power`
- `Connector`
- `Resistor_SMD`
- `Capacitor_SMD`

So the repo is now a clean single-library setup for all custom receiver parts, but it is not a fully vendored copy of the entire KiCad standard library stack.
