"""apps_research bridge for apps_rg managed R3R4 resume briefing delegation."""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List


@dataclass(frozen=True)
class EvidenceItem:
    source_id: str
    label: str
    uri: str
    source_type: str
    field_ref: str
    confidence: float = 0.0


@dataclass(frozen=True)
class ResearchResult:
    run_id: str
    trace_id: str
    request_id: str
    is_blocked: bool
    block_reason: str
    is_stale: bool
    age_days: float
    evidence_items: tuple
    confidence_score: float
    result_hash: str
    company_brief_hash: str
    fetch_duration_ms: float
    audit_ref: str
    research_artifact_dir: str = ""
    company_brief_text: str = ""


class AppsResearchBridge:
    SUPPORTED_CAPABILITIES = frozenset({"apps_research.v1", "apps_research.v2"})

    def __init__(self, capability_ref: str = "apps_research.v1") -> None:
        self._capability_ref = capability_ref
        self._bridge_id = f"rg_research_bridge:{uuid.uuid4().hex[:8]}"

    def fetch(
        self,
        *,
        company_name: str,
        job_title: str,
        capability_ref: str,
        request_id: str,
        run_id: str,
        trace_id: str,
    ) -> ResearchResult:
        t_start = time.time() * 1000.0
        bridge_trace_id = f"bridge:{self._bridge_id}:{trace_id}"
        if capability_ref not in self.SUPPORTED_CAPABILITIES:
            return ResearchResult(
                run_id=run_id,
                trace_id=bridge_trace_id,
                request_id=request_id,
                is_blocked=True,
                block_reason=f"Unsupported capability_ref={capability_ref!r}",
                is_stale=False,
                age_days=0.0,
                evidence_items=(),
                confidence_score=0.0,
                result_hash="",
                company_brief_hash="",
                fetch_duration_ms=time.time() * 1000.0 - t_start,
                audit_ref=bridge_trace_id,
            )
        try:
            raw = self._invoke_apps_research(
                company_name=company_name,
                job_title=job_title,
                capability_ref=capability_ref,
                request_id=request_id,
                run_id=run_id,
                trace_id=bridge_trace_id,
            )
        except Exception as exc:  # noqa: BLE001
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
                company_brief_hash="",
                fetch_duration_ms=time.time() * 1000.0 - t_start,
                audit_ref=bridge_trace_id,
            )
        return self._translate(
            raw=raw,
            run_id=run_id,
            trace_id=bridge_trace_id,
            request_id=request_id,
            t_start=t_start,
        )

    def _invoke_apps_research(
        self,
        *,
        company_name: str,
        job_title: str,
        capability_ref: str,
        request_id: str,
        run_id: str,
        trace_id: str,
    ) -> Any:
        from apps_research.integrations.governed_research_run import GovernedResearchRun
        from apps_research.types.research_types import ResearchRequest

        # Topic is the company entity only — the role/JD live in jd_context so
        # they never pollute company identification in the targeting route.
        research_request = ResearchRequest(
            topic=company_name,
            mode="brief",
            audience_style="executive",
            depth_profile="COMPANY_BRIEF_STANDARD",
            trace_id=trace_id,
            jd_context={
                "company_name": company_name,
                "job_title": job_title,
                "request_id": request_id,
                "run_id": run_id,
                "output_format": "apps_rg_targeting_brief_v1",
                "synthesis_template": "apps_rg_targeting_brief_synthesis_v1",
                # JD relevance context only — never used to identify the company.
                "jd_context": {
                    "role": job_title or "target role",
                },
            },
        )
        runner = GovernedResearchRun()
        return runner.run_governed_e2e(request=research_request)

    def _translate(
        self,
        *,
        raw: Any,
        run_id: str,
        trace_id: str,
        request_id: str,
        t_start: float,
    ) -> ResearchResult:
        import hashlib
        import json as _json

        evidence_items_raw = getattr(raw, "evidence_items", None) or ()
        if not evidence_items_raw:
            try:
                from apps_research.integrations.evidence_lineage import evidence_from_c0_bundle
            except ImportError:
                evidence_from_c0_bundle = None  # type: ignore[misc, assignment]
            fec_ctx = getattr(raw, "fec_run_context", None) or {}
            if evidence_from_c0_bundle and isinstance(fec_ctx, dict):
                c0_bundle = fec_ctx.get("c0_bundle")
                if c0_bundle:
                    evidence_items_raw = evidence_from_c0_bundle(
                        c0_bundle,
                        default_confidence=float(getattr(raw, "support_coverage", 0.0) or 0.0),
                    )

        evidence_items = tuple(
            EvidenceItem(
                source_id=str(getattr(ev, "source_id", f"ev-{i}")),
                label=str(getattr(ev, "label", f"evidence_{i}")),
                uri=str(getattr(ev, "uri", getattr(ev, "source_uri", ""))),
                source_type=str(getattr(ev, "source_type", "company_brief")),
                field_ref=str(getattr(ev, "field_ref", "company_brief")),
                confidence=float(getattr(ev, "confidence", 0.0)),
            )
            for i, ev in enumerate(evidence_items_raw)
        )

        confidence = float(
            getattr(raw, "confidence_score", None)
            or getattr(raw, "support_coverage", 0.0)
            or 0.0
        )
        # The targeting route returns a sealed, contract-valid company_brief_text.
        # Reject missing or contract-invalid briefs (fail closed). No generic
        # "Delegated company research briefing" evidence-label fallback.
        brief_text = str(getattr(raw, "company_brief_text", "") or "").strip()
        block_reason = ""
        is_blocked = bool(getattr(raw, "is_blocked", False))
        if not is_blocked:
            if not brief_text:
                is_blocked = True
                block_reason = "missing_company_brief_text"
            else:
                from apps_research.types.apps_rg_targeting_brief_contract import (  # noqa: PLC0415
                    validate_targeting_brief_text,
                )

                validation = validate_targeting_brief_text(brief_text)
                if not validation.valid:
                    is_blocked = True
                    block_reason = (
                        "contract_invalid_company_brief_text:"
                        + ",".join(validation.violations[:5])
                    )
                    brief_text = ""

        if is_blocked:
            return ResearchResult(
                run_id=str(getattr(raw, "run_id", run_id) or run_id),
                trace_id=trace_id,
                request_id=request_id,
                is_blocked=True,
                block_reason=block_reason or str(getattr(raw, "block_reason", "") or "blocked"),
                is_stale=bool(getattr(raw, "is_stale", False)),
                age_days=float(getattr(raw, "age_days", 0.0)),
                evidence_items=evidence_items,
                confidence_score=confidence,
                result_hash="",
                company_brief_hash="",
                fetch_duration_ms=time.time() * 1000.0 - t_start,
                audit_ref=trace_id,
                company_brief_text="",
            )

        result_hash = hashlib.sha256(
            _json.dumps(
                {"run_id": run_id, "n": len(evidence_items), "confidence": confidence},
                sort_keys=True,
            ).encode("utf-8")
        ).hexdigest()

        research_dir = ""
        rid = str(getattr(raw, "run_id", run_id) or run_id)
        candidate = Path("artifacts") / "apps_research" / "runs" / rid
        if candidate.is_dir():
            research_dir = str(candidate)

        return ResearchResult(
            run_id=rid,
            trace_id=trace_id,
            request_id=request_id,
            is_blocked=bool(getattr(raw, "is_blocked", False)),
            block_reason=str(getattr(raw, "block_reason", "") or ""),
            is_stale=bool(getattr(raw, "is_stale", False)),
            age_days=float(getattr(raw, "age_days", 0.0)),
            evidence_items=evidence_items,
            confidence_score=confidence,
            result_hash=f"sha256:{result_hash}",
            company_brief_hash=result_hash,
            fetch_duration_ms=time.time() * 1000.0 - t_start,
            audit_ref=trace_id,
            research_artifact_dir=research_dir,
            company_brief_text=brief_text,
        )


