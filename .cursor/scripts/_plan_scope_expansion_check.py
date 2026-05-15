"""
_plan_scope_expansion_check.py — Pure logic for detecting plan scope drift and authorization.

Exports:
    - AuthorizationState: Dataclass tracking authorization state for a plan session
    - is_authorized_for_scope(): Check if work is authorized
    - detect_retroactive_authorization(): Detect work-before-auth patterns
    - parse_discovered_scope(): Parse DISCOVERED_SCOPE markers
    - parse_authorization_decision(): Parse AUTHORIZATION_DECISION markers
    - parse_scope_expansion(): Parse SCOPE_EXPANSION markers
    - AuthorizationResult: Result of authorization check

Fail policy: All functions return Result objects; never raise publicly.
"""
from __future__ import annotations

import dataclasses
import re
from datetime import datetime, timedelta, timezone
from typing import NamedTuple


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_AUTH_RECENCY_SEC = 300  # 5 minutes
MIN_FILES_FOR_AUDIT = 3

# Decision types
DECISION_ACCEPTED = "ACCEPTED"
DECISION_DEFERRED = "DEFERRED"
DECISION_SPLIT = "SPLIT_TO_NEW_PLAN"
DECISION_REJECTED = "REJECTED"

VALID_DECISIONS = {DECISION_ACCEPTED, DECISION_DEFERRED, DECISION_SPLIT, DECISION_REJECTED}

# Reason codes
REASON_OK = "AUTHORIZED"
REASON_MISSING_DISCOVERED = "MISSING_DISCOVERED_SCOPE"
REASON_MISSING_AUTHORIZATION = "MISSING_AUTHORIZATION_DECISION"
REASON_RETROACTIVE = "RETROACTIVE_AUTHORIZATION_DETECTED"
REASON_DEFERRED = "DEFERRED_NOT_AUTHORIZED"
REASON_SPLIT = "SPLIT_TO_NEW_PLAN_NOT_AUTHORIZED"
REASON_REJECTED = "REJECTED_NOT_AUTHORIZED"
REASON_EXPIRED = "AUTHORIZATION_EXPIRED"
REASON_MALFORMED_MARKER = "MALFORMED_MARKER"


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclasses.dataclass(frozen=True)
class DiscoveredScope:
    """Represents a DISCOVERED_SCOPE marker."""
    plan_slug: str
    wave: int
    phase: int
    gap_description: str
    impact: str
    timestamp: datetime
    raw: str


@dataclasses.dataclass(frozen=True)
class AuthorizationDecision:
    """Represents an AUTHORIZATION_DECISION marker."""
    plan_slug: str
    decision: str  # ACCEPTED | DEFERRED | SPLIT_TO_NEW_PLAN | REJECTED
    authorized_by: str
    decisive_reason: str
    timestamp: datetime
    raw: str


@dataclasses.dataclass(frozen=True)
class ScopeExpansion:
    """Represents a SCOPE_EXPANSION marker."""
    plan_slug: str
    reason: str
    added: str
    authorized: bool
    timestamp: datetime
    raw: str


@dataclasses.dataclass(frozen=True)
class WorkEvidence:
    """Evidence of work performed."""
    files_modified: list[str]
    files_created: list[str]
    timestamp: datetime  # When the work was observed


@dataclasses.dataclass(frozen=True)
class AuthorizationResult:
    """Result of authorization check."""
    authorized: bool
    reason: str
    discovered_scope: DiscoveredScope | None
    authorization_decision: AuthorizationDecision | None
    message: str


