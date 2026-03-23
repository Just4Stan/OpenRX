# Mono / Gemini Topology Research

Date: 2026-03-23

Purpose: compare current ELRS Mono and Gemini receiver topologies, cross-check them against the current ExpressLRS firmware/target model, and recommend the right OpenRX `Mono` and `Gemini` hardware direction.

## Executive Summary

The current market has mostly converged on three distinct product types:

- `Mono`: one `LR1121`, one `U.FL`, one dual-band antenna, band-switching between `2.4GHz` and `868/915MHz`
- `Gemini`: two `LR1121`, two `U.FL`, two dual-band antennas, true dual-chain Gemini / GemX
- `Diversity`: one `LR1121`, two antennas, switched antenna diversity on a single radio chain

The important conclusion is that `Mono` and `Gemini` are not the same board scaled up or down. A good `Mono` is not a crippled Gemini, and a good `Gemini` is not just “Mono plus one more chip”.

For OpenRX, the clean recommendation is:

- `OpenRX-Mono`: one `LR1121`, one shared dual-band antenna path, one `U.FL`, one dual-band antenna
- `OpenRX-Gemini`: two complete dual-band RF chains, two `U.FL`, two dual-band antennas
- do **not** make `Mono` into an `XR3`-style diversity board unless you intentionally add a separate diversity SKU later
- do **not** copy the older `DBR4` four-antenna topology unless you deliberately want a larger legacy-style board

## What The Market Ships Now

### 1. Single-Radio Mono

Current mainstream Mono products use:

- `ESP32-C3`
- one `LR1121`
- one `U.FL`
- one antenna, sold either as `2.4`, `900`, or dual-band

Examples:

- RadioMaster `XR1`:
  - `ESP32C3`
  - `Semtech LR1121`
  - `IPEX-1`
  - `1x T-Antenna`
  - `2.4GHz or Sub-G 900MHz`
  - `100mW telemetry`
  - secondary UART exposed
  - source: <https://radiomasterrc.com/products/xr1-nano-multi-frequency-expresslrs-receiver>
- BETAFPV `SuperX Mono`:
  - `ESP32-C3`
  - `Single LR1121`
  - `U.FL x1`
  - `900M/2.4G`
  - explicitly described as a `band-switching` receiver with a `dual-band antenna`
  - source: <https://betafpv.com/products/superx-elrs-gemini-xross-receiver>

This is the clearest current mainstream pattern.

### 2. Single-Radio Diversity

RadioMaster `XR3` is not a Mono and not a Gemini. It is:

- `ESP32C3`
- one `LR1121`
- `IPEX-1 x2`
- `2x` antennas
- antenna diversity on one radio chain

Source: <https://radiomasterrc.com/products/xr3-nano-multi-frequency-antenna-diversity-expresslrs-receiver>

This matters because it proves there is a valid market for `one LR1121 + two antennas`, but that is a separate product category. If OpenRX ever wants that, it should be a future `Diversity` SKU, not the default `Mono`.

### 3. Modern Gemini / GemX

Current premium Gemini products use:

- `2x LR1121`
- `2x U.FL`
- `2x` dual-band antennas
- true dual-chain Gemini / GemX operation

Examples:

- RadioMaster `XR4`:
  - `ESP32D4`
  - `LR1121 x 2`
  - `IPEX-1 x 2`
  - `Dual-Band T Antenna x 2`
  - secondary UART
  - source: <https://radiomasterrc.com/products/xr4-gemini-xrossband-dual-band-expresslrs-receiver>
- BETAFPV `SuperX Nano`:
  - `ESP32-C3`
  - `Dual LR1121`
  - `U.FL x2`
  - `900M+2.4G`
  - explicitly positioned as the Gemini / GemX board
  - source: <https://betafpv.com/products/superx-elrs-gemini-xross-receiver>

This is where the market is heading now.

### 4. Older Four-Antenna Gemini

RadioMaster `DBR4` is the older pattern:

- dual-band Gemini / GemX
- `4 discrete antennas`
- larger board / more legacy topology

Source: <https://radiomasterrc.com/products/dbr4-dual-band-xross-gemini-expresslrs-receiver>

That design still works, but the newer `XR4` pattern is clearly cleaner:

- `2` antennas instead of `4`
- each antenna is dual-band
- less external antenna clutter
- smaller end product

So for a new design, `DBR4` is a legacy reference, not the topology to copy.

## What ExpressLRS Actually Expects

The local ExpressLRS code and the official targets repo are aligned around a fairly clean `LR1121` hardware model.

### 1. ELRS Supports Mono and Gemini As Different Hardware Contracts

From the local code:

