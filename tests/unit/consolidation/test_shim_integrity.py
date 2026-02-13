"""Shim integrity tests — ensures no consolidation shim contains ClassDef or residual logic.

Phase F requirement: Verify all merge shims and retirement shims maintain structural invariants.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
TARGETS = json.loads((ROOT / "artifacts" / "consolidation" / "target_paths.json").read_text())

# Merge shim → (old_class, canonical_class, canonical_module)
MERGE_SHIM_MAP: dict[str, tuple[str, str, str]] = {
    "agentic_core/L3_orchestration/reasoning/DagRuntimeInspectorAgent.py": (
        "DagRuntimeInspectorAgent",
        "InspectorExecutor",
        "agentic_core.L5_safety.reasoning.InspectorExecutor",
    ),
    "agentic_core/L5_safety/reasoning/SignatureVerifierAgent.py": (
        "SignatureVerifierAgent",
        "InspectorExecutor",
        "agentic_core.L5_safety.reasoning.InspectorExecutor",
    ),
    "agentic_core/L5_safety/reasoning/TokenBudgetInspectorAgent.py": (
        "TokenBudgetInspectorAgent",
        "InspectorExecutor",
        "agentic_core.L5_safety.reasoning.InspectorExecutor",
    ),
    "apps_lic/engines/CampaignBalanceAgent.py": (
        "CampaignBalanceAgent",
        "LICValidationExecutor",
        "apps_lic.engines.LICValidationExecutor",
    ),
    "apps_lic/engines/DeliverabilityAgent.py": (
        "DeliverabilityAgent",
        "LICValidationExecutor",
        "apps_lic.engines.LICValidationExecutor",
    ),
    "apps_lic/engines/Hop1ProfileAnalysisAgent.py": (
        "HOP1ProfileAnalysisAgent",
        "HOPPipelineExecutor",
        "apps_lic.engines.HOPPipelineExecutor",
    ),
    "apps_lic/engines/Hop2ResearchAgent.py": (
        "HOP2ResearchAgent",
        "HOPPipelineExecutor",
        "apps_lic.engines.HOPPipelineExecutor",
    ),
    "apps_lic/engines/HOP3SenderGroundingAgent.py": (
        "HOP3SenderGroundingAgent",
        "HOPPipelineExecutor",
        "apps_lic.engines.HOPPipelineExecutor",
    ),
    "apps_lic/engines/Hop4RoutingAgent.py": (
        "HOP4RoutingAgent",
        "HOPPipelineExecutor",
        "apps_lic.engines.HOPPipelineExecutor",
    ),
    "apps_lic/engines/HOP5GenerationAgent.py": (
        "HOP5GenerationAgent",
        "HOPPipelineExecutor",
        "apps_lic.engines.HOPPipelineExecutor",
    ),
    "apps_lic/engines/Hop6ValidationAgent.py": (
        "HOP6ValidationAgent",
        "HOPPipelineExecutor",
        "apps_lic.engines.HOPPipelineExecutor",
    ),
    "apps_lic/engines/HOP7GateDecisionAgent.py": (
        "HOP7GateDecisionAgent",
        "HOPPipelineExecutor",
        "apps_lic.engines.HOPPipelineExecutor",
    ),
    "apps_lic/engines/HOP8QAReportAgent.py": (
        "HOP8QAReportAgent",
        "HOPPipelineExecutor",
        "apps_lic.engines.HOPPipelineExecutor",
    ),
    "apps_lic/engines/HOP9IntegrationAgent.py": (
        "HOP9IntegrationAgent",
        "HOPPipelineExecutor",
        "apps_lic.engines.HOPPipelineExecutor",
    ),
    "apps_rg/reasoning/ATSCompatibilityAgent.py": (
        "ATSCompatibilityAgent",
        "RGValidationExecutor",
        "apps_rg.engines.RGValidationExecutor",
    ),
    "apps_rg/reasoning/BrandComplianceAgent.py": (
        "BrandComplianceAgent",
        "RGValidationExecutor",
        "apps_rg.engines.RGValidationExecutor",
    ),
    "apps_rg/reasoning/ContentStrategyAgent.py": (
        "ContentStrategyAgent",
        "RGStrategyExecutor",
        "apps_rg.engines.RGStrategyExecutor",
    ),
    "apps_rg/reasoning/FactCheckAgent.py": (
        "FactCheckAgent",
        "RGValidationExecutor",
        "apps_rg.engines.RGValidationExecutor",
    ),
    "apps_rg/reasoning/RgStrategicPlannerAgent.py": (
        "RgStrategicPlannerAgent",
        "RGStrategyExecutor",
        "apps_rg.engines.RGStrategyExecutor",
    ),
    "apps_rg/reasoning/RgTemplateOptimizerAgent.py": (
        "RgTemplateOptimizerAgent",
        "RGStrategyExecutor",
        "apps_rg.engines.RGStrategyExecutor",
    ),
    "apps_rg/reasoning/SectionBalanceAgent.py": (
        "SectionBalanceAgent",
        "RGValidationExecutor",
        "apps_rg.engines.RGValidationExecutor",
    ),
    "agentic_core/L2_execution/reasoning/RgStrategicPlannerAgent.py": (
        "RgStrategicPlannerAgent",
        "RGStrategyExecutor",
        "apps_rg.engines.RGStrategyExecutor",
    ),
}


class TestMergeShimNoClassDef:
    """No merge shim file may contain a ClassDef node."""

    @pytest.mark.parametrize("rel_path", list(MERGE_SHIM_MAP.keys()), ids=lambda p: Path(p).stem)
    def test_no_classdef(self, rel_path: str) -> None:
        full = ROOT / rel_path
        assert full.exists(), f"Shim missing: {rel_path}"
        tree = ast.parse(full.read_text(encoding="utf-8"))
        class_defs = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        assert class_defs == [], f"Shim {rel_path} contains ClassDef: {class_defs}"

    @pytest.mark.parametrize("rel_path", list(MERGE_SHIM_MAP.keys()), ids=lambda p: Path(p).stem)
    def test_under_30_loc(self, rel_path: str) -> None:
        full = ROOT / rel_path
        loc = len([l for l in full.read_text(encoding="utf-8").splitlines() if l.strip()])
        assert loc < 30, f"Shim {rel_path} has {loc} LOC (limit 30)"

    @pytest.mark.parametrize("rel_path", list(MERGE_SHIM_MAP.keys()), ids=lambda p: Path(p).stem)
    def test_no_functions(self, rel_path: str) -> None:
        full = ROOT / rel_path
        tree = ast.parse(full.read_text(encoding="utf-8"))
        funcs = [
            n.name
            for n in ast.iter_child_nodes(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        assert funcs == [], f"Shim {rel_path} contains functions: {funcs}"

    @pytest.mark.parametrize("rel_path", list(MERGE_SHIM_MAP.keys()), ids=lambda p: Path(p).stem)
    def test_has_import_alias(self, rel_path: str) -> None:
        full = ROOT / rel_path
        old_cls = MERGE_SHIM_MAP[rel_path][0]
        tree = ast.parse(full.read_text(encoding="utf-8"))
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.asname == old_cls or (alias.name == old_cls and alias.asname is None):
                        found = True
        assert found, f"Shim {rel_path} missing re-export alias for {old_cls}"

    @pytest.mark.parametrize("rel_path", list(MERGE_SHIM_MAP.keys()), ids=lambda p: Path(p).stem)
    def test_import_target_exists(self, rel_path: str) -> None:
        canon_mod = MERGE_SHIM_MAP[rel_path][2]
        mod_path = canon_mod.replace(".", "/") + ".py"
        assert (ROOT / mod_path).exists(), f"Import target does not exist: {mod_path}"


class TestRetirementShimNoDiscovery:
    """Retirement shim files must not contain discoverable agent ClassDefs."""

    FULL_RETIRE_FILES = [
        p
        for p in TARGETS["retire"]
        if p
        not in {
            "apps_lic/engines/LicReflectionAgent.py",
            "apps_lic/engines/LicTemplateOptimizerAgent.py",
            "apps_lic/engines/MessageComplianceAgent.py",
            "apps_lic/engines/OutreachLearningAgent.py",
            "apps_lic/engines/OutreachProactiveAgent.py",
            "apps_lic/engines/MessageDiversityValidator.py",
            "agentic_core/runtime/utils/discovery_util.py",
        }
    ]

    @pytest.mark.parametrize("rel_path", FULL_RETIRE_FILES, ids=lambda p: Path(p).stem)
    def test_no_classdef_in_full_retirement(self, rel_path: str) -> None:
        full = ROOT / rel_path
        assert full.exists(), f"Retirement file missing: {rel_path}"
        tree = ast.parse(full.read_text(encoding="utf-8"))
        class_defs = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        assert class_defs == [], f"Full retirement {rel_path} has ClassDefs: {class_defs}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
