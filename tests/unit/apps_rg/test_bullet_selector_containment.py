"""W5 (AIG E2E remediation, E2E-09/E2E-10) — truthful block labels + empty-selection signal.

Deterministic, hermetic. No provider calls. Covers the shared helpers that contain the
bullet-lane empty-selection failure mode:

1. truthful_block_reason: never says 'provider blocked' when the provider produced REAL_LLM
   output (the E2E-09/10 mislabel).
2. summarize_selector_emptiness: flags an empty selection and records the sub-threshold scores
   so a downstream block is truthful and the < 0.72 selector scores are observable.
3. should_short_circuit_empty_selection (W4.4, G16): pre-X2 short-circuit predicate truth
   table + write_empty_selection_short_circuit_artifacts single-true-reason bundle.
"""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from apps_rg.runtime.reasoning.bullet_lane_generation import (
    SELECTOR_EMPTY_BLOCK_REASON,
    empty_selection_min_bullets,
    should_short_circuit_empty_selection,
    summarize_selector_emptiness,
    truthful_block_reason,
)


def _result(err: str | None) -> SimpleNamespace:
    return SimpleNamespace(exact_provider_error=err)


def test_truthful_reason_uses_exact_provider_error_when_present() -> None:
    assert truthful_block_reason(_result("timeout"), "BLOCKED", "") == "timeout"


def test_truthful_reason_real_llm_never_says_provider_blocked() -> None:
    # Provider produced output -> must NOT claim provider blocked.
    reason = truthful_block_reason(_result(None), "REAL_LLM", "")
    assert reason != "provider blocked"
    assert "selector" in reason or "parse" in reason


def test_truthful_reason_real_llm_preserves_existing_parse_error() -> None:
    assert truthful_block_reason(_result(None), "REAL_LLM", "bad_json") == "bad_json"


def test_truthful_reason_genuine_block_still_says_provider_blocked() -> None:
    assert truthful_block_reason(_result(None), "BLOCKED", "") == "provider blocked"
    assert truthful_block_reason(None, "BLOCKED", "") == "provider blocked"


def test_empty_selection_flagged_with_block_reason_and_scores() -> None:
    pool = SimpleNamespace(selections=[], selection_mode="fallback_empty")
    gate = SimpleNamespace(bullets_in_merged=0)
    out = summarize_selector_emptiness(pool=pool, gate=gate)
    assert out["selector_empty"] is True
    assert out["selector_block_reason"] == SELECTOR_EMPTY_BLOCK_REASON
    assert out["selector_subthreshold_scores"] == []
    assert out["selector_selection_count"] == 0


def test_subthreshold_scores_recorded_when_present() -> None:
    # Selections exist but merged is empty (all below threshold) -> still empty, scores captured.
    pool = SimpleNamespace(
        selections=[{"score": 0.61}, {"score": 0.55}], selection_mode="claude_top_n"
    )
    gate = SimpleNamespace(bullets_in_merged=0)
    out = summarize_selector_emptiness(pool=pool, gate=gate)
    assert out["selector_empty"] is True  # bullets_in_merged == 0
    assert out["selector_subthreshold_scores"] == [0.61, 0.55]
    assert out["selector_block_reason"] == SELECTOR_EMPTY_BLOCK_REASON


def test_nonempty_selection_is_not_flagged_empty() -> None:
    pool = SimpleNamespace(
        selections=[{"score": 0.81}, {"score": 0.79}], selection_mode="claude_top_n"
    )
    gate = SimpleNamespace(bullets_in_merged=6)
    out = summarize_selector_emptiness(pool=pool, gate=gate)
    assert out["selector_empty"] is False
    assert "selector_block_reason" not in out
    assert out["selector_subthreshold_scores"] == [0.81, 0.79]


# ---------------------------------------------------------------------------
# W4.4 (G16): should_short_circuit_empty_selection truth table
# ---------------------------------------------------------------------------


def _pool_gen_meta(**overrides: object) -> dict:
    meta: dict = {
        "generation_mode": "qwen_employment_pool_claude_top_n_regen",
        "total_paths_executed": 4,
        "claude_selection_count": 0,
        "min_selection_score": 0.72,
        "regen_rounds_executed": 2,
        "selection_mode": "fallback_empty",
        "selection_gate": {"ok": False, "slots_missing": ["bul_unify_001", "bul_unify_002"]},
        "selector_subthreshold_scores": [0.61, 0.55, 0.8],
    }
    meta.update(overrides)
    return meta


