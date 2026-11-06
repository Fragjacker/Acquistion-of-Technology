#!/usr/bin/env python3
"""Compare AOT component_templates against Ancient Cache of Technologies (ACOT).

Extracts every `*_component_template` block (identified by its `key = "..."` line)
from both trees, matches them per key, and reports value differences per key.
"""
import re
import sys
from pathlib import Path

AOT_DIR = Path(__file__).resolve().parent.parent / "acquistion_of_technology/common/component_templates"
ACOT_DIR = Path("D:/SteamLibrary/steamapps/workshop/content/281990/1419304439/common/component_templates")

BLOCK_RE = re.compile(r"(\w+_component_template)\s*=\s*\{")


def extract_blocks(path):
    """Return dict key -> (block_type, [lines]) for each component block in file."""
    text = path.read_text(encoding="utf-8", errors="replace")
    blocks = {}
    # find all top-level blocks
    for m in re.finditer(r"(\w*_component_template)\s*=\s*\{", text):
        start = m.start()
        depth = 0
        i = m.end() - 1  # at the '{'
        end = None
        while i < len(text):
            c = text[i]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    end = i
                    break
            i += 1
        if end is None:
            continue
        block_text = text[start:end + 1]
        km = re.search(r'\bkey\s*=\s*"([^"]+)"', block_text)
        if not km:
            continue
        blocks[km.group(1)] = (m.group(1), block_text.splitlines())
    return blocks


def load(dirpath):
    result = {}
    for f in sorted(dirpath.glob("*.txt")):
        for k, v in extract_blocks(f).items():
            if k in result:
                print(f"DUPLICATE KEY across files: {k} in {f} and {result[k][2]}", file=sys.stderr)
            result[k] = (v[0], v[1], str(f))
    return result


aot = load(AOT_DIR)
acot = load(ACOT_DIR)

common = sorted(set(aot) & set(acot))
only_aot = sorted(set(aot) - set(acot))
only_acot = sorted(set(acot) - set(aot))

print(f"AOT keys: {len(aot)}, ACOT keys: {len(acot)}, common: {len(common)}, "
      f"only-AOT: {len(only_aot)}, only-ACOT: {len(only_acot)}\n")

print("== KEYS ONLY IN AOT (kept as-is) ==")
for k in only_aot:
    print(f"  {k}  ({aot[k][0]})  in {aot[k][2]}")

print("\n== KEYS ONLY IN ACOT (candidates to merge over) ==")
for k in only_acot:
    print(f"  {k}  ({acot[k][0]})  in {acot[k][2]}")

print("\n== COMMON KEYS WITH DIFFERENCES ==")
for k in common:
    a = "\n".join(aot[k][1])
    c = "\n".join(acot[k][1])
    if a == c:
        continue
    print(f"\n--- {k}")
    print(f"    AOT : {aot[k][2]}  type={aot[k][0]}")
    print(f"    ACOT: {acot[k][2]}  type={acot[k][0]}")
    import difflib
    for line in difflib.unified_diff(a.splitlines(), c.splitlines(), lineterm="", n=1):
        print("    " + line)
