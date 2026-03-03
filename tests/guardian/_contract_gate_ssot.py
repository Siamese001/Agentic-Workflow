"""
SSOT Contract Gate Configuration — Single Source of Truth for contract gate scope.

Derived from guardian registry - covers all enabled_by_default guardians.
No manual exclusion lists - SSOT-derived only.
"""

from __future__ import annotations

from agentic_core.L0_routing.types.guardian_registry_types import get_guardian_specs

# ---------------------------------------------------------------------------
# SSOT: Contract gate test modules derived from guardian registry
# ---------------------------------------------------------------------------

# Map each guardian_id to its required test module(s)
# NOTE: Only list modules that ACTUALLY EXIST on disk
# Each guardian maps to its ACTUAL behavioral test module (not a catch-all)
GUARDIAN_ID_TO_TEST_MODULES: dict[str, tuple[str, ...]] = {
    "architecture_governance": ("test_guardian_architecture_governance",),
    "classification_compliance": ("test_guardian_classification_compliance",),
    "contract_integrity": ("test_guardian_self_integrity",),
    "drift_detection": ("test_drift_detection",),
    "hierarchy_compliance": ("test_guardian_hierarchy_compliance",),
    "hygiene": ("test_guardian_hygiene",),
    "location_alignment": ("test_location_alignment",),
    "manifest_integrity": ("test_guardian_manifest",),
}

# Required test symbols that prove semantic coverage per guardian
# At least ONE of these symbols must appear in the mapped test module(s)
GUARDIAN_ID_TO_REQUIRED_TEST_SYMBOLS: dict[str, tuple[str, ...]] = {
    "architecture_governance": (
        "run_architecture_governance_guardian",
        "TestArchitectureGovernance",
        "test_architecture_governance",
    ),
    "classification_compliance": (
        "run_classification_compliance_guardian",
        "TestClassificationCompliance",
        "test_classification_compliance",
    ),
    "contract_integrity": (
        "TestStatusPromotion",
        "TestRealRepoIntegrity",
        "run_contract_integrity_guardian",
    ),
    "drift_detection": (
        "TestDriftDetection",
        "test_drift_detection",
        "run_drift_detection_guardian",
    ),
    "hierarchy_compliance": (
        "run_hierarchy_compliance_guardian",
        "TestHierarchyCompliance",
        "test_hierarchy_compliance",
    ),
    "hygiene": (
        "TestHygieneRealRepo",
        "TestHygieneSyntheticViolation",
        "run_hygiene_guardian",
    ),
    "location_alignment": (
        "run_location_alignment_guardian",
        "TestLocationAlignment",
        "test_location_alignment",
    ),
    "manifest_integrity": (
        "TestManifestRealRepo",
        "TestManifestSyntheticViolation",
        "run_manifest_guardian",
    ),
}

# Required status assertions per guardian (enforces actual behavioral testing)
# Each guardian must have at least one assertion comparing *.status to the required status
GUARDIAN_ID_TO_REQUIRED_STATUS_ASSERTIONS: dict[str, tuple[str, ...]] = {
    "architecture_governance": (),
    "classification_compliance": (),
    "contract_integrity": (
        # Must test FAIL and PASS status detection
        "GuardianStatus.FAIL.value",
        "GuardianStatus.PASS.value",
    ),
    "drift_detection": (),
    "hierarchy_compliance": (),
    "hygiene": (
        # Must test FAIL status detection (synthetic violations)
        "GuardianStatus.FAIL.value",
    ),
    "location_alignment": (),
    "manifest_integrity": (
        # Must test FAIL status detection
        "GuardianStatus.FAIL.value",
    ),
}

# Canonical status values the structural AST scanner recognises.
STATUS_ASSERTION_ENUM_VALUES: frozenset[str] = frozenset(
    {
        "PASS",
        "FAIL",
        "ERROR",
        "SKIP",
    },
)

