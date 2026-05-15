"""
Unit tests for post_cursor_agent_plan_scope_audit.py

Tests cover:
- Advisory mode (warning, no block)
- Strict mode (blocking with exit 2)
- Bypass mode (exit 0)
- Threshold configuration
- Recency window
- Retroactive detection via hook
- JSONL logging
"""
import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Load module from .windsurf directory
REPO_ROOT = Path(__file__).parent.parent.parent.parent
MODULE_PATH = REPO_ROOT / ".windsurf" / "scripts" / "post_cursor_agent_plan_scope_audit.py"

spec = importlib.util.spec_from_file_location(
    "post_cursor_agent_plan_scope_audit", MODULE_PATH
)
_module = importlib.util.module_from_spec(spec)
sys.modules["post_cursor_agent_plan_scope_audit"] = _module
spec.loader.exec_module(_module)

from post_cursor_agent_plan_scope_audit import (
    main,
    get_config,
    extract_markers_from_text,
    detect_active_plan,
    detect_changed_files,
    write_audit_record,
    LOG_PATH,
)


class TestGetConfig:
    """Test configuration loading."""
    
    def test_default_config(self):
        """Default configuration values."""
        with patch.dict(os.environ, {}, clear=True):
            config = get_config()
            assert config["strict"] is False
            assert config["bypass"] is False
            assert config["min_files"] == 3
            assert config["recency_sec"] == 300
    
    def test_strict_mode_env(self):
        """Strict mode via PLAN_SCOPE_AUDIT_STRICT=1."""
        with patch.dict(os.environ, {"PLAN_SCOPE_AUDIT_STRICT": "1"}):
            config = get_config()
            assert config["strict"] is True
    
    def test_bypass_mode_env(self):
        """Bypass via PLAN_SCOPE_AUDIT_BYPASS=1."""
        with patch.dict(os.environ, {"PLAN_SCOPE_AUDIT_BYPASS": "1"}):
            config = get_config()
            assert config["bypass"] is True
    
    def test_custom_thresholds(self):
        """Custom thresholds via env vars."""
        with patch.dict(os.environ, {
            "MIN_FILES_FOR_AUDIT": "5",
            "AUTH_MARKER_RECENCY_SEC": "600"
        }):
            config = get_config()
            assert config["min_files"] == 5
            assert config["recency_sec"] == 600


class TestExtractMarkers:
    """Test marker extraction from response text."""
    
    def test_extract_discovered_scope(self):
        """Extract DISCOVERED_SCOPE marker."""
        text = '''Some response text
DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12" impact="High"
More text'''
        markers = extract_markers_from_text(text)
        assert len(markers) == 1
        assert "DISCOVERED_SCOPE" in markers[0]
    
    def test_extract_authorization_decision(self):
        """Extract AUTHORIZATION_DECISION marker."""
        text = '''Some text
AUTHORIZATION_DECISION: plan=foo-abc123 decision=ACCEPTED authorized_by=user decisive_reason="Critical"
More text'''
        markers = extract_markers_from_text(text)
        assert len(markers) == 1
        assert "AUTHORIZATION_DECISION" in markers[0]
    
    def test_extract_scope_expansion(self):
        """Extract SCOPE_EXPANSION marker."""
        text = '''Some text
SCOPE_EXPANSION: plan=foo-abc123 reason="W3 gap" added="W5.P8" authorized="yes"
More text'''
        markers = extract_markers_from_text(text)
        assert len(markers) == 1
        assert "SCOPE_EXPANSION" in markers[0]
    
    def test_extract_multiple_markers(self):
        """Extract multiple markers from response."""
        text = '''DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12" impact="High"
Some processing
AUTHORIZATION_DECISION: plan=foo-abc123 decision=ACCEPTED authorized_by=user decisive_reason="Critical"
SCOPE_EXPANSION: plan=foo-abc123 reason="W3 gap" added="W5.P8" authorized="yes"'''
        markers = extract_markers_from_text(text)
        assert len(markers) == 3


