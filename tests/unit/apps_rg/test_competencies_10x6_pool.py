"""W4 — competencies graph_8x8 pool (8 paths -> 8 categories) + selector/judge split.

The selector receipt is Anthropic-backed; the formal competencies judge is Gemini-backed.
"""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from apps_rg.runtime.judges.bullet_pool_claude_selector import (
    PoolSelectionResult,
    PoolSelectorUnavailableError,
    run_claude_bullet_pool_selection,
)
from apps_rg.runtime.providers.provider_contract import ProviderResult
from apps_rg.runtime.reasoning.bullet_lane_self_consistency import SelfConsistencyPath
from apps_rg.runtime.reasoning.bullet_lane_generation import generate_bullet_lane_with_sc_and_claude
from apps_rg.runtime.reasoning.competencies_graph_pool import (
    COMPETENCIES_CANDIDATE_CATEGORY_COUNT,
    COMPETENCIES_FINAL_CATEGORY_COUNT,
    COMPETENCIES_SC_PATH_COUNT,
    build_competencies_rejected_neighbor_audit,
    build_competencies_targeting_context,
    evaluate_competencies_selection_quality,
    is_competencies_pool_generation,
    merge_competencies_graph_pool_top_eight,
    min_competencies_selection_score,
)
from apps_rg.runtime.reasoning.employment_bullet_pool import (
    competencies_pool_x1d_judge_rows,
    sc_path_count_for_lane,
)
from apps_rg.runtime.sections.section_product_shape_ssot import section_product_shape


def _cat(label: str, terms: list[str]) -> dict:
    return {
        "category_label": label,
        "terms": [{"text": t, "source_fact_ids": ["bul_001"]} for t in terms],
        "source_fact_ids": ["bul_001"],
    }


def _path_with_categories(
    path_index: int,
    n_categories: int = COMPETENCIES_FINAL_CATEGORY_COUNT,
) -> SelfConsistencyPath:
    return SelfConsistencyPath(
        path_index=path_index,
        temperature=0.35 + path_index * 0.01,
        runtime_generation_status="REAL_LLM",
        raw_output="",
        parsed={
            "competencies": [
                _cat(f"Category_{path_index}_{i}", [f"t{i}a", f"t{i}b"])
                for i in range(n_categories)
            ],
            "claim_ledger": [],
        },
        parse_error="",
        provider_result=None,
    )


class _FakeSelectorJudge:
    def __init__(
        self,
        *,
        provider_key: str = "openai_chatgpt",
        model_name: str = "gpt-5.5",
        passed: bool = True,
        status: str = "MODEL_BACKED_PASS",
        exact_provider_error: str | None = None,
        rationale: str = "yaml_judge_models",
    ) -> None:
        self.judge_id = f"x1d_{provider_key}_bullet_pool_selector"
        self.provider_name = "OpenAI ChatGPT"
        self.provider_key = provider_key
        self.evaluator_mode = "MODEL_BACKED"
        self.provider_status = status
        self.model_name = model_name
        self.provider_available = True
        self.provider_blocked = not passed
        self.exact_provider_error = exact_provider_error
        self.pass_ = passed
        self.rationale = rationale

    def to_dict(self) -> dict[str, object]:
        return {
            "judge_id": self.judge_id,
            "provider_name": self.provider_name,
            "provider_key": self.provider_key,
            "evaluator_mode": self.evaluator_mode,
            "provider_status": self.provider_status,
            "model_name": self.model_name,
            "provider_available": self.provider_available,
            "provider_blocked": self.provider_blocked,
            "exact_provider_error": self.exact_provider_error,
            "pass": self.pass_,
            "pass_": self.pass_,
            "rationale": self.rationale,
        }


def test_competencies_pool_generation_mode_detected() -> None:
    assert is_competencies_pool_generation(
        {"generation_mode": "qwen_competencies_graph_pool_claude_top_8_regen"}
    )
    assert not is_competencies_pool_generation({"generation_mode": "singleton"})


