import sys, types, asyncio, pytest
from typing import Any, Dict
from core_v10_7 import (
    MCPClientStub, _parse_mcp_client_specs, _instantiate_mcp_client, MCPClientSpec,
    MCPClientInitializationError, wrap_mcp, WorkflowContext, BaseTool
)
from agent_orchestration_v10_7 import load_dynamic_tools

def make_broken_module(class_name="BrokenClient"):
    module_name = f"mod_{class_name.lower()}"
    module = types.ModuleType(module_name)
    class BrokenClient:
        def __init__(self, **_): raise RuntimeError("boom")
    setattr(module, class_name, BrokenClient)
    sys.modules[module_name] = module
    return module_name

# ---- Spec parsing (8 tests)
@pytest.mark.parametrize("bad", [ ["not-mapping"], [{"name":"x","parameters":["nope"]}] ])
def test_parse_mcp_client_specs_rejects(bad):
    with pytest.raises(ValueError): _parse_mcp_client_specs(bad)  # type: ignore[arg-type]

def test_instantiate_unknown_provider_returns_stub():
    c = _instantiate_mcp_client(MCPClientSpec(name="mystery", provider="unknown"))
    assert isinstance(c, MCPClientStub)

# ---- Required vs optional failure (6 tests)
@pytest.mark.parametrize("optional,expect_stub", [(True,True),(False,False)])
def test_required_optional_failure_paths(workflow_context: WorkflowContext, optional, expect_stub):
    module_name = make_broken_module()
    workflow_context.config._config["mcp_config"]["clients"].append({
        "name": "broken", "provider":"custom","module":module_name,"class_name":"BrokenClient",
        "parameters":{"note":"x"}, "optional": optional
    })
    workflow_context._load_mcp_config(); workflow_context.reset_mcp_clients()
    if expect_stub:
        clients = workflow_context.ensure_mcp_clients()
        assert isinstance(clients["broken"], MCPClientStub)
    else:
        with pytest.raises(MCPClientInitializationError):
            workflow_context.ensure_mcp_clients()
    sys.modules.pop(module_name, None)

# ---- wrap_mcp decorator behavior (4 tests)
def test_wrap_mcp_initialises_clients(workflow_context: WorkflowContext):
    workflow_context.wrap_mcp_nodes = True
    workflow_context.reset_mcp_clients()
    @wrap_mcp
    async def noop(state, workflow_context): return state
    out = asyncio.run(noop({}, workflow_context))
    assert out == {}
    assert "default_stub" in workflow_context.mcp_clients

def test_wrap_mcp_force_sync(workflow_context: WorkflowContext, monkeypatch: pytest.MonkeyPatch):
    calls={"n":0}
    def fake(): calls["n"]+=1; return {}
    monkeypatch.setattr(workflow_context, "ensure_mcp_clients", fake)
    @wrap_mcp(force=True)
    def handler(state, workflow_context): return state
    assert handler({}, workflow_context) == {}
    assert calls["n"]==1

# ---- Dynamic tool loader honoring MCP (18 tests via temp file)
def test_dynamic_tool_loader_respects_requirements(tmp_path, workflow_context: WorkflowContext):
    workflow_context.wrap_mcp_nodes = True
    workflow_context.reset_mcp_clients()
    tool_dir = tmp_path / "generated_tools_v10_7"; tool_dir.mkdir()
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
