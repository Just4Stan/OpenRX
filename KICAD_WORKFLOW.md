# KiCad Workflow — OpenRX Receiver Family

Working procedure for schematic capture and layout. Checked against the local ExpressLRS tree at `/Users/stan/Documents/GitHub/ExpressLRS` on 2026-03-23.

## Golden Rule

Do not advance all 6 projects independently. Three reusable hardware cores feed the six products. Capture one core, freeze it, then fan out.

## KiCad File Safety

Do not hand-author large `.kicad_sch` or `.kicad_pcb` structure in a text editor.

Use the KiCad GUI for:
- creating new sheets
- placing symbols
- wiring symbols
- building PCB structure

Text-side edits are only for small, targeted fixes copied from a known-good KiCad file pattern.
Every text-side schematic change must be validated before it is handed back:

- schematic: `'/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli' sch erc <project>.kicad_sch`
- pcb: validate in KiCad GUI or use the matching `kicad-cli pcb` path where applicable

This repo should be treated as GUI-authored KiCad data with CLI verification, not as freehand S-expression source.

## Shared Library Policy

`shared/libs/OpenRX-Shared.*` is the source of truth for reusable parts shared across multiple receivers.

Use the shared library for:
- MCUs, radios, shared power parts, shared clocks, shared LEDs, shared antennas
- any part that will appear in more than one receiver family

Use project-local `libs/` only for:
- one-off parts unique to a single receiver
- temporary imports while evaluating a part before promoting it to the shared library

Do not hand-draw new reusable symbols or footprints when the part exists in LCSC / EasyEDA. Import it first, then do only minimal cleanup.

Current shared compact defaults:
- `TLV75533PDQNR` on `OpenRX-Shared:X2SON-4_L1.0-W1.0-P0.65-TL-EP`
- `XL-1010RGBC-WS2812B` on `OpenRX-Shared:LED-SMD_4P-L1.0-W1.0-TL_XL-1010RGBC-WS2812B`

Legacy parts may still exist in project-local receiver libraries, but they are not part of the shared baseline for new work.

## Shared Part Import Rule

When a new reusable part is needed:
1. `cd` into a product directory such as `OpenRX-Lite/`
2. import into the shared library, not the project-local one
3. verify the symbol, footprint, and 3D path before using it in a schematic

Example:

```bash
cd OpenRX-Lite
easyeda2kicad --lcsc_id C2861882 --full --output ../shared/libs/OpenRX-Shared.kicad_sym --project-relative --overwrite
easyeda2kicad --lcsc_id C5349953 --full --output ../shared/libs/OpenRX-Shared.kicad_sym --project-relative --overwrite
```

Post-import checks:
- symbol footprint field should point at `OpenRX-Shared:<footprint-name>`
- footprint `model` path should point at `${KIPRJMOD}/../shared/libs/OpenRX-Shared.3dshapes/...`
- if the importer writes a bad relative 3D path, fix only that path text and nothing else

## Capture Order

| # | Receiver | Core | Status | Notes |
|---|----------|------|--------|-------|
| 1 | **OpenRX-Lite** | ESP32-C3 + SX1281 | **Start now** | Simplest SX1281 baseline |
| 2 | **OpenRX-Nano** | reuse Lite core + add FEM sheet | Start after Lite | Add RFX2401C front-end |
| 3 | **OpenRX-900** | ESP32-C3 + LR1121 | After LR1121 datasheet pass | LR1121 pinout needs verification |
| 4 | **OpenRX-Dual** | reuse 900 core + add 2.4GHz FEM | After 900 | FEM driven from LR1121 RFSW pins |
| 5 | **OpenRX-Gemini** | ESP32-C3 + 2x LR1121 | After Dual | Dual-radio SPI, tightest GPIO |
| 6 | **OpenRX-PWM** | reuse Lite core + add PWM bank | Last | GPIO allocation needs firmware check |

## Shared Schematic Sheets

Use KiCad hierarchical sheets. Capture these blocks once in `shared/sheets/`, then instantiate from each product project:

