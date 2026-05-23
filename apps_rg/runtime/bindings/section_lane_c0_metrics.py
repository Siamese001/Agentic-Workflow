"""Section-lane C0 metrics emit/consume (artifact_dir-local c0_metrics.json).

Canonical generated lanes write metrics after FEC bridge wiring and consume them
for X2 gates, section_metric_receipt, and run_manifest fields.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.final_evidence_contract import (
    ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
    EvidenceItem,
    FinalEvidenceContract,
    STATUS_UNKNOWN,
    SUPPORT_STATUS_EMPTY,
    SUPPORT_STATUS_PASS,
    SUPPORT_STATUS_WEAK_WITH_CAVEATS,
)
from apps_rg.runtime.bindings.briefing_mode_classifier import classify_briefing_mode
from apps_rg.runtime.bindings.c0_metrics_writer import (
    SCHEMA_VERSION,
    build_c0_metrics,
)
from apps_rg.runtime.c0.c0_section_authority import proof_support_target
from apps_rg.runtime.bindings.c0_minimum_safety import is_c0_minimum_safe
from apps_rg.runtime.c0_mandatory_policy import is_c03_mandatory_section
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.spine.front_contracts import SectionFrontSpineBridge

_logger = logging.getLogger(__name__)

C0_METRICS_FILENAME = "c0_metrics.json"
_BLOCKING_SUPPORT_STATUSES = frozenset({SUPPORT_STATUS_EMPTY, "BLOCKED", STATUS_UNKNOWN})

# Section FEC bridge / C03 graph may emit product-facing labels; normalize before metrics.
_BRIDGE_SUPPORT_STATUS_NORMALIZE: dict[str, str] = {
    "SUPPORTED": SUPPORT_STATUS_PASS,
    "UNSUPPORTED": SUPPORT_STATUS_EMPTY,
    "PARTIAL": STATUS_UNKNOWN,
    "WEAK": STATUS_UNKNOWN,
}

# Mirrors apps_rg/runtime/schemas/c0_metrics.schema.json support_status enum.
CANONICAL_C0_METRICS_SUPPORT_STATUSES: frozenset[str] = frozenset(
    {
        SUPPORT_STATUS_PASS,
        SUPPORT_STATUS_WEAK_WITH_CAVEATS,
        "CONFLICTED",
        SUPPORT_STATUS_EMPTY,
        "BLOCKED",
        STATUS_UNKNOWN,
    }
)

_C0_METRICS_REQUIRED_KEYS: frozenset[str] = frozenset(
    {
        "schema_version",
        "run_id",
        "route_id",
        "retrieval_mode",
        "briefing_source_type",
        "company_brief_provenance",
        "source_class_coverage",
        "support_status",
        "support_target_met",
        "evidence_counts",
        "retrieval_sources",
        "excluded_evidence_refs",
        "blocked_source_refs",
        "freshness_receipts",
        "citation_map",
        "support_score_profile",
        "final_evidence_digest",
    }
)


def _read_json_dict(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):  # guardian: allow-return-empty-dict -- fail-soft read
        return {}
    return raw if isinstance(raw, dict) else {}


def _validated_request_payload(front_spine: SectionFrontSpineBridge) -> dict[str, Any]:
    vr = getattr(front_spine, "validated_request", None)
    if isinstance(vr, dict):
        return vr
    if vr is not None and hasattr(vr, "model_dump"):
        dumped = vr.model_dump()
        return dumped if isinstance(dumped, dict) else {}
    if vr is not None and hasattr(vr, "__dict__"):
        return {k: v for k, v in vars(vr).items() if not k.startswith("_")}
    return {}


def _resolve_route_id(artifact_dir: Path) -> str:
    rc = _read_json_dict(artifact_dir / "route_contract.json")
    rid = str(rc.get("route_id") or "").strip()
    return rid or "R3_SIMPLE_GROUNDED_READ"


def fec_from_section_bridge(
    bridge_doc: dict[str, Any],
    *,
    run_id: str,
) -> FinalEvidenceContract:
    """Reconstruct a governed FEC snapshot from section_fec_bridge for metrics extraction."""
    snap = bridge_doc.get("final_evidence_contract_snapshot")
    if not isinstance(snap, dict):
        snap = bridge_doc.get("final_evidence_contract")
    if not isinstance(snap, dict):
        snap = {}

    raw_status = str(
        bridge_doc.get("support_status")
        or snap.get("support_status")
        or SUPPORT_STATUS_EMPTY
    ).strip() or SUPPORT_STATUS_EMPTY
    support_status = _BRIDGE_SUPPORT_STATUS_NORMALIZE.get(raw_status, raw_status)

    items: list[EvidenceItem] = []
    for raw in bridge_doc.get("evidence_items") or ():
        if not isinstance(raw, dict):
            continue
        source = str(raw.get("source_fact_id") or raw.get("evidence_id") or "section_evidence")
        items.append(
            EvidenceItem(
                source=source,
                content=str(raw.get("content") or raw.get("content_digest") or source),
                source_id=source,
                source_type=str(raw.get("source_class") or bridge_doc.get("proof_source") or ""),
                allowed_prompt_slot=ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
            )
        )

    allowed_ids = list(bridge_doc.get("allowed_fact_ids") or bridge_doc.get("source_fact_ids") or ())
    if not items and allowed_ids:
        proof_source = str(bridge_doc.get("proof_source") or "proof_pool")
        for fid in allowed_ids:
            fid_s = str(fid)
            items.append(
                EvidenceItem(
                    source=fid_s,
                    content=fid_s,
                    source_id=fid_s,
                    source_type=proof_source,
                    allowed_prompt_slot=ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
                )
            )

    snap_target = snap.get("support_target_met")
    if isinstance(snap_target, bool):
        support_target_met = snap_target
    else:
        support_target_met = bool(items) and support_status in (
            SUPPORT_STATUS_PASS,
            SUPPORT_STATUS_WEAK_WITH_CAVEATS,
        )
    digest = str(snap.get("final_evidence_digest") or "").strip()
    if not digest and items:
        from apps_rg.runtime.bindings.c0_metrics_writer import _compute_evidence_digest

        digest = _compute_evidence_digest(
            FinalEvidenceContract(
                request_id=run_id,
                run_id=run_id,
                app_id="apps_rg",
                trace_id=run_id,
                evidence_items=tuple(items),
                support_status=support_status,
                support_target_met=support_target_met,
                l5_certification_ref="section-fec-bridge-metrics",
            )
        )

    return FinalEvidenceContract(
        request_id=run_id,
        run_id=run_id,
        app_id="apps_rg",
        trace_id=run_id,
        evidence_items=tuple(items),
        retrieval_sources=tuple(
            sorted(
                {
                    str(it.source_type or it.source).split(":", 1)[0]
                    for it in items
                    if str(it.source_type or it.source)
                }
            )
        ),
        support_target_met=support_target_met,
        support_status=support_status,
        final_evidence_digest=digest or None,
        l5_certification_ref="section-fec-bridge-metrics",
    )


def emit_section_lane_c0_metrics(
    artifact_dir: Path,
    *,
    section_id: str,
    runtime_payload: dict[str, Any],
    front_spine: SectionFrontSpineBridge,
) -> dict[str, Any] | None:
    """Write ``c0_metrics.json`` under ``artifact_dir`` and attach consume fields to payload."""
    if section_id not in GENERATED_LANES:
        return None
    bridge_doc = runtime_payload.get("section_fec_bridge")
    if not isinstance(bridge_doc, dict):
        _logger.warning("emit_section_lane_c0_metrics: missing section_fec_bridge for %s", section_id)
        return None

    run_id = str(runtime_payload.get("run_id") or artifact_dir.name)
    fec = fec_from_section_bridge(bridge_doc, run_id=run_id)
    chroma = os.environ.get("CHROMA_PERSIST_DIR", "").strip() or None
    briefing_decision = classify_briefing_mode(
        _validated_request_payload(front_spine),
        chroma_path_resolved=chroma,
    )
    data = build_c0_metrics(
        fec=fec,
        run_id=run_id,
        route_id=_resolve_route_id(artifact_dir),
        briefing_decision=briefing_decision,
        support_target=proof_support_target(),
    )
    path = artifact_dir / C0_METRICS_FILENAME
    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except OSError as exc:  # guardian: allow-return-none-swallow -- fail-soft optional artifact
        _logger.warning("emit_section_lane_c0_metrics write failed: %s", exc)
        return None

    runtime_payload["c0_metrics_ref"] = C0_METRICS_FILENAME
    runtime_payload["support_status"] = data.get("support_status")
    runtime_payload["support_target_met"] = data.get("support_target_met")
    runtime_payload["c0_metrics"] = data
    return data


def load_section_lane_c0_metrics(artifact_dir: Path) -> dict[str, Any] | None:
    """Consume lane-local ``c0_metrics.json`` if present."""
    path = artifact_dir / C0_METRICS_FILENAME
    if not path.is_file():
        return None
    doc = _read_json_dict(path)
    return doc or None


def _metrics_from_runtime_payload(runtime_payload: dict[str, Any]) -> dict[str, Any] | None:
    raw = runtime_payload.get("c0_metrics")
    return raw if isinstance(raw, dict) and raw else None


def materialize_section_lane_c0_metrics(
    artifact_dir: Path,
    metrics: dict[str, Any],
) -> Path | None:
    """Persist in-memory metrics to disk when X2/finalize needs the artifact file."""
    if not metrics:
        return None
    path = artifact_dir / C0_METRICS_FILENAME
    if path.is_file():
        return path
    try:
        path.write_text(
            json.dumps(metrics, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return path
    except OSError as exc:  # guardian: allow-return-none-swallow -- fail-soft optional artifact
        _logger.warning("materialize_section_lane_c0_metrics failed: %s", exc)
        return None


def resolve_section_lane_c0_metrics(
    artifact_dir: Path,
    runtime_payload: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Load metrics from disk, else runtime_payload / runtime_payload.json."""
    loaded = load_section_lane_c0_metrics(artifact_dir)
    if loaded:
        return loaded
    if runtime_payload:
        mem = _metrics_from_runtime_payload(runtime_payload)
        if mem:
            materialize_section_lane_c0_metrics(artifact_dir, mem)
            return mem
    disk_payload = _read_json_dict(artifact_dir / "runtime_payload.json")
    mem = _metrics_from_runtime_payload(disk_payload)
    if mem:
        materialize_section_lane_c0_metrics(artifact_dir, mem)
        return mem
    return None


