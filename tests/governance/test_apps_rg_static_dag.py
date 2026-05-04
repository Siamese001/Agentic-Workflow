"""W5 T-suite — Static L2 recipe governance tests (5 tests).

Validates that apps_rg/config/apps_rg_static_dag.yaml conforms to the
structural invariants required by the apps-rg canonical wireup plan
(apps-rg-canonical-wireup-c8a4f2 W4 P9).

All tests are pure static YAML analysis — no live run required.
"""
from __future__ import annotations

from pathlib import Path

import pytest

try:
    import yaml  # type: ignore[import-untyped]
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

REPO_ROOT = Path(__file__).resolve().parents[2]
STATIC_DAG = REPO_ROOT / "apps_rg" / "config" / "apps_rg_static_dag.yaml"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_dag() -> dict:
    if not _YAML_AVAILABLE:
        pytest.skip("PyYAML not installed — install with: pip install pyyaml")
    if not STATIC_DAG.exists():
        pytest.skip(f"apps_rg_static_dag.yaml not found at {STATIC_DAG}")
    import yaml  # noqa: PLC0415
    return yaml.safe_load(STATIC_DAG.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Test 1: DAG file exists and is valid YAML
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_rg_static_dag_exists_and_valid_yaml() -> None:
    """apps_rg/config/apps_rg_static_dag.yaml must exist and parse as valid YAML."""
    assert STATIC_DAG.exists(), (
        f"apps_rg_static_dag.yaml not found at {STATIC_DAG}. "
        "W4 P9 must land before this test can pass."
    )
    dag = _load_dag()
    assert isinstance(dag, dict), "apps_rg_static_dag.yaml must parse to a YAML mapping."


# ---------------------------------------------------------------------------
# Test 2: DAG declares R4_SINGLE_ACTION route family
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_rg_static_dag_declares_r4_single_action() -> None:
    """Static DAG must declare route_family: R4_SINGLE_ACTION."""
    dag = _load_dag()
    assert dag.get("route_family") == "R4_SINGLE_ACTION", (
        f"apps_rg_static_dag.yaml route_family must be R4_SINGLE_ACTION, "
        f"got: {dag.get('route_family')!r}. "
        "apps_rg performs no corpus retrieval — R3_grounded_read is incorrect (W3 P5)."
    )


# ---------------------------------------------------------------------------
# Test 3: DAG is acyclic (no edge points back to an ancestor)
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_rg_static_dag_is_acyclic() -> None:
    """Static DAG must be acyclic — no cycles allowed in a deterministic HOP pipeline."""
    dag = _load_dag()
    nodes = {n["id"] for n in dag.get("nodes", [])}
    edges = dag.get("edges", [])

    # Build adjacency set
    children: dict[str, set[str]] = {n: set() for n in nodes}
    for e in edges:
        src, tgt = e.get("from"), e.get("to")
        if src in children:
            children[src].add(tgt)

    # DFS cycle detection
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in nodes}
    cycle_detected = []

    def dfs(node: str) -> None:
        if cycle_detected:
            return
        color[node] = GRAY
        for child in children.get(node, set()):
            if color.get(child) == GRAY:
                cycle_detected.append((node, child))
                return
            if color.get(child) == WHITE:
                dfs(child)
        color[node] = BLACK

    for node in nodes:
        if color[node] == WHITE:
            dfs(node)

    assert not cycle_detected, (
        f"apps_rg_static_dag.yaml contains a cycle: {cycle_detected}. "
        "apps_rg pipeline is deterministic — cycles are forbidden."
    )


# ---------------------------------------------------------------------------
# Test 4: Every DAG node has required fields
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_rg_static_dag_nodes_have_required_fields() -> None:
    """Every node in the static DAG must declare id, name, owner, kind, step_contract_schema."""
    dag = _load_dag()
    required = {"id", "name", "owner", "kind", "step_contract_schema"}
    violations = []
    for node in dag.get("nodes", []):
        missing = required - set(node.keys())
        if missing:
            violations.append((node.get("id", "?"), sorted(missing)))

    assert not violations, (
        f"DAG nodes missing required fields: {violations}. "
        "Every node must declare id, name, owner, kind, step_contract_schema."
    )


# ---------------------------------------------------------------------------
# Test 5: DAG entry and terminal nodes exist as declared nodes
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_rg_static_dag_entry_and_terminal_nodes_exist() -> None:
    """entry_nodes and terminal_nodes must reference declared node IDs."""
    dag = _load_dag()
    node_ids = {n["id"] for n in dag.get("nodes", [])}
    entry = dag.get("entry_nodes", [])
    terminal = dag.get("terminal_nodes", [])

    missing_entry = [n for n in entry if n not in node_ids]
    missing_terminal = [n for n in terminal if n not in node_ids]

    assert not missing_entry, (
        f"entry_nodes reference unknown node IDs: {missing_entry}"
    )
    assert not missing_terminal, (
        f"terminal_nodes reference unknown node IDs: {missing_terminal}"
    )
    assert entry, "apps_rg_static_dag.yaml must declare at least one entry_node."
    assert terminal, "apps_rg_static_dag.yaml must declare at least one terminal_node."
