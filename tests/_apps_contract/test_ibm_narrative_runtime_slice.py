from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
LANE_KEY = "ibm_narrative"
# Canonical selected-section entry: `python -m apps_rg --section ibm_narrative` (no standalone dispatch CLI).
_CMD = [
    sys.executable,
    "-m",
    "apps_rg",
    "--section",
    "ibm_narrative",
    "--provider",
    "qwen_vllm",
    "--allow-non-allow-exit-zero",
    "--mock-judges",
    "--allow-test-mock-judges",
]


_LAST_CMD_ARTIFACT_DIR: Path | None = None


def _capture_artifact_dir(result: subprocess.CompletedProcess[str]) -> Path | None:
    text = f"{result.stdout}\n{result.stderr}"
    last: Path | None = None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("artifact_dir="):
            p = Path(line.split("=", 1)[1].strip())
            if p.is_dir():
                last = p
    return last


def run_cmd(*extra: str) -> subprocess.CompletedProcess[str]:
    global _LAST_CMD_ARTIFACT_DIR
    env = {**os.environ, "APPS_RG_QWEN_OFFLINE_CONTRACT_STUB": "1"}
    proc = subprocess.run(
        _CMD + list(extra),
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=180,
        env=env,
    )
    _LAST_CMD_ARTIFACT_DIR = _capture_artifact_dir(proc)
    return proc


def mock_artifacts_dir() -> Path:
    from apps_rg.runtime.runtime_proof_layout import (
        resolve_accepted_real_rollup_run_dir,
        resolve_latest_mock_run_dir,
        resolve_run_dir_from_pointer,
    )

    global _LAST_CMD_ARTIFACT_DIR
    if _LAST_CMD_ARTIFACT_DIR is not None and (_LAST_CMD_ARTIFACT_DIR / "l2_output.json").is_file():
        return _LAST_CMD_ARTIFACT_DIR

    rm = resolve_latest_mock_run_dir(REPO_ROOT, LANE_KEY)
    if rm is not None and (rm / "l2_output.json").is_file():
        return rm
    rr = resolve_run_dir_from_pointer(REPO_ROOT, LANE_KEY, "real")
    if rr is not None and (rr / "l2_output.json").is_file():
        return rr
    accepted, tag = resolve_accepted_real_rollup_run_dir(REPO_ROOT, LANE_KEY)
    if accepted is not None and tag != "missing_successful_real_run" and (accepted / "l2_output.json").is_file():
        return accepted
    legacy = REPO_ROOT / "artifacts" / "apps_rg" / "runtime_proofs" / LANE_KEY
    if (legacy / "l2_output.json").is_file():
        return legacy
    raise AssertionError(
        f"No ibm_narrative runtime_proof artifacts under artifacts/apps_rg/runtime_proofs/{LANE_KEY}; "
        "run the canonical slice test command first."
    )


def load_json(name: str):
    return json.loads((mock_artifacts_dir() / name).read_text(encoding="utf-8"))


def test_mock_dispatch_executes():
    result = run_cmd()
    assert result.returncode == 0, result.stderr
    assert "IBM_NARRATIVE_OUTPUT:" in result.stdout


def test_mock_one_sentence():
    run_cmd()
    l2 = load_json("l2_output.json")
    text = l2["narrative_sentence"].strip()
    assert text.count(".") >= 1
    assert "\n" not in text or len(text.split(".")) <= 2


def test_x2_gate_count():
    run_cmd()
    x2 = load_json("x2_gate_outputs.json")
    gates_list = x2["gates"]
    assert x2["total_x2_gates"] == len(gates_list)
    assert x2["x2_failed"] == 0
    ids = [g["gate_id"] for g in gates_list]
    assert "x2_no_mock_or_plumbing_language_in_real_l2_output" in ids


def test_clean_x3_allow_readiness_emitted():
    run_cmd()
    path = mock_artifacts_dir() / "clean_x3_allow_readiness.json"
    assert path.is_file()
    readiness = json.loads(path.read_text(encoding="utf-8"))
    assert readiness["section_id"] == "ibm_narrative"
    assert readiness["mocked_judge_flags_active"] is True
    assert readiness["clean_allow_possible_at_start"] is False
    blockers = readiness.get("decisive_blockers") or []
    assert any("mock" in str(b).lower() for b in blockers)


