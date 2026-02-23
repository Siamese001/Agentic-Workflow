"""Unit tests for Programmatic Tool Calling (PTC) system."""

import pytest

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
    """Test ToolCall validation."""
    # Valid call
    call = ToolCall(
        call_id="abc123",
        tool_id="test_tool",
        args={"pattern": "test"},
    )
    assert call.tool_id == "test_tool"
    assert call.args["pattern"] == "test"

    # Empty call_id
    with pytest.raises(ValueError, match="call_id cannot be empty"):
        ToolCall("", "test", {})

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
    """Test that call ID is stable for same inputs."""
    tool_id = "test_tool"
    args1 = {"pattern": "test", "case_sensitive": True}
    args2 = {"case_sensitive": True, "pattern": "test"}  # Different order

    # Should generate same call ID (canonical JSON normalizes order)
    call_id1 = generate_call_id(tool_id, args1)
    call_id2 = generate_call_id(tool_id, args2)

    assert call_id1 == call_id2
    assert len(call_id1) == 64  # SHA256 hex length

    # Different args should produce different call ID
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
    """Test ToolCallStore integration with in-memory storage."""
    from agentic_core.L3_orchestration.ptc.tool_call_store import ToolCallStore

    # Create in-memory store
    store = ToolCallStore()

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

    # Record call
    store.record_call(call, result, spec)

    # List calls
    calls = store.list_calls()
    assert len(calls) == 1
    assert calls[0]["call"]["call_id"] == "test123"
    assert calls[0]["result"]["stdout"] == "success"

    # Get specific call
    retrieved = store.get_call("test_tool", "test123")
    assert retrieved is not None
    assert retrieved["call"]["call_id"] == "test123"


@pytest.mark.unit_min_deps
def test_tool_call_store_deterministic_ordering():
    """Test that ToolCallStore maintains deterministic ordering."""
    from agentic_core.L3_orchestration.ptc.tool_call_store import ToolCallStore

    # Create in-memory store
    store = ToolCallStore()

    # Record multiple calls
    for i in range(3):
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

    # List calls - should be ordered by timestamp and call_id
    calls = store.list_calls()
    assert len(calls) == 3

    # Check ordering
    call_ids = [c["call"]["call_id"] for c in calls]
    assert call_ids == ["test0", "test1", "test2"]

    # List twice should be identical
    calls2 = store.list_calls()
    call_ids2 = [c["call"]["call_id"] for c in calls2]
    assert call_ids2 == call_ids


@pytest.mark.unit_min_deps
def test_builtin_repo_rg_tool():
    """Test repo_rg built-in tool."""
    from agentic_core.L3_orchestration.ptc.ptc_registry import get_global_registry
    from agentic_core.L3_orchestration.ptc.tool_contract import generate_call_id
    from agentic_core.L3_orchestration.ptc.tool_invoker import ToolInvoker

    # Get global registry (tools auto-registered on import)
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
    from agentic_core.L3_orchestration.ptc.ptc_registry import get_global_registry
    from agentic_core.L3_orchestration.ptc.tool_contract import generate_call_id
    from agentic_core.L3_orchestration.ptc.tool_invoker import ToolInvoker

    # Get global registry (tools auto-registered on import)
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
        assert "unsafe" in result.stdout.lower()


@pytest.mark.unit_min_deps
def test_builtin_tools_deterministic():
    """Test that built-in tools are deterministic across runs."""
    from agentic_core.L3_orchestration.ptc.ptc_registry import get_global_registry
    from agentic_core.L3_orchestration.ptc.tool_contract import generate_call_id
    from agentic_core.L3_orchestration.ptc.tool_invoker import ToolInvoker

    # Get global registry (tools auto-registered on import)
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
    from agentic_core.L3_orchestration.ptc.ptc_registry import get_global_registry, list_tools

    # Get global registry (tools auto-registered on import)
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
    """Test that execute_ssot plan mode includes PTC when flag enabled."""
    import subprocess
    import sys

    # Test plan without PTC
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "agentic_core.L0_routing.scripts.execute_ssot_entrypoint",
            "--legacy",
            "--plan",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "PROGRAMMATIC TOOL CALLING" not in result.stdout

    # Test plan with PTC
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

    assert result.returncode == 0
    assert "No violations found" in result.stdout