class MockAppsResearchBridge(AppsResearchBridge):
    def __init__(
        self,
        *,
        is_blocked: bool = False,
        block_reason: str = "",
        is_stale: bool = False,
        evidence_items: List[EvidenceItem] | None = None,
        confidence_score: float = 0.85,
        company_brief_text: str = "",
        capability_ref: str = "apps_research.v1",
    ) -> None:
        super().__init__(capability_ref=capability_ref)
        self._mock_blocked = is_blocked
        self._mock_block_reason = block_reason
        self._mock_stale = is_stale
        self._mock_evidence = evidence_items or [
            EvidenceItem(
                source_id="mock-ev-000",
                label="Mock company overview",
                uri="sha256:mockev000",
                source_type="company_brief",
                field_ref="company_brief",
                confidence=confidence_score,
            )
        ]
        self._mock_confidence = confidence_score
        # Default mock brief is a contract-valid sealed targeting brief so the
        # _translate validation gate (real, not mocked) passes for integration
        # tests. Override via company_brief_text for rejection-path tests.
        self._mock_brief = company_brief_text or (
            "Mock Co (MOCK) - SVP IT Strategy targeting brief\n"
            "| SVP IT Strategy | comp band | Reports to CIO (2026) |\n\n"
            "=== STRATEGIC MANDATE ===\n"
            "- Mid-cap insurer scaling distribution after carrier roll-ups\n"
            "- Role anchors platform consolidation across acquired books\n"
            "- 2025 cloud-core migration shifts spend to data services\n"
            "- Central tension: federated speed versus enterprise control\n\n"
            "=== LEADERSHIP ===\n"
            "- CEO drives acquisitive growth with disciplined integration\n"
            "- CIO mandate: unify policy systems onto one platform\n"
            "- CDO mandate: build governed shared data backbone\n\n"
            "=== TECH & AI PLATFORM ===\n"
            "- Mainframe-to-cloud core underway across business units\n"
            "- Integration debt from acquisitions slows new product launch\n"
            "- Peers investing in agentic underwriting assistance\n\n"
            "=== BUSINESS CONTEXT (JD alignment hooks) ===\n"
            "- Commercial lines: margin focus after rate hardening\n"
            "- Personal lines: retention pressure from direct carriers\n"
            "- Data priority: unify claims and policy for analytics\n"
            "- Culture: pragmatic, integration-heavy operating model\n\n"
            "=== EXEC SUMMARY FRAMING (not proof) ===\n"
            "- Deliver one platform that absorbs acquired books faster\n"
            "- Mirror CIO push for governed consolidation, not features\n"
            "- 12-month win: single rated quote path live in two units\n"
        )

    def _invoke_apps_research(self, **_kwargs: Any) -> Any:
        class _MockRaw:
            pass

        raw = _MockRaw()
        raw.is_blocked = self._mock_blocked
        raw.block_reason = self._mock_block_reason
        raw.is_stale = self._mock_stale
        raw.age_days = 0.0
        raw.evidence_items = list(self._mock_evidence)
        raw.confidence_score = self._mock_confidence
        raw.run_id = str(uuid.uuid4())
        raw.company_brief_text = self._mock_brief
        raw.support_coverage = self._mock_confidence
        return raw


__all__ = [
    "AppsResearchBridge",
    "EvidenceItem",
    "MockAppsResearchBridge",
    "ResearchResult",
]
