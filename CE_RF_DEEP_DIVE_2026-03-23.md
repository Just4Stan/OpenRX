# OpenRX CE RF Deep Dive

Date: 2026-03-23

Release-plan note:

- current release stack is `Lite`, `Mono`, `Gemini`
- `Nano`, `900`, `Dual`, and `PWM` are legacy concept studies in the repo
- this document still audits those legacy concept schematics because they contain useful RF decisions and failure modes

This is a radio-spectrum compliance risk review for the current and legacy OpenRX receiver schematics:

- `OpenRX-Lite`
- `OpenRX-Nano`
- `OpenRX-900`
- `OpenRX-Dual`
- `OpenRX-Gemini`

It is not a lab report and it does not cover the full RED stack end-to-end. The focus here is Article 3.2 style RF-spectrum risk: output power, spurious/harmonics, antenna assumptions, and whether the current RF chains are plausible CE candidates.

## 1. Applicable CE / RED RF Framework

### 2.4 GHz ELRS receivers

The main radio standard is `ETSI EN 300 328 V2.2.2` for wideband data equipment in `2.4 GHz`.

Key limits relevant here:

- FHSS equipment RF output power must be `<= 20 dBm e.i.r.p.`.
- For transmitter unwanted emissions in the spurious domain above `1 GHz`, the limit is `-30 dBm / 1 MHz`.
- The limit applies for any combination of power level and intended antenna assembly.

Primary sources:

- `EN 300 328 V2.2.2`:
  - RF output power limit for FHSS: `The RF output power for FHSS equipment shall be equal to or less than 20 dBm.`  
    `https://www.etsi.org/deliver/etsi_en/300300_300399/300328/02.02.02_60/en_300328v020202p.pdf`
  - Spurious-domain limits above 1 GHz: `-30 dBm 1 MHz`
  - The antenna-assembly clause is in the same section.
- EU implementing decision summary:
  - `2 400-2 483.5 MHz`
  - `100 mW e.i.r.p. and 100 mW/100 kHz e.i.r.p. density applies when frequency hopping modulation is used`
  - `10 mW/MHz e.i.r.p. density applies when other types of modulation are used`
  - `https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32017D1483`

### Sub-GHz ELRS receivers for Europe

The generic radio standard is now `ETSI EN 300 220-2 V3.3.1 (2025-03)`, which covers SRDs up to `500 mW e.r.p.`. That is only the framework. Actual usable power depends on the sub-band and access rules from the CEPT SRD tables.

Primary sources:

- `EN 300 220-2 V3.3.1`:
  - `https://www.etsi.org/deliver/etsi_en/300200_300299/30022002/03.03.01_60/en_30022002v030301p.pdf`
- CEPT EFIS / ERC 70-03:
  - `863-868 MHz` wideband data systems: `25 mW e.r.p.`, polite spectrum access required, duty-cycle conditions apply  
    `https://efis.cept.org/adhoc_grabber.jsp?annex=6`
  - `869.4-869.65 MHz`: `500 mW e.r.p.`, `<= 10% duty cycle or LBT+AFA`  
    `https://efis.cept.org/adhoc_grabber.jsp?annex=4`

Important consequence:

- You cannot treat "EU 868" as a blanket `500 mW` region.
- The current ExpressLRS EU868 hopping domain spans `863.275 MHz` to `869.575 MHz` across `13` channels, which crosses multiple CEPT sub-bands with different conditions:
  - local code: `src/lib/FHSS/FHSS.cpp`

## 2. What The Current Hardware Can Put Out

### Lite

Current chain:

