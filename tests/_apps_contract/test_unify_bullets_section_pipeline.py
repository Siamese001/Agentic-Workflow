"""Contract tests: unify_bullets runs through ``python -m apps_rg`` + canonical_dispatch only."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _apps_rg_contract_env() -> dict[str, str]:
    """Deterministic mock+provider runs: avoid live vLLM JSON typos breaking X2 gates."""
    return {**os.environ, "APPS_RG_QWEN_OFFLINE_CONTRACT_STUB": "1"}

BASE_CANONICAL = [
    sys.executable,
    "-m",
    "apps_rg",
    "--section",
    "unify_bullets",
    "--target-company",
    "Synthetic Enterprise Corp.",
    "--target-role",
    "SVP Engineering, Agentic AI Platforms",
    "--provider",
    "mock",
    "--mock-judges",
    "--allow-non-allow-exit-zero",
]


def _latest_run_dir() -> Path:
    from apps_rg.runtime.runtime_proof_layout import resolve_latest_mock_run_dir

    rd = resolve_latest_mock_run_dir(REPO, "unify_bullets")
    assert rd is not None
    return rd


def _run_unify_contract() -> None:
    subprocess.run(
        BASE_CANONICAL,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        check=True,
        env=_apps_rg_contract_env(),
    )


def test_canonical_cli_emits_required_unify_bullets_artifacts():
    r = subprocess.run(
        BASE_CANONICAL,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        env=_apps_rg_contract_env(),
    )
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
        "run_manifest.json",
    ]
    for name in required:
        assert (rd / name).is_file(), f"missing {name} under {rd}"


def test_unify_section_flag_alias():
    cmd = [
        sys.executable,
        "-m",
        "apps_rg",
        "--unify-bullets",
        "--target-company",
        "Synthetic Enterprise Corp.",
        "--target-role",
        "SVP Engineering, Agentic AI Platforms",
        "--provider",
        "mock",
        "--mock-judges",
        "--allow-non-allow-exit-zero",
    ]
    r = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        env=_apps_rg_contract_env(),
    )
    assert r.returncode == 0, r.stderr


def test_canonical_dispatch_does_not_reference_unify_dispatch():
    path = REPO / "apps_rg" / "runtime" / "orchestration" / "canonical_dispatch.py"
    text = path.read_text(encoding="utf-8")
    assert "unify_bullets_dispatch" not in text


def test_compiled_unify_prompt_contains_allowed_source_fact_ids_and_claim_text_contract():
    _run_unify_contract()
    rd = _latest_run_dir()
    compiled = (rd / "compiled_prompt.txt").read_text(encoding="utf-8").lower()
    assert "allowed_source_fact_ids" in compiled
    assert "bul_unify_001" in compiled
    assert "claim_text" in compiled
    assert "non-empty" in compiled


def test_x2_contains_claim_text_gate_and_passes_on_mock():
    _run_unify_contract()
    rd = _latest_run_dir()
    x2 = json.loads((rd / "x2_gate_outputs.json").read_text(encoding="utf-8"))
    gate_ids = {g["gate_id"] for g in x2["gates"]}
    assert "x2_claim_ledger_claim_text_non_empty" in gate_ids
    g = next(g for g in x2["gates"] if g["gate_id"] == "x2_claim_ledger_claim_text_non_empty")
    assert g["pass"] is True
    assert x2["failed_gates"] == []


def test_x2_text_claim_coverage_integrity_gate_present_and_passes_on_mock():
    _run_unify_contract()
    rd = _latest_run_dir()
    x2 = json.loads((rd / "x2_gate_outputs.json").read_text(encoding="utf-8"))
    gate_ids = {g["gate_id"] for g in x2["gates"]}
    assert "x2_text_claim_coverage_integrity" in gate_ids
    ig = next(g for g in x2["gates"] if g["gate_id"] == "x2_text_claim_coverage_integrity")
    assert ig["pass"] is True


def test_canonical_claim_ledger_ids_use_unify_bullets_prefix_on_mock():
    _run_unify_contract()
    rd = _latest_run_dir()
    canon = json.loads((rd / "canonical_claim_ledger_v2.json").read_text(encoding="utf-8"))
    for row in canon.get("claims") or []:
        cid = str(row.get("claim_id") or "")
        assert cid.startswith("unify_bullets_claim_"), cid


def test_text_claim_coverage_structural_schema_on_mock():
    _run_unify_contract()
    rd = _latest_run_dir()
    cov = json.loads((rd / "text_claim_coverage.json").read_text(encoding="utf-8"))
    assert cov.get("coverage_schema") == "unify_bullets_structural_v1"
    assert len(cov.get("sentences") or []) == 6
    assert cov.get("overall_pass") is True
    ids = [s.get("bullet_id") for s in cov["sentences"]]
    assert ids == [
        "bul_unify_001",
        "bul_unify_002",
        "bul_unify_003",
        "bul_unify_004",
        "bul_unify_005",
        "bul_unify_006",
    ]


def test_x3_code_and_failed_gate_lists_on_mock_review():
    _run_unify_contract()
    rd = _latest_run_dir()
    x3 = json.loads((rd / "x3_disposition.json").read_text(encoding="utf-8"))
    assert x3["x3_code"] == "X3_REVIEW_MOCKED_PLUMBING_ONLY"
    assert "x2_failed_gates" in x3
    assert "proof_eligible" in x3
    assert "judge_proof_eligible" in x3


def test_run_manifest_contains_proof_eligible_fields():
    _run_unify_contract()
    rd = _latest_run_dir()
    mf = json.loads((rd / "run_manifest.json").read_text(encoding="utf-8"))
    assert "proof_eligible" in mf
    assert "judge_proof_eligible" in mf
    assert mf["proof_scope"] == "plumbing_only"
    assert mf["test_only_mock_provider"] is True
    assert mf["test_only_mock_judges"] is True


def test_l6_learning_shadow_written_after_x3_par_key_fields():
    from apps_rg.runtime.shadow.unify_bullets_l6 import CLAIM_TEXT_GATE_ID
    from apps_rg.runtime.validators.unify_bullets_x2 import TEXT_COVERAGE_INTEGRITY_GATE_ID

    _run_unify_contract()
    rd = _latest_run_dir()
    x3_mtime = (rd / "x3_disposition.json").stat().st_mtime_ns
    l6_mtime = (rd / "l6_shadow_eval_package.json").stat().st_mtime_ns
    assert l6_mtime >= x3_mtime

    x2_blob = json.loads((rd / "x2_gate_outputs.json").read_text(encoding="utf-8"))
    ct_gate = next(g for g in x2_blob["gates"] if g["gate_id"] == CLAIM_TEXT_GATE_ID)

    pkg = json.loads((rd / "l6_shadow_eval_package.json").read_text(encoding="utf-8"))
    assert pkg["section_id"] == "unify_bullets"
    assert pkg.get("offline_only") is True
    assert pkg.get("human_label_required") is True
    assert pkg.get("future_run_only") is True
    assert pkg.get("current_run_mutation_assertion") is False
    assert pkg.get("current_run_rescue_assertion") is False
    assert pkg.get("durable_write_assertion") is False
    assert pkg.get("direct_l4_write_assertion") is False
    assert pkg.get("learning_promotion_status") == "NOT_REQUESTED"
    assert pkg.get("claim_text_gate_id") == CLAIM_TEXT_GATE_ID
    assert pkg.get("claim_text_gate_result") is bool(ct_gate.get("pass"))
    assert pkg.get("text_claim_coverage_integrity_gate_id") == TEXT_COVERAGE_INTEGRITY_GATE_ID
    cov_gate = next(g for g in x2_blob["gates"] if g["gate_id"] == TEXT_COVERAGE_INTEGRITY_GATE_ID)
    assert pkg.get("text_claim_coverage_integrity_gate_pass") is bool(cov_gate.get("pass"))
    assert pkg.get("provider") == "mock"
    assert pkg.get("x3_code") == "X3_REVIEW_MOCKED_PLUMBING_ONLY"
    rid = pkg.get("run_id")
    assert isinstance(rid, str) and len(rid) > 4
    srd = pkg.get("source_run_dir") or ""
    assert rid in str(srd)
    assert isinstance(pkg.get("x2_failed_gates"), list)
    assert "proof_eligible" in pkg
    assert "judge_proof_eligible" in pkg
    mf_pkg = json.loads((rd / "run_manifest.json").read_text(encoding="utf-8"))
    assert pkg["proof_eligible"] is mf_pkg["proof_eligible"]


def test_x3_block_when_claim_text_gate_fails_in_aggregate():
    from apps_rg.runtime.exit.unify_bullets_x3 import aggregate_x3

    x3 = aggregate_x3(
        resume_display_text="bullets text",
        claim_ledger=[{"claim_text": "ok", "source_fact_ids": ["bul_unify_001"]}],
        x2_gates=[{"gate_id": "x2_claim_ledger_claim_text_non_empty", "pass": False}],
        x1d_judges=[
            {"provider_key": "gemini_pro", "evaluator_mode": "MODEL_BACKED", "pass": True},
        ],
        runtime_generation_status="REAL_LLM",
        product_quality_status="PASS",
    )
    assert x3.x3_code == "X3_BLOCK"
    assert "x2_claim_ledger_claim_text_non_empty" in x3.x2_failed_gates


def _payload_and_allowed():
    from apps_rg.runtime.sections.unify_bullets_lane import (
        build_runtime_payload,
        build_selected_fact_plan,
        extract_unify_employment,
        load_base_resume,
    )

    base, path, base_hash = load_base_resume()
    header, facts, allowed = extract_unify_employment(base)
    plan = build_selected_fact_plan(facts)
    rp = build_runtime_payload(
        base_json_path=path,
        base_hash=base_hash,
        unify_header=header,
        selected_fact_plan=plan,
        allowed_fact_ids=allowed,
        target_title="SVP",
        target_company="Corp",
        jd_text="AI governance synthetic role description.",
        briefing="regulated",
    )
    return rp, allowed, facts


def _three_model_backed_judges_pass() -> list[dict]:
    key = {"evaluator_mode": "MODEL_BACKED", "provider_status": "MODEL_BACKED_PASS", "pass": True, "decisive_failure": False}
    return [
        {"provider_key": "gemini_pro", **key},
        {"provider_key": "openai_chatgpt", **key},
        {"provider_key": "anthropic_claude", **key},
    ]


def _run_x2(parsed_template: dict, *, merged_claim_ledger: list | None) -> dict[str, bool]:
    from apps_rg.runtime.sections.unify_bullets_lane import normalize_unify_parsed_without_ledger_synthesis
    from apps_rg.runtime.validators.unify_bullets_x2 import (
        build_unify_bullets_text_claim_coverage,
        run_unify_bullets_x2_gates,
    )

    rp, allowed, _ = _payload_and_allowed()
    parsed = normalize_unify_parsed_without_ledger_synthesis(dict(parsed_template), rp)
    assert parsed is not None
    bullets = list(parsed["bullets"])

    parsed_out = dict(parsed)
    if merged_claim_ledger is not None:
        parsed_out["claim_ledger"] = merged_claim_ledger

    ledger_for_checks = merged_claim_ledger if merged_claim_ledger is not None else list(parsed_out.get("claim_ledger") or [])
    enriched_min = dict(parsed_out)
    enriched_min["text_claim_coverage"] = build_unify_bullets_text_claim_coverage(
        bullets,
        ledger_for_checks,
        allowed,
    )

    gates = run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=enriched_min,
        claim_ledger=ledger_for_checks,
        allowed_fact_ids=allowed,
        jd_text=str(rp.get("jd_text") or ""),
        runtime_generation_status="MOCKED",
        rewrite_distribution=parsed_out.get("rewrite_distribution"),
        x1d_judges=_three_model_backed_judges_pass(),
    )
    return {g.gate_id: g.pass_ for g in gates}


def test_x2_required_keys_fail_when_claim_ledger_missing():
    from apps_rg.runtime.sections.unify_bullets_lane import build_mock_output

    rp, _, _ = _payload_and_allowed()
    base = build_mock_output(rp)
    del base["claim_ledger"]
    gm = _run_x2(base, merged_claim_ledger=None)
    assert gm["x2_required_top_level_json_keys"] is False


def test_x2_claim_text_gate_fails_when_claim_text_missing():
    from apps_rg.runtime.sections.unify_bullets_lane import build_mock_output

    rp, _, _ = _payload_and_allowed()
    parsed = build_mock_output(rp)
    led = list(parsed["claim_ledger"])
    led[0] = {"source_fact_ids": ["bul_unify_001"]}
    gm = _run_x2(parsed, merged_claim_ledger=led)
    assert gm["x2_claim_ledger_claim_text_non_empty"] is False


def test_x2_claim_text_gate_fails_null_empty_whitespace():
    from apps_rg.runtime.sections.unify_bullets_lane import build_mock_output

    rp, _, _ = _payload_and_allowed()
    parsed = build_mock_output(rp)

    led = json.loads(json.dumps(parsed["claim_ledger"]))
    led[0] = {"claim_text": None, "source_fact_ids": ["bul_unify_001"]}
    assert _run_x2(parsed, merged_claim_ledger=led)["x2_claim_ledger_claim_text_non_empty"] is False

    led[0] = {"claim_text": "", "source_fact_ids": ["bul_unify_001"]}
    assert _run_x2(parsed, merged_claim_ledger=led)["x2_claim_ledger_claim_text_non_empty"] is False

    led[0] = {"claim_text": "   ", "source_fact_ids": ["bul_unify_001"]}
    assert _run_x2(parsed, merged_claim_ledger=led)["x2_claim_ledger_claim_text_non_empty"] is False


def test_claim_text_gate_passes_for_normalized_mock_output():
    from apps_rg.runtime.sections.unify_bullets_lane import build_mock_output

    rp, _, _ = _payload_and_allowed()
    parsed = build_mock_output(rp)
    gm = _run_x2(parsed, merged_claim_ledger=None)
    assert gm["x2_claim_ledger_claim_text_non_empty"] is True


def test_x2_unify_only_fact_scope_passes_on_normalized_mock_output():
    from apps_rg.runtime.sections.unify_bullets_lane import build_mock_output

    rp, _, _ = _payload_and_allowed()
    gm = _run_x2(build_mock_output(rp), merged_claim_ledger=None)
    assert gm["x2_unify_only_fact_scope"] is True


def test_x2_unify_only_fact_scope_fails_when_bullet_row_has_bul_un_ify_typo():
    from apps_rg.runtime.sections.unify_bullets_lane import build_mock_output, normalize_unify_parsed_without_ledger_synthesis
    from apps_rg.runtime.validators.unify_bullets_x2 import (
        build_unify_bullets_text_claim_coverage,
        run_unify_bullets_x2_gates,
    )

    rp, allowed, _ = _payload_and_allowed()
    parsed = normalize_unify_parsed_without_ledger_synthesis(dict(build_mock_output(rp)), rp)
    assert parsed is not None
    bullets: list[dict] = []
    for b in parsed["bullets"]:
        if b.get("bullet_id") == "bul_unify_006":
            bullets.append({**dict(b), "source_fact_ids": ["bul_unify_006", "bul_un_ify_006_metric_deadbeef"]})
        else:
            bullets.append(dict(b))
    ledger = list(parsed["claim_ledger"])
    enriched = dict(parsed)
    enriched["bullets"] = bullets
    enriched["text_claim_coverage"] = build_unify_bullets_text_claim_coverage(bullets, ledger, allowed)
    gates = run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=enriched,
        claim_ledger=ledger,
        allowed_fact_ids=allowed,
        jd_text=str(rp.get("jd_text") or ""),
        runtime_generation_status="REAL_LLM",
        rewrite_distribution=parsed.get("rewrite_distribution"),
        x1d_judges=_three_model_backed_judges_pass(),
    )
    scope = next(g for g in gates if g.gate_id == "x2_unify_only_fact_scope")
    assert scope.pass_ is False
    assert scope.failure_reason and "tokens_not_bul_unify_prefix" in scope.failure_reason
    assert "bul_un_ify_006_metric_deadbeef" in scope.failure_reason


def test_compiled_unify_prompt_documents_bul_un_ify_typo_guard():
    from apps_rg.runtime.dispatch.unify_bullets_pa import compile_unify_bullets_prompt

    rp, _, _ = _payload_and_allowed()
    sp = compile_unify_bullets_prompt(rp, run_id="contract_typo_guard_compile")
    blob = sp.artifact.system_prompt.lower()
    assert "bul_un_ify" in blob
    assert "x2_unify_only_fact_scope" in blob


def test_normalize_does_not_synthesize_claim_ledger_from_bullets():
    from apps_rg.runtime.sections.unify_bullets_lane import build_mock_output, normalize_unify_parsed_without_ledger_synthesis

    rp, _, _ = _payload_and_allowed()
    p = dict(build_mock_output(rp))
    del p["claim_ledger"]
    out = normalize_unify_parsed_without_ledger_synthesis(p, rp)
    assert out is not None
    assert "claim_ledger" not in out


def test_section_lane_main_calls_canonical_primitives(monkeypatch):
    called: list[str] = []

    def fake_primitives(*, section: str = "", **_kwargs):  # type: ignore[no-untyped-def]
        called.append(str(section))
        return {
            "exit_status": "success",
            "execution_status": "completed",
            "outcome_authorized": False,
            "x3_disposition": "X3_REVIEW_MOCKED_PLUMBING_ONLY",
            "fault": "",
            "artifact_dir": "",
            "run_id": "stub",
            "request_id": "",
            "l7_how_trace_emitted": False,
            "terminal_r5": False,
            "executive_summary_cli_output_text": "",
            "unify_bullets_cli_output_text": "",
        }

    monkeypatch.setattr(
        "apps_rg.runtime.orchestration.canonical_dispatch.run_canonical_apps_rg_from_cli_primitives",
        fake_primitives,
    )
    from apps_rg.__main__ import main

    main(
        [
            "--section",
            "unify_bullets",
            "--target-company",
            "Synthetic Enterprise Corp.",
            "--target-role",
            "SVP Engineering, Agentic AI Platforms",
            "--provider",
            "mock",
            "--allow-non-allow-exit-zero",
        ]
    )
    assert called == ["unify_bullets"]

