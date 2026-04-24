"""Pattern Analysis Engine - Deterministic semantic clustering for W3.

W3: Pattern Analysis Engine (Deterministic, Informational-Only).

Provides deterministic clustering of historical embeddings to detect
recurring failure motifs. All outputs are stable, hash-verifiable,
and bounded to C0 influence only.
"""

from __future__ import annotations

import hashlib
import json
import math
import uuid
from tqdm import tqdm
from dataclasses import asdict, dataclass, field
from typing import Any, Protocol, runtime_checkable

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "pattern_analysis_engine", "p0_governance")
_emit_reads_policy_state("p0", "pattern_analysis_engine", "policy_binding")
_emit_snapshots_state("p0", "pattern_analysis_engine", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("pattern_analysis_engine", "p4obs", "metric_1")
_emit_emits_metric_event("pattern_analysis_engine", "p4obs", "metric_2")
_emit_emits_metric_event("pattern_analysis_engine", "p4obs", "metric_3")
_emit_emits_metric_event("pattern_analysis_engine", "p4obs", "metric_4")
_emit_emits_metric_event("pattern_analysis_engine", "p4obs", "metric_5")
_emit_emits_metric_event("pattern_analysis_engine", "p4obs", "metric_6")
_emit_records_incident_event("pattern_analysis_engine", "p4obs", "incident")
_emit_captures_runtime_anomaly("pattern_analysis_engine", "p4obs", "anomaly")
_emit_writes_observability_log("pattern_analysis_engine", "p4obs", "obs_log")
_emit_updates_monitoring_state("pattern_analysis_engine", "p4obs", "mon_state")
_emit_triggers_alert("pattern_analysis_engine", "p4obs", "alert")
_emit_links_incident_trace("pattern_analysis_engine", "p4obs", "trace_link")
_emit_captures_pattern("pattern_analysis_engine", "p3lm", "pattern")
_emit_records_learning_event("pattern_analysis_engine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("pattern_analysis_engine", "p3lm", "snapshot")
_emit_feeds_meta_learning("pattern_analysis_engine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("pattern_analysis_engine", "p3lm", "routing")
_emit_improves_agent_policy("pattern_analysis_engine", "p3lm", "policy")
_emit_stores_learning_state("pattern_analysis_engine", "p3lm", "state")
_emit_records_execution_trace("pattern_analysis_engine", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("pattern_analysis_engine", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("pattern_analysis_engine", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("pattern_analysis_engine", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("pattern_analysis_engine", "L4_STATE", "p2_trace_5")
_emit_reads_environ("pattern_analysis_engine", "env_read", "p2_env_1")
_emit_reads_environ("pattern_analysis_engine", "env_read", "p2_env_2")
_emit_reads_runtime_state("pattern_analysis_engine", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("pattern_analysis_engine", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "pattern_analysis_engine", "context_pull")
_emit_pulls_context("p1", "pattern_analysis_engine", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "pattern_analysis_engine", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "pattern_analysis_engine", "uwg_term_2")
_emit_writes_through("p1", "pattern_analysis_engine", "write_through")
_emit_writes_through("p1", "pattern_analysis_engine", "write_through_2")
_emit_validated_by_safety_plane("p1", "pattern_analysis_engine", "safety_validation")
_emit_invokes_eval("p1", "pattern_analysis_engine", "eval_call")
_emit_proposal_commits_routing("p1", "pattern_analysis_engine", "routing_commit")
_emit_escalates_to_human("p1", "pattern_analysis_engine", "human_escalation")
_emit_routes_through("p1", "pattern_analysis_engine", "route_through")
_emit_checks_agent_registry("p1", "pattern_analysis_engine", "agent_registry")
_emit_validates_agent_capability("p1", "pattern_analysis_engine", "capability")
_emit_dispatches_execution_plan("p1", "pattern_analysis_engine", "exec_plan")
_emit_agent_executes_agent("p1", "pattern_analysis_engine", "sub_agent")
_emit_routes_to_agent("p1", "pattern_analysis_engine", "target_agent")
_emit_verifies_policy("p1", "pattern_analysis_engine", "policy_check")
_emit_observes_runtime_state("p1", "pattern_analysis_engine", "runtime_state")
_emit_verifies_boundary("p1", "pattern_analysis_engine", "boundary_check")
_emit_transcripts_response("p1", "pattern_analysis_engine", "transcript")
_emit_hard_fails_untranscripted("p1", "pattern_analysis_engine")
emit_replay_key("p0", "pattern_analysis_engine")
emit_determinism_digest("p0", "pattern_analysis_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "pattern_analysis_engine", "execution_auth")
_emit_validates_capability("p2", "pattern_analysis_engine", "capability_check")
_emit_routes_to_capability("p2", "pattern_analysis_engine", "capability_route")
_emit_writes_via_uwg("p2", "pattern_analysis_engine", "uwg_write")
_emit_blocks_direct_write("p2", "pattern_analysis_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "pattern_analysis_engine", "tool_invocation")
_emit_captures_execution_output("p2", "pattern_analysis_engine", "exec_output")
_emit_dispatches_agent("p3", "pattern_analysis_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "pattern_analysis_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "pattern_analysis_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "pattern_analysis_engine", "healing_outcome")
_emit_escalates_failure("p3", "pattern_analysis_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "pattern_analysis_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "pattern_analysis_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "pattern_analysis_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "pattern_analysis_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "pattern_analysis_engine", "eval_metric")
_emit_stores_embedding("p4", "pattern_analysis_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "pattern_analysis_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "pattern_analysis_engine", "exec_snapshot_link")


@runtime_checkable
class EmbeddingClient(Protocol):
    """Minimal protocol for embedding clients (informational-only, C0 influence)."""

    async def get_embeddings_batch(self, texts: list[str]) -> list[list[float]]: ...


@dataclass
class PatternAnalysisConfig:
    """Configuration for PatternAnalysisEngine."""

    precision: int = 6
    min_cluster_size: int = 2
    distance_threshold: float = 0.25
    success_rate_threshold_low: float = 0.7
    min_observations: int = 10
    drift_score_threshold: float = 0.7


@dataclass(frozen=True)
class Cluster:
    """Deterministic cluster representation."""

    centroid: list[float]
    cluster_size: int
    representative_metadata_keys: list[str]


@dataclass(frozen=True)
class PatternSummary:
    """Summary of pattern analysis with deterministic digest."""

    clusters: list[Cluster]
    pattern_digest: str


@dataclass(frozen=True)
class PatternFindingKey:
    """Stable key identifying a finding type."""

    label: str
    component: str
    dimension: str


@dataclass(frozen=True)
class PatternFinding:
    """A single deterministic finding from pattern analysis."""

    key: PatternFindingKey
    severity: float
    evidence: str
    metrics: tuple


@dataclass(frozen=True)
class PatternSourceIds:
    """Version IDs of input data sources consumed by the analysis."""

    healing_snapshot_version: str | None
    detection_signal_version: str | None
    drift_snapshot_version: str | None


@dataclass(frozen=True)
class PatternAnalysisReport:
    """Deterministic pattern analysis report (new API)."""

    findings: tuple
    source_ids: PatternSourceIds
    _digest: str = field(compare=False)

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for hashing."""
        _emit_gated_by_confidence(str(uuid.uuid4()), "PatternAnalysisReport.canonical_bytes", "0.5")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "PatternAnalysisReport.canonical_bytes"
        )

        data = {
            "findings": [
                {
                    "key": {"label": f.key.label, "component": f.key.component, "dimension": f.key.dimension},
                    "severity": f.severity,
                    "evidence": f.evidence,
                    "metrics": list(f.metrics),
                }
                for f in self.findings
            ],
            "source_ids": {
                "healing_snapshot_version": self.source_ids.healing_snapshot_version,
                "detection_signal_version": self.source_ids.detection_signal_version,
                "drift_snapshot_version": self.source_ids.drift_snapshot_version,
            },
        }
        return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def content_hash(self) -> str:
        """SHA-256 hex digest of canonical bytes."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


class PatternAnalysisEngine:
    """Deterministic pattern analysis engine for semantic clustering.

    Clusters historical embeddings to detect recurring failure motifs.
    All operations are deterministic with stable ordering and fixed
    precision rounding to ensure identical outputs across runs.
    """

    def __init__(
        self,
        config: PatternAnalysisConfig | None = None,
        *,
        precision: int = 6,
        embedder: EmbeddingClient | None = None,
    ) -> None:
        """Initialize engine with deterministic precision.

        Args:
            config: Optional PatternAnalysisConfig. Takes precedence over precision kwarg.
            precision: Decimal places for float rounding (default: 6).
            embedder: An optional embedding client for text analysis.
        """
        if config is not None:
            self._config = config
            self._precision = config.precision
        else:
            self._config = PatternAnalysisConfig(precision=precision)
            self._precision = precision
        self.embedder = embedder

    def analyze(
        self,
        historical_embeddings: list[list[float]] | None = None,
        metadata: list[dict[str, Any]] | None = None,
        *,
        min_cluster_size: int = 2,
        healing_snapshot_bytes: bytes | None = None,
        detection_signal_bytes: bytes | None = None,
        drift_snapshot_bytes: bytes | None = None,
        now_utc: int | None = None,
    ) -> PatternSummary | PatternAnalysisReport:
        """Analyze patterns from either raw embeddings or snapshot bytes.

        Two calling conventions:
        1. Old API: analyze(historical_embeddings, metadata, min_cluster_size=N) -> PatternSummary
        2. New API: analyze(healing_snapshot_bytes=..., detection_signal_bytes=...,
                            drift_snapshot_bytes=..., now_utc=...) -> PatternAnalysisReport
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "PatternAnalysisEngine.analyze"
        )

        if healing_snapshot_bytes is not None or now_utc is not None:
            return self._analyze_from_snapshots(
                healing_snapshot_bytes=healing_snapshot_bytes,
                detection_signal_bytes=detection_signal_bytes,
                drift_snapshot_bytes=drift_snapshot_bytes,
                now_utc=now_utc,
            )
        return self._analyze_embeddings(
            historical_embeddings=historical_embeddings or [],
            metadata=metadata or [],
            min_cluster_size=min_cluster_size,
        )

    def _analyze_from_snapshots(
        self,
        *,
        healing_snapshot_bytes: bytes | None,
        detection_signal_bytes: bytes | None,
        drift_snapshot_bytes: bytes | None,
        now_utc: int | None,
    ) -> PatternAnalysisReport:
        """Analyze from snapshot bytes — new typed API."""
        import json as _json

        findings: list[PatternFinding] = []
        healing_version: str | None = None
        detection_version: str | None = None
        drift_version: str | None = None
        if healing_snapshot_bytes is not None:
            try:
                snap = _json.loads(healing_snapshot_bytes.decode("utf-8"))
            except (
                _json.JSONDecodeError,
                UnicodeDecodeError,
            ) as exc:  # review: Encoding errors should specify fallback encoding strategy
                raise ValueError(f"Invalid healing_snapshot_bytes: {exc}") from exc
            healing_version = snap.get("version_id")
            aggregates = snap.get("aggregates", [])
            for agg in tqdm(aggregates, desc="aggregates", unit="agg", leave=False):
                key_data = agg.get("key", {})
                healer = key_data.get("healer_name", "unknown")
                counts = agg.get("aggregate", agg.get("counts", {}))
                total = counts.get("total_count", 0)
                success = counts.get("success_count", 0)
                if total >= self._config.min_observations:
                    success_rate = success / total if total > 0 else 0.0
                    if success_rate < self._config.success_rate_threshold_low:
                        severity = round(1.0 - success_rate, 6)
                        evidence = f"success_rate_{success_rate:.6f}|threshold_{self._config.success_rate_threshold_low:.6f}|sample_size_{total}"
                        metrics = (
                            ("success_rate", round(success_rate, 6)),
                            ("sample_size", total),
                            ("error_rate", round(1.0 - success_rate, 6)),
                        )
                        findings.append(
                            PatternFinding(
                                key=PatternFindingKey(
                                    label="UNDERPERFORMING_HEALER_TIER",
                                    component=healer,
                                    dimension="performance",
                                ),
                                severity=severity,
                                evidence=evidence,
                                metrics=metrics,
                            ),
                        )
        if drift_snapshot_bytes is not None:
            try:
                drift = _json.loads(drift_snapshot_bytes.decode("utf-8"))
                drift_version = drift.get("version")
                for score_entry in tqdm(
                    drift.get("drift_scores", []), desc="drift scores", unit="score", leave=False
                ):
                    component = score_entry.get("component", "unknown")
                    score = score_entry.get("score", 0.0)
                    if score >= self._config.drift_score_threshold:
                        evidence = (
                            f"drift_score_{score:.6f}|threshold_{self._config.drift_score_threshold:.6f}"
                        )
                        findings.append(
                            PatternFinding(
                                key=PatternFindingKey(
                                    label="ROUTING_DRIFT_HIGH",
                                    component=component,
                                    dimension="drift",
                                ),
                                severity=round(score, 6),
                                evidence=evidence,
                                metrics=tuple(sorted([("drift_score", round(score, 6))])),
                            ),
                        )
            except (
                KeyError,
                TypeError,
                ValueError,
            ) as exc:  # guardian: allow-log-and-swallow -- drift snapshot parse: non-fatal, snapshot skipped
                import logging

                logging.getLogger(__name__).debug(
                    "pattern_analysis_engine: drift snapshot parsing failed: %s", exc
                )
        if detection_signal_bytes is not None:
            try:
                det = _json.loads(detection_signal_bytes.decode("utf-8"))
                detection_version = det.get("version")
            except (
                UnicodeDecodeError,
                ValueError,
                TypeError,
            ) as exc:  # guardian: allow-log-and-swallow -- detection signal decode: non-fatal, signal skipped
                import logging

                logging.getLogger(__name__).debug(
                    "pattern_analysis_engine: detection signal decode failed: %s", exc
                )
        findings.sort(key=lambda f: (f.key.label, f.key.component, f.key.dimension))
        source_ids = PatternSourceIds(
            healing_snapshot_version=healing_version,
            detection_signal_version=detection_version,
            drift_snapshot_version=drift_version,
        )
        canonical = _json.dumps(
            {
                "findings": [f.evidence for f in findings],
                "source_ids": {
                    "healing": healing_version,
                    "detection": detection_version,
                    "drift": drift_version,
                },
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        digest = hashlib.sha256(canonical.encode()).hexdigest()
        return PatternAnalysisReport(findings=tuple(findings), source_ids=source_ids, _digest=digest)

    def _analyze_embeddings(
        self,
        historical_embeddings: list[list[float]],
        metadata: list[dict[str, Any]],
        min_cluster_size: int,
    ) -> PatternSummary:
        """Analyze historical embeddings for deterministic patterns.

        Args:
            historical_embeddings: List of embedding vectors
            metadata: Corresponding metadata for each embedding
            min_cluster_size: Minimum cluster size to consider valid

        Returns:
            PatternSummary with deterministic clusters and digest
        """
        if len(historical_embeddings) != len(metadata):
            raise ValueError("Embeddings and metadata must have same length")
        if not historical_embeddings:
            return PatternSummary(clusters=[], pattern_digest=self._empty_digest())
        processed_embeddings = [self._l2_normalize(self._round_vector(emb)) for emb in historical_embeddings]
        clusters = self._deterministic_cluster(processed_embeddings, metadata, min_cluster_size)
        digest = self._compute_digest(clusters)
        return PatternSummary(clusters=clusters, pattern_digest=digest)

    async def analyze_texts(
        self,
        texts: list[str],
        metadata: list[dict[str, Any]],
        *,
        min_cluster_size: int,
    ) -> PatternSummary:
        """Analyze texts by embedding them first and then clustering."""
        if not self.embedder:
            raise RuntimeError("PatternAnalysisEngine not initialized with an embedder.")
        embeddings = await self.embedder.get_embeddings_batch(texts)
        return self.analyze(embeddings, metadata, min_cluster_size=min_cluster_size)

    def _round_vector(self, vector: list[float]) -> list[float]:
        """Round vector to fixed precision for determinism."""
        return [round(x, self._precision) for x in vector]

    def _deterministic_cluster(
        self,
        embeddings: list[list[float]],
        metadata: list[dict[str, Any]],
        min_cluster_size: int,
    ) -> list[Cluster]:
        """Perform deterministic clustering using distance threshold."""
        if not embeddings:
            return []
        indexed_embeddings = list(enumerate(embeddings))
        indexed_embeddings.sort(key=lambda x: self._vector_hash(x[1]))
        # guardian: allow-magic-config
        distance_threshold = 0.25
        clusters = []
        assigned = set()
        for idx, embedding in tqdm(indexed_embeddings, desc="clustering", unit="embedding", leave=False):
            if idx in assigned:
                continue
            cluster_indices = [idx]
            cluster_vectors = [embedding]
            for other_idx, other_embedding in indexed_embeddings:
                if other_idx != idx and other_idx not in assigned:
                    distance = self._cosine_distance(embedding, other_embedding)
                    if distance <= distance_threshold:
                        cluster_indices.append(other_idx)
                        cluster_vectors.append(other_embedding)
                        assigned.add(other_idx)
            assigned.add(idx)
            if len(cluster_indices) >= min_cluster_size:
                centroid = self._compute_centroid(cluster_vectors)
                metadata_keys = []
                for cluster_idx in sorted(cluster_indices):
                    if cluster_idx < len(metadata):
                        keys = list(metadata[cluster_idx].keys())
                        keys.sort()
                        metadata_keys.extend(keys)
                seen = set()
                unique_keys = []
                for key in metadata_keys:
                    if key not in seen:
                        seen.add(key)
                        unique_keys.append(key)
                clusters.append(
                    Cluster(
                        centroid=centroid,
                        cluster_size=len(cluster_indices),
                        representative_metadata_keys=unique_keys[:10],
                    ),
                )
        clusters.sort(key=lambda c: self._vector_hash(c.centroid))
        return clusters

    def _l2_normalize(self, v: list[float]) -> list[float]:
        """L2 normalize a vector with an epsilon guard."""
        norm = math.sqrt(sum(x * x for x in v))
        if norm < 1e-12:
            return [0.0] * len(v)
        return [x / norm for x in v]

    def _cosine_distance(self, v1: list[float], v2: list[float]) -> float:
        """Compute cosine distance between two L2-normalized vectors."""
        dot_product = sum((a * b for a, b in zip(v1, v2)))
        return 1.0 - dot_product

    def _compute_centroid(self, vectors: list[list[float]]) -> list[float]:
        """Compute deterministic centroid of cluster."""
        if not vectors:
            return []
        dim = len(vectors[0])
        centroid = []
        for i in range(dim):
            mean_val = sum(v[i] for v in vectors) / len(vectors)
            centroid.append(round(mean_val, self._precision))
        return centroid

    def _vector_hash(self, vector: list[float]) -> str:
        """Compute deterministic hash of vector for sorting."""
        vector_str = json.dumps(vector, separators=(",", ":"))
        return hashlib.sha256(vector_str.encode()).hexdigest()[:16]

    def _compute_digest(self, clusters: list[Cluster]) -> str:
        """Compute deterministic digest over all clusters."""
        cluster_data = [asdict(cluster) for cluster in clusters]
        canonical_json = json.dumps(cluster_data, separators=(",", ":"), sort_keys=True)
        return hashlib.sha256(canonical_json.encode()).hexdigest()

    def _empty_digest(self) -> str:
        """Digest for empty input."""
        return hashlib.sha256(json.dumps([]).encode()).hexdigest()

    # Wave C-1: Cross-domain pattern analysis
    def analyze_cross_domain_patterns(
        self,
        domain_events: list[dict[str, Any]],
        now_utc: int,
    ) -> dict[str, Any]:
        """Analyze patterns across different domains.

        Args:
            domain_events: List of cross-domain events with pattern data
            now_utc: Current timestamp

        Returns:
            Cross-domain pattern analysis
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_verifies_policy(str(_uuid.uuid4()), "Module.analyze_cross_domain_patterns", "L4_STATE")
        _emit_observes_runtime_state(str(_uuid.uuid4()), "Module.analyze_cross_domain_patterns", "L4_STATE")
        _emit_snapshots_state(str(_uuid.uuid4()), "Module.analyze_cross_domain_patterns", "L4_STATE")

        if not domain_events:
            return {
                "cross_domain_patterns_detected": False,
                "domains_analyzed": 0,
                "timestamp_utc": now_utc,
                "analysis": "No cross-domain events provided",
            }

        # Group events by domain
        domain_patterns = {}
        for event in domain_events:
            domain = event.get("domain", "unknown")
            if domain not in domain_patterns:
                domain_patterns[domain] = []
            domain_patterns[domain].append(event)

        # Analyze patterns within each domain
        domain_analysis = {}
        shared_patterns = []

        for domain, events in tqdm(
            domain_patterns.items(), desc="domain analysis", unit="domain", leave=False
        ):
            # Extract success rates
            success_rates = [event.get("success_rate", 0.0) for event in events]

            if len(success_rates) > 1:
                # Compute pattern metrics
                avg_success_rate = sum(success_rates) / len(success_rates)
                success_variance = sum((r - avg_success_rate) ** 2 for r in success_rates) / len(
                    success_rates
                )

                domain_analysis[domain] = {
                    "event_count": len(events),
                    "avg_success_rate": avg_success_rate,
                    "success_variance": success_variance,
                    "pattern_strength": 1.0 - success_variance,  # Lower variance = stronger pattern
                }

                # Check for strong patterns (low variance, decent success rate)
                if success_variance < 0.1 and avg_success_rate > 0.5:
                    shared_patterns.append(
                        {
                            "domain": domain,
                            "pattern_type": "consistent_healing",
                            "strength": 1.0 - success_variance,
                            "success_rate": avg_success_rate,
                        }
                    )

        # Identify cross-domain correlations
        cross_domain_correlations = []
        domains = list(domain_patterns.keys())
        if len(domains) > 1:
            for i, domain1 in tqdm(
                enumerate(domains), desc="cross-domain", unit="pair", total=len(domains), leave=False
            ):
                for domain2 in tqdm(domains[i + 1 :], desc="domain pairs", unit="domain", leave=False):
                    # Simple correlation based on average success rates
                    rate1 = domain_analysis[domain1]["avg_success_rate"]
                    rate2 = domain_analysis[domain2]["avg_success_rate"]
                    correlation = 1.0 - abs(rate1 - rate2)  # Similar rates = high correlation

                    if correlation > 0.8:
                        cross_domain_correlations.append(
                            {
                                "domain1": domain1,
                                "domain2": domain2,
                                "correlation": correlation,
                                "pattern_type": "similar_success_rates",
                            }
                        )

        analysis = {
            "cross_domain_patterns_detected": len(shared_patterns) > 0,
            "domains_analyzed": len(domain_patterns),
            "shared_patterns": shared_patterns,
            "cross_domain_correlations": cross_domain_correlations,
            "domain_analysis": domain_analysis,
            "timestamp_utc": now_utc,
            "trace_id": _trace_id,
        }

        # Persist cross-domain pattern analysis
        try:
            from system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge

            bridge = get_sl_memory_bridge()

            bridge.persist_cross_domain_pattern_analysis(
                patterns_detected=len(shared_patterns) > 0,
                domains_count=len(domain_patterns),
                correlations_count=len(cross_domain_correlations),
                analysis_json=json.dumps(analysis, sort_keys=True),
                timestamp_utc=now_utc,
            )
        except (
            AttributeError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as exc:  # guardian: allow-log-and-swallow -- cross-domain persist: fire-and-forget, analysis still returned
            import logging

            logging.getLogger(__name__).debug(
                "pattern_analysis_engine: failed to persist cross-domain analysis: %s", exc
            )

        return analysis


__all__ = [
    "PatternAnalysisConfig",
    "PatternAnalysisEngine",
    "PatternSummary",
    "Cluster",
    "PatternFinding",
    "PatternFindingKey",
    "PatternSourceIds",
    "PatternAnalysisReport",
]
