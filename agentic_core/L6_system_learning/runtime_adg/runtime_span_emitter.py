"""Runtime ADG Tier 2 span emitters.

Plan: `docs/archive/windsurf/legacy-tree/plans/runtime-adg-tier2-emit-sites-b3e9a7.md`
Doctrine: `docs/reference/Runtime ADG and OTEL Spans.md`

Provides three emission helpers that close the 3 Tier 1 emit-site gaps
identified by the Tier 1.5 corpus analyzer:

    runtime.trace_root   -> emit_trace_root()
    L2.step.seal         -> seal_step()
    Exit.disposition     -> emit_exit_disposition()

Each helper appends a span record directly to the tracing adapter's
`_completed_spans` list. This bypasses OpenTelemetry entirely so the
emitter works regardless of OTel availability — the same shape is consumed
by `RuntimeADGMaterializer.materialize()` downstream.

Design rules
------------
  1. Fail-open: if the adapter is None or lacks `_completed_spans`, the
     emitter logs DEBUG and returns. Never raises. Observability code must
     never crash its host.
  2. Idempotent per call: callers decide when to emit. No global state.
  3. Deterministic attribute shape: each span record matches the schema
     consumed by `RuntimeADGMaterializer`.
"""

from __future__ import annotations

# OTel GenAI semconv alignment (Plan: three-bucket-gap-remediation-069806 W3).
# Tier-1 runtime spans — trace_root / step.seal / exit.disposition workflow stages.
# The constants below are imported and surfaced so future span construction
# in this module attaches gen_ai.operation.name, satisfying the upstream
# OTel GenAI SIG semantic conventions.
from agentic_core.L6_observability.semconv.gen_ai import (
    ATTR_OPERATION_NAME,
    OPERATION_INVOKE_WORKFLOW,
)

#: Canonical GenAI operation discriminator for spans emitted by this module.
_GEN_AI_OPERATION: str = OPERATION_INVOKE_WORKFLOW
#: OTel attribute key for the discriminator (gen_ai.operation.name).
_GEN_AI_OPERATION_KEY: str = ATTR_OPERATION_NAME

import contextvars
import hashlib
import logging
import time
import uuid
from contextlib import contextmanager
from typing import Any, Iterator, Sequence

logger = logging.getLogger(__name__)

# Context-var that carries the currently-active tracing adapter. Any code
# running inside an orchestrator context can resolve the adapter without
# having it plumbed through every call frame. Tier 3 uses this so agents
# (e.g. HOPPipelineExecutor._process) can call seal_step() without knowing
# about the adapter wiring.
_current_adapter_var: contextvars.ContextVar[Any] = contextvars.ContextVar(
    "runtime_adg_current_adapter", default=None
)


def set_current_adapter(adapter: Any) -> contextvars.Token:
    """Install `adapter` as the ambient adapter for this context.

    Returns a token that MUST be passed to `reset_current_adapter` to restore
    the previous value (typically from a `finally` in the same frame).
    """
    return _current_adapter_var.set(adapter)


def reset_current_adapter(token: contextvars.Token) -> None:
    """Restore the adapter saved at the matching `set_current_adapter` call."""
    _current_adapter_var.reset(token)


def get_current_adapter() -> Any:
    """Return the ambient adapter, or None if no orchestrator is active."""
    return _current_adapter_var.get()


def back_patch_trace_id(adapter: Any, old_trace_id: str, new_trace_id: str) -> int:
    """Rewrite `trace_id` on previously-emitted spans that used `old_trace_id`.

    Tier 2 harden: `emit_trace_root` stamps a uuid before `super().trace_orchestrator`
    creates the OTel trace, so by the time children know the real trace_id, the
    root span already carries a stale one. After super() yields, callers invoke
    this helper with (stale uuid, real OTel trace_id) to unify the buffer.

    Returns the count of patched spans. Fail-open.
    """
    spans_list = getattr(adapter, "_completed_spans", None)
    if spans_list is None or not isinstance(spans_list, list) or not old_trace_id:
        return 0
    patched = 0
    for record in spans_list:
        if record.get("trace_id") == old_trace_id:
            record["trace_id"] = new_trace_id
            attrs = record.get("attributes")
            if isinstance(attrs, dict) and attrs.get("trace_id") == old_trace_id:
                attrs["trace_id"] = new_trace_id
            patched += 1
    return patched


