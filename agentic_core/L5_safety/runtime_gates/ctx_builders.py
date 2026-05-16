"""Per-layer ``GateContext`` builders.

Production layer call sites use these instead of constructing ``GateContext``
inline. Each builder populates exactly the fields the relevant G-gates read,
plus identity fields shared across the mesh.

All builders are pure: same inputs -> same context. Compose via
``merge_ctx`` to assemble multi-layer contexts.
"""

from __future__ import annotations

from dataclasses import fields, replace
from typing import Any

from agentic_core.L5_safety.runtime_gates.contracts import GateContext

# Identity fields propagated across every layer.
_IDENTITY_FIELDS = (
    "request_id",
    "session_id",
    "trace_root",
    "tenant_id",
    "policy_hash",
    "compliance_hash",
    "blueprint_hash",
    "risk_tier",
    "reversible",
    "impact_class",
)


def _identity_kwargs(**identity: Any) -> dict[str, Any]:
    """Filter to identity fields the GateContext recognizes."""
    return {k: v for k, v in identity.items() if k in _IDENTITY_FIELDS and v is not None}


def build_u0_ctx(
    *,
    request_id: str,
    session_id: str,
    trace_root: str,
    tenant_id: str = "",
    intent: dict[str, Any] | None = None,
    caller_scope_baseline: dict[str, Any] | None = None,
    **identity: Any,
) -> GateContext:
    """Context for U0 ingress (G01, G02).

    Required: ``request_id``, ``session_id``, ``trace_root`` (G01 stop).
    Recommended: ``intent`` with ``objective`` + ``raw_text`` + ``payload_bytes``.
    """
    return GateContext(
        request_id=request_id,
        session_id=session_id,
        trace_root=trace_root,
        tenant_id=tenant_id,
        intent=dict(intent or {}),
        caller_scope_baseline=dict(caller_scope_baseline or {}),
        **_identity_kwargs(**identity),
    )


def build_l1_ctx(
    *,
    intent: dict[str, Any],
    **identity: Any,
) -> GateContext:
    """Context for L1 cognition (G03)."""
    return GateContext(
        intent=dict(intent),
        **_identity_kwargs(**identity),
    )


def build_l0_ctx(
    *,
    intent: dict[str, Any] | None = None,
    route_contract: dict[str, Any] | None = None,
    hitl: dict[str, Any] | None = None,
    risk_tier: str = "",
    impact_class: str = "",
    reversible: bool = True,
    policy_hash: str = "",
    **identity: Any,
) -> GateContext:
    """Context for L0 routing (G04, G05, G06, G07)."""
    return GateContext(
        intent=dict(intent or {}),
        route_contract=dict(route_contract or {}),
        hitl=dict(hitl or {}),
        risk_tier=risk_tier,
        impact_class=impact_class,
        reversible=reversible,
        policy_hash=policy_hash,
        **_identity_kwargs(**identity),
    )


def build_c0_ctx(
    *,
    retrieval_plan: dict[str, Any] | None = None,
    evidence: dict[str, Any] | None = None,
    **identity: Any,
) -> GateContext:
    """Context for C0 retrieval / evidence (G08, G09)."""
    return GateContext(
        retrieval_plan=dict(retrieval_plan or {}),
        evidence=dict(evidence or {}),
        **_identity_kwargs(**identity),
    )


def build_prompt_ctx(
    *,
    prompt_packet: dict[str, Any],
    **identity: Any,
) -> GateContext:
    """Context for prompt assembly (G10)."""
    return GateContext(
        prompt_packet=dict(prompt_packet),
        **_identity_kwargs(**identity),
    )


