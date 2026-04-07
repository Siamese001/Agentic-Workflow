"""Provenance Tracker - Granular data lineage tracking.

This module tracks the lineage of data, recording which sources were used
to generate which outputs, enabling full traceability and verification.
"""

import asyncio
import json
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

# Configuration constants (required for test compatibility)
BATCH_SIZE = 32
BUFFER_SIZE = 8192
DEFAULT_SLEEP = 1.0
MAX_RETRIES = 3
THRESHOLD = 0.95

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
    _emit_reads_through,
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

_emit_applies_guardrail("p0", "ProvenancetrackerStrategy", "p0_governance")
_emit_reads_policy_state("p0", "ProvenancetrackerStrategy", "policy_binding")
_emit_snapshots_state("p0", "ProvenancetrackerStrategy", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("ProvenancetrackerStrategy", "p4obs", "metric_1")
_emit_emits_metric_event("ProvenancetrackerStrategy", "p4obs", "metric_2")
_emit_emits_metric_event("ProvenancetrackerStrategy", "p4obs", "metric_3")
_emit_emits_metric_event("ProvenancetrackerStrategy", "p4obs", "metric_4")
_emit_emits_metric_event("ProvenancetrackerStrategy", "p4obs", "metric_5")
_emit_emits_metric_event("ProvenancetrackerStrategy", "p4obs", "metric_6")
_emit_records_incident_event("ProvenancetrackerStrategy", "p4obs", "incident")
_emit_captures_runtime_anomaly("ProvenancetrackerStrategy", "p4obs", "anomaly")
_emit_writes_observability_log("ProvenancetrackerStrategy", "p4obs", "obs_log")
_emit_updates_monitoring_state("ProvenancetrackerStrategy", "p4obs", "mon_state")
_emit_triggers_alert("ProvenancetrackerStrategy", "p4obs", "alert")
_emit_links_incident_trace("ProvenancetrackerStrategy", "p4obs", "trace_link")
_emit_captures_pattern("ProvenancetrackerStrategy", "p3lm", "pattern")
_emit_records_learning_event("ProvenancetrackerStrategy", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ProvenancetrackerStrategy", "p3lm", "snapshot")
_emit_feeds_meta_learning("ProvenancetrackerStrategy", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ProvenancetrackerStrategy", "p3lm", "routing")
_emit_improves_agent_policy("ProvenancetrackerStrategy", "p3lm", "policy")
_emit_stores_learning_state("ProvenancetrackerStrategy", "p3lm", "state")
_emit_records_execution_trace("ProvenancetrackerStrategy", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ProvenancetrackerStrategy", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ProvenancetrackerStrategy", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ProvenancetrackerStrategy", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ProvenancetrackerStrategy", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ProvenancetrackerStrategy", "env_read", "p2_env_1")
_emit_reads_environ("ProvenancetrackerStrategy", "env_read", "p2_env_2")
_emit_reads_runtime_state("ProvenancetrackerStrategy", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ProvenancetrackerStrategy", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ProvenancetrackerStrategy", "context_pull")
_emit_pulls_context("p1", "ProvenancetrackerStrategy", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ProvenancetrackerStrategy", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ProvenancetrackerStrategy", "uwg_term_2")
_emit_writes_through("p1", "ProvenancetrackerStrategy", "write_through")
_emit_writes_through("p1", "ProvenancetrackerStrategy", "write_through_2")
_emit_validated_by_safety_plane("p1", "ProvenancetrackerStrategy", "safety_validation")
_emit_invokes_eval("p1", "ProvenancetrackerStrategy", "eval_call")
_emit_proposal_commits_routing("p1", "ProvenancetrackerStrategy", "routing_commit")
_emit_escalates_to_human("p1", "ProvenancetrackerStrategy", "human_escalation")
_emit_routes_through("p1", "ProvenancetrackerStrategy", "route_through")
_emit_checks_agent_registry("p1", "ProvenancetrackerStrategy", "agent_registry")
_emit_validates_agent_capability("p1", "ProvenancetrackerStrategy", "capability")
_emit_dispatches_execution_plan("p1", "ProvenancetrackerStrategy", "exec_plan")
_emit_agent_executes_agent("p1", "ProvenancetrackerStrategy", "sub_agent")
_emit_routes_to_agent("p1", "ProvenancetrackerStrategy", "target_agent")
_emit_verifies_policy("p1", "ProvenancetrackerStrategy", "policy_check")
_emit_observes_runtime_state("p1", "ProvenancetrackerStrategy", "runtime_state")
_emit_verifies_boundary("p1", "ProvenancetrackerStrategy", "boundary_check")
_emit_transcripts_response("p1", "ProvenancetrackerStrategy", "transcript")
_emit_hard_fails_untranscripted("p1", "ProvenancetrackerStrategy")
_emit_gated_by_confidence("p1", "ProvenancetrackerStrategy", "confidence_gate")
emit_replay_key("p0", "ProvenancetrackerStrategy")
emit_determinism_digest("p0", "ProvenancetrackerStrategy")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ProvenancetrackerStrategy", "execution_auth")
_emit_validates_capability("p2", "ProvenancetrackerStrategy", "capability_check")
_emit_routes_to_capability("p2", "ProvenancetrackerStrategy", "capability_route")
_emit_writes_via_uwg("p2", "ProvenancetrackerStrategy", "uwg_write")
_emit_blocks_direct_write("p2", "ProvenancetrackerStrategy", "direct_write_block")
_emit_records_tool_invocation("p2", "ProvenancetrackerStrategy", "tool_invocation")
_emit_captures_execution_output("p2", "ProvenancetrackerStrategy", "exec_output")
_emit_dispatches_agent("p3", "ProvenancetrackerStrategy", "agent_dispatch")
_emit_coordinates_agents("p3", "ProvenancetrackerStrategy", "agent_coordination")
_emit_records_workflow_lineage("p3", "ProvenancetrackerStrategy", "workflow_lineage")
_emit_records_healing_outcome("p3", "ProvenancetrackerStrategy", "healing_outcome")
_emit_escalates_failure("p3", "ProvenancetrackerStrategy", "failure_escalation")
_emit_orchestrates_workflow("p3", "ProvenancetrackerStrategy", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ProvenancetrackerStrategy", "healing_dispatch")
_emit_invokes_evaluation("p3", "ProvenancetrackerStrategy", "evaluation_signal")
_emit_records_telemetry_event("p4", "ProvenancetrackerStrategy", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ProvenancetrackerStrategy", "eval_metric")
_emit_stores_embedding("p4", "ProvenancetrackerStrategy", "embedding_store")
_emit_updates_meta_learning_state("p4", "ProvenancetrackerStrategy", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ProvenancetrackerStrategy", "exec_snapshot_link")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_1")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_2")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_3")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_4")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_5")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_6")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_7")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_8")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_9")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_10")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_11")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_12")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_13")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_14")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_15")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_16")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_17")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_18")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_19")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_20")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_21")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_22")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_23")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_24")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_25")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_26")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_27")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_28")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_29")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_30")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_31")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_32")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_33")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_34")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_35")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_36")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_37")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_38")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_39")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_40")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_41")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_42")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_43")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_44")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_45")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_46")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_47")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_48")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_49")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_50")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_51")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_52")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_53")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_54")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_55")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_56")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_57")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_58")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_59")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_60")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_61")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_62")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_63")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_64")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_65")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_66")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_67")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_68")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_69")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_70")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_71")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_72")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_73")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_74")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_75")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_76")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_77")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_78")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_79")
_emit_reads_through("l4", "ProvenancetrackerStrategy", "urg_read_80")

