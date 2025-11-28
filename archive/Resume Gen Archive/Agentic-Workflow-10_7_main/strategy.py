"""Strategy stack agents."""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from core_v10_7 import (
    BaseAgent,
    StrategyPlan,
    ValidationError,
    track_metrics,
    _format_prompt_with_defaults,
)
from agent_stacks_v10_8.state_adapter_stack import StateAdapterStack


class QueryComplexityClassifier(BaseAgent):
    """Classifies query complexity for dynamic routing."""

    class ComplexityOutput(BaseModel):
        complexity: str
        reason: str

    @track_metrics("run_complexity_classifier")
    async def run_async(self, job_description: str, workflow_id: str) -> str:
        self.log_info("Classifying query complexity...")

        client = self.get_model_client("strategy_model_simple")

        pruned_jd = await self.budget_manager.prune(job_description, 2000)
        prompt = f"""
        {client.goal_state}
        {client.top_failures}
        -------------------
        MODE: ANALYTICAL
        TASK: Classify the job description's complexity as 'simple' or 'complex'.
        'simple' = Junior role, few requirements, common tech.
        'complex' = Senior/Executive role, many requirements, niche tech, leadership.

        Job Description:
        {pruned_jd}

        REFLECTION: What is the seniority level?
        Output JSON:
        {{"complexity": "simple/complex", "reason": "..."}}
        """

        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.strategy_model_simple.temperature,
            response_format="json_object",
        )

        validated_output, error = self.validator.validate(
            response["content"],
            self.ComplexityOutput,
        )
        if error:
            self.log_error(
                f"ComplexityClassifier failed validation: {error}. Defaulting to 'complex'."
            )
            return "complex"

        self.log_info(f"Task complexity classified as: {validated_output.complexity}")
        if self.context.policy_auto_tuner and self.context.policy_auto_tuner.enabled():
            if self.context.tuning_profile.temperature < 0.2:
                return "simple"
        if self.context.world_model_store and self.context.world_model_store.enabled():
            self.context.world_model_store.append_strategy_outcome(
                {
                    "workflow_id": workflow_id,
                    "job_title": (job_description or "")[:120],
                    "complexity": validated_output.complexity,
                }
            )
        return validated_output.complexity


