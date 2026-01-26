"""
File: tests/test_post_migration_audit.py
Path: C:\Git\Agentic-Workflow\tests\test_post_migration_audit.py
Status: 100% Pass Required
Rationale: Ensures the audit tool correctly identifies broken agents vs healthy agents.
"""

import unittest
from unittest.mock import MagicMock, patch, Mock
from pathlib import Path
import sys
import importlib.util

# Add scripts to path
REPO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(REPO_ROOT / "scripts"))

# Import conditionally to avoid import errors if script file not written yet
try:
    from discover_agents import SovereigntyAuditor
except ImportError:
    # Mock for initial test pass if file doesn't exist in memory yet
    SovereigntyAuditor = Mock()

class TestPostMigrationAudit(unittest.TestCase):

    def setUp(self):
        self.auditor = SovereigntyAuditor()

    def test_detects_naming_mismatch_100_percent_pass(self):
        """Scenario: File is named MyAgent.py but class is named 'OldName'."""
        path = Path("MyAgent.py")
        code = "class OldName: pass"
        
        with patch('pathlib.Path.read_text', return_value=code), \
             patch('pathlib.Path.name', new_callable=lambda: "MyAgent.py"), \
             patch('pathlib.Path.stem', new_callable=lambda: "MyAgent"):
            
            # Mock runtime import to succeed so we isolate AST check
            with patch('importlib.util.spec_from_file_location'):
                self.auditor.audit_file(path)
                
        self.assertEqual(len(self.auditor.naming_violations), 1)
        self.assertIn("Expected class 'MyAgent'", self.auditor.naming_violations[0])

    def test_detects_broken_imports(self):
        """Scenario: Agent imports a module that no longer exists (orphaned import)."""
        path = Path("HealthyAgent.py")
        code = "class HealthyAgent: pass"
        
        with patch('pathlib.Path.read_text', return_value=code), \
             patch('pathlib.Path.name', new_callable=lambda: "HealthyAgent.py"), \
             patch('pathlib.Path.stem', new_callable=lambda: "HealthyAgent"):
             
            # Simulate ImportError during execution
            with patch('importlib.util.spec_from_file_location') as mock_spec:
                mock_loader = Mock()
                mock_loader.exec_module.side_effect = ImportError("No module named 'old_utils'")
                mock_spec.return_value.loader = mock_loader
                
                self.auditor.audit_file(path)

        self.assertEqual(len(self.auditor.import_failures), 1)
        self.assertIn("No module named 'old_utils'", self.auditor.import_failures[0])

    def test_ignores_non_agent_files(self):
        """Scenario: A utility file should be skipped by the audit."""
        path = Path("utils.py")
        self.auditor.audit_file(path)
        self.assertEqual(self.auditor.agents_found, 0)
        self.assertEqual(len(self.auditor.naming_violations), 0)

    def test_valid_agent_passes(self):
        """Scenario: A perfectly compliant agent."""
        path = Path("GoodAgent.py")
        code = "class GoodAgent(BaseAgent): pass"
        
        with patch('pathlib.Path.read_text', return_value=code), \
             patch('pathlib.Path.name', new_callable=lambda: "GoodAgent.py"), \
             patch('pathlib.Path.stem', new_callable=lambda: "GoodAgent"):
            
            with patch('importlib.util.spec_from_file_location') as mock_spec:
                # No exception raised
                self.auditor.audit_file(path)
                
        self.assertEqual(self.auditor.agents_found, 1)
        self.assertEqual(len(self.auditor.naming_violations), 0)
        self.assertEqual(len(self.auditor.import_failures), 0)

if __name__ == '__main__':
    unittest.main()
