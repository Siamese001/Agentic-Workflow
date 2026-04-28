"""Shared fixtures for apps_proof tests.

Provides a ``proof_dir`` fixture pointing at the most-recent passing run
for ``apps_underwriting_ai`` (the Phase 1 first-slice app). If no run
exists, the fixture loudly fails — tests are NOT skipped (constitutional
§1: no test skipping).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
PROOF_ROOT = REPO / "artifacts" / "apps_proof"


def _latest_run(app_name: str) -> Path | None:
    app_dir = PROOF_ROOT / app_name
    if not app_dir.exists():
        return None
    runs = [d for d in app_dir.iterdir() if d.is_dir() and not d.name.startswith("_")]
    if not runs:
        return None
    return max(runs, key=lambda d: d.stat().st_mtime)


@pytest.fixture(scope="session")
def proof_dir() -> Path:
    """Latest passing run dir for apps_underwriting_ai. Fails loudly if missing."""
    p = _latest_run("apps_underwriting_ai")
    if p is None:
        pytest.fail(
            "No proof run exists at "
            f"{PROOF_ROOT / 'apps_underwriting_ai'}. Run "
            "`python -m tools.apps_proof.run_app_proof --app apps_underwriting_ai "
            "--fixture tests/fixtures/apps_underwriting_ai/golden_borrower_package.json "
            "--require-otel --require-replay --require-adg` first."
        )
    return p


@pytest.fixture(scope="session")
def run_manifest(proof_dir: Path) -> dict:
    """Loaded run_manifest.json for the current run."""
    body = json.loads((proof_dir / "run_manifest.json").read_text(encoding="utf-8"))
    return body


@pytest.fixture(scope="session")
def otel_trace(proof_dir: Path) -> list[dict]:
    """Loaded OTEL trace export (list of span dicts)."""
    body = json.loads((proof_dir / "trace" / "otel_trace.json").read_text(encoding="utf-8"))
    assert isinstance(body, list)
    return body


@pytest.fixture(scope="session")
def proof_verdict(proof_dir: Path) -> dict:
    """Loaded proof_verdict.json — should report PASS."""
    body = json.loads((proof_dir / "verifier" / "proof_verdict.json").read_text(encoding="utf-8"))
    return body
