from types import SimpleNamespace

from agent_orchestration_v10_7 import get_graph_app
from core_v10_7.models import ArbitrationReport


class DummyArbitrationEngine:
    async def run_check(self, stage: str, state: dict) -> ArbitrationReport:  # pragma: no cover - trivial stub
        return ArbitrationReport(stage=stage, decision="ACCEPT", reasons=["stub"], confidence=1.0)


class DummyWorkflowContext:
    def __init__(self) -> None:
        agent_stacks = SimpleNamespace(
            enable_hil_stack=False,
            max_local_retries=1,
            enable_prompt_injection_detection=False,
        )
        performance_config = SimpleNamespace(workflow_node_timeout_seconds=1)
        self.config = SimpleNamespace(agent_stacks=agent_stacks, performance_config=performance_config)
        self.arbitration_engine = DummyArbitrationEngine()
        self.wrap_mcp_nodes = True

    def reset_mcp_clients(self) -> None:  # pragma: no cover - stubbed
        self.wrap_mcp_nodes = False


def test_graph_app_contains_arbitration_nodes():
    context = DummyWorkflowContext()
    workflow = get_graph_app(checkpointer=None, workflow_context=context, enable_hil=False)

    node_names = set(workflow.nodes.keys())
    expected = {
        "run_arbitration_after_strategy",
        "run_arbitration_after_join",
        "run_arbitration_after_bullets",
        "run_arbitration_after_drafting",
        "run_arbitration_after_qa",
    }

    assert expected.issubset(node_names)
