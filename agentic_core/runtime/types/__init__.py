"""Runtime Domain - Type definitions and domain entities."""

__all__ = [
    "CacheEntry",
    "CacheMiss",
    "SemanticCacheHit",
    "create_semantic_cache",
    "semantic_cache",
    "Claim",
    "ClaimAnalysisResult",
    "ClaimConfidenceScorer",
    "ClaimType",
    "ConfidenceLevel",
    "create_claim_scorer",
    "BudgetExceededError",
    "CostGovernor",
    "CostGovernorManager",
    "UsageRecord",
    "get_global_cost_governor",
    "track_api_call",
    "ExpansionStrategy",
    "HyDeDocument",
    "HyDeProcessor",
    "HyDeResult",
]


def __getattr__(name: str):
    if name in ("CacheEntry", "CacheMiss", "SemanticCacheHit", "create_semantic_cache", "semantic_cache"):
        from .cache_entry_types import CacheEntry, CacheMiss, SemanticCacheHit, create_semantic_cache, semantic_cache
        return locals()[name]
    if name in ("Claim", "ClaimAnalysisResult", "ClaimConfidenceScorer", "ClaimType", "ConfidenceLevel", "create_claim_scorer"):
        from .claim_type_types import Claim, ClaimAnalysisResult, ClaimConfidenceScorer, ClaimType, ConfidenceLevel, create_claim_scorer
        return locals()[name]
    if name in ("BudgetExceededError", "CostGovernor", "CostGovernorManager", "UsageRecord", "get_global_cost_governor", "track_api_call"):
        from .cost_governor_types import BudgetExceededError, CostGovernor, CostGovernorManager, UsageRecord, get_global_cost_governor, track_api_call
        return locals()[name]
    if name in ("ExpansionStrategy", "HyDeDocument", "HyDeProcessor", "HyDeResult"):
        from .expansion_strategy_types import ExpansionStrategy, HyDeDocument, HyDeProcessor, HyDeResult
        return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