def test_cli_manifest_exit_override_accounting_when_allow_non_allow():
    run_cmd()
    ad = mock_artifacts_dir()
    mf = json.loads((ad / "run_manifest.json").read_text(encoding="utf-8"))
    assert mf.get("shell_exit_overridden_for_inspection") is True
    assert mf.get("x3_json_source_of_truth") is True
    assert mf.get("not_release_signoff") is True
    assert mf.get("product_authorized") is False


def test_command_output_banner_for_exit_override_and_mocks():
    run_cmd()
    txt = (mock_artifacts_dir() / "command_output.txt").read_text(encoding="utf-8")
    assert "PROCESS EXIT OVERRIDDEN FOR INSPECTION ONLY" in txt
    assert "Mocked judges cannot satisfy clean X3 ALLOW." in txt


def test_preflight_reports_missing_credentials_for_empty_env():
    from apps_rg.runtime.ibm_narrative_judge_preflight import run_ibm_narrative_judge_credentials_preflight

    report = run_ibm_narrative_judge_credentials_preflight(
        ["gemini_pro", "openai_chatgpt", "anthropic_claude"],
        {},
    )
    assert report["preflight_blocked"] is True


def test_x2_gate_rejects_mock_plumbing_lexicon_in_real_llm_payload():
    from apps_rg.runtime.validators.ibm_narrative_x2 import run_ibm_narrative_x2_gates

    po = {"change_log": [{"operation": "mocked_runtime_slice", "why": "x"}]}
    gates = [
        g
        for g in run_ibm_narrative_x2_gates(
            narrative_sentence="At IBM, modernization focused on disciplined delivery.",
            parsed_output=po,
            claim_ledger=[{"claim_text": "text", "source_fact_ids": ["bul_ibm_001"]}],
            jd_text="",
            runtime_generation_status="REAL_LLM",
            companion_bullet_texts=None,
            provider_requested="qwen_vllm",
            provider_attempted="qwen_vllm",
            raw_output=json.dumps(po),
            x1d_judges=_minimal_x1d_rows(),
            allowed_fact_ids=["bul_ibm_001"],
            test_only_mock_provider=False,
        )
    ]
    by_id = {g.gate_id: g for g in gates}
    assert not by_id["x2_no_mock_or_plumbing_language_in_real_l2_output"].pass_


def test_mock_x3_review_plumbing():
    run_cmd()
    x3 = load_json("x3_disposition.json")
    assert x3["x3_code"] == "X3_REVIEW_MOCKED_PLUMBING_ONLY"
    run_cmd()
    l6 = load_json("l6_shadow_eval_package.json")
    assert l6["offline_only"] is True
    assert l6["human_label_required"] is True
    assert l6["promotion_allowed"] is False
    assert l6["learning_mutation_performed"] is False
    assert l6["runtime_approval_authority"] == "NONE"
    assert l6["section_id"] == "ibm_narrative"
    assert l6.get("current_run_effect") == "none"
    assert l6.get("promotion_request_candidate") is False
    shadow = l6.get("ibm_narrative_shadow_learning") or {}
    assert shadow.get("current_run_effect") == "none"
    assert shadow.get("promotion_request_candidate") is False
    assert shadow.get("section_id") == "ibm_narrative"
    gate_rows = shadow.get("x2_claim_and_allowed_fact_gates") or []
    gate_ids = {str(g.get("gate_id")) for g in gate_rows if isinstance(g, dict)}
    assert "x2_claim_ledger_claim_text_non_empty" in gate_ids


