"""W0 contract test: pin the AIG E2E regression fixtures (JD + briefing).

These two files are the targeting inputs for the apps_rg AIG E2E remediation. Pinning
their sha256 guards against silent drift of the regression baseline -- if either file
changes, this test fails and the plan's evidence chain must be re-validated.
(apps_rg AIG E2E remediation, Wave 0.)
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

# sha256 pinned 2026-06-07 against the AIG VP Global Head of Agentic AI inputs.
AIG_FIXTURES = {
    "apps_rg/config/targeting/aig_vp_global_head_agentic_ai_jd.txt":
        "32c1cb8010ee31e6a6479a1d36a65561f590f033a832acc650b38bee4259b8fc",
    "apps_rg/config/targeting/aig_vp_global_head_agentic_ai_briefing.md":
        "8703d22fded0466c170f0a7997fef14b905040476c4f17222e04bcc37f990a65",
}


@pytest.mark.parametrize("rel_path, expected_sha", sorted(AIG_FIXTURES.items()))
def test_aig_fixture_exists_and_pinned(rel_path: str, expected_sha: str):
    path = REPO_ROOT / rel_path
    assert path.is_file(), f"missing AIG E2E fixture: {rel_path}"
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    assert actual == expected_sha, (
        f"AIG E2E fixture drift for {rel_path}: expected {expected_sha}, got {actual}. "
        "If this change is intentional, re-pin the hash and re-validate the remediation evidence."
    )