class TestDetectActivePlan:
    """Test active plan detection."""
    
    def test_detect_from_marker(self):
        """Detect plan from marker in response."""
        text = 'DISCOVERED_SCOPE: plan=my-plan-abc123 wave=3 phase=5 gap="G12" impact="High"'
        plan = detect_active_plan(text, [])
        assert plan == "my-plan-abc123"
    
    def test_detect_from_file_path(self):
        """Detect plan from file path."""
        text = "Some response"
        files = [".windsurf/plans/plan-markdown-update-enforcement-a7d4e1.md"]
        plan = detect_active_plan(text, files)
        # Regex extracts: descriptive_part + "-" + hash
        assert plan == "markdown-update-enforcement-a7d4e1"
    
    def test_detect_plan_with_multiple_hyphens(self):
        """Detect plan where descriptive part has multiple hyphens (e.g., my-foo-bar-a7d4e1)."""
        # This tests that regex handles slugs with multiple hyphenated segments
        text = 'DISCOVERED_SCOPE: plan=my-foo-bar-a7d4e1 wave=3 phase=5 gap="G12" impact="High"'
        plan = detect_active_plan(text, [])
        # Should extract: my-foo-bar-a7d4e1 (starts with letter, has hyphens, ends with 6 hex)
        assert plan == "my-foo-bar-a7d4e1"
    
    def test_no_plan_detected(self):
        """Return None when no plan detected."""
        text = "Some random response without plan references"
        plan = detect_active_plan(text, [])
        assert plan is None


class TestDetectChangedFiles:
    """Test changed file detection."""
    
    def test_detect_edit_call(self):
        """Detect files from edit() calls."""
        text = 'edit(file_path=".windsurf/rules/new.md", ...)'
        files = detect_changed_files(text)
        assert ".windsurf/rules/new.md" in files
    
    def test_detect_write_to_file(self):
        """Detect files from write_to_file() calls."""
        text = 'write_to_file(TargetFile="tests/unit/test.py", ...)'
        files = detect_changed_files(text)
        assert "tests/unit/test.py" in files
    
    def test_detect_multiple_files(self):
        """Detect multiple file changes."""
        text = '''edit(file_path="file1.py")
write_to_file(TargetFile="file2.py")
edit(file_path="file3.py")'''
        files = detect_changed_files(text)
        assert len(files) == 3


class TestAdvisoryMode:
    """Test advisory mode behavior (default)."""
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('post_cursor_agent_plan_scope_audit.detect_changed_files')
    @patch('post_cursor_agent_plan_scope_audit.detect_active_plan')
    @patch('post_cursor_agent_plan_scope_audit.extract_markers_from_text')
    @patch('post_cursor_agent_plan_scope_audit.check_scope_authorization')
    @patch('post_cursor_agent_plan_scope_audit.write_audit_record')
    def test_advisory_warning_no_block(
        self, mock_write, mock_check, mock_extract, mock_plan, mock_files
    ):
        """Advisory mode: emit warning, do not block (exit 0)."""
        # Setup: 3 files changed, plan detected, but no authorization
        mock_files.return_value = ["file1.py", "file2.py", "file3.py"]
        mock_plan.return_value = "foo-abc123"
        mock_extract.return_value = []  # No markers
        
        # Mock unauthorized result
        mock_result = MagicMock()
        mock_result.authorized = False
        mock_result.reason = "MISSING_AUTHORIZATION_DECISION"
        mock_result.message = "No authorization"
        mock_result.decision = None
        mock_result.should_warn = True
        mock_result.should_block = True
        mock_check.return_value = mock_result
        
        exit_code = main()
        
        assert exit_code == 0  # Advisory mode doesn't block
        mock_write.assert_called_once()
        call_args = mock_write.call_args
        assert call_args[1]["mode"] == "advisory"
        assert call_args[1]["exit_code"] == 0


class TestStrictMode:
    """Test strict mode behavior."""
    
    @patch.dict(os.environ, {"PLAN_SCOPE_AUDIT_STRICT": "1"}, clear=True)
    @patch('post_cursor_agent_plan_scope_audit.detect_changed_files')
    @patch('post_cursor_agent_plan_scope_audit.detect_active_plan')
    @patch('post_cursor_agent_plan_scope_audit.extract_markers_from_text')
    @patch('post_cursor_agent_plan_scope_audit.check_scope_authorization')
    @patch('post_cursor_agent_plan_scope_audit.write_audit_record')
    def test_strict_blocks_unauthorized(
        self, mock_write, mock_check, mock_extract, mock_plan, mock_files
    ):
        """Strict mode: exit 2 on unauthorized scope drift."""
        mock_files.return_value = ["file1.py", "file2.py", "file3.py"]
        mock_plan.return_value = "foo-abc123"
        mock_extract.return_value = []
        
        mock_result = MagicMock()
        mock_result.authorized = False
        mock_result.reason = "MISSING_AUTHORIZATION_DECISION"
        mock_result.message = "No authorization"
        mock_result.decision = None
        mock_result.should_warn = True
        mock_result.should_block = True
        mock_check.return_value = mock_result
        
        exit_code = main()
        
        assert exit_code == 2  # Strict mode blocks
        call_args = mock_write.call_args
        assert call_args[1]["mode"] == "strict"
        assert call_args[1]["exit_code"] == 2


