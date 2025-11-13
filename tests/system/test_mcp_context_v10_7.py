import core_v10_7.context as context_module
from core_v10_7 import MCPClientSpec, MCPClientStub


def test_ensure_mcp_clients_converts_optional_failures(monkeypatch, mock_workflow_context):
    ctx = mock_workflow_context
    ctx.reset_mcp_clients()
    ctx._mcp_enabled = True
    ctx._mcp_client_specs = [
        MCPClientSpec(
            name="optional_client",
            provider="custom",
            module="fake.module",
            class_name="FakeClient",
            optional=True,
            parameters={"foo": "bar"},
        )
    ]

    def boom(_spec):
        raise RuntimeError("boom")

    monkeypatch.setattr(context_module, "instantiate_mcp_client", boom)

    clients = ctx.ensure_mcp_clients()
    assert "optional_client" in clients
    assert isinstance(clients["optional_client"], MCPClientStub)
    assert ctx._mcp_errors["optional_client"] == "boom"


def test_get_mcp_client_returns_stub_when_missing_in_stub_mode(mock_workflow_context):
    ctx = mock_workflow_context
    ctx.reset_mcp_clients()
    ctx._mcp_enabled = False
    ctx._mcp_fallback_mode = "stub"

    stub = ctx.get_mcp_client("dynamic_client")
    assert isinstance(stub, MCPClientStub)
    assert stub.name == "dynamic_client"
    assert ctx.mcp_clients["dynamic_client"] is stub