def test_short_circuit_fires_on_real_llm_employment_pool_empty_merge() -> None:
    fire, reason = should_short_circuit_empty_selection(_pool_gen_meta(), [], "REAL_LLM")
    assert fire is True
    assert reason.startswith("EMPTY_SELECTION_PRE_X2:")
    assert "paths=4" in reason
    assert "selections=0" in reason
    assert "merged=0" in reason
    assert "source_fact_id_not_allowed:0" in reason
    assert "numeric_token_not_entailed:0" in reason
    assert "below_min_score:2" in reason
    assert "slots_missing=[bul_unify_001, bul_unify_002]" in reason


def test_short_circuit_never_fires_on_blocked_provider() -> None:
    # Provider-BLOCKED runs keep today's path — G16 scope is REAL_LLM only.
    assert should_short_circuit_empty_selection(_pool_gen_meta(), [], "BLOCKED") == (False, "")
    assert should_short_circuit_empty_selection(_pool_gen_meta(), [], "OFFLINE_CONTRACT_STUB") == (
        False,
        "",
    )
    assert should_short_circuit_empty_selection(_pool_gen_meta(), [], "") == (False, "")


def test_short_circuit_never_fires_on_non_employment_pool_generation() -> None:
    assert should_short_circuit_empty_selection(
        _pool_gen_meta(generation_mode="singleton"), [], "REAL_LLM"
    ) == (False, "")
    assert should_short_circuit_empty_selection(None, [], "REAL_LLM") == (False, "")


def test_short_circuit_never_fires_when_merge_meets_floor() -> None:
    bullets = [{"bullet_id": f"bul_unify_{i:03d}"} for i in range(1, 7)]
    assert should_short_circuit_empty_selection(_pool_gen_meta(), bullets, "REAL_LLM") == (
        False,
        "",
    )


def test_short_circuit_bypass_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_EMPTY_SELECTION_SHORT_CIRCUIT_BYPASS", "1")
    assert should_short_circuit_empty_selection(_pool_gen_meta(), [], "REAL_LLM") == (False, "")


def test_short_circuit_min_bullets_env_raises_floor(monkeypatch: pytest.MonkeyPatch) -> None:
    assert empty_selection_min_bullets() == 1
    monkeypatch.setenv("APPS_RG_EMPTY_SELECTION_MIN_BULLETS", "6")
    assert empty_selection_min_bullets() == 6
    bullets = [{"bullet_id": f"bul_unify_{i:03d}"} for i in range(1, 4)]
    fire, reason = should_short_circuit_empty_selection(_pool_gen_meta(), bullets, "REAL_LLM")
    assert fire is True
    assert "merged=3" in reason


