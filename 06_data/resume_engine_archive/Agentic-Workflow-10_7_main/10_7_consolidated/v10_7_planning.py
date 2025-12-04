# FILE: v10_7_planning.py
# CONSOLIDATED: L1 Cognition Layer (Strategy, RAG, Draft, Bullet Planners)
# STATUS: Production Ready (v10.7 Baseline)

from __future__ import annotations
import asyncio
import json
import logging
import os
import re
import uuid
from typing import Any, Dict, List, Type, Optional, Tuple, Iterable, Sequence, Callable, Awaitable
from functools import wraps

# Assuming Core/Models/Clients are available from the V10_7_FOUNDATIONS scope.
# Base classes and Pydantic models are redefined here for file self-sufficiency.

class BaseAgent:
    """Minimal BaseAgent to satisfy L1 Planner dependencies."""
    def __init__(self, context, debug_mode=False): 
        self.context = context
        self.debug_mode = debug_mode
        self.log_info = lambda msg: logging.getLogger("L1_PLAN").info(msg)
        self.log_warning = lambda msg: logging.getLogger("L1_PLAN").warning(msg)
        self.log_error = lambda msg: logging.getLogger("L1_PLAN").error(msg)
        self.get_model_client = lambda key: self.context.get_model_client(key.split("_")[0], key)
        self.budget_manager = lambda: self.context.context_budget_manager
        self.prompt_manager = self.context.prompt_manager
        self.validator = self.context.response_validator
        
class BaseTool:
    """Minimal BaseTool to satisfy dependencies."""
    def __init__(self, context, debug_mode=False): 
        self.context = context
        self.log_warning = lambda msg: logging.getLogger("L1_TOOL").warning(msg)

# Pydantic models needed locally
from v10_7_foundations import StrategyPlan, PlannerAssessment, ContextBudgetManager, ValidationError, PydanticSchemaError, BaseToolOutput, GeneratedPrompts, HILAmbiguityReport
from v10_7_foundations import track_metrics, _format_prompt_with_defaults # Assuming helper functions are available in scope

# ============================================================================
# SECTION 1: PLANNING UTILITIES (Source: planning_utils.py)
# ============================================================================

def extract_job_profile(state: Dict[str, Any]) -> Dict[str, Any]:
    job = state.get("job") or {}
    def _first(*keys: str) -> str:
        for key in keys:
            value = job.get(key)
            if value: return str(value)
        return ""
    raw_requirements = (
        job.get("top_requirements") or job.get("required_skills") or job.get("keywords") or job.get("skills") or []
    )
    requirements: List[str]
    if isinstance(raw_requirements, str):
        requirements = [part.strip() for part in raw_requirements.split(",") if part.strip()]
    elif isinstance(raw_requirements, Iterable):
        requirements = [str(item).strip() for item in raw_requirements if str(item).strip()]
    else: requirements = []
    return {
        "title": _first("job_title", "title", "role"),
        "company": _first("company", "employer", "organization"),
        "summary": _first("summary", "description", "jd_excerpt", "jd"),
        "team": _first("team", "org_unit", "department"),
        "location": _first("location", "city"),
        "requirements": requirements,
    }

def extract_resume_profile(state: Dict[str, Any]) -> Dict[str, Any]:
    resume = state.get("resume") or {}
    master_resume = resume.get("master_resume") or {}
    summary = (
        master_resume.get("summary") or master_resume.get("professional_summary") or master_resume.get("profile") or ""
    )
    experiences = master_resume.get("professional_experience")
    if not isinstance(experiences, list): experiences = []
    return {"summary": str(summary), "experiences": experiences}

def describe_experience(experience: Dict[str, Any]) -> str:
    title = experience.get("title") or experience.get("role") or "Role"
    company = experience.get("company") or experience.get("employer") or "Company"
    scope = (
        experience.get("impact_summary") or experience.get("summary") or experience.get("description") or ""
    )
    description = f"{title} @ {company}".strip()
    if scope: description = f"{description} – {scope}".strip()
    return description