class TestBypassMode:
    """Test bypass mode."""
    
    @patch.dict(os.environ, {"PLAN_SCOPE_AUDIT_BYPASS": "1"}, clear=True)
    @patch('post_cursor_agent_plan_scope_audit.write_audit_record')
    def test_bypass_exits_zero(self, mock_write):
        """Bypass mode: exit 0 and log bypass."""
        exit_code = main()
        
        assert exit_code == 0
        mock_write.assert_called_once()
        call_args = mock_write.call_args
        assert call_args[1]["mode"] == "bypass"
        assert call_args[1]["extra"]["bypass_reason"] == "PLAN_SCOPE_AUDIT_BYPASS=1"


class TestThresholds:
    """Test configurable thresholds."""
    
    @patch.dict(os.environ, {"MIN_FILES_FOR_AUDIT": "5"}, clear=True)
    @patch('post_cursor_agent_plan_scope_audit.detect_changed_files')
    @patch('post_cursor_agent_plan_scope_audit.write_audit_record')
    def test_min_files_threshold(self, mock_write, mock_files):
        """MIN_FILES_FOR_AUDIT threshold prevents audit below threshold."""
        # Only 3 files changed, threshold is 5
        mock_files.return_value = ["file1.py", "file2.py", "file3.py"]
        
        exit_code = main()
        
        # Should exit 0 silently (not enough files)
        assert exit_code == 0
        mock_write.assert_not_called()


class TestRetroactiveDetection:
    """Test retroactive authorization detection via hook."""
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('post_cursor_agent_plan_scope_audit.detect_changed_files')
    @patch('post_cursor_agent_plan_scope_audit.detect_active_plan')
    @patch('post_cursor_agent_plan_scope_audit.extract_markers_from_text')
    @patch('post_cursor_agent_plan_scope_audit.check_scope_authorization')
    @patch('post_cursor_agent_plan_scope_audit.write_audit_record')
    def test_retroactive_detected_advisory(
        self, mock_write, mock_check, mock_extract, mock_plan, mock_files
    ):
        """Retroactive authorization detected in advisory mode."""
        mock_files.return_value = ["file1.py", "file2.py", "file3.py"]
        mock_plan.return_value = "foo-abc123"
        mock_extract.return_value = [
            'DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12" impact="High"',
            'AUTHORIZATION_DECISION: plan=foo-abc123 decision=ACCEPTED authorized_by=user decisive_reason="Critical"',
        ]
        
        mock_result = MagicMock()
        mock_result.authorized = False
        mock_result.reason = "RETROACTIVE_AUTHORIZATION_DETECTED"
        mock_result.message = "Work before auth"
        mock_result.decision = "ACCEPTED"
        mock_result.should_warn = True
        mock_result.should_block = True
        mock_check.return_value = mock_result
        
        exit_code = main()
        
        # Advisory mode: warning but no block
        assert exit_code == 0
        call_args = mock_write.call_args
        assert "RETROACTIVE_AUTHORIZATION_DETECTED" in call_args[1]["result"].reason
    
    @patch.dict(os.environ, {"PLAN_SCOPE_AUDIT_STRICT": "1"}, clear=True)
    @patch('post_cursor_agent_plan_scope_audit.detect_changed_files')
    @patch('post_cursor_agent_plan_scope_audit.detect_active_plan')
    @patch('post_cursor_agent_plan_scope_audit.extract_markers_from_text')
    @patch('post_cursor_agent_plan_scope_audit.check_scope_authorization')
    @patch('post_cursor_agent_plan_scope_audit.write_audit_record')
    def test_retroactive_blocks_strict(
        self, mock_write, mock_check, mock_extract, mock_plan, mock_files
    ):
        """Retroactive authorization blocks in strict mode."""
        mock_files.return_value = ["file1.py", "file2.py", "file3.py"]
        mock_plan.return_value = "foo-abc123"
        mock_extract.return_value = []
        
        mock_result = MagicMock()
        mock_result.authorized = False
        mock_result.reason = "RETROACTIVE_AUTHORIZATION_DETECTED"
        mock_result.message = "Work before auth"
        mock_result.decision = None
        mock_result.should_warn = True
        mock_result.should_block = True
        mock_check.return_value = mock_result
        
        exit_code = main()
        
        assert exit_code == 2


