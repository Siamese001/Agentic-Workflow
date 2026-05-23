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
SPINE_SPAN_COVERAGE_RECEIPT = "spine_span_coverage_receipt.json"

REQUIRED_PRODUCT_SPINE_LAYERS: tuple[str, ...] = tuple(
    row.layer_key for row in APPS_RG_SPINE_SPAN_CHECKLIST
)


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
    otel_attempted = _otel_sdk_enabled()
    otel_ok = False
    if otel_attempted:
        otel_ok = _try_otel_span(
            layer_key=layer_key,
            binding_seam=binding_seam,
            status=status,
            extra=extra,
        )
    event["otel_dual_write_attempted"] = otel_attempted
    event["otel_dual_write_ok"] = otel_ok
    if otel_attempted:
        event["proof_classification"] = (
            "otel_sdk_and_receipt" if otel_ok else "receipt_fallback_otel_unavailable"
        )
    path = root / SPINE_SPAN_RECEIPT
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    return path


def _otel_sdk_enabled() -> bool:
    return os.environ.get("APPS_RG_SPINE_OTEL_SDK", "").strip().lower() in ("1", "true", "yes")


def _try_otel_span(
    *,
    layer_key: str,
    binding_seam: str,
    status: str,
    extra: dict[str, Any] | None,
) -> bool:
    """Best-effort OTEL span when SDK enabled; never raises (receipt remains SSOT)."""
    if not _otel_sdk_enabled():
        return False
    try:
        from opentelemetry import trace  # type: ignore[import-untyped]

        tracer = trace.get_tracer("apps_rg.spine")
        with tracer.start_as_current_span(f"apps_rg.spine.{layer_key}") as span:
            span.set_attribute("apps_rg.layer_key", layer_key)
            span.set_attribute("apps_rg.binding_seam", binding_seam)
            span.set_attribute("apps_rg.status", status)
            if extra:
                for key, value in extra.items():
                    if isinstance(value, (str, int, float, bool)):
                        span.set_attribute(f"apps_rg.extra.{key}", value)
        return True
    except Exception:
        return False


def audit_spine_span_emit_sites() -> dict[str, object]:
    """Static emit-site audit for CI (W4)."""
    from system_learning.runtime_adg.span_contracts import APPS_RG_SPINE_SPAN_CHECKLIST

    repo = Path(__file__).resolve().parents[3]
    rows: list[dict[str, object]] = []
    for item in APPS_RG_SPINE_SPAN_CHECKLIST:
        rel = str(item.binding_seam).replace("\\", "/")
        path = repo / rel
        ok = path.is_file()
        rows.append({"layer_key": item.layer_key, "binding_seam": rel, "file_exists": ok})
    return {"row_count": len(rows), "rows": rows}


def read_spine_span_layer_keys(artifact_dir: Path | str | None) -> tuple[str, ...]:
    if artifact_dir is None:
        return ()
    path = Path(artifact_dir) / SPINE_SPAN_RECEIPT
    if not path.is_file():
        return ()
    layers: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        doc = json.loads(line)
        key = str(doc.get("layer_key") or "")
        if key:
            layers.append(key)
    return tuple(layers)


def validate_spine_span_coverage(
    artifact_dir: Path | str | None,
    *,
    required_layers: tuple[str, ...] | None = None,
    product_visible: bool = True,
) -> dict[str, Any]:
    """Return coverage report; ``complete`` when all required layer_keys appear in receipt log."""
    required = required_layers or REQUIRED_PRODUCT_SPINE_LAYERS
    if not spine_span_emit_enabled(product_visible=product_visible):
        return {
            "schema_version": "apps_rg_spine_span_coverage_v1",
            "complete": True,
            "skipped": True,
            "reason": "span_emit_disabled",
            "required_layers": list(required),
            "observed_layers": [],
            "missing_layers": [],
        }
    observed = list(read_spine_span_layer_keys(artifact_dir))
    observed_set = set(observed)
    missing = [layer for layer in required if layer not in observed_set]
    return {
        "schema_version": "apps_rg_spine_span_coverage_v1",
        "complete": len(missing) == 0,
        "skipped": False,
        "required_layers": list(required),
        "observed_layers": observed,
        "missing_layers": missing,
        "proof_classification": "receipt_fallback_not_otel_sdk",
    }


def emit_spine_span_coverage_receipt(
    artifact_dir: Path | str | None,
    *,
    product_visible: bool = True,
    required_layers: tuple[str, ...] | None = None,
) -> Path | None:
    if artifact_dir is None:
        return None
    root = Path(artifact_dir)
    root.mkdir(parents=True, exist_ok=True)
    report = validate_spine_span_coverage(
        root,
        required_layers=required_layers,
        product_visible=product_visible,
    )
    report["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    path = root / SPINE_SPAN_COVERAGE_RECEIPT
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


__all__ = [
    "REQUIRED_PRODUCT_SPINE_LAYERS",
    "SPINE_SPAN_COVERAGE_RECEIPT",
    "SPINE_SPAN_RECEIPT",
    "emit_spine_span_coverage_receipt",
    "emit_spine_span_event",
    "read_spine_span_layer_keys",
    "spine_span_emit_enabled",
    "validate_spine_span_coverage",
    "audit_spine_span_emit_sites",
    "_otel_sdk_enabled",
]