def validate_c0_metrics_document(metrics: dict[str, Any]) -> tuple[bool, str]:
    """Lightweight structural validation (no jsonschema dependency)."""
    missing = _C0_METRICS_REQUIRED_KEYS - set(metrics.keys())
    if missing:
        return False, f"missing keys: {sorted(missing)}"
    if str(metrics.get("schema_version") or "") != SCHEMA_VERSION:
        return False, f"schema_version must be {SCHEMA_VERSION!r}"
    status = str(metrics.get("support_status") or "").strip()
    if status not in CANONICAL_C0_METRICS_SUPPORT_STATUSES:
        return False, f"support_status not canonical: {status!r}"
    counts = metrics.get("evidence_counts")
    if not isinstance(counts, dict):
        return False, "evidence_counts must be object"
    if not {"total", "excluded", "blocked"}.issubset(counts.keys()):
        return False, "evidence_counts missing total/excluded/blocked"
    return True, "ok"


def merge_c0_metrics_into_section_metric_receipt(
    receipt: dict[str, Any],
    runtime_payload: dict[str, Any],
) -> None:
    """Add ``c0_metrics_ref`` and support fields to section_metric_receipt."""
    ref = str(runtime_payload.get("c0_metrics_ref") or "").strip()
    if ref:
        receipt["c0_metrics_ref"] = ref
    if "support_status" in runtime_payload:
        receipt["support_status"] = runtime_payload.get("support_status")
    if "support_target_met" in runtime_payload:
        receipt["support_target_met"] = runtime_payload.get("support_target_met")


