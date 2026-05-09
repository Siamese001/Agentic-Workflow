"""
W4 Quarantine Bypass Tests — AG-RGGOV-5, AG-RGGOV-8, AG-RGGOV-9

Validates that:
1. apps_rg cannot emit FinalEvidenceContract (AG-RGGOV-5)
2. apps_rg cannot import or execute hops (AG-RGGOV-8)
3. Core aliases cannot reach apps_rg runtime code (AG-RGGOV-9)
4. Quarantine is inert (RuntimeError on import)

These tests MUST pass before W4 is considered complete.
"""

import sys
import pathlib

import pytest


class TestAG_RGGOV_5_FEC_Quarantine:
    """AG-RGGOV-5: CORE_OWNED_FEC_ONLY — apps_rg cannot emit FEC."""

    def test_fec_producer_import_raises_runtime_error(self):
        """Importing apps_rg.cert.fec_producer raises RuntimeError."""
        # Remove module from cache if present
        if "apps_rg.cert.fec_producer" in sys.modules:
            del sys.modules["apps_rg.cert.fec_producer"]
        
        with pytest.raises(RuntimeError) as exc_info:
            import apps_rg.cert.fec_producer  # noqa: F401
        
        assert "QUARANTINE VIOLATION" in str(exc_info.value)
        assert "AG-RGGOV-5" in str(exc_info.value)
        assert "apps_rg may NOT emit FinalEvidenceContract" in str(exc_info.value)

    def test_produce_fec_not_callable(self):
        """produce_fec function is not reachable."""
        # If we somehow got the module, the function shouldn't work
        with pytest.raises(RuntimeError):
            import apps_rg.cert.fec_producer as fec_module
            # Should never reach here, but if we do:
            if hasattr(fec_module, 'produce_fec'):
                fec_module.produce_fec({})

    def test_fec_emission_blocked_static_scan(self):
        """Static scan: produce_fec function presence under apps_rg/ = fail."""
        # This test documents the static scan requirement
        # In CI, a grep-based scan will enforce this
        apps_rg_path = pathlib.Path(__file__).parent.parent.parent / "apps_rg"
        
        # Look for any Python file that defines produce_fec (excluding quarantine stubs)
        py_files = list(apps_rg_path.rglob("*.py"))
        
        for py_file in py_files:
            if "quarantine" in str(py_file).lower() or "test" in str(py_file).lower():
                continue
            
            content = py_file.read_text(encoding="utf-8")
            # Check for actual function definition, not just the word in comments
            if "def produce_fec(" in content:
                # Check if it's the quarantine stub (which is allowed)
                if "QUARANTINE VIOLATION" not in content:
                    pytest.fail(
                        f"AG-RGGOV-5 VIOLATION: Live produce_fec found in {py_file}. "
                        f"apps_rg may NOT emit FinalEvidenceContract."
                    )


class TestAG_RGGOV_8_Hops_Quarantine:
    """AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS — apps_rg cannot run hops."""

    def test_hops_import_raises_runtime_error(self):
        """Importing apps_rg.integrations.hops raises RuntimeError."""
        # Remove module from cache if present
        for mod in list(sys.modules.keys()):
            if mod.startswith("apps_rg.integrations.hops"):
                del sys.modules[mod]
        
        with pytest.raises(RuntimeError) as exc_info:
            import apps_rg.integrations.hops  # noqa: F401
        
        assert "QUARANTINE VIOLATION" in str(exc_info.value)
        assert "AG-RGGOV-8" in str(exc_info.value)
        assert "apps_rg.integrations.hops is QUARANTINED" in str(exc_info.value)

    def test_hops_submodule_import_blocked(self):
        """Any hops submodule import raises RuntimeError."""
        # Remove module from cache if present
        for mod in list(sys.modules.keys()):
            if mod.startswith("apps_rg.integrations.hops"):
                del sys.modules[mod]
        
        # Try importing a specific submodule that used to exist
        with pytest.raises(RuntimeError):
            from apps_rg.integrations.hops import _ensemble_runner  # noqa: F401

    def test_no_live_hop_runners_in_apps_rg(self):
        """Static scan: No live hop runners under apps_rg/."""
        apps_rg_path = pathlib.Path(__file__).parent.parent.parent / "apps_rg"
        
        # These are runtime authority patterns that must not exist in live code
        forbidden_patterns = [
            "def run_ensemble(",
            "def run_hop(",
            "def execute_runner(",
            "class.*Runner",  # Runner classes
            "class.*Judge",   # Judge classes
            "def judge_",     # Judge functions
            "def generate_",  # Generation functions (if runtime)
        ]
        
        py_files = list(apps_rg_path.rglob("*.py"))
        
        for py_file in py_files:
            if "quarantine" in str(py_file).lower() or "test" in str(py_file).lower():
                continue
            
            content = py_file.read_text(encoding="utf-8")
            
            for pattern in forbidden_patterns:
                # Simple pattern check (not regex)
                if pattern in content and "QUARANTINE" not in content:
                    pytest.fail(
                        f"AG-RGGOV-8 VIOLATION: Pattern '{pattern}' found in {py_file}. "
                        f"apps_rg may NOT contain runtime hop runners."
                    )

    def test_llm_client_quarantined(self):
        """apps_rg LLM client is quarantined."""
        # The _llm_client.py should not be importable
        with pytest.raises(RuntimeError):
            from apps_rg.integrations.hops import _llm_client  # noqa: F401


