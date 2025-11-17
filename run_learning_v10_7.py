"""Meta-learning runner for v10_7 runtime.

This module exposes ``run_meta_learning`` for tests to import and execute without
requiring external services. The function consumes feedback logs and produces a
lightweight summary to validate the meta-learning loop wiring.
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from core_v10_7.config import ConfigV10_7
from core_v10_7.context import WorkflowContext


async def _read_feedback_entries(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    entries: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


async def _persist_summary(path: Path, summary: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)


async def run_meta_learning(config: ConfigV10_7, feedback_log_path: Optional[str] = None) -> Dict[str, Any]:
    """Execute a deterministic meta-learning pass.

    The implementation is intentionally lightweight: it loads feedback entries,
    aggregates simple metrics, and stores a summary on disk. This keeps the
    workflow testable without external model calls while exercising the
    meta-learning plumbing.
    """

    feedback_path = Path(feedback_log_path or config.telemetry.get("feedback_log_path", "feedback.log"))
    output_path = Path(config.telemetry.get("meta_learning_output", "meta_learning_summary.json"))

    context = WorkflowContext(config)
    feedback_entries = await _read_feedback_entries(feedback_path)

    metrics = {
        "total_entries": len(feedback_entries),
        "workflow_ids": sorted({entry.get("workflow_id", "unknown") for entry in feedback_entries}),
    }

    context.metrics_collector.record("meta_learning_entries", metrics["total_entries"])

    summary = {
        "meta_learning_enabled": bool(getattr(config, "meta_loop_config", {}).get("enable_meta_learning", False)),
        "feedback_path": str(feedback_path),
        "output_path": str(output_path),
        "metrics": metrics,
    }

    await _persist_summary(output_path, summary)
    await asyncio.sleep(0)
    return summary


__all__ = ["run_meta_learning"]