@dataclasses.dataclass
class AuthorizationState:
    """Tracks authorization state for a plan session.
    
    Usage:
        state = AuthorizationState(plan_slug="foo-abc123")
        state.add_discovered_scope(marker_text, timestamp)
        state.add_authorization_decision(marker_text, timestamp)
        
        result = state.is_authorized_for_scope(work_evidence)
    """
    plan_slug: str
    discovered_scopes: list[DiscoveredScope] = dataclasses.field(default_factory=list)
    authorization_decisions: list[AuthorizationDecision] = dataclasses.field(default_factory=list)
    scope_expansions: list[ScopeExpansion] = dataclasses.field(default_factory=list)
    recency_window_sec: int = DEFAULT_AUTH_RECENCY_SEC
    
    def add_discovered_scope(self, marker_text: str, timestamp: datetime | None = None) -> DiscoveredScope | None:
        """Parse and add a DISCOVERED_SCOPE marker."""
        parsed = parse_discovered_scope(marker_text, timestamp)
        if parsed and parsed.plan_slug == self.plan_slug:
            self.discovered_scopes.append(parsed)
            return parsed
        return None
    
    def add_authorization_decision(self, marker_text: str, timestamp: datetime | None = None) -> AuthorizationDecision | None:
        """Parse and add an AUTHORIZATION_DECISION marker."""
        parsed = parse_authorization_decision(marker_text, timestamp)
        if parsed and parsed.plan_slug == self.plan_slug:
            self.authorization_decisions.append(parsed)
            return parsed
        return None
    
    def add_scope_expansion(self, marker_text: str, timestamp: datetime | None = None) -> ScopeExpansion | None:
        """Parse and add a SCOPE_EXPANSION marker."""
        parsed = parse_scope_expansion(marker_text, timestamp)
        if parsed and parsed.plan_slug == self.plan_slug:
            self.scope_expansions.append(parsed)
            return parsed
        return None
    
    def is_authorized_for_scope(
        self,
        work_evidence: WorkEvidence,
        require_expansion_marker: bool = False
    ) -> AuthorizationResult:
        """Check if work is authorized for scope expansion.
        
        Args:
            work_evidence: Evidence of work performed
            require_expansion_marker: If True, also require SCOPE_EXPANSION marker
            
        Returns:
            AuthorizationResult with authorized=True only if ACCEPTED decision exists
            and no retroactive authorization detected.
        """
        # Check for retroactive authorization (work before markers)
        retroactive = detect_retroactive_authorization(
            work_evidence,
            self.discovered_scopes,
            self.authorization_decisions
        )
        if retroactive:
            return AuthorizationResult(
                authorized=False,
                reason=REASON_RETROACTIVE,
                discovered_scope=None,
                authorization_decision=None,
                message=f"RETROACTIVE_AUTHORIZATION_DETECTED: work at {work_evidence.timestamp.isoformat()} precedes authorization markers"
            )
        
        # Must have at least one DISCOVERED_SCOPE
        if not self.discovered_scopes:
            return AuthorizationResult(
                authorized=False,
                reason=REASON_MISSING_DISCOVERED,
                discovered_scope=None,
                authorization_decision=None,
                message="No DISCOVERED_SCOPE marker found"
            )
        
        # Must have at least one AUTHORIZATION_DECISION
        if not self.authorization_decisions:
            return AuthorizationResult(
                authorized=False,
                reason=REASON_MISSING_AUTHORIZATION,
                discovered_scope=None,
                authorization_decision=None,
                message="No AUTHORIZATION_DECISION marker found"
            )
        
        # Get the most recent authorization decision
        latest_decision = max(self.authorization_decisions, key=lambda d: d.timestamp)
        
        # Check recency window
        time_since_auth = work_evidence.timestamp - latest_decision.timestamp
        if time_since_auth.total_seconds() > self.recency_window_sec:
            return AuthorizationResult(
                authorized=False,
                reason=REASON_EXPIRED,
                discovered_scope=self.discovered_scopes[-1] if self.discovered_scopes else None,
                authorization_decision=latest_decision,
                message=f"Authorization expired: {time_since_auth.total_seconds():.0f}s > {self.recency_window_sec}s window"
            )
        
        # Decision-specific handling
        if latest_decision.decision == DECISION_ACCEPTED:
            if require_expansion_marker:
                # Check for SCOPE_EXPANSION marker with authorized="yes"
                has_expansion = any(
                    exp.authorized for exp in self.scope_expansions
                    if exp.timestamp >= latest_decision.timestamp
                )
                if not has_expansion:
                    return AuthorizationResult(
                        authorized=False,
                        reason="MISSING_SCOPE_EXPANSION_MARKER",
                        discovered_scope=self.discovered_scopes[-1],
                        authorization_decision=latest_decision,
                        message="ACCEPTED but no SCOPE_EXPANSION marker with authorized='yes'"
                    )
            
            return AuthorizationResult(
                authorized=True,
                reason=REASON_OK,
                discovered_scope=self.discovered_scopes[-1],
                authorization_decision=latest_decision,
                message=f"Authorized: {latest_decision.decision} by {latest_decision.authorized_by}"
            )
        
        elif latest_decision.decision == DECISION_DEFERRED:
            return AuthorizationResult(
                authorized=False,
                reason=REASON_DEFERRED,
                discovered_scope=self.discovered_scopes[-1],
                authorization_decision=latest_decision,
                message=f"Not authorized: DEFERRED — scope valid but time/volume gated"
            )
        
        elif latest_decision.decision == DECISION_SPLIT:
            return AuthorizationResult(
                authorized=False,
                reason=REASON_SPLIT,
                discovered_scope=self.discovered_scopes[-1],
                authorization_decision=latest_decision,
                message=f"Not authorized: SPLIT_TO_NEW_PLAN — scope moved to new plan"
            )
        
        elif latest_decision.decision == DECISION_REJECTED:
            return AuthorizationResult(
                authorized=False,
                reason=REASON_REJECTED,
                discovered_scope=self.discovered_scopes[-1],
                authorization_decision=latest_decision,
                message=f"Not authorized: REJECTED — scope is gold-plating or off-charter"
            )
        
        # Unknown decision type
        return AuthorizationResult(
            authorized=False,
            reason="UNKNOWN_DECISION",
            discovered_scope=self.discovered_scopes[-1],
            authorization_decision=latest_decision,
            message=f"Unknown decision type: {latest_decision.decision}"
        )


