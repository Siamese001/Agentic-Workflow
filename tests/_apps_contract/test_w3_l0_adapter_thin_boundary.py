"""
W3 Boundary Check: L0 Adapter is Thin Only

Validates that apps_research_l0_binding_v2.py is a thin adapter with no app-specific logic.
"""
from __future__ import annotations

import ast
import inspect
import pytest
from pathlib import Path


class TestW3AppsResearchL0AdapterIsThinOnly:
    """Verify L0 adapter delegates to generic binding only."""
    
    def test_w3_apps_research_l0_adapter_is_thin_only(self):
        """
        Prove that apps_research_l0_binding_v2.py:
        - Delegates to generic L0 only
        - Has no route order constants
        - Has no semantic cache policy constants
        - Has no managed_workflow policy
        - Has no apps_rg/apps_lic final-output reuse rules
        """
        repo_root = Path(__file__).parent.parent.parent
        adapter_path = repo_root / "agentic_core/L0_routing/apps_research_l0_binding_v2.py"
        
        assert adapter_path.exists(), "L0 adapter file must exist"
        
        source = adapter_path.read_text()
        
        # Must delegate to generic binding
        assert "l0_evaluate_routes_package_driven" in source, \
            "Adapter must delegate to generic l0_evaluate_routes_package_driven"
        
        # Must NOT have route order constants
        forbidden_route_constants = [
            "ROUTE_ORDER",
            "ROUTE_SEQUENCE",
            "EVALUATION_ORDER",
            "['R5', 'R1A', 'R1B', 'R3']",
        ]
        for term in forbidden_route_constants:
            assert term not in source, f"Adapter must not hardcode route order: {term}"
        
        # Must NOT have semantic cache policy constants
        forbidden_cache_constants = [
            "SEMANTIC_CACHE_SCOPE",
            "research_substrate_only",
            "RESEARCH_SUBSTRATE",
            "CACHE_TTL",
        ]
        for term in forbidden_cache_constants:
            assert term not in source, f"Adapter must not hardcode cache policy: {term}"
        
        # Must NOT have managed_workflow policy
        forbidden_workflow_constants = [
            "MANAGED_WORKFLOW_ALLOWED",
            "managed_workflow_allowed = True",
            "managed_workflow = True",
        ]
        for term in forbidden_workflow_constants:
            assert term not in source, f"Adapter must not hardcode managed_workflow: {term}"
        
        # Must NOT have apps_rg/apps_lic final-output reuse rules
        forbidden_reuse_rules = [
            "apps_rg_output",
            "apps_lic_output",
            "final_output_reuse",
            "resume_output",
            "response_output",
        ]
        for term in forbidden_reuse_rules:
            assert term not in source.lower(), f"Adapter must not hardcode final-output reuse: {term}"
    
    def test_w3_l0_adapter_has_no_function_body_beyond_delegation(self):
        """Prove the adapter function has minimal body beyond calling generic binding."""
        from agentic_core.L0_routing.apps_research_l0_binding_v2 import l0_route_apps_research
        
        import inspect
        source = inspect.getsource(l0_route_apps_research)
        
        # Should be a simple delegation
        # Allowed: docstring, return statement, function call
        lines = [line.strip() for line in source.split('\n') if line.strip() and not line.strip().startswith('#')]
        
        # Count non-trivial lines (excluding def, docstring markers, return)
        code_lines = []
        for line in lines:
            if line.startswith('def '):
                continue
            if line.startswith('"""') or line.startswith("'''"):
                continue
            if line in ['"""', "'''", 'pass']:
                continue
            code_lines.append(line)
        
        # Should primarily be: return l0_evaluate_routes_package_driven(...)
        assert len(code_lines) <= 3, f"Adapter should be minimal, got {len(code_lines)} code lines"
        
        # Must call the generic function
        assert "l0_evaluate_routes_package_driven" in source
    
    def test_w3_l0_adapter_imports_only_generic_bindings(self):
        """Prove adapter imports only generic bindings, not app-specific policy."""
        repo_root = Path(__file__).parent.parent.parent
        adapter_path = repo_root / "agentic_core/L0_routing/apps_research_l0_binding_v2.py"
        
        source = adapter_path.read_text()
        
        # Must import from generic package_driven_l0_binding
        assert "from agentic_core.L0_routing.package_driven_l0_binding import" in source
        
        # Must NOT import app-specific constants
        forbidden_imports = [
            "APPS_RESEARCH",
            "company_brief",
            "RESEARCH_SUBSTRATE",
            "apps_rg",
            "apps_lic",
        ]
        for term in forbidden_imports:
            assert term not in source, f"Adapter must not import app-specific constants: {term}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
