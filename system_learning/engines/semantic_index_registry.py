"""SemanticIndexRegistry — Unified facade over all 7 BGE semantic indexes.

Provides a single entry-point for the meta-learning bus and telemetry
pipeline to ingest into and query across all semantic memory indexes:

  incident_index    — IncidentBundle cases (healer selection, failure clustering)
  graph_index       — GraphNeighborhood motifs (mutation broker detection)
  mutation_index    — MutationDiffRecord cases (rollback strategy, risk scoring)
  prompt_index      — PromptOutcomeEmbeddingRecord (template selection, drift)
  retrieval_index   — RetrievalCaseRecord (chunk ranking, corpus expansion)
  replay_index      — ReplayFailureRecord (determinism clustering, triage)
  preference_index  — PathDPreferencePair (DPO dataset, HITL precedent)

Design constraints:
- No wall-clock reads; timestamps caller-supplied.
- Thread-safe: delegates to individual embedders which hold their own locks.
- C0_INFORMATIONAL: no routing influence from any result.
- Registry itself carries no mutable state beyond the 7 embedder instances.
- Fail-safe: routing errors from one embedder never affect others.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from system_learning.config.semantic_memory_config import (
    DEFAULT_EMBEDDER_BUFFER_SIZE,
    GRAPH_NEIGHBORHOOD_BUFFER_SIZE,
)
from system_learning.engines.graph_neighborhood_embedder import (
    GraphNeighborhoodEmbedder,
    NeighborhoodRetrievalResult,
)
from system_learning.engines.healer_outcome_embedder import (
    HealerOutcomeEmbedder,
    HealerRetrievalResult,
)
from system_learning.engines.incident_bundle_embedder import (
    IncidentBundleEmbedder,
    IncidentRetrievalResult,
)
from system_learning.engines.mutation_diff_embedder import (
    MutationDiffEmbedder,
    MutationRetrievalResult,
)
from system_learning.engines.path_d_preference_embedder import (
    PathDPreferenceEmbedder,
    PreferenceRetrievalResult,
)
from system_learning.engines.policy_guardrail_embedder import (
    PolicyGuardrailEmbedder,
    GuardrailRetrievalResult,
)
from system_learning.engines.prompt_outcome_embedder import (
    PromptOutcomeEmbedder,
    PromptOutcomeRetrievalResult,
)
from system_learning.engines.replay_failure_embedder import (
    ReplayFailureEmbedder,
    ReplayFailureRetrievalResult,
)
from system_learning.engines.retrieval_case_embedder import (
    RetrievalCaseEmbedder,
    RetrievalCaseRetrievalResult,
)
from system_learning.engines.embedding_corpus_extraction import CorpusRecord
from system_learning.types.semantic_memory_types import (
    GraphNeighborhood,
    HealerOutcomeRecord,
    IncidentBundle,
    MutationDiffRecord,
    PathDPreferencePair,
    PolicyGuardrailCase,
    PromptOutcomeEmbeddingRecord,
    ReplayFailureRecord,
    RetrievalCaseRecord,
)

logger = logging.getLogger(__name__)

# Index name constants — used as keys in snapshot dicts
INDEX_INCIDENT = "incident_index"
INDEX_GRAPH = "graph_index"
INDEX_MUTATION = "mutation_index"
INDEX_PROMPT = "prompt_index"
INDEX_RETRIEVAL = "retrieval_index"
INDEX_REPLAY = "replay_index"
INDEX_PREFERENCE = "preference_index"
INDEX_GUARDRAIL = "guardrail_index"

ALL_INDEXES = frozenset({
    INDEX_INCIDENT,
    INDEX_GRAPH,
    INDEX_MUTATION,
    INDEX_PROMPT,
    INDEX_RETRIEVAL,
    INDEX_REPLAY,
    INDEX_PREFERENCE,
    INDEX_GUARDRAIL,
})


@dataclass(frozen=True)
class RegistryBufferSnapshot:
    """Buffer size snapshot across all 8 indexes.

    Returned by SemanticIndexRegistry.buffer_snapshot() for monitoring.
    C0_INFORMATIONAL — no routing influence.
    """

    incident_index: int
    graph_index: int
    mutation_index: int
    prompt_index: int
    retrieval_index: int
    replay_index: int
    preference_index: int
    guardrail_index: int

    @property
    def total(self) -> int:
        """Total records across all indexes."""
        return (
            self.incident_index
            + self.graph_index
            + self.mutation_index
            + self.prompt_index
            + self.retrieval_index
            + self.replay_index
            + self.preference_index
            + self.guardrail_index
        )


@dataclass(frozen=True)
class MultiIndexIngestResult:
    """Result of a multi-index ingest operation.

    Records which index received the record and its content_hash.
    """

    index_name: str
    content_hash: str
    trace_id: str


class SemanticIndexRegistry:
    """Unified facade over all 8 BGE semantic memory indexes.

    Instantiate once per process and share across components that need
    to ingest into or query the semantic memory layer.

    Usage:
        registry = SemanticIndexRegistry()

        # Ingest
        registry.ingest_incident(bundle)
        registry.ingest_prompt_outcome(record)
        registry.ingest_retrieval_case(record)

        # Query (requires live embedding gateway)
        results = registry.query_incidents("IMPORT_ERROR in L3", k=5)

        # Monitoring
        snap = registry.buffer_snapshot()
        print(snap.total)

        # Telemetry hook
        trace_records = registry.export_all_corpus_records()
    """

    def __init__(
        self,
        *,
        incident_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE,
        graph_buffer: int = GRAPH_NEIGHBORHOOD_BUFFER_SIZE,
        mutation_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE,
        prompt_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE,
        retrieval_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE,
        replay_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE,
        preference_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE,
        guardrail_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE,
    ) -> None:
        self.incident = IncidentBundleEmbedder(max_buffer=incident_buffer)
        self.graph = GraphNeighborhoodEmbedder(max_buffer=graph_buffer)
        self.mutation = MutationDiffEmbedder(max_buffer=mutation_buffer)
        self.prompt = PromptOutcomeEmbedder(max_buffer=prompt_buffer)
        self.retrieval = RetrievalCaseEmbedder(max_buffer=retrieval_buffer)
        self.replay = ReplayFailureEmbedder(max_buffer=replay_buffer)
        self.preference = PathDPreferenceEmbedder(max_buffer=preference_buffer)
        self.guardrail = PolicyGuardrailEmbedder(max_buffer=guardrail_buffer)

    # -----------------------------------------------------------------------
    # Ingest helpers
    # -----------------------------------------------------------------------

    def ingest_incident(self, bundle: IncidentBundle) -> MultiIndexIngestResult:
        r = self.incident.ingest(bundle)
        return MultiIndexIngestResult(INDEX_INCIDENT, r.content_hash, r.trace_id)

    def ingest_graph_neighborhood(
        self, neighborhood: GraphNeighborhood
    ) -> MultiIndexIngestResult:
        r = self.graph.ingest(neighborhood)
        return MultiIndexIngestResult(INDEX_GRAPH, r.content_hash, r.trace_id)

    def ingest_mutation(self, record: MutationDiffRecord) -> MultiIndexIngestResult:
        r = self.mutation.ingest(record)
        return MultiIndexIngestResult(INDEX_MUTATION, r.content_hash, r.trace_id)

    def ingest_prompt_outcome(
        self, record: PromptOutcomeEmbeddingRecord
    ) -> MultiIndexIngestResult:
        r = self.prompt.ingest(record)
        return MultiIndexIngestResult(INDEX_PROMPT, r.content_hash, r.trace_id)

    def ingest_retrieval_case(
        self, record: RetrievalCaseRecord
    ) -> MultiIndexIngestResult:
        r = self.retrieval.ingest(record)
        return MultiIndexIngestResult(INDEX_RETRIEVAL, r.content_hash, r.trace_id)

    def ingest_replay_failure(
        self, record: ReplayFailureRecord
    ) -> MultiIndexIngestResult:
        r = self.replay.ingest(record)
        return MultiIndexIngestResult(INDEX_REPLAY, r.content_hash, r.trace_id)

    def ingest_preference(self, pair: PathDPreferencePair) -> MultiIndexIngestResult:
        r = self.preference.ingest(pair)
        return MultiIndexIngestResult(INDEX_PREFERENCE, r.content_hash, r.trace_id)

    def ingest_guardrail_case(
        self, case: PolicyGuardrailCase
    ) -> MultiIndexIngestResult:
        r = self.guardrail.ingest(case)
        return MultiIndexIngestResult(INDEX_GUARDRAIL, r.content_hash, r.trace_id)

    # -----------------------------------------------------------------------
    # Query helpers (delegate to individual embedders)
    # -----------------------------------------------------------------------

    def query_incidents(
        self, query_text: str, *, k: int = 5
    ) -> list[IncidentRetrievalResult]:
        """Retrieve similar historical incidents."""
        from system_learning.types.semantic_memory_types import IncidentBundle as _IB
        try:
            from agentic_core.interfaces.embeddings import query_similarity
            raw = query_similarity(query_text, top_k=min(k, 20),
                                   namespace="incident_bundles")
            out: list[IncidentRetrievalResult] = []
            for r in raw:
                meta = self.incident._meta.get(r.content_hash, {})  # noqa: SLF001
                out.append(IncidentRetrievalResult(
                    content_hash=r.content_hash,
                    similarity_score=r.similarity_score,
                    trace_id=meta.get("trace_id", ""),
                    outcome=meta.get("outcome", ""),
                    healer_id=meta.get("healer_id", ""),
                    route_path=meta.get("route_path", ""),
                    content_preview=r.content_preview,
                ))
            return out
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("SemanticIndexRegistry.query_incidents: %s", exc)
            return []

    def query_graph_motifs(
        self, query_text: str, *, k: int = 5
    ) -> list[NeighborhoodRetrievalResult]:
        """Retrieve similar architectural motifs from the graph index."""
        try:
            from agentic_core.interfaces.embeddings import query_similarity
            raw = query_similarity(query_text, top_k=min(k, 20),
                                   namespace="graph_neighborhoods")
            out: list[NeighborhoodRetrievalResult] = []
            for r in raw:
                meta = self.graph._meta.get(r.content_hash, {})  # noqa: SLF001
                out.append(NeighborhoodRetrievalResult(
                    content_hash=r.content_hash,
                    similarity_score=r.similarity_score,
                    node_id=meta.get("node_id", ""),
                    node_type=meta.get("node_type", ""),
                    layer=meta.get("layer", ""),
                    risk_label=meta.get("risk_label", ""),
                    content_preview=r.content_preview,
                ))
            return out
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("SemanticIndexRegistry.query_graph_motifs: %s", exc)
            return []

    def query_mutations(
        self, query_text: str, *, k: int = 5
    ) -> list[MutationRetrievalResult]:
        """Retrieve similar prior mutations."""
        try:
            from agentic_core.interfaces.embeddings import query_similarity
            raw = query_similarity(query_text, top_k=min(k, 20),
                                   namespace="mutation_diffs")
            out: list[MutationRetrievalResult] = []
            for r in raw:
                meta = self.mutation._meta.get(r.content_hash, {})  # noqa: SLF001
                out.append(MutationRetrievalResult(
                    content_hash=r.content_hash,
                    similarity_score=r.similarity_score,
                    mutation_id=meta.get("mutation_id", ""),
                    target_resource=meta.get("target_resource", ""),
                    commit_outcome=meta.get("commit_outcome", ""),
                    content_preview=r.content_preview,
                ))
            return out
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("SemanticIndexRegistry.query_mutations: %s", exc)
            return []

    def query_prompt_outcomes(
        self, query_text: str, *, k: int = 5
    ) -> list[PromptOutcomeRetrievalResult]:
        """Retrieve similar prompt construction outcomes."""
        try:
            from agentic_core.interfaces.embeddings import query_similarity
            raw = query_similarity(query_text, top_k=min(k, 20),
                                   namespace="prompt_outcomes")
            out: list[PromptOutcomeRetrievalResult] = []
            for r in raw:
                meta = self.prompt._meta.get(r.content_hash, {})  # noqa: SLF001
                out.append(PromptOutcomeRetrievalResult(
                    content_hash=r.content_hash,
                    similarity_score=r.similarity_score,
                    record_id=meta.get("record_id", ""),
                    safety_outcome=meta.get("safety_outcome", ""),
                    template_id=meta.get("template_id", ""),
                    model=meta.get("model", ""),
                    content_preview=r.content_preview,
                ))
            return out
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("SemanticIndexRegistry.query_prompt_outcomes: %s", exc)
            return []

    def query_retrieval_cases(
        self, query_text: str, *, k: int = 5
    ) -> list[RetrievalCaseRetrievalResult]:
        """Retrieve similar RAG retrieval quality cases."""
        try:
            from agentic_core.interfaces.embeddings import query_similarity
            raw = query_similarity(query_text, top_k=min(k, 20),
                                   namespace="retrieval_cases")
            out: list[RetrievalCaseRetrievalResult] = []
            for r in raw:
                meta = self.retrieval._meta.get(r.content_hash, {})  # noqa: SLF001
                out.append(RetrievalCaseRetrievalResult(
                    content_hash=r.content_hash,
                    similarity_score=r.similarity_score,
                    case_id=meta.get("case_id", ""),
                    support_score=float(meta.get("support_score", 0.0)),
                    completeness_score=float(meta.get("completeness_score", 0.0)),
                    escalation_flag=bool(meta.get("escalation_flag", False)),
                    content_preview=r.content_preview,
                ))
            return out
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("SemanticIndexRegistry.query_retrieval_cases: %s", exc)
            return []

    def query_replay_failures(
        self, query_text: str, *, k: int = 5
    ) -> list[ReplayFailureRetrievalResult]:
        """Retrieve similar historical replay failures."""
        try:
            from agentic_core.interfaces.embeddings import query_similarity
            raw = query_similarity(query_text, top_k=min(k, 20),
                                   namespace="replay_failures")
            out: list[ReplayFailureRetrievalResult] = []
            for r in raw:
                meta = self.replay._meta.get(r.content_hash, {})  # noqa: SLF001
                out.append(ReplayFailureRetrievalResult(
                    content_hash=r.content_hash,
                    similarity_score=r.similarity_score,
                    failure_id=meta.get("failure_id", ""),
                    nondeterminism_type=meta.get("nondeterminism_type", ""),
                    replay_key=meta.get("replay_key", ""),
                    content_preview=r.content_preview,
                ))
            return out
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("SemanticIndexRegistry.query_replay_failures: %s", exc)
            return []

    def query_preferences(
        self, query_text: str, *, k: int = 5
    ) -> list[PreferenceRetrievalResult]:
        """Retrieve similar HITL preference precedents."""
        try:
            from agentic_core.interfaces.embeddings import query_similarity
            raw = query_similarity(query_text, top_k=min(k, 20),
                                   namespace="path_d_preferences")
            out: list[PreferenceRetrievalResult] = []
            for r in raw:
                meta = self.preference._meta.get(r.content_hash, {})  # noqa: SLF001
                out.append(PreferenceRetrievalResult(
                    content_hash=r.content_hash,
                    similarity_score=r.similarity_score,
                    decision_id=meta.get("decision_id", ""),
                    decision=meta.get("decision", ""),
                    agent=meta.get("agent", ""),
                    content_preview=r.content_preview,
                ))
            return out
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("SemanticIndexRegistry.query_preferences: %s", exc)
            return []

    def query_guardrail_cases(
        self, query_text: str, *, k: int = 5
    ) -> list[GuardrailRetrievalResult]:
        """Retrieve similar guardrail block cases."""
        try:
            from agentic_core.interfaces.embeddings import query_similarity
            raw = query_similarity(query_text, top_k=min(k, 20),
                                   namespace="policy_guardrail_cases")
            out: list[GuardrailRetrievalResult] = []
            for r in raw:
                meta = self.guardrail._meta.get(r.content_hash, {})  # noqa: SLF001
                out.append(GuardrailRetrievalResult(
                    content_hash=r.content_hash,
                    similarity_score=r.similarity_score,
                    case_id=meta.get("case_id", ""),
                    policy_hash=meta.get("policy_hash", ""),
                    verdict=meta.get("verdict", ""),
                    strictness_level=meta.get("strictness_level", ""),
                    content_preview=r.content_preview,
                ))
            return out
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("SemanticIndexRegistry.query_guardrail_cases: %s", exc)
            return []

    # -----------------------------------------------------------------------
    # Monitoring and telemetry
    # -----------------------------------------------------------------------

    def buffer_snapshot(self) -> RegistryBufferSnapshot:
        """Return buffer sizes across all 8 indexes."""
        return RegistryBufferSnapshot(
            incident_index=self.incident.buffer_size(),
            graph_index=self.graph.buffer_size(),
            mutation_index=self.mutation.buffer_size(),
            prompt_index=self.prompt.buffer_size(),
            retrieval_index=self.retrieval.buffer_size(),
            replay_index=self.replay.buffer_size(),
            preference_index=self.preference.buffer_size(),
            guardrail_index=self.guardrail.buffer_size(),
        )

    def export_all_corpus_records(self) -> dict[str, list[CorpusRecord]]:
        """Export sorted corpus record snapshots from all indexes.

        Returns:
            Dict mapping index_name -> sorted list of CorpusRecord.
            Useful for seed-pack building or telemetry dump.
        """
        return {
            INDEX_INCIDENT: self.incident.export_corpus_records(),
            INDEX_GRAPH: self.graph.export_corpus_records(),
            INDEX_MUTATION: self.mutation.export_corpus_records(),
            INDEX_PROMPT: self.prompt.export_corpus_records(),
            INDEX_RETRIEVAL: self.retrieval.export_corpus_records(),
            INDEX_REPLAY: self.replay.export_corpus_records(),
            INDEX_PREFERENCE: self.preference.export_corpus_records(),
            INDEX_GUARDRAIL: self.guardrail.export_corpus_records(),
        }

    def retrieval_quality_summary(self) -> dict[str, Any]:
        """Aggregate quality signals from the retrieval index.

        Delegates to RetrievalCaseEmbedder.quality_signal_summary().
        """
        return self.retrieval.quality_signal_summary()

    def prompt_safety_outcome_stats(self) -> dict[str, int]:
        """Aggregate safety outcomes from the prompt index.

        Delegates to PromptOutcomeEmbedder.safety_outcome_stats().
        """
        return self.prompt.safety_outcome_stats()

    def replay_nondeterminism_stats(self) -> dict[str, int]:
        """Nondeterminism type frequencies from the replay index.

        Delegates to ReplayFailureEmbedder.nondeterminism_type_stats().
        """
        return self.replay.nondeterminism_type_stats()

    def guardrail_verdict_stats(self) -> dict[str, int]:
        """Verdict frequencies from the guardrail index.

        Delegates to PolicyGuardrailEmbedder.verdict_stats().
        """
        return self.guardrail.verdict_stats()

    def total_buffer_utilization(self) -> dict[str, Any]:
        """Return buffer utilization fractions for all 8 indexes.

        For each index returns:
          - ``used``: current record count
          - ``capacity``: max_buffer configured at construction
          - ``utilization``: used / capacity rounded to 4 dp (0.0 when cap=0)

        Also includes ``total_used`` and ``total_capacity`` aggregate keys.

        Returns:
            Dict with one entry per index name plus aggregates.
        """
        def _frac(used: int, cap: int) -> float:
            return round(used / cap, 4) if cap > 0 else 0.0

        snap = self.buffer_snapshot()
        entries = {
            INDEX_INCIDENT: {
                "used": snap.incident_index,
                "capacity": self.incident._max_buffer,  # noqa: SLF001
                "utilization": _frac(snap.incident_index, self.incident._max_buffer),  # noqa: SLF001
            },
            INDEX_GRAPH: {
                "used": snap.graph_index,
                "capacity": self.graph._max_buffer,  # noqa: SLF001
                "utilization": _frac(snap.graph_index, self.graph._max_buffer),  # noqa: SLF001
            },
            INDEX_MUTATION: {
                "used": snap.mutation_index,
                "capacity": self.mutation._max_buffer,  # noqa: SLF001
                "utilization": _frac(snap.mutation_index, self.mutation._max_buffer),  # noqa: SLF001
            },
            INDEX_PROMPT: {
                "used": snap.prompt_index,
                "capacity": self.prompt._max_buffer,  # noqa: SLF001
                "utilization": _frac(snap.prompt_index, self.prompt._max_buffer),  # noqa: SLF001
            },
            INDEX_RETRIEVAL: {
                "used": snap.retrieval_index,
                "capacity": self.retrieval._max_buffer,  # noqa: SLF001
                "utilization": _frac(snap.retrieval_index, self.retrieval._max_buffer),  # noqa: SLF001
            },
            INDEX_REPLAY: {
                "used": snap.replay_index,
                "capacity": self.replay._max_buffer,  # noqa: SLF001
                "utilization": _frac(snap.replay_index, self.replay._max_buffer),  # noqa: SLF001
            },
            INDEX_PREFERENCE: {
                "used": snap.preference_index,
                "capacity": self.preference._max_buffer,  # noqa: SLF001
                "utilization": _frac(snap.preference_index, self.preference._max_buffer),  # noqa: SLF001
            },
            INDEX_GUARDRAIL: {
                "used": snap.guardrail_index,
                "capacity": self.guardrail._max_buffer,  # noqa: SLF001
                "utilization": _frac(snap.guardrail_index, self.guardrail._max_buffer),  # noqa: SLF001
            },
        }
        total_used = sum(v["used"] for v in entries.values())
        total_cap = sum(v["capacity"] for v in entries.values())
        entries["total_used"] = total_used  # type: ignore[assignment]
        entries["total_capacity"] = total_cap  # type: ignore[assignment]
        return entries

    def cross_index_health_report(self) -> dict[str, Any]:
        """Generate a unified health report across all 8 semantic indexes.

        Combines:
          - Buffer snapshot with utilization
          - Retrieval quality summary (avg scores, escalation rate)
          - Prompt safety outcome stats
          - Replay nondeterminism stats (top 3 types)
          - Guardrail verdict stats
          - Corpus expansion quality tier from retrieval index
          - Overall health: 'OK' | 'WARN' | 'CRITICAL'

        Health rules:
          - CRITICAL if retrieval quality_tier == 'CRITICAL'
          - WARN if retrieval quality_tier == 'DEGRADED' or any index > 90% full
          - OK otherwise

        Returns:
            Flat dict with health fields for telemetry emission.
        """
        util = self.total_buffer_utilization()
        rq = self.retrieval_quality_summary()
        prompt_stats = self.prompt_safety_outcome_stats()
        replay_stats = self.replay_nondeterminism_stats()
        guardrail_stats = self.guardrail_verdict_stats()
        exp_report = self.retrieval.corpus_expansion_report()

        top3_nd = sorted(replay_stats.items(), key=lambda kv: -kv[1])[:3]
        any_over_90 = any(
            v["utilization"] >= 0.9
            for k, v in util.items()
            if isinstance(v, dict) and "utilization" in v
        )

        tier = exp_report.get("quality_tier", "HEALTHY")
        if tier == "CRITICAL":
            health = "CRITICAL"
        elif tier == "DEGRADED" or any_over_90:
            health = "WARN"
        else:
            health = "OK"

        return {
            "health": health,
            "total_records": util.get("total_used", 0),
            "total_capacity": util.get("total_capacity", 0),
            "retrieval_avg_support_score": rq.get("avg_support_score", 0.0),
            "retrieval_avg_completeness_score": rq.get("avg_completeness_score", 0.0),
            "retrieval_escalation_rate": rq.get("escalation_rate", 0.0),
            "retrieval_quality_tier": tier,
            "prompt_blocked_count": prompt_stats.get("BLOCKED", 0),
            "prompt_escalated_count": prompt_stats.get("ESCALATED", 0),
            "replay_top3_nondeterminism": top3_nd,
            "guardrail_false_positive_count": guardrail_stats.get("false_positive", 0),
            "guardrail_true_positive_count": guardrail_stats.get("true_positive", 0),
        }

    def bulk_evict_by_trace_id(self, trace_id: str) -> dict[str, int]:
        """Evict all records matching a trace_id across every index.

        Used when a trace is invalidated (e.g. replay failure, policy revocation)
        and all derived semantic memory records must be retired atomically.

        Args:
            trace_id: The trace ID to evict across all indexes.

        Returns:
            Dict mapping index_name -> evicted_count for all 8 indexes.
            Indexes with zero evictions are still included.

        Raises:
            ValueError: If trace_id is empty.
        """
        if not trace_id:
            raise ValueError("trace_id must not be empty")

        def _evict_from(embedder: Any) -> int:
            evicted = 0
            with embedder._lock:  # noqa: SLF001
                keep = []
                for record in embedder._records:  # noqa: SLF001
                    if record.trace_id == trace_id:
                        embedder._meta.pop(record.content_hash, None)  # noqa: SLF001
                        evicted += 1
                    else:
                        keep.append(record)
                embedder._records = keep  # noqa: SLF001
            return evicted

        return {
            INDEX_INCIDENT:   _evict_from(self.incident),
            INDEX_GRAPH:      _evict_from(self.graph),
            INDEX_MUTATION:   _evict_from(self.mutation),
            INDEX_PROMPT:     _evict_from(self.prompt),
            INDEX_RETRIEVAL:  _evict_from(self.retrieval),
            INDEX_REPLAY:     _evict_from(self.replay),
            INDEX_PREFERENCE: _evict_from(self.preference),
            INDEX_GUARDRAIL:  _evict_from(self.guardrail),
        }

    @staticmethod
    def index_namespace_map() -> dict[str, str]:
        """Return the canonical namespace string for each index.

        Useful for building seed-pack manifests or verifying namespace routing.

        Returns:
            Dict mapping index_name -> namespace string.
        """
        return {
            INDEX_INCIDENT:   "incident_bundles",
            INDEX_GRAPH:      "graph_neighborhoods",
            INDEX_MUTATION:   "mutation_diffs",
            INDEX_PROMPT:     "prompt_outcomes",
            INDEX_RETRIEVAL:  "retrieval_cases",
            INDEX_REPLAY:     "replay_failures",
            INDEX_PREFERENCE: "path_d_preferences",
            INDEX_GUARDRAIL:  "policy_guardrail_cases",
        }


__all__ = [
    "SemanticIndexRegistry",
    "RegistryBufferSnapshot",
    "MultiIndexIngestResult",
    "INDEX_INCIDENT",
    "INDEX_GRAPH",
    "INDEX_MUTATION",
    "INDEX_PROMPT",
    "INDEX_RETRIEVAL",
    "INDEX_REPLAY",
    "INDEX_PREFERENCE",
    "INDEX_GUARDRAIL",
    "ALL_INDEXES",
]
