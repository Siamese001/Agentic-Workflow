"""Runtime exhaust bundle (S1A) — promoted into agentic_core 2026-05-01.

Previously lived at ``system_learning.engines.runtime_exhaust_collector``.
It is core spine machinery (sealed completed-run evidence aggregator)
and belongs in ``agentic_core/L6_observability/runtime_trace/`` next to
the snapshot adapter and canary emitter, not in the post-run learning
layer.

``system_learning.engines.runtime_exhaust_collector`` is now a thin
re-export shim that imports from this module to preserve every existing
caller import path.

Reference: docs/reference/06_Shadow_Evaluation_System_Learning v7 spec
lines 132-205 (S1A spec).

Spec required preserves (20 fields):
    trace_id, span_id, parent_span_id, run_id, session_id, request_id,
    route_id, step_id, attempt_id, replay_key, blueprint_hash, policy_hash,
    prompt_hash, context_hash, model_id, tool_id, provider_lane, source
    lineage, artifact digest, L4 snapshot ref, UWG receipt ref.

Spec required detections (11 conditions):
    missing trace link, orphan artifact, unsealed span, impossible stage
    order, policy hash mismatch, missing replay key, non-deterministic
    metadata, duplicate run identity, incomplete invocation log, unbound
    HITL input, unknown provider fallback.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Sequence

logger = logging.getLogger(__name__)


REQUIRED_LINEAGE_FIELDS: tuple[str, ...] = (
    "trace_id",
    "span_id",
    "parent_span_id",
    "run_id",
    "session_id",
    "request_id",
    "route_id",
    "step_id",
    "attempt_id",
    "replay_key",
    "blueprint_hash",
    "policy_hash",
    "prompt_hash",
    "context_hash",
    "model_id",
    "tool_id",
    "provider_lane",
    "source_lineage",
    "artifact_digest",
    "l4_snapshot_ref",
    "uwg_receipt_ref",
)


class ExhaustDefect(str, Enum):
    """The 11 defect classes the collector must detect."""

    MISSING_TRACE_LINK = "missing_trace_link"
    ORPHAN_ARTIFACT = "orphan_artifact"
    UNSEALED_SPAN = "unsealed_span"
    IMPOSSIBLE_STAGE_ORDER = "impossible_stage_order"
    POLICY_HASH_MISMATCH = "policy_hash_mismatch"
    MISSING_REPLAY_KEY = "missing_replay_key"
    NON_DETERMINISTIC_METADATA = "non_deterministic_metadata"
    DUPLICATE_RUN_IDENTITY = "duplicate_run_identity"
    INCOMPLETE_INVOCATION_LOG = "incomplete_invocation_log"
    UNBOUND_HITL_INPUT = "unbound_hitl_input"
    UNKNOWN_PROVIDER_FALLBACK = "unknown_provider_fallback"


@dataclass(frozen=True)
class GapReport:
    """Per-record gap inventory."""

    record_id: str
    missing_fields: tuple[str, ...]
    detected_defects: tuple[ExhaustDefect, ...]


@dataclass(frozen=True)
class RuntimeExhaustBundle:
    """The S1A output."""

    raw_evidence_refs: tuple[str, ...]
    lineage_manifest: Mapping[str, Mapping[str, Any]]
    stage_map: Mapping[str, str]
    artifact_inventory: tuple[str, ...]
    gap_report: tuple[GapReport, ...]
    ingest_quality_score: float
    newest_span_age_seconds: float
    bundle_id: str
    tenant_id: str = ""  # W1: identity quad extension (D6)
    l5_certification_ref: str = ""

    def __post_init__(self) -> None:
        from agentic_core.L5_safety.contracts.verify import verify_certification_ref
        if not verify_certification_ref(self.l5_certification_ref):
            raise ValueError(
                f"RuntimeExhaustBundle: missing or invalid l5_certification_ref={self.l5_certification_ref!r} "
                "(AG-W0-5=fail_closed)"
            )


class RuntimeExhaustCollector:
    """S1A engine - gather completed-run exhaust into a sealed bundle."""

    def __init__(self) -> None:
        self._bundles_collected: int = 0
        self._records_processed: int = 0
        self._records_with_defects: int = 0

    def collect(
        self,
        records: Sequence[Mapping[str, Any]],
        *,
        now_epoch: float | None = None,
        bundle_id: str | None = None,
    ) -> RuntimeExhaustBundle:
        ts = now_epoch if now_epoch is not None else time.time()
        bid = bundle_id or f"bundle-{int(ts * 1000)}-{len(records)}"

        lineage: dict[str, dict[str, Any]] = {}
        stage_map: dict[str, str] = {}
        artifact_inventory: list[str] = []
        gap_reports: list[GapReport] = []
        run_ids_seen: dict[str, int] = {}
        newest_span_ts: float | None = None

        for idx, rec in enumerate(records):
            self._records_processed += 1
            rec_id = str(rec.get("record_id", f"rec-{idx}"))

            missing = tuple(
                f for f in REQUIRED_LINEAGE_FIELDS
                if f not in rec or rec[f] in (None, "", [])
            )
            defects = list(self._detect_defects(rec, run_ids_seen))
            if missing or defects:
                self._records_with_defects += 1
                gap_reports.append(GapReport(
                    record_id=rec_id,
                    missing_fields=missing,
                    detected_defects=tuple(defects),
                ))

            lineage[rec_id] = {
                f: rec.get(f) for f in REQUIRED_LINEAGE_FIELDS if f in rec
            }
            stage_map[rec_id] = str(rec.get("stage", "unknown"))
            ad = rec.get("artifact_digest")
            if ad:
                artifact_inventory.append(str(ad))

            sp_ts = rec.get("span_end_epoch") or rec.get("span_start_epoch")
            if sp_ts is not None:
                try:
                    sp_f = float(sp_ts)
                except (TypeError, ValueError):
                    sp_f = None  # type: ignore[assignment]
                if sp_f is not None and (newest_span_ts is None or sp_f > newest_span_ts):
                    newest_span_ts = sp_f

        defective = sum(
            1 for g in gap_reports if g.missing_fields or g.detected_defects
        )
        quality = (
            1.0 - (defective / len(records))
            if records else 1.0
        )

        newest_age = (
            ts - newest_span_ts if newest_span_ts is not None else float("inf")
        )

        self._bundles_collected += 1
        return RuntimeExhaustBundle(
            raw_evidence_refs=tuple(
                str(r.get("record_id", f"rec-{i}"))
                for i, r in enumerate(records)
            ),
            lineage_manifest=lineage,
            stage_map=stage_map,
            artifact_inventory=tuple(artifact_inventory),
            gap_report=tuple(gap_reports),
            ingest_quality_score=quality,
            newest_span_age_seconds=newest_age,
            bundle_id=bid,
        )

    def _detect_defects(
        self,
        record: Mapping[str, Any],
        run_ids_seen: dict[str, int],
    ) -> Sequence[ExhaustDefect]:
        defects: list[ExhaustDefect] = []

        if not record.get("trace_id"):
            defects.append(ExhaustDefect.MISSING_TRACE_LINK)
        if (record.get("artifact_digest")
                and not record.get("trace_id")
                and not record.get("run_id")):
            defects.append(ExhaustDefect.ORPHAN_ARTIFACT)
        if record.get("span_id") and not record.get("span_sealed", True):
            defects.append(ExhaustDefect.UNSEALED_SPAN)
        prior = record.get("prior_step_id")
        cur = record.get("step_id")
        if prior is not None and cur is not None:
            try:
                if int(cur) < int(prior):
                    defects.append(ExhaustDefect.IMPOSSIBLE_STAGE_ORDER)
            except (TypeError, ValueError):  # guardian: allow-silent-swallow -- step_id comparison: non-numeric step IDs are valid; skip ordering check silently
                pass
        ph = record.get("policy_hash")
        php = record.get("policy_hash_at_planning")
        if ph and php and ph != php:
            defects.append(ExhaustDefect.POLICY_HASH_MISMATCH)
        if not record.get("replay_key"):
            defects.append(ExhaustDefect.MISSING_REPLAY_KEY)
        if record.get("non_deterministic", False):
            defects.append(ExhaustDefect.NON_DETERMINISTIC_METADATA)

        run_id = record.get("run_id")
        if run_id:
            run_ids_seen[run_id] = run_ids_seen.get(run_id, 0) + 1
            if run_ids_seen[run_id] > 1:
                defects.append(ExhaustDefect.DUPLICATE_RUN_IDENTITY)

        invs = record.get("invocations", [])
        for inv in invs if isinstance(invs, list) else ():
            if not isinstance(inv, dict):
                continue
            if inv.get("span_id") and not (inv.get("tool_id") or inv.get("model_id")):
                defects.append(ExhaustDefect.INCOMPLETE_INVOCATION_LOG)
                break

        if record.get("hitl_packet") and not record.get("hitl_inputs_bound"):
            defects.append(ExhaustDefect.UNBOUND_HITL_INPUT)

        provider = record.get("provider_lane")
        if provider == "unknown_fallback":
            defects.append(ExhaustDefect.UNKNOWN_PROVIDER_FALLBACK)

        return defects

    @property
    def counters(self) -> tuple[int, int, int]:
        return (
            self._bundles_collected,
            self._records_processed,
            self._records_with_defects,
        )

    def reset(self) -> None:
        self._bundles_collected = 0
        self._records_processed = 0
        self._records_with_defects = 0

    def publish_kpi_sample(self, board: Any, bundle: RuntimeExhaustBundle) -> None:
        """Publish TRACE_INGEST_FRESHNESS KPI for this bundle.

        The KPI board lives in system_learning; we import lazily and
        fail-soft so this method is callable from agentic_core without
        creating a hard dependency on system_learning.
        """
        try:
            from system_learning.engines.v6_kpi_board import (  # noqa: PLC0415
                V6KPIName,
                V6KPISample,
            )

            board.record(V6KPISample(
                name=V6KPIName.TRACE_INGEST_FRESHNESS,
                value=float(bundle.newest_span_age_seconds),
                timestamp=time.time(),
                source="runtime_exhaust_collector",
                metadata={"bundle_id": bundle.bundle_id,
                          "records": len(bundle.raw_evidence_refs)},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-log-and-swallow -- KPI must not break collection
            logger.warning("v6_kpi_trace_ingest_freshness_failed: %s", exc)


__all__ = [
    "REQUIRED_LINEAGE_FIELDS",
    "ExhaustDefect",
    "GapReport",
    "RuntimeExhaustBundle",
    "RuntimeExhaustCollector",
]
