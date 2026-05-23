"""Apps_rg spine span emit receipts — REQ parent checklist (W8 follow-up).

Filesystem receipt fallback until full OTEL semconv on every product lane.
Append-only ``spine_span_emit_receipt.jsonl`` under the section artifact dir.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from system_learning.runtime_adg.span_contracts import APPS_RG_SPINE_SPAN_CHECKLIST

SPINE_SPAN_RECEIPT = "spine_span_emit_receipt.jsonl"


def spine_span_emit_enabled(*, product_visible: bool = True) -> bool:
    if os.environ.get("APPS_RG_SPINE_SPAN_EMIT", "").strip().lower() in ("0", "false", "no"):
        return False
    if os.environ.get("APPS_RG_SPINE_SPAN_EMIT", "").strip().lower() in ("1", "true", "yes"):
        return True
    return bool(product_visible)


def _row_for_layer(layer_key: str) -> dict[str, Any] | None:
    for row in APPS_RG_SPINE_SPAN_CHECKLIST:
        if row.layer_key == layer_key:
            return {
                "req_parent": row.req_parent,
                "tier2_stage": row.tier2_stage,
                "span_patterns": list(row.span_patterns),
                "spine_receipt_fallback": row.spine_receipt_fallback,
            }
    return None


def emit_spine_span_event(
    artifact_dir: Path | str | None,
    *,
    layer_key: str,
    binding_seam: str,
    status: str = "receipt_emitted",
    extra: dict[str, Any] | None = None,
    product_visible: bool = True,
) -> Path | None:
    """Append one span checklist row to the artifact dir receipt log."""
    if artifact_dir is None:
        return None
    if not spine_span_emit_enabled(product_visible=product_visible):
        return None
    root = Path(artifact_dir)
    root.mkdir(parents=True, exist_ok=True)
    meta = _row_for_layer(layer_key) or {}
    event = {
        "schema_version": "apps_rg_spine_span_emit_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "layer_key": layer_key,
        "binding_seam": binding_seam,
        "status": status,
        "proof_classification": "receipt_fallback_not_otel_sdk",
        **meta,
    }
    if extra:
        event["extra"] = extra
    path = root / SPINE_SPAN_RECEIPT
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    return path


__all__ = ["SPINE_SPAN_RECEIPT", "emit_spine_span_event", "spine_span_emit_enabled"]