# ---------------------------------------------------------------------------
# Parser Functions
# ---------------------------------------------------------------------------

# Regex patterns for markers
_DISCOVERED_SCOPE_RE = re.compile(
    r'DISCOVERED_SCOPE:\s*'
    r'plan=(?P<slug>[\w-]+)\s+'
    r'wave=(?P<wave>\d+)\s+'
    r'phase=(?P<phase>\d+)\s+'
    r'gap="(?P<gap>[^"]*)"\s+'
    r'impact="(?P<impact>[^"]*)"'
)

_AUTHORIZATION_DECISION_RE = re.compile(
    r'AUTHORIZATION_DECISION:\s*'
    r'plan=(?P<slug>[\w-]+)\s+'
    r'decision=(?P<decision>\w+(?:_\w+)*)\s+'
    r'authorized_by=(?P<by>\w+)\s+'
    r'decisive_reason="(?P<reason>[^"]*)"'
)

_SCOPE_EXPANSION_RE = re.compile(
    r'SCOPE_EXPANSION:\s*'
    r'plan=(?P<slug>[\w-]+)\s+'
    r'reason="(?P<reason>[^"]*)"\s+'
    r'added="(?P<added>[^"]*)"'
    r'(?:\s+authorized="(?P<auth>yes|no)")?'
)


def parse_discovered_scope(marker_text: str, timestamp: datetime | None = None) -> DiscoveredScope | None:
    """Parse a DISCOVERED_SCOPE marker.
    
    Format: DISCOVERED_SCOPE: plan=<slug-6hex> wave=<N> phase=<M> gap="<desc>" impact="<sev>"
    """
    m = _DISCOVERED_SCOPE_RE.match(marker_text.strip())
    if not m:
        return None
    
    return DiscoveredScope(
        plan_slug=m.group('slug'),
        wave=int(m.group('wave')),
        phase=int(m.group('phase')),
        gap_description=m.group('gap'),
        impact=m.group('impact'),
        timestamp=timestamp or datetime.now(timezone.utc),
        raw=marker_text
    )


def parse_authorization_decision(marker_text: str, timestamp: datetime | None = None) -> AuthorizationDecision | None:
    """Parse an AUTHORIZATION_DECISION marker.
    
    Format: AUTHORIZATION_DECISION: plan=<slug> decision=<TYPE> authorized_by=<who> decisive_reason="<why>"
    """
    m = _AUTHORIZATION_DECISION_RE.match(marker_text.strip())
    if not m:
        return None
    
    decision = m.group('decision')
    # Normalize decision names
    if decision not in VALID_DECISIONS:
        # Try common aliases
        aliases = {
            'ACCEPT': DECISION_ACCEPTED,
            'DEFER': DECISION_DEFERRED,
            'SPLIT': DECISION_SPLIT,
            'REJECT': DECISION_REJECTED,
        }
        decision = aliases.get(decision, decision)
    
    return AuthorizationDecision(
        plan_slug=m.group('slug'),
        decision=decision,
        authorized_by=m.group('by'),
        decisive_reason=m.group('reason'),
        timestamp=timestamp or datetime.now(timezone.utc),
        raw=marker_text
    )


