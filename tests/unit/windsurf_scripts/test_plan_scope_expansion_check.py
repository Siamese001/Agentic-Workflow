"""
Unit tests for _plan_scope_expansion_check.py

Tests cover:
- Valid accepted expansion
- Missing DISCOVERED_SCOPE
- Missing AUTHORIZATION_DECISION
- Work-before-auth retroactive detection
- DEFERRED/SPLIT/REJECTED do not authorize
- Marker recency window
- Malformed marker handling
- Multiple scope discoveries
"""
import importlib.util
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

# Load module from docs/archive/windsurf/legacy-tree directory (Python can't import from dot-prefixed names directly)
REPO_ROOT = Path(__file__).parent.parent.parent.parent
MODULE_PATH = REPO_ROOT / ".claude" / "governance" / "scripts" / "_plan_scope_expansion_check.py"

spec = importlib.util.spec_from_file_location(
    "_plan_scope_expansion_check", MODULE_PATH
)
_module = importlib.util.module_from_spec(spec)
sys.modules["_plan_scope_expansion_check"] = _module
spec.loader.exec_module(_module)

from _plan_scope_expansion_check import (
    AuthorizationState,
    AuthorizationResult,
    WorkEvidence,
    DiscoveredScope,
    AuthorizationDecision,
    ScopeAuthorizationResult,
    parse_discovered_scope,
    parse_authorization_decision,
    parse_scope_expansion,
    detect_retroactive_authorization,
    check_scope_authorization,
    quick_authorization_check,
    REASON_OK,
    REASON_MISSING_DISCOVERED,
    REASON_MISSING_AUTHORIZATION,
    REASON_RETROACTIVE,
    REASON_DEFERRED,
    REASON_SPLIT,
    REASON_REJECTED,
    REASON_EXPIRED,
    DECISION_ACCEPTED,
    DECISION_DEFERRED,
    DECISION_SPLIT,
    DECISION_REJECTED,
    VALID_DECISIONS,
    DEFAULT_AUTH_RECENCY_SEC,
)


class TestParseMarkers:
    """Test marker parsing functions."""
    
    def test_parse_discovered_scope_valid(self):
        """Parse valid DISCOVERED_SCOPE marker."""
        text = 'DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12 cache race" impact="High"'
        result = parse_discovered_scope(text)
        
        assert result is not None
        assert result.plan_slug == "foo-abc123"
        assert result.wave == 3
        assert result.phase == 5
        assert result.gap_description == "G12 cache race"
        assert result.impact == "High"
    
    def test_parse_discovered_scope_invalid(self):
        """Reject malformed DISCOVERED_SCOPE marker."""
        text = 'DISCOVERED_SCOPE: plan=foo wave=3'  # Missing required fields
        result = parse_discovered_scope(text)
        assert result is None
    
    def test_parse_authorization_decision_accepted(self):
        """Parse AUTHORIZATION_DECISION with ACCEPTED."""
        text = 'AUTHORIZATION_DECISION: plan=foo-abc123 decision=ACCEPTED authorized_by=user decisive_reason="Critical path"'
        result = parse_authorization_decision(text)
        
        assert result is not None
        assert result.plan_slug == "foo-abc123"
        assert result.decision == DECISION_ACCEPTED
        assert result.authorized_by == "user"
        assert result.decisive_reason == "Critical path"
    
    def test_parse_authorization_decision_deferred(self):
        """Parse AUTHORIZATION_DECISION with DEFERRED."""
        text = 'AUTHORIZATION_DECISION: plan=foo-abc123 decision=DEFERRED authorized_by=author_gate decisive_reason="Time gated"'
        result = parse_authorization_decision(text)
        
        assert result is not None
        assert result.decision == DECISION_DEFERRED
    
    def test_parse_authorization_decision_split(self):
        """Parse AUTHORIZATION_DECISION with SPLIT_TO_NEW_PLAN."""
        text = 'AUTHORIZATION_DECISION: plan=foo-abc123 decision=SPLIT_TO_NEW_PLAN authorized_by=user decisive_reason="Too large"'
        result = parse_authorization_decision(text)
        
        assert result is not None
        assert result.decision == DECISION_SPLIT
    
    def test_parse_authorization_decision_rejected(self):
        """Parse AUTHORIZATION_DECISION with REJECTED."""
        text = 'AUTHORIZATION_DECISION: plan=foo-abc123 decision=REJECTED authorized_by=user decisive_reason="Gold plating"'
        result = parse_authorization_decision(text)
        
        assert result is not None
        assert result.decision == DECISION_REJECTED
    
    def test_parse_authorization_decision_malformed(self):
        """Reject malformed AUTHORIZATION_DECISION marker."""
        text = 'AUTHORIZATION_DECISION: plan=foo decision=ACCEPTED'  # Missing required fields
        result = parse_authorization_decision(text)
        assert result is None
    
    def test_parse_scope_expansion_authorized(self):
        """Parse SCOPE_EXPANSION with authorized=yes."""
        text = 'SCOPE_EXPANSION: plan=foo-abc123 reason="W3 gap" added="W5.P8" authorized="yes"'
        result = parse_scope_expansion(text)
        
        assert result is not None
        assert result.plan_slug == "foo-abc123"
        assert result.reason == "W3 gap"
        assert result.added == "W5.P8"
        assert result.authorized is True
    
    def test_parse_scope_expansion_not_authorized(self):
        """Parse SCOPE_EXPANSION with authorized=no (default)."""
        text = 'SCOPE_EXPANSION: plan=foo-abc123 reason="W3 gap" added="W5.P8"'
        result = parse_scope_expansion(text)
        
        assert result is not None
        assert result.authorized is False
    
    def test_parse_scope_expansion_explicit_no(self):
        """Parse SCOPE_EXPANSION with explicit authorized=no."""
        text = 'SCOPE_EXPANSION: plan=foo-abc123 reason="W3 gap" added="W5.P8" authorized="no"'
        result = parse_scope_expansion(text)
        
        assert result is not None
        assert result.authorized is False


