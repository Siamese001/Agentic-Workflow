"""Core service helpers for arbitration and resilience (v10.7)."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from telemetry_v10_7 import log_event

logger = logging.getLogger("core_v10_7.services")


@dataclass
class ArbitrationReport:
    """Structured result emitted by the ArbitrationEngine."""

    stage: str
    decision: str
    suggested_route: str
    reason: str = ""
    issues: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> Dict[str, Any]:
        """Return a serialisable representation of the report."""

        return {
            "stage": self.stage,
            "decision": self.decision,
            "suggested_route": self.suggested_route,
            "reason": self.reason,
            "issues": list(self.issues),
            "metadata": dict(self.metadata),
        }


class SelfCorrectionManager:
    """Collects arbitration decisions for downstream observability."""

    def __init__(self) -> None:
        self._signals: List[Dict[str, Any]] = []

    def register_signal(
        self,
        stage: str,
        route: str,
        report: ArbitrationReport,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "stage": stage,
            "route": route,
            "decision": report.decision,
            "issues": list(report.issues),
            "metadata": dict(report.metadata),
        }
        if extra:
            payload.update(extra)
        self._signals.append(payload)
        return payload

    def last_signal(self, stage: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if not self._signals:
            return None
        if stage is None:
            return self._signals[-1]
        for payload in reversed(self._signals):
            if payload.get("stage") == stage:
                return payload
        return None


class RobustnessStack:
    """Tracks retry budgets for key workflow stages."""

    def __init__(
        self,
        *,
        config: Optional[Any] = None,
        retry_limits: Optional[Dict[str, int]] = None,
    ) -> None:
        max_local = 1
        qa_limit = 1
        if config is not None:
            try:
                max_local = int(config.agent_stacks.max_local_retries)
            except Exception:
                logger.debug("Falling back to default bullet retry limit")
            try:
                qa_limit = int(getattr(config.agent_stacks, "qa_retry_limit", 1))
            except Exception:
                logger.debug("Falling back to default QA retry limit")
        base_limits = {
            "bullets_quality": max(max_local, 0),
            "qa_validation": max(qa_limit, 0),
        }
        if retry_limits:
            for key, value in retry_limits.items():
                base_limits[key] = max(int(value), 0)
        self._limits = base_limits
        self._counters: Dict[str, int] = {key: 0 for key in self._limits}

    def should_retry(self, check_name: str, issue_code: str = "") -> bool:
        limit = self._limits.get(check_name, 0)
        count = self._counters.get(check_name, 0)
        if count < limit:
            self._counters[check_name] = count + 1
            logger.debug(
                "Retry approved for %s (%s/%s)", check_name, self._counters[check_name], limit
            )
            return True
        logger.debug(
            "Retry denied for %s (%s/%s)", check_name, self._counters.get(check_name, 0), limit
        )
        return False

    def reset(self, check_name: str) -> None:
        if check_name in self._counters:
            self._counters[check_name] = 0

    def snapshot(self) -> Dict[str, int]:
        return dict(self._counters)


class ArbitrationEngine:
    """Produces authoritative routing signals for orchestration decisions."""

    ROUTE_ACCEPT = "ACCEPT"
    ROUTE_REPLAN_STRATEGY = "REPLAN_STRATEGY"
    ROUTE_RETRY_RAG = "RETRY_RAG"
    ROUTE_RETRY_BULLETS = "RETRY_BULLETS"
    ROUTE_RETRY_DRAFTING = "RETRY_DRAFTING"
    ROUTE_RETRY_QA = "RETRY_QA"
    ROUTE_GLOBAL_REPLAN = "GLOBAL_REPLAN"
    ROUTE_END = "END"

    def __init__(
        self,
        *,
        robustness_stack: RobustnessStack,
        self_correction_manager: SelfCorrectionManager,
        config: Optional[Any] = None,
    ) -> None:
        self.robustness_stack = robustness_stack
        self.self_correction_manager = self_correction_manager
        self.config = config
        self.bullet_threshold = 7.0
        if config is not None:
            try:
                self.bullet_threshold = float(
                    getattr(config.agent_stacks, "bullet_accept_threshold", self.bullet_threshold)
                )
            except Exception:
                logger.debug("Using default bullet acceptance threshold")

    def run_check(self, stage: str, payload: Optional[Dict[str, Any]] = None) -> ArbitrationReport:
        handler = getattr(self, f"_handle_{stage}", None)
        if handler is None:
            report = self._handle_generic(stage, payload or {})
        else:
            report = handler(payload or {})
        log_event(
            "arbitration",
            "decision",
            {
                "stage": stage,
                "decision": report.decision,
                "suggested_route": report.suggested_route,
                "issues": report.issues,
            },
        )
        self.self_correction_manager.register_signal(stage, report.suggested_route, report)
        return report

    # ------------------------------------------------------------------
    # Stage handlers
    # ------------------------------------------------------------------

    def _handle_bullets_post_selection(self, payload: Dict[str, Any]) -> ArbitrationReport:
        scores: List[float] = [float(score) for score in payload.get("scores", []) if score is not None]
        issues: List[str] = []
        metadata = {
            "avg_score": payload.get("avg_score"),
            "critique_count": len(scores),
        }
        if not scores:
            issues.append("missing_scores")
            return self._build_report(
                stage="bullets_post_selection",
                decision="MISSING_DATA",
                route=self.ROUTE_GLOBAL_REPLAN,
                reason="No critique scores provided.",
                issues=issues,
                metadata=metadata,
            )
        avg_score = payload.get("avg_score")
        if avg_score is None:
            avg_score = sum(scores) / len(scores)
            metadata["avg_score"] = avg_score
        if avg_score >= self.bullet_threshold:
            self.robustness_stack.reset("bullets_quality")
            return self._build_report(
                stage="bullets_post_selection",
                decision="ACCEPT",
                route=self.ROUTE_ACCEPT,
                reason="Bullets met the minimum quality threshold.",
                metadata=metadata,
            )
        issues.append("avg_score_below_threshold")
        reason = f"Average score {avg_score:.2f} below threshold {self.bullet_threshold:.1f}."
        if self.robustness_stack.should_retry("bullets_quality", "avg_score_below_threshold"):
            route = self.ROUTE_RETRY_BULLETS
            decision = "REQUEST_REVISE"
        else:
            route = self.ROUTE_GLOBAL_REPLAN
            decision = "ESCALATE"
        return self._build_report(
            stage="bullets_post_selection",
            decision=decision,
            route=route,
            reason=reason,
            issues=issues,
            metadata=metadata,
        )

    def _handle_qa_post_validation(self, payload: Dict[str, Any]) -> ArbitrationReport:
        qa_passed = bool(payload.get("qa_passed"))
        severity = str(payload.get("severity", "minor") or "minor").lower()
        issues = payload.get("issues", []) or []
        metadata = {
            "blocking_issues": issues,
            "severity": severity,
        }
        if qa_passed:
            self.robustness_stack.reset("qa_validation")
            return self._build_report(
                stage="qa_post_validation",
                decision="ACCEPT",
                route=self.ROUTE_ACCEPT,
                reason="QA stack approved the draft.",
                metadata=metadata,
            )
        needs_new_draft = bool(payload.get("needs_new_draft"))
        issue_code = "qa_failed"
        if severity in {"critical", "blocker"}:
            needs_new_draft = True
        reason = payload.get("reason") or "QA stack reported blocking issues."
        if needs_new_draft:
            if self.robustness_stack.should_retry("qa_validation", issue_code):
                route = self.ROUTE_RETRY_DRAFTING
                decision = "REQUEST_REVISE"
            else:
                route = self.ROUTE_GLOBAL_REPLAN
                decision = "ESCALATE"
        else:
            if self.robustness_stack.should_retry("qa_validation", issue_code):
                route = self.ROUTE_RETRY_QA
                decision = "REQUEST_REVISE"
            else:
                route = self.ROUTE_GLOBAL_REPLAN
                decision = "ESCALATE"
        return self._build_report(
            stage="qa_post_validation",
            decision=decision,
            route=route,
            reason=reason,
            issues=[str(item) for item in issues],
            metadata=metadata,
        )

    def _handle_generic(self, stage: str, payload: Dict[str, Any]) -> ArbitrationReport:
        decision = payload.get("decision", "ACCEPT")
        route = payload.get("suggested_route")
        if not route:
            route = self._map_decision_to_route(decision)
        reason = payload.get("reason", "Decision routed via generic handler.")
        issues = payload.get("issues", [])
        metadata = {key: value for key, value in payload.items() if key not in {"decision", "suggested_route", "reason", "issues"}}
        return self._build_report(stage=stage, decision=decision, route=route, reason=reason, issues=issues, metadata=metadata)

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------

    def _map_decision_to_route(self, decision: str) -> str:
        decision_map = {
            "ACCEPT": self.ROUTE_ACCEPT,
            "REQUEST_REPLAN": self.ROUTE_REPLAN_STRATEGY,
            "REQUEST_RAG_RETRY": self.ROUTE_RETRY_RAG,
            "REQUEST_BULLET_RETRY": self.ROUTE_RETRY_BULLETS,
            "REQUEST_DRAFT_RETRY": self.ROUTE_RETRY_DRAFTING,
            "REQUEST_QA_RETRY": self.ROUTE_RETRY_QA,
            "ESCALATE": self.ROUTE_GLOBAL_REPLAN,
        }
        return decision_map.get(decision, self.ROUTE_ACCEPT)

    def _build_report(
        self,
        *,
        stage: str,
        decision: str,
        route: str,
        reason: str,
        issues: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ArbitrationReport:
        issues_list = list(issues or [])
        metadata_dict = dict(metadata or {})
        report = ArbitrationReport(
            stage=stage,
            decision=decision,
            suggested_route=route,
            reason=reason,
            issues=issues_list,
            metadata=metadata_dict,
        )
        return report


__all__ = [
    "ArbitrationEngine",
    "ArbitrationReport",
    "RobustnessStack",
    "SelfCorrectionManager",
]
