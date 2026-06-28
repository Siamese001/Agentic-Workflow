"""W3: apps_rg executive_summary delegates prescriptive regen to core runner."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from agentic_core.L2_execution.regen.prompt_lock import PROMPT_LOCK_GENERIC
from apps_rg.runtime.sections.executive_summary_judge_remediation import (
    build_judge_remediation_prescriptive_delta_message,
    collect_judge_remediation_delta_lines,
    retry_provider_for_judge_remediation,
)
from apps_rg.runtime.sections.executive_summary_same_authority_regen_bridge import (
    build_incremental_repair_contract,
    messages_to_prompt_messages,
)


def _soft_judge() -> dict:
    return {
        "provider_key": "anthropic_claude",
        "provider_name": "anthropic_claude",
        "evaluator_mode": "MODEL_BACKED",
        "provider_status": "MODEL_BACKED_FAIL",
        "pass": False,
        "decisive_failure": False,
        "normalized_score": 0.5,
        "normalized_threshold": 0.8,
        "findings": ["weak synthesis weave"],
        "fail_reasons": [],
    }


def test_prescriptive_delta_uses_core_prompt_lock_not_apps_duplicate() -> None:
    msg = build_judge_remediation_prescriptive_delta_message(
        x1d_judges=[_soft_judge()],
        unused_fact_ids=[],
        allowed_fact_count=8,
        prior_resume_display_text="Anchor sentence one.",
        prior_word_count=42,
        prior_ledger_rows=6,
    )
    assert "REGEN_DELTA_v1" in msg
    assert PROMPT_LOCK_GENERIC.split(".")[0] in msg
    assert "Do NOT reinterpret ALLOWED_SOURCE_FACT_IDS" not in msg
    assert "ANCHOR_DRAFT" not in msg
    assert "JUDGE_DELTA" in msg or "synthesis" in msg


def test_collect_delta_lines_includes_x2_floor() -> None:
    lines = collect_judge_remediation_delta_lines(
        [_soft_judge()],
        unused_fact_ids=[],
        allowed_fact_count=8,
        prior_word_count=100,
        prior_ledger_rows=5,
    )
    joined = "\n".join(lines)
    assert "X2_FLOOR" in joined or "100" in joined


def test_messages_to_prompt_messages_extracts_system_and_user() -> None:
    pm = messages_to_prompt_messages(
        [
            {"role": "system", "content": "SYS"},
            {"role": "user", "content": "USER"},
        ],
    )
    assert pm.system_text() == "SYS"
    assert pm.user_text() == "USER"


def test_retry_provider_delegates_to_core_runner(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN", "1")
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN_PRESCRIPTIVE_DELTA", "1")
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_CORE_SAME_AUTHORITY_REGEN", "1")
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN_LEGACY_BLOCK", "0")

    (tmp_path / "compiled_prompt_artifact.json").write_text(
        json.dumps(
            {
                "compilation_hash": "compile-abc",
                "replay_key": "rk-1",
                "policy_hash": "pol-1",
                "blueprint_hash": "bp-1",
                "registry_digest_set": ["r1"],
                "target_model": "retired_provider-test",
                "target_provider": "local_model_server",
                "trace_id": "trace-1",
                "run_id": "run-1",
            },
        ),
        encoding="utf-8",
    )

    parsed = {
        "resume_display_text": "Six sentences of anchor text here for testing regen.",
        "claim_ledger": [{"fact_id": "f1", "claim_text": "Led platform."}],
    }
    raw = json.dumps(parsed)

    def _fake_run(**kwargs):
        contract = kwargs["contract"]
        from agentic_core.L2_execution.regen import SameAuthorityRegenRunner

        def _gen(msgs: list[dict[str, str]]) -> dict[str, object]:
            return {
                "content": json.dumps(
                    {
                        **parsed,
                        "resume_display_text": "Revised six sentences for regen path.",
                    },
                ),
            }

        result = SameAuthorityRegenRunner().run(contract, provider_generate=_gen)
        from apps_rg.runtime.sections.executive_summary_lane import write_json

        receipt_dict = {
            "accepted": result.accepted,
            "same_authority_regen_receipt": result.receipt.as_dict() if result.receipt else {},
        }
        write_json(tmp_path / "same_authority_regen_receipt.json", receipt_dict)
        return (
            result.regenerated_text,
            receipt_dict,
            result.receipt.as_dict() if result.receipt else {},
            result.chat_messages,
        )

    monkeypatch.setattr(
        "apps_rg.runtime.sections.executive_summary_same_authority_regen_bridge.run_core_same_authority_regen",
        _fake_run,
    )

    new_raw, new_parsed, receipt = retry_provider_for_judge_remediation(
        [{"role": "system", "content": "SYS"}, {"role": "user", "content": "USER"}],
        {"model": "retired_provider-test", "temperature": 0.1, "max_tokens": 1024},
        raw,
        parsed,
        x1d_judges=[_soft_judge()],
        trigger_receipt={"trigger_mode": "quorum_soft_fail", "parent_attempt_receipt_id": "a1"},
        selected_fact_plan={"facts": [{"fact_id": "f1"}]},
        allowed_fact_ids={"f1"},
        unused_fact_ids=[],
        artifact_dir=tmp_path,
        run_id="run-1",
        max_attempts=1,
    )
    assert receipt.get("regen_engine") == "core.SameAuthorityRegenRunner"
    assert receipt.get("accepted") is True
    assert "Revised" in str(new_parsed.get("resume_display_text") or "")
    assert (tmp_path / "same_authority_regen_receipt.json").is_file()
