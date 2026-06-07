"""Wave C.2 audit v2: filter analysis-artifact noise, classify by commit-message nature."""

from __future__ import annotations

import pathlib
import re
import subprocess
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]

# Known-benign files that reference these modules as analysis targets, not consumers
NOISE_PREFIXES = (
    "docs/reports/",
    "tools/archive/",
    "artifacts/",
    "docs/archive/windsurf/legacy-tree/plans/",
)
# Known-mechanical commit subjects (blanket refactors, not feature touches)
MECHANICAL_COMMIT_PATTERNS = [
    r"guardian exception",
    r"progress bar",
    r"phase [A-Z]: narrow",
    r"Wave \d+:",
    r"ratchet",
    r"line endings",
    r"trailing whitespace",
    r"W\d+[A-Z]?:",
    r"adg-ci",
]


def run(args: list[str]) -> str:
    r = subprocess.run(args, capture_output=True, text=True, cwd=ROOT, timeout=60, check=False)
    return r.stdout


def is_noise(path: str) -> bool:
    return any(path.startswith(p) for p in NOISE_PREFIXES)


def classify_last_commit_nature(target: str) -> tuple[str, str]:
    """Return (nature, subject). nature in {mechanical, feature, unknown}."""
    subj = run(["git", "log", "-1", "--format=%s", "--", target]).strip()
    if not subj:
        return ("unknown", "")
    for pat in MECHANICAL_COMMIT_PATTERNS:
        if re.search(pat, subj, re.IGNORECASE):
            return ("mechanical", subj)
    return ("feature", subj)


all_targets = (ROOT / "artifacts" / "adg" / "wave_c_targets.txt").read_text().splitlines()
targets = [t for t in all_targets if t.startswith("apps_shared/utils/")]

safe: list[str] = []
risky: list[tuple[str, str]] = []

for t in targets:
    stem = pathlib.Path(t).stem
    mod = t.replace(".py", "").replace("/", ".")
    real_refs: list[str] = []

    for q in (f'"{mod}"', f"'{mod}'", f'"{t}"'):
        r = run(["git", "grep", "-l", "--", q])
        for line in r.splitlines():
            line = line.strip()
            if not line or line == t or "archives/" in line or is_noise(line):
                continue
            real_refs.append(f"{q[:40]}:{line}")

    nature, subj = classify_last_commit_nature(t)

    if real_refs:
        risky.append((t, f"real-refs={len(real_refs)};{real_refs[0][:80]}"))
    elif nature == "feature":
        risky.append((t, f"feature-commit:{subj[:80]}"))
    else:
        safe.append(t)

print(f"SAFE (no real refs, last commit mechanical/unknown): {len(safe)}")
print(f"RISKY: {len(risky)}")
print("\n--- risky samples ---")
for t, r in risky[:12]:
    print(f"  {t}")
    print(f"    -> {r}")

(ROOT / "artifacts" / "adg" / "wave_c2_safe.txt").write_text("\n".join(safe) + "\n", encoding="utf-8")
(ROOT / "artifacts" / "adg" / "wave_c2_risky.txt").write_text(
    "\n".join(f"{t}\t{r}" for t, r in risky) + "\n", encoding="utf-8"
)
print(f"\nwrote wave_c2_safe.txt ({len(safe)}) and wave_c2_risky.txt ({len(risky)})")
