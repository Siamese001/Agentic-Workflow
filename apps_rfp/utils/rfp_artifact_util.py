"""
RFP Artifact Utilities — apps_rfp.

Helpers for artifact path resolution, manifest building,
and dry-run guards. Keeps RfpOrchestrator clean.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)


def resolve_artifact_path(output_dir: str, prefix: str, trace_id: str, ext: str) -> Path:
    """Resolve a deterministic artifact path.

    Args:
        output_dir: Base output directory.
        prefix: Filename prefix (e.g. "proposal", "manifest").
        trace_id: Run trace ID (first 8 chars used).
        ext: File extension without dot (e.g. "md", "json").

    Returns:
        Resolved Path object.
    """
    return Path(output_dir) / f"{prefix}_{trace_id[:8]}.{ext}"


def build_manifest(
    trace_id: str,
    industry: str,
    sections: list[str],
    roadmap_phases: int,
    risks: int,
) -> dict[str, Any]:
    """Build a JSON-serializable proposal manifest.

    Args:
        trace_id: Run trace ID.
        industry: Target industry key.
        sections: List of section IDs generated.
        roadmap_phases: Number of roadmap phases.
        risks: Number of risks identified.

    Returns:
        Dict suitable for JSON serialization.
    """
    return {
        "trace_id": trace_id,
        "industry": industry,
        "sections": sections,
        "roadmap_phases": roadmap_phases,
        "risks_identified": risks,
    }


def write_json(path: Path, data: dict[str, Any]) -> str:
    """Write JSON data to path, creating parent dirs as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    _log.debug("[rfp_artifact_util] Wrote %s", path)
    return str(path)


def is_dry_run(*flags: bool) -> bool:
    """Return True if any dry-run flag is set."""
    return any(flags)


__all__ = [
    "resolve_artifact_path",
    "build_manifest",
    "write_json",
    "is_dry_run",
]
