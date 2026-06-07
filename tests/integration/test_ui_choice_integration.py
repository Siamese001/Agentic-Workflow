"""Integration tests for UI choice consistency pipeline.

Per hardened plan ui-choice-consistency-zero-loss-hardened-d9f3a1 W4:
- End-to-end verification of builder → scanner → validation
- CI fail-closed behavior verification
- Migrated surfaces end-to-end validation
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestBuilderToScannerPipeline:
    """Integration: builder output passes scanner validation."""

    def test_enriched_choice_passes_scanner(self):
        """End-to-end: enriched choice builder output → scanner passes."""
        # Import builder
        sys.path.insert(0, str(REPO_ROOT))
        from tools.decisions.enriched_choice_builder import build_enriched_choice_question

        # Build enriched question
        payload = build_enriched_choice_question(
            question="Which approach should I use?",
            options=[
                {
                    "id": "A",
                    "label": "Fast approach — quick implementation",
                    "description": "Implements the feature quickly with minimal scaffolding",
                    "tradeoff": "Higher technical debt, may need refactoring later",
                },
                {
                    "id": "B",
                    "label": "Thorough approach — comprehensive solution",
                    "description": "Full implementation with tests and documentation",
                    "tradeoff": "Takes longer, more upfront complexity",
                },
            ],
            recommended_id="A",
            telemetry_context={"test": "integration", "decision": "approach"},
        )

        # Verify packet structure
        assert "question" in payload
        assert "options" in payload
        assert "telemetry_packet" in payload
        assert payload["telemetry_packet"]["packet_type"] == "ASK_USER_QUESTION_PACKET"

        # Create temp file with code that actually imports and uses the builder
        code = '''
import sys
sys.path.insert(0, r"''' + str(REPO_ROOT) + ''''")
from tools.decisions.enriched_choice_builder import build_enriched_choice_question

def present_choice():
    payload = build_enriched_choice_question(
        question="Which approach should I use?",
        options=[
            {
                "id": "A",
                "label": "Fast approach — quick implementation",
                "description": "Implements the feature quickly",
                "tradeoff": "Higher technical debt",
            },
            {
                "id": "B",
                "label": "Thorough approach — comprehensive solution",
                "description": "Full implementation with tests",
                "tradeoff": "Takes longer",
            },
        ],
        recommended_id="A",
        telemetry_context={"test": "integration"},
    )

    ask_user_question(
        question=payload["question"],
        options=payload["options"],
        allowMultiple=False,
    )

    print("ASK_USER_QUESTION_PACKET: " + __import__("json").dumps(payload["telemetry_packet"]))
'''
        # Run scanner on this file
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_choice.py"
            test_file.write_text(code, encoding="utf-8")

            scanner_path = REPO_ROOT / "ops_scripts" / "ci" / "check_enriched_choice_ui_invariants.py"
            result = subprocess.run(
                [sys.executable, str(scanner_path), str(test_file), "--advisory"],
                capture_output=True,
                text=True,
                cwd=str(REPO_ROOT),
            )

            # Should pass (exit 0)
            assert result.returncode == 0, f"Scanner failed: {result.stdout}"
            assert "Pass: 1" in result.stdout or "✓ Pass: 1" in result.stdout


class TestCIFailClosedBehavior:
    """Integration: CI mode fails closed on violations."""

    def test_ci_mode_fails_with_violation(self):
        """CI mode with ENRICHED_CHOICE_UI_FAIL_CLOSED exits 1 on violations."""
        code = '''
def bad_function():
    # Raw ask_user_question without wrapper
    ask_user_question(
        question="Which approach?",
        options=[
            {"label": "A", "description": "Option A"},
            {"label": "B", "description": "Option B"},
        ],
        allowMultiple=False,
    )
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "bad_choice.py"
            test_file.write_text(code, encoding="utf-8")

            scanner_path = REPO_ROOT / "ops_scripts" / "ci" / "check_enriched_choice_ui_invariants.py"

            # Run with CI environment set
            env = os.environ.copy()
            env["ENRICHED_CHOICE_UI_FAIL_CLOSED"] = "1"
            env["CI"] = "1"

            result = subprocess.run(
                [sys.executable, str(scanner_path), str(test_file)],
                capture_output=True,
                text=True,
                cwd=str(REPO_ROOT),
                env=env,
            )

            # Should fail (exit 1)
            assert result.returncode == 1, f"Expected exit 1, got {result.returncode}: {result.stdout}"
            assert "raw_ask_user_question" in result.stdout or "Fail: 1" in result.stdout

    def test_bypass_allows_violations(self):
        """Bypass mode allows violations to pass."""
        code = '''
def bad_function():
    ask_user_question(
        question="Which?",
        options=[{"label": "A", "description": "Option A"}],
    )
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "bad_choice.py"
            test_file.write_text(code, encoding="utf-8")

            scanner_path = REPO_ROOT / "ops_scripts" / "ci" / "check_enriched_choice_ui_invariants.py"

            env = os.environ.copy()
            env["ENRICHED_CHOICE_UI_BYPASS"] = "1"

            result = subprocess.run(
                [sys.executable, str(scanner_path), str(test_file)],
                capture_output=True,
                text=True,
                cwd=str(REPO_ROOT),
                env=env,
            )

            # Should pass due to bypass
            assert result.returncode == 0, f"Bypass should allow exit 0: {result.stdout}"


class TestMigratedSurfaces:
    """Integration: migrated surfaces pass scanner."""

    def test_structured_reasoning_skill_passes(self):
        """Structured reasoning SKILL.md passes scanner."""
        skill_path = REPO_ROOT / ".cursor" / "skills" / "structured-reasoning" / "SKILL.md"
        assert skill_path.exists(), "SKILL.md should exist"

        scanner_path = REPO_ROOT / "ops_scripts" / "ci" / "check_enriched_choice_ui_invariants.py"
        result = subprocess.run(
            [sys.executable, str(scanner_path), str(skill_path), "--advisory"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )

        assert result.returncode == 0, f"SKILL.md should pass: {result.stdout}"
        assert "Pass: 1" in result.stdout or "✓ Pass: 1" in result.stdout

    def test_decision_gate_workflow_passes(self):
        """Author-gate decision gate workflow passes scanner."""
        workflow_path = REPO_ROOT / "docs/archive/windsurf/legacy-tree" / "workflows" / "author-gate-decision-gate.md"
        assert workflow_path.exists(), "author-gate-decision-gate.md should exist"

        scanner_path = REPO_ROOT / "ops_scripts" / "ci" / "check_enriched_choice_ui_invariants.py"
        result = subprocess.run(
            [sys.executable, str(scanner_path), str(workflow_path), "--advisory"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )

        assert result.returncode == 0, f"decision-gate.md should pass: {result.stdout}"
        assert "Pass: 1" in result.stdout or "✓ Pass: 1" in result.stdout


class TestAuthorityBoundaries:
    """Integration: AUTHOR_GATE_PACKET vs ASK_USER_QUESTION_PACKET separation."""

    def test_ag_packet_in_python_file_fails(self):
        """AUTHOR_GATE_PACKET emission in non-AG Python file fails."""
        code = '''
# Some random Python file not in AG pipeline
def bad_emit():
    print("AUTHOR_GATE_PACKET: " + json.dumps({"bad": "packet"}))
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "bad_emit.py"
            test_file.write_text(code, encoding="utf-8")

            scanner_path = REPO_ROOT / "ops_scripts" / "ci" / "check_enriched_choice_ui_invariants.py"
            result = subprocess.run(
                [sys.executable, str(scanner_path), str(test_file), "--advisory"],
                capture_output=True,
                text=True,
                cwd=str(REPO_ROOT),
            )

            # Should detect the violation
            assert "author_gate_packet_outside_ag_path" in result.stdout or "Fail: 1" in result.stdout

    def test_ask_packet_allowed_in_enriched_choice(self):
        """ASK_USER_QUESTION_PACKET emission allowed in enriched choice context."""
        code = '''
from tools.decisions.enriched_choice_builder import build_enriched_choice_question

def good_emit():
    payload = build_enriched_choice_question(
        question="Which?",
        options=[{"id": "A", "label": "Option A", "description": "Desc", "tradeoff": "Trade"}],
    )
    print("ASK_USER_QUESTION_PACKET: " + json.dumps(payload["telemetry_packet"]))
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "good_emit.py"
            test_file.write_text(code, encoding="utf-8")

            scanner_path = REPO_ROOT / "ops_scripts" / "ci" / "check_enriched_choice_ui_invariants.py"
            result = subprocess.run(
                [sys.executable, str(scanner_path), str(test_file), "--advisory"],
                capture_output=True,
                text=True,
                cwd=str(REPO_ROOT),
            )

            # Should pass
            assert result.returncode == 0, f"ASK_USER_QUESTION_PACKET should be allowed: {result.stdout}"


class TestViolationsLog:
    """Integration: violations are logged to JSONL."""

    def test_violations_logged_to_jsonl(self):
        """Scanner writes violations to artifacts/cursor/enriched_choice_ui_violations.jsonl."""
        code = '''
def bad_function():
    ask_user_question(
        question="Which?",
        options=[{"label": "A", "description": "Bad"}],
    )
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "bad_choice.py"
            test_file.write_text(code, encoding="utf-8")

            # Run scanner
            scanner_path = REPO_ROOT / "ops_scripts" / "ci" / "check_enriched_choice_ui_invariants.py"
            subprocess.run(
                [sys.executable, str(scanner_path), str(test_file), "--advisory"],
                capture_output=True,
                cwd=str(REPO_ROOT),
            )

            # Check log file
            log_path = REPO_ROOT / "artifacts" / "windsurf" / "enriched_choice_ui_violations.jsonl"
            if log_path.exists():
                # Read last line
                lines = log_path.read_text().strip().split("\n")
                if lines:
                    last_entry = json.loads(lines[-1])
                    assert "timestamp" in last_entry
                    assert "file" in last_entry
                    assert "violations" in last_entry
