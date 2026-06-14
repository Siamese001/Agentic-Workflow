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
