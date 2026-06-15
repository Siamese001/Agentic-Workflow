"""Span artifact export for L6 shadow evaluation.

The exporter is intentionally write-only to caller-supplied artifact paths. It
does not publish telemetry, mutate runtime state, or touch L4/UWG surfaces.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from agentic_core.L6_observability.shadow_eval.otel_spans import (
    L6SpanRecord,
    REQUIRED_SPAN_ATTRS,
    SPAN_NAMES,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def span_record_to_dict(span: L6SpanRecord) -> dict[str, object]:
    """Return a stable JSON-serializable dict for one recorded L6 span."""
    return asdict(span)


def build_span_export_bundle(
    records: Iterable[L6SpanRecord],
    *,
    source: str = "l6_shadow_eval",
) -> dict[str, object]:
    spans = [span_record_to_dict(record) for record in records]
    return {
        "schema_version": "l6_span_export.v1",
        "generated_at": _now_iso(),
        "source": source,
        "canonical_span_registry": list(SPAN_NAMES),
        "required_span_attrs": list(REQUIRED_SPAN_ATTRS),
        "span_count": len(spans),
        "spans": spans,
        "observer_law": {
            "runtime_feedback_edge_allowed": False,
            "current_run_mutation_allowed": False,
            "direct_l4_write_allowed": False,
        },
    }


def write_span_artifacts(
    records: Iterable[L6SpanRecord],
    artifact_dir: Path,
    *,
    json_name: str = "l6_span_artifacts.json",
    jsonl_name: str = "l6_span_artifacts.jsonl",
    source: str = "l6_shadow_eval",
) -> dict[str, Path]:
    """Write JSON and JSONL span artifacts and return their paths."""
    artifact_dir.mkdir(parents=True, exist_ok=True)
    bundle = build_span_export_bundle(records, source=source)
    json_path = artifact_dir / json_name
    json_path.write_text(
        json.dumps(bundle, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    jsonl_path = artifact_dir / jsonl_name
    with jsonl_path.open("w", encoding="utf-8", newline="\n") as handle:
        for span in bundle["spans"]:
            handle.write(json.dumps(span, sort_keys=True) + "\n")

    return {"span_export_json": json_path, "span_export_jsonl": jsonl_path}


__all__ = [
    "build_span_export_bundle",
    "span_record_to_dict",
    "write_span_artifacts",
]
