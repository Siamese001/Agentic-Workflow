"""
Phase 3 helper -- scan the test directories for references to anchor symbols.

For each anchor symbol that appeared in any IMPLEMENTED_CANDIDATE or
AMBIGUOUS_CANDIDATE mapping, find which test files mention it. A simple
substring match is sufficient; this is a recall-oriented signal feeding
into the coverage_matrix.

The scanner returns:
    {anchor: [(test_relative_path, line_count_with_match), ...]}

Only test files with at least one occurrence of the anchor are listed.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from agentic_core.runtime.prove_requirements.layer_paths import TEST_PATH_ROOTS


SKIP_DIRS = frozenset({"__pycache__", ".pytest_cache"})


@dataclass(frozen=True)
class TestHit:
    anchor: str
    relative_path: str
    occurrences: int


def _walk_test_files(repo_root: Path) -> List[Path]:
    out: List[Path] = []
    for root in TEST_PATH_ROOTS:
        base = repo_root / root
        if not base.exists():
            continue
        for p in base.rglob("test_*.py"):
            if any(part in SKIP_DIRS for part in p.parts):
                continue
            out.append(p)
    return sorted(out)


def scan_test_files_for_anchors(
    repo_root: Path,
    anchors: Iterable[str],
) -> Dict[str, List[TestHit]]:
    """Return {anchor: [TestHit, ...]} for anchors with >=1 occurrence."""
    anchor_set = sorted({a for a in anchors if a and len(a) >= 4})
    if not anchor_set:
        return {}
    # Build a single regex with word boundaries for fast pass.
    escaped = "|".join(re.escape(a) for a in anchor_set)
    pattern = re.compile(rf"\b({escaped})\b")

    hits: Dict[str, List[TestHit]] = defaultdict(list)
    for tf in _walk_test_files(repo_root):
        try:
            text = tf.read_text(encoding="utf-8", errors="replace")
        except (OSError, IOError):
            continue
        # Count per-anchor occurrences.
        counts: Dict[str, int] = defaultdict(int)
        for m in pattern.finditer(text):
            counts[m.group(1)] += 1
        if not counts:
            continue
        rel = tf.relative_to(repo_root).as_posix()
        for anchor, count in counts.items():
            hits[anchor].append(TestHit(anchor=anchor, relative_path=rel, occurrences=count))
    return dict(hits)
