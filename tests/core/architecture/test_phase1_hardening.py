#!/usr/bin/env python3
"""
Test Suite: Phase 1 Hardening - Safety Net Components

Tests for the foundational hardening components:
1. IOrchestrator Protocol adherence
2. InfrastructureMixin state verification
3. SovereignIndex cache invalidation

All tests must pass 100%.
"""
import sys
import os
import tempfile
from pathlib import Path
from typing import Dict, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest


class TestIOrchestrator:
    """Tests for IOrchestrator Protocol."""
    
    def test_protocol_adherence_complete(self):
        """Test Case C: Complete implementation passes isinstance check."""
        from agentic_core.L5_safety.validators.orchestrator import IOrchestrator
        
        class CompleteOrchestrator:
            def run_mission(self, context: Dict[str, Any]) -> Dict[str, Any]:
                return {"status": "SUCCESS"}
            
            def validate_stability(self, result: Dict[str, Any]) -> bool:
                return True
        
        obj = CompleteOrchestrator()
        assert isinstance(obj, IOrchestrator), "Complete implementation should pass isinstance check"
    
    def test_protocol_adherence_missing_validate_stability(self):
        """Test Case C: Missing validate_stability fails isinstance check."""
        from agentic_core.L5_safety.validators.orchestrator import IOrchestrator
        
        class IncompleteOrchestrator:
            def run_mission(self, context: Dict[str, Any]) -> Dict[str, Any]:
                return {"status": "SUCCESS"}
            # Missing validate_stability!
        
        obj = IncompleteOrchestrator()
        assert not isinstance(obj, IOrchestrator), "Missing validate_stability should fail isinstance check"
    
    def test_protocol_adherence_missing_run_mission(self):
        """Missing run_mission fails isinstance check."""
        from agentic_core.L5_safety.validators.orchestrator import IOrchestrator
        
        class IncompleteOrchestrator:
            # Missing run_mission!
            def validate_stability(self, result: Dict[str, Any]) -> bool:
                return True
        
        obj = IncompleteOrchestrator()
        assert not isinstance(obj, IOrchestrator), "Missing run_mission should fail isinstance check"
    
    def test_ihealable_protocol_complete(self):
        """IHealable protocol with complete implementation."""
        from agentic_core.L5_safety.validators.orchestrator import IHealable
        
        class CompleteHealer:
            def heal_repository(
                self,
                dry_run: bool = True,
                execute: bool = False,
                **kwargs: Any
            ) -> Dict[str, Any]:
                return {"violations_found": 0, "violations_fixed": 0}
        
        obj = CompleteHealer()
        assert isinstance(obj, IHealable), "Complete healer should pass isinstance check"
    
    def test_ihealable_protocol_missing(self):
        """IHealable protocol with missing method."""
        from agentic_core.L5_safety.validators.orchestrator import IHealable
        
        class IncompleteHealer:
            pass  # Missing heal_repository
        
        obj = IncompleteHealer()
        assert not isinstance(obj, IHealable), "Missing heal_repository should fail isinstance check"


class TestInfrastructureMixin:
    """Tests for InfrastructureMixin state verification."""
    
    def test_proper_initialization(self):
        """Proper initialization sets _infra_initialized flag."""
        from agentic_core.utils.core_extensions.infrastructure_mixin import InfrastructureMixin
        
        class ProperAgent(InfrastructureMixin):
            def __init__(self):
                super().__init__()
        
        agent = ProperAgent()
        assert agent._infra_initialized is True
        # verify_state should not raise
        assert agent.verify_state() is True
    
    def test_broken_chain_no_super_init(self):
        """Test Case A: Forgetting super().__init__() causes verify_state to raise."""
        from agentic_core.utils.core_extensions.infrastructure_mixin import InfrastructureMixin
        
        class BrokenAgent(InfrastructureMixin):
            def __init__(self):
                # BROKEN: Forgot to call super().__init__()
                self.project_root = Path(".")
        
        agent = BrokenAgent()
        
        # _infra_initialized should be False (class default, not instance)
        assert getattr(agent, '_infra_initialized', False) is False
        
        # verify_state should raise RuntimeError
        with pytest.raises(RuntimeError) as exc_info:
            agent.verify_state()
        
        assert "_infra_initialized is False" in str(exc_info.value)
        assert "super().__init__()" in str(exc_info.value)
    
    def test_get_infrastructure_status(self):
        """get_infrastructure_status returns correct status."""
        from agentic_core.utils.core_extensions.infrastructure_mixin import InfrastructureMixin
        
        class StatusAgent(InfrastructureMixin):
            def __init__(self):
                super().__init__()
        
        agent = StatusAgent()
        status = agent.get_infrastructure_status()
        
        assert status["infra_initialized"] is True
        assert status["class_name"] == "StatusAgent"
        assert "healer_ready" in status
    
    def test_reset_infrastructure(self):
        """reset_infrastructure clears the initialized flag."""
        from agentic_core.utils.core_extensions.infrastructure_mixin import InfrastructureMixin
        
        class ResetAgent(InfrastructureMixin):
            def __init__(self):
                super().__init__()
        
        agent = ResetAgent()
        assert agent._infra_initialized is True
        
        agent.reset_infrastructure()
        assert agent._infra_initialized is False


