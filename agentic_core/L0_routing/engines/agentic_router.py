"""AgenticRouter — user/task input → classified intent → specialist agent/workflow.

Exposes the ShadowRouterClassifier logic as a first-class routing pattern.
Supports Multi-Agent Debate (MAD) as a routing target.

Layer: L0_routing
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

Logger = logging.getLogger(__name__)


@dataclass
class RouteTarget:
    """A registered routing target (agent or workflow)."""

    name: str
    handler: Callable[[str, dict[str, Any]], Awaitable[Any]]
    intent_keywords: list[str] = field(default_factory=list)
    description: str = ""


@dataclass
class RoutingDecision:
    """Result of an AgenticRouter dispatch."""

    intent: str
    target_name: str
    confidence: float
    result: Any = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


_MAD_TARGET = "multi_agent_debate"


class AgenticRouter:
    """Classifies input intent and dispatches to the most relevant registered target.

    Usage::

        router = AgenticRouter()
        router.register("resume_writer", handler_fn, intent_keywords=["resume", "cv"])
        router.register("code_reviewer", handler_fn2, intent_keywords=["code", "review"])
        decision = await router.route("Please review my Python code")

    Args:
        fallback_handler: Optional async fn called when no target scores above threshold.
        min_confidence:   Minimum score to dispatch to a target (default 0.2).
    """

    # guardian: allow-magic-config
    def __init__(
        self,
        fallback_handler: Callable[[str, dict[str, Any]], Awaitable[Any]] | None = None,
        min_confidence: float = 0.2,
    ) -> None:
        self._targets: dict[str, RouteTarget] = {}
        self._fallback = fallback_handler
        self.min_confidence = min_confidence

    def register(
        self,
        name: str,
        handler: Callable[[str, dict[str, Any]], Awaitable[Any]],
        intent_keywords: list[str] | None = None,
        description: str = "",
    ) -> None:
        """Register a specialist agent or workflow as a routing target."""
        self._targets[name] = RouteTarget(
            name=name,
            handler=handler,
            intent_keywords=[kw.lower() for kw in (intent_keywords or [])],
            description=description,
        )
        Logger.debug("agentic_router_register", extra={"target": name, "keywords": intent_keywords})

    def register_mad(
        self,
        debaters: list[Callable[[str, dict[str, Any]], Awaitable[Any]]],
        synthesizer: Callable[[list[Any]], Awaitable[str]],
    ) -> None:
        """Register Multi-Agent Debate as a named routing target.

        Args:
            debaters:   List of agent handlers that independently answer the input.
            synthesizer: Async fn that synthesizes debater outputs into a final answer.
        """
        import asyncio

        async def _mad_handler(user_input: str, context: dict[str, Any]) -> Any:
            outputs = await asyncio.gather(
                *[d(user_input, context) for d in debaters], return_exceptions=True
            )
            valid = [o for o in outputs if not isinstance(o, BaseException)]
            if not valid:
                return None
            return await synthesizer(valid)

        self._targets[_MAD_TARGET] = RouteTarget(
            name=_MAD_TARGET,
            handler=_mad_handler,
            intent_keywords=["debate", "compare", "perspectives", "multiple agents"],
            description="Multi-Agent Debate: gather multiple perspectives, then synthesize",
        )

    async def route(self, user_input: str, context: dict[str, Any] | None = None) -> RoutingDecision:
        """Classify input and dispatch to the best-matching target.

        Args:
            user_input: Raw user or task input string.
            context:    Optional metadata forwarded to the target handler.

        Returns:
            RoutingDecision with chosen target, confidence, and handler result.
        """
        context = context or {}
        intent, target_name, confidence = self._classify(user_input)

        Logger.info(
            "agentic_router_dispatch",
            extra={"intent": intent, "target": target_name, "confidence": confidence},
        )

        decision = RoutingDecision(
            intent=intent,
            target_name=target_name,
            confidence=confidence,
            metadata={"input_preview": user_input[:80]},
        )

        target = self._targets.get(target_name)
        if target is None or confidence < self.min_confidence:
            if self._fallback is not None:
                try:
                    decision.result = await self._fallback(user_input, context)
                except Exception as exc:  # guardian: allow-silent-swallower
                    decision.error = str(exc)
                    Logger.error("agentic_router_fallback_error", extra={"error": str(exc)})
            else:
                decision.error = f"No target for intent '{intent}' (confidence={confidence:.2f})"
            return decision

        try:
            decision.result = await target.handler(user_input, context)
        except Exception as exc:  # guardian: allow-silent-swallower
            decision.error = str(exc)
            Logger.error("agentic_router_handler_error", extra={"target": target_name, "error": str(exc)})

        return decision

    def _classify(self, user_input: str) -> tuple[str, str, float]:
        """Keyword-based intent classification.

        Returns (intent_label, best_target_name, confidence_score).
        """
        text = user_input.lower()
        scores: dict[str, float] = {}

        for name, target in self._targets.items():
            hit_count = sum(1 for kw in target.intent_keywords if kw in text)
            if target.intent_keywords:
                scores[name] = hit_count / len(target.intent_keywords)
            else:
                scores[name] = 0.0

        if not scores:
            return ("unknown", "", 0.0)

        best_name = max(scores, key=scores.__getitem__)
        best_score = scores[best_name]
        return (best_name, best_name, best_score)

    def list_targets(self) -> list[str]:
        return list(self._targets.keys())