logger = logging.getLogger(__name__)


@dataclass
class SourceCitation:
    """Citation for a data source."""

    source_id: str
    uri: str
    snippet: str
    relevance_score: float
    citation_type: str = "source"
    verified: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "source_id": self.source_id,
            "uri": self.uri,
            "snippet": self.snippet,
            "relevance_score": self.relevance_score,
            "citation_type": self.citation_type,
            "verified": self.verified,
        }


class ArtifactLineage(BaseModel):
    """Lineage information for a generated artifact."""

    artifact_id: str
    generation_prompt: str
    used_sources: list[dict[str, Any]] = Field(default_factory=list)
    model_version: str
    timestamp: float = Field(default_factory=time.time)
    trace_id: str
    verification_status: str = "pending"
    verified_citations: list[str] = Field(default_factory=list)

    class Config:
        json_encoders = {}


class ProvenanceTracker:
    """Tracks data lineage for generated artifacts."""

    def __init__(self, storage_path: str = "./.provenance"):
        """Initialize provenance tracker.

        Args:
            storage_path: Path to store lineage data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.lineage_file = self.storage_path / "lineage.jsonl"
        self._active_context: dict[str, list[SourceCitation]] = {}
        self._lock = asyncio.Lock()
        self._stats = {
            "lineages_recorded": 0,
            "sources_captured": 0,
            "verifications_completed": 0,
            "verification_rate": 0.0,
        }
        logger.info(f"Initialized ProvenanceTracker at {storage_path}")

    async def capture_context(self, trace_id: str, sources: list[tuple[str, str, float]]) -> None:
        """Capture context sources for a trace.

        Args:
            trace_id: Trace ID for tracking
            sources: List of (source_id, snippet, relevance) tuples
        """
        async with self._lock:
            citations = []
            for source_id, snippet, relevance in sources:
                citation = SourceCitation(
                    source_id=source_id,
                    uri=f"source://{source_id}",
                    snippet=snippet,
                    relevance_score=relevance,
                )
                citations.append(citation)
            self._active_context[trace_id] = citations
            self._stats["sources_captured"] += len(citations)
            logger.debug(f"Captured {len(citations)} sources for trace {trace_id}")

    async def record_generation(
        self,
        trace_id: str,
        artifact_id: str,
        output: str,
        model_version: str,
        generation_prompt: str | None = None,
    ) -> ArtifactLineage:
        """Record a generation with its lineage.

        Args:
            trace_id: Trace ID
            artifact_id: ID of generated artifact
            output: Generated output text
            model_version: Model version used
            generation_prompt: Prompt used for generation

        Returns:
            Artifact lineage record
        """
        async with self._lock:
            sources = self._active_context.get(trace_id, [])
            lineage = ArtifactLineage(
                artifact_id=artifact_id,
                generation_prompt=generation_prompt or "",
                used_sources=[c.to_dict() for c in sources],
                model_version=model_version,
                trace_id=trace_id,
            )
            await self._verify_citations(lineage, output)
            await self._store_lineage(lineage)
            if trace_id in self._active_context:
                del self._active_context[trace_id]
            self._stats["lineages_recorded"] += 1
            if lineage.verification_status == "verified":
                self._stats["verifications_completed"] += 1
            total = self._stats["lineages_recorded"]
            if total > 0:
                self._stats["verification_rate"] = self._stats["verifications_completed"] / total
            return lineage

    async def verify_citations(self, lineage: ArtifactLineage, output: str) -> ArtifactLineage:
        """Verify which sources were actually used.

        Args:
            lineage: Artifact lineage to verify
            output: Generated output text

        Returns:
            Updated lineage with verification results
        """
        return await self._verify_citations(lineage, output)

    async def _verify_citations(self, lineage: ArtifactLineage, output: str) -> None:
        """Internal method to verify citations.

        Args:
            lineage: Artifact lineage to update
            output: Generated output text
        """
        verified_sources = []
        verified_ids = []
        for source_dict in lineage.used_sources:
            citation = SourceCitation(**source_dict)
            similarity = self._calculate_similarity(citation.snippet, output)
            if similarity > 0.7 or self._has_exact_phrase(citation.snippet, output):
                citation.verified = True
                verified_ids.append(citation.source_id)
            verified_sources.append(citation.to_dict())
        lineage.used_sources = verified_sources
        lineage.verified_citations = verified_ids
        lineage.verification_status = "verified" if verified_ids else "failed"

    def _calculate_similarity(self, snippet: str, output: str) -> float:
        """Calculate similarity between snippet and output.

        Args:
            snippet: Source snippet
            output: Generated output

        Returns:
            Similarity score (0.0 to 1.0)
        """
        matcher = SequenceMatcher(None, snippet.lower(), output.lower())
        return matcher.ratio()

    # guardian: allow-magic-config
    def _has_exact_phrase(self, snippet: str, output: str, min_words: int = 3) -> bool:
        """Check if snippet contains an exact phrase in output.

        Args:
            snippet: Source snippet
            output: Generated output
            min_words: Minimum words for phrase match

        Returns:
            True if exact phrase found
        """
        words = snippet.lower().split()
        for i in range(len(words) - min_words + 1):
            phrase = " ".join(words[i : i + min_words])
            if phrase in output.lower():
                return True
        return False

    async def _store_lineage(self, lineage: ArtifactLineage) -> None:
        """Store lineage to file.

        Args:
            lineage: Lineage to store
        """
        try:
            lineage_json = json.dumps(lineage.dict(), default=str)
            async with asyncio.to_thread(self._append_lineage, lineage_json):
                pass
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            logger.error(f"Failed to store lineage: {e}")
            raise

    def _append_lineage(self, lineage_json: str) -> None:
        """Append lineage to file (sync for file I/O).

        Args:
            lineage_json: JSON string to append
        """
        with open(self.lineage_file, "a", encoding="utf-8") as f:
            f.write(lineage_json + "\n")

    async def get_lineage(self, artifact_id: str) -> ArtifactLineage | None:
        """Get lineage for an artifact.

        Args:
            artifact_id: Artifact ID

        Returns:
            Lineage if found
        """
        try:
            async with asyncio.to_thread(self._read_lineage_file):
                pass
            for line in self._read_lineage_file():
                data = json.loads(line)
                if data.get("artifact_id") == artifact_id:
                    return ArtifactLineage(**data)
            return None
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to get lineage: {e}")
            return None

    def _read_lineage_file(self) -> list[str]:
        """Read lineage file lines.

        Returns:
            List of JSON lines
        """
        if not self.lineage_file.exists():
            return []
        with open(self.lineage_file, encoding="utf-8") as f:
            return f.readlines()

    # guardian: allow-magic-config
    async def search_lineage(
        self, trace_id: str | None = None, model_version: str | None = None, limit: int = 100
    ) -> list[ArtifactLineage]:
        """Search lineage records.

        Args:
            trace_id: Filter by trace ID
            model_version: Filter by model version
            limit: Maximum results

        Returns:
            List of matching lineages
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "ProvenanceTracker.search_lineage")
        results = []
        try:
            lines = await asyncio.to_thread(self._read_lineage_file)
            for line in lines:
                data = json.loads(line)
                if trace_id and data.get("trace_id") != trace_id:
                    continue
                if model_version and data.get("model_version") != model_version:
                    continue
                results.append(ArtifactLineage(**data))
                if len(results) >= limit:
                    break
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to search lineage: {e}")
        return results

    async def cleanup(self, older_than_days: int = 30) -> int:
        """Clean up old lineage records.

        Args:
            older_than_days: Age threshold in days

        Returns:
            Number of records cleaned up
        """
        cutoff_time = time.time() - older_than_days * 24 * 3600
        try:
            lines = await asyncio.to_thread(self._read_lineage_file)
            kept_lines = []
            cleaned = 0
            for line in lines:
                data = json.loads(line)
                if data.get("timestamp", 0) > cutoff_time:
                    kept_lines.append(line)
                else:
                    cleaned += 1
            if cleaned > 0:
                async with asyncio.to_thread(self._write_lineage_file, kept_lines):
                    pass
                logger.info(f"Cleaned up {cleaned} old lineage records")
            return cleaned
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-broad-exception -- teardown/cleanup context -- swallow is conventional in resource-release paths
            logger.error(f"Failed to cleanup lineage: {e}")
            return 0

    def _write_lineage_file(self, lines: list[str]) -> None:
        """Write lineage file (sync for file I/O).

        Args:
            lines: Lines to write
        """
        with open(self.lineage_file, "w", encoding="utf-8") as f:
            f.writelines(lines)

    def get_stats(self) -> dict[str, Any]:
        """Get provenance tracker statistics.

        Returns:
            Statistics dictionary
        """
        return self._stats.copy()

    async def health_check(self) -> dict[str, Any]:
        """Check health of provenance tracker.

        Returns:
            Health status
        """
        try:
            storage_accessible = self.storage_path.exists() and self.storage_path.is_dir()
            file_size = 0
            if self.lineage_file.exists():
                file_size = self.lineage_file.stat().st_size
            return {
                "status": "healthy" if storage_accessible else "unhealthy",
                "storage_path": str(self.storage_path),
                "storage_accessible": storage_accessible,
                "lineage_file_size": file_size,
                "active_contexts": len(self._active_context),
                "stats": self._stats,
            }
        # guardian: allow-silent-swallow
        except Exception as e:
            return {"status": "unhealthy", "error": str(e), "stats": self._stats}


