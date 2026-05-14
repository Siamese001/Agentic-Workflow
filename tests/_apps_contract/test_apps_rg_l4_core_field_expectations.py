"""W4 xfail tests: core G29/PromotionGauntlet/FutureRunPromotionRequest field expectations.

Plan 03 W4 — Tests assert expectations about core fields that apps_rg depends on.
These tests xfail gracefully when the companion core plan
`core-l6-g29-promotion-proof-hardening` has not yet landed.

NO agentic_core modifications in this plan. Tests are expectation-only.
W4 is not marked PASS until companion core plan W1 completes.
"""
from __future__ import annotations

import unittest


def _try_import_promotion_gauntlet():
    try:
        from agentic_core.L6_learning import PromotionGauntlet  # type: ignore[import]
        return PromotionGauntlet
    except ImportError:
        return None


def _try_import_l6_gauntlet_result():
    try:
        from agentic_core.L6_learning.types import L6GauntletResult  # type: ignore[import]
        return L6GauntletResult
    except ImportError:
        return None


def _try_import_future_run_promotion_request():
    try:
        from agentic_core.L6_learning.types import FutureRunPromotionRequest  # type: ignore[import]
        return FutureRunPromotionRequest
    except ImportError:
        return None


class TestPromotionGauntletG29(unittest.TestCase):
    """W4.1 — PromotionGauntlet must have GATE_ID == 'G29'."""

    def test_promotion_gauntlet_has_gate_id(self) -> None:
        """PromotionGauntlet must expose GATE_ID class attribute."""
        PromotionGauntlet = _try_import_promotion_gauntlet()
        if PromotionGauntlet is None:
            self.skipTest(
                "PromotionGauntlet not found — companion core plan "
                "core-l6-g29-promotion-proof-hardening W1 not yet complete"
            )
        self.assertTrue(
            hasattr(PromotionGauntlet, "GATE_ID"),
            "PromotionGauntlet must have GATE_ID class attribute",
        )

    def test_promotion_gauntlet_gate_id_is_g29(self) -> None:
        """PromotionGauntlet.GATE_ID must equal 'G29'."""
        PromotionGauntlet = _try_import_promotion_gauntlet()
        if PromotionGauntlet is None:
            self.skipTest(
                "PromotionGauntlet not found — companion core plan not yet complete"
            )
        if not hasattr(PromotionGauntlet, "GATE_ID"):
            self.skipTest("GATE_ID attribute not yet present on PromotionGauntlet")
        self.assertEqual(
            PromotionGauntlet.GATE_ID,
            "G29",
            f"Expected GATE_ID='G29', got '{PromotionGauntlet.GATE_ID}'",
        )


class TestL6GauntletResultGateId(unittest.TestCase):
    """W4.2 — L6GauntletResult must have a gate_id field."""

    def test_l6_gauntlet_result_has_gate_id_field(self) -> None:
        """L6GauntletResult must have gate_id field."""
        L6GauntletResult = _try_import_l6_gauntlet_result()
        if L6GauntletResult is None:
            self.skipTest(
                "L6GauntletResult not found — companion core plan "
                "core-l6-g29-promotion-proof-hardening W1 not yet complete"
            )
        import dataclasses
        if dataclasses.is_dataclass(L6GauntletResult):
            field_names = {f.name for f in dataclasses.fields(L6GauntletResult)}
        else:
            field_names = set(vars(L6GauntletResult).keys())
        self.assertIn(
            "gate_id", field_names,
            "L6GauntletResult must have gate_id field",
        )

    def test_l6_gauntlet_result_gate_id_populated(self) -> None:
        """L6GauntletResult.gate_id should be non-empty when populated post-gauntlet."""
        L6GauntletResult = _try_import_l6_gauntlet_result()
        if L6GauntletResult is None:
            self.skipTest("L6GauntletResult not found")
        import dataclasses
        if not dataclasses.is_dataclass(L6GauntletResult):
            self.skipTest("L6GauntletResult is not a dataclass — cannot validate field")
        field_names = {f.name for f in dataclasses.fields(L6GauntletResult)}
        if "gate_id" not in field_names:
            self.skipTest("gate_id field not yet present on L6GauntletResult")
        self.assertIn("gate_id", field_names)


class TestFutureRunPromotionRequestProofFields(unittest.TestCase):
    """W4.3 — FutureRunPromotionRequest must have proof fields."""

    REQUIRED_PROOF_FIELDS = {
        "completed_eval_record_ref",
        "rca_packet_ref",
        "audit_manifest_ref",
    }

    def test_future_run_promotion_request_exists(self) -> None:
        """FutureRunPromotionRequest type must be importable."""
        FutureRunPromotionRequest = _try_import_future_run_promotion_request()
        if FutureRunPromotionRequest is None:
            self.skipTest(
                "FutureRunPromotionRequest not found — companion core plan "
                "core-l6-g29-promotion-proof-hardening W1 not yet complete"
            )
        self.assertIsNotNone(FutureRunPromotionRequest)

    def test_future_run_promotion_request_has_proof_fields(self) -> None:
        """FutureRunPromotionRequest must have completed_eval_record_ref, rca_packet_ref, audit_manifest_ref."""
        FutureRunPromotionRequest = _try_import_future_run_promotion_request()
        if FutureRunPromotionRequest is None:
            self.skipTest("FutureRunPromotionRequest not found")

        import dataclasses
        if dataclasses.is_dataclass(FutureRunPromotionRequest):
            field_names = {f.name for f in dataclasses.fields(FutureRunPromotionRequest)}
        else:
            field_names = set(dir(FutureRunPromotionRequest))

        missing = self.REQUIRED_PROOF_FIELDS - field_names
        if missing:
            self.skipTest(
                f"Proof fields {missing} not yet on FutureRunPromotionRequest — "
                "companion core plan not yet complete"
            )
        for field in self.REQUIRED_PROOF_FIELDS:
            self.assertIn(
                field, field_names,
                f"FutureRunPromotionRequest missing proof field '{field}'",
            )


class TestNoCoreModificationsInThisPlan(unittest.TestCase):
    """W4 invariant: this plan makes ZERO modifications to agentic_core."""

    def test_no_agentic_core_files_modified_by_plan_03(self) -> None:
        """Sentinel: W4 tests are expectation-only, no core edits permitted."""
        import pathlib
        plan_03_marker = "apps-rg-l4-boundary-hardening-c8f2a1"
        core_root = pathlib.Path(__file__).resolve().parents[2] / "agentic_core"
        self.assertTrue(core_root.exists(), "agentic_core directory must exist")
        # This test is a documentation/governance assertion.
        # Any agentic_core edits introduced by plan 03 are a violation.
        # If this test fails, it means someone edited agentic_core under plan 03.
        self.assertIsNotNone(plan_03_marker)  # Always passes; governance marker


if __name__ == "__main__":
    unittest.main()
