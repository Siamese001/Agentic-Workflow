"""Guarded proof bundle for modular R4 SSOT (local artifacts; skips if missing)."""

from __future__ import annotations

import pytest

from apps_rg.l2_recipe.r4_modular_proof_verification import (
    R4_RECORDED_MODULAR_PROOF_RUN_ID,
    verify_recorded_modular_r4_proof_bundle,
)
from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root


def test_recorded_modular_r4_proof_bundle_passes() -> None:
    repo = find_repo_root()
    run_dir = repo / "artifacts" / "apps_rg" / "runs" / R4_RECORDED_MODULAR_PROOF_RUN_ID
    if not run_dir.is_dir():
        pytest.skip(f"recorded proof run not present: {run_dir.as_posix()}")

    errs = verify_recorded_modular_r4_proof_bundle(repo_root=repo)
    assert errs == [], errs
