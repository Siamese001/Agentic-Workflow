from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "mcp_sovereign_authority_enforcer")
trace_contract.emit_determinism_digest("p0", "mcp_sovereign_authority_enforcer")

trace_contract._emit_dispatches_healing_run("p1", "mcp_sovereign_authority_enforcer", "L5")
trace_contract._emit_routes_through("p1", "mcp_sovereign_authority_enforcer", "L5")
trace_contract._emit_checks_agent_registry("p1", "mcp_sovereign_authority_enforcer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "mcp_sovereign_authority_enforcer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "mcp_sovereign_authority_enforcer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "mcp_sovereign_authority_enforcer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "mcp_sovereign_authority_enforcer", "target_agent")
trace_contract._emit_verifies_policy("p1", "mcp_sovereign_authority_enforcer", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "mcp_sovereign_authority_enforcer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "mcp_sovereign_authority_enforcer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "mcp_sovereign_authority_enforcer", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "mcp_sovereign_authority_enforcer")
trace_contract._emit_gated_by_confidence("p1", "mcp_sovereign_authority_enforcer", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "mcp_sovereign_authority_enforcer", "L5")
trace_contract._emit_reads_policy_state("p1", "mcp_sovereign_authority_enforcer", "L5")

trace_contract._emit_applies_guardrail("p0", "mcp_sovereign_authority_enforcer", "p0_governance")
trace_contract._emit_snapshots_state("p0", "mcp_sovereign_authority_enforcer", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "mcp_sovereign_authority_enforcer", "execution_auth")
trace_contract._emit_validates_capability("p2", "mcp_sovereign_authority_enforcer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "mcp_sovereign_authority_enforcer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "mcp_sovereign_authority_enforcer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "mcp_sovereign_authority_enforcer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "mcp_sovereign_authority_enforcer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "mcp_sovereign_authority_enforcer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "mcp_sovereign_authority_enforcer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "mcp_sovereign_authority_enforcer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "mcp_sovereign_authority_enforcer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "mcp_sovereign_authority_enforcer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "mcp_sovereign_authority_enforcer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "mcp_sovereign_authority_enforcer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "mcp_sovereign_authority_enforcer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "mcp_sovereign_authority_enforcer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "mcp_sovereign_authority_enforcer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "mcp_sovereign_authority_enforcer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "mcp_sovereign_authority_enforcer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "mcp_sovereign_authority_enforcer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "mcp_sovereign_authority_enforcer", "exec_snapshot_link")

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

trace_contract._emit_emits_metric_event("mcp_sovereign_authority_enforcer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("mcp_sovereign_authority_enforcer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("mcp_sovereign_authority_enforcer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("mcp_sovereign_authority_enforcer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("mcp_sovereign_authority_enforcer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("mcp_sovereign_authority_enforcer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("mcp_sovereign_authority_enforcer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("mcp_sovereign_authority_enforcer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("mcp_sovereign_authority_enforcer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("mcp_sovereign_authority_enforcer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("mcp_sovereign_authority_enforcer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("mcp_sovereign_authority_enforcer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("mcp_sovereign_authority_enforcer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("mcp_sovereign_authority_enforcer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("mcp_sovereign_authority_enforcer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("mcp_sovereign_authority_enforcer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("mcp_sovereign_authority_enforcer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("mcp_sovereign_authority_enforcer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("mcp_sovereign_authority_enforcer", "p3lm", "state")
trace_contract._emit_records_execution_trace("mcp_sovereign_authority_enforcer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("mcp_sovereign_authority_enforcer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("mcp_sovereign_authority_enforcer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("mcp_sovereign_authority_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("mcp_sovereign_authority_enforcer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("mcp_sovereign_authority_enforcer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("mcp_sovereign_authority_enforcer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("mcp_sovereign_authority_enforcer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("mcp_sovereign_authority_enforcer", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "mcp_sovereign_authority_enforcer", "context_pull")
trace_contract._emit_pulls_context("p1", "mcp_sovereign_authority_enforcer", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "mcp_sovereign_authority_enforcer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "mcp_sovereign_authority_enforcer", "uwg_term_2")
trace_contract._emit_writes_through("p1", "mcp_sovereign_authority_enforcer", "write_through")
trace_contract._emit_writes_through("p1", "mcp_sovereign_authority_enforcer", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "mcp_sovereign_authority_enforcer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "mcp_sovereign_authority_enforcer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "mcp_sovereign_authority_enforcer", "routing_commit")

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
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L5_POLICY,
            "MCPSovereignAuthority.is_authorized",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:MCPSovereignAuthority.is_authorized".encode()).hexdigest()[
            :24
        ]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
                    "L1 tool input contains forbidden cognitive patterns — blocked by shield.",
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
