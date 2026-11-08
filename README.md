# Acquistion-of-Technology

The repository for the **Acquistion of Technology** mod for Stellaris.

## Dependencies

This mod is a **fork of "Ancient Cache of Technologies"** and builds on top of
it. Please install the following so it works as intended.

### Required
* **Ancient Cache of Technologies** (the base mod this fork extends).
  The fork overrides / adds on top of its definitions, so the base mod should be
  in your `mod` folder and enabled.

### Optional (content adds / integrates with these; the mod loads without them)
* **Phanon** — adds the "Phanon" building line, the `aot_sr_runic_power` resource
  and the `spawn_habitat_in_fe_system` effect. Without Phanon these resolve to
  nothing (a handful of log warnings about them are expected and harmless). Phanon
  content is hidden when the `aot_phanon_content_OFF` global flag is set, so the
  buildings can also be disabled by the player/other mods.
* **GigaMod (Gigamod)** — the fork's planet/habitat triggers
  (`giga_is_pc_*`, `is_giga_*`, Planetary Diversity ringworlds, etc.) extend
  GigaMod's planetary-computer and habitat definitions. This repo ships
  `always = no` placeholder stubs (see `common/scripted_triggers/!_aot_placeholder_triggers.txt`)
  so the mod still loads; GigaMod's own triggers used by the base mod will simply
  be inactive until GigaMod is installed.
* **SAS – Space Astromancy Society (or similar)** — a few starbase-size
  comparisons (`sas_xxtitan_warship`) and the SBTG starbase triggers
  (`is_sbtg_sb_starbase`, `is_sbtg_megastructure_shipyard`) are used to grant
  extra build options when those mods are present. They are inert without them.
* **BPV – Better Planet View (More Building Slots)** — the mod ships a neutral
  fallback for the `BPV_district_slots2` script so it also loads without this mod;
  install BPV for the extra building-slot features to actually take effect.
* **Ruler's Court** — provides the `jobs/politician_output` script. A no-op
  fallback is included so the mod loads without it.

> Note: the fallback scripts in `common/inline_scripts/` (districts)
> and the placeholder scripted triggers above are neutral no-ops provided so the mod
> loads even when the mods above are absent. When the real mod is present and loaded
> after this one, its definition takes precedence.
>
> The log will show a number of harmless "unknown ..." messages for the optional
> mods above (and for the base mod's own GigaMod/Phanon cross-references). These are
> expected when the corresponding optional mod is not installed and do not prevent
> the game from loading.

## Maintenance notes
* Files in this repository use CRLF line endings (the game reader can choke on
  bare LF). Preserve CRLF when editing.
* After changing any `common/` file, clear the mod cache:
  `del "%LOCALAPPDATA%\Paradox Interactive\Stellaris\cache\*.bin"`.
