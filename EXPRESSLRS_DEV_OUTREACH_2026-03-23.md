# ExpressLRS Developer Outreach — March 23, 2026

This note is for contacting the ExpressLRS core team about OpenRX hardware direction before target submission.

## Public Contact Paths

- Official contact page: https://www.expresslrs.org/contact-us/
- Official Discord invite: https://discord.gg/expresslrs
- General contact email: `info@expresslrs.org`
- Official target-review repo: https://github.com/ExpressLRS/targets

The `targets` repository explicitly says manufacturers should contact an ExpressLRS developer on Discord early in the design process.

## Public-Facing Core Maintainers I Could Verify

These are the people I could justify calling public-facing core maintainers from official release history and the local repository history. This is not a verified Discord staff list.

1. Paul Kendall
   - GitHub: `pkendall64`
   - Strongest current signal as a lead maintainer.
   - The local repository shortlog shows the highest all-time commit count.
   - The `4.0.0` tag points to a merge by Paul Kendall in the local tree.

2. Bryan Mayland
   - GitHub: `CapnBry`
   - Publicly visible long-time core contributor and release author presence.
   - High contributor count in the local repository.
   - Authored or directly drove part of the `4.0.0` RC cycle.

3. Jye Smith
   - GitHub: `JyeSmith`
   - Publicly visible long-time maintainer and major contributor.
   - Second-highest all-time contributor in the local repository shortlog.

4. Michael
   - GitHub: `mha1`
   - Publicly visible recent release-cycle contributor.
   - Shows up in `4.0.0` RC tags and recent `LR1121` fixes.

Secondary likely maintainer / hardware-relevant contributor:

- Cru Waller
  - GitHub: `cruwaller`

## Important Caveat On Discord Identities

I could verify the official ExpressLRS Discord server, but I could not verify individual Discord handles for the people above from public web sources alone.

So the safe recommendation is:

- join the official Discord
- post in the hardware / development area or ask moderators to point you to the right maintainer
- refer to the GitHub names above, not guessed Discord usernames

## Likely Discord Name Matches From Server Screenshot

Based on the server screenshot you provided, these are the strongest likely mappings:

- `PK` -> very likely Paul Kendall / `pkendall64`
- `maybenikhil` -> very likely Nikhil / `maybenikhil`
- `schugabe` -> very likely Johannes / `schugabe`
- `Mr tiger` -> likely `MUSTARDTIGERFPV`

These are plausible but not fully verified from public sources alone:

- `deadbyte` -> possibly `deadbytefpv`
- `Maveric`
- `Spec`

Recommendation:

- if you post publicly, tag `PK`, `maybenikhil`, and `schugabe`
- treat `Mr tiger` as likely relevant too
- do not rely on the weaker matches unless someone redirects you

## Recommended Outreach Message

Use this as a first contact message in Discord or by email:

> Hi ExpressLRS team, I’m working on an open-source receiver family called OpenRX and wanted to reach out before we lock hardware.
>
> We’ve reduced the plan to three products:
>
> - `Lite`: tiny `2.4GHz` `ESP32-C3 + SX1281`, ceramic-antenna-only
> - `Mono`: mainstream single-`LR1121` receiver with one `U.FL`, intended as the main multi-band board
> - `Gemini`: later premium `2x LR1121` GemX receiver
>
> We’re designing around current ExpressLRS `4.0` direction and want to make sure we align with the codebase and target-review expectations before we go further.
>
> The main things I’d like feedback on are:
>
> 1. whether a single-`LR1121` “Mono” receiver is the right mainstream hardware direction for ELRS `4.0`, versus keeping a separate `SX1281 + FEM` mainstream board
> 2. any strong preferences or gotchas for `LR1121` receiver pin mapping, `RFSW` usage, and single-radio target definitions
> 3. any guidance on what you want to see before an official target submission to the `targets` repo
> 4. whether there are known concerns around CE / LBT / dual-band hardware decisions we should design around from day one
>
> We’re happy to share schematics and early hardware files if that helps. I’d prefer to get alignment early instead of showing up with a nearly finished board that fights the ELRS direction.

## Shorter Version

> Hi, I’m developing an open-source ELRS receiver family and want early hardware feedback before target submission. Our current stack is `Lite (SX1281)`, `Mono (single LR1121)`, and later `Gemini (2x LR1121)`. Who on the ExpressLRS side is best to sanity-check receiver architecture, `LR1121` target expectations, and target-review requirements?

## Source Notes

- Official contact + Discord link came from the ExpressLRS contact page.
- The recommendation to contact developers on Discord early came from the official `ExpressLRS/targets` repository README.
- Maintainer ranking came from the local `ExpressLRS` git history and the public GitHub release history.
