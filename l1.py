# FILE: l1.py
"""
Unified L1 Cognition Layer (v10_9, fully agentic — ENTERPRISE REFACTOR)

This module implements ALL L1 responsibilities needed to support a
v10_9 agentic workflow with feature parity to the legacy 10_7 / 10_8
design, but WITHOUT any execution, orchestration, state mutation, or
safety decisions.

L1 is *pure cognition*:

    • No execution (no LLM calls, no tools)
    • No orchestration (no DAGs, no retries)
    • No state mutation (no DB / no I/O)
    • No safety enforcement (only *planning* for safety / QA)

It produces *PlanObject* instances that describe *what* should happen
at L2–L5:

    • StrategyReasoner          – multi-branch strategy / ToT planning
    • RAGReasoner               – retrieval planning (HYDE-aware)
    • DraftingReasoner          – drafting structure, tone, risks
    • QACoordinatorPlanner      – QA validation plan (multi-check)
    • SafetyPlanner             – safety / constitutional plan
    • PromptEngineeringPlanner  – prompt engineering / template planning
    • HILPlanner                – human-in-the-loop escalation planning
    • MetaLearningPlanner       – meta-learning orchestration planning
    • Mode routing              – route_mode / route_plan
    • Shared utilities          – job/resume extraction, metrics detection

The actual execution of these plans is the responsibility of L2
(executors), L3 (orchestrators), L4 (state adapters), and L5 (safety).
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Iterable, List, Optional

from models import PlanObject


# ============================================================================
# META PROFILE & INJECTION CONFIGURATION
# ============================================================================


@dataclass
class MetaProfile:
    """
    Global meta-configuration for L1 planning behavior.

    planning_bias:
        • conservative: if True, fewer branches / simpler plans
        • exploratory: if True, encourage more branches / scenarios

    routing_bias:
        • per-mode hints (e.g., prefer RAG vs Strategy)
    """

    planning_bias: Dict[str, Any] = field(
        default_factory=lambda: {"conservative": False, "exploratory": True}
    )
    routing_bias: Dict[str, Any] = field(default_factory=dict)


META_PROFILE = MetaProfile()


@dataclass
class InjectionConfig:
    """
    Controls how much explicit "reasoning metadata" is attached to the
    plans so that L2/L3 can inject it into prompts.

    failure_anticipation_enabled:
        Include an explicit "top_failure_modes" list in each plan.

    self_consistency_enabled:
        Include fields describing how many alternative branches or
        self-consistency checks to run.

    reason_then_answer:
        Mark plans with a hint that responses should be structured as
        (reasoning → answer).

    error_simulation_enabled:
        Allow L2 to optionally simulate common error modes to improve
        robustness (used by some planners).
    """

    failure_anticipation_enabled: bool = True
    self_consistency_enabled: bool = True
    reason_then_answer: bool = True
    error_simulation_enabled: bool = True

    def as_dict(self) -> Dict[str, Any]:
        return {
            "failure_anticipation_enabled": self.failure_anticipation_enabled,
            "self_consistency_enabled": self.self_consistency_enabled,
            "reason_then_answer": self.reason_then_answer,
            "error_simulation_enabled": self.error_simulation_enabled,
        }


INJECTION_CONFIG = InjectionConfig()


# ============================================================================
# SHARED PLANNING UTILITIES (job/resume analysis, metrics, sections)
# ============================================================================


def _as_list(value: Any) -> List[str]:
    """Normalize arbitrary value to a list of strings."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray)):
        return [str(v) for v in value]
    return [str(value)]


