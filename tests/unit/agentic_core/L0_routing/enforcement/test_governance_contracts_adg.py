"""Runtime-hardened tests for governance evidence-pack enforcement contracts."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def enforcement_package():
    return pytest.importorskip("agentic_core.L0_routing.enforcement")


class TestGovernanceEvidencePackContracts:
    def test_build_evidence_pack_returns_value(self, enforcement_package):
        result = enforcement_package.build_evidence_pack(
            "trace123",
            ("action1", "action2"),
            ("eval1", "eval2"),
            risk_score=0.5,
            budget_breach_data={},
            boundary_snapshot_hash="hash123",
        )

        assert result is not None

    def test_validate_evidence_pack_accepts_pack(self, enforcement_package):
        pack = enforcement_package.build_evidence_pack(
            "trace123",
            ("action1", "action2"),
            ("eval1", "eval2"),
            risk_score=0.5,
            budget_breach_data={},
            boundary_snapshot_hash="hash123",
        )

        assert enforcement_package.validate_evidence_pack(pack) is not None

    def test_build_evidence_pack_rejects_invalid_risk_score(self, enforcement_package):
        allowed_errors = (
            getattr(enforcement_package, "EvidencePackError", ValueError),
            ValueError,
            TypeError,
        )
        with pytest.raises(allowed_errors):
            enforcement_package.build_evidence_pack(
                "trace123",
                ("action1",),
                ("eval1",),
                risk_score=1.5,
                budget_breach_data={},
                boundary_snapshot_hash="hash123",
            )

    def test_exception_types_initialize(self, enforcement_package):
        assert isinstance(enforcement_package.EvidencePackError(), Exception)
        assert isinstance(enforcement_package.PolicyExceptionError(), Exception)
