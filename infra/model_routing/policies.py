"""
Model routing policies for résumé processing workflows.

Provides intelligent model selection and budget enforcement for optimal résumé improvement performance.
"""

from typing import Optional
from l1.outreach_dataclasses import ArchetypeType
from core.models.models import ExecutionProfile, ComplexityLevel
from meta.routing import RoutingPolicy, LIGHT_MODELS, MEDIUM_MODELS, HEAVY_MODELS, DRAFTING_MODELS, QA_SAFETY_MODELS
from runtime.execution_budget_manager import ExecutionBudgetManager

from .models import ModelChoice, RoutingContext


def _infer_provider_from_model(model: str) -> str:
    """
    Infers provider from model name for résumé processing workflows.

    Ensures proper provider identification for optimal résumé improvement routing.
    """
    m = (model or "").lower()
    if "claude" in m:
        return "anthropic"
    if "gemini" in m or "google" in m:
        return "google"
    return "openai"


def choose_provider_and_model(
    ctx: RoutingContext,
    requested_model: Optional[str] = None,
) -> ModelChoice:
    """
    Selects optimal provider and model for résumé processing tasks.

    Balances cost, latency, and quality requirements for comprehensive résumé enhancement.
    """

    model = requested_model or "gpt-5.1-codex-mini"
    provider = _infer_provider_from_model(model)

    cost_tier = "medium"
    latency_ms = 800

    task = ctx.task_type
    if task in {"retrieval", "qa", "safety"}:
        cost_tier = "medium"
        latency_ms = 700
    if task in {"drafting", "deep_reasoning"}:
        cost_tier = "high"
        latency_ms = 1200
    if task in {"metadata", "classifier"}:
        cost_tier = "low"
        latency_ms = 400

    estimated_cost = {"low": 0.001, "medium": 0.002, "high": 0.004}[cost_tier]

    return ModelChoice(
        provider=provider,
        model_name=model,
        cost_tier=cost_tier,
        estimated_cost=estimated_cost,
        latency_ms=latency_ms,
    )


def enforce_budget(choice: ModelChoice, profile: Optional[ExecutionProfile]) -> ModelChoice:
    """
    Enforces cost budget constraints for résumé processing model selection.

    Ensures optimal model choice within budget limits for résumé improvement workflows.
    """

    if profile is None:
        return choice

    max_tier = (profile.metadata or {}).get("max_cost_tier")
    if not max_tier:
        return choice

    order = {"low": 0, "medium": 1, "high": 2}
    current = order.get(choice.cost_tier, 1)
    allowed = order.get(max_tier, current)

    if current <= allowed:
        return choice

    # Downgrade to allowed tier by adjusting cost/latency; we keep
    # provider/model_name untouched for compatibility.
    if allowed == order["low"]:
        cost_tier = "low"
        estimated_cost = 0.001
        latency_ms = max(200, int(choice.latency_ms * 0.6))
    else:
        cost_tier = "medium"
        estimated_cost = 0.002
        latency_ms = max(400, int(choice.latency_ms * 0.8))

    return ModelChoice(
        provider=choice.provider,
        model_name=choice.model_name,
        cost_tier=cost_tier,
        estimated_cost=estimated_cost,
        latency_ms=latency_ms,
    )


def fallback_chain(choice: ModelChoice) -> list[ModelChoice]:
    """
    Creates fallback model chain for résumé processing reliability.

    Ensures robust model selection with backup options for comprehensive résumé enhancement.
    """

    fallbacks: list[ModelChoice] = [choice]

    if choice.provider == "openai":
        fallbacks.append(
            ModelChoice(
                provider="anthropic",
                model_name=choice.model_name,
                cost_tier=choice.cost_tier,
                estimated_cost=choice.estimated_cost,
                latency_ms=choice.latency_ms + 200,
            )
        )
    elif choice.provider == "anthropic":
        fallbacks.append(
            ModelChoice(
                provider="openai",
                model_name=choice.model_name,
                cost_tier=choice.cost_tier,
                estimated_cost=choice.estimated_cost,
                latency_ms=choice.latency_ms + 200,
            )
        )

    return fallbacks


def choose_model(ctx: RoutingContext) -> ModelChoice:
    """
    Selects optimal model for résumé processing workflows.

    Provides intelligent model choice based on routing context for résumé improvement.
    """

    return choose_provider_and_model(ctx, requested_model=None)


def enforce_cost_budget(choice: ModelChoice, profile: Optional[ExecutionProfile]) -> ModelChoice:
    """
    Enforces cost budget constraints for résumé processing model selection.

    Ensures optimal model choice within budget limits for résumé improvement workflows.
    """

    return enforce_budget(choice, profile)


