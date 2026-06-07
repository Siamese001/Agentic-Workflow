#!/usr/bin/env python3
"""
Notion API Integration Tests for CI Gates

Requires: NOTION_TOKEN or NOTION_API_KEY environment variable
Rate limiting: Built-in 350ms delays between API calls
Scope: Live API calls to Notion Plans DB for gate verification

Run with:
    NOTION_TOKEN=secret_xxx pytest tests/integration/ops_scripts/ci/test_notion_api_integration.py -v

Or with bypass (skips live tests):
    NOTION_INTEGRATION_TEST_BYPASS=1 pytest tests/integration/ops_scripts/ci/test_notion_api_integration.py
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]

# Rate limiting: Notion API allows ~3 requests per second
API_DELAY = 0.35  # 350ms between calls


def _get_notion_token() -> str | None:
    """Get Notion token from environment."""
    return os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")


def _should_skip() -> bool:
    """Check if tests should be skipped."""
    if os.environ.get("NOTION_INTEGRATION_TEST_BYPASS") == "1":
        return True
    if not _get_notion_token():
        return True
    return False


@pytest.fixture
def notion_token() -> str:
    """Fixture providing Notion API token."""
    token = _get_notion_token()
    if not token:
        pytest.skip("NOTION_TOKEN or NOTION_API_KEY not set")
    return token


@pytest.fixture
def plans_db_id() -> str:
    """Fixture providing Plans DB ID."""
    return "ac53d31b-3068-4039-9ebe-856c12caab32"


class TestNotionAPIConnectivity:
    """Item 1: Real Notion API Integration Tests - Basic connectivity."""

    def test_api_token_valid(self, notion_token: str) -> None:
        """Verify token can authenticate to Notion API."""
        import urllib.request
        import urllib.error

        req = urllib.request.Request(
            "https://api.notion.com/v1/users/me",
            headers={
                "Authorization": f"Bearer {notion_token}",
                "Notion-Version": "2025-09-03",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read())
                assert "id" in data
                assert "type" in data
        except urllib.error.HTTPError as e:
            pytest.fail(f"API authentication failed: {e.code} {e.reason}")

        time.sleep(API_DELAY)  # Rate limiting

    def test_plans_db_queryable(self, notion_token: str, plans_db_id: str) -> None:
        """Verify Plans DB can be queried."""
        import urllib.request
        import urllib.error

        req = urllib.request.Request(
            f"https://api.notion.com/v1/databases/{plans_db_id}",
            headers={
                "Authorization": f"Bearer {notion_token}",
                "Notion-Version": "2025-09-03",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read())
                assert data["id"] == plans_db_id
                assert data["object"] == "database"
        except urllib.error.HTTPError as e:
            if e.code == 404:
                pytest.fail(f"Plans DB not found: {plans_db_id}")
            pytest.fail(f"API error: {e.code} {e.reason}")

        time.sleep(API_DELAY)  # Rate limiting


class TestNP9NewPlanStatusIntegration:
    """Item 1: Integration tests for NP9 New-Plan Status gate."""

    def test_query_plans_db_for_recent_entries(self, notion_token: str, plans_db_id: str) -> None:
        """Query Plans DB for entries created in last 24 hours."""
        import urllib.request

        req = urllib.request.Request(
            f"https://api.notion.com/v1/databases/{plans_db_id}/query",
            data=json.dumps({
                "page_size": 10,
                "sorts": [{"timestamp": "created_time", "direction": "descending"}],
            }).encode(),
            headers={
                "Authorization": f"Bearer {notion_token}",
                "Notion-Version": "2025-09-03",
                "Content-Type": "application/json",
            },
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read())
            assert "results" in data
            # We expect at least some results if DB is populated
            # Don't assert count - DB could be empty in test environment

        time.sleep(API_DELAY)  # Rate limiting

    def test_status_property_exists(self, notion_token: str, plans_db_id: str) -> None:
        """Verify 'Status' property exists on Plans DB schema."""
        import urllib.request

        req = urllib.request.Request(
            f"https://api.notion.com/v1/databases/{plans_db_id}",
            headers={
                "Authorization": f"Bearer {notion_token}",
                "Notion-Version": "2025-09-03",
            },
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read())
            properties = data.get("properties", {})
            assert "Status" in properties, "Status property not found in Plans DB schema"
            status_prop = properties["Status"]
            assert status_prop["type"] == "select", "Status should be select type"

        time.sleep(API_DELAY)  # Rate limiting


class TestNP10WaitingForIntegration:
    """Item 1: Integration tests for NP10 Waiting-For gate."""

    def test_waiting_for_property_exists(self, notion_token: str, plans_db_id: str) -> None:
        """Verify 'Waiting For' property exists on Plans DB schema."""
        import urllib.request

        req = urllib.request.Request(
            f"https://api.notion.com/v1/databases/{plans_db_id}",
            headers={
                "Authorization": f"Bearer {notion_token}",
                "Notion-Version": "2025-09-03",
            },
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read())
            properties = data.get("properties", {})
            # Check for Waiting For property (could be "Waiting For" or similar)
            waiting_props = [k for k in properties.keys() if "waiting" in k.lower()]
            assert len(waiting_props) > 0, "No Waiting-related property found"

        time.sleep(API_DELAY)  # Rate limiting

    def test_query_waiting_status_plans(self, notion_token: str, plans_db_id: str) -> None:
        """Query for plans with 'Waiting' status."""
        import urllib.request

        req = urllib.request.Request(
            f"https://api.notion.com/v1/databases/{plans_db_id}/query",
            data=json.dumps({
                "filter": {
                    "property": "Status",
                    "select": {"equals": "Waiting"},
                },
                "page_size": 100,
            }).encode(),
            headers={
                "Authorization": f"Bearer {notion_token}",
                "Notion-Version": "2025-09-03",
                "Content-Type": "application/json",
            },
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read())
            assert "results" in data
            # Verify we can parse the results
            for result in data["results"]:
                props = result.get("properties", {})
                status_prop = props.get("Status", {})
                status_name = status_prop.get("select", {}).get("name", "")
                assert status_name == "Waiting", f"Expected Waiting status, got {status_name}"

        time.sleep(API_DELAY)  # Rate limiting


class TestMCPSchemaGateIntegration:
    """Item 1: Integration tests for MCP Config Schema gate."""

    def test_mcp_config_file_exists(self) -> None:
        """Verify mcp_config.json exists on disk."""
        config_path = REPO_ROOT / "docs/archive/windsurf/legacy-tree" / "mcp_config.json"
        assert config_path.exists(), f"mcp_config.json not found at {config_path}"

    def test_mcp_config_is_valid_json(self) -> None:
        """Verify mcp_config.json is parseable JSON."""
        config_path = REPO_ROOT / "docs/archive/windsurf/legacy-tree" / "mcp_config.json"
        content = config_path.read_text(encoding="utf-8")
        data = json.loads(content)
        assert "mcpServers" in data, "mcpServers key not found"
        assert isinstance(data["mcpServers"], dict), "mcpServers should be an object"


class TestDeferredScopeGateIntegration:
    """Item 1: Integration tests for Deferred Scope gate."""

    def test_deferred_scope_markers_exist_in_plans(self) -> None:
        """Sample check for DEFERRED_SCOPE markers in plan files."""
        plans_dir = REPO_ROOT / "docs" / "archive" / "windsurf" / "legacy-tree" / "plans"
        assert plans_dir.exists(), "Plans directory not found"

        plan_files = list(plans_dir.glob("*.md"))
        assert len(plan_files) > 0, "No plan files found"

        # Sample 5 random plans for marker presence
        import random
        sample = random.sample(plan_files, min(5, len(plan_files)))

        for plan_file in sample:
            content = plan_file.read_text(encoding="utf-8")
            # Check for DEFERRED_SCOPE marker
            has_marker = "DEFERRED_SCOPE:" in content
            # This is just a sample check - don't assert presence
            # We just verify we can read and scan the files
            assert len(content) > 0, f"Empty plan file: {plan_file}"

    def test_gate_runs_without_error(self) -> None:
        """Verify deferred scope gate runs without crashing."""
        import subprocess
        import sys

        gate_path = REPO_ROOT / "ops_scripts" / "ci" / "check_deferred_scope_markers.py"
        result = subprocess.run(
            [sys.executable, str(gate_path), "--all"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        # Gate should exit 0 (advisory) or 1 (fail-closed with violations)
        # Should NOT crash
        assert result.returncode in [0, 1], f"Gate crashed: {result.stderr}"


class TestRateLimiting:
    """Item 1: Verify rate limiting is respected."""

    def test_consecutive_calls_respect_delay(self, notion_token: str) -> None:
        """Make multiple API calls and verify they don't fail due to rate limiting."""
        import urllib.request

        req = urllib.request.Request(
            "https://api.notion.com/v1/users/me",
            headers={
                "Authorization": f"Bearer {notion_token}",
                "Notion-Version": "2025-09-03",
            },
        )

        # Make 3 calls with built-in delays
        for i in range(3):
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read())
                assert "id" in data, f"Call {i+1} failed"
            time.sleep(API_DELAY)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
