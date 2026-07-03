"""Tests for the apps_rg inline-evidence Stop gate.

The gate protects the chat-delivery contract: producer-side apps_rg JSON can pass
while the final assistant response still fails if mandatory runtime evidence is not
pasted inline.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from io import StringIO
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
HOOKS_DIR = REPO_ROOT / ".codex" / "hooks"
GATE = HOOKS_DIR / "stop_apps_rg_inline_evidence_gate.py"


@pytest.fixture()
def gate_mod(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.syspath_prepend(str(HOOKS_DIR))
    name = "_stop_apps_rg_inline_evidence_gate_test"
    spec = importlib.util.spec_from_file_location(name, GATE)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    monkeypatch.delenv("APPS_RG_INLINE_EVIDENCE_GATE_BYPASS", raising=False)
    return mod


def _run(mod, response_text: str, monkeypatch: pytest.MonkeyPatch, session: str = "s1") -> int:
    payload = json.dumps({"session_id": session, "tool_info": {"response": response_text}})
    monkeypatch.setattr(sys, "stdin", StringIO(payload))
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    return mod.main()


def _run_transcript(
    mod,
    response_text: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    session: str = "t1",
    prior_assistant_text: str = "",
) -> int:
    transcript = tmp_path / "transcript.jsonl"
    lines = [
        json.dumps({"type": "user", "message": {"role": "user", "content": "run apps_rg"}}),
    ]
    if prior_assistant_text:
        lines.append(
            json.dumps(
                {
                    "type": "assistant",
                    "message": {
                        "role": "assistant",
                        "content": [{"type": "text", "text": prior_assistant_text}],
                    },
                }
            )
        )
    lines.append(
        json.dumps(
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": response_text}],
                },
            }
        )
    )
    transcript.write_text("\n".join(lines) + "\n", encoding="utf-8")
    payload = json.dumps({"session_id": session, "transcript_path": str(transcript)})
    monkeypatch.setattr(sys, "stdin", StringIO(payload))
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    return mod.main()


def _write_run(tmp_path: Path) -> tuple[Path, dict]:
    run_dir = tmp_path / "artifacts" / "rg_b_20260703_090203"
    run_dir.mkdir(parents=True)
    inline = {
        "schema_version": "apps_rg.inline_required_output.v1",
        "immutable_section_order": [
            "bcg",
            "section_lane_summary_table",
            "resume_docx_full_version_inline",
        ],
        "bcg": {
            "title": "BCG Executive Output - apps_rg Run",
            "section_order": [
                "executive_answer",
                "p0_p1_px_recommendations",
                "board_level_readout",
                "issue_tree",
                "recommended_next_move",
                "evidence_map",
            ],
            "executive_answer": "The run is blocked and must not authorize a final resume.",
            "p0_p1_px_recommendations": {
                "columns": ["priority", "recommendation", "evidence", "gate_outcome"],
                "rows": [
                    {
                        "priority": "P0",
                        "recommendation": "Fix first blocked lane before rerun.",
                        "evidence": "lane_dependency_contract",
                        "gate_outcome": "Downstream lanes cannot prove product authority.",
                    }
                ],
            },
            "board_level_readout": {
                "columns": ["question", "answer"],
                "rows": [{"question": "Final product authorized?", "answer": "False"}],
            },
            "issue_tree": [
                {
                    "section": "executive_summary",
                    "classification": "P0_STATIC_MANUAL_BRIEF_USED",
                    "root_cause": "Downstream lane scheduled without upstream token.",
                    "evidence": ["lane_dependency_contract"],
                    "causal_allocation": {},
                    "required_implementation_plan": ["Require an upstream token before scheduling downstream lanes."],
                }
            ],
            "recommended_next_move": ["Fix P0 gates before rerun."],
            "evidence_map": [{"label": "Mandatory run ledger", "path": str(run_dir / "APPS_RG_MANDATORY_RUN_OUTPUT.md")}],
        },
        "section_lane_summary_table": {
            "title": "Section Lane Summary Table",
            "columns": [
                "order",
                "section",
                "r1a",
                "r1b",
                "lane_record",
                "provider_call_attempted",
                "primary_provider",
                "primary_model_observed",
                "pooling_selector_llm",
                "secondary_provider",
                "secondary_model_observed",
                "generation_status",
                "judges_run",
                "judge_models_scores",
                "judge_retry_fallback",
                "x2",
                "x3",
                "past_fail_blocker",
                "display_output",
                "l6_evidence",
            ],
            "rows": [
                {
                    "order": 1,
                    "section": "headline",
                    "r1a": "PASS",
                    "r1b": "PASS",
                    "lane_record": "YES",
                    "provider_call_attempted": True,
                    "primary_provider": "anthropic",
                    "primary_model_observed": "claude-test",
                    "pooling_selector_llm": "YES",
                    "secondary_provider": "openai",
                    "secondary_model_observed": "gpt-test",
                    "generation_status": "REAL_LLM",
                    "judges_run": "YES",
                    "judge_models_scores": "judge-a=0.91",
                    "judge_retry_fallback": "none",
                    "x2": "PASS",
                    "x3": "X3_ALLOW",
                    "past_fail_blocker": "none",
                    "display_output": "PRESENT",
                    "l6_evidence": "PRESENT",
                },
                {
                    "order": 2,
                    "section": "executive_summary",
                    "r1a": "PASS",
                    "r1b": "PASS",
                    "lane_record": "YES",
                    "provider_call_attempted": False,
                    "primary_provider": "NOT_OBSERVED",
                    "primary_model_observed": "NOT_OBSERVED",
                    "pooling_selector_llm": "NO",
                    "secondary_provider": "NOT_OBSERVED",
                    "secondary_model_observed": "NOT_OBSERVED",
                    "generation_status": "PRE_RUN_BLOCKED",
                    "judges_run": "NO",
                    "judge_models_scores": "NOT_OBSERVED",
                    "judge_retry_fallback": "blocked",
                    "x2": "BLOCK",
                    "x3": "X3_BLOCK",
                    "past_fail_blocker": "missing upstream token",
                    "display_output": "MISSING",
                    "l6_evidence": "NOT_OBSERVED",
                },
            ],
        },
        "resume_docx_full_version_inline": {
            "title": "Resume DOCX Full Version Inline",
            "source": "FINAL_RESUME_OUTPUT.txt rendered from the same final-resume spine used for outputs/resume.docx.",
            "text": "Amit Ayer\n\nAI Partnerships Leader\n\nBuilt governed AI systems for partner-facing architecture.",
        },
    }
    payload = {"inline_required_output": inline}
    (run_dir / "APPS_RG_MANDATORY_RUN_OUTPUT.json").write_text(json.dumps(payload), encoding="utf-8")
    return run_dir, inline


def _full_inline_response(run_dir: Path, inline: dict) -> str:
    rows = inline["section_lane_summary_table"]["rows"]
    return f"""
