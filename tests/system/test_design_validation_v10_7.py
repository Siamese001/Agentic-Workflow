import pytest
from workflow.graph import get_nodes, get_edges

# Minimal but concrete: assert core safety and qa nodes exist across many ids
@pytest.mark.parametrize("node", [
    "PromptInjectionDetector","PIISanitizerAgent","QAAgent",
    "StrategyAgent","RAGAgent","DraftingAgent"
])
def test_required_nodes_present(node):
    assert node in set(get_nodes())

@pytest.mark.parametrize("edge_contains", ["->"])
def test_edges_render(edge_contains):
    edges = get_edges()
    assert edges and all(edge_contains in e for e in edges)
