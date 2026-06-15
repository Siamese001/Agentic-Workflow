"""Tests for the ADR-061 scheduled retrieval-eval harness."""

from __future__ import annotations

import json

from tools.eval.cron_retrieval_eval import load_retrieval_cases, run_scheduled_eval


def test_load_retrieval_cases_scores_only_rows_with_retrieved_chunks(tmp_path):
    golden = tmp_path / "code.jsonl"
    golden.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "query_id": "q1",
                        "expected_chunks": ["a"],
                        "retrieved_chunks": ["a", "b"],
                    }
                ),
                json.dumps(
                    {
                        "query_id": "q2",
                        "expected_chunks": ["z"],
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    cases, rows = load_retrieval_cases(golden)

    assert rows == 2
    assert len(cases) == 1
    assert cases[0].query_id == "q1"


def test_run_scheduled_eval_writes_artifact_and_history(tmp_path):
    golden_dir = tmp_path / "golden"
    output_dir = tmp_path / "out"
    golden_dir.mkdir()
    (golden_dir / "code.jsonl").write_text(
        json.dumps(
            {
                "query_id": "q1",
                "expected_chunks": ["a"],
                "retrieved_chunks": ["x"],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result, artifact_path = run_scheduled_eval(
        golden_dir=golden_dir,
        output_dir=output_dir,
        mode="slice",
        min_recall_at_20=0.5,
    )

    assert result.scored_cases == 1
    assert result.metrics.recall_at_20 == 0.0
    assert result.failed_gates
    assert artifact_path.exists()
    assert (output_dir / "history.jsonl").exists()
