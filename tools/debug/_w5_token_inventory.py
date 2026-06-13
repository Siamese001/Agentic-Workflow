"""W5 Phase 5.1 — inventory all authored guardian tokens across the repo.

Goal: identify non-canonical tokens used by ≥2 different guardian comments
so we can add them to _CANONICAL_GUARDIAN_TOKENS and _GUARDIAN_MAP deterministically.
"""

from __future__ import annotations
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Directories to scan (exclude archives, pycache, node_modules, etc.)
ROOTS = (
    "agentic_core",
    "apps_rg",
    "apps_shared",
    "apps_lic",
    "apps_eval",
    "apps_exec",
    "apps_research",
    "apps_rfp",
    "apps_underwriting_ai",
    "tools",
    "ops_scripts",
    "system_learning",
    "docs/archive/windsurf/legacy-tree/governance_scripts",
    "infrastructure",
)
EXCLUDES = (r"\\__pycache__\\", r"\\archives\\", r"\\_archive\\", r"\\tests\\")

GUARD_RE = re.compile(r"#\s*guardian:\s*(allow-[a-z0-9_\-]+)", re.IGNORECASE)


def main() -> int:
    counter: Counter[str] = Counter()
    examples: dict[str, list[tuple[str, int, str]]] = defaultdict(list)

    for root in ROOTS:
        p = Path(root)
        if not p.exists():
            continue
        for py in p.rglob("*.py"):
            sp = str(py)
            if any(re.search(ex, sp) for ex in EXCLUDES):
                continue
            try:
                text = py.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                m = GUARD_RE.search(line)
                if not m:
                    continue
                tok = m.group(1).lower()
                counter[tok] += 1
                if len(examples[tok]) < 3:
                    examples[tok].append((sp, i, line.strip()[:120]))

    print(f"Total unique tokens: {len(counter)}")
    print(f"Total guardian comment lines: {sum(counter.values())}")
    print("\nAll tokens ranked by count:")
    print(f"{'count':>6}  token")
    for tok, n in counter.most_common():
        print(f"{n:>6}  {tok}")

    # Focus: tokens used ≥2 times that are NOT canonical
    from agentic_core.adg.artifact.multi_writer import _CANONICAL_GUARDIAN_TOKENS

    print("\n" + "=" * 80)
    print("NON-CANONICAL tokens used >=2 times (candidates for expansion):")
    print("=" * 80)
    candidates = []
    for tok, n in counter.most_common():
        if tok not in _CANONICAL_GUARDIAN_TOKENS and n >= 2:
            candidates.append((tok, n))
            print(f"\n{tok}  (used {n} times)")
            for fp, ln, src in examples[tok][:3]:
                print(f"  {fp}:{ln}")
                print(f"    {src}")
    print(
        f"\nTotal non-canonical >= 2: {len(candidates)} tokens, {sum(n for _, n in candidates)} occurrences"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