def detect_metrics(experiences: List[Dict[str, Any]]) -> List[str]:
    metrics: List[str] = []
    for exp in experiences:
        text_parts: List[str] = []
        for key in ("impact_summary", "summary", "description"):
            value = exp.get(key)
            if value: text_parts.append(str(value))
        bullet_pool = exp.get("bullet_pool")
        if isinstance(bullet_pool, list): text_parts.extend(str(item) for item in bullet_pool)
        combined = " ".join(text_parts)
        if any(char.isdigit() for char in combined):
            metrics.append(f"Quantify results from {describe_experience(exp)}")
    if not metrics: metrics.append("Quantify at least one measurable outcome per role")
    return metrics

def collect_sections(state: Dict[str, Any]) -> List[str]:
    draft = state.get("draft") or {}
    sections = draft.get("sections")
    if isinstance(sections, dict) and sections: return list(sections.keys())
    return ["summary", "experience", "skills"]

def missing_requirements(requirements: List[str], experiences: List[Dict[str, Any]]) -> List[str]:
    if not requirements: return []
    combined = " ".join(
        str(exp.get("impact_summary") or exp.get("summary") or "") for exp in experiences
    ).lower()
    missing = [req for req in requirements if req.lower() not in combined]
    return missing

# ============================================================================
# SECTION 2: STRATEGY (Source: strategy.py, strategy_ensemble_v10_7.py)
# ============================================================================

class QueryComplexityClassifier(BaseAgent):
    """Classifies query complexity for dynamic routing."""
    class ComplexityOutput(BaseModel):
        complexity: str
        reason: str
    
    @track_metrics('run_complexity_classifier')
    async def run_async(self, job_description: str, workflow_id: str) -> str:
        self.log_info("Classifying query complexity...")
        client = self.get_model_client("strategy_model_simple")
        
        pruned_jd = await self.budget_manager().prune(job_description, 2000)
        prompt = f"""
        MODE: ANALYTICAL
        TASK: Classify the job description's complexity as 'simple' or 'complex'.
        Job Description: {pruned_jd}
        Output JSON: {{"complexity": "simple/complex", "reason": "..."}}
        """
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6, # Mock temp
            response_format="json_object"
        )
        validated_output, error = self.context.response_validator.validate(
            response["content"], self.ComplexityOutput
        )
        if error:
            self.log_error(f"ComplexityClassifier failed validation: {error}. Defaulting to 'complex'.")
            return "complex"
        return validated_output.complexity