| Sheet | Contents | Used By |
|-------|----------|---------|
| `esp32c3_core.kicad_sch` | ESP32-C3 + 40MHz crystal + EN RC delay + boot button + USB pads + XL-1010RGBC-WS2812B + C89334 Wi-Fi antenna | Lite, Nano, 900, Dual |
| `power_3v3.kicad_sch` | TLV75533PDQNR + 1uF local VIN/VOUT caps | Lite, Nano, 900, Dual |
| `sx1281_radio.kicad_sch` | SX1281 + 52MHz TCXO + VR_PA cap + NSS pull-up + NRESET RC | Lite, Nano, PWM |
| `rfx2401c_fem.kicad_sch` | RFX2401C + SAW filter + UFL connector + matching | Nano, Dual, PWM, Gemini |
| `lr1121_radio.kicad_sch` | LR1121 + 32MHz TCXO + DC-DC inductor + RFSW connections | 900, Dual, Gemini |
| `subghz_output.kicad_sch` | Sub-GHz balun + UFL connector | 900, Dual, Gemini |
| `crsf_io.kicad_sch` | UART TX/RX pads + 5V/GND pads | All 6 |
| `pwm_bank.kicad_sch` | 6x PWM outputs + protection resistors + servo headers | PWM only |

**How to reference shared sheets from a product project:**
- In KiCad: Add Hierarchical Sheet -> browse to `../shared/sheets/esp32c3_core.kicad_sch`
- The `${KIPRJMOD}/../shared/` path is already configured in sym-lib-table and fp-lib-table
- Place shared symbols and footprints from the `OpenRX-Shared` library first; only fall back to project-local libraries for receiver-specific parts

## Package Policy

- Default active packages: `QFN`, `DFN`, `X2SON`, `WSON`
- Default passive package: `0402`
- Use `0603` / `0805` only where capacitance, voltage rating, RF behavior, or thermal margin requires it
- Do not keep `SOT-23-5`, `SOT-223`, or `2x2/3.5x3.5` LEDs as the shared default when a smaller validated part exists

## ELRS Pin Contract

These are the firmware-backed pin names. Your `hardware.json` target definition must use these exact keys.

### SX1281 Receivers (Lite, Nano, PWM)

| ELRS Key | ESP32-C3 GPIO | SX1281 Pin | Notes |
|----------|---------------|------------|-------|
| `radio_sck` | GPIO4 | SCK (18) | SPI clock |
| `radio_miso` | GPIO6 | MISO (16) | SPI data out |
| `radio_mosi` | GPIO7 | MOSI (17) | SPI data in |
| `radio_nss` | GPIO8 | NSS (19) | Chip select, 10k pull-up to 3.3V |
| `radio_dio1` | GPIO5 | DIO1 (5) | **Main IRQ — NOT DIO0** |
| `radio_busy` | GPIO3 | BUSY (4) | Mandatory for OpenRX |
| `radio_rst` | GPIO2 | NRESETn (3) | Include always |
| `power_txen` | GPIO1 | — | RFX2401C TXEN (Nano/PWM only) |
| `power_rxen` | GPIO0 | — | RFX2401C RXEN (Nano/PWM only) |

**UART:** GPIO20 (RX) / GPIO21 (TX) — CRSF serial to flight controller.

### LR1121 Single-Radio (900, Dual)

| ELRS Key | ESP32-C3 GPIO | LR1121 Pin | Notes |
|----------|---------------|------------|-------|
| `radio_sck` | GPIO4 | SCK | SPI clock |
| `radio_miso` | GPIO6 | MISO | SPI data out |
| `radio_mosi` | GPIO7 | MOSI | SPI data in |
| `radio_nss` | GPIO8 | NSS | Chip select, 10k pull-up |
| `radio_dio1` | GPIO5 | DIO9 | **Physical DIO9 -> logical radio_dio1** |
| `radio_busy` | GPIO3 | BUSY/DIO0 | Mandatory |
| `radio_rst` | GPIO2 | NRESET | Include always |
| `radio_rfsw_ctrl` | — | RFSW_0-3 | **FEM control via radio, NOT MCU GPIOs** |

**FEM control on LR1121 receivers:** The LR1121 controls the RFX2401C TXEN/RXEN directly through its RFSW pins via `SetDioAsRfSwitch()`. Do NOT wire TXEN/RXEN to ESP32-C3 GPIOs. This is different from SX1281 receivers.

### LR1121 Dual-Radio (Gemini)

Same as single-radio plus second radio on shared SPI bus:

| ELRS Key | ESP32-C3 GPIO | Notes |
|----------|---------------|-------|
| `radio_nss_2` | GPIO10 | Second chip select |
| `radio_dio1_2` | GPIO9 | Second IRQ (boot pin — needs pull-up) |
| `radio_busy_2` | GPIO1 | Second BUSY |
| `radio_rst_2` | GPIO0 | Second NRESET (or share with radio 1) |

