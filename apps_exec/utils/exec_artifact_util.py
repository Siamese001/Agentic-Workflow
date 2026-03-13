"""
Executive Brief Artifact Utilities — apps_exec.

Helpers for artifact path resolution, manifest building,
and dry-run guards. Keeps orchestrator clean.
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
        prefix: Filename prefix (e.g. "brief", "manifest").
        trace_id: Run trace ID (first 8 chars used).
        ext: File extension without dot (e.g. "md", "json").

    Returns:
        Resolved Path object (parent dirs not created here).
    """
    out = Path(output_dir)
    return out / f"{prefix}_{trace_id[:8]}.{ext}"


def build_manifest(trace_id: str, audience: str, sections: list[str]) -> dict[str, Any]:
    """Build a JSON-serializable artifact manifest.

    Args:
        trace_id: Run trace ID.
        audience: Target persona key.
        sections: List of section IDs included in the brief.

    Returns:
        Dict suitable for JSON serialization.
    """
    return {
        "trace_id": trace_id,
        "audience": audience,
        "sections": sections,
        "section_count": len(sections),
    }


def write_json(path: Path, data: dict[str, Any]) -> str:
    """Write JSON data to path, creating parent dirs as needed.

    Args:
        path: Target file path.
        data: Dict to serialize.

    Returns:
        Absolute path string of written file.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    _log.debug("[exec_artifact_util] Wrote %s", path)
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
