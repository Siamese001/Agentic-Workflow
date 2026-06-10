"""W4.1 (G14) — bullet judge-feedback reselection unit coverage.

Hermetic: no provider calls (run_x2 / run_judges are recorded fakes), tmp_path artifact
dirs, deterministic pool fixtures. Covers the trigger truth table (decisive + soft-fail
arms, synthetic-row exclusion, X2-failed suppression), slot resolution priority,
replacement compliance (line discipline / fact scope / numeric entailment), the
X2-regression revert, the soft-arm revert-on-worse rule, the exactly-once bound, the
kill-switch, the receipt schema, and post-swap x1d composition (sidecar supersession +
``aggregate_x3`` outcomes).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.exit.executive_summary_x3 import aggregate_x3
from apps_rg.runtime.reasoning.bullet_pool_reselection import (
    OUTCOME_DISABLED,
    OUTCOME_NO_COMPLIANT_ALTERNATE,
    OUTCOME_NOT_FIRED,
    OUTCOME_REJUDGE_FAIL_FINAL,
    OUTCOME_REJUDGE_PASS,
    OUTCOME_REVERTED_REJUDGE_WORSE,
    OUTCOME_REVERTED_X2_REGRESSION,
    PRE_RESELECTION_SELECTION_FILENAME,
    PRE_RESELECTION_X1D_SIDECAR_FILENAME,
    RESELECTION_DISABLE_ENV,
    RESELECTION_RECEIPT_FILENAME,
    SLOT_RESOLUTION_BULLET_ID_REGEX,
    SLOT_RESOLUTION_CITED_SENTENCE_INDEXES,
    SLOT_RESOLUTION_LOWEST_SELECTOR_SCORE,
    TRIGGER_ARM_DECISIVE,
    TRIGGER_ARM_SOFT_FAIL,
    LaneRebuildState,
    build_reselection_plan,
    load_pool_alternates,
    run_bullet_judge_reselection,
)

SLOT_A = "bul_ibm_001"
SLOT_B = "bul_ibm_002"
REQUIRED = (SLOT_A, SLOT_B)


def _compliant(suffix: str) -> str:
    """Single sentence, strong verb, scale signal + tech token, < 320 chars, no metric."""
    return (
        f"Architected the enterprise agentic AI platform {suffix} "
        "for regulated financial delivery"
    )


def _noncompliant() -> str:
    # Weak verb, no scale signal, no tech token -> fails the seniority/specificity floors.
    return "Helped with various tasks for the team"


def _bullet(slot: str, text: str, source_ids: list[str] | None = None) -> dict[str, Any]:
    return {
        "bullet_id": slot,
        "bullet_text": text,
        "source_fact_ids": source_ids if source_ids is not None else [slot],
    }


def _current_bullets() -> list[dict[str, Any]]:
    return [
        _bullet(SLOT_A, _compliant("governance layer")),
        _bullet(SLOT_B, _compliant("evidence spine")),
    ]


def _ledger_row(slot: str, text: str) -> dict[str, Any]:
    return {"bullet_id": slot, "claim_text": text, "source_fact_ids": [slot]}


def _doc(bullets: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "bullets": bullets,
        "claim_ledger": [_ledger_row(str(b["bullet_id"]), str(b["bullet_text"])) for b in bullets],
        "change_log": [
            {"bullet_id": str(b["bullet_id"]), "operation": "path_gen"} for b in bullets
        ],
    }


def _write_pool(tmp: Path, paths: dict[int, dict[str, Any]]) -> None:
    for idx, doc in paths.items():
        (tmp / f"self_consistency_path_{idx}_parsed.json").write_text(
            json.dumps(doc, indent=2) + "\n", encoding="utf-8"
        )


def _write_selection(
    tmp: Path,
    *,
    scores: dict[str, float] | None = None,
    source_map: dict[str, int] | None = None,
) -> dict[str, Any]:
    scores = scores or {SLOT_A: 0.95, SLOT_B: 0.74}
    source_map = source_map or {SLOT_A: 0, SLOT_B: 0}
    doc = {
        "selection_mode": "claude_employment_top_n_pass",
        "selections": [
            {"bullet_id": slot, "path_index": source_map.get(slot, 0), "score": score, "passes": True}
            for slot, score in scores.items()
        ],
        "source_path_by_slot": dict(source_map),
        "selection_gate": {"ok": True},
    }
    (tmp / "bullet_pool_selection.json").write_text(
        json.dumps(doc, indent=2) + "\n", encoding="utf-8"
    )
    return doc


def _seed_default_pool(tmp: Path) -> None:
    """Path 0 = current winners; path 1 = noncompliant SLOT_B; path 2 = compliant SLOT_B."""
    _write_pool(
        tmp,
        {
            0: _doc(_current_bullets()),
            1: _doc([_bullet(SLOT_B, _noncompliant())]),
            2: _doc([_bullet(SLOT_B, _compliant("lineage control plane"))]),
        },
    )
    _write_selection(tmp)


def _judge_row(
    provider_key: str,
    *,
    normalized_score: float = 0.9,
    normalized_threshold: float = 0.8,
    decisive: bool = False,
    passes: bool | None = None,
    judge_role: str | None = None,
    findings: list[str] | None = None,
    cited: list[int] | None = None,
) -> dict[str, Any]:
    passed = passes if passes is not None else (normalized_score >= normalized_threshold and not decisive)
    row: dict[str, Any] = {
        "judge_id": f"x1d_{provider_key}_ibm_bullets",
        "provider_key": provider_key,
        "provider_name": provider_key,
        "evaluator_mode": "MODEL_BACKED",
        "provider_status": "MODEL_BACKED_PASS" if passed else "MODEL_BACKED_FAIL",
        "provider_blocked": False,
        "score": normalized_score * 5,
        "threshold": normalized_threshold * 5,
        "normalized_score": normalized_score,
        "normalized_threshold": normalized_threshold,
        "pass": passed,
        "decisive_failure": decisive,
        "findings": findings or [],
        "cited_sentence_indexes": cited or [],
        "fail_reasons": [],
        "unsupported_claims": [],
        "remediation_suggestions": [],
    }
    if judge_role:
        row["judge_role"] = judge_role
    return row


def _synthetic_row(*, passes: bool = True) -> dict[str, Any]:
    return _judge_row(
        "anthropic_claude",
        normalized_score=0.83 if passes else 0.5,
        normalized_threshold=0.72,
        decisive=not passes,
        passes=passes,
        judge_role="employment_bullet_pool_selector",
    )


def _decisive_gemini(**kw: Any) -> dict[str, Any]:
    kw.setdefault("findings", [f"{SLOT_B} claims an unsupported outcome"])
    return _judge_row("gemini_pro", normalized_score=0.5, decisive=True, passes=False, **kw)


def _soft_gemini(**kw: Any) -> dict[str, Any]:
    kw.setdefault("findings", [f"{SLOT_B} reads generic for the level"])
    return _judge_row("gemini_pro", normalized_score=0.7, decisive=False, passes=False, **kw)


def _passing_openai() -> dict[str, Any]:
    return _judge_row("openai_chatgpt", normalized_score=0.9)


_X2_PASS = [{"gate_id": "g1", "pass": True}, {"gate_id": "g2", "pass": True}]

_VALID_USAGE_LEDGER = {
    "schema": "section_input_usage_ledger_v1",
    "parity_match": True,
    "evidence_boundary": {
        "non_evidence_inputs_used_as_claim_evidence": False,
        "non_evidence_inputs_in_source_fact_ids": False,
    },
    "claim_support_summary": {
        "claims_with_targeting_input_in_source_fact_ids": 0,
        "claims_with_context_input_in_source_fact_ids": 0,
    },
}


def _x3(x1d: list[dict[str, Any]]) -> Any:
    return aggregate_x3(
        resume_display_text="display",
        claim_ledger=[],
        x2_gates=list(_X2_PASS),
        x1d_judges=x1d,
        runtime_generation_status="REAL_LLM",
        product_quality_status="PASS",
        section_input_usage_ledger=dict(_VALID_USAGE_LEDGER),
    )


def _plan(
    tmp: Path,
    *,
    x1d: list[dict[str, Any]],
    x2_failed: list[str] | None = None,
    bullets: list[dict[str, Any]] | None = None,
    corpus: dict[str, str] | None = None,
    allowed: set[str] | None = None,
):
    pool = load_pool_alternates(tmp, REQUIRED)
    return build_reselection_plan(
        x1d_rows=x1d,
        x2_failed_gate_ids=list(x2_failed or []),
        pool=pool,
        bullets=bullets if bullets is not None else _current_bullets(),
        required_bullet_ids=REQUIRED,
        allowed_fact_ids=allowed if allowed is not None else {SLOT_A, SLOT_B},
        entailment_corpus=corpus,
    )


def _run_seam(
    tmp: Path,
    *,
    x1d: list[dict[str, Any]],
    x2: list[dict[str, Any]] | None = None,
    x2_after: list[dict[str, Any]] | None = None,
    rejudge_rows: list[dict[str, Any]] | None = None,
    corpus: dict[str, str] | None = None,
    allowed: set[str] | None = None,
    parsed: dict[str, Any] | None = None,
):
    calls: dict[str, list[Any]] = {"run_x2": [], "run_judges": [], "write_artifacts": [], "write_usage": []}
    parsed = parsed if parsed is not None else _doc(_current_bullets())
    bullets = list(parsed.get("bullets") or [])
    claim_ledger = list(parsed.get("claim_ledger") or [])
    pre_x2 = [dict(g) for g in (x2 if x2 is not None else _X2_PASS)]

    def _post_chain(doc: dict[str, Any]) -> dict[str, Any]:
        return doc

    def _rebuild(doc: dict[str, Any]) -> LaneRebuildState:
        new_bullets = list(doc.get("bullets") or [])
        return LaneRebuildState(
            parsed=doc,
            bullets=new_bullets,
            claim_ledger=list(doc.get("claim_ledger") or []),
            coverage={"overall_pass": True},
            parsed_for_x2=doc,
            canon_doc={"claims": []},
            usage_doc=dict(_VALID_USAGE_LEDGER),
            display_text="\n".join(str(b.get("bullet_text") or "") for b in new_bullets),
            parse_status="OK",
        )

    def _run_x2(state: LaneRebuildState, x1d_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        calls["run_x2"].append({"slots": [b["bullet_id"] for b in state.bullets], "x1d_rows": list(x1d_rows)})
        return [dict(g) for g in (x2_after if x2_after is not None else _X2_PASS)]

    def _run_judges(state: LaneRebuildState, keys: list[str]) -> list[dict[str, Any]]:
        calls["run_judges"].append(list(keys))
        return [dict(r) for r in (rejudge_rows if rejudge_rows is not None else [_judge_row("gemini_pro")])]

    def _write_usage(state: LaneRebuildState) -> None:
        calls["write_usage"].append(True)
        (tmp / "section_input_usage_ledger.json").write_text(
            json.dumps({**state.usage_doc, "marker": "post_swap"}) + "\n", encoding="utf-8"
        )

    def _write_artifacts(state: LaneRebuildState, x2_rows: list[dict[str, Any]]) -> None:
        calls["write_artifacts"].append(True)
        (tmp / "parsed_output.json").write_text(
            json.dumps({"parsed": state.parsed, "parse_status": state.parse_status}) + "\n",
            encoding="utf-8",
        )
        (tmp / "x2_gate_outputs.json").write_text(
            json.dumps({"gates": x2_rows}) + "\n", encoding="utf-8"
        )
        (tmp / "fact_check_result.json").write_text(
            json.dumps({"passed": not [g for g in x2_rows if not g["pass"]]}) + "\n",
            encoding="utf-8",
        )

    result = run_bullet_judge_reselection(
        artifact_dir=tmp,
        section_id="ibm_bullets",
        run_id="run-test",
        required_bullet_ids=REQUIRED,
        parsed=parsed,
        bullets=bullets,
        claim_ledger=claim_ledger,
        parsed_for_x2=parsed,
        x1d=x1d,
        x2=pre_x2,
        usage_doc=dict(_VALID_USAGE_LEDGER),
        canon_doc={"claims": []},
        allowed_fact_ids=allowed if allowed is not None else {SLOT_A, SLOT_B},
        judge_mode="mocked",
        entailment_corpus=corpus,
        post_chain=_post_chain,
        rebuild_state=_rebuild,
        run_x2=_run_x2,
        run_judges=_run_judges,
        write_usage_ledger=_write_usage,
        write_lane_artifacts=_write_artifacts,
    )
    return result, calls


def _receipt(tmp: Path) -> dict[str, Any]:
    return json.loads((tmp / RESELECTION_RECEIPT_FILENAME).read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Trigger truth table
# ---------------------------------------------------------------------------


def test_trigger_decisive_model_backed_fires(tmp_path: Path) -> None:
    _seed_default_pool(tmp_path)
    plan = _plan(tmp_path, x1d=[_synthetic_row(), _decisive_gemini()])
    assert plan.fired is True
    assert plan.trigger_arm == TRIGGER_ARM_DECISIVE
    assert plan.x2_all_pass_pre is True
    assert [s.slot for s in plan.swaps] == [SLOT_B]
    assert plan.swaps[0].new_path_index == 2  # path 1 fails the floors


def test_trigger_soft_fail_fires_soft_arm(tmp_path: Path) -> None:
    _seed_default_pool(tmp_path)
    plan = _plan(tmp_path, x1d=[_synthetic_row(), _soft_gemini()])
    assert plan.fired is True
    assert plan.trigger_arm == TRIGGER_ARM_SOFT_FAIL


def test_trigger_synthetic_selector_rows_never_fire(tmp_path: Path) -> None:
    _seed_default_pool(tmp_path)
    for role in ("employment_bullet_pool_selector", "competencies_graph_pool_selector"):
        failing_synthetic = _judge_row(
            "anthropic_claude", normalized_score=0.5, decisive=True, passes=False, judge_role=role
        )
        plan = _plan(tmp_path, x1d=[failing_synthetic])
        assert plan.fired is False
        assert plan.outcome == OUTCOME_NOT_FIRED
        assert plan.trigger_arm == ""


def test_trigger_suppressed_when_x2_failed(tmp_path: Path) -> None:
    _seed_default_pool(tmp_path)
    plan = _plan(tmp_path, x1d=[_decisive_gemini()], x2_failed=["x2_some_gate"])
    assert plan.fired is False
    assert plan.outcome == OUTCOME_NOT_FIRED
    assert plan.x2_all_pass_pre is False


def test_trigger_not_fired_when_all_rows_pass(tmp_path: Path) -> None:
    _seed_default_pool(tmp_path)
    plan = _plan(tmp_path, x1d=[_synthetic_row(), _judge_row("gemini_pro"), _passing_openai()])
    assert plan.fired is False
    assert plan.outcome == OUTCOME_NOT_FIRED


def test_trigger_non_model_backed_rows_ignored(tmp_path: Path) -> None:
    _seed_default_pool(tmp_path)
    mocked = dict(_decisive_gemini(), evaluator_mode="MOCKED")
    plan = _plan(tmp_path, x1d=[mocked])
    assert plan.fired is False


# ---------------------------------------------------------------------------
# Slot resolution priority
# ---------------------------------------------------------------------------


def test_slot_resolution_regex_beats_cited_indexes(tmp_path: Path) -> None:
    _seed_default_pool(tmp_path)
    row = _decisive_gemini(cited=[1])  # cites SLOT_A positionally, names SLOT_B in findings
    plan = _plan(tmp_path, x1d=[row])
    assert plan.slot_resolution_method == SLOT_RESOLUTION_BULLET_ID_REGEX
    assert plan.implicated_slots == (SLOT_B,)


def test_slot_resolution_cited_indexes_positional(tmp_path: Path) -> None:
    _seed_default_pool(tmp_path)
    row = _decisive_gemini(findings=["second bullet overstates the outcome"], cited=[2])
    plan = _plan(tmp_path, x1d=[row])
    assert plan.slot_resolution_method == SLOT_RESOLUTION_CITED_SENTENCE_INDEXES
    assert plan.implicated_slots == (SLOT_B,)


def test_slot_resolution_lowest_selector_score_fallback(tmp_path: Path) -> None:
    _seed_default_pool(tmp_path)  # SLOT_B has the lowest selector score (0.74 vs 0.95)
    row = _decisive_gemini(findings=["the section overstates scale"], cited=[])
    plan = _plan(tmp_path, x1d=[row])
    assert plan.slot_resolution_method == SLOT_RESOLUTION_LOWEST_SELECTOR_SCORE
    assert plan.implicated_slots == (SLOT_B,)


# ---------------------------------------------------------------------------
# Replacement compliance
# ---------------------------------------------------------------------------


def test_replacement_excludes_source_path_and_noncompliant(tmp_path: Path) -> None:
    # Path 0 (current source) holds a compliant variant; path 1 fails floors; path 2 compliant.
    _write_pool(
        tmp_path,
        {
            0: _doc(_current_bullets()),
            1: _doc([_bullet(SLOT_B, _noncompliant())]),
            2: _doc([_bullet(SLOT_B, _compliant("lineage control plane"))]),
        },
    )
    _write_selection(tmp_path)
    plan = _plan(tmp_path, x1d=[_decisive_gemini()])
    assert plan.fired is True
    swap = plan.swaps[0]
    assert swap.old_path_index == 0
    assert swap.new_path_index == 2
    assert swap.alternate_basis == "first_compliant_alternate"
    assert "line_discipline" in swap.compliance_checks
    assert "fact_scope" in swap.compliance_checks


def test_replacement_rejects_out_of_scope_source_fact_ids(tmp_path: Path) -> None:
    _write_pool(
        tmp_path,
        {
            0: _doc(_current_bullets()),
            1: _doc([_bullet(SLOT_B, _compliant("scoped variant"), ["fact_forbidden"])]),
            2: _doc([_bullet(SLOT_B, _compliant("allowed variant"))]),
        },
    )
    _write_selection(tmp_path)
    plan = _plan(tmp_path, x1d=[_decisive_gemini()])
    assert plan.fired is True
    assert plan.swaps[0].new_path_index == 2  # path 1 cites a non-allowed fact id


def test_replacement_entailment_blocks_numeric_drift(tmp_path: Path) -> None:
    drift = "Generated $10M ARR on the enterprise platform modernization program"
    _write_pool(
        tmp_path,
        {
            0: _doc(_current_bullets()),
            1: _doc([_bullet(SLOT_B, drift)]),
            2: _doc([_bullet(SLOT_B, _compliant("qualitative variant"))]),
        },
    )
    _write_selection(tmp_path)
    corpus = {SLOT_B: "Generated $12M platform revenue for enterprise clients"}
    plan = _plan(tmp_path, x1d=[_decisive_gemini()], corpus=corpus)
    assert plan.fired is True
    assert plan.swaps[0].new_path_index == 2  # $10M not entailed by the $12M corpus
    assert "fact_entailment" in plan.swaps[0].compliance_checks


def test_replacement_entailment_fails_open_without_corpus(tmp_path: Path) -> None:
    drift = "Generated $10M ARR on the enterprise platform modernization program"
    _write_pool(
        tmp_path,
        {
            0: _doc(_current_bullets()),
            1: _doc([_bullet(SLOT_B, drift)]),
        },
    )
    _write_selection(tmp_path)
    plan = _plan(tmp_path, x1d=[_decisive_gemini()], corpus={})
    assert plan.fired is True
    assert plan.swaps[0].new_path_index == 1
    assert "fact_entailment:skipped_no_corpus" in plan.swaps[0].compliance_checks


def test_no_compliant_alternate_outcome(tmp_path: Path) -> None:
    _write_pool(
        tmp_path,
        {
            0: _doc(_current_bullets()),
            1: _doc([_bullet(SLOT_B, _noncompliant())]),
        },
    )
    _write_selection(tmp_path)
    plan = _plan(tmp_path, x1d=[_decisive_gemini()])
    assert plan.fired is False
    assert plan.outcome == OUTCOME_NO_COMPLIANT_ALTERNATE
    assert plan.slots_without_alternate == (SLOT_B,)


# ---------------------------------------------------------------------------
# Glue: X2-regression revert
# ---------------------------------------------------------------------------


def test_x2_regression_reverts_and_skips_rejudge(tmp_path: Path) -> None:
    _seed_default_pool(tmp_path)
    original_usage = json.dumps({"marker": "original"}) + "\n"
    (tmp_path / "section_input_usage_ledger.json").write_text(original_usage, encoding="utf-8")
    x1d = [_synthetic_row(), _decisive_gemini()]
    result, calls = _run_seam(
        tmp_path,
        x1d=x1d,
        x2_after=[{"gate_id": "g1", "pass": False}, {"gate_id": "g2", "pass": True}],
    )
    assert result.fired is False
    assert result.outcome == OUTCOME_REVERTED_X2_REGRESSION
    assert result.x1d == x1d  # originals returned untouched
    assert calls["run_judges"] == []  # re-judge skipped
    assert calls["write_artifacts"] == []  # no artifact rewrites
    # usage ledger byte-restored
    assert (tmp_path / "section_input_usage_ledger.json").read_text(encoding="utf-8") == original_usage
    receipt = _receipt(tmp_path)
    assert receipt["outcome"] == OUTCOME_REVERTED_X2_REGRESSION
    assert receipt["x2"]["regressed_gates"] == ["g1"]
    # the X2 re-run received the PRE-swap x1d set (presence/schema gates depend on it)
    assert calls["run_x2"][0]["x1d_rows"] == x1d


# ---------------------------------------------------------------------------
# Glue: soft-fail arm revert-on-worse
# ---------------------------------------------------------------------------


def test_soft_arm_reverts_when_rejudge_scores_lower(tmp_path: Path) -> None:
    _seed_default_pool(tmp_path)
    x1d = [_synthetic_row(), _soft_gemini()]  # 0.7 vs threshold 0.8 -> REVIEW floor
    worse = [_judge_row("gemini_pro", normalized_score=0.6, passes=False)]
    result, calls = _run_seam(tmp_path, x1d=x1d, rejudge_rows=worse)
    assert result.outcome == OUTCOME_REVERTED_REJUDGE_WORSE
    assert result.fired is False
    assert result.x1d == x1d  # original judge rows restored entirely
    assert calls["write_artifacts"] == []
    assert not (tmp_path / PRE_RESELECTION_X1D_SIDECAR_FILENAME).is_file()
    # floor remains the original non-blocking REVIEW
    assert _x3(result.x1d).x3_code == "X3_REVIEW_JUDGE_SOFT_FAIL"


def test_soft_arm_reverts_when_rejudge_is_decisive(tmp_path: Path) -> None:
    _seed_default_pool(tmp_path)
    x1d = [_synthetic_row(), _soft_gemini()]
    decisive = [_judge_row("gemini_pro", normalized_score=0.4, decisive=True, passes=False)]
    result, _calls = _run_seam(tmp_path, x1d=x1d, rejudge_rows=decisive)
    assert result.outcome == OUTCOME_REVERTED_REJUDGE_WORSE
    assert result.x1d == x1d
    assert _x3(result.x1d).x3_code == "X3_REVIEW_JUDGE_SOFT_FAIL"


def test_soft_arm_keeps_swap_on_equal_score_floor_preserved(tmp_path: Path) -> None:
    _seed_default_pool(tmp_path)
    x1d = [_synthetic_row(), _soft_gemini()]
    equal = [_judge_row("gemini_pro", normalized_score=0.7, passes=False)]  # equal, not worse
    result, _calls = _run_seam(tmp_path, x1d=x1d, rejudge_rows=equal)
    assert result.fired is True
    assert result.outcome == OUTCOME_REJUDGE_FAIL_FINAL
    assert _x3(result.x1d).x3_code == "X3_REVIEW_JUDGE_SOFT_FAIL"  # floor unchanged


def test_soft_arm_promotes_to_allow_on_rejudge_pass(tmp_path: Path) -> None:
    _seed_default_pool(tmp_path)
    x1d = [_synthetic_row(), _soft_gemini()]
    result, _calls = _run_seam(tmp_path, x1d=x1d, rejudge_rows=[_judge_row("gemini_pro", normalized_score=0.9)])
    assert result.fired is True
    assert result.outcome == OUTCOME_REJUDGE_PASS
    assert _x3(result.x1d).x3_code == "X3_ALLOW"


# ---------------------------------------------------------------------------
# Glue: exactly-once + kill-switch
# ---------------------------------------------------------------------------


def test_exactly_once_existing_receipt_noop(tmp_path: Path) -> None:
    _seed_default_pool(tmp_path)
    prior = json.dumps({"outcome": OUTCOME_REJUDGE_PASS, "fired": True}) + "\n"
    (tmp_path / RESELECTION_RECEIPT_FILENAME).write_text(prior, encoding="utf-8")
    x1d = [_synthetic_row(), _decisive_gemini()]
    result, calls = _run_seam(tmp_path, x1d=x1d)
    assert result.fired is False
    assert result.receipt_written is False
    assert result.outcome == OUTCOME_REJUDGE_PASS  # echoed from the existing receipt
    assert calls["run_x2"] == [] and calls["run_judges"] == [] and calls["write_artifacts"] == []
    assert (tmp_path / RESELECTION_RECEIPT_FILENAME).read_text(encoding="utf-8") == prior


def test_kill_switch_writes_disabled_receipt(tmp_path: Path, monkeypatch: Any) -> None:
    _seed_default_pool(tmp_path)
    monkeypatch.setenv(RESELECTION_DISABLE_ENV, "1")
    x1d = [_synthetic_row(), _decisive_gemini()]
    result, calls = _run_seam(tmp_path, x1d=x1d)
    assert result.fired is False
    assert result.outcome == OUTCOME_DISABLED
    assert calls["run_x2"] == [] and calls["run_judges"] == []
    receipt = _receipt(tmp_path)
    assert receipt["outcome"] == OUTCOME_DISABLED
    assert receipt["fired"] is False
    assert receipt["kill_switch"] == {"env": RESELECTION_DISABLE_ENV, "disabled": True}


# ---------------------------------------------------------------------------
# Glue: receipt schema
# ---------------------------------------------------------------------------


def test_receipt_schema_on_fired_swap(tmp_path: Path) -> None:
    _seed_default_pool(tmp_path)
    x1d = [_synthetic_row(), _decisive_gemini(), _passing_openai()]
    result, _calls = _run_seam(tmp_path, x1d=x1d)
    receipt = _receipt(tmp_path)
    for key in (
        "receipt_version",
        "section_id",
        "run_id",
        "fired",
        "outcome",
        "kill_switch",
        "trigger",
        "slot_resolution_method",
        "slots",
        "x2",
        "rejudge",
        "attempt",
        "max_attempts",
    ):
        assert key in receipt, f"missing receipt key: {key}"
    assert receipt["receipt_version"] == 1
    assert receipt["fired"] is True
    assert receipt["attempt"] == 1 and receipt["max_attempts"] == 1
    assert receipt["outcome"] in (OUTCOME_REJUDGE_PASS, OUTCOME_REJUDGE_FAIL_FINAL)
    assert receipt["trigger"]["trigger_arm"] == TRIGGER_ARM_DECISIVE
    assert receipt["trigger"]["x2_all_pass_pre"] is True
    assert receipt["trigger"]["rows"][0]["provider_key"] == "gemini_pro"
    slot = receipt["slots"][0]
    for key in (
        "slot",
        "old_path_index",
        "new_path_index",
        "old_text_sha16",
        "new_text_sha16",
        "alternate_basis",
        "compliance_checks",
    ):
        assert key in slot
    assert len(slot["old_text_sha16"]) == 16 and len(slot["new_text_sha16"]) == 16
    assert receipt["x2"]["failed_before"] == [] and receipt["x2"]["failed_after"] == []
    assert receipt["rejudge"]["provider_keys"] == ["gemini_pro"]
    assert receipt["rejudge"]["dropped_non_required_keys"] == ["openai_chatgpt"]
    assert result.outcome == receipt["outcome"]


def test_receipt_written_on_not_fired(tmp_path: Path) -> None:
    _seed_default_pool(tmp_path)
    result, _calls = _run_seam(tmp_path, x1d=[_synthetic_row(), _judge_row("gemini_pro")])
    assert result.outcome == OUTCOME_NOT_FIRED
    assert _receipt(tmp_path)["outcome"] == OUTCOME_NOT_FIRED


# ---------------------------------------------------------------------------
# Glue: x1d composition, sidecar supersession, X3 outcomes, artifact rewrites
# ---------------------------------------------------------------------------


def test_x1d_sidecar_supersedes_all_nonsynthetic_model_backed_rows(tmp_path: Path) -> None:
    _seed_default_pool(tmp_path)
    synthetic = _synthetic_row()
    decisive = _decisive_gemini()
    panel_pass = _passing_openai()  # non-decisive panel row MUST also be superseded
    result, _calls = _run_seam(tmp_path, x1d=[synthetic, decisive, panel_pass])
    assert result.fired is True
    sidecar = json.loads(
        (tmp_path / PRE_RESELECTION_X1D_SIDECAR_FILENAME).read_text(encoding="utf-8")
    )
    side_keys = sorted(r["provider_key"] for r in sidecar["judges"])
    assert side_keys == ["gemini_pro", "openai_chatgpt"]
    assert all(r["superseded_by_reselection"] is True for r in sidecar["judges"])
    # active set = kept synthetic row + stamped re-judge rows
    active_doc = json.loads((tmp_path / "x1d_llm_judge_outputs.json").read_text(encoding="utf-8"))
    assert active_doc["sidecar_ref"] == PRE_RESELECTION_X1D_SIDECAR_FILENAME
    active = active_doc["judges"]
    assert [r.get("judge_role") for r in active if r["provider_key"] == "anthropic_claude"] == [
        "employment_bullet_pool_selector"
    ]
    rejudge = [r for r in active if r.get("reselection_rejudge_row")]
    assert [r["provider_key"] for r in rejudge] == ["gemini_pro"]
    assert result.x1d == active
    # stale passing panel row no longer counts toward all_model_backed_pass
    assert _x3(result.x1d).x3_code == "X3_ALLOW"


def test_decisive_rejudge_fail_final_blocks(tmp_path: Path) -> None:
    _seed_default_pool(tmp_path)
    x1d = [_synthetic_row(), _decisive_gemini()]
    still_decisive = [_judge_row("gemini_pro", normalized_score=0.4, decisive=True, passes=False)]
    result, calls = _run_seam(tmp_path, x1d=x1d, rejudge_rows=still_decisive)
    assert result.fired is True
    assert result.outcome == OUTCOME_REJUDGE_FAIL_FINAL
    assert len(calls["run_judges"]) == 1  # no second attempt
    assert _x3(result.x1d).x3_code == "X3_BLOCK"


def test_selection_rewrite_preserves_original_and_marks_swap(tmp_path: Path) -> None:
    _seed_default_pool(tmp_path)
    original = json.loads((tmp_path / "bullet_pool_selection.json").read_text(encoding="utf-8"))
    result, _calls = _run_seam(tmp_path, x1d=[_synthetic_row(), _decisive_gemini()])
    assert result.fired is True
    pre = json.loads((tmp_path / PRE_RESELECTION_SELECTION_FILENAME).read_text(encoding="utf-8"))
    assert pre == original
    rewritten = json.loads((tmp_path / "bullet_pool_selection.json").read_text(encoding="utf-8"))
    assert rewritten["reselection_applied"] is True
    swapped = next(r for r in rewritten["selections"] if r["bullet_id"] == SLOT_B)
    assert swapped["path_index"] == 2
    assert swapped["score"] is None
    assert swapped["reselection_applied"] is True
    untouched = next(r for r in rewritten["selections"] if r["bullet_id"] == SLOT_A)
    assert untouched["score"] == 0.95 and "reselection_applied" not in untouched
    assert rewritten["source_path_by_slot"][SLOT_B] == 2


def test_stick_rewrites_downstream_artifacts_and_swaps_content(tmp_path: Path) -> None:
    _seed_default_pool(tmp_path)
    result, calls = _run_seam(tmp_path, x1d=[_synthetic_row(), _decisive_gemini()])
    assert result.fired is True
    assert calls["write_artifacts"] == [True]
    assert calls["write_usage"] == [True]
    # post-swap x2 evidence on disk (rewrite-list mandate: x2_gate_outputs + fact_check_result)
    assert json.loads((tmp_path / "x2_gate_outputs.json").read_text(encoding="utf-8"))["gates"]
    assert json.loads((tmp_path / "fact_check_result.json").read_text(encoding="utf-8"))["passed"] is True
    # swapped content flowed into the returned state
    swapped_bullet = next(b for b in result.bullets if b["bullet_id"] == SLOT_B)
    assert "lineage control plane" in swapped_bullet["bullet_text"]
    # claim_ledger rows for the swapped slot were pulled from the alternate's source path
    slot_rows = [r for r in result.claim_ledger if r.get("bullet_id") == SLOT_B]
    assert slot_rows and all("lineage control plane" in r["claim_text"] for r in slot_rows)
    # repair ledger carries the authorized deterministic-rewrite operation
    ledger = json.loads((tmp_path / "section_repair_ledger.json").read_text(encoding="utf-8"))
    ops = [r.get("operation") for r in ledger.get("repairs") or []]
    assert "bullet_judge_feedback_reselection" in ops


def test_repair_ledger_op_is_authorized_for_product_pass(tmp_path: Path) -> None:
    from apps_rg.runtime.section_repair_ledger import (
        KIND_DETERMINISTIC_REWRITE,
        ledger_blocks_product_pass,
        record_repair,
    )

    record_repair(
        tmp_path,
        kind=KIND_DETERMINISTIC_REWRITE,
        operation="bullet_judge_feedback_reselection",
        replaced_l2=True,
        detail={"section_id": "ibm_bullets"},
    )
    ledger = json.loads((tmp_path / "section_repair_ledger.json").read_text(encoding="utf-8"))
    ledger["product_fail_closed"] = True
    blocked, reason = ledger_blocks_product_pass(ledger)
    assert blocked is False, reason
