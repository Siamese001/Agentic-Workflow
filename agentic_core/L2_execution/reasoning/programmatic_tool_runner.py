"""
Programmatic Tool Calling sub-context — W4-P4.2 (gap plan b7c4e2: G7).

Anthropic pattern: when a tool chain produces large intermediate outputs,
orchestrate the chain in a *code-based sub-context* and surface only the
final summary to the parent trace. This keeps the parent L2 execution log
from being polluted by raw tool outputs (pages of JSON, large embeddings,
massive search results).

This module provides a ``ProgrammaticToolRunner`` that:

1. Accepts a sequence of ``ToolStep`` entries (tool_name + args + optional
   transform).
2. Executes them against a supplied ``tool_executor`` callable.
3. Returns a ``SubContextResult`` with a *summary* view plus the count of
   suppressed intermediate outputs. The full intermediates are available
   via ``result.intermediates`` for debugging but are never merged into
   the parent log payload unless explicitly asked.

No implicit retries or healing here — that's the heal-loop's job. This
runner is purely a context-scoping primitive.

Guardian note: catches only its own ``SubContextToolError`` where needed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Sequence

__all__ = [
    "ToolStep",
    "SubContextResult",
    "SubContextToolError",
    "ProgrammaticToolRunner",
]


class SubContextToolError(Exception):
    """Raised when a step inside the sub-context fails."""

    def __init__(self, step_index: int, tool_name: str, cause: BaseException) -> None:
        super().__init__(
            f"sub-context step {step_index} tool={tool_name!r} failed: {cause!r}"
        )
        self.step_index = step_index
        self.tool_name = tool_name
        self.cause = cause


Transform = Callable[[Any], Any]
ToolExecutor = Callable[[str, dict[str, Any]], Any]


@dataclass(frozen=True, slots=True)
class ToolStep:
    """One step in the sub-context chain."""

    tool_name: str
    args: dict[str, Any]
    transform: Transform | None = None


@dataclass(slots=True)
class SubContextResult:
    """What the parent sees after the sub-context completes.

    ``summary`` is the single value returned to the parent trace.
    ``intermediates_count`` is the number of tool results that were
    produced but not surfaced to the parent (pollution that *was* prevented).
    ``intermediates`` holds the raw values for debugging only; callers who
    care about trace size should discard them via ``discard_intermediates()``.
    """

    summary: Any
    intermediates_count: int
    intermediates: list[Any] = field(default_factory=list)
    step_names: list[str] = field(default_factory=list)

    def discard_intermediates(self) -> None:
        """Drop captured intermediates to keep memory + trace small."""
        self.intermediates.clear()


class ProgrammaticToolRunner:
    """Run a tool chain in a sub-context that hides intermediate output.

    Usage::

        runner = ProgrammaticToolRunner(tool_executor=call_tool)
        result = runner.run(
            steps=[
                ToolStep("search", {"q": "x"}),
                ToolStep("filter", {"field": "status"}, transform=lambda r: r[:3]),
            ],
            summarize=lambda outs: {"count": len(outs[-1])},
        )
        parent_trace.log("sub_context_summary", result.summary)
    """

    def __init__(self, *, tool_executor: ToolExecutor) -> None:
        self._executor = tool_executor

    def run(
        self,
        *,
        steps: Sequence[ToolStep],
        summarize: Callable[[list[Any]], Any],
        keep_intermediates: bool = False,
    ) -> SubContextResult:
        """Execute each step in order, then compute a summary.

        ``summarize`` is given the full list of (post-transform) outputs
        and must return the single value the parent will see. Raising in
        a tool or transform is wrapped in ``SubContextToolError``; the
        caller is responsible for routing this failure to the heal loop
        via an outer try/except.
        """
        outputs: list[Any] = []
        step_names: list[str] = []
        for idx, step in enumerate(steps):
            try:
                raw = self._executor(step.tool_name, step.args)
                value = step.transform(raw) if step.transform is not None else raw
            except SubContextToolError:
                raise
            except BaseException as exc:  # guardian: allow-broad-exception -- sub-context tool isolation: wrap-and-rethrow as SubContextToolError preserves original; never swallows
                raise SubContextToolError(idx, step.tool_name, exc) from exc
            outputs.append(value)
            step_names.append(step.tool_name)

        summary = summarize(outputs)
        result = SubContextResult(
            summary=summary,
            intermediates_count=len(outputs),
            step_names=step_names,
        )
        if keep_intermediates:
            result.intermediates.extend(outputs)
        return result
