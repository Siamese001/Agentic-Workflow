"""
Evaluation Lab Artifact Utilities — apps_eval.

Helpers for artifact path resolution, scorecard CSV writing,
and manifest building. Keeps EvalOrchestrator clean.
"""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "eval_artifact_util", "uwg_governed_write")
_emit_writes_through("p1", "eval_artifact_util", "uwg_governed_write_2")
_emit_pulls_context("p1", "eval_artifact_util", "context_retrieval")
_emit_pulls_context("p1", "eval_artifact_util", "context_retrieval_2")
emit_determinism_digest("trace_eval_artifact_util", "eval_artifact_util_dispatch")
emit_determinism_digest("trace_eval_artifact_util", "eval_artifact_util_complete")
_emit_validated_by_safety_plane("p1", "eval_artifact_util", "safety_validation")

_log = logging.getLogger(__name__)


def resolve_artifact_path(output_dir: str, prefix: str, trace_id: str, ext: str) -> Path:
    """Resolve a deterministic artifact path."""
    return Path(output_dir) / f"{prefix}_{trace_id[:8]}.{ext}"


def write_scorecard_csv(path: Path, scorecard_rows: list[Any]) -> str:
    """Write scorecard rows to CSV.

    Args:
        path: Target CSV path.
        scorecard_rows: List of ScorecardRow objects.

    Returns:
        Absolute path string of written file.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["dimension_id", "display_name", "score", "weight", "weighted_score", "verdict"])
        for row in scorecard_rows:
            writer.writerow(
                [
                    row.dimension_id,
                    row.display_name,
                    f"{row.score:.4f}",
                    f"{row.weight:.1f}",
                    f"{row.weighted_score:.4f}",
                    row.verdict,
                ],
            )
    _log.debug("[eval_artifact_util] Wrote scorecard CSV %s", path)
    return str(path)


def build_manifest(
    trace_id: str,
    overall_score: float,
    suite_results: list[Any],
) -> dict[str, Any]:
    """Build a JSON-serializable eval manifest."""
    return {
        "trace_id": trace_id,
        "overall_score": overall_score,
        "suites": [
            {
                "suite_id": sr.suite_id,
                "pass_rate": sr.pass_rate,
                "scenarios": len(sr.scenarios),
            }
            for sr in suite_results
        ],
    }


def write_json(path: Path, data: dict[str, Any]) -> str:
    """Write JSON data to path, creating parent dirs as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    _log.debug("[eval_artifact_util] Wrote %s", path)
    return str(path)


def is_dry_run(*flags: bool) -> bool:
    """Return True if any dry-run flag is set."""
    return any(flags)


__all__ = [
    "resolve_artifact_path",
    "write_scorecard_csv",
    "build_manifest",
    "write_json",
    "is_dry_run",
]
