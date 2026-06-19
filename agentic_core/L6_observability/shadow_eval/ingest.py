"""06.1 — Runtime Exhaust Ingest and Normalization.

Implements the 6A pipeline:
  I1 receive completed-run marker
  I2 collect source refs
  I3 validate lineage keys
  I4 build StageMap
  I5 build ArtifactInventory
  I6 normalize records
  I7 stratify run outcome

All functions are pure: they consume sealed exhaust dicts and emit dataclass
contracts. There are no L4 writes, no live runtime calls, and no mutation of
inputs. Inputs that look in-flight or non-sealed are rejected at the marker.
"""

from __future__ import annotations

import uuid
from dataclasses import replace
from typing import Any, Mapping, Sequence

from agentic_core.L6_observability.shadow_eval._digest import stamp_digest
from agentic_core.L6_observability.shadow_eval.contracts import (
    RUN_OUTCOME_CLASSES,
    ArtifactInventory,
    ExhaustGapReport,
    ExhaustSourceManifest,
    NormalizedEvidenceRecord,
    RuntimeExhaustBundle,
    StageMap,
)


class IngestError(Exception):
    """Raised when ingest preconditions are violated."""


# Reason codes used across the package
REASON_LIVE_RUN_NOT_CLOSED = "LIVE_RUN_NOT_CLOSED"
REASON_EXIT_DISPOSITION_MISSING = "EXIT_DISPOSITION_MISSING"
REASON_TRACE_LINK_MISSING = "TRACE_LINK_MISSING"
REASON_ORPHAN_ARTIFACT = "ORPHAN_ARTIFACT"
REASON_IMPOSSIBLE_STAGE_ORDER = "IMPOSSIBLE_STAGE_ORDER"
REASON_POLICY_HASH_MISMATCH = "POLICY_HASH_MISMATCH"
REASON_REPLAY_KEY_MISSING = "REPLAY_KEY_MISSING"
REASON_UNKNOWN_PROVIDER_FALLBACK = "UNKNOWN_PROVIDER_FALLBACK"
REASON_CERT_REF_MISSING = "L5_CERT_REF_MISSING"
REASON_CERT_REF_UNRESOLVED = "L5_CERT_REF_UNRESOLVED"
MISSING_CERT_REF_SENTINEL = "l5-cert-ref:MISSING"  # valid non-empty sentinel for gap-analysis bundles
UNRESOLVED_CERT_REF_PREFIXES = ("l5-cert-ref:apps_eval:",)

# Canonical pipeline stages used by StageMap.expected_stages.
EXPECTED_STAGES = ("U0", "L1", "L0", "C0", "PA", "L3", "L2", "EXIT", "UWG")


def _gen_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


def is_missing_l5_certification_ref(value: object | None) -> bool:
    ref = str(value or "").strip()
    return not ref or ref == MISSING_CERT_REF_SENTINEL


def is_unresolved_l5_certification_ref(value: object | None) -> bool:
    """Return True for placeholder/generated refs that are not L5 artifacts."""
    ref = str(value or "").strip()
    if is_missing_l5_certification_ref(ref):
        return True
    return any(ref.startswith(prefix) for prefix in UNRESOLVED_CERT_REF_PREFIXES)


# ---------------------------------------------------------------------------
# I1 — receive completed-run marker
# ---------------------------------------------------------------------------


def receive_completed_run_marker(
    raw_exhaust: Mapping[str, Any],
    *,
    repair_fixture: bool = False,
) -> Mapping[str, Any]:
    """Refuse live/in-flight runs; require Exit disposition or repair fixture.

    Returns the same mapping unmodified after validation.
    Raises ``IngestError`` on policy violation.
    """
    if not raw_exhaust.get("runtime_boundary_crossed"):
        raise IngestError(REASON_LIVE_RUN_NOT_CLOSED)
    if not raw_exhaust.get("exit_disposition_ref") and not repair_fixture:
        raise IngestError(REASON_EXIT_DISPOSITION_MISSING)
    if not raw_exhaust.get("completed_at"):
        raise IngestError(REASON_LIVE_RUN_NOT_CLOSED)
    return raw_exhaust


# ---------------------------------------------------------------------------
# I2 — collect source refs (no live recompute)
# ---------------------------------------------------------------------------


