"""
Tool guardrail pipeline — W1 additive (L2 best-practices gap plan, G1).

Unified input/output/tool guardrail wrappers with a ``TripwireTriggered``
halt exception, modelled on the OpenAI Agents SDK ``tripwire_triggered``
pattern (https://openai.github.io/openai-agents-python/guardrails/).

This pipeline does NOT replace ``boundary_verifier`` or
``execution_guardrail_chokepoint``; it composes them. The pipeline is
additive and opt-in: call sites wire it explicitly. It exists to give E2
and E3 a single place to register pre- and post-call checks with a
consistent tripwire contract.

Doctrinal anchor: v33 §4.1.2 Work Order Check (E2) and §4.1.3 Execute (E3).

Guardian note: this module catches only
``TripwireTriggered`` (its own exception type) and re-raises it. No broad
``except Exception`` is introduced.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Iterable, Protocol, runtime_checkable

__all__ = [
    "GuardrailPhase",
    "GuardrailOutput",
    "TripwireTriggered",
    "ToolGuardrail",
    "ToolGuardrailPipeline",
]


class GuardrailPhase(str, Enum):
    """When in the call lifecycle a guardrail runs."""

    PRE_EXECUTE = "pre_execute"
    POST_EXECUTE = "post_execute"


@dataclass(frozen=True, slots=True)
class GuardrailOutput:
    """Result of running a single guardrail function.

    ``tripwire_triggered=True`` halts the pipeline and raises
    ``TripwireTriggered``. ``replacement`` lets an output-guardrail swap the
    payload without raising (e.g. redact sensitive fields).
    """

    guardrail_name: str
    phase: GuardrailPhase
    tripwire_triggered: bool = False
    reason: str = ""
    replacement: Any | None = None
    evidence: dict[str, Any] = field(default_factory=dict)


class TripwireTriggered(Exception):
    """Raised when any guardrail in the pipeline sets ``tripwire_triggered=True``.

    This is a narrow, named exception — callers MUST catch it specifically
    (never via ``except Exception``).
    """

    def __init__(self, output: GuardrailOutput) -> None:
        super().__init__(
            f"tripwire={output.guardrail_name} phase={output.phase.value} "
            f"reason={output.reason!r}"
        )
        self.output = output


@runtime_checkable
class ToolGuardrail(Protocol):
    """Protocol a guardrail function must satisfy."""

    name: str
    phase: GuardrailPhase

    def __call__(self, payload: Any) -> GuardrailOutput: ...  # pragma: no cover


@dataclass(slots=True)
class _InlineGuardrail:
    name: str
    phase: GuardrailPhase
    fn: Callable[[Any], GuardrailOutput]

    def __call__(self, payload: Any) -> GuardrailOutput:
        return self.fn(payload)


class ToolGuardrailPipeline:
    """Compose pre- and post-execute guardrails for a single tool invocation.

    Wiring is explicit and additive. The pipeline is created per call site and
    is NOT a global singleton. This keeps guardrails colocated with the agent
    that owns the tool, matching OpenAI's rationale for locality of guardrails.

    Usage::

        pipeline = ToolGuardrailPipeline()
        pipeline.add(pre_schema_validator)
        pipeline.add(post_pii_redactor)
        pipeline.run_pre(args)            # raises TripwireTriggered on breach
        result = invoke_tool(args)
        result = pipeline.run_post(result)
    """

    def __init__(self) -> None:
        self._pre: list[ToolGuardrail] = []
        self._post: list[ToolGuardrail] = []

    def add(self, guardrail: ToolGuardrail) -> None:
        if guardrail.phase is GuardrailPhase.PRE_EXECUTE:
            self._pre.append(guardrail)
        elif guardrail.phase is GuardrailPhase.POST_EXECUTE:
            self._post.append(guardrail)
        else:
            raise ValueError(f"unknown GuardrailPhase: {guardrail.phase}")

    def add_inline(
        self,
        name: str,
        phase: GuardrailPhase,
        fn: Callable[[Any], GuardrailOutput],
    ) -> None:
        self.add(_InlineGuardrail(name=name, phase=phase, fn=fn))

    @property
    def pre_guardrails(self) -> tuple[ToolGuardrail, ...]:
        return tuple(self._pre)

    @property
    def post_guardrails(self) -> tuple[ToolGuardrail, ...]:
        return tuple(self._post)

    def run_pre(self, payload: Any) -> Any:
        """Run pre-execute guardrails. Raises ``TripwireTriggered`` on breach.

        Returns the (possibly replaced) payload so callers can propagate
        redactions or normalizations.
        """
        current = payload
        for g in self._pre:
            out = g(current)
            if out.tripwire_triggered:
                raise TripwireTriggered(out)
            if out.replacement is not None:
                current = out.replacement
        return current

    def run_post(self, result: Any) -> Any:
        """Run post-execute guardrails. Raises ``TripwireTriggered`` on breach."""
        current = result
        for g in self._post:
            out = g(current)
            if out.tripwire_triggered:
                raise TripwireTriggered(out)
            if out.replacement is not None:
                current = out.replacement
        return current

    def run_all(
        self,
        payload: Any,
        execute: Callable[[Any], Any],
    ) -> Any:
        """Convenience: pre → execute(payload) → post. Single ``TripwireTriggered``
        surface. ``execute`` must be the caller-supplied tool invocation.
        """
        normalized = self.run_pre(payload)
        result = execute(normalized)
        return self.run_post(result)


def guardrails_from_iterable(items: Iterable[ToolGuardrail]) -> ToolGuardrailPipeline:
    """Factory helper for tests and composition."""
    pipeline = ToolGuardrailPipeline()
    for g in items:
        pipeline.add(g)
    return pipeline