- [Unified_ESP_RX.h](/Users/stan/Documents/GitHub/ExpressLRS/src/include/target/Unified_ESP_RX.h)
- [rx_main.cpp](/Users/stan/Documents/GitHub/ExpressLRS/src/src/rx_main.cpp)
- [common.cpp](/Users/stan/Documents/GitHub/ExpressLRS/src/src/common.cpp)
- [LR1121.cpp](/Users/stan/Documents/GitHub/ExpressLRS/src/lib/LR1121Driver/LR1121.cpp)
- [LR1121_hal.cpp](/Users/stan/Documents/GitHub/ExpressLRS/src/lib/LR1121Driver/LR1121_hal.cpp)

Important points:

- `radio_dio1` on `LR1121` means the IRQ line, so it maps to physical `DIO9`
- physical `DIO1` remains `SPI NSS`
- single-radio `LR1121` receivers can bind and switch between `900` and `2.4`
- dual-radio receivers are first-class citizens: `radio_nss_2`, `radio_busy_2`, `radio_dio1_2`, optionally `radio_rst_2`
- ELRS supports separate `power_values` and `power_values_dual` for low-band and high-band behavior

### 2. ELRS Already Expects LR1121-Driven RF Switch Logic

`LR1121.cpp` includes explicit `SetDioAsRfSwitch()` handling and an 8-state `radio_rfsw_ctrl` model. That is the strong signal from the codebase:

- `Mono` and `Gemini` LR1121 designs should prefer `LR1121` DIO-driven RF switch / FEM truth tables
- do **not** model LR1121 RF switching like an `SX1281 + MCU TXEN/RXEN` design

### 3. Official Targets Show Multiple RF Front-End Truth Tables

The current official targets repo does not assume one universal LR1121 front-end. Different vendors already use different `radio_rfsw_ctrl` values:

- BETAFPV `SuperX Nano` and `SuperX Mono`
- BrotherHobby dual-band `C3` Gemini
- BAYCKRC dual-band `C3` Gemini
- DakeFPV `GemX`

Source: <https://github.com/ExpressLRS/targets/blob/master/targets.json>

That means there really are multiple front-end topologies in the wild. The core ELRS pin contract is stable, but the RF truth table around each `LR1121` can vary.

### 4. C3 Is Enough For Compact Mono And Compact Gemini

Official targets already prove this:

- `BETAFPV SuperX Mono` uses `Generic C3 LR1121.json`
- `BETAFPV SuperX Nano` uses `Generic C3 LR1121 True Diversity.json`
- both are `esp32-c3` targets

Source: <https://github.com/ExpressLRS/targets/blob/master/targets.json>

The generic target files are especially useful:

- `Generic C3 LR1121.json` includes `led_rgb`, `button`, and the LR1121 radio interface
  - source: <https://github.com/ExpressLRS/targets/blob/master/RX/Generic%20C3%20LR1121.json>
- `Generic C3 LR1121 True Diversity.json` includes dual-radio pins plus `led_rgb` and `button`
  - source: <https://github.com/ExpressLRS/targets/blob/master/RX/Generic%20C3%20LR1121%20True%20Diversity.json>

So the answer to “do we need more MCU GPIO just to keep a button and RGB LED?” is:

- `Mono`: no, `ESP32-C3` is fine
- `Gemini`: `ESP32-C3` is still fine if you keep the feature set disciplined

### 5. S3 Shows Up When The Product Wants Lots Of Extra I/O

The official `BlackSheep IP YB-Diversity Dual Band RX` target uses:

- `Generic S3 LR1121 True Diversity.json`
- `esp32-s3`
- many `pwm_outputs`
- `i2c_sda/i2c_scl`
- RGB LED indexing

Source: <https://github.com/ExpressLRS/targets/blob/master/targets.json>

That is the clearest current evidence that `S3` is not required for Gemini itself. It is used when the product wants lots of auxiliary features.

## RF Architecture: What Is Actually Different Between Mono And Gemini

### Mono

A good Mono board should be:

- one `LR1121`
- one sub-GHz front-end path
- one 2.4GHz front-end path
- one shared antenna output
- one dual-band antenna

The real engineering question is how to combine sub-GHz and 2.4GHz onto that one antenna path.

Current products strongly imply a shared dual-band antenna architecture, but they do not publish full RF schematics. So this part is an engineering inference from:

- `XR1` and `SuperX Mono` both shipping as one-radio, one-connector, dual-band products
- ELRS targets using `radio_rfsw_ctrl` on `LR1121`
- `LR1121` having separate LF and HF RF ports

The two realistic approaches are:

- passive band combiner / diplexer after separate LF and HF conditioning
- active RF switching / muxing between LF and HF into one antenna

My recommendation for `Mono` is:

- prefer a clean shared-antenna dual-band topology
- prefer the simpler, more repeatable topology over maximum cleverness
- do **not** expose separate `900` and `2.4` external connectors on the mainstream product

### Gemini

A good Gemini board should be:

- `2x LR1121`
- each radio chain capable of full dual-band behavior
- `2x` antenna connectors
- `2x` dual-band antennas

This is the modern `XR4` / `SuperX Nano` pattern.

What that means in practice:

- each chain should look like a small dual-band receiver chain, not like a single-band chain
- avoid “one radio dedicated to 900, the other dedicated to 2.4” if your goal is the most flexible modern GemX product
- keep both chains symmetric where possible

That symmetry matters for:

- RF behavior
- firmware assumptions
- calibration / power table sanity
- certification repeatability

## CE Implications

The CE-safe answer is not “copy the board with the most antennas”. It is “choose the topology that gives repeatable RF states with the fewest unnecessary RF variables”.

### Mono

For CE, the best Mono product is usually:

- one connector
- one dual-band antenna SKU
- one clear LF chain
- one clear HF chain
- one well-defined shared antenna topology

This is simpler commercially too:

- one main receiver SKU
- fewer antenna/package combinations
- easier documentation

### Gemini

For CE, a modern two-chain Gemini is preferable to the older four-antenna style because:

- fewer exposed antennas/connectors
- cleaner end-user install
- lower packaging complexity
- closer alignment with the current premium market direction

The board is still more complex than Mono, but it is cleaner than a `DBR4`-style four-antenna product.

### 2.4GHz Front-End Risk

If you want `20dBm / 100mW` class marketing parity on the high-frequency side, you are likely still in external front-end territory, not “bare LR1121 only”.

That means:

- `Mono` with HF PA/FEM is more market-competitive
- `Mono` without HF PA/FEM is easier to certify but will not match current `100mW` Mono marketing

So the real tradeoff is:

- `simpler CE path`
- versus
- `parity with XR1 / SuperX Mono class products`

For OpenRX, I would choose parity for `Mono`, but only if the HF path is kept disciplined and measured properly.

## Recommended OpenRX Direction

### OpenRX-Mono

Recommended topology:

- `ESP32-C3`
- `1x LR1121`
- keep `button` and `RGB LED`
- keep one extra UART if you want the `XR1` / premium-Mono style feature set
- `1x U.FL`
- `1x` dual-band antenna
- LF front-end:
  - use the proper `LR1121` sub-GHz matched IPD or a faithful discrete network
- HF front-end:
  - keep a proper 2.4GHz front-end if the goal is `100mW` class parity
- control RF states from `LR1121` via `radio_rfsw_ctrl`

What to avoid:

- do not keep the current inherited “separate 900 connector + separate 2.4 connector” concept as the release Mono
- do not turn Mono into a diversity board by default

### OpenRX-Gemini

Recommended topology:

- `ESP32-C3` is acceptable for the compact flagship if features are disciplined
- `2x LR1121`
- shared SPI, separate `NSS/BUSY/DIO9`, ideally separate resets
- `2x U.FL`
- `2x` dual-band antennas
- each chain should be a full dual-band chain
- keep `RGB LED` and `button` only if they fit cleanly in the chosen pin map
- if you want more than that:
  - second aux UART
  - lots of sensors
  - PWM outputs
  - richer status I/O
  - move to `ESP32-S3` or a roomier `ESP32` class MCU

What to avoid:

- do not copy `DBR4`’s four-antenna layout as the default 2026 flagship pattern
- do not build Gemini as one fixed `900` chain plus one fixed `2.4` chain if the goal is modern GemX flexibility

### Diversity As A Future Optional SKU

If OpenRX later wants a fourth product:

- `OpenRX-Diversity`
- `1x LR1121`
- `2x` antennas
- one-radio antenna diversity

That would be the `XR3` category.

It should stay separate from both:

- `Mono`
- `Gemini`

## MCU Recommendation

### Mono

Use `ESP32-C3`.

Why:

- market-proven in `XR1` and `SuperX Mono`
- official targets already support the generic Mono pattern on `C3`
- enough GPIO headroom for:
  - CRSF UART
  - LR1121 interface
  - RGB LED
  - button
  - one additional aux serial function if budgeted carefully

### Gemini

Use `ESP32-C3` if the goal is:

- compact flagship
- CRSF + Wi-Fi OTA + button + RGB
- no large auxiliary I/O set

Use `ESP32-S3` or a roomier `ESP32` if the goal is:

