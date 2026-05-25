"""W4.1: apps env → IncrementalRepairContract.max_delta_tokens (no core edits)."""

from __future__ import annotations

import json
from pathlib import Path

from agentic_core.L2_execution.regen.delta_shape_guard import estimate_token_count
from agentic_core.L2_execution.regen.prompt_lock import DEFAULT_MAX_DELTA_TOKENS
from apps_rg.runtime.sections.executive_summary_judge_remediation import (
    collect_judge_remediation_delta_lines,
)
from apps_rg.runtime.sections.executive_summary_repair_policy import (
    REGEN_MAX_DELTA_TOKENS_DEFAULT,
    REGEN_MAX_DELTA_TOKENS_HARD_CAP,
    judge_regen_max_delta_tokens,
)
from apps_rg.runtime.sections.executive_summary_same_authority_regen_bridge import (
    build_incremental_repair_contract,
)


def test_regen_max_delta_tokens_defaults(monkeypatch) -> None:
    monkeypatch.delenv("APPS_RG_EXEC_SUMMARY_REGEN_MAX_DELTA_TOKENS", raising=False)
    assert judge_regen_max_delta_tokens() == REGEN_MAX_DELTA_TOKENS_DEFAULT == 512


def test_regen_max_delta_tokens_env_clamped(monkeypatch) -> None:
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_REGEN_MAX_DELTA_TOKENS", "900")
    assert judge_regen_max_delta_tokens() == REGEN_MAX_DELTA_TOKENS_HARD_CAP
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_REGEN_MAX_DELTA_TOKENS", "640")
    assert judge_regen_max_delta_tokens() == 640


def test_build_incremental_repair_contract_sets_max_delta_tokens(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_REGEN_MAX_DELTA_TOKENS", "600")
    (tmp_path / "compiled_prompt_artifact.json").write_text(
        json.dumps(
            {
                "compilation_hash": "c1",
                "replay_key": "rk",
                "policy_hash": "p",
                "blueprint_hash": "b",
                "registry_digest_set": [],
                "target_model": "qwen-test",
                "target_provider": "vllm",
            }
        ),
        encoding="utf-8",
    )
    contract = build_incremental_repair_contract(
        messages=[{"role": "system", "content": "SYS"}, {"role": "user", "content": "USER"}],
        provider_payload={"model": "qwen-test"},
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
    assert contract.max_delta_tokens == 600


def test_compact_dimension_delta_passes_shape_guard_at_default_cap() -> None:
    """Regression: compact judge deltas must fit default 512-token core guard."""
    judge = {
        "provider_key": "anthropic_claude",
        "pass": False,
        "findings": ["stacked bullets"],
        "dimension_verdicts": {
            "executive_signal": {"pass": False, "severity": "major", "codes": ["bullet_stack"]},
            "synthesis_quality": {
                "pass": False,
                "severity": "major",
                "codes": ["sequential_achievement_stack"],
            },
        },
    }
    lines = collect_judge_remediation_delta_lines(
        [judge],
        unused_fact_ids=[],
        allowed_fact_count=8,
        prior_word_count=120,
        prior_ledger_rows=6,
        compact=True,
    )
    joined = "\n".join(lines)
    assert estimate_token_count(joined) <= DEFAULT_MAX_DELTA_TOKENS
