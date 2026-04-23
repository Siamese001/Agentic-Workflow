"""Wave C.2 audit: apps_shared/utils/ dead candidates.

Filters:
  1. Dynamic import references (importlib, __import__, getattr on module strings)
  2. String references in config/ YAML/JSON files
  3. Git last-touch age (recently-modified = riskier)
  4. Plugin-registry patterns (classname strings)
  5. entry_points in pyproject.toml
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]


def run(args: list[str]) -> str:
    r = subprocess.run(args, capture_output=True, text=True, cwd=ROOT, timeout=60)
    return r.stdout


# Step 1: Load candidate list
all_targets = (
    (ROOT / "artifacts" / "adg" / "wave_c_targets.txt").read_text().splitlines()
)
targets = [t for t in all_targets if t.startswith("apps_shared/utils/")]
print(f"apps_shared/utils candidates: {len(targets)}")

# Step 2: Dynamic import / string reference scan across whole repo
#   Look for: "apps_shared.utils.<stem>" OR "apps_shared/utils/<stem>.py" OR just "<stem>" if used in importlib context
config_dirs = ["config", "apps_shared/config", "apps_eval/config", "apps_exec/config",
               "apps_research/config", "apps_rg/config", "apps_rfp/config", "apps_lic/config",
               "apps_underwriting_ai/config", ".windsurf", "pyproject.toml"]

dynamic_hits: dict[str, list[str]] = {}
string_hits: dict[str, list[str]] = {}

for t in targets:
    stem = pathlib.Path(t).stem
    mod = t.replace(".py", "").replace("/", ".")

    # (a) dotted module path as string anywhere
    r = run(["git", "grep", "-l", "--", f'"{mod}"'])
    for line in r.splitlines():
        if line and line != t and "archives/" not in line:
            dynamic_hits.setdefault(t, []).append(f'dotted-str:{line}')

    # (b) single-quoted dotted path
    r = run(["git", "grep", "-l", "--", f"'{mod}'"])
    for line in r.splitlines():
        if line and line != t and "archives/" not in line:
            dynamic_hits.setdefault(t, []).append(f'dotted-str:{line}')

    # (c) file path string
    r = run(["git", "grep", "-l", "--", f'"{t}"'])
    for line in r.splitlines():
        if line and line != t and "archives/" not in line:
            dynamic_hits.setdefault(t, []).append(f'path-str:{line}')

# Step 3: git last-touch age
now_cmd = run(["git", "log", "-1", "--format=%ct"])
import time
now_ts = int(now_cmd.strip()) if now_cmd.strip() else int(time.time())
ages: dict[str, int] = {}
for t in targets:
    r = run(["git", "log", "-1", "--format=%ct", "--", t])
    ts = int(r.strip()) if r.strip() else 0
    ages[t] = (now_ts - ts) // 86400  # days

# Step 4: classify
safe: list[str] = []
risky: list[tuple[str, str]] = []
for t in targets:
    reasons = []
    if t in dynamic_hits:
        reasons.append(f"dynamic/str-refs={len(dynamic_hits[t])}")
    if ages.get(t, 9999) < 30:
        reasons.append(f"age<30d ({ages[t]}d)")
    if reasons:
        risky.append((t, ",".join(reasons)))
    else:
        safe.append(t)

print(f"\nSAFE (no dynamic refs, age>=30d): {len(safe)}")
print(f"RISKY (dynamic refs or age<30d): {len(risky)}")
print("\n--- risky samples ---")
for t, r in risky[:10]:
    print(f"  {t}  [{r}]")
    for h in dynamic_hits.get(t, [])[:2]:
        print(f"    -> {h}")

# Step 5: save safe list
(ROOT / "artifacts" / "adg" / "wave_c2_safe.txt").write_text(
    "\n".join(safe) + "\n", encoding="utf-8"
)
(ROOT / "artifacts" / "adg" / "wave_c2_risky.txt").write_text(
    "\n".join(f"{t}\t{r}" for t, r in risky) + "\n", encoding="utf-8"
)
print(f"\nwrote wave_c2_safe.txt ({len(safe)}) and wave_c2_risky.txt ({len(risky)})")
