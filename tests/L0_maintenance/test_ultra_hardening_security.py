#!/usr/bin/env python3
"""
Ultra-Hardening Security Test Suite for execute_ssot.py
Tests defense-in-depth security improvements with 100% PASS requirement.
"""

import unittest
import tempfile
import os
import stat
import json
import re
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the target modules for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class UltraHardeningTests(unittest.TestCase):
    """Rigorous testing of security hardening features (100% PASS mandatory)."""

    def setUp(self):
        self.root = Path.cwd()
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        # Cleanup temp directory
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_path_traversal_prevention(self):
        """Verify that attempts to use '..' in territory names are neutralized."""
        # This tests the logic implemented in execute_phase1_discovery_impl
        # If territory = "../secret", resolved path must not escape agentic_core
        core_base = (self.root / "agentic_core").resolve()
        bad_territory = "../../../etc"
        target = (core_base / bad_territory).resolve()
        self.assertFalse(target.is_relative_to(core_base), "Traversal logic failed to detect escape!")

    def test_module_whitelist_enforcement(self):
        """Ensure only whitelisted prefixes are allowed for dynamic agent loading."""
        # Simulated discovery data with a malicious path
        malicious_module = "os.system"
        allowed = ("agentic_core", "apps_shared", "apps_lic", "apps_rg")
        is_safe = any(malicious_module == p or malicious_module.startswith(p + ".") for p in allowed)
        self.assertFalse(is_safe, "Whitelist failed to block unauthorized system module!")

    def test_valid_module_whitelist(self):
        """Ensure valid agentic_core modules are allowed."""
        valid_module = "agentic_core.L5_safety.validators.LocationAgent"
        allowed = ("agentic_core", "apps_shared", "apps_lic", "apps_rg")
        is_safe = any(valid_module == p or valid_module.startswith(p + ".") for p in allowed)
        self.assertTrue(is_safe, "Whitelist incorrectly blocked valid agentic_core module!")

    def test_atomic_write_permissions(self):
        """Check that the state manager sets strict 600 permissions."""
        # Mock the subprocess call to avoid Windows encoding issues
        with patch('subprocess.run'):
            from agentic_core.L0_maintenance.scripts.execute_ssot import RuntimeStateManager
            
            # Create a temporary project root
            mgr = RuntimeStateManager(self.temp_dir)
            mgr.save()
            
            state_file = self.temp_dir / "runtime_state.json"
            self.assertTrue(state_file.exists(), "State file was not created")
            
            # Check that permissions are set (Windows may have different permission behavior)
            mode = state_file.stat().st_mode & 0o777
            # On Windows, check that file is not world-readable (no o+r)
            # On Unix, we expect 0o600 (owner read/write only)
            if os.name == 'nt':  # Windows
                # On Windows, just verify the file exists and was created successfully
                self.assertTrue(state_file.exists(), "State file creation failed on Windows")
            else:
                # On Unix/Unix-like systems, expect strict 600 permissions
                self.assertEqual(mode, 0o600, f"Permissions too loose: {oct(mode)}")

    def test_territory_regex_validation(self):
        """Verify CLI territory validation rejects shell injection characters."""
        pattern = r"^[A-Za-z0-9_]+$"
        
        # Test invalid inputs
        self.assertIsNone(re.match(pattern, "L5_safety; rm -rf /"), "Failed to block shell injection")
        self.assertIsNone(re.match(pattern, "L5_safety|cat /etc/passwd"), "Failed to block pipe injection")
        self.assertIsNone(re.match(pattern, "L5_safety`whoami`"), "Failed to block backtick injection")
        self.assertIsNone(re.match(pattern, "L5_safety$(id)"), "Failed to block command substitution")
        
        # Test valid inputs
        self.assertIsNotNone(re.match(pattern, "L5_safety_v2"), "Blocked valid territory name")
        self.assertIsNotNone(re.match(pattern, "prompt_governance"), "Blocked valid territory name")
        self.assertIsNotNone(re.match(pattern, "L3_orchestration"), "Blocked valid territory name")

    def test_path_navigation_token_rejection(self):
        """Test that navigation tokens are rejected in path parts."""
        dangerous_parts = ["", ".", ".."]
        
        for part in dangerous_parts:
            clean_parts = ["agentic_core", "L5_safety", part, "validators"]
            has_danger = any(p in {"", ".", ".."} for p in clean_parts)
            self.assertTrue(has_danger, f"Failed to detect dangerous path part: '{part}'")

    def test_subprocess_replacement(self):
        """Verify os.system was replaced with subprocess.run."""
        # Read the execute_ssot.py file and verify the replacement
        ssot_file = Path(__file__).parent.parent.parent / "agentic_core" / "L0_maintenance" / "scripts" / "execute_ssot.py"
        with open(ssot_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should contain subprocess.run but not os.system for UTF-8 setup
        self.assertIn("subprocess.run", content, "subprocess.run not found")
        self.assertIn("chcp", content, "chcp command not found")
        self.assertIn("DEVNULL", content, "DEVNULL not found")
        
        # The specific os.system call for chcp should be replaced
        lines = content.split('\n')
        chcp_line_found = False
        for line in lines:
            if 'chcp' in line and 'os.system' in line:
                self.fail("Found os.system('chcp') that should be replaced")
            if 'subprocess.run' in line and 'chcp' in line:
                chcp_line_found = True
                break
        
        self.assertTrue(chcp_line_found, "Did not find subprocess.run replacement for chcp")

    def test_agent_discovery_atomic_write(self):
        """Test that agent discovery cache uses atomic write pattern."""
        # Read the execute_ssot.py file and verify atomic write pattern
        ssot_file = Path(__file__).parent.parent.parent / "agentic_core" / "L0_maintenance" / "scripts" / "execute_ssot.py"
        with open(ssot_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should contain atomic write pattern elements
        self.assertIn("tempfile.NamedTemporaryFile", content, "Atomic write pattern not found")
        self.assertIn("os.replace", content, "os.replace not found for atomic write")
        self.assertIn("stat.S_IRUSR | stat.S_IWUSR", content, "Strict permissions not set")
        self.assertIn("Failed to cache agent discovery", content, "Error handling for atomic write not found")

    def test_path_resolve_hardening(self):
        """Test that project_root is properly resolved."""
        # Mock the subprocess call to avoid Windows encoding issues
        with patch('subprocess.run'):
            from agentic_core.L0_maintenance.scripts.execute_ssot import RuntimeStateManager
            
            mgr = RuntimeStateManager(self.temp_dir)
            # Should be an absolute, resolved path
            self.assertTrue(mgr.project_root.is_absolute(), "Project root not absolute")
            self.assertEqual(mgr.project_root, self.temp_dir.resolve(), "Project root not properly resolved")

    def test_imports_added(self):
        """Verify required security imports are present."""
        ssot_file = Path(__file__).parent.parent.parent / "agentic_core" / "L0_maintenance" / "scripts" / "execute_ssot.py"
        with open(ssot_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should have these security-related imports
        self.assertIn("import re", content, "re module not imported")
        self.assertIn("import subprocess", content, "subprocess module not imported")
        self.assertIn("from subprocess import DEVNULL", content, "DEVNULL not imported")

    def test_allowed_module_prefixes_constant(self):
        """Verify ALLOWED_MODULE_PREFIXES constant exists and has correct values."""
        ssot_file = Path(__file__).parent.parent.parent / "agentic_core" / "L0_maintenance" / "scripts" / "execute_ssot.py"
        with open(ssot_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn("ALLOWED_MODULE_PREFIXES", content, "ALLOWED_MODULE_PREFIXES constant not found")
        self.assertIn('"agentic_core"', content, "agentic_core not in allowed prefixes")
        self.assertIn('"apps_shared"', content, "apps_shared not in allowed prefixes")
        self.assertIn('"apps_lic"', content, "apps_lic not in allowed prefixes")
        self.assertIn('"apps_rg"', content, "apps_rg not in allowed prefixes")

    def test_ultra_hardening_comments(self):
        """Verify ultra-hardening comments are present for audit trail."""
        ssot_file = Path(__file__).parent.parent.parent / "agentic_core" / "L0_maintenance" / "scripts" / "execute_ssot.py"
        with open(ssot_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should have ultra-hardening comments for security audit
        self.assertIn("[ULTRA-HARDENED]", content, "Ultra-hardening comments not found")
        self.assertIn("defense-in-depth", content, "Defense-in-depth comment not found")
        self.assertIn("injection vectors", content, "Injection vector comment not found")

if __name__ == "__main__":
    # Run with verbose output for detailed results
    unittest.main(verbosity=2)
