# OpenRX ELRS 4 Receiver Portfolio Brief

Date: 2026-03-23

## Executive answer

If the goal is "fully ExpressLRS 4.x compatible and future-proof", do not build a fresh receiver family around ESP8285 or around single-purpose 2.4-only / 900-only boards unless size or cost absolutely force it.

The cleanest plan is:

1. Make one mainstream serial receiver platform around ESP32-C3 + single LR1121.
2. Make one premium platform around ESP32-C3 + dual LR1121.
3. Keep the OpenFC ELRS design only as a cost-down 2.4 GHz template for a minimal serial receiver or FC-integrated receiver, not as the main OpenRX architecture.

That gives you:

- a modern mainstream receiver that can cover 2.4 GHz and sub-GHz with one electrical platform
- a premium Gemini / GemX / X-Band receiver that aligns with where ELRS 4.0 is clearly going
- an optional low-cost 2.4 GHz derivative if you want a whoop/race SKU later

## What ELRS 4.0 changed that matters for hardware

Official 4.0.0 was released on 2026-02-06. The major hardware-relevant changes are:

- OTA v4 is not cross-compatible with 3.x
- STM32-based hardware support was removed
- receiver antenna mode handling is now more automatic
- LR1121 gets the biggest expansion in packet-rate and band-mode support
- X-Band / GemX is now a first-class mode rather than a side path

Sources:

