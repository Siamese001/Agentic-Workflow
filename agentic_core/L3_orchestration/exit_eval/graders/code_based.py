"""Code-based (deterministic) graders.

Per grader_composition_spec §1, code-based graders are the only class
permitted for hard sub-gates that carry safety invariants.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping

from agentic_core.L3_orchestration.exit_eval.dimension import (
    Dimension,
    GraderClass,
)
from agentic_core.L3_orchestration.exit_eval.graders.base import (
    Grader,
    GraderError,
    GraderOutput,
)


class CodeBasedGrader(Grader):
    """Thin base for deterministic graders."""

    grader_class = GraderClass.CODE_BASED


class SchemaGrader(CodeBasedGrader):
    """Checks that agent output satisfies a declared schema predicate.

    The predicate receives the agent output and returns a bool (passes)
    plus an optional reason string bundled as evidence.

    Context keys expected:
        ``output``: the agent output to validate.
    """

    def __init__(
        self,
        predicate: Callable[[Any], tuple[bool, str]],
    ) -> None:
        self._predicate = predicate

    def grade(
        self,
        dimension: Dimension,
        context: Mapping[str, Any],
    ) -> GraderOutput:
        if "output" not in context:
            raise GraderError(f"SchemaGrader on {dimension.name}: context missing 'output'")
        try:
            passed, reason = self._predicate(context["output"])
        except (ValueError, TypeError, KeyError, AttributeError) as exc:
            raise GraderError(f"SchemaGrader on {dimension.name}: predicate failed: {exc}") from exc
        # Binary score in [0, 1]
        return GraderOutput(
            score=1.0 if passed else 0.0,
            abstain=False,
            evidence={"reason": reason},
        )


class CitationGrader(CodeBasedGrader):
    """Binary check that every citation is resolvable.

    Context keys expected:
        ``citations``: iterable of citation identifiers.
        ``resolver``: callable ``(citation_id) -> bool``.
    """

    def grade(
        self,
        dimension: Dimension,
        context: Mapping[str, Any],
    ) -> GraderOutput:
        citations = context.get("citations")
        resolver = context.get("resolver")
        if citations is None or resolver is None:
            raise GraderError(
                f"CitationGrader on {dimension.name}: context missing 'citations' or 'resolver'"
            )
        if not callable(resolver):
            raise GraderError(f"CitationGrader on {dimension.name}: resolver must be callable")

        unresolved: list[str] = []
        for cid in citations:
            try:
                ok = bool(resolver(cid))
            except (ValueError, TypeError, KeyError, RuntimeError) as exc:
                raise GraderError(
                    f"CitationGrader on {dimension.name}: resolver raised on {cid!r}: {exc}"
                ) from exc
            if not ok:
                unresolved.append(str(cid))

        total = len(list(citations)) if not isinstance(citations, list) else len(citations)
        # Score = 1.0 iff no unresolved citations. A resolvable partial score
        # would mask missing citations on a hard sub-gate — not permitted.
        score = 1.0 if not unresolved else 0.0
        return GraderOutput(
            score=score,
            abstain=False,
            evidence={
                "total_citations": total,
                "unresolved": unresolved,
            },
        )


__all__ = ["CitationGrader", "CodeBasedGrader", "SchemaGrader"]
