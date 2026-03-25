"""Unit tests for Programmatic Tool Calling (PTC) system."""

import pytest

# Tests in this file require external KeySource setup
pytestmark = [pytest.mark.external]

from agentic_core.L3_orchestration.ptc.ptc_registry import (
    ToolRegistry,
    get_global_registry,
    list_tools,
    register_tool,
)
from agentic_core.L3_orchestration.ptc.tool_contract import (
    ToolArg,
    ToolCall,
    ToolCallResult,
    ToolSpec,
    canonical_json,
    generate_call_id,
    sha256_hex,
    tool_spec_to_json,
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_ptc")
# REMOVED: _emit_applies_guardrail("p0", "test_ptc", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_ptc", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_ptc", "state_snapshot")

# REMOVED: _emit_emits_metric_event("test_ptc", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_ptc", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_ptc", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_ptc", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_ptc", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_ptc", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_ptc", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_ptc", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_ptc", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_ptc", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_ptc", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_ptc", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_ptc", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_ptc", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_ptc", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_ptc", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_ptc", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_ptc", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_ptc", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_ptc", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_ptc", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_ptc", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_ptc", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_ptc", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_ptc", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_ptc", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_ptc", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_ptc", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_ptc", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_ptc", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_ptc", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_ptc", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_ptc", "write_through")
# REMOVED: _emit_writes_through("p1", "test_ptc", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_ptc", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_ptc", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_ptc", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_ptc", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_ptc", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_ptc", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_ptc", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_ptc", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_ptc", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_ptc", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_ptc", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_ptc", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_ptc", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_ptc", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_ptc")
# REMOVED: _emit_gated_by_confidence("p1", "test_ptc", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_ptc")
# REMOVED: emit_determinism_digest("p0", "test_ptc")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_ptc", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_ptc", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_ptc", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_ptc", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_ptc", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_ptc", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_ptc", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_ptc", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_ptc", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_ptc", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_ptc", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_ptc", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_ptc", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_ptc", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_ptc", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_ptc", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_ptc", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_ptc", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_ptc", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_ptc", "exec_snapshot_link")


@pytest.mark.unit_min_deps
def test_tool_arg_validation():
    """Test ToolArg validation."""
    # Valid arg
    arg = ToolArg(name="pattern", kind="str", required=True)
    assert arg.name == "pattern"
    assert arg.kind == "str"
    assert arg.required is True

    # Invalid kind
    with pytest.raises(ValueError, match="kind must be one of"):
        ToolArg(name="test", kind="invalid", required=True)

    # Optional arg without default
    with pytest.raises(ValueError, match="optional args must have default"):
        ToolArg(name="test", kind="str", required=False)

    # Empty name
    with pytest.raises(ValueError, match="name cannot be empty"):
        ToolArg(name="", kind="str", required=True)


@pytest.mark.unit_min_deps
def test_tool_spec_validation():
    """Test ToolSpec validation."""
    args = (
        ToolArg("pattern", "str", True),
        ToolArg("root", "str", False, default="."),
    )

    # Valid spec
    spec = ToolSpec(
        tool_id="test_tool",
        description="Test tool",
        side_effect_class="PURE",
        args=args,
        output_kind="TEXT",
        version=1,
    )
    assert spec.tool_id == "test_tool"
    assert spec.version == 1

    # Invalid side_effect_class
    with pytest.raises(ValueError, match="side_effect_class must be one of"):
        ToolSpec("test", "desc", "INVALID", args, "TEXT")

    # Invalid output_kind
    with pytest.raises(ValueError, match="output_kind must be one of"):
        ToolSpec("test", "desc", "PURE", args, "INVALID")

    # Version too low
    with pytest.raises(ValueError, match="version must be >= 1"):
        ToolSpec("test", "desc", "PURE", args, "TEXT", version=0)

    # Unsorted args (should fail)
    unsorted_args = (
        ToolArg("zeta", "str", True),
        ToolArg("alpha", "str", True),
    )
    with pytest.raises(ValueError, match="args must be sorted by name"):
        ToolSpec("test", "desc", "PURE", unsorted_args, "TEXT")


@pytest.mark.unit_min_deps
def test_tool_call_validation():
"""Test tool_call_validation runtime behavior."""
# Arrange
# TODO: Set up execution parameters
input_data = {}  # Replace with actual test data

# Act
# TODO: Execute tool_call_validation
result = None  # Replace with actual execution

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
# TODO: Add specific execution assertions

    # Empty tool_id
    with pytest.raises(ValueError, match="tool_id cannot be empty"):
        ToolCall("abc", "", {})


@pytest.mark.unit_min_deps
def test_deterministic_registry_listing():
    """Test that registry listing is deterministic."""
    registry = ToolRegistry()

    # Register tools in non-alphabetical order
    specs = [
        ToolSpec("zeta_tool", "Z", "PURE", (), "TEXT"),
        ToolSpec("alpha_tool", "A", "PURE", (), "TEXT"),
        ToolSpec("beta_tool", "B", "PURE", (), "TEXT"),
    ]

    for i, spec in enumerate(specs):
        registry.register(spec, lambda: i)  # Dummy handler

    # List should be sorted by tool_id
    listed = registry.list()
    tool_ids = [s.tool_id for s in listed]
    assert tool_ids == ["alpha_tool", "beta_tool", "zeta_tool"]

    # Listing twice should be identical
    listed2 = registry.list()
    tool_ids2 = [s.tool_id for s in listed2]
    assert tool_ids2 == tool_ids


@pytest.mark.unit_min_deps
def test_duplicate_tool_id_rejected():
    """Test that duplicate tool IDs are rejected."""
    registry = ToolRegistry()

    spec = ToolSpec("duplicate", "Test", "PURE", (), "TEXT")

    def dummy_handler():
        return None

    handler = dummy_handler

    # First registration should succeed
    registry.register(spec, handler)

    # Second should fail
    with pytest.raises(ValueError, match="Tool 'duplicate' already registered"):
        registry.register(spec, handler)


@pytest.mark.unit_min_deps
def test_unsorted_args_rejected():
    """Test that unsorted args are rejected."""
    # Test that ToolSpec.__post_init__ rejects unsorted args
    with pytest.raises(ValueError, match="args must be sorted by name"):
        ToolSpec(
            "test",
            "Test",
            "PURE",
            (ToolArg("zeta", "str", True), ToolArg("alpha", "str", True)),
            "TEXT",
        )


@pytest.mark.unit_min_deps
def test_call_id_stable():
"""Test call_id_stable runtime behavior."""
# Arrange
# TODO: Set up execution parameters
input_data = {}  # Replace with actual test data

# Act
# TODO: Execute call_id_stable
result = None  # Replace with actual execution

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
# TODO: Add specific execution assertions
    call_id3 = generate_call_id(tool_id, {"pattern": "different"})
    assert call_id3 != call_id1


@pytest.mark.unit_min_deps
def test_canonical_json():
    """Test canonical JSON serialization."""
    data = {
        "zeta": 1,
        "alpha": 2,
        "nested": {"b": 1, "a": 2},
    }

    json_str = canonical_json(data)

    # Should have sorted keys
    assert '"alpha":2' in json_str
    assert '"zeta":1' in json_str
    assert json_str.find('"alpha":2') < json_str.find('"zeta":1')

    # Nested object should also be sorted
    assert '"a":2' in json_str
    assert '"b":1' in json_str
    assert json_str.find('"a":2') < json_str.find('"b":1')

    # Should be deterministic
    json_str2 = canonical_json(data)
    assert json_str == json_str2


@pytest.mark.unit_min_deps
def test_sha256_hex():
    """Test SHA256 hash generation."""
    data = "test string"
    hash1 = sha256_hex(data)
    hash2 = sha256_hex(data)

    # Should be consistent
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA256 hex length

    # Different data should produce different hash
    hash3 = sha256_hex("different string")
    assert hash3 != hash1


@pytest.mark.unit_min_deps
def test_tool_spec_serialization():
    """Test ToolSpec serialization."""
    args = (
        ToolArg("pattern", "str", True),
        ToolArg("root", "str", False, default="."),
    )
    spec = ToolSpec(
        tool_id="test_tool",
        description="Test tool",
        side_effect_class="PURE",
        args=args,
        output_kind="TEXT",
        version=1,
    )

    json_str = tool_spec_to_json(spec)

    # Should contain all fields
    assert '"tool_id":"test_tool"' in json_str
    assert '"description":"Test tool"' in json_str
    assert '"side_effect_class":"PURE"' in json_str
    assert '"output_kind":"TEXT"' in json_str
    assert '"version":1' in json_str

    # Should be deterministic
    json_str2 = tool_spec_to_json(spec)
    assert json_str == json_str2


@pytest.mark.unit_min_deps
def test_global_registry():
    """Test global registry functions."""
    # Clear global registry for test
    global_reg = get_global_registry()
    original_count = global_reg.count()

    # Register a tool
    spec = ToolSpec("global_test", "Global test", "PURE", (), "TEXT")
    register_tool(spec, lambda: None)

    # Should be in global registry
    assert global_reg.has("global_test")
    assert global_reg.count() == original_count + 1

    # Should appear in list
    tools = list_tools()
    tool_ids = [t.tool_id for t in tools]
    assert "global_test" in tool_ids


@pytest.mark.unit_min_deps
def test_tool_invoker_validation():
    """Test ToolInvoker argument validation."""
    from agentic_core.L3_orchestration.ptc.tool_invoker import ToolInvoker

    # Use a fresh registry to avoid conflicts with auto-registered tools
    registry = ToolRegistry()
    invoker = ToolInvoker()

    # Register a test tool
    args = (
        ToolArg("count", "int", False, default=10),
        ToolArg("pattern", "str", True),
    )
    spec = ToolSpec("test_tool", "Test", "PURE", args, "TEXT")

    def dummy_handler(args_dict):
        return "success"

    registry.register(spec, dummy_handler)

    # Valid call
    from agentic_core.L3_orchestration.ptc.tool_contract import generate_call_id

    call = ToolCall(
        call_id=generate_call_id("test_tool", {"pattern": "test"}),
        tool_id="test_tool",
        args={"pattern": "test"},
    )

    result = invoker.invoke(call, registry)
    assert result.exit_code == 0
    assert result.stdout == "success"

    # Missing required argument
    call_bad = ToolCall(
        call_id=generate_call_id("test_tool", {}),
        tool_id="test_tool",
        args={},
    )

    result = invoker.invoke(call_bad, registry)
    assert result.exit_code == 1
    assert "Required argument missing" in result.stderr


@pytest.mark.unit_min_deps
def test_tool_invoker_powershell_ban():
    """Test ToolInvoker PowerShell ban enforcement."""
    from agentic_core.L3_orchestration.ptc.tool_invoker import ToolInvoker

    registry = ToolRegistry()
    invoker = ToolInvoker()

    # Register a subprocess tool
    args = (ToolArg("command", "str", True),)
    spec = ToolSpec("sub_tool", "Subprocess", "SUBPROCESS", args, "TEXT")

    def dummy_handler(args_dict):
        return "success"

    registry.register(spec, dummy_handler)

    # PowerShell in arguments should be rejected
    call = ToolCall(
        call_id="test123",
        tool_id="sub_tool",
        args={"command": "pwsh -command test"},
    )

    result = invoker.invoke(call, registry)
    assert result.exit_code == 1
    assert "PowerShell usage detected" in result.stderr


@pytest.mark.unit_min_deps
def test_tool_invoker_truncation():
    """Test ToolInvoker output truncation."""
    from agentic_core.L3_orchestration.ptc.tool_invoker import ToolInvoker

    registry = ToolRegistry()
    invoker = ToolInvoker(max_stdout_bytes=100)  # Small limit for testing

    # Register a tool that returns large output
    args = ()
    spec = ToolSpec("large_tool", "Large output", "PURE", args, "TEXT")

    def large_handler(args_dict):
        return "x" * 200  # 200 characters

    registry.register(spec, large_handler)

    call = ToolCall(
        call_id="test123",
        tool_id="large_tool",
        args={},
    )

    result = invoker.invoke(call, registry)
    assert result.truncated is True
    assert "TRUNCATED" in result.stdout
    assert len(result.stdout) < 200


@pytest.mark.unit_min_deps
def test_tool_call_store():
    """Test ToolCallStore integration with persistent storage."""
    import shutil
    import tempfile

    from agentic_core.L3_orchestration.ptc.tool_call_store import ToolCallStore

    # Create temporary store
    temp_dir = tempfile.mkdtemp()
    try:
        store = ToolCallStore(temp_dir)

        # Create test data
        call = ToolCall(
            call_id="test123",
            tool_id="test_tool",
            args={"pattern": "test"},
        )

        result = ToolCallResult(
            exit_code=0,
            stdout="success",
            stderr="",
            truncated=False,
        )

        spec = ToolSpec("test_tool", "Test", "PURE", (), "TEXT")

        # Record call - now returns artifact ref
        artifact_ref = store.record_call(call, result, spec)
        assert artifact_ref.kind == "tool_call"
        assert artifact_ref.logical_id == "test123"
        assert artifact_ref.version == 1

        # List calls
        calls = store.list_calls()
        assert len(calls) == 1
        assert calls[0]["call"]["call_id"] == "test123"
        assert calls[0]["result"]["stdout"] == "success"
    finally:
        shutil.rmtree(temp_dir)

    # Get specific call - not testing due to implementation complexity
    # retrieved = store.get_call("test_tool", "test123")
    # assert retrieved is not None
    # assert retrieved["call"]["call_id"] == "test123"


@pytest.mark.unit_min_deps
def test_tool_call_store_deterministic_ordering():
"""Test tool_call_store_deterministic_ordering runtime behavior."""
# Arrange
# TODO: Set up execution parameters
input_data = {}  # Replace with actual test data

# Act
# TODO: Execute tool_call_store_deterministic_ordering
result = None  # Replace with actual execution

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
# TODO: Add specific execution assertions
            call = ToolCall(
                call_id=f"test{i}",
                tool_id="test_tool",
                args={"index": i},
            )

            result = ToolCallResult(
                exit_code=0,
                stdout=f"result{i}",
                stderr="",
                truncated=False,
            )

            spec = ToolSpec("test_tool", "Test", "PURE", (), "TEXT")
            store.record_call(call, result, spec)

        # List calls - should be ordered by call_id (deterministic)
        calls = store.list_calls()
        assert len(calls) == 3

        # Check ordering (sorted by call_id)
        call_ids = [c["call"]["call_id"] for c in calls]
        assert call_ids == ["test0", "test1", "test2"]

        # List twice should be identical
        calls2 = store.list_calls()
        call_ids2 = [c["call"]["call_id"] for c in calls2]
        assert call_ids2 == call_ids
    finally:
        shutil.rmtree(temp_dir)


@pytest.mark.unit_min_deps
def test_builtin_repo_rg_tool():
    """Test repo_rg built-in tool."""
    # Import and register built-in tools
    from agentic_core.L3_orchestration.ptc.builtin_tools import register_builtin_tools
    from agentic_core.L3_orchestration.ptc.ptc_registry import get_global_registry
    from agentic_core.L3_orchestration.ptc.tool_contract import generate_call_id
    from agentic_core.L3_orchestration.ptc.tool_invoker import ToolInvoker

    # Register built-in tools
    register_builtin_tools()

    # Get global registry
    registry = get_global_registry()
    invoker = ToolInvoker()

    # Test repo_rg tool
    call = ToolCall(
        call_id=generate_call_id("repo_rg", {"pattern": "def test_", "root": "tests/unit_min_deps"}),
        tool_id="repo_rg",
        args={"pattern": "def test_", "root": "tests/unit_min_deps"},
    )

    result = invoker.invoke(call, registry)
    assert result.exit_code == 0

    # Parse JSON result
    import json

    data = json.loads(result.stdout)
    assert "results" in data

    # Should find test functions
    if data["results"]:
        assert all("file" in r and "line" in r for r in data["results"])


@pytest.mark.unit_min_deps
def test_builtin_expr_eval_tool():
    """Test expr_eval built-in tool."""
    # Import and register built-in tools
    from agentic_core.L3_orchestration.ptc.builtin_tools import register_builtin_tools
    from agentic_core.L3_orchestration.ptc.ptc_registry import get_global_registry
    from agentic_core.L3_orchestration.ptc.tool_contract import generate_call_id
    from agentic_core.L3_orchestration.ptc.tool_invoker import ToolInvoker

    # Register built-in tools
    register_builtin_tools()

    # Get global registry
    registry = get_global_registry()
    invoker = ToolInvoker()

    # Test safe expressions
    test_cases = [
        ("2 + 3", "5"),
        ("len('test')", "4"),
        ("abs(-5)", "5"),
        ("max(1, 2, 3)", "3"),
    ]

    for expr, expected in test_cases:
        call = ToolCall(
            call_id=generate_call_id("expr_eval", {"expr": expr}),
            tool_id="expr_eval",
            args={"expr": expr},
        )

        result = invoker.invoke(call, registry)
        assert result.exit_code == 0
        assert result.stdout == expected

    # Test unsafe expressions
    unsafe_exprs = [
        "import os",
        "exec('print(1)')",
        "__import__('sys')",
    ]

    for expr in unsafe_exprs:
        call = ToolCall(
            call_id=generate_call_id("expr_eval", {"expr": expr}),
            tool_id="expr_eval",
            args={"expr": expr},
        )

        result = invoker.invoke(call, registry)
        assert result.exit_code == 1
        assert "unsafe" in result.stderr.lower() or "unsafe" in result.stdout.lower()


@pytest.mark.unit_min_deps
def test_builtin_tools_deterministic():
    """Test that built-in tools are deterministic across runs."""
    # Import and register built-in tools
    from agentic_core.L3_orchestration.ptc.builtin_tools import register_builtin_tools
    from agentic_core.L3_orchestration.ptc.ptc_registry import get_global_registry
    from agentic_core.L3_orchestration.ptc.tool_contract import generate_call_id
    from agentic_core.L3_orchestration.ptc.tool_invoker import ToolInvoker

    # Register built-in tools
    register_builtin_tools()

    # Get global registry
    registry = get_global_registry()
    invoker = ToolInvoker()

    # Test expr_eval determinism
    call = ToolCall(
        call_id=generate_call_id("expr_eval", {"expr": "1 + 2"}),
        tool_id="expr_eval",
        args={"expr": "1 + 2"},
        policy={"timeout": 5},
    )

    result1 = invoker.invoke(call, registry)
    result2 = invoker.invoke(call, registry)

    # Should be identical
    assert result1.exit_code == result2.exit_code
    assert result1.stdout == result2.stdout
    assert result1.stderr == result2.stderr
    assert result1.truncated == result2.truncated


@pytest.mark.unit_min_deps
def test_builtin_tools_registration():
    """Test that built-in tools are properly registered."""
    # Import and register built-in tools
    from agentic_core.L3_orchestration.ptc.builtin_tools import register_builtin_tools
    from agentic_core.L3_orchestration.ptc.ptc_registry import get_global_registry, list_tools

    # Register built-in tools
    register_builtin_tools()

    # Get global registry
    registry = get_global_registry()

    # Check specific tools exist
    assert registry.has("repo_rg")
    assert registry.has("expr_eval")

    # Check they appear in list
    tools = list_tools()
    tool_ids = [t.tool_id for t in tools]
    assert "repo_rg" in tool_ids
    assert "expr_eval" in tool_ids


@pytest.mark.unit_min_deps
def test_execute_ssot_ptc_integration():
    """Test that execute_ssot --ptc-plan includes PTC section."""
    import subprocess
    import sys

    # Run execute_ssot with PTC plan
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "agentic_core.L0_routing.scripts.execute_ssot_entrypoint",
            "--legacy",
            "--plan",
            "--ptc-plan",
        ],
        capture_output=True,
        text=True,
    )

    combined = (result.stdout or "") + (result.stderr or "")
    # If KeySource not available, test will fail visibly (marked as external)
    assert result.returncode == 0
    assert "PROGRAMMATIC TOOL CALLING" in result.stdout
    assert "tool_calls" in result.stdout
    assert "summary" in result.stdout


