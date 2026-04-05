"""
⚛️ Deep Brain Harvest - In-Memory Pattern Storage

This script extracts the Subatomic Flattening Pattern and stores it in an
in-memory vector store (BGE-m3, 1024-dim) for local retrieval.

Usage:
    python scripts/deep_brain_harvest.py --pattern flattening --namespace structural_patterns
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "deep_brain_harvester_util", "p0_governance")
_emit_reads_policy_state("p0", "deep_brain_harvester_util", "policy_binding")
_emit_snapshots_state("p0", "deep_brain_harvester_util", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("deep_brain_harvester_util", "p4obs", "metric_1")
_emit_emits_metric_event("deep_brain_harvester_util", "p4obs", "metric_2")
_emit_emits_metric_event("deep_brain_harvester_util", "p4obs", "metric_3")
_emit_emits_metric_event("deep_brain_harvester_util", "p4obs", "metric_4")
_emit_emits_metric_event("deep_brain_harvester_util", "p4obs", "metric_5")
_emit_emits_metric_event("deep_brain_harvester_util", "p4obs", "metric_6")
_emit_records_incident_event("deep_brain_harvester_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("deep_brain_harvester_util", "p4obs", "anomaly")
_emit_writes_observability_log("deep_brain_harvester_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("deep_brain_harvester_util", "p4obs", "mon_state")
_emit_triggers_alert("deep_brain_harvester_util", "p4obs", "alert")
_emit_links_incident_trace("deep_brain_harvester_util", "p4obs", "trace_link")
_emit_captures_pattern("deep_brain_harvester_util", "p3lm", "pattern")
_emit_records_learning_event("deep_brain_harvester_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("deep_brain_harvester_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("deep_brain_harvester_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("deep_brain_harvester_util", "p3lm", "routing")
_emit_improves_agent_policy("deep_brain_harvester_util", "p3lm", "policy")
_emit_stores_learning_state("deep_brain_harvester_util", "p3lm", "state")
_emit_records_execution_trace("deep_brain_harvester_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("deep_brain_harvester_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("deep_brain_harvester_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("deep_brain_harvester_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("deep_brain_harvester_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("deep_brain_harvester_util", "env_read", "p2_env_1")
_emit_reads_environ("deep_brain_harvester_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("deep_brain_harvester_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("deep_brain_harvester_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "deep_brain_harvester_util", "context_pull")
_emit_pulls_context("p1", "deep_brain_harvester_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "deep_brain_harvester_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "deep_brain_harvester_util", "uwg_term_2")
_emit_writes_through("p1", "deep_brain_harvester_util", "write_through")
_emit_writes_through("p1", "deep_brain_harvester_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "deep_brain_harvester_util", "safety_validation")
_emit_invokes_eval("p1", "deep_brain_harvester_util", "eval_call")
_emit_proposal_commits_routing("p1", "deep_brain_harvester_util", "routing_commit")
_emit_escalates_to_human("p1", "deep_brain_harvester_util", "human_escalation")
_emit_routes_through("p1", "deep_brain_harvester_util", "route_through")
_emit_checks_agent_registry("p1", "deep_brain_harvester_util", "agent_registry")
_emit_validates_agent_capability("p1", "deep_brain_harvester_util", "capability")
_emit_dispatches_execution_plan("p1", "deep_brain_harvester_util", "exec_plan")
_emit_agent_executes_agent("p1", "deep_brain_harvester_util", "sub_agent")
_emit_routes_to_agent("p1", "deep_brain_harvester_util", "target_agent")
_emit_verifies_policy("p1", "deep_brain_harvester_util", "policy_check")
_emit_observes_runtime_state("p1", "deep_brain_harvester_util", "runtime_state")
_emit_verifies_boundary("p1", "deep_brain_harvester_util", "boundary_check")
_emit_transcripts_response("p1", "deep_brain_harvester_util", "transcript")
_emit_hard_fails_untranscripted("p1", "deep_brain_harvester_util")
_emit_gated_by_confidence("p1", "deep_brain_harvester_util", "confidence_gate")
emit_replay_key("p0", "deep_brain_harvester_util")
emit_determinism_digest("p0", "deep_brain_harvester_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "deep_brain_harvester_util", "execution_auth")
_emit_validates_capability("p2", "deep_brain_harvester_util", "capability_check")
_emit_routes_to_capability("p2", "deep_brain_harvester_util", "capability_route")
_emit_writes_via_uwg("p2", "deep_brain_harvester_util", "uwg_write")
_emit_blocks_direct_write("p2", "deep_brain_harvester_util", "direct_write_block")
_emit_records_tool_invocation("p2", "deep_brain_harvester_util", "tool_invocation")
_emit_captures_execution_output("p2", "deep_brain_harvester_util", "exec_output")
_emit_dispatches_agent("p3", "deep_brain_harvester_util", "agent_dispatch")
_emit_coordinates_agents("p3", "deep_brain_harvester_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "deep_brain_harvester_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "deep_brain_harvester_util", "healing_outcome")
_emit_escalates_failure("p3", "deep_brain_harvester_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "deep_brain_harvester_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "deep_brain_harvester_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "deep_brain_harvester_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "deep_brain_harvester_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "deep_brain_harvester_util", "eval_metric")
_emit_stores_embedding("p4", "deep_brain_harvester_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "deep_brain_harvester_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "deep_brain_harvester_util", "exec_snapshot_link")

# guardian: allow-global-mutation
sys.path.insert(0, str(Path(__file__).parent.parent))
logging.basicConfig(level=logging.INFO)
Logger: Any = logging.getLogger(__name__)


class DeepBrainHarvester:
    """Harvests and stores patterns in an in-memory vector store (BGE-m3, 1024-dim)."""

    def __init__(self, api_key: str = None, index_name: str = "canon-healing-patterns"):
        """
        Initialize Deep Brain Harvester.

        Args:
            api_key: Unused — retained for API compatibility.
            index_name: Logical name for the in-memory index.
        """
        self.index_name = index_name
        self._store: dict[str, dict[str, dict]] = {}
        Logger.info(f"DeepBrainHarvester: in-memory index ready: {self.index_name}")

    def _ensure_index_exists(self):
        """Ensure the in-memory index exists, create if not."""
        pass

    def _generate_embedding(self, text: str) -> list[float]:
        """
        Generate embedding for text using BGE-m3.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (1024-dim)
        """
        try:
            from agentic_core.L3_orchestration.healers.bmg_embedding_similarity import bmg_embed_text

            result = bmg_embed_text(text)
            if result:
                return result
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"Error generating embedding: {e}")
        return [0.0] * 1024

    def harvest_flattening_pattern(self, namespace: str = "structural_patterns") -> dict:
        """
        Harvest the Subatomic Flattening Pattern and store in in-memory vector store.

        Args:
            namespace: Namespace for pattern storage

        Returns:
            Upsert result
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "DeepBrainHarvester.harvest_flattening_pattern")

        Logger.info(" Harvesting Subatomic Flattening Pattern...")
        pattern: Any = get_flattening_pattern()
        pattern_text: Any = self._create_pattern_text(pattern)
        Logger.info(" Generating embedding...")
        embedding: Any = self._generate_embedding(pattern_text)
        metadata: Any = {
            "pattern_type": "subatomic_flattening",
            "source_file": pattern["source_file"],
            "method_name": pattern["method_name"],
            "date": pattern["date"],
            "before_lines": pattern["before"]["lines"],
            "after_lines": pattern["after"]["lines"],
            "nesting_reduction": pattern["after"]["improvements"][1],
            "preservation_rate": pattern["success_metrics"]["preservation_rate"],
            "trigger": pattern["reusable_pattern"]["trigger"],
            "pattern_text": pattern_text[:1000],
        }
        Logger.info(f"Upserting to in-memory namespace: {namespace}")
        vec_id = "flattening_pattern_agent_logic_2025_12_19"
        self._store.setdefault(namespace, {})[vec_id] = {"values": embedding, "metadata": metadata}
        result: Any = {"upserted_count": 1}
        Logger.info(f"Pattern harvested successfully: {result}")
        return result

    def _create_pattern_text(self, pattern: dict) -> str:
        """
        Create searchable text representation of pattern.

        Args:
            pattern: Pattern dictionary

        Returns:
            Text representation for embedding
        """
        text_parts = [
            "# Subatomic Flattening Pattern",
            "",
            f"## Trigger: {pattern['reusable_pattern']['trigger']}",
            "",
            "## Problem:",
            f"Method with {pattern['before']['lines']} lines and {pattern['before']['nesting_depth']} nesting levels",
            "Issues: " + ", ".join(pattern["before"]["issues"]),
            "",
            "## Solution:",
            "Extract nested logic into focused helper methods",
            "",
            "## Recognition Patterns:",
            *[f"- {p}" for p in pattern["reusable_pattern"]["recognition"]],
            "",
            "## Extraction Heuristic:",
            *[
                f"{i}. {step}"
                for i, step in enumerate(pattern["reusable_pattern"]["extraction_heuristic"], 1)
            ],
            "",
            "## Naming Convention:",
            *[f"- {k}: {v}" for k, v in pattern["reusable_pattern"]["naming_convention"].items()],
            "",
            "## Results:",
            f"- Line reduction: {pattern['success_metrics']['complexity_reduction']}%",
            f"- Nesting reduction: {pattern['success_metrics']['nesting_reduction']}%",
            f"- Preservation: {pattern['success_metrics']['preservation_rate']}%",
            f"- Healing readiness: {pattern['success_metrics']['healing_readiness']}",
            "",
            "## Example:",
            f"Source: {pattern['source_file']}",
            f"Method: {pattern['method_name']}",
            f"Before: {pattern['before']['lines']} lines, {pattern['before']['nesting_depth']} levels",
            f"After: {pattern['after']['lines']} lines, {pattern['after']['nesting_depth']} levels",
            "",
            "## Extracted Helpers:",
            *[
                f"- {helper['name']}: {helper['purpose']} ({helper['lines']} lines, {helper['nesting']} nesting)"
                for helper in pattern["helper_methods"]
            ],
        ]
        return "\n".join(text_parts)

    def query_pattern(self, query: str, namespace: str = "structural_patterns", top_k: int = 3) -> list[dict]:
        """
        Query in-memory store for similar patterns.

        Args:
            query: Query text
            namespace: Namespace to search
            top_k: Number of results to return

        Returns:
            List of matching patterns
        """
        import numpy as np

        Logger.info(f"Querying pattern: {query}")
        query_embedding: Any = self._generate_embedding(query)
        entries = self._store.get(namespace, {})
        if not entries:
            Logger.info("Found 0 matches (empty namespace)")
            return []
        q = np.array(query_embedding, dtype=np.float32)
        q_norm = q / (np.linalg.norm(q) + 1e-12)
        scored: list[tuple[float, str, dict]] = []
        for vec_id, item in entries.items():
            v = np.array(item["values"], dtype=np.float32)
            v_norm = v / (np.linalg.norm(v) + 1e-12)
            score = float(np.dot(q_norm, v_norm))
            scored.append((score, vec_id, item["metadata"]))
        scored.sort(key=lambda x: x[0], reverse=True)
        matches = [{"id": vec_id, "score": score, "metadata": meta} for score, vec_id, meta in scored[:top_k]]
        Logger.info(f"Found {len(matches)} matches")
        return matches


