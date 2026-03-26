# API Documentation: cache_key_builders

**Target Audience**: developers, api_users

# cache_key_builders API Documentation

**File**: `cache_key_builders.py`
**Classes**: 0
**Functions**: 12


## Functions

- **_require_safe_segment** -> None
- **_require_hash_segment** -> None
- **build_routing_rule_surface_key** -> str
- **build_route_decision_key** -> str
- **build_cap_registry_key** -> str
- **build_compiled_prompt_key** -> str
- **build_template_render_key** -> str
- **build_safety_eval_key** -> str
- **build_orch_plan_key** -> str
- **build_lease_key** -> str
- **build_tool_result_key** -> str
- **build_rag_topk_key** -> str


## Function: _require_safe_segment

**Parameters**: name, value
**Returns**: None
**Description**: Raise ``ValueError`` if *value* contains characters illegal in a key segment.

    Cache keys use ``:`` as the segment delimiter.  Non-hash segments such as
    ``trace_id``, ``template_id``, and ``embedder_version`` are supplied by
    callers and may in principle contain a colon, which would corrupt the
    key schema and create silent collision vulnerabilities.  This guard
    prevents that at construction time.

    Hash-typed segments (64-hex strings) are never affected — SHA-256
    hexdigests contain only ``[0-9a-f]``.
    



## Function: _require_hash_segment

**Parameters**: name, value
**Returns**: None
**Description**: Raise ``ValueError`` if *value* is not a valid SHA-256 hexdigest.

    In strict mode (default, production) the value must be exactly 64
    lowercase hex characters [0-9a-f].  Set the environment variable
    ``REDIS_CACHE_STRICT_HASH_VALIDATION=0`` to fall back to a non-empty
    check only (useful for tests that use short placeholder hashes).
    



## Function: build_routing_rule_surface_key

**Parameters**: routing_state_hash
**Returns**: str
**Description**: Key for the active rule-surface snapshot (read-only L4 mirror).

    Schema::
        routing_rules:{routing_state_hash}

    Invalidated when the routing ruleset changes (new ``routing_state_hash``).
    



## Function: build_route_decision_key

**Parameters**: intent_hash, policy_hash, routing_state_hash
**Returns**: str
**Description**: Key for a memoised ``RouteDecisionArtifact``.

    Schema::
        route_decision:{intent_hash}:{policy_hash}:{routing_state_hash}

    All three segments are required so a stale decision is never served
    when any input surface changes.
    



## Function: build_cap_registry_key

**Parameters**: cap_registry_hash
**Returns**: str
**Description**: Key for the capability-registry / tool-inventory mirror.

    Schema::
        cap_registry:{cap_registry_hash}

    Value holds allowlists, tool availability, and rate-limit envelopes.
    



## Function: build_compiled_prompt_key

**Parameters**: prompt_bom_hash, s0_hash, i0_hash, d0_hash, c0_hash
**Returns**: str
**Description**: Key for a ``CompiledPromptArtifact`` (final assembled strings + token
    estimate + allowed tool schema + signature).

    Schema::
        compiled_prompt:{prompt_bom_hash}:{s0_hash}:{i0_hash}:{d0_hash}:{c0_hash}

    Segments:
        prompt_bom_hash   — hash of the prompt bill-of-materials
        s0_hash           — sovereign context hash
        i0_hash           — intent hash
        d0_hash           — document / retrieval context hash
        c0_hash           — constraint / policy hash
    



## Function: build_template_render_key

**Parameters**: template_id, template_version, args_hash
**Returns**: str
**Description**: Key for a rendered template string (L4 registry mirror).

    Schema::
        template_render:{template_id}:{template_version}:{args_hash}

    ``template_id`` and ``template_version`` are stable, well-known
    identifiers from the L4 template registry (not user-supplied free text).
    ``args_hash`` is the SHA-256 of the canonical-JSON of the render args.
    



## Function: build_safety_eval_key

**Parameters**: compiled_prompt_hash, policy_hash, toolset_hash
**Returns**: str
**Description**: Key for a memoised safety-evaluation result.

    Schema::
        safety_eval:{compiled_prompt_hash}:{policy_hash}:{toolset_hash}

    Value holds allow/block decision, stamped compliance hash, and
    remediation hints.  L5 remains the certifier; this entry caches the
    result only for identical inputs.
    



## Function: build_orch_plan_key

**Parameters**: trace_id, plan_hash, tool_budget_hash
**Returns**: str
**Description**: Key for a resolved orchestration plan (step DAG + deduped tool calls
    + handshake schedule).

    Schema::
        orch_plan:{trace_id}:{plan_hash}:{tool_budget_hash}

    ``trace_id`` scopes the cache entry to a specific execution trace so
    plans from different traces never collide even when ``plan_hash`` is
    identical.
    



## Function: build_lease_key

**Parameters**: plan_hash
**Returns**: str
**Description**: Key for a cross-process execution lease (DB 1, short TTL).

    Schema::
        lease:{plan_hash}

    Value holds ``holder_id``, ``nonce``, and ``semantic_clock_tick``.
    



## Function: build_tool_result_key

**Parameters**: tool_call_hash
**Returns**: str
**Description**: Key for an idempotency record — the exact bytes returned by a tool
    call identified by the hash of its canonical input arguments.

    Schema::
        tool_result:{tool_call_hash}

    Only populated when ``replay_mode=False`` and the tool call is
    strictly input-hashed.  Must be disabled / bypassed in replay mode.
    



## Function: build_rag_topk_key

**Parameters**: u0_hash, embedder_version, seed_pack_manifest_hash, k, cutoff
**Returns**: str
**Description**: Key for a top-k retrieval result set (C0 informational payload only).

    Schema::
        rag_topk:{u0_hash}:{embedder_version}:{seed_pack_manifest_hash}:{k}:{cutoff_r6}

    ``cutoff`` is rounded to 6 decimal places to avoid floating-point noise
    producing different keys for semantically identical cutoffs.

    This entry is strictly informational — it MUST NOT influence
    routing/safety/tier decisions.
    



## Usage Examples

### Function Usage

```python
# Using _require_safe_segment
result = _require_safe_segment(name, value)
```

```python
# Using _require_hash_segment
result = _require_hash_segment(name, value)
```

```python
# Using build_routing_rule_surface_key
result = build_routing_rule_surface_key(routing_state_hash)
```



---
**Generated**: 2026-03-26T09:39:04.696094
**Type**: api_reference
**Quality**: comprehensive
