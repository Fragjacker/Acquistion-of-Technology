#!/usr/bin/env python3
"""
acot_overlap_check.py — re-evaluate which ACoT (Ancient Cache of Technologies)
definitions this mod overrides, and flag the ones a *base-mod update* may have
made worth re-merging.

WHAT THIS IS (and is NOT)
-------------------------
This project is a DELIBERATE FORK / integration layer on top of the ACoT base
mod. Many overrides differ from ACoT ON PURPOSE (e.g. Phanon-unlock
differences). A naive "ACoT has text we lack -> copy it over" diff is WRONG and
produces a wall of false positives. This tool therefore:

  1. Enumerates the top-level (column-0) definitions we override in ACoT.
  2. Classifies each overlap: identical / we-have-more / acot-has-more / divergent.
  3. STRIPS inline-script bodies (`script = { ... }`) before the token diff, so
     that "we implement X in an inline script, ACoT hardcodes X" (a DRY difference)
     is NOT mistaken for a real missing feature.
  4. Ranks the result so the few blocks that are genuinely worth a human re-merge
     decision after a base update float to the top (TIER 1).

It does NOT merge anything. It reports. A human makes the adoption decision.

USAGE
-----
  python tools/acot_overlap_check.py                     # full report (ACoT auto-detected, ours=acquistion_of_technology)
  python tools/acot_overlap_check.py --key <def_name>    # deep-dive one definition
  python tools/acot_overlap_check.py --acot <path>       # pin the base mod explicitly
  python tools/acot_overlap_check.py --json              # machine-readable
  python tools/acot_overlap_check.py --verbose           # also list TIER 2 (DRY-only)

ACoT AUTO-DETECTION
-------------------
Looks under <steam>/workshop/content/281990/*/ for a *.mod whose name is
"Ancient Cache of Technologies" (or remote_file_id "1419304439"). The folder id
is the stable handle across base-mod updates; the *.mod file is named
`descriptor.mod` (generic), so we match on the name/id, never the filename.

METHOD NOTES (the hard-won part — see docs/overriding-acot.md)
--------------------------------------------------------------
* Definitions are matched at COLUMN 0 only. Indented blocks (component_set,
  zone sub-blocks, script bodies) are nested, NOT separate overrides; matching
  them inflates counts and mis-labels them.
* Tokens, not words, are compared (whitespace/comment/brace-insensitive).
* Inline-script content is a separate view, so DRY refactors are demoted.
"""
import argparse
import json
import os
import re
import sys

# ---------------------------------------------------------------- constants --
STELLARIS_APP_ID = "281990"
ACOT_DISPLAY_NAME = "Ancient Cache of Technologies"
ACOT_REMOTE_FILE_ID = "1419304439"

TOKEN = re.compile(r"[A-Za-z_@][\w@.]*|\d+\.?\d*")
KEYLINE = re.compile(r"^([A-Za-z_]\w*)\s*=\s*(.*)$")
SCRIPT_START = re.compile(r"^script\s*=")


# ------------------------------------------------------------- path finding --
def find_acot(steam_root):
    """Return the folder of the ACoT base mod under steam workshop content."""
    base = os.path.join(steam_root, "workshop", "content", STELLARIS_APP_ID)
    if not os.path.isdir(base):
        return None
    best = None
    for entry in sorted(os.listdir(base)):
        moddir = os.path.join(base, entry)
        if not os.path.isdir(moddir):
            continue
        for fn in os.listdir(moddir):
            if not fn.endswith(".mod"):
                continue
            try:
                text = open(os.path.join(moddir, fn), encoding="utf-8",
                            errors="replace").read()
            except OSError:
                continue
            if ('name="%s"' % ACOT_DISPLAY_NAME) in text or \
               ('remote_file_id="%s"' % ACOT_REMOTE_FILE_ID) in text:
                best = moddir  # keep scanning for an id match below
                if ('remote_file_id="%s"' % ACOT_REMOTE_FILE_ID) in text:
                    return moddir  # exact id match wins immediately
    return best


# ------------------------------------------------------------------- parsing --
def top_level_blocks(root):
    """Return {name: (relpath, [lines])} for COLUMN-0 definitions in `root`.

    A definition is a line that starts at column 0 with `name =`. Its extent is
    balanced by counting `{`/`}` from that line. Lines indented under a block
    are content, not definitions.
    """
    out = {}
    for dirpath, _, files in os.walk(root):
        for fn in sorted(files):
            if not fn.endswith(".txt"):
                continue
            p = os.path.join(dirpath, fn)
            try:
                L = open(p, encoding="utf-8", errors="replace").read().splitlines()
            except OSError:
                continue
            rel = os.path.relpath(p, root)
            i, n = 0, len(L)
            while i < n:
                m = KEYLINE.match(L[i])          # KEYLINE has ^ anchor => column 0
                if m:
                    rest = m.group(2).lstrip()
                    is_block = rest.startswith("{") or (
                        i + 1 < n and L[i + 1].lstrip().startswith("{"))
                    if is_block:
                        depth, j, started = 0, i, False
                        while j < n:
                            depth += L[j].count("{") - L[j].count("}")
                            if L[j].count("{"):
                                started = True
                            if started and depth <= 0:
                                break
                            j += 1
                        out.setdefault(m.group(1), (rel, L[i:j + 1]))
                        i = j
                i += 1
    return out