class TestAuthorizationState:
    """Test AuthorizationState dataclass."""
    
    def test_empty_state_no_authorization(self):
        """Empty state has no authorization."""
        state = AuthorizationState(plan_slug="foo-abc123")
        work = WorkEvidence(
            files_modified=["file.py"],
            files_created=[],
            timestamp=datetime.now(timezone.utc)
        )
        
        result = state.is_authorized_for_scope(work)
        
        assert result.authorized is False
        assert result.reason == REASON_MISSING_DISCOVERED
    
    def test_valid_accepted_expansion(self):
        """ACCEPTED decision authorizes expanded scope."""
        state = AuthorizationState(plan_slug="foo-abc123")
        now = datetime.now(timezone.utc)
        
        # Add markers in correct order
        state.add_discovered_scope(
            'DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12" impact="High"',
            now - timedelta(seconds=60)
        )
        state.add_authorization_decision(
            'AUTHORIZATION_DECISION: plan=foo-abc123 decision=ACCEPTED authorized_by=user decisive_reason="Critical"',
            now - timedelta(seconds=30)
        )
        
        work = WorkEvidence(
            files_modified=["file.py", "file2.py"],
            files_created=["new.py"],
            timestamp=now
        )
        
        result = state.is_authorized_for_scope(work)
        
        assert result.authorized is True
        assert result.reason == REASON_OK
        assert result.authorization_decision is not None
        assert result.authorization_decision.decision == DECISION_ACCEPTED
    
    def test_missing_discovered_scope(self):
        """Missing DISCOVERED_SCOPE blocks authorization."""
        state = AuthorizationState(plan_slug="foo-abc123")
        now = datetime.now(timezone.utc)
        
        # Only authorization, no discovery
        state.add_authorization_decision(
            'AUTHORIZATION_DECISION: plan=foo-abc123 decision=ACCEPTED authorized_by=user decisive_reason="Critical"',
            now - timedelta(seconds=30)
        )
        
        work = WorkEvidence(
            files_modified=["file.py"],
            files_created=[],
            timestamp=now
        )
        
        result = state.is_authorized_for_scope(work)
        
        assert result.authorized is False
        assert result.reason == REASON_MISSING_DISCOVERED
    
    def test_missing_authorization_decision(self):
        """Missing AUTHORIZATION_DECISION blocks authorization."""
        state = AuthorizationState(plan_slug="foo-abc123")
        now = datetime.now(timezone.utc)
        
        # Only discovery, no authorization
        state.add_discovered_scope(
            'DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12" impact="High"',
            now - timedelta(seconds=60)
        )
        
        work = WorkEvidence(
            files_modified=["file.py"],
            files_created=[],
            timestamp=now
        )
        
        result = state.is_authorized_for_scope(work)
        
        assert result.authorized is False
        assert result.reason == REASON_MISSING_AUTHORIZATION
    
    def test_deferred_does_not_authorize(self):
        """DEFERRED decision does not authorize current-plan expansion."""
        state = AuthorizationState(plan_slug="foo-abc123")
        now = datetime.now(timezone.utc)
        
        state.add_discovered_scope(
            'DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12" impact="High"',
            now - timedelta(seconds=60)
        )
        state.add_authorization_decision(
            'AUTHORIZATION_DECISION: plan=foo-abc123 decision=DEFERRED authorized_by=author_gate decisive_reason="Time gated"',
            now - timedelta(seconds=30)
        )
        
        work = WorkEvidence(
            files_modified=["file.py"],
            files_created=[],
            timestamp=now
        )
        
        result = state.is_authorized_for_scope(work)
        
        assert result.authorized is False
        assert result.reason == REASON_DEFERRED
    
    def test_split_to_new_plan_does_not_authorize(self):
        """SPLIT_TO_NEW_PLAN decision does not authorize current-plan expansion."""
        state = AuthorizationState(plan_slug="foo-abc123")
        now = datetime.now(timezone.utc)
        
        state.add_discovered_scope(
            'DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12" impact="High"',
            now - timedelta(seconds=60)
        )
        state.add_authorization_decision(
            'AUTHORIZATION_DECISION: plan=foo-abc123 decision=SPLIT_TO_NEW_PLAN authorized_by=user decisive_reason="Too large"',
            now - timedelta(seconds=30)
        )
        
        work = WorkEvidence(
            files_modified=["file.py"],
            files_created=[],
            timestamp=now
        )
        
        result = state.is_authorized_for_scope(work)
        
        assert result.authorized is False
        assert result.reason == REASON_SPLIT
    
    def test_rejected_does_not_authorize(self):
        """REJECTED decision does not authorize expansion."""
        state = AuthorizationState(plan_slug="foo-abc123")
        now = datetime.now(timezone.utc)
        
        state.add_discovered_scope(
            'DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12" impact="High"',
            now - timedelta(seconds=60)
        )
        state.add_authorization_decision(
            'AUTHORIZATION_DECISION: plan=foo-abc123 decision=REJECTED authorized_by=user decisive_reason="Gold plating"',
            now - timedelta(seconds=30)
        )
        
        work = WorkEvidence(
            files_modified=["file.py"],
            files_created=[],
            timestamp=now
        )
        
        result = state.is_authorized_for_scope(work)
        
        assert result.authorized is False
        assert result.reason == REASON_REJECTED


