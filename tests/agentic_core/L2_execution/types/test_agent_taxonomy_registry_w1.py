"""W1 spine axes on agent taxonomy registry."""

from __future__ import annotations

from agentic_core.L2_execution.types.agent_taxonomy_registry import (
    AGENT_TAXONOMY_MAP,
    AgenthoodStatus,
    ProductSpineInvocationStatus,
)
from agentic_core.L2_execution.types.agent_taxonomy_w1_merge import load_agentic_core_w1_rows


def test_w1_json_covers_all_agentic_core_map_entries():
    w1 = load_agentic_core_w1_rows()
    core_in_map = {
        k for k, v in AGENT_TAXONOMY_MAP.items() if v.file_path.startswith("agentic_core/")
    }
    assert len(w1) == 118
    assert w1.keys() <= core_in_map
    assert len(core_in_map) >= 118


def test_existing_ast_validator_has_four_axes():
    entry = AGENT_TAXONOMY_MAP["ASTValidatorAgent"]
    assert entry.agenthood_status == AgenthoodStatus.TRUE_AGENT
    assert entry.product_spine_invocation_status == ProductSpineInvocationStatus.NOT_ARTIFACT_PROVEN


def test_gap_fill_adversarial_probe_registered():
    assert "AdversarialProbeAgent" in AGENT_TAXONOMY_MAP
    row = AGENT_TAXONOMY_MAP["AdversarialProbeAgent"]
    assert row.file_path.startswith("agentic_core/")
    assert row.agenthood_status == AgenthoodStatus.TRUE_AGENT
