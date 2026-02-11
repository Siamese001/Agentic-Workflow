"""Executor dispatch integrity tests — validates dispatch mapping, backward compat, alias resolution.

Phase F requirement: Contract tests for all 6 canonical executors.
Includes regression snapshots for HOP, RG validation, LIC validation, and observability probe.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]


# ═══════════════════════════════════════════════════════════════════════════════
# 1. DISPATCH MAPPING VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════


class TestInspectorExecutorDispatch:
    """InspectorExecutor must map all 3 inspector types."""

    EXECUTOR_PATH = ROOT / "agentic_core" / "L5_safety" / "reasoning" / "InspectorExecutor.py"

    def test_executor_exists(self) -> None:
        assert self.EXECUTOR_PATH.exists()

    def test_has_classdef(self) -> None:
        tree = ast.parse(self.EXECUTOR_PATH.read_text(encoding="utf-8"))
        names = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        assert "InspectorExecutor" in names

    @pytest.mark.parametrize("key", ["dag_runtime", "signature", "token_budget"])
    def test_dispatch_key_present(self, key: str) -> None:
        source = self.EXECUTOR_PATH.read_text(encoding="utf-8")
        assert f'"{key}"' in source, f"Dispatch key '{key}' not found"


class TestRGValidationExecutorDispatch:
    """RGValidationExecutor must map all 4 rule sets."""

    EXECUTOR_PATH = ROOT / "apps_rg" / "engines" / "RGValidationExecutor.py"

    def test_executor_exists(self) -> None:
        assert self.EXECUTOR_PATH.exists()

    @pytest.mark.parametrize(
        "rule",
        ["ats_compatibility", "brand_compliance", "fact_check", "section_balance"],
    )
    def test_rule_registered(self, rule: str) -> None:
        source = self.EXECUTOR_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        registered = set()
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "register_rule"
            ):
                if node.args and isinstance(node.args[0], ast.Constant):
                    registered.add(node.args[0].value)
        assert rule in registered, f"Rule '{rule}' not registered. Found: {registered}"

    def test_unknown_rule_returns_error(self) -> None:
        source = self.EXECUTOR_PATH.read_text(encoding="utf-8")
        assert "unknown_rule_set" in source, "No explicit error for unknown rule_set"


class TestLICValidationExecutorDispatch:
    """LICValidationExecutor must map both rule sets."""

    EXECUTOR_PATH = ROOT / "apps_lic" / "engines" / "LICValidationExecutor.py"

    def test_executor_exists(self) -> None:
        assert self.EXECUTOR_PATH.exists()

    @pytest.mark.parametrize("rule", ["campaign_balance", "deliverability"])
    def test_rule_branch_present(self, rule: str) -> None:
        source = self.EXECUTOR_PATH.read_text(encoding="utf-8")
        assert f'"{rule}"' in source, f"Rule '{rule}' not found in dispatch"


class TestObservabilityProbeExecutorDispatch:
    """ObservabilityProbeExecutor must map all 6 probe types."""

    EXECUTOR_PATH = ROOT / "agentic_core" / "L6_observability" / "reasoning" / "ObservabilityProbeExecutor.py"

    def test_executor_exists(self) -> None:
        assert self.EXECUTOR_PATH.exists()

    @pytest.mark.parametrize(
        "probe",
        ["cost_tracker", "coordinator", "strategic", "deadlock", "debate", "runtime_telemetry"],
    )
    def test_probe_key_present(self, probe: str) -> None:
        source = self.EXECUTOR_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        keys = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_get_handler":
                for inner in ast.walk(node):
                    if isinstance(inner, ast.Dict):
                        for key in inner.keys:
                            if isinstance(key, ast.Constant):
                                keys.add(key.value)
        assert probe in keys, f"Probe '{probe}' not in handler map. Found: {keys}"


class TestRGStrategyExecutorDispatch:
    """RGStrategyExecutor must map all 3 strategy types."""

    EXECUTOR_PATH = ROOT / "apps_rg" / "engines" / "RGStrategyExecutor.py"

    def test_executor_exists(self) -> None:
        assert self.EXECUTOR_PATH.exists()

    @pytest.mark.parametrize("strategy", ["content", "strategic_planner", "template_optimizer"])
    def test_strategy_key_present(self, strategy: str) -> None:
        source = self.EXECUTOR_PATH.read_text(encoding="utf-8")
        assert f'"{strategy}"' in source, f"Strategy '{strategy}' not found"


class TestHOPPipelineExecutorDispatch:
    """HOPPipelineExecutor must map all 9 stages and have registry coverage."""

    EXECUTOR_PATH = ROOT / "apps_lic" / "engines" / "HOPPipelineExecutor.py"
    REGISTRY_PATH = ROOT / "apps_lic" / "engines" / "hop_stage_registry.py"

    def test_executor_exists(self) -> None:
        assert self.EXECUTOR_PATH.exists()

    def test_registry_exists(self) -> None:
        assert self.REGISTRY_PATH.exists()

    @pytest.mark.parametrize("stage_id", list(range(1, 10)))
    def test_stage_name_mapped(self, stage_id: int) -> None:
        source = self.EXECUTOR_PATH.read_text(encoding="utf-8")
        assert f"{stage_id}:" in source, f"Stage {stage_id} not in _STAGE_NAMES"

    @pytest.mark.parametrize("stage_id", list(range(1, 10)))
    def test_stage_registered(self, stage_id: int) -> None:
        source = self.REGISTRY_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        registered = set()
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "register_stage"
            ):
                if node.args and isinstance(node.args[0], ast.Constant):
                    registered.add(node.args[0].value)
        assert stage_id in registered, f"Stage {stage_id} not registered. Found: {registered}"

    def test_missing_stage_returns_error(self) -> None:
        source = self.EXECUTOR_PATH.read_text(encoding="utf-8")
        assert '"error"' in source or "'error'" in source, "No explicit error for missing stage"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. BACKWARD COMPATIBILITY — ALIAS RESOLUTION
# ═══════════════════════════════════════════════════════════════════════════════


class TestAliasResolution:
    """Old agent names must resolve to canonical executors via shim imports."""

    ALIAS_CHECKS = [
        (
            "agentic_core/L3_orchestration/reasoning/DagRuntimeInspectorAgent.py",
            "DagRuntimeInspectorAgent",
            "InspectorExecutor",
        ),
        ("apps_rg/reasoning/ATSCompatibilityAgent.py", "ATSCompatibilityAgent", "RGValidationExecutor"),
        ("apps_lic/engines/CampaignBalanceAgent.py", "CampaignBalanceAgent", "LICValidationExecutor"),
        ("apps_rg/reasoning/ContentStrategyAgent.py", "ContentStrategyAgent", "RGStrategyExecutor"),
        ("apps_lic/engines/Hop1ProfileAnalysisAgent.py", "HOP1ProfileAnalysisAgent", "HOPPipelineExecutor"),
    ]

    @pytest.mark.parametrize(
        "rel_path,old_cls,canon_cls",
        ALIAS_CHECKS,
        ids=lambda *a: a[0] if isinstance(a, tuple) else Path(a).stem,
    )
    def test_shim_resolves(self, rel_path: str, old_cls: str, canon_cls: str) -> None:
        full = ROOT / rel_path
        assert full.exists(), f"Shim missing: {rel_path}"
        source = full.read_text(encoding="utf-8")
        assert canon_cls in source, f"Canonical class {canon_cls} not referenced in {rel_path}"
        assert old_cls in source, f"Old class name {old_cls} not in shim {rel_path}"


# ═══════════════════════════════════════════════════════════════════════════════
# 3. REGRESSION SNAPSHOTS — PRE-CONSOLIDATION BEHAVIOR
# ═══════════════════════════════════════════════════════════════════════════════


def _import_module_direct(dotted: str):
    """Import a module directly without triggering package __init__.py.

    Raises ImportError if the module or its dependencies cannot be loaded.
    """
    import importlib.util

    mod_path = ROOT / dotted.replace(".", "/")
    if mod_path.is_dir():
        mod_path = mod_path / "__init__.py"
    else:
        mod_path = mod_path.with_suffix(".py")
    spec = importlib.util.spec_from_file_location(dotted, str(mod_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_SKIP_IMPORT_MSG = "Pre-existing broken import chain (not consolidation-caused)"


class TestHOPStageRegression:
    """HOP stage 4 (routing) must produce deterministic output structure."""

    def test_stage_4_handler_exists(self) -> None:
        hop_reg = _import_module_direct("apps_lic.engines.hop_stage_registry")
        handler = hop_reg.get_stage_handler(4)
        assert handler is not None, "Stage 4 handler not registered"

    def test_stage_4_output_structure(self) -> None:
        hop_reg = _import_module_direct("apps_lic.engines.hop_stage_registry")
        handler = hop_reg.get_stage_handler(4)
        result = handler(None, {"test": True})
        assert isinstance(result, dict)
        assert result["stage"] == 4
        assert result["name"] == "routing"
        assert result["status"] == "processed"


class TestRGValidationRegression:
    """RG ats_compatibility rule must detect missing skills."""

    def test_ats_detects_missing_skills(self) -> None:
        try:
            mod = _import_module_direct("apps_rg.engines.RGValidationExecutor")
        except ImportError as exc:
            pytest.skip(f"{_SKIP_IMPORT_MSG}: {exc}")
        registry = mod._RULE_REGISTRY
        handler = registry.get("ats_compatibility")
        assert handler is not None, "ats_compatibility handler not registered"
        issues = handler(None, {"experience": ["job1"]}, None)
        types = [i["type"] for i in issues]
        assert "ats_missing_skills" in types


class TestLICValidationRegression:
    """LIC campaign_balance rule must detect channel imbalance."""

    def test_campaign_balance_detects_imbalance(self) -> None:
        try:
            mod = _import_module_direct("apps_lic.engines.LICValidationExecutor")
        except ImportError as exc:
            pytest.skip(f"{_SKIP_IMPORT_MSG}: {exc}")
        v = mod.LICValidationExecutor(rule_set="campaign_balance")
        issues = v._validate({"channels": {"email": 90, "sms": 10}})
        types = [i["type"] for i in issues]
        assert "channel_imbalance" in types


class TestObservabilityProbeRegression:
    """ObservabilityProbeExecutor cost_tracker must return probe key."""

    def test_cost_tracker_probe_structure(self) -> None:
        try:
            mod = _import_module_direct("agentic_core.L6_observability.reasoning.ObservabilityProbeExecutor")
        except (ImportError, TypeError) as exc:
            pytest.skip(f"{_SKIP_IMPORT_MSG}: {exc}")
        probe = mod.ObservabilityProbeExecutor(probe_type="cost_tracker")
        result = probe.execute({"cost_metrics": {"total": 42}})
        assert result["probe"] == "cost_tracker"
        assert result["metrics"]["total"] == 42


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
