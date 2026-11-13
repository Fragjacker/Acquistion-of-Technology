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
- **on_action `events` lists are subscribers, NOT override lists.** Every mod's
  list for the same on_action is *unioned* at runtime (dispatchers accumulate
  subscribers across all loaded mods). So if the base already subscribes one of
  its own events in *its* `common/on_actions/*.txt`, we must NOT add it to our
  list either — that is a duplicate listener and the event fires twice. The
  overlap tool cannot model this accumulation, so for on_actions defs a
  "missing" base event in `acot_only_raw` often means **the base self-subscribes
  and there is nothing to merge** (2026-11-13: `acot_mega.100`). Always check
  the base's own on_actions files first; prefer "base already handles it".

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
- **`on_action` event blocks ACCUMULATE — never merge into them.** An
  `events = { ... }` list under an `on_action` (e.g. `on_megastructure_upgraded`)
  is a **subscriber dispatcher**: the game merges the lists of *all* loaded
  mods, and each subscriber fires once. Appending an event the base mod already
  subscribes (e.g. `acot_mega.100`, already subscribed in the base's own
  `common/on_actions/acot_on_actions.txt`) creates a **duplicate listener** —
  the event would fire twice. So the "whole-list replacement" fear does NOT
  apply to on_actions: a token that is `acot_only_raw` in an on_actions `events`
  list is **base already handles it — leave it alone, do NOT add it to ours**.
  (This is the exact opposite of the scripted-trigger case below.)
- **Whole-list keys in scripted triggers / zones ARE silent replacements.** For
  normal `scripted_trigger` `OR` lists
  (`ship_uses_titan_reactors`) and zone `potential`/`unlock` blocks, our
  definition fully replaces the base's, so when the base **adds an entry**
  (new ship size, new requirement) that entry silently disappears unless we
  append it too. Treat added tokens inside those list blocks as real changes
  even though no top-level key changed. **on_actions `events` lists are the
  exception** — see the gotcha above.
- **Name collisions ≠ same definition.** Two mods can define the *same key name*
  with different intent (observed: `ship_section_template` — base's arkship
  entry vs our BATTLESTATION entry; the checker pairs them by name and reports a
  divergence). Before acting on any diff, confirm the paired blocks are the
  *same semantic object* (same ship/building/zone), not just the same key.
- **Inline scripts are the merge point for modifiers.** If the base added a
  `triggered_country_modifier` (or similar) to a building whose modifiers we
  express via `inline_script = { script = buildings/... }`, port it **into the
  inline script**, not into each building block. One edit then covers every tier
  that shares the script (e.g. `buildings/civilian/resource_silo` feeds the AE,
  Phanon, and Stellarite silos).
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
7. **Commit the rebaseline edits immediately** on the branch the user is
   working (ideally `main`) — uncommitted rebaseline work is lost when a
   non-descendant branch is checked out and resurfaces as a phantom "base
   change" on the next scan (see 2026-11-13 log entry).

## Status of this tree (as of the Phanson fork)
- TIER 1a (structural key gaps): **0**
- TIER 1b (divergent, noise): **~304** (all DRY-refactor / tuning)
- Known intended delta: `acot_star_annihilator` unlocked here vs. locked in base.
- Conclusion: the fork is **not** missing a base capability; apparent "gaps" are
  deliberate Phanon design, not drift to be reverted.

## Rebaseline log
### 2026-11-10 (base scan 1105 → 1110): 6 merges applied
1. `acot_star_annihilator` (`z_aot_ship_size_override.txt`): added base's 8
   `required_component_set` lines (power_core, 2× ftl, 2× thruster, 2× sensor,
   combat_computers, 2× ship_aura).
2. `building_acot_ae_resource_silo`: base added two
   `triggered_country_modifier`s (`is_nomadic` →
   `situation_nomad_economy_max_progress_add = 10000`; `civic_machine_obsessional_directive`
   → `country_resource_max_consumer_goods_add = 100000`). Ported into our shared
   inline script `common/inline_scripts/buildings/civilian/resource_silo.txt`,
   which also covers the Phanon/Stellarite silos.
3. `has_enigmatic_capital` / `has_ascended_capital`
   (`z_aot_scripted_triggers_buildings.txt`): added base's
   `hidden_trigger = { exists = owner }` guard.
4. `on_megastructure_upgraded` (`aot_on_actions.txt`): base's new `acot_mega.100`
   subscriber appeared in `acot_only_raw`. **MISTAKE — merged it into our
   `events` list, which created a duplicate listener** (see the 2026-11-13
   entry: on_action `events` lists accumulate across loaded mods; the base
   already subscribes it in its own on_actions file). This line was later
   removed.
5. `ship_uses_titan_reactors` (`z_aot_scripted_triggers_override.txt`): added
   `paladin_ship` plus `large_fallen_stinger` / `cosmo_crisis_stinger` from the
   base OR-list (whole-list replacement!).
6. `zone_acot_ae_urban` / `zone_acot_dm_urban`
   (`z_acot_vanilla_zones_override.txt`): base removed the
   `unlock = { hidden_trigger = { owner is_wilderness_empire = no } }` exclusion;
   we dropped it too (previously a known intended delta — now aligned with base).
**False positive, NOT merged:** `ship_section_template` — the checker paired the
base's arkship section with our BATTLESTATION section by key name alone. Different
ships; both intentionally keep their own definition.

## 2026-11-13 ACoT base update check

Base mod reported as "just updated" (workshop files dated Nov 11–12, post-dating
the Nov 10–11 rebaseline; it added the DM citadel chain and `acot_mega.100`
which upgrades `starbase_dm_base` → `starbase_citadel_dm`). Fresh scan
(`acot_base_20261113.json`) vs. the **post**-rebaseline baseline: 350 defs,
0 added, 0 removed, exactly **one** changed def — `on_megastructure_upgraded`
gained `acot_mega.100` in `acot_only_raw`.

**First wrong fix (commit `1e38150e`):** I read that delta as "a rebaseline
merge of ours was lost" and re-added `acot_mega.100` to our `events` list.

**Real cause (user correction):** on_action `events` lists are **subscriber
accumulators** — the game unions the list from every loaded mod. Base
*already* subscribes `acot_mega.100` to `on_megastructure_upgraded` in its own
`common/on_actions/acot_on_actions.txt`, so re-subscribing it in our file made
the event fire **twice**.

**Correct fix (commit `b81815e7`):** removed the line. Our
`aot_on_actions.txt` contains no `acot_*` refs; base's own subscription covers
the DM citadel upgrade, so nothing of ours is needed for that event.

**Learnings:**
1. **Tool limitation:** the overlap checker treats on_action `events` lists as
   whole-list replacements and will flag base's event subscriptions in
   `acot_only_raw` ("divergent") even when base self-subscribes and we should
   add nothing. For any on_action list delta, **check the base's own
   on_actions file** for the event before merging; prefer "base already
   handles it".
2. **A "delta" in `acot_only_raw` can go three directions:** a genuine base
   addition to merge, a loss of one of our own uncommitted edits, or a base
   self-subscription we must *not* duplicate. Check the PRE-rebaseline scan
   and the base's own files before touching our list.
3. **Commit rebaseline edits immediately** on the branch the user works on;
   uncommitted work is lost on branch switches and resurfaces as a phantom
   "base change" delta on the next scan.
