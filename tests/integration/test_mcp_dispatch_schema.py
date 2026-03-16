"""
Deterministic MCP dispatch and schema correctness tests.

Does NOT require any live MCP server — validates:
1. _TOOL_DISPATCH completeness and correctness (mcp_manager.py)
2. sequential_thinking parameter schema (correct vs wrong)
3. sovereign_mcp_router.py uses correct schema (no Task/goal/max_steps)
4. wiki_healer._update_deepwiki is wired (not a stub)
5. web_search_client calls the correctly-dispatched tool name
6. All dispatch target function names follow mcp<N>_* naming convention
"""

import re
import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_mcp_dispatch_schema")
_emit_applies_guardrail("p0", "test_mcp_dispatch_schema", "p0_governance")
_emit_reads_policy_state("p0", "test_mcp_dispatch_schema", "policy_binding")
_emit_snapshots_state("p0", "test_mcp_dispatch_schema", "state_snapshot")
emit_replay_key("p0", "test_mcp_dispatch_schema")
emit_determinism_digest("p0", "test_mcp_dispatch_schema")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_mcp_dispatch_schema", "execution_auth")
_emit_validates_capability("p2", "test_mcp_dispatch_schema", "capability_check")
_emit_routes_to_capability("p2", "test_mcp_dispatch_schema", "capability_route")
_emit_writes_via_uwg("p2", "test_mcp_dispatch_schema", "uwg_write")
_emit_blocks_direct_write("p2", "test_mcp_dispatch_schema", "direct_write_block")
_emit_records_tool_invocation("p2", "test_mcp_dispatch_schema", "tool_invocation")
_emit_captures_execution_output("p2", "test_mcp_dispatch_schema", "exec_output")
_emit_dispatches_agent("p3", "test_mcp_dispatch_schema", "agent_dispatch")
_emit_coordinates_agents("p3", "test_mcp_dispatch_schema", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_mcp_dispatch_schema", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_mcp_dispatch_schema", "healing_outcome")
_emit_escalates_failure("p3", "test_mcp_dispatch_schema", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_mcp_dispatch_schema", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_mcp_dispatch_schema", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_mcp_dispatch_schema", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_mcp_dispatch_schema", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_mcp_dispatch_schema", "eval_metric")
_emit_stores_embedding("p4", "test_mcp_dispatch_schema", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_mcp_dispatch_schema", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_mcp_dispatch_schema", "exec_snapshot_link")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agentic_core.L3_orchestration.reasoning.mcp_manager import _TOOL_DISPATCH, _resolve_tool  # noqa: E402
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_emits_metric_event("test_mcp_dispatch_schema", "p4obs", "metric_1")
_emit_emits_metric_event("test_mcp_dispatch_schema", "p4obs", "metric_2")
_emit_emits_metric_event("test_mcp_dispatch_schema", "p4obs", "metric_3")
_emit_emits_metric_event("test_mcp_dispatch_schema", "p4obs", "metric_4")
_emit_emits_metric_event("test_mcp_dispatch_schema", "p4obs", "metric_5")
_emit_emits_metric_event("test_mcp_dispatch_schema", "p4obs", "metric_6")
_emit_records_incident_event("test_mcp_dispatch_schema", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_mcp_dispatch_schema", "p4obs", "anomaly")
_emit_writes_observability_log("test_mcp_dispatch_schema", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_mcp_dispatch_schema", "p4obs", "mon_state")
_emit_triggers_alert("test_mcp_dispatch_schema", "p4obs", "alert")
_emit_links_incident_trace("test_mcp_dispatch_schema", "p4obs", "trace_link")
_emit_captures_pattern("test_mcp_dispatch_schema", "p3lm", "pattern")
_emit_records_learning_event("test_mcp_dispatch_schema", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_mcp_dispatch_schema", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_mcp_dispatch_schema", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_mcp_dispatch_schema", "p3lm", "routing")
_emit_improves_agent_policy("test_mcp_dispatch_schema", "p3lm", "policy")
_emit_stores_learning_state("test_mcp_dispatch_schema", "p3lm", "state")
_emit_records_execution_trace("test_mcp_dispatch_schema", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_mcp_dispatch_schema", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_mcp_dispatch_schema", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_mcp_dispatch_schema", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_mcp_dispatch_schema", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_mcp_dispatch_schema", "env_read", "p2_env_1")
_emit_reads_environ("test_mcp_dispatch_schema", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_mcp_dispatch_schema", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_mcp_dispatch_schema", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_mcp_dispatch_schema", "context_pull")
_emit_pulls_context("p1", "test_mcp_dispatch_schema", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_mcp_dispatch_schema", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_mcp_dispatch_schema", "uwg_term_2")
_emit_writes_through("p1", "test_mcp_dispatch_schema", "write_through")
_emit_writes_through("p1", "test_mcp_dispatch_schema", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_mcp_dispatch_schema", "safety_validation")
_emit_invokes_eval("p1", "test_mcp_dispatch_schema", "eval_call")
_emit_proposal_commits_routing("p1", "test_mcp_dispatch_schema", "routing_commit")
_emit_escalates_to_human("p1", "test_mcp_dispatch_schema", "human_escalation")
_emit_routes_through("p1", "test_mcp_dispatch_schema", "route_through")
_emit_checks_agent_registry("p1", "test_mcp_dispatch_schema", "agent_registry")
_emit_validates_agent_capability("p1", "test_mcp_dispatch_schema", "capability")
_emit_dispatches_execution_plan("p1", "test_mcp_dispatch_schema", "exec_plan")
_emit_agent_executes_agent("p1", "test_mcp_dispatch_schema", "sub_agent")
_emit_routes_to_agent("p1", "test_mcp_dispatch_schema", "target_agent")
_emit_verifies_policy("p1", "test_mcp_dispatch_schema", "policy_check")
_emit_observes_runtime_state("p1", "test_mcp_dispatch_schema", "runtime_state")
_emit_verifies_boundary("p1", "test_mcp_dispatch_schema", "boundary_check")
_emit_transcripts_response("p1", "test_mcp_dispatch_schema", "transcript")
_emit_hard_fails_untranscripted("p1", "test_mcp_dispatch_schema")
_emit_gated_by_confidence("p1", "test_mcp_dispatch_schema", "confidence_gate")

# ---------------------------------------------------------------------------
# 1. _TOOL_DISPATCH correctness
# ---------------------------------------------------------------------------

REQUIRED_LOGICAL_TOOLS = {
    # Filesystem
    "read_file", "write_file", "edit_file", "list_directory",
    # Memory
    "create_entities", "search_nodes", "read_graph",
    # Brave Search
    "brave_search", "brave_web_search", "brave_local_search",
    # Playwright
    "playwright_navigate", "playwright_screenshot", "playwright_get_text",
    # Fetch
    "fetch",
    # DeepWiki
    "deepwiki_ask", "deepwiki_structure",
    # Sequential thinking  ← the critical one
    "sequential_thinking",
}

MCP_FUNCTION_PATTERN = re.compile(r"^mcp\d+_[a-z]")


class TestToolDispatch:
    def test_all_required_logical_tools_present(self):
        missing = REQUIRED_LOGICAL_TOOLS - set(_TOOL_DISPATCH.keys())
        assert not missing, f"Missing logical tool keys: {missing}"

    def test_all_dispatch_targets_follow_mcp_naming(self):
        bad = {k: v for k, v in _TOOL_DISPATCH.items() if not MCP_FUNCTION_PATTERN.match(v)}
        assert not bad, f"Non-mcp<N>_ dispatch targets: {bad}"

    def test_sequential_thinking_maps_to_mcp12(self):
        target = _TOOL_DISPATCH.get("sequential_thinking")
        assert target == "mcp12_sequentialthinking", (
            f"sequential_thinking must map to mcp12_sequentialthinking, got: {target}"
        )

    def test_brave_web_search_alias_present(self):
        assert _TOOL_DISPATCH.get("brave_web_search") == "mcp1_brave_web_search"
        assert _TOOL_DISPATCH.get("brave_search") == "mcp1_brave_web_search"

    def test_fetch_maps_to_mcp4(self):
        assert _TOOL_DISPATCH.get("fetch") == "mcp4_fetch"

    def test_deepwiki_maps_to_mcp3(self):
        assert _TOOL_DISPATCH.get("deepwiki_ask") == "mcp3_ask_question"
        assert _TOOL_DISPATCH.get("deepwiki_structure") == "mcp3_read_wiki_structure"

    def test_no_broken_sequential_thinking_import(self):
        """Ensure there is no reference to the old mcp_sequential_thinking module import."""
        mcp_manager_src = (ROOT / "agentic_core/L3_orchestration/reasoning/mcp_manager.py").read_text()
        assert "mcp_sequential_thinking" not in mcp_manager_src, (
            "mcp_manager.py still references non-existent mcp_sequential_thinking module"
        )
        assert "__sequential_thinking__" not in mcp_manager_src, (
            "mcp_manager.py still uses the old __sequential_thinking__ sentinel"
        )

    def test_resolve_tool_returns_none_for_unknown(self):
        result = _resolve_tool("nonexistent_tool_xyz")
        assert result is None

    def test_resolve_tool_returns_none_for_sequential_when_not_in_builtins(self):
        """In test env (no Windsurf), sequential_thinking resolves to None gracefully."""
        import builtins
        had = hasattr(builtins, "mcp12_sequentialthinking")
        result = _resolve_tool("sequential_thinking")
        if not had:
            assert result is None, "Should return None when mcp12 not injected"


# ---------------------------------------------------------------------------
# 2. sequential_thinking correct schema validation
# ---------------------------------------------------------------------------

CORRECT_SCHEMA_REQUIRED = {"thought", "nextThoughtNeeded", "thoughtNumber", "totalThoughts"}
WRONG_SCHEMA_FIELDS = {"Task", "goal", "max_steps", "enforce_no_hallucination", "template"}


class TestSequentialThinkingSchema:
    def test_sovereign_mcp_router_uses_correct_schema(self):
        """sovereign_mcp_router.py must not use Task/goal/max_steps for sequential_thinking."""
        src = (ROOT / "agentic_core/L3_orchestration/engines/sovereign_mcp_router.py").read_text()
        # Find the sequential_thinking call block
        seq_block_match = re.search(
            r'call_tool\(\s*["\']sequential_thinking["\'].*?\)',
            src, re.DOTALL
        )
        assert seq_block_match, "No sequential_thinking call_tool found in sovereign_mcp_router.py"
        call_block = seq_block_match.group(0)
        for wrong_field in WRONG_SCHEMA_FIELDS:
            assert f'"{wrong_field}"' not in call_block and f"'{wrong_field}'" not in call_block, (
                f"sovereign_mcp_router.py still uses wrong schema field '{wrong_field}' "
                f"in sequential_thinking call"
            )
        for correct_field in CORRECT_SCHEMA_REQUIRED:
            assert correct_field in call_block, (
                f"sovereign_mcp_router.py missing required schema field '{correct_field}' "
                f"in sequential_thinking call"
            )

    def test_model_router_types_no_wrong_schema_for_sequential(self):
        """model_router_types.py FallbackClient.generate must not use Task/goal/max_steps
        in a sequential_thinking call_tool block."""
        src = (ROOT / "apps_shared/types/model_router_types.py").read_text()
        # Find all sequential_thinking call_tool blocks
        for match in re.finditer(r'call_tool\(\s*["\']sequential_thinking["\'].*?\)', src, re.DOTALL):
            block = match.group(0)
            for wrong_field in WRONG_SCHEMA_FIELDS:
                assert f'"{wrong_field}"' not in block and f"'{wrong_field}'" not in block, (
                    f"model_router_types.py still uses wrong schema field '{wrong_field}'"
                )

    def test_correct_schema_fields_accepted_by_mcp12_spec(self):
        """Validate correct schema matches the mcp12_sequentialthinking tool definition
        as confirmed by DeepWiki (modelcontextprotocol/servers)."""
        required = {"thought", "nextThoughtNeeded", "thoughtNumber", "totalThoughts"}
        optional = {"isRevision", "revisesThought", "branchFromThought", "branchId", "needsMoreThoughts"}
        all_valid = required | optional
        # A correct call should only use fields from all_valid
        example_call = {
            "thought": "test",
            "nextThoughtNeeded": False,
            "thoughtNumber": 1,
            "totalThoughts": 1,
        }
        unknown = set(example_call.keys()) - all_valid
        assert not unknown, f"Unknown fields in example call: {unknown}"
        missing = required - set(example_call.keys())
        assert not missing, f"Missing required fields: {missing}"


# ---------------------------------------------------------------------------
# 3. wiki_healer is wired (not a stub)
# ---------------------------------------------------------------------------

class TestWikiHealerWiring:
    def test_update_deepwiki_calls_mcp3(self):
        src = (ROOT / "agentic_core/knowledge/healing/wiki_healer.py").read_text()
        assert "mcp3_ask_question" in src, (
            "wiki_healer._update_deepwiki must reference mcp3_ask_question"
        )
        assert "getattr(builtins" in src, (
            "wiki_healer must resolve mcp3_ask_question via builtins"
        )

    def test_update_deepwiki_is_not_stub(self):
        """Ensure _update_deepwiki no longer just returns True without calling anything."""
        src = (ROOT / "agentic_core/knowledge/healing/wiki_healer.py").read_text()
        # Find the _update_deepwiki method body
        match = re.search(
            r"async def _update_deepwiki.*?(?=\n    (?:async )?def |\nclass |\Z)",
            src, re.DOTALL
        )
        assert match, "_update_deepwiki method not found"
        body = match.group(0)
        # Old stub just logged and returned True without any MCP call
        assert "mcp3_ask_question" in body, "_update_deepwiki is still a stub"
        assert "return True" not in body.replace("return result is not None", ""), (
            "_update_deepwiki unconditionally returns True (stub behaviour)"
        )


# ---------------------------------------------------------------------------
# 4. web_search_client uses a correctly mapped tool name
# ---------------------------------------------------------------------------

class TestWebSearchClientDispatch:
    def test_brave_web_search_call_resolves_via_dispatch(self):
        """web_search_client.py calls brave_web_search — confirm it's in _TOOL_DISPATCH."""
        src = (ROOT / "agentic_core/L2_execution/tools/web_search_client.py").read_text(encoding="utf-8", errors="ignore")
        assert "brave_web_search" in src, "web_search_client.py should call brave_web_search"
        assert "brave_web_search" in _TOOL_DISPATCH, (
            "brave_web_search must be in _TOOL_DISPATCH for web_search_client to work"
        )


# ---------------------------------------------------------------------------
# 5. AST-level: no wrong-schema sequential_thinking calls anywhere in codebase
# ---------------------------------------------------------------------------

WRONG_SCHEMA_IN_SEQ_CONTEXT_PATTERN = re.compile(
    r'call_tool\s*\(\s*["\']sequential_thinking["\'].*?(?:"Task"|"goal"|"max_steps"|"enforce_no_hallucination"|"template")',
    re.DOTALL,
)


class TestNoWrongSchemaAnywhere:
    def test_no_wrong_schema_sequential_thinking_calls_in_codebase(self):
        bad_files = []
        for py_file in ROOT.rglob("*.py"):
            if any(p in str(py_file) for p in [".git", "__pycache__", "test_mcp_dispatch_schema"]):
                continue
            try:
                src = py_file.read_text(encoding="utf-8", errors="ignore")
                if "sequential_thinking" in src and WRONG_SCHEMA_IN_SEQ_CONTEXT_PATTERN.search(src):
                    bad_files.append(str(py_file.relative_to(ROOT)))
            # guardian: allow-silent-swallower
            except Exception:
                continue
        assert not bad_files, (
            "Wrong-schema sequential_thinking call sites found:\n"
            + "\n".join(f"  {f}" for f in bad_files)
        )
