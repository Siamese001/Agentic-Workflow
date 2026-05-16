from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LANE_KEY = "ibm_narrative"
CMD = [
    sys.executable,
    "-m",
    "apps_rg.runtime.dispatch.ibm_narrative_dispatch",
    "--allow-non-allow-exit-zero",
]


def run_cmd(*extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(CMD + list(extra), cwd=REPO_ROOT, text=True, capture_output=True, timeout=180)


def mock_artifacts_dir() -> Path:
    from apps_rg.runtime.runtime_proof_layout import resolve_latest_mock_run_dir

    rd = resolve_latest_mock_run_dir(REPO_ROOT, LANE_KEY)
    if rd is not None:
        return rd
    legacy = REPO_ROOT / "artifacts" / "apps_rg" / "runtime_proofs" / LANE_KEY
    if (legacy / "l2_output.json").is_file():
        return legacy
    raise AssertionError(f"No mock artifacts for lane {LANE_KEY}; run mock dispatch first")


def load_json(name: str):
    return json.loads((mock_artifacts_dir() / name).read_text(encoding="utf-8"))


def test_mock_dispatch_executes():
    result = run_cmd("--provider", "mock", "--mock-judges")
    assert result.returncode == 0, result.stderr
    assert "IBM_NARRATIVE_OUTPUT:" in result.stdout


def test_mock_one_sentence():
    run_cmd("--provider", "mock", "--mock-judges")
    l2 = load_json("l2_output.json")
    text = l2["narrative_sentence"].strip()
    assert text.count(".") >= 1
    assert "\n" not in text or len(text.split(".")) <= 2


def test_x2_gate_count():
    run_cmd("--provider", "mock", "--mock-judges")
    x2 = load_json("x2_gate_outputs.json")
    assert x2["total_x2_gates"] == 20
    assert x2["x2_failed"] == 0


def test_mock_x3_review_plumbing():
    run_cmd("--provider", "mock", "--mock-judges")
    x3 = load_json("x3_disposition.json")
    assert x3["x3_code"] == "X3_REVIEW_MOCKED_PLUMBING_ONLY"


def test_l6_shadow_offline_only():
    run_cmd("--provider", "mock", "--mock-judges")
    l6 = load_json("l6_shadow_eval_package.json")
    assert l6["offline_only"] is True
    assert l6["human_label_required"] is True
    assert l6["promotion_allowed"] is False
    assert l6["learning_mutation_performed"] is False
    assert l6["runtime_approval_authority"] == "NONE"
    assert l6["section_id"] == "ibm_narrative"


def test_ibm_narrative_overlay_files_exist():
    expected = [
        "apps_rg/runtime/dispatch/ibm_narrative_dispatch.py",
        "apps_rg/runtime/validators/ibm_narrative_x2.py",
        "apps_rg/runtime/judges/ibm_narrative_x1d.py",
        "apps_rg/runtime/exit/ibm_narrative_x3.py",
        "apps_rg/runtime/shadow/ibm_narrative_l6.py",
    ]
    for rel in expected:
        assert (REPO_ROOT / rel).is_file(), rel


def test_no_agentic_core_in_overlay_files():
    overlay = [
        REPO_ROOT / "apps_rg/runtime/dispatch/ibm_narrative_dispatch.py",
        REPO_ROOT / "apps_rg/runtime/validators/ibm_narrative_x2.py",
        REPO_ROOT / "apps_rg/runtime/judges/ibm_narrative_x1d.py",
        REPO_ROOT / "apps_rg/runtime/exit/ibm_narrative_x3.py",
        REPO_ROOT / "apps_rg/runtime/shadow/ibm_narrative_l6.py",
    ]
    for path in overlay:
        text = path.read_text(encoding="utf-8")
        assert "agentic_core" not in text, path


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
    )
    assert x3.x3_code == "X3_REVIEW_JUDGE_SOFT_FAIL"


_FULL_METRIC_COMPANION = """bul_ibm_001: reclaimed $15M in annual run-rate cost.
bul_ibm_002: uptime 99.9%.
bul_ibm_003: 30% acceleration.
bul_ibm_004: cut 25% cycle time.
bul_ibm_005: boosted 50% adoption.
"""


def test_companion_metric_budget_collapse_keeps_single_tracked_metric():
    from apps_rg.runtime.dispatch.ibm_narrative_dispatch import collapse_narrative_sentence_for_companion_metric_budget
    from apps_rg.runtime.validators.ibm_narrative_x2 import count_ibm_narrative_metric_hits

    noisy = (
        "At IBM, platform teams delivered $15M run-rate exits, held 99.9% uptime, and accelerated modernization by 30%."
    )
    out = collapse_narrative_sentence_for_companion_metric_budget(noisy, _FULL_METRIC_COMPANION)
    assert count_ibm_narrative_metric_hits(out) <= 1


def test_truncate_keeps_only_first_numeric_metric_in_clause():
    from apps_rg.runtime.dispatch.ibm_narrative_dispatch import truncate_narrative_after_first_metric_hit
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
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_ibm_narrative_source_supported"].pass_
    assert by_id["x2_ibm_narrative_ibm_only_fact_scope"].pass_


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
    )
    by_id = {g.gate_id: g for g in gates}
    assert not by_id["x2_ibm_narrative_source_supported"].pass_
    assert not by_id["x2_ibm_narrative_ibm_only_fact_scope"].pass_
