"""
L4 State Caching Module

Provides Redis-backed cache implementations for L4 persistence layer.
All Redis connectivity uses the canonical client from agentic_core.cache
(get_hot_cache / get_coordination_cache) — NOT direct connections.

Note: redis_mcp_client is tombstoned — do not import from it.
"""

from agentic_core.L4_state.cache.cache_key_builders import (
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
from agentic_core.L4_state.cache.config_file_cache import (
    ConfigFileCache,
    get_config_file_cache,
)
from agentic_core.L4_state.cache.discovery_cache import (
    AgentDiscoveryCache,
    get_agent_discovery_cache,
)
from agentic_core.L4_state.cache.gptcache_client import (
    NativePersistentCacheClient,
    get_global_l2_cache,
)
from agentic_core.L4_state.cache.policy_registry_cache import (
    PolicyRegistryCache,
    get_policy_registry_cache,
)
from agentic_core.L4_state.cache.schema_validator_cache import (
    SchemaValidatorCache,
    get_schema_validator_cache,
)
from agentic_core.L4_state.cache.tool_embedding_cache import (
    ToolEmbeddingCache,
    get_tool_embedding_cache,
)

# RH2B.1: dual-read replay-key migration scaffolding (imports by consumers that
# compute prompt-replay cache keys — current consumers are tests + golden
# harness; production callers wire in via the follow-on plan
# prompt-reception-followups-a7b3c4).
from agentic_core.L4_state.cache.replay_key import (
    LEGACY_FLAT_PREFIX,
    SLOT_DIGEST_PREFIX,
    SLOT_DIGEST_SCHEME_VERSION,
    compute_slot_digest_key,
)

__all__ = [
    # Key builders
    "build_cap_registry_key",
    "build_compiled_prompt_key",
    "build_lease_key",
    "build_orch_plan_key",
    "build_rag_topk_key",
    "build_route_decision_key",
    "build_routing_rule_surface_key",
    "build_safety_eval_key",
    "build_template_render_key",
    "build_tool_result_key",
    # Cache clients
    "ConfigFileCache",
    "get_config_file_cache",
    "AgentDiscoveryCache",
    "get_agent_discovery_cache",
    "NativePersistentCacheClient",
    "get_global_l2_cache",
    "PolicyRegistryCache",
    "get_policy_registry_cache",
    "SchemaValidatorCache",
    "get_schema_validator_cache",
    "ToolEmbeddingCache",
    "get_tool_embedding_cache",
    # RH2B.1 replay-key migration
    "LEGACY_FLAT_PREFIX",
    "SLOT_DIGEST_PREFIX",
    "SLOT_DIGEST_SCHEME_VERSION",
    "compute_slot_digest_key",
]