class ModelRoutingPolicy:
    """
    Policy-driven model routing for outreach workflows with budget awareness.
    
    Wraps the existing meta/routing.RoutingPolicy to maintain backward compatibility
    while adding budget-aware model selection for outreach workflows.
    """
    
    def __init__(self, base_policy: Optional[RoutingPolicy] = None):
        """Initialize with optional base routing policy."""
        # Configure base policy to respect complexity constraints
        self.base_policy = base_policy or RoutingPolicy(
            prefer_anthropic=False,
            prefer_openai=True,
            allow_heavy=True,  # Allow heavy but respect complexity for non-C_LEVEL
            enforce_low_cost=False
        )
    
    # Stage to task mapping for compatibility with existing RoutingPolicy
    _stage_to_task = {
        "message_generation": "drafting_narrative",
        "research": "strategy_generate_branch", 
        "safety": "safety_check",
        "qa": "qa_semantic_check",
        "planning": "strategy_generate_branch",
        "drafting": "drafting_structure",
    }
    
    # Archetype to complexity mapping
    _archetype_to_complexity = {
        ArchetypeType.C_LEVEL: ComplexityLevel.HIGH,
        ArchetypeType.EXECUTIVE: ComplexityLevel.MEDIUM,
        ArchetypeType.SENIOR_TA: ComplexityLevel.LOW,
        ArchetypeType.RECRUITER: ComplexityLevel.LOW,
    }
    
    def select_model(
        self,
        stage: str,
        archetype: ArchetypeType,
        budget_manager: ExecutionBudgetManager
    ) -> str:
        """
        Select appropriate model based on stage, archetype, and budget constraints.
        
        Args:
            stage: Workflow stage (message_generation, research, safety, etc.)
            archetype: Target archetype for model quality requirements
            budget_manager: ExecutionBudgetManager for budget-aware selection
            
        Returns:
            Selected model name string
        """
        # Get base complexity from archetype
        base_complexity = self._archetype_to_complexity.get(archetype, ComplexityLevel.MEDIUM)
        
        # Apply budget-based complexity adjustment
        adjusted_complexity = self._adjust_complexity_for_budget(
            base_complexity, stage, budget_manager
        )
        
        # Safety stages always use high complexity regardless of budget
        if stage == "safety":
            adjusted_complexity = ComplexityLevel.HIGH
        
        # Get provider from base policy (reuses provider selection logic)
        provider = self.base_policy._choose_provider(meta_profile=None)
        
        # Direct model selection based on stage and complexity
        if stage.startswith("drafting") or stage == "message_generation":
            if adjusted_complexity == ComplexityLevel.LOW:
                return LIGHT_MODELS[provider]
            elif adjusted_complexity == ComplexityLevel.MEDIUM:
                return MEDIUM_MODELS[provider]
            else:  # HIGH
                return HEAVY_MODELS[provider]
        elif stage == "safety" or stage.startswith("qa"):
            # Safety and QA always use appropriate models regardless of complexity
            if stage == "safety":
                return QA_SAFETY_MODELS[provider]
            else:  # QA
                return MEDIUM_MODELS[provider]
        elif stage == "research" or stage.startswith("strategy"):
            # Research uses complexity-based selection
            if adjusted_complexity == ComplexityLevel.LOW:
                return LIGHT_MODELS[provider]
            elif adjusted_complexity == ComplexityLevel.MEDIUM:
                return MEDIUM_MODELS[provider]
            else:  # HIGH
                return HEAVY_MODELS[provider]
        else:
            # Default to medium models for unknown stages
            return MEDIUM_MODELS[provider]
    
    def _adjust_complexity_for_budget(
        self,
        base_complexity: ComplexityLevel,
        stage: str,
        budget_manager: ExecutionBudgetManager
    ) -> ComplexityLevel:
        """
        Adjust complexity based on budget constraints.
        
        Args:
            base_complexity: Initial complexity from archetype
            stage: Current workflow stage
            budget_manager: Budget manager for usage checking
            
        Returns:
            Budget-adjusted complexity level
        """
        try:
            usage = budget_manager.current_usage()
            tokens_remaining = usage.get("tokens_remaining", 0)
            tokens_total = usage.get("tokens_remaining", 0) + usage.get("tokens_used", 0)
            
            if tokens_total == 0:
                return base_complexity
            
            remaining_percentage = tokens_remaining / tokens_total
            
            # Budget-based downgrade logic
            if remaining_percentage < 0.2:  # < 20% remaining
                # Force light models for non-critical stages
                if stage != "safety":
                    return ComplexityLevel.LOW
            elif remaining_percentage < 0.5:  # < 50% remaining
                # Downgrade one level from base
                if base_complexity == ComplexityLevel.HIGH:
                    return ComplexityLevel.MEDIUM
                elif base_complexity == ComplexityLevel.MEDIUM:
                    return ComplexityLevel.LOW
            
            return base_complexity
            
        except Exception:
            # If budget checking fails, return base complexity
            return base_complexity



