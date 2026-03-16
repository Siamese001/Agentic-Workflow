"""Redis key namespace governance for the agentic architecture.

Enforces a deterministic key schema:
    {layer}:{component}:{scope}:{entity_type}:{content_hash}

Design invariants:
  1. LAYER-PREFIXED: Every key carries its owning layer (L0-L6, L_SL, etc.)
  2. SCOPE-ISOLATED: Mission-scoped keys never collide with global keys
  3. HASH-ONLY IDENTITY: The last segment is always a content hash
  4. NO WALL-CLOCK: No timestamps in key segments (breaks determinism)
  5. COLON-FREE SEGMENTS: Segments must not contain ':' (validated at construction)

Key examples::
    L4:semantic_cache:m_abc123:file:e3b0c44298fc1c14
    L1:assembly:global:thought:a1b2c3d4e5f6a7b8
    L3:orchestration:global:workflow:def456789abc1234
    L2:coordination:global:lease:resource_xyz_hash16
    L_SL:rag_topk:global:retrieval:0f3ec30c8c678abc

[SSOT] Canonical implementation for Redis key namespace governance.
"""

from __future__ import annotations

import re

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "namespace_builder", "p0_governance")
_emit_reads_policy_state("p0", "namespace_builder", "policy_binding")
_emit_snapshots_state("p0", "namespace_builder", "state_snapshot")
emit_replay_key("p0", "namespace_builder")
emit_determinism_digest("p0", "namespace_builder")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

_LAYER_NAMES = frozenset(
    {
        "L0",
        "L1",
        "L2",
        "L3",
        "L4",
        "L5",
        "L6",
        "L_APP",
        "L_SL",
        "L_OPS",
        "L_TOOLS",
        "L_TEST",
        "L_RUNTIME",
        "L_SHARED",
        "L_UNKNOWN",
    }
)

_SAFE_SEGMENT_RE = re.compile(r"^[a-zA-Z0-9_\-\.]+$")
_HEX_SUFFIX_RE = re.compile(r"^[0-9a-f]{8,64}$")

_SCOPE_GLOBAL = "global"


def _validate_segment(name: str, value: str) -> None:
    """Raise ValueError if a segment contains illegal characters."""
    if not value:
        raise ValueError(f"Namespace segment '{name}' must not be empty")
    if ":" in value:
        raise ValueError(f"Namespace segment '{name}' contains illegal ':' — use slug or hash: {value!r}")
    if not _SAFE_SEGMENT_RE.match(value):
        raise ValueError(
            f"Namespace segment '{name}' contains special characters: {value!r}. Use only [a-zA-Z0-9_.-]"
        )


def build_key(
    layer: str,
    component: str,
    entity_type: str,
    content_hash: str,
    *,
    mission_id: str = _SCOPE_GLOBAL,
) -> str:
    """Build a fully-qualified, governed Redis cache key.

    Args:
        layer: ADG layer label (e.g. "L4", "L_SL"). Must be a known layer name.
        component: Component slug within the layer (e.g. "semantic_cache", "rag_topk").
        entity_type: What kind of entity is cached (e.g. "file", "thought", "workflow").
        content_hash: SHA-256 hexdigest or short 8-64 hex suffix identifying the value.
        mission_id: Optional mission/tenant scope. Defaults to "global".

    Returns:
        Governed key string, e.g. "L4:semantic_cache:m_abc123:file:e3b0c44298fc1c14"

    Raises:
        ValueError: If any segment is invalid or layer is unknown.
    """
    if layer not in _LAYER_NAMES:
        raise ValueError(f"Unknown layer '{layer}'. Valid layers: {sorted(_LAYER_NAMES)}")
    _validate_segment("component", component)
    _validate_segment("entity_type", entity_type)
    _validate_segment("mission_id", mission_id)

    if not _HEX_SUFFIX_RE.match(content_hash):
        raise ValueError(f"content_hash must be a hex string (8-64 chars): {content_hash!r}")

    return f"{layer}:{component}:{mission_id}:{entity_type}:{content_hash}"


