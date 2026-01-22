"""Strategy stack agents."""

import asyncio
import json

    BaseAgent,
    StrategyPlan,
    ValidationError,
    _format_prompt_with_defaults,
    track_metrics,
)


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
        return validated_output.complexity


class ToTStrategistAgent(BaseAgent):
    """Tree-of-Thought strategist with self-consistency voting."""

    async def _generate_branches(
        self,
        job_context: dict[str, Any],
        client: Any,
        branching_factor: int,
    ) -> list[dict[str, Any]]:
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

        branches: list[dict[str, Any]] = []
        for i, res in enumerate(responses):
            if isinstance(res, Exception):
                self.log_warning(f"ToT Branch {i + 1} failed API call: {res}")
                continue
            validated_output, error = self.validator.validate(res["content"], StrategyPlan)
            if error:
                self.log_warning(f"ToT Branch {i + 1} failed validation: {error}")
                continue
            branches.append({"branch_id": f"branch_{i}", "strategy": validated_output})
        return branches

    @track_metrics("run_tot_strategy")
    async def run_async(self, job_context: dict[str, Any], workflow_id: str) -> dict[str, Any]:
        self.log_info("Generating ToT strategy with voting (v10.7)...")

        branching_factor = self.config.agent_stacks.strategy_tot_branching_factor
        client = self.get_model_client("strategy_model")

        branches = await self._generate_branches(job_context, client, branching_factor)
        if not branches:
            raise ValidationError("All ToT strategy branches failed validation.")

        self.log_info(f"Generated {len(branches)} branches. Starting vote...")
        vote_client = self.get_model_client("strategy_model_simple")
        vote_prompt_template = self.prompt_manager.get_template("strategy_tot_vote")

        branches_json = json.dumps(
            [{"id": b["branch_id"], "plan": b["strategy"].model_dump()} for b in branches]
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
            vote_response["content"],
            VoteOutput,
        )

        if error:
            self.log_error(f"Strategy vote validation failed: {error}. Defaulting to first branch.")
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

        self.log_feedback(
            workflow_id,
            "tot_strategy_vote",
            "success",
            {
                "branches_generated": len(branches),
                "selected": selected_strategy.strategy_name,
            },
        )

        return {
            "strategy_plan": selected_strategy,
            "tot_branches": [b["strategy"].model_dump() for b in branches],
        }