class ToTStrategistAgent(BaseAgent):
    """Tree-of-Thought strategist with self-consistency voting."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        super().__init__(context, debug_mode)
        self._adapter = StateAdapterStack(context, debug_mode)

    async def _generate_branches(
        self,
        job_context: Dict[str, Any],
        client: Any,
        branching_factor: int,
    ) -> List[Dict[str, Any]]:
        prompt_template = self.prompt_manager.get_template("strategy_tot_branch")

        branch_tasks = []
        for i in range(branching_factor):
            prompt = await _format_prompt_with_defaults(
                prompt_template,
                {
                    "job_title": job_context.get("job_title", "N/A"),
                    "company": job_context.get("company", "N/A"),
                    "job_description": job_context.get("job_description", "N/A"),
                    "branch_num": i + 1,
                    "total_branches": branching_factor,
                    "style_guide": "Style: Be creative and strategically distinct.",
                },
                self.budget_manager,
                client.goal_state,
                client.top_failures,
            )
            branch_tasks.append(
                client.chat_completion_async(
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.config.model_config.strategy_model.temperature,
                    response_format="json_object",
                )
            )

        responses = await asyncio.gather(*branch_tasks, return_exceptions=True)

        branches: List[Dict[str, Any]] = []
        for i, res in enumerate(responses):
            if isinstance(res, Exception):
                self.log_warning(f"ToT Branch {i + 1} failed API call: {res}")
                continue
            validated_output, error = self.validator.validate(
                res["content"], StrategyPlan
            )
            if error:
                self.log_warning(f"ToT Branch {i + 1} failed validation: {error}")
                continue
            branches.append(
                {"branch_id": f"branch_{i}", "strategy": validated_output}
            )
        return branches

    @track_metrics("run_tot_strategy")
    async def run_async(
        self,
        job_context: Dict[str, Any],
        workflow_id: str,
        state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self.log_info("Generating ToT strategy with voting (v10.7)...")

        workflow_id = workflow_id or ""
        state_ref = state if isinstance(state, dict) else None
        if state_ref is None and isinstance(job_context, dict):
            state_ref = job_context

        autonomy = getattr(self.context, "autonomy_engine", None)
        if autonomy and autonomy.enabled():
            hints = autonomy.decide(workflow_id)
            self.log_debug(f"Autonomy hints: {hints}")
            if state_ref is not None:
                state_ref.setdefault("autonomy_hints", {}).update(hints)
        adv = getattr(self.context, "advanced_meta_learner", None)
        if adv and adv.enabled():
            hints = adv.analyze(workflow_id)
            target_state = state_ref if state_ref is not None else state
            if isinstance(target_state, dict):
                target_state.setdefault("meta_hints", {}).update(hints)

        episodic = getattr(self.context, "episodic_memory", None)
        if episodic and workflow_id:
            prior = episodic.get(workflow_id)
            self.log_debug(
                f"Episodic prior events: {len(prior.get('events', []))}"
            )

        branching_factor = self.config.agent_stacks.strategy_tot_branching_factor
        client = self.get_model_client("strategy_model")

        branches = await self._generate_branches(
            job_context, client, branching_factor
        )
        if not branches:
            raise ValidationError("All ToT strategy branches failed validation.")

        self.log_info(f"Generated {len(branches)} branches. Starting vote...")

        vote_client = self.get_model_client("strategy_model_simple")
        vote_prompt_template = self.prompt_manager.get_template("strategy_tot_vote")

        branches_json = json.dumps(
            [
                {"id": b["branch_id"], "plan": b["strategy"].model_dump()}
                for b in branches
            ]
        )

        vote_prompt = await _format_prompt_with_defaults(
            vote_prompt_template,
            {
                "num_branches": len(branches),
                "job_description": job_context.get("job_description", "N/A"),
                "branches_json": branches_json,
            },
            self.budget_manager,
            vote_client.goal_state,
            vote_client.top_failures,
        )

        vote_response = await vote_client.chat_completion_async(
            messages=[{"role": "user", "content": vote_prompt}],
            temperature=0.1,
            response_format="json_object",
        )

        class VoteOutput(BaseModel):
            best_branch_id: str
            reason: str

        validated_vote, error = self.validator.validate(
            vote_response["content"], VoteOutput
        )

        if error:
            self.log_error(
                f"Strategy vote validation failed: {error}. Defaulting to first branch."
            )
            selected_strategy = branches[0]["strategy"]
        else:
            self.log_info(
                f"Vote selected: {validated_vote.best_branch_id}. Reason: {validated_vote.reason}"
            )
            selected_strategy = next(
                (
                    b["strategy"]
                    for b in branches
                    if b["branch_id"] == validated_vote.best_branch_id
                ),
                branches[0]["strategy"],
            )

        if self.context.world_model_store and self.context.world_model_store.enabled():
            self.context.world_model_store.append_strategy_outcome(
                {
                    "workflow_id": workflow_id,
                    "strategy_name": selected_strategy.strategy_name,
                    "tone": selected_strategy.tone,
                }
            )

        self.log_feedback(
            workflow_id,
            "tot_strategy_vote",
            "success",
            {
                "branches_generated": len(branches),
                "selected": selected_strategy.strategy_name,
            },
        )

        # ======================================================
        # 🔥 CRITICAL FIX — ALWAYS RETURN DICTS, NEVER MODELS
        # ======================================================
        result = {
            "strategy_plan": selected_strategy.model_dump(),
            "tot_branches": [b["strategy"].model_dump() for b in branches],
        }
        notes = []
        if isinstance(state_ref, dict):
            notes = state_ref.get("memory", {}).get("episodic", {}).get(
                "agent_notes", []
            ) or []
        summary_note = (
            f"Strategy selected: {selected_strategy.strategy_name} (tone: {selected_strategy.tone})"
        )
        mem_patch = self._adapter.patch_memory(agent_notes=[*notes, summary_note])
        result.update(mem_patch.model_dump(exclude_none=True))
        if episodic and workflow_id:
            episodic.append(
                workflow_id,
                {
                    "stack": "strategy",
                    "event": "strategy_selected",
                    "strategy_name": selected_strategy.strategy_name,
                },
            )
        return result