def build_mission_key(
    layer: str,
    component: str,
    entity_type: str,
    content_hash: str,
    mission_id: str,
) -> str:
    """Convenience wrapper — build a mission-scoped key.

    Normalises the mission_id by stripping non-safe characters.
    """
    safe_mission = re.sub(r"[^a-zA-Z0-9_\-]", "_", mission_id)[:32]
    return build_key(layer, component, entity_type, content_hash, mission_id=safe_mission)


def build_global_key(
    layer: str,
    component: str,
    entity_type: str,
    content_hash: str,
) -> str:
    """Convenience wrapper — build a global (non-mission-scoped) key."""
    return build_key(layer, component, entity_type, content_hash, mission_id=_SCOPE_GLOBAL)


def parse_key(key: str) -> dict[str, str]:
    """Parse a governed key back into its component parts.

    Args:
        key: A key produced by ``build_key``.

    Returns:
        Dict with keys: layer, component, mission_id, entity_type, content_hash

    Raises:
        ValueError: If the key does not have exactly 5 colon-separated segments.
    """
    parts = key.split(":")
    if len(parts) != 5:
        raise ValueError(f"Expected 5 colon-separated segments, got {len(parts)}: {key!r}")
    return {
        "layer": parts[0],
        "component": parts[1],
        "mission_id": parts[2],
        "entity_type": parts[3],
        "content_hash": parts[4],
    }


def key_prefix(layer: str, component: str, *, mission_id: str = _SCOPE_GLOBAL) -> str:
    """Return the scan/delete prefix for a layer+component+scope.

    Useful for bulk eviction::

        pattern = key_prefix("L4", "semantic_cache", mission_id="m_abc123") + "*"
        # → "L4:semantic_cache:m_abc123:*"

    Args:
        layer: ADG layer label.
        component: Component slug.
        mission_id: Optional scope (default "global").

    Returns:
        Prefix string ending with ":"  ready for glob append.
    """
    if layer not in _LAYER_NAMES:
        raise ValueError(f"Unknown layer '{layer}'")
    _validate_segment("component", component)
    _validate_segment("mission_id", mission_id)
    return f"{layer}:{component}:{mission_id}:"


# ---------------------------------------------------------------------------
# Pre-defined component slugs (prevents typos across the codebase)
# ---------------------------------------------------------------------------


class NS:  # noqa: N801 — intentionally short namespace class
    """Pre-defined namespace constants for common cache uses."""

    # L4 — State / Semantic cache
    L4_SEMANTIC = ("L4", "semantic_cache")
    L4_VECTOR = ("L4", "vector_store")
    L4_REASONING = ("L4", "reasoning_memory")
    L4_CHECKPOINT = ("L4", "checkpoint")

    # L1 — Cognition / Assembly
    L1_ASSEMBLY = ("L1", "assembly")
    L1_THOUGHT = ("L1", "thought")

    # L3 — Orchestration
    L3_WORKFLOW = ("L3", "orchestration")
    L3_POLICY = ("L3", "policy_registry")

    # L2 — Execution / Coordination
    L2_LEASE = ("L2", "coordination")
    L2_IDEMPOTENCY = ("L2", "idempotency")

    # L_SL — System Learning / RAG
    L_SL_RAG_TOPK = ("L_SL", "rag_topk")
    L_SL_EMBEDDING = ("L_SL", "embedding")

    # L0 — Routing
    L0_ROUTING = ("L0", "routing")
    L0_CONFIG = ("L0", "config")

    # L5 — Safety
    L5_COMPLIANCE = ("L5", "compliance")

    @staticmethod
    def build(
        spec: tuple[str, str], entity_type: str, content_hash: str, *, mission_id: str = _SCOPE_GLOBAL
    ) -> str:
        """Build a key from a pre-defined NS spec tuple.

        Args:
            spec: One of the NS class tuples, e.g. NS.L4_SEMANTIC.
            entity_type: Entity type slug.
            content_hash: Hex content hash.
            mission_id: Optional mission scope.

        Returns:
            Governed Redis key.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "NS.build")

        layer, component = spec
        return build_key(layer, component, entity_type, content_hash, mission_id=mission_id)


__all__ = [
    "build_key",
    "build_mission_key",
    "build_global_key",
    "parse_key",
    "key_prefix",
    "NS",
]
