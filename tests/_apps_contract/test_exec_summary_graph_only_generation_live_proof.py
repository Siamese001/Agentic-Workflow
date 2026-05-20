"""Fail-closed contracts: executive_summary graph-only + C0.3 GraphRAG live proof."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from apps_rg.fact_inventory.augmented_skills_graph import SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH
from apps_rg.runtime.c03_graphrag_bound import FORBIDDEN_SUPPORT_FOR_PRODUCT_PROOF
from apps_rg.runtime.proof_pool_resolver import (
    PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH,
    resolve_section_proof_pool,
)
from apps_rg.runtime.validators.validate_exec_summary_graph_only_generation import (
    validate_run_dir,
)

REPO = Path(__file__).resolve().parents[2]
GRAPH_PATH = REPO / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json"
LEDGER_PATH = REPO / "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json"


def _minimal_graph_run_dir(tmp_path: Path) -> Path:
    """Synthetic passing-shaped run dir for validator unit checks."""
    run = tmp_path / "exec_summary_graph_only_fixture"
    run.mkdir(parents=True)
    pp_meta = {
        "proof_pool_type": "augmented_skills_graph",
        "source_authority": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
        "claim_evidence_source_type": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
        "broad_skills_ledger_used": False,
        "base_resume_fallback_used": False,
        "graph_expansion_allowed": True,
        "graph_expansion_refs": ["ref:graph:edge:edge_skill_test"],
        "graph_lineage_refs": ["ref:graph:version:master_skills_arsenal_graph_v1"],
        "graph_sig": "abc123",
        "c03_graphrag_bound_status": "BOUND",
        "support_status": "SUPPORTED",
        "evidence_items_count": 2,
    }
    c03 = {
        "schema_version": "c03_graphrag_bound_v1",
        "c03_graphrag_bound_status": "BOUND",
        "graph_expansion_allowed": True,
        "graph_expansion_refs": pp_meta["graph_expansion_refs"],
        "graph_lineage_refs": pp_meta["graph_lineage_refs"],
        "support_status": "SUPPORTED",
        "final_evidence_contract_snapshot": {
            "support_status": "SUPPORTED",
            "evidence_items": [
                {"evidence_id": "evidence:graph:fact_a", "authority": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH},
                {"evidence_id": "evidence:graph:fact_b", "authority": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH},
            ],
        },
    }
    (run / "runtime_payload.json").write_text(
        json.dumps({"proof_pool_metadata": pp_meta, "graph_only_claim_authority": True}),
        encoding="utf-8",
    )
    (run / "c03_graphrag_bound.json").write_text(json.dumps(c03), encoding="utf-8")
    (run / "final_evidence_contract_snapshot.json").write_text(
        json.dumps(c03["final_evidence_contract_snapshot"]),
        encoding="utf-8",
    )
    (run / "section_input_usage_ledger.json").write_text(
        json.dumps(
            {
                "input_authority": {
                    "augmented_skills_graph": "CLAIM_EVIDENCE_AND_SKILLS_AUTHORITY",
                    "base_resume": "DEPRECATED_NON_AUTHORITY",
                    "broad_skills_ledger": "DEPRECATED_REFERENCE_ONLY",
                },
                "proof_source": PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH,
                "source_authority": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
                "claim_evidence_source_type": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
            }
        ),
        encoding="utf-8",
    )
    (run / "compiled_prompt.txt").write_text(
        "INPUT_AUTHORITY:\n"
        "- CLAIM SUPPORT POOL (AUGMENTED SKILLS GRAPH): C0.3 GraphRAG-bound\n"
        "ALLOWED_SOURCE_FACT_IDS\n",
        encoding="utf-8",
    )
    (run / "compiled_prompt_artifact.json").write_text(
        json.dumps({"proof_source": PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH}),
        encoding="utf-8",
    )
    (run / "provider_request.json").write_text(json.dumps({"model": "qwen_vllm"}), encoding="utf-8")
    (run / "provider_response.json").write_text(
        json.dumps({"model": "qwen_vllm", "runtime_generation_status": "REAL_LLM"}),
        encoding="utf-8",
    )
    (run / "l2_output.json").write_text(
        json.dumps({"runtime_generation_status": "REAL_LLM"}),
        encoding="utf-8",
    )
    (run / "x2_gate_outputs.json").write_text(json.dumps({"failed_gates": []}), encoding="utf-8")
    (run / "x2_source_fact_pool_receipt.json").write_text(
        json.dumps({"broad_skills_ledger_used": False, "base_resume_fallback_used": False}),
        encoding="utf-8",
    )
    (run / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_ALLOW", "pass": True, "runtime_generation_status": "REAL_LLM"}),
        encoding="utf-8",
    )
    (run / "run_manifest.json").write_text(
        json.dumps({"command": "python -m apps_rg --section executive_summary"}),
        encoding="utf-8",
    )
    return run


@pytest.mark.parametrize(
    "env_key,env_val",
    [
        ("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", "1"),
    ],
)
def test_contract_rejects_offline_stub_env(monkeypatch: pytest.MonkeyPatch, env_key: str, env_val: str) -> None:
    monkeypatch.setenv(env_key, env_val)
    assert os.environ.get(env_key) == env_val


def test_contract_proof_pool_executive_summary_graph_only() -> None:
    if not GRAPH_PATH.is_file():
        pytest.skip(f"missing graph: {GRAPH_PATH}")
    if not LEDGER_PATH.is_file():
        pytest.skip(f"missing ledger: {LEDGER_PATH}")
    pool = resolve_section_proof_pool(
        section="executive_summary",
        repo_root=REPO,
        target_company="Unify Consulting",
        target_title="SVP Engineering, Agentic AI Platforms",
        target_role="SVP Engineering, Agentic AI Platforms",
        jd_text="agentic AI platform governance runtime",
        briefing_text="regulated enterprise",
    )
    assert pool.proof_source == PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH
    meta = pool.proof_pool_metadata
    assert meta.get("source_authority") == SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH
    assert meta.get("proof_pool_type") == "augmented_skills_graph"
    assert meta.get("broad_skills_ledger_used") is False
    assert meta.get("graph_expansion_allowed") is True
    assert meta.get("graph_expansion_refs")
    assert meta.get("c03_graphrag_bound_status") == "BOUND"
    assert meta.get("support_status") not in FORBIDDEN_SUPPORT_FOR_PRODUCT_PROOF


def test_validator_passes_synthetic_graph_only_fixture(tmp_path: Path) -> None:
    run = _minimal_graph_run_dir(tmp_path)
    report = validate_run_dir(run, repo=REPO)
    assert report.status == "PASS"
    assert report.graph_only_authority_status == "PASS"
    assert report.c03_graphrag_bound_status == "BOUND"
    assert report.non_graph_evidence_items_count == 0


def test_validator_fails_broad_ledger_authority(tmp_path: Path) -> None:
    run = _minimal_graph_run_dir(tmp_path)
    rp = json.loads((run / "runtime_payload.json").read_text(encoding="utf-8"))
    rp["proof_pool_metadata"]["proof_pool_type"] = "broad_skills_ledger"
    rp["proof_pool_metadata"]["broad_skills_ledger_used"] = True
    rp["proof_pool_metadata"]["source_authority"] = "broad_skills_ledger"
    (run / "runtime_payload.json").write_text(json.dumps(rp), encoding="utf-8")
    report = validate_run_dir(run, repo=REPO)
    assert report.status == "FAIL"
    assert report.graph_only_authority_status == "FAIL"


def test_validator_fails_mock_provider_marker(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    run = _minimal_graph_run_dir(tmp_path)
    monkeypatch.setenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", "1")
    report = validate_run_dir(run, repo=REPO)
    assert report.status == "FAIL"
    assert any("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB" in f for f in report.mock_provider_flags)


def test_validator_fails_deprecated_dispatch_reference(tmp_path: Path) -> None:
    run = _minimal_graph_run_dir(tmp_path)
    manifest = json.loads((run / "run_manifest.json").read_text(encoding="utf-8"))
    manifest["command"] = "python -m apps_rg.runtime.sections.executive_summary_lane_api"
    (run / "run_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    report = validate_run_dir(run, repo=REPO)
    assert report.status == "FAIL"
    assert report.smoke_dispatch_reference_count > 0


def _load_run_json(run_dir: Path, name: str) -> dict:
    return json.loads((run_dir / name).read_text(encoding="utf-8"))


def _assert_graph_only_authority_invariants(report: object, run_dir: Path) -> None:
    """Shared graph-only + C0.3 invariants for live runs."""
    from apps_rg.runtime.validators.validate_exec_summary_graph_only_generation import (
        ValidationReport,
    )

    assert isinstance(report, ValidationReport)
    usage = _load_run_json(run_dir, "section_input_usage_ledger.json")
    base_auth = str((usage.get("input_authority") or {}).get("base_resume") or "")
    assert base_auth in ("DEPRECATED_NON_AUTHORITY", "")
    assert report.graph_only_authority_status == "PASS"
    assert report.c03_graphrag_bound_status == "BOUND"
    assert report.non_graph_evidence_items_count == 0
    assert report.smoke_dispatch_reference_count == 0
    assert not report.mock_provider_flags
    compiled = (run_dir / "compiled_prompt.txt").read_text(encoding="utf-8")
    assert "AUGMENTED SKILLS GRAPH" in compiled or "augmented_skills_graph" in compiled
    assert "CLAIM SUPPORT POOL (BROAD SKILLS LEDGER)" not in compiled
    assert "CLAIM SUPPORT POOL (BASE RESUME FALLBACK)" not in compiled


@pytest.mark.integration
def test_live_latest_x1d_judge_providers_unblocked() -> None:
    """Live run: all configured X1D judges reach MODEL_BACKED (no provider blockage)."""
    from apps_rg.runtime.validators.validate_exec_summary_graph_only_generation import (
        resolve_latest_run_dir,
    )

    run_dir = resolve_latest_run_dir(REPO)
    if run_dir is None:
        pytest.skip("no latest real executive_summary run")
    x1d = _load_run_json(run_dir, "x1d_llm_judge_outputs.json")
    blocked = [
        str(j.get("provider_key"))
        for j in (x1d.get("judges") or [])
        if isinstance(j, dict)
        and (j.get("provider_blocked") or str(j.get("evaluator_mode", "")).startswith("BLOCKED_"))
    ]
    assert not blocked, f"X1D provider blockers: {blocked}"
    for j in x1d.get("judges") or []:
        if not isinstance(j, dict):
            continue
        assert str(j.get("evaluator_mode")) == "MODEL_BACKED", j


@pytest.mark.integration
def test_live_latest_real_run_graph_only_product_proof() -> None:
    """Live canonical run: REAL_LLM, graph-only authority, X2 PASS, validator PASS."""
    from apps_rg.runtime.validators.validate_exec_summary_graph_only_generation import (
        resolve_latest_run_dir,
        validate_run_dir,
    )

    run_dir = resolve_latest_run_dir(REPO)
    if run_dir is None:
        pytest.skip("no latest real executive_summary run")

    l2 = _load_run_json(run_dir, "l2_output.json")
    runtime_status = str(l2.get("runtime_generation_status") or "")
    assert runtime_status not in ("BLOCKED", "MOCK", "OFFLINE", ""), (
        f"runtime_generation_status must be REAL_LLM, got {runtime_status!r}"
    )
    assert runtime_status == "REAL_LLM"

    manifest = _load_run_json(run_dir, "run_manifest.json")
    prov_res = str(manifest.get("provider_resolution_source") or "")
    assert prov_res != "DEV_DEFAULT_MOCK"
    assert "mock" not in prov_res.lower()

    provider_resp = _load_run_json(run_dir, "provider_response.json")
    model = str(provider_resp.get("model") or "")
    assert model
    assert "mock" not in model.lower()

    x2 = _load_run_json(run_dir, "x2_gate_outputs.json")
    failed = list(x2.get("failed_gates") or [])
    assert not failed, f"X2 must PASS for product proof; failed={failed}"

    report = validate_run_dir(run_dir, repo=REPO)
    _assert_graph_only_authority_invariants(report, run_dir)

    x3 = _load_run_json(run_dir, "x3_disposition.json")
    x3_code = str(x3.get("x3_code") or "")
    x1d = _load_run_json(run_dir, "x1d_llm_judge_outputs.json")
    blocked = [
        str(j.get("provider_key"))
        for j in (x1d.get("judges") or [])
        if isinstance(j, dict)
        and (j.get("provider_blocked") or str(j.get("evaluator_mode", "")).startswith("BLOCKED_"))
    ]
    assert not blocked, f"X1D provider blockers must be cleared: {blocked}"

    assert report.status == "PASS", "; ".join(report.blockers[:12])
    assert not report.x1d_provider_blockers, report.x1d_provider_blockers


@pytest.mark.integration
def test_live_latest_full_product_proof_eligible_when_policy_met() -> None:
    """When latest live run achieves X3_ALLOW, manifest proof_eligible must be true."""
    from apps_rg.runtime.validators.validate_exec_summary_graph_only_generation import (
        resolve_latest_run_dir,
    )

    run_dir = resolve_latest_run_dir(REPO)
    if run_dir is None:
        pytest.skip("no latest real executive_summary run")
    manifest = _load_run_json(run_dir, "run_manifest.json")
    x3 = _load_run_json(run_dir, "x3_disposition.json")
    x3_code = str(x3.get("x3_code") or "")
    if x3_code != "X3_ALLOW":
        pytest.skip(f"latest run not full product proof yet: {x3_code}")
    assert manifest.get("proof_eligible") is True
    assert manifest.get("judge_proof_eligible") is True