# Span name constants — MUST match patterns in `span_contracts.py`.
SPAN_TRACE_ROOT = "runtime.trace_root"
SPAN_STEP_SEAL = "L2.step.seal"
SPAN_EXIT_DISPOSITION = "exit.disposition"

# Layer strings — align with `_CategoryContract.layers` in `span_contracts.py`.
_LAYER_L0 = "L0_routing"
_LAYER_L2 = "L2_execution"
_LAYER_L5 = "L5_safety"


def _hash_envelope(payload: Any) -> str:
    """Deterministic content-addressable hash of any JSON-serialisable payload."""
    try:
        canonical = repr(payload).encode("utf-8")
    except (TypeError, ValueError):
        canonical = str(payload).encode("utf-8", errors="replace")
    return hashlib.sha256(canonical).hexdigest()[:16]


def _append_span(
    adapter: Any,
    *,
    name: str,
    kind: str,
    layer: str,
    component: str,
    attributes: dict[str, Any],
    started_at: float,
    duration_ms: float,
    trace_id: str,
    parent_span_id: str = "",
    status: str = "ok",
) -> None:
    """Append a span record to the adapter's `_completed_spans` buffer.

    Fail-open: silently no-op if adapter is missing the expected seam.
    """
    spans_list = getattr(adapter, "_completed_spans", None)
    if spans_list is None or not isinstance(spans_list, list):
        logger.debug(
            "runtime_span_emitter_no_seam",
            extra={"adapter_type": type(adapter).__name__ if adapter else "None"},
        )
        return

    span_id = f"{time.time_ns():016x}"[-16:]
    spans_list.append(
        {
            "ts_utc": int(started_at * 1000),
            "duration_ms": round(duration_ms, 3),
            "kind": kind,
            "trace_id": trace_id,
            "span_id": span_id,
            "parent_span_id": parent_span_id,
            "layer": layer,
            "component": component,
            "name": name,
            "status": status,
            "attributes": dict(attributes),
        }
    )


# ---------------------------------------------------------------------------
# 1) runtime.trace_root — "Which execution is this?"
# ---------------------------------------------------------------------------