def c0_metrics_run_manifest_fields(artifact_dir: Path) -> dict[str, Any]:
    """Fields merged into ``run_manifest.json`` at finalize."""
    metrics = load_section_lane_c0_metrics(artifact_dir)
    if not metrics:
        return {}
    out: dict[str, Any] = {
        "c0_metrics_ref": C0_METRICS_FILENAME,
        "support_status": metrics.get("support_status"),
        "support_target_met": metrics.get("support_target_met"),
    }
    return {k: v for k, v in out.items() if v is not None}


def build_section_c0_metrics_x2_gates(
    metrics: dict[str, Any] | None,
    *,
    section_id: str,
) -> list[dict[str, Any]]:
    """Deterministic X2 gates for grounded (generated) lanes."""
    if not is_c03_mandatory_section(section_id):
        return []

    if metrics is None:
        return [
            {
                "gate_id": "x2_c0_metrics_artifact_present",
                "pass": False,
                "reason": f"missing {C0_METRICS_FILENAME}",
                "observed_value": None,
                "expected_value": SCHEMA_VERSION,
            },
            {
                "gate_id": "x2_c0_support_status_gate",
                "pass": False,
                "reason": "c0_metrics unavailable for support_status evaluation",
                "observed_value": None,
                "expected_value": "canonical support_status present",
            },
        ]

    struct_ok, struct_reason = validate_c0_metrics_document(metrics)
    schema_ok = str(metrics.get("schema_version") or "") == SCHEMA_VERSION
    support_status = str(metrics.get("support_status") or "").strip()
    support_target_met = bool(metrics.get("support_target_met"))
    enum_ok = support_status in CANONICAL_C0_METRICS_SUPPORT_STATUSES
    support_pass = bool(support_status) and support_status not in _BLOCKING_SUPPORT_STATUSES
    minimum_safe = is_c0_minimum_safe(support_status)
    artifact_ok = struct_ok and schema_ok

    return [
        {
            "gate_id": "x2_c0_metrics_artifact_present",
            "pass": artifact_ok,
            "reason": "c0_metrics artifact structurally valid" if artifact_ok else struct_reason,
            "observed_value": {
                "schema_version": metrics.get("schema_version"),
                "required_keys_present": sorted(_C0_METRICS_REQUIRED_KEYS & set(metrics.keys())),
            },
            "expected_value": SCHEMA_VERSION,
        },
        {
            "gate_id": "x2_c0_support_status_gate",
            "pass": enum_ok and support_pass and (minimum_safe or support_target_met),
            "reason": (
                f"support_status={support_status!r} support_target_met={support_target_met} "
                f"enum_ok={enum_ok} minimum_safe={minimum_safe}"
            ),
            "observed_value": {
                "support_status": support_status,
                "support_target_met": support_target_met,
                "c0_minimum_safe": minimum_safe,
                "canonical_enum": enum_ok,
            },
            "expected_value": "non-blocking canonical support_status with evidence target",
        },
    ]


def augment_section_x2_gates(
    gates: list[dict[str, Any]],
    artifact_dir: Path,
    section_id: str,
    *,
    runtime_payload: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Append C0 metrics X2 gates for generated lanes."""
    metrics = resolve_section_lane_c0_metrics(artifact_dir, runtime_payload)
    return list(gates) + build_section_c0_metrics_x2_gates(metrics, section_id=section_id)


__all__ = [
    "C0_METRICS_FILENAME",
    "CANONICAL_C0_METRICS_SUPPORT_STATUSES",
    "augment_section_x2_gates",
    "build_section_c0_metrics_x2_gates",
    "c0_metrics_run_manifest_fields",
    "emit_section_lane_c0_metrics",
    "fec_from_section_bridge",
    "load_section_lane_c0_metrics",
    "materialize_section_lane_c0_metrics",
    "merge_c0_metrics_into_section_metric_receipt",
    "resolve_section_lane_c0_metrics",
    "validate_c0_metrics_document",
]