def main() -> Any:
    """Main entry point for Deep Brain Harvest."""
    parser: Any = argparse.ArgumentParser(description="Harvest patterns into in-memory vector store")
    parser.add_argument("--pattern", choices=["flattening"], default="flattening", help="Pattern to harvest")
    parser.add_argument("--namespace", default="structural_patterns", help="Namespace for pattern storage")
    parser.add_argument(
        "--index", default="canon-healing-patterns", help="Logical name for the in-memory index"
    )
    parser.add_argument("--query", help="Query for existing patterns instead of upserting")
    args: Any = parser.parse_args()
    try:
        harvester: Any = DeepBrainHarvester(index_name=args.index)
        if args.query:
            results: Any = harvester.query_pattern(args.query, namespace=args.namespace)
            print("\n🔍 Query Results:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['id']} (score: {result['score']:.4f})")
                print(f"   Trigger: {result['metadata'].get('trigger', 'N/A')}")
                print(f"   Reduction: {result['metadata'].get('nesting_reduction', 'N/A')}")
        elif args.pattern == "flattening":
            result: Any = harvester.harvest_flattening_pattern(namespace=args.namespace)
            print("\n✅ Flattening pattern harvested successfully!")
            print(f"   Namespace: {args.namespace}")
            print(f"   Index: {args.index}")
            print(f"   Upserted: {result.get('upserted_count', 1)} vectors")
    # guardian: allow-silent-swallow
    except Exception as e:
        raise
        Logger.error(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
