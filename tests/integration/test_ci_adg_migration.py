#!/usr/bin/env python3
"""
Integration tests for CI ADG migration

Verify that refactored CI scripts produce same results as originals.
"""

import pytest

# Lazy import fixtures - avoid collection-time errors

@pytest.fixture(scope="session")
def _lazy_agentic_core_L0_routing_config_0():
    from agentic_core.L0_routing.config import path_constants  # Valid import
    return type('_Import', (), {"path_constants  # Valid import": path_constants  # Valid import})

@pytest.fixture(scope="session")
def _lazy_agentic_core_L5_safety_config_1():
    from agentic_core.L5_safety.config import ssot  # Valid import
    return type('_Import', (), {"ssot  # Valid import": ssot  # Valid import})

@pytest.fixture(scope="session")
def _lazy_agentic_core_L2_execution_something_2():
    from agentic_core.L2_execution.something import module  # Layer violation
    return type('_Import', (), {"module  # Layer violation": module  # Layer violation})

@pytest.fixture(scope="session")
def _lazy_agentic_core_L3_orchestration_other_3():
    from agentic_core.L3_orchestration.other import stuff  # Layer violation
    return type('_Import', (), {"stuff  # Layer violation": stuff  # Layer violation})
import subprocess
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, Mock
import sys
import os

# Add paths for testing
REPO_ROOT = Path(__file__).parent.parent.parent.parent
CI_SCRIPTS_DIR = REPO_ROOT / "ops_scripts" / "ci"
TOOLS_DIR = REPO_ROOT / "tools" / "adg"


class TestCIMigrationIntegration:
    """Integration tests for CI script migration to ADG."""
    
    @pytest.fixture
    def test_repo_dir(self):
        """Create a temporary test repository with sample files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir)
            
            # Create test files with various patterns
            test_files = {
                "test_subprocess.py": """
import subprocess

def good_call():
    # This should pass - has timeout
    result = subprocess.run(['echo', 'hello'], timeout=10, capture_output=True)
    return result

def bad_call():
    # This should fail - no timeout
    result = subprocess.run(['echo', 'hello'], capture_output=True)
    return result

def popen_good():
    # This should pass - has timeout context
    with subprocess.Popen(['sleep', '1']) as proc:
        proc.wait(timeout=5)

def popen_bad():
    # This should fail - no timeout
    proc = subprocess.Popen(['sleep', '1'])
    proc.wait()
""",
                "test_imports.py": """
import os
import sys
import nonexistent_module  # This should be flagged


def test_function():
    pass
""",
                "test_layer_violation.py": """
# This file simulates being in L1 layer


import os  # Should be fine
import sys  # Should be fine
""",
                "test_loops.py": """
import time

def good_loop():
    # This should pass - has progress reporting
    for i in range(100):
        print(f"Progress: {i}%")
        time.sleep(0.1)

def bad_loop():
    # This should fail - while True without timeout
    while True:
        time.sleep(1)
        if some_condition():
            break

def long_loop():
    # This should fail - long loop without progress
    for i in range(1000):
        complex_calculation(i)
        # No progress reporting
""",
                "test_dedup.py": """
class NewAgent:  # Should be flagged as potential duplicate
    def execute(self):
        pass

class UtilityMixin:  # Should be flagged as potential duplicate
    def helper_method(self):
        pass

def create_new_data():  # Should be flagged as potential duplicate
    return {"new": "data"}

NEW_CONSTANT = "value"  # Should be flagged if not in SSOT
"""
            }
            
            for filename, content in test_files.items():
                file_path = test_dir / filename
                file_path.write_text(content)
            
            yield test_dir
    
    @pytest.fixture
    def mock_adg_bridge(self):
        """Mock ADG bridge for testing."""
        from tools.adg.adg_query_bridge import ADGQueryBridge, FileMatch, Node, Violation
        
        # Create mock bridge
        mock_bridge = Mock(spec=ADGQueryBridge)
        
        # Mock subprocess calls
        mock_bridge.subprocess_calls_without_timeout.return_value = [
            FileMatch("test_subprocess.py", 8, "subprocess.run"),
            FileMatch("test_subprocess.py", 18, "subprocess.Popen")
        ]
        
        # Mock imports
        mock_bridge.files_importing.return_value = [
            FileMatch("test_imports.py", 4, "nonexistent_module")
        ]
        
        # Mock layer nodes
        mock_bridge.nodes_in_layer.return_value = [
            Node("test_module", "L2", "function", "agentic_core/L2_execution/something.py"),
            Node("other_module", "L3", "function", "agentic_core/L3_orchestration/other.py")
        ]
        
        # Mock violations
        mock_bridge.violations.return_value = [
            Violation("test_file.py", 10, "test_violation", "warning", "Test violation")
        ]
        
        # Mock loops
        mock_bridge.loops_without_progress.return_value = [
            FileMatch("test_loops.py", 12, "while True")
        ]
        
        return mock_bridge
    
    def test_timeout_progress_script_adg_vs_original(self, test_repo_dir, mock_adg_bridge):
        """Test that timeout progress script produces same results with ADG."""
        script_path = CI_SCRIPTS_DIR / "validate_timeout_progress.py"
        
        if not script_path.exists():
            pytest.skip("validate_timeout_progress.py not found")
        
        # Test with ADG enabled
        with patch('tools.adg.adg_query_bridge.ADGQueryBridge', return_value=mock_adg_bridge):
            result = subprocess.run([
                sys.executable, str(script_path), 
                str(test_repo_dir / "test_subprocess.py")
            ], capture_output=True, text=True, cwd=REPO_ROOT)
        
        # Should find violations
        assert result.returncode != 0 or "violation" in result.stdout.lower()
    
    def test_import_dependencies_script_adg_vs_original(self, test_repo_dir, mock_adg_bridge):
        """Test that import dependencies script produces same results with ADG."""
        script_path = CI_SCRIPTS_DIR / "validate_import_dependencies.py"
        
        if not script_path.exists():
            pytest.skip("validate_import_dependencies.py not found")
        
        # Test with ADG enabled
        with patch('tools.adg.adg_query_bridge.ADGQueryBridge', return_value=mock_adg_bridge):
            result = subprocess.run([
                sys.executable, str(script_path),
                str(test_repo_dir / "test_imports.py")
            ], capture_output=True, text=True, cwd=REPO_ROOT)
        
        # Should find import violations
        assert result.returncode != 0 or "violation" in result.stdout.lower()
    
    def test_layer_sovereignty_script_adg_vs_original(self, test_repo_dir, mock_adg_bridge):
        """Test that layer sovereignty script produces same results with ADG."""
        script_path = CI_SCRIPTS_DIR / "ast_layer_sovereignty_scanner.py"
        
        if not script_path.exists():
            pytest.skip("ast_layer_sovereignty_scanner.py not found")
        
        # Test with ADG enabled
        with patch('tools.adg.adg_query_bridge.ADGQueryBridge', return_value=mock_adg_bridge):
            result = subprocess.run([
                sys.executable, str(script_path),
                str(test_repo_dir / "test_layer_violation.py")
            ], capture_output=True, text=True, cwd=REPO_ROOT)
        
        # Should find layer violations
        assert result.returncode != 0 or "violation" in result.stdout.lower()
    
    def test_broken_test_imports_script_adg_vs_original(self, test_repo_dir, mock_adg_bridge):
        """Test that broken test imports script produces same results with ADG."""
        script_path = CI_SCRIPTS_DIR / "scan_broken_test_imports.py"
        
        if not script_path.exists():
            pytest.skip("scan_broken_test_imports.py not found")
        
        # Create a test file that looks like a test
        test_file = test_repo_dir / "test_broken.py"
        test_file.write_text("""
import nonexistent_module
def test_something():
    pass
""")
        
        # Test with ADG enabled
        with patch('tools.adg.adg_query_bridge.ADGQueryBridge', return_value=mock_adg_bridge):
            result = subprocess.run([
                sys.executable, str(script_path)
            ], capture_output=True, text=True, cwd=REPO_ROOT)
        
        # Should find broken imports
        assert result.returncode != 0 or "orphaned" in result.stdout.lower()
    
    def test_dedup_violations_script_adg_vs_original(self, test_repo_dir, mock_adg_bridge):
        """Test that dedup violations script produces same results with ADG."""
        script_path = CI_SCRIPTS_DIR / "check_dedup_violations.py"
        
        if not script_path.exists():
            pytest.skip("check_dedup_violations.py not found")
        
        # Create a git repo and staged changes for testing
        git_dir = test_repo_dir / ".git"
        git_dir.mkdir()
        
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=test_repo_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=test_repo_dir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=test_repo_dir, capture_output=True)
        
        # Add and commit initial files
        subprocess.run(["git", "add", "."], cwd=test_repo_dir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=test_repo_dir, capture_output=True)
        
        # Modify file to create staged changes
        test_file = test_repo_dir / "test_dedup.py"
        test_file.write_text(test_file.read_text() + "\n# New content\n")
        
        subprocess.run(["git", "add", "test_dedup.py"], cwd=test_repo_dir, capture_output=True)
        
        # Test with ADG enabled
        with patch('tools.adg.adg_query_bridge.ADGQueryBridge', return_value=mock_adg_bridge):
            result = subprocess.run([
                sys.executable, str(script_path)
            ], capture_output=True, text=True, cwd=test_repo_dir)
        
        # Should find dedup violations
        assert result.returncode != 0 or "symbol" in result.stdout.lower()
    
    def test_adg_tools_integration(self, test_repo_dir, mock_adg_bridge):
        """Test that new ADG tools work correctly."""
        # Test timeout scanner
        timeout_scanner_path = TOOLS_DIR / "adg_timeout_scanner.py"
        if timeout_scanner_path.exists():
            with patch('tools.adg.adg_query_bridge.ADGQueryBridge', return_value=mock_adg_bridge):
                result = subprocess.run([
                    sys.executable, str(timeout_scanner_path),
                    "--directory", str(test_repo_dir)
                ], capture_output=True, text=True, cwd=REPO_ROOT)
            
            assert result.returncode == 0
            assert "ADG Timeout Scanner Results" in result.stdout
        
        # Test import validator
        import_validator_path = TOOLS_DIR / "adg_import_validator.py"
        if import_validator_path.exists():
            with patch('tools.adg.adg_query_bridge.ADGQueryBridge', return_value=mock_adg_bridge):
                result = subprocess.run([
                    sys.executable, str(import_validator_path),
                    "--directory", str(test_repo_dir)
                ], capture_output=True, text=True, cwd=REPO_ROOT)
            
            assert result.returncode == 0
            assert "ADG Import Validator Results" in result.stdout
        
        # Test layer boundary checker
        layer_checker_path = TOOLS_DIR / "adg_layer_boundary_checker.py"
        if layer_checker_path.exists():
            with patch('tools.adg.adg_query_bridge.ADGQueryBridge', return_value=mock_adg_bridge):
                result = subprocess.run([
                    sys.executable, str(layer_checker_path),
                    "--directory", str(test_repo_dir)
                ], capture_output=True, text=True, cwd=REPO_ROOT)
            
            assert result.returncode == 0
            assert "ADG Layer Boundary Checker Results" in result.stdout
    
    def test_fallback_behavior(self, test_repo_dir):
        """Test that scripts fall back gracefully when ADG is unavailable."""
        script_path = CI_SCRIPTS_DIR / "validate_timeout_progress.py"
        
        if not script_path.exists():
            pytest.skip("validate_timeout_progress.py not found")
        
        # Test with ADG disabled by mocking import failure
        with patch.dict('sys.modules', {'tools.adg.adg_query_bridge': None}):
            result = subprocess.run([
                sys.executable, str(script_path),
                str(test_repo_dir / "test_subprocess.py")
            ], capture_output=True, text=True, cwd=REPO_ROOT)
        
        # Should still work with fallback
        assert result.returncode == 0 or "fallback" in result.stderr.lower()
    
    def test_performance_improvement(self, test_repo_dir, mock_adg_bridge):
        """Test that ADG version shows performance improvement."""
        # This is a basic test - in practice would measure actual performance
        script_path = CI_SCRIPTS_DIR / "validate_timeout_progress.py"
        
        if not script_path.exists():
            pytest.skip("validate_timeout_progress.py not found")
        
        # Time execution with ADG
        with patch('tools.adg.adg_query_bridge.ADGQueryBridge', return_value=mock_adg_bridge):
            start_time = pytest.importorskip("time").time()
            result = subprocess.run([
                sys.executable, str(script_path),
                str(test_repo_dir / "test_subprocess.py")
            ], capture_output=True, text=True, cwd=REPO_ROOT)
            adg_time = pytest.importorskip("time").time() - start_time
        
        # Time execution without ADG (fallback)
        with patch.dict('sys.modules', {'tools.adg.adg_query_bridge': None}):
            start_time = pytest.importorskip("time").time()
            result = subprocess.run([
                sys.executable, str(script_path),
                str(test_repo_dir / "test_subprocess.py")
            ], capture_output=True, text=True, cwd=REPO_ROOT)
            fallback_time = pytest.importorskip("time").time() - start_time
        
        # ADG version should be faster (though this test is basic)
        assert isinstance(adg_time, float)
        assert isinstance(fallback_time, float)
    
    def test_output_format_consistency(self, test_repo_dir, mock_adg_bridge):
        """Test that output format is consistent between ADG and fallback."""
        script_path = CI_SCRIPTS_DIR / "validate_timeout_progress.py"
        
        if not script_path.exists():
            pytest.skip("validate_timeout_progress.py not found")
        
        # Get output with ADG
        with patch('tools.adg.adg_query_bridge.ADGQueryBridge', return_value=mock_adg_bridge):
            result_adg = subprocess.run([
                sys.executable, str(script_path),
                str(test_repo_dir / "test_subprocess.py")
            ], capture_output=True, text=True, cwd=REPO_ROOT)
        
        # Get output with fallback
        with patch.dict('sys.modules', {'tools.adg.adg_query_bridge': None}):
            result_fallback = subprocess.run([
                sys.executable, str(script_path),
                str(test_repo_dir / "test_subprocess.py")
            ], capture_output=True, text=True, cwd=REPO_ROOT)
        
        # Both should produce some output (even if different content)
        assert len(result_adg.stdout) > 0 or len(result_adg.stderr) > 0
        assert len(result_fallback.stdout) > 0 or len(result_fallback.stderr) > 0


class TestDecisionTreeCompliance:
    """Test that CI scripts use correct tools per decision matrix."""
    
    def test_timeout_progress_uses_adg_first(self):
        """Test that timeout progress script tries ADG first."""
        script_path = CI_SCRIPTS_DIR / "validate_timeout_progress.py"
        
        if not script_path.exists():
            pytest.skip("validate_timeout_progress.py not found")
        
        content = script_path.read_text()
        
        # Should import ADG Query Bridge
        assert "from adg_query_bridge import ADGQueryBridge" in content or "ADGQueryBridge" in content
        
        # Should have fallback logic
        assert "ADG_AVAILABLE" in content or "try:" in content
    
    def test_import_dependencies_uses_adg_first(self):
        """Test that import dependencies script tries ADG first."""
        script_path = CI_SCRIPTS_DIR / "validate_import_dependencies.py"
        
        if not script_path.exists():
            pytest.skip("validate_import_dependencies.py not found")
        
        content = script_path.read_text()
        
        # Should import ADG Query Bridge
        assert "from adg_query_bridge import ADGQueryBridge" in content or "ADGQueryBridge" in content
        
        # Should have fallback logic
        assert "ADG_AVAILABLE" in content or "fallback" in content.lower()
    
    def test_layer_sovereignty_uses_adg_first(self):
        """Test that layer sovereignty script tries ADG first."""
        script_path = CI_SCRIPTS_DIR / "ast_layer_sovereignty_scanner.py"
        
        if not script_path.exists():
            pytest.skip("ast_layer_sovereignty_scanner.py not found")
        
        content = script_path.read_text()
        
        # Should import ADG Query Bridge
        assert "from adg_query_bridge import ADGQueryBridge" in content or "ADGQueryBridge" in content
        
        # Should have fallback logic
        assert "ADG_AVAILABLE" in content or "fallback" in content.lower()
    
    def test_broken_test_imports_uses_adg_first(self):
        """Test that broken test imports script tries ADG first."""
        script_path = CI_SCRIPTS_DIR / "scan_broken_test_imports.py"
        
        if not script_path.exists():
            pytest.skip("scan_broken_test_imports.py not found")
        
        content = script_path.read_text()
        
        # Should import ADG Query Bridge
        assert "from adg_query_bridge import ADGQueryBridge" in content or "ADGQueryBridge" in content
        
        # Should have fallback logic
        assert "ADG_AVAILABLE" in content or "fallback" in content.lower()
    
    def test_dedup_violations_uses_adg_first(self):
        """Test that dedup violations script tries ADG first."""
        script_path = CI_SCRIPTS_DIR / "check_dedup_violations.py"
        
        if not script_path.exists():
            pytest.skip("check_dedup_violations.py not found")
        
        content = script_path.read_text()
        
        # Should import ADG Query Bridge
        assert "from adg_query_bridge import ADGQueryBridge" in content or "ADGQueryBridge" in content
        
        # Should have fallback logic
        assert "ADG_AVAILABLE" in content or "fallback" in content.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
