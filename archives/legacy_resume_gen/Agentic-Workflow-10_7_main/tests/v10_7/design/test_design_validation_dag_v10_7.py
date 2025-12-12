import pytest

# from archives.legacy_resume_gen.Agentic-Workflow-10_7_main.agent_orchestration_v10_7 import get_graph_app  # INVALID: Cannot import from path with hyphens

EXPECTED_NODES = [
    "SafetyGuardStack",
    "StrategyStack",
    "RAGStack",
    "BulletStack",
    "DraftingStack",
    "QAStack",
    "HILInteractionStack",
]

EXPECTED_EDGES = [
    ("SafetyGuardStack", "StrategyStack"),
    ("StrategyStack", "RAGStack"),
    ("RAGStack", "BulletStack"),
    ("BulletStack", "DraftingStack"),
    ("DraftingStack", "QAStack"),
    ("QAStack", "HILInteractionStack"),
]

EXPECTED_ORDER = [
    "SafetyGuardStack",
    "StrategyStack",
    "RAGStack",
    "BulletStack",
    "DraftingStack",
    "QAStack",
    "HILInteractionStack",
]


@pytest.fixture()
def compiled_workflow(workflow_context):
    workflow_context.config.agent_stacks.enable_hil_stack = True
    workflow = get_graph_app(
        checkpointer=None,
        workflow_context=workflow_context,
        enable_hil=True,
    )
    return workflow


def _runtime_node_names(compiled_workflow):
    return set(compiled_workflow.nodes.keys())


@pytest.mark.design
def test_conceptual_nodes_match_specification_order() -> None:
    names = [node.name for node in CONCEPTUAL_DAG]
    assert names == EXPECTED_ORDER, "Conceptual DAG order drifted from spec"


@pytest.mark.design
def test_conceptual_node_names_match_expected_set() -> None:
    assert set(node.name for node in CONCEPTUAL_DAG) == set(EXPECTED_NODES), (
        "Conceptual DAG names must match v10.7 design document"
    )


@pytest.mark.design
def test_conceptual_edges_match_design_doc() -> None:
    lookup = {name: idx for idx, name in enumerate(EXPECTED_ORDER)}
    for src, dst in EXPECTED_EDGES:
        assert lookup[src] < lookup[dst], f"{src} must precede {dst}"


@pytest.mark.design
def test_conceptual_edge_spec_matches_expected() -> None:
    assert CONCEPTUAL_EDGES == EXPECTED_EDGES


@pytest.mark.design
def test_all_conceptual_nodes_have_concrete_mappings() -> None:
    for node in CONCEPTUAL_DAG:
        assert node.concrete_nodes, f"Conceptual node {node.name} has no concrete mapping"


@pytest.mark.design
def test_conceptual_nodes_exist_in_runtime(compiled_workflow):
    runtime_nodes = _runtime_node_names(compiled_workflow)
    for node in CONCEPTUAL_DAG:
        missing = set(node.concrete_nodes) - runtime_nodes
        assert not missing, f"{node.name} missing runtime nodes: {sorted(missing)}"


@pytest.mark.design
def test_runtime_nodes_align_with_conceptual_spec(compiled_workflow):
    runtime_nodes = _runtime_node_names(compiled_workflow)
    spec_nodes = all_concrete_nodes()
    missing = spec_nodes - runtime_nodes
    extra = runtime_nodes - spec_nodes
    assert not missing, f"Spec nodes not found in runtime graph: {sorted(missing)}"
    assert not extra, f"Runtime nodes missing from conceptual spec: {sorted(extra)}"


@pytest.mark.design
def test_conceptual_lookup_contains_all_nodes() -> None:
    lookup = conceptual_node_map()
    for name in EXPECTED_NODES:
        assert name in lookup, f"Missing conceptual node mapping for {name}"