def test_deprecated_ibm_narrative_dispatch_module_exits_with_guidance():
    r = subprocess.run(
        [sys.executable, "-m", "apps_rg.runtime.sections.ibm_narrative_lane_runtime"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert r.returncode == 2
    combined = f"{r.stderr}\n{r.stdout}"
    assert "--section" in combined and "ibm_narrative" in combined


def test_ibm_narrative_overlay_files_exist():
    expected = [
        "apps_rg/runtime/sections/ibm_narrative_lane_runtime.py",
        "apps_rg/runtime/sections/ibm_narrative_lane.py",
        "apps_rg/runtime/validators/ibm_narrative_x2.py",
        "apps_rg/runtime/judges/ibm_narrative_x1d.py",
        "apps_rg/runtime/exit/ibm_narrative_x3.py",
        "apps_rg/runtime/shadow/ibm_narrative_l6.py",
    ]
    for rel in expected:
        assert (REPO_ROOT / rel).is_file(), rel


def test_no_agentic_core_in_overlay_files():
    overlay = [
        REPO_ROOT / "apps_rg/runtime/sections/ibm_narrative_lane_runtime.py",
        REPO_ROOT / "apps_rg/runtime/sections/ibm_narrative_lane.py",
        REPO_ROOT / "apps_rg/runtime/validators/ibm_narrative_x2.py",
        REPO_ROOT / "apps_rg/runtime/judges/ibm_narrative_x1d.py",
        REPO_ROOT / "apps_rg/runtime/exit/ibm_narrative_x3.py",
        REPO_ROOT / "apps_rg/runtime/shadow/ibm_narrative_l6.py",
    ]
    for path in overlay:
        text = path.read_text(encoding="utf-8")
        assert "agentic_core" not in text, path


def _minimal_section_input_usage_ledger() -> dict[str, Any]:
    return {
        "schema": "section_input_usage_ledger_v1",
        "evidence_boundary": {
            "non_evidence_inputs_used_as_claim_evidence": False,
            "non_evidence_inputs_in_source_fact_ids": False,
        },
        "claim_support_summary": {
            "claims_with_targeting_input_in_source_fact_ids": 0,
            "claims_with_context_input_in_source_fact_ids": 0,
        },
    }

_FULL_METRIC_COMPANION = """bul_ibm_001: reclaimed $15M in annual run-rate cost.
bul_ibm_002: uptime 99.9%.
bul_ibm_003: 30% acceleration.
bul_ibm_004: cut 25% cycle time.
bul_ibm_005: boosted 50% adoption.
"""


def test_x3_soft_fail_unit():
    from apps_rg.runtime.exit.ibm_narrative_x3 import aggregate_x3

    x3 = aggregate_x3(
        resume_display_text="One IBM sentence.",
        claim_ledger=[{"claim_text": "c", "source_fact_ids": ["bul_ibm_001"]}],
        x2_gates=[{"gate_id": "x2_json_parse_valid", "pass": True}],
        x1d_judges=[
            {
                "provider_key": "gemini_pro",
                "evaluator_mode": "MODEL_BACKED",
                "provider_status": "MODEL_BACKED_PASS",
                "pass": True,
                "decisive_failure": False,
                "normalized_score": 1.0,
                "normalized_threshold": 0.8,
            },
            {
                "provider_key": "openai_chatgpt",
                "evaluator_mode": "MODEL_BACKED",
                "provider_status": "MODEL_BACKED_PASS",
                "pass": True,
                "decisive_failure": False,
                "normalized_score": 0.92,
                "normalized_threshold": 0.8,
            },
            {
                "provider_key": "anthropic_claude",
                "evaluator_mode": "MODEL_BACKED",
                "provider_status": "MODEL_BACKED_FAIL",
                "pass": False,
                "decisive_failure": False,
                "normalized_score": 0.72,
                "normalized_threshold": 0.8,
            },
        ],
        runtime_generation_status="REAL_LLM",
        product_quality_status="PASS",
        section_input_usage_ledger=_minimal_section_input_usage_ledger(),
    )
    assert x3.x3_code == "X3_REVIEW_JUDGE_SOFT_FAIL"


def test_x2_theme_coverage_fails_when_sentence_themes_outpace_ledger_union():
    from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_BULLET_IDS
    from apps_rg.runtime.validators.ibm_narrative_x2 import run_ibm_narrative_x2_gates

    po = {"section_id": "ibm_narrative"}
    narrative = (
        "At IBM, accelerated modernization for regulated financial services while strengthening lineage and observability."
    )
    gates = run_ibm_narrative_x2_gates(
        narrative_sentence=narrative,
        parsed_output=po,
        claim_ledger=[{"claim_text": "financial services modernization", "source_fact_ids": ["bul_ibm_001"]}],
        jd_text="",
        runtime_generation_status="REAL_LLM",
        companion_bullet_texts=None,
        provider_requested="qwen_vllm",
        provider_attempted="qwen_vllm",
        raw_output=json.dumps(po),
        x1d_judges=_minimal_x1d_rows(),
        allowed_fact_ids=list(IBM_BULLET_IDS),
    )
    by_id = {g.gate_id: g for g in gates}
    assert not by_id["x2_ibm_narrative_claim_theme_coverage"].pass_


def test_x2_rejects_migration_cadence_weak_jargon():
    from apps_rg.runtime.validators.ibm_narrative_x2 import run_ibm_narrative_x2_gates

    po = {"section_id": "ibm_narrative"}
    narrative = (
        "At IBM, tightened reliability posture and migration cadence for enterprise programs in regulated contexts."
    )
    gates = run_ibm_narrative_x2_gates(
        narrative_sentence=narrative,
        parsed_output=po,
        claim_ledger=[{"claim_text": "IBM delivery", "source_fact_ids": ["bul_ibm_001", "bul_ibm_002"]}],
        jd_text="",
        runtime_generation_status="REAL_LLM",
        companion_bullet_texts=None,
        provider_requested="qwen_vllm",
        provider_attempted="qwen_vllm",
        raw_output=json.dumps(po),
        x1d_judges=_minimal_x1d_rows(),
        allowed_fact_ids=["bul_ibm_001", "bul_ibm_002"],
    )
    by_id = {g.gate_id: g for g in gates}
    assert not by_id["x2_ibm_narrative_weak_resume_jargon_phrases"].pass_


def test_x2_metric_replay_fails_with_full_metric_companion_bundle():
    from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_BULLET_IDS
    from apps_rg.runtime.validators.ibm_narrative_x2 import run_ibm_narrative_x2_gates

    po = {"section_id": "ibm_narrative"}
    narrative = "Production discipline at IBM sustained 99.9% uptime in regulated delivery programs."
    gates = run_ibm_narrative_x2_gates(
        narrative_sentence=narrative,
        parsed_output=po,
        claim_ledger=[{"claim_text": "uptime", "source_fact_ids": ["bul_ibm_001"]}],
        jd_text="",
        runtime_generation_status="REAL_LLM",
        companion_bullet_texts=_FULL_METRIC_COMPANION,
        provider_requested="qwen_vllm",
        provider_attempted="qwen_vllm",
        raw_output=json.dumps(po),
        x1d_judges=_minimal_x1d_rows(),
        allowed_fact_ids=list(IBM_BULLET_IDS),
    )
    by_id = {g.gate_id: g for g in gates}
    assert not by_id["x2_no_metric_repetition_unless_justified"].pass_


def test_companion_metric_budget_collapse_strips_tracked_metrics_to_zero_when_companion_kpi_bundle():
    from apps_rg.runtime.sections.ibm_narrative_lane_runtime import collapse_narrative_sentence_for_companion_metric_budget
    from apps_rg.runtime.validators.ibm_narrative_x2 import count_ibm_narrative_metric_hits

    noisy = (
        "At IBM, platform teams delivered $15M run-rate exits, held 99.9% uptime, and accelerated modernization by 30%."
    )
    out = collapse_narrative_sentence_for_companion_metric_budget(noisy, _FULL_METRIC_COMPANION)
    assert count_ibm_narrative_metric_hits(out) == 0


def test_truncate_keeps_only_first_numeric_metric_in_clause():
    from apps_rg.runtime.sections.ibm_narrative_lane_runtime import truncate_narrative_after_first_metric_hit
    from apps_rg.runtime.validators.ibm_narrative_x2 import count_ibm_narrative_metric_hits

    raw = "IBM teams captured $15M savings while sustaining 99.9% uptime in regulated delivery."
    out = truncate_narrative_after_first_metric_hit(raw)
    assert "$15m" in out.lower() or "$15" in out
    assert "99.9%" not in out
    assert count_ibm_narrative_metric_hits(out) <= 1


def _minimal_x1d_rows() -> list[dict]:
    return [
        {"provider_key": "gemini_pro"},
        {"provider_key": "openai_chatgpt"},
        {"provider_key": "anthropic_claude"},
    ]


def test_ledger_fact_ids_string_source_fact_ids_one_token_not_chars():
    from apps_rg.runtime.validators.ibm_narrative_x2 import _ledger_fact_ids

    ledger = [{"claim_text": "architected platforms", "source_fact_ids": "bul_ibm_001"}]
    assert _ledger_fact_ids(ledger) == {"bul_ibm_001"}


def test_ledger_fact_ids_comma_separated_string():
    from apps_rg.runtime.validators.ibm_narrative_x2 import _ledger_fact_ids

    ledger = [{"claim_text": "x", "source_fact_ids": "bul_ibm_001, bul_ibm_002"}]
    assert _ledger_fact_ids(ledger) == {"bul_ibm_001", "bul_ibm_002"}


def test_ledger_fact_ids_list_form_still_works():
    from apps_rg.runtime.validators.ibm_narrative_x2 import _ledger_fact_ids

    ledger = [
        {"claim_text": "a", "source_fact_ids": ["bul_ibm_001"]},
        {"claim_text": "b", "source_fact_ids": ["bul_ibm_002", "bul_ibm_003"]},
    ]
    assert _ledger_fact_ids(ledger) == {"bul_ibm_001", "bul_ibm_002", "bul_ibm_003"}


def test_ledger_fact_ids_metric_suffix_stripped():
    from apps_rg.runtime.validators.ibm_narrative_x2 import _ledger_fact_ids

    ledger = [{"claim_text": "x", "source_fact_ids": "bul_ibm_001_metric_extra"}]
    assert _ledger_fact_ids(ledger) == {"bul_ibm_001"}


def test_string_source_fact_ids_passes_ibm_only_gates_when_valid():
    from apps_rg.runtime.validators.ibm_narrative_x2 import run_ibm_narrative_x2_gates

    po = {"section_id": "ibm_narrative"}
    raw = json.dumps(po)
    claim = [{"claim_text": "led enterprise cloud programs", "source_fact_ids": "bul_ibm_001"}]
    gates = run_ibm_narrative_x2_gates(
        narrative_sentence="At IBM, the executive led enterprise cloud programs for major accounts.",
        parsed_output=po,
        claim_ledger=claim,
        jd_text="",
        runtime_generation_status="REAL_LLM",
        companion_bullet_texts=None,
        provider_requested="qwen_vllm",
        provider_attempted="qwen_vllm",
        raw_output=raw,
        x1d_judges=_minimal_x1d_rows(),
        allowed_fact_ids=["bul_ibm_001"],
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_ibm_narrative_source_supported"].pass_
    assert by_id["x2_ibm_narrative_ibm_only_fact_scope"].pass_
    assert by_id["x2_claim_ledger_claim_text_non_empty"].pass_
    assert by_id["x2_claim_ledger_source_fact_ids_allow_list"].pass_


def test_invalid_non_ibm_source_fact_id_fails_ibm_gates():
    from apps_rg.runtime.validators.ibm_narrative_x2 import run_ibm_narrative_x2_gates

    po = {"section_id": "ibm_narrative"}
    raw = json.dumps(po)
    claim = [{"claim_text": "unify scope work", "source_fact_ids": "bul_unify_001"}]
    gates = run_ibm_narrative_x2_gates(
        narrative_sentence="At IBM, the executive led unify scope work for clients.",
        parsed_output=po,
        claim_ledger=claim,
        jd_text="",
        runtime_generation_status="REAL_LLM",
        companion_bullet_texts=None,
        provider_requested="qwen_vllm",
        provider_attempted="qwen_vllm",
        raw_output=raw,
        x1d_judges=_minimal_x1d_rows(),
        allowed_fact_ids=["bul_ibm_001"],
    )
    by_id = {g.gate_id: g for g in gates}
    assert not by_id["x2_ibm_narrative_source_supported"].pass_
    assert not by_id["x2_ibm_narrative_ibm_only_fact_scope"].pass_
    assert not by_id["x2_claim_ledger_source_fact_ids_allow_list"].pass_


def test_x2_claim_text_gate_fails_closed_on_whitespace_claim():
    from apps_rg.runtime.validators.ibm_narrative_x2 import run_ibm_narrative_x2_gates

    po = {"section_id": "ibm_narrative"}
    raw = json.dumps(po)
    claim = [{"claim_text": "   ", "source_fact_ids": ["bul_ibm_001"]}]
    gates = run_ibm_narrative_x2_gates(
        narrative_sentence="At IBM, the executive led enterprise cloud programs for major accounts.",
        parsed_output=po,
        claim_ledger=claim,
        jd_text="",
        runtime_generation_status="REAL_LLM",
        companion_bullet_texts=None,
        provider_requested="qwen_vllm",
        provider_attempted="qwen_vllm",
        raw_output=raw,
        x1d_judges=_minimal_x1d_rows(),
        allowed_fact_ids=["bul_ibm_001"],
    )
    by_id = {g.gate_id: g for g in gates}
    assert not by_id["x2_claim_ledger_claim_text_non_empty"].pass_
