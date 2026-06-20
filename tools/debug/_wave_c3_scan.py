"""Wave C.3: audit apps_lic/tools/ and apps_shared/scripts/ dead candidates.

Extra filters vs Wave C.1/C.2:
  - Exclude any file with 'if __name__ == __main__' (CLI entry point)
  - Exclude any file referenced in shell scripts, Makefiles, .bat files
  - Exclude any file referenced in pyproject [project.scripts] or entry_points
  - Exclude any file referenced in .pre-commit-config.yaml
  - Exclude any file referenced in .github/workflows/*.yml
  - Exclude any file referenced in docs/archive/windsurf/legacy-tree/workflows/*.md or hooks.json
"""

from __future__ import annotations

import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
NOISE = ("docs/reports/", "tools/archive/", "artifacts/", "docs/archive/windsurf/legacy-tree/plans/", "archives/")


def run(args: list[str]) -> str:
    p = subprocess.run(args, capture_output=True, text=True, cwd=ROOT, timeout=60, check=False)
    return p.stdout


def has_main(f: pathlib.Path) -> bool:
    try:
        txt = f.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return bool(re.search(r"if __name__ ?== ?.__main__.", txt))


# Gather candidates
candidates: list[str] = []
for d in ("apps_lic/tools", "apps_shared/scripts"):
    p = ROOT / d
    if not p.exists():
        continue
    for f in p.rglob("*.py"):
        if f.name == "__init__.py":
            continue
        rel = str(f.relative_to(ROOT)).replace("\\", "/")
        candidates.append(rel)

print(f"Total candidates: {len(candidates)}")

# Pre-load CLI/hook/workflow reference files as one concatenated haystack
haystack_parts = []
for pat in (
    "pyproject.toml",
    ".pre-commit-config.yaml",
    ".codex/hooks.json",
):
    p = ROOT / pat
    if p.exists():
        haystack_parts.append(p.read_text(encoding="utf-8", errors="replace"))
for wd in (".github/workflows", "docs/archive/windsurf/legacy-tree/workflows", "ops_scripts"):
    p = ROOT / wd
    if not p.exists():
        continue
    for f in p.rglob("*"):
        if f.is_file() and f.suffix in (".yml", ".yaml", ".md", ".json", ".sh", ".bat", ".ps1", ".cmd"):
            try:
                haystack_parts.append(f.read_text(encoding="utf-8", errors="replace"))
            except OSError:
                pass
haystack = "\n".join(haystack_parts)

safe: list[str] = []
risky: list[tuple[str, str]] = []
for t in candidates:
    # Filter: has __main__ block
    if has_main(ROOT / t):
        risky.append((t, "has __main__ block"))
        continue
    # Filter: referenced in haystack by path or dotted name
    mod = t.replace(".py", "").replace("/", ".")
    stem = pathlib.Path(t).stem
    if t in haystack or mod in haystack:
        risky.append((t, "referenced in CLI/hook/workflow haystack"))
        continue
    # Filter: real code refs
    real_refs: list[str] = []
    for q in (f"from {mod} import", f"import {mod}", f'"{mod}"', f"'{mod}'", f'"{t}"'):
        out = run(["git", "grep", "-l", "--", q])
        for line in out.splitlines():
            line = line.strip()
            if line and line != t and not any(line.startswith(p) for p in NOISE):
                real_refs.append(f"{q[:30]}:{line}")
    if real_refs:
        risky.append((t, f"real-refs={len(real_refs)}:{real_refs[0][:80]}"))
    else:
        safe.append(t)

print(f"SAFE: {len(safe)}")
print(f"RISKY: {len(risky)}")
print("\n--- SAFE list ---")
for s in safe:
    print(f"  {s}")
print("\n--- RISKY sample (first 15) ---")
for t, r in risky[:15]:
    print(f"  {t}  [{r}]")

(ROOT / "artifacts" / "adg" / "wave_c3_safe.txt").write_text("\n".join(safe) + "\n", encoding="utf-8")
print(f"\nwrote wave_c3_safe.txt ({len(safe)})")
