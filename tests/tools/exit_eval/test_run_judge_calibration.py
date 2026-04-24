"""Tests for the judge calibration harness."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.exit_eval.run_judge_calibration import (
    DEFAULT_DIMENSIONS,
    _FakeCalibrationJudge,
    _main,
    run_calibration,
)


@pytest.fixture
def gold_file(tmp_path: Path) -> Path:
    path = tmp_path / "gold.jsonl"
    rows = [
        {
            "item_id": "g1",
            "query": "What is 2+2?",
            "context": "Arithmetic basics",
            "answer": "4",
            "faithfulness": 5,
            "answer_relevancy": 5,
            "context_precision": 5,
            "groundedness": 5,
        },
        {
            "item_id": "g2",
            "query": "Capital of France?",
            "context": "France is in Europe",
            "answer": "Paris",
            "faithfulness": 2,
            "answer_relevancy": 5,
            "context_precision": 2,
            "groundedness": 1,
        },
        {
            "item_id": "g3",
            "query": "Side effects of Drug X?",
            "context": "",
            "answer": "generally safe",
            "faithfulness": "Unknown",
            "answer_relevancy": "Unknown",
            "context_precision": "Unknown",
            "groundedness": "Unknown",
        },
    ]
    path.write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8"
    )
    return path


class TestFakeJudge:
    def test_mirrors_human_score_with_zero_noise(self, gold_file: Path, tmp_path: Path) -> None:
        rows = [
            json.loads(line)
            for line in gold_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        gold_by_id = {r["item_id"]: r for r in rows}
        judge = _FakeCalibrationJudge(gold_by_id=gold_by_id)
        summary = run_calibration(
            judge=judge,
            judge_id="fake-test",
            gold_path=gold_file,
            outputs_path=tmp_path / "out.jsonl",
            report_path=tmp_path / "report.json",
        )
        assert summary.n_items == 3
        # Perfect kappa (1.0) on every non-Unknown dim for perfectly-mirrored judge.
        for dim in ("faithfulness", "answer_relevancy", "context_precision", "groundedness"):
            assert summary.report.dimension_kappa[dim] == 1.0

    def test_noise_reduces_kappa(self, gold_file: Path, tmp_path: Path) -> None:
        rows = [
            json.loads(line) for line in gold_file.read_text(encoding="utf-8").splitlines() if line
        ]
        # Force enough agreement mass so κ is measurable: duplicate rows with
        # varied scores so kappa != 0/1 degenerate.
        extra = tmp_path / "bigger_gold.jsonl"
        big_rows = []
        for i in range(20):
            r = dict(rows[i % 2])
            r["item_id"] = f"g{i}"
            big_rows.append(r)
        extra.write_text("\n".join(json.dumps(r) for r in big_rows), encoding="utf-8")
        gold_by_id = {r["item_id"]: r for r in big_rows}

        perfect = _FakeCalibrationJudge(gold_by_id=gold_by_id)
        noisy = _FakeCalibrationJudge(
            gold_by_id=gold_by_id,
            noise_by_dim={dim: 2 for dim in DEFAULT_DIMENSIONS},
        )
        perfect_summary = run_calibration(
            judge=perfect,
            judge_id="p",
            gold_path=extra,
            outputs_path=tmp_path / "perfect.jsonl",
            report_path=tmp_path / "perfect_report.json",
        )
        noisy_summary = run_calibration(
            judge=noisy,
            judge_id="n",
            gold_path=extra,
            outputs_path=tmp_path / "noisy.jsonl",
            report_path=tmp_path / "noisy_report.json",
        )
        for dim in DEFAULT_DIMENSIONS:
            # Noisy judge scores clamp to [1,5]; kappa should drop vs perfect.
            p_k = perfect_summary.report.dimension_kappa[dim]
            n_k = noisy_summary.report.dimension_kappa[dim]
            assert n_k <= p_k

    def test_unknown_mirroring(self, gold_file: Path, tmp_path: Path) -> None:
        rows = [
            json.loads(line) for line in gold_file.read_text(encoding="utf-8").splitlines() if line
        ]
        gold_by_id = {r["item_id"]: r for r in rows}
        judge = _FakeCalibrationJudge(gold_by_id=gold_by_id, abstain_on_unknown=True)
        summary = run_calibration(
            judge=judge,
            judge_id="fake",
            gold_path=gold_file,
            outputs_path=tmp_path / "out.jsonl",
            report_path=tmp_path / "report.json",
        )
        # g3 is Unknown on every dim → unknown_rate = 1/3 per dim.
        # Report rounds to 4 decimals (0.3333), compare with matching tolerance.
        for dim in DEFAULT_DIMENSIONS:
            assert summary.report.unknown_rate_by_dim[dim] == pytest.approx(
                1 / 3, abs=1e-4
            )

    def test_abstains_on_missing_item(self, gold_file: Path) -> None:
        judge = _FakeCalibrationJudge(gold_by_id={})
        from agentic_core.L3_orchestration.exit_eval.dimension import (
            Dimension,
            GraderClass,
        )

        dim = Dimension(
            name="faithfulness",
            grader_class=GraderClass.MODEL_BASED,
            threshold=0.6,
            weight=1.0,
            abstain_allowed=True,
        )
        response = judge.judge(dim, context={"item_id": "never-saw-this"})
        assert response.abstain


class TestHarnessEdgeCases:
    def test_empty_gold_raises(self, tmp_path: Path) -> None:
        empty = tmp_path / "empty.jsonl"
        empty.write_text("", encoding="utf-8")
        judge = _FakeCalibrationJudge(gold_by_id={})
        with pytest.raises(ValueError, match="gold set is empty"):
            run_calibration(
                judge=judge,
                judge_id="x",
                gold_path=empty,
                outputs_path=tmp_path / "out.jsonl",
                report_path=tmp_path / "r.json",
            )

    def test_missing_gold_file_raises(self, tmp_path: Path) -> None:
        judge = _FakeCalibrationJudge(gold_by_id={})
        with pytest.raises(FileNotFoundError):
            run_calibration(
                judge=judge,
                judge_id="x",
                gold_path=tmp_path / "nope.jsonl",
            )

    def test_malformed_gold_row_raises(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.jsonl"
        bad.write_text("not-json\n", encoding="utf-8")
        judge = _FakeCalibrationJudge(gold_by_id={})
        with pytest.raises(ValueError, match="invalid JSON"):
            run_calibration(
                judge=judge,
                judge_id="x",
                gold_path=bad,
            )


class TestCLI:
    def test_fake_run_succeeds(self, gold_file: Path, tmp_path: Path) -> None:
        rc = _main(
            [
                "--judge",
                "fake",
                "--gold",
                str(gold_file),
                "--outputs",
                str(tmp_path / "out.jsonl"),
                "--report",
                str(tmp_path / "r.json"),
            ]
        )
        assert rc == 0
        assert (tmp_path / "out.jsonl").exists()
        assert (tmp_path / "r.json").exists()

    def test_min_kappa_gate_passes_on_perfect(
        self, gold_file: Path, tmp_path: Path
    ) -> None:
        rc = _main(
            [
                "--judge",
                "fake",
                "--gold",
                str(gold_file),
                "--outputs",
                str(tmp_path / "out.jsonl"),
                "--report",
                str(tmp_path / "r.json"),
                "--min-kappa",
                "0.9",
            ]
        )
        assert rc == 0

    def test_min_kappa_gate_fails_when_kappa_below(
        self, gold_file: Path, tmp_path: Path
    ) -> None:
        rc = _main(
            [
                "--judge",
                "fake",
                "--gold",
                str(gold_file),
                "--outputs",
                str(tmp_path / "out.jsonl"),
                "--report",
                str(tmp_path / "r.json"),
                "--fake-noise",
                "3",
                "--min-kappa",
                "0.9",
            ]
        )
        # Noise 3 pushes kappa below 0.9 → exit 3.
        assert rc == 3

    def test_invalid_judge_kind_rejected(self, gold_file: Path) -> None:
        with pytest.raises(SystemExit):
            _main(["--judge", "nonexistent", "--gold", str(gold_file)])