def collect_source_refs(raw_exhaust: Mapping[str, Any]) -> list[ExhaustSourceManifest]:
    manifests: list[ExhaustSourceManifest] = []
    for entry in raw_exhaust.get("source_exhaust", []) or []:
        manifests.append(
            ExhaustSourceManifest(
                manifest_id=_gen_id("manifest"),
                source_type=str(entry.get("source_type", "unknown")),
                source_ref=str(entry.get("source_ref", "")),
                source_hash=str(entry.get("source_hash", "")),
                source_schema_version=str(entry.get("source_schema_version", "v1")),
                observed_stage=str(entry.get("observed_stage", "UNKNOWN")),
                expected_stage_order=int(entry.get("expected_stage_order", -1)),
                lineage_parent_refs=list(entry.get("lineage_parent_refs", [])),
                lineage_child_refs=list(entry.get("lineage_child_refs", [])),
                completeness_status=str(entry.get("completeness_status", "UNKNOWN")),
                trust_status=str(entry.get("trust_status", "UNKNOWN")),
                gap_codes=list(entry.get("gap_codes", [])),
            )
        )
    return manifests


# ---------------------------------------------------------------------------
# I3 — validate lineage keys (collect gap codes)
# ---------------------------------------------------------------------------


def validate_lineage(
    raw_exhaust: Mapping[str, Any],
    manifests: Sequence[ExhaustSourceManifest],
) -> list[str]:
    gap_codes: list[str] = []
    if not raw_exhaust.get("trace_root"):
        gap_codes.append(REASON_TRACE_LINK_MISSING)
    if not raw_exhaust.get("policy_hash"):
        gap_codes.append(REASON_POLICY_HASH_MISMATCH)
    if not raw_exhaust.get("replay_key"):
        gap_codes.append(REASON_REPLAY_KEY_MISSING)
    if is_missing_l5_certification_ref(raw_exhaust.get("l5_certification_ref")):
        gap_codes.append(REASON_CERT_REF_MISSING)
    elif is_unresolved_l5_certification_ref(raw_exhaust.get("l5_certification_ref")):
        gap_codes.append(REASON_CERT_REF_UNRESOLVED)
    # Orphan artifacts (those without lineage parents AND not stage-anchored).
    for m in manifests:
        if not m.lineage_parent_refs and m.observed_stage == "UNKNOWN":
            gap_codes.append(REASON_ORPHAN_ARTIFACT)
            break
    return gap_codes


# ---------------------------------------------------------------------------
# I4 — build StageMap
# ---------------------------------------------------------------------------


def build_stage_map(
    raw_exhaust: Mapping[str, Any],
    manifests: Sequence[ExhaustSourceManifest],
) -> StageMap:
    observed = sorted({m.observed_stage for m in manifests if m.observed_stage != "UNKNOWN"})
    expected = list(EXPECTED_STAGES)
    missing: list[str] = []
    for required in ("U0", "L1", "L0", "L2", "EXIT"):
        if required not in observed:
            missing.append(required)

    impossible: list[str] = []
    # Any manifest claiming UWG before EXIT is impossible.
    if "UWG" in observed and "EXIT" not in observed:
        impossible.append("UWG_BEFORE_EXIT")

    orphan_refs = [
        m.source_ref for m in manifests if not m.lineage_parent_refs and m.observed_stage == "UNKNOWN"
    ]

    return StageMap(
        stage_map_id=_gen_id("stagemap"),
        observed_stages=observed,
        expected_stages=expected,
        missing_stages=missing,
        impossible_order_flags=impossible,
        orphan_stage_refs=orphan_refs,
        cross_stage_join_keys={
            "trace_root": str(raw_exhaust.get("trace_root", "")),
            "run_id": str(raw_exhaust.get("run_id", "")),
            "request_id": str(raw_exhaust.get("request_id", "")),
        },
        route_id=raw_exhaust.get("route_id"),
        execution_form=raw_exhaust.get("execution_form"),
        terminal_class=raw_exhaust.get("terminal_class"),
        exit_disposition=raw_exhaust.get("exit_disposition"),
        uwg_commit_status=raw_exhaust.get("uwg_commit_status"),
    )


# ---------------------------------------------------------------------------
# I5 — build ArtifactInventory
# ---------------------------------------------------------------------------


