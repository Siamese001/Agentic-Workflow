"""Unit tests for check_enriched_choice_ui_invariants scanner.

Per hardened plan ui-choice-consistency-zero-loss-hardened-d9f3a1:
- Scanner tests prove callsite discipline (review correction #6)
- Unit tests prove builder formatting (in test_enriched_choice_builder.py)
- Scanner is SEPARATE from AG audit (review correction #2)
- CI mode defaults to fail-closed (review correction #1)
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Import the module under test
REPO_ROOT = Path(__file__).resolve().parents[4]
SCANNER_PATH = REPO_ROOT / "ops_scripts" / "ci" / "check_enriched_choice_ui_invariants.py"

def _load_scanner():
    """Load scanner module using importlib."""
    spec = importlib.util.spec_from_file_location("check_enriched_choice_ui_invariants", SCANNER_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["check_enriched_choice_ui_invariants"] = mod
    spec.loader.exec_module(mod)
    return mod


# Load scanner module
import importlib.util
scanner = _load_scanner()

check_file = scanner.check_file
check_paths = scanner.check_paths
_is_exempt = scanner._is_exempt
_is_active_surface = scanner._is_active_surface
_detect_raw_ask_user_question = scanner._detect_raw_ask_user_question
_detect_markdown_prose_options = scanner._detect_markdown_prose_options
_detect_ag_packet_outside_path = scanner._detect_ag_packet_outside_path
_detect_missing_telemetry = scanner._detect_missing_telemetry
main = scanner.main


class TestExemptions:
    """Tests 12-13: Exemption allowlist and active surfaces."""

    def test_data_collection_wizard_exempt(self):
        """Test 12: CLI data-collection wizard exemption passes."""
        path = REPO_ROOT / "apps_shared" / "cli" / "interactive_wizard.py"
        is_exempt, reason = _is_exempt(path)
        assert is_exempt is True
        assert reason == "data_collection_field_input"

    def test_test_fixture_exempt(self):
        """Test 13: Test fixtures are exempt."""
        path = REPO_ROOT / "tests" / "unit" / "some_test.py"
        is_exempt, reason = _is_exempt(path)
        assert is_exempt is True
        assert "test_fixture" in reason

    def test_docs_exempt(self):
        """Docs-only examples are exempt."""
        path = REPO_ROOT / "docs" / "reference" / "example.md"
        is_exempt, reason = _is_exempt(path)
        assert is_exempt is True
        assert "documentation" in reason

    def test_plans_exempt(self):
        """Plan documentation is exempt."""
        path = REPO_ROOT / "docs" / "archive" / "windsurf" / "legacy-tree" / "plans" / "some-plan.md"
        is_exempt, reason = _is_exempt(path)
        assert is_exempt is True
        assert "plan_documentation" in reason

    def test_active_surfaces_not_exempt(self):
        """Active decision surfaces are NOT exempt."""
        path = REPO_ROOT / ".cursor" / "skills" / "structured-reasoning" / "SKILL.md"
        is_exempt, _ = _is_exempt(path)
        assert is_exempt is False


class TestRawAskUserQuestionDetection:
    """Test 14: Raw ask_user_question detection."""

    def test_detects_raw_ask_user_question(self):
        """Test 14: Raw ask_user_question in decision context fails scanner."""
        content = '''
def some_function():
    # Raw ask_user_question without enrichment
    result = ask_user_question(
        question="Which approach?",
        options=[
            {"label": "A", "description": "Option A"},
            {"label": "B", "description": "Option B"},
        ],
        allowMultiple=False,
    )
'''
        violations = _detect_raw_ask_user_question(content)
        assert len(violations) == 1
        assert violations[0]["pattern"] == "raw_ask_user_question"
        assert violations[0]["severity"] == "critical"

    def test_skips_enriched_wrapper_usage(self):
        """Using build_enriched_choice_question is allowed."""
        content = '''
def some_function():
    from tools.decisions.enriched_choice_builder import build_enriched_choice_question
    
    payload = build_enriched_choice_question(
        question="Which approach?",
        options=[...],
    )
    result = ask_user_question(
        question=payload["question"],
        options=payload["options"],
    )
'''
        violations = _detect_raw_ask_user_question(content)
        # Should not flag because build_enriched_choice_question is in context
        assert len(violations) == 0

    def test_skips_ag_pipeline_usage(self):
        """Using AG pipeline is allowed."""
        content = '''
def some_function():
    # Using Author-Gate pipeline
    packet = emit_packet.build_packet(spec)
    result = ask_user_question(
        question=packet["question"],
        options=packet["options"],
    )
'''
        violations = _detect_raw_ask_user_question(content)
        # Should not flag because emit_packet is in context
        assert len(violations) == 0


class TestMarkdownProseDetection:
    """Test 15: Markdown prose option detection."""

    def test_detects_markdown_prose_options(self):
        """Test 15: Markdown prose options in workflow fails scanner."""
        content = '''### Step 2 — STOP and prompt

Present this prompt to the user:

> A) Narrow the exception type — no guardian comment needed
> B) Add guardian comment — counted in ratchet
> C) Restructure to avoid the pattern
> D) Proceed as-is

Do NOT proceed until the user selects.
'''
        # Create a temporary markdown file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)
        
        try:
            violations = _detect_markdown_prose_options(content, path)
            assert len(violations) == 1
            assert violations[0]["pattern"] == "markdown_prose_options"
            assert violations[0]["severity"] == "high"
        finally:
            path.unlink()

    def test_skips_python_files_for_prose_check(self):
        """Prose detection only runs on markdown files."""
        content = '''# Some Python file
options = ["A", "B", "C"]
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)
        
        try:
            violations = _detect_markdown_prose_options(content, path)
            assert len(violations) == 0
        finally:
            path.unlink()


class TestAGPacketAuthority:
    """Test 16: AUTHOR_GATE_PACKET authority boundary."""

    def test_detects_ag_packet_outside_ag_path(self):
        """Test 16: AUTHOR_GATE_PACKET outside canonical AG path is violation."""
        content = '''
def some_function():
    # Wrong: Emitting AG packet outside AG pipeline
    print("AUTHOR_GATE_PACKET: " + json.dumps(packet))
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)
        
        try:
            violations = _detect_ag_packet_outside_path(content, path)
            assert len(violations) == 1
            assert violations[0]["pattern"] == "author_gate_packet_outside_ag_path"
            assert violations[0]["severity"] == "critical"
        finally:
            path.unlink()

    def test_allows_ag_packet_in_emit_packet(self):
        """AG path is allowed to emit AUTHOR_GATE_PACKET."""
        content = '''
def emit():
    print("AUTHOR_GATE_PACKET: " + json.dumps(packet))
'''
        # Create file in AG pipeline path
        path = REPO_ROOT / ".cursor" / "skills" / "author-gate-packet-builder" / "emit_packet.py"
        
        violations = _detect_ag_packet_outside_path(content, path)
        assert len(violations) == 0

    def test_allows_ag_packet_in_antipattern_workflow(self):
        """antipattern-author-gate.md is AUTHOR_GATE path."""
        content = '''
Use the canonical Author-Gate pipeline:
> AUTHOR_GATE_PACKET: {...}
'''
        path = REPO_ROOT / "docs/archive/windsurf/legacy-tree" / "workflows" / "antipattern-author-gate.md"
        
        violations = _detect_ag_packet_outside_path(content, path)
        assert len(violations) == 0


class TestTelemetryDetection:
    """Test 17: Telemetry emission detection."""

    def test_detects_missing_telemetry(self):
        """Test 17: Enriched wrapper without telemetry emission is violation."""
        content = '''
from tools.decisions.enriched_choice_builder import build_enriched_choice_question

def ask():
    payload = build_enriched_choice_question(
        question="Which?",
        options=[...],
    )
    result = ask_user_question(
        question=payload["question"],
        options=payload["options"],
    )
    # Telemetry emission is missing here
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)
        
        try:
            violations = _detect_missing_telemetry(content, path)
            assert len(violations) == 1
            assert violations[0]["pattern"] == "missing_telemetry_emission"
        finally:
            path.unlink()

    def test_allows_with_telemetry(self):
        """Enriched wrapper with telemetry emission is allowed."""
        content = '''
from tools.decisions.enriched_choice_builder import build_enriched_choice_question

def ask():
    payload = build_enriched_choice_question(
        question="Which?",
        options=[...],
    )
    result = ask_user_question(
        question=payload["question"],
        options=payload["options"],
    )
    print("ASK_USER_QUESTION_PACKET: " + json.dumps(payload["telemetry_packet"]))
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)
        
        try:
            violations = _detect_missing_telemetry(content, path)
            assert len(violations) == 0
        finally:
            path.unlink()


class TestFailPolicy:
    """Tests 18-19: Fail-closed CI mode and advisory manual mode."""

    def test_ci_mode_fail_closed_by_default(self, monkeypatch):
        """Test 18: CI mode defaults to fail-closed (exit 1 on violations)."""
        # Simulate CI environment
        monkeypatch.setenv("CI", "1")
        
        # Create temp file with violation
        content = '''
ask_user_question(
    question="Which?",
    options=[{"label": "A", "description": "Option A"}],
)
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text(content)
            
            # Run main with the file
            old_argv = sys.argv
            sys.argv = ["check_enriched_choice_ui_invariants.py", str(test_file)]
            
            try:
                result = main()
                assert result == 1  # Fail-closed: exit 1 on violations
            finally:
                sys.argv = old_argv

    def test_manual_mode_advisory_allowed(self, monkeypatch):
        """Test 19: Manual mode with --advisory flag exits 0 even with violations."""
        # Ensure not in CI mode
        monkeypatch.delenv("CI", raising=False)
        monkeypatch.delenv("ENRICHED_CHOICE_UI_FAIL_CLOSED", raising=False)
        
        content = '''
ask_user_question(
    question="Which?",
    options=[{"label": "A", "description": "Option A"}],
)
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text(content)
            
            old_argv = sys.argv
            sys.argv = ["check_enriched_choice_ui_invariants.py", "--advisory", str(test_file)]
            
            try:
                result = main()
                assert result == 0  # Advisory: exit 0 even with violations
            finally:
                sys.argv = old_argv


class TestBypass:
    """Test bypass environment variable."""

    def test_bypass_exits_cleanly(self, monkeypatch):
        """ENRICHED_CHOICE_UI_BYPASS=1 exits 0 immediately."""
        monkeypatch.setenv("ENRICHED_CHOICE_UI_BYPASS", "1")
        
        old_argv = sys.argv
        sys.argv = ["check_enriched_choice_ui_invariants.py"]
        
        try:
            result = main()
            assert result == 0
        finally:
            sys.argv = old_argv


class TestFullFileCheck:
    """Integration tests for full file checking."""

    def test_clean_file_passes(self):
        """File with enriched wrapper passes."""
        content = '''
from tools.decisions.enriched_choice_builder import build_enriched_choice_question

def present_choice():
    payload = build_enriched_choice_question(
        question="Which approach?",
        options=[
            {
                "id": "A",
                "label": "Fast approach",
                "description": "Quick implementation",
                "tradeoff": "Higher risk",
            },
        ],
        recommended_id="A",
    )
    
    ask_user_question(
        question=payload["question"],
        options=payload["options"],
        allowMultiple=False,
    )
    
    print("ASK_USER_QUESTION_PACKET: " + json.dumps(payload["telemetry_packet"]))
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "clean.py"
            test_file.write_text(content)
            
            result = check_file(test_file)
            assert result["status"] == "pass"
            assert len(result["violations"]) == 0

    def test_violating_file_fails(self):
        """File with raw ask_user_question fails."""
        content = '''
def present_choice():
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
            test_file = Path(tmpdir) / "violating.py"
            test_file.write_text(content)
            
            result = check_file(test_file)
            assert result["status"] == "fail"
            assert len(result["violations"]) > 0
            assert any(v["pattern"] == "raw_ask_user_question" for v in result["violations"])


class TestActiveSurfaceCheck:
    """Verify active surfaces are identified."""

    def test_structured_reasoning_is_active(self):
        path = REPO_ROOT / ".cursor" / "skills" / "structured-reasoning" / "SKILL.md"
        assert _is_active_surface(path) is True

    def test_decision_gate_is_active(self):
        path = REPO_ROOT / "docs/archive/windsurf/legacy-tree" / "workflows" / "author-gate-decision-gate.md"
        assert _is_active_surface(path) is True

    def test_random_file_not_active(self):
        path = REPO_ROOT / "README.md"
        assert _is_active_surface(path) is False
