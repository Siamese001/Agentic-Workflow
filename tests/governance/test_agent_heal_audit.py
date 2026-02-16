#!/usr/bin/env python3
"""
Tests for Agent Healing Audit - CI-Grade Determinism

Phase 1, Wave 1.3: Strict deterministic tests
- Byte-identical JSON verification
- Structure contract validation
- Enumeration integrity testing
- No runtime import verification
"""

import ast
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

# Test fixtures
TEST_FIXTURE_CONTENT = '''
"""Test fixture for agent scanning."""

class TestAgent:
    """Test agent with both methods."""

    def heal(self):
        pass

    def heal_repository(self):
        pass

class PartialAgent:
    """Test agent with only heal method."""

    def heal(self):
        pass

class MissingAgent:
    """Test agent with no healing methods."""
    pass

class NotAgentClass:
    """Not an agent - doesn't end with Agent."""
    pass
'''

EXPECTED_SCHEMA_KEYS = {"audit_results", "summary"}

EXPECTED_RESULT_KEYS = {
    "repo_relative_path",
    "class_name",
    "has_heal",
    "has_heal_repository",
    "base_class_names",
}

EXPECTED_SUMMARY_KEYS = {"total_agents", "missing_heal", "missing_heal_repository", "missing_both"}


def run_audit_cli(format_type: str = "json", out_path: Path | None = None) -> dict[str, Any]:
    """Run the audit CLI and return parsed output."""
    cmd = [
        sys.executable,
        "-m",
        "agentic_core.L5_safety.enforcement.governance.agent_heal_audit",
        "--format",
        format_type,
    ]

    if out_path:
        cmd.extend(["--out", str(out_path)])

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

    if result.returncode != 0:
        pytest.fail(f"Audit CLI failed: {result.stderr}")

    if format_type == "json":
        return json.loads(result.stdout)
    else:
        return {"stdout": result.stdout}


@pytest.mark.governance
class TestDeterminism:
    """Test determinism of audit output."""

    def test_byte_identical_json_runs(self, tmp_path):
        """Test that consecutive runs produce byte-identical JSON."""
        # Run audit twice
        result1 = run_audit_cli()
        result2 = run_audit_cli()

        # Convert to JSON strings with sorted keys
        json1 = json.dumps(result1, sort_keys=True)
        json2 = json.dumps(result2, sort_keys=True)

        # Assert byte-identical
        assert json1 == json2, "JSON output not byte-identical across runs"

    def test_deterministic_ordering(self):
        """Test that output ordering is deterministic."""
        result = run_audit_cli()

        # Check audit_results ordering
        results = result["audit_results"]
        paths = [agent["repo_relative_path"] for agent in results]
        classes = [agent["class_name"] for agent in results]

        # Should be sorted by path, then class
        sorted_pairs = sorted(zip(paths, classes), key=lambda x: (x[0], x[1]))
        expected_paths = [pair[0] for pair in sorted_pairs]
        expected_classes = [pair[1] for pair in sorted_pairs]

        assert paths == expected_paths, "Results not sorted by path"
        assert classes == expected_classes, "Results not sorted by class within path"

    def test_no_nondeterministic_fields(self):
        """Test that no timestamps, UUIDs, or environment-dependent fields exist."""
        result = run_audit_cli()

        # Convert to string and check for common nondeterministic patterns
        result_str = json.dumps(result, sort_keys=True)

        nondeterministic_patterns = [
            "timestamp",
            "uuid",
            "time.",
            "date.",
            "random",
            "pid",
            "hostname",
            "environment",
        ]

        for pattern in nondeterministic_patterns:
            assert pattern.lower() not in result_str.lower(), f"Found nondeterministic field: {pattern}"


@pytest.mark.governance
class TestStructureContract:
    """Test that output structure matches expected schema."""

    def test_top_level_schema(self):
        """Test top-level JSON schema."""
        result = run_audit_cli()

        # Check exact keys (no extra allowed)
        assert set(result.keys()) == EXPECTED_SCHEMA_KEYS, (
            f"Unexpected top-level keys: {set(result.keys()) - EXPECTED_SCHEMA_KEYS}"
        )

    def test_result_item_schema(self):
        """Test schema of individual audit result items."""
        result = run_audit_cli()

        for item in result["audit_results"]:
            # Check exact keys (no extra allowed)
            actual_keys = set(item.keys())
            assert actual_keys == EXPECTED_RESULT_KEYS, (
                f"Unexpected result keys: {actual_keys - EXPECTED_RESULT_KEYS}"
            )

            # Check data types
            assert isinstance(item["repo_relative_path"], str)
            assert isinstance(item["class_name"], str)
            assert isinstance(item["has_heal"], bool)
            assert isinstance(item["has_heal_repository"], bool)
            assert isinstance(item["base_class_names"], list)

            # Check base_class_names content
            for base in item["base_class_names"]:
                assert isinstance(base, str)

    def test_summary_schema(self):
        """Test summary schema."""
        result = run_audit_cli()
        summary = result["summary"]

        # Check exact keys (no extra allowed)
        assert set(summary.keys()) == EXPECTED_SUMMARY_KEYS, (
            f"Unexpected summary keys: {set(summary.keys()) - EXPECTED_SUMMARY_KEYS}"
        )

        # Check data types and values
        for key, value in summary.items():
            assert isinstance(value, int)
            assert value >= 0, f"Summary value {key} should be non-negative"

        # Check logical consistency
        assert summary["total_agents"] >= summary["missing_heal"]
        assert summary["total_agents"] >= summary["missing_heal_repository"]
        assert summary["total_agents"] >= summary["missing_both"]
        assert summary["missing_both"] <= summary["missing_heal"]
        assert summary["missing_both"] <= summary["missing_heal_repository"]


