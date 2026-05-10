#!/usr/bin/env python3
"""Tests for pre_notion_plan_write_gate.py — plan identity verification hook."""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest import mock

import pytest

# Ensure script is importable
REPO_ROOT = Path(__file__).parents[3]  # tests/unit/windsurf_scripts/ -> tests/unit/ -> tests/ -> repo root
SCRIPTS_PATH = REPO_ROOT / ".windsurf" / "scripts"
if str(SCRIPTS_PATH) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_PATH))

from pre_notion_plan_write_gate import (
    verify_plan_identity,
    extract_slug_from_context,
    _ids_match,
    _normalize_id,
)


class TestNormalizeId:
    """Test ID normalization logic."""
    
    def test_lowercase(self):
        assert _normalize_id("ABC123") == "abc123"
    
    def test_strip_dashes(self):
        assert _normalize_id("35b27693-f55c-81f1") == "35b27693f55c81f1"
    
    def test_already_normalized(self):
        assert _normalize_id("35b27693f55c81f1") == "35b27693f55c81f1"
    
    def test_whitespace(self):
        assert _normalize_id("  35b27693-f55c  ") == "35b27693f55c"


class TestIdsMatch:
    """Test ID comparison logic."""
    
    def test_exact_match(self):
        assert _ids_match("abc123", "abc123") is True
    
    def test_case_insensitive(self):
        assert _ids_match("ABC123", "abc123") is True
    
    def test_dash_tolerance(self):
        assert _ids_match("35b27693-f55c", "35b27693f55c") is True
    
    def test_mismatch(self):
        assert _ids_match("abc123", "def456") is False


class TestExtractSlugFromContext:
    """Test slug extraction from various context formats."""
    
    def test_plan_created_marker(self):
        ctx = "PLAN_CREATED: slug=my-plan-test123 path=.windsurf/plans/my-plan-test123.md"
        assert extract_slug_from_context(ctx) == "my-plan-test123"
    
    def test_plan_file_path(self):
        ctx = "Open file .windsurf/plans/l6-alignment-deferred-scope-c5e8a7.md for editing"
        assert extract_slug_from_context(ctx) == "l6-alignment-deferred-scope-c5e8a7"
    
    def test_backtick_slug(self):
        ctx = "The plan `notion-plan-identity-enforcement-f2a9c1` is ready"
        assert extract_slug_from_context(ctx) == "notion-plan-identity-enforcement-f2a9c1"
    
    def test_quote_slug(self):
        ctx = 'Mark "l5-cert-ref-deferred-scope-f3a1b8" as Deferred'
        assert extract_slug_from_context(ctx) == "l5-cert-ref-deferred-scope-f3a1b8"
    
    def test_no_slug_found(self):
        ctx = "This text has no plan reference"
        assert extract_slug_from_context(ctx) is None
    
    def test_empty_context(self):
        assert extract_slug_from_context("") is None
    
    def test_none_context(self):
        assert extract_slug_from_context(None) is None


class TestVerifyPlanIdentity:
    """Test the core verification logic."""
    
    @mock.patch("pre_notion_plan_write_gate._query_notion_plans_db")
    def test_match_success(self, mock_query):
        """Verification passes when slug resolves to targeted page."""
        mock_query.return_value = {
            "id": "35b27693-f55c-8189-8827-c3dec80f05fa",
            "properties": {
                "Slug": {"title": [{"text": {"content": "l6-alignment-deferred-scope-c5e8a7"}}]}
            }
        }
        
        result = verify_plan_identity(
            "l6-alignment-deferred-scope-c5e8a7",
            "35b27693-f55c-8189-8827-c3dec80f05fa"
        )
        
        assert result.ok is True
        assert "verified" in result.message.lower()
        assert result.actual_slug == "l6-alignment-deferred-scope-c5e8a7"
    
    @mock.patch("pre_notion_plan_write_gate._query_notion_plans_db")
    def test_mismatch_detected(self, mock_query):
        """Verification fails when slug resolves to different page."""
        mock_query.return_value = {
            "id": "35b27693-f55c-8189-8827-c3dec80f05fa",  # Correct page for slug
            "properties": {
                "Slug": {"title": [{"text": {"content": "l6-alignment-deferred-scope-c5e8a7"}}]}
            }
        }
        
        result = verify_plan_identity(
            "l6-alignment-deferred-scope-c5e8a7",
            "WRONG-PAGE-ID-12345678"  # Wrong page targeted
        )
        
        assert result.ok is False
        assert "PLAN_IDENTITY_MISMATCH" in result.message
        assert "35b27693" in result.actual_page_id  # Shows actual page
    
    @mock.patch("pre_notion_plan_write_gate._query_notion_plans_db")
    def test_slug_not_found(self, mock_query):
        """Allow new plans (slug not in DB yet)."""
        mock_query.return_value = None
        
        result = verify_plan_identity(
            "brand-new-plan-a1b2c3",
            "35b27693-f55c-81f1-baf1-fb859d6fd066"
        )
        
        assert result.ok is True  # Allow new plans
        assert "not found" in result.message.lower()
    
    @mock.patch("pre_notion_plan_write_gate._query_notion_plans_db")
    def test_query_error(self, mock_query):
        """Handle query failure appropriately."""
        mock_query.return_value = {"id": "ERROR:connection timeout", "error": "connection timeout"}
        
        result = verify_plan_identity(
            "some-plan-slug",
            "35b27693-f55c-81f1-baf1-fb859d6fd066"
        )
        
        assert result.ok is False
        assert "Failed to query" in result.message
    
    def test_missing_inputs(self):
        """Handle missing inputs gracefully."""
        result = verify_plan_identity("", "some-page-id")
        assert result.ok is False
        assert "Missing" in result.message
        
        result = verify_plan_identity("some-slug", "")
        assert result.ok is False
        assert "Missing" in result.message


