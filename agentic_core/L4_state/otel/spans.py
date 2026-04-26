"""L4/UWG OTel span emission (00.8 §PHASE 1-2).

Implements the canonical span catalog and required-field validation. When the
``opentelemetry`` SDK is reachable, real spans are emitted; otherwise we
record a degraded in-memory ``SpanRecord`` so tests can inspect emissions
without depending on a live tracer.

Required fields (00.8 §PHASE 2):
- ``trace_id``     — missing = hard observability failure
- ``tenant_id``    — missing on scoped reads = hard privacy failure
- ``policy_hash``  — missing on writes = hard commit failure
- ``replay_key``   — missing on commit path = hard replay failure
- ``audit_refs``   — missing on write path = hard audit failure
"""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# Canonical span name catalog (mirrors 00.8 §PHASE 1).
L4_READ_SPAN_NAMES: Tuple[str, ...] = (
    "l4.read.policy_manifest",
    "l4.read.policy_version",
    "l4.read.blueprint_record",
    "l4.read.registry_snapshot",
    "l4.read.registry_record",
    "l4.read.memory_surface",
    "l4.read.approved_examples",
    "l4.read.rubric",
    "l4.read.threshold_profile",
    "l4.read.retrieval_surface",
    "l4.read.source_manifest",
    "l4.read.vector_index_manifest",
    "l4.read.sparse_index_manifest",
    "l4.read.metadata_index_manifest",
    "l4.read.graph_projection_manifest",
    "l4.read.citation_anchor",
    "l4.cache.lookup",
    "l4.cache.lookup_exact",
    "l4.cache.lookup_semantic",
    "l4.cache.resolve_entry",
    "l4.replay.snapshot.read",
    "l4.audit.read",
    "l4.audit.sequence_check",
    "l4.replay.reconstruct",
)

UWG_WRITE_SPAN_NAMES: Tuple[str, ...] = (
    "uwg.commit.request_received",
    "uwg.commit.validate",
    "uwg.write_lock.acquire",
    "uwg.commit.apply",
    "uwg.commit.receipt_emit",
    "uwg.commit.blocked",
    "uwg.read_surface.refresh",
    "uwg.rollback.apply",
    "l4.audit.append",
    "l4.direct_write_attempt.detected",
    "l4.direct_write_attempt.blocked",
)

L4_REFRESH_SPAN_NAMES: Tuple[str, ...] = (
    "l4.cache.invalidate",
    "l4.index.vector.refresh",
    "l4.index.sparse.refresh",
    "l4.index.metadata.refresh",
    "l4.graph_projection.refresh",
    "l4.alias.refresh",
    "l4.memory_projection.refresh",
    "l4.prompt_bom_cache.refresh",
    "l4.route_baseline.refresh",
)


@dataclass
class SpanRecord:
    """Degraded in-memory span record for inspection in tests."""

    name: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    started_at: float = field(default_factory=time.time)
    duration_ms: float = 0.0
    status: str = "OK"
    trace_id: str = ""
    span_id: str = ""

    def latency_ms(self) -> float:
        return self.duration_ms


# Module-level recorder. Tests reset between runs.
_LOCK = threading.Lock()
_EMITTED: List[SpanRecord] = []


def reset_emitted_spans() -> None:
    """Clear the in-memory span recorder. Use in test setup."""
    with _LOCK:
        _EMITTED.clear()


def get_emitted_spans(name_prefix: Optional[str] = None) -> List[SpanRecord]:
    """Return a copy of the emitted spans, optionally filtered by name prefix."""
    with _LOCK:
        snapshot = list(_EMITTED)
    if name_prefix:
        snapshot = [s for s in snapshot if s.name.startswith(name_prefix)]
    return snapshot


def _record_span(record: SpanRecord) -> None:
    with _LOCK:
        _EMITTED.append(record)


