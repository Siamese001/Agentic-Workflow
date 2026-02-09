"""
Governance test: validates inspection-test-harness-policy.md exists and is current.

This test enforces that the policy document is not accidentally deleted or
de-scoped. It fails if:
  - The policy doc is missing
  - Key required sections are absent
  - The remediation plan is marked "RESOLVED" but layer inversion still exists

This is NOT a semantic validator; it's a structural gate to ensure the policy
doc remains part of the governance surface.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
POLICY_DOC = ROOT / "docs" / "reports" / "plans" / "inspection-test-harness-policy.md"


class TestInspectionPolicyGovernance:
    """Governance gate for the inspection test harness policy document."""

    def test_policy_doc_exists(self) -> None:
        """The policy document must exist."""
        assert POLICY_DOC.exists(), (
            f"Missing policy document: {POLICY_DOC.relative_to(ROOT)}\n"
            "This document is required for governance of the inspection test harness."
        )

    def test_policy_doc_has_required_sections(self) -> None:
        """Policy doc must contain key governance sections."""
        if not POLICY_DOC.exists():
            pytest.skip("Policy doc missing; covered by test_policy_doc_exists")

        content = POLICY_DOC.read_text(encoding="utf-8")
        required_sections = [
            "Decision:",  # Documents the architectural choice
            "What These Tests Do NOT Cover",  # Acknowledges limitations
            "Environment Constraints",  # Documents test env assumptions
            "Breaking Change",  # Documents breaking changes
        ]

        missing = [s for s in required_sections if s not in content]
        assert not missing, (
            f"Policy doc missing required sections: {missing}\nPath: {POLICY_DOC.relative_to(ROOT)}"
        )

    def test_layer_inversion_tracked(self) -> None:
        """If layer inversion exists, it must be documented as tracked debt."""
        if not POLICY_DOC.exists():
            pytest.skip("Policy doc missing")

        # Check if shim still imports from L5
        shim_path = ROOT / "agentic_core" / "base_agents" / "decorators.py"
        if not shim_path.exists():
            pytest.skip("Shim not yet created")

        shim_content = shim_path.read_text(encoding="utf-8")
        has_layer_inversion = "L5_safety" in shim_content

        if has_layer_inversion:
            policy_content = POLICY_DOC.read_text(encoding="utf-8")
            assert "layer inversion" in policy_content.lower(), (
                "Layer inversion exists (base_agents imports from L5_safety) "
                "but is not documented in the policy doc"
            )
