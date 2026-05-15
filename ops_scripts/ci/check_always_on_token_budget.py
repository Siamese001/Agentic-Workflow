"""CI gate — enforce Anthropic two-tier compliance for always_on rules.

Per Anthropic's "Architecture of Agentic RAG" (Apr 2026), knowledge files /
always-on rules exceeding ~50 KB / 12,000 tokens trigger autonomous context
compaction, where the model arbitrarily discards instructions to free space.

This gate sums the bytes of every `.cursor/rules/*.md` file with frontmatter
`trigger: always_on` and fails the commit if the total exceeds the threshold.

Threshold:
- 51,200 bytes  (50 KB hard limit per Anthropic doctrine)
- 12,800 tokens (≈ bytes / 4)

Bypass: ALWAYS_ON_BUDGET_BYPASS=1 environment variable.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

THRESHOLD_BYTES = 51_200
REPO_ROOT = Path(__file__).resolve().parents[2]
RULES_DIR = REPO_ROOT / ".windsurf" / "rules"
TRIGGER_RE = re.compile(r"^trigger:\s*(\w+)", re.MULTILINE)


def _scan() -> tuple[int, list[tuple[int, str]]]:
    total = 0
    rows: list[tuple[int, str]] = []
    for f in sorted(RULES_DIR.glob("*.md")):
        try:
            txt = f.read_text(encoding="utf-8")
        except OSError:
            continue
        m = TRIGGER_RE.search(txt)
        if m and m.group(1) == "always_on":
            sz = len(txt.encode("utf-8"))
            rows.append((sz, f.name))
            total += sz
    rows.sort(reverse=True)
    return total, rows


def main() -> int:
    if os.environ.get("ALWAYS_ON_BUDGET_BYPASS") == "1":
        print(
            "[always-on-budget] BYPASS via ALWAYS_ON_BUDGET_BYPASS=1",
            file=sys.stderr,
        )
        return 0

    total, rows = _scan()
    print(f"always_on rules: {len(rows)}")
    for sz, name in rows:
        print(f"  {sz:>6}  {name}")
    print(f"\nTOTAL: {total:,} bytes (~{total // 4:,} tokens)")
    print(f"Threshold: {THRESHOLD_BYTES:,} bytes ({THRESHOLD_BYTES // 4:,} tokens)")

    if total > THRESHOLD_BYTES:
        delta = total - THRESHOLD_BYTES
        pct = delta / THRESHOLD_BYTES * 100
        print(
            f"\n[always-on-budget] FAIL: {delta:,} bytes over ({pct:.1f}% over)",
            file=sys.stderr,
        )
        print(
            "Anthropic doctrine: always_on >50 KB triggers context compaction.",
            file=sys.stderr,
        )
        print(
            "Demote a rule to trigger=model_decision or trim procedural detail "
            "to a skill.",
            file=sys.stderr,
        )
        print("Bypass: ALWAYS_ON_BUDGET_BYPASS=1", file=sys.stderr)
        return 1

    print(f"\n[always-on-budget] PASS ({THRESHOLD_BYTES - total:,} bytes under threshold)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