def parse_scope_expansion(marker_text: str, timestamp: datetime | None = None) -> ScopeExpansion | None:
    """Parse a SCOPE_EXPANSION marker.
    
    Format: SCOPE_EXPANSION: plan=<slug> reason="<summary>" added="<waves/phases>" authorized="yes"
    """
    m = _SCOPE_EXPANSION_RE.match(marker_text.strip())
    if not m:
        return None
    
    authorized_str = m.group('auth') or 'no'
    
    return ScopeExpansion(
        plan_slug=m.group('slug'),
        reason=m.group('reason'),
        added=m.group('added'),
        authorized=authorized_str.lower() == 'yes',
        timestamp=timestamp or datetime.now(timezone.utc),
        raw=marker_text
    )


# ---------------------------------------------------------------------------
# Retroactive Authorization Detection
# ---------------------------------------------------------------------------

def detect_retroactive_authorization(
    work_evidence: WorkEvidence,
    discovered_scopes: list[DiscoveredScope],
    authorization_decisions: list[AuthorizationDecision]
) -> bool:
    """Detect if work occurred before authorization markers.
    
    This is the critical negative-control: work-before-auth indicates
    retroactive authorization (plan update as post-hoc rationalization).
    
    Returns True if work timestamp precedes any authorization marker.
    """
    work_time = work_evidence.timestamp
    
    # Check if work precedes all DISCOVERED_SCOPE markers
    for scope in discovered_scopes:
        if work_time < scope.timestamp:
            # Work happened before scope was even discovered
            return True
    
    # Check if work precedes all AUTHORIZATION_DECISION markers
    for decision in authorization_decisions:
        if work_time < decision.timestamp:
            # Work happened before authorization was granted
            return True
    
    return False


def check_marker_order(
    work_evidence: WorkEvidence,
    discovered_scopes: list[DiscoveredScope],
    authorization_decisions: list[AuthorizationDecision]
) -> dict:
    """Detailed check of marker ordering for diagnostic purposes.
    
    Returns dict with timeline analysis.
    """
    events = []
    
    # Add work event
    events.append({
        'type': 'work',
        'timestamp': work_evidence.timestamp,
        'details': f"{len(work_evidence.files_modified)} modified, {len(work_evidence.files_created)} created"
    })
    
    # Add scope discoveries
    for scope in discovered_scopes:
        events.append({
            'type': 'discovered_scope',
            'timestamp': scope.timestamp,
            'details': f"W{scope.wave}.P{scope.phase}: {scope.gap_description[:50]}..."
        })
    
    # Add authorization decisions
    for decision in authorization_decisions:
        events.append({
            'type': 'authorization_decision',
            'timestamp': decision.timestamp,
            'details': f"{decision.decision} by {decision.authorized_by}"
        })
    
    # Sort by timestamp
    events.sort(key=lambda e: e['timestamp'])
    
    # Check for retroactive pattern
    work_index = next((i for i, e in enumerate(events) if e['type'] == 'work'), -1)
    first_auth_index = next((i for i, e in enumerate(events) if e['type'] == 'authorization_decision'), -1)
    
    return {
        'timeline': events,
        'retroactive_detected': work_index >= 0 and first_auth_index >= 0 and work_index < first_auth_index,
        'work_first': work_index == 0 if events else False
    }


# ---------------------------------------------------------------------------
# Convenience Functions
# ---------------------------------------------------------------------------

def create_authorization_state(
    plan_slug: str,
    marker_texts: list[str],
    timestamps: list[datetime] | None = None
) -> AuthorizationState:
    """Create an AuthorizationState from a list of markers.
    
    Convenience function for parsing a response/session worth of markers.
    """
    state = AuthorizationState(plan_slug=plan_slug)
    
    for i, text in enumerate(marker_texts):
        ts = timestamps[i] if timestamps and i < len(timestamps) else None
        
        # Try each parser
        if parse_discovered_scope(text, ts):
            state.add_discovered_scope(text, ts)
        elif parse_authorization_decision(text, ts):
            state.add_authorization_decision(text, ts)
        elif parse_scope_expansion(text, ts):
            state.add_scope_expansion(text, ts)
    
    return state


