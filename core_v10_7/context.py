"""Workflow context wiring for v10_7 runtime."""
from __future__ import annotations

from typing import Any, Dict, Optional

from context_budget_v10_8 import ContextBudgetConfigV10_8, ContextBudgetManagerV10_8

from .clients import build_client
from .config import ConfigV10_7, load_config
from .constants import CANONICAL_MODEL_DEFAULT, LEGACY_MODEL_ALIASES
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
from .exceptions import RuntimeConfigurationError


class WorkflowContext:
    """Aggregate runtime services available to orchestration layers."""

    def __init__(self, config: Optional[ConfigV10_7] = None, **overrides: Any):
        self.config = config or load_config()
        if self.config.schema_version != "master_config_v10.7":
            raise RuntimeConfigurationError("WorkflowContext requires ConfigV10_7")

        self.cache_manager: CacheManager = overrides.get("cache_manager", CacheManager())
        self.cost_tracker: CostTracker = overrides.get("cost_tracker", CostTracker())
        self.feedback_reader: Any = overrides.get("feedback_reader")
        self.rules_loader: Any = overrides.get("rules_loader")
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
            "self_correction_manager", SelfCorrectionManager(self.response_validator)
        )
        self.policy_auto_tuner: PolicyAutoTuner = overrides.get(
            "policy_auto_tuner", PolicyAutoTuner()
        )
        self.world_model_store: Any = overrides.get("world_model_store")
        self.semantic_validator: Any = overrides.get("semantic_validator")
        self.predictive_cache_manager: PredictiveCacheManager = overrides.get(
            "predictive_cache_manager", PredictiveCacheManager()
        )
        self.precompute_engine: PrecomputeEngine = overrides.get(
            "precompute_engine", PrecomputeEngine()
        )

        self.legacy_context_budget_manager: ContextBudgetManager = overrides.get(
            "legacy_context_budget_manager", self._build_legacy_budget_manager()
        )
        self.context_budget_manager: ContextBudgetManagerV10_8 = overrides.get(
            "context_budget_manager",
            ContextBudgetManagerV10_8(
                ContextBudgetConfigV10_8(),
                delegate=self.legacy_context_budget_manager,
            ),
        )

        self.precompute_engine.context = self

    def _build_legacy_budget_manager(self) -> ContextBudgetManager:
        try:
            return ContextBudgetManager(
                config=self.config,
                model_client_getter=self.get_model_client,
                self_correction_manager=self.self_correction_manager,
                workflow_id_getter=lambda: getattr(self, "workflow_id", None),
            )
        except TypeError:
            return ContextBudgetManager(self.config.budget.get("max_tokens", 32000))

    def get_model_client(self, model_name: Optional[str] = None):
        """Resolve and instantiate an async client for the requested model."""

        resolved = canonical_model_name(
            model_name or self.config.default_model or CANONICAL_MODEL_DEFAULT,
            {**LEGACY_MODEL_ALIASES, **self.config.canonical_alias_map()},
        )
        return build_client(resolved)
