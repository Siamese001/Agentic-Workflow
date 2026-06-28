"""W4.1: regen retry policy — cycle-bounded; full judge feedback in REGEN_DELTA."""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.sections.executive_summary_repair_policy import (
    JUDGE_REGEN_CORE_DELTA_TOKEN_CEILING,
    judge_regen_max_delta_tokens,
)
from apps_rg.runtime.sections.executive_summary_same_authority_regen_bridge import (
    build_incremental_repair_contract,
)


def test_judge_regen_max_delta_tokens_is_fixed_ceiling() -> None:
    assert judge_regen_max_delta_tokens() == JUDGE_REGEN_CORE_DELTA_TOKEN_CEILING


def test_build_incremental_repair_contract_sets_max_delta_tokens(tmp_path: Path) -> None:
    (tmp_path / "compiled_prompt_artifact.json").write_text(
        json.dumps(
            {
                "compilation_hash": "c1",
                "replay_key": "rk",
                "policy_hash": "p",
                "blueprint_hash": "b",
                "registry_digest_set": [],
                "target_model": "retired_provider-test",
                "target_provider": "local_model_server",
            }
        ),
        encoding="utf-8",
    )
    contract = build_incremental_repair_contract(
        messages=[{"role": "system", "content": "SYS"}, {"role": "user", "content": "USER"}],
        provider_payload={"model": "retired_provider-test"},
        x1d_judges=[
            {
                "provider_key": "anthropic_claude",
                "pass": False,
                "findings": ["weak synthesis"],
                "dimension_verdicts": {
                    "executive_signal": {"pass": False, "severity": "major", "codes": ["x"]},
                },
            }
        ],
        trigger_receipt={"trigger_mode": "quorum_soft_fail"},
        unused_fact_ids=[],
        allowed_fact_count=8,
        anchor_output_text="anchor text",
        prior_word_count=100,
        prior_ledger_rows=5,
        artifact_dir=tmp_path,
        run_id="run-w4",
    )
    assert contract.max_delta_tokens == JUDGE_REGEN_CORE_DELTA_TOKEN_CEILING


def test_audit_judge_feedback_pack_never_drops_feedback() -> None:
    from apps_rg.runtime.sections.executive_summary_regen_observability import (
        audit_judge_feedback_pack,
    )

    judges = [
        {
            "provider_key": "anthropic_claude",
            "provider_name": "Anthropic Claude",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_FAIL",
            "pass": False,
            "findings": ["stacked bullets " + ("detail " * 80)],
            "remediation_suggestions": ["fix voice " + ("hint " * 80)],
            "dimension_verdicts": {
                "executive_signal": {"pass": False, "severity": "major", "codes": ["bullet_stack"]},
            },
        },
    ]
    stats = audit_judge_feedback_pack(judges)
    assert stats["judge_feedback_lines_dropped"] == 0
    assert stats.get("dropped_reason") is None
    assert stats["judge_feedback_lines_included"] == stats["judge_feedback_lines_total"]