def test_sc_path_count_and_targeting_context_graph_8x8() -> None:
    # Variance-class alignment (2026-06): candidate-category pool is the final exact 8.
    assert sc_path_count_for_lane("competencies") == COMPETENCIES_SC_PATH_COUNT == 8
    ctx = build_competencies_targeting_context(
        {
            "target_title": "SVP",
            "target_company": "Acme",
            "jd_text": "agentic AI",
            "briefing": "platform",
            "proof_pool_metadata": {
                "graph_ref": "artifacts/skills/graph.json",
                "proof_pool_type": "augmented_skills_graph",
                "selected_skill_rows": [{"skill_id": "sk_graph_001"}],
            },
            "selected_fact_plan": {"selection_method": "augmented_skills_graph"},
        },
        allowed_fact_ids={"bul_001"},
        allowed_skill_ids={"sk_graph_001"},
    )
    assert ctx["candidate_category_count"] == COMPETENCIES_CANDIDATE_CATEGORY_COUNT
    assert ctx["final_category_count"] == COMPETENCIES_FINAL_CATEGORY_COUNT
    assert ctx["pool_path_count"] == 8
    assert ctx["proof_pool_type"] == "augmented_skills_graph"
    assert ctx["selection_model"] == "graph_8x8_v1"


def test_section_product_shape_competencies_exactly_eight() -> None:
    shape = section_product_shape("competencies")
    assert "x2_competencies_min_category_count" in shape.required_gate_ids
    assert "graph_8x8" in shape.shape_summary


def test_evaluate_competencies_gate_requires_eight_passing_categories() -> None:
    labels = [f"Cat_{i}" for i in range(COMPETENCIES_FINAL_CATEGORY_COUNT)]
    selections = [
        {"category_label": lab, "path_index": 0, "score": 0.9, "passes": True} for lab in labels
    ]
    merged = {"competencies": [_cat(lab, ["a", "b"]) for lab in labels]}
    gate = evaluate_competencies_selection_quality(
        selections=selections,
        merged_parsed=merged,
        min_score=min_competencies_selection_score(),
    )
    assert gate.ok is True
    assert gate.categories_in_merged == COMPETENCIES_FINAL_CATEGORY_COUNT


def test_merge_competencies_graph_pool_preserves_selector_scores() -> None:
    labels = [f"Category_0_{i}" for i in range(COMPETENCIES_FINAL_CATEGORY_COUNT)]
    scores = [0.91, 0.89, 0.88, 0.86, 0.84, 0.83, 0.81, 0.78]
    selections = [
        {"category_label": lab, "path_index": 0, "score": score, "passes": True}
        for lab, score in zip(labels, scores, strict=True)
    ]
    merged, _ = merge_competencies_graph_pool_top_eight(
        [_path_with_categories(0)],
        selections,
        min_score_threshold=0.72,
    )

    merged_scores = [
        row.get("selection_score")
        for row in (merged.get("competencies") or [])
    ]
    assert merged_scores == scores


def test_competencies_rejected_neighbor_audit_records_unselected_candidates() -> None:
    paths = [_path_with_categories(0), _path_with_categories(1)]
    labels = [f"Category_0_{i}" for i in range(COMPETENCIES_FINAL_CATEGORY_COUNT)]
    selections = [
        {"category_label": lab, "path_index": 0, "score": 0.9 - idx * 0.01, "passes": True}
        for idx, lab in enumerate(labels)
    ]
    merged, source_map = merge_competencies_graph_pool_top_eight(
        paths,
        selections,
        min_score_threshold=0.72,
    )

    audit = build_competencies_rejected_neighbor_audit(
        paths,
        selections,
        merged,
        source_map,
        min_score_threshold=0.72,
    )

    assert audit["schema_version"] == "competencies_rejected_neighbor_audit_v1"
    assert audit["audit_status"] == "present"
    assert audit["candidate_label_count"] == 16
    assert audit["selected_count"] == COMPETENCIES_FINAL_CATEGORY_COUNT
    assert audit["rejected_neighbor_count"] == COMPETENCIES_FINAL_CATEGORY_COUNT
    assert {row["rejection_reason"] for row in audit["rejected_neighbors"]} == {
        "not_selected_by_model"
    }