If `radio_nss_2` is absent, ELRS treats hardware as single-radio.

## ESP32-C3 Boot Pin Rules

These apply to every receiver:

- **GPIO8**: Must be HIGH at boot for normal SPI flash mode. NSS pull-up satisfies this.
- **GPIO9**: Must be HIGH at boot. If used for radio_dio1_2 (Gemini), the pull-up keeps boot safe. LR1121 DIO9 is normally low, pulses high on interrupt — boot-safe.
- **CHIP_EN**: Always use 10k pull-up + 1uF RC delay to GND.
- **GPIO2**: Safe to use for NRESET (no boot function).

## ESP32 Wi-Fi Update Path

ExpressLRS receivers on ESP32-C3 support receiver-side Wi-Fi update / admin mode. That is an ESP32 function and should not be merged with the ELRS radio RF path.

- Use `2450AT18A100E` (`C89334`) on `LNA_IN` as the ESP32 Wi-Fi/BLE antenna
- treat it as a short-range update / admin path only
- keep it fully separate from the SX1281 or LR1121 antenna path
- do not add RF sharing or switching between ESP32 Wi-Fi and the ELRS radio
- keep the OpenFC pattern in mind here: ceramic antenna on the ESP32 side, separate ELRS radio path

## 2.4GHz RF Path

The DEA102700LT-6307A2 (TDK, LCSC C574024) is a 50-ohm-in/50-ohm-out multilayer LPF in 0402. RadioMaster uses this as the **sole component** between SX1281 RFIO and antenna/FEM on all their receivers. No discrete matching network needed — the ~40-to-50 ohm mismatch on RFIO is acceptable in practice (~0.5 dB loss).

### Without FEM (Lite)

```
SX1281 RFIO (pin 15) → DEA102700LT-6307A2 → ceramic antenna or UFL
```

### With RFX2401C (Nano, PWM, Dual, Gemini)

```
SX1281 RFIO (pin 15) → DEA102700LT-6307A2 → RFX2401C TXRX (pin 4, 50Ω)
RFX2401C ANT (pin 10) → 0.3pF shunt to GND → UFL connector
```

The 0.3pF on the ANT output is **mandatory per RFX2401C datasheet** — filters the 5th harmonic (~12 GHz). Without it, expect CE spurious emission failure. Place as close to ANT pin as possible.

**Do NOT add** discrete L-match or pi-filter networks. The DESIGN.md files contain stale matching network sections that should be ignored.

## SX1281 Power Mode

Use **LDO mode** on all SX1281 receivers:
- VR_PA (pin 10): 470nF cap to GND. **No inductor.**
- DC-DC mode would need a 15nH inductor — unnecessary for RX power levels.

## LR1121 Power

- VR_PA: 4.7uF + 100nF to GND (internal DC-DC output)
- DCC_SW: 10uH inductor to VBAT (internal DC-DC switching node)
- VTCXO: internal regulator output — configure firmware to match TCXO voltage (3.3V for YXC)

## Step-by-Step: Capturing OpenRX-Lite

This is the first receiver to capture. It establishes the SX1281 core that Nano and PWM reuse.

### Step 1: Create shared ESP32-C3 core sheet

1. Open `OpenRX-Lite/OpenRX-Lite.kicad_pro` in KiCad
2. Create `shared/sheets/esp32c3_core.kicad_sch` as a hierarchical sheet
3. Place: ESP32-C3FH4, 40MHz crystal (C90924), 2x 10pF load caps
4. Add: CHIP_EN circuit (10k pull-up + 1uF to GND)
5. Add: GPIO9 boot pull-up (10k)
6. Add: XL-1010RGBC-WS2812B on GPIO10 + 330R series + 100nF decoupling, powered from 5V
7. Add: `2450AT18A100E` (`C89334`) on `LNA_IN` as the ESP32 Wi-Fi update antenna, with the required edge placement and keepout
8. Add: USB D+/D- test pads on GPIO18/19
9. Add: 3.3V decoupling (3x 100nF on VDD3P3, VDD_SPI, VDD3P3_RTC + 1uF on VDDA)
10. Export hierarchical pins for: SPI bus (SCK/MISO/MOSI/NSS), radio control (DIO1/BUSY/RST), UART (TX/RX), power control (TXEN/RXEN), power rails (3.3V/GND/5V)

### Step 2: Create shared power sheet