class TestAG_RGGOV_9_Alias_Cleanup:
    """AG-RGGOV-9: REMOVE_APPS_RG_RUNTIME_ALIASES — Core aliases cannot reach apps_rg runtime."""

    def test_apps_engines_aliases_no_apps_rg_orchestrators(self):
        """apps_engines_aliases.py does not import apps_rg orchestrators."""
        alias_file = (
            pathlib.Path(__file__).parent.parent.parent
            / "agentic_core"
            / "utils"
            / "workflow_engines"
            / "apps_engines_aliases.py"
        )
        
        content = alias_file.read_text(encoding="utf-8")
        
        # Check for removed imports
        forbidden_apps_rg_imports = [
            "from apps_rg",
            "import apps_rg",
            "RgResumeOrchestrator",
            "RgHealingOrchestrator",
            "RgReflectionAgent",
            "BrandComplianceAgent",
            "CampaignPlannerAgent",
            "ContentStrategyAgent",
            "ContentQualityAgent",
        ]
        
        for import_pattern in forbidden_apps_rg_imports:
            # Allow comments that mention these
            for line in content.split("\n"):
                if import_pattern in line and not line.strip().startswith("#"):
                    if "AG-RGGOV-9" not in line and "REMOVED" not in line:
                        pytest.fail(
                            f"AG-RGGOV-9 VIOLATION: Live apps_rg import '{import_pattern}' "
                            f"found in apps_engines_aliases.py: {line.strip()}. "
                            f"Core aliases must NOT point to apps_rg runtime code."
                        )

    def test_apps_engines_aliases_documented_removals(self):
        """apps_engines_aliases.py documents all removed apps_rg imports."""
        alias_file = (
            pathlib.Path(__file__).parent.parent.parent
            / "agentic_core"
            / "utils"
            / "workflow_engines"
            / "apps_engines_aliases.py"
        )
        
        content = alias_file.read_text(encoding="utf-8")
        
        # Should mention AG-RGGOV-9
        assert "AG-RGGOV-9" in content, "Alias file must reference AG-RGGOV-9"
        
        # Should list removed imports in comments
        assert "BrandComplianceAgent" in content
        assert "CampaignPlannerAgent" in content
        assert "RgResumeOrchestrator" in content

    def test_cannot_import_rg_orchestrator_via_alias(self):
        """Cannot import RgResumeOrchestrator via apps_engines_aliases."""
        # The alias should not exist
        try:
            from agentic_core.utils.workflow_engines.apps_engines_aliases import (
                RgResumeOrchestrator,  # noqa: F401
            )
            pytest.fail(
                "AG-RGGOV-9 VIOLATION: RgResumeOrchestrator is still importable via aliases."
            )
        except ImportError:
            pass  # Expected — import should fail

    def test_adg_edge_scan_no_apps_rg_runtime_symbols(self):
        """ADG edge scan: apps_engines_aliases.py → apps_rg runtime symbols = fail."""
        # This test documents the ADG scan requirement
        # In CI, ADG-based scan will verify this
        
        # For now, do a simple text check
        alias_file = (
            pathlib.Path(__file__).parent.parent.parent
            / "agentic_core"
            / "utils"
            / "workflow_engines"
            / "apps_engines_aliases.py"
        )
        
        content = alias_file.read_text(encoding="utf-8")
        
        # Should not have any live imports from apps_rg (only comments)
        for line in content.split("\n"):
            if line.strip().startswith("from apps_rg") or line.strip().startswith("import apps_rg"):
                if not line.strip().startswith("#"):
                    pytest.fail(
                        f"AG-RGGOV-9 VIOLATION: Live apps_rg import found: {line.strip()}"
                    )


