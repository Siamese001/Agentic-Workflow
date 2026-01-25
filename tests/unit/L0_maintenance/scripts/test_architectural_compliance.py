"""
file: tests/unit/L0_maintenance/scripts/test_architectural_compliance.py
description: Aggressive testing of the audit tool to ensure zero false negatives.
"""

import ast
import os
import sys
import tempfile
import shutil

# Dynamic path resolution to import the script without installing it as a package
# Assuming we are running from project root
script_path = os.path.abspath("agentic_core/L0_maintenance/scripts")
sys.path.append(script_path)

# Verify import
try:
    from architectural_audit import DriftDetector, scan_repository
except ImportError:
    # Fallback for running pytest from within the tests directory
    sys.path.append(os.path.abspath("../../../../agentic_core/L0_maintenance/scripts"))
    from architectural_audit import DriftDetector, scan_repository


class TestDriftDetector:
    """
    Targeted tests to verify the AST visitor catches all forms of inheritance drift.
    100% Pass Rate Mandatory.
    """

    def test_detects_standard_inheritance(self):
        """Verify basic subclass detection."""
        source = "class BadAgent(L2Agent): pass"
        visitor = DriftDetector("test.py")
        visitor.visit(ast.parse(source))

        assert len(visitor.violations) == 1
        assert visitor.violations[0]["class"] == "BadAgent"
        assert visitor.violations[0]["detected"] == "L2Agent"

    def test_detects_aliased_import(self):
        """
        Verify detection survives aliasing.
        CRITICAL: Regex often fails here.
        """
        source = """
from legacy import L2Agent as BaseClass
class SneakyAgent(BaseClass):
    pass
        """
        visitor = DriftDetector("test.py")
        visitor.visit(ast.parse(source))

        assert len(visitor.violations) == 1
        assert visitor.violations[0]["class"] == "SneakyAgent"
        assert "alias of L2Agent" in visitor.violations[0]["detected"]

    def test_detects_dotted_path(self):
        """Verify detection of module.Class usage."""
        source = """
import agentic_core.L2_execution
class DirectReferenceAgent(agentic_core.L2_execution.L2Agent):
    pass
        """
        visitor = DriftDetector("test.py")
        visitor.visit(ast.parse(source))

        assert len(visitor.violations) == 1
        assert "L2Agent" in visitor.violations[0]["detected"]

    def test_broken_syntax_handling(self, capsys):
        """
        Verify that a file with broken syntax is reported as a SKIP/ERROR,
        not silently ignored.
        """
        tmp_dir = tempfile.mkdtemp()
        try:
            # Create a broken file
            with open(os.path.join(tmp_dir, "broken.py"), "w", encoding="utf-8") as f:
                f.write("class BrokenAgent(L2Agent:  # Missing parenthesis and syntax error")

            # Run scan on this directory - EXPECT EXIT CODE 1
            exit_code = scan_repository(tmp_dir)

            captured = capsys.readouterr()

            # Must return failure
            assert exit_code == 1, "Audit must fail on syntax errors"

            # Must output the specific error
            assert "[SKIP]" in captured.out
            assert "broken.py" in captured.out
            assert "[SYNTAX ERROR" in captured.out

        finally:
            shutil.rmtree(tmp_dir)

    def test_detects_unicode_failure(self, capsys):
        """
        Verify that files with bad encoding don't crash the scanner but are logged.
        """
        tmp_dir = tempfile.mkdtemp()
        try:
            # Create a file with bad byte sequence for UTF-8
            file_path = os.path.join(tmp_dir, "bad_encoding.py")
            with open(file_path, "wb") as f:
                f.write(b"\x80abc")  # Invalid start byte for UTF-8

            exit_code = scan_repository(tmp_dir)
            captured = capsys.readouterr()

            assert exit_code == 1
            assert "[SKIP]" in captured.out
            assert "[ENCODING ERROR]" in captured.out

        finally:
            shutil.rmtree(tmp_dir)
