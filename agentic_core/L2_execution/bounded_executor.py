"""L2 bounded executor — single entry point that consumes a CompiledPromptEnvelope
and emits a sealed artifact ready for Exit Eval.

This module is the minimum-viable production path between Prompt Assembly
and Exit. It is deliberately thin: it does NOT itself implement model
invocation or tool calls; instead, callers inject a ``model_invoke``
callable (production wires the SovereignLLMGateway / Anthropic client; the
proof harness wires a deterministic stub).

What this module DOES own:

  - Capability token issuance (a bounded, single-use ticket scoped to one
    invocation).
  - Sandbox envelope construction (caps token / latency / cost / retry).
  - Tool/model invocation record collection.
  - Retry loop with bounded attempts and explicit failure record.
  - Sealed artifact construction in the exact shape consumed by
    :class:`agentic_core.L5_safety.eval_spine.exit_eval.SealedArtifact`.

What it does NOT do (anti-cheat):

  - Make a model call without an injected callable (no implicit defaults).
  - Mutate L4 state (commits go through UWG, not L2).
  - Invent answer text (caller's ``model_invoke`` is the only source).
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Mapping, Sequence

if TYPE_CHECKING:
    # Plan: adg-p0-wave1-protected-plane-fixes (Group B). The L2 executor
    # only references ``CompiledPromptEnvelope`` as a type annotation (no
    # runtime construction), so a ``TYPE_CHECKING``-gated import removes
    # the L2 → L_PG runtime layer-violation edge while preserving the
    # exact same static-typing surface for callers and IDEs.
    from agentic_core.prompt_governance.orchestrator import CompiledPromptEnvelope


class L2ExecutorError(RuntimeError):
    """Raised on unrecoverable L2 execution failure."""


# ---------------------------------------------------------------------------
# Capability token + sandbox envelope (lightweight, scoped to one call)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CapabilityToken:
    """Minimal single-use ticket issued for one L2 invocation.

    Production wiring may swap this for the v4 capability token in
    ``agentic_core.L2_execution.types.capability_token_v4_types``. This
    shape is the smallest contract that satisfies the spec:
    invocation_id, principal, scope, expiry, ledger_ref.
    """

    token_id: str
    invocation_id: str
    principal_id: str
    tenant_scope: str
    capability_class: str
    issued_at_unix: float
    expires_at_unix: float
    ledger_ref: str = ""

    @property
    def expired(self) -> bool:
        return time.time() > self.expires_at_unix


@dataclass(frozen=True)
class SandboxEnvelope:
    """Hard caps applied to one L2 invocation."""

    max_tokens: int
    max_latency_ms: int
    max_tool_calls: int
    max_cost_usd: float
    max_attempts: int = 1
    forbidden_tools: tuple[str, ...] = ()


@dataclass(frozen=True)
class ModelInvocationRecord:
    """One model call attempt."""

    attempt_index: int
    model_id: str
    started_at_unix: float
    ended_at_unix: float
    output_text: str
    token_usage: int
    error: str | None = None

    @property
    def latency_ms(self) -> int:
        return int((self.ended_at_unix - self.started_at_unix) * 1000)


@dataclass(frozen=True)
class ToolInvocationRecord:
    """One tool call attempt (placeholder for routes that issue tools)."""

    attempt_index: int
    tool_name: str
    args_hash: str
    started_at_unix: float
    ended_at_unix: float
    return_code: int
    stdout_ref: str = ""
    stderr_ref: str = ""
    error: str | None = None


@dataclass(frozen=True)
class L2SealedArtifact:
    """Sealed L2 output. Field names are 1:1 with
    ``agentic_core.L5_safety.eval_spine.exit_eval.SealedArtifact`` so the
    shape can be passed directly into ``evaluate_exit``.
    """

    request_id: str
    trace_id: str
    answer_text: str
    artifact_payload: Any
    context_text: str
    predicted_tool_calls: tuple[Mapping[str, str], ...]
    retry_count: int
    failure: bool
    latency_ms: int
    tokens_consumed: int
    cost_usd_consumed: float
    session_id: str | None
    tenant: str | None
    agent_class: str | None
    agent_version: str | None
    capability_token_id: str
    invocation_records: tuple[ModelInvocationRecord, ...] = ()
    tool_records: tuple[ToolInvocationRecord, ...] = ()
    replay_metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_exit_artifact_kwargs(self) -> dict[str, Any]:
        """Return the kwargs needed to construct the Exit Eval SealedArtifact."""
        return {
            "request_id": self.request_id,
            "trace_id": self.trace_id,
            "answer_text": self.answer_text,
            "artifact_payload": self.artifact_payload,
            "context_text": self.context_text,
            "predicted_tool_calls": self.predicted_tool_calls,
            "retry_count": self.retry_count,
            "failure": self.failure,
            "latency_ms": self.latency_ms,
            "tokens_consumed": self.tokens_consumed,
            "cost_usd_consumed": self.cost_usd_consumed,
            "session_id": self.session_id,
            "tenant": self.tenant,
            "agent_class": self.agent_class,
            "agent_version": self.agent_version,
        }


# ---------------------------------------------------------------------------
# Issuance helpers
# ---------------------------------------------------------------------------

def issue_capability_token(
    *,
    request_id: str,
    principal_id: str,
    tenant_scope: str,
    capability_class: str = "model_invoke",
    ttl_seconds: int = 30,
) -> CapabilityToken:
    """Mint a single-use capability token for one L2 invocation."""
    now = time.time()
    return CapabilityToken(
        token_id=f"cap-{uuid.uuid4().hex[:12]}",
        invocation_id=f"inv-{uuid.uuid4().hex[:12]}",
        principal_id=principal_id,
        tenant_scope=tenant_scope,
        capability_class=capability_class,
        issued_at_unix=now,
        expires_at_unix=now + ttl_seconds,
        ledger_ref=f"req:{request_id}",
    )


def build_sandbox_from_envelope(
    envelope: CompiledPromptEnvelope,
    *,
    max_attempts: int = 1,
) -> SandboxEnvelope:
    """Derive sandbox caps from the compiled prompt envelope's budget report."""
    budget = envelope.prompt_budget_report or {}
    max_tokens = int(budget.get("input_token_estimate", 0) or 0) + int(
        budget.get("reserved_output_tokens", 4096) or 4096
    )
    return SandboxEnvelope(
        max_tokens=max_tokens or 8000,
        max_latency_ms=30_000,
        max_tool_calls=4,
        max_cost_usd=0.50,
        max_attempts=max_attempts,
        forbidden_tools=("system_shell", "uwg_commit"),
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

ModelInvokeFn = Callable[["CompiledPromptEnvelope"], "ModelInvokeResult"]


@dataclass(frozen=True)
class ModelInvokeResult:
    """Return shape of an injected ``model_invoke`` callable."""

    output_text: str
    token_usage: int
    model_id: str = "injected"
    cost_usd: float = 0.0
    error: str | None = None


def execute(
    envelope: CompiledPromptEnvelope,
    *,
    model_invoke: ModelInvokeFn,
    request_id: str,
    trace_id: str,
    session_id: str | None = None,
    tenant: str = "default",
    principal_id: str = "default",
    agent_class: str = "L2BoundedExecutor",
    agent_version: str = "1.0",
    max_attempts: int = 1,
    tool_invocations: Sequence[ToolInvocationRecord] = (),
) -> L2SealedArtifact:
    """Run one bounded L2 invocation and return a sealed artifact.

    Args:
        envelope: Output of
            :func:`agentic_core.prompt_governance.orchestrator.assemble_prompt`.
            MUST have ``is_dispatchable=True``; otherwise this function
            raises :class:`L2ExecutorError`.
        model_invoke: Caller-provided callable that performs the actual
            model call. Returns :class:`ModelInvokeResult`. The proof
            harness injects a deterministic stub; production wires the
            sovereign gateway / Anthropic client.
        request_id, trace_id: Telemetry ids from upstream.
        max_attempts: Bounded retry count. Each attempt is recorded
            individually in ``invocation_records``.
        tool_invocations: Optional pre-recorded tool calls (e.g. for
            R4_SINGLE_ACTION routes).

    Returns:
        :class:`L2SealedArtifact` ready to feed into Exit Eval.

    Raises:
        L2ExecutorError: When the envelope is not dispatchable, the
            sandbox is breached, or all attempts fail.
    """
    if not envelope.is_dispatchable:
        raise L2ExecutorError(
            f"PromptEnvelope is not dispatchable: "
            f"disposition={envelope.dispatch_disposition}"
        )

    token = issue_capability_token(
        request_id=request_id,
        principal_id=principal_id,
        tenant_scope=tenant,
    )
    sandbox = build_sandbox_from_envelope(envelope, max_attempts=max_attempts)

    invocation_records: list[ModelInvocationRecord] = []
    final_output = ""
    final_tokens = 0
    final_cost = 0.0
    final_model_id = ""
    final_error: str | None = None

    started_overall = time.time()
    for attempt in range(1, sandbox.max_attempts + 1):
        if token.expired:
            raise L2ExecutorError("capability token expired before invocation")
        started = time.time()
        try:
            result = model_invoke(envelope)
        except Exception as exc:  # guardian: allow-broad-catch -- caller-supplied callable; we record any failure as a sealed attempt and let Exit Eval grade it
            ended = time.time()
            invocation_records.append(
                ModelInvocationRecord(
                    attempt_index=attempt,
                    model_id="unknown",
                    started_at_unix=started,
                    ended_at_unix=ended,
                    output_text="",
                    token_usage=0,
                    error=repr(exc),
                )
            )
            final_error = repr(exc)
            continue

        ended = time.time()
        invocation_records.append(
            ModelInvocationRecord(
                attempt_index=attempt,
                model_id=result.model_id,
                started_at_unix=started,
                ended_at_unix=ended,
                output_text=result.output_text,
                token_usage=result.token_usage,
                error=result.error,
            )
        )
        if result.error:
            final_error = result.error
            continue
        final_output = result.output_text
        final_tokens = result.token_usage
        final_cost = result.cost_usd
        final_model_id = result.model_id
        final_error = None
        break

    ended_overall = time.time()
    latency_ms = int((ended_overall - started_overall) * 1000)
    failure = bool(final_error) or not final_output
    retry_count = max(0, len(invocation_records) - 1)

    if final_tokens > sandbox.max_tokens:
        # Sandbox breach is a sealed event, not a crash. Mark failure and
        # let Exit Eval route to deny_reroute / escalate.
        failure = True
        final_error = (
            (final_error or "")
            + f" sandbox_breach:tokens_consumed={final_tokens}>max={sandbox.max_tokens}"
        )

    context_text = "\n".join(
        f"[{h.candidate.manifest.file_path}:{h.candidate.manifest.line_range[0]}-"
        f"{h.candidate.manifest.line_range[1]}] {h.candidate.text[:200]}"
        for h in envelope.envelope.metadata.get("c0_chunks", [])  # type: ignore[union-attr]
    ) if isinstance(envelope.envelope.metadata, dict) else ""

    replay_metadata: dict[str, Any] = {
        **dict(envelope.replay_metadata),
        "capability_token_id": token.token_id,
        "invocation_id": token.invocation_id,
        "sandbox_max_tokens": sandbox.max_tokens,
        "sandbox_max_latency_ms": sandbox.max_latency_ms,
        "sandbox_max_attempts": sandbox.max_attempts,
        "model_id": final_model_id,
        "attempts": len(invocation_records),
        "final_error": final_error,
    }

    sealed = L2SealedArtifact(
        request_id=request_id,
        trace_id=trace_id,
        answer_text=final_output,
        artifact_payload=None,  # caller may attach typed payload via wrapper
        context_text=context_text,
        predicted_tool_calls=tuple(
            {"tool_name": t.tool_name, "return_code": str(t.return_code)}
            for t in tool_invocations
        ),
        retry_count=retry_count,
        failure=failure,
        latency_ms=latency_ms,
        tokens_consumed=final_tokens,
        cost_usd_consumed=final_cost,
        session_id=session_id,
        tenant=tenant,
        agent_class=agent_class,
        agent_version=agent_version,
        capability_token_id=token.token_id,
        invocation_records=tuple(invocation_records),
        tool_records=tuple(tool_invocations),
        replay_metadata=replay_metadata,
    )
    return sealed


__all__ = [
    "CapabilityToken",
    "L2ExecutorError",
    "L2SealedArtifact",
    "ModelInvocationRecord",
    "ModelInvokeFn",
    "ModelInvokeResult",
    "SandboxEnvelope",
    "ToolInvocationRecord",
    "build_sandbox_from_envelope",
    "execute",
    "issue_capability_token",
]