class TestQuarantineInertness:
    """Verify quarantine stubs are properly inert."""

    def test_fec_producer_stub_content(self):
        """fec_producer.py is a quarantine stub, not live code."""
        fec_file = (
            pathlib.Path(__file__).parent.parent.parent
            / "apps_rg"
            / "cert"
            / "fec_producer.py"
        )
        
        content = fec_file.read_text(encoding="utf-8")
        
        # Should be a stub
        assert "QUARANTINE" in content
        assert "RuntimeError" in content
        
        # Should NOT have the original function
        assert "def produce_fec(" not in content

    def test_hops_init_stub_content(self):
        """hops/__init__.py is a quarantine stub."""
        init_file = (
            pathlib.Path(__file__).parent.parent.parent
            / "apps_rg"
            / "integrations"
            / "hops"
            / "__init__.py"
        )
        
        content = init_file.read_text(encoding="utf-8")
        
        # Should be a stub
        assert "QUARANTINE" in content
        assert "RuntimeError" in content
        assert "AG-RGGOV-8" in content

    def test_no_provider_calls_reachable(self):
        """No provider calls (openai, anthropic, etc.) reachable under apps_rg."""
        apps_rg_path = pathlib.Path(__file__).parent.parent.parent / "apps_rg"
        
        # Check for provider import patterns
        provider_patterns = [
            "import openai",
            "from openai",
            "import anthropic",
            "from anthropic",
            "import google.generativeai",
            "from vllm",
            "import vllm",
        ]
        
        py_files = list(apps_rg_path.rglob("*.py"))
        
        for py_file in py_files:
            if "quarantine" in str(py_file).lower() or "test" in str(py_file).lower():
                continue
            
            content = py_file.read_text(encoding="utf-8")
            
            for pattern in provider_patterns:
                if pattern in content:
                    # Check if it's the quarantine stub
                    if "QUARANTINE" not in content and "RuntimeError" not in content:
                        pytest.fail(
                            f"AG-RGGOV-8 VIOLATION: Provider import '{pattern}' in {py_file}. "
                            f"apps_rg may NOT make provider calls."
                        )


class TestNoCoreContractEmission:
    """apps_rg cannot emit core runtime contracts."""

    def test_no_l1_plan_contract_emission(self):
        """apps_rg code cannot construct or emit L1PlanContract."""
        apps_rg_path = pathlib.Path(__file__).parent.parent.parent / "apps_rg"
        
        py_files = list(apps_rg_path.rglob("*.py"))
        
        for py_file in py_files:
            if "quarantine" in str(py_file).lower() or "test" in str(py_file).lower():
                continue
            
            content = py_file.read_text(encoding="utf-8")
            
            # Check for contract emission patterns
            forbidden_contracts = [
                "L1PlanContract",
                "RouteContract",
                "FinalEvidenceContract",
                "CompiledPromptArtifact",
                "SealedL2Artifact",
                "X3Disposition",
                "GateVerdict",
                "CommitRequest",
                "LearningProposal",
            ]
            
            for contract in forbidden_contracts:
                if contract in content and "QUARANTINE" not in content:
                    # Allow imports for type checking if no emission
                    if "(" in content and contract in content.split("(")[0]:
                        pytest.fail(
                            f"CONTRACT_EMISSION VIOLATION: {contract} in {py_file}. "
                            f"apps_rg may NOT emit core runtime contracts."
                        )
