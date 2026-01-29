"""
File: tests/unit/agentic_core/L0_maintenance/test_ssot_documentation_consistency.py
Description: Enforces that the Operational Runbook matches the actual code implementation.
Mandate: 100% Pass.
"""

import pytest
import re
from pathlib import Path

# Define paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
README_PATH = PROJECT_ROOT / "agentic_core" / "L0_maintenance" / "EXECUTE_SSOT_README.md"
SCRIPT_PATH = PROJECT_ROOT / "agentic_core" / "L0_maintenance" / "scripts" / "execute_ssot.py"


class TestDocumentationConsistency:
    @pytest.fixture
    def documented_flags(self):
        """Parses the README to extract documented CLI flags."""
        if not README_PATH.exists():
            pytest.fail(f"Runbook not found at {README_PATH}")

        content = README_PATH.read_text(encoding="utf-8")
        # Regex to find flags like `--territory` or `--dry-run` in table or text
        # This pattern handles flags with or without parameters
        flags = set(re.findall(r"`(--[a-zA-Z0-9-]+)(?:\s+<[^>]+>)?`", content))
        return flags

    @pytest.fixture
    def implemented_flags(self):
        """Introspects the script's argparse setup to find actual flags."""
        captured_flags = set()

        # We need to parse the script to extract argparse calls
        if not SCRIPT_PATH.exists():
            pytest.fail(f"Script not found at {SCRIPT_PATH}")

        script_content = SCRIPT_PATH.read_text(encoding="utf-8")

        # Find all add_argument calls with flag arguments
        add_argument_pattern = r'add_argument\s*\(\s*[\'"](--[a-zA-Z0-9-]+)[\'"]'
        matches = re.findall(add_argument_pattern, script_content)
        captured_flags.update(matches)

        # Also look for argument lists with multiple flags
        multi_flag_pattern = r"add_argument\s*\(\s*\[([^\]]+)\]"
        multi_matches = re.findall(multi_flag_pattern, script_content)

        for match in multi_matches:
            # Extract individual flags from the list
            flags = re.findall(r'[\'"](--[a-zA-Z0-9-]+)[\'"]', match)
            captured_flags.update(flags)

        return captured_flags

    def test_critical_flags_documented(self, documented_flags):
        """
        Critical: Verify essential safety flags are in the Runbook.
        """
        critical_flags = {"--dry-run", "--max-budget", "--territory"}
        missing = critical_flags - documented_flags
        assert not missing, f"Critical flags missing from Runbook: {missing}"

    def test_implementation_matches_documentation(self, documented_flags, implemented_flags):
        """
        Critical: Verify that every flag in the code is documented in the README.
        (Prevent hidden/undocumented dangerous flags).
        """
        # We allow some standard flags like --help or --version to be skipped
        ignored = {"--help", "--version"}

        undocumented = (implemented_flags - ignored) - documented_flags

        # Note: If this fails, it means you added a new flag to the code but forgot the README.
        assert not undocumented, (
            f"Found UNDOCUMENTED flags in code: {undocumented}. Update EXECUTE_SSOT_README.md."
        )

    def test_runbook_step_consistency(self):
        """
        Critical: Verify the Runbook steps reference valid scripts.
        """
        content = README_PATH.read_text(encoding="utf-8")

        # Check Step 1 references execute_ssot.py
        assert "scripts/execute_ssot.py" in content, (
            "Runbook Step 1 missing execute script reference"
        )

        # Check Step 2 references verify_manifest.py
        assert "scripts/verify_manifest.py" in content, (
            "Runbook Step 2 missing verify script reference"
        )

    def test_documentation_exists(self):
        """
        Critical: Verify the operational manual exists.
        """
        assert README_PATH.exists(), f"Operational manual missing at {README_PATH}"

        content = README_PATH.read_text(encoding="utf-8")
        assert len(content) > 1000, "Operational manual appears to be empty or too short"

    def test_safety_sections_documented(self):
        """
        Critical: Verify safety architecture is documented.
        """
        content = README_PATH.read_text(encoding="utf-8")

        required_sections = ["Safety Architecture", "Budget Gate", "Cycle Gate", "Confidence Gate"]

        for section in required_sections:
            assert section in content, f"Required safety section missing: {section}"

    def test_troubleshooting_section_exists(self):
        """
        Critical: Verify troubleshooting guidance is available.
        """
        content = README_PATH.read_text(encoding="utf-8")
        assert "Troubleshooting" in content, "Troubleshooting section missing"

        # Check for common issues
        assert "Agent not found" in content, "Missing troubleshooting for agent discovery"
        assert "fix was skipped" in content, "Missing troubleshooting for skipped fixes"
