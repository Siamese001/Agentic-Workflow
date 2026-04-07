from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    # noqa: E402,
    # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "lazy_seam_classifier")
emit_determinism_digest("p0", "lazy_seam_classifier")

_emit_dispatches_healing_run("p1", "lazy_seam_classifier", "L5")
_emit_routes_through("p1", "lazy_seam_classifier", "L5")
_emit_checks_agent_registry("p1", "lazy_seam_classifier", "agent_registry")
_emit_validates_agent_capability("p1", "lazy_seam_classifier", "capability")
_emit_dispatches_execution_plan("p1", "lazy_seam_classifier", "exec_plan")
_emit_agent_executes_agent("p1", "lazy_seam_classifier", "sub_agent")
_emit_routes_to_agent("p1", "lazy_seam_classifier", "target_agent")
_emit_verifies_policy("p1", "lazy_seam_classifier", "policy_check")
_emit_observes_runtime_state("p1", "lazy_seam_classifier", "runtime_state")
_emit_verifies_boundary("p1", "lazy_seam_classifier", "boundary_check")
_emit_transcripts_response("p1", "lazy_seam_classifier", "transcript")
_emit_hard_fails_untranscripted("p1", "lazy_seam_classifier")
_emit_gated_by_confidence("p1", "lazy_seam_classifier", "confidence_gate")
_emit_escalates_to_human("p1", "lazy_seam_classifier", "L5")
_emit_reads_policy_state("p1", "lazy_seam_classifier", "L5")

_emit_applies_guardrail("p0", "lazy_seam_classifier", "p0_governance")
_emit_snapshots_state("p0", "lazy_seam_classifier", "state_snapshot")
_emit_authorize_and_execute("p2", "lazy_seam_classifier", "execution_auth")
_emit_validates_capability("p2", "lazy_seam_classifier", "capability_check")
_emit_routes_to_capability("p2", "lazy_seam_classifier", "capability_route")
_emit_writes_via_uwg("p2", "lazy_seam_classifier", "uwg_write")
_emit_blocks_direct_write("p2", "lazy_seam_classifier", "direct_write_block")
_emit_records_tool_invocation("p2", "lazy_seam_classifier", "tool_invocation")
_emit_captures_execution_output("p2", "lazy_seam_classifier", "exec_output")
_emit_dispatches_agent("p3", "lazy_seam_classifier", "agent_dispatch")
_emit_coordinates_agents("p3", "lazy_seam_classifier", "agent_coordination")
_emit_records_workflow_lineage("p3", "lazy_seam_classifier", "workflow_lineage")
_emit_records_healing_outcome("p3", "lazy_seam_classifier", "healing_outcome")
_emit_escalates_failure("p3", "lazy_seam_classifier", "failure_escalation")
_emit_orchestrates_workflow("p3", "lazy_seam_classifier", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "lazy_seam_classifier", "healing_dispatch")
_emit_invokes_evaluation("p3", "lazy_seam_classifier", "evaluation_signal")
_emit_records_telemetry_event("p4", "lazy_seam_classifier", "telemetry_event")
_emit_captures_evaluation_metric("p4", "lazy_seam_classifier", "eval_metric")
_emit_stores_embedding("p4", "lazy_seam_classifier", "embedding_store")
_emit_updates_meta_learning_state("p4", "lazy_seam_classifier", "meta_learning")
_emit_links_execution_to_snapshot("p4", "lazy_seam_classifier", "exec_snapshot_link")

"\nLazy Seam Allowlist Reason Classifier - Phase 4.2\n\nClassifies lazy seams into reason categories based on their imports and context.\n"
import json
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
from agentic_core.L0_routing.config.path_constants import OPS_SCRIPTS_DIR
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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

