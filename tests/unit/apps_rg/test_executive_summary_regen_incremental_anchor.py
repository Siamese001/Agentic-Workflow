"""W3 — cycle 2 regen anchors prior attempt assistant content."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from apps_rg.runtime.sections.executive_summary_judge_remediation import (
    retry_qwen_for_judge_remediation,
)


def _soft_judge() -> dict:
    return {
        "provider_key": "anthropic_claude",
        "provider_name": "anthropic_claude",
        "evaluator_mode": "MODEL_BACKED",
        "provider_status": "MODEL_BACKED_FAIL",
        "pass": False,
        "findings": ["weak synthesis weave"],
    }


@pytest.fixture
def _regen_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN", "1")
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN_PRESCRIPTIVE_DELTA", "1")
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_CORE_SAME_AUTHORITY_REGEN", "1")
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN_LEGACY_BLOCK", "0")
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN_MAX_ATTEMPTS", "2")
    (tmp_path / "compiled_prompt_artifact.json").write_text(
        json.dumps(
            {
                "compilation_hash": "compile-abc",
                "replay_key": "rk-1",
                "policy_hash": "pol-1",
                "blueprint_hash": "bp-1",
                "registry_digest_set": ["r1"],
                "target_model": "qwen-test",
                "target_provider": "vllm",
                "trace_id": "trace-1",
                "run_id": "run-1",
            },
        ),
        encoding="utf-8",
    )
    return tmp_path


def test_retry_qwen_cycle2_uses_incremental_anchor_parsed(
    _regen_env: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scratch = {
        "resume_display_text": "Scratch S1. Scratch S2. Scratch S3. Scratch S4. Scratch S5. Scratch S6.",
        "claim_ledger": [{"claim_id": "c1", "claim_text": "Led platform.", "source_fact_ids": ["f1"]}],
    }
    prior_attempt = {
        "resume_display_text": "Prior S1. Prior S2. Prior S3. Prior S4. Prior S5. Prior S6.",
        "claim_ledger": [{"claim_id": "c1", "claim_text": "Led platform.", "source_fact_ids": ["f1"]}],
    }
    captured: dict[str, object] = {}

    def _fake_run(**kwargs):
        captured["contract"] = kwargs["contract"]
        from agentic_core.L2_execution.regen import SameAuthorityRegenRunner

        contract = kwargs["contract"]

        def _gen(msgs: list[dict[str, str]]) -> dict[str, object]:
            captured["messages"] = msgs
            return {
                "content": json.dumps(
                    {
                        **prior_attempt,
                        "resume_display_text": "Next S1. Next S2. Next S3. Next S4. Next S5. Next S6.",
                    },
                ),
            }

        result = SameAuthorityRegenRunner().run(contract, provider_generate=_gen)
        return (
            result.regenerated_text,
            {"accepted": result.accepted},
            result.receipt.as_dict() if result.receipt else {},
            result.chat_messages,
        )

    monkeypatch.setattr(
        "apps_rg.runtime.sections.executive_summary_same_authority_regen_bridge.run_core_same_authority_regen",
        _fake_run,
    )

    _new_raw, _new_parsed, receipt = retry_qwen_for_judge_remediation(
        [{"role": "system", "content": "SYS"}, {"role": "user", "content": "USER"}],
        {"model": "qwen-test", "temperature": 0.1, "max_tokens": 1024},
        json.dumps(scratch),
        scratch,
        x1d_judges=[_soft_judge()],
        trigger_receipt={"trigger_mode": "quorum_soft_fail", "parent_attempt_receipt_id": "a1"},
        selected_fact_plan={"facts": [{"fact_id": "f1"}]},
        allowed_fact_ids={"f1"},
        unused_fact_ids=[],
        artifact_dir=_regen_env,
        run_id="run-1",
        max_attempts=1,
        cycle_index=1,
        incremental_anchor_parsed=prior_attempt,
        baseline_resume_display_text=str(scratch["resume_display_text"]),
        prior_cycle_judges=[_soft_judge()],
    )

    contract = captured["contract"]
    assert contract is not None
    assert receipt.get("regen_anchor_source") == "incremental_prior_attempt"
    anchor_payload = json.loads(str(contract.anchor_output_text))
    assert "Prior S2" in anchor_payload["resume_display_text"]
    assert "Scratch S2" not in anchor_payload["resume_display_text"]
    messages = captured.get("messages") or []
    assistant_turns = [m for m in messages if m.get("role") == "assistant"]
    assert assistant_turns
    assert "Prior S2" in assistant_turns[-1]["content"]
    delta_blob = "\n".join(contract.delta_lines)
    assert "PRIOR_ATTEMPT_SUMMARY" in delta_blob
    assert "Next S1" in str(_new_parsed.get("resume_display_text") or "")