STATUS: FAIL

## apps_rg Runtime Evidence

# apps_rg Run Summary

Run root: `@{run_dir}`

## Locked BCG Output

# BCG Executive Output - apps_rg Run

## Executive Answer

{inline["bcg"]["executive_answer"]}

| Priority | Recommendation | Evidence | Gate / Outcome |
|---|---|---|---|
| `P0` | Fix first blocked lane before rerun. | `lane_dependency_contract` | Downstream lanes cannot prove product authority. |

## Board-Level Readout

| Question | Answer |
|---|---|
| Final product authorized? | `False` |

## Issue Tree

- `executive_summary`: P0_STATIC_MANUAL_BRIEF_USED
  - Root cause: Downstream lane scheduled without upstream token.

## Locked Section Lane Summary Table

| # | Section | R1A | R1B | Lane record | Provider call attempted | Primary provider | Primary model observed | Pooling selector LLM | Secondary provider | Secondary model observed | Generation status | Judges run | Judge models / scores | Judge retry / fallback | X2 | X3 | Past fail / blocker | Display output | L6 evidence |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `{rows[0]["section"]}` | `PASS` | `PASS` | `YES` | `True` | `anthropic` | `claude-test` | `YES` | `openai` | `gpt-test` | `{rows[0]["generation_status"]}` | `YES` | `judge-a=0.91` | `none` | `PASS` | `{rows[0]["x3"]}` | `none` | `{rows[0]["display_output"]}` | `PRESENT` |
| 2 | `{rows[1]["section"]}` | `PASS` | `PASS` | `YES` | `False` | `NOT_OBSERVED` | `NOT_OBSERVED` | `NO` | `NOT_OBSERVED` | `NOT_OBSERVED` | `{rows[1]["generation_status"]}` | `NO` | `NOT_OBSERVED` | `blocked` | `BLOCK` | `{rows[1]["x3"]}` | `missing upstream token` | `{rows[1]["display_output"]}` | `NOT_OBSERVED` |