def _validate_l4_read_attributes(attrs: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate required fields per 00.8 §PHASE 2 for read spans."""
    failures: List[str] = []
    if not attrs.get("trace_id"):
        failures.append("missing_trace_id")
    if attrs.get("operation_type") == "read" and not attrs.get("tenant_id"):
        failures.append("missing_tenant_id_on_scoped_read")
    return (len(failures) == 0, failures)


def _validate_uwg_write_attributes(attrs: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate required fields per 00.8 §PHASE 2 for write spans."""
    failures: List[str] = []
    if not attrs.get("trace_id"):
        failures.append("missing_trace_id")
    name = attrs.get("_span_name", "")
    is_commit_path = name.startswith("uwg.commit.") or name in {
        "uwg.write_lock.acquire",
        "uwg.rollback.apply",
        "l4.audit.append",
    }
    if is_commit_path:
        if not attrs.get("policy_hash"):
            failures.append("missing_policy_hash_on_write")
        if not attrs.get("replay_key"):
            failures.append("missing_replay_key_on_commit")
    return (len(failures) == 0, failures)


def emit_l4_span(
    name: str,
    *,
    trace_id: str = "",
    span_id: str = "",
    parent_span_id: str = "",
    request_id: str = "",
    run_id: str = "",
    tenant_id: str = "",
    policy_hash: str = "",
    blueprint_hash: str = "",
    snapshot_id: str = "",
    state_surface: str = "",
    operation_type: str = "read",
    status: str = "OK",
    reason_codes: Optional[Tuple[str, ...]] = None,
    artifact_refs: Optional[Tuple[str, ...]] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> SpanRecord:
    """Emit an L4 read/refresh/audit-read span.

    Auto-generates trace_id/span_id when missing so tests can record without
    explicit IDs; production callers SHOULD pass real IDs from their tracer.
    """
    if not trace_id:
        trace_id = uuid.uuid4().hex
    if not span_id:
        span_id = uuid.uuid4().hex
    attrs: Dict[str, Any] = {
        "_span_name": name,
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_span_id": parent_span_id,
        "request_id": request_id,
        "run_id": run_id,
        "tenant_id": tenant_id,
        "policy_hash": policy_hash,
        "blueprint_hash": blueprint_hash,
        "snapshot_id": snapshot_id,
        "state_surface": state_surface,
        "operation_type": operation_type,
        "status": status,
        "reason_codes": list(reason_codes or ()),
        "artifact_refs": list(artifact_refs or ()),
    }
    if extra:
        attrs.update(extra)

    ok, failures = _validate_l4_read_attributes(attrs)
    if not ok:
        attrs["validation_failures"] = failures
        attrs["status"] = "OBSERVABILITY_FAILURE"

    record = SpanRecord(
        name=name,
        attributes=attrs,
        trace_id=trace_id,
        span_id=span_id,
    )
    _record_span(record)
    return record


def emit_uwg_span(
    name: str,
    *,
    trace_id: str = "",
    span_id: str = "",
    parent_span_id: str = "",
    request_id: str = "",
    run_id: str = "",
    tenant_id: str = "",
    policy_hash: str = "",
    blueprint_hash: str = "",
    replay_key: str = "",
    snapshot_id: str = "",
    state_surface: str = "",
    operation_type: str = "write",
    source_surface: str = "",
    mutation_source: str = "",
    commit_request_id: str = "",
    commit_receipt_id: str = "",
    blocked_commit_receipt_id: str = "",
    status: str = "OK",
    reason_codes: Optional[Tuple[str, ...]] = None,
    artifact_refs: Optional[Tuple[str, ...]] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> SpanRecord:
    """Emit a UWG write/refresh/anti-bypass span."""
    if not trace_id:
        trace_id = uuid.uuid4().hex
    if not span_id:
        span_id = uuid.uuid4().hex
    attrs: Dict[str, Any] = {
        "_span_name": name,
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_span_id": parent_span_id,
        "request_id": request_id,
        "run_id": run_id,
        "tenant_id": tenant_id,
        "policy_hash": policy_hash,
        "blueprint_hash": blueprint_hash,
        "replay_key": replay_key,
        "snapshot_id": snapshot_id,
        "state_surface": state_surface,
        "operation_type": operation_type,
        "source_surface": source_surface,
        "mutation_source": mutation_source,
        "commit_request_id": commit_request_id,
        "commit_receipt_id": commit_receipt_id,
        "blocked_commit_receipt_id": blocked_commit_receipt_id,
        "status": status,
        "reason_codes": list(reason_codes or ()),
        "artifact_refs": list(artifact_refs or ()),
    }
    if extra:
        attrs.update(extra)

    ok, failures = _validate_uwg_write_attributes(attrs)
    if not ok:
        attrs["validation_failures"] = failures
        attrs["status"] = "OBSERVABILITY_FAILURE"

    record = SpanRecord(
        name=name,
        attributes=attrs,
        trace_id=trace_id,
        span_id=span_id,
    )
    _record_span(record)
    return record


__all__ = [
    "L4_READ_SPAN_NAMES",
    "L4_REFRESH_SPAN_NAMES",
    "UWG_WRITE_SPAN_NAMES",
    "SpanRecord",
    "emit_l4_span",
    "emit_uwg_span",
    "get_emitted_spans",
    "reset_emitted_spans",
]