def build_artifact_inventory(raw_exhaust: Mapping[str, Any]) -> ArtifactInventory:
    artifacts = raw_exhaust.get("artifacts", {}) or {}
    return ArtifactInventory(
        inventory_id=_gen_id("inv"),
        generated_artifacts=list(artifacts.get("generated", [])),
        sealed_artifacts=list(artifacts.get("sealed", [])),
        quarantined_artifacts=list(artifacts.get("quarantined", [])),
        proposed_state_diffs=list(artifacts.get("proposed_state_diffs", [])),
        committed_state_refs=list(artifacts.get("committed_state_refs", [])),
        stdout_stderr_refs=list(artifacts.get("stdout_stderr_refs", [])),
        file_hashes=dict(artifacts.get("file_hashes", {})),
        artifact_lineage=dict(artifacts.get("artifact_lineage", {})),
        missing_artifact_refs=list(artifacts.get("missing", [])),
        orphan_artifact_refs=list(artifacts.get("orphans", [])),
    )


# ---------------------------------------------------------------------------
# I6 — normalize records
# ---------------------------------------------------------------------------


def normalize_records(
    raw_exhaust: Mapping[str, Any],
    bundle_id: str,
) -> list[NormalizedEvidenceRecord]:
    out: list[NormalizedEvidenceRecord] = []
    for ev in raw_exhaust.get("events", []) or []:
        warnings: list[str] = []
        prov = ev.get("provider_lane")
        if prov in (None, "", "unknown"):
            warnings.append(REASON_UNKNOWN_PROVIDER_FALLBACK)
        rec = NormalizedEvidenceRecord(
            normalized_record_id=_gen_id("norm"),
            runtime_exhaust_bundle_id=bundle_id,
            canonical_event_type=str(ev.get("event_type", "unknown")),
            canonical_stage=str(ev.get("stage", "UNKNOWN")),
            source_ref=str(ev.get("source_ref", "")),
            normalized_payload_ref=str(ev.get("payload_ref", "")),
            trace_id=str(ev.get("trace_id", "")),
            span_id=str(ev.get("span_id", "")),
            parent_span_id=ev.get("parent_span_id"),
            request_id=str(raw_exhaust.get("request_id", "")),
            run_id=str(raw_exhaust.get("run_id", "")),
            tenant_id=str(raw_exhaust.get("tenant_id", "")),
            route_id=raw_exhaust.get("route_id"),
            step_id=ev.get("step_id"),
            attempt_id=ev.get("attempt_id"),
            model_id=ev.get("model_id"),
            tool_id=ev.get("tool_id"),
            provider_lane=prov,
            token_count_in=int(ev.get("token_count_in", 0)),
            token_count_out=int(ev.get("token_count_out", 0)),
            cost_estimate=float(ev.get("cost_estimate", 0.0)),
            latency_ms=float(ev.get("latency_ms", 0.0)),
            retry_count=int(ev.get("retry_count", 0)),
            repair_count=int(ev.get("repair_count", 0)),
            fallback_depth=int(ev.get("fallback_depth", 0)),
            error_code=ev.get("error_code"),
            reason_codes=list(ev.get("reason_codes", [])),
            policy_hash=raw_exhaust.get("policy_hash"),
            blueprint_hash=raw_exhaust.get("blueprint_hash"),
            replay_key=raw_exhaust.get("replay_key"),
            prompt_hash=ev.get("prompt_hash"),
            context_hash=ev.get("context_hash"),
            artifact_digest=ev.get("artifact_digest"),
            eval_readiness_hint=str(ev.get("eval_readiness_hint", "UNKNOWN")),
            normalization_warnings=warnings,
        )
        out.append(stamp_digest(rec))
    return out


# ---------------------------------------------------------------------------
# I7 — stratify run outcome
# ---------------------------------------------------------------------------


def stratify_outcome(raw_exhaust: Mapping[str, Any]) -> str:
    cls = str(raw_exhaust.get("outcome_class", "unresolved_unknown"))
    if cls not in RUN_OUTCOME_CLASSES:
        return "unresolved_unknown"
    return cls


# ---------------------------------------------------------------------------
# Bundle assembly
# ---------------------------------------------------------------------------


