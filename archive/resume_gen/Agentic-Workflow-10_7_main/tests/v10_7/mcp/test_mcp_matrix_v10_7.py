import asyncio
import asyncio
import sys
import types
from typing import Any, Dict

import pytest

from core_v10_7 import (
    BaseTool,
    MCPClientInitializationError,
    MCPClientSpec,
    MCPClientStub,
    WorkflowContext,
    instantiate_mcp_client,
    parse_mcp_client_specs,
    wrap_mcp,
)
from agent_orchestration_v10_7 import load_dynamic_tools
from agent_tools_v10_7 import resolve_mcp_client

def make_broken_module(class_name: str = "BrokenClient") -> str:
    module_name = f"mod_{class_name.lower()}"
    module = types.ModuleType(module_name)
    class BrokenClient:
        def __init__(self, **_: Any) -> None:
            raise RuntimeError("boom")
    setattr(module, class_name, BrokenClient)
    sys.modules[module_name] = module
    return module_name

# ---- Spec parsing (8 tests)
@pytest.mark.parametrize(
    "bad",
    [["not-mapping"], [{"name": "x", "parameters": ["nope"]}]],
)
def test_parse_mcp_client_specs_rejects(bad):
    with pytest.raises(ValueError):
        parse_mcp_client_specs(bad)  # type: ignore[arg-type]

def test_instantiate_missing_class_raises_attribute_error():
    module_name = "failing_mcp_module"
    module = types.ModuleType(module_name)
    sys.modules[module_name] = module

    spec = MCPClientSpec(
        name="missing",
        provider="custom",
        module=module_name,
        class_name="DoesNotExist",
    )

    try:
        with pytest.raises(AttributeError):
            instantiate_mcp_client(spec)
    finally:
        sys.modules.pop(module_name, None)

def test_instantiate_unknown_provider_returns_stub():
    c = instantiate_mcp_client(MCPClientSpec(name="mystery", provider="unknown"))
    assert isinstance(c, MCPClientStub)


def test_workflow_context_initialises_default_stub(workflow_context: WorkflowContext):
    workflow_context.wrap_mcp_nodes = True
    workflow_context.reset_mcp_clients()

    clients = workflow_context.ensure_mcp_clients()

    assert "default_stub" in clients
    assert isinstance(clients["default_stub"], MCPClientStub)

# ---- Required vs optional failure (6 tests)
@pytest.mark.parametrize("optional,expect_stub", [(True, True), (False, False)])
def test_required_optional_failure_paths(workflow_context: WorkflowContext, optional, expect_stub):
    module_name = make_broken_module()
    clients_cfg = workflow_context.config._config["mcp_config"]["clients"]
    clients_cfg.append({
        "name": "broken",
        "provider": "custom",
        "module": module_name,
        "class_name": "BrokenClient",
        "parameters": {"note": "x"},
        "optional": optional,
    })
    try:
        workflow_context._load_mcp_config()
        workflow_context.reset_mcp_clients()
        if expect_stub:
            clients = workflow_context.ensure_mcp_clients()
            stub = clients["broken"]
            assert isinstance(stub, MCPClientStub)
            assert stub.parameters["note"] == "x"
            assert "error" in stub.parameters
        else:
            with pytest.raises(MCPClientInitializationError):
                workflow_context.ensure_mcp_clients()
    finally:
        clients_cfg.pop()
        workflow_context._load_mcp_config()
        workflow_context.reset_mcp_clients()
        sys.modules.pop(module_name, None)

# ---- wrap_mcp decorator behavior (4 tests)
def test_wrap_mcp_initialises_clients(workflow_context: WorkflowContext):
    workflow_context.wrap_mcp_nodes = True
    workflow_context.reset_mcp_clients()
    @wrap_mcp
    async def noop(state, workflow_context):
        return state
    out = asyncio.run(noop({}, workflow_context))
    assert out == {}
    assert "default_stub" in workflow_context.mcp_clients

def test_wrap_mcp_force_sync(workflow_context: WorkflowContext, monkeypatch: pytest.MonkeyPatch):
    calls = {"n": 0}

    def fake():
        calls["n"] += 1
        return {}
    monkeypatch.setattr(workflow_context, "ensure_mcp_clients", fake)
    @wrap_mcp(force=True)
    def handler(state, workflow_context):
        return state
    assert handler({}, workflow_context) == {}
    assert calls["n"] == 1


def test_wrap_mcp_sync_skips_when_disabled(workflow_context: WorkflowContext, monkeypatch: pytest.MonkeyPatch):
    workflow_context.wrap_mcp_nodes = False
    calls = {"n": 0}

    def fake():
        calls["n"] += 1
        return {}

    monkeypatch.setattr(workflow_context, "ensure_mcp_clients", fake)

    @wrap_mcp
    def handler(state, workflow_context):
        return state

    assert handler({}, workflow_context) == {}
    assert calls["n"] == 0