## Resume DOCX Full Version Inline

Source: `FINAL_RESUME_OUTPUT.txt` rendered from the same final-resume spine used for `outputs/resume.docx`.

```text
{inline["resume_docx_full_version_inline"]["text"]}
```
"""


class TestAppsRgInlineEvidenceGate:
    def test_summary_link_only_response_fails(self, gate_mod, monkeypatch, tmp_path, capsys) -> None:
        run_dir, _inline = _write_run(tmp_path)
        response = (
            "STATUS: FAIL\n"
            "apps_rg run evidence is saved at "
            f"`{run_dir / 'APPS_RG_MANDATORY_RUN_OUTPUT.json'}` and "
            f"`{run_dir / 'RUN_SUMMARY_RENDERED.md'}`."
        )
        rc = _run(gate_mod, response, monkeypatch)
        assert rc == 2
        decision = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
        assert decision["decision"] == "block"
        assert "must paste mandatory apps_rg runtime evidence inline" in decision["reason"]
        assert "## Locked BCG Output" in decision["reason"]

    def test_full_inline_rendered_response_passes(self, gate_mod, monkeypatch, tmp_path, capsys) -> None:
        run_dir, inline = _write_run(tmp_path)
        assert _run(gate_mod, _full_inline_response(run_dir, inline), monkeypatch) == 0
        assert "decision" not in capsys.readouterr().out

    def test_headings_without_required_body_fail(self, gate_mod, monkeypatch, tmp_path, capsys) -> None:
        run_dir, _inline = _write_run(tmp_path)
        response = f"""
STATUS: FAIL

## apps_rg Runtime Evidence

Run root: `@{run_dir}`

## Locked BCG Output

## Locked Section Lane Summary Table

## Resume DOCX Full Version Inline
"""
        rc = _run(gate_mod, response, monkeypatch)
        assert rc == 2
        reason = json.loads(capsys.readouterr().out.strip().splitlines()[-1])["reason"]
        assert "bcg.body_missing" in reason
        assert "resume_docx_full_version_inline.body_missing" in reason

    def test_incomplete_lane_table_rows_fail(self, gate_mod, monkeypatch, tmp_path, capsys) -> None:
        run_dir, inline = _write_run(tmp_path)
        response = "\n".join(
            line
            for line in _full_inline_response(run_dir, inline).splitlines()
            if not line.startswith("| 2 |")
        )
        rc = _run(gate_mod, response, monkeypatch)
        assert rc == 2
        reason = json.loads(capsys.readouterr().out.strip().splitlines()[-1])["reason"]
        assert "section_lane_summary_table.row_count expected=2 observed=1" in reason

    def test_real_transcript_payload_is_enforced(self, gate_mod, monkeypatch, tmp_path, capsys) -> None:
        run_dir, _inline = _write_run(tmp_path)
        response = f"apps_rg run done; see `{run_dir / 'APPS_RG_MANDATORY_RUN_OUTPUT.json'}`."
        rc = _run_transcript(gate_mod, response, monkeypatch, tmp_path)
        assert rc == 2
        assert json.loads(capsys.readouterr().out.strip().splitlines()[-1])["decision"] == "block"

    def test_transcript_context_triggers_gate_when_final_message_is_terse(
        self, gate_mod, monkeypatch, tmp_path, capsys
    ) -> None:
        run_dir, _inline = _write_run(tmp_path)
        prior = (
            "Ran `python -m apps_rg` with watch dir "
            f"`{run_dir}` and emitted `{run_dir / 'APPS_RG_MANDATORY_RUN_OUTPUT.json'}`."
        )
        response = "STATUS: FAIL\nCOMMANDS_RUN:\n- apps_rg run completed\nARTIFACTS:\n- see run directory"

        rc = _run_transcript(gate_mod, response, monkeypatch, tmp_path, prior_assistant_text=prior)

        assert rc == 2
        reason = json.loads(capsys.readouterr().out.strip().splitlines()[-1])["reason"]
        assert "## Locked BCG Output" in reason


class TestAppsRgInlineEvidenceGateRegistration:
    def test_hook_registered_in_stop_chain(self) -> None:
        settings = json.loads((REPO_ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
        cmds = [h["command"] for group in settings["hooks"]["Stop"] for h in group["hooks"]]
        assert any("stop_apps_rg_inline_evidence_gate.py" in c for c in cmds), cmds
