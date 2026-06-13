"""W5 singleton-token sites: find the exact source-line locations of
singleton non-canonical guardian tokens so Cursor Agent can normalize them
deterministically (typo fixes, not vocabulary additions).
"""

from __future__ import annotations
import re
import sys
from collections import defaultdict
from pathlib import Path

SINGLETONS = {
    # token -> intended canonical replacement (evidence-based)
    "allow-broad-to-wrap": "allow-broad-exception",  # broad catch that re-raises as wrapped
    "allow-broad-shadow": "allow-broad-exception",  # broad catch in shadow-eval path
    "allow-broad-enforce": "allow-broad-exception",  # broad catch in enforcement chokepoint
    "allow-importerror": "allow-import-fail",  # ImportError catch; use W5.1 canonical
    "allow-x": None,  # likely placeholder/garbage — manual review
    "allow-exception": "allow-broad-exception",  # synonym
}

ROOTS = (
    "agentic_core",
    "apps_rg",
    "apps_shared",
    "apps_lic",
    "apps_eval",
    "apps_exec",
    "apps_research",
    "apps_underwriting_ai",
    "tools",
    "ops_scripts",
    "system_learning",
    "docs/archive/windsurf/legacy-tree/governance_scripts",
    "infrastructure",
)
EXCLUDE_PATS = (r"\\__pycache__\\", r"\\archives?\\", r"\\_archive\\", r"\\tools\\archive\\", r"\\tests\\")


def main() -> int:
    sites: dict[str, list[tuple[str, int, str]]] = defaultdict(list)
    for root in ROOTS:
        p = Path(root)
        if not p.exists():
            continue
        for py in p.rglob("*.py"):
            sp = str(py)
            if any(re.search(pat, sp) for pat in EXCLUDE_PATS):
                continue
            try:
                text = py.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                m = re.search(r"#\s*guardian:\s*(allow-[a-z0-9_\-]+)", line, re.I)
                if not m:
                    continue
                tok = m.group(1).lower()
                if tok in SINGLETONS:
                    sites[tok].append((sp, i, line.strip()))

    print("Singleton-token sites (for normalization):")
    for tok, replacement in SINGLETONS.items():
        rows = sites.get(tok, [])
        arrow = f" -> {replacement}" if replacement else " (NEEDS MANUAL REVIEW)"
        print(f"\n{tok}{arrow}  ({len(rows)} site(s))")
        for fp, ln, src in rows:
            print(f"  {fp}:{ln}")
            print(f"    {src[:140]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
