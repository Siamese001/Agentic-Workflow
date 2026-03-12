"""ADG execute_ssot Integration — pre-run impact analysis for SSOT flows.

Provides a lightweight integration seam for execute_ssot.py to call before
running any healing or validation phase. Returns a structured pre-run report
containing:
  - Blast radius of files in scope
  - Route mode recommendation (NORMAL / RESTRICTED / HUMAN_REVIEW)
  - Impacted tests (scoped, no silent full-suite fallback)
  - Layer violation signals relevant to the scope
  - Scope widening events (cross-layer dependencies)
  - Impact digest for audit trail

Usage from execute_ssot:
    from agentic_core.adg.applications.execute_ssot_integration import (
        PreRunADGReport,
        build_pre_run_report,
    )
    report = build_pre_run_report(changed_files=files_in_scope)
    if report.route_mode == "HUMAN_REVIEW":
        logger.warning("ADG: HUMAN_REVIEW threshold exceeded — %s", report.summary)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult

logger = logging.getLogger(__name__)


@dataclass
class PreRunADGReport:
    """Structured pre-run impact report for one execute_ssot invocation."""

    changed_files: list[str]
    impacted_module_count: int
    impacted_modules: list[str]
    impacted_test_count: int
    impacted_tests: list[str]
    risk_score: int
    route_mode: str
    scope_widening_events: list[str]
    uncovered_changed_files: list[str]
    layer_violation_count: int
    impact_digest: str
    adg_available: bool = True
    adg_error: str = ""

    @property
    def summary(self) -> str:
        return (
            f"route_mode={self.route_mode} "
            f"risk={self.risk_score} "
            f"impacted={self.impacted_module_count} modules "
            f"tests={self.impacted_test_count} "
            f"violations={self.layer_violation_count} "
            f"digest={self.impact_digest[:12]}"
        )

    def to_dict(self) -> dict:
        return {
            "changed_files": sorted(self.changed_files),
            "impacted_module_count": self.impacted_module_count,
            "impacted_modules": sorted(self.impacted_modules),
            "impacted_test_count": self.impacted_test_count,
            "impacted_tests": sorted(self.impacted_tests),
            "risk_score": self.risk_score,
            "route_mode": self.route_mode,
            "scope_widening_events": sorted(self.scope_widening_events),
            "uncovered_changed_files": sorted(self.uncovered_changed_files),
            "layer_violation_count": self.layer_violation_count,
            "impact_digest": self.impact_digest,
            "adg_available": self.adg_available,
            "adg_error": self.adg_error,
            "summary": self.summary,
        }

    @classmethod
    def unavailable(cls, changed_files: list[str], reason: str) -> "PreRunADGReport":
        """Return a degraded report when ADG is unavailable."""
        return cls(
            changed_files=sorted(changed_files),
            impacted_module_count=0,
            impacted_modules=[],
            impacted_test_count=0,
            impacted_tests=[],
            risk_score=0,
            route_mode="NORMAL",
            scope_widening_events=[],
            uncovered_changed_files=sorted(changed_files),
            layer_violation_count=0,
            impact_digest="",
            adg_available=False,
            adg_error=reason,
        )


def build_pre_run_report(
    changed_files: list[str],
    repo_root: Path | None = None,
    force_fresh: bool = False,
) -> PreRunADGReport:
    """Build an ADG pre-run report for the given changed files.

    Gracefully degrades: if ADG is unavailable, returns a report with
    adg_available=False and adg_error explaining why. Never raises.

    Parameters
    ----------
    changed_files:
        Repo-relative forward-slash paths of files being processed.
    repo_root:
        Repository root. Defaults to cwd.
    force_fresh:
        If True, bypass the ADG cache and run a fresh scan.
    """
    repo_root = Path(repo_root) if repo_root else Path.cwd()
    norm_files = [f.replace("\\", "/") for f in (changed_files or [])]

    try:
        from agentic_core.adg.runtime.cache_loader import load_or_scan
        from tools.change_impact_engine import ChangeImpactEngine

        result = load_or_scan(repo_root=str(repo_root))
        engine = ChangeImpactEngine(result, repo_root=repo_root)
        impact = engine.analyze(norm_files, include_tests=True)

        # Count layer violations in blast radius
        layer_violation_count = _count_layer_violations_in_scope(
            result, impact.impacted_modules
        )

        return PreRunADGReport(
            changed_files=impact.changed_files,
            impacted_module_count=len(impact.impacted_modules),
            impacted_modules=impact.impacted_modules,
            impacted_test_count=len(impact.impacted_tests),
            impacted_tests=impact.impacted_tests,
            risk_score=impact.risk_score,
            route_mode=impact.route_mode,
            scope_widening_events=impact.scope_widening_events,
            uncovered_changed_files=impact.uncovered_changed_files,
            layer_violation_count=layer_violation_count,
            impact_digest=impact.impact_digest,
            adg_available=True,
            adg_error="",
        )

    # guardian: allow-silent-swallow
    except Exception as exc:  # guardian: allow-silent-swallower
        logger.warning(
            "ADG pre-run report unavailable: %s — proceeding without impact analysis",
            exc,
        )
        return PreRunADGReport.unavailable(norm_files, str(exc))


def _count_layer_violations_in_scope(result: ScanResult, impacted_modules: list[str]) -> int:
    """Count import edges among impacted_modules that violate layer rules."""
    from agentic_core.adg.schema import ALLOWED_LAYER_EDGES, module_path_to_layer

    impacted_set = set(impacted_modules)
    count = 0
    for edge in result.edges:
        if edge.relation_type != "imports":
            continue
        module_prefix = "ADG::Module::"
        from_path = edge.from_name[len(module_prefix):] if edge.from_name.startswith(module_prefix) else ""
        to_path = edge.to_name[len(module_prefix):] if edge.to_name.startswith(module_prefix) else ""
        if from_path not in impacted_set or to_path not in impacted_set:
            continue
        fl = module_path_to_layer(from_path)
        tl = module_path_to_layer(to_path)
        if fl != tl and (fl, tl) not in ALLOWED_LAYER_EDGES:
            count += 1
    return count


def emit_pre_run_log(report: PreRunADGReport) -> None:
    """Emit structured log lines for the pre-run ADG report."""
    if not report.adg_available:
        logger.warning("ADG pre-run: UNAVAILABLE — %s", report.adg_error)
        return

    level = logging.WARNING if report.route_mode != "NORMAL" else logging.INFO
    logger.log(
        level,
        "ADG pre-run: %s",
        report.summary,
    )
    if report.scope_widening_events:
        logger.info(
            "ADG pre-run: scope widening into %d module(s): %s",
            len(report.scope_widening_events),
            report.scope_widening_events[:5],
        )
    if report.uncovered_changed_files:
        logger.info(
            "ADG pre-run: %d changed file(s) not in ADG index (blind spots): %s",
            len(report.uncovered_changed_files),
            report.uncovered_changed_files[:5],
        )


__all__ = [
    "PreRunADGReport",
    "build_pre_run_report",
    "emit_pre_run_log",
]
