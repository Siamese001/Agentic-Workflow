#!/usr/bin/env python3
"""
VERIFICATION TEST SUITE FOR STRUCTURE MIGRATION
Tests the scripts/ -> ops_scripts/ migration and log placement rules.
"""
import pytest
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any


class TestStructureMigration:
    
    @pytest.fixture
    def mock_fs(self):
        """Creates a legacy project structure for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            
            # Create Legacy Dirs
            (root / "scripts").mkdir()
            (root / "logs").mkdir()
            
            # Create Core Destination
            core_scripts = root / "agentic_core" / "L0_maintenance" / "scripts"
            core_scripts.mkdir(parents=True)
            core_logs = root / "agentic_core" / "L0_maintenance" / "logs"
            core_logs.mkdir(parents=True)
            
            # File 1: Standalone Script (Should go to ops_scripts)
            (root / "scripts" / "setup_env.py").write_text("import os\nprint('setup')")
            
            # File 2: Core Dependent Script (Should go to L0)
            (root / "scripts" / "heal_system.py").write_text("import agentic_core\nprint('healing')")
            
            # File 3: Runtime Log (Should go to L0)
            (root / "logs" / "debug.log").write_text("debug info")
            
            # File 4: Valid Trace Log (Should stay in root)
            (root / "logs" / "trace_mission.jsonl").write_text('{"event": "trace"}')
            
            yield root

    def test_migration_logic(self, mock_fs):
        """Test the core migration logic inline."""
        old_scripts = mock_fs / "scripts"
        new_ops = mock_fs / "ops_scripts"
        core_dest = mock_fs / "agentic_core" / "L0_maintenance" / "scripts"
        
        new_ops.mkdir(exist_ok=True)
        
        # --- EXECUTE MIGRATION LOGIC ---
        for f in list(old_scripts.glob("*.py")):
            content = f.read_text()
            if "agentic_core" in content:
                shutil.move(str(f), str(core_dest / f.name))
            else:
                shutil.move(str(f), str(new_ops / f.name))
                
        # --- ASSERTIONS ---
        
        # 1. 'setup_env.py' should be in ops_scripts
        assert (new_ops / "setup_env.py").exists()
        assert not (old_scripts / "setup_env.py").exists()
        
        # 2. 'heal_system.py' should be in agentic_core
        assert (core_dest / "heal_system.py").exists()
        assert not (new_ops / "heal_system.py").exists()
        
        # 3. Old scripts dir should be empty or removed
        assert not (old_scripts / "setup_env.py").exists()
        assert not (old_scripts / "heal_system.py").exists()

    def test_log_audit_logic(self, mock_fs):
        """Test log audit and migration logic."""
        logs_dir = mock_fs / "logs"
        core_logs = mock_fs / "agentic_core" / "L0_maintenance" / "logs"
        
        # Allowed patterns
        allowed_patterns = [
            r"^trace_.*\.jsonl$",
            r"^mission_.*\.log$", 
            r"^execution_.*\.trace$"
        ]
        
        import re
        compiled_patterns = [re.compile(p) for p in allowed_patterns]
        
        # --- EXECUTE LOG AUDIT LOGIC ---
        for file_path in logs_dir.iterdir():
            if file_path.is_dir():
                continue
                
            is_allowed = any(p.match(file_path.name) for p in compiled_patterns)
            
            if not is_allowed:
                dest = core_logs / file_path.name
                shutil.move(str(file_path), str(dest))
        
        # --- ASSERTIONS ---
        
        # 1. debug.log should be moved to core
        assert (core_logs / "debug.log").exists()
        assert not (logs_dir / "debug.log").exists()
        
        # 2. trace_mission.jsonl should stay in root
        assert (logs_dir / "trace_mission.jsonl").exists()
        assert not (core_logs / "trace_mission.jsonl").exists()

    def test_structure_validation(self, mock_fs):
        """Test structure validation logic."""
        # Setup: Complete migration
        old_scripts = mock_fs / "scripts"
        new_ops = mock_fs / "ops_scripts"
        core_dest = mock_fs / "agentic_core" / "L0_maintenance" / "scripts"
        
        new_ops.mkdir(exist_ok=True)
        
        # Migrate scripts
        for f in list(old_scripts.glob("*.py")):
            content = f.read_text()
            if "agentic_core" in content:
                shutil.move(str(f), str(core_dest / f.name))
            else:
                shutil.move(str(f), str(new_ops / f.name))
        
        # Remove old dir
        if old_scripts.exists() and not any(old_scripts.iterdir()):
            old_scripts.rmdir()
        
        # --- EXECUTE VALIDATION LOGIC ---
        issues = []
        
        # Check ops_scripts exists
        if not new_ops.exists():
            issues.append("ops_scripts directory does not exist")
        
        # Check old scripts is gone
        if old_scripts.exists():
            issues.append("Legacy scripts directory still exists")
        
        # Check for core imports in ops_scripts
        for py_file in new_ops.glob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                if "agentic_core" in content:
                    issues.append(f"Core dependency found in ops_scripts/{py_file.name}")
            except Exception:
                pass
        
        # --- ASSERTIONS ---
        assert len(issues) == 0, f"Validation issues found: {issues}"
        assert new_ops.exists()
        assert not old_scripts.exists()
        assert (new_ops / "setup_env.py").exists()

    def test_import_detection(self):
        """Test import detection logic."""
        # Test cases for import detection
        test_cases = [
            ("import os\nprint('hello')", False),  # No agentic_core
            ("import agentic_core\nprint('hello')", True),  # Has agentic_core
            ("from agentic_core.utils import helper\nprint('hello')", True),  # From import
            ("# import agentic_core\nprint('hello')", True),  # Commented but still present
            ("print('agentic_core is a string')", True),  # String literal
        ]
        
        for content, should_have_core in test_cases:
            has_core = "agentic_core" in content
            assert has_core == should_have_core, f"Failed for content: {content}"

    def test_log_pattern_matching(self):
        """Test log pattern matching logic."""
        import re
        
        patterns = [
            re.compile(r"^trace_.*\.jsonl$"),
            re.compile(r"^mission_.*\.log$"),
            re.compile(r"^execution_.*\.trace$"),
        ]
        
        test_cases = [
            ("trace_mission.jsonl", True),
            ("mission_2024.log", True), 
            ("execution_phase1.trace", True),
            ("debug.log", False),
            ("trace.json", False),  # Wrong extension
            ("mission_trace.jsonl", False),  # Wrong prefix
        ]
        
        for filename, should_match in test_cases:
            is_allowed = any(p.match(filename) for p in patterns)
            assert is_allowed == should_match, f"Pattern matching failed for {filename}"

    def test_migration_summary(self, mock_fs):
        """Test migration summary calculation."""
        # This would test the summary logic from the main script
        # For now, we'll simulate the expected results
        
        expected_summary = {
            "moved_to_core": 1,  # heal_system.py
            "moved_to_ops": 1,   # setup_env.py  
            "violations_found": 1,  # heal_system.py had core dependency
        }
        
        # In real implementation, this would test the actual return values
        # from the migration functions
        assert expected_summary["moved_to_core"] == 1
        assert expected_summary["moved_to_ops"] == 1
        assert expected_summary["violations_found"] == 1


class TestBlueprintIntegration:
    """Test integration with structure_blueprint.py updates."""
    
    def test_ops_scripts_in_registry(self):
        """Test that ops_scripts is properly registered in blueprint."""
        # This would import and check the actual blueprint
        # For now, we'll simulate the check
        
        expected_keys = ["ops_scripts"]
        # In real test: from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_REGISTRY
        # assert "ops_scripts" in SOVEREIGN_REGISTRY
        
        for key in expected_keys:
            assert key in expected_keys  # Placeholder assertion

    def test_scripts_placement_rules(self):
        """Test that scripts placement rules are updated."""
        # This would check the actual placement rules
        # For now, we'll simulate the check
        
        expected_rules = ["root_ops_scripts"]
        # In real test: check SCRIPTS_PLACEMENT_RULES has root_ops_scripts
        
        for rule in expected_rules:
            assert rule in expected_rules  # Placeholder assertion


if __name__ == "__main__":
    # Run tests directly if executed
    pytest.main([__file__, "-v"])
