"""Trace Feature Extractor — converts execution signals into FeatureBundles.

Converts raw execution trace signals (routing, confidence, retrieval,
policy, guardrail, healing, HITL, mutation) into deterministic
``FeatureBundle`` and ``TraceFeatureRecord`` objects.

Design invariants
-----------------
1. Pure function interface — no global mutable state.
2. No wall-clock reads; caller supplies ``timestamp_utc``.
3. All outputs are deterministically hash-keyed.
4. Fail-closed: missing or malformed signal fields produce safe defaults
   rather than raising (documented per method).
5. ADG relation families tagged per field (see FeatureBundle docstring).
"""

from __future__ import annotations

import logging
from typing import Any

from system_learning.types.trace_feature_types import (
    FeatureBundle,
    TraceFeatureRecord,
)
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Outcome classifier
# ---------------------------------------------------------------------------

_OUTCOME_PRIORITY: tuple[str, ...] = (
    "REPLAY_FAILURE",
    "ROLLBACK",
    "HUMAN_OVERRIDE",
    "HEALED_SUCCESS",
    "SAFE_FAILURE",
    "SUCCESS",
)


def _classify_outcome(signal: dict[str, Any]) -> str:
    """Derive final outcome class from a raw signal dict.

    Priority order (highest first):
      1. REPLAY_FAILURE  — replay_failed key is truthy
      2. ROLLBACK        — rollback key is truthy
      3. HUMAN_OVERRIDE  — human_override key is truthy
      4. HEALED_SUCCESS  — healed key is truthy AND success is truthy
      5. SAFE_FAILURE    — success is falsy but no error/exception flag
      6. SUCCESS         — success is truthy and none of the above

    Falls back to ``"UNKNOWN"`` when neither success nor failure is
    determinable from the signal.
    """
    if signal.get("replay_failed"):
        return "REPLAY_FAILURE"
    if signal.get("rollback"):
        return "ROLLBACK"
    if signal.get("human_override"):
        return "HUMAN_OVERRIDE"
    if signal.get("healed") and signal.get("success"):
        return "HEALED_SUCCESS"
    success = signal.get("success")
    if success is True:
        return "SUCCESS"
    if success is False:
        return "SAFE_FAILURE"
    return "UNKNOWN"


# ---------------------------------------------------------------------------
# Confidence gate state extractor
# ---------------------------------------------------------------------------

_GATE_STATE_MAP: dict[str, str] = {
    "pass": "PASS",
    "passed": "PASS",
    "stall": "STALL",
    "stalled": "STALL",
    "escalate": "ESCALATE",
    "escalated": "ESCALATE",
    "skip": "PASS",
}


def _extract_gate_state(signal: dict[str, Any]) -> str:
    raw = str(signal.get("confidence_gate_state", "")).lower()
    return _GATE_STATE_MAP.get(raw, "PASS")


# ---------------------------------------------------------------------------
# Core extractor
# ---------------------------------------------------------------------------


