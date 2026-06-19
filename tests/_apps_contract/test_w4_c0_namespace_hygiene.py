"""
W4 C0 Namespace Hygiene Tests for apps_research

Validates that:
1. C0 files live under agentic_core/runtime/c0/ or agentic_core/C0_context/
2. C0 files do NOT live under agentic_core/L1_cognition/
3. C0 adapter is thin (delegates only)
"""
from __future__ import annotations

import pytest
from pathlib import Path


class TestC0NamespaceHygiene:
    """Verify C0 files are in correct namespace location."""
    
    def test_w4_c0_binding_lives_under_c0_or_runtime_c0_not_l1(self):
        """C0 package driven grounding must live under runtime/c0/, not L1_cognition/."""
        repo_root = Path(__file__).parent.parent.parent
        
        # Correct locations
        runtime_c0_path = repo_root / "agentic_core/runtime/c0/c0_package_driven_grounding.py"
        
        # Incorrect location (should not exist)
        l1_c0_path = repo_root / "agentic_core/L1_cognition/c0_package_driven_grounding.py"
        
        # Must exist in correct location
        assert runtime_c0_path.exists(), "C0 binding must exist under agentic_core/runtime/c0/"
        
        # Must NOT exist in L1_cognition
        assert not l1_c0_path.exists(), "C0 binding must NOT exist under agentic_core/L1_cognition/"
    
    def test_w4_no_c0_runtime_under_l1_cognition(self):
        """No C0 runtime files should exist under L1_cognition directory."""
        repo_root = Path(__file__).parent.parent.parent
        l1_path = repo_root / "agentic_core/L1_cognition"
        
        # Get all Python files in L1_cognition
        c0_files_in_l1 = []
        if l1_path.exists():
            for py_file in l1_path.glob("*.py"):
                # Check if file contains C0 runtime logic (imports or defines C0 contracts)
                content = py_file.read_text()
                if "c0" in py_file.name.lower() or "FinalEvidenceContract" in content:
                    # Exclude the thin adapter (allowed to reference C0)
                    if "_c0_binding" not in py_file.name:
                        c0_files_in_l1.append(py_file.name)
        
        assert len(c0_files_in_l1) == 0, f"C0 runtime files found in L1_cognition: {c0_files_in_l1}"
    
    def test_w4_apps_research_c0_adapter_is_thin_only(self):
        """apps_research C0 adapter must only delegate to generic binding."""
        repo_root = Path(__file__).parent.parent.parent
        adapter_path = repo_root / "agentic_core/L1_cognition/apps_research_c0_binding.py"
        
        assert adapter_path.exists(), "C0 adapter must exist"
        
        content = adapter_path.read_text()
        
        # Must import from runtime.c0 (correct location)
        assert "from agentic_core.runtime.c0.c0_package_driven_grounding import" in content, \
            "C0 adapter must import from agentic_core.runtime.c0"
        
        # Must NOT have retrieval logic
        forbidden = [
            "retrieval_strategy",
            "source_list",
            "freshness_override",
            "execute_retrieval",
            "searxng",
            "tavily",
        ]
        
        for term in forbidden:
            assert term not in content.lower(), f"C0 adapter has retrieval logic: {term}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
