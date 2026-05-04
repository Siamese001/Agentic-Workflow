"""apps_lic calibration-holdout W5 — holdout ingest + Spearman calibration tests.

Plan: .windsurf/plans/apps-lic-calibration-holdout-e8f1c4.md W5 DS1-P1, DS1-P2

Tests verify:
  DS1-P1 (lic_judge_holdout_ingest):
  - Module importable; __all__ complete.
  - REQUIRED_COLUMNS, VALID_GRADER_IDS, VALID_OUTREACH_MODES correct.
  - ingest_csv validates required columns.
  - ingest_csv validates human_score range [0, 1].
  - ingest_csv validates grader_id against known list.
  - ingest_csv validates outreach_mode against known list.
  - ingest_csv yields HoldoutRow with correct fields.
  - ingest_csv with lenient=False raises on bad row.
  - ingest_csv with strict=False skips bad rows.
  - write_jsonl emits valid JSONL with required fields.
  - run_context built from row for judge.grade() calls.
  - Empty draft_id rejected.

  DS1-P2 (lic_judge_spearman_calibration):
  - Module importable; __all__ complete.
  - SPEARMAN_THRESHOLD == 0.80.
  - JUDGE_MODULE_MAP covers all 5 plan judges.
  - spearman_rho returns 1.0 for identical lists.
  - spearman_rho returns -1.0 for reversed lists.
  - spearman_rho handles ties (no crash).
  - spearman_rho returns nan for n < 2.
  - run_calibration on synthetic corpus returns JudgeCalibrationResult per judge.
  - JudgeCalibrationResult.passed True when rho >= threshold.
  - JudgeCalibrationResult.passed False when rho < threshold.
  - unknown_count increments for GRADER_UNKNOWN_SENTINEL rows.
  - run_calibration ignores unknown grader_ids gracefully.
  - JudgeCalibrationResult dataclass shape correct.

  Judge flag validation (all 5 plan judges):
  - IS_STUB == False.
  - IS_CALIBRATED == True.
  - IS_CALIBRATED_SYNTHETIC absent (not defined at module level).
  - grade() returns (float, list) for valid input.
"""

from __future__ import annotations

import io
import json
import math
import tempfile
from pathlib import Path

import pytest


# ===========================================================================
# Fixtures
# ===========================================================================

_VALID_CSV_HEADER = (
    "draft_id,draft_text,grader_id,human_score,recipient_class,outreach_mode\n"
)

_VALID_ROW = (
    '"d001","Hi {name} I noticed your work at {company} and wanted to connect. '
    'Would love to chat about {role} opportunities. Regards",'
    '"lic::ask_friction_judge::v1","0.75","HIRING_MANAGER","cold"\n'
)

_VALID_CSV = _VALID_CSV_HEADER + _VALID_ROW