1. Create `shared/sheets/power_3v3.kicad_sch`
2. Place: TLV75533PDQNR (C2861882)
3. Local input cap: 1uF at IN to GND, plus 10uF bulk at the 5V power entry
4. Local output cap: 1uF at OUT to GND, plus 10uF bulk on the 3.3V rail near the ESP32-C3
5. EN tied to VIN
6. Export: 5V_IN, 3V3_OUT, GND

### Step 3: Create SX1281 radio core sheet

1. Create `shared/sheets/sx1281_radio.kicad_sch`
2. Place: SX1281IMLTRT (C2151551)
3. Add: 52MHz TCXO (C22434896) -> XTA, XTB floating
4. Add: VDD pins (1, 11) + VDD_IN (pin 2) -> 3.3V, each with 100nF
5. Add: VR_PA (pin 10) -> 470nF to GND (LDO mode)
6. Add: NSS 10k pull-up, NRESET 10k pull-up
7. Export: SPI bus, DIO1, BUSY, RST, RFIO (to antenna/FEM)

### Step 4: Create CRSF I/O sheet

1. Create `shared/sheets/crsf_io.kicad_sch`
2. 4 pads: 5V, GND, TX (GPIO21), RX (GPIO20)
3. 1.27mm pitch castellated edge pads

### Step 5: Wire the Lite top-level schematic

1. In `OpenRX-Lite.kicad_sch`, instantiate:
   - `esp32c3_core` sheet
   - `power_3v3` sheet
   - `sx1281_radio` sheet
   - `crsf_io` sheet
2. Add Lite-specific ELRS RF path: DEA102700LT-6307A2 on SX1281 RFIO → chosen ELRS antenna path. This is separate from the ESP32 Wi-Fi ceramic antenna in `esp32c3_core`.
3. Connect all hierarchical pins
4. Run ERC

### Step 6: Freeze the SX1281 pin contract

Once Lite passes ERC:
- The GPIO assignments in the ESP32-C3 core sheet are now frozen
- Nano and PWM must use the same core sheet without modifying pin assignments
- Any Nano/PWM-specific features go in separate sheets (FEM, PWM bank)

### Step 7: OpenRX-Nano

1. Copy Lite's top-level structure
2. Reuse same 3 shared sheets (esp32c3_core, power_3v3, sx1281_radio)
3. Add new shared sheet: `rfx2401c_fem.kicad_sch` (RFX2401C + 0.3pF 5th harmonic cap + UFL connector)
4. Wire: SX1281 RFIO → DEA102700LT-6307A2 → RFX2401C TXRX. RFX2401C ANT → 0.3pF shunt → UFL
5. Wire TXEN → GPIO1, RXEN → GPIO0
6. Remove ceramic antenna (Lite-specific)

### Step 8: Move to LR1121 family

Only after Lite + Nano are stable:
1. Do LR1121 datasheet reconciliation pass for OpenRX-900
2. Create `shared/sheets/lr1121_radio.kicad_sch`
3. Create `shared/sheets/subghz_output.kicad_sch`
4. Capture OpenRX-900 -> OpenRX-Dual -> OpenRX-Gemini -> OpenRX-PWM

## Layout Guidelines

- **SX1281**: Keep RFIO trace as short as possible, 50 ohm controlled impedance
- **LR1121**: Sub-GHz differential pair needs matched-length traces
- **ESP32-C3**: Crystal close to XTAL pins, no routing under crystal
- **Decoupling**: Every VDD pin gets its own 100nF, placed within 1mm of pin
- **GND**: Solid ground pour on both sides, via stitch around RF sections
- **Antenna keepout**: keep the ESP32 Wi-Fi ceramic antenna keepout separate from any ELRS 2.4GHz antenna keepout or feed structure
- **UFL connector**: Place at board edge, ground vias surrounding pad

## Known Issues

1. **LR1121 footprint**: easyeda2kicad imported as 5x5mm QFN-32, but LR1121 is actually 4x4mm. Fix footprint before layout.
2. **Sub-GHz balun** (Johanson 0900BM15A0001): Not on LCSC. Either consign from DigiKey or design discrete LC balun.
3. **PWM GPIO allocation**: 6 channels + FEM control exceeds ESP32-C3 GPIO count. 4ch safe, 6ch needs DIO2-based antenna switching (unconfirmed in ELRS).
4. **Gemini FEM control**: Must use LR1121 RFSW pins, not MCU GPIOs. Current DESIGN.md partially wrong on this.
