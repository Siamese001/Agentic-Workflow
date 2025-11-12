import json
import pytest
from workflow.graph import get_nodes, get_edges


@pytest.mark.design
def test_all_design_nodes_exist():
    with open("agentic_design_v10_7.md") as f:
        doc = f.read()
    runtime = set(get_nodes())
    for n in ["PromptInjectionDetector", "PIISanitizerAgent", "QAAgent"]:
        assert n in runtime, f"{n} missing in runtime graph"


@pytest.mark.design
def test_edges_consistency():
    edges = get_edges()
    assert all("->" in e for e in edges)


@pytest.mark.skip("Add 18 design validation tests comparing LIC_10-05-2025_v8.54.json to runtime")
def test_placeholder():
    pass
