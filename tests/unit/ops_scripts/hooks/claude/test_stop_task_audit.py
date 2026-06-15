"""Tests for the STATUS-floor Stop audit hook.

The hook executes at module import (it ``raise SystemExit(...)`` at top level), so we run
it as a real subprocess and assert on exit code + the ``{"decision":"block"}`` JSON it
prints on stdout. The central regression: on a REAL Claude Stop payload (``transcript_path``,
no inline response) the hook must now recover the final assistant turn from the transcript
and actually fire the STATUS-floor / PASS-without-proof blocks instead of silently no-opping.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
HOOK = REPO_ROOT / ".claude" / "hooks" / "stop_task_audit.py"


def _write_transcript(tmp_path: Path, final_text: str) -> Path:
    lines = [
        json.dumps({"type": "user", "message": {"role": "user", "content": "go"}}),
        json.dumps(
            {
                "type": "assistant",
                "message": {"role": "assistant", "content": [{"type": "text", "text": final_text}]},
            }
        ),
    ]
    path = tmp_path / "transcript.jsonl"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _run(payload) -> subprocess.CompletedProcess:
    raw = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=raw,
        text=True,
        capture_output=True,
        timeout=60,
        cwd=str(REPO_ROOT),
    )


def _block_decision(proc: subprocess.CompletedProcess) -> dict:
    line = proc.stdout.strip().splitlines()[-1]
    return json.loads(line)


_REPO_WORK_NO_STATUS = "Here is the work.\nFILES_CHANGED:\n- foo.py\nCOMMANDS_RUN:\n- ran it\n"
_PASS_FULL_PROOF = (
    "STATUS: PASS\nFILES_CHANGED:\n- foo.py\nCOMMANDS_RUN:\n- ran\nTESTS_GATES:\n- pytest 3 passed\n"
    "ARTIFACTS:\n- out.json\n"
)
_PASS_MISSING_PROOF = "STATUS: PASS\nFILES_CHANGED:\n- foo.py\n"


class TestStopTaskAuditTranscript:
    def test_repo_work_without_status_blocks(self, tmp_path) -> None:
        tr = _write_transcript(tmp_path, _REPO_WORK_NO_STATUS)
        proc = _run({"session_id": "s1", "transcript_path": str(tr)})
        assert proc.returncode == 2, proc.stdout + proc.stderr
        assert _block_decision(proc)["decision"] == "block"
        assert "STATUS" in _block_decision(proc)["reason"]

    def test_pass_with_full_proof_allows(self, tmp_path) -> None:
        tr = _write_transcript(tmp_path, _PASS_FULL_PROOF)
        proc = _run({"session_id": "s2", "transcript_path": str(tr)})
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "decision" not in proc.stdout

    def test_pass_missing_proof_blocks(self, tmp_path) -> None:
        tr = _write_transcript(tmp_path, _PASS_MISSING_PROOF)
        proc = _run({"session_id": "s3", "transcript_path": str(tr)})
        assert proc.returncode == 2, proc.stdout + proc.stderr
        assert "proof" in _block_decision(proc)["reason"].lower()


class TestStopTaskAuditFailOpen:
    def test_empty_payload_allows(self) -> None:
        proc = _run("")
        assert proc.returncode == 0
        assert "decision" not in proc.stdout

    def test_malformed_payload_allows(self) -> None:
        proc = _run("this is not json {")
        assert proc.returncode == 0
        assert "decision" not in proc.stdout

    def test_missing_transcript_file_allows(self, tmp_path) -> None:
        proc = _run({"session_id": "s4", "transcript_path": str(tmp_path / "absent.jsonl")})
        assert proc.returncode == 0
        assert "decision" not in proc.stdout


class TestStopTaskAuditBackwardCompat:
    def test_inline_tool_info_response_still_blocks(self) -> None:
        # Legacy/synthetic payload shape (tool_info.response) must still be honored.
        proc = _run({"session_id": "s5", "tool_info": {"response": _REPO_WORK_NO_STATUS}})
        assert proc.returncode == 2
        assert _block_decision(proc)["decision"] == "block"


class TestStopTaskAuditFalseBlockFix:
    """Regression tests: the old 'GATE in prose' / 'CREATED in prose' false-blocks
    are gone. The thin detect()-layer only blocks on actual floor / proof violations."""

    def test_prose_with_gate_word_and_no_floor_signals_allows(self, tmp_path) -> None:
        # Old code: "GATE" in repo_work_cues -> repo_work_present=True, no STATUS -> block.
        # New code: detect() sees no STATUS and no floor signals -> (None, []) -> allow.
        text = (
            "This design covers the north-star gate and its role in the enforcement surface. "
            "No code was changed or committed in this turn."
        )
        tr = _write_transcript(tmp_path, text)
        proc = _run({"session_id": "fb1", "transcript_path": str(tr)})
        assert proc.returncode == 0, proc.stdout + proc.stderr

    def test_prose_with_created_word_and_no_floor_signals_allows(self, tmp_path) -> None:
        # Old code: "CREATED" in repo_work_cues -> repo_work_present=True, no STATUS -> block.
        # New code: detect() sees no STATUS and no floor signals -> (None, []) -> allow.
        text = "I created a design document and outlined the approach. No edits made."
        tr = _write_transcript(tmp_path, text)
        proc = _run({"session_id": "fb2", "transcript_path": str(tr)})
        assert proc.returncode == 0, proc.stdout + proc.stderr

    def test_prose_with_implemented_word_and_no_floor_signals_allows(self, tmp_path) -> None:
        # Old code: "IMPLEMENTED" in repo_work_cues -> would block with no STATUS.
        text = "Discussed how the feature could be implemented. Analysis only, no edits."
        tr = _write_transcript(tmp_path, text)
        proc = _run({"session_id": "fb3", "transcript_path": str(tr)})
        assert proc.returncode == 0, proc.stdout + proc.stderr

    def test_speculative_should_pass_blocks(self, tmp_path) -> None:
        # "should pass" on a repo-work turn -> speculative_pass -> block.
        text = (
            "STATUS: PARTIAL\n"
            "COMMANDS_RUN:\n- run -> in progress\n"
            "ARTIFACTS:\n- NONE\n"
            "These tests should pass on the next run."
        )
        tr = _write_transcript(tmp_path, text)
        proc = _run({"session_id": "fb4", "transcript_path": str(tr)})
        assert proc.returncode == 2, proc.stdout + proc.stderr
        reason = _block_decision(proc)["reason"]
        assert "speculative" in reason.lower() or "should pass" in reason.lower(), reason

    def test_speculative_likely_pass_blocks(self, tmp_path) -> None:
        # "likely pass" on a repo-work turn -> speculative_pass -> block.
        text = (
            "STATUS: PARTIAL\n"
            "COMMANDS_RUN:\n- run -> in progress\n"
            "ARTIFACTS:\n- NONE\n"
            "This will likely pass once the fixture is fixed."
        )
        tr = _write_transcript(tmp_path, text)
        proc = _run({"session_id": "fb5", "transcript_path": str(tr)})
        assert proc.returncode == 2, proc.stdout + proc.stderr
        reason = _block_decision(proc)["reason"]
        assert "speculative" in reason.lower() or "likely pass" in reason.lower(), reason

    def test_full_receipt_all_statuses_allow(self, tmp_path) -> None:
        # PARTIAL + FAIL + BLOCKED with correct receipts all allow.
        partial_text = (
            "STATUS: PARTIAL\nCOMMANDS_RUN:\n- pytest -> 3 passed, 2 pending\n"
            "TESTS_GATES:\n- pytest -> 3 passed\nARTIFACTS:\n- NONE\n"
        )
        blocked_text = (
            "STATUS: BLOCKED\nCOMMANDS_RUN:\n- N/A\n"
            "TESTS_GATES:\n- N/A\nARTIFACTS:\n- NONE\n"
        )
        fail_text = (
            "STATUS: FAIL\nCOMMANDS_RUN:\n- run -> X3_BLOCK\n"
            "TESTS_GATES:\n- N/A\nARTIFACTS:\n- NONE\n"
        )
        for session, text in [("fb6", partial_text), ("fb7", blocked_text), ("fb8", fail_text)]:
            subdir = tmp_path / session
            subdir.mkdir(exist_ok=True)
            tr = _write_transcript(subdir, text)
            proc = _run({"session_id": session, "transcript_path": str(tr)})
            assert proc.returncode == 0, f"{session}: " + proc.stdout + proc.stderr