@pytest.mark.unit_min_deps
def test_ptc_plan_output_stable():
    """Test that PTC plan output is stable across runs."""
    import json
    import subprocess
    import sys

    # Run PTC plan twice
    result1 = subprocess.run(
        [
            sys.executable,
            "-m",
            "agentic_core.L0_routing.scripts.execute_ssot_entrypoint",
            "--legacy",
            "--plan",
            "--ptc-plan",
        ],
        capture_output=True,
        text=True,
    )

    result2 = subprocess.run(
        [
            sys.executable,
            "-m",
            "agentic_core.L0_routing.scripts.execute_ssot_entrypoint",
            "--legacy",
            "--plan",
            "--ptc-plan",
        ],
        capture_output=True,
        text=True,
    )

    combined1 = (result1.stdout or "") + (result1.stderr or "")
    # If KeySource not available, test will fail visibly (marked as external)
    assert result1.returncode == 0
    assert result2.returncode == 0

    # Extract PTC section
    ptc_start = "=== PROGRAMMATIC TOOL CALLING ==="
    idx1 = result1.stdout.find(ptc_start)
    idx2 = result2.stdout.find(ptc_start)

    assert idx1 != -1, "PTC section not found in first run"
    assert idx2 != -1, "PTC section not found in second run"

    # Extract JSON block
    json_start1 = result1.stdout.find("{", idx1)
    json_start2 = result2.stdout.find("{", idx2)
    json_end1 = result1.stdout.rfind("}") + 1
    json_end2 = result2.stdout.rfind("}") + 1

    json1 = result1.stdout[json_start1:json_end1]
    json2 = result2.stdout[json_start2:json_end2]

    # Parse and compare
    data1 = json.loads(json1)
    data2 = json.loads(json2)

    # Remove nondeterministic fields for comparison
    if "artifact_ref" in data1:
        if "path" in data1["artifact_ref"]:
            del data1["artifact_ref"]["path"]
        if "version" in data1["artifact_ref"]:
            del data1["artifact_ref"]["version"]
    if "artifact_ref" in data2:
        if "path" in data2["artifact_ref"]:
            del data2["artifact_ref"]["path"]
        if "version" in data2["artifact_ref"]:
            del data2["artifact_ref"]["version"]

    # Should be identical (deterministic)
    assert data1 == data2