# ---- Dynamic tool loader honoring MCP (18 tests via temp file)
def test_dynamic_tool_loader_respects_requirements(tmp_path, workflow_context: WorkflowContext):
    workflow_context.wrap_mcp_nodes = True
    workflow_context.reset_mcp_clients()
    tool_dir = tmp_path / "generated_tools_v10_7"
    tool_dir.mkdir()
    code = """
from core_v10_7 import BaseTool, track_metrics
class MCPSampleTool(BaseTool):
    tool_name="mcp_sample_tool"
    required_mcp_clients=["default_stub"]
    optional_mcp_clients=["aux_client"]
    @track_metrics('tool_dynamic_test')
    async def _run_async_internal(self, tool_input, workflow_id):
        c = self.get_mcp_client('default_stub')
        return {"status": c.parameters.get("note","missing")}
"""
    (tool_dir / "mcp_tool.py").write_text(code)
    workflow_context.config.meta_loop_config._data["generated_tools_path"]=str(tool_dir)
    tools = load_dynamic_tools(workflow_context, debug_mode=False)
    assert "mcp_sample_tool" in tools
    out = asyncio.run(tools["mcp_sample_tool"]._run_async_internal({}, "wf"))
    assert "status" in out


def test_resolve_mcp_client_optional_returns_stub(workflow_context: WorkflowContext):
    workflow_context.wrap_mcp_nodes = True
    workflow_context.reset_mcp_clients()

    class DummyTool(BaseTool):
        tool_name = "dummy"

        async def _run_async_internal(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
            return {}

    tool = DummyTool(workflow_context)
    stub = resolve_mcp_client(tool, "nonexistent", optional=True)

    assert isinstance(stub, MCPClientStub)
    assert tool.get_mcp_client("nonexistent") is stub


def test_resolve_mcp_client_required_raises_without_fallback(workflow_context: WorkflowContext):
    cfg = workflow_context.config._config["mcp_config"]
    original_mode = cfg.get("fallback_mode")
    try:
        cfg["fallback_mode"] = "error"
        workflow_context._load_mcp_config()
        workflow_context.reset_mcp_clients()

        class DummyTool(BaseTool):
            tool_name = "dummy-required"

            async def _run_async_internal(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
                return {}

        tool = DummyTool(workflow_context)

        with pytest.raises(KeyError):
            resolve_mcp_client(tool, "nonexistent", optional=False)
    finally:
        cfg["fallback_mode"] = original_mode
        workflow_context._load_mcp_config()
        workflow_context.reset_mcp_clients()


def test_optional_mcp_client_failure_falls_back_to_stub(workflow_context: WorkflowContext):
    module_name = make_broken_module("OptionalBrokenClient")
    clients_cfg = workflow_context.config._config["mcp_config"]["clients"]
    cfg = workflow_context.config._config["mcp_config"]
    original_mode = cfg.get("fallback_mode")

    clients_cfg.append(
        {
            "name": "optional_broken",
            "provider": "custom",
            "module": module_name,
            "class_name": "OptionalBrokenClient",
            "parameters": {"note": "from optional"},
            "optional": True,
        }
    )

    try:
        cfg["fallback_mode"] = "error"
        workflow_context._load_mcp_config()
        workflow_context.reset_mcp_clients()
        clients = workflow_context.ensure_mcp_clients()

        assert "optional_broken" in clients
        stub = clients["optional_broken"]
        assert isinstance(stub, MCPClientStub)
        assert stub.parameters["note"] == "from optional"
        assert "error" in stub.parameters
    finally:
        clients_cfg.pop()
        cfg["fallback_mode"] = original_mode
        workflow_context._load_mcp_config()
        workflow_context.reset_mcp_clients()
        sys.modules.pop(module_name, None)


def test_required_mcp_client_failure_raises_error(workflow_context: WorkflowContext):
    module_name = make_broken_module("RequiredBrokenClient")
    clients_cfg = workflow_context.config._config["mcp_config"]["clients"]
    cfg = workflow_context.config._config["mcp_config"]
    original_mode = cfg.get("fallback_mode")

    clients_cfg.append(
        {
            "name": "required_broken",
            "provider": "custom",
            "module": module_name,
            "class_name": "RequiredBrokenClient",
            "parameters": {"note": "from required"},
            "optional": False,
        }
    )

    try:
        cfg["fallback_mode"] = "error"
        workflow_context._load_mcp_config()
        workflow_context.reset_mcp_clients()

        with pytest.raises(MCPClientInitializationError):
            workflow_context.ensure_mcp_clients()
    finally:
        clients_cfg.pop()
        cfg["fallback_mode"] = original_mode
        workflow_context._load_mcp_config()
        workflow_context.reset_mcp_clients()
        sys.modules.pop(module_name, None)


def test_get_mcp_client_returns_fallback_stub_when_configured(workflow_context: WorkflowContext):
    cfg = workflow_context.config._config["mcp_config"]
    original_mode = cfg.get("fallback_mode")
    original_params = cfg.get("fallback_parameters", {}).copy()

    try:
        cfg["fallback_mode"] = "stub"
        cfg["fallback_parameters"] = {"source": "test"}
        workflow_context._load_mcp_config()
        workflow_context.reset_mcp_clients()

        missing = workflow_context.get_mcp_client("auto_stub")
        assert isinstance(missing, MCPClientStub)
        assert missing.parameters["source"] == "test"
    finally:
        if original_mode is None:
            cfg.pop("fallback_mode", None)
        else:
            cfg["fallback_mode"] = original_mode
        if original_params:
            cfg["fallback_parameters"] = original_params
        else:
            cfg.pop("fallback_parameters", None)
        workflow_context._load_mcp_config()
        workflow_context.reset_mcp_clients()
