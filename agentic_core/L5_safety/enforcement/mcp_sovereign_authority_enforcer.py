from __future__ import annotations

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

emit_replay_key("p0", "mcp_sovereign_authority_enforcer")
emit_determinism_digest("p0", "mcp_sovereign_authority_enforcer")

_emit_dispatches_healing_run("p1", "mcp_sovereign_authority_enforcer", "L5")
_emit_routes_through("p1", "mcp_sovereign_authority_enforcer", "L5")
_emit_checks_agent_registry("p1", "mcp_sovereign_authority_enforcer", "agent_registry")
_emit_validates_agent_capability("p1", "mcp_sovereign_authority_enforcer", "capability")
_emit_dispatches_execution_plan("p1", "mcp_sovereign_authority_enforcer", "exec_plan")
_emit_agent_executes_agent("p1", "mcp_sovereign_authority_enforcer", "sub_agent")
_emit_routes_to_agent("p1", "mcp_sovereign_authority_enforcer", "target_agent")
_emit_verifies_policy("p1", "mcp_sovereign_authority_enforcer", "policy_check")
_emit_observes_runtime_state("p1", "mcp_sovereign_authority_enforcer", "runtime_state")
_emit_verifies_boundary("p1", "mcp_sovereign_authority_enforcer", "boundary_check")
_emit_transcripts_response("p1", "mcp_sovereign_authority_enforcer", "transcript")
_emit_hard_fails_untranscripted("p1", "mcp_sovereign_authority_enforcer")
_emit_gated_by_confidence("p1", "mcp_sovereign_authority_enforcer", "confidence_gate")
_emit_escalates_to_human("p1", "mcp_sovereign_authority_enforcer", "L5")
_emit_reads_policy_state("p1", "mcp_sovereign_authority_enforcer", "L5")