- extra UARTs
- PWM
- I2C accessories
- richer LEDs / UX
- feature-heavy premium board

## What This Means For The Current OpenRX Schematics

### OpenRX-Mono

The current inherited `OpenRX-Mono` concept still behaves more like a split-path lab/reference board than a finished mainstream Mono product.

What should change:

- collapse the current separate external RF outputs into one shared dual-band antenna output
- keep the `LR1121` as the only radio
- keep `ESP32-C3`
- keep `button` and `RGB LED`
- keep one auxiliary UART only if it still fits cleanly after the final pin map is frozen
- keep the RF state machine centered on `radio_rfsw_ctrl`

What should not change:

- do not move away from `LR1121`
- do not add a second radio
- do not convert it into an `XR3`-style diversity board by default

### OpenRX-Gemini

The current `OpenRX-Gemini` direction should become a fully symmetric modern dual-chain design.

What should change:

- make sure both radio chains are genuinely dual-band chains
- keep `2x LR1121`
- keep `2x U.FL`
- keep `2x` dual-band antennas as the default topology
- keep chain symmetry wherever possible

What should not change:

- do not fall back to the old four-antenna `DBR4` style
- do not specialize one chain as “the 900 radio” and the other as “the 2.4 radio” unless you intentionally give up the cleaner modern Gemini pattern
- do not jump to `ESP32-S3` unless you add enough auxiliary features to justify it

## Bottom Line

If OpenRX wants the best 2026 topology choices:

- `Mono` should follow the `XR1 / SuperX Mono` category:
  - one `LR1121`
  - one `U.FL`
  - one dual-band antenna
  - one shared dual-band RF output path
- `Gemini` should follow the `XR4 / SuperX Nano` category:
  - two `LR1121`
  - two `U.FL`
  - two dual-band antennas
  - two symmetric dual-band chains

The current market is moving away from:

- `ESP8285`
- older four-antenna Gemini layouts
- fragmented single-band receiver families

The current market is moving toward:

- `LR1121` everywhere important
- compact `ESP32-C3` designs
- one mainstream `Mono`
- one premium `Gemini`
- dual-band antennas instead of multiplying antenna count

## Sources

- Local ExpressLRS code:
  - [Unified_ESP_RX.h](/Users/stan/Documents/GitHub/ExpressLRS/src/include/target/Unified_ESP_RX.h)
  - [rx_main.cpp](/Users/stan/Documents/GitHub/ExpressLRS/src/src/rx_main.cpp)
  - [common.cpp](/Users/stan/Documents/GitHub/ExpressLRS/src/src/common.cpp)
  - [LR1121.cpp](/Users/stan/Documents/GitHub/ExpressLRS/src/lib/LR1121Driver/LR1121.cpp)
  - [LR1121_hal.cpp](/Users/stan/Documents/GitHub/ExpressLRS/src/lib/LR1121Driver/LR1121_hal.cpp)
- Official ExpressLRS targets repo:
  - <https://github.com/ExpressLRS/targets/blob/master/targets.json>
  - <https://github.com/ExpressLRS/targets/blob/master/RX/Generic%20C3%20LR1121.json>
  - <https://github.com/ExpressLRS/targets/blob/master/RX/Generic%20C3%20LR1121%20True%20Diversity.json>
- Official product pages:
  - <https://radiomasterrc.com/products/xr1-nano-multi-frequency-expresslrs-receiver>
  - <https://radiomasterrc.com/products/xr3-nano-multi-frequency-antenna-diversity-expresslrs-receiver>
  - <https://radiomasterrc.com/products/xr4-gemini-xrossband-dual-band-expresslrs-receiver>
  - <https://radiomasterrc.com/products/dbr4-dual-band-xross-gemini-expresslrs-receiver>
  - <https://betafpv.com/products/superx-elrs-gemini-xross-receiver>
- Local datasheets:
  - [LR1121_datasheet.pdf](/Users/stan/Library/Mobile%20Documents/com~apple~CloudDocs/OpenRX/datasheets/common/LR1121_datasheet.pdf)
  - [LR1121_user_manual.pdf](/Users/stan/Library/Mobile%20Documents/com~apple~CloudDocs/OpenRX/datasheets/common/LR1121_user_manual.pdf)
  - [RFX2401C_datasheet.pdf](/Users/stan/Library/Mobile%20Documents/com~apple~CloudDocs/OpenRX/datasheets/common/RFX2401C_datasheet.pdf)
  - [ESP32-C3FH4_datasheet.pdf](/Users/stan/Library/Mobile%20Documents/com~apple~CloudDocs/OpenRX/datasheets/common/ESP32-C3FH4_datasheet.pdf)