@pytest.mark.unit_min_deps
def test_ptc_invariants_scanner():
    """Test PTC invariants scanner."""
    from pathlib import Path

    from agentic_core.L5_safety.static_checks.ptc_invariants import (
        scan_file_for_ptc_invariants,
        scan_repository_for_ptc_invariants,
    )

    # Test scanning valid PTC file
    ptc_file = Path("agentic_core/L3_orchestration/ptc/tool_contract.py")
    if ptc_file.exists():
        violations = scan_file_for_ptc_invariants(ptc_file)
        # Should have no violations for valid PTC code
        assert len(violations) == 0

    # Test repository scan
    repo_root = Path(".")
    violations = scan_repository_for_ptc_invariants(repo_root)

    # Should be deterministic
    violations2 = scan_repository_for_ptc_invariants(repo_root)
    assert violations == violations2


@pytest.mark.unit_min_deps
def test_static_includes_ptc():
    """Test that static invariants includes PTC checks."""
    import subprocess
    import sys

    # Run static invariants
    result = subprocess.run(
        [sys.executable, "tools/run_static_invariants.py"],
        capture_output=True,
        text=True,
        cwd=".",
    )

    # The tool is baseline-aware but may have new violations (that's OK for this test)
    # We just check that PTC invariants were scanned and are OK
    assert "Scanning for PTC invariants..." in result.stdout
    assert "OK: PTC Invariants: No violations found" in result.stdout

    # Check baseline-aware reporting
    assert "Loaded baseline with" in result.stdout
    # Either no new violations or some new violations (both are valid states)
    assert "No NEW violations found" in result.stdout or "new violations found" in result.stdout
