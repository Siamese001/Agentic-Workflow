from __future__ import annotations

import json
from pathlib import Path

from tools.eval.x2_micro_eval import REQUIRED_FAMILIES, evaluate_fixture, evaluate_suite, load_fixtures


def _fixture(family: str, *, expected: str = "BLOCK", hard_pass: bool = False) -> dict:
    return {
        "fixture_id": f"fixture-{family}",
        "family": family,
        "expected_disposition": expected,
        "required_gate_ids": [f"x2_{family}_gate"],
        "gate_observations": [
            {
                "gate_id": f"x2_{family}_gate",
                "pass": hard_pass,
                "severity": "hard",
            }
        ],
    }


def test_canonical_fixture_file_covers_all_required_families() -> None:
    fixtures = load_fixtures(Path("data/eval/x2_micro"))
    result = evaluate_suite(fixtures)

    assert result.passed is True
    assert result.missing_required_families == []
    assert {r.family for r in result.results} == set(REQUIRED_FAMILIES)


def test_expected_block_fails_closed_when_no_hard_gate_fails() -> None:
    result = evaluate_fixture(_fixture("numeric_precision", hard_pass=True))

    assert result.passed is False
    assert result.observed_disposition == "ALLOW"
    assert "EXPECTED_BLOCK_NOT_TRIGGERED" in result.reason_codes


def test_allow_fixture_fails_on_unexpected_hard_failure() -> None:
    result = evaluate_fixture(_fixture("mock_not_allowed", expected="ALLOW", hard_pass=False))

    assert result.passed is False
    assert result.observed_disposition == "BLOCK"
    assert "UNEXPECTED_HARD_FAILURE" in result.reason_codes


def test_suite_reports_missing_required_family(tmp_path: Path) -> None:
    fixture_path = tmp_path / "fixtures.json"
    fixture_path.write_text(json.dumps([_fixture("numeric_precision")]), encoding="utf-8")

    result = evaluate_suite(load_fixtures(fixture_path))

    assert result.passed is False
    assert "mock_not_allowed" in result.missing_required_families
