"""apps_research bridge for apps_lic managed workflow.

This module provides the AppsResearchBridge — the ONLY sanctioned interface
between apps_lic and apps_research. All managed-workflow research calls MUST
go through this bridge.

Design constraints
------------------
- Bridge uses the REGISTERED PUBLIC INTERFACE of apps_research only.
  Direct import of apps_research internals is FORBIDDEN.
- Bridge emits a trace line and audit_ref for every call (observability).
- Bridge wraps all apps_research exceptions and translates them into a
  structured ResearchResult so the dispatcher never sees raw exceptions.
- Bridge is STATELESS — no caching, no durable writes, no config mutations.
- Bridge is composition-only: no subprocess, no OS calls, no provider APIs.

Result shape
------------
AppsResearchBridge.fetch() always returns a ResearchResult dataclass.
ResearchResult.is_blocked / .is_stale / .evidence_items / .confidence_score
are the contract fields that ManagedWorkflowDispatcher reads.

Plan: .windsurf/plans/apps-lic-canonical-spine-wireup-e7c2a5.md W3 P8
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Public result contract (bridge output → dispatcher input)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EvidenceItem:
    """A single piece of research evidence returned by apps_research."""

    source_id: str
    label: str
    uri: str
    source_type: str  # "company_brief"|"job_description"|"recipient_brief"|"web"|"resume"
    field_ref: str    # which manifest field this evidence populates
    confidence: float = 0.0


@dataclass(frozen=True)
class ResearchResult:
    """Structured result from AppsResearchBridge.fetch().

    Dispatcher reads: is_blocked, is_stale, evidence_items, confidence_score.
    All other fields are for observability / manifest construction.
    """

    run_id: str
    trace_id: str
    request_id: str
    is_blocked: bool
    block_reason: str           # non-empty when is_blocked=True
    is_stale: bool
    age_days: float             # age of oldest evidence item
    evidence_items: tuple       # tuple[EvidenceItem, ...]
    confidence_score: float
    result_hash: str            # sha256 of serialized evidence (for manifest)
    jd_hash: str                # hash of job description evidence (if any)
    jd_uri: str                 # URI of job description (if any)
    company_brief_hash: str     # hash of company brief evidence (if any)
    fetch_duration_ms: float
    audit_ref: str              # trace ref for upstream research call


# ---------------------------------------------------------------------------
# Bridge
# ---------------------------------------------------------------------------


class AppsResearchBridge:
    """Sanctioned interface between apps_lic and apps_research.

    Usage:
        bridge = AppsResearchBridge(capability_ref="apps_research.v1")
        result = bridge.fetch(
            recipient_class="RECRUITER",
            recipient_name="Jane Smith",
            company_name="Acme Corp",
            job_title="Engineering Manager",
            channel="email",
            outreach_mode="cold",
            relationship_distance="cold",
            capability_ref="apps_research.v1",
            request_id="req-001",
            run_id="run-001",
            trace_id="tr-001",
        )
        # result is always ResearchResult — never raises
    """

    SUPPORTED_CAPABILITIES = frozenset({
        "apps_research.v1",
        "apps_research.v2",
    })

    def __init__(self, capability_ref: str = "apps_research.v1") -> None:
        self._capability_ref = capability_ref
        self._bridge_id = f"lic_research_bridge:{uuid.uuid4().hex[:8]}"

    def fetch(
        self,
        *,
        recipient_class: str,
        recipient_name: str,
        company_name: str,
        job_title: str,
        channel: str,
        outreach_mode: str,
        relationship_distance: str,
        capability_ref: str,
        request_id: str,
        run_id: str,
        trace_id: str,
    ) -> ResearchResult:
        """Invoke apps_research and return a structured ResearchResult.

        Never raises — all exceptions are wrapped into is_blocked=True with
        a descriptive block_reason. This ensures the dispatcher always gets
        a typed result it can classify.

        Args:
            recipient_class: Recipient classification (RECRUITER|HIRING_MANAGER|…).
            recipient_name: Human-readable name for trace/audit.
            company_name: Target company for research context.
            job_title: Target role (empty string for exploratory outreach).
            channel: "email"|"linkedin"|"text".
            outreach_mode: "cold"|"warm"|"referral"|"followup".
            relationship_distance: "cold"|"warm"|"referral"|"known".
            capability_ref: Registered capability token for apps_research.
            request_id: Caller's request ID (for trace propagation).
            run_id: Caller's run ID.
            trace_id: Caller's trace ID.

        Returns:
            ResearchResult — always. Never raises.
        """
        t_start = time.time() * 1000.0
        bridge_trace_id = f"bridge:{self._bridge_id}:{trace_id}"

        # ------------------------------------------------------------------
        # Capability check
        # ------------------------------------------------------------------
        if capability_ref not in self.SUPPORTED_CAPABILITIES:
            return ResearchResult(
                run_id=run_id,
                trace_id=bridge_trace_id,
                request_id=request_id,
                is_blocked=True,
                block_reason=(
                    f"Unsupported capability_ref={capability_ref!r}. "
                    f"Supported: {sorted(self.SUPPORTED_CAPABILITIES)}"
                ),
                is_stale=False,
                age_days=0.0,
                evidence_items=(),
                confidence_score=0.0,
                result_hash="",
                jd_hash="",
                jd_uri="",
                company_brief_hash="",
                fetch_duration_ms=time.time() * 1000.0 - t_start,
                audit_ref=bridge_trace_id,
            )

        # ------------------------------------------------------------------
        # Invoke apps_research via registered public interface
        # ------------------------------------------------------------------
        try:
            raw = self._invoke_apps_research(
                recipient_class=recipient_class,
                recipient_name=recipient_name,
                company_name=company_name,
                job_title=job_title,
                channel=channel,
                outreach_mode=outreach_mode,
                relationship_distance=relationship_distance,
                capability_ref=capability_ref,
                request_id=request_id,
                run_id=run_id,
                trace_id=bridge_trace_id,
            )
        except Exception as exc:  # noqa: BLE001
            # guardian: allow-broad-except -- apps_research is an external system;
            # any exception from the bridge must produce a blocked result, not
            # propagate up to the dispatcher or entrypoint as an uncaught exception.
            return ResearchResult(
                run_id=run_id,
                trace_id=bridge_trace_id,
                request_id=request_id,
                is_blocked=True,
                block_reason=f"{type(exc).__name__}: {exc}",
                is_stale=False,
                age_days=0.0,
                evidence_items=(),
                confidence_score=0.0,
                result_hash="",
                jd_hash="",
                jd_uri="",
                company_brief_hash="",
                fetch_duration_ms=time.time() * 1000.0 - t_start,
                audit_ref=bridge_trace_id,
            )

        # ------------------------------------------------------------------
        # Translate raw apps_research output to ResearchResult
        # ------------------------------------------------------------------
        return self._translate(
            raw=raw,
            run_id=run_id,
            trace_id=bridge_trace_id,
            request_id=request_id,
            t_start=t_start,
        )

    # ------------------------------------------------------------------
    # Internal: apps_research invocation (registered public interface only)
    # ------------------------------------------------------------------

    def _invoke_apps_research(
        self,
        *,
        recipient_class: str,
        recipient_name: str,
        company_name: str,
        job_title: str,
        channel: str,
        outreach_mode: str,
        relationship_distance: str,
        capability_ref: str,
        request_id: str,
        run_id: str,
        trace_id: str,
    ) -> Any:
        """Call apps_research via its registered public interface.

        Only imports from apps_research's public surface are permitted here.
        Direct access to apps_research internals is FORBIDDEN.

        NOTE: The actual apps_research call is implemented when the
        apps_research public interface is registered and stable. This stub
        raises NotImplementedError so that integration tests can inject
        a mock bridge and validate the dispatcher logic without a real
        apps_research backend. Production callers must subclass and override.
        """
        raise NotImplementedError(
            "AppsResearchBridge._invoke_apps_research is a stub. "
            "Subclass AppsResearchBridge and override _invoke_apps_research "
            "to wire the real apps_research public interface. "
            "For tests, inject a MockAppsResearchBridge."
        )

    def _translate(
        self,
        *,
        raw: Any,
        run_id: str,
        trace_id: str,
        request_id: str,
        t_start: float,
    ) -> ResearchResult:
        """Translate raw apps_research output to ResearchResult contract shape."""
        import hashlib
        import json as _json

        evidence_items_raw = getattr(raw, "evidence_items", []) or []
        evidence_items = tuple(
            EvidenceItem(
                source_id=str(getattr(ev, "source_id", f"ev-{i}")),
                label=str(getattr(ev, "label", f"evidence_{i}")),
                uri=str(getattr(ev, "uri", getattr(ev, "source_uri", ""))),
                source_type=str(getattr(ev, "source_type", "web")),
                field_ref=str(getattr(ev, "field_ref", "recipient_brief_ref")),
                confidence=float(getattr(ev, "confidence", 0.0)),
            )
            for i, ev in enumerate(evidence_items_raw)
        )

        confidence = float(getattr(raw, "confidence_score", 0.0))
        is_blocked = bool(getattr(raw, "is_blocked", False))
        is_stale = bool(getattr(raw, "is_stale", False))
        age_days = float(getattr(raw, "age_days", 0.0))

        result_payload = _json.dumps(
            {"run_id": run_id, "evidence_count": len(evidence_items), "confidence": confidence},
            sort_keys=True,
        ).encode()
        result_hash = f"sha256:{hashlib.sha256(result_payload).hexdigest()}"

        return ResearchResult(
            run_id=str(getattr(raw, "run_id", run_id)),
            trace_id=trace_id,
            request_id=request_id,
            is_blocked=is_blocked,
            block_reason=str(getattr(raw, "block_reason", "")),
            is_stale=is_stale,
            age_days=age_days,
            evidence_items=evidence_items,
            confidence_score=confidence,
            result_hash=result_hash,
            jd_hash=str(getattr(raw, "jd_hash", "")),
            jd_uri=str(getattr(raw, "jd_uri", "")),
            company_brief_hash=str(getattr(raw, "company_brief_hash", "")),
            fetch_duration_ms=time.time() * 1000.0 - t_start,
            audit_ref=trace_id,
        )


# ---------------------------------------------------------------------------
# Test / injection helpers
# ---------------------------------------------------------------------------


class MockAppsResearchBridge(AppsResearchBridge):
    """Injectable mock bridge for unit tests.

    Allows tests to control research results without a real apps_research
    backend. Override _make_mock_result to configure per-test scenarios.
    """

    def __init__(
        self,
        *,
        is_blocked: bool = False,
        block_reason: str = "",
        is_stale: bool = False,
        age_days: float = 0.0,
        evidence_items: List[EvidenceItem] | None = None,
        confidence_score: float = 0.85,
        capability_ref: str = "apps_research.v1",
    ) -> None:
        super().__init__(capability_ref=capability_ref)
        self._mock_blocked = is_blocked
        self._mock_block_reason = block_reason
        self._mock_stale = is_stale
        self._mock_age_days = age_days
        self._mock_evidence = (
            evidence_items
            if evidence_items is not None
            else [
                EvidenceItem(
                    source_id="mock-ev-000",
                    label="Mock Evidence",
                    uri="sha256:mockev000",
                    source_type="web",
                    field_ref="recipient_brief_ref",
                    confidence=confidence_score,
                )
            ]
        )
        self._mock_confidence = confidence_score

    def _invoke_apps_research(self, **_kwargs: Any) -> Any:
        """Return a mock result object with the configured attributes."""

        class _MockRaw:
            pass

        raw = _MockRaw()
        raw.is_blocked = self._mock_blocked
        raw.block_reason = self._mock_block_reason
        raw.is_stale = self._mock_stale
        raw.age_days = self._mock_age_days
        raw.evidence_items = list(self._mock_evidence)
        raw.confidence_score = self._mock_confidence
        raw.run_id = str(uuid.uuid4())
        raw.jd_hash = ""
        raw.jd_uri = ""
        raw.company_brief_hash = ""
        return raw