# Canonical assertion families the gate accepts (must be structural, not substring):
# 1) dot_status_equals:   <expr>.status == <Enum>.<VALUE>.value   OR   == "<VALUE>"
# 2) rolled_up_equals:    <expr> == <Enum>.<VALUE>.value          OR   == "<VALUE>"
ALLOWED_STATUS_ASSERTION_FAMILIES: frozenset[str] = frozenset(
    {
        "dot_status_equals",
        "rolled_up_equals",
    },
)

# Derived contract gate test modules (SSOT)
# ONLY include modules that ACTUALLY EXIST - no phantom files
CONTRACT_GATE_TEST_MODULES: tuple[str, ...] = tuple(
    sorted(
        {module for modules in GUARDIAN_ID_TO_TEST_MODULES.values() for module in modules}
        | {
            # Core contract enforcement modules that EXIST on disk
            "test_aggregator_invariants",
            "test_artifact_class_enum_ratchet",
            "test_behavioral_coverage_ratchet",
            "test_conftest_ignore_policy",
            "test_contract_compatibility",
            "test_core_components",
            "test_execute_ssot_v15_contract",
            "test_guardian_aggregation",
            "test_guardian_contract",
            "test_guardian_contract_gate_scope",
            "test_guardian_runtime_budget",
            "test_guardian_self_integrity",
            "test_guardian_hygiene",
            "test_guardian_manifest",
            "test_l6_signal_contract",
            "test_no_xfail_skip_in_contract_gate",
            "test_performance_caps",
            "test_registry_completeness",
            "test_scan_budget_integrity",
            "test_semantic_coverage_quality",
        },
    ),
)

# Contract gate guardian IDs (enabled_by_default only)
CONTRACT_GATE_GUARDIAN_IDS: tuple[str, ...] = tuple(
    sorted(spec.guardian_id for spec in get_guardian_specs(enabled_only=True)),
)

# Meta-guardian IDs that must always be covered (even if enabled set is empty)
META_GUARDIAN_IDS: frozenset[str] = frozenset({"contract_integrity"})


def enabled_guardian_ids_from_registry() -> set[str]:
    """
    Compute the set of enabled guardian IDs from the registry.

    Returns:
        Set of guardian_id strings where enabled_by_default=True.
    """
    return {spec.guardian_id for spec in get_guardian_specs(enabled_only=True)}


def validate_contract_gate_ssot() -> None:
    """
    Validate that SSOT configuration is valid and non-vacuous.
    Raises AssertionError if validation fails.
    """
    import pathlib

    test_dir = pathlib.Path(__file__).parent
    actual_modules = {py_file.stem for py_file in test_dir.glob("test_*.py")}

    # 1. All listed test modules must exist on disk
    missing_modules = set(CONTRACT_GATE_TEST_MODULES) - actual_modules
    assert not missing_modules, (
        f"Contract gate test modules not found: {sorted(missing_modules)}\n"
        f"Create missing modules or remove from CONTRACT_GATE_TEST_MODULES"
    )

    # 2. Minimum module count guard
    assert len(CONTRACT_GATE_TEST_MODULES) >= 5, (
        f"CONTRACT_GATE_TEST_MODULES has too few entries ({len(CONTRACT_GATE_TEST_MODULES)}). "
        f"This may indicate accidental deletion."
    )

    # 3. Non-vacuous check: If enabled guardians exist, they must be covered
    enabled_ids = enabled_guardian_ids_from_registry()
    if enabled_ids:
        uncovered = enabled_ids - set(GUARDIAN_ID_TO_TEST_MODULES.keys())
        assert not uncovered, (
            f"Enabled guardians not covered by GUARDIAN_ID_TO_TEST_MODULES: {sorted(uncovered)}\n"
            f"Add test module mappings for these guardians."
        )

    # 4. Meta-guardian coverage: At least one meta-guardian must be mapped
    meta_covered = META_GUARDIAN_IDS & set(GUARDIAN_ID_TO_TEST_MODULES.keys())
    assert meta_covered, (
        f"No meta-guardians covered. At least one of {sorted(META_GUARDIAN_IDS)} must be mapped "
        f"in GUARDIAN_ID_TO_TEST_MODULES to prevent vacuous gate."
    )
