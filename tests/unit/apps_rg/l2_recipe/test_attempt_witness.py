"""apps-test-model: APP CONTRACT.

Attempt-witness aggregation for the apps_rg L2 recipe.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.l2_recipe.attempt_witness import build_runtime_execution_witness


def test_build_runtime_execution_witness_counts_distinct_attempts(tmp_path: Path) -> None:
    section = tmp_path / "lanes" / "executive_summary"
    section.mkdir(parents=True)
    (section / "judge_attempt_ledger.json").write_text(
        json.dumps(
            {
                "schema_version": "apps_rg.judge_attempt_ledger.v1",
                "attempts": [
                    {"provider_key": "anthropic_claude", "attempt": 1},
                    {"provider_key": "anthropic_claude", "attempt": 2},
                ],
            }
        ),
        encoding="utf-8",
    )
    (section / "provider_response.json").write_text(
        json.dumps(
            {
                "provider_attempt_spans": [
                    {"attempt_id": "provider-1"},
                    {"attempt_id": "provider-2"},
                ]
            }
        ),
        encoding="utf-8",
    )

    witness = build_runtime_execution_witness(
        artifact_dir=tmp_path,
        step_results=[],
        context={},
    )

    assert witness["generation_provider_attempt_count"] == 2
    assert witness["judge_attempt_count"] == 2
    assert witness["attempt_evidence_status"] == "COMPLETE"
    assert len(witness["attempt_evidence_refs"]) == 2


def test_build_runtime_execution_witness_rejects_noncontiguous_judge_attempts(
    tmp_path: Path,
) -> None:
    section = tmp_path / "lanes" / "competencies"
    section.mkdir(parents=True)
    (section / "judge_attempt_ledger.json").write_text(
        json.dumps(
            {
                "schema_version": "apps_rg.judge_attempt_ledger.v1",
                "attempts": [
                    {"provider_key": "gemini_pro", "attempt": 1},
                    {"provider_key": "gemini_pro", "attempt": 3},
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="noncontiguous"):
        build_runtime_execution_witness(
            artifact_dir=tmp_path,
            step_results=[],
            context={},
        )