- `SX1281IMLTRT` at [`OpenRX-Lite/esp32c3_sx1281_lite.kicad_sch:8478`](./OpenRX-Lite/esp32c3_sx1281_lite.kicad_sch#L8478)
- `DEA102700LT-6307A2` at [`OpenRX-Lite/esp32c3_sx1281_lite.kicad_sch:7222`](./OpenRX-Lite/esp32c3_sx1281_lite.kicad_sch#L7222)
- main antenna `47948-0001` at [`OpenRX-Lite/esp32c3_sx1281_lite.kicad_sch:8906`](./OpenRX-Lite/esp32c3_sx1281_lite.kicad_sch#L8906)
- separate ESP Wi-Fi chip antenna `2450AT18A100E` at [`OpenRX-Lite/esp32c3_sx1281_lite.kicad_sch:7809`](./OpenRX-Lite/esp32c3_sx1281_lite.kicad_sch#L7809)

Relevant device ceiling:

- `SX1281` transmitter is `+12.5 dBm` max
  - source: Semtech SX1281 datasheet

Power verdict:

- Lite is comfortably below the `20 dBm e.i.r.p.` ceiling on transmit power alone.
- Even with a modest positive antenna gain, this board has several dB of headroom.

Real CE risk on Lite:

- not output power
- not receiver telemetry power ceiling
- the real risk is whether the `DEA102700LT-6307A2`-only RF path gives enough harmonic suppression and repeatability on your layout

Engineering judgment:

- Lite is the best CE candidate in the current lineup.
- It is the least likely to fail purely on power.
- It still needs a chamber pre-scan because `DEA102700LT-6307A2` is a generic `50 ohm -> 50 ohm` LPF, not a Semtech-specific matched front end.

### Nano

Current chain:

- `SX1281` at [`OpenRX-Nano/esp32c3_sx1281_rx_core.kicad_sch:9465`](./OpenRX-Nano/esp32c3_sx1281_rx_core.kicad_sch#L9465)
- `DEA102700LT-6307A2` at [`OpenRX-Nano/esp32c3_sx1281_rx_core.kicad_sch:7915`](./OpenRX-Nano/esp32c3_sx1281_rx_core.kicad_sch#L7915)
- `RFX2401C` at [`OpenRX-Nano/esp32c3_sx1281_rx_core.kicad_sch:11473`](./OpenRX-Nano/esp32c3_sx1281_rx_core.kicad_sch#L11473)
- the sheet includes a note `ANT trace needs 0.3pF trace capacitance` at [`OpenRX-Nano/esp32c3_sx1281_rx_core.kicad_sch:3755`](./OpenRX-Nano/esp32c3_sx1281_rx_core.kicad_sch#L3755)
- but the explicit caps around that area are `C20 = 220pF` and `C22 = 100nF` at [`OpenRX-Nano/esp32c3_sx1281_rx_core.kicad_sch:8034`](./OpenRX-Nano/esp32c3_sx1281_rx_core.kicad_sch#L8034) and [`OpenRX-Nano/esp32c3_sx1281_rx_core.kicad_sch:9059`](./OpenRX-Nano/esp32c3_sx1281_rx_core.kicad_sch#L9059)

Relevant device ceiling:

- `RFX2401C` saturated output power is `+22 dBm`
- datasheet harmonic data at `POUT = +20 dBm`:
  - second harmonic: `-10 dBm/MHz`
  - third harmonic: `-20 dBm/MHz`
  - non-harmonic spurs: `< -43 dBm/MHz`

The big issue:

- Skyworks does not show the FEM as a bare `ANT pin -> connector` solution.
- Their reference requires:
  - an explicit `0.3 pF` capacitor at `ANT`
  - plus either:
    - a discrete LPF, or
    - a ceramic LPF
- The current Nano schematic does not implement that full post-FEM harmonic filter.

What that means numerically:

- CE spurious limit above `1 GHz` is `-30 dBm / 1 MHz`
- At `+20 dBm` output, the raw RFX harmonic figures imply:
  - second harmonic needs about `20 dB` more suppression
  - third harmonic needs about `10 dB` more suppression

That is the strongest compliance blocker in the current family.

Power verdict:

- If Nano really reaches `+22 dBm` conducted, it is already `2 dB` over the `20 dBm e.i.r.p.` limit with a `0 dBi` antenna.
- With a `2 dBi` antenna, it needs roughly `4 dB` backoff.
- For manufacturing margin, a realistic CE target is closer to `17-18 dBm conducted`, not `20-22 dBm`.

Engineering judgment:

- Nano is not CE-ready as drawn.
- The problem is not routing quality. The problem is the RF architecture after the FEM.
- To make it a serious CE candidate, add the full Skyworks-recommended output filtering and explicitly cap the shipped power table.

### 900

Current chain:

- `LR1121IMLTRT` at [`OpenRX-900/esp32c3_lr1121_900.kicad_sch:6702`](./OpenRX-900/esp32c3_lr1121_900.kicad_sch#L6702)
- Johanson `0900PC16J0042001E` at [`OpenRX-900/esp32c3_lr1121_900.kicad_sch:10271`](./OpenRX-900/esp32c3_lr1121_900.kicad_sch#L10271)
- both `TX_LP` and `TX_HP` paths are present in the LR1121 symbol block, see [`OpenRX-900/esp32c3_lr1121_900.kicad_sch:826`](./OpenRX-900/esp32c3_lr1121_900.kicad_sch#L826) and [`OpenRX-900/esp32c3_lr1121_900.kicad_sch:844`](./OpenRX-900/esp32c3_lr1121_900.kicad_sch#L844)

Relevant device ceiling:

- `LR1121` sub-GHz LP PA: `+15 dBm` capable, optimized around `+14 dBm`
- `LR1121` sub-GHz HP PA: `+22 dBm`

Important regulatory consequence for Europe:

- In the common EU wideband / SRD style sub-bands, `25 mW e.r.p.` is the normal design target, not `500 mW`.
- `25 mW e.r.p.` is about `14 dBm ERP`, which is about `16.15 dBm EIRP`.

Required backoff:

- If the board uses the `+22 dBm` HP PA path, it needs about `6 dB` backoff even before accounting for antenna gain.
- With a `2 dBi` antenna, the required backoff is closer to `8 dB`.
- The LP PA path is much closer to a viable CE target.

Important firmware evidence:

- ExpressLRS itself already encodes a CE view of this:
  - TX UI string: `25/100mW 868M/2G4 CE LIMIT`
  - power-management code caps sub-GHz CE operation to `25 mW` when using LR1121 dual-band CE mode
  - local sources:
    - `src/lib/tx-crsf/TXModuleParameters.cpp`
    - `src/lib/POWERMGNT/POWERMGNT.cpp`

Engineering judgment:

- `OpenRX-900` can be a CE-capable board.
- But only if the EU SKU is treated as an EU SKU:
  - correct domain
  - capped power table
  - fixed antenna assumption
  - probably LP-PA-first design intent
- The RF front-end part choice is reasonable. The main compliance risk is output-power policy, not the Johanson part.

### Dual

Current chain:

- `LR1121` at [`OpenRX-Dual/esp32c3_lr1121_dual.kicad_sch:7908`](./OpenRX-Dual/esp32c3_lr1121_dual.kicad_sch#L7908)
- sub-GHz Johanson front end at [`OpenRX-Dual/esp32c3_lr1121_dual.kicad_sch:12257`](./OpenRX-Dual/esp32c3_lr1121_dual.kicad_sch#L12257)
- `RFX2401C` at [`OpenRX-Dual/esp32c3_lr1121_dual.kicad_sch:9552`](./OpenRX-Dual/esp32c3_lr1121_dual.kicad_sch#L9552)
- explicit small RF parts shown around the FEM are again only `C22 = 100nF` and `C25 = 220pF` at [`OpenRX-Dual/esp32c3_lr1121_dual.kicad_sch:7147`](./OpenRX-Dual/esp32c3_lr1121_dual.kicad_sch#L7147) and [`OpenRX-Dual/esp32c3_lr1121_dual.kicad_sch:11613`](./OpenRX-Dual/esp32c3_lr1121_dual.kicad_sch#L11613)

Verdict:

- Dual inherits the `900` power-policy problem
- and it inherits the `Nano` missing-post-FEM-filter problem

Engineering judgment:

- Dual is not CE-ready as drawn.

### Gemini

Current chain:

- only one `LR1121` instance is present at [`OpenRX-Gemini/esp32c3_lr1121_gemini.kicad_sch:7882`](./OpenRX-Gemini/esp32c3_lr1121_gemini.kicad_sch#L7882)
- `RFX2401C` is present at [`OpenRX-Gemini/esp32c3_lr1121_gemini.kicad_sch:9263`](./OpenRX-Gemini/esp32c3_lr1121_gemini.kicad_sch#L9263)
- sub-GHz Johanson front end is present at [`OpenRX-Gemini/esp32c3_lr1121_gemini.kicad_sch:11968`](./OpenRX-Gemini/esp32c3_lr1121_gemini.kicad_sch#L11968)
- around the FEM you again only have `C22 = 100nF` and `C25 = 220pF` at [`OpenRX-Gemini/esp32c3_lr1121_gemini.kicad_sch:7121`](./OpenRX-Gemini/esp32c3_lr1121_gemini.kicad_sch#L7121) and [`OpenRX-Gemini/esp32c3_lr1121_gemini.kicad_sch:11324`](./OpenRX-Gemini/esp32c3_lr1121_gemini.kicad_sch#L11324)

Two separate blockers:

- it is not a real dual-radio Gemini board yet
- its 2.4 GHz FEM path has the same CE risk as Nano and Dual

Engineering judgment:

- do not treat Gemini as CE-assessable yet
- it is not even the intended product in hardware form today

## 3. Board-by-Board CE RF Verdict

### Best chance today

1. `Lite`
2. `900` if locked to EU-specific power tables and antenna assumptions

### Not CE-ready as drawn

1. `Nano`
2. `Dual`
3. `Gemini`

## 4. What Needs To Change Before Real CE Testing

### Nano / Dual / Gemini

Must change:

- Implement the full `RFX2401C` post-PA harmonic filtering that Skyworks actually recommends.
- Do not rely on `trace capacitance` as the CE baseline.
- Add an explicit `0.3 pF` part at `ANT`.
- Then choose one of:
  - the discrete LPF from the datasheet, or
  - the ceramic LPF option from the datasheet

### 900 / Dual / Gemini sub-GHz

Must decide before certification:

- EU-only capped SKU, or global SKU with different target definitions
- approved antenna gain
- HP PA usage policy

Recommended CE baseline:

- EU sub-GHz boards should ship with a power ceiling around the `25 mW` class for the EU hopping domain
- if you want a "high power" EU variant, it needs a much more careful sub-band / duty-cycle / access-strategy justification than the current generic `EU868` assumption

### All boards with U.FL

Do not leave antenna gain open-ended for CE.

Use:

- a defined antenna list
- a declared maximum antenna gain
- matching conducted power tables tied to that antenna list

## 5. Practical Next Decision

If the goal is "what can I route now and have the best odds of turning into a CE product later":

1. Route `Lite`
2. Route `900`
3. Do not freeze `Nano / Dual / Gemini` RF layout until the `RFX2401C` output filter decision is fixed

That is the highest-signal conclusion from the current hardware and the current standards.