def build_l2_ctx(
    *,
    tool_call: dict[str, Any] | None = None,
    sandbox: dict[str, Any] | None = None,
    capability: dict[str, Any] | None = None,
    **identity: Any,
) -> GateContext:
    """Context for L2 execution (G11..G15).

    The ``sandbox`` and ``capability`` dicts are merged into ``tool_call``
    where the gates read them; production may also pass these via the
    tool_call dict directly.
    """
    tc = dict(tool_call or {})
    if sandbox:
        tc.setdefault("sandbox", {}).update(sandbox)
    if capability:
        tc.setdefault("capability", {}).update(capability)
    return GateContext(
        tool_call=tc,
        **_identity_kwargs(**identity),
    )


def build_l4_ctx(
    *,
    memory_op: dict[str, Any] | None = None,
    **identity: Any,
) -> GateContext:
    """Context for L4 memory access (G16, G17)."""
    return GateContext(
        memory_op=dict(memory_op or {}),
        **_identity_kwargs(**identity),
    )


def build_l3_ctx(
    *,
    workflow_state: dict[str, Any] | None = None,
    budget: dict[str, Any] | None = None,
    **identity: Any,
) -> GateContext:
    """Context for L3 orchestration (G18, G19, G20)."""
    return GateContext(
        workflow_state=dict(workflow_state or {}),
        budget=dict(budget or {}),
        **_identity_kwargs(**identity),
    )


def build_exit_ctx(
    *,
    output: dict[str, Any] | None = None,
    trace_artifacts: dict[str, Any] | None = None,
    **identity: Any,
) -> GateContext:
    """Context for Exit gates (G21..G24, G26)."""
    return GateContext(
        output=dict(output or {}),
        trace_artifacts=dict(trace_artifacts or {}),
        **_identity_kwargs(**identity),
    )


def build_uwg_ctx(
    *,
    memory_op: dict[str, Any],
    compliance_hash: str = "",
    policy_hash: str = "",
    **identity: Any,
) -> GateContext:
    """Context for UWG durable-write sovereignty (G27)."""
    return GateContext(
        memory_op=dict(memory_op),
        compliance_hash=compliance_hash,
        policy_hash=policy_hash,
        **_identity_kwargs(**identity),
    )


def build_l6_ctx(
    *,
    baseline: dict[str, Any] | None = None,
    observed: dict[str, Any] | None = None,
    trace_artifacts: dict[str, Any] | None = None,
    learning_signal: dict[str, Any] | None = None,
    **identity: Any,
) -> GateContext:
    """Context for L6 observability + learning (G25, G28, G29)."""
    return GateContext(
        baseline=dict(baseline or {}),
        observed=dict(observed or {}),
        trace_artifacts=dict(trace_artifacts or {}),
        learning_signal=dict(learning_signal or {}),
        **_identity_kwargs(**identity),
    )


def merge_ctx(*ctxs: GateContext) -> GateContext:
    """Combine partial contexts into a single one.

    Merge order: later contexts override earlier ones for scalar fields;
    dict fields are merged with later wins on key collisions. Lists are
    concatenated.
    """
    if not ctxs:
        return GateContext()
    if len(ctxs) == 1:
        return ctxs[0]
    merged: dict[str, Any] = {}
    for ctx in ctxs:
        for f in fields(ctx):
            value = getattr(ctx, f.name)
            if isinstance(value, dict):
                base = merged.get(f.name, {}) or {}
                if isinstance(base, dict):
                    base = {**base, **value}
                merged[f.name] = base
            elif isinstance(value, list):
                base = merged.get(f.name, []) or []
                if isinstance(base, list):
                    merged[f.name] = base + value
                else:
                    merged[f.name] = list(value)
            else:
                # Scalar: only override if truthy (so default empty values
                # don't clobber a previously-set field).
                if value or f.name not in merged:
                    merged[f.name] = value
    return replace(GateContext(), **merged)


__all__ = [
    "build_c0_ctx",
    "build_exit_ctx",
    "build_l0_ctx",
    "build_l1_ctx",
    "build_l2_ctx",
    "build_l3_ctx",
    "build_l4_ctx",
    "build_l6_ctx",
    "build_prompt_ctx",
    "build_u0_ctx",
    "build_uwg_ctx",
    "merge_ctx",
]