class TestJSONLLogging:
    """Test JSONL audit log format."""
    
    def test_log_record_structure(self, tmp_path):
        """JSONL record has all required fields."""
        log_file = tmp_path / "test_audit.jsonl"
        
        with patch('post_cursor_agent_plan_scope_audit.LOG_PATH', log_file):
            mock_result = MagicMock()
            mock_result.authorized = False
            mock_result.reason = "MISSING_AUTHORIZATION_DECISION"
            mock_result.message = "No auth"
            mock_result.decision = None
            mock_result.should_warn = True
            mock_result.should_block = True
            
            write_audit_record(
                plan_id="foo-abc123",
                mode="strict",
                changed_files_count=3,
                markers_count=2,
                result=mock_result,
                exit_code=2,
                extra={"reason_codes": ["MISSING_AUTHORIZATION_DECISION"]}
            )
            
            # Read and parse log
            with open(log_file, 'r') as f:
                record = json.loads(f.readline())
            
            # Verify required fields
            assert record["plan_id"] == "foo-abc123"
            assert record["mode"] == "strict"
            assert record["changed_files_count"] == 3
            assert record["markers_count"] == 2
            assert record["exit_code"] == 2
            assert record["authorized"] is False
            assert record["reason"] == "MISSING_AUTHORIZATION_DECISION"
            assert record["should_warn"] is True
            assert record["should_block"] is True
            assert "timestamp" in record
            assert record["reason_codes"] == ["MISSING_AUTHORIZATION_DECISION"]


class TestReasonCodes:
    """Test specific reason code detection and surfacing."""
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('post_cursor_agent_plan_scope_audit.detect_changed_files')
    @patch('post_cursor_agent_plan_scope_audit.detect_active_plan')
    @patch('post_cursor_agent_plan_scope_audit.extract_markers_from_text')
    @patch('post_cursor_agent_plan_scope_audit.check_scope_authorization')
    @patch('post_cursor_agent_plan_scope_audit.write_audit_record')
    def test_missing_discovered_scope(
        self, mock_write, mock_check, mock_extract, mock_plan, mock_files
    ):
        """MISSING_DISCOVERED_SCOPE reason surfaced."""
        mock_files.return_value = ["file1.py", "file2.py", "file3.py"]
        mock_plan.return_value = "foo-abc123"
        mock_extract.return_value = []
        
        mock_result = MagicMock()
        mock_result.authorized = False
        mock_result.reason = "MISSING_DISCOVERED_SCOPE"
        mock_result.message = "No DISCOVERED_SCOPE"
        mock_result.decision = None
        mock_result.should_warn = True
        mock_result.should_block = False
        mock_check.return_value = mock_result
        
        main()
        
        call_args = mock_write.call_args
        assert call_args[1]["result"].reason == "MISSING_DISCOVERED_SCOPE"
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('post_cursor_agent_plan_scope_audit.detect_changed_files')
    @patch('post_cursor_agent_plan_scope_audit.detect_active_plan')
    @patch('post_cursor_agent_plan_scope_audit.extract_markers_from_text')
    @patch('post_cursor_agent_plan_scope_audit.check_scope_authorization')
    @patch('post_cursor_agent_plan_scope_audit.write_audit_record')
    def test_authorization_not_accepted_deferred(
        self, mock_write, mock_check, mock_extract, mock_plan, mock_files
    ):
        """AUTHORIZATION_NOT_ACCEPTED for DEFERRED decision."""
        mock_files.return_value = ["file1.py", "file2.py", "file3.py"]
        mock_plan.return_value = "foo-abc123"
        mock_extract.return_value = [
            'DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12" impact="High"',
            'AUTHORIZATION_DECISION: plan=foo-abc123 decision=DEFERRED authorized_by=author_gate decisive_reason="Time gated"',
        ]
        
        mock_result = MagicMock()
        mock_result.authorized = False
        mock_result.reason = "DEFERRED_NOT_AUTHORIZED"
        mock_result.message = "Not authorized"
        mock_result.decision = "DEFERRED"
        mock_result.should_warn = True
        mock_result.should_block = False
        mock_check.return_value = mock_result
        
        main()
        
        call_args = mock_write.call_args
        assert call_args[1]["result"].decision == "DEFERRED"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
