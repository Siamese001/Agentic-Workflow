from __future__ import annotations

import json
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

from tests._apps_contract.lane_cli_common import (
    REPO_ROOT,
    artifact_dir_from_stdout,
    contract_artifact_dir,
    contract_live_pytestmark,
    run_lane_cli,
)

pytestmark = contract_live_pytestmark("ibm_bullets_runtime_slice")

_IBM_COMPANY = "Synthetic Enterprise Corp."
_IBM_ROLE = "SVP Engineering, Agentic AI Platforms"


def _run_contract(*extra: str) -> Path:
    art = contract_artifact_dir("ibm_bullets", run_key=f"ibm_slice_{uuid.uuid4().hex[:10]}")
    rel = art.relative_to(REPO_ROOT).as_posix()
    proc = run_lane_cli(
        "ibm_bullets",
        artifact_dir=rel,
        target_company=_IBM_COMPANY,
        target_role=_IBM_ROLE,
        timeout_s=600,
    )
    assert proc.returncode == 0, proc.stderr
    rd = artifact_dir_from_stdout(proc)
    assert rd.is_dir(), rd
    return rd


def load_json_at(rd: Path, name: str):
    return json.loads((rd / name).read_text(encoding="utf-8"))


def test_deprecated_dispatch_module_not_a_cli():
    """``python -m apps_rg.runtime.sections.ibm_bullets_lane`` is not an entrypoint."""
    r = subprocess.run(
        [sys.executable, "-m", "apps_rg.runtime.sections.ibm_bullets_lane"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 1, r.stderr
    blob = (r.stderr + r.stdout).lower()
    assert "not an operator cli entrypoint" in blob
    assert "python -m apps_rg" in blob


def test_live_cli_dispatch_executes():
    art = contract_artifact_dir("ibm_bullets")
    rel = art.relative_to(REPO_ROOT).as_posix()
    proc = run_lane_cli(
        "ibm_bullets",
        artifact_dir=rel,
        target_company=_IBM_COMPANY,
        target_role=_IBM_ROLE,
        timeout_s=600,
    )
    assert proc.returncode == 0, proc.stderr
    assert "IBM_BULLETS_OUTPUT:" in proc.stdout


def test_live_outputs_five_bullets():
    rd = _run_contract()
    l2 = load_json_at(rd, "l2_output.json")
    assert len(l2["bullets"]) == 5
    ids = [b["bullet_id"] for b in l2["bullets"]]
    assert ids == [
        "bul_ibm_001",
        "bul_ibm_002",
        "bul_ibm_003",
        "bul_ibm_004",
        "bul_ibm_005",
    ]


def test_l2_output_has_no_rewrite_intensity_model():
    rd = _run_contract()
    l2 = load_json_at(rd, "l2_output.json")
    assert "rewrite_intensity" not in json.dumps(l2).lower()


def test_ibm_overlay_files_exist():
    expected = [
        "apps_rg/runtime/sections/ibm_bullets_lane.py",
        "apps_rg/runtime/validators/ibm_bullets_x2.py",
        "apps_rg/runtime/judges/ibm_bullets_x1d.py",
        "apps_rg/runtime/exit/ibm_bullets_x3.py",
        "apps_rg/runtime/shadow/ibm_bullets_l6.py",
    ]
    for rel in expected:
        assert (REPO_ROOT / rel).is_file(), rel


def test_no_agentic_core_in_overlay_files():
    overlay = [
        REPO_ROOT / "apps_rg/runtime/sections/ibm_bullets_lane.py",
        REPO_ROOT / "apps_rg/runtime/validators/ibm_bullets_x2.py",
        REPO_ROOT / "apps_rg/runtime/judges/ibm_bullets_x1d.py",
        REPO_ROOT / "apps_rg/runtime/exit/ibm_bullets_x3.py",
        REPO_ROOT / "apps_rg/runtime/shadow/ibm_bullets_l6.py",
    ]
    for path in overlay:
        text = path.read_text(encoding="utf-8")
        assert "agentic_core" not in text, path


def test_core_metrics_in_live_output():
    rd = _run_contract()
    l2 = load_json_at(rd, "l2_output.json")
    joined = " ".join(b["bullet_text"] for b in l2["bullets"])
    assert "$15M" in joined or "$15m" in joined.lower()
    assert "99.9%" in joined
    assert "30%" in joined
    assert "25%" in joined
    assert "50%" in joined


def test_canonicalize_bul_ibm_double_underscore_source_fact_id():
    from apps_rg.runtime.sections.ibm_bullets_lane import _canonicalize_bul_ibm_source_fact_id

    assert _canonicalize_bul_ibm_source_fact_id("bul_ibm__002") == "bul_ibm_002"
    assert _canonicalize_bul_ibm_source_fact_id("bul_ibm____003") == "bul_ibm_003"


def test_lane_proof_bundle_mock_judge_hatch_unit():
    from types import SimpleNamespace

    from apps_rg.runtime.qwen_offline_contract_stub import OFFLINE_CONTRACT_STUB_RUNTIME_STATUS
    from apps_rg.runtime.section_proof.mock_runtime_proof_policy import compute_lane_proof_bundle

    class X3Allow:
        x3_code = "X3_ALLOW"
        pass_ = True
        authorization_scope = "PRODUCT_QUALITY"

    judge = {
        "evaluator_mode": "MODEL_BACKED",
        "provider_status": "MODEL_BACKED_PASS",
        "pass": True,
        "decisive_failure": False,
        "normalized_score": 0.9,
        "normalized_threshold": 0.5,
        "provider_key": "openai_chatgpt",
    }
    x2 = [{"gate_id": "g1", "pass": True}]
    args = SimpleNamespace(
        mock_judges=False,
        allow_test_mock_judges=True,
        allow_non_allow_exit_zero=False,
        provider="qwen_vllm",
        allow_test_mock_provider=False,
    )
    hatch_bundle = compute_lane_proof_bundle(
        args,
        runtime_generation_status="REAL_LLM",
        x1d_judges=[judge],
        x2_gates=x2,
        x3=X3Allow(),
        offline_contract_stub_used=False,
    )
    assert hatch_bundle["proof_eligible"] is False
    assert hatch_bundle["proof_scope"] == "plumbing_only"

    stub_bundle = compute_lane_proof_bundle(
        args,
        runtime_generation_status=OFFLINE_CONTRACT_STUB_RUNTIME_STATUS,
        x1d_judges=[judge],
        x2_gates=x2,
        x3=X3Allow(),
        offline_contract_stub_used=True,
    )
    assert stub_bundle["provider_proof_eligible"] is False
    assert stub_bundle["runtime_generation_status_class"] == "OFFLINE_CONTRACT_STUB"


def test_ibm_bullet_taxonomy_prefix_detector():
    from apps_rg.runtime.validators.ibm_bullets_x2 import ibm_bullet_text_has_taxonomy_label_prefix

    assert ibm_bullet_text_has_taxonomy_label_prefix(
        "AI and Data Platform Architecture: Architected cloud-native AI."
    )
    assert ibm_bullet_text_has_taxonomy_label_prefix("Cloud Modernization: Led migration from legacy.")
    assert not ibm_bullet_text_has_taxonomy_label_prefix(
        "Architected cloud-native AI and analytics platforms supporting regulated enterprise decision systems."
    )


def test_provider_request_dict_redacts_bearer_substrings():
    import json

    from apps_rg.runtime.providers.qwen_vllm_provider import ProviderRequest

    req = ProviderRequest(
        provider_requested="qwen_vllm",
        provider_attempted=True,
        provider_url="http://127.0.0.1:8000/v1/chat?api_key=supersecret",
        model="m",
        temperature=0.4,
        max_tokens=10,
        timeout_seconds=30,
        prompt_hash="p",
        input_payload_hash="i",
        mock_fallback_allowed=False,
    )
    dumped = json.dumps(req.to_dict())
    assert "supersecret" not in dumped
    assert "?" not in dumped
