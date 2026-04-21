# pylint: disable=protected-access
"""Unit tests for .windsurf/scripts/post_cascade_author_gate_miss_detector.py.

Coverage:
    _extract_edited_files       - pulls .py/.md/.js/.yaml/.json paths from
                                  file_path= / TargetFile= patterns
    _decision_keywords_hit      - case-insensitive keyword counting
    _has_capture_marker         - detects DECISION_CAPTURED / AUTHOR_GATE_PACKET
                                  / HITL_PACKET / ask_user_question invocation
    _compute_miss_score         - positive signals accumulate, anti-signals zero
                                  or reduce score
    main()                      - end-to-end: stdin JSON -> jsonl append when
                                  score >= threshold; no-op on empty stdin
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parents[4] / ".windsurf" / "scripts"
sys.path.insert(0, str(_SCRIPTS_DIR))

import post_cascade_author_gate_miss_detector as _m  # noqa: E402

from post_cascade_author_gate_miss_detector import (  # noqa: E402
    MISS_SCORE_THRESHOLD,
    _compute_miss_score,
    _decision_keywords_hit,
    _extract_edited_files,
    _has_capture_marker,
)


# --------------------------------------------------------------------- #
# _extract_edited_files
# --------------------------------------------------------------------- #


class TestExtractEditedFiles:
    def test_file_path_kwarg(self):
        text = 'edit(file_path="agentic_core/L3_orchestration/run.py", ...)'
        files = _extract_edited_files(text)
        assert files == ["agentic_core/L3_orchestration/run.py"]

    def test_target_file_kwarg(self):
        text = 'write_to_file(TargetFile="docs/architecture/adr/ADR-NNN.md")'
        files = _extract_edited_files(text)
        assert files == ["docs/architecture/adr/ADR-NNN.md"]

    def test_deduplicates_and_sorts(self):
        text = """
        edit(file_path="a.py") ... edit(file_path="b.py") ...
        edit(file_path="a.py") ...
        """
        files = _extract_edited_files(text)
        assert files == ["a.py", "b.py"]

    def test_ignores_non_source_extensions(self):
        text = 'edit(file_path="tmp.log", ...) edit(file_path="x.py", ...)'
        files = _extract_edited_files(text)
        assert files == ["x.py"]  # .log not matched

    def test_accepts_multiple_extensions(self):
        text = """
        file_path="a.py"  file_path="b.md"  file_path="c.yaml"
        file_path="d.json"  file_path="e.ts"  file_path="f.tsx"
        """
        files = _extract_edited_files(text)
        assert set(files) == {"a.py", "b.md", "c.yaml", "d.json", "e.ts", "f.tsx"}


# --------------------------------------------------------------------- #
# _decision_keywords_hit
# --------------------------------------------------------------------- #


class TestDecisionKeywords:
    def test_case_insensitive(self):
        # "DELETING" contains substring "delet" but not "delete" (different 6th letter),
        # so use "DELETED" which contains "delete" as a proper substring.
        hits = _decision_keywords_hit("REFACTORING the module and DELETED files")
        assert "refactoring" in hits
        assert "delete" in hits

    def test_no_hits_returns_empty(self):
        assert _decision_keywords_hit("typo fix") == []

    def test_multiple_keywords_all_reported(self):
        text = "refactor with bare except inside a subprocess call for cross-layer"
        hits = _decision_keywords_hit(text)
        assert "refactor" in hits
        assert "bare except" in hits
        assert "subprocess" in hits
        assert "cross-layer" in hits


# --------------------------------------------------------------------- #
# _has_capture_marker
# --------------------------------------------------------------------- #


class TestHasCaptureMarker:
    def test_decision_captured_detected(self):
        text = "Some preamble\nDECISION_CAPTURED: type=refactor_scope, repo_area=x, selected=y, outcome=executed\nmore text"
        assert _has_capture_marker(text) != []

    def test_author_gate_packet_detected(self):
        text = 'preamble\nAUTHOR_GATE_PACKET: {"version": 1, "decision_type": "foo"}\n'
        assert _has_capture_marker(text) != []

    def test_legacy_hitl_packet_detected(self):
        text = 'HITL_PACKET: {"version": 1, "options": []}'
        assert _has_capture_marker(text) != []

    def test_ask_user_question_invoke_detected(self):
        text = 'Some analysis\n<invoke name="ask_user_question">\n<parameter name="question">...</parameter>'
        assert _has_capture_marker(text) != []

    def test_no_marker_returns_empty(self):
        assert _has_capture_marker("A plain response with no markers") == []


# --------------------------------------------------------------------- #
# _compute_miss_score
# --------------------------------------------------------------------- #


class TestComputeMissScore:
    def test_multi_file_plus_keywords_exceeds_threshold(self):
        text = (
            "Refactoring the system. "
            'edit(file_path="agentic_core/L3_orchestration/run.py") '
            'edit(file_path="apps_lic/engines/control_plane.py") '
            "Removing bare except and adding subprocess timeout."
        )
        score, report = _compute_miss_score(text)
        assert score >= MISS_SCORE_THRESHOLD
        assert any(s.startswith("multi_file_edit") for s in report["positive_signals"])
        assert any(s.startswith("keywords") for s in report["positive_signals"])

    def test_capture_marker_zeros_score(self):
        text = (
            "DECISION_CAPTURED: type=refactor_scope, repo_area=x, selected=y, outcome=executed\n"
            "Refactoring across modules. "
            'edit(file_path="a.py") edit(file_path="b.py") '
            "bare except subprocess cross-layer"
        )
        score, report = _compute_miss_score(text)
        assert score == 0
        assert report.get("anti_signal") == "capture_marker_present"

    def test_trivial_tier_reduces_score(self):
        """A T1 trivial marker reduces score even if keywords appear."""
        text = (
            'T1 trivial fix: rename a variable. edit(file_path="only_one.py") '
            "comment mentions refactor but is trivial"
        )
        score, _report = _compute_miss_score(text)
        assert score < MISS_SCORE_THRESHOLD

    def test_user_directive_reduces_score(self):
        """Explicit user directive reduces score by 1."""
        text_without = 'edit(file_path="a.py") edit(file_path="b.py") refactor scope'
        text_with = text_without + " This was as requested by the user."
        s_without, _ = _compute_miss_score(text_without)
        s_with, _ = _compute_miss_score(text_with)
        assert s_with < s_without

    def test_sr_plan_without_approval_adds_signal(self):
        text = 'SR_PLAN follows\nedit(file_path="a.py") edit(file_path="b.py")'
        score, report = _compute_miss_score(text)
        assert "sr_plan_without_approval" in report["positive_signals"]

    def test_sr_plan_with_approval_does_not_add_signal(self):
        text = 'SR_PLAN follows\nSR_APPROVAL: APPROVED\nedit(file_path="a.py") edit(file_path="b.py")'
        _score, report = _compute_miss_score(text)
        assert "sr_plan_without_approval" not in report["positive_signals"]

    def test_plan_file_touched_adds_signal(self):
        text = '.windsurf/plans/foo-ab1234.md edit(file_path="a.py") edit(file_path="b.py") refactor'
        _score, report = _compute_miss_score(text)
        assert "plan_file_touched" in report["positive_signals"]

    def test_single_file_below_threshold_no_miss(self):
        """One file + one keyword should be below threshold."""
        text = 'edit(file_path="x.py") mentions refactor once'
        score, _ = _compute_miss_score(text)
        assert score < MISS_SCORE_THRESHOLD


# --------------------------------------------------------------------- #
# main() — end-to-end via subprocess
# --------------------------------------------------------------------- #


class TestMainEndToEnd:
    SCRIPT = _SCRIPTS_DIR / "post_cascade_author_gate_miss_detector.py"

    def _run(self, payload: dict, repo_root: Path) -> tuple[int, str]:
        proc = subprocess.run(
            [sys.executable, str(self.SCRIPT)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            timeout=10,
            check=False,
        )
        return proc.returncode, proc.stderr

    def test_miss_logged_when_score_above_threshold(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        log = tmp_path / "artifacts" / "windsurf" / "author_gate_misses.jsonl"
        monkeypatch.setattr(_m, "MISS_LOG", log)

        payload = {
            "response_text": (
                "Refactoring the system. "
                'edit(file_path="a.py") edit(file_path="b.py") '
                "bare except subprocess cross-layer"
            ),
            "cascade_id": "unit-test-cascade",
        }
        # Invoke main() in-process (module globals already patched)
        import io

        monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))
        rc = _m.main()
        assert rc == 0
        assert log.exists()
        lines = log.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["miss_score"] >= MISS_SCORE_THRESHOLD
        assert record["cascade_id"] == "unit-test-cascade"
        assert any(s.startswith("multi_file_edit") for s in record["signals"])

    def test_no_log_when_capture_present(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        log = tmp_path / "artifacts" / "windsurf" / "author_gate_misses.jsonl"
        monkeypatch.setattr(_m, "MISS_LOG", log)

        payload = {
            "response_text": (
                "DECISION_CAPTURED: type=refactor_scope, repo_area=x, "
                "selected=y, outcome=executed\n"
                'edit(file_path="a.py") edit(file_path="b.py") refactor bare except'
            ),
        }
        import io

        monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))
        rc = _m.main()
        assert rc == 0
        assert not log.exists()

    def test_empty_stdin_is_noop(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        log = tmp_path / "artifacts" / "windsurf" / "author_gate_misses.jsonl"
        monkeypatch.setattr(_m, "MISS_LOG", log)
        import io

        monkeypatch.setattr("sys.stdin", io.StringIO(""))
        rc = _m.main()
        assert rc == 0
        assert not log.exists()

    def test_invalid_json_treated_as_raw_text(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        log = tmp_path / "artifacts" / "windsurf" / "author_gate_misses.jsonl"
        monkeypatch.setattr(_m, "MISS_LOG", log)
        import io

        raw = 'not json at all edit(file_path="a.py") edit(file_path="b.py") refactor bare except subprocess'
        monkeypatch.setattr("sys.stdin", io.StringIO(raw))
        rc = _m.main()
        assert rc == 0
        # Raw text fallback does compute miss score
        assert log.exists()