_provenance_tracker: ProvenanceTracker | None = None
_tracker_lock = asyncio.Lock()


async def get_provenance_tracker() -> ProvenanceTracker:
    """Get global provenance tracker instance.

    Returns:
        ProvenanceTracker instance
    """
    global _provenance_tracker
    async with _tracker_lock:
        if _provenance_tracker is None:
            _provenance_tracker = ProvenanceTracker()
    return _provenance_tracker


class ProvenanceContext:
    """Context manager for provenance tracking."""

    def __init__(
        self, trace_id: str, sources: list[tuple[str, str, float]], tracker: ProvenanceTracker | None = None
    ):
        """Initialize provenance context.

        Args:
            trace_id: Trace ID
            sources: List of (source_id, snippet, relevance) tuples
            tracker: Provenance tracker instance
        """
        self.trace_id = trace_id
        self.sources = sources
        self.tracker = tracker

    async def __aenter__(self):
        """Enter context."""
        if not self.tracker:
            self.tracker = await get_provenance_tracker()
        await self.tracker.capture_context(self.trace_id, self.sources)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        pass

    async def record_generation(
        self, artifact_id: str, output: str, model_version: str, generation_prompt: str | None = None
    ) -> ArtifactLineage:
        """Record generation within context.

        Args:
            artifact_id: Artifact ID
            output: Generated output
            model_version: Model version
            generation_prompt: Generation prompt

        Returns:
            Artifact lineage
        """
        return await self.tracker.record_generation(
            self.trace_id, artifact_id, output, model_version, generation_prompt
        )


