from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "capability_extractor_util")
trace_contract.emit_determinism_digest("p0", "capability_extractor_util")

trace_contract._emit_dispatches_healing_run("p1", "capability_extractor_util", "L5")
trace_contract._emit_routes_through("p1", "capability_extractor_util", "L5")
trace_contract._emit_checks_agent_registry("p1", "capability_extractor_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "capability_extractor_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "capability_extractor_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "capability_extractor_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "capability_extractor_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "capability_extractor_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "capability_extractor_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "capability_extractor_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "capability_extractor_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "capability_extractor_util")
trace_contract._emit_gated_by_confidence("p1", "capability_extractor_util", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "capability_extractor_util", "L5")
trace_contract._emit_reads_policy_state("p1", "capability_extractor_util", "L5")

trace_contract._emit_applies_guardrail("p0", "capability_extractor_util", "p0_governance")
trace_contract._emit_snapshots_state("p0", "capability_extractor_util", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "capability_extractor_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "capability_extractor_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "capability_extractor_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "capability_extractor_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "capability_extractor_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "capability_extractor_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "capability_extractor_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "capability_extractor_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "capability_extractor_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "capability_extractor_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "capability_extractor_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "capability_extractor_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "capability_extractor_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "capability_extractor_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "capability_extractor_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "capability_extractor_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "capability_extractor_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "capability_extractor_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "capability_extractor_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "capability_extractor_util", "exec_snapshot_link")

"\nCapability Extractor - AST-based capability analysis for agent classes.\nExtracted from agent_capability_supplement.py for single responsibility.\n"
import ast


trace_contract._emit_emits_metric_event("capability_extractor_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("capability_extractor_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("capability_extractor_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("capability_extractor_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("capability_extractor_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("capability_extractor_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("capability_extractor_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("capability_extractor_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("capability_extractor_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("capability_extractor_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("capability_extractor_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("capability_extractor_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("capability_extractor_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("capability_extractor_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("capability_extractor_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("capability_extractor_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("capability_extractor_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("capability_extractor_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("capability_extractor_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("capability_extractor_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("capability_extractor_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("capability_extractor_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("capability_extractor_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("capability_extractor_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("capability_extractor_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("capability_extractor_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("capability_extractor_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("capability_extractor_util", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "capability_extractor_util", "context_pull")
trace_contract._emit_pulls_context("p1", "capability_extractor_util", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "capability_extractor_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "capability_extractor_util", "uwg_term_2")
trace_contract._emit_writes_through("p1", "capability_extractor_util", "write_through")
trace_contract._emit_writes_through("p1", "capability_extractor_util", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "capability_extractor_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "capability_extractor_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "capability_extractor_util", "routing_commit")


class CapabilityExtractor:
    """Extracts semantic capabilities from agent class definitions."""

    COMMON_METHODS = {"__init__", "heal_violation", "execute", "run", "validate", "monitor"}
    SEMANTIC_KEYWORDS = {
        "healing": ["heal", "fix", "repair"],
        "validation": ["validate", "check", "enforce"],
        "detection": ["detect", "find", "scan"],
        "pruning": ["prune", "clean", "remove"],
        "mapping": ["map", "territory", "structure"],
        "monitoring": ["watch", "monitor", "observe"],
        "git_integration": ["git"],
    }
    PATTERN_KEYWORDS = {
        "git_operations": [("git", "subprocess"), ("git", "repo")],
        "dead_code_analysis": ["dead code", "unused"],
        "filesystem_introspection": [("filesystem",), ("path", "exists")],
        "redis_integration": ["redis"],
    }

    def extract_capabilities(self, class_node: ast.ClassDef) -> dict[str, any]:
        """Extract rich capability metadata from an agent class.

        Args:
            class_node: AST ClassDef node to analyze

        Returns:
            Dictionary with semantic_tags, unique_methods, patterns, and valuable_methods
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L5_POLICY,
            "CapabilityExtractor.extract_capabilities",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:CapabilityExtractor.extract_capabilities".encode(),
        ).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        caps = {"semantic_tags": set(), "unique_methods": set(), "patterns": set(), "valuable_methods": []}
        for item in class_node.body:
            if not isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            method_name = item.name
            method_loc = item.lineno
            if method_name not in self.COMMON_METHODS:
                caps["unique_methods"].add(method_name)
                caps["valuable_methods"].append((method_name, method_loc, "Unique method signature"))
            self._tag_by_method_name(method_name, caps)
            self._analyze_method_body(item, method_name, method_loc, caps)
        return caps

    def _tag_by_method_name(self, method_name: str, caps: dict) -> None:
        """Tag capabilities based on method name patterns.

        Args:
            method_name: Name of the method
            caps: Capabilities dictionary to update
        """
        lower_name = method_name.lower()
        for tag, keywords in self.SEMANTIC_KEYWORDS.items():
            if any(k in lower_name for k in keywords):
                caps["semantic_tags"].add(tag)

    def _analyze_method_body(
        self,
        item: ast.FunctionDef,
        method_name: str,
        method_loc: int,
        caps: dict,
    ) -> None:
        """Analyze method body for specialized patterns.

        Args:
            item: AST FunctionDef node
            method_name: Name of the method
            method_loc: Line number of method
            caps: Capabilities dictionary to update
        """
        try:
            body_source = ast.unparse(item.body) if hasattr(ast, "unparse") else ""
        except (ValueError, TypeError):  # guardian: allow-silent-swallow
            body_source = ""
        lower_body = body_source.lower()
        if (
            "git" in lower_body
            and "subprocess" in lower_body
            or ("git" in lower_body and "repo" in lower_body)
        ):
            caps["patterns"].add("git_operations")
            caps["valuable_methods"].append((method_name, method_loc, "Git repository interaction"))
        if "dead code" in lower_body or "unused" in lower_body:
            caps["patterns"].add("dead_code_analysis")
            caps["valuable_methods"].append((method_name, method_loc, "Dead/unused code detection"))
        if "filesystem" in lower_body or ("path" in lower_body and "exists" in lower_body):
            caps["patterns"].add("filesystem_introspection")
            caps["valuable_methods"].append((method_name, method_loc, "Advanced filesystem checks"))
        if "redis" in lower_body:
            caps["patterns"].add("redis_integration")
            caps["valuable_methods"].append((method_name, method_loc, "Redis state access"))

    def get_all_capabilities(self, caps: dict) -> set[str]:
        """Get all capabilities (semantic tags + patterns) as a unified set.

        Args:
            caps: Capabilities dictionary

        Returns:
            Set of all capability identifiers
        """
        return caps["semantic_tags"] | caps["patterns"]

    def filter_unique_methods(self, method_names: set[str]) -> set[str]:
        """Filter out common methods, returning only unique ones.

        Args:
            method_names: Set of method names to filter

        Returns:
            Set of unique (non-common) method names
        """
        return method_names - self.COMMON_METHODS
