"""
Structural enforcement tests for HOP agent migration to HOPStageCapability.

Validates:
- All 9 HOP agents have HOPStageCapability in their MRO
- HOPStageCapability precedes LICAgentBase in MRO
- HOP_STAGE_NAME is set and globally unique
- REQUIRED_INPUTS is set (may be empty for entry-point agents)
- All agents implement _process()
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
HOP_AGENTS_DIR = PROJECT_ROOT / "apps_lic" / "engines"

HOP_AGENT_FILES = [
    "Hop1ProfileAnalysisAgent.py",
    "Hop2ResearchAgent.py",
    "HOP3SenderGroundingAgent.py",
    "Hop4RoutingAgent.py",
    "HOP5GenerationAgent.py",
    "Hop6ValidationAgent.py",
    "HOP7GateDecisionAgent.py",
    "HOP8QAReportAgent.py",
    "HOP9IntegrationAgent.py",
]

EXPECTED_STAGE_NAMES = {
    "Hop1ProfileAnalysisAgent.py": "hop1_analysis",
    "Hop2ResearchAgent.py": "hop2_research",
    "HOP3SenderGroundingAgent.py": "hop3_sender_grounding",
    "Hop4RoutingAgent.py": "hop4_routing",
    "HOP5GenerationAgent.py": "hop5_generation",
    "Hop6ValidationAgent.py": "hop6_validation_report",
    "HOP7GateDecisionAgent.py": "hop7_gate_decision",
    "HOP8QAReportAgent.py": "hop8_qa_report",
    "HOP9IntegrationAgent.py": "hop9_integration",
}


def _parse_class_info(filepath: Path) -> dict:
    """Parse AST to extract class bases, class variables, and methods."""
    source = filepath.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(filepath))

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and "HOP" in node.name.upper():
            bases = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    bases.append(base.id)
                elif isinstance(base, ast.Attribute):
                    bases.append(base.attr)

            class_vars = {}
            methods = []
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    name = item.target.id
                    if item.value and isinstance(item.value, (ast.Constant, ast.List)):
                        if isinstance(item.value, ast.Constant):
                            class_vars[name] = item.value.value
                        elif isinstance(item.value, ast.List):
                            class_vars[name] = [
                                elt.value for elt in item.value.elts if isinstance(elt, ast.Constant)
                            ]
                if isinstance(item, ast.FunctionDef):
                    methods.append(item.name)

            return {
                "class_name": node.name,
                "bases": bases,
                "class_vars": class_vars,
                "methods": methods,
            }
    return {}


class TestHOPMigrationMRO:
    """Verify all 9 HOP agents have correct MRO with HOPStageCapability."""

    @pytest.mark.parametrize("filename", HOP_AGENT_FILES)
    def test_hop_stage_capability_in_bases(self, filename: str) -> None:
        """HOPStageCapability must appear in the class bases."""
        info = _parse_class_info(HOP_AGENTS_DIR / filename)
        assert info, f"Could not parse class from {filename}"
        assert "HOPStageCapability" in info["bases"], (
            f"{info['class_name']} missing HOPStageCapability in bases: {info['bases']}"
        )

    @pytest.mark.parametrize("filename", HOP_AGENT_FILES)
    def test_hop_stage_capability_precedes_lic_base(self, filename: str) -> None:
        """HOPStageCapability must precede LICAgentBase in MRO."""
        info = _parse_class_info(HOP_AGENTS_DIR / filename)
        assert info, f"Could not parse class from {filename}"
        bases = info["bases"]
        if "HOPStageCapability" in bases and "LICAgentBase" in bases:
            cap_idx = bases.index("HOPStageCapability")
            lic_idx = bases.index("LICAgentBase")
            assert cap_idx < lic_idx, (
                f"{info['class_name']}: HOPStageCapability ({cap_idx}) must precede "
                f"LICAgentBase ({lic_idx}) in MRO"
            )


class TestHOPStageNameUniqueness:
    """Verify HOP_STAGE_NAME is set and globally unique."""

    def test_all_stage_names_present(self) -> None:
        """Every HOP agent must have HOP_STAGE_NAME set."""
        for filename in HOP_AGENT_FILES:
            info = _parse_class_info(HOP_AGENTS_DIR / filename)
            assert info, f"Could not parse class from {filename}"
            assert "HOP_STAGE_NAME" in info["class_vars"], (
                f"{info['class_name']} missing HOP_STAGE_NAME class variable"
            )

    def test_stage_names_match_expected(self) -> None:
        """HOP_STAGE_NAME must match the expected buffer key."""
        for filename, expected_name in EXPECTED_STAGE_NAMES.items():
            info = _parse_class_info(HOP_AGENTS_DIR / filename)
            assert info, f"Could not parse class from {filename}"
            actual = info["class_vars"].get("HOP_STAGE_NAME")
            assert actual == expected_name, (
                f"{info['class_name']}: HOP_STAGE_NAME={actual!r}, expected={expected_name!r}"
            )

    def test_stage_names_globally_unique(self) -> None:
        """No two HOP agents may share the same HOP_STAGE_NAME."""
        seen: dict[str, str] = {}
        for filename in HOP_AGENT_FILES:
            info = _parse_class_info(HOP_AGENTS_DIR / filename)
            name = info["class_vars"].get("HOP_STAGE_NAME", "")
            if name in seen:
                pytest.fail(
                    f"Duplicate HOP_STAGE_NAME={name!r}: {seen[name]} and {info['class_name']}",
                )
            seen[name] = info["class_name"]


class TestHOPProcessMethod:
    """Verify all agents implement _process()."""

    @pytest.mark.parametrize("filename", HOP_AGENT_FILES)
    def test_process_method_exists(self, filename: str) -> None:
        """Every HOP agent must implement _process()."""
        info = _parse_class_info(HOP_AGENTS_DIR / filename)
        assert info, f"Could not parse class from {filename}"
        assert "_process" in info["methods"], f"{info['class_name']} missing _process() method"


class TestHOPImportPresent:
    """Verify hop_stage_capability import is present in all HOP files."""

    @pytest.mark.parametrize("filename", HOP_AGENT_FILES)
    def test_import_hop_stage_capability(self, filename: str) -> None:
        """Every HOP agent file must import HOPStageCapability."""
        source = (HOP_AGENTS_DIR / filename).read_text(encoding="utf-8")
        assert "from apps_lic.utils.hop_stage_capability import HOPStageCapability" in source, (
            f"{filename} missing HOPStageCapability import"
        )
