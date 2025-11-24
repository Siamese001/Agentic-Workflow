"""Strategy planning module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List

import config_profiles_v10_10 as config_profiles
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
from prompt_builder import (
    PromptInstance,
    build_drafting_prompt,
    build_strategy_prompt,
)


@dataclass(frozen=True)
class StrategyPlan:
    """Pure planning artifact for the strategy agent."""

    prompt: PromptInstance


@dataclass(frozen=True)
class DraftPlan:
    """Pure planning artifact for the drafting agent."""

    prompt: PromptInstance


@dataclass(frozen=True)
class LatentThinkingPlan:
    """Latent thinking instructions derived from profile + draft text."""

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
) -> StrategyPlan:
    prompt = build_strategy_prompt(
        plan=strategy_plan,
        ctx=ctx,
        job=job,
        resume=resume,
        config=config,
        prompt_id="system.strategy",
        layer="L2",
        agent="strategy",
        model_tier="balanced",
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

