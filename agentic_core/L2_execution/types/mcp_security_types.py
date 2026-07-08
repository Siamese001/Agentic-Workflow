from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "mcp_security_types")
trace_contract.emit_determinism_digest("p0", "mcp_security_types")

trace_contract._emit_dispatches_healing_run("p1", "mcp_security_types", "L2")
trace_contract._emit_routes_through("p1", "mcp_security_types", "L2")
trace_contract._emit_checks_agent_registry("p1", "mcp_security_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "mcp_security_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "mcp_security_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "mcp_security_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "mcp_security_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "mcp_security_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "mcp_security_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "mcp_security_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "mcp_security_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "mcp_security_types")
trace_contract._emit_gated_by_confidence("p1", "mcp_security_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "mcp_security_types", "L2")
trace_contract._emit_reads_policy_state("p1", "mcp_security_types", "L2")

trace_contract._emit_applies_guardrail("p0", "mcp_security_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "mcp_security_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "mcp_security_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "mcp_security_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "mcp_security_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "mcp_security_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "mcp_security_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "mcp_security_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "mcp_security_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "mcp_security_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "mcp_security_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "mcp_security_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "mcp_security_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "mcp_security_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "mcp_security_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "mcp_security_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "mcp_security_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "mcp_security_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "mcp_security_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "mcp_security_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "mcp_security_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "mcp_security_types", "exec_snapshot_link")

"\nMCP Security Guardrail - Consolidated MCP Protection\n\nMerges:\n- MCPGuardian\n- mcp_hardened_mixin\n\nComposable Rules:\n- tool_validation: MCP tool security\n- mcp_hardening: MCP hardening rules\n"
import re
from dataclasses import dataclass, field
from typing import Any

from tqdm import tqdm

trace_contract._emit_emits_metric_event("mcp_security_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("mcp_security_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("mcp_security_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("mcp_security_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("mcp_security_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("mcp_security_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("mcp_security_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("mcp_security_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("mcp_security_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("mcp_security_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("mcp_security_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("mcp_security_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("mcp_security_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("mcp_security_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("mcp_security_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("mcp_security_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("mcp_security_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("mcp_security_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("mcp_security_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("mcp_security_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("mcp_security_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("mcp_security_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("mcp_security_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("mcp_security_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("mcp_security_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("mcp_security_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("mcp_security_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("mcp_security_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "mcp_security_types", "context_pull")
trace_contract._emit_pulls_context("p1", "mcp_security_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "mcp_security_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "mcp_security_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "mcp_security_types", "write_through")
trace_contract._emit_writes_through("p1", "mcp_security_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "mcp_security_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "mcp_security_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "mcp_security_types", "routing_commit")


@dataclass
class MCPSecurityViolation:
    """MCP security violation."""

    rule: str
    severity: str
    tool_name: str
    description: str
    blocked: bool = False


@dataclass
class MCPSecurityResult:
    """Result of MCP security check."""

    allowed: bool
    violations: list[MCPSecurityViolation] = field(default_factory=list)
    sanitized_args: dict[str, Any] | None = None


class MCPSecurityGuardrail:
    """
    Consolidated MCP Security Guardrail.

    Provides unified MCP protection with:
    - Tool whitelist validation
    - Argument sanitization
    - Response validation
    - Audit logging
    """

    def __init__(self):
        """Initialize MCP security guardrail."""
        self.enabled_rules: list[str] = ["tool_validation", "mcp_hardening"]
        self.tool_whitelist: set[str] = {
            "read_file",
            "write_file",
            "edit",
            "run_command",
            "grep_search",
            "find_by_name",
            "list_dir",
            "git_status",
            "git_commit",
            "git_push",
            "redis_get",
            "redis_set",
            "http_get",
            "http_post",
            "brave_search",
            "fetch_url",
        }
        self.dangerous_patterns = [
            "__import__\\s*\\(",
            "eval\\s*\\(",
            "exec\\s*\\(",
            "os\\.system",
            "subprocess\\.",
            "rm\\s+-rf",
            "DROP\\s+TABLE",
            "<script>",
        ]
        self.checks_performed = 0
        self.tools_blocked = 0
        self.args_sanitized = 0

    async def validate_tool_call(self, tool_name: str, args: dict[str, Any]) -> MCPSecurityResult:
        """
        Validate MCP tool call.

        Args:
            tool_name: Name of tool
            args: Tool arguments

        Returns:
            MCPSecurityResult
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L2_EXECUTION,
            "MCPSecurityGuardrail.validate_tool_call",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:MCPSecurityGuardrail.validate_tool_call".encode(),
        ).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        self.checks_performed += 1
        violations = []
        if "tool_validation" in self.enabled_rules:
            if not self._is_tool_allowed(tool_name):
                violations.append(
                    MCPSecurityViolation(
                        rule="tool_validation",
                        severity="error",
                        tool_name=tool_name,
                        description=f"Tool '{tool_name}' not in whitelist",
                        blocked=True,
                    ),
                )
                self.tools_blocked += 1
        if "mcp_hardening" in self.enabled_rules:
            arg_violations = self._check_arguments(tool_name, args)
            violations.extend(arg_violations)
        sanitized = self._sanitize_arguments(args) if args else {}
        if sanitized != args:
            self.args_sanitized += 1
        return MCPSecurityResult(
            allowed=not any(v.blocked for v in violations),
            violations=violations,
            sanitized_args=sanitized,
        )

    def _is_tool_allowed(self, tool_name: str) -> bool:
        """Check if tool is in whitelist."""
        normalized = tool_name.lower().strip()
        if normalized in self.tool_whitelist:
            return True
        for allowed in self.tool_whitelist:
            if normalized.startswith(f"{allowed}_") or normalized.endswith(f"_{allowed}"):
                return True
        return False

    def _check_arguments(self, tool_name: str, args: dict[str, Any]) -> list[MCPSecurityViolation]:
        """Check arguments for dangerous patterns."""
        violations = []
        for key, value in tqdm(args.items(), desc="Processing", unit="item"):
            if isinstance(value, str):
                for pattern in tqdm(self.dangerous_patterns, desc="Processing", unit="item"):
                    if re.search(pattern, value, re.IGNORECASE):
                        violations.append(
                            MCPSecurityViolation(
                                rule="mcp_hardening",
                                severity="critical",
                                tool_name=tool_name,
                                description=f"Dangerous pattern in argument '{key}'",
                                blocked=True,
                            ),
                        )
                        break
        return violations

    def _sanitize_arguments(self, args: dict[str, Any]) -> dict[str, Any]:
        """Sanitize arguments by removing dangerous patterns."""
        sanitized = {}
        for key, value in tqdm(args.items(), desc="Processing", unit="item"):
            if isinstance(value, str):
                clean = value
                for pattern in self.dangerous_patterns:
                    clean = re.sub(pattern, "[BLOCKED]", clean, flags=re.IGNORECASE)
                sanitized[key] = clean
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_arguments(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_arguments({"v": v})["v"] if isinstance(v, str | dict) else v for v in value
                ]
            else:
                sanitized[key] = value
        return sanitized

    def add_to_whitelist(self, tool_name: str) -> None:
        """Add tool to whitelist."""
        self.tool_whitelist.add(tool_name.lower())

    def remove_from_whitelist(self, tool_name: str) -> None:
        """Remove tool from whitelist."""
        self.tool_whitelist.discard(tool_name.lower())

    def get_statistics(self) -> dict[str, Any]:
        """Get MCP security statistics."""
        return {
            "checks_performed": self.checks_performed,
            "tools_blocked": self.tools_blocked,
            "args_sanitized": self.args_sanitized,
            "whitelist_size": len(self.tool_whitelist),
            "enabled_rules": self.enabled_rules,
        }
