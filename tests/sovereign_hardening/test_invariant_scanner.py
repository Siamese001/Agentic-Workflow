"""Tests for System Invariant Scanner - bypass detection."""

import pytest
import ast
import tempfile
from pathlib import Path

from agentic_core.L5_safety.static_checks.system_invariant_scanner import (
    SystemInvariantScanner,
    BypassViolation,
    scan_repository_for_bypasses,
    print_bypass_report,
    get_bypass_scan_summary
)


class TestSystemInvariantScanner:
    """Tests for bypass detection scanner."""

    def test_gateway_bypass_detection(self):
        """Test detection of direct file operations (gateway bypass)."""
        # Create test file with direct file operations
        test_code = """
import os

def bad_function():
    # Direct file write - should be flagged
    with open("test.txt", "w") as f:
        f.write("content")

    # Direct file removal - should be flagged
    os.remove("old_file.txt")

    # Allowlisted operation with comment - should not be flagged
    with open("allowed.txt", "w") as f:  # guardian: allow-direct-write
        f.write("allowed")
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_path = Path(f.name)

        try:
            scanner = SystemInvariantScanner(temp_path)
            tree = ast.parse(test_code)
            scanner.visit(tree)

            violations = scanner.violations
            assert len(violations) >= 2

            # Check for specific violations
            violation_rules = [v.rule_id for v in violations]
            assert "GATEWAY_BYPASS" in violation_rules

        finally:
            temp_path.unlink()

    def test_provider_bypass_detection(self):
        """Test detection of direct provider SDK calls."""
        test_code = """
import openai
from anthropic import Anthropic

def bad_llm_call():
    # Direct OpenAI call - should be flagged
    client = openai.Client()
    response = client.chat.completions.create(...)

    # Direct Anthropic call - should be flagged
    anthropic = Anthropic()
    response = anthropic.messages.create(...)
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_path = Path(f.name)

        try:
            scanner = SystemInvariantScanner(temp_path)
            tree = ast.parse(test_code)
            scanner.visit(tree)

            violations = scanner.violations
            assert len(violations) >= 2

            # Check for provider bypass violations
            violation_rules = [v.rule_id for v in violations]
            assert "PROVIDER_BYPASS" in violation_rules

        finally:
            temp_path.unlink()

    def test_embedding_bypass_detection(self):
        """Test detection of direct embedding operations."""
        test_code = """
from sentence_transformers import SentenceTransformer
import openai

def bad_embedding():
    # Direct embedding model - should be flagged
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(['text'])

    # Direct OpenAI embeddings - should be flagged
    client = openai.Client()
    embeddings = client.embeddings.create(...)
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_path = Path(f.name)

        try:
            scanner = SystemInvariantScanner(temp_path)
            tree = ast.parse(test_code)
            scanner.visit(tree)

            violations = scanner.violations

            # Should detect both import and usage violations
            violation_rules = [v.rule_id for v in violations]
            assert "PROVIDER_BYPASS" in violation_rules or "EMBEDDING_BYPASS" in violation_rules

        finally:
            temp_path.unlink()

    def test_allowlisted_modules_not_flagged(self):
        """Test that allowlisted modules are not flagged."""
        test_code = """
from agentic_core.L2_execution.UniversalWriteGateway import get_write_gateway
from agentic_core.L2_execution.healers.healing_provider_adapters import HealingProviderInvoker
from system_learning.engines.embedding_service_factory import EmbeddingServiceFactory

