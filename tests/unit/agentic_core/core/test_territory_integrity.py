import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to path for imports
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent  # Go up 3 levels from tests/unit/ to project root
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from agentic_core.L5_safety.validators.core.hierarchy_agent import HierarchyAgent
except (ImportError, NameError, AttributeError, TypeError) as e:
    print(f"Import error: {e}")
    print(f"Project root: {project_root}")
    print(f"Sys path: {sys.path[:3]}")  # Show first 3 paths
    raise


class TestTerritoryIntegrity(unittest.TestCase):
    """Ultra-hardened testing for territory root violation detection."""

    def setUp(self):
        """Set up test environment with temporary directory structure."""
        self.tmp = Path(tempfile.mkdtemp())
        self.project_root = self.tmp
        self.target = self.tmp / "agentic_core" / "prompt_governance"
        self.target.mkdir(parents=True)

        # Create some root squatter files
        (self.target / "stray_prompt.py").write_text("class Stray: pass")
        (self.target / "readme.md").write_text("# Info")
        (self.target / "config.json").write_text('{"setting": true}')

        # Create legitimate subfolders
        (self.target / "meta_prompts").mkdir()
        (self.target / "templates").mkdir()
        (self.target / "scripts").mkdir()
        (self.target / "version_registry").mkdir()
        (self.target / "agents").mkdir()
        (self.target / "registry").mkdir()

        # Create allowed files
        (self.target / "__init__.py").write_text("")
        (self.target / ".gitkeep").write_text("")

    def tearDown(self):
        """Clean up temporary directory."""
        if self.tmp.exists():
            shutil.rmtree(self.tmp)

    def test_detection_of_root_files(self):
        """Test 1: Verify all files in territory root are flagged as STRUCTURE violations."""
        agent = HierarchyAgent(project_root=self.tmp)
        report = agent.scan_root_violations(target_territory="prompt_governance")

        # Should detect 3 squatter files (.py, .md, .json) but not __init__.py or .gitkeep
        self.assertEqual(
            len(report["territory_root_files"]), 3, "Should detect exactly 3 squatter files"
        )
        self.assertEqual(report["violations_found"], 3, "Should report 3 violations found")

        # Verify violation structure
        violation_names = [v["file"] for v in report["territory_root_files"]]
        self.assertIn("stray_prompt.py", violation_names, "Should detect .py squatter")
        self.assertIn("readme.md", violation_names, "Should detect .md squatter")
        self.assertIn("config.json", violation_names, "Should detect .json squatter")

        print("✅ PASS: Root File Detection")

    def test_json_payload_format(self):
        """Test 2: Verify violation dict contains required keys for execute_ssot JSON merge."""
        agent = HierarchyAgent(project_root=self.tmp)
        violations = agent.scan_root_violations("prompt_governance")["territory_root_files"]

        # Check first violation has all required keys
        violation = violations[0]
        required_keys = ["type", "file", "message", "severity", "path", "territory"]
        for key in required_keys:
            self.assertIn(key, violation, f"Missing required key: {key}")

        # Verify specific values
        self.assertEqual(violation["type"], "STRUCTURE", "Type should be STRUCTURE")
        self.assertEqual(violation["severity"], "ERROR", "Severity should be ERROR")
        self.assertEqual(violation["territory"], "prompt_governance", "Territory should be correct")
        self.assertIn(
            "sitting in prompt_governance root",
            violation["message"],
            "Message should be descriptive",
        )

        print("✅ PASS: JSON Payload Integrity")

    def test_empty_territory_grace(self):
        """Test 3: Verify no false positives in a clean room."""
        # Remove all squatter files
        (self.target / "stray_prompt.py").unlink()
        (self.target / "readme.md").unlink()
        (self.target / "config.json").unlink()

        agent = HierarchyAgent(project_root=self.tmp)
        report = agent.scan_root_violations("prompt_governance")

        self.assertEqual(
            len(report["territory_root_files"]), 0, "Should detect no violations in clean territory"
        )
        self.assertEqual(report["violations_found"], 0, "Should report 0 violations found")

        print("✅ PASS: Clean Room Certification")

    def test_non_existent_territory(self):
        """Test 4: Verify resilience when a non-existent territory is audited."""
        agent = HierarchyAgent(project_root=self.tmp)
        report = agent.scan_root_violations("fake_zone")

        self.assertIn("errors", report, "Should include errors key for non-existent territory")
        self.assertEqual(len(report["errors"]), 1, "Should have exactly one error")
        self.assertIn(
            "not found", report["errors"][0], "Error message should mention path not found"
        )

        print("✅ PASS: Failure Resilience")

    def test_ultra_scan_logging(self):
        """Test 5: Verify ultra scan produces correct logging output."""
        import io
        import logging

        # Capture log output
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger("agentic_core.L5_safety.validators.HierarchyAgent")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        try:
            agent = HierarchyAgent(project_root=self.tmp)
            agent.scan_root_violations("prompt_governance")

            log_output = log_capture.getvalue()
            self.assertIn("ULTRA SCAN", log_output, "Should log ultra scan message")
            self.assertIn("prompt_governance", log_output, "Should mention territory name")
            self.assertIn("TERRITORY ROOT FILE", log_output, "Should log specific violations")

        finally:
            logger.removeHandler(handler)

        print("✅ PASS: Ultra Scan Logging")

    def test_backwards_compatibility(self):
        """Test 6: Verify original project root scanning still works."""
        # Create some project root violations
        (self.tmp / "coverage_html").mkdir()
        (self.tmp / "test.archived").write_text("backup")

        agent = HierarchyAgent(project_root=self.tmp)

        # Test without target_territory (original behavior)
        report = agent.scan_root_violations()

        # Should detect project root violations
        self.assertGreater(report["violations_found"], 0, "Should detect project root violations")
        self.assertIn("forbidden_folders", report, "Should include forbidden_folders key")

        print("✅ PASS: Backwards Compatibility")

    def test_approved_subfolders_ignored(self):
        """Test 7: Verify files in approved subfolders are NOT flagged."""
        # Create files in approved subfolders
        (self.target / "meta_prompts" / "persona.py").write_text("class Persona: pass")
        (self.target / "templates" / "template.j2").write_text("Hello {{name}}")
        (self.target / "agents" / "TestAgent.py").write_text("class TestAgent: pass")

        agent = HierarchyAgent(project_root=self.tmp)
        report = agent.scan_root_violations("prompt_governance")

        # Should still only detect the 3 root squatters, not the files in subfolders
        self.assertEqual(
            len(report["territory_root_files"]),
            3,
            "Should only detect root files, not subfolder files",
        )

        # Verify violation names don't include subfolder files
        violation_names = [v["file"] for v in report["territory_root_files"]]
        self.assertNotIn("persona.py", violation_names, "Should not flag files in meta_prompts")
        self.assertNotIn("template.j2", violation_names, "Should not flag files in templates")
        self.assertNotIn("TestAgent.py", violation_names, "Should not flag files in agents")

        print("✅ PASS: Approved Subfolders Ignored")

    def test_multiple_territories_isolation(self):
        """Test 8: Verify territory scanning is properly isolated."""
        # Create another territory with squatters
        other_target = self.tmp / "agentic_core" / "other_territory"
        other_target.mkdir(parents=True)
        (other_target / "other_squatter.py").write_text("class Other: pass")

        agent = HierarchyAgent(project_root=self.tmp)

        # Scan prompt_governance only
        report_pg = agent.scan_root_violations("prompt_governance")

        # Scan other_territory only
        report_other = agent.scan_root_violations("other_territory")

        # Each should only detect violations in their own territory
        self.assertEqual(
            len(report_pg["territory_root_files"]), 3, "prompt_governance should have 3 violations"
        )
        self.assertEqual(
            len(report_other["territory_root_files"]), 1, "other_territory should have 1 violation"
        )

        # Verify territory names are correct
        for violation in report_pg["territory_root_files"]:
            self.assertEqual(violation["territory"], "prompt_governance")

        for violation in report_other["territory_root_files"]:
            self.assertEqual(violation["territory"], "other_territory")

        print("✅ PASS: Multiple Territories Isolation")


if __name__ == "__main__":
    print("🧪 Running Ultra-Hardened Territory Integrity Tests")
    print("=" * 60)
    unittest.main(verbosity=2)
