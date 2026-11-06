#!/usr/bin/env python3
"""Classify each shared component_template diff as:
  DRIFT   : same field structure & same script refs on both sides -> value-only change, safe to sync.
  DESIGN  : AOT side changes/removes a script/inline_script/cost/upkeep mechanism -> fork design, leave alone.
Prints one line per shared key.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AOT_DIR = ROOT / "acquistion_of_technology/common/component_templates"
ACOT_DIR = Path("D:/SteamLibrary/steamapps/workshop/content/281990/1419304439/common/component_templates")

KEY_RE = re.compile(r'^\s*key\s*=\s*"([^"]+)"', re.M)
BLOCK_RE = re.compile(r'^[a-z_]*component_template\s*=\s*\{\s*$')


def load(dirpath):
    out = {}
    for p in dirpath.glob("*.txt"):
        lines = p.read_text(encoding="utf-8-sig", errors="replace").splitlines()
        n = len(lines); i = 0
        while i < n:
            if BLOCK_RE.match(lines[i]):
                depth = 0; j = i
                while j < n:
                    depth += lines[j].count("{") - lines[j].count("}")
                    j += 1
                    if depth <= 0:
                        break
                block = lines[i:j]
                km = KEY_RE.search("\n".join(block))
                if km:
                    out[km.group(1)] = block
                i = j
            else:
                i += 1
    return out


def sig(block):
    """Signature: ordered list of (field, script-ref) pairs at every depth."""
    sig = []
    for ln in block:
        s = ln.strip()
        if not s:
            continue
        m = re.match(r'^(\w+)\s*=', s)
        if m:
            sig.append(m.group(1))
        m2 = re.search(r'script\s*=\s*(\S+)', s)
        if m2:
            sig.append("script:" + m2.group(1))
    return sig


def main():
    aot = load(AOT_DIR)
    acot = load(ACOT_DIR)
    shared = sorted(set(aot) & set(acot))
    drift, design = [], []
    for k in shared:
        sa, sb = sig(aot[k]), sig(acot[k])
        # DESIGN if the multiset of script refs or field names differs at all
        if sorted(sa) != sorted(sb):
            design.append(k)
        else:
            # value-only: compare actual scalar values
            va = re.findall(r'=\s*([0-9][0-9._]*)', "\n".join(aot[k]))
            vb = re.findall(r'=\s*([0-9][0-9._]*)', "\n".join(acot[k]))
            if va != vb:
                drift.append((k, va, vb))
            else:
                # identical values but different ordering -> cosmetic
                pass
    print(f"shared={len(shared)}  VALUE-DRIFT={len(drift)}  DESIGN/STRUCT={len(design)}")
    print("\n== VALUE-DRIFT (safe to sync from ACOT) ==")
    for k, va, vb in drift:
        print(f"  {k}: AOT={va} -> ACOT={vb}")
    print("\n== DESIGN/STRUCT (fork design; needs manual review) ==")
    for k in design:
        print(f"  {k}")


if __name__ == "__main__":
    main()