def good_function():
    gateway = get_write_gateway()
    gateway.record_mutation("test.txt", "write", "content")

    factory = EmbeddingServiceFactory.get_or_disabled()
    embeddings = factory.get_embeddings(["text"])
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_path = Path(f.name)

        try:
            scanner = SystemInvariantScanner(temp_path)
            tree = ast.parse(test_code)
            scanner.visit(tree)

            violations = scanner.violations
            # Should not have violations for allowlisted modules
            provider_violations = [v for v in violations if v.rule_id == "PROVIDER_BYPASS"]
            embedding_violations = [v for v in violations if v.rule_id == "EMBEDDING_BYPASS"]

            assert len(provider_violations) == 0, f"Unexpected provider violations: {provider_violations}"
            assert len(embedding_violations) == 0, f"Unexpected embedding violations: {embedding_violations}"

        finally:
            temp_path.unlink()

    def test_allowlist_comment_bypass(self):
        """Test that allowlist comments prevent violations."""
        test_code = """
def function_with_allowlist():
    # This should be allowed due to comment
    with open("test.txt", "w") as f:  # guardian: allow-direct-write
        f.write("content")

    # This should also be allowed
    os.remove("old.txt")  # guardian: allow-file-operation
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_path = Path(f.name)

        try:
            scanner = SystemInvariantScanner(temp_path)
            tree = ast.parse(test_code)
            scanner.visit(tree)

            violations = scanner.violations
            # Should not have violations due to allowlist comments
            gateway_violations = [v for v in violations if v.rule_id == "GATEWAY_BYPASS"]
            assert len(gateway_violations) == 0

        finally:
            temp_path.unlink()

    def test_repository_scan(self):
        """Test scanning a repository structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            good_file = temp_path / "good.py"
            good_file.write_text("""
def good_function():
    return "no violations here"
""")

            bad_file = temp_path / "bad.py"
            bad_file.write_text("""
import openai

def bad_function():
    with open("test.txt", "w") as f:
        f.write("bad")
    client = openai.Client()
    return client
""")

            # Scan repository
            violations = scan_repository_for_bypasses(temp_path)

            # Should find violations in bad.py but not good.py
            assert len(violations) > 0

            bad_violations = [v for v in violations if "bad.py" in v.file_path]
            good_violations = [v for v in violations if "good.py" in v.file_path]

            assert len(bad_violations) > 0
            assert len(good_violations) == 0

    def test_violation_sorting(self):
        """Test that violations are sorted deterministically."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create files in non-alphabetical order
            files = ["z_file.py", "a_file.py", "m_file.py"]
            for filename in files:
                file_path = temp_path / filename
                file_path.write_text("""
import openai
with open("test.txt", "w") as f:
    f.write("content")
""")

            violations = scan_repository_for_bypasses(temp_path)

            # Check that violations are sorted by file path, then line, then rule
            file_paths = [v.file_path for v in violations]
            assert file_paths == sorted(file_paths)

    def test_scan_summary(self):
        """Test bypass scan summary generation."""
        violations = [
            BypassViolation("file1.py", 10, "GATEWAY_BYPASS", "open()", "Direct file operation"),
            BypassViolation("file1.py", 20, "PROVIDER_BYPASS", "openai", "Direct provider call"),
            BypassViolation("file2.py", 5, "GATEWAY_BYPASS", "os.remove", "Direct file removal"),
        ]

        summary = get_bypass_scan_summary(violations)

        assert summary["total_violations"] == 3
        assert summary["by_rule"]["GATEWAY_BYPASS"] == 2
        assert summary["by_rule"]["PROVIDER_BYPASS"] == 1
        assert summary["files_affected"] == 2
        assert len(summary["files_affected_list"]) == 2

    def test_no_violations_report(self):
        """Test report generation when no violations found."""
        violations = []

        # Should not raise exception
        print_bypass_report(violations)

        summary = get_bypass_scan_summary(violations)
        assert summary["total_violations"] == 0
        assert summary["files_affected"] == 0

    def test_syntax_error_handling(self):
        """Test handling of syntax errors during scanning."""
        test_code = """
def broken_function(
    # Missing closing parenthesis - syntax error
    pass
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_path = Path(f.name)

        try:
            violations = scan_repository_for_bypasses(temp_path.parent)

            # Should find syntax error violation
            syntax_violations = [v for v in violations if v.rule_id == "SYNTAX_ERROR"]
            assert len(syntax_violations) > 0

        finally:
            temp_path.unlink()

    @pytest.mark.sovereignty
    def test_comprehensive_bypass_detection(self):
        """Comprehensive test for all bypass types (marked for sovereignty)."""
        test_code = """
import openai
import os
from sentence_transformers import SentenceTransformer
from pathlib import Path

def comprehensive_bypass():
    # Gateway bypasses
    with open("file1.txt", "w") as f:
        f.write("content")
    os.remove("file2.txt")
    Path("file3.txt").write_text("content")

    # Provider bypasses
    client = openai.Client()
    response = client.chat.completions.create(...)

    # Embedding bypasses
    model = SentenceTransformer('model')
    embeddings = model.encode(['text'])
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_path = Path(f.name)

        try:
            violations = scan_repository_for_bypasses(temp_path.parent)

            # Should detect multiple types of violations
            violation_types = set(v.rule_id for v in violations)

            # At least one of each type should be detected
            assert len(violation_types) >= 2, "Should detect multiple bypass types"

        finally:
            temp_path.unlink()
