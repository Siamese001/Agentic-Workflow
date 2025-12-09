"""
Strategy planning for comprehensive résumé improvement.

Creates targeted plans to enhance résumé alignment with job requirements.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional

from config import config_profiles_v10_10 as config_profiles
from core.models.models import (
    DraftingPlan as WorkflowDraftingPlan,
    ExecutionContext,
    RAGResult,
    StrategyPlan as WorkflowStrategyPlan,
    StrategyResult,
)
from infra.reasoning.cot import expand_chain_of_thought
from infra.reasoning.react import run_react_loop
from infra.reasoning.reflexion import apply_reflexion
from infra.reasoning.tot import tree_search
from l1.builders.prompt_builder import (
    PromptInstance,
    build_drafting_prompt,
)
from l1.v6_prompt_adapter import build_v6_strategy_prompt, V6PromptConfig
from l5.injection_detection import InjectionDetector, SafetyContext
from infra.di_container import get_service
from l5.policy import SafetyEngine


@dataclass(frozen=True)
class StrategyPlan:
    """
    Defines résumé strategy planning structure.

    Ensures systematic approach to comprehensive résumé improvement.
    """

    prompt: PromptInstance


@dataclass(frozen=True)
class DraftPlan:
    """
    Structures résumé drafting planning approach.

    Guides content creation for professional résumé enhancement.
    """

    prompt: PromptInstance


@dataclass(frozen=True)
class LatentThinkingPlan:
    """
    Coordinates cognitive processing for résumé analysis.

    Optimizes reasoning strategy for effective résumé improvement.
    """

    profile_name: str
    reasoning_mode: str
    depth: int
    trace: List[str]


def plan_strategy(
    strategy_plan: WorkflowStrategyPlan,
    *,
    ctx: ExecutionContext,
    job: Any,
    resume: Any,
    config: Any,
    v6_config: Optional[V6PromptConfig] = None,
) -> StrategyPlan:
    """
    Creates comprehensive résumé improvement strategy plan.

    Generates targeted approach to enhance résumé job alignment.
    """
    
    if v6_config is None:
        v6_config = V6PromptConfig(
            include_examples=True,
            enable_cot=True,
        )
    
    # Build V6 prompt with context
    v6_prompt = build_v6_strategy_prompt(ctx, job, resume, config, v6_config)
    
    # Security validation before prompt creation
    safety_engine = get_service(SafetyEngine)
    if safety_engine:
        safety_context = SafetyContext(
            content_type="strategy_prompt",
            source="l1_strategy_planning",
            destination="l2_execution",
            content=v6_prompt,
            user_id=getattr(ctx, "user_id", "unknown"),
            session_id=getattr(ctx, "session_id", "unknown"),
            metadata={"agent": "strategy_planner", "v6_enabled": True}
        )
        policy_result = safety_engine.evaluate(safety_context)
        if policy_result.blocking_findings:
            # Log security violations but continue with fallback
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Security violations in strategy prompt: {[f.message for f in policy_result.blocking_findings]}")
    
    # Create prompt instance with V6 content
    prompt = PromptInstance(
        id="system.strategy.v6",
        content=v6_prompt,
        layer="L1",
        agent="strategy",
        model_tier="balanced",
        metadata={"v6_prompt": True, "security_validated": safety_engine is not None}
    )
    
    return StrategyPlan(prompt=prompt)


def plan_draft(
    drafting_plan: WorkflowDraftingPlan,
    *,
    ctx: ExecutionContext,
    strategy_result: StrategyResult,
    rag_result: RAGResult,
    job: Any,
    resume: Any,
    config: Any,
) -> DraftPlan:
    """
    Creates comprehensive résumé drafting plan.

    Structures approach for generating professional résumé content aligned with job requirements.
    """
    prompt = build_drafting_prompt(
        plan=drafting_plan,
        ctx=ctx,
        strategy=strategy_result,
        rag=rag_result,
        job=job,
        resume=resume,
        layer="L2",
        agent="drafting",
        model_tier="balanced",
    )
    return DraftPlan(prompt=prompt)


def generate_latent_thinking_plan(
    result: Any,
    ctx: ExecutionContext,
) -> LatentThinkingPlan:
    """
    Generates cognitive processing plan for résumé analysis.

    Optimizes reasoning strategy to enhance résumé improvement quality.
    """
    profile_name = getattr(ctx, "profile_name", None) or getattr(ctx.config, "profile_id", "default")
    reasoning_mode = "cot"
    depth = 1

    try:
        spec = config_profiles.get_profile(profile_name)
        reasoning_mode = str(getattr(spec, "reasoning_mode", "cot") or "cot")
        depth = int(getattr(spec, "drafting_depth", 1) or 1)
    except Exception:
        reasoning_mode = "cot"
        depth = 1

    sections: List[Any] = []
    try:
        drafting_result = getattr(result, "drafting", None)
        sections = list(getattr(drafting_result, "sections", []) or [])
    except Exception:
        sections = []

    trace: List[str] = []
    if sections:
        seed_text = (getattr(sections[0], "body", None) or "").strip()
        if seed_text:
            try:
                mode = reasoning_mode.lower()
                if "tot" in mode:
                    path, _ = tree_search(seed_text, max_depth=2, branching=max(1, depth))
                    trace = [node.content for node in path]
                elif "react" in mode:
                    steps = run_react_loop(seed_text, max_steps=max(1, depth))
                    trace = [step.thought for step in steps]
                elif "reflex" in mode:
                    trace = apply_reflexion(seed_text)
                else:
                    trace = expand_chain_of_thought(seed_text, steps=max(1, depth))
            except Exception:
                trace = []

    return LatentThinkingPlan(
        profile_name=profile_name,
        reasoning_mode=reasoning_mode,
        depth=depth,
        trace=trace,
    )