@dataclasses.dataclass(frozen=True)
class ScopeAuthorizationResult:
    """Result of scope authorization check — simplified API for W3 hook consumption.
    
    This is the primary return type for check_scope_authorization(), designed
    for easy consumption by post-cursor_agent hooks without internal state knowledge.
    """
    authorized: bool
    reason: str  # REASON_OK, REASON_MISSING_DISCOVERED, REASON_RETROACTIVE, etc.
    message: str  # Human-readable explanation
    decision: str | None = None  # ACCEPTED, DEFERRED, SPLIT, REJECTED, or None
    discovered_gap: str | None = None  # Gap description if DISCOVERED_SCOPE found
    
    # Advisory vs strict mode behavior
    @property
    def should_warn(self) -> bool:
        """True if advisory mode should emit a warning."""
        return not self.authorized and self.reason != REASON_OK
    
    @property
    def should_block(self) -> bool:
        """True if strict mode should block (exit 2)."""
        return not self.authorized and self.reason in {
            REASON_RETROACTIVE, REASON_MISSING_AUTHORIZATION, REASON_EXPIRED
        }


def check_scope_authorization(
    plan_id: str,
    changed_files: list[str],
    markers: list[str],
    now: datetime | None = None,
    strict: bool = False,
    recency_window_sec: int = DEFAULT_AUTH_RECENCY_SEC
) -> ScopeAuthorizationResult:
    """Check if scope expansion is authorized — primary API for W3 hook.
    
    W3 should NOT re-implement marker parsing. Call this function.
    
    Args:
        plan_id: Plan slug (e.g., "foo-abc123")
        changed_files: List of file paths modified/created (relative or absolute)
        markers: List of marker strings from Cursor Agent response text
        now: Current timestamp (defaults to UTC now)
        strict: If True, treats missing/expired auth as blocking (not just advisory)
        recency_window_sec: Authorization validity window (default 300s)
        
    Returns:
        ScopeAuthorizationResult with authorized flag, reason code, and message
        
    Example:
        result = check_scope_authorization(
            plan_id="my-plan-abc123",
            changed_files=[".cursor/rules/new-rule.md"],
            markers=[
                'DISCOVERED_SCOPE: plan=my-plan-abc123 wave=2 phase=3 gap="new rule needed" impact="High"',
                'AUTHORIZATION_DECISION: plan=my-plan-abc123 decision=ACCEPTED authorized_by=user decisive_reason="Critical path"',
            ],
            strict=False
        )
        if not result.authorized:
            print(f"Warning: {result.message}")
    """
    now = now or datetime.now(timezone.utc)
    
    # Build state from markers (W2 handles all parsing)
    state = AuthorizationState(plan_slug=plan_id, recency_window_sec=recency_window_sec)
    
    for marker in markers:
        state.add_discovered_scope(marker, now)
        state.add_authorization_decision(marker, now)
        state.add_scope_expansion(marker, now)
    
    # Build work evidence
    work_evidence = WorkEvidence(
        files_modified=changed_files,
        files_created=[],  # W3 doesn't track created separately
        timestamp=now
    )
    
    # Get detailed result from W2 logic
    auth_result = state.is_authorized_for_scope(work_evidence)
    
    # Map to simplified ScopeAuthorizationResult
    decision = None
    if auth_result.authorization_decision:
        decision = auth_result.authorization_decision.decision
    
    discovered_gap = None
    if auth_result.discovered_scope:
        discovered_gap = auth_result.discovered_scope.gap_description
    
    return ScopeAuthorizationResult(
        authorized=auth_result.authorized,
        reason=auth_result.reason,
        message=auth_result.message,
        decision=decision,
        discovered_gap=discovered_gap
    )


def quick_authorization_check(
    plan_slug: str,
    work_files_modified: list[str],
    work_files_created: list[str],
    marker_texts: list[str],
    work_timestamp: datetime | None = None
) -> AuthorizationResult:
    """Quick check without building state manually.
    
    DEPRECATED: Use check_scope_authorization() for W3 hook integration.
    This function kept for backward compatibility with existing tests.
    
    Args:
        plan_slug: The plan identifier
        work_files_modified: List of modified file paths
        work_files_created: List of created file paths
        marker_texts: List of marker strings from response
        work_timestamp: When work occurred (defaults to now)
        
    Returns:
        AuthorizationResult
    """
    state = create_authorization_state(plan_slug, marker_texts)
    
    work_evidence = WorkEvidence(
        files_modified=work_files_modified,
        files_created=work_files_created,
        timestamp=work_timestamp or datetime.now(timezone.utc)
    )
    
    return state.is_authorized_for_scope(work_evidence)
