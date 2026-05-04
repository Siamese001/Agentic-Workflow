"""DS-3 Governance sentinels for apps_rg L3 static_dag_registry binding.

DS-3 was: "apps_rg DAG registered in static_dag_registry; no inline dag
construction remains".

The YAML topology (apps_rg/config/apps_rg_static_dag.yaml) was created in
canonical-wireup W4 P9 but never registered in the L3 static_dag_registry.
DS-3 closes that gap by wiring _build_apps_rg_dag() into get_default_registry().

Tests:
1. APPS_RG_DAG_ID exported from registry module.
2. get_default_registry() contains the apps_rg DAG.
3. Registered proof has correct dag_id, 9 nodes, 8 edges.
4. Entry node is hop_0_load_validated_inputs; terminal is hop_8_seal_exhaust_bundle.
5. All L3 policy flags are True (no-execute, no-retrieve, no-prompt-assembly, no-l4-write).
6. has_cycle is False; dag_sha256 is non-empty and deterministic (stable across calls).
7. route_ids includes apps_rg.resume_generation_v1.
8. YAML file exists on disk and its dag_id matches the registered proof.
9. Registry raises KeyError on unknown dag_id (no silent None return).
10. known_dag_ids() includes both the demo DAG and the apps_rg DAG.

Plan: apps-rg-deferred-scope-followon-d4e1b9 DS-3.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
APPS_RG_DAG_YAML = REPO_ROOT / "apps_rg" / "config" / "apps_rg_static_dag.yaml"


@pytest.mark.governance
def test_apps_rg_dag_id_exported() -> None:
    """APPS_RG_DAG_ID must be importable from the registry module."""
    from agentic_core.L3_orchestration.registry.static_dag_registry import (
        APPS_RG_DAG_ID,
    )
    assert APPS_RG_DAG_ID == "apps_rg.resume_generation_v1.static_dag"


@pytest.mark.governance
def test_apps_rg_dag_in_default_registry() -> None:
    """get_default_registry() must contain the apps_rg DAG."""
    from agentic_core.L3_orchestration.registry.static_dag_registry import (
        APPS_RG_DAG_ID,
        get_default_registry,
    )
    registry = get_default_registry()
    assert APPS_RG_DAG_ID in registry.known_dag_ids(), (
        f"apps_rg DAG not registered. Known: {registry.known_dag_ids()}"
    )


@pytest.mark.governance
def test_apps_rg_dag_proof_shape() -> None:
    """Registered proof must have 9 nodes and 8 edges matching the YAML spec."""
    from agentic_core.L3_orchestration.registry.static_dag_registry import (
        APPS_RG_DAG_ID,
        get_default_registry,
    )
    proof = get_default_registry().get(APPS_RG_DAG_ID)
    assert proof.dag_id == APPS_RG_DAG_ID
    assert len(proof.nodes) == 9, f"Expected 9 nodes, got {len(proof.nodes)}"
    assert len(proof.edges) == 8, f"Expected 8 edges, got {len(proof.edges)}"


@pytest.mark.governance
def test_apps_rg_dag_entry_and_terminal_nodes() -> None:
    """Entry must be hop_0_load_validated_inputs; terminal hop_8_seal_exhaust_bundle."""
    from agentic_core.L3_orchestration.registry.static_dag_registry import (
        APPS_RG_DAG_ID,
        get_default_registry,
    )
    proof = get_default_registry().get(APPS_RG_DAG_ID)
    assert "hop_0_load_validated_inputs" in proof.entry_nodes, (
        f"Entry node missing. Got: {proof.entry_nodes}"
    )
    assert "hop_8_seal_exhaust_bundle" in proof.terminal_nodes, (
        f"Terminal node missing. Got: {proof.terminal_nodes}"
    )


@pytest.mark.governance
def test_apps_rg_dag_l3_policy_flags() -> None:
    """All L3 no-execute/retrieve/prompt/l4-write policies must be True."""
    from agentic_core.L3_orchestration.registry.static_dag_registry import (
        APPS_RG_DAG_ID,
        get_default_registry,
    )
    proof = get_default_registry().get(APPS_RG_DAG_ID)
    d = proof.to_dict()
    for flag in (
        "l3_no_execute_policy",
        "l3_no_retrieve_policy",
        "l3_no_prompt_assembly_policy",
        "l3_no_l4_write_policy",
    ):
        assert d[flag] is True, (
            f"apps_rg static DAG proof: {flag} must be True. "
            "L3 shapes workflow only — no execution, retrieval, prompt assembly, or L4 writes."
        )


@pytest.mark.governance
def test_apps_rg_dag_no_cycle_and_digest_stable() -> None:
    """has_cycle must be False; dag_sha256 non-empty and identical across two builds."""
    from agentic_core.L3_orchestration.registry.static_dag_registry import (
        APPS_RG_DAG_ID,
        _build_apps_rg_dag,
        get_default_registry,
    )
    proof = get_default_registry().get(APPS_RG_DAG_ID)
    assert proof.has_cycle is False, "apps_rg static DAG must be acyclic."
    assert proof.dag_sha256.startswith("sha256:"), (
        f"dag_sha256 must start with 'sha256:'. Got: {proof.dag_sha256!r}"
    )
    # Determinism: rebuilding produces identical digest
    proof2 = _build_apps_rg_dag()
    assert proof.dag_sha256 == proof2.dag_sha256, (
        "StaticDagProof digest is not deterministic — build_static_dag_proof "
        "produced two different hashes for the same topology."
    )


@pytest.mark.governance
def test_apps_rg_dag_route_id() -> None:
    """route_ids must include apps_rg.resume_generation_v1."""
    from agentic_core.L3_orchestration.registry.static_dag_registry import (
        APPS_RG_DAG_ID,
        get_default_registry,
    )
    proof = get_default_registry().get(APPS_RG_DAG_ID)
    assert "apps_rg.resume_generation_v1" in proof.route_ids, (
        f"apps_rg DAG must declare route_id=apps_rg.resume_generation_v1. "
        f"Got: {proof.route_ids}"
    )


@pytest.mark.governance
def test_apps_rg_static_dag_yaml_exists_and_matches_registry() -> None:
    """YAML file must exist and its dag_id must match the registered proof."""
    assert APPS_RG_DAG_YAML.exists(), (
        f"apps_rg/config/apps_rg_static_dag.yaml missing: {APPS_RG_DAG_YAML}"
    )
    from agentic_core.L3_orchestration.registry.static_dag_registry import (
        APPS_RG_DAG_ID,
    )
    doc = yaml.safe_load(APPS_RG_DAG_YAML.read_text(encoding="utf-8"))
    assert doc.get("dag_id") == APPS_RG_DAG_ID, (
        f"YAML dag_id {doc.get('dag_id')!r} != registry APPS_RG_DAG_ID {APPS_RG_DAG_ID!r}"
    )


@pytest.mark.governance
def test_registry_raises_key_error_on_unknown_dag() -> None:
    """get(unknown_dag_id) must raise KeyError — no silent None return."""
    from agentic_core.L3_orchestration.registry.static_dag_registry import (
        get_default_registry,
    )
    registry = get_default_registry()
    with pytest.raises(KeyError, match="not registered"):
        registry.get("completely.unknown.dag_id.xyz")


@pytest.mark.governance
def test_registry_known_dag_ids_includes_both() -> None:
    """known_dag_ids() must list both demo and apps_rg DAGs."""
    from agentic_core.L3_orchestration.registry.static_dag_registry import (
        APPS_RG_DAG_ID,
        DEMO_TWO_NODE_DAG_ID,
        get_default_registry,
    )
    ids = get_default_registry().known_dag_ids()
    assert DEMO_TWO_NODE_DAG_ID in ids, f"Demo DAG missing from known_dag_ids: {ids}"
    assert APPS_RG_DAG_ID in ids, f"apps_rg DAG missing from known_dag_ids: {ids}"
