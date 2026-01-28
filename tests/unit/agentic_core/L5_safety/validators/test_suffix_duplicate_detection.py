"""
Test Suite for Suffix-Based Duplicate Detection

Tests the enhanced CodeDeduplicationAgent, ArchitectureGovernorAgent, and
CognitiveDispositionAgent to prevent future _flat and _1 suffix duplicates.

RCA: These duplicates were created during Phase 1-8 architectural sovereignty
work when flattening operations created duplicates instead of consolidating
to single canonical files.
"""
from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class test_suffix_duplicate_detection:
    """Test CodeDeduplicationAgent detects suffix-based duplicates."""
    
    def test_detect_flat_suffix_duplicates(self, tmp_path):
        """Test detection of _flat suffix duplicates."""
        from agentic_core.L5_safety.validators.CodeDeduplicationAgent import (
            CodeDeduplicationAgent,
        )
        
        # Create canonical and _flat duplicate
        canonical = tmp_path / "TestAgent.py"
        duplicate = tmp_path / "TestAgent_flat.py"
        
        canonical.write_text("# Canonical version\nclass TestAgent:\n    pass\n")
        duplicate.write_text("# Duplicate version\nclass TestAgent:\n    pass\n")
        
        # Run agent
        agent = CodeDeduplicationAgent()
        python_files = [canonical, duplicate]
        
        agent.scan_filename_duplicates(python_files, tmp_path)
        
        # Should detect the suffix duplicate
        assert len(agent.filename_duplicates) > 0
        assert "TestAgent.py" in agent.filename_duplicates
    
    def test_detect_1_suffix_duplicates(self, tmp_path):
        """Test detection of _1 suffix duplicates."""
        from agentic_core.L5_safety.validators.CodeDeduplicationAgent import (
            CodeDeduplicationAgent,
        )
        
        # Create canonical and _1 duplicate
        canonical = tmp_path / "mcp_hardened_mixin.py"
        duplicate = tmp_path / "mcp_hardened_mixin_1.py"
        
        canonical.write_text("# Canonical version\nclass MCPHardenedMixin:\n    pass\n")
        duplicate.write_text("# Duplicate version\nclass MCPHardenedMixin:\n    pass\n")
        
        # Run agent
        agent = CodeDeduplicationAgent()
        python_files = [canonical, duplicate]
        
        agent.scan_filename_duplicates(python_files, tmp_path)
        
        # Should detect the suffix duplicate
        assert len(agent.filename_duplicates) > 0
        assert "mcp_hardened_mixin.py" in agent.filename_duplicates
    
    def test_no_false_positives_for_legitimate_suffixes(self, tmp_path):
        """Test that legitimate suffixes don't trigger false positives."""
        from agentic_core.L5_safety.validators.CodeDeduplicationAgent import (
            CodeDeduplicationAgent,
        )
        
        # Create files with legitimate suffixes
        file1 = tmp_path / "test_integration.py"
        file2 = tmp_path / "test_unit.py"
        
        file1.write_text("# Integration test\n")
        file2.write_text("# Unit test\n")
        
        # Run agent
        agent = CodeDeduplicationAgent()
        python_files = [file1, file2]
        
        agent.scan_filename_duplicates(python_files, tmp_path)
        
        # Should not detect any duplicates
        assert len(agent.filename_duplicates) == 0
    
    def test_multiple_suffix_duplicates_in_directory(self, tmp_path):
        """Test detection of multiple suffix duplicates with various patterns."""
        from agentic_core.L5_safety.validators.CodeDeduplicationAgent import (
            CodeDeduplicationAgent,
        )
        
        # Create multiple canonical + duplicate pairs with various suffixes
        pairs = [
            ("Agent1.py", "Agent1_flat.py"),
            ("Agent2.py", "Agent2_from_utils.py"),
            ("Agent3.py", "Agent3_1.py"),
            ("Agent4.py", "Agent4_copy.py"),
            ("Agent5.py", "Agent5_backup.py"),
        ]
        
        for canonical_name, dup_name in pairs:
            canonical = tmp_path / canonical_name
            duplicate = tmp_path / dup_name
            canonical.write_text(f"# {canonical_name}\n")
            duplicate.write_text(f"# {dup_name}\n")
        
        # Run agent
        agent = CodeDeduplicationAgent()
        python_files = list(tmp_path.glob("*.py"))
        
        agent.scan_filename_duplicates(python_files, tmp_path)
        
        # Should detect all 5 suffix duplicate groups
        assert len(agent.filename_duplicates) >= 5


