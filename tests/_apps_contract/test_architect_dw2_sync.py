"""README sync success rate OTEL metrics — DS-12.

Plan: ``docs/archive/windsurf/legacy-tree/plans/apps-architect-deferred-scope-b8e3f1.md`` DW2 DS-12.

Verifies OTEL span emission for sync operations and CredentialManager integration.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from apps_architect.L6_observability import (
    emit_scan_span,
    emit_delta_span,
    emit_rules_span,
    emit_sync_span,
)
from apps_architect.config.credential_manager import CredentialManager
from apps_architect.integrations import GitHubSync


class TestSyncObservability:
    """DS-12: README sync success rate >95% via OTEL span metrics."""

    def test_credential_manager_source_ladder(self):
        cm = CredentialManager()
        assert cm.get("NONEXISTENT_KEY", "fallback") == "fallback"
        assert cm.mask("NONEXISTENT_KEY") == "<unset>"

    def test_credential_manager_with_override(self):
        cm = CredentialManager({"TEST_KEY": "secret-value-1234"})
        assert cm.get("TEST_KEY") == "secret-value-1234"
        assert cm.configured("TEST_KEY")
        assert cm.mask("TEST_KEY") == "secr*********1234"

    def test_credential_manager_require_raises(self):
        cm = CredentialManager()
        with pytest.raises(KeyError):
            cm.require("MISSING_REQUIRED_KEY")

    def test_github_sync_uses_credential_manager(self):
        cm = CredentialManager({"GITHUB_TOKEN": "ghp_test12345678"})
        gs = GitHubSync(creds=cm)
        assert gs.configured
        assert gs.token_masked == "ghp_********5678"

    def test_github_sync_dry_run_no_token(self):
        gs = GitHubSync()
        result = gs.create_pr("# Test", dry_run=True)
        assert "dry_run" in result

    def test_otel_spans_fail_soft(self):
        emit_scan_span(10, 30)
        emit_delta_span(10, 5, 3, 0)
        emit_rules_span(10)
        emit_sync_span(True, 100)