class TestCli:
    """Test command-line interface."""
    
    @mock.patch("pre_notion_plan_write_gate._query_notion_plans_db")
    def test_cli_success(self, mock_query):
        """CLI exits 0 on successful verification."""
        mock_query.return_value = {
            "id": "35b27693-f55c-8189-8827-c3dec80f05fa",
            "properties": {
                "Slug": {"title": [{"text": {"content": "test-plan"}}]}
            }
        }
        
        from pre_notion_plan_write_gate import cli_main
        
        with mock.patch("sys.argv", [
            "pre_notion_plan_write_gate.py",
            "--intended-slug", "test-plan",
            "--notion-page-id", "35b27693-f55c-8189-8827-c3dec80f05fa"
        ]):
            exit_code = cli_main()
        
        assert exit_code == 0
    
    def test_cli_test_mismatch(self):
        """Test --test-mismatch flag simulates and detects mismatch."""
        from pre_notion_plan_write_gate import cli_main
        
        with mock.patch("sys.argv", [
            "pre_notion_plan_write_gate.py",
            "--intended-slug", "any-slug",
            "--notion-page-id", "correct-page-id",
            "--test-mismatch"
        ]):
            exit_code = cli_main()
        
        assert exit_code == 2  # Mismatch detected


class TestLogging:
    """Test audit logging."""
    
    def test_log_written(self):
        """Verification attempts are logged to JSONL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "artifacts" / "windsurf"
            log_path.mkdir(parents=True, exist_ok=True)
            
            with mock.patch(
                "pre_notion_plan_write_gate._query_notion_plans_db",
                return_value=None
            ):
                with mock.patch(
                    "pre_notion_plan_write_gate.Path",
                    return_value=log_path
                ):
                    result = verify_plan_identity("test-slug", "test-page")
                    # Log should have been written


class TestEnvironmentVariables:
    """Test bypass and fail-closed environment variables."""
    
    @mock.patch("pre_notion_plan_write_gate._query_notion_plans_db")
    def test_bypass_allows_mismatch(self, mock_query, monkeypatch):
        """NOTION_PLAN_IDENTITY_BYPASS=1 allows mismatches with warning."""
        monkeypatch.setenv("NOTION_PLAN_IDENTITY_BYPASS", "1")
        
        mock_query.return_value = {
            "id": "correct-page-id",
            "properties": {"Slug": {"title": [{"text": {"content": "test"}}]}}
        }
        
        from pre_notion_plan_write_gate import run_gate
        
        exit_code = run_gate("test", "wrong-page-id")
        
        assert exit_code == 0  # Bypass allows
    
    @mock.patch("pre_notion_plan_write_gate._query_notion_plans_db")
    def test_fail_closed_blocks(self, mock_query, monkeypatch):
        """NOTION_PLAN_IDENTITY_FAIL_CLOSED=1 blocks on mismatch."""
        monkeypatch.setenv("NOTION_PLAN_IDENTITY_FAIL_CLOSED", "1")
        
        mock_query.return_value = {
            "id": "correct-page-id",
            "properties": {"Slug": {"title": [{"text": {"content": "test"}}]}}
        }
        
        from pre_notion_plan_write_gate import run_gate
        
        exit_code = run_gate("test", "wrong-page-id")
        
        assert exit_code == 2  # Fail-closed blocks


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