- [ExpressLRS 4.0.0 release](https://github.com/ExpressLRS/ExpressLRS/releases/tag/4.0.0)
- [Hardware Selection](https://www.expresslrs.org/hardware/hardware-selection/)
- [Lua RF Band docs](https://www.expresslrs.org/quick-start/transmitters/lua-howto/)

Local code confirms the product split very clearly:

- unified receiver targets exist for ESP32, ESP32-C3, ESP32-S3, and ESP8285 across `2400`, `900`, and `LR1121` in [unified.ini](/Users/stan/Documents/GitHub/ExpressLRS/src/targets/unified.ini#L240)
- unified RX hardware already supports second-radio pins, RF switch control, and dual power tables in [Unified_ESP_RX.h](/Users/stan/Documents/GitHub/ExpressLRS/src/include/target/Unified_ESP_RX.h#L7)
- ELRS 4.x local code exposes single-band 900, single-band 2.4, and dual-band LR1121 rates in [common.cpp](/Users/stan/Documents/GitHub/ExpressLRS/src/src/common.cpp#L26)
- dual-band operation is explicitly gated on a second radio path and the right power tables in [common.cpp](/Users/stan/Documents/GitHub/ExpressLRS/src/src/common.cpp#L223)
- the transmitter-side UI now treats RF band as `subGHz`, `2.4GHz`, and `X-Band`, and forces Gemini on dual-band modes in [TXModuleParameters.cpp](/Users/stan/Documents/GitHub/ExpressLRS/src/lib/tx-crsf/TXModuleParameters.cpp#L804)

## Official ELRS reference designs

ExpressLRS still publishes DIY receiver references, but they should be treated as reference starting points, not as the final answer for a 2026 product line.

Useful starting points:

- [DIY RX docs](https://www.expresslrs.org/hardware/special-targets/diy-rx/)
- [ExpressLRS-Hardware PCB repository](https://github.com/ExpressLRS/ExpressLRS-Hardware/tree/master/PCB)

The official DIY references called out in the current docs include boards like:

- 20x20 RX
- DIY 900RX
- 0805 Mini RX

These are useful for checking proven legacy SX128x / SX127x implementation details, but I would not use them as the direct architectural template for the mainstream OpenRX line when ELRS 4.0 is now leaning so hard into LR1121 and X-Band.

## What a standard receiver lineup looks like in 2026

The current market pattern is:

- tiny 2.4 GHz single-radio receiver
- mainstream 2.4 GHz full-range receiver
- 900 MHz single-radio long-range receiver
- 2.4 GHz true-diversity receiver
- 900 MHz true-diversity receiver
- premium dual-LR1121 Gemini / GemX / X-Band receiver
- optional PWM receiver for fixed-wing / surface

ExpressLRS official hardware guidance still frames the market this way:

- 2.4 GHz is the default recommendation for most users
- 900 MHz is still the long-range / noisy-environment option
- diversity and PA/LNA matter more once range and blockage matter
- PWM is still its own segment

See [Hardware Selection](https://www.expresslrs.org/hardware/hardware-selection/).

## What competitors are doing

### RadioMaster

RadioMaster is already running a split portfolio:

- legacy RP line for low-cost / older architecture 2.4 GHz
- XR line for LR1121-based new-generation products
- RP4TD / RP4TD-M for premium 2.4 GHz true diversity
- XR4 for premium dual-band GemX / Gemini

Useful product pages:

- [RP1 V2 2.4 GHz Nano Receiver](https://www.radiomasterrc.com/products/rp1-expresslrs-2-4ghz-nano-receiver)
- [XR3 Nano Multi-Frequency Receiver](https://www.radiomasterrc.com/products/xr3-nano-multi-frequency-antenna-diversity-expresslrs-receiver)
- [XR4 Gemini Xrossband Receiver](https://www.radiomasterrc.com/products/xr4-gemini-xrossband-dual-band-expresslrs-receiver)
- [RP4TD-M True Diversity Receiver](https://radiomasterrc.com/collections/receivers/products/rp4td-m-expresslrs-2-4ghz-mini-true-diversity-receiver)

The strategic signal is obvious: RadioMaster is not abandoning cheap 2.4 GHz, but its forward-looking line is LR1121.

### BETAFPV

BETAFPV now spans old and new generations in one family:

- Nano receivers for basic 2.4 / 900
- SuperD for dual-radio true diversity
- SuperX Mono for single LR1121 multi-band
- SuperX Nano for dual LR1121 GemX

Useful product pages:

- [SuperD ELRS Diversity Receiver](https://betafpv.com/products/superd-elrs-2-4g-diversity-receiver)
- [SuperX ELRS Gemini Xross Receiver](https://betafpv.com/products/superx-elrs-gemini-xross-receiver)

### GEPRC

GEPRC is doing the same thing:

- dual 2.4 diversity
- dual-band LR1121
- dual-LR1121 GemX

Useful product pages:

- [GEPRC ELRS DUAL 2.4G Diversity Receiver](https://geprc.com/product/geprc-elrs-dual-2-4g-diversity-receiver/)
- [GEPRC ELRS 915M/2.4G Gemini Xrossband Receiver](https://geprc.com/product/geprc-elrs-915m-2-4g-gemini-xrossband-receiver/)
- [GEPRC ELRS 915M/2.4G C3 Gemini Xrossband Receiver](https://geprc.com/product/geprc-elrs-915m-2-4g-c3-gemini-xrossband-receiver/)

## Recommended OpenRX lineup

Do not make seven unrelated boards. Make two core platforms and one optional derivative.

### Platform A: mainstream serial receiver

Recommended architecture:

- ESP32-C3
- single LR1121
- TCXO
- U.FL / IPEX antenna
- clean Wi-Fi update path
- footprints for optional PA/LNA and filtering variants if needed

Use this one electrical platform to ship:

- OpenRX Nano-MF 2.4
- OpenRX Nano-MF 900
- OpenRX Nano-MF dual-band single-radio variant

Why:

- matches ELRS 4.0 band model directly
- lets one board cover the normal 2.4 and 900 SKUs
- reduces validation, firmware, tooling, and stock complexity
- positions you against RadioMaster XR3 and BETAFPV SuperX Mono rather than against old RP/EP commodity parts

### Platform B: premium receiver

Recommended architecture:

- ESP32-C3
- dual LR1121
- dual RF chains
- 2 x U.FL / IPEX
- 100 mW telemetry target
- strong TCXO / clock discipline

Use this platform to ship:

- OpenRX Gemini 2.4
- OpenRX Gemini 900
- OpenRX GemX dual-band

Why:

- it covers the premium 2.4, premium 900, and xrossband story with one board
- ELRS 4.0 now explicitly supports `X-Band` as a band choice and forces Gemini on dual-band rates
- this is the product that makes the brand look technically current

### Platform C: optional low-cost / integrated derivative

Recommended only if you need a very small and cheap 2.4 GHz product:

- ESP32-C3 or ESP8285 only if size / BOM absolutely force it
- SX1281
- no PA/LNA
- ceramic or single-U.FL variant

This is where the OpenFC ELRS design can help, after cleanup.

## What I would actually build first

Priority order:

1. OpenRX Nano-MF on ESP32-C3 + LR1121
2. OpenRX GemX on ESP32-C3 + dual LR1121
3. Only then decide whether a tiny SX1281 cost-down SKU is worth it

Reason:

- the cheapest tiny 2.4 GHz receivers are the hardest place to win
- the best opportunity is a cleaner, more unified LR1121 family
- ELRS 4.x momentum is clearly behind LR1121, not legacy ESP8285 + SX128x-only thinking

## Where OpenRX can beat the competition

Not by making yet another anonymous RP1/EP1 clone.

Better places to win:

- one PCB family instead of separate 2.4 and 900 mainstream boards
- better bring-up robustness: proper reset timing, supervisor options, sane boot/test access
- better documentation and sane net naming
- better RF serviceability: coax anchoring, antenna keepouts, tuning provisions
- better integration features on day one: CRSF, SBUS, SUMD, MAVLink, optional second UART where practical
- verified chip-antenna tuning instead of "copy a footprint and hope"
- better manufacturing discipline: approved target path, hardware.json cleanliness, published reference measurements

## LCSC sourcing signal

The LCSC snapshots I found point to this:

- ESP32-C3FH4 is easy to source from LCSC and shows healthy recent stock: [C2858491](https://www.lcsc.com/product-detail/C2858491.html)
- SX1281IMLTRT is listed and still available, but with much thinner stock than ESP32-C3 in the latest indexed result: [C2151551](https://www.lcsc.com/product-detail/C2151551.html)
- SX1276IMLTRT is listed and currently looks easier to source than LR1121: [C80171](https://www.lcsc.com/product-detail/C80171.html)
- LR1121IMLTRT is listed by LCSC as [C7498014](https://www.lcsc.com/product-detail/C7498014.html), but the latest indexed result I found showed only very low stock

Implication:

- building the whole line around LR1121 is still the right long-term move
- but before freezing the portfolio, validate LR1121 supply and lead time directly

## OpenFC ELRS receiver review

### Short verdict

The OpenFC ELRS section is directionally correct as a minimal 2.4 GHz serial receiver core, but it is not a production-ready standalone template as-is.

Use it as:

- a reference for a compact ESP32-C3 + SX1281 2.4 GHz receiver core
- a reference for FC-integrated / break-off ELRS

Do not use it as:

- the main future-proof OpenRX platform
- a direct copy-paste standalone production receiver without cleanup

### What is good

- It is already on ESP32-C3, not STM32 or only-legacy ESP8285.
- The ELRS radio path is a normal SX1281 2.4 GHz implementation with external ELRS antenna output through a filter.
- The ESP32 Wi-Fi path is separated onto its own Johanson chip antenna rather than trying to share the ELRS RF chain.
- Several issues from the older preproduction review are already fixed in the current PCB.

Evidence:

- SX1281 RF output is routed on `RFIO` into the filter path in [OpenFC.kicad_pcb](/Users/stan/Library/Mobile Documents/com~apple~CloudDocs/OpenFC/hardware/OpenFC.kicad_pcb#L16158)
- the external ELRS antenna connector is [OpenFC.kicad_pcb](/Users/stan/Library/Mobile Documents/com~apple~CloudDocs/OpenFC/hardware/OpenFC.kicad_pcb#L583)
- the ESP32-C3 Wi-Fi input uses the separate chip antenna path at [OpenFC.kicad_pcb](/Users/stan/Library/Mobile Documents/com~apple~CloudDocs/OpenFC/hardware/OpenFC.kicad_pcb#L38142)
- the ELRS LDO now has `EN` tied to `+5V` and `VOUT` to `+3.3V_ELRS` in [OpenFC.kicad_pcb](/Users/stan/Library/Mobile Documents/com~apple~CloudDocs/OpenFC/hardware/OpenFC.kicad_pcb#L8526)
- `C7` is now `470nF`, not the undersized value mentioned in the old review, in [OpenFC.kicad_pcb](/Users/stan/Library/Mobile Documents/com~apple~CloudDocs/OpenFC/hardware/OpenFC.kicad_pcb#L4602)
- the SX1281 `CS` pull-up exists as `R2 10k` in [OpenFC.kicad_pcb](/Users/stan/Library/Mobile Documents/com~apple~CloudDocs/OpenFC/hardware/OpenFC.kicad_pcb#L11180)

### What still needs improvement

#### 1. The ESP32-C3 `CHIP_EN` power-up network is weak

In the actual PCB netlist, `CHIP_EN` appears tied to:

- the ESP32-C3 `CHIP_EN` pin
- `R3` 10 k pull-up to `+3.3V_ELRS`
- `R26` 1 k link from the FC host-control net `/ELRS/ESP8285_EN`

I do not see the Espressif-recommended RC delay capacitor on that node.

Evidence:

- [OpenFC.kicad_pcb](/Users/stan/Library/Mobile Documents/com~apple~CloudDocs/OpenFC/hardware/OpenFC.kicad_pcb#L35891)
- [OpenFC.kicad_pcb](/Users/stan/Library/Mobile Documents/com~apple~CloudDocs/OpenFC/hardware/OpenFC.kicad_pcb#L21354)
- [OpenFC.kicad_pcb](/Users/stan/Library/Mobile Documents/com~apple~CloudDocs/OpenFC/hardware/OpenFC.kicad_pcb#L38187)
- Espressif explicitly recommends an RC delay, typically `10 kOhm + 1 uF`, on `CHIP_EN`: [ESP32-C3 Hardware Design Guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html)

Verdict:

- fine for a lab prototype if the power rail is well behaved
- not what I would carry forward unchanged into a standalone product

#### 2. The design is still FC-specific, not a clean standalone receiver

The enable / boot control and naming are still inherited from the FC integration:

- stale `/ELRS/ESP8285_EN` net name
- stale `ELRX_TX` naming in the schematic

Evidence:

- [OpenFC.kicad_sch](/Users/stan/Library/Mobile Documents/com~apple~CloudDocs/OpenFC/hardware/elrs.kicad_sch#L5228)
- [OpenFC.kicad_sch](/Users/stan/Library/Mobile Documents/com~apple~CloudDocs/OpenFC/hardware/elrs.kicad_sch#L5239)

Verdict:

- acceptable inside the FC project
- not acceptable as the template for a new receiver family

#### 3. It is a good 2.4 GHz SX1281 template, but not a future-proof portfolio template

OpenFC is architecturally a compact single-band 2.4 GHz receiver. That is useful, but ELRS 4.0's strategic direction is clearly broader:

- single-band 2.4
- single-band 900
- dual-band LR1121
- dual-radio Gemini / GemX

So OpenFC is a good branch of the tree, not the tree.

## Concrete recommendation on OpenFC reuse

Yes, you can use OpenFC as a template if the target is:

- a cheap 2.4 GHz serial receiver
- an FC-integrated receiver
- a break-off daughterboard

Before reuse, change at least:

1. Add proper `CHIP_EN` RC timing, or a reset supervisor.
2. Remove stale net names and FC-specific assumptions.
3. Add clean boot / flash / test pads for standalone manufacturing.
4. Add ESD review and pad protection review for external interfaces.
5. Re-check the Wi-Fi chip antenna keepout and tuning strategy if you change board outline.

If the target is the main OpenRX product family, start from a new LR1121 architecture instead.

## Final recommendation

If I were freezing the OpenRX plan today:

- main volume product: single-LR1121 ESP32-C3 receiver
- halo product: dual-LR1121 ESP32-C3 GemX receiver
- optional cheap derivative: SX1281 2.4 GHz receiver based loosely on OpenFC

That gives you a line that is compatible with how ELRS 4.0 actually behaves now, matches where the market is moving, and avoids getting trapped maintaining too many dead-end SKUs.
