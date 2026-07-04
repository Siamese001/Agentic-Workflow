"""apps_research bridge for apps_rg managed R3R4 resume briefing delegation."""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
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
    apps_research_handoff_envelope: dict[str, Any] | None = None


def _resolve_jd_text(*, job_description_ref: str = "", job_description_text: str = "") -> str:
    text = str(job_description_text or "").strip()
    if text:
        return text
    ref = str(job_description_ref or "").strip()
    if not ref:
        return ""
    path = Path(ref)
    if path.is_file():
        try:
            return path.read_text(encoding="utf-8", errors="replace").strip()
        except OSError:
            return ""
    return ref


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
        job_description_ref: str = "",
        job_description_text: str = "",
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
                job_description_ref=job_description_ref,
                job_description_text=job_description_text,
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
            company_name=company_name,
            job_title=job_title,
            job_description_ref=job_description_ref,
            job_description_text=job_description_text,
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
        job_description_ref: str = "",
        job_description_text: str = "",
    ) -> Any:
        from apps_research.integrations.governed_research_run import GovernedResearchRun
        from apps_research.types.research_types import ResearchRequest
        jd_text = _resolve_jd_text(
            job_description_ref=job_description_ref,
            job_description_text=job_description_text,
        )

        # Topic is the company entity only — the role/JD live in jd_context so
        # they never pollute company identification in the targeting route.
        jd_payload = {
            "role": job_title or "target role",
        }
        if jd_text:
            jd_payload["content"] = jd_text
            jd_payload["jd_text"] = jd_text
        if job_description_ref:
            jd_payload["jd_ref"] = job_description_ref
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
                "content": jd_text,
                "jd_text": jd_text,
                "jd_ref": job_description_ref,
                # JD relevance context only — never used to identify the company.
                "jd_context": jd_payload,
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
        company_name: str,
        job_title: str,
        job_description_ref: str = "",
        job_description_text: str = "",
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

                validation = validate_targeting_brief_text(brief_text, profile="apps_rg")
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

        handoff_envelope: dict[str, Any] | None = None
        try:
            from apps_research.integrations.apps_rg_handoff import (  # noqa: PLC0415
                build_apps_rg_handoff_envelope,
                find_apps_rg_targeting_sidecar,
            )

            sidecar = find_apps_rg_targeting_sidecar(getattr(raw, "fec_run_context", {}) or {})
            jd_text = _resolve_jd_text(
                job_description_ref=job_description_ref,
                job_description_text=job_description_text,
            )
            handoff_envelope = build_apps_rg_handoff_envelope(
                sidecar=sidecar,
                run_id=str(getattr(raw, "run_id", run_id) or run_id),
                target_company=company_name,
                target_role=job_title,
                briefing_text=brief_text,
                jd_text=jd_text,
                generated_at_utc=datetime.now(timezone.utc).isoformat(),
            )
        except (ImportError, RuntimeError, TypeError, ValueError) as exc:
            return ResearchResult(
                run_id=str(getattr(raw, "run_id", run_id) or run_id),
                trace_id=trace_id,
                request_id=request_id,
                is_blocked=True,
                block_reason=f"missing_apps_research_handoff_envelope:{exc}",
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
            apps_research_handoff_envelope=handoff_envelope,
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
        apps_research_handoff_envelope: dict[str, Any] | None = None,
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
        self._mock_handoff_envelope = apps_research_handoff_envelope
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
        raw.fec_run_context = {
            "company_brief": {
                "apps_rg_targeting_brief_sidecar": self._mock_sidecar(raw.company_brief_text),
            }
        }
        return raw

    def _mock_sidecar(self, brief_text: str) -> dict[str, Any]:
        if self._mock_handoff_envelope:
            upstream = self._mock_handoff_envelope.get("upstream_sidecar")
            if isinstance(upstream, dict):
                return upstream
        import hashlib

        normalized = str(brief_text or "").strip()
        return {
            "schema_version": "apps_research.apps_rg_targeting_brief_sidecar/v1",
            "company_name": "Mock Co",
            "generation_provider": "external_openai",
            "generation_model": "gpt-5.4-mini-2026-03-17",
            "provider_call_attempted": True,
            "generation_token_budget": 2048,
            "judge_name": "gemini_pro",
            "judge_model": "gemini-3.1-pro-preview",
            "briefing_semantic_score": 0.91,
            "semantic_gate_mode": "model_backed_llm_judge",
            "handoff_eligible": bool(normalized),
            "reason": "ok" if normalized else "missing_mock_brief",
            "x2_judge_receipt": {
                "schema_version": "apps_research.apps_rg_handoff_x2_judge_receipt.v1",
                "gate_id": "X2_RESEARCH_SEMANTIC_GATE",
                "judge_name": "gemini_pro",
                "judge_provider": "gemini_pro",
                "judge_model": "gemini-3.1-pro-preview",
                "threshold": 0.75,
                "model_backed": True,
                "status": "PASS",
                "score": 0.91,
                "verdict": "PASS",
                "provider_status": "MODEL_BACKED_PASS",
            },
            "role_archetype": "it_strategy",
            "required_sections_present": ["strategic mandate"],
            "missing_sections": [],
            "source_families_present": ["overview"],
            "source_families_missing": [],
            "signal_terms_present": ["platform"],
            "signal_terms_missing": [],
            "source_register": [{"family": "overview", "has_content": True}],
            "brief_text_sha256": hashlib.sha256(normalized.encode("utf-8")).hexdigest(),
        }


__all__ = [
    "AppsResearchBridge",
    "EvidenceItem",
    "MockAppsResearchBridge",
    "ResearchResult",
]
