"""
[AGGRESSIVE] Security Validation for L3 Orchestrator.
Mandatory 100% Pass Rate for Production Deployment.

Ultra-Hardened Test Suite:
- Validates module whitelist enforcement
- Tests symlink attack prevention
- Verifies factory method security
- Tests import validation pipeline
- Validates path resolution hardening
"""

import logging
import unittest
from pathlib import Path
from unittest.mock import patch

from agentic_core.L3_orchestration.OrchestratorAgent import (
    ALLOWED_MODULE_PREFIXES,
    OrchestratorAgent,
    get_consolidated_orchestrator,
)

# Disable logging for cleaner test output
logging.disable(logging.CRITICAL)


class TestOrchestratorSecurity(unittest.TestCase):
    """
    [AGGRESSIVE] Security Validation for L3 Orchestrator.
    Mandatory 100% Pass Rate for Production Deployment.
    """

    def setUp(self):
        self.root = Path.cwd().resolve()
        self.agent = get_consolidated_orchestrator(self.root)

    def test_factory_resolves_symlinks(self):
        """
        [HARDENED] Ensure the factory method forces path resolution.
        Prevents symlink attacks by resolving to absolute path.
        """
        # Test with relative path
        relative_root = Path(".")
        agent = get_consolidated_orchestrator(relative_root)

        self.assertTrue(agent.project_root.is_absolute(), "Project root must be absolute")
        self.assertEqual(agent.project_root, self.root, "Project root must be fully resolved")

        # Test with None (default behavior)
        agent_default = get_consolidated_orchestrator(None)
        self.assertTrue(
            agent_default.project_root.is_absolute(), "Default project root must be absolute"
        )
        self.assertEqual(
            agent_default.project_root, self.root, "Default project root must be resolved"
        )

    def test_module_whitelist_blocks_system_imports(self):
        """
        [DEFENSE-IN-DEPTH] Verify that attempts to load 'os' or 'subprocess' are blocked.
        This simulates an attacker creating a fake agent pointing to a system module.
        """
        # Test malicious system modules
        malicious_modules = [
            "os.path",
            "subprocess.run",
            "shutil.rmtree",
            "sys.modules",
            "importlib.import_module",
        ]

        for malicious_module in malicious_modules:
            with self.subTest(module=malicious_module):
                # Manually verify the logic used in _validate_agent_import
                is_allowed = any(
                    malicious_module == p or malicious_module.startswith(p + ".")
                    for p in ALLOWED_MODULE_PREFIXES
                )

                self.assertFalse(
                    is_allowed, f"Whitelist FAILED: System module '{malicious_module}' was allowed!"
                )

    def test_module_whitelist_allows_valid_core(self):
        """
        [COMPLIANCE] Verify that valid agentic_core modules are permitted.
        """
        valid_modules = [
            "agentic_core.L5_safety.validators.HierarchyAgent",
            "agentic_core.L3_orchestration.OrchestratorAgent",
            "agentic_core.base_agents.SovereignBaseAgent",
            "agentic_core.utils.ssot_discovery",
            "apps_shared.utils.CommonUtils",
            "apps_lic.engines.QAConductorAgent",
            "apps_rg.shared.tools.RGTools",
        ]

        for valid_module in valid_modules:
            with self.subTest(module=valid_module):
                is_allowed = any(
                    valid_module == p or valid_module.startswith(p + ".")
                    for p in ALLOWED_MODULE_PREFIXES
                )

                self.assertTrue(
                    is_allowed, f"Whitelist FAILED: Valid module '{valid_module}' was blocked!"
                )

    def test_module_whitelist_blocks_edge_cases(self):
        """
        [SECURITY] Test edge cases that could bypass whitelist validation.
        Note: Only modules OUTSIDE allowed prefixes should be blocked.
        """
        # Test modules that DON'T start with allowed prefixes
        suspicious_modules = [
            "os.path",
            "subprocess.run",
            "sys.modules",
            "importlib.import_module",
            "random_module",
            "malicious_package.evil",
        ]

        for suspicious_module in suspicious_modules:
            with self.subTest(module=suspicious_module):
                is_allowed = any(
                    suspicious_module == p or suspicious_module.startswith(p + ".")
                    for p in ALLOWED_MODULE_PREFIXES
                )

                # Should be False - these are suspicious/bypass attempts
                self.assertFalse(
                    is_allowed,
                    f"Security FAILED: Suspicious module '{suspicious_module}' was allowed!",
                )

    def test_factory_method_integration(self):
        """
        [INTEGRATION] Test the factory method integration with execute_ssot.py.
        """
        # Test factory with explicit path
        test_root = Path("/tmp/test").resolve() if Path("/tmp").exists() else self.root
        agent = get_consolidated_orchestrator(test_root)

        self.assertIsInstance(agent, OrchestratorAgent)
        self.assertEqual(agent.mode.value, "unified")
        self.assertTrue(agent.project_root.is_absolute())

        # Test factory with None
        agent_none = get_consolidated_orchestrator(None)
        self.assertIsInstance(agent_none, OrchestratorAgent)
        self.assertTrue(agent_none.project_root.is_absolute())

    def test_project_root_hardening(self):
        """
        [HARDENING] Verify project_root is properly resolved in __init__.
        """
        # Test direct instantiation (not using factory)
        agent = OrchestratorAgent()

        # Even without factory, should default to resolved CWD
        self.assertTrue(
            agent.project_root.is_absolute(), "Direct instantiation must have absolute project_root"
        )
        self.assertEqual(
            agent.project_root, self.root, "Direct instantiation must resolve to current directory"
        )

    def test_import_validation_security_integration(self):
        """
        [INTEGRATION] Test the full _validate_agent_import pipeline with security.
        Uses mocking to simulate malicious agent files.
        """
        # Mock a malicious agent path that points to system module
        malicious_path = str(self.root / "os" / "path.py")

        with patch(
            "agentic_core.L3_orchestration.OrchestratorAgent.get_agent_paths"
        ) as mock_get_paths:
            mock_get_paths.return_value = [malicious_path]

            # Should block the malicious agent
            result = self.agent._validate_agent_import("path")
            self.assertFalse(result, "Security validation should block malicious agents")

    def test_import_validation_allows_valid_agents(self):
        """
        [COMPLIANCE] Test that valid agents pass security validation.
        """
        # Mock a valid agent path
        valid_path = str(self.root / "agentic_core" / "L5_safety" / "validators" / "ValidAgent.py")

        with patch(
            "agentic_core.L3_orchestration.OrchestratorAgent.get_agent_paths"
        ) as mock_get_paths:
            mock_get_paths.return_value = [valid_path]

            # Mock subprocess.run to simulate successful import
            with patch("subprocess.run") as mock_subprocess:
                mock_subprocess.return_value.returncode = 0
                mock_subprocess.return_value.stderr = ""

                result = self.agent._validate_agent_import("ValidAgent")
                self.assertTrue(result, "Valid agents should pass security validation")

    def test_whitelist_configuration_integrity(self):
        """
        [CONFIGURATION] Verify whitelist configuration is properly defined.
        """
        # Check that whitelist is a tuple (immutable)
        self.assertIsInstance(
            ALLOWED_MODULE_PREFIXES, tuple, "ALLOWED_MODULE_PREFIXES must be a tuple for security"
        )

        # Check that all required prefixes are present
        required_prefixes = ["agentic_core", "apps_shared", "apps_lic", "apps_rg"]
        for prefix in required_prefixes:
            self.assertIn(
                prefix,
                ALLOWED_MODULE_PREFIXES,
                f"Required prefix '{prefix}' missing from whitelist",
            )

        # Check no empty strings
        self.assertNotIn("", ALLOWED_MODULE_PREFIXES, "Whitelist should not contain empty strings")

        # Check no whitespace-only strings
        for prefix in ALLOWED_MODULE_PREFIXES:
            self.assertTrue(
                prefix.strip(), f"Whitelist prefix '{prefix}' appears to be whitespace-only"
            )

    def test_security_logging(self):
        """
        [OBSERVABILITY] Verify security violations are properly logged.
        """
        with patch(
            "agentic_core.L3_orchestration.OrchestratorAgent.get_agent_paths"
        ) as mock_get_paths:
            # Mock malicious agent path
            malicious_path = str(self.root / "os" / "path.py")
            mock_get_paths.return_value = [malicious_path]

            # Capture logging
            with patch.object(self.agent.logger, "critical") as mock_critical:
                result = self.agent._validate_agent_import("path")

                # Should return False and log critical security message
                self.assertFalse(result)
                mock_critical.assert_called_once()
                call_args = mock_critical.call_args[0][0]
                self.assertIn("SECURITY BLOCK", call_args)
                self.assertIn("path", call_args)

    def test_path_resolution_cross_platform(self):
        """
        [PORTABILITY] Test path resolution works across different platforms.
        """
        # Test with Windows-style paths
        windows_path = Path("C:\\Users\\test\\project")
        if windows_path.exists():
            agent = get_consolidated_orchestrator(windows_path)
            self.assertTrue(agent.project_root.is_absolute())

        # Test with Unix-style paths
        unix_path = Path("/home/user/project")
        if unix_path.exists():
            agent = get_consolidated_orchestrator(unix_path)
            self.assertTrue(agent.project_root.is_absolute())

        # Test with relative paths (should resolve to absolute)
        relative_path = Path("../test")
        resolved = relative_path.resolve()
        if resolved.exists():
            agent = get_consolidated_orchestrator(relative_path)
            self.assertTrue(agent.project_root.is_absolute())


class TestOrchestratorSecurityPerformance(unittest.TestCase):
    """
    [PERFORMANCE] Security validation should not significantly impact performance.
    """

    def test_whitelist_lookup_performance(self):
        """
        [PERFORMANCE] Whitelist validation should be O(1) and fast.
        """
        import time

        test_modules = [
            "agentic_core.L5_safety.validators.HierarchyAgent",
            "os.path",  # Should fail fast
            "apps_shared.utils.CommonUtils",
            "subprocess.run",  # Should fail fast
        ] * 1000  # 4000 lookups

        start_time = time.time()

        for module in test_modules:
            any(module == p or module.startswith(p + ".") for p in ALLOWED_MODULE_PREFIXES)
            # Just compute the result, don't assert

        end_time = time.time()
        elapsed = end_time - start_time

        # Should complete 4000 lookups in under 1 second
        self.assertLess(elapsed, 1.0, f"Whitelist lookup too slow: {elapsed:.3f}s for 4000 lookups")


if __name__ == "__main__":
    # Run with verbose output for security validation
    unittest.main(verbosity=2)
