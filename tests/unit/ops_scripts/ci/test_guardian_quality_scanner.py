"""Tests for ops_scripts/ci/guardian_quality_scanner.py — W3.7 residual gap coverage."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# _load_ratchet
# ---------------------------------------------------------------------------


class TestLoadRatchet:
    def test_returns_empty_when_file_missing(self, tmp_path):
        import ops_scripts.ci.guardian_quality_scanner as gqs

        original = gqs.RATCHET_FILE
        gqs.RATCHET_FILE = tmp_path / "nonexistent.json"
        try:
            out = gqs._load_ratchet()
            assert out == {}
        finally:
            gqs.RATCHET_FILE = original

    def test_returns_parsed_content(self, tmp_path):
        import ops_scripts.ci.guardian_quality_scanner as gqs

        original = gqs.RATCHET_FILE
        ratchet_file = tmp_path / "ratchet.json"
        ratchet_file.write_text(json.dumps({"duplicate_ceiling": 0, "weak_justification_ceiling": 5}))
        gqs.RATCHET_FILE = ratchet_file
        try:
            out = gqs._load_ratchet()
            assert out["duplicate_ceiling"] == 0
            assert out["weak_justification_ceiling"] == 5
        finally:
            gqs.RATCHET_FILE = original

    def test_corrupt_json_prints_warning_returns_empty(self, tmp_path, capsys):
        """G4 fix: corrupt ratchet must warn on stderr, not silently return {}."""
        import ops_scripts.ci.guardian_quality_scanner as gqs

        original = gqs.RATCHET_FILE
        ratchet_file = tmp_path / "ratchet.json"
        ratchet_file.write_text("{not valid json}")
        gqs.RATCHET_FILE = ratchet_file
        try:
            out = gqs._load_ratchet()
            assert out == {}
            captured = capsys.readouterr()
            assert "WARNING" in captured.err
            assert "corrupt" in captured.err
        finally:
            gqs.RATCHET_FILE = original

    def test_os_error_prints_warning_returns_empty(self, tmp_path, capsys):
        import ops_scripts.ci.guardian_quality_scanner as gqs

        original = gqs.RATCHET_FILE
        ratchet_file = tmp_path / "ratchet.json"
        ratchet_file.write_text("{}")
        gqs.RATCHET_FILE = ratchet_file
        with patch("pathlib.Path.read_text", side_effect=OSError("permission denied")):
            try:
                out = gqs._load_ratchet()
                assert out == {}
                captured = capsys.readouterr()
                assert "WARNING" in captured.err
            finally:
                gqs.RATCHET_FILE = original


# ---------------------------------------------------------------------------
# _save_ratchet
# ---------------------------------------------------------------------------


class TestSaveRatchet:
    def test_creates_file_with_correct_content(self, tmp_path):
        import ops_scripts.ci.guardian_quality_scanner as gqs

        original = gqs.RATCHET_FILE
        gqs.RATCHET_FILE = tmp_path / "sub" / "ratchet.json"
        try:
            gqs._save_ratchet({"duplicate_ceiling": 0, "weak_justification_ceiling": 3})
            written = json.loads(gqs.RATCHET_FILE.read_text())
            assert written["duplicate_ceiling"] == 0
            assert written["weak_justification_ceiling"] == 3
        finally:
            gqs.RATCHET_FILE = original

    def test_creates_parent_dirs(self, tmp_path):
        import ops_scripts.ci.guardian_quality_scanner as gqs

        original = gqs.RATCHET_FILE
        deep = tmp_path / "a" / "b" / "c" / "ratchet.json"
        gqs.RATCHET_FILE = deep
        try:
            gqs._save_ratchet({"x": 1})
            assert deep.exists()
        finally:
            gqs.RATCHET_FILE = original


# ---------------------------------------------------------------------------
# main — ratchet logic via env vars
# ---------------------------------------------------------------------------


class TestMain:
    def _make_scanner(self, tmp_path, duplicates: int, weak: int):
        """Patch _run_scan and RATCHET_FILE for isolated main() tests."""
        import ops_scripts.ci.guardian_quality_scanner as gqs

        gqs.RATCHET_FILE = tmp_path / "ratchet.json"
        return patch.object(gqs, "_run_scan", return_value=(duplicates, weak))

    def test_init_mode_writes_ratchet(self, tmp_path, monkeypatch):
        import ops_scripts.ci.guardian_quality_scanner as gqs

        original_rf = gqs.RATCHET_FILE
        gqs.RATCHET_FILE = tmp_path / "ratchet.json"
        monkeypatch.setenv("GUARDIAN_INIT", "1")
        monkeypatch.delenv("GUARDIAN_DRY_RUN", raising=False)
        with patch.object(gqs, "_run_scan", return_value=(0, 10)):
            rc = gqs.main()
        assert rc == 0
        ratchet = json.loads(gqs.RATCHET_FILE.read_text())
        assert ratchet["weak_justification_ceiling"] == 10
        assert ratchet["duplicate_ceiling"] == 0
        gqs.RATCHET_FILE = original_rf

    def test_pass_when_below_ceiling(self, tmp_path, monkeypatch):
        import ops_scripts.ci.guardian_quality_scanner as gqs

        original_rf = gqs.RATCHET_FILE
        gqs.RATCHET_FILE = tmp_path / "ratchet.json"
        gqs.RATCHET_FILE.write_text(json.dumps({"duplicate_ceiling": 0, "weak_justification_ceiling": 10}))
        monkeypatch.delenv("GUARDIAN_INIT", raising=False)
        monkeypatch.delenv("GUARDIAN_DRY_RUN", raising=False)
        with patch.object(gqs, "_run_scan", return_value=(0, 8)):
            rc = gqs.main()
        assert rc == 0
        gqs.RATCHET_FILE = original_rf

    def test_fail_when_duplicates_exceed_ceiling(self, tmp_path, monkeypatch):
        import ops_scripts.ci.guardian_quality_scanner as gqs

        original_rf = gqs.RATCHET_FILE
        gqs.RATCHET_FILE = tmp_path / "ratchet.json"
        gqs.RATCHET_FILE.write_text(json.dumps({"duplicate_ceiling": 0, "weak_justification_ceiling": 5}))
        monkeypatch.delenv("GUARDIAN_INIT", raising=False)
        monkeypatch.delenv("GUARDIAN_DRY_RUN", raising=False)
        with patch.object(gqs, "_run_scan", return_value=(2, 5)):
            rc = gqs.main()
        assert rc == 1
        gqs.RATCHET_FILE = original_rf

    def test_fail_when_weak_exceeds_ceiling(self, tmp_path, monkeypatch):
        import ops_scripts.ci.guardian_quality_scanner as gqs

        original_rf = gqs.RATCHET_FILE
        gqs.RATCHET_FILE = tmp_path / "ratchet.json"
        gqs.RATCHET_FILE.write_text(json.dumps({"duplicate_ceiling": 0, "weak_justification_ceiling": 5}))
        monkeypatch.delenv("GUARDIAN_INIT", raising=False)
        monkeypatch.delenv("GUARDIAN_DRY_RUN", raising=False)
        with patch.object(gqs, "_run_scan", return_value=(0, 7)):
            rc = gqs.main()
        assert rc == 1
        gqs.RATCHET_FILE = original_rf

    def test_ratchet_tightens_when_weak_improves(self, tmp_path, monkeypatch):
        import ops_scripts.ci.guardian_quality_scanner as gqs

        original_rf = gqs.RATCHET_FILE
        gqs.RATCHET_FILE = tmp_path / "ratchet.json"
        gqs.RATCHET_FILE.write_text(json.dumps({"duplicate_ceiling": 0, "weak_justification_ceiling": 10}))
        monkeypatch.delenv("GUARDIAN_INIT", raising=False)
        monkeypatch.delenv("GUARDIAN_DRY_RUN", raising=False)
        with patch.object(gqs, "_run_scan", return_value=(0, 6)):
            rc = gqs.main()
        assert rc == 0
        updated = json.loads(gqs.RATCHET_FILE.read_text())
        assert updated["weak_justification_ceiling"] == 6
        gqs.RATCHET_FILE = original_rf

    def test_dry_run_does_not_tighten_ratchet(self, tmp_path, monkeypatch):
        import ops_scripts.ci.guardian_quality_scanner as gqs

        original_rf = gqs.RATCHET_FILE
        gqs.RATCHET_FILE = tmp_path / "ratchet.json"
        gqs.RATCHET_FILE.write_text(json.dumps({"duplicate_ceiling": 0, "weak_justification_ceiling": 10}))
        monkeypatch.delenv("GUARDIAN_INIT", raising=False)
        monkeypatch.setenv("GUARDIAN_DRY_RUN", "1")
        with patch.object(gqs, "_run_scan", return_value=(0, 6)):
            rc = gqs.main()
        assert rc == 0
        unchanged = json.loads(gqs.RATCHET_FILE.read_text())
        assert unchanged["weak_justification_ceiling"] == 10
        gqs.RATCHET_FILE = original_rf
