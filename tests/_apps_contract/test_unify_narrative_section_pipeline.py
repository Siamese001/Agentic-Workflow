"""Contract tests: unify_narrative runs through ``python -m apps_rg`` + canonical_dispatch only."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from tests._apps_contract.lane_cli_common import (
    REPO_ROOT as REPO,
    base_canonical_argv,
    contract_artifact_dir,
    contract_env,
    contract_live_pytestmark,
    run_lane_cli_once,
)

pytestmark = contract_live_pytestmark("unify_narrative")

_SYNTHETIC_COMPANY = "Synthetic Enterprise Corp."
_SYNTHETIC_ROLE = "SVP Engineering, Agentic AI Platforms"

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


@pytest.fixture(scope="module")
def unify_narrative_lane_run_dir() -> Path:
    return run_lane_cli_once(
        "unify_narrative",
        run_key="unify_narrative_pipeline_module",
        target_company=_SYNTHETIC_COMPANY,
        target_role=_SYNTHETIC_ROLE,
    )


def test_canonical_cli_emits_required_unify_narrative_artifacts(unify_narrative_lane_run_dir: Path):
    rd = unify_narrative_lane_run_dir
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
    art = contract_artifact_dir("unify_narrative")
    rel = art.relative_to(REPO).as_posix()
    cmd = base_canonical_argv(
        "unify_narrative",
        artifact_dir=rel,
        target_company=_SYNTHETIC_COMPANY,
        target_role=_SYNTHETIC_ROLE,
    )
    sec_idx = cmd.index("--section")
    cmd = cmd[:sec_idx] + ["--unify-narrative"] + cmd[sec_idx + 2 :]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=600, env=contract_env())
    assert r.returncode == 0, r.stderr


def test_canonical_dispatch_does_not_reference_unify_narrative_dispatch():
    path = REPO / "apps_rg" / "runtime" / "orchestration" / "canonical_dispatch.py"
    text = path.read_text(encoding="utf-8")
    assert "unify_narrative_dispatch" not in text


def test_compiled_unify_narrative_prompt_contains_allowed_source_fact_ids_and_claim_text_contract(
    unify_narrative_lane_run_dir: Path,
):
    rd = unify_narrative_lane_run_dir
    compiled = (rd / "compiled_prompt.txt").read_text(encoding="utf-8").lower()
    assert "allowed_source_fact_ids" in compiled
    assert "bul_unify_001" in compiled
    assert "unify_narrative_base_001" in compiled
    assert "north-star" in compiled or "north star" in compiled
    assert "claim_text" in compiled
    assert "non-empty" in compiled


def test_x2_contains_claim_text_gate_and_passes_on_live_run(unify_narrative_lane_run_dir: Path):
    rd = unify_narrative_lane_run_dir
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
    art = contract_artifact_dir("unify_narrative")
    rel = art.relative_to(REPO).as_posix()
    r = run_lane_cli(
        "unify_narrative",
        artifact_dir=rel,
        target_company=_SYNTHETIC_COMPANY,
        target_role=_SYNTHETIC_ROLE,
        timeout_s=600,
    )
    assert r.returncode == 0
    assert "L2_UNIFY_NARRATIVE_OUTPUT:" in r.stdout
