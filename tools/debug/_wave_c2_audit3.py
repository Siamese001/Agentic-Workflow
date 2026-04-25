"""Wave C.2 final audit: zero-real-refs signal only, ignore mechanical-commit-age noise."""

from __future__ import annotations

import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
NOISE = (
    "docs/reports/",
    "tools/archive/",
    "artifacts/",
    ".windsurf/plans/",
    "archives/",
)


def run(args: list[str]) -> str:
    r = subprocess.run(args, capture_output=True, text=True, cwd=ROOT, timeout=60, check=False)
    return r.stdout


all_targets = (ROOT / "artifacts" / "adg" / "wave_c_targets.txt").read_text().splitlines()
targets = [t for t in all_targets if t.startswith("apps_shared/utils/")]
safe: list[str] = []
risky: list[tuple[str, list[tuple[str, str]]]] = []

for t in targets:
    mod = t.replace(".py", "").replace("/", ".")
    real_refs: list[tuple[str, str]] = []
    queries = [f'"{mod}"', f"'{mod}'", f'"{t}"', f"from {mod} import", f"import {mod}"]
    for q in queries:
        out = run(["git", "grep", "-l", "--", q])
        for line in out.splitlines():
            line = line.strip()
            if not line or line == t or any(line.startswith(p) for p in NOISE):
                continue
            real_refs.append((q[:30], line))
    if real_refs:
        risky.append((t, real_refs[:3]))
    else:
        safe.append(t)

print(f"SAFE (zero real refs): {len(safe)}")
print(f"RISKY (has non-noise refs): {len(risky)}")
print("\n--- risky details ---")
for t, refs in risky:
    print(f"  {t}")
    for q, f in refs:
        print(f"    [{q}] {f}")

(ROOT / "artifacts" / "adg" / "wave_c2_safe.txt").write_text("\n".join(safe) + "\n", encoding="utf-8")
print(f"\nwrote wave_c2_safe.txt ({len(safe)})")
