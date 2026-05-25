"""ADR-088 orthogonal taxonomy axes — separate from canonical_role (W1)."""

from __future__ import annotations

from enum import Enum

__all__ = [
    "AgenthoodStatus",
    "InventoryRole",
    "ProductSpineInvocationStatus",
    "RuntimeProofClass",
    "W1_REGISTRATION_DEFAULTS",
    "validate_taxonomy_spine_invariants",
]


class AgenthoodStatus(Enum):
    TRUE_AGENT = "TRUE_AGENT"
    NOT_AGENT = "NOT_AGENT"
    WRAPPER_ONLY = "WRAPPER_ONLY"
    SHIM_OR_DEAD_LEGACY = "SHIM_OR_DEAD_LEGACY"


class InventoryRole(Enum):
    PRODUCT_SPINE_FUNCTION = "PRODUCT_SPINE_FUNCTION"
    TRUE_AGENT_NOT_ON_PRODUCT_SPINE = "TRUE_AGENT_NOT_ON_PRODUCT_SPINE"
    GOVERNANCE_CERTIFIER_OR_VALIDATOR = "GOVERNANCE_CERTIFIER_OR_VALIDATOR"
    HEALER_OR_DEV_AGENT = "HEALER_OR_DEV_AGENT"
    UTILITY_OR_WRAPPER = "UTILITY_OR_WRAPPER"
    SHIM_OR_DEAD_LEGACY = "SHIM_OR_DEAD_LEGACY"


class ProductSpineInvocationStatus(Enum):
    ARTIFACT_PROVEN = "ARTIFACT_PROVEN"
    NOT_ARTIFACT_PROVEN = "NOT_ARTIFACT_PROVEN"


class RuntimeProofClass(Enum):
    LIVE_RUNTIME_PROOF = "LIVE_RUNTIME_PROOF"
    REPLAY_RUNTIME_PROOF = "REPLAY_RUNTIME_PROOF"
    TEST_RUNTIME_PROOF = "TEST_RUNTIME_PROOF"
    MOCK_ONLY_PROOF = "MOCK_ONLY_PROOF"
    NONE = "NONE"


W1_REGISTRATION_DEFAULTS: dict[str, object] = {
    "product_spine_invocation_status": ProductSpineInvocationStatus.NOT_ARTIFACT_PROVEN,
    "runtime_proof_class": RuntimeProofClass.NONE,
    "spine_proof_ref": "",
}

_ALLOWED_PROOF_FOR_ARTIFACT_PROVEN = frozenset({
    RuntimeProofClass.LIVE_RUNTIME_PROOF,
    RuntimeProofClass.REPLAY_RUNTIME_PROOF,
    RuntimeProofClass.TEST_RUNTIME_PROOF,
})


def validate_taxonomy_spine_invariants(
    taxonomy_map: dict[str, object],
    *,
    require_agentic_core_true_agent_count: int | None = 87,
) -> list[str]:
    """Return violation messages (empty if valid). Used by CI and unit tests."""
    violations: list[str] = []
    true_agent_core = 0

    for class_name, entry in taxonomy_map.items():
        file_path = getattr(entry, "file_path", "")
        agenthood = getattr(entry, "agenthood_status", None)
        inventory_role = getattr(entry, "inventory_role", None)
        invocation = getattr(entry, "product_spine_invocation_status", None)
        proof_class = getattr(entry, "runtime_proof_class", None)
        spine_proof_ref = getattr(entry, "spine_proof_ref", "") or ""

        for label, value in (
            ("agenthood_status", agenthood),
            ("inventory_role", inventory_role),
            ("product_spine_invocation_status", invocation),
            ("runtime_proof_class", proof_class),
        ):
            if value is None:
                violations.append(f"{class_name}: missing {label}")

        if invocation == ProductSpineInvocationStatus.ARTIFACT_PROVEN:
            if not spine_proof_ref.strip():
                violations.append(
                    f"{class_name}: ARTIFACT_PROVEN requires non-empty spine_proof_ref (A2)",
                )
            if proof_class not in _ALLOWED_PROOF_FOR_ARTIFACT_PROVEN:
                violations.append(
                    f"{class_name}: ARTIFACT_PROVEN requires LIVE/REPLAY/TEST proof class, "
                    f"got {proof_class}",
                )

        if proof_class == RuntimeProofClass.MOCK_ONLY_PROOF and (
            invocation == ProductSpineInvocationStatus.ARTIFACT_PROVEN
        ):
            violations.append(
                f"{class_name}: MOCK_ONLY_PROOF cannot satisfy product-spine invocation (W1)",
            )

        if (
            file_path.startswith("agentic_core/")
            and class_name.endswith("Agent")
            and inventory_role == InventoryRole.PRODUCT_SPINE_FUNCTION
        ):
            violations.append(
                f"{class_name}: *Agent class cannot use PRODUCT_SPINE_FUNCTION inventory_role",
            )

        if (
            str(file_path).startswith("agentic_core/")
            and agenthood == AgenthoodStatus.TRUE_AGENT
        ):
            true_agent_core += 1

    if (
        require_agentic_core_true_agent_count is not None
        and true_agent_core < require_agentic_core_true_agent_count
    ):
        violations.append(
            f"agentic_core TRUE_AGENT count {true_agent_core} < "
            f"{require_agentic_core_true_agent_count}",
        )

    proven = sum(
        1
        for e in taxonomy_map.values()
        if getattr(e, "product_spine_invocation_status", None)
        == ProductSpineInvocationStatus.ARTIFACT_PROVEN
    )
    if proven > 0:
        violations.append(
            f"W1 baseline: expected 0 ARTIFACT_PROVEN rows, found {proven}",
        )

    return violations