def test_openai_competencies_selection_emits_eight_categories(monkeypatch: pytest.MonkeyPatch) -> None:
    paths = [_path_with_categories(0)]
    selections = [
        {
            "category_label": f"Category_0_{i}",
            "path_index": 0,
            "score": 0.9,
            "passes": True,
            "rationale": f"slot {i}",
        }
        for i in range(COMPETENCIES_FINAL_CATEGORY_COUNT)
    ]

    monkeypatch.setenv("OPENAI_API_KEY", "fake-openai-key")
    monkeypatch.setattr(
        "apps_rg.runtime.judges.bullet_pool_claude_selector.bootstrap_apps_rg_env",
        lambda: None,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.judges.bullet_pool_claude_selector._call_openai_pool_selector",
        lambda **_: (_FakeSelectorJudge(), {"selections": selections, "pool_summary": {}}),
    )
    pool: PoolSelectionResult = run_claude_bullet_pool_selection(
        section_id="competencies",
        slot_kind="competencies",
        paths=paths,
        targeting_context={
            "allowed_fact_ids": ["bul_001"],
            "allowed_skill_ids": [],
            "resume_support_blob_lower": "bul_001 alpha beta",
        },
        mode="blocked_if_unavailable",
    )
    assert pool.selection_mode == "openai_competencies_top_8_pass"
    assert pool.judge_output is not None
    assert pool.judge_output.provider_key == "openai_chatgpt"
    assert pool.judge_output.model_name == "gpt-5.5"
    comps = pool.merged_parsed.get("competencies") or []
    assert len(comps) == COMPETENCIES_FINAL_CATEGORY_COUNT
    audit = pool.rejected_neighbor_audit
    assert audit is not None
    assert audit["schema_version"] == "competencies_rejected_neighbor_audit_v1"


def test_openai_competencies_selector_fails_closed_without_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    paths = [_path_with_categories(0)]
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(
        "apps_rg.runtime.judges.bullet_pool_claude_selector.bootstrap_apps_rg_env",
        lambda: None,
    )

    with pytest.raises(
        PoolSelectorUnavailableError,
        match="competencies selector unavailable: missing OpenAI credentials",
    ):
        run_claude_bullet_pool_selection(
            section_id="competencies",
            slot_kind="competencies",
            paths=paths,
            targeting_context={
                "allowed_fact_ids": ["bul_001"],
                "allowed_skill_ids": [],
                "resume_support_blob_lower": "bul_001 alpha beta",
            },
            mode="blocked_if_unavailable",
        )