def strip_inline_scripts(lines):
    """Return lines with the body of each `script = { ... }` removed.

    `script = buildings/...` (file reference, no braces) is left intact: the
    point is to neutralise *inline* script implementations when comparing the
    non-script surface of two definitions.
    """
    out, i, n = [], 0, len(lines)
    while i < n:
        if SCRIPT_START.match(lines[i].strip()):
            depth, j, started = 0, i, False
            while j < n:
                depth += lines[j].count("{") - lines[j].count("}")
                if lines[j].count("{"):
                    started = True
                if started and depth <= 0:
                    break
                j += 1
            i = j + 1
            continue
        out.append(lines[i])
        i += 1
    return out


def tokens(lines, strip_scripts=False):
    if strip_scripts:
        lines = strip_inline_scripts(lines)
    s = "\n".join(lines)
    s = re.sub(r"#.*$", " ", s)
    s = s.replace("{", " ").replace("}", " ")
    return set(TOKEN.findall(s))


def top_keys(lines):
    """Set of COLUMN-0 `key =` names used directly in this block (top-level only).

    Call on script-stripped lines so only real definition-level keys count.
    This is the strongest signal for 'did ACoT add a capability we lack': a
    key like `building_sets`, `upgrades`, `cost`, `produces` that ACoT's block
    has and ours does not. Unlike token-diffs, it is immune to the DRY-refactor
    false-positive (values/names inside inline scripts don't count as keys).
    """
    keys = set()
    for ln in lines:
        if re.match(r"^[a-z][a-z0-9_]*\s*=", ln):
            keys.add(ln.split("=")[0].strip())
    return keys


# --------------------------------------------------------------- classification --
def classify(o_lines, a_lines):
    o_raw, a_raw = tokens(o_lines, False), tokens(a_lines, False)
    o_s, a_s = tokens(o_lines, True), tokens(a_lines, True)

    acot_only_raw = sorted(a_raw - o_raw)
    ours_only_raw = sorted(o_raw - a_raw)
    acot_only_ns = sorted(a_s - o_s)          # ACoT non-script tokens we lack
    ours_only_ns = sorted(o_s - a_s)
    acot_only_keys = sorted(top_keys(a_s) - top_keys(o_s))  # col-0 keys ACoT uses that we don't

    if not acot_only_raw and not ours_only_raw:
        raw_class = "identical"
    elif not acot_only_raw:
        raw_class = "we_have_more"
    elif not ours_only_raw:
        raw_class = "acot_has_more"
    else:
        raw_class = "divergent"

    # Review tiers (what actually matters after a base update):
    if acot_only_ns:
        tier = 1   # ACoT has non-script content we lack
    elif acot_only_raw:
        tier = 2   # DRY / inline-script-only difference
    else:
        tier = 3   # no ACoT-side gap

    # A tier-1 row where ACoT uses NO column-0 key we lack is very likely the
    # DRY-refactor false-positive (ACoT inlined a tier's logic; we expressed the
    # same logic as a parameter in an inline script). Flag it so reviewers can
    # skip straight past the noise.
    weak = (tier == 1 and not acot_only_keys)

    return {
        "class": raw_class,
        "tier": tier,
        "weak": weak,
        "acot_only_raw": acot_only_raw,
        "ours_only_raw": ours_only_raw,
        "acot_only_nonscript": acot_only_ns,
        "ours_only_nonscript": ours_only_ns,
        "acot_only_keys": acot_only_keys,
    }


# ---------------------------------------------------------------------- report --
def collect(ours_root, acot_root):
    O = top_level_blocks(ours_root)
    A = top_level_blocks(acot_root)
    overlap = sorted(set(O) & set(A))
    results = {}
    for k in overlap:
        res = classify(O[k][1], A[k][1])
        res["ours_file"] = O[k][0]
        res["acot_file"] = A[k][0]
        results[k] = res
    return O, A, overlap, results


def _cap(tokens, n=40):
    if len(tokens) <= n:
        return ", ".join(tokens)
    return ", ".join(tokens[:n]) + "  (+%d more — use --key)" % (len(tokens) - n)


