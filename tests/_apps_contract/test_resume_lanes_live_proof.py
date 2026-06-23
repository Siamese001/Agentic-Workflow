"""Live ``python -m apps_rg`` proof for Unify/IBM bullets+narrative (real bucket).

Set ``PYTEST_APPS_RG_LIVE_L2=1`` to execute. Requires external provider credentials.
"""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

import pytest

from tests._apps_contract.lane_cli_common import (
    REPO_ROOT,
    assert_live_lane_product_proof,
    run_lane_cli,
)

pytestmark = pytest.mark.skipif(
    os.environ.get("PYTEST_APPS_RG_LIVE_L2", "").strip().lower() not in ("1", "true", "yes"),
    reason="set PYTEST_APPS_RG_LIVE_L2=1 for live external provider lane proofs",
)


def _external_provider_available() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY", "").strip())


@pytest.fixture(scope="module")
def _require_external_provider() -> None:
    if not _external_provider_available():
        pytest.skip("live external_claude unavailable: ANTHROPIC_API_KEY is not set")


@pytest.fixture(scope="module")
def live_proof_bundle_dir(_require_external_provider) -> Path:
    root = REPO_ROOT / "artifacts" / "apps_rg" / "runtime_proofs" / f"live_lane_proof_{uuid.uuid4().hex[:12]}"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _run_and_assert(section: str, bundle_parent: Path) -> Path:
    art = bundle_parent / section
    art.mkdir(parents=True, exist_ok=True)
    rel = art.relative_to(REPO_ROOT).as_posix()
    proc = run_lane_cli(section, artifact_dir=rel, timeout_s=900)
    assert proc.returncode == 0, f"{section} CLI failed:\n{proc.stderr}\n{proc.stdout}"
    assert_live_lane_product_proof(art, section)
    return art


def test_live_unify_bullets(live_proof_bundle_dir: Path) -> None:
    run = _run_and_assert("unify_bullets", live_proof_bundle_dir)
    out = (run / "unify_bullets_output.txt").read_text(encoding="utf-8")
    assert "bul_unify_001" in out
    assert "without claiming" not in out.lower()


def test_live_unify_narrative(live_proof_bundle_dir: Path) -> None:
    _run_and_assert("unify_narrative", live_proof_bundle_dir)
    narr = (live_proof_bundle_dir / "unify_narrative" / "unify_narrative_output.txt").read_text(encoding="utf-8")
    assert narr.strip()
    assert "without claiming" not in narr.lower()


def test_live_ibm_bullets(live_proof_bundle_dir: Path) -> None:
    _run_and_assert("ibm_bullets", live_proof_bundle_dir)


def test_live_ibm_narrative(live_proof_bundle_dir: Path) -> None:
    _run_and_assert("ibm_narrative", live_proof_bundle_dir)
    narr = (live_proof_bundle_dir / "ibm_narrative" / "ibm_narrative_output.txt").read_text(encoding="utf-8").lower()
    assert "without claiming" not in narr
    assert "without asserting" not in narr
    assert "supported later" not in narr
