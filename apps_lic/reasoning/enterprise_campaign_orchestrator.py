"""Enterprise LIC orchestrator for production-like campaign planning."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from apps_lic.services.repo_signal_service import RepoSignalService


@dataclass
class EnterpriseLicRequest:
    """Request envelope for enterprise LIC campaign planning."""

    campaign_goal: str
    audience_segment: str = "technical_buyers"
    channel: str = "linkedin"
    output_mode: str = "planning"
    enable_repo_signals: bool = True
    trace_id: str = ""

    def __post_init__(self) -> None:
        if not self.trace_id:
            stamp = f"{self.campaign_goal}:{self.audience_segment}:{datetime.now().isoformat()}"
            self.trace_id = hashlib.sha256(stamp.encode()).hexdigest()[:16]


@dataclass
class EnterpriseLicResult:
    """Decision-grade output for enterprise LIC campaign planning."""

    trace_id: str
    status: str
    campaign_plan: dict[str, Any] = field(default_factory=dict)
    repo_signals: dict[str, Any] = field(default_factory=dict)
    risk_summary: dict[str, Any] = field(default_factory=dict)
    confidence_summary: dict[str, Any] = field(default_factory=dict)
    recommendations: list[dict[str, Any]] = field(default_factory=list)
    provenance_block: dict[str, Any] = field(default_factory=dict)
    execution_log: list[dict[str, Any]] = field(default_factory=list)


class EnterpriseLicOrchestrator:
    """Production-simulation orchestrator for LIC campaign planning."""

    def __init__(self) -> None:
        self.repo_signal_service = RepoSignalService()
        self._execution_log: list[dict[str, Any]] = []

    async def process(self, request: EnterpriseLicRequest) -> EnterpriseLicResult:
        result = EnterpriseLicResult(trace_id=request.trace_id, status="processing")

        self._log_step(request.trace_id, "INGEST", "start")
        result.campaign_plan = {
            "goal": request.campaign_goal,
            "audience_segment": request.audience_segment,
            "channel": request.channel,
            "output_mode": request.output_mode,
        }
        self._log_step(request.trace_id, "INGEST", "complete")

        if request.enable_repo_signals:
            self._log_step(request.trace_id, "ENRICH", "start")
            snapshot = self.repo_signal_service.collect()
            result.repo_signals = snapshot.as_dict()
            self._log_step(
                request.trace_id,
                "ENRICH",
                "complete",
                details={
                    "adg_available": bool(result.repo_signals.get("adg", {}).get("available")),
                    "workflow_count": result.repo_signals.get("ci", {}).get("workflow_count", 0),
                    "agent_spec_count": result.repo_signals.get("governance", {})
                    .get("lic_domain", {})
                    .get("agent_spec_count", 0),
                },
            )

        self._log_step(request.trace_id, "DECIDE", "start")
        result.risk_summary = self._build_risk_summary(result.repo_signals)
        result.confidence_summary = self._build_confidence_summary(result.repo_signals)
        result.recommendations = self._build_recommendations(
            request, result.risk_summary, result.confidence_summary
        )
        result.provenance_block = {
            "captured_at": result.repo_signals.get("captured_at"),
            "files_used": result.repo_signals.get("provenance", {}),
            "trace_id": request.trace_id,
        }
        result.status = "complete"
        self._log_step(request.trace_id, "DECIDE", "complete")

        result.execution_log = self._execution_log
        return result

    def _build_risk_summary(self, repo_signals: dict[str, Any]) -> dict[str, Any]:
        governance = repo_signals.get("governance", {})
        lic_domain = governance.get("lic_domain", {})
        observability = governance.get("observability", {})

        risk_points = 0
        reasons: list[str] = []

        if not governance.get("denominator_baseline_available"):
            risk_points += 2
            reasons.append("governance_baseline_missing")

        if lic_domain.get("agent_spec_count", 0) == 0:
            risk_points += 2
            reasons.append("agent_specs_unavailable")

        if observability.get("observability_artifact_count", 0) == 0:
            risk_points += 1
            reasons.append("observability_history_missing")

        if observability.get("governance_artifact_count", 0) == 0:
            risk_points += 1
            reasons.append("governance_history_missing")

        level = "low"
        if risk_points >= 4:
            level = "high"
        elif risk_points >= 2:
            level = "medium"

        return {"score": risk_points, "level": level, "reasons": reasons}

    def _build_confidence_summary(self, repo_signals: dict[str, Any]) -> dict[str, Any]:
        adg = repo_signals.get("adg", {})
        tests = repo_signals.get("tests", {})
        ci = repo_signals.get("ci", {})

        checks = {
            "adg_available": bool(adg.get("available")),
            "test_signals_available": bool(
                tests.get("inventory_available") or tests.get("surface_available")
            ),
            "workflow_signals_available": ci.get("workflow_count", 0) > 0,
        }
        passed = sum(1 for value in checks.values() if value)
        confidence = round(passed / len(checks), 3)

        return {
            "score": confidence,
            "level": "high" if confidence >= 0.8 else "medium" if confidence >= 0.5 else "low",
            "checks": checks,
        }

    def _build_recommendations(
        self,
        request: EnterpriseLicRequest,
        risk_summary: dict[str, Any],
        confidence_summary: dict[str, Any],
    ) -> list[dict[str, Any]]:
        recommendation_level = "go"
        if risk_summary.get("level") == "high" or confidence_summary.get("level") == "low":
            recommendation_level = "hold"
        elif risk_summary.get("level") == "medium":
            recommendation_level = "go_with_guardrails"

        return [
            {
                "action": "campaign_launch_decision",
                "decision": recommendation_level,
                "rationale": {
                    "goal": request.campaign_goal,
                    "risk_level": risk_summary.get("level"),
                    "confidence_level": confidence_summary.get("level"),
                },
            },
            {
                "action": "policy_guardrail_recheck",
                "decision": "required" if recommendation_level != "go" else "recommended",
                "rationale": {
                    "reason_codes": risk_summary.get("reasons", []),
                },
            },
        ]

    def _log_step(
        self,
        trace_id: str,
        step: str,
        status: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self._execution_log.append(
            {
                "trace_id": trace_id,
                "step": step,
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "details": details or {},
            },
        )


async def run_enterprise_lic_campaign(
    campaign_goal: str,
    audience_segment: str = "technical_buyers",
) -> EnterpriseLicResult:
    """Convenience API for enterprise LIC campaign planning."""
    orchestrator = EnterpriseLicOrchestrator()
    request = EnterpriseLicRequest(campaign_goal=campaign_goal, audience_segment=audience_segment)
    return await orchestrator.process(request)
