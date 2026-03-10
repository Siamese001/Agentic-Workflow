"""Deterministic, non-authoritative Redis cache infrastructure.

This package provides a strictly non-authoritative, version-keyed Redis cache
for L0, L1 (Assembly), L2, L3, and L5 seams.

L4 remains the only source of truth.  Redis stores memoised derivatives only.
"""

from agentic_core.cache.cache_key_builders import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    build_cap_registry_key,
    build_compiled_prompt_key,
    build_lease_key,
    build_orch_plan_key,
    build_rag_topk_key,
    build_route_decision_key,
    build_routing_rule_surface_key,
    build_safety_eval_key,
    build_template_render_key,
    build_tool_result_key,
)
from agentic_core.cache.redis_cache_client import (
    CacheDB,
    DeterministicRedisCache,
    canonical_json_bytes,
    content_hash,
    get_coordination_cache,
    get_hot_cache,
    reset_cache_singletons,
)

__all__ = [
    "DeterministicRedisCache",
    "CacheDB",
    "canonical_json_bytes",
    "content_hash",
    "get_hot_cache",
    "get_coordination_cache",
    "reset_cache_singletons",
    "build_route_decision_key",
    "build_routing_rule_surface_key",
    "build_cap_registry_key",
    "build_compiled_prompt_key",
    "build_template_render_key",
    "build_safety_eval_key",
    "build_orch_plan_key",
    "build_lease_key",
    "build_tool_result_key",
    "build_rag_topk_key",
]
