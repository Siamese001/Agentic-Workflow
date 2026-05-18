"""W10b — R1B UWG receipt contract parity contract tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "artifacts" / "apps_rg" / "r1b_semantic_cache" / "w10b_fixtures"


@pytest.fixture(scope="module", autouse=True)
def _ensure_w10b_fixtures() -> None:
    if not (FIXTURES / "admitted_receipt_with_l5.json").is_file():
        import subprocess
        import sys

        subprocess.run(
            [sys.executable, str(REPO_ROOT / "tools" / "apps_rg" / "emit_r1b_w10b_fixtures.py")],
            check=True,
            cwd=str(REPO_ROOT),
        )


def test_w10b_fixtures_present() -> None:
    for name in (
        "admitted_receipt_with_l5",
        "blocked_missing_l5",
        "blocked_missing_gate_verdict",
        "receipt_field_parity_matrix",
        "shim_vs_core_gap",
        "file_backed_non_durable_manifest",
    ):
        assert (FIXTURES / f"{name}.json").is_file(), name


def test_admitted_fixture_has_l5_and_gate() -> None:
    payload = json.loads((FIXTURES / "admitted_receipt_with_l5.json").read_text(encoding="utf-8"))
    gov = payload["governance_receipt"]
    assert gov["l5_certification_ref"]
    assert gov["gate_verdict_refs"]
    assert gov["source_surface"] == "Exit"


def test_blocked_missing_l5_fixture() -> None:
    payload = json.loads((FIXTURES / "blocked_missing_l5.json").read_text(encoding="utf-8"))
    assert payload["status"] == "BLOCKED"
    assert "l5_certification_ref" in payload["missing_contract_fields"]


def test_blocked_missing_gate_fixture() -> None:
    payload = json.loads((FIXTURES / "blocked_missing_gate_verdict.json").read_text(encoding="utf-8"))
    assert payload["status"] == "BLOCKED"
    assert "gate_verdict_refs" in payload["missing_contract_fields"]


def test_shim_core_gap_fixture() -> None:
    payload = json.loads((FIXTURES / "shim_vs_core_gap.json").read_text(encoding="utf-8"))
    assert "gate_verdict_refs" in payload["fields_core_cannot_carry"]
    assert "l5_certification_ref" in payload["fields_shim_patches"]