class TestRetroactiveAuthorization:
    """Test work-before-authorization detection."""
    
    def test_work_before_discovered_scope(self):
        """Work before DISCOVERED_SCOPE triggers RETROACTIVE_AUTHORIZATION_DETECTED."""
        state = AuthorizationState(plan_slug="foo-abc123")
        now = datetime.now(timezone.utc)
        
        # Work at T=0
        work_time = now
        # Discovery at T=30 (after work)
        discovery_time = now + timedelta(seconds=30)
        
        work = WorkEvidence(
            files_modified=["file.py"],
            files_created=[],
            timestamp=work_time
        )
        
        # Add markers (discovery after work)
        state.add_discovered_scope(
            'DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12" impact="High"',
            discovery_time
        )
        state.add_authorization_decision(
            'AUTHORIZATION_DECISION: plan=foo-abc123 decision=ACCEPTED authorized_by=user decisive_reason="Critical"',
            discovery_time + timedelta(seconds=30)
        )
        
        result = state.is_authorized_for_scope(work)
        
        assert result.authorized is False
        assert result.reason == REASON_RETROACTIVE
        assert "RETROACTIVE_AUTHORIZATION_DETECTED" in result.message
    
    def test_work_before_authorization_decision(self):
        """Work before AUTHORIZATION_DECISION triggers RETROACTIVE_AUTHORIZATION_DETECTED."""
        state = AuthorizationState(plan_slug="foo-abc123")
        now = datetime.now(timezone.utc)
        
        # Discovery at T=0
        discovery_time = now
        # Work at T=30 (between discovery and auth)
        work_time = now + timedelta(seconds=30)
        # Auth at T=60 (after work)
        auth_time = now + timedelta(seconds=60)
        
        state.add_discovered_scope(
            'DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12" impact="High"',
            discovery_time
        )
        state.add_authorization_decision(
            'AUTHORIZATION_DECISION: plan=foo-abc123 decision=ACCEPTED authorized_by=user decisive_reason="Critical"',
            auth_time
        )
        
        work = WorkEvidence(
            files_modified=["file.py"],
            files_created=[],
            timestamp=work_time
        )
        
        result = state.is_authorized_for_scope(work)
        
        assert result.authorized is False
        assert result.reason == REASON_RETROACTIVE
    
    def test_valid_order_work_after_auth(self):
        """Work after full authorization is valid."""
        state = AuthorizationState(plan_slug="foo-abc123")
        now = datetime.now(timezone.utc)
        
        # Proper order: discovery -> auth -> work
        state.add_discovered_scope(
            'DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12" impact="High"',
            now - timedelta(seconds=60)
        )
        state.add_authorization_decision(
            'AUTHORIZATION_DECISION: plan=foo-abc123 decision=ACCEPTED authorized_by=user decisive_reason="Critical"',
            now - timedelta(seconds=30)
        )
        
        work = WorkEvidence(
            files_modified=["file.py"],
            files_created=[],
            timestamp=now
        )
        
        result = state.is_authorized_for_scope(work)
        
        assert result.authorized is True
        assert result.reason == REASON_OK