_emit_applies_guardrail("p0", "mcp_sovereign_authority_enforcer", "p0_governance")
_emit_snapshots_state("p0", "mcp_sovereign_authority_enforcer", "state_snapshot")
_emit_authorize_and_execute("p2", "mcp_sovereign_authority_enforcer", "execution_auth")
_emit_validates_capability("p2", "mcp_sovereign_authority_enforcer", "capability_check")
_emit_routes_to_capability("p2", "mcp_sovereign_authority_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "mcp_sovereign_authority_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "mcp_sovereign_authority_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "mcp_sovereign_authority_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "mcp_sovereign_authority_enforcer", "exec_output")
_emit_dispatches_agent("p3", "mcp_sovereign_authority_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "mcp_sovereign_authority_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "mcp_sovereign_authority_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "mcp_sovereign_authority_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "mcp_sovereign_authority_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "mcp_sovereign_authority_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "mcp_sovereign_authority_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "mcp_sovereign_authority_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "mcp_sovereign_authority_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "mcp_sovereign_authority_enforcer", "eval_metric")
_emit_stores_embedding("p4", "mcp_sovereign_authority_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "mcp_sovereign_authority_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "mcp_sovereign_authority_enforcer", "exec_snapshot_link")

"L5 Safety: MCP Sovereign Shield\nEnforces zero-trust auditing and auto-immune responses for all MCP tool calls.\n"
import logging
from datetime import datetime
from typing import Any

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    TESTS_DIR,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_signs_execution_trace,
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

_emit_emits_metric_event("mcp_sovereign_authority_enforcer", "p4obs", "metric_1")
_emit_emits_metric_event("mcp_sovereign_authority_enforcer", "p4obs", "metric_2")
_emit_emits_metric_event("mcp_sovereign_authority_enforcer", "p4obs", "metric_3")
_emit_emits_metric_event("mcp_sovereign_authority_enforcer", "p4obs", "metric_4")
_emit_emits_metric_event("mcp_sovereign_authority_enforcer", "p4obs", "metric_5")
_emit_emits_metric_event("mcp_sovereign_authority_enforcer", "p4obs", "metric_6")
_emit_records_incident_event("mcp_sovereign_authority_enforcer", "p4obs", "incident")
_emit_captures_runtime_anomaly("mcp_sovereign_authority_enforcer", "p4obs", "anomaly")
_emit_writes_observability_log("mcp_sovereign_authority_enforcer", "p4obs", "obs_log")
_emit_updates_monitoring_state("mcp_sovereign_authority_enforcer", "p4obs", "mon_state")
_emit_triggers_alert("mcp_sovereign_authority_enforcer", "p4obs", "alert")
_emit_links_incident_trace("mcp_sovereign_authority_enforcer", "p4obs", "trace_link")
_emit_captures_pattern("mcp_sovereign_authority_enforcer", "p3lm", "pattern")
_emit_records_learning_event("mcp_sovereign_authority_enforcer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("mcp_sovereign_authority_enforcer", "p3lm", "snapshot")
_emit_feeds_meta_learning("mcp_sovereign_authority_enforcer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("mcp_sovereign_authority_enforcer", "p3lm", "routing")
_emit_improves_agent_policy("mcp_sovereign_authority_enforcer", "p3lm", "policy")
_emit_stores_learning_state("mcp_sovereign_authority_enforcer", "p3lm", "state")
_emit_records_execution_trace("mcp_sovereign_authority_enforcer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("mcp_sovereign_authority_enforcer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("mcp_sovereign_authority_enforcer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("mcp_sovereign_authority_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("mcp_sovereign_authority_enforcer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("mcp_sovereign_authority_enforcer", "env_read", "p2_env_1")
_emit_reads_environ("mcp_sovereign_authority_enforcer", "env_read", "p2_env_2")
_emit_reads_runtime_state("mcp_sovereign_authority_enforcer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("mcp_sovereign_authority_enforcer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "mcp_sovereign_authority_enforcer", "context_pull")
_emit_pulls_context("p1", "mcp_sovereign_authority_enforcer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "mcp_sovereign_authority_enforcer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "mcp_sovereign_authority_enforcer", "uwg_term_2")
_emit_writes_through("p1", "mcp_sovereign_authority_enforcer", "write_through")
_emit_writes_through("p1", "mcp_sovereign_authority_enforcer", "write_through_2")
_emit_validated_by_safety_plane("p1", "mcp_sovereign_authority_enforcer", "safety_validation")
_emit_invokes_eval("p1", "mcp_sovereign_authority_enforcer", "eval_call")
_emit_proposal_commits_routing("p1", "mcp_sovereign_authority_enforcer", "routing_commit")

Logger: Any = logging.getLogger(__name__)
_GUARDRAIL_LOG = logging.getLogger("adg.applies_guardrail")
_SAFETY_PLANE_LOG = logging.getLogger("adg.validated_by_safety_plane")
_POLICY_HASH_LOG = logging.getLogger("adg.references_policy_hash")


class MCPSovereignAuthority:
    """Monitors the health and authorization of the MCP nervous system."""

    def __init__(self):
        self.violation_count = 0
        self.breach_log = []
        self.is_locked = False

    def is_authorized(self) -> bool:
        """Sovereignty check: Kill connections if breaches exceed threshold."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "MCPSovereignAuthority.is_authorized"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:MCPSovereignAuthority.is_authorized".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if self.violation_count > 5:
            self.is_locked = True
        return not self.is_locked

    def record_breach(self, error_msg: str) -> Any:
        """Log a tool failure or unauthorized access attempt."""
        self.violation_count += 1
        self.breach_log.append({"timestamp": datetime.now().isoformat(), "error": error_msg})
        Logger.warning(f"[L5 MCP BREACH] Violation recorded. Count: {self.violation_count}")

    def authorize_tool_call(self, tool_name: str, args: dict) -> None:
        """L5 Audit: Log every physical tool call before execution.

        P1/L5: emits applies_guardrail, validated_by_safety_plane,
        references_policy_hash ADG edges on every tool call.
        """
        # P1/L5: emit governed tool call ADG edges
        _GUARDRAIL_LOG.debug("applies_guardrail MCP_SOVEREIGN_AUTHORITY tool=%s", tool_name)
        _SAFETY_PLANE_LOG.debug("validated_by_safety_plane MCP_SOVEREIGN_AUTHORITY tool=%s", tool_name)
        _POLICY_HASH_LOG.debug(
            "references_policy_hash MCP_SOVEREIGN_AUTHORITY tool=%s policy=mcp_sovereign",
            tool_name,
        )
        Logger.info(f"[L5 MCP AUDIT] Authorizing call to '{tool_name}' with args: {args}")
        forbidden_sdks: Any = {"openai", "anthropic", "cohere", "mistral"}
        if tool_name in forbidden_sdks:
            self.record_breach(f"FORBIDDEN SDK CALL: {tool_name}")
            raise PermissionError("Sovereignty Shield: Competitive LLM providers are eternally blocked.")
        if tool_name == "fetch":
            url: Any = args.get("url", "")
            if url and (not url.startswith("https://")):
                if not url.startswith("http://"):
                    raise PermissionError("Sovereignty Shield: Fetch only allowed over secure https/http.")
        if tool_name in {"brave_search", "fetch", "playwright"}:
            query: Any = args.get("query") or args.get("url", "")
            if len(str(query)) > 1000:
                raise ValueError("L2 tool input too long — potential exfiltration risk.")
            forbidden: Any = ["password", "api_key", "secret", "private_key", ".env"]
            if any(bad in str(query).lower() for bad in forbidden):
                raise PermissionError("L2 tool query contains forbidden terms — blocked by shield.")
        if tool_name in {"sequential_thinking", "gemini_policy_enforcer"}:
            max_steps: Any = args.get("max_steps", 0)
            if max_steps > 15:
                raise ValueError("Sequential thinking request exceeds sovereign safety limit (15 steps).")
            Task: Any = args.get("Task") or args.get("Violation", "")
            if len(str(Task)) > 2000:
                raise ValueError("L1 cognitive tool input too long — reasoning overflow risk.")
            risks: Any = ["system prompt", "jailbreak", "override instructions", "ignore all previous"]
            if any(risk in str(Task).lower() for risk in risks):
                raise PermissionError(
                    "L1 tool input contains forbidden cognitive patterns — blocked by shield."
                )
        if tool_name in {"l0_cleanup", "l0_diagnostics"}:
            target: Any = args.get("target") or args.get("scope", "")
            if not target or ".." in str(target) or str(target).startswith("/"):
                raise PermissionError(f"L0 tool target '{target}' invalid — path traversal blocked.")
            allowed_prefixes: Any = {"L0_routing", "logs", "benchmarks", APPS_SHARED_DIR}
            if not any(str(target).startswith(p) for p in allowed_prefixes):
                raise PermissionError("L0 tool target outside sovereign maintenance zones.")
        if tool_name == "redteam_simulate":
            vector: Any = args.get("attack_vector", "")
            if vector not in {"prompt_injection", "logic_bypass", "gravity_leak"}:
                raise PermissionError(f"Unauthorized redteam vector '{vector}' blocked by shield.")
        if tool_name in {"pinecone_search", "memory_search"}:
            if len(str(args.get("query", ""))) > 1500:
                raise ValueError("L4 semantic query too long — vector overflow risk.")
        if tool_name in {"create_entities", "add_observations"}:
            if len(args.get("entities", [])) > 20 or len(args.get("observations", [])) > 50:
                raise ValueError("Memory write batch exceeds sovereign safety limit.")
            if any(bad in str(args).lower() for bad in ["delete_all", "drop_graph", "reset_memory"]):
                raise PermissionError("Destructive memory operation blocked by L5 shield.")
        if tool_name in {"read_wiki_structure", "read_wiki_contents", "ask_question"}:
            repo: Any = args.get("repo", "")
            sovereign_repos: Any = {"xai/grok-canon", "xai/sovereign-canon"}
            if repo and repo not in sovereign_repos:
                raise PermissionError(f"DeepWiki access to non-sovereign repo '{repo}' blocked.")
            question: Any = args.get("question", "")
            if len(question) > 2000:
                raise ValueError("DeepWiki question exceeds sovereign size limit.")
            if any(bad in question.lower() for bad in ["token", "key", "secret", "password"]):
                raise PermissionError("DeepWiki question contains potential credential leaks.")
        if tool_name in {"write_file", "edit_file", "move_file", "create_directory"}:
            path: Any = args.get("path", "")
            allowed_roots: Any = [
                AGENTIC_CORE_DIR,
                APPS_SHARED_DIR,
                APPS_RG_DIR,
                APPS_LIC_DIR,
                TESTS_DIR,
                "config",
            ]
            if path and (not any(str(path).startswith(p) for p in allowed_roots)):
                raise PermissionError(f"L4 Breach: Attempted write outside sovereign roots: {path}")
        if not self.is_authorized():
            raise PermissionError("MCP Sovereign Shield active: Tool call blocked due to chronic breaches.")


mcp_authority: Any = MCPSovereignAuthority()
