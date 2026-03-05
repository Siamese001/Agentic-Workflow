"""Deterministic, hash-only cache key builders for all layer seams.

Key-construction rules (enforced by design):
  - Every segment is a content hash, a stable enum value, or a
    well-defined version string — never a wall-clock timestamp.
  - The namespace prefix identifies the layer/concern so Redis keyspace
    collisions are impossible even when DB 0 is shared.
  - No optional or positional magic: every parameter is named, and the
    key format is documented so callers can reproduce it independently.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Internal segment validator
# ---------------------------------------------------------------------------


def _require_safe_segment(name: str, value: str) -> None:
    """Raise ``ValueError`` if *value* contains characters illegal in a key segment.

    Cache keys use ``:`` as the segment delimiter.  Non-hash segments such as
    ``trace_id``, ``template_id``, and ``embedder_version`` are supplied by
    callers and may in principle contain a colon, which would corrupt the
    key schema and create silent collision vulnerabilities.  This guard
    prevents that at construction time.

    Hash-typed segments (64-hex strings) are never affected — SHA-256
    hexdigests contain only ``[0-9a-f]``.
    """
    if ":" in value:
        raise ValueError(
            f"Key segment {name!r} contains illegal ':' character: {value!r}. "
            "Use a slug, version tag, or hex digest instead."
        )
    if not value:
        raise ValueError(f"Key segment {name!r} must not be empty")


# ---------------------------------------------------------------------------
# L0 Routing
# ---------------------------------------------------------------------------


def build_routing_rule_surface_key(routing_state_hash: str) -> str:
    """Key for the active rule-surface snapshot (read-only L4 mirror).

    Schema::
        routing_rules:{routing_state_hash}

    Invalidated when the routing ruleset changes (new ``routing_state_hash``).
    """
    return f"routing_rules:{routing_state_hash}"


def build_route_decision_key(
    intent_hash: str,
    policy_hash: str,
    routing_state_hash: str,
) -> str:
    """Key for a memoised ``RouteDecisionArtifact``.

    Schema::
        route_decision:{intent_hash}:{policy_hash}:{routing_state_hash}

    All three segments are required so a stale decision is never served
    when any input surface changes.
    """
    return f"route_decision:{intent_hash}:{policy_hash}:{routing_state_hash}"


def build_cap_registry_key(cap_registry_hash: str) -> str:
    """Key for the capability-registry / tool-inventory mirror.

    Schema::
        cap_registry:{cap_registry_hash}

    Value holds allowlists, tool availability, and rate-limit envelopes.
    """
    return f"cap_registry:{cap_registry_hash}"


# ---------------------------------------------------------------------------
# L1 / Assembly — compiled prompt artefacts
# ---------------------------------------------------------------------------


def build_compiled_prompt_key(
    prompt_bom_hash: str,
    s0_hash: str,
    i0_hash: str,
    d0_hash: str,
    c0_hash: str,
) -> str:
    """Key for a ``CompiledPromptArtifact`` (final assembled strings + token
    estimate + allowed tool schema + signature).

    Schema::
        compiled_prompt:{prompt_bom_hash}:{s0_hash}:{i0_hash}:{d0_hash}:{c0_hash}

    Segments:
        prompt_bom_hash   — hash of the prompt bill-of-materials
        s0_hash           — sovereign context hash
        i0_hash           — intent hash
        d0_hash           — document / retrieval context hash
        c0_hash           — constraint / policy hash
    """
    return f"compiled_prompt:{prompt_bom_hash}:{s0_hash}:{i0_hash}:{d0_hash}:{c0_hash}"


def build_template_render_key(
    template_id: str,
    template_version: str,
    args_hash: str,
) -> str:
    """Key for a rendered template string (L4 registry mirror).

    Schema::
        template_render:{template_id}:{template_version}:{args_hash}

    ``template_id`` and ``template_version`` are stable, well-known
    identifiers from the L4 template registry (not user-supplied free text).
    ``args_hash`` is the SHA-256 of the canonical-JSON of the render args.
    """
    _require_safe_segment("template_id", template_id)
    _require_safe_segment("template_version", template_version)
    return f"template_render:{template_id}:{template_version}:{args_hash}"


# ---------------------------------------------------------------------------
# L5 Safety — policy evaluation
# ---------------------------------------------------------------------------


def build_safety_eval_key(
    compiled_prompt_hash: str,
    policy_hash: str,
    toolset_hash: str,
) -> str:
    """Key for a memoised safety-evaluation result.

    Schema::
        safety_eval:{compiled_prompt_hash}:{policy_hash}:{toolset_hash}

    Value holds allow/block decision, stamped compliance hash, and
    remediation hints.  L5 remains the certifier; this entry caches the
    result only for identical inputs.
    """
    return f"safety_eval:{compiled_prompt_hash}:{policy_hash}:{toolset_hash}"


# ---------------------------------------------------------------------------
# L3 Orchestration — DAG / step-plan
# ---------------------------------------------------------------------------


def build_orch_plan_key(
    trace_id: str,
    plan_hash: str,
    tool_budget_hash: str,
) -> str:
    """Key for a resolved orchestration plan (step DAG + deduped tool calls
    + handshake schedule).

    Schema::
        orch_plan:{trace_id}:{plan_hash}:{tool_budget_hash}

    ``trace_id`` scopes the cache entry to a specific execution trace so
    plans from different traces never collide even when ``plan_hash`` is
    identical.
    """
    _require_safe_segment("trace_id", trace_id)
    return f"orch_plan:{trace_id}:{plan_hash}:{tool_budget_hash}"


# ---------------------------------------------------------------------------
# L2 Execution — coordination (DB 1)
# ---------------------------------------------------------------------------


def build_lease_key(plan_hash: str) -> str:
    """Key for a cross-process execution lease (DB 1, short TTL).

    Schema::
        lease:{plan_hash}

    Value holds ``holder_id``, ``nonce``, and ``semantic_clock_tick``.
    """
    return f"lease:{plan_hash}"


def build_tool_result_key(tool_call_hash: str) -> str:
    """Key for an idempotency record — the exact bytes returned by a tool
    call identified by the hash of its canonical input arguments.

    Schema::
        tool_result:{tool_call_hash}

    Only populated when ``replay_mode=False`` and the tool call is
    strictly input-hashed.  Must be disabled / bypassed in replay mode.
    """
    return f"tool_result:{tool_call_hash}"


# ---------------------------------------------------------------------------
# C0 / RAG — semantic retrieval memoisation
# ---------------------------------------------------------------------------


def build_rag_topk_key(
    u0_hash: str,
    embedder_version: str,
    seed_pack_manifest_hash: str,
    k: int,
    cutoff: float,
) -> str:
    """Key for a top-k retrieval result set (C0 informational payload only).

    Schema::
        rag_topk:{u0_hash}:{embedder_version}:{seed_pack_manifest_hash}:{k}:{cutoff_r6}

    ``cutoff`` is rounded to 6 decimal places to avoid floating-point noise
    producing different keys for semantically identical cutoffs.

    This entry is strictly informational — it MUST NOT influence
    routing/safety/tier decisions.
    """
    _require_safe_segment("embedder_version", embedder_version)
    cutoff_r6 = f"{cutoff:.6f}"
    return f"rag_topk:{u0_hash}:{embedder_version}:{seed_pack_manifest_hash}:{k}:{cutoff_r6}"