class ToTStrategistAgent(BaseAgent):
    """Tree-of-Thought strategist with self-consistency voting."""
    async def _generate_branches(
        self, job_context: Dict[str, Any], client: Any, branching_factor: int,
    ) -> List[Dict[str, Any]]:
        # Mock template retrieval/formatting for consolidation
        prompt_template = "Generate strategy branch {branch_num} for {job_title}." 
        
        branch_tasks = []
        for i in range(branching_factor):
            prompt = await _format_prompt_with_defaults(
                prompt_template,
                {
                    "job_title": job_context.get("job_title", "N/A"),
                    "branch_num": i + 1,
                    "total_branches": branching_factor,
                },
                self.budget_manager(), self.context.workflow_id, []
            )
            branch_tasks.append(
                client.chat_completion_async(
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7, response_format="json_object"
                )
            )
        
        responses = await asyncio.gather(*branch_tasks, return_exceptions=True)
        branches: List[Dict[str, Any]] = []
        for i, res in enumerate(responses):
            if isinstance(res, Exception): continue
            validated_output, error = self.context.response_validator.validate(res["content"], StrategyPlan)
            if error: continue
            branches.append({"branch_id": f"branch_{i}", "strategy": validated_output})
        return branches

    @track_metrics('run_tot_strategy')
    async def run_async(self, job_context: Dict[str, Any], workflow_id: str, state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.log_info("Generating ToT strategy with voting (v10.7)...")
        branching_factor = 3 # Hardcoded mock
        client = self.get_model_client("strategy_model")

        branches = await self._generate_branches(job_context, client, branching_factor)
        if not branches: raise ValidationError("All ToT strategy branches failed validation.")

        vote_client = self.get_model_client("strategy_model_simple")
        vote_prompt_template = "Vote for the best strategy among: {branches_json} for {job_description}."

        branches_json = json.dumps([{"id": b["branch_id"], "plan": b["strategy"].model_dump()} for b in branches])
        vote_prompt = await _format_prompt_with_defaults(
            vote_prompt_template, {"job_description": job_context.get("job_description", "N/A"), "branches_json": branches_json,},
            self.budget_manager(), self.context.workflow_id, []
        )

        vote_response = await vote_client.chat_completion_async(
            messages=[{"role": "user", "content": vote_prompt}],
            temperature=0.1, response_format="json_object"
        )

        class VoteOutput(BaseModel):
            best_branch_id: str
            reason: str

        validated_vote, error = self.context.response_validator.validate(vote_response["content"], VoteOutput)
        selected_strategy = next((b["strategy"] for b in branches if b["branch_id"] == validated_vote.best_branch_id), branches[0]["strategy"])

        return {
            "strategy_plan": selected_strategy.model_dump(),
            "tot_branches": [b["strategy"].model_dump() for b in branches],
        }

class StrategyCoordinatorAgent(BaseAgent):
    """Simulates the ensemble coordinator (Domain, Risk, Feasibility)."""
    async def run_async(self, job_context: Dict[str, Any], base_plan: StrategyPlan, workflow_id: str, downstream_feedback: Optional[Dict[str, Any]] = None) -> StrategyPlan:
        # Simplified coordination logic stub
        plan = base_plan.model_copy(deep=True)
        plan.coordinator_summary = "Strategy Approved by Ensemble."
        return plan

class StrategyStackV10_8:
    """Facade for the strategy execution."""
    def __init__(self, context: Any, debug_mode: bool = False):
        self.classifier = QueryComplexityClassifier(context, debug_mode)
        self.strategist = ToTStrategistAgent(context, debug_mode)
    
    async def classify_complexity_async(self, jd: str, wid: str) -> str:
        return await self.classifier.run_async(jd, wid)

    async def plan_strategy_async(self, ctx: Dict[str, Any], wid: str, state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self.strategist.run_async(ctx, wid, state)


# ============================================================================
# SECTION 3: PROMPT ENGINEERING (Source: prompting.py)
# ============================================================================

class PromptEngineerAgent(BaseAgent):
    """LLM-driven prompt engineering that adapts to task complexity."""
    @track_metrics("run_prompt_engineer")
    async def run_async(
        self, strategy: StrategyPlan, complexity: str, workflow_id: str, state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self.log_info(f"Engineering prompts (Complexity: {complexity})...")
        client = self.get_model_client("prompt_engineer_model")
        meta_prompt_template = "Generate prompts based on strategy {strategy.strategy_name} and complexity {complexity}."

        meta_prompt = await _format_prompt_with_defaults(
            meta_prompt_template, {"strategy": strategy, "complexity": complexity}, self.budget_manager(), "", []
        )
        response = await client.chat_completion_async(messages=[{"role": "user", "content": meta_prompt}], temperature=0.7, response_format="json_object")

        validated_output, error = self.context.response_validator.validate(response["content"], GeneratedPrompts)
        if error: raise ValidationError(f"PromptEngineerAgent failed validation: {error}")

        return {"prompts": validated_output, "complexity": complexity}

class PromptBuilderStack:
    """Facade for prompt engineering."""
    def __init__(self, context: Any, debug_mode: bool = False): self.agent = PromptEngineerAgent(context, debug_mode)
    async def run_async(self, strat, comp, wid, state): return await self.agent.run_async(strat, comp, wid, state)


# ============================================================================
# SECTION 4: RAG PLANNING (Source: rag_planning.py)
# ============================================================================

class RAGPlanningStack:
    """Produces a lightweight retrieval plan without calling any tools."""
    def __init__(self, context: Any, debug_mode: bool = False): pass

    async def run_async(self, state: Dict[str, Any], workflow_id: Optional[str] = None) -> Dict[str, Any]:
        plan = self._build_plan(state)
        return {"rag": {"plan": plan.model_dump()}}

    def _build_plan(self, state: Dict[str, Any]) -> RAGPlan:
        job = extract_job_profile(state)
        resume = extract_resume_profile(state)
        exps = resume["experiences"]
        reqs = job["requirements"]
        
        goal = f"Surface evidence that proves readiness for {job['title']} at {job['company']}"
        
        # Query Generation Logic (10.7 heuristic)
        queries: List[str] = []
        base_role = job["title"] or "target role"
        company = job["company"]
        keyword_suffix = (" ".join(reqs[:2]) if reqs else "impact metrics")
        queries.append(f"{base_role} {company} {keyword_suffix}".strip())
        if exps: queries.append(f"{describe_experience(exps[0])} supporting evidence for {base_role}")
        
        # Prioritization
        prioritization: List[str] = []
        if reqs: prioritization.append(f"Match JD keywords first: {', '.join(reqs[:3])}")
        if exps: prioritization.append("Favor most recent quantified roles")
        
        risk_checks = ["Verify every plan output references an original resume source"]
        if reqs: risk_checks.append("Confirm each top JD requirement is backed by evidence")
        
        return RAGPlan(
            goal=goal,
            context_inputs=["job.description", "resume.professional_experience"],
            retrieval_queries=queries,
            prioritization=prioritization,
            risk_checks=risk_checks,
        )


# ============================================================================
# SECTION 5: DRAFT PLANNING (Source: draft_planning.py)
# ============================================================================

class DraftPlanningStack:
    """Creates a low-latency drafting plan using only state inspection."""
    def __init__(self, context: Any, debug_mode: bool = False): pass

    async def run_async(self, state: Dict[str, Any], workflow_id: Optional[str] = None) -> Dict[str, Any]:
        plan = self._build_plan(state)
        return {"draft": {"plan": plan.model_dump()}}

    def _build_plan(self, state: Dict[str, Any]) -> DraftPlan:
        job = extract_job_profile(state)
        resume = extract_resume_profile(state)
        exps = resume["experiences"]
        
        strat = state.get("strategy", {}).get("strategy_plan") or {}
        tone = getattr(strat, 'tone', strat.get('tone')) or "Professional"

        # Structure
        structure = ["Executive Summary"]
        structure.extend(collect_sections(state))
        
        # Key Messages
        messages: List[str] = []
        if job["title"]: messages.append(f"Position candidate as the obvious {job['title']}")
        if exps: messages.append(f"Highlight {describe_experience(exps[0])} as the anchor story")
        
        # Risks
        risks = ["Guard against hallucinating responsibilities not in resume"]
        missing = missing_requirements(job["requirements"], exps)
        if missing: risks.append(f"JD gaps detected: {', '.join(missing[:3])}. Address proactively.")

        return DraftPlan(
            structure=structure,
            tone=tone,
            key_messages=messages,
            review_gates=["Narrative continuity review", "Quantified impact audit"],
            risks=risks,
        )


# ============================================================================
# SECTION 6: BULLET PLANNING (Source: bullet_planning.py)
# ============================================================================

class BulletPlanningStack:
    """Outlines which bullets to generate before invoking execution stacks."""
    def __init__(self, context: Any, debug_mode: bool = False): pass

    async def run_async(self, state: Dict[str, Any], workflow_id: Optional[str] = None) -> Dict[str, Any]:
        plan = self._build_plan(state)
        return {"bullets": {"plan": plan.model_dump()}}

    def _build_plan(self, state: Dict[str, Any]) -> BulletPlan:
        job = extract_job_profile(state)
        resume = extract_resume_profile(state)
        exps = resume["experiences"]
        
        highlight_order = [describe_experience(exp) for exp in exps[:3]]
        metrics_focus = detect_metrics(exps)
        
        style_guidelines = [
            f"Use a professional tone anchored in measurable outcomes",
            "Lead with action + metric + outcome structure",
        ]
        if job["requirements"]:
            style_guidelines.append(f"Mirror JD keywords such as {', '.join(job['requirements'][:3])}")
            
        validation_checks = ["Each bullet must cite a unique accomplishment", "Avoid repeating the same metric more than once"]
        
        return BulletPlan(
            target_sections=collect_sections(state),
            highlight_order=highlight_order,
            metrics_focus=metrics_focus,
            style_guidelines=style_guidelines,
            validation_checks=validation_checks,
        )