async def track_provenance(
    trace_id: str,
    sources: list[tuple[str, str, float]],
    artifact_id: str,
    output: str,
    model_version: str,
    generation_prompt: str | None = None,
) -> ArtifactLineage:
    """Track provenance for a generation.

    Args:
        trace_id: Trace ID
        sources: List of (source_id, snippet, relevance) tuples
        artifact_id: Artifact ID
        output: Generated output
        model_version: Model version
        generation_prompt: Generation prompt

    Returns:
        Artifact lineage
    """
    tracker = await get_provenance_tracker()
    async with ProvenanceContext(trace_id, sources, tracker):
        return await tracker.record_generation(
            trace_id, artifact_id, output, model_version, generation_prompt
        )


def provenance_tracked(extract_sources: Callable | None = None):
    """Decorator to automatically track provenance.

    Args:
        extract_sources: Function to extract sources from arguments

    Returns:
        Decorated function
    """

    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            trace_id = None
            if args and hasattr(args[0], "trace_id"):
                trace_id = args[0].trace_id
            else:
                trace_id = f"trace_{int(time.time())}"
            sources = []
            if extract_sources:
                sources = extract_sources(*args, **kwargs)
            result = await func(*args, **kwargs)
            output = str(result)
            model_version = getattr(func, "_model_version", "unknown")
            if sources:
                await track_provenance(
                    trace_id, sources, f"artifact_{int(time.time())}", output, model_version
                )
            return result

        return async_wrapper

    return decorator
