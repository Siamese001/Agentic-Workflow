"""Unified WorkflowContext for v10_9_clean.

Preserves 10_7 functionality (services, validators, correction manager, caching,
policy tuning, arbitration) while aligning to the 10_8+ architecture and the
new unified ContextBudgetManager defined in services.py.
"""

from __future__ import annotations

from typing import Any, Optional

from .clients import build_client
from .config import Config, load_config
from .constants import CANONICAL_MODEL_DEFAULT, LEGACY_MODEL_ALIASES
from .exceptions import RuntimeConfigurationError
from .models import canonical_model_name
from .services import (
    ArbitrationEngine,
    CacheManager,
    ContextBudgetManager,
    CostTracker,
    MetricsCollector,
    PolicyAutoTuner,
    PredictiveCacheManager,
    PrecomputeEngine,
    PromptTemplateManager,
    ResponseValidator,
    SelfCorrectionManager,
)


class WorkflowContext:
    """Aggregates all runtime services available to orchestration and execution."""

    def __init__(self, config: Optional[Config] = None, **overrides: Any) -> None:
        # v10_9_clean config loader
        self.config: Config = config or load_config()
        if not hasattr(self.config, "schema_version"):
            raise RuntimeConfigurationError("Invalid Config object for WorkflowContext")

        # -------------------------------
        # Core v10_7-style runtime services
        # -------------------------------

        self.cache_manager: CacheManager = overrides.get(
            "cache_manager", CacheManager()
        )
        self.cost_tracker: CostTracker = overrides.get(
            "cost_tracker", CostTracker()
        )

        self.prompt_manager: PromptTemplateManager = overrides.get(
            "prompt_manager", PromptTemplateManager()
        )
        self.response_validator: ResponseValidator = overrides.get(
            "response_validator", ResponseValidator()
        )
        self.metrics_collector: MetricsCollector = overrides.get(
            "metrics_collector", MetricsCollector()
        )
        self.self_correction_manager: SelfCorrectionManager = overrides.get(
            "self_correction_manager",
            SelfCorrectionManager(self.response_validator),
        )
        self.policy_auto_tuner: PolicyAutoTuner = overrides.get(
            "policy_auto_tuner", PolicyAutoTuner()
        )

        # -------------------------------
        # Predictive caching (10_7 surface, 10_8 architecture)
        # -------------------------------

        self.predictive_cache_manager: PredictiveCacheManager = overrides.get(
            "predictive_cache_manager", PredictiveCacheManager()
        )

        # -------------------------------
        # Precompute engine
        # -------------------------------

        self.precompute_engine: PrecomputeEngine = overrides.get(
            "precompute_engine", PrecomputeEngine()
        )
        self.precompute_engine.context = self

        # -------------------------------
        # World model /
        # semantic validator (optional)
        # -------------------------------

        self.world_model_store: Any = overrides.get("world_model_store")
        self.semantic_validator: Any = overrides.get("semantic_validator")

        # -------------------------------
        # Context budgeting (unified 10_7 + 10_8 + 10_9 semantics)
        # -------------------------------

        # Delegated legacy budgeting (10_7 style hard token budget)
        legacy_max_tokens = (
            getattr(self.config, "max_tokens", None)
            or getattr(getattr(self.config, "budget", {}), "get", lambda *_: None)(
                "max_tokens", None
            )
            or 32000
        )

        self.legacy_context_budget_manager: ContextBudgetManager = overrides.get(
            "legacy_context_budget_manager",
            ContextBudgetManager(max_tokens=legacy_max_tokens),
        )

        # Full unified manager (soft budgets + message/RAG/summary pruning)
        self.context_budget_manager: ContextBudgetManager = overrides.get(
            "context_budget_manager",
            ContextBudgetManager(
                max_tokens=legacy_max_tokens,
                budget_config=getattr(self.config, "budget", None),
                soft_config=None,
                delegate=self.legacy_context_budget_manager,
            ),
        )

        # -------------------------------
        # Arbitration engine
        # -------------------------------

        self.arbitration_engine: ArbitrationEngine = overrides.get(
            "arbitration_engine", ArbitrationEngine()
        )

        # -------------------------------
        # Feedback & rules loaders (optional)
        # -------------------------------

        self.feedback_reader: Any = overrides.get("feedback_reader")
        self.rules_loader: Any = overrides.get("rules_loader")

        # Dynamic workflow id for tracking
        self.workflow_id: Optional[str] = overrides.get("workflow_id")

    # ---------------------------------------------------------------------
    # Model client resolution
    # ---------------------------------------------------------------------

    def get_model_client(self, model_name: Optional[str] = None):
        """Resolve and instantiate an async client for the requested model."""
        resolved = canonical_model_name(
            model_name or self.config.default_model or CANONICAL_MODEL_DEFAULT,
            {**LEGACY_MODEL_ALIASES, **self.config.canonical_alias_map()},
        )
        return build_client(resolved)
