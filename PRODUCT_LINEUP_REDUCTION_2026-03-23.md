# Product Lineup Reduction — March 23, 2026

Current OpenRX concepts are over-segmented for a first release. The market is converging on a much smaller receiver ladder, and ExpressLRS 4.0 makes `LR1121` materially more attractive than it was in 3.x.

## Executive Decision

Do not launch six or seven receiver SKUs.

Recommended launch plan:

1. `Lite`
   - Tiny, cheapest, 2.4 GHz only, ceramic antenna, whoop/micro target.
   - Keep this because the market still buys ultra-small dedicated 2.4 receivers.

2. `Mono`
   - Single `LR1121`, single-U.FL mainstream receiver.
   - This should replace separate `900` and `Dual` first-wave products.
   - It should be configurable as `2.4`, `868/915`, or dual-band-antenna switchable by antenna/accessory choice, not by maintaining multiple near-identical boards.

3. `Gemini`
   - True premium `2x LR1121` GemX / Gemini board.
   - Keep only if you want a flagship or halo product.

Pause or drop for now:

- `Nano` as a separate `SX1281 + FEM` product
- `900` as a separate single-band board
- `Dual` as a separate board if it remains distinct from a simpler `Mono`
- `PWM`

## Why This Is The Right Cut

## 1. The market already compressed

RadioMaster's current receiver ladder is effectively:

- `XR2`: tiny dedicated `2.4 GHz`
- `XR1`: single `LR1121`, single antenna, multi-frequency
- `XR3`: diversity / higher-end single `LR1121`
- `DBR4`: dual `LR1121` GemX / Gemini

That is not six unrelated receivers. It is a compact ladder with one tiny board, one mainstream board, and one premium board.

BETAFPV's newer line is even more explicit:

- `SuperX Mono`: single `LR1121`, `900M/2.4G`
- `SuperX Nano`: dual `LR1121`, `900M+2.4G`

That is the same strategic pattern.

Inference: the market wants fewer receiver families with clearer steps up in capability, not separate boards for every band permutation.

## 2. ExpressLRS 4.0 shifts value toward LR1121

ExpressLRS `4.0.0` was released on `February 6, 2026`, and the highlights matter directly to receiver product strategy:

- expanded `LR1121` packet modes
- `K1000` / `DK500` class modes
- better dynamic power behavior for `LR1121`
- improved Gemini telemetry behavior
- automatic antenna-mode syncing

Your local ExpressLRS tree is already on `4.0.0-55-ga96f13dd`, and the codebase clearly treats `LR1121` dual-band / Gemini as first-class:

- [common.cpp](/Users/stan/Documents/GitHub/ExpressLRS/src/src/common.cpp)
- [TXModuleParameters.cpp](/Users/stan/Documents/GitHub/ExpressLRS/src/lib/tx-crsf/TXModuleParameters.cpp)
- [Unified_ESP_RX.h](/Users/stan/Documents/GitHub/ExpressLRS/src/include/target/Unified_ESP_RX.h)

Inference: a mainstream first-wave board should be `LR1121`-based, not another dedicated `SX1281` variant unless the entire point is minimum size/cost.

## 3. Your current OpenRX overlap is mostly artificial

Today the main overlaps are:

- `Lite` vs `Nano`: both are `2.4 GHz`
- `900` vs `Dual`: both are single-`LR1121` products covering the same long-range / multi-band buyer story
- `Gemini` is a real separate premium concept
- `PWM` is a niche concept, but not part of the current release stack

That means the natural reduction is:

- keep `Lite`
- merge `900` + `Dual` into `Mono`
- keep `Gemini`
- leave `PWM` out for now

## Recommended Product Ladder

## Tier 1: `Lite`

Target:

- whoops
- micro quads
- lowest cost
- smallest physical envelope

Why it survives:

- RadioMaster still sells `XR2`
- this segment values size and simplicity more than band flexibility

## Tier 2: `Mono`

Target:

- mainstream 3" to 7" quads
- general-purpose receiver buyers
- EU / FCC regional flexibility
- users who do not want to commit to one band forever

What it should be:

- single `LR1121`
- single U.FL
- one clean accessory / antenna strategy
- firmware and marketing centered on `2.4 or 900 on one hardware platform`

Why this should replace `900` and `Dual`:

- fewer SKUs
- simpler certification story
- stronger alignment with ELRS 4.0
- more future-proof than a dedicated `SX1281 + FEM` mainstream board

## Tier 3: `Gemini`

Target:

- premium pilots
- noisy RF environments
- mountain surfing / long-range / critical-link users

Why it survives:

- it is genuinely different hardware
- it matches where ExpressLRS GemX support is going
- competitors already use it as a flagship step-up product

## What To Do In This Repo

Short term:

- continue routing `Lite`
- use the transferred `OpenRX-Mono` project as the active single-`LR1121` board
- keep `900` only as archived RF reference material
- do not spend more roadmap energy on `Nano` until a future `Mono` vs `Nano` decision is explicit

Recommended first two releases:

1. `Lite`
2. `Mono` (not separate `900` plus `Dual`)

Recommended full but lean portfolio:

1. `Lite`
2. `Mono`
3. `Gemini`

## Sources

- ExpressLRS 4.0 release: https://github.com/ExpressLRS/ExpressLRS/releases/tag/4.0.0
- RadioMaster XR1: https://www.radiomasterrc.com/products/xr1-nano-multi-frequency-expresslrs-receiver
- RadioMaster XR2: https://www.radiomasterrc.com/products/xr2-nano-2-4ghz-expresslrs-receiver
- RadioMaster XR3: https://radiomasterrc.com/products/xr3-nano-multi-frequency-antenna-diversity-expresslrs-receiver
- RadioMaster DBR4: https://radiomasterrc.com/products/dbr4-dual-band-xross-gemini-expresslrs-receiver
- BETAFPV SuperX: https://betafpv.com/products/superx-elrs-gemini-xross-receiver
- GEPRC ELRS Nano Receiver: https://geprc.com/product/geprc-elrs-nano-receiver/
