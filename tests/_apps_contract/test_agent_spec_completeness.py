"""Tests for AgentSpec completeness — W2, apps-core-contract-rectification-a8f3c2.

Verifies:
- All 8 apps have agent_spec_config.py
- Each exports a root *AgentSpecs class
- Root class inherits PromptReceptionSpec fields (adapter_version, exemplar_task_class)
- apps_qna QnaAgentSpecs has pack_builder + route sub-specs
- apps_lic LicAgentSpecs has hop_topology with all 9 stage fields
- CI gate script exits 0 with no errors
"""

from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

ALL_APPS = [
    "apps_qna",
    "apps_rg",
    "apps_lic",
    "apps_research",
    "apps_rfp",
    "apps_exec",
    "apps_eval",
    "apps_underwriting_ai",
]

ROOT_CLASS_NAMES = {
    "apps_qna": "QnaAgentSpecs",
    "apps_rg": "RGAgentSpecs",
    "apps_lic": "LicAgentSpecs",
    "apps_research": "ResearchAgentSpecs",
    "apps_rfp": "RfpAgentSpecs",
    "apps_exec": "ExecAgentSpecs",
    "apps_eval": "EvalAgentSpecs",
    "apps_underwriting_ai": "UnderwritingAgentSpecs",
}


@pytest.mark.parametrize("app_id", ALL_APPS)
def test_agent_spec_config_file_exists(app_id: str) -> None:
    path = REPO_ROOT / app_id / "config" / "agent_spec_config.py"
    assert path.is_file(), f"agent_spec_config.py missing for {app_id}"


@pytest.mark.parametrize("app_id", ALL_APPS)
def test_agent_spec_config_importable(app_id: str) -> None:
    mod = importlib.import_module(f"{app_id}.config.agent_spec_config")
    assert mod is not None


def _find_root_cls(mod: object) -> type | None:
    """Prefer *AgentSpecs (plural), fall back to *AgentSpec with PromptReceptionSpec."""
    for name in dir(mod):
        obj = getattr(mod, name, None)
        if obj and isinstance(obj, type) and name.endswith("AgentSpecs"):
            return obj
    for name in dir(mod):
        obj = getattr(mod, name, None)
        if obj and isinstance(obj, type) and name.endswith("AgentSpec"):
            bases = [b.__name__ for b in getattr(obj, "__mro__", ())]
            if "PromptReceptionSpec" in bases:
                return obj
    return None


@pytest.mark.parametrize("app_id", ALL_APPS)
def test_agent_spec_has_root_class(app_id: str) -> None:
    mod = importlib.import_module(f"{app_id}.config.agent_spec_config")
    root_cls = _find_root_cls(mod)
    assert root_cls is not None, f"{app_id}: no root *AgentSpecs class found in agent_spec_config"


@pytest.mark.parametrize("app_id", ALL_APPS)
def test_agent_spec_has_prompt_reception_fields(app_id: str) -> None:
    mod = importlib.import_module(f"{app_id}.config.agent_spec_config")
    root_cls = _find_root_cls(mod)
    assert root_cls is not None, f"{app_id}: no root class"

    if hasattr(root_cls, "model_fields"):
        fields = set(root_cls.model_fields.keys())
    else:
        fields = set(getattr(root_cls, "__fields__", {}).keys())

    assert "adapter_version" in fields, (
        f"{app_id}.{root_cls.__name__} missing adapter_version (PromptReceptionSpec)"
    )
    assert "exemplar_task_class" in fields, (
        f"{app_id}.{root_cls.__name__} missing exemplar_task_class (PromptReceptionSpec)"
    )


def test_qna_agent_specs_has_pack_builder_and_route() -> None:
    from apps_qna.config.agent_spec_config import QnaAgentSpecs

    if hasattr(QnaAgentSpecs, "model_fields"):
        fields = set(QnaAgentSpecs.model_fields.keys())
    else:
        fields = set(QnaAgentSpecs.__fields__.keys())

    assert "pack_builder" in fields, "QnaAgentSpecs missing pack_builder field"
    assert "route" in fields, "QnaAgentSpecs missing route field"


def test_qna_agent_specs_defaults() -> None:
    from apps_qna.config.agent_spec_config import QnaAgentSpecs

    spec = QnaAgentSpecs()
    assert spec.adapter_version == "v2"
    assert spec.exemplar_task_class is None
    assert spec.pack_builder.template_set == "v1"
    assert spec.route.primary_task_class == "qna_pack_build"


def test_lic_agent_specs_has_hop_topology() -> None:
    from apps_lic.config.agent_spec_config import LicAgentSpecs

    if hasattr(LicAgentSpecs, "model_fields"):
        fields = set(LicAgentSpecs.model_fields.keys())
    else:
        fields = set(LicAgentSpecs.__fields__.keys())

    assert "hop_topology" in fields, "LicAgentSpecs missing hop_topology field"


def test_lic_hop_topology_has_all_9_stages() -> None:
    from apps_lic.config.agent_spec_config import LicAgentSpecs, LicHopTopologySpec

    expected_stages = {
        "profile_analysis",
        "research",
        "sender_grounding",
        "routing",
        "generation",
        "validation",
        "gate_decision",
        "qa_report",
        "integration",
    }
    if hasattr(LicHopTopologySpec, "model_fields"):
        actual = set(LicHopTopologySpec.model_fields.keys())
    else:
        actual = set(LicHopTopologySpec.__fields__.keys())

    assert expected_stages == actual, (
        f"LicHopTopologySpec stage mismatch. Missing: {expected_stages - actual}. "
        f"Extra: {actual - expected_stages}"
    )


def test_lic_agent_specs_defaults() -> None:
    from apps_lic.config.agent_spec_config import LicAgentSpecs

    spec = LicAgentSpecs()
    assert spec.adapter_version == "v2"
    assert spec.version == "1.0.0"
    assert spec.hop_topology.generation.timeout_sec == 60
    assert spec.hop_topology.generation.retry_on_low_score is True
    assert spec.hop_topology.gate_decision.timeout_sec == 15
    assert spec.hop_topology.profile_analysis.criticality == "required"


def test_ci_gate_exits_zero() -> None:
    gate_path = REPO_ROOT / "ops_scripts" / "ci" / "check_agent_spec_completeness.py"
    assert gate_path.is_file(), "check_agent_spec_completeness.py not found"
    result = subprocess.run(
        [sys.executable, str(gate_path)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        timeout=30,
    )
    assert result.returncode == 0, (
        f"check_agent_spec_completeness.py exited {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "RESULT: PASS" in result.stdout
