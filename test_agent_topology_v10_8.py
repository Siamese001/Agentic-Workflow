from agent_topology import (
    AgentGraph,
    AgentNode,
    AgentRole,
    COUNCIL_OF_QA,
    LINEAR_PIPELINE,
)


def test_agent_role_member_count():
    assert len(AgentRole) == 6


def test_agent_graph_is_deterministic():
    node = AgentNode(AgentRole.PLANNER, {"example": True})
    graph_one = AgentGraph(nodes=[node], edges=[(AgentRole.PLANNER, AgentRole.PLANNER)])
    graph_two = AgentGraph(
        nodes=[AgentNode(AgentRole.PLANNER, {"example": True})],
        edges=[(AgentRole.PLANNER, AgentRole.PLANNER)],
    )

    assert graph_one == graph_two


def test_linear_pipeline_roles_order():
    expected_roles = [
        AgentRole.PLANNER,
        AgentRole.RETRIEVER,
        AgentRole.DRAFTER,
        AgentRole.QA,
        AgentRole.SAFETY,
    ]
    assert [node.role for node in LINEAR_PIPELINE.nodes] == expected_roles

    assert LINEAR_PIPELINE.edges == [
        (AgentRole.PLANNER, AgentRole.RETRIEVER),
        (AgentRole.RETRIEVER, AgentRole.DRAFTER),
        (AgentRole.DRAFTER, AgentRole.QA),
        (AgentRole.QA, AgentRole.SAFETY),
    ]


def test_council_of_qa_contains_three_nodes():
    assert len(COUNCIL_OF_QA.nodes) == 3
    assert all(node.role == AgentRole.QA for node in COUNCIL_OF_QA.nodes)
    assert [node.config.get("id") for node in COUNCIL_OF_QA.nodes] == [1, 2, 3]
