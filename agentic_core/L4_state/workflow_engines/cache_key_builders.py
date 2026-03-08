"""Deterministic cache key builders for all layer seams.

All key-building functions produce namespace-prefixed, hash-only keys that
enforce the non-authoritative cache contract:
  - No wall-clock timestamps.
  - No random nonces (unless also stored in the deterministic transcript).
  - All ``*_hash`` parameters are SHA-256 hexdigests (64 lowercase hex chars).
  - Keys are stable: identical inputs always produce identical keys.
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


def _require_hash_segment(name: str, value: str) -> None:
    """Raise ``ValueError`` if *value* is not a valid SHA-256 hexdigest.

    In strict mode (default, production) the value must be exactly 64
    lowercase hex characters [0-9a-f].  Set the environment variable
    ``REDIS_CACHE_STRICT_HASH_VALIDATION=0`` to fall back to a non-empty
    check only (useful for tests that use short placeholder hashes).
    """
    import os

    if not value:
        raise ValueError(f"Hash segment {name!r} must not be empty")
    strict = os.environ.get("REDIS_CACHE_STRICT_HASH_VALIDATION", "1") != "0"
    if strict:
        import re

        if not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError(
                f"Hash segment {name!r} must be a 64-char lowercase SHA-256 hexdigest, "
                f"got {value!r}. Set REDIS_CACHE_STRICT_HASH_VALIDATION=0 to disable "
                "this check in tests."
            )


# ---------------------------------------------------------------------------
# L0 Routing
# ---------------------------------------------------------------------------


def build_routing_rule_surface_key(routing_state_hash: str) -> str:
    """Key for the active rule-surface snapshot (read-only L4 mirror).

    Schema::
        routing_rules:{routing_state_hash}

    Invalidated when the routing ruleset changes (new ``routing_state_hash``).
    """
    _require_hash_segment("routing_state_hash", routing_state_hash)
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
    _require_hash_segment("intent_hash", intent_hash)
    _require_hash_segment("policy_hash", policy_hash)
    _require_hash_segment("routing_state_hash", routing_state_hash)
    return f"route_decision:{intent_hash}:{policy_hash}:{routing_state_hash}"


def build_cap_registry_key(cap_registry_hash: str) -> str:
    """Key for the capability-registry / tool-inventory mirror.

    Schema::
        cap_registry:{cap_registry_hash}

    Value holds allowlists, tool availability, and rate-limit envelopes.
    """
    _require_hash_segment("cap_registry_hash", cap_registry_hash)
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
    _require_hash_segment("prompt_bom_hash", prompt_bom_hash)
    _require_hash_segment("s0_hash", s0_hash)
    _require_hash_segment("i0_hash", i0_hash)
    _require_hash_segment("d0_hash", d0_hash)
    _require_hash_segment("c0_hash", c0_hash)
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
    _require_hash_segment("args_hash", args_hash)
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
    _require_hash_segment("compiled_prompt_hash", compiled_prompt_hash)
    _require_hash_segment("policy_hash", policy_hash)
    _require_hash_segment("toolset_hash", toolset_hash)
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
    _require_hash_segment("plan_hash", plan_hash)
    _require_hash_segment("tool_budget_hash", tool_budget_hash)
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
    _require_hash_segment("plan_hash", plan_hash)
    return f"lease:{plan_hash}"


def build_tool_result_key(tool_call_hash: str) -> str:
    """Key for an idempotency record — the exact bytes returned by a tool
    call identified by the hash of its canonical input arguments.

    Schema::
        tool_result:{tool_call_hash}

    Only populated when ``replay_mode=False`` and the tool call is
    strictly input-hashed.  Must be disabled / bypassed in replay mode.
    """
    _require_hash_segment("tool_call_hash", tool_call_hash)
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
    _require_hash_segment("u0_hash", u0_hash)
    _require_safe_segment("embedder_version", embedder_version)
    _require_hash_segment("seed_pack_manifest_hash", seed_pack_manifest_hash)
    cutoff_r6 = f"{cutoff:.6f}"
    return f"rag_topk:{u0_hash}:{embedder_version}:{seed_pack_manifest_hash}:{k}:{cutoff_r6}"