def test_generate_competencies_graph_pool_lane_mocked(monkeypatch: pytest.MonkeyPatch) -> None:
    paths = [_path_with_categories(i, n_categories=COMPETENCIES_FINAL_CATEGORY_COUNT) for i in range(8)]

    class _Judge:
        provider_key = "openai_chatgpt"
        provider_name = "OpenAI ChatGPT"
        model_name = "gpt-5.5"
        provider_status = "MODEL_BACKED_PASS"
        exact_provider_error = None
        pass_ = True
        rationale = "yaml_judge_models"

        def to_dict(self) -> dict[str, object]:
            return {
                "judge_id": "x1d_openai_chatgpt_bullet_pool_selector",
                "provider_name": self.provider_name,
                "provider_key": self.provider_key,
                "provider_status": self.provider_status,
                "model_name": self.model_name,
                "provider_available": True,
                "provider_blocked": False,
                "exact_provider_error": self.exact_provider_error,
                "pass": True,
                "pass_": True,
                "rationale": self.rationale,
            }

    def _fake_paths(**_: object) -> tuple[list[SelfConsistencyPath], ProviderResult]:
        return paths, ProviderResult(
            provider_requested="qwen_vllm",
            provider_attempted=True,
            provider_available=True,
            exact_provider_error=None,
            runtime_generation_status="REAL_LLM",
            model="stub",
            raw_model_output="{}",
            provider_response={},
        )

    monkeypatch.setattr(
        "apps_rg.runtime.reasoning.bullet_lane_generation.run_provider_self_consistency_paths",
        _fake_paths,
    )
    monkeypatch.setenv("OPENAI_API_KEY", "fake-openai-key")
    monkeypatch.setattr(
        "apps_rg.runtime.judges.bullet_pool_claude_selector.bootstrap_apps_rg_env",
        lambda: None,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.judges.bullet_pool_claude_selector._call_openai_pool_selector",
        lambda **_: (
            _Judge(),
            {
                "selections": [
                    {
                        "category_label": f"Category_0_{i}",
                        "path_index": 0,
                        "score": 0.9,
                        "passes": True,
                        "rationale": f"slot {i}",
                    }
                    for i in range(COMPETENCIES_FINAL_CATEGORY_COUNT)
                ],
                "pool_summary": {},
            },
        ),
    )

    result, raw, parsed, err, meta = generate_bullet_lane_with_sc_and_claude(
        section_lane="competencies",
        slot_kind="competencies",
        provider_payload={"model": "stub", "messages": []},
        parse_model_json=lambda r: (json.loads(r) if r.strip().startswith("{") else None, ""),
        normalize_parsed=lambda p: p,
        targeting_context={"allowed_fact_ids": ["bul_001"], "resume_support_blob_lower": ""},
        judge_mode="mocked",
    )
    assert err == ""
    assert is_competencies_pool_generation(meta)
    assert meta["initial_path_count"] == 8
    assert meta["final_category_count"] == COMPETENCIES_FINAL_CATEGORY_COUNT
    assert parsed is not None
    assert len(parsed.get("competencies") or []) == COMPETENCIES_FINAL_CATEGORY_COUNT
    assert result is not None


def test_generate_competencies_graph_pool_lane_forced_sc_ignores_disable_toggle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called: list[bool] = []

    def _fake_competencies_graph_pool_lane(**_: object) -> tuple[None, str, dict[str, object], str, dict[str, object]]:
        called.append(True)
        return (
            None,
            '{"competencies":[],"claim_ledger":[]}',
            {"competencies": [], "claim_ledger": []},
            "",
            {"generation_mode": "qwen_competencies_graph_pool_claude_top_8_regen"},
        )

    monkeypatch.setenv("APPS_RG_BULLET_SC_DISABLE", "1")
    monkeypatch.setattr(
        "apps_rg.runtime.reasoning.bullet_lane_generation._generate_competencies_graph_pool_lane",
        _fake_competencies_graph_pool_lane,
    )

    result, raw, parsed, err, meta = generate_bullet_lane_with_sc_and_claude(
        section_lane="competencies",
        slot_kind="competencies",
        provider_payload={"model": "stub", "messages": []},
        parse_model_json=lambda r: (json.loads(r) if r.strip().startswith("{") else None, ""),
        normalize_parsed=lambda p: p,
        targeting_context={"allowed_fact_ids": ["bul_001"], "resume_support_blob_lower": ""},
        judge_mode="mocked",
        use_sc_path=True,
    )

    assert called == [True]
    assert result is None
    assert raw == '{"competencies":[],"claim_ledger":[]}'
    assert parsed == {"competencies": [], "claim_ledger": []}
    assert err == ""
    assert meta["generation_mode"] == "qwen_competencies_graph_pool_claude_top_8_regen"


