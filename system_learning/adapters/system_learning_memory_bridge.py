"""System Learning → Memory MCP Bridge.

Canonical adapter that persists system_learning knowledge into the Memory MCP
knowledge graph via GraphMemoryBridge, enabling cross-session learning for:

  - HealingSuccessRateStore  — EMA rates survive restarts (no more cold-start)
  - RCAEngine findings       — failure pattern library accumulates over time
  - ShadowDriftAnalyzer      — drift trend history queryable across sessions
  - PolicyRecommendationEngine — recommendation outcomes feed back into future decisions
  - HealingOutcomeAggregator — aggregate snapshots queryable across restarts

Design constraints:
  - Resilient: MCP unavailability is logged, never raises
  - Non-authoritative: MCP is a read-supplement; file/in-memory stores remain authoritative
  - Idempotent: repeated calls for the same content_hash are safe (entity upsert)
  - Bounded: observations capped at _MAX_OBS chars to stay within MCP payload limits

[SSOT] Canonical implementation for system_learning → Memory MCP persistence.
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_snapshots_state,
)

logger = logging.getLogger(__name__)

_MAX_OBS = 200
_MAX_SIGNATURES = 50
_MAX_RCA_FINDINGS = 20
_MAX_POLICY_RECS = 30


def _trunc(s: str, n: int = _MAX_OBS) -> str:
    return s[:n] if len(s) > n else s


def _content_hash(payload: str) -> str:
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


class SystemLearningMemoryBridge:
    """Persists system_learning signals into the Memory MCP knowledge graph.

    All public methods are fire-and-forget: they log on failure and return
    a bool indicating whether the write succeeded.

    Usage::

        bridge = SystemLearningMemoryBridge.get_instance()

        # After healing outcome recorded
        bridge.persist_healing_success_rate("IMPORT_ERROR", rate=0.87, count=42)

        # After RCA analysis
        bridge.persist_rca_findings(snapshot_id, findings)

        # After drift analysis
        bridge.persist_drift_summary(drift_summary)

        # After policy recommendation
        bridge.persist_policy_recommendation(recommendation)

        # After outcome aggregation
        bridge.persist_healing_aggregate_snapshot(snapshot)

        # On startup: restore healing rates
        rates = bridge.restore_healing_success_rates()
    """

    ENTITY_TYPE_HEALING_RATE = "SLHealingSuccessRate"
    ENTITY_TYPE_RCA_FINDING = "SLRCAFinding"
    ENTITY_TYPE_RCA_REPORT = "SLRCAReport"
    ENTITY_TYPE_DRIFT = "SLDriftSummary"
    ENTITY_TYPE_POLICY_REC = "SLPolicyRecommendation"
    ENTITY_TYPE_AGGREGATE = "SLHealingAggregate"
    ENTITY_TYPE_PATTERN = "SLFailurePattern"

    RELATION_TRIGGERED = "SL_TRIGGERED"
    RELATION_RESOLVED_BY = "SL_RESOLVED_BY"
    RELATION_DRIFT_DETECTED_IN = "SL_DRIFT_DETECTED_IN"
    RELATION_POLICY_APPLIES_TO = "SL_POLICY_APPLIES_TO"
    RELATION_AGGREGATES = "SL_AGGREGATES"

    _instance: SystemLearningMemoryBridge | None = None

    def __init__(self) -> None:
        self._bridge = self._load_bridge()

    @classmethod
    def get_instance(cls) -> SystemLearningMemoryBridge:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SystemLearningMemoryBridge.get_instance")

        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_bridge(self) -> Any:
        try:
            from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge

            return GraphMemoryBridge.get_instance()
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-silent-swallower
            logger.debug("[SLMemoryBridge] GraphMemoryBridge unavailable: %s", e)
            return None

    @property
    def is_available(self) -> bool:
        return self._bridge is not None and getattr(self._bridge, "is_available", False)

    # ------------------------------------------------------------------
    # 1. Healing Success Rates — persist/restore EMA rates cross-session
    # ------------------------------------------------------------------

    def persist_healing_success_rate(
        self,
        error_signature: str,
        rate: float,
        count: int,
        *,
        ts: str = "",
    ) -> bool:
        """Store a healing success rate for an error signature.

        Args:
            error_signature: The error pattern key (e.g. "IMPORT_ERROR").
            rate: EMA success rate (0.0–1.0).
            count: Observation count.
            ts: Optional timestamp tag.

        Returns:
            True if persisted, False if MCP unavailable.
        """
        _emit_snapshots_state(str(uuid.uuid4()), "SystemLearningMemoryBridge.persist_healing_success_rate", "L4_STATE")
        if not self._bridge:
            return False
        sig_hash = _content_hash(error_signature)
        entity_name = f"SLHealRate_{sig_hash}"
        try:
            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_HEALING_RATE,
                observations=[
                    _trunc(f"error_signature={error_signature}"),
                    f"rate={rate:.6f}",
                    f"count={count}",
                    f"ts={ts}",
                ],
            )
            return True
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-silent-swallower
            logger.debug("[SLMemoryBridge] persist_healing_success_rate failed: %s", e)
            return False

    def persist_all_healing_rates(
        self,
        rates: dict[str, float],
        counts: dict[str, int],
        *,
        ts: str = "",
    ) -> int:
        """Bulk-persist all healing success rates from a HealingSuccessRateStore.

        Args:
            rates: Dict of error_signature -> EMA rate.
            counts: Dict of error_signature -> observation count.
            ts: Optional timestamp tag.

        Returns:
            Number of rates successfully persisted.
        """
        persisted = 0
        for sig, rate in sorted(rates.items())[:_MAX_SIGNATURES]:
            count = counts.get(sig, 0)
            if self.persist_healing_success_rate(sig, rate, count, ts=ts):
                persisted += 1
        logger.info("[SLMemoryBridge] Persisted %d/%d healing rates", persisted, len(rates))
        return persisted

    def restore_healing_success_rates(self) -> dict[str, tuple[float, int]]:
        """Restore healing success rates from Memory MCP on startup.

        Returns:
            Dict of error_signature -> (rate, count). Empty if MCP unavailable.
        """
        if not self._bridge:
            return {}
        try:
            results = self._bridge.search_entities(self.ENTITY_TYPE_HEALING_RATE)
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-silent-swallower
            logger.debug("[SLMemoryBridge] restore_healing_success_rates failed: %s", e)
            return {}

        restored: dict[str, tuple[float, int]] = {}
        for entity in results:
            obs = entity.get("observations", [])
            sig = rate = count = None
            for o in obs:
                if o.startswith("error_signature="):
                    sig = o[len("error_signature=") :]
                elif o.startswith("rate="):
                    try:
                        rate = float(o[5:])
                    except ValueError:
                        pass
                elif o.startswith("count="):
                    try:
                        count = int(o[6:])
                    except ValueError:
                        pass
            if sig and rate is not None and count is not None:
                restored[sig] = (rate, count)

        logger.info("[SLMemoryBridge] Restored %d healing rate(s) from Memory MCP", len(restored))
        return restored

    # ------------------------------------------------------------------
    # 2. RCA Findings — accumulate failure pattern library
    # ------------------------------------------------------------------

    def persist_rca_findings(
        self,
        snapshot_id: str,
        findings: Any,
        *,
        window_start: int = 0,
        window_end: int = 0,
    ) -> bool:
        """Persist RCA findings from rca_engine.analyze_failures().

        Args:
            snapshot_id: The snapshot this RCA was based on.
            findings: RCAReport object or iterable of RCAFinding objects.
            window_start: Analysis window start (UTC epoch).
            window_end: Analysis window end (UTC epoch).

        Returns:
            True if report entity created.
        """
        if not self._bridge:
            return False

        rca_findings = []
        if hasattr(findings, "findings"):
            rca_findings = list(findings.findings)
        elif hasattr(findings, "__iter__"):
            rca_findings = list(findings)

        report_hash = _content_hash(f"{snapshot_id}:{window_start}:{window_end}")
        report_name = f"SLRCAReport_{report_hash}"

        obs = [
            f"snapshot_id={_trunc(snapshot_id, 80)}",
            f"finding_count={len(rca_findings)}",
            f"window={window_start}-{window_end}",
        ]
        for f in rca_findings[:5]:
            cat = getattr(f, "category", "?")
            sig = getattr(f, "signature", "?")
            cnt = getattr(f, "count", 0)
            obs.append(_trunc(f"finding={cat}:{sig}:n={cnt}"))

        try:
            self._bridge.create_agent_entity(
                agent_name=report_name,
                agent_type=self.ENTITY_TYPE_RCA_REPORT,
                observations=obs,
            )
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-silent-swallower
            logger.debug("[SLMemoryBridge] persist_rca_findings report failed: %s", e)
            return False

        # Individual finding entities for pattern library queries
        for finding in rca_findings[:_MAX_RCA_FINDINGS]:
            cat = getattr(finding, "category", "UNKNOWN")
            sig = getattr(finding, "signature", "unknown")
            cnt = getattr(finding, "count", 0)
            evhash = getattr(finding, "evidence_hash", "")[:16]
            finding_name = f"SLRCAFinding_{cat}_{_content_hash(sig)}"
            try:
                self._bridge.create_agent_entity(
                    agent_name=finding_name,
                    agent_type=self.ENTITY_TYPE_RCA_FINDING,
                    observations=[
                        f"category={cat}",
                        f"signature={_trunc(sig, 80)}",
                        f"count={cnt}",
                        f"evidence_hash={evhash}",
                        f"snapshot_id={_trunc(snapshot_id, 60)}",
                    ],
                )
                self._bridge.create_relation(finding_name, report_name, self.RELATION_TRIGGERED)
            # guardian: allow-silent-swallow
            except Exception as e:  # guardian: allow-silent-swallower
                logger.debug("[SLMemoryBridge] persist rca finding entity failed: %s", e)

        logger.info(
            "[SLMemoryBridge] RCA report persisted: %s (%d findings)",
            report_name,
            len(rca_findings),
        )
        return True

    def query_rca_pattern_frequency(self, category: str = "") -> list[dict[str, Any]]:
        """Query accumulated RCA findings, optionally filtered by category.

        Args:
            category: Filter by category (e.g. "IMPORT", "SYNTAX"). Empty = all.

        Returns:
            List of SLRCAFinding entity dicts from the knowledge graph.
        """
        if not self._bridge:
            return []
        query = f"SLRCAFinding {category}" if category else "SLRCAFinding"
        try:
            return self._bridge.search_entities(query)
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-silent-swallower
            logger.debug("[SLMemoryBridge] query_rca_pattern_frequency failed: %s", e)
            return []

    # ------------------------------------------------------------------
    # 3. Shadow Drift Summaries — drift trend history
    # ------------------------------------------------------------------

    def persist_drift_summary(self, drift_summary: Any, *, ts: str = "") -> bool:
        """Persist a ShadowDriftAnalyzer DriftSummary to Memory MCP.

        Args:
            drift_summary: DriftSummary dataclass from shadow_drift_analyzer.
            ts: Optional timestamp tag.

        Returns:
            True if entity created.
        """
        if not self._bridge:
            return False

        profile_id = getattr(drift_summary, "profile_id", "unknown")
        digest = getattr(drift_summary, "deterministic_digest", "")[:16]
        drift_flag = getattr(drift_summary, "drift_flag", False)
        drift_score = getattr(drift_summary, "drift_score", 0.0)
        p95 = getattr(drift_summary, "p95_cosine", 0.0)
        mean = getattr(drift_summary, "mean_cosine", 0.0)
        batch_size = getattr(drift_summary, "batch_size", 0)

        entity_name = f"SLDrift_{_content_hash(f'{profile_id}:{digest}')}"
        try:
            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_DRIFT,
                observations=[
                    f"profile_id={_trunc(profile_id, 60)}",
                    f"drift_flag={drift_flag}",
                    f"drift_score={drift_score:.6f}",
                    f"p95_cosine={p95:.6f}",
                    f"mean_cosine={mean:.6f}",
                    f"batch_size={batch_size}",
                    f"digest={digest}",
                    f"ts={ts}",
                ],
            )
            logger.info(
                "[SLMemoryBridge] Drift summary persisted: profile=%s drift=%s score=%.4f",
                profile_id,
                drift_flag,
                drift_score,
            )
            return True
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-silent-swallower
            logger.debug("[SLMemoryBridge] persist_drift_summary failed: %s", e)
            return False

    def query_drift_history(self, profile_id: str = "") -> list[dict[str, Any]]:
        """Return all persisted drift summaries, optionally filtered by profile.

        Args:
            profile_id: Substring match on profile_id observation. Empty = all.

        Returns:
            List of SLDriftSummary entity dicts.
        """
        if not self._bridge:
            return []
        query = f"SLDriftSummary {profile_id}" if profile_id else "SLDriftSummary"
        try:
            return self._bridge.search_entities(query)
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-silent-swallower
            logger.debug("[SLMemoryBridge] query_drift_history failed: %s", e)
            return []

    # ------------------------------------------------------------------
    # 4. Policy Recommendations — history + outcome feedback
    # ------------------------------------------------------------------

    def persist_policy_recommendation(
        self,
        recommendation: Any,
        *,
        ts: str = "",
        applied: bool = False,
    ) -> bool:
        """Persist a PolicyRecommendationEngine recommendation.

        Args:
            recommendation: PolicyRecommendation dataclass.
            ts: Optional timestamp tag.
            applied: Whether the recommendation was applied.

        Returns:
            True if entity created.
        """
        if not self._bridge:
            return False

        profile_id = getattr(recommendation, "profile_id", "unknown")
        digest = getattr(recommendation, "deterministic_digest", "")[:16]
        rationale = getattr(recommendation, "rationale", "")
        confidence = getattr(recommendation, "confidence_score", 0.0)
        changes = getattr(recommendation, "recommended_changes", {})

        entity_name = f"SLPolicyRec_{_content_hash(f'{profile_id}:{digest}')}"
        changes_str = _trunc(json.dumps(changes, separators=(",", ":"), sort_keys=True))

        try:
            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_POLICY_REC,
                observations=[
                    f"profile_id={_trunc(profile_id, 60)}",
                    f"confidence={confidence:.6f}",
                    f"changes={changes_str}",
                    f"rationale={_trunc(rationale, 120)}",
                    f"applied={applied}",
                    f"digest={digest}",
                    f"ts={ts}",
                ],
            )
            logger.info(
                "[SLMemoryBridge] Policy recommendation persisted: profile=%s confidence=%.4f applied=%s",
                profile_id,
                confidence,
                applied,
            )
            return True
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-silent-swallower
            logger.debug("[SLMemoryBridge] persist_policy_recommendation failed: %s", e)
            return False

    def mark_recommendation_applied(self, entity_name: str) -> bool:
        """Update a policy recommendation entity to mark it as applied.

        Args:
            entity_name: Full entity name (e.g. SLPolicyRec_abcdef12...).

        Returns:
            True if observation added.
        """
        if not self._bridge:
            return False
        try:
            return self._bridge.add_observation(entity_name, "applied=true")
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-silent-swallower
            logger.debug("[SLMemoryBridge] mark_recommendation_applied failed: %s", e)
            return False

    def query_policy_recommendations(
        self, profile_id: str = "", *, applied_only: bool = False
    ) -> list[dict[str, Any]]:
        """Query persisted policy recommendations.

        Args:
            profile_id: Optional profile filter.
            applied_only: If True, filter by applied=true observation.

        Returns:
            List of SLPolicyRecommendation entities.
        """
        if not self._bridge:
            return []
        query = f"SLPolicyRecommendation {profile_id}" if profile_id else "SLPolicyRecommendation"
        try:
            results = self._bridge.search_entities(query)
            if applied_only:
                results = [r for r in results if any("applied=true" in o for o in r.get("observations", []))]
            return results
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-silent-swallower
            logger.debug("[SLMemoryBridge] query_policy_recommendations failed: %s", e)
            return []

    # ------------------------------------------------------------------
    # 5. Healing Aggregate Snapshots — cross-session aggregate history
    # ------------------------------------------------------------------

    def persist_healing_aggregate_snapshot(self, snapshot: Any, *, ts: str = "") -> bool:
        """Persist a HealingOutcomeAggregateSnapshot to Memory MCP.

        Args:
            snapshot: HealingOutcomeAggregateSnapshot dataclass.
            ts: Optional timestamp tag.

        Returns:
            True if entity created.
        """
        if not self._bridge:
            return False

        version_id = getattr(snapshot, "version_id", "unknown")
        created_utc = getattr(snapshot, "created_utc", 0)
        aggregates = getattr(snapshot, "aggregates", ())
        total = len(aggregates)

        # Summary stats
        top_rates: list[str] = []
        for key, agg in list(aggregates)[:5]:
            healer = getattr(key, "healer_name", "?")
            s = getattr(agg, "success_count", 0)
            f = getattr(agg, "failure_count", 0)
            rate = round(s / (s + f), 4) if (s + f) > 0 else 0.0
            top_rates.append(f"{healer}:{rate:.3f}")

        entity_name = f"SLAggrSnap_{_content_hash(version_id)}"
        try:
            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_AGGREGATE,
                observations=[
                    f"version_id={_trunc(version_id, 60)}",
                    f"created_utc={created_utc}",
                    f"aggregate_count={total}",
                    _trunc(f"top_rates={','.join(top_rates)}"),
                    f"ts={ts}",
                ],
            )
            logger.info(
                "[SLMemoryBridge] Healing aggregate snapshot persisted: %s (%d aggregates)",
                entity_name,
                total,
            )
            return True
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-silent-swallower
            logger.debug("[SLMemoryBridge] persist_healing_aggregate_snapshot failed: %s", e)
            return False

    # ------------------------------------------------------------------
    # 6. Failure Pattern Library — accumulated from PatternAnalysisEngine
    # ------------------------------------------------------------------

    def persist_failure_pattern(
        self,
        pattern_id: str,
        pattern_label: str,
        centroid_hash: str,
        member_count: int,
        *,
        ts: str = "",
    ) -> bool:
        """Persist a detected failure pattern cluster.

        Args:
            pattern_id: Unique pattern identifier (content hash).
            pattern_label: Human-readable cluster label.
            centroid_hash: Hash of the cluster centroid embedding.
            member_count: Number of failure events in this cluster.
            ts: Optional timestamp tag.

        Returns:
            True if entity created.
        """
        if not self._bridge:
            return False

        entity_name = f"SLFailurePattern_{pattern_id[:16]}"
        try:
            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_PATTERN,
                observations=[
                    f"pattern_id={pattern_id[:32]}",
                    f"label={_trunc(pattern_label, 80)}",
                    f"centroid_hash={centroid_hash[:16]}",
                    f"member_count={member_count}",
                    f"ts={ts}",
                ],
            )
            return True
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-silent-swallower
            logger.debug("[SLMemoryBridge] persist_failure_pattern failed: %s", e)
            return False

    def query_failure_patterns(self) -> list[dict[str, Any]]:
        """Return all persisted failure pattern entities."""
        if not self._bridge:
            return []
        try:
            return self._bridge.search_entities("SLFailurePattern")
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-silent-swallower
            logger.debug("[SLMemoryBridge] query_failure_patterns failed: %s", e)
            return []


def get_sl_memory_bridge() -> SystemLearningMemoryBridge:
    """Return the process-global SystemLearningMemoryBridge instance."""
    return SystemLearningMemoryBridge.get_instance()


__all__ = [
    "SystemLearningMemoryBridge",
    "get_sl_memory_bridge",
]
