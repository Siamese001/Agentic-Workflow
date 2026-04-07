"""
Research Artifact Utilities — apps_research.

Helpers for artifact path resolution, source register serialization,
and dry-run guards. Keeps ResearchOrchestrator clean.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)


def resolve_artifact_path(output_dir: str, prefix: str, trace_id: str, ext: str) -> Path:
    """Resolve a deterministic artifact path."""
    return Path(output_dir) / f"{prefix}_{trace_id[:8]}.{ext}"


def serialize_source_register(sources: list[Any]) -> list[dict[str, Any]]:
    """Serialize a list of SourceEntry objects to dicts.

    Args:
        sources: List of SourceEntry objects with source_id, title,
                 claim_type, confidence, summary, url, section_id fields.

    Returns:
        List of dicts suitable for JSON serialization.
    """
    result = []
    for s in sources:
        result.append(
            {
                "source_id": s.source_id,
                "title": s.title,
                "claim_type": s.claim_type.value if hasattr(s.claim_type, "value") else str(s.claim_type),
                "confidence": s.confidence,
                "summary": s.summary,
                "url": s.url,
                "section_id": s.section_id,
            },
        )
    return result


def write_json(path: Path, data: Any) -> str:
    """Write JSON data to path, creating parent dirs as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    _log.debug("[research_artifact_util] Wrote %s", path)
    return str(path)


def is_dry_run(*flags: bool) -> bool:
    """Return True if any dry-run flag is set."""
    return any(flags)


__all__ = [
    "resolve_artifact_path",
    "serialize_source_register",
    "write_json",
    "is_dry_run",
]
