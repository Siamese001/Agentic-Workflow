"""SP-005: retired prove_apps_rg harness; CI boundary helper is not product cert."""
from __future__ import annotations

from pathlib import Path

from apps_rg.runtime.non_product_proof_stamp import CI_LANE_DEV_HARNESS_CLASSIFICATION


def test_prove_apps_rg_e2e_runtime_physically_deleted() -> None:
    path = (
        Path(__file__).resolve().parents[3]
        / "ops_scripts"
        / "ci"
        / "prove_apps_rg_e2e_runtime.py"
    )
    assert not path.is_file()


def test_ci_lane_dev_boundary_classification_not_product_cert() -> None:
    assert CI_LANE_DEV_HARNESS_CLASSIFICATION == "LANE_DEV_HARNESS"
