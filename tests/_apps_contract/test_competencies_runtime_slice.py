from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LANE_KEY = "competencies"
CMD = [
    sys.executable,
    "-m",
    "apps_rg.runtime.dispatch.competencies_dispatch",
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
    result = run_cmd("--provider", "mock", "--allow-test-mock-provider", "--mock-judges")
    assert result.returncode == 0, result.stderr
    assert "COMPETENCIES_OUTPUT:" in result.stdout


def test_mock_eight_categories():
    run_cmd("--provider", "mock", "--allow-test-mock-provider", "--mock-judges")
    l2 = load_json("l2_output.json")
    assert len(l2["competencies"]) == 8


def test_x2_gate_count():
    run_cmd("--provider", "mock", "--allow-test-mock-provider", "--mock-judges")
    x2 = load_json("x2_gate_outputs.json")
    assert x2["total_x2_gates"] == 26
    assert x2["x2_failed"] == 0


def test_mock_x3_review_plumbing():
    run_cmd("--provider", "mock", "--allow-test-mock-provider", "--mock-judges")
    x3 = load_json("x3_disposition.json")
    assert x3["x3_code"] == "X3_REVIEW_MOCKED_PLUMBING_ONLY"


def test_l6_shadow_offline_only():
    run_cmd("--provider", "mock", "--allow-test-mock-provider", "--mock-judges")
    l6 = load_json("l6_shadow_eval_package.json")
    assert l6["offline_only"] is True
    assert l6["human_label_required"] is True
    assert l6["promotion_allowed"] is False
    assert l6["learning_mutation_performed"] is False
    assert l6["runtime_approval_authority"] == "NONE"
    assert l6["section_id"] == "competencies"


def test_competencies_overlay_files_exist():
    expected = [
        "apps_rg/runtime/dispatch/competencies_dispatch.py",
        "apps_rg/runtime/validators/competencies_x2.py",
        "apps_rg/runtime/judges/competencies_x1d.py",
        "apps_rg/runtime/exit/competencies_x3.py",
        "apps_rg/runtime/shadow/competencies_l6.py",
    ]
    for rel in expected:
        assert (REPO_ROOT / rel).is_file(), rel


def test_no_agentic_core_in_overlay_files():
    overlay = [
        REPO_ROOT / "apps_rg/runtime/dispatch/competencies_dispatch.py",
        REPO_ROOT / "apps_rg/runtime/validators/competencies_x2.py",
        REPO_ROOT / "apps_rg/runtime/judges/competencies_x1d.py",
        REPO_ROOT / "apps_rg/runtime/exit/competencies_x3.py",
        REPO_ROOT / "apps_rg/runtime/shadow/competencies_l6.py",
    ]
    for path in overlay:
        text = path.read_text(encoding="utf-8")
        assert "agentic_core" not in text, path


def test_duplicate_variants_collapsed_regression_fixture():
    """Historical REAL_LLM run duplicated 'high availability' across categories."""
    import json
    from pathlib import Path

    from apps_rg.runtime.dispatch.competencies_dispatch import (
        JD_TEXT_DEFAULT,
        build_resume_support_blob,
        collect_employment_bullets,
        collapse_duplicate_competency_terms,
        load_base_resume,
        load_companion_context,
        rebuild_claim_ledger_from_competencies,
    )
    from apps_rg.runtime.validators.competencies_x2 import run_competencies_x2_gates

    fixture = (
        REPO_ROOT
        / "artifacts"
        / "apps_rg"
        / "runtime_proofs"
        / "competencies"
        / "real"
        / "competencies_20260515_190942"
        / "l2_output.json"
    )
    if not fixture.is_file():
        pytest.skip(f"Missing competencies regression fixture under {fixture.parent}")
    p = json.loads(fixture.read_text(encoding="utf-8"))
    base, _, _ = load_base_resume()
    rows, allowed, bullet_lowers = collect_employment_bullets(base)
    blob = build_resume_support_blob(rows, load_companion_context())
    parsed = {
        "competencies": json.loads(json.dumps(p["competencies"])),
        "selected_fact_plan": p["selected_fact_plan"],
        "jd_alignment": p.get("jd_alignment", {}),
        "excluded_jd_skills": list(p.get("excluded_jd_skills") or []),
        "removed_or_rewritten_terms": list(p.get("removed_or_rewritten_terms") or []),
        "gap_notes": list(p.get("gap_notes") or []),
        "change_log": list(p.get("change_log") or []),
        "self_check": p.get("self_check", {}) or {},
        "claim_ledger": list(p.get("claim_ledger") or []),
    }
    flat_before = []
    for c in parsed["competencies"]:
        flat_before.extend(str(t).lower() for t in (c.get("terms") or []) if str(t).strip())
    assert flat_before.count("high availability") >= 2

    collapse_duplicate_competency_terms(parsed, rows, blob)
    rebuild_claim_ledger_from_competencies(parsed, allowed)
    flat_after = []
    for c in parsed["competencies"]:
        flat_after.extend(str(t).lower() for t in (c.get("terms") or []) if str(t).strip())
    assert flat_after.count("high availability") <= 1

    gates = run_competencies_x2_gates(
        competencies=parsed["competencies"],
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        jd_text=JD_TEXT_DEFAULT,
        bullet_texts_lower=bullet_lowers,
        resume_support_blob=blob,
        allowed_fact_ids=allowed,
        runtime_generation_status="REAL_LLM",
        provider_requested="qwen_vllm",
        provider_attempted="qwen_vllm",
        model_name="regression",
        raw_output=json.dumps(parsed, sort_keys=True),
        x1d_judges=[],
    )
    dup = next(g for g in gates if g.gate_id == "x2_duplicate_variants_collapsed")
    assert dup.pass_ is True, dup.observed_value


def test_x3_soft_fail_unit():
    from apps_rg.runtime.exit.competencies_x3 import aggregate_x3

    x3 = aggregate_x3(
        resume_display_text="Label: one, two, three",
        claim_ledger=[{"claim_text": "one", "source_fact_ids": ["bul_unify_001"]}],
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