@pytest.mark.governance
class TestEnumerationIntegrity:
    """Test accuracy of AST enumeration."""

    def test_controlled_fixture_scanning(self, tmp_path):
        """Test scanning of controlled fixture file."""
        # Create test fixture
        fixture_file = tmp_path / "test_fixture.py"
        fixture_file.write_text(TEST_FIXTURE_CONTENT)

        # Import and use scanner directly
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from agentic_core.L5_safety.enforcement.governance.agent_heal_audit import AgentHealAuditScanner

        scanner = AgentHealAuditScanner(tmp_path)
        results = scanner.scan_agent_file(fixture_file)

        # Should find exactly 3 agents (TestAgent, PartialAgent, MissingAgent)
        assert len(results) == 3, f"Expected 3 agents, found {len(results)}"

        # Check TestAgent
        test_agent = next(r for r in results if r["class_name"] == "TestAgent")
        assert test_agent["has_heal"] is True
        assert test_agent["has_heal_repository"] is True
        assert test_agent["base_class_names"] == []  # No base classes in fixture

        # Check PartialAgent
        partial_agent = next(r for r in results if r["class_name"] == "PartialAgent")
        assert partial_agent["has_heal"] is True
        assert partial_agent["has_heal_repository"] is False

        # Check MissingAgent
        missing_agent = next(r for r in results if r["class_name"] == "MissingAgent")
        assert missing_agent["has_heal"] is False
        assert missing_agent["has_heal_repository"] is False

    def test_agent_naming_detection(self):
        """Test that only classes ending with 'Agent' are detected."""
        result = run_audit_cli()

        for item in result["audit_results"]:
            class_name = item["class_name"]
            assert class_name.endswith("Agent"), f"Class {class_name} doesn't end with 'Agent'"

    def test_base_class_name_extraction(self):
        """Test that base class names are correctly extracted."""
        result = run_audit_cli()

        for item in result["audit_results"]:
            base_classes = item["base_class_names"]
            assert isinstance(base_classes, list)

            # Should be sorted deterministically
            assert base_classes == sorted(base_classes), f"Base classes not sorted for {item['class_name']}"


@pytest.mark.governance
class TestNoRuntimeImports:
    """Test that audit module doesn't import runtime modules."""

    def test_source_code_imports(self):
        """Inspect source code for forbidden imports."""
        audit_file = (
            Path(__file__).parent.parent.parent
            / "agentic_core"
            / "L5_safety"
            / "enforcement"
            / "governance"
            / "agent_heal_audit.py"
        )
        source = audit_file.read_text()

        # Parse AST to find imports
        tree = ast.parse(source)

        forbidden_patterns = ["agentic_core", "apps_lic", "apps_rg", "apps_shared"]

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    for pattern in forbidden_patterns:
                        if alias.name.startswith(pattern):
                            pytest.fail(f"Found forbidden import: {alias.name}")

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for pattern in forbidden_patterns:
                        if node.module.startswith(pattern):
                            pytest.fail(f"Found forbidden import from: {node.module}")

    def test_stdlib_only_imports(self):
        """Verify only standard library imports are used."""
        audit_file = (
            Path(__file__).parent.parent.parent
            / "agentic_core"
            / "L5_safety"
            / "enforcement"
            / "governance"
            / "agent_heal_audit.py"
        )
        source = audit_file.read_text()

        # Parse AST to find imports
        tree = ast.parse(source)

        allowed_stdlib_modules = {"argparse", "ast", "json", "sys", "pathlib", "typing"}

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split(".")[0]
                    if module_name not in allowed_stdlib_modules:
                        pytest.fail(f"Non-stdlib import found: {alias.name}")

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_name = node.module.split(".")[0]
                    if module_name not in allowed_stdlib_modules:
                        pytest.fail(f"Non-stdlib import from: {node.module}")


@pytest.mark.governance
class TestMarkdownGeneration:
    """Test markdown report generation."""

    def test_markdown_generation(self, tmp_path):
        """Test markdown file generation."""
        output_file = tmp_path / "test_report.md"

        # Generate markdown
        run_audit_cli("md", Path(output_file))

        # Check file exists
        assert output_file.exists(), "Markdown file not generated"

        # Check content structure
        content = output_file.read_text()

        # Should contain required sections
        assert "# Agent Healing Audit Report" in content
        assert "## Summary" in content
        assert "## Detailed Results" in content
        assert "| Path | Class | heal | heal_repository |" in content

        # Should contain summary numbers
        assert "Total Agents" in content
        assert "Missing heal()" in content
        assert "Missing heal_repository()" in content

    def test_markdown_determinism(self, tmp_path):
        """Test that markdown generation is deterministic."""
        output_file1 = tmp_path / "test_report1.md"
        output_file2 = tmp_path / "test_report2.md"

        # Generate twice
        run_audit_cli("md", Path(output_file1))
        run_audit_cli("md", Path(output_file2))

        # Compare content
        content1 = output_file1.read_text()
        content2 = output_file2.read_text()

        assert content1 == content2, "Markdown output not deterministic"
