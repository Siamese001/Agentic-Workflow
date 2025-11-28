import pytest

from agent_orchestration_v10_7 import get_graph_app


@pytest.mark.design
def test_prompt_nodes_available_when_enabled(workflow_context):
    workflow_context.enable_v10_8_prompts = True
    workflow = get_graph_app(checkpointer=None, workflow_context=workflow_context, enable_hil=False)

    node_names = set(workflow.nodes.keys())
    assert {"run_prompt_builder", "run_prompt_renderer"}.issubset(node_names)
