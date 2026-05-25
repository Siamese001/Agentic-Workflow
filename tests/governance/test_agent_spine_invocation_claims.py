"""ADR-088 W1: taxonomy registration must not imply product-spine invocation."""

from __future__ import annotations

from agentic_core.L2_execution.types.agent_taxonomy_registry import (
    AGENT_TAXONOMY_MAP,
    validate_taxonomy_spine_invariants,
)
from agentic_core.L2_execution.types.agent_taxonomy_spine_axes import (
    InventoryRole,
    ProductSpineInvocationStatus,
    RuntimeProofClass,
)


def test_w1_zero_artifact_proven_on_product_spine():
    violations = validate_taxonomy_spine_invariants(AGENT_TAXONOMY_MAP)
    assert violations == [], f"invariant violations: {violations}"


def test_agentic_core_true_agent_count_at_least_87():
    count = sum(
        1
        for e in AGENT_TAXONOMY_MAP.values()
        if str(e.file_path).startswith("agentic_core/")
        and e.agenthood_status.value == "TRUE_AGENT"
    )
    assert count >= 87, f"expected >=87 agentic_core TRUE_AGENT, got {count}"


def test_no_agent_class_marked_product_spine_function():
    bad = [
        k
        for k, e in AGENT_TAXONOMY_MAP.items()
        if k.endswith("Agent")
        and str(e.file_path).startswith("agentic_core/")
        and e.inventory_role == InventoryRole.PRODUCT_SPINE_FUNCTION
    ]
    assert bad == []


def test_w1_registration_defaults_not_artifact_proven():
    core_rows = [e for e in AGENT_TAXONOMY_MAP.values() if e.file_path.startswith("agentic_core/")]
    assert core_rows, "expected agentic_core inventory rows"
    for entry in core_rows:
        assert entry.product_spine_invocation_status == ProductSpineInvocationStatus.NOT_ARTIFACT_PROVEN
        assert entry.runtime_proof_class == RuntimeProofClass.NONE
        assert not (entry.spine_proof_ref or "").strip()