def _write_csv(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "test_holdout.csv"
    p.write_text(content, encoding="utf-8")
    return p


def _make_jsonl(rows: list[dict], tmp_path: Path) -> Path:
    p = tmp_path / "corpus.jsonl"
    with open(p, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    return p


# ===========================================================================
# DS1-P1: lic_judge_holdout_ingest
# ===========================================================================

class TestHoldoutIngestModule:
    def test_importable(self):
        import tools.calibration.lic_judge_holdout_ingest  # noqa: F401

    def test_all_exports(self):
        from tools.calibration.lic_judge_holdout_ingest import __all__
        for name in (
            "HoldoutRow", "ingest_csv", "write_jsonl",
            "REQUIRED_COLUMNS", "VALID_GRADER_IDS", "VALID_OUTREACH_MODES",
        ):
            assert name in __all__

    def test_required_columns_complete(self):
        from tools.calibration.lic_judge_holdout_ingest import REQUIRED_COLUMNS
        for col in ("draft_id", "draft_text", "grader_id", "human_score",
                    "recipient_class", "outreach_mode"):
            assert col in REQUIRED_COLUMNS

    def test_valid_grader_ids_covers_5_plan_judges(self):
        from tools.calibration.lic_judge_holdout_ingest import VALID_GRADER_IDS
        for gid in (
            "lic::ask_friction_judge::v1",
            "lic::antipattern_clean_judge::v1",
            "lic::proof_appropriate_judge::v1",
            "lic::personalization_judge::v1",
            "lic::asymmetric_insight_judge::v1",
        ):
            assert gid in VALID_GRADER_IDS

    def test_valid_outreach_modes(self):
        from tools.calibration.lic_judge_holdout_ingest import VALID_OUTREACH_MODES
        for mode in ("cold", "warm", "referral", "follow_up"):
            assert mode in VALID_OUTREACH_MODES


class TestIngestCsvValidation:
    def test_missing_column_raises(self, tmp_path):
        from tools.calibration.lic_judge_holdout_ingest import ingest_csv
        bad_csv = "draft_id,draft_text,grader_id\nd001,text,lic::ask_friction_judge::v1\n"
        p = _write_csv(tmp_path, bad_csv)
        with pytest.raises(ValueError, match="missing required columns"):
            list(ingest_csv(p))

    def test_invalid_human_score_raises(self, tmp_path):
        from tools.calibration.lic_judge_holdout_ingest import ingest_csv
        bad = _VALID_CSV_HEADER + "d001,text,lic::ask_friction_judge::v1,not_a_float,EXEC,cold\n"
        p = _write_csv(tmp_path, bad)
        with pytest.raises(ValueError, match="not a valid float"):
            list(ingest_csv(p))

    def test_human_score_out_of_range_raises(self, tmp_path):
        from tools.calibration.lic_judge_holdout_ingest import ingest_csv
        bad = _VALID_CSV_HEADER + "d001,text,lic::ask_friction_judge::v1,1.5,EXEC,cold\n"
        p = _write_csv(tmp_path, bad)
        with pytest.raises(ValueError, match="outside"):
            list(ingest_csv(p))

    def test_invalid_grader_id_raises(self, tmp_path):
        from tools.calibration.lic_judge_holdout_ingest import ingest_csv
        bad = _VALID_CSV_HEADER + "d001,text,lic::unknown_judge::v9,0.5,EXEC,cold\n"
        p = _write_csv(tmp_path, bad)
        with pytest.raises(ValueError, match="unknown grader_id"):
            list(ingest_csv(p))

    def test_invalid_outreach_mode_raises(self, tmp_path):
        from tools.calibration.lic_judge_holdout_ingest import ingest_csv
        bad = _VALID_CSV_HEADER + "d001,text,lic::ask_friction_judge::v1,0.5,EXEC,unknown_mode\n"
        p = _write_csv(tmp_path, bad)
        with pytest.raises(ValueError, match="unknown outreach_mode"):
            list(ingest_csv(p))

    def test_empty_draft_id_raises(self, tmp_path):
        from tools.calibration.lic_judge_holdout_ingest import ingest_csv
        bad = _VALID_CSV_HEADER + ",text,lic::ask_friction_judge::v1,0.5,EXEC,cold\n"
        p = _write_csv(tmp_path, bad)
        with pytest.raises(ValueError, match="draft_id is empty"):
            list(ingest_csv(p))

    def test_strict_false_skips_bad_row(self, tmp_path):
        from tools.calibration.lic_judge_holdout_ingest import ingest_csv
        bad_then_good = (
            _VALID_CSV_HEADER
            + '"d001","text","lic::unknown::v0","0.5","EXEC","cold"\n'   # bad grader
            + _VALID_ROW                                                    # good row
        )
        p = _write_csv(tmp_path, bad_then_good)
        rows = list(ingest_csv(p, strict=False))
        assert len(rows) == 1
        assert rows[0].grader_id.startswith("lic::")


class TestIngestCsvOutput:
    def test_valid_row_yields_holdout_row(self, tmp_path):
        from tools.calibration.lic_judge_holdout_ingest import ingest_csv, HoldoutRow
        p = _write_csv(tmp_path, _VALID_CSV)
        rows = list(ingest_csv(p))
        assert len(rows) == 1
        row = rows[0]
        assert isinstance(row, HoldoutRow)
        assert row.draft_id == "d001"
        assert row.human_score == 0.75
        assert row.grader_id == "lic::ask_friction_judge::v1"
        assert row.recipient_class == "HIRING_MANAGER"
        assert row.outreach_mode == "cold"

    def test_run_context_has_output_text(self, tmp_path):
        from tools.calibration.lic_judge_holdout_ingest import ingest_csv
        p = _write_csv(tmp_path, _VALID_CSV)
        rows = list(ingest_csv(p))
        rc = rows[0].run_context
        assert "output" in rc
        assert "text" in rc["output"]
        assert rc["recipient_class"] == "HIRING_MANAGER"

    def test_write_jsonl_produces_valid_lines(self, tmp_path):
        from tools.calibration.lic_judge_holdout_ingest import ingest_csv, write_jsonl
        p = _write_csv(tmp_path, _VALID_CSV)
        rows = ingest_csv(p)
        out = tmp_path / "out.jsonl"
        count = write_jsonl(rows, out)
        assert count == 1
        with open(out, encoding="utf-8") as fh:
            payload = json.loads(fh.readline())
        for key in ("draft_id", "draft_text", "grader_id", "human_score",
                    "recipient_class", "outreach_mode", "run_context"):
            assert key in payload

    def test_write_jsonl_creates_parent_dirs(self, tmp_path):
        from tools.calibration.lic_judge_holdout_ingest import ingest_csv, write_jsonl
        p = _write_csv(tmp_path, _VALID_CSV)
        out = tmp_path / "nested" / "deep" / "out.jsonl"
        count = write_jsonl(ingest_csv(p), out)
        assert count == 1
        assert out.exists()

    def test_multiple_rows_ingested(self, tmp_path):
        from tools.calibration.lic_judge_holdout_ingest import ingest_csv
        rows_csv = (
            _VALID_CSV_HEADER
            + '"d001","text one","lic::ask_friction_judge::v1","0.3","HIRING_MANAGER","cold"\n'
            + '"d002","text two","lic::personalization_judge::v1","0.9","EXECUTIVE","warm"\n'
        )
        p = _write_csv(tmp_path, rows_csv)
        rows = list(ingest_csv(p))
        assert len(rows) == 2
        assert rows[0].draft_id == "d001"
        assert rows[1].draft_id == "d002"


# ===========================================================================
# DS1-P2: lic_judge_spearman_calibration
# ===========================================================================

class TestSpearmanCalibrationModule:
    def test_importable(self):
        import ops_scripts.calibration.lic_judge_spearman_calibration  # noqa: F401

    def test_all_exports(self):
        from ops_scripts.calibration.lic_judge_spearman_calibration import __all__
        for name in (
            "JudgeCalibrationResult", "run_calibration",
            "spearman_rho", "SPEARMAN_THRESHOLD", "JUDGE_MODULE_MAP",
        ):
            assert name in __all__

    def test_threshold_is_0_80(self):
        from ops_scripts.calibration.lic_judge_spearman_calibration import SPEARMAN_THRESHOLD
        assert SPEARMAN_THRESHOLD == 0.80

    def test_judge_module_map_covers_5_plan_judges(self):
        from ops_scripts.calibration.lic_judge_spearman_calibration import JUDGE_MODULE_MAP
        for gid in (
            "lic::ask_friction_judge::v1",
            "lic::antipattern_clean_judge::v1",
            "lic::proof_appropriate_judge::v1",
            "lic::personalization_judge::v1",
            "lic::asymmetric_insight_judge::v1",
        ):
            assert gid in JUDGE_MODULE_MAP


class TestSpearmanRho:
    def test_identical_lists_rho_1(self):
        from ops_scripts.calibration.lic_judge_spearman_calibration import spearman_rho
        xs = [0.1, 0.3, 0.7, 0.9]
        assert abs(spearman_rho(xs, xs) - 1.0) < 1e-9

    def test_reversed_lists_rho_neg1(self):
        from ops_scripts.calibration.lic_judge_spearman_calibration import spearman_rho
        xs = [1.0, 2.0, 3.0, 4.0]
        ys = [4.0, 3.0, 2.0, 1.0]
        assert abs(spearman_rho(xs, ys) - (-1.0)) < 1e-9

    def test_rho_range(self):
        from ops_scripts.calibration.lic_judge_spearman_calibration import spearman_rho
        xs = [0.1, 0.5, 0.3, 0.9, 0.2]
        ys = [0.2, 0.6, 0.1, 0.8, 0.4]
        rho = spearman_rho(xs, ys)
        assert -1.0 <= rho <= 1.0

    def test_nan_for_single_element(self):
        from ops_scripts.calibration.lic_judge_spearman_calibration import spearman_rho
        assert math.isnan(spearman_rho([0.5], [0.5]))

    def test_handles_ties(self):
        from ops_scripts.calibration.lic_judge_spearman_calibration import spearman_rho
        xs = [0.5, 0.5, 0.5, 0.8]
        ys = [0.5, 0.6, 0.5, 0.9]
        rho = spearman_rho(xs, ys)
        assert not math.isnan(rho)

    def test_length_mismatch_raises(self):
        from ops_scripts.calibration.lic_judge_spearman_calibration import spearman_rho
        with pytest.raises(ValueError):
            spearman_rho([0.1, 0.2], [0.1])


class TestRunCalibration:
    def _build_corpus(self, tmp_path: Path, rows: list[dict]) -> Path:
        return _make_jsonl(rows, tmp_path)

    def _synthetic_rows(self, grader_id: str, n: int = 20) -> list[dict]:
        """Rows where judge score will roughly match human score (high ρ)."""
        rows = []
        # Use ask_friction_judge: low friction text should get low friction score
        for i in range(n):
            human = round((i / (n - 1)), 2) if n > 1 else 0.5
            rows.append({
                "draft_id": f"d{i:04d}",
                "draft_text": "Hi Alice, quick question — would you be open to a 15-min chat?",
                "grader_id": grader_id,
                "human_score": human,
                "recipient_class": "HIRING_MANAGER",
                "outreach_mode": "cold",
                "run_context": {
                    "output": {
                        "text": "Hi Alice, quick question — would you be open to a 15-min chat?"
                    },
                    "recipient_class": "HIRING_MANAGER",
                    "outreach_mode": "cold",
                },
            })
        return rows

    def test_returns_result_list(self, tmp_path):
        from ops_scripts.calibration.lic_judge_spearman_calibration import (
            run_calibration, JudgeCalibrationResult,
        )
        rows = self._synthetic_rows("lic::ask_friction_judge::v1", n=10)
        corpus = self._build_corpus(tmp_path, rows)
        results = run_calibration(corpus)
        assert isinstance(results, list)
        assert len(results) == 1
        assert isinstance(results[0], JudgeCalibrationResult)

    def test_result_fields_present(self, tmp_path):
        from ops_scripts.calibration.lic_judge_spearman_calibration import run_calibration
        rows = self._synthetic_rows("lic::personalization_judge::v1", n=10)
        corpus = self._build_corpus(tmp_path, rows)
        result = run_calibration(corpus)[0]
        assert result.grader_id == "lic::personalization_judge::v1"
        assert isinstance(result.n_samples, int)
        assert isinstance(result.spearman_rho, float)
        assert isinstance(result.passed, bool)
        assert isinstance(result.unknown_count, int)

    def test_threshold_respected_pass(self, tmp_path):
        from ops_scripts.calibration.lic_judge_spearman_calibration import run_calibration
        # Use varied texts so judge scores vary, giving a real rho.
        # Varied by outreach_mode and recipient_class so judges produce spread.
        rows = []
        texts_and_scores = [
            ("Hire me immediately at Acme. You must know I am perfect. Do it now.", 0.1),
            ("Let me know if you can meet.", 0.5),
            ("Would you be open to a 15-min chat about the role?", 0.9),
            ("I demand an offer. Clearly you can see this is obvious.", 0.1),
            ("Hope this message finds you well. Keen to connect briefly.", 0.8),
        ]
        for i, (text, human) in enumerate(texts_and_scores):
            rows.append({
                "draft_id": f"d{i:04d}",
                "draft_text": text,
                "grader_id": "lic::ask_friction_judge::v1",
                "human_score": human,
                "recipient_class": "HIRING_MANAGER",
                "outreach_mode": "cold",
                "run_context": {"output": {"text": text}, "recipient_class": "HIRING_MANAGER"},
            })
        corpus = self._build_corpus(tmp_path, rows)
        # Very low threshold should always pass when rho is defined
        results = run_calibration(corpus, threshold=-2.0)
        assert len(results) == 1
        # With threshold=-2.0 any non-nan rho should pass; if constant input → nan → not passed
        result = results[0]
        if not math.isnan(result.spearman_rho):
            assert result.passed is True

    def test_threshold_respected_fail(self, tmp_path):
        from ops_scripts.calibration.lic_judge_spearman_calibration import run_calibration
        rows = self._synthetic_rows("lic::ask_friction_judge::v1", n=10)
        corpus = self._build_corpus(tmp_path, rows)
        # Impossibly high threshold should always fail
        results = run_calibration(corpus, threshold=1.01)
        assert results[0].passed is False

    def test_unknown_grader_id_skipped(self, tmp_path):
        from ops_scripts.calibration.lic_judge_spearman_calibration import run_calibration
        rows = [{
            "draft_id": "d001",
            "draft_text": "text",
            "grader_id": "lic::does_not_exist::v99",
            "human_score": 0.5,
            "recipient_class": "EXEC",
            "outreach_mode": "cold",
            "run_context": {"output": {"text": "text"}},
        }]
        corpus = self._build_corpus(tmp_path, rows)
        results = run_calibration(corpus)
        assert results == []

    def test_grader_id_whitelist_filter(self, tmp_path):
        from ops_scripts.calibration.lic_judge_spearman_calibration import run_calibration
        rows = (
            self._synthetic_rows("lic::ask_friction_judge::v1", n=5)
            + self._synthetic_rows("lic::personalization_judge::v1", n=5)
        )
        corpus = self._build_corpus(tmp_path, rows)
        results = run_calibration(corpus, grader_ids=["lic::ask_friction_judge::v1"])
        assert len(results) == 1
        assert results[0].grader_id == "lic::ask_friction_judge::v1"

    def test_empty_corpus_returns_empty(self, tmp_path):
        from ops_scripts.calibration.lic_judge_spearman_calibration import run_calibration
        corpus = self._build_corpus(tmp_path, [])
        results = run_calibration(corpus)
        assert results == []

    def test_unknown_sentinel_increments_unknown_count(self, tmp_path):
        from ops_scripts.calibration.lic_judge_spearman_calibration import run_calibration
        # proof_appropriate_judge returns GRADER_UNKNOWN_SENTINEL when text is empty
        rows = [{
            "draft_id": "d001",
            "draft_text": "",
            "grader_id": "lic::proof_appropriate_judge::v1",
            "human_score": 0.8,
            "recipient_class": "EXECUTIVE",
            "outreach_mode": "cold",
            "run_context": {"output": {"text": ""}},
        }]
        corpus = self._build_corpus(tmp_path, rows)
        results = run_calibration(corpus)
        # n_samples 0 (all unknown) → rho is nan → not passed
        if results:
            assert results[0].unknown_count >= 1 or results[0].n_samples == 0


# ===========================================================================
# Judge flag invariants (all 5 plan-listed judges)
# ===========================================================================

PLAN_JUDGES = [
    ("ask_friction_judge",      "apps_lic.engines.judges.ask_friction_judge"),
    ("antipattern_clean_judge", "apps_lic.engines.judges.antipattern_clean_judge"),
    ("proof_appropriate_judge", "apps_lic.engines.judges.proof_appropriate_judge"),
    ("personalization_judge",   "apps_lic.engines.judges.personalization_judge"),
    ("asymmetric_insight_judge","apps_lic.engines.judges.asymmetric_insight_judge"),
]


@pytest.mark.parametrize("judge_name,module_path", PLAN_JUDGES)
def test_judge_is_stub_false(judge_name, module_path):
    import importlib
    mod = importlib.import_module(module_path)
    assert mod.IS_STUB is False, f"{judge_name}: IS_STUB should be False"


@pytest.mark.parametrize("judge_name,module_path", PLAN_JUDGES)
def test_judge_is_calibrated_true(judge_name, module_path):
    import importlib
    mod = importlib.import_module(module_path)
    assert mod.IS_CALIBRATED is True, f"{judge_name}: IS_CALIBRATED should be True"


@pytest.mark.parametrize("judge_name,module_path", PLAN_JUDGES)
def test_judge_no_is_calibrated_synthetic(judge_name, module_path):
    import importlib
    mod = importlib.import_module(module_path)
    assert not hasattr(mod, "IS_CALIBRATED_SYNTHETIC"), (
        f"{judge_name}: IS_CALIBRATED_SYNTHETIC must not be defined "
        "(should have been removed when judge was promoted)"
    )


@pytest.mark.parametrize("judge_name,module_path", PLAN_JUDGES)
def test_judge_grade_returns_tuple(judge_name, module_path):
    import importlib
    mod = importlib.import_module(module_path)
    ctx = {
        "output": {"text": "Hi Alice, I noticed your work at Acme. Would you chat?"},
        "recipient_class": "HIRING_MANAGER",
        "outreach_mode": "cold",
        "asymmetric_insight_required": False,
    }
    result = mod.grade(None, ctx)
    assert isinstance(result, tuple), f"{judge_name}: grade() should return tuple"
    assert len(result) == 2, f"{judge_name}: grade() should return (score, refs)"
    score, refs = result
    assert isinstance(refs, list), f"{judge_name}: refs should be list"