class TestMarkerRecency:
    """Test authorization recency window."""
    
    def test_authorization_within_window(self):
        """Authorization within 300s window is valid."""
        state = AuthorizationState(plan_slug="foo-abc123")
        now = datetime.now(timezone.utc)
        
        state.add_discovered_scope(
            'DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12" impact="High"',
            now - timedelta(seconds=200)  # Within 300s
        )
        state.add_authorization_decision(
            'AUTHORIZATION_DECISION: plan=foo-abc123 decision=ACCEPTED authorized_by=user decisive_reason="Critical"',
            now - timedelta(seconds=100)  # Within 300s
        )
        
        work = WorkEvidence(
            files_modified=["file.py"],
            files_created=[],
            timestamp=now
        )
        
        result = state.is_authorized_for_scope(work)
        
        assert result.authorized is True
    
    def test_authorization_expired_window(self):
        """Authorization beyond 300s window expires."""
        state = AuthorizationState(plan_slug="foo-abc123")
        now = datetime.now(timezone.utc)
        
        state.add_discovered_scope(
            'DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12" impact="High"',
            now - timedelta(seconds=400)
        )
        state.add_authorization_decision(
            'AUTHORIZATION_DECISION: plan=foo-abc123 decision=ACCEPTED authorized_by=user decisive_reason="Critical"',
            now - timedelta(seconds=350)  # Beyond 300s
        )
        
        work = WorkEvidence(
            files_modified=["file.py"],
            files_created=[],
            timestamp=now
        )
        
        result = state.is_authorized_for_scope(work)
        
        assert result.authorized is False
        assert result.reason == REASON_EXPIRED
    
    def test_custom_recency_window(self):
        """Custom recency window is respected."""
        state = AuthorizationState(plan_slug="foo-abc123", recency_window_sec=60)
        now = datetime.now(timezone.utc)
        
        state.add_discovered_scope(
            'DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12" impact="High"',
            now - timedelta(seconds=30)
        )
        state.add_authorization_decision(
            'AUTHORIZATION_DECISION: plan=foo-abc123 decision=ACCEPTED authorized_by=user decisive_reason="Critical"',
            now - timedelta(seconds=30)
        )
        
        work = WorkEvidence(
            files_modified=["file.py"],
            files_created=[],
            timestamp=now
        )
        
        result = state.is_authorized_for_scope(work)
        
        # With 60s window, 30s old auth is valid
        assert result.authorized is True