def test_competencies_pool_x1d_row_from_generation_meta(tmp_path) -> None:
    selections = [
        {"category_label": f"C{i}", "path_index": 0, "score": 0.88, "passes": True}
        for i in range(COMPETENCIES_FINAL_CATEGORY_COUNT)
    ]
    (tmp_path / "bullet_pool_selection.json").write_text(
        json.dumps({"selections": selections}),
        encoding="utf-8",
    )
    gen_meta = {
        "generation_mode": "qwen_competencies_graph_pool_claude_top_8_regen",
        "selection_gate": {"ok": True, "categories_in_merged": COMPETENCIES_FINAL_CATEGORY_COUNT},
        "selection_mode": "openai_competencies_top_8_pass",
    }
    rows = competencies_pool_x1d_judge_rows(
        artifact_dir=tmp_path,
        section_id="competencies",
        gen_meta=gen_meta,
    )
    assert len(rows) == 1
    assert rows[0]["judge_id"] == "x1d_openai_chatgpt_competencies_pool"
    assert rows[0]["provider_key"] == "openai_chatgpt"
    assert rows[0]["provider_name"] == "OpenAI ChatGPT"
    assert rows[0]["model_name"] == "gpt-5.5"
    assert rows[0]["selection_mode"] == "openai_competencies_top_8_pass"
    assert rows[0]["judge_role"] == "competencies_graph_pool_selector"
    assert rows[0]["advisory_only"] is True
    assert rows[0]["proof_eligible_judge"] is False


def test_competencies_non_sc_path_is_removed() -> None:
    from apps_rg.runtime.reasoning.bullet_lane_generation import generate_bullet_lane_with_sc_and_claude

    with pytest.raises(ValueError, match="competencies lane requires self-consistency generation"):
        generate_bullet_lane_with_sc_and_claude(
            section_lane="competencies",
            slot_kind="competencies",
            provider_payload={"model": "stub", "messages": []},
            parse_model_json=lambda r: (json.loads(r) if r.strip().startswith("{") else None, ""),
            normalize_parsed=lambda p: p,
            targeting_context={"allowed_fact_ids": ["bul_001"], "resume_support_blob_lower": ""},
            judge_mode="mocked",
            use_sc_path=False,
        )


def test_apply_executive_capability_projection_trims_to_eight_emit() -> None:
    from apps_rg.runtime.sections.competencies_capability_projection import (
        apply_executive_capability_projection,
    )
    from apps_rg.runtime.sections.competencies_rigor import MAX_CATEGORY_COUNT

    parsed = {
        "competencies": [
            _cat("Technology Strategy & Innovation", ["roadmap", "portfolio"]),
            _cat("AI Platform Leadership", ["graphrag", "orchestration"]),
            _cat("Data & Analytics Modernization", ["lakehouse", "catalog"]),
            _cat("Governance, Risk & Compliance", ["lineage", "policy"]),
            _cat("Engineering & Delivery Leadership", ["scale-out", "sre"]),
            _cat("Commercial & Operating Impact", ["gtm", "revenue"]),
            _cat("LLMOps & Reliability", ["evaluation", "telemetry"]),
            _cat("Distributed Infrastructure", ["lakehouse", "streaming"]),
        ],
        "change_log": [],
    }
    out = apply_executive_capability_projection(
        parsed,
        allowed_fact_ids={"bul_001"},
        allowed_skill_ids={"sk_graph_001"},
        skill_rows_by_id={
            "sk_graph_001": {"skill_id": "sk_graph_001", "canonical_name": "GraphRAG"}
        },
        resume_support_blob_lower="bul_001 graphrag orchestration",
    )
    comps = out.get("competencies") or []
    assert len(comps) == MAX_CATEGORY_COUNT
    assert len(out.get("categories") or []) == MAX_CATEGORY_COUNT


def test_canonical_competencies_cli_uses_gemini_pro_only() -> None:
    from apps_rg.runtime.internal.generated_lane_rollup import canonical_lane_command

    cmd = canonical_lane_command("competencies")
    assert "--x1d-judges gemini_pro" in cmd
    assert "openai_chatgpt" not in cmd
    assert "anthropic_claude" not in cmd
