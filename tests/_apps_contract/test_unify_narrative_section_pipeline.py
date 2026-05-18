"""Contract tests: unify_narrative runs through ``python -m apps_rg`` + canonical_dispatch only."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

_MIN_JD_ALIGNMENT = {
    "selected_jd_themes": ["synthetic contract theme"],
    "selected_briefing_themes": [],
    "targeting_rationale": "Synthetic test rationale for deterministic X2 gates.",
    "jd_used_as_proof": False,
    "briefing_used_as_proof": False,
    "targeting_only": True,
}


def _unify_narrative_proof_allowlist() -> set[str]:
    from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS

    return set(UNIFY_BULLET_IDS) | {"unify_narrative_base_001", "exp_unify_001"}


BASE_CANONICAL = [
    sys.executable,
    "-m",
    "apps_rg",
    "--section",
    "unify_narrative",
    "--target-company",
    "Synthetic Enterprise Corp.",
    "--target-role",
    "SVP Engineering, Agentic AI Platforms",
    "--provider",
    "mock",
    "--mock-judges",
    "--allow-test-mock-judges",
    "--allow-non-allow-exit-zero",
]


def _latest_run_dir() -> Path:
    from apps_rg.runtime.runtime_proof_layout import resolve_latest_mock_run_dir

    rd = resolve_latest_mock_run_dir(REPO, "unify_narrative")
    assert rd is not None
    return rd


def _run_unify_narr_contract() -> None:
    subprocess.run(BASE_CANONICAL, cwd=REPO, capture_output=True, text=True, timeout=180, check=True)


def test_canonical_cli_emits_required_unify_narrative_artifacts():
    r = subprocess.run(BASE_CANONICAL, cwd=REPO, capture_output=True, text=True, timeout=180)
    assert r.returncode == 0, r.stderr
    rd = _latest_run_dir()
    required = [
        "compiled_prompt.txt",
        "compiled_prompt_artifact.json",
        "provider_request.json",
        "provider_response.json",
        "parsed_output.json",
        "canonical_claim_ledger_v2.json",
        "text_claim_coverage.json",
        "x2_gate_outputs.json",
        "x3_disposition.json",
        "l6_shadow_eval_package.json",
        "l6_shadow_learning.json",
    ]
    for name in required:
        assert (rd / name).is_file(), f"missing {name} under {rd}"


def test_unify_narrative_section_flag_alias():
    cmd = [
        sys.executable,
        "-m",
        "apps_rg",
        "--unify-narrative",
        "--target-company",
        "Synthetic Enterprise Corp.",
        "--target-role",
        "SVP Engineering, Agentic AI Platforms",
        "--provider",
        "mock",
        "--mock-judges",
        "--allow-test-mock-judges",
        "--allow-non-allow-exit-zero",
    ]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=180)
    assert r.returncode == 0, r.stderr


def test_canonical_dispatch_does_not_reference_unify_narrative_dispatch():
    path = REPO / "apps_rg" / "runtime" / "orchestration" / "canonical_dispatch.py"
    text = path.read_text(encoding="utf-8")
    assert "unify_narrative_dispatch" not in text


def test_compiled_unify_narrative_prompt_contains_allowed_source_fact_ids_and_claim_text_contract():
    _run_unify_narr_contract()
    rd = _latest_run_dir()
    compiled = (rd / "compiled_prompt.txt").read_text(encoding="utf-8").lower()
    assert "allowed_source_fact_ids" in compiled
    assert "bul_unify_001" in compiled
    assert "unify_narrative_base_001" in compiled
    assert "north-star" in compiled or "north star" in compiled
    assert "claim_text" in compiled
    assert "non-empty" in compiled


def test_x2_contains_claim_text_gate_and_passes_on_mock():
    _run_unify_narr_contract()
    rd = _latest_run_dir()
    x2 = json.loads((rd / "x2_gate_outputs.json").read_text(encoding="utf-8"))
    gate_ids = {g["gate_id"] for g in x2["gates"]}
    assert "x2_claim_ledger_claim_text_non_empty" in gate_ids
    g = next(g for g in x2["gates"] if g["gate_id"] == "x2_claim_ledger_claim_text_non_empty")
    assert g["pass"] is True
    assert x2["failed_gates"] == []


def test_x2_claim_text_gate_fails_empty_ledger():
    from apps_rg.runtime.validators.unify_narrative_x2 import run_unify_narrative_x2_gates

    gates = run_unify_narrative_x2_gates(
        narrative_sentence="One sentence only.",
        parsed_output={"claim_ledger": [], "jd_alignment": _MIN_JD_ALIGNMENT},
        claim_ledger=[],
        jd_text="jd",
        briefing_text="",
        runtime_generation_status="MOCKED",
        companion_bullet_texts="",
        x1d_judges=[],
        allowed_fact_ids=_unify_narrative_proof_allowlist(),
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_claim_ledger_claim_text_non_empty"].pass_ is False


def test_x2_claim_text_gate_fails_blank_claim_text():
    from apps_rg.runtime.validators.unify_narrative_x2 import run_unify_narrative_x2_gates

    led = [{"claim_text": "   ", "source_fact_ids": ["bul_unify_001"]}]
    gates = run_unify_narrative_x2_gates(
        narrative_sentence="One sentence only.",
        parsed_output={"claim_ledger": led, "jd_alignment": _MIN_JD_ALIGNMENT},
        claim_ledger=led,
        jd_text="jd",
        briefing_text="",
        runtime_generation_status="MOCKED",
        companion_bullet_texts="",
        x1d_judges=[],
        allowed_fact_ids=_unify_narrative_proof_allowlist(),
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_claim_ledger_claim_text_non_empty"].pass_ is False


def test_x2_claim_text_gate_fails_missing_claim_text_key():
    from apps_rg.runtime.validators.unify_narrative_x2 import run_unify_narrative_x2_gates

    led = [{"source_fact_ids": ["bul_unify_001"]}]
    gates = run_unify_narrative_x2_gates(
        narrative_sentence="One sentence only.",
        parsed_output={"claim_ledger": led, "jd_alignment": _MIN_JD_ALIGNMENT},
        claim_ledger=led,
        jd_text="jd",
        briefing_text="",
        runtime_generation_status="MOCKED",
        companion_bullet_texts="",
        x1d_judges=[],
        allowed_fact_ids=_unify_narrative_proof_allowlist(),
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_claim_ledger_claim_text_non_empty"].pass_ is False


def test_x2_claim_text_gate_passes_non_empty_with_unify_ids():
    from apps_rg.runtime.validators.unify_narrative_x2 import run_unify_narrative_x2_gates

    led = [{"claim_text": "Architected governed execution.", "source_fact_ids": ["bul_unify_001"]}]
    gates = run_unify_narrative_x2_gates(
        narrative_sentence="One sentence only.",
        parsed_output={"claim_ledger": led, "jd_alignment": _MIN_JD_ALIGNMENT},
        claim_ledger=led,
        jd_text="jd",
        briefing_text="",
        runtime_generation_status="MOCKED",
        companion_bullet_texts="",
        x1d_judges=[],
        allowed_fact_ids=_unify_narrative_proof_allowlist(),
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_claim_ledger_claim_text_non_empty"].pass_ is True


def test_cli_stdout_mentions_unify_narrative_lane():
    r = subprocess.run(BASE_CANONICAL, cwd=REPO, capture_output=True, text=True, timeout=180)
    assert r.returncode == 0
    assert "L2_UNIFY_NARRATIVE_OUTPUT:" in r.stdout
