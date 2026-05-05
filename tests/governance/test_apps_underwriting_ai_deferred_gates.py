"""Tests for deferred-scope gates and tools from
apps-underwriting-ai-rationale-judge-deferred-d4e7a2.

Covers:
- W3 P3.1: check_eval_holdout_split — gate contract, bypass, no-overlap pass
- W3 P3.2: prod_log_miner — PII redaction, candidate conversion, mine()
- W4 P4.1: run_contract_gates — RJC1+RJC2 entries present
- W5 P5.1: rationale_judge_weekly_report — _query_ledger shape, _write_markdown
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# W3 P3.1 — check_eval_holdout_split
# ---------------------------------------------------------------------------

class TestEvalHoldoutSplitGate:
    def _run(self, env: dict | None = None) -> subprocess.CompletedProcess:
        e = os.environ.copy()
        if env:
            e.update(env)
        return subprocess.run(
            [sys.executable, "ops_scripts/ci/check_eval_holdout_split.py"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            env=e,
            timeout=30,
        )

    def test_bypass_exits_zero(self):
        r = self._run({"EVAL_HOLDOUT_SPLIT_BYPASS": "1"})
        assert r.returncode == 0
        assert "BYPASS" in r.stdout

    def test_no_overlap_passes(self):
        r = self._run()
        assert r.returncode == 0, r.stdout + r.stderr
        assert "PASS" in r.stdout

    def test_overlap_detected(self):
        from ops_scripts.ci.check_eval_holdout_split import _DECISION_ID_RE
        text = "uw-holdout-evidence_sufficiency-001 is in this file"
        ids = set(_DECISION_ID_RE.findall(text))
        assert len(ids) == 1
        assert "uw-holdout-evidence_sufficiency-001" in ids

    def test_holdout_ids_loaded(self):
        from ops_scripts.ci.check_eval_holdout_split import _load_holdout_ids
        ids = _load_holdout_ids()
        assert len(ids) == 100
        assert all(id_.startswith("uw-holdout-") for id_ in ids)


# ---------------------------------------------------------------------------
# W3 P3.2 — prod_log_miner
# ---------------------------------------------------------------------------

class TestProdLogMiner:
    def test_bypass_exits_zero(self, monkeypatch):
        monkeypatch.setenv("PROD_LOG_MINER_BYPASS", "1")
        import importlib
        import tools.underwriting.prod_log_miner as mod
        importlib.reload(mod)
        with pytest.raises(SystemExit) as exc:
            mod.main()
        assert exc.value.code == 0

    def test_redact_text_ssn(self):
        from tools.underwriting.prod_log_miner import redact_text
        result = redact_text("SSN: 123-45-6789 was confirmed.")
        assert "123-45-6789" not in result
        assert "<REDACTED_SSN>" in result

    def test_redact_text_email(self):
        from tools.underwriting.prod_log_miner import redact_text
        result = redact_text("Contact: john.doe@example.com for details.")
        assert "john.doe@example.com" not in result
        assert "<REDACTED_EMAIL>" in result

    def test_redact_text_phone(self):
        from tools.underwriting.prod_log_miner import redact_text
        result = redact_text("Call 555-867-5309 for follow-up.")
        assert "555-867-5309" not in result
        assert "<REDACTED_PHONE>" in result

    def test_redact_record_pii_fields(self):
        from tools.underwriting.prod_log_miner import redact_record
        record = {
            "applicant_name": "Jane Smith",
            "ssn": "987-65-4321",
            "rationale": "The application looks solid.",
            "score": 0.85,
        }
        cleaned = redact_record(record)
        assert cleaned["applicant_name"] == "<REDACTED>"
        assert cleaned["ssn"] == "<REDACTED>"
        assert cleaned["rationale"] == "The application looks solid."
        assert cleaned["score"] == 0.85

    def test_to_candidate_returns_none_for_short_rationale(self):
        from tools.underwriting.prod_log_miner import _to_candidate
        result = _to_candidate({"rationale": "OK"}, 0)
        assert result is None

    def test_to_candidate_well_formed(self):
        from tools.underwriting.prod_log_miner import _to_candidate
        record = {
            "rationale": "A" * 50,
            "evidence_refs": ["ref::a", "ref::b"],
            "dim_id": "policy_compliance",
        }
        c = _to_candidate(record, 3)
        assert c is not None
        assert c["candidate_id"].startswith("uw-candidate-")
        assert c["_review_required"] is True
        assert c["_pii_redacted"] is True
        assert c["labeler_id"] is None
        assert c["ground_truth_score"] is None

    def test_mine_empty_source(self, tmp_path):
        from tools.underwriting.prod_log_miner import mine
        src = tmp_path / "empty.jsonl"
        src.write_text("")
        out = tmp_path / "out"
        summary = mine(src, out, limit=10)
        assert summary["total_read"] == 0
        assert summary["candidates_emitted"] == 0

    def test_mine_valid_records(self, tmp_path):
        from tools.underwriting.prod_log_miner import mine
        records = [
            {"rationale": "B" * 60, "evidence_refs": [], "dim_id": "evidence_sufficiency"},
            {"rationale": "short"},
            {"rationale": "C" * 40, "evidence_refs": ["ref::x"]},
        ]
        src = tmp_path / "logs.jsonl"
        src.write_text("\n".join(json.dumps(r) for r in records))
        out = tmp_path / "staging"
        summary = mine(src, out, limit=100)
        assert summary["total_read"] == 3
        assert summary["candidates_emitted"] == 2
        assert summary["skipped_no_rationale"] == 1
        out_files = list(out.glob("*.jsonl"))
        assert len(out_files) == 1
        lines = out_files[0].read_text().splitlines()
        assert len(lines) == 2

    def test_mine_respects_limit(self, tmp_path):
        from tools.underwriting.prod_log_miner import mine
        records = [{"rationale": "X" * 50} for _ in range(20)]
        src = tmp_path / "logs.jsonl"
        src.write_text("\n".join(json.dumps(r) for r in records))
        out = tmp_path / "staging"
        summary = mine(src, out, limit=5)
        assert summary["candidates_emitted"] == 5
        assert summary["skipped_limit"] == 15


# ---------------------------------------------------------------------------
# W4 P4.1 — run_contract_gates has RJC1 + RJC2
# ---------------------------------------------------------------------------

class TestRunContractGatesRJCEntries:
    def _read_gates(self) -> str:
        return (REPO_ROOT / "ops_scripts" / "ci" / "run_contract_gates.py").read_text(
            encoding="utf-8"
        )

    def test_rjc1_entry_present(self):
        content = self._read_gates()
        assert "RJC1" in content
        assert "check_rationale_judge_calibration.py" in content

    def test_rjc2_entry_present(self):
        content = self._read_gates()
        assert "RJC2" in content
        assert "check_eval_holdout_split.py" in content


# ---------------------------------------------------------------------------
# W5 P5.1 — weekly report _query_ledger + _write_markdown
# ---------------------------------------------------------------------------

class TestWeeklyReportLedgerIntegration:
    def test_query_ledger_no_file(self, tmp_path, monkeypatch):
        import ops_scripts.calibration.rationale_judge_weekly_report as mod
        monkeypatch.setattr(mod, "_LEDGER_PATH", tmp_path / "nonexistent.sqlite")
        result = mod._query_ledger()
        assert result["available"] is False
        assert "reason" in result

    def test_query_ledger_empty_db(self, tmp_path, monkeypatch):
        import sqlite3
        import ops_scripts.calibration.rationale_judge_weekly_report as mod
        db = tmp_path / "ledger.sqlite"
        conn = sqlite3.connect(str(db))
        conn.execute(
            "CREATE TABLE events ("
            "event_kind TEXT, repo_area TEXT, score_band TEXT, "
            "score_numeric REAL, ts_utc TEXT, prediction_json TEXT)"
        )
        conn.commit()
        conn.close()
        monkeypatch.setattr(mod, "_LEDGER_PATH", db)
        result = mod._query_ledger()
        assert result["available"] is True
        assert result["sample_size"] == 0
        assert result["weekly_pass_rates"] == []

    def test_query_ledger_with_rows(self, tmp_path, monkeypatch):
        import sqlite3
        import ops_scripts.calibration.rationale_judge_weekly_report as mod
        db = tmp_path / "ledger.sqlite"
        conn = sqlite3.connect(str(db))
        conn.execute(
            "CREATE TABLE events ("
            "event_kind TEXT, repo_area TEXT, score_band TEXT, "
            "score_numeric REAL, ts_utc TEXT, prediction_json TEXT)"
        )
        rows = [
            ("app_eval_bound", "apps_underwriting_ai", "pass", 0.9, "2026-05-05T10:00:00Z", "{}"),
            ("app_eval_bound", "apps_underwriting_ai", "pass", 0.85, "2026-05-05T11:00:00Z", "{}"),
            ("app_eval_bound", "apps_underwriting_ai", "deny", 0.3, "2026-05-05T12:00:00Z", "{}"),
            ("app_eval_bound", "apps_rg", "pass", 0.95, "2026-05-05T09:00:00Z", "{}"),
        ]
        conn.executemany(
            "INSERT INTO events VALUES (?,?,?,?,?,?)", rows
        )
        conn.commit()
        conn.close()
        monkeypatch.setattr(mod, "_LEDGER_PATH", db)
        result = mod._query_ledger()
        assert result["available"] is True
        assert result["sample_size"] == 3
        assert result["pass_rate"] == pytest.approx(2 / 3, abs=0.01)
        assert "pass" in result["score_band_counts"]

    def test_write_markdown_no_ledger(self, tmp_path):
        import ops_scripts.calibration.rationale_judge_weekly_report as mod
        stats = {"status": "no_holdout_data", "week": "2026-W19"}
        ledger = {"available": False, "reason": "ledger_not_found"}
        out = tmp_path / "report.md"
        mod._write_markdown(stats, ledger, "2026-W19", out)
        content = out.read_text()
        assert "Rationale Judge Weekly Calibration Report" in content
        assert "ledger_not_found" in content

    def test_write_markdown_with_data(self, tmp_path):
        import ops_scripts.calibration.rationale_judge_weekly_report as mod
        stats = {
            "status": "ok",
            "global_spearman": 0.801,
            "global_pass": True,
            "n_total": 100,
            "unknown_rate": 0.0,
            "per_dim": {
                "evidence_sufficiency": {"spearman": 0.796, "n": 20, "pass": True},
            },
            "week": "2026-W19",
        }
        ledger = {
            "available": True,
            "sample_size": 50,
            "pass_rate": 0.9,
            "score_band_counts": {"pass": 45, "deny": 5},
            "weekly_pass_rates": [{"week": "2026-W19", "pass_rate": 0.9, "n": 50}],
            "holdout_comparison": None,
        }
        out = tmp_path / "report.md"
        mod._write_markdown(stats, ledger, "2026-W19", out)
        content = out.read_text()
        assert "0.801" in content
        assert "PASS" in content
        assert "50" in content
        assert "Pass Rate Trend" in content
        assert "DS-R1" in content
        assert "DS-R2" in content
