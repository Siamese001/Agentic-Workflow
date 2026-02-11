"""
SSOT Guardian Registry — Single Source of Truth for Guardian enumeration.

All consumers of Guardian metadata MUST derive from this registry:
- run_all_guardians.py (aggregator)
- test_guardian_meta_coverage.py (coverage ratchet)
- run_guardian_contract_integrity.py (integrity checker)
- docs/contracts/guardian_to_L6.md (observability contract)

NO filesystem globs. NO duplicated lists. Registry is SSOT.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal


class GuardianTier(str, Enum):
    """Execution tier for guardians."""

    FAST = "fast"  # <1s expected
    SLOW = "slow"  # >1s expected


@dataclass(frozen=True)
class GuardianSpec:
    """
    Specification for a single Guardian.

    Attributes:
        guardian_id: Stable unique identifier (used in artifacts, logs, tests).
        entrypoint_module: Full dotted module path to the guardian script.
        entrypoint_fn: Name of the runner function that returns GuardianResult.
        check_ids: Exhaustive tuple of check_ids this guardian may emit.
        tier: Execution tier (fast/slow) for scheduling.
        enabled_by_default: Whether included in default aggregation runs.
    """

    guardian_id: str
    entrypoint_module: str
    entrypoint_fn: str
    check_ids: tuple[str, ...]
    tier: Literal["fast", "slow"] = "fast"
    enabled_by_default: bool = True


# ---------------------------------------------------------------------------
# SSOT Registry — ALL guardians MUST be registered here
# ---------------------------------------------------------------------------

ALL_GUARDIANS: tuple[GuardianSpec, ...] = tuple(
    sorted(
        [
            GuardianSpec(
                guardian_id="location_alignment",
                entrypoint_module="agentic_core.L0_maintenance.scripts.run_guardian_location_alignment",
                entrypoint_fn="run_location_alignment_guardian",
                check_ids=("misplaced_files", "missing_directories"),
                tier="slow",
                enabled_by_default=True,
            ),
            GuardianSpec(
                guardian_id="hygiene",
                entrypoint_module="agentic_core.L0_maintenance.scripts.run_guardian_hygiene",
                entrypoint_fn="run_hygiene_guardian",
                check_ids=(
                    "temp_artifacts",
                    "empty_folders",
                    "init_only_folders",
                ),
                tier="fast",
                enabled_by_default=True,
            ),
            GuardianSpec(
                guardian_id="manifest_integrity",
                entrypoint_module="agentic_core.L0_maintenance.scripts.run_guardian_manifest",
                entrypoint_fn="run_manifest_guardian",
                check_ids=(
                    "manifest_exists",
                    "lock_exists",
                    "checksum_match",
                ),
                tier="fast",
                enabled_by_default=True,
            ),
            GuardianSpec(
                guardian_id="drift_detection",
                entrypoint_module="agentic_core.L0_maintenance.scripts.run_guardian_drift_detection",
                entrypoint_fn="run_drift_detection_guardian",
                check_ids=("root_drift",),
                tier="fast",
                enabled_by_default=True,
            ),
            GuardianSpec(
                guardian_id="classification_compliance",
                entrypoint_module="agentic_core.L0_maintenance.scripts.run_guardian_classification_compliance",
                entrypoint_fn="run_classification_compliance_guardian",
                check_ids=("naming_compliance", "territory_compliance"),
                tier="slow",
                enabled_by_default=True,
            ),
            GuardianSpec(
                guardian_id="hierarchy_compliance",
                entrypoint_module="agentic_core.L0_maintenance.scripts.run_guardian_hierarchy_compliance",
                entrypoint_fn="run_hierarchy_compliance_guardian",
                check_ids=("missing_structure", "subfolder_compliance"),
                tier="fast",
                enabled_by_default=True,
            ),
            GuardianSpec(
                guardian_id="contract_integrity",
                entrypoint_module="agentic_core.L0_maintenance.scripts.run_guardian_contract_integrity",
                entrypoint_fn="run_contract_integrity_guardian",
                check_ids=(
                    "scripts_found",
                    "imports_contract",
                    "imports_normalize",
                    "returns_result",
                ),
                tier="fast",
                enabled_by_default=False,  # Meta-guardian, run explicitly
            ),
        ],
        key=lambda s: s.guardian_id,
    ),
)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def get_guardian_specs(
    *,
    enabled_only: bool = False,
    tier: GuardianTier | str | None = None,
) -> tuple[GuardianSpec, ...]:
    """
    Retrieve guardian specs with optional filtering.

    Args:
        enabled_only: If True, return only guardians with enabled_by_default=True.
        tier: If provided, filter to only guardians of this tier.

    Returns:
        Tuple of GuardianSpec in deterministic sorted order by guardian_id.
    """
    result = list(ALL_GUARDIANS)
    if enabled_only:
        result = [s for s in result if s.enabled_by_default]
    if tier is not None:
        tier_val = tier.value if isinstance(tier, GuardianTier) else tier
        result = [s for s in result if s.tier == tier_val]
    return tuple(sorted(result, key=lambda s: s.guardian_id))


def get_guardian_by_id(guardian_id: str) -> GuardianSpec | None:
    """Lookup a guardian spec by its ID. Returns None if not found."""
    for spec in ALL_GUARDIANS:
        if spec.guardian_id == guardian_id:
            return spec
    return None


def get_all_check_ids() -> dict[str, tuple[str, ...]]:
    """
    Return a mapping of guardian_id → check_ids for all registered guardians.
    Used by behavioral coverage ratchet.
    """
    return {spec.guardian_id: spec.check_ids for spec in ALL_GUARDIANS}


def get_guardian_entrypoints() -> dict[str, tuple[str, str]]:
    """
    Return a mapping of guardian_id → (module, function) for integrity checking.
    """
    return {spec.guardian_id: (spec.entrypoint_module, spec.entrypoint_fn) for spec in ALL_GUARDIANS}
