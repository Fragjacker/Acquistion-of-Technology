"""Top-level-key (TIER 1a) check for component_template definitions.

Implements the skills/acot-base-rebaseline.md decision rule for the
component_templates folder only: for every definition key present in BOTH
trees, flag any column-level (top-level) key that the ACOT base uses but our
override lacks. That is the only category that is a real structural gap.
Value-only differences (token drift) are reported separately and NOT treated
as gaps — per the skill doc those are usually deliberate DRY refactors /
design (SR rework, sigma tiers, inline scripts).
"""
import re
import sys
from pathlib import Path

DEFAULT_ACOT = Path("D:/SteamLibrary/steamapps/workshop/content/281990/1419304439")
CT_REL = "common/component_templates"

KEY_RE = re.compile(r'^\s*key\s*=\s*"([^"]+)"', re.M)
BLOCK_RE = re.compile(r'^[a-z_]*component_template\s*=\s*\{\s*$')
TOPKEY_RE = re.compile(r'^([a-zA-Z_]+)\s*=')


def iter_definitions(path: Path):
    """Yield (key, block_text, top_level_keys) for each top-level def block."""
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    lines = text.splitlines()
    i = 0
    n = len(lines)
    while i < n:
        if BLOCK_RE.match(lines[i]):
            depth = 0
            j = i
            while j < n:
                depth += lines[j].count("{") - lines[j].count("}")
                j += 1
                if depth <= 0:
                    break
            block = "\n".join(lines[i:j])
            km = KEY_RE.search(block)
            if km:
                tops = [TOPKEY_RE.match(l).group(1) for l in lines[i:j]
                        if TOPKEY_RE.match(l)]
                yield km.group(1), block, tops
            i = j
        else:
            i += 1


def load(dirpath: Path):
    defs = {}
    for f in sorted(dirpath.glob("*.txt")):
        for key, block, tops in iter_definitions(f):
            if key in defs:
                print(f"WARN duplicate key {key} in {f.name}", file=sys.stderr)
            defs[key] = (f.name, block, tops)
    return defs


def main():
    acot_dir = DEFAULT_ACOT / CT_REL
    aot_dir = Path("acquistion_of_technology") / CT_REL
    acot = load(acot_dir)
    aot = load(aot_dir)
    shared = sorted(set(acot) & set(aot))
    aot_only = sorted(set(aot) - set(acot))
    acot_only = sorted(set(acot) - set(aot))
    print(f"AOT defs: {len(aot)}  ACOT defs: {len(acot)}  shared: {len(shared)}")
    print(f"ACOT-only defs ({len(acot_only)}): " + ", ".join(acot_only))
    print(f"AOT-only defs  ({len(aot_only)}): " + ", ".join(aot_only))
    print()
    gaps = 0
    for k in shared:
        acot_tops = set(acot[k][2])
        aot_tops = set(aot[k][2])
        missing = sorted(acot_tops - aot_tops)
        extra = sorted(aot_tops - acot_tops)
        if missing:
            gaps += 1
            print(f"## GAP  {k}  ({aot[k][0]} vs {acot[k][0]})")
            print(f"     ACOT top-level keys we lack: {missing}")
            if extra:
                print(f"     AOT top-level keys base lacks: {extra}")
    print()
    print(f"Shared defs with a top-level key gap: {gaps}")


if __name__ == "__main__":
    main()