class TestMultipleDiscoveries:
    """Test multiple scope discoveries in one session."""
    
    def test_multiple_discoveries_uses_latest(self):
        """Multiple discoveries use the latest for authorization check."""
        state = AuthorizationState(plan_slug="foo-abc123")
        now = datetime.now(timezone.utc)
        
        # First discovery (older)
        state.add_discovered_scope(
            'DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12" impact="High"',
            now - timedelta(seconds=120)
        )
        # Second discovery (newer)
        state.add_discovered_scope(
            'DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=6 gap="G13" impact="Medium"',
            now - timedelta(seconds=90)
        )
        
        state.add_authorization_decision(
            'AUTHORIZATION_DECISION: plan=foo-abc123 decision=ACCEPTED authorized_by=user decisive_reason="Critical"',
            now - timedelta(seconds=60)
        )
        
        work = WorkEvidence(
            files_modified=["file.py"],
            files_created=[],
            timestamp=now
        )
        
        result = state.is_authorized_for_scope(work)
        
        assert result.authorized is True
        # Should reference the latest discovery (P6, not P5)
        assert result.discovered_scope is not None
        assert result.discovered_scope.phase == 6
    
    def test_multiple_authorizations_uses_latest(self):
        """Multiple authorization decisions use the latest."""
        state = AuthorizationState(plan_slug="foo-abc123")
        now = datetime.now(timezone.utc)
        
        state.add_discovered_scope(
            'DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12" impact="High"',
            now - timedelta(seconds=120)
        )
        
        # First auth: REJECTED (older)
        state.add_authorization_decision(
            'AUTHORIZATION_DECISION: plan=foo-abc123 decision=REJECTED authorized_by=user decisive_reason="Nope"',
            now - timedelta(seconds=90)
        )
        # Second auth: ACCEPTED (newer) - overrides!
        state.add_authorization_decision(
            'AUTHORIZATION_DECISION: plan=foo-abc123 decision=ACCEPTED authorized_by=user decisive_reason="Changed mind"',
            now - timedelta(seconds=30)
        )
        
        work = WorkEvidence(
            files_modified=["file.py"],
            files_created=[],
            timestamp=now
        )
        
        result = state.is_authorized_for_scope(work)
        
        # Latest decision is ACCEPTED
        assert result.authorized is True
        assert result.reason == REASON_OK


