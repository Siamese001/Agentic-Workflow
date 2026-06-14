"""X1H observable-trace check — a pure validator over harvested span records.

Answers one question for a finished run: *did this run actually leave an
observable trace?* It is the runtime counterpart to L6 eval-readiness, but it
runs at/after Exit over the raw span records (before they are shaped into L6
``raw_exhaust``), so the spine can stamp a ``trace_completeness_status`` and
populate ``source_exhaust`` gap codes.

It is **pure and non-fatal**: it never raises and never crashes the run. Callers
use the verdict to annotate evidence, not to abort the current run.

Verdict semantics:
  * ``PASS``    — a trace root exists, an Exit disposition span exists (for runs
                  that crossed Exit), and an L2 execution/seal span exists (for
                  executed, non-terminal runs).
  * ``PARTIAL`` — a trace root exists but stage coverage is incomplete
                  (e.g. the L2 seal span is missing on an executed run).
  * ``FAIL``    — no spans at all, no trace root, or no Exit disposition for a
                  run that crossed Exit.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

__all__ = ["ObservableTraceCheck", "check_observable_trace"]


@dataclass(frozen=True, slots=True)
class ObservableTraceCheck:
    """Result of :func:`check_observable_trace`."""

    status: str  # PASS | PARTIAL | FAIL
    missing: tuple[str, ...]
    span_count: int
    trace_root: str
    reason_codes: tuple[str, ...]


def _first_trace_id(spans: Sequence[Mapping[str, Any]]) -> str:
    for span in spans:
        tid = str(span.get("trace_id", "") or "")
        if tid:
            return tid
    return ""


def _name(span: Mapping[str, Any]) -> str:
    return str(span.get("name", "") or "").lower()


def _kind(span: Mapping[str, Any]) -> str:
    return str(span.get("kind", "") or "").lower()


def _layer(span: Mapping[str, Any]) -> str:
    return str(span.get("layer", "") or "").upper()


def check_observable_trace(
    spans: Sequence[Mapping[str, Any]],
    *,
    require_trace_root: bool = True,
    require_exit_disposition: bool = True,
    require_l2_for_executed_run: bool = True,
) -> ObservableTraceCheck:
    """Validate that *spans* constitute an observable runtime trace.

    All ``require_*`` flags default True (the executed-run contract). Set the
    relevant flag False for terminal/short-circuit runs that legitimately skip a
    stage (e.g. an L0 R5 terminal never executes L2).
    """
    span_list = list(spans or [])
    span_count = len(span_list)
    if span_count == 0:
        return ObservableTraceCheck("FAIL", ("spans",), 0, "", ("NO_SPANS",))

    trace_root = _first_trace_id(span_list)
    has_trace_root = bool(trace_root) or any(_name(s) == "runtime.trace_root" for s in span_list)
    has_exit = any("exit" in _name(s) or _kind(s) == "exit" for s in span_list)
    has_l2 = any(_layer(s).startswith("L2") or _kind(s) == "seal" or _name(s).startswith("l2.") for s in span_list)

    missing: list[str] = []
    reason_codes: list[str] = []
    if require_trace_root and not has_trace_root:
        missing.append("trace_root")
        reason_codes.append("TRACE_ROOT_MISSING")
    if require_exit_disposition and not has_exit:
        missing.append("exit_disposition")
        reason_codes.append("EXIT_DISPOSITION_MISSING")
    if require_l2_for_executed_run and not has_l2:
        missing.append("l2_execution")
        reason_codes.append("L2_EXECUTION_SPAN_MISSING")

    # trace_root / exit_disposition are hard requirements (when required); their
    # absence is a FAIL. Incomplete coverage (only the L2 stage missing) is PARTIAL.
    hard_missing = [m for m in missing if m in ("trace_root", "exit_disposition")]
    if hard_missing:
        status = "FAIL"
    elif missing:
        status = "PARTIAL"
    else:
        status = "PASS"
    return ObservableTraceCheck(status, tuple(missing), span_count, trace_root, tuple(reason_codes))