def test_short_circuit_reason_folds_in_validity_and_entailment_receipt_counts(
    tmp_path: Path,
) -> None:
    (tmp_path / "bullet_pool_candidate_validity.json").write_text(
        json.dumps(
            {
                "paths": [
                    {
                        "rejections": [
                            {"bullet_id": "bul_unify_001", "reason": "source_fact_id_not_allowed"},
                            {"bullet_id": "bul_unify_002", "reason": "missing_source_fact_ids"},
                        ]
                    },
                    {
                        "rejections": [
                            {"bullet_id": "bul_unify_003", "reason": "source_fact_id_not_allowed"},
                        ]
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "bullet_pool_fact_entailment.json").write_text(
        json.dumps({"rounds": [{"excluded_total": 2}, {"excluded_total": 1}]}),
        encoding="utf-8",
    )
    fire, reason = should_short_circuit_empty_selection(
        _pool_gen_meta(), [], "REAL_LLM", artifact_dir=tmp_path
    )
    assert fire is True
    assert "source_fact_id_not_allowed:2" in reason
    assert "numeric_token_not_entailed:3" in reason


# ---------------------------------------------------------------------------
# W4.4 (G16): write_empty_selection_short_circuit_artifacts bundle
# ---------------------------------------------------------------------------


def test_empty_selection_writer_emits_single_honest_block_bundle(tmp_path: Path) -> None:
    from apps_rg.runtime.sections.upstream_evidence_block import (
        write_empty_selection_short_circuit_artifacts,
    )

    artifact_dir = tmp_path / "run"
    artifact_dir.mkdir()
    # Pre-written truthful artifacts at the lane insertion point — must NOT be overwritten.
    preserved = {
        "raw_model_output.txt": "RAW_SENTINEL",
        "parsed_output.json": '{"parsed": null, "sentinel": true}',
        "canonical_claim_ledger_v2.json": '{"sentinel": true}',
        "provider_request.json": '{"sentinel": true}',
        "provider_response.json": '{"runtime_generation_status": "REAL_LLM", "sentinel": true}',
        "bullet_pool_selection.json": '{"selections": [], "sentinel": true}',
        "bullet_lane_generation.json": '{"sentinel": true}',
    }
    for name, content in preserved.items():
        (artifact_dir / name).write_text(content, encoding="utf-8")

    reason = "EMPTY_SELECTION_PRE_X2: paths=4 selections=0 merged=0; excluded_by=[...]; slots_missing=[]"
    runtime_payload = {"run_id": "unify_bullets_test_run", "selected_fact_plan": {"facts": []}}
    ctx = write_empty_selection_short_circuit_artifacts(
        repo_root=tmp_path,
        artifact_dir=artifact_dir,
        section_id="unify_bullets",
        provider="external_claude",
        runtime_payload=runtime_payload,
        reason=reason,
        gen_meta={
            "total_paths_executed": 4,
            "claude_selection_count": 0,
            "regen_rounds_executed": 2,
            "selection_mode": "fallback_empty",
            "selection_gate": {"ok": False},
        },
        bullets_in_merged=0,
        output_filename="unify_bullets_output.txt",
    )

    # Skip-list artifacts preserved byte-for-byte.
    for name, content in preserved.items():
        assert (artifact_dir / name).read_text(encoding="utf-8") == content, name

    # Exactly ONE failing X2 row — the X2 wall was never dispatched.
    x2 = json.loads((artifact_dir / "x2_gate_outputs.json").read_text(encoding="utf-8"))
    assert x2["x2_failed"] == 1
    assert x2["x2_passed"] == 0
    assert x2["total_x2_gates"] == 1
    assert x2["failed_gates"] == ["x2_unify_bullets_nonempty_selection_pre_x2"]
    row = x2["gates"][0]
    assert row["gate_id"] == "x2_unify_bullets_nonempty_selection_pre_x2"
    assert row["pass"] is False
    assert row["severity"] == "block"
    assert row["reason"] == reason

    # X3 mirror: X3_BLOCK with the true reason; runtime status stays REAL_LLM.
    x3_doc = json.loads((artifact_dir / "x3_disposition.json").read_text(encoding="utf-8"))
    assert x3_doc["x3_code"] == "X3_BLOCK"
    assert x3_doc["decisive_reason"] == reason
    assert x3_doc["runtime_generation_status"] == "REAL_LLM"
    assert ctx["x3"]["x3_code"] == "X3_BLOCK"

    # L2 output is truthful: provider ran, zero bullets, quality FAIL.
    l2 = json.loads((artifact_dir / "l2_output.json").read_text(encoding="utf-8"))
    assert l2["runtime_generation_status"] == "REAL_LLM"
    assert l2["bullets"] == []
    assert l2["product_quality_status"] == "FAIL"

    # Nothing to judge — X1D saved entirely.
    x1d = json.loads((artifact_dir / "x1d_llm_judge_outputs.json").read_text(encoding="utf-8"))
    assert x1d == {"judges": []}

    receipt = json.loads(
        (artifact_dir / "empty_selection_pre_x2_receipt.json").read_text(encoding="utf-8")
    )
    assert receipt["schema_version"] == "empty_selection_pre_x2_v1"
    assert receipt["section_id"] == "unify_bullets"
    assert receipt["reason"] == reason
    assert receipt["provider_attempted"] is True
    assert receipt["runtime_generation_status"] == "REAL_LLM"
    assert receipt["fired_by"] == "should_short_circuit_empty_selection"
    assert receipt["pool_stats"]["total_paths_executed"] == 4
    assert receipt["regen_rounds_executed"] == 2

    smr = json.loads((artifact_dir / "section_metric_receipt.json").read_text(encoding="utf-8"))
    assert smr["x3_code"] == "X3_BLOCK"
    assert smr["runtime_generation_status"] == "REAL_LLM"

    assert (artifact_dir / "command_output.txt").read_text(encoding="utf-8").strip() == (
        f"unify_bullets: X3_BLOCK: {reason}"
    )
    assert (artifact_dir / "unify_bullets_output.txt").read_text(encoding="utf-8") == ""

    # Blocked ctx dict matches the section_cli_runners consumer contract; X3_BLOCK maps to
    # a non-zero lane exit via _lane_dispatch_status_from_x3.
    from apps_rg.runtime.spine.section_cli_runners import _lane_dispatch_status_from_x3

    assert set(ctx) == {"artifact_dir", "runtime_payload", "x3", "output_text"}
    authorized, exit_status, x3_code = _lane_dispatch_status_from_x3(ctx["x3"])
    assert authorized is False
    assert exit_status == "error"
    assert x3_code == "X3_BLOCK"
