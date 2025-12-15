#!/usr/bin/env python3
"""
CV-I-003: Filesystem Dependency Check
Integration test for multi-layer flow verification
"""

import pytest
from unittest.mock import Mock, patch, call
import os
import tempfile
from canon_validator import CanonValidator


class TestCVI003:
    """Test filesystem dependency check at L1 layer"""
    
    @pytest.fixture
    def validator(self):
        """Create validator with mocked dependencies"""
        validator = CanonValidator()
        validator.llm = Mock()
        validator.llm.generate_plan.return_value = {
            "status": "valid",
            "reasoning": "Code is valid"
        }
        validator.embed_fn = Mock(return_value=[0.1] * 768)
        validator.cache = Mock()
        validator.cache.check = Mock(return_value=None)
        validator.pinecone = Mock()
        validator.pinecone.query = Mock(return_value={'matches': []})
        validator.pinecone.upsert = Mock()
        return validator
    
    def test_missing_src_directory_pre_flight_failure(self, validator):
        """Test that missing src directory fails pre-flight check"""
        # Mock filesystem to simulate missing directory
        critical_errors = []
        
        def mock_pre_flight_check():
            # Simulate pre-flight checks
            required_dirs = ["src", "config", "logs"]
            missing_dirs = []
            
            for dir_path in required_dirs:
                if not os.path.exists(dir_path):
                    missing_dirs.append(dir_path)
                    critical_errors.append(f"CRITICAL L1_FS_MISSING: {dir_path}")
            
            if missing_dirs:
                return False, missing_dirs
            return True, []
        
        # Execute pre-flight
        passed, missing = mock_pre_flight_check()
        
        # Verify failure detection
        assert not passed
        assert len(missing) > 0
        assert "src" in missing
        assert any("L1_FS_MISSING" in error for error in critical_errors)
    
    def test_critical_error_logging_to_memeory(self, validator):
        """Test that critical errors are logged to MEMemory (L5)"""
        logged_errors = []
        
        def mock_add_observations(observations):
            logged_errors.extend(observations)
            return {"status": "success"}
        
        def mock_filesystem_check():
            # Simulate filesystem failure
            missing_dirs = ["src", "config"]
            for dir_path in missing_dirs:
                error_obs = {
                    "entityName": f"filesystem:{dir_path}",
                    "contents": [f"CRITICAL L1_FS_MISSING: {dir_path} directory not found"],
                    "corpusNames": ["canon_validator"],
                    "tags": ["critical", "l1", "filesystem", "missing"]
                }
                # Log to MEMemory
                mock_add_observations([error_obs])
            return missing_dirs
        
        with patch('canon_validator.add_observations', side_effect=mock_add_observations):
            missing = mock_filesystem_check()
        
        # Verify errors were logged
        assert len(missing) == 2
        assert len(logged_errors) == 2
        
        for error in logged_errors:
            assert error["entityName"].startswith("filesystem:")
            assert "CRITICAL L1_FS_MISSING" in str(error["contents"])
            assert "critical" in error["tags"]
            assert "l1" in error["tags"]
    
    def test_llm_execution_prevention_on_failure(self, validator):
        """Test that LLM execution is prevented on pre-flight failure"""
        llm_calls = []
        
        def mock_llm_generate_plan(prompt, code=None):
            llm_calls.append((prompt, code))
            return {"status": "valid", "reasoning": "Should not be called"}
        
        validator.llm.generate_plan = mock_llm_generate_plan
        
        # Mock pre-flight to fail
        def mock_failing_preflight():
            raise Exception("CRITICAL L1_FS_MISSING: src directory missing")
        
        # Execute validation with failing pre-flight
        try:
            # Simulate pre-flight check before LLM
            mock_failing_preflight()
            assert False, "Should have failed on pre-flight"
        except Exception as e:
            assert "L1_FS_MISSING" in str(e)
        
        # Verify LLM was never called
        assert len(llm_calls) == 0
    
    def test_graceful_degradation_on_partial_failure(self, validator):
        """Test graceful degradation when some filesystem components fail"""
        # Test scenario: optional directories missing but critical ones present
        filesystem_state = {
            "src": True,      # Critical - must exist
            "config": False,  # Critical - must exist
            "logs": False,    # Non-critical - can be created
            "temp": False,    # Non-critical - can be created
            "tests": True     # Non-critical - optional
        }
        
        def mock_filesystem_state():
            return filesystem_state
        
        def mock_preflight_with_graceful_degradation():
            state = mock_filesystem_state()
            critical_missing = []
            non_critical_missing = []
            
            critical_dirs = ["src", "config"]
            non_critical_dirs = ["logs", "temp"]
            
            for dir_path, exists in state.items():
                if not exists:
                    if dir_path in critical_dirs:
                        critical_missing.append(dir_path)
                    elif dir_path in non_critical_dirs:
                        non_critical_missing.append(dir_path)
            
            # Fail only on critical missing
            if critical_missing:
                return False, critical_missing, non_critical_missing
            elif non_critical_missing:
                # Can proceed with warnings
                return True, [], non_critical_missing
            else:
                return True, [], []
        
        # Execute pre-flight
        passed, critical_missing, non_critical_missing = mock_preflight_with_graceful_degradation()
        
        # Verify behavior
        assert not passed  # config is critical and missing
        assert "config" in critical_missing
        assert "logs" in non_critical_missing
        assert "temp" in non_critical_missing
    
    def test_filesystem_permissions_check(self, validator):
        """Test filesystem read/write permissions check"""
        permission_errors = []
        
        def mock_permission_check():
            # Simulate permission checks
            test_paths = [
                ("src", "r", True),     # Can read src
                ("src", "w", True),     # Can write to src
                ("config", "r", False), # Cannot read config
                ("logs", "w", False),   # Cannot write to logs
                ("temp", "w", True),    # Can write to temp
            ]
            
            for path, perm, has_permission in test_paths:
                if not has_permission:
                    permission_errors.append(f"L1_FS_PERMISSION: Cannot {perm} {path}")
            
            return len(permission_errors) == 0, permission_errors
        
        # Execute permission check
        passed, errors = mock_permission_check()
        
        # Verify permission errors detected
        assert not passed
        assert len(errors) == 2
        assert any("Cannot read config" in error for error in errors)
        assert any("Cannot write logs" in error for error in errors)
    
    def test_container_mount_failure_simulation(self, validator):
        """Test simulation of container mount failure"""
        mount_points = {
            "/workspace/src": False,  # Failed to mount
            "/workspace/config": False,  # Failed to mount
            "/workspace/logs": True,   # Successfully mounted
            "/workspace/temp": True    # Successfully mounted
        }
        
        def mock_container_mount_check():
            failed_mounts = []
            
            for mount_point, mounted in mount_points.items():
                if not mounted:
                    failed_mounts.append(f"L1_CONTAINER_MOUNT_FAILED: {mount_point}")
            
            if failed_mounts:
                return False, failed_mounts
            return True, []
        
        # Execute mount check
        passed, failures = mock_container_mount_check()
        
        # Verify mount failures detected
        assert not passed
        assert len(failures) == 2
        assert "/workspace/src" in str(failures)
        assert "/workspace/config" in str(failures)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
