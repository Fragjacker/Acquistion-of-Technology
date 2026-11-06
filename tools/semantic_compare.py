#!/usr/bin/env python3
"""Semantic comparison of AOT vs ACOT component blocks for common keys.

- Resolves AOT local variables (@x = n) and inline_script MIN_DMG/MAX_DMG
  references so damage comparisons are value-based, not line-based.
- Reports: value mismatches, AOT-only lines, ACOT-only lines per key.
"""
import re
from pathlib import Path
from compare_components import aot, acot, common

from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent
AOT_DIR = _ROOT / "acquistion_of_technology/common/component_templates"


def normalize(lines, vars_):
    """Normalize block lines for value comparison: replace inline_script damage
    with equivalent `damage = { min = X max = Y }` and drop the var usages."""
    out = []
    i = 0
    text = "\n".join(lines)
    inline = re.search(r"inline_script\s*=\s*\{", text)
    if inline:
        # find matching brace from inline
        depth = 0
        start = text.find("{", inline.end() - 1)
        i = start
        while i < len(text):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        block_text = text[start:i + 1]
        md = re.search(r"MIN_DMG\s*=\s*@(\w+)", block_text)
        xd = re.search(r"MAX_DMG\s*=\s*@(\w+)", block_text)
        if md and xd and md.group(1) in vars_ and xd.group(1) in vars_:
            text = text[:start] + f" damage = {{ min = {vars_[md.group(1)]} max = {vars_[xd.group(1)]} }} " + text[i + 1:]
    return [l.rstrip() for l in text.splitlines()]


print("== COMMON KEYS: DIFFERENCES (semantic) ==")
diff_keys = []
for k in common:
    a_lines = aot[k][1]
    c_lines = acot[k][1]
    # collect top-level vars from each file
    aot_file = AOT_DIR / aot[k][2].split("\\")[-1]
    a_vars = dict(re.findall(r"^@(\w+)\s*=\s*([\d.]+)\s*$", aot_file.read_text(encoding="utf-8", errors="replace"), re.M))
    acot_file = Path(acot[k][2])
    c_vars = dict(re.findall(r"^@(\w+)\s*=\s*([\d.]+)\s*$", acot_file.read_text(encoding="utf-8", errors="replace"), re.M))
    a_norm = normalize(a_lines, a_vars)
    c_norm = normalize(c_lines, c_vars)
    a_set = [l for l in a_norm if l.strip()]
    c_set = [l for l in c_norm if l.strip()]
    if a_set == c_set:
        continue
    diff_keys.append(k)
    print(f"\n### {k}")
    print(f"  AOT : {aot[k][2]}")
    print(f"  ACOT: {acot[k][2]}")
    import difflib
    for line in difflib.unified_diff(a_set, c_set, lineterm="", n=0):
        if line.startswith(("+++", "---")):
            continue
        print("  " + line)

print(f"\n\nTotal keys with semantic differences: {len(diff_keys)}")