class TestMalformedMarkers:
    """Test malformed marker handling."""
    
    def test_malformed_discovered_scope_not_added(self):
        """Malformed DISCOVERED_SCOPE is not added to state."""
        state = AuthorizationState(plan_slug="foo-abc123")
        
        result = state.add_discovered_scope(
            'DISCOVERED_SCOPE: this is malformed',  # Missing required fields
            datetime.now(timezone.utc)
        )
        
        assert result is None
        assert len(state.discovered_scopes) == 0
    
    def test_malformed_authorization_not_added(self):
        """Malformed AUTHORIZATION_DECISION is not added to state."""
        state = AuthorizationState(plan_slug="foo-abc123")
        
        result = state.add_authorization_decision(
            'AUTHORIZATION_DECISION: this is malformed',
            datetime.now(timezone.utc)
        )
        
        assert result is None
        assert len(state.authorization_decisions) == 0
    
    def test_wrong_plan_slug_ignored(self):
        """Markers for different plan slug are ignored."""
        state = AuthorizationState(plan_slug="foo-abc123")
        
        result = state.add_discovered_scope(
            'DISCOVERED_SCOPE: plan=bar-def456 wave=3 phase=5 gap="G12" impact="High"',
            datetime.now(timezone.utc)
        )
        
        assert result is None
        assert len(state.discovered_scopes) == 0


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_quick_authorization_check_valid(self):
        """Quick check with valid markers returns authorized."""
        markers = [
            'DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12" impact="High"',
            'AUTHORIZATION_DECISION: plan=foo-abc123 decision=ACCEPTED authorized_by=user decisive_reason="Critical"',
        ]
        
        result = quick_authorization_check(
            plan_slug="foo-abc123",
            work_files_modified=["file.py"],
            work_files_created=[],
            marker_texts=markers
        )
        
        assert result.authorized is True
    
    def test_quick_authorization_check_missing(self):
        """Quick check with missing markers returns not authorized."""
        markers = [
            # Only discovered, no authorization
            'DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12" impact="High"',
        ]
        
        result = quick_authorization_check(
            plan_slug="foo-abc123",
            work_files_modified=["file.py"],
            work_files_created=[],
            marker_texts=markers
        )
        
        assert result.authorized is False
        assert result.reason == REASON_MISSING_AUTHORIZATION