def build_runtime_exhaust_bundle(
    raw_exhaust: Mapping[str, Any],
    *,
    repair_fixture: bool = False,
) -> tuple[
    RuntimeExhaustBundle,
    list[NormalizedEvidenceRecord],
    list[ExhaustSourceManifest],
    StageMap,
    ArtifactInventory,
    ExhaustGapReport,
]:
    """Run the full 6A pipeline; return the bundle and the side artifacts.

    The order of operations matches doctrine §I1..§I7.
    """
    receive_completed_run_marker(raw_exhaust, repair_fixture=repair_fixture)
    manifests = collect_source_refs(raw_exhaust)
    gap_codes = validate_lineage(raw_exhaust, manifests)
    stage_map = build_stage_map(raw_exhaust, manifests)
    inv = build_artifact_inventory(raw_exhaust)

    bundle_id = _gen_id("rxb")
    gap_report = ExhaustGapReport(
        gap_report_id=_gen_id("gap"),
        runtime_exhaust_bundle_id=bundle_id,
        gap_codes=gap_codes + stage_map.missing_stages,
        missing_evidence_refs=list(inv.missing_artifact_refs),
        orphan_artifact_refs=list(inv.orphan_artifact_refs) + list(stage_map.orphan_stage_refs),
        impossible_order_flags=list(stage_map.impossible_order_flags),
        repair_required=bool(gap_codes or stage_map.missing_stages or stage_map.impossible_order_flags),
    )

    bundle = RuntimeExhaustBundle(
        runtime_exhaust_bundle_id=bundle_id,
        request_id=str(raw_exhaust.get("request_id", "")),
        run_id=str(raw_exhaust.get("run_id", "")),
        session_id=str(raw_exhaust.get("session_id", "")),
        tenant_id=str(raw_exhaust.get("tenant_id", "")),
        trace_root=str(raw_exhaust.get("trace_root", "")),
        completed_at=str(raw_exhaust.get("completed_at", "")),
        runtime_boundary_crossed=bool(raw_exhaust.get("runtime_boundary_crossed")),
        source_exhaust_refs=[m.source_ref for m in manifests],
        route_contract_ref=raw_exhaust.get("route_contract_ref"),
        l1_plan_ref=raw_exhaust.get("l1_plan_ref"),
        c0_evidence_contract_refs=list(raw_exhaust.get("c0_evidence_contract_refs", [])),
        prompt_envelope_refs=list(raw_exhaust.get("prompt_envelope_refs", [])),
        l2_artifact_refs=list(raw_exhaust.get("l2_artifact_refs", [])),
        l3_workflow_package_ref=raw_exhaust.get("l3_workflow_package_ref"),
        exit_disposition_ref=raw_exhaust.get("exit_disposition_ref"),
        hitl_packet_refs=list(raw_exhaust.get("hitl_packet_refs", [])),
        uwg_receipt_refs=list(raw_exhaust.get("uwg_receipt_refs", [])),
        policy_hash=raw_exhaust.get("policy_hash"),
        blueprint_hash=raw_exhaust.get("blueprint_hash"),
        replay_key=raw_exhaust.get("replay_key"),
        source_lineage_manifest_ref=raw_exhaust.get("source_lineage_manifest_ref"),
        artifact_inventory_ref=inv.inventory_id,
        ingest_gap_report_ref=gap_report.gap_report_id,
        l5_certification_ref=str(raw_exhaust.get("l5_certification_ref") or MISSING_CERT_REF_SENTINEL),
    )
    bundle = stamp_digest(bundle)
    normalized = normalize_records(raw_exhaust, bundle_id)
    return bundle, normalized, manifests, stage_map, inv, gap_report


__all__ = [
    "IngestError",
    "EXPECTED_STAGES",
    "REASON_LIVE_RUN_NOT_CLOSED",
    "REASON_EXIT_DISPOSITION_MISSING",
    "REASON_TRACE_LINK_MISSING",
    "REASON_ORPHAN_ARTIFACT",
    "REASON_IMPOSSIBLE_STAGE_ORDER",
    "REASON_POLICY_HASH_MISMATCH",
    "REASON_REPLAY_KEY_MISSING",
    "REASON_UNKNOWN_PROVIDER_FALLBACK",
    "REASON_CERT_REF_MISSING",
    "REASON_CERT_REF_UNRESOLVED",
    "MISSING_CERT_REF_SENTINEL",
    "UNRESOLVED_CERT_REF_PREFIXES",
    "is_missing_l5_certification_ref",
    "is_unresolved_l5_certification_ref",
    "receive_completed_run_marker",
    "collect_source_refs",
    "validate_lineage",
    "build_stage_map",
    "build_artifact_inventory",
    "normalize_records",
    "stratify_outcome",
    "build_runtime_exhaust_bundle",
]
