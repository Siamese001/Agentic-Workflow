"""Regression tests for stop_task_audit.py.

These cover both real transcript recovery and inline response payloads so the
STATUS-floor hook keeps enforcing the PASS proof contract without regressing on
legacy payload shapes.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
HOOK = REPO_ROOT / ".codex" / "hooks" / "stop_task_audit.py"

_ALLOW = 0
_BLOCK = 2


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


def _run_response(text: str) -> subprocess.CompletedProcess:
    return _run({"response": text})


def _block_decision(proc: subprocess.CompletedProcess) -> dict:
    line = proc.stdout.strip().splitlines()[-1]
    return json.loads(line)


_REPO_WORK_NO_STATUS = "Here is the work.\nFILES_CHANGED:\n- foo.py\nCOMMANDS_RUN:\n- ran it\n"
_PASS_FULL_PROOF = (
    "STATUS: PASS\nFILES_CHANGED:\n- foo.py\nCOMMANDS_RUN:\n- ran\nTESTS_GATES:\n- pytest 3 passed\n"
    "ARTIFACTS:\n- out.json\n"
)
_PASS_MISSING_PROOF = "STATUS: PASS\nFILES_CHANGED:\n- foo.py\n"
_PASS_PLAN_FILE_MISSING_WAVES = (
    "STATUS: PASS\n"
    "FILES_CHANGED:\n- [plan.md](plans/post-turn-mini-table-a1b2c3.md)\n"
    "COMMANDS_RUN:\n- pytest tests/unit/ops_scripts/hooks/codex -> 3 passed\n"
    "TESTS_GATES:\n- pytest tests/unit/ops_scripts/hooks/codex -> 3 passed\n"
    "ARTIFACTS:\n- NONE\n"
)
_PASS_PLAN_FILE_WITH_WAVES = (
    "STATUS: PASS\n"
    "FILES_CHANGED:\n- [plan.md](plans/post-turn-mini-table-a1b2c3.md)\n"
    "COMMANDS_RUN:\n- pytest tests/unit/ops_scripts/hooks/codex -> 3 passed\n"
    "TESTS_GATES:\n- pytest tests/unit/ops_scripts/hooks/codex -> 3 passed\n"
    "PLAN_WAVES:\n"
    "| Wave | State | Summary |\n"
    "|---|---|---|\n"
    "| NONE | COMPLETE | No completed waves yet |\n"
    "| W1 | OPEN | Wire the post-turn mini table contract |\n"
    "ARTIFACTS:\n- NONE\n"
)
_PASS_PLAN_FILE_MALFORMED_WAVES = (
    "STATUS: PASS\n"
    "FILES_CHANGED:\n- [plan.md](plans/post-turn-mini-table-a1b2c3.md)\n"
    "COMMANDS_RUN:\n- pytest tests/unit/ops_scripts/hooks/codex -> 3 passed\n"
    "TESTS_GATES:\n- pytest tests/unit/ops_scripts/hooks/codex -> 3 passed\n"
    "PLAN_WAVES:\n- Wave W1: IN_PROGRESS\n"
    "ARTIFACTS:\n- NONE\n"
)
_PASS_PLAN_COMPLETE_ALL_COMPLETE = (
    "STATUS: PASS\n"
    "FILES_CHANGED:\n- [plan.md](plans/post-turn-mini-table-a1b2c3.md)\n"
    "COMMANDS_RUN:\n- pytest tests/unit/ops_scripts/hooks/codex -> 3 passed\n"
    "TESTS_GATES:\n- pytest tests/unit/ops_scripts/hooks/codex -> 3 passed\n"
    "PLAN_COMPLETE: plan=post-turn-mini-table-a1b2c3 note=\"done\"\n"
    "PLAN_WAVES:\n"
    "| Wave | State | Summary |\n"
    "|---|---|---|\n"
    "| W1 | COMPLETE | Contract documentation landed |\n"
    "| W2 | COMPLETE | Detector enforcement landed |\n"
    "ARTIFACTS:\n- NONE\n"
)


class TestStopTaskAuditResponsePayloads:
    def test_plain_prose_allowed(self) -> None:
        result = _run_response("Thanks for the question - no repo work here.")
        assert result.returncode == _ALLOW

    def test_full_pass_proof_allowed(self) -> None:
        result = _run_response(_PASS_FULL_PROOF)
        assert result.returncode == _ALLOW

    def test_pass_missing_artifacts_blocked(self) -> None:
        text = (
            "STATUS: PASS\n"
            "FILES_CHANGED:\n- tests/foo.py\n"
            "COMMANDS_RUN:\n- pytest tests/foo.py\n"
            "TESTS_GATES:\n- 3 passed\n"
        )
        result = _run_response(text)
        assert result.returncode == _BLOCK
        assert "ARTIFACTS" in result.stdout

    def test_bare_pass_without_proof_blocked(self) -> None:
        result = _run_response("STATUS: PASS - all done.")
        assert result.returncode == _BLOCK
        assert "proof sections" in result.stdout

    def test_repo_work_without_status_blocked(self) -> None:
        result = _run_response(
            "FILES_CHANGED:\n- apps_rg/foo.py\nCOMMANDS_RUN:\n- pytest\nImplemented the patch."
        )
        assert result.returncode == _BLOCK
        assert "missing STATUS" in result.stdout

    def test_speculative_pass_language_allowed_without_floor(self) -> None:
        result = _run_response("This SHOULD PASS once CI runs.")
        assert result.returncode == _ALLOW

    def test_likely_pass_language_allowed_without_floor(self) -> None:
        result = _run_response("LIKELY PASS after the gate finishes.")
        assert result.returncode == _ALLOW

    def test_empty_payload_allowed(self) -> None:
        result = _run({})
        assert result.returncode == _ALLOW


class TestStopTaskAuditTranscript:
    def test_repo_work_without_status_blocks(self, tmp_path) -> None:
        tr = _write_transcript(tmp_path, _REPO_WORK_NO_STATUS)
        proc = _run({"session_id": "s1", "transcript_path": str(tr)})
        assert proc.returncode == _BLOCK, proc.stdout + proc.stderr
        assert _block_decision(proc)["decision"] == "block"
        assert "STATUS" in _block_decision(proc)["reason"]

    def test_pass_with_full_proof_allows(self, tmp_path) -> None:
        tr = _write_transcript(tmp_path, _PASS_FULL_PROOF)
        proc = _run({"session_id": "s2", "transcript_path": str(tr)})
        assert proc.returncode == _ALLOW, proc.stdout + proc.stderr
        assert "decision" not in proc.stdout

    def test_pass_missing_proof_blocks(self, tmp_path) -> None:
        tr = _write_transcript(tmp_path, _PASS_MISSING_PROOF)
        proc = _run({"session_id": "s3", "transcript_path": str(tr)})
        assert proc.returncode == _BLOCK, proc.stdout + proc.stderr
        assert "proof" in _block_decision(proc)["reason"].lower()

    def test_active_plan_missing_plan_waves_blocks(self, tmp_path) -> None:
        tr = _write_transcript(tmp_path, _PASS_PLAN_FILE_MISSING_WAVES)
        proc = _run({"session_id": "s_plan_missing", "transcript_path": str(tr)})
        assert proc.returncode == _BLOCK, proc.stdout + proc.stderr
        reason = _block_decision(proc)["reason"].lower()
        assert "plan_waves" in reason or "mini table" in reason

    def test_active_plan_malformed_plan_waves_blocks(self, tmp_path) -> None:
        tr = _write_transcript(tmp_path, _PASS_PLAN_FILE_MALFORMED_WAVES)
        proc = _run({"session_id": "s_plan_malformed", "transcript_path": str(tr)})
        assert proc.returncode == _BLOCK, proc.stdout + proc.stderr
        reason = _block_decision(proc)["reason"].lower()
        assert "plan_waves" in reason or "wave | state | summary" in reason

    def test_active_plan_with_plan_waves_allows(self, tmp_path) -> None:
        tr = _write_transcript(tmp_path, _PASS_PLAN_FILE_WITH_WAVES)
        proc = _run({"session_id": "s_plan_ok", "transcript_path": str(tr)})
        assert proc.returncode == _ALLOW, proc.stdout + proc.stderr
        assert "decision" not in proc.stdout

    def test_plan_complete_all_complete_waves_allows(self, tmp_path) -> None:
        tr = _write_transcript(tmp_path, _PASS_PLAN_COMPLETE_ALL_COMPLETE)
        proc = _run({"session_id": "s_plan_complete_ok", "transcript_path": str(tr)})
        assert proc.returncode == _ALLOW, proc.stdout + proc.stderr
        assert "decision" not in proc.stdout

    def test_missing_transcript_file_allows(self, tmp_path) -> None:
        proc = _run({"session_id": "s4", "transcript_path": str(tmp_path / "absent.jsonl")})
        assert proc.returncode == _ALLOW
        assert "decision" not in proc.stdout

    def test_malformed_payload_allows(self) -> None:
        proc = _run("this is not json {")
        assert proc.returncode == _ALLOW
        assert "decision" not in proc.stdout


class TestStopTaskAuditBackwardCompat:
    def test_inline_tool_info_response_still_blocks(self) -> None:
        # Legacy/synthetic payload shape (tool_info.response) must still be honored.
        proc = _run({"session_id": "s5", "tool_info": {"response": _REPO_WORK_NO_STATUS}})
        assert proc.returncode == _BLOCK
        assert _block_decision(proc)["decision"] == "block"


class TestStopTaskAuditFalseBlockFix:
    """Regression tests: the old 'GATE in prose' / 'CREATED in prose' false-blocks are gone."""

    def test_prose_with_gate_word_and_no_floor_signals_allows(self, tmp_path) -> None:
        # Old code: "GATE" in repo_work_cues -> repo_work_present=True, no STATUS -> block.
        # New code: detect() sees no STATUS and no floor signals -> (None, []) -> allow.
        text = (
            "This design covers the north-star gate and its role in the enforcement surface. "
            "No code was changed or committed in this turn."
        )
        tr = _write_transcript(tmp_path, text)
        proc = _run({"session_id": "fb1", "transcript_path": str(tr)})
        assert proc.returncode == _ALLOW, proc.stdout + proc.stderr

    def test_prose_with_created_word_and_no_floor_signals_allows(self, tmp_path) -> None:
        # Old code: "CREATED" in repo_work_cues -> repo_work_present=True, no STATUS -> block.
        # New code: detect() sees no STATUS and no floor signals -> (None, []) -> allow.
        text = "I created a design document and outlined the approach. No edits made."
        tr = _write_transcript(tmp_path, text)
        proc = _run({"session_id": "fb2", "transcript_path": str(tr)})
        assert proc.returncode == _ALLOW, proc.stdout + proc.stderr

    def test_prose_with_implemented_word_and_no_floor_signals_allows(self, tmp_path) -> None:
        # Old code: "IMPLEMENTED" in repo_work_cues -> would block with no STATUS.
        text = "Discussed how the feature could be implemented. Analysis only, no edits."
        tr = _write_transcript(tmp_path, text)
        proc = _run({"session_id": "fb3", "transcript_path": str(tr)})
        assert proc.returncode == _ALLOW, proc.stdout + proc.stderr

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
        assert proc.returncode == _BLOCK, proc.stdout + proc.stderr
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
        assert proc.returncode == _BLOCK, proc.stdout + proc.stderr
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
            assert proc.returncode == _ALLOW, f"{session}: " + proc.stdout + proc.stderr