def print_report(acot_root, ours_root, overlap, results):
    counts = {"identical": 0, "we_have_more": 0, "acot_has_more": 0, "divergent": 0}
    for r in results.values():
        counts[r["class"]] += 1
    print("ACoT base mod: %s" % acot_root)
    print("Ours root:     %s" % ours_root)
    print("Our defs: %d | ACoT defs: %d | Overlapping: %d"
          % (len(set(k for k in results)), len(results), len(overlap)))
    print("  identical=%(identical)d  we_have_more=%(we_have_more)d  "
          "acot_has_more=%(acot_has_more)d  divergent=%(divergent)d" % counts)
    print()

    t1 = sorted([k for k, r in results.items() if r["tier"] == 1],
                key=lambda k: -len(results[k]["acot_only_keys"]))
    t2 = sorted([k for k, r in results.items() if r["tier"] == 2])

    # TIER 1 splits into "real gap" (ACoT uses a column-0 key we lack — a new
    # capability) and "likely DRY refactor" (no key diff — usually a false
    # positive where ACoT inlined a tier's logic and we parameterized it).
    t1_real = [k for k in t1 if results[k]["acot_only_keys"]]
    t1_noise = [k for k in t1 if not results[k]["acot_only_keys"]]

    print("TIER 1a — REVIEW: ACoT uses a top-level key we lack (real gap candidate) (%d)" % len(t1_real))
    for k in t1_real:
        r = results[k]
        print("  %-40s o=%-40s a=%s" % (k, r["ours_file"], r["acot_file"]))
        print("     new keys in ACoT: %s" % ", ".join(r["acot_only_keys"]))
        print("     (acot-only tokens: %s)" % _cap(r["acot_only_nonscript"], 8))
    print()

    print("TIER 1b — LIKELY DRY REFACOR / false-positive (no top-level key diff) (%d)" % len(t1_noise))
    for k in t1_noise:
        r = results[k]
        print("  %-40s acot-only tokens: %s" % (k, _cap(r["acot_only_nonscript"], 6)))
    print()

    print("TIER 2 — DRY / inline-script-only differences (%d)" % len(t2))
    for k in t2:
        r = results[k]
        print("  %-40s acot-only(raw): %s" % (k, _cap(r["acot_only_raw"], 12)))
    print()
    print("TIER 3 — no ACoT-side gap: %d  (identical or we-have-more; nothing to adopt)"
          % len([k for k, r in results.items() if r["tier"] == 3]))
    print()
    print("DECISION RULE: for each TIER 1 block, open BOTH files (paths above), read the")
    print("acot-only tokens in context, and adopt ONLY if it is a genuine new base feature")
    print("consistent with this fork's design. Never bulk-merge: differences are often")
    print("deliberate (Phanon integration). Run with --key <name> for a full side-by-side.")


def deep_dive(key, O, A, results):
    if key not in results:
        print("key not in overlap set: %s" % key)
        return
    r = results[key]
    print("=" * 72)
    print(key)
    print("class=%s tier=%d weak=%s" % (r["class"], r["tier"], r.get("weak")))
    if r.get("acot_only_keys"):
        print("NEW top-level keys in ACoT (real gap signal): %s" % ", ".join(r["acot_only_keys"]))
    print("acot-only (non-script): %s" % (", ".join(r["acot_only_nonscript"]) or "-"))
    print("ours-only (non-script): %s" % (", ".join(r["ours_only_nonscript"]) or "-"))
    print("-" * 72)
    print("OURS — %s" % O[key][0])
    print("-" * 72)
    for ln in O[key][1]:
        print("  " + ln)
    print("-" * 72)
    print("ACoT — %s" % A[key][0])
    print("-" * 72)
    for ln in A[key][1]:
        print("  " + ln)


# ----------------------------------------------------------------------- main --
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ours", default="acquistion_of_technology",
                    help="path to this mod's source tree (default: acquistion_of_technology)")
    ap.add_argument("--acot", default=None,
                    help="explicit path to the ACoT base mod (overrides auto-detect)")
    ap.add_argument("--steam-root", default="D:/SteamLibrary/steamapps",
                    help="steamapps root for auto-detect (default: D:/SteamLibrary/steamapps)")
    ap.add_argument("--key", default=None, help="deep-dive a single definition name")
    ap.add_argument("--verbose", action="store_true", help="(reserved; TIER 2 already listed)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    args = ap.parse_args(argv)

    ours_root = os.path.abspath(args.ours)
    if not os.path.isdir(ours_root):
        sys.exit("ours path not found: %s" % ours_root)
    acot_root = args.acot or find_acot(os.path.abspath(args.steam_root))
    if not acot_root or not os.path.isdir(acot_root):
        sys.exit("Could not locate the ACoT base mod. Pass --acot <path>. "
                 "Looked under: %s" % os.path.abspath(args.steam_root))

    O, A, overlap, results = collect(ours_root, acot_root)

    if args.key:
        deep_dive(args.key, O, A, results)
        return
    if args.json:
        out = {
            "acot": acot_root,
            "ours": ours_root,
            "overlap": len(overlap),
            "results": {k: {kk: vv for kk, vv in r.items()} for k, r in results.items()},
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return
    print_report(acot_root, ours_root, overlap, results)


if __name__ == "__main__":
    main()
