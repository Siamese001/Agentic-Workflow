"""Centralized routing + retry policy for orchestration decisions."""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from core_v10_7 import NodeStatus
from core_v10_7_services import RobustnessStack

NODE_RESULT_KEY = "__node_result__"


class OrchestrationDecision:
    """Represents a routing decision with optional retry semantics."""

    def __init__(self, route: str, *, should_retry: bool = False, reason: str = "") -> None:
        self.route = route
        self.should_retry = should_retry
        self.reason = reason


class OrchestrationRoutingPolicy:
    """Owns all DAG routing heuristics for v10.8 orchestrators."""

    def __init__(
        self,
        context: Any,
        debug_mode: bool = False,
        *,
        robustness: Optional[RobustnessStack] = None,
    ) -> None:
        self.context = context
        self.debug_mode = debug_mode
        config = getattr(context, "config", None)
        self.config = config
        self.robustness = robustness or RobustnessStack(config=config)

    # ------------------------------------------------------------------
    # Public routing APIs
    # ------------------------------------------------------------------

    def after_prompt_injection(self, state: Dict[str, Any]) -> str:
        if state.get("safety", {}).get("injection_detected", False):
            return "injection_detected"
        return "injection_safe"

    def after_bullet_critique(self, state: Dict[str, Any]) -> str:
        result = self._extract_node_result(state, "run_critique_bullets")
        status = self._result_status(result)
        if status and status is not NodeStatus.SUCCESS:
            return "global_replanner"
        payload = result.get("payload") if result else None
        route, _ = self._read_arbitration_route(state, payload, "bullets_post_selection")
        if route in {"GLOBAL_REPLAN", "REPLAN_STRATEGY"}:
            return "global_replanner"
        if route == "RETRY_BULLETS":
            if self.robustness.should_retry("bullets_quality", "arbitration_retry"):
                return "retry_bullets"
            return "global_replanner"
        if route == "ACCEPT":
            self.robustness.reset("bullets_quality")
            return "bullets_passed"
        if route and route != "ACCEPT":
            return "global_replanner"

        bullet_state = self._resolve_section(payload, state, "bullets")
        critiques = bullet_state.get("critiqued_bullets", [])
        if not critiques:
            return "global_replanner"
        avg_score = sum(
            float(crit.get("critique", {}).get("score", 0.0)) for crit in critiques
        ) / max(len(critiques), 1)
        if avg_score >= self._bullet_accept_threshold():
            self.robustness.reset("bullets_quality")
            return "bullets_passed"
        if self.robustness.should_retry("bullets_quality", "fallback_avg_score"):
            return "retry_bullets"
        return "global_replanner"

    def after_qa_validation(self, state: Dict[str, Any]) -> str:
        result = self._extract_node_result(state, "run_qa_validation")
        status = self._result_status(result)
        if status and status is not NodeStatus.SUCCESS:
            return "global_replanner"
        payload = result.get("payload") if result else None
        route, _ = self._read_arbitration_route(state, payload, "qa_post_validation")
        if route in {"GLOBAL_REPLAN", "REPLAN_STRATEGY"}:
            return "global_replanner"
        if route in {"RETRY_QA", "RETRY_DRAFTING"}:
            if self.robustness.should_retry("qa_validation", "arbitration_retry"):
                return "retry_drafting"
            return "global_replanner"
        if route == "ACCEPT":
            self.robustness.reset("qa_validation")
            return "qa_passed"
        if route and route != "ACCEPT":
            return "global_replanner"

        qa_state = self._resolve_section(payload, state, "qa")
        if qa_state.get("qa_passed", False):
            self.robustness.reset("qa_validation")
            return "qa_passed"
        if self.robustness.should_retry("qa_validation", "fallback_qa_failed"):
            return "retry_drafting"
        return "global_replanner"

    def after_rag_execution(self, state: Dict[str, Any]) -> OrchestrationDecision:
        rag_state = state.get("rag", {})
        if rag_state.get("needs_retry"):
            return OrchestrationDecision(
                route="retry_rag",
                should_retry=True,
                reason="rag_retry_requested",
            )
        return OrchestrationDecision(route="rag_complete")

    def after_hil_reentry(self, state: Dict[str, Any]) -> str:
        retries = self._get_current_hil_retries(state)
        max_loops = self._get_hil_max_reentry_loops()
        return "continue" if retries <= max_loops else "halt"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract_node_result(
        self, state: Dict[str, Any], expected_node: str
    ) -> Optional[Dict[str, Any]]:
        result = state.get(NODE_RESULT_KEY)
        if not isinstance(result, dict):
            return None
        if result.get("node") != expected_node:
            return None
        return result

    def _result_status(self, result: Optional[Dict[str, Any]]) -> Optional[NodeStatus]:
        if not result:
            return None
        status = result.get("status")
        if isinstance(status, NodeStatus):
            return status
        if isinstance(status, str):
            try:
                return NodeStatus(status)
            except ValueError:
                return None
        return None

    def _read_arbitration_route(
        self,
        state: Dict[str, Any],
        payload: Optional[Dict[str, Any]],
        stage: str,
    ) -> Tuple[str, bool]:
        containers = []
        if isinstance(payload, dict):
            containers.append(payload.get("arbitration"))
        containers.append(state.get("arbitration"))
        for container in containers:
            route = self._from_container(container, stage)
            if route:
                return route, True
        return "", False

    def _from_container(
        self, container: Optional[Dict[str, Any]], stage: str
    ) -> str:
        if not isinstance(container, dict):
            return ""
        value = container.get(stage)
        if isinstance(value, dict):
            route = value.get("suggested_route")
            if isinstance(route, str):
                return route
            decision = value.get("decision")
            if isinstance(decision, str) and decision:
                return decision
        if isinstance(value, str):
            return value
        return ""

    def _resolve_section(
        self,
        payload: Optional[Dict[str, Any]],
        state: Dict[str, Any],
        key: str,
    ) -> Dict[str, Any]:
        if isinstance(payload, dict) and isinstance(payload.get(key), dict):
            return payload.get(key, {})
        section = state.get(key)
        if isinstance(section, dict):
            return section
        return {}

    def _bullet_accept_threshold(self) -> float:
        try:
            return float(self.config.agent_stacks.bullet_accept_threshold)
        except Exception:
            return 7.0

    def _get_current_hil_retries(self, state: Dict[str, Any]) -> int:
        try:
            return int(state.get("hil", {}).get("retries", 0))
        except Exception:
            return 0

    def _get_hil_max_reentry_loops(self) -> int:
        try:
            return int(getattr(self.config.agent_stacks, "hil_max_reentry_loops", 1))
        except Exception:
            return 1