class TestSovereignIndex:
    """Tests for SovereignIndex cache and invalidation."""
    
    def setup_method(self):
        """Reset singleton before each test."""
        from archives.location_violations.sovereign_index import SovereignIndex
        SovereignIndex.reset_instance()
    
    def teardown_method(self):
        """Reset singleton after each test."""
        from archives.location_violations.sovereign_index import SovereignIndex
        SovereignIndex.reset_instance()
    
    def test_singleton_pattern(self):
        """get_instance returns the same instance."""
        from archives.location_violations.sovereign_index import SovereignIndex
        
        index1 = SovereignIndex.get_instance(PROJECT_ROOT)
        index2 = SovereignIndex.get_instance()
        
        assert index1 is index2
    
    def test_get_files_basic(self):
        """get_files returns files matching pattern."""
        from archives.location_violations.sovereign_index import SovereignIndex
        
        index = SovereignIndex.get_instance(PROJECT_ROOT)
        
        # Get Python files
        py_files = index.get_files("*.py")
        assert len(py_files) > 0
        assert all(f.suffix == ".py" for f in py_files)
    
    def test_get_agent_files(self):
        """get_agent_files returns agent files."""
        from archives.location_violations.sovereign_index import SovereignIndex
        import fnmatch
        
        index = SovereignIndex.get_instance(PROJECT_ROOT)
        
        agent_files = index.get_agent_files()
        assert len(agent_files) > 0
        # All returned files should match the *Agent.py pattern (fnmatch)
        # This includes files like "find_missing_agent.py" since fnmatch is case-sensitive
        # and the pattern is *Agent.py (capital A)
        assert all(fnmatch.fnmatch(f.name, "*Agent.py") for f in agent_files)
    
    def test_phantom_file_cache_invalidation(self, tmp_path):
        """Test Case B: Phantom file detection via cache invalidation."""
        from archives.location_violations.sovereign_index import SovereignIndex
        
        # Create a temporary directory structure
        test_dir = tmp_path / "test_project"
        test_dir.mkdir()
        
        # Create initial file
        existing_file = test_dir / "existing.py"
        existing_file.write_text("# existing")
        
        # Create index for temp directory
        SovereignIndex.reset_instance()
        index = SovereignIndex.get_instance(test_dir)
        
        # Verify existing file is found
        files = index.get_files("*.py")
        assert existing_file in files
        
        # Create ghost file
        ghost_file = test_dir / "ghost.py"
        ghost_file.write_text("# ghost")
        
        # Invalidate cache
        index.invalidate()
        
        # Verify ghost file is now found
        files = index.get_files("*.py")
        assert ghost_file in files
        
        # Delete ghost file externally
        os.remove(ghost_file)
        
        # Invalidate cache again
        index.invalidate()
        
        # Verify ghost file is NOT returned (cache invalidation works)
        files = index.get_files("*.py")
        assert ghost_file not in files, "Deleted file should not be in index after invalidation"
    
    def test_exclusion_patterns(self, tmp_path):
        """Excluded directories are not scanned."""
        from archives.location_violations.sovereign_index import SovereignIndex
        
        # Create temp structure with excluded dir
        test_dir = tmp_path / "test_project"
        test_dir.mkdir()
        
        # Create file in main dir
        main_file = test_dir / "main.py"
        main_file.write_text("# main")
        
        # Create file in __pycache__ (should be excluded)
        pycache_dir = test_dir / "__pycache__"
        pycache_dir.mkdir()
        cached_file = pycache_dir / "cached.py"
        cached_file.write_text("# cached")
        
        SovereignIndex.reset_instance()
        index = SovereignIndex.get_instance(test_dir)
        
        files = index.get_files("*.py")
        
        assert main_file in files
        assert cached_file not in files, "__pycache__ files should be excluded"
    
    def test_get_stats(self):
        """get_stats returns index statistics."""
        from archives.location_violations.sovereign_index import SovereignIndex
        
        index = SovereignIndex.get_instance(PROJECT_ROOT)
        index.refresh()
        
        stats = index.get_stats()
        
        assert "total_files" in stats
        assert stats["total_files"] > 0
        assert "cached_patterns" in stats
        assert stats["initialized"] is True
    
    def test_add_remove_exclusion(self, tmp_path):
        """add_exclusion and remove_exclusion work correctly."""
        from archives.location_violations.sovereign_index import SovereignIndex
        
        test_dir = tmp_path / "test_project"
        test_dir.mkdir()
        
        # Create custom dir
        custom_dir = test_dir / "custom_exclude"
        custom_dir.mkdir()
        custom_file = custom_dir / "file.py"
        custom_file.write_text("# custom")
        
        SovereignIndex.reset_instance()
        index = SovereignIndex.get_instance(test_dir)
        
        # Initially, custom_exclude is not excluded
        files = index.get_files("*.py")
        assert custom_file in files
        
        # Add exclusion
        index.add_exclusion("custom_exclude")
        files = index.get_files("*.py")
        assert custom_file not in files
        
        # Remove exclusion
        index.remove_exclusion("custom_exclude")
        files = index.get_files("*.py")
        assert custom_file in files


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "#" * 60)
    print("# Phase 1 Hardening Test Suite")
    print("#" * 60)
    
    # Run with pytest
    exit_code = pytest.main([__file__, "-v", "--tb=short"])
    
    if exit_code == 0:
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED (100%)")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("SOME TESTS FAILED")
        print("=" * 60)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(run_all_tests())
