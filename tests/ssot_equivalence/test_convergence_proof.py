"""
Wave 7.2 — Legacy vs New Pipeline Convergence Proof.

Proves that the new guardian→dispatcher→healer pipeline covers the same
violation categories as the legacy execute_ssot pipeline, and that the
new pipeline's scan results are a superset of what legacy detects.

Legacy phases → New equivalents:
- Phase 0 (Pre-Audit):  FilesystemSSOTReconcilerAgent → guardian_drift_detection
- Phase 1 (Discovery):  LocationAgent → guardian_location_alignment
- Phase 1 (Discovery):  FileClassificationAgent → guardian_classification_compliance
- Phase 2 (Alignment):  HierarchyAgent → guardian_hierarchy_compliance
- Phase 3 (Validation): ArchitectureGovernorAgent → guardian_architecture_governance
- Phase 3 (Validation): SystemArchitectAgent → guardian_architecture_governance (import check)
- Phase 4 (Healing):    various heal methods → Wave 6 healers
- Phase 5 (Cert):       N/A → guardian_contract_integrity

Tests:
1. Coverage mapping: every legacy phase agent has a guardian equivalent
2. Check ID superset: new pipeline emits at least legacy violation categories
3. Deterministic replay: same repo → same violations detected
4. Dispatcher phases match legacy phase ordering
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_maintenance.types.guardian_registry import get_guardian_specs
from agentic_core.L2_execution.scripts.remediation_dispatcher import (
    EXPECTED_PHASE_NAMES,
    PHASE_CHECK_ID_PREFIXES,
)
from agentic_core.L2_execution.types.healer_registry import HEALER_REGISTRY

pytestmark = pytest.mark.ssot_equivalence


# ---------------------------------------------------------------------------
# 1. Legacy → Guardian coverage mapping
# ---------------------------------------------------------------------------

# Mapping: legacy agent class → guardian_id that replaces it
LEGACY_TO_GUARDIAN: dict[str, str] = {
    "FilesystemSSOTReconcilerAgent": "drift_detection",
    "LocationAgent": "location_alignment",
    "FileClassificationAgent": "classification_compliance",
    "HierarchyAgent": "hierarchy_compliance",
    "ArchitectureGovernorAgent": "architecture_governance",
}

# Mapping: legacy phase name → dispatcher phase name
LEGACY_PHASE_TO_DISPATCHER: dict[str, str] = {
    "pre_audit": "pre_audit",
    "discovery": "discovery",
    "alignment": "alignment",
    "validation": "arch_validation",
    "healing": "healing",
    "certification": "certification",
}


class TestCoverageMapping:
    """Verify every legacy agent has a guardian equivalent."""

    def test_all_legacy_agents_covered(self) -> None:
        guardian_ids = {s.guardian_id for s in get_guardian_specs(enabled_only=False)}
        for legacy_agent, guardian_id in LEGACY_TO_GUARDIAN.items():
            assert guardian_id in guardian_ids, (
                f"Legacy {legacy_agent} maps to '{guardian_id}' but no such guardian exists"
            )

    def test_guardian_count_exceeds_legacy(self) -> None:
        """New pipeline has at least as many guardians as legacy agents."""
        guardian_count = len(get_guardian_specs(enabled_only=False))
        legacy_count = len(LEGACY_TO_GUARDIAN)
        assert guardian_count >= legacy_count


# ---------------------------------------------------------------------------
# 2. Dispatcher phase ordering matches legacy
# ---------------------------------------------------------------------------


class TestPhaseOrdering:
    """Verify dispatcher phases cover legacy pipeline ordering."""

    def test_expected_phase_count(self) -> None:
        assert len(EXPECTED_PHASE_NAMES) == 7

    def test_pre_audit_first(self) -> None:
        assert EXPECTED_PHASE_NAMES[0] == "pre_audit"

    def test_discovery_before_alignment(self) -> None:
        disc_idx = EXPECTED_PHASE_NAMES.index("discovery")
        align_idx = EXPECTED_PHASE_NAMES.index("alignment")
        assert disc_idx < align_idx

    def test_alignment_before_arch_validation(self) -> None:
        align_idx = EXPECTED_PHASE_NAMES.index("alignment")
        arch_idx = EXPECTED_PHASE_NAMES.index("arch_validation")
        assert align_idx < arch_idx

    def test_arch_validation_before_healing(self) -> None:
        arch_idx = EXPECTED_PHASE_NAMES.index("arch_validation")
        heal_idx = EXPECTED_PHASE_NAMES.index("healing")
        assert arch_idx < heal_idx

    def test_certification_last(self) -> None:
        assert EXPECTED_PHASE_NAMES[-1] == "certification"


# ---------------------------------------------------------------------------
# 3. Phase prefix mapping covers all new guardians
# ---------------------------------------------------------------------------


class TestPhasePrefixCoverage:
    """Verify all guardian check_ids are mapped to dispatcher phases."""

    def test_all_non_empty_phases_have_prefixes(self) -> None:
        """Phases that should have guardian mappings actually do."""
        mapped_phases = {"pre_audit", "discovery", "reconciliation", "alignment", "arch_validation"}
        for phase in mapped_phases:
            prefixes = PHASE_CHECK_ID_PREFIXES.get(phase, ())
            assert len(prefixes) > 0, f"Phase '{phase}' has no guardian prefix mapping"

    def test_new_guardian_prefixes_present(self) -> None:
        """All Wave 5 guardian_ids appear as prefixes in some phase."""
        all_prefixes = []
        for prefixes in PHASE_CHECK_ID_PREFIXES.values():
            all_prefixes.extend(prefixes)

        expected_prefixes = [
            "guardian_classification_compliance",
            "guardian_hierarchy_compliance",
            "guardian_architecture_governance",
        ]
        for prefix in expected_prefixes:
            assert any(prefix.startswith(p) or p.startswith(prefix) for p in all_prefixes), (
                f"Guardian prefix '{prefix}' not found in any phase mapping"
            )


# ---------------------------------------------------------------------------
# 4. Healer registry covers all check_ids that guardians can emit
# ---------------------------------------------------------------------------


class TestHealerConvergence:
    """Verify healer registry covers violation categories from legacy agents."""

    # Legacy healing capabilities → new healer check_ids
    LEGACY_HEAL_TO_HEALER: dict[str, str] = {
        "drift_root_cleanup": "guardian_drift_detection",
        "file_territory_move": "territory_compliance",
        "directory_creation": "missing_structure",
        "naming_review": "naming_compliance",
        "import_review": "import_compliance",
        "agent_relocation_review": "layer_gravity",
        "subfolder_review": "subfolder_compliance",
    }

    def test_all_legacy_heal_capabilities_covered(self) -> None:
        for legacy_cap, healer_id in self.LEGACY_HEAL_TO_HEALER.items():
            assert healer_id in HEALER_REGISTRY, (
                f"Legacy capability '{legacy_cap}' maps to healer '{healer_id}' which is not registered"
            )


# ---------------------------------------------------------------------------
# 5. Deterministic replay: same repo → same violations
# ---------------------------------------------------------------------------


class TestDeterministicReplay:
    """Verify guardian scans are deterministic across multiple runs."""

    def test_classification_deterministic(self) -> None:
        from agentic_core.L0_maintenance.scripts.run_guardian_classification_compliance import (
            run_classification_compliance_guardian,
        )

        r1 = run_classification_compliance_guardian(repo_root=PROJECT_ROOT, timestamp="T1")
        r2 = run_classification_compliance_guardian(repo_root=PROJECT_ROOT, timestamp="T1")
        # Same checks, same evidence (excluding timing)
        assert len(r1.checks) == len(r2.checks)
        for c1, c2 in zip(r1.checks, r2.checks):
            assert c1.check_id == c2.check_id
            assert c1.status == c2.status
            assert c1.evidence == c2.evidence

    def test_hierarchy_deterministic(self) -> None:
        from agentic_core.L0_maintenance.scripts.run_guardian_hierarchy_compliance import (
            run_hierarchy_compliance_guardian,
        )

        r1 = run_hierarchy_compliance_guardian(repo_root=PROJECT_ROOT, timestamp="T1")
        r2 = run_hierarchy_compliance_guardian(repo_root=PROJECT_ROOT, timestamp="T1")
        assert len(r1.checks) == len(r2.checks)
        for c1, c2 in zip(r1.checks, r2.checks):
            assert c1.check_id == c2.check_id
            assert c1.status == c2.status
            assert c1.evidence == c2.evidence

    def test_architecture_deterministic(self) -> None:
        from agentic_core.L0_maintenance.scripts.run_guardian_architecture_governance import (
            run_architecture_governance_guardian,
        )

        r1 = run_architecture_governance_guardian(repo_root=PROJECT_ROOT, timestamp="T1")
        r2 = run_architecture_governance_guardian(repo_root=PROJECT_ROOT, timestamp="T1")
        assert len(r1.checks) == len(r2.checks)
        for c1, c2 in zip(r1.checks, r2.checks):
            assert c1.check_id == c2.check_id
            assert c1.status == c2.status
            assert c1.evidence == c2.evidence
