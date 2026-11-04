# Skill: Re-baselining against the ACoT base mod

## When to use
When the **base ACoT mod** ("Ancient Cache of Technologies", Steam Workshop
`1419304439`) updates, the files this fork overrides may have changed underneath
us. Re-run this to find out **what actually diverged** and decide what to fix.

This is the same job as "the food-producing building that cannot be upgraded to
sigma tier": a building whose `upgrades = { ... }` chain points at a tier
definition the base no longer provides (or that we renamed/removed). The tool
and method below are the general version of that one-off fix.

## CRITICAL context — read first
This repo is a **Phanon-integration fork**, not a stale copy of ACoT. Divergence
from the base is usually **deliberate design**, not drift.

- The base is named `name = "Ancient Cache of Technologies"` and is identified
  by `remote_file_id = "1419304439"`. Its `.mod` file is generically named
  `descriptor.mod` — **do NOT detect the base by filename**; match the name/id.
- Many things look like "we're missing X" but are **DRY refactors**: the base
  inlines a tier's logic into a big block; we replaced it with a parameterised
  inline script (`script = { ... }` or `script = buildings/...`). The *values*
  are the same, just expressed differently. **Do not re-add the inlined block.**
- Example of a **known, intended** delta (do not "fix" this): `acot_star_annihilator`
  is **unlocked in our fork, locked in the base**. The only token difference is
  the `always` gate. Leaving it alone is correct.

## The decision rule (the whole point)
For every definition that exists in **both** trees, ask:

> **Did the base add a top-level capability (a column-0 `key =` we lack)?**

- **YES** → real structural gap. This is what to fix (e.g. base added an
  `upgrades`/`building_sets`/`cost` tier our override dropped). Compare the two
  blocks, then port the new key/values **into our override style** (parameterise
  rather than paste the inlined block, to stay consistent with the fork).
- **NO** → almost certainly a DRY-refactor false-positive or value-tuning.
  **Leave it** unless a specific value is wrong.

The reason: token-level diffs flag every *value* and every *name inside inline
scripts* as "missing", which drowns real gaps. A **top-level key-name diff**
does not — it only fires when the base genuinely added a new definition-level
field. This is the single most reliable signal.

## How to run
Durable tool: **`tools/acot_overlap_check.py`** (Python 3, no deps).

```bash
# Full report; base auto-detected by remote_file_id, ours defaults to the repo folder.
python tools/acot_overlap_check.py

# Machine-readable (drives CI / diffing between base versions).
python tools/acot_overlap_check.py --json

# Deep-dive one definition (shows the key diff + both token sets).
python tools/acot_overlap_check.py --key acot_star_annihilator

# Non-default locations.
python tools/acot_overlap_check.py --ours ./acquistion_of_technology \
    --acot "D:/SteamLibrary/steamapps/workshop/content/281990/1419304439"
```

Exit code: `0` if the base was found and scanned (even if it reports gaps).

### Output tiers
- **TIER 1a — structural key gap (review first):** base uses a top-level key we
  don't. *This is where real regressions live.* In the current tree this is
  **0**, i.e. the fork is not missing any capability the base defines.
- **TIER 1b — divergent (usually false positives):** token/value differences only.
  These are the DRY-refactor / tuning noise. Skim; only act if a value is wrong.
- **`ours_only` / `acot_only` (top of report):** definitions present in only one
  side. Expected — we add Phanson buildings; the base has its own. Not an error.
- **counts:** `identical` / `we_have_more` / `acot_has_more` / `divergent`.

## The method, decomposed (if you must inspect by hand)
1. **Parse column-0 definitions.** A definition is a line at **column 0**
   matching `name =`. Its extent is balanced by counting `{`/`}`. Lines indented
   under a block are *content*, not definitions (e.g. `component_set`, nested
   `zone` sub-blocks must not be treated as override targets).
2. **Key both trees by definition name** and take the intersection — that is the
   set of "overridden" definitions.
3. **Classify each pair** (base vs ours), in order:
   - `acot_only_keys = top_keys(base) - top_keys(ours)` → non-empty = **structural gap**.
   - else if base has non-script tokens we lack → `acot_has_more` (may still be refactor).
   - else if base has only in-script differences → `acot_superset` (refactor; leave).
   - else if we have tokens base lacks → `we_have_more` (our additions; fine).
   - else → `identical`.
4. **Resolve `script =`.** `script = { ... }` and `script = buildings/...` both
   hide real content. Token-diffs must strip inline `script` bodies before
   comparing, or they misreport. (See `strip_inline_scripts`.)

## Gotchas
- **Folder name is `acquistion_of_technology`** (the repo's "Acquistion" spelling),
  not `acquisition_...`. The default already accounts for this.
- **Binary/media files** (`gfx`, `.dds`-related `.txt` settings) get scanned as
  text and can produce noisy `divergent` rows (e.g. `gfx_settings`). They are not
  "code" overrides; ignore them.
- **Do not merge "stale" lines** just because the base file has them. Verify each
  against the decision rule before porting. The base's extra lines are frequently
  the pre-refactor form of what we already express.
- **`upgrades = { ... }` chains are the concrete symptom** of the original bug:
  an `upgrades` entry naming a tier definition that is `acot_only` (only in the
  base) or missing from **our** tree means an upgrade path is broken. (Note: the
  field is `upgrades`, **not** `upgrade_to` — `upgrade_to` appears only as a
  decision flag like `acot_upgrade_to_delta_building`, never as a building
  upgrade link. Both trees use `upgrades`: base 74 uses, ours 112.) Check the
  terminal `upgrades` target of each building chain when chasing
  "cannot upgrade to sigma tier".

## Checklist when the base updates
1. `python tools/acot_overlap_check.py --json > .scratch/acot_base_<date>.json`
2. Diff against the previous JSON (counts + per-def class) — the delta *is* the
   base's changes.
3. Work **TIER 1a** top-down: for each, confirm intent, port the new key into our
   override style, re-run.
4. Spot-check **TIER 1b** only for values that look semantically wrong.
5. Verify every `upgrades = { ... }` entry names a definition that exists in
   **our** tree (a target present only in the base = broken upgrade path).
6. Re-run; confirm TIER 1a returns to the expected baseline.

## Status of this tree (as of the Phanson fork)
- TIER 1a (structural key gaps): **0**
- TIER 1b (divergent, noise): **~304** (all DRY-refactor / tuning)
- Known intended delta: `acot_star_annihilator` unlocked here vs. locked in base.
- Conclusion: the fork is **not** missing a base capability; apparent "gaps" are
  deliberate Phanon design, not drift to be reverted.