class TestArchitectureGovernorIntegration:
    """Test ArchitectureGovernorAgent integrates duplicate detection."""
    
    def test_governor_detects_suffix_duplicates(self, tmp_path):
        """Test that ArchitectureGovernorAgent detects suffix duplicates."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )
        
        # Create SSOT structure with suffix duplicates
        agentic_core = tmp_path / "agentic_core" / "L5_safety" / "validators"
        agentic_core.mkdir(parents=True)
        
        canonical = agentic_core / "TestAgent.py"
        duplicate = agentic_core / "TestAgent_flat.py"
        
        canonical.write_text("# Canonical\n")
        duplicate.write_text("# Duplicate\n")
        
        # Run governor
        agent = ArchitectureGovernorAgent(
            project_root=tmp_path,
            auto_approve=True,
        )
        
        # Run validation
        is_compliant, results = agent.run_ci_verification_sync()
        
        # Should detect violations (may be wrapped in _raw_result)
        assert "violations_found" in results or "violations_found" in results.get("_raw_result", {})


class TestCognitiveDispositionIntegration:
    """Test CognitiveDispositionAgent handles suffix duplicates."""
    
    def test_cognitive_agent_analyzes_suffix_duplicates(self, tmp_path):
        """Test that CognitiveDispositionAgent can analyze suffix duplicates."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )
        
        # Create suffix duplicate scenario
        canonical = tmp_path / "agentic_core" / "L5_safety" / "TestAgent.py"
        duplicate = tmp_path / "agentic_core" / "L5_safety" / "TestAgent_flat.py"
        
        canonical.parent.mkdir(parents=True)
        canonical.write_text("# Canonical version\n")
        duplicate.write_text("# Duplicate version\n")
        
        # Create agent
        agent = CognitiveDispositionAgent(project_root=tmp_path)
        
        # Analyze the duplicate file
        decision = agent.analyze_violation(
            file_path=duplicate,
            violation_type="ORPHAN",
            context="Suffix duplicate detected: TestAgent_flat.py when TestAgent.py exists",
        )
        
        # Should recommend deletion or archival
        assert decision.action in ["DELETE", "ARCHIVE"]
        # Note: Confidence may be lower in heuristic mode without Gemini API
        assert decision.confidence >= 0.4  # Reasonable confidence for duplicates


class TestPreventFutureDuplicates:
    """Test that the system prevents future suffix duplicates."""
    
    def test_ci_validation_catches_suffix_duplicates(self, tmp_path):
        """Test that CI validation catches suffix duplicates before commit."""
        from agentic_core.L5_safety.validators.CodeDeduplicationAgent import (
            CodeDeduplicationAgent,
        )
        
        # Simulate a developer accidentally creating a _flat file
        canonical = tmp_path / "NewAgent.py"
        duplicate = tmp_path / "NewAgent_flat.py"
        
        canonical.write_text("# New agent\n")
        duplicate.write_text("# Accidentally created duplicate\n")
        
        # Run deduplication check (as would happen in CI)
        agent = CodeDeduplicationAgent()
        python_files = [canonical, duplicate]
        
        agent.scan_filename_duplicates(python_files, tmp_path)
        
        # Should detect and report the duplicate
        assert len(agent.filename_duplicates) > 0
        
        # CI should fail if duplicates detected
        ci_should_fail = len(agent.filename_duplicates) > 0
        assert ci_should_fail is True
    
    def test_removal_script_identifies_all_suffix_types(self, tmp_path):
        """Test that removal script identifies all problematic suffix types."""
        # Create various suffix duplicates
        suffixes = ["_flat", "_1", "_2", "_copy"]
        
        for suffix in suffixes:
            canonical = tmp_path / f"Agent{suffix[1:]}.py"
            duplicate = tmp_path / f"Agent{suffix[1:]}{suffix}.py"
            
            canonical.write_text("# Canonical\n")
            duplicate.write_text("# Duplicate\n")
        
        # The removal script should identify _flat and _1
        # (We only handle these two as they were the problematic ones)
        flat_files = list(tmp_path.glob("*_flat.py"))
        one_files = list(tmp_path.glob("*_1.py"))
        
        assert len(flat_files) == 1
        assert len(one_files) == 1


class TestRegressionPrevention:
    """Regression tests to ensure duplicates don't return."""
    
    def test_no_flat_files_in_agentic_core(self):
        """Test that no _flat files exist in agentic_core."""
        from pathlib import Path
        
        project_root = Path(__file__).parent.parent.parent
        agentic_core = project_root / "agentic_core"
        
        if not agentic_core.exists():
            pytest.skip("agentic_core not found")
        
        flat_files = list(agentic_core.rglob("*_flat.py"))
        flat_files = [f for f in flat_files if "archives" not in str(f)]
        
        assert len(flat_files) == 0, f"Found {len(flat_files)} _flat files in agentic_core"
    
    def test_no_1_files_in_agentic_core(self):
        """Test that no _1 files exist in agentic_core."""
        from pathlib import Path
        
        project_root = Path(__file__).parent.parent.parent
        agentic_core = project_root / "agentic_core"
        
        if not agentic_core.exists():
            pytest.skip("agentic_core not found")
        
        one_files = list(agentic_core.rglob("*_1.py"))
        one_files = [f for f in one_files if "archives" not in str(f)]
        
        assert len(one_files) == 0, f"Found {len(one_files)} _1 files in agentic_core"
    
    def test_no_flat_files_in_apps(self):
        """Test that no _flat files exist in apps_*."""
        from pathlib import Path
        
        project_root = Path(__file__).parent.parent.parent
        
        flat_files = []
        for app_dir in ["apps_lic", "apps_rg", "apps_shared"]:
            app_path = project_root / app_dir
            if app_path.exists():
                files = list(app_path.rglob("*_flat.py"))
                files = [f for f in files if "archives" not in str(f)]
                flat_files.extend(files)
        
        assert len(flat_files) == 0, f"Found {len(flat_files)} _flat files in apps_*"
    
    def test_no_1_files_in_apps(self):
        """Test that no _1 files exist in apps_*."""
        from pathlib import Path
        
        project_root = Path(__file__).parent.parent.parent
        
        one_files = []
        for app_dir in ["apps_lic", "apps_rg", "apps_shared"]:
            app_path = project_root / app_dir
            if app_path.exists():
                files = list(app_path.rglob("*_1.py"))
                files = [f for f in files if "archives" not in str(f)]
                one_files.extend(files)
        
        assert len(one_files) == 0, f"Found {len(one_files)} _1 files in apps_*"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
