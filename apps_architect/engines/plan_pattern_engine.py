"""Plan file pattern extractor — parses .windsurf/plans/*.md for methodological patterns.

Plan: ``.windsurf/plans/apps-architect-pattern-hardening-d7e4f9.md`` W2.P2.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

from apps_architect.types.architect_types import Pattern, PatternType

_log = logging.getLogger(__name__)

_PLANS_DIR = Path(__file__).resolve().parents[2] / ".windsurf" / "plans"
_YAML_FRONT_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
_WAVE_RE = re.compile(r"\|\s*W\d+\s*\|")
_PHASE_RE = re.compile(r"\|\s*\d+\.\d+\s*\|")
_ADG_MV_RE = re.compile(r"`(adg_mv_\w+|adg_p_view_query|adg_blast_radius)`")
_FEC_RE = re.compile(r"(fec_producer|produce_fec|resolve_fec|FinalEvidenceContract)")
_EXIT_V6_RE = re.compile(r"(Exit\s*v6|maybe_invoke_exit_eval|exit_eval)")


def _extract_frontmatter(text: str) -> dict[str, str]:
    m = _YAML_FRONT_RE.search(text)
    if not m:
        return {}
    result: dict[str, str] = {}
    for line in m.group(1).split("\n"):
        if ":" in line:
            k, _, v = line.partition(":")
            result[k.strip()] = v.strip()
    return result


def _count_matches(pattern: re.Pattern, text: str) -> int:
    return len(pattern.findall(text))


class PlanPatternEngine:
    """Extracts methodological patterns from plan markdown files."""

    def __init__(self, plans_dir: str | Path | None = None) -> None:
        self._plans_dir = Path(plans_dir) if plans_dir else _PLANS_DIR

    def extract_from_file(self, filepath: Path) -> list[Pattern]:
        try:
            text = filepath.read_text(encoding="utf-8")
        except Exception:
            return []

        fm = _extract_frontmatter(text)
        patterns: list[Pattern] = []

        wave_count = _count_matches(_WAVE_RE, text)
        phase_count = _count_matches(_PHASE_RE, text)
        if wave_count > 0:
            patterns.append(Pattern.from_source(
                pattern_type=PatternType.PLAN,
                source_ref=str(filepath.relative_to(filepath.parents[2])),
                content=f"waves={wave_count} phases={phase_count}",
                summary=f"Plan with {wave_count} waves, {phase_count} phases",
                tags=("plan_structure",),
            ))

        adg_count = _count_matches(_ADG_MV_RE, text)
        if adg_count > 0:
            patterns.append(Pattern.from_source(
                pattern_type=PatternType.PLAN,
                source_ref=str(filepath.relative_to(filepath.parents[2])),
                content=f"adg_references={adg_count}",
                summary=f"ADG graph-layer usage: {adg_count} references",
                tags=("adg_evidence",),
            ))

        if _FEC_RE.search(text):
            patterns.append(Pattern.from_source(
                pattern_type=PatternType.PLAN,
                source_ref=str(filepath.relative_to(filepath.parents[2])),
                content="fec_wiring=true",
                summary="FEC producer wiring pattern",
                tags=("fec", "cert"),
            ))

        if _EXIT_V6_RE.search(text):
            patterns.append(Pattern.from_source(
                pattern_type=PatternType.PLAN,
                source_ref=str(filepath.relative_to(filepath.parents[2])),
                content="exit_v6=true",
                summary="Exit v6 integration pattern",
                tags=("exit_v6", "observability"),
            ))

        return patterns

    def extract_all(self, max_files: int = 200) -> Tuple[Pattern, ...]:
        all_patterns: list[Pattern] = []
        plan_files = sorted(self._plans_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        for fp in plan_files[:max_files]:
            all_patterns.extend(self.extract_from_file(fp))
        return tuple(all_patterns)


__all__ = ["PlanPatternEngine"]