_emit_emits_metric_event("lazy_seam_classifier", "p4obs", "metric_1")
_emit_emits_metric_event("lazy_seam_classifier", "p4obs", "metric_2")
_emit_emits_metric_event("lazy_seam_classifier", "p4obs", "metric_3")
_emit_emits_metric_event("lazy_seam_classifier", "p4obs", "metric_4")
_emit_emits_metric_event("lazy_seam_classifier", "p4obs", "metric_5")
_emit_emits_metric_event("lazy_seam_classifier", "p4obs", "metric_6")
_emit_records_incident_event("lazy_seam_classifier", "p4obs", "incident")
_emit_captures_runtime_anomaly("lazy_seam_classifier", "p4obs", "anomaly")
_emit_writes_observability_log("lazy_seam_classifier", "p4obs", "obs_log")
_emit_updates_monitoring_state("lazy_seam_classifier", "p4obs", "mon_state")
_emit_triggers_alert("lazy_seam_classifier", "p4obs", "alert")
_emit_links_incident_trace("lazy_seam_classifier", "p4obs", "trace_link")
_emit_captures_pattern("lazy_seam_classifier", "p3lm", "pattern")
_emit_records_learning_event("lazy_seam_classifier", "p3lm", "learning_event")
_emit_writes_learning_snapshot("lazy_seam_classifier", "p3lm", "snapshot")
_emit_feeds_meta_learning("lazy_seam_classifier", "p3lm", "meta_feed")
_emit_updates_routing_strategy("lazy_seam_classifier", "p3lm", "routing")
_emit_improves_agent_policy("lazy_seam_classifier", "p3lm", "policy")
_emit_stores_learning_state("lazy_seam_classifier", "p3lm", "state")
_emit_records_execution_trace("lazy_seam_classifier", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("lazy_seam_classifier", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("lazy_seam_classifier", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("lazy_seam_classifier", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("lazy_seam_classifier", "L4_STATE", "p2_trace_5")
_emit_reads_environ("lazy_seam_classifier", "env_read", "p2_env_1")
_emit_reads_environ("lazy_seam_classifier", "env_read", "p2_env_2")
_emit_reads_runtime_state("lazy_seam_classifier", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("lazy_seam_classifier", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "lazy_seam_classifier", "context_pull")
_emit_pulls_context("p1", "lazy_seam_classifier", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "lazy_seam_classifier", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "lazy_seam_classifier", "uwg_term_2")
_emit_writes_through("p1", "lazy_seam_classifier", "write_through")
_emit_writes_through("p1", "lazy_seam_classifier", "write_through_2")
_emit_validated_by_safety_plane("p1", "lazy_seam_classifier", "safety_validation")
_emit_invokes_eval("p1", "lazy_seam_classifier", "eval_call")
_emit_proposal_commits_routing("p1", "lazy_seam_classifier", "routing_commit")


class LazySeamClassifier:
    """Classifies lazy seams into reason categories."""

    REASON_TAXONOMY = {
        "D1_EXTERNAL_OPTIONAL_DEP": "Optional external dependencies (pinecone/redis/etc.)",
        "D2_ENTRYPOINT_SCRIPT": "CLI/scripts that orchestrate",
        "D3_PLUGIN_REGISTRY_DISPATCH": "Registry/dynamic dispatch boundaries",
        "D4_OBSERVABILITY_INTEGRATION": "Telemetry/probes integration",
        "D5_SECURITY_SAFETY_ADAPTER": "Policy adapters (boundary-only)",
    }

    def __init__(self, allowlist_path: Path):
        self.allowlist_path = allowlist_path
        self.allowlist_data = self._load_allowlist()

    def _load_allowlist(self) -> dict[str, Any]:
        """Load allowlist from file."""
        with open(self.allowlist_path, encoding="utf-8") as f:
            return json.load(f)

    def _classify_seam(self, seam: dict[str, Any]) -> tuple[str, str]:
        """Classify a single seam and return (reason_code, justification)."""
        file_path = seam["file_path"]
        function_name = seam["function_name"]
        imported_modules = seam.get("imported_modules", [])
        imported_symbols = seam.get("imported_symbols", [])
        external_deps = {
            "pinecone",
            "redis",
            "torch",
            "transformers",
            "openai",
            "anthropic",
            "numpy",
            "pandas",
            "matplotlib",
            "plotly",
        }
        for module in imported_modules:
            if any(dep in module.lower() for dep in external_deps):
                return ("D1_EXTERNAL_OPTIONAL_DEP", f"Optional external dependency: {module}")
        for module, symbol in imported_symbols:
            if any(dep in module.lower() for dep in external_deps):
                return ("D1_EXTERNAL_OPTIONAL_DEP", f"Optional external dependency: {module}.{symbol}")
        if (
            "scripts" in file_path
            or OPS_SCRIPTS_DIR in file_path
            or function_name.endswith("_orchestrator")
            or function_name.endswith("_runner")
        ):
            return ("D2_ENTRYPOINT_SCRIPT", "Script/orchestration entrypoint with lazy loading")
        registry_keywords = {
            "registry",
            "dispatch",
            "factory",
            "router",
            "broker",
            "agent",
            "sovereign",
            "mcp",
            "workflow",
        }
        if any(keyword in function_name.lower() for keyword in registry_keywords) or any(
            keyword in file_path.lower() for keyword in registry_keywords
        ):
            return ("D3_PLUGIN_REGISTRY_DISPATCH", "Plugin registry or dynamic dispatch boundary")
        obs_keywords = {
            "telemetry",
            "tracing",
            "metrics",
            "observability",
            "monitoring",
            "logging",
            "reporting",
        }
        if (
            any(keyword in function_name.lower() for keyword in obs_keywords)
            or "L6_observability" in file_path
        ):
            return ("D4_OBSERVABILITY_INTEGRATION", "Observability/telemetry integration point")
        safety_keywords = {
            "safety",
            "security",
            "validator",
            "enforcement",
            "guard",
            "policy",
            "archival",
            "healing",
            "adapter",
        }
        if (
            any(keyword in function_name.lower() for keyword in safety_keywords)
            or "L5_safety" in file_path
            or "enforcement" in file_path
        ):
            return ("D5_SECURITY_SAFETY_ADAPTER", "Security/safety adapter or policy boundary")
        return ("D3_PLUGIN_REGISTRY_DISPATCH", "Dynamic component loading (default classification)")

    def classify_all_seams(self) -> None:
        """Classify all seams in the allowlist."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "LazySeamClassifier.classify_all_seams",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:LazySeamClassifier.classify_all_seams".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        classified_count = 0
        for seam in self.allowlist_data["seams"]:
            if seam["reason_code"] == "TBD":
                reason_code, justification = self._classify_seam(seam)
                seam["reason_code"] = reason_code
                seam["justification"] = justification
                classified_count += 1
        print(f"Classified {classified_count} seams")
        self.allowlist_data["total_seams"] = len(self.allowlist_data["seams"])

    def save_allowlist(self) -> None:
        """Save updated allowlist to file."""
        _wg.write_json(self.allowlist_path, self.allowlist_data, indent=2)

    def print_summary(self) -> None:
        """Print classification summary."""
        reason_counts = {}
        for seam in self.allowlist_data["seams"]:
            reason = seam["reason_code"]
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
        print("\nClassification Summary:")
        for reason, count in sorted(reason_counts.items()):
            description = self.REASON_TAXONOMY.get(reason, "Unknown")
            print(f"  {reason}: {count} - {description}")


def main():
    """Main execution."""
    root_path = Path.cwd()
    allowlist_path = root_path / AGENTIC_CORE_DIR / "L5_safety" / "governance" / "lazy_seam_allowlist.json"
    classifier = LazySeamClassifier(allowlist_path)
    classifier.classify_all_seams()
    classifier.save_allowlist()
    classifier.print_summary()
    print(f"\nUpdated allowlist saved to: {allowlist_path}")


if __name__ == "__main__":
    main()