def extract_job_profile(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract a normalized "job profile" from state["job"] and related fields.

    Returns:
        {
            "title": str,
            "company": str,
            "summary": str,
            "team": str,
            "location": str,
            "requirements": List[str]
        }
    """
    job = state.get("job") or {}

    def _first(*keys: str) -> str:
        for key in keys:
            value = job.get(key)
            if value:
                return str(value)
        return ""

    raw_requirements = (
        job.get("top_requirements")
        or job.get("required_skills")
        or job.get("keywords")
        or job.get("skills")
        or []
    )

    if isinstance(raw_requirements, str):
        requirements = [part.strip() for part in raw_requirements.split(",") if part.strip()]
    elif isinstance(raw_requirements, Iterable):
        requirements = [str(item).strip() for item in raw_requirements if str(item).strip()]
    else:
        requirements = []

    return {
        "title": _first("job_title", "title", "role"),
        "company": _first("company", "employer", "organization"),
        "summary": _first("summary", "description", "jd_excerpt", "jd"),
        "team": _first("team", "org_unit", "department"),
        "location": _first("location", "city"),
        "requirements": requirements,
    }


def extract_resume_profile(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract a normalized "resume profile" from state["resume"]["master_resume"].

    Returns:
        {
            "summary": str,
            "experiences": List[Dict[str, Any]]
        }
    """
    resume = state.get("resume") or {}
    master = resume.get("master_resume") or {}
    summary = (
        master.get("summary")
        or master.get("professional_summary")
        or master.get("profile")
        or ""
    )
    experiences = master.get("professional_experience")
    if not isinstance(experiences, list):
        experiences = []
    return {"summary": str(summary), "experiences": experiences}


def describe_experience(exp: Dict[str, Any]) -> str:
    """Produce a compact, human-readable description for an experience block."""
    title = exp.get("title") or exp.get("role") or "Role"
    company = exp.get("company") or exp.get("employer") or "Company"
    scope = (
        exp.get("impact_summary")
        or exp.get("summary")
        or exp.get("description")
        or ""
    )
    text = f"{title} @ {company}"
    if scope:
        text += f" – {scope}"
    return text.strip()


def detect_metrics(exps: List[Dict[str, Any]]) -> List[str]:
    """
    Identify experiences that contain explicit metrics and emit
    metric-focused guidance for bullet/draft planning.
    """
    metrics: List[str] = []
    for exp in exps:
        parts: List[str] = []
        for key in ("impact_summary", "summary", "description"):
            value = exp.get(key)
            if value:
                parts.append(str(value))
        bullet_pool = exp.get("bullet_pool")
        if isinstance(bullet_pool, list):
            parts.extend(str(b) for b in bullet_pool)
        combined = " ".join(parts)
        if any(ch.isdigit() for ch in combined):
            metrics.append(f"Quantify results from {describe_experience(exp)}")
    if not metrics:
        metrics.append("Quantify at least one measurable outcome per major role")
    return metrics


def collect_sections(state: Dict[str, Any]) -> List[str]:
    """
    Determine which sections should be present in the draft.

    Uses existing draft sections if any; otherwise defaults.
    """
    draft = state.get("draft") or {}
    sections = draft.get("sections")
    if isinstance(sections, dict) and sections:
        return list(sections.keys())
    return ["summary", "experience", "skills"]


def _latest_user_message(state: Dict[str, Any]) -> str:
    """Return the latest user-facing message content from state['messages']."""
    messages = state.get("messages") or []
    for msg in reversed(messages):
        if isinstance(msg, dict) and msg.get("role") == "user" and msg.get("content"):
            return str(msg["content"])
    return ""


# ============================================================================
# COMPLEXITY CLASSIFICATION (for routing & ToT depth)
# ============================================================================


def classify_complexity(state: Dict[str, Any]) -> str:
    """
    Deterministic complexity classifier for planning:

        • "simple"  – short objectives, few requirements
        • "medium"  – moderate token length / JD complexity
        • "complex" – long objectives or many requirements

    L2/L3 can refine this using real cost/latency signals; L1 emits
    only a heuristic hint for downstream routing.
    """
    objective = str(state.get("objective") or "")
    latest = _latest_user_message(state)
    job = extract_job_profile(state)

    token_count = len((objective + " " + latest).split())
    req_count = len(job["requirements"])

    if token_count < 10 and req_count <= 2:
        return "simple"
    if token_count < 40 and req_count <= 5:
        return "medium"
    return "complex"


# ============================================================================
# STRATEGY PLANNING (ToT, multi-branch, assessments, scenarios)
# ============================================================================


@dataclass
class StrategyBranchPlan:
    branch_id: str
    strategy_name: str
    focus_areas: List[str] = field(default_factory=list)
    key_achievements: List[str] = field(default_factory=list)
    tone: str = "Professional"
    rationale: str = ""


@dataclass
class PlannerAssessment:
    planner_name: str
    vote: str                # "approve" | "revise"
    rationale: str
    confidence: float
    recommended_actions: List[str] = field(default_factory=list)


@dataclass
class ScenarioSimulation:
    scenario_name: str
    risk_level: str          # "low" | "medium" | "high"
    impact_score: float      # 0.0–1.0
    summary: str
    mitigation_actions: List[str] = field(default_factory=list)


def _objective_from_state(state: Dict[str, Any]) -> str:
    for key in ("objective", "task", "goal"):
        value = state.get(key)
        if value:
            return str(value)
    return "unspecified-objective"


def _strategy_branches_from_context(
    job_profile: Dict[str, Any],
    resume_profile: Dict[str, Any],
    state: Dict[str, Any],
    branching_factor: int,
) -> List[StrategyBranchPlan]:
    """
    Deterministically construct "strategy branches" using job & resume context.

    This is a purely cognitive planning step; L2 may later choose to
    *realize* these branches via LLM calls.
    """
    title = job_profile["title"] or "Target Role"
    company = job_profile["company"] or "Target Company"
    summary = resume_profile["summary"]
    experiences = resume_profile["experiences"]

    base_focus = [
        f"Position candidate as a leading {title} at {company}",
        "Demonstrate measurable impact across key roles",
        "Align narrative with top JD requirements",
    ]
    base_achievements: List[str] = []
    for exp in experiences[:3]:
        base_achievements.append(describe_experience(exp))

    if not base_achievements and summary:
        base_achievements.append(f"Leverage summary: {summary[:120]}")

    branches: List[StrategyBranchPlan] = []
    for idx in range(branching_factor):
        suffix = f"Variant {idx + 1}"
        strategy_name = f"{title} @ {company} – {suffix}"

        # introduce small deterministic variation by slicing
        focus_slice = base_focus[:]
        if idx == 1 and job_profile["team"]:
            focus_slice.append(f"Highlight leadership of {job_profile['team']}")
        if idx == 2 and job_profile["location"]:
            focus_slice.append(f"Emphasize regional experience in {job_profile['location']}")

        achievements_slice = base_achievements[:]
        if idx == 1 and len(achievements_slice) > 1:
            achievements_slice = achievements_slice[1:] + achievements_slice[:1]
        if idx == 2 and len(achievements_slice) > 2:
            achievements_slice = achievements_slice[2:] + achievements_slice[:2]

        title_lower = title.lower()
        tone = state.get("tone") or ("Leadership" if "lead" in title_lower else "Professional")
        rationale = f"Branch {idx + 1} balances JD focus with resume strengths."

        branches.append(
            StrategyBranchPlan(
                branch_id=f"branch_{idx + 1}",
                strategy_name=strategy_name,
                focus_areas=focus_slice,
                key_achievements=achievements_slice,
                tone=tone,
                rationale=rationale,
            )
        )

    return branches


def _assess_branches(
    branches: List[StrategyBranchPlan],
    job_profile: Dict[str, Any],
) -> List[PlannerAssessment]:
    """
    Lightweight "planner ensemble" – domain, risk, feasibility – as
    deterministic heuristics. L2 can later run deeper LLM-based analyses.
    """
    assessments: List[PlannerAssessment] = []

    # Domain alignment: does strategy mention title/company?
    for br in branches:
        focus_text = " ".join(br.focus_areas).lower()
        title = job_profile["title"].lower()
        company = job_profile["company"].lower()

        matches = 0
        if title and title.split()[0] in focus_text:
            matches += 1
        if company and company in focus_text:
            matches += 1

        if matches >= 1:
            vote = "approve"
            rationale = "Focus areas reference role/company context."
            confidence = 0.7 + 0.1 * min(matches, 2)
        else:
            vote = "revise"
            rationale = "No explicit domain alignment detected."
            confidence = 0.55

        assessments.append(
            PlannerAssessment(
                planner_name=f"DomainPlanner::{br.branch_id}",
                vote=vote,
                rationale=rationale,
                confidence=round(confidence, 3),
                recommended_actions=(
                    []
                    if matches
                    else [
                        "Introduce at least one focus area referencing job title or company priorities."
                    ]
                ),
            )
        )

    # Simple risk/feasibility: number of focus areas & achievements
    for br in branches:
        focus_count = len(br.focus_areas)
        dup_focus = len({f.lower() for f in br.focus_areas}) != focus_count
        quantified = any(any(ch.isdigit() for ch in a) for a in br.key_achievements)

        vote = "approve"
        rationale_bits: List[str] = []
        if focus_count > 5:
            vote = "revise"
            rationale_bits.append("Too many focus areas; risk of dilution.")
        if dup_focus:
            vote = "revise"
            rationale_bits.append("Overlapping/duplicate focus areas.")
        if not quantified:
            rationale_bits.append("Lacks clearly quantified wins.")
        if not rationale_bits:
            rationale_bits.append("Balanced number of focus areas with measurable wins.")
        rationale = " ".join(rationale_bits)

        confidence = 0.75 if vote == "approve" else 0.6

        recs: List[str] = []
        if focus_count > 5:
            recs.append("Prioritize the top 3–4 focus areas with strongest evidence.")
        if dup_focus:
            recs.append("Merge or remove overlapping focus areas.")
        if not quantified:
            recs.append("Add at least two quantified achievements (%, $, x).")

        assessments.append(
            PlannerAssessment(
                planner_name=f"RiskFeasibility::{br.branch_id}",
                vote=vote,
                rationale=rationale,
                confidence=round(confidence, 3),
                recommended_actions=recs,
            )
        )

    return assessments


def _simulate_scenarios(branches: List[StrategyBranchPlan]) -> List[ScenarioSimulation]:
    """
    Scenario simulations approximate "what if" analysis for hiring manager,
    technical deep-dive, and cross-functional collaboration.

    This is a deterministic heuristic simulation; L2 may augment/replace
    it with LLM-based scenario reasoning.
    """
    scenarios: List[ScenarioSimulation] = []

    for br in branches:
        # Hiring Manager Adoption
        quantified = any(any(ch.isdigit() for ch in a) for a in br.key_achievements)
        risk = "low" if quantified else "medium"
        impact = 0.35 if quantified else 0.65
        scenarios.append(
            ScenarioSimulation(
                scenario_name=f"HiringManager::{br.branch_id}",
                risk_level=risk,
                impact_score=round(impact, 3),
                summary=(
                    "Metrics-driven achievements improve adoption."
                    if quantified
                    else "Lack of metrics may slow stakeholder buy-in."
                ),
                mitigation_actions=(
                    []
                    if quantified
                    else ["Add quantified impact statements for at least 2 key achievements."]
                ),
            )
        )

        # Technical Deep Dive
        has_tech = any("tech" in f.lower() or "data" in f.lower() for f in br.focus_areas)
        risk = "low" if has_tech else "medium"
        impact = 0.4 if has_tech else 0.7
        scenarios.append(
            ScenarioSimulation(
                scenario_name=f"TechnicalDeepDive::{br.branch_id}",
                risk_level=risk,
                impact_score=round(impact, 3),
                summary=(
                    "Technical focus prepares for deep-dive discussions."
                    if has_tech
                    else "Potential technical grilling may expose focus gaps."
                ),
                mitigation_actions=(
                    []
                    if has_tech
                    else ["Introduce a technical depth focus area (platforms, stacks, tooling)."]
                ),
            )
        )

        # Cross-Functional Alignment
        has_lead = any("lead" in f.lower() or "stakeholder" in f.lower() for f in br.focus_areas)
        risk = "low" if has_lead else "medium"
        impact = 0.3 if has_lead else 0.6
        scenarios.append(
            ScenarioSimulation(
                scenario_name=f"CrossFunctional::{br.branch_id}",
                risk_level=risk,
                impact_score=round(impact, 3),
                summary=(
                    "Leadership emphasis supports cross-functional narratives."
                    if has_lead
                    else "Missing leadership signal may reduce collaboration confidence."
                ),
                mitigation_actions=(
                    []
                    if has_lead
                    else ["Add a focus area on cross-functional leadership / stakeholder alignment."]
                ),
            )
        )

    return scenarios


class StrategyReasoner:
    """
    L1 Strategy Reasoner (ToT + planner ensemble).

    Produces a PlanObject with:
        • mode: "strategy"
        • branches: list of candidate strategies
        • planner_assessments: domain/risk/feasibility signals
        • scenario_simulations: predicted outcomes
        • aggregated_decision: "approve" / "revise"
        • aggregated_confidence: float
        • aggregated_rationale: str
        • injection & safety metadata
    """

    def plan(self, state: Dict[str, Any]) -> PlanObject:
        job_profile = extract_job_profile(state)
        resume_profile = extract_resume_profile(state)
        objective = _objective_from_state(state)
        complexity = classify_complexity(state)

        # Determine branching factor from meta profile + complexity
        base_branches = 3
        if complexity == "simple":
            base_branches = 2
        elif complexity == "complex":
            base_branches = 4

        if META_PROFILE.planning_bias.get("conservative"):
            branching_factor = max(1, base_branches - 1)
        elif META_PROFILE.planning_bias.get("exploratory", True):
            branching_factor = base_branches + 1
        else:
            branching_factor = base_branches

        branches = _strategy_branches_from_context(
            job_profile=job_profile,
            resume_profile=resume_profile,
            state=state,
            branching_factor=branching_factor,
        )
        assessments = _assess_branches(branches, job_profile)
        scenarios = _simulate_scenarios(branches)

        # Aggregate votes across planners
        vote_weight: Dict[str, float] = {"approve": 0.0, "revise": 0.0}
        rationales: List[str] = []
        for a in assessments:
            vote_weight[a.vote] = vote_weight.get(a.vote, 0.0) + a.confidence
            rationales.append(f"{a.planner_name}: {a.vote} ({a.rationale})")

        total_weight = max(vote_weight["approve"] + vote_weight["revise"], 1e-6)
        approve_ratio = vote_weight["approve"] / total_weight
        aggregated_decision = "approve" if approve_ratio >= 0.5 else "revise"
        aggregated_confidence = round(approve_ratio, 3)
        aggregated_rationale = " | ".join(rationales)

        plan = PlanObject(
            {
                "layer": "l1",
                "mode": "strategy",
                "objective": objective,
                "job_profile": job_profile,
                "resume_profile": {
                    "has_summary": bool(resume_profile["summary"]),
                    "experience_count": len(resume_profile["experiences"]),
                },
                "branches": [asdict(b) for b in branches],
                "planner_assessments": [asdict(a) for a in assessments],
                "scenario_simulations": [asdict(s) for s in scenarios],
                "aggregated_decision": aggregated_decision,
                "aggregated_confidence": aggregated_confidence,
                "aggregated_rationale": aggregated_rationale,
                "complexity": complexity,
                # ToT / self-consistency hints for L2
                "tot_config": {
                    "branching_factor": branching_factor,
                    "vote_method": "weighted_confidence",
                    "reason_then_answer": INJECTION_CONFIG.reason_then_answer,
                },
                # Handoff hint for L2 strategy execution
                "handoff": {
                    "target_layer": "l2",
                    "preferred_executor": "strategy",
                    "expected_deliverables": ["strategy_summary", "prompt_blueprint"],
                },
                # Injection metadata
                "injection_framing": {
                    "global_goal": "Create a verified, high-signal job strategy.",
                    "success_criteria": "Clear focus areas, measurable wins, alignment to JD.",
                    "task_mode": "strategy_planning",
                    "scope_boundaries": "Do not hallucinate roles or companies that do not exist.",
                    "cost_latency": "Optimize for quality over speed; limit branches if necessary.",
                },
                "injection_reasoning": INJECTION_CONFIG.as_dict(),
                "safety_metadata": {
                    "objective": objective,
                    "audience": state.get("audience", "general"),
                    "tags": ["planning", "strategy"],
                    "sensitivity": "low",
                },
            }
        )
        return plan


# ============================================================================
# RAG PLANNING (HYDE-aware, hybrid ranking, risk checks)
# ============================================================================


def _build_rag_queries(state: Dict[str, Any]) -> List[str]:
    """
    Construct retrieval queries from state:
        • explicit rag_queries, if provided
        • objective, latest user message
        • job/resume context
    """
    explicit = state.get("rag_queries")
    if explicit:
        return [str(q) for q in explicit]

    objective = state.get("objective") or "unspecified-objective"
    latest = _latest_user_message(state)
    job = extract_job_profile(state)
    resume = extract_resume_profile(state)

    queries: List[str] = []
    if objective:
        queries.append(f"evidence supporting objective: {objective}")
    if latest:
        queries.append(f"user_intent: {latest}")
    if job.get("title"):
        queries.append(f"industry context for role: {job['title']} at {job.get('company', '')}")
    if resume.get("summary"):
        queries.append(f"resume summary alignment: {resume['summary'][:160]}")

    return queries or ["general background for candidate suitability"]


class RAGReasoner:
    """
    L1 RAG Reasoner.

    Produces a PlanObject with:
        • mode: "rag"
        • retrieval: queries, filters, ranking strategy, HYDE usage
        • risk_checks: what must be enforced by L2/L3
        • injection & safety metadata
    """

    def plan(self, state: Dict[str, Any]) -> PlanObject:
        job_profile = extract_job_profile(state)
        resume_profile = extract_resume_profile(state)
        objective = state.get("objective") or "unspecified-objective"

        queries = _build_rag_queries(state)
        filters = state.get("rag_filters") or {}
        ranking = {
            "strategy": state.get("rag_ranking_strategy", "hybrid"),
            "limit": state.get("rag_limit", 5),
            "enable_hyde": state.get("rag_enable_hyde", True),
        }

        risk_checks: List[str] = [
            "tie_each_top_result_to_resume_source",
            "avoid conflicting evidence across experiences",
            "ensure at least one leadership and one technical example if relevant",
        ]
        if job_profile["requirements"]:
            risk_checks.append(
                "map RAG results to top JD requirements: "
                + ", ".join(job_profile["requirements"][:3])
            )

        plan = PlanObject(
            {
                "layer": "l1",
                "mode": "rag",
                "objective": objective,
                "job_profile": job_profile,
                "resume_profile": {
                    "has_summary": bool(resume_profile["summary"]),
                    "experience_count": len(resume_profile["experiences"]),
                },
                "retrieval": {
                    "queries": queries,
                    "filters": filters,
                    "ranking": ranking,
                    "metadata": {
                        "use_hyde": ranking["enable_hyde"],
                        "fusion_strategy": "query_rank_merge",
                        "hybrid_ranker_enabled": ranking["strategy"] == "hybrid",
                    },
                },
                "risk_checks": risk_checks,
                "handoff": {
                    "target_layer": "l2",
                    "preferred_executor": "rag",
                    "expected_deliverables": ["ranked_documents", "rag_metadata"],
                },
                "injection_framing": {
                    "global_goal": "Surface trustworthy, resume-aligned evidence.",
                    "success_criteria": "High recall, high precision, low redundancy.",
                    "task_mode": "retrieval_planning",
                    "scope_boundaries": "Do not fabricate sources; respect privacy constraints.",
                    "cost_latency": "Prefer semantic caching & hybrid ranking to reduce cost.",
                },
                "injection_reasoning": INJECTION_CONFIG.as_dict(),
                "safety_metadata": {
                    "objective": objective,
                    "audience": state.get("audience", "general"),
                    "tags": ["planning", "rag"],
                    "sensitivity": "low",
                },
            }
        )
        return plan


# ============================================================================
# DRAFTING PLANNING (structure, tone, key messages, risks)
# ============================================================================


class DraftingReasoner:
    """
    L1 Drafting Reasoner.

    Produces a PlanObject with:
        • mode: "drafting"
        • sections: which sections to produce/edit
        • tone & audience
        • key_messages: narrative guardrails
        • review_gates: checkpoints for QA
        • risks: narrative / JD gap risks
    """

    def plan(self, state: Dict[str, Any]) -> PlanObject:
        job_profile = extract_job_profile(state)
        resume_profile = extract_resume_profile(state)
        objective = state.get("objective") or "unspecified-objective"
        sections = collect_sections(state)
        tone = state.get("tone") or self._infer_tone(job_profile, state)
        audience = state.get("audience", "general")

        key_messages = self._build_key_messages(job_profile, resume_profile, sections)
        review_gates = self._build_review_gates(job_profile)
        risks = self._build_risks(job_profile, resume_profile)

        plan = PlanObject(
            {
                "layer": "l1",
                "mode": "drafting",
                "objective": objective,
                "sections": sections,
                "tone": tone,
                "audience": audience,
                "key_messages": key_messages,
                "review_gates": review_gates,
                "risks": risks,
                "handoff": {
                    "target_layer": "l2",
                    "preferred_executor": "drafting",
                    "expected_deliverables": ["section_drafts", "draft_metadata"],
                },
                "injection_framing": {
                    "global_goal": "Assemble a coherent, evidence-backed narrative.",
                    "success_criteria": "Clear structure, consistent tone, JD-aligned messaging.",
                    "task_mode": "drafting_planning",
                    "scope_boundaries": "Do not invent new roles or employers.",
                    "cost_latency": "Favor clarity and correctness over verbosity.",
                },
                "injection_reasoning": INJECTION_CONFIG.as_dict(),
                "safety_metadata": {
                    "objective": objective,
                    "audience": audience,
                    "tags": ["planning", "drafting"],
                    "sensitivity": "low",
                },
            }
        )
        return plan

    def _infer_tone(self, job_profile: Dict[str, Any], state: Dict[str, Any]) -> str:
        title = (job_profile["title"] or "").lower()
        if any(token in title for token in ["vp", "chief", "director", "head"]):
            return "Executive"
        if any(token in title for token in ["lead", "manager"]):
            return "Leadership"
        return state.get("tone", "Professional")

    def _build_key_messages(
        self,
        job_profile: Dict[str, Any],
        resume_profile: Dict[str, Any],
        sections: List[str],
    ) -> List[str]:
        messages: List[str] = []
        if job_profile["title"]:
            messages.append(f"Position candidate as the ideal {job_profile['title']}")
        if job_profile["company"]:
            messages.append(f"Align story with {job_profile['company']} priorities")
        if resume_profile["summary"]:
            messages.append("Preserve unique language from resume summary where appropriate")
        if job_profile["requirements"]:
            messages.append(
                "Explicitly cover JD focus areas: "
                + ", ".join(job_profile["requirements"][:3])
            )
        if "experience" in [s.lower() for s in sections]:
            messages.append("Highlight 2–3 signature achievements per key role")

        return messages

    def _build_review_gates(self, job_profile: Dict[str, Any]) -> List[str]:
        gates = [
            "Narrative continuity review",
            "Quantified impact audit",
            "Tone & voice alignment with strategy",
            "RAG evidence consistency check",
        ]
        if job_profile["location"]:
            gates.append("Localization & market nuance review")
        return gates

    def _build_risks(
        self,
        job_profile: Dict[str, Any],
        resume_profile: Dict[str, Any],
    ) -> List[str]:
        risks = [
            "Avoid hallucinating responsibilities not present in resume.",
            "Avoid over-indexing on low-impact tasks at the expense of high-leverage wins.",
        ]
        experiences = resume_profile["experiences"]
        combined = " ".join(
            str(exp.get("impact_summary") or exp.get("summary") or "")
            for exp in experiences
        ).lower()
        missing: List[str] = []
        for req in job_profile["requirements"]:
            if req and req.lower() not in combined:
                missing.append(req)
        if missing:
            risks.append(
                "JD gaps detected: " + ", ".join(missing[:5]) + ". Address or acknowledge explicitly."
            )
        return risks


# ============================================================================
# QA PLANNING (multi-check, severity)
# ============================================================================


def _basic_qa_checks() -> List[str]:
    return [
        "content_not_empty",
        "no_forbidden_phrases",
        "narrative_coherence",
        "semantic_alignment_with_jd",
        "signal_to_noise_ratio",
        "tenure_consistency",
        "keyword_coverage",
        "bias_check",
        "adversarial_review",
        "word_count_bounds",
    ]


class QACoordinatorPlanner:
    """
    L1 QA Planner.

    Produces a PlanObject with:
        • mode: "qa"
        • checks: list of QA checks to run
        • severity: "normal" | "strict"
        • handoff hints for L2 QA executor / QA tools
    """

    def plan(self, state: Dict[str, Any]) -> PlanObject:
        objective = state.get("objective") or "qa_validation"
        audience = state.get("audience", "general")
        severity = state.get("qa_severity") or "normal"

        checks = _basic_qa_checks()
        if audience.lower() in {"executive", "board", "partner"}:
            checks.append("executive_readability")
        if severity == "strict":
            checks.append("deep_fact_checking")

        plan = PlanObject(
            {
                "layer": "l1",
                "mode": "qa",
                "objective": objective,
                "audience": audience,
                "severity": severity,
                "checks": checks,
                "handoff": {
                    "target_layer": "l2",
                    "preferred_executor": "qa",
                    "expected_deliverables": ["qa_report", "issue_annotations"],
                },
                "injection_framing": {
                    "global_goal": "Validate that the artifact is safe, accurate, and high-signal.",
                    "success_criteria": "No critical red flags; strong signal-to-noise; JD alignment.",
                    "task_mode": "qa_planning",
                    "scope_boundaries": "Do not modify content; only plan validation.",
                    "cost_latency": "Allow multiple QA passes for critical roles.",
                },
                "injection_reasoning": INJECTION_CONFIG.as_dict(),
                "safety_metadata": {
                    "objective": objective,
                    "audience": audience,
                    "tags": ["planning", "qa"],
                    "sensitivity": "normal" if severity == "normal" else "high",
                },
            }
        )
        return plan


# ============================================================================
# SAFETY / CONSTITUTIONAL PLANNING
# ============================================================================


def _default_safety_checks(audience: str) -> List[str]:
    checks = [
        "pii_redaction",
        "forbidden_content_scan",
        "toxicity_scan",
        "bias_scan",
    ]
    if audience.lower() in {"student", "underage", "minor", "child", "children"}:
        checks.append("child_protection_rules")
    return checks


class SafetyPlanner:
    """
    L1 Safety Planner.

    Produces a PlanObject with:
        • mode: "safety"
        • checks: list of safety/constitutional checks to run
        • contracts: high-level safety contract hints
    """

    def plan(self, state: Dict[str, Any]) -> PlanObject:
        objective = state.get("objective") or "safety_validation"
        audience = state.get("audience", "general")
        risk_level = state.get("risk_level", "normal")  # normal | strict | high_safety

        checks = _default_safety_checks(audience)
        contracts = {
            "allowed_audience": ["general", "professional"],
            "forbidden_terms": ["explicit", "violence", "hate", "slur"],
            "max_toxicity": 0.25 if risk_level == "normal" else 0.15,
        }

        plan = PlanObject(
            {
                "layer": "l1",
                "mode": "safety",
                "objective": objective,
                "audience": audience,
                "risk_level": risk_level,
                "checks": checks,
                "contracts": contracts,
                "handoff": {
                    "target_layer": "l2",
                    "preferred_executor": "safety",
                    "expected_deliverables": ["safety_report", "sanitized_content"],
                },
                "injection_framing": {
                    "global_goal": "Enforce safety, policy, and constitutional constraints.",
                    "success_criteria": "No PII leakage, no forbidden content, toxicity under threshold.",
                    "task_mode": "safety_planning",
                    "scope_boundaries": "Do not change underlying meaning beyond safety requirements.",
                    "cost_latency": "Allow retry or replan if safety fails.",
                },
                "injection_reasoning": INJECTION_CONFIG.as_dict(),
                "safety_metadata": {
                    "objective": objective,
                    "audience": audience,
                    "tags": ["planning", "safety"],
                    "sensitivity": risk_level,
                },
            }
        )
        return plan


# ============================================================================
# PROMPT ENGINEERING PLANNING
# ============================================================================


class PromptEngineeringPlanner:
    """
    L1 Prompt Engineering Planner.

    Plans how prompts should be structured across layers for a given task:
        • Which sections need prompt templates.
        • Which modes (strategy, rag, drafting, qa, safety) are in scope.
        • Prompt goals & constraints.

    L2 executors will realize this plan by selecting templates and
    rendering them; L1 never calls LLMs or tools.
    """

    def plan(self, state: Dict[str, Any]) -> PlanObject:
        objective = state.get("objective") or "prompt_engineering"
        audience = state.get("audience", "general")
        target_modes = state.get("prompt_target_modes") or ["strategy", "rag", "drafting", "qa", "safety"]

        plan = PlanObject(
            {
                "layer": "l1",
                "mode": "prompt_engineering",
                "objective": objective,
                "audience": audience,
                "target_modes": [str(m).lower() for m in target_modes],
                "constraints": {
                    "max_sections": 6,
                    "must_include_reasoning": True,
                    "must_include_safety_context": True,
                },
                "handoff": {
                    "target_layer": "l2",
                    "preferred_executor": "prompt_engineering",
                    "expected_deliverables": ["prompt_envelopes", "prompt_metadata"],
                },
                "injection_framing": {
                    "global_goal": "Design robust, reusable prompt envelopes.",
                    "success_criteria": "Stable sections, clear reasoning, safe outputs.",
                    "task_mode": "prompt_engineering",
                    "scope_boundaries": "Do not hardcode provider-specific tokens.",
                    "cost_latency": "Prompt templates should be reusable and cost-efficient.",
                },
                "injection_reasoning": INJECTION_CONFIG.as_dict(),
                "safety_metadata": {
                    "objective": objective,
                    "audience": audience,
                    "tags": ["planning", "prompt_engineering"],
                    "sensitivity": "low",
                },
            }
        )
        return plan


# ============================================================================
# HIL (HUMAN-IN-THE-LOOP) PLANNING
# ============================================================================


class HILPlanner:
    """
    L1 HIL Planner.

    Plans how and when human review should occur:
        • escalation triggers
        • question framing
        • urgency levels
        • which artifact(s) to present

    L2 HIL executor will actually interface with humans; L1 only plans.
    """

    def plan(self, state: Dict[str, Any]) -> PlanObject:
        objective = state.get("objective") or "hil_review"
        audience = state.get("audience", "general")
        severity = state.get("hil_severity", "normal")  # normal | high | critical

        # Simple deterministic triggers
        triggers: List[str] = []
        if state.get("requires_hil") is True:
            triggers.append("explicit_requires_hil_flag")
        if "executive" in str(audience).lower():
            triggers.append("executive_audience")
        if severity in {"high", "critical"}:
            triggers.append(f"severity_{severity}")

        if not triggers:
            triggers.append("fallback_trigger_for_uncertain_cases")

        plan = PlanObject(
            {
                "layer": "l1",
                "mode": "hil",
                "objective": objective,
                "audience": audience,
                "severity": severity,
                "triggers": triggers,
                "question_template": (
                    "Please review this artifact for correctness, tone, and completeness. "
                    "Indicate whether to approve, reject, or request changes."
                ),
                "handoff": {
                    "target_layer": "l2",
                    "preferred_executor": "hil",
                    "expected_deliverables": ["hil_prompt", "hil_response"],
                },
                "injection_framing": {
                    "global_goal": "Integrate human judgment for critical decisions.",
                    "success_criteria": "Clear, actionable human feedback recorded.",
                    "task_mode": "hil_planning",
                    "scope_boundaries": "Do not bypass safety or policy decisions.",
                    "cost_latency": "Use HIL only when necessary due to latency/cost.",
                },
                "injection_reasoning": INJECTION_CONFIG.as_dict(),
                "safety_metadata": {
                    "objective": objective,
                    "audience": audience,
                    "tags": ["planning", "hil"],
                    "sensitivity": severity,
                },
            }
        )
        return plan


# ============================================================================
# META-LEARNING PLANNING
# ============================================================================


class MetaLearningPlanner:
    """
    L1 Meta-Learning Planner.

    Describes how a meta-learning pass should interpret logs and results:
        • which signals to ingest
        • what patterns/hypotheses to look for
        • which self-correction surfaces to target

    L2/L3 handle the actual meta-learning execution.
    """

    def plan(self, state: Dict[str, Any]) -> PlanObject:
        objective = state.get("objective") or "meta_learning"
        audience = state.get("audience", "internal")
        workflow_id = state.get("workflow_id", "unknown")

        signals = state.get("meta_signals") or [
            "qa_failures",
            "safety_incidents",
            "hil_interventions",
        ]

        plan = PlanObject(
            {
                "layer": "l1",
                "mode": "meta_learning",
                "objective": objective,
                "audience": audience,
                "workflow_id": workflow_id,
                "signals": signals,
                "targets": [
                    "strategy_replan",
                    "rag_retry",
                    "qa_recheck",
                    "hil_escalation",
                ],
                "handoff": {
                    "target_layer": "l2",
                    "preferred_executor": "meta_learning",
                    "expected_deliverables": ["meta_snapshot", "meta_recommendations"],
                },
                "injection_framing": {
                    "global_goal": "Improve future workflows via meta-learning.",
                    "success_criteria": "Actionable recommendations, reduced failure patterns.",
                    "task_mode": "meta_learning_planning",
                    "scope_boundaries": "Do not alter live workflows; only produce learning signals.",
                    "cost_latency": "Can run asynchronously; not on critical user path.",
                },
                "injection_reasoning": INJECTION_CONFIG.as_dict(),
                "safety_metadata": {
                    "objective": objective,
                    "audience": audience,
                    "tags": ["planning", "meta_learning"],
                    "sensitivity": "low",
                },
            }
        )
        return plan


# ============================================================================
# MODE ROUTING & PLAN ROUTING
# ============================================================================


def route_mode(state: Dict[str, Any]) -> str:
    """
    Decide which L1 mode to use based on state.

    Priority:
        1. explicit state["mode"]
        2. explicit state["task_mode"]
        3. heuristics from objective text
    """
    mode = (state.get("mode") or "").strip().lower()
    if mode:
        return mode

    task_mode = (state.get("task_mode") or "").strip().lower()
    if task_mode:
        return task_mode

    objective = (state.get("objective") or "").lower()

    if any(k in objective for k in ["meta", "meta-learning", "learn from logs"]):
        return "meta_learning"
    if any(k in objective for k in ["prompt", "prompting", "prompt engineering"]):
        return "prompt_engineering"
    if any(k in objective for k in ["hil", "human-in-the-loop", "human review", "human approval"]):
        return "hil"
    if any(k in objective for k in ["retrieve", "rag", "evidence", "hybrid", "hyde"]):
        return "rag"
    if any(k in objective for k in ["bullet", "bullets"]):
        # For now, bullets planning is folded into drafting; we can
        # later add a dedicated BulletReasoner if needed.
        return "bullets"
    if any(k in objective for k in ["draft", "rewrite", "resume", "summary", "narrative"]):
        return "drafting"
    if "qa" in objective or "validate" in objective:
        return "qa"
    if "safety" in objective or "sanitize" in objective or "policy" in objective:
        return "safety"

    return "strategy"


def route_plan(state: Dict[str, Any]) -> PlanObject:
    """
    Top-level L1 entrypoint.

    Chooses the appropriate reasoner/planner based on route_mode and returns
    a fully-populated PlanObject describing the next agentic step.
    """
    mode = route_mode(state)

    if mode == "strategy":
        return StrategyReasoner().plan(state)
    if mode == "rag":
        return RAGReasoner().plan(state)
    if mode == "drafting":
        return DraftingReasoner().plan(state)
    if mode == "qa":
        return QACoordinatorPlanner().plan(state)
    if mode == "safety":
        return SafetyPlanner().plan(state)
    if mode == "bullets":
        # For now, bullets planning is folded into drafting; we can
        # later add a dedicated BulletReasoner if needed.
        return DraftingReasoner().plan(state)
    if mode == "prompt_engineering":
        return PromptEngineeringPlanner().plan(state)
    if mode == "hil":
        return HILPlanner().plan(state)
    if mode == "meta_learning":
        return MetaLearningPlanner().plan(state)

    # Fallback to strategy planning
    return StrategyReasoner().plan(state)