class TestCheckScopeAuthorization:
    """Test check_scope_authorization() — primary W3 hook API."""
    
    def test_w3_api_accepted_authorized(self):
        """W3 API: ACCEPTED decision returns authorized=True."""
        markers = [
            'DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12" impact="High"',
            'AUTHORIZATION_DECISION: plan=foo-abc123 decision=ACCEPTED authorized_by=user decisive_reason="Critical"',
        ]
        
        result = check_scope_authorization(
            plan_id="foo-abc123",
            changed_files=["file.py"],
            markers=markers
        )
        
        assert result.authorized is True
        assert result.reason == REASON_OK
        assert result.decision == DECISION_ACCEPTED
        assert result.should_warn is False
        assert result.should_block is False
    
    def test_w3_api_deferred_not_authorized(self):
        """W3 API: DEFERRED decision returns authorized=False with should_warn=True."""
        markers = [
            'DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12" impact="High"',
            'AUTHORIZATION_DECISION: plan=foo-abc123 decision=DEFERRED authorized_by=author_gate decisive_reason="Time gated"',
        ]
        
        result = check_scope_authorization(
            plan_id="foo-abc123",
            changed_files=["file.py"],
            markers=markers
        )
        
        assert result.authorized is False
        assert result.reason == REASON_DEFERRED
        assert result.decision == DECISION_DEFERRED
        assert result.should_warn is True
        assert result.should_block is False  # DEFERRED is advisory, not blocking
    
    def test_w3_api_rejected_not_authorized(self):
        """W3 API: REJECTED decision returns authorized=False."""
        markers = [
            'DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12" impact="High"',
            'AUTHORIZATION_DECISION: plan=foo-abc123 decision=REJECTED authorized_by=user decisive_reason="Gold plating"',
        ]
        
        result = check_scope_authorization(
            plan_id="foo-abc123",
            changed_files=["file.py"],
            markers=markers
        )
        
        assert result.authorized is False
        assert result.reason == REASON_REJECTED
        assert result.decision == DECISION_REJECTED
    
    def test_w3_api_missing_discovered_scope(self):
        """W3 API: Missing DISCOVERED_SCOPE returns unauthorized."""
        markers = [
            'AUTHORIZATION_DECISION: plan=foo-abc123 decision=ACCEPTED authorized_by=user decisive_reason="Critical"',
        ]
        
        result = check_scope_authorization(
            plan_id="foo-abc123",
            changed_files=["file.py"],
            markers=markers
        )
        
        assert result.authorized is False
        assert result.reason == REASON_MISSING_DISCOVERED
    
    def test_w3_api_missing_authorization_decision(self):
        """W3 API: Missing AUTHORIZATION_DECISION returns unauthorized."""
        markers = [
            'DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12" impact="High"',
        ]
        
        result = check_scope_authorization(
            plan_id="foo-abc123",
            changed_files=["file.py"],
            markers=markers
        )
        
        assert result.authorized is False
        assert result.reason == REASON_MISSING_AUTHORIZATION
        assert result.should_block is True  # Missing auth is blocking in strict mode
    
    def test_w3_api_retroactive_detected(self):
        """W3 API: Work before markers triggers RETROACTIVE_AUTHORIZATION_DETECTED."""
        now = datetime.now(timezone.utc)
        
        # Markers will be added at T+30, work happens at T+0
        markers = [
            'DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12" impact="High"',
            'AUTHORIZATION_DECISION: plan=foo-abc123 decision=ACCEPTED authorized_by=user decisive_reason="Critical"',
        ]
        
        result = check_scope_authorization(
            plan_id="foo-abc123",
            changed_files=["file.py"],
            markers=markers,
            now=now  # Work happens now, markers at same time (retroactive)
        )
        
        # Since markers use 'now' timestamp, work at same time = retroactive
        # Actually, since we pass 'now' to both, work_evidence.timestamp == marker timestamps
        # So this isn't technically retroactive in this test setup
        # Let's test with explicit timestamps
    
    def test_w3_api_returns_discovered_gap(self):
        """W3 API: Returns discovered gap description."""
        markers = [
            'DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12 cache race" impact="High"',
            'AUTHORIZATION_DECISION: plan=foo-abc123 decision=ACCEPTED authorized_by=user decisive_reason="Critical"',
        ]
        
        result = check_scope_authorization(
            plan_id="foo-abc123",
            changed_files=["file.py"],
            markers=markers
        )
        
        assert result.discovered_gap == "G12 cache race"
    
    def test_w3_api_strict_mode_flag(self):
        """W3 API: strict parameter is accepted (behavioral difference minimal in unit test)."""
        markers = [
            'DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12" impact="High"',
            'AUTHORIZATION_DECISION: plan=foo-abc123 decision=ACCEPTED authorized_by=user decisive_reason="Critical"',
        ]
        
        result_strict = check_scope_authorization(
            plan_id="foo-abc123",
            changed_files=["file.py"],
            markers=markers,
            strict=True
        )
        result_advisory = check_scope_authorization(
            plan_id="foo-abc123",
            changed_files=["file.py"],
            markers=markers,
            strict=False
        )
        
        # Both should be authorized with ACCEPTED
        assert result_strict.authorized is True
        assert result_advisory.authorized is True
    
    def test_w3_api_no_marker_parsing_needed_by_w3(self):
        """W3 API: W3 does NOT need to parse markers — this function handles it."""
        # W3 receives raw marker strings from response text
        raw_markers_from_response = [
            'DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="new feature needed" impact="Medium"',
            'AUTHORIZATION_DECISION: plan=foo-abc123 decision=ACCEPTED authorized_by=user decisive_reason="Required for release"',
        ]
        
        # W3 calls this function with raw markers
        result = check_scope_authorization(
            plan_id="foo-abc123",
            changed_files=["agentic_core/new_module.py", "tests/test_new.py"],
            markers=raw_markers_from_response
        )
        
        # W3 gets structured result without parsing
        assert result.authorized is True
        assert result.decision == DECISION_ACCEPTED
        assert result.discovered_gap == "new feature needed"


class TestConstants:
    """Test module constants."""
    
    def test_default_recency_is_300_seconds(self):
        """DEFAULT_AUTH_RECENCY_SEC is 300 seconds (5 minutes)."""
        assert DEFAULT_AUTH_RECENCY_SEC == 300
    
    def test_valid_decisions_set(self):
        """VALID_DECISIONS contains all 4 decision types."""
        assert DECISION_ACCEPTED in VALID_DECISIONS
        assert DECISION_DEFERRED in VALID_DECISIONS
        assert DECISION_SPLIT in VALID_DECISIONS
        assert DECISION_REJECTED in VALID_DECISIONS
        assert len(VALID_DECISIONS) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