class TraceFeatureExtractor:
    """Converts execution trace signal dicts into FeatureBundles.

    Signal dict schema (all fields optional — extractor is fail-safe):

    .. code-block:: python

        {
            # Routing (ADG: routes_path, routes_through)
            "route_selected": str,

            # Confidence gate (ADG: gated_by_confidence, forces_stall)
            "confidence_gate_state": "pass" | "stall" | "escalate",

            # Retrieval (ADG: retrieves_via)
            "retrieval_path": str,

            # Groundedness (ADG: scores_groundedness)
            "retrieval_groundedness_score": float,

            # Policy (ADG: applies_policy)
            "policy_hashes": list[str],

            # Guardrails (ADG: applies_guardrail)
            "guardrails_applied": list[str],

            # Determinism / replay (ADG: records_execution_trace)
            "determinism_markers": list[str],

            # Healing (ADG: orchestrates_healing, dispatches_healing_run)
            "healing_invoked": bool,
            "healer_id": str | None,

            # HITL (ADG: escalates_to_human)
            "human_escalation_flag": bool,

            # Mutation (ADG: records_mutation_transport)
            "mutation_presence": bool,

            # Outcome
            "success": bool,
            "replay_failed": bool,
            "rollback": bool,
            "human_override": bool,
            "healed": bool,

            # ADG context
            "adg_entity_name": str,
            "adg_relation_ids": list[str],
        }
    """

    def extract(
        self,
        trace_id: str,
        signal: dict[str, Any],
        timestamp_utc: int,
    ) -> FeatureBundle:
        """Extract a FeatureBundle from a raw execution signal dict.

        Parameters
        ----------
        trace_id:
            Unique trace correlation ID.
        signal:
            Raw execution signal dict (schema above).  Unknown keys are
            silently ignored.
        timestamp_utc:
            Caller-supplied Unix timestamp (no wall-clock read).

        Returns
        -------
        FeatureBundle
            Deterministic feature snapshot.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "TraceFeatureExtractor.extract")

        route = str(signal.get("route_selected") or "UNKNOWN")
        gate_state = _extract_gate_state(signal)

        retrieval_path = str(signal.get("retrieval_path") or "UNKNOWN")
        try:
            gnd = float(signal.get("retrieval_groundedness_score", 0.0))
        except (TypeError, ValueError):
            gnd = 0.0
        gnd = max(0.0, min(1.0, gnd))

        policy_hashes: tuple[str, ...] = tuple(str(h) for h in (signal.get("policy_hashes") or []) if h)
        guardrails: tuple[str, ...] = tuple(str(g) for g in (signal.get("guardrails_applied") or []) if g)
        det_markers: tuple[str, ...] = tuple(str(m) for m in (signal.get("determinism_markers") or []) if m)

        healing_invoked = bool(signal.get("healing_invoked", False))
        healer_id_raw = signal.get("healer_id")
        healer_id = str(healer_id_raw) if healer_id_raw else None

        hitl = bool(signal.get("human_escalation_flag", False))
        mutation = bool(signal.get("mutation_presence", False))

        try:
            routing_conf = float(signal.get("routing_confidence", 0.0))
        except (TypeError, ValueError):
            routing_conf = 0.0
        routing_conf = max(0.0, min(1.0, routing_conf))
        routing_target = str(signal.get("routing_target") or "")

        outcome = _classify_outcome(signal)

        adg_entity = str(signal.get("adg_entity_name") or "ADG::Unknown")
        adg_rels: tuple[str, ...] = tuple(str(r) for r in (signal.get("adg_relation_ids") or []) if r)

        return FeatureBundle(
            trace_id=trace_id,
            route_selected=route,
            confidence_gate_state=gate_state,
            retrieval_path=retrieval_path,
            retrieval_groundedness_score=gnd,
            policy_state_accessed=policy_hashes,
            guardrails_applied=guardrails,
            determinism_markers=det_markers,
            healing_invoked=healing_invoked,
            healer_id=healer_id,
            human_escalation_flag=hitl,
            mutation_presence=mutation,
            final_outcome_class=outcome,
            timestamp_utc=timestamp_utc,
            adg_entity_name=adg_entity,
            adg_relation_ids=adg_rels,
            routing_confidence=routing_conf,
            routing_target=routing_target,
        )

    def extract_record(
        self,
        trace_id: str,
        signal: dict[str, Any],
        timestamp_utc: int,
    ) -> TraceFeatureRecord:
        """Extract and immediately promote to a TraceFeatureRecord.

        Convenience wrapper around ``extract()`` +
        ``TraceFeatureRecord.from_bundle()``.
        """
        bundle = self.extract(trace_id, signal, timestamp_utc)
        return TraceFeatureRecord.from_bundle(bundle)

    def extract_batch(
        self,
        traces: list[tuple[str, dict[str, Any], int]],
    ) -> list[FeatureBundle]:
        """Extract FeatureBundles from a batch of (trace_id, signal, ts) tuples.

        Skips entries where extraction fails, logging a warning per failure.
        Preserves input order in output.
        """
        results: list[FeatureBundle] = []
        for trace_id, signal, ts in traces:
            try:
                results.append(self.extract(trace_id, signal, ts))
            except Exception as exc:  # guardian: allow-silent-swallow
                logger.warning(
                    "trace_feature_extractor: extraction failed",
                    extra={"trace_id": trace_id, "error": str(exc)},
                )
        return results


# ---------------------------------------------------------------------------
# Convenience factory
# ---------------------------------------------------------------------------


def build_feature_bundle(
    trace_id: str,
    signal: dict[str, Any],
    timestamp_utc: int,
) -> FeatureBundle:
    """Module-level convenience wrapper for ``TraceFeatureExtractor.extract``."""
    return TraceFeatureExtractor().extract(trace_id, signal, timestamp_utc)


def build_trace_record(
    trace_id: str,
    signal: dict[str, Any],
    timestamp_utc: int,
) -> TraceFeatureRecord:
    """Module-level convenience wrapper for ``TraceFeatureExtractor.extract_record``."""
    return TraceFeatureExtractor().extract_record(trace_id, signal, timestamp_utc)


__all__ = [
    "TraceFeatureExtractor",
    "build_feature_bundle",
    "build_trace_record",
]