def emit_trace_root(
    adapter: Any,
    mission: str,
    trace_id: str | None = None,
    run_id: str | None = None,
    input_envelope: Any = None,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Emit the runtime.trace_root span and return the `trace_id` used.

    Called at the very start of a run, before any L1/L0/C0 work spawns child
    spans. Stamps the three required identity attributes.
    """
    resolved_trace_id = trace_id or uuid.uuid4().hex
    resolved_run_id = run_id or f"run-{uuid.uuid4().hex[:12]}"
    envelope_hash = _hash_envelope(input_envelope) if input_envelope is not None else ""

    attrs: dict[str, Any] = {
        "trace_id": resolved_trace_id,
        "run_id": resolved_run_id,
        "input_envelope_hash": envelope_hash,
        "parent_span_id": "",  # runtime.trace_root has no parent by definition
        "mission": mission,
    }
    if metadata:
        attrs.update(metadata)

    now = time.time()
    _append_span(
        adapter,
        name=SPAN_TRACE_ROOT,
        kind="trace_root",
        layer=_LAYER_L0,
        component="RuntimeIntake",
        attributes=attrs,
        started_at=now,
        duration_ms=0.0,
        trace_id=resolved_trace_id,
        parent_span_id="",
    )
    return resolved_trace_id


# ---------------------------------------------------------------------------
# 2) L2.step.seal — "What did execution finish with?"
# ---------------------------------------------------------------------------


@contextmanager
def seal_step(
    adapter: Any,
    step_id: str,
    trace_id: str,
    parent_span_id: str = "",
    evidence_ids: Sequence[str] | None = None,
    replay_key: str | None = None,
    component: str = "L2Execution",
) -> Iterator[dict[str, Any]]:
    """Context manager that seals an L2 execution step.

    Usage:

        with seal_step(adapter, step_id="s1", trace_id=tid) as seal:
            seal["output"] = do_work()
            seal["evidence_ids"] = ("ev-1", "ev-2")

    On exit: stamps `output_hash` from `seal["output"]`, plus
    `evidence_ids`, `replay_key`, `lineage_hash` (hash of parent+output).
    """
    started_at = time.time()
    bag: dict[str, Any] = {
        "output": None,
        "evidence_ids": tuple(evidence_ids) if evidence_ids else (),
        "replay_key": replay_key or f"replay-{uuid.uuid4().hex[:12]}",
    }
    status = "error"
    try:
        yield bag
        status = "ok"
    except (OSError, ValueError, TypeError, RuntimeError):
        raise
    finally:
        duration_ms = (time.time() - started_at) * 1000
        output_hash = _hash_envelope(bag.get("output"))
        evidence = tuple(bag.get("evidence_ids") or ())
        lineage_hash = _hash_envelope((parent_span_id, output_hash))
        attrs: dict[str, Any] = {
            "step_id": step_id,
            "output_hash": output_hash,
            "output_artifact_ids": list(evidence),  # best-effort alias
            "evidence_ids": list(evidence),
            "lineage_hash": lineage_hash,
            "replay_key": bag["replay_key"],
            "parent_span_id": parent_span_id,
        }
        _append_span(
            adapter,
            name=SPAN_STEP_SEAL,
            kind="seal",
            layer=_LAYER_L2,
            component=component,
            attributes=attrs,
            started_at=started_at,
            duration_ms=duration_ms,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            status=status,
        )


# ---------------------------------------------------------------------------
# 3) Exit.disposition — "Was it allowed / denied / escalated?"
# ---------------------------------------------------------------------------

# Legal values for exit_disposition — must match runtime Exit contract.
_VALID_DISPOSITIONS = frozenset({"allow", "deny", "reroute", "escalate", "commit_request"})


def emit_exit_disposition(
    adapter: Any,
    trace_id: str,
    disposition: str,
    policy_hash: str | None = None,
    reason_codes: Sequence[str] | None = None,
    guardrail_result: str | None = None,
    parent_span_id: str = "",
    metadata: dict[str, Any] | None = None,
) -> None:
    """Emit the Exit.disposition span.

    Called at the end of a run by the Exit Eval gate. `disposition` MUST
    be one of `_VALID_DISPOSITIONS`.
    """
    if disposition not in _VALID_DISPOSITIONS:
        raise ValueError(
            f"invalid exit_disposition {disposition!r}; must be one of {sorted(_VALID_DISPOSITIONS)}"
        )
    attrs: dict[str, Any] = {
        "exit_disposition": disposition,
        "policy_hash": policy_hash or "",
        "reason_codes": list(reason_codes) if reason_codes else [],
        "guardrail_result": guardrail_result or "",
        "parent_span_id": parent_span_id,
    }
    if metadata:
        attrs.update(metadata)
    now = time.time()
    _append_span(
        adapter,
        name=SPAN_EXIT_DISPOSITION,
        kind="exit",
        layer=_LAYER_L5,
        component="ExitGate",
        attributes=attrs,
        started_at=now,
        duration_ms=0.0,
        trace_id=trace_id,
        parent_span_id=parent_span_id,
    )


__all__ = [
    "SPAN_TRACE_ROOT",
    "SPAN_STEP_SEAL",
    "SPAN_EXIT_DISPOSITION",
    "emit_trace_root",
    "seal_step",
    "emit_exit_disposition",
    "set_current_adapter",
    "reset_current_adapter",
    "get_current_adapter",
    "back_patch_trace_id",
]
