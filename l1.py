# FILE: l1.py
"""
Unified L1 Cognition Layer (v10_9 Enterprise Refactor — FULL OVERWRITE)

This module implements ALL **pure cognition** responsibilities for v10_9:

    • StrategyReasoner             — multi-branch ToT strategy planning
    • RAGReasoner                  — hybrid retrieval planning (HYDE-aware)
    • DraftingReasoner             — structure, tone, review gates, risks
    • QACoordinatorPlanner         — QA checks, severity, tool-suite signals
    • SafetyPlanner                — safety scenario planning
    • HILPlanner                   — human-in-loop escalation planning
    • PromptEngineeringPlanner     — meta-structure for prompt shaping
    • ComplexityClassifier         — deterministic (or optional tool-hinted) complexity scoring
    • MetaLearningPlanner          — orchestration of meta-learning surfaces

**STRICT L1 RULES**:
    • NO tool / LLM execution.
    • NO orchestration, retries, pauses, or DAG control.
    • NO state mutation.
    • NO safety enforcement logic.
    • Only return PlanObject containing WHAT should happen at L2–L5.

All heavy lifting occurs in L2 executors, L3 orchestrators, L4 state adapters,
and L5 gateways.

This file is intentionally pure and deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Iterable

from models import PlanObject


# =============================================================================
# Utility Functions
# =============================================================================

def _as_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray)):
        return [str(v) for v in value]
    return [str(value)]


def _latest_user_message(state: Dict[str, Any]) -> str:
    msgs = state.get("messages") or []
    for msg in reversed(msgs):
        if isinstance(msg, dict) and msg.get("role") == "user":
            return str(msg.get("content", ""))
    return ""


def _norm_summary(state: Dict[str, Any]) -> str:
    return str(state.get("summary") or "")


# =============================================================================
# Complexity Classifier (Agentic Pillar: Reasoning Models)
# =============================================================================

class ComplexityClassifier:
    """
    Deterministic complexity classifier.

    L1-only: no LLM calls. If desired, L2 may override with actual model
    embeddings or metrics, but L1 emits the desired signal.
    """

    @staticmethod
    def classify(state: Dict[str, Any]) -> str:
        # Deterministic heuristic based on objective length and signals.
        text = (
            (state.get("objective") or "") +
            " " +
            _latest_user_message(state)
        )
        length = len(text.split())
        if length < 10:
            return "simple"
        if length < 30:
            return "medium"
        return "complex"


# =============================================================================
# Job & Resume Extraction Utilities
# =============================================================================

def extract_job_profile(state: Dict[str, Any]) -> Dict[str, Any]:
    job = state.get("job") or {}
    def first(*keys):
        for k in keys:
            if k in job and job[k]:
                return str(job[k])
        return ""
    raw_req = (
        job.get("top_requirements")
        or job.get("skills")
        or job.get("keywords")
        or []
    )
    if isinstance(raw_req, str):
        reqs = [r.strip() for r in raw_req.split(",") if r.strip()]
    elif isinstance(raw_req, Iterable):
        reqs = [str(x).strip() for x in raw_req]
    else:
        reqs = []
    return {
        "title": first("job_title", "title", "role"),
        "company": first("company", "employer"),
        "summary": first("summary", "description"),
        "requirements": reqs,
    }


def extract_resume_profile(state: Dict[str, Any]) -> Dict[str, Any]:
    resume = state.get("resume") or {}
    master = resume.get("master_resume") or {}
    exp = master.get("professional_experience")
    if not isinstance(exp, list):
        exp = []
    return {
        "summary": str(master.get("summary") or ""),
        "experiences": exp,
    }


def describe_experience(exp: Dict[str, Any]) -> str:
    role = exp.get("title") or "Role"
    comp = exp.get("company") or "Company"
    desc = (
        exp.get("impact_summary")
        or exp.get("summary")
        or exp.get("description")
        or ""
    )
    out = f"{role} @ {comp}"
    if desc:
        out += f" – {desc}"
    return out


# =============================================================================
# Strategy Reasoner (ToT)
# =============================================================================

class StrategyReasoner:
    """
    Multi-branch strategy planner using Tree-of-Thought structure:
      • branches
      • planner assessments
      • scenario simulations
      • aggregated rationale
      • complexity classification
    """

    def plan(self, state: Dict[str, Any]) -> PlanObject:
        jobp = extract_job_profile(state)
        resp = extract_resume_profile(state)
        objective = str(state.get("objective") or "unspecified-objective")
        complexity = ComplexityClassifier.classify(state)

        # Branch count depends on complexity
        branch_factor = 3 if complexity == "simple" else 4 if complexity == "medium" else 5

        # Build strategy branches
        branches = []
        for i in range(branch_factor):
            branches.append({
                "branch_id": f"branch_{i+1}",
                "strategy_name": f"{jobp['title'] or 'Role'} at {jobp['company'] or 'Company'} – Variant {i+1}",
                "focus_areas": [
                    "Align candidate profile to job requirements",
                    "Highlight metric-driven achievements",
                    "Establish leadership narrative",
                ],
                "key_achievements": [
                    describe_experience(e) for e in resp["experiences"][:3]
                ],
                "tone": state.get("tone") or "Professional",
                "rationale": "Branch variation based on deterministic complexity heuristic.",
            })

        # Simple deterministic planner assessments
        assessments = [
            {
                "planner_name": f"Assessment::{br['branch_id']}",
                "vote": "approve",
                "confidence": 0.7,
                "rationale": "Deterministic approval based on structural criteria.",
            }
            for br in branches
        ]

        # Scenario simulations
        scenarios = [
            {
                "scenario_name": f"HiringManager::{br['branch_id']}",
                "risk_level": "low",
                "impact_score": 0.35,
                "summary": "Metrics-driven achievements improve adoption.",
            }
            for br in branches
        ]

        plan = PlanObject({
            "layer": "l1",
            "mode": "strategy",
            "objective": objective,
            "job_profile": jobp,
            "resume_profile": {
                "has_summary": bool(resp["summary"]),
                "experience_count": len(resp["experiences"]),
            },
            "branches": branches,
            "planner_assessments": assessments,
            "scenario_simulations": scenarios,
            "aggregated_decision": "approve",
            "aggregated_confidence": 0.7,
            "aggregated_rationale": "Deterministic aggregated rationale.",
            "complexity": complexity,
            "handoff": {
                "target_layer": "l2",
                "preferred_executor": "strategy",
            },
        })

        return plan


# =============================================================================
# RAG Reasoner
# =============================================================================

def _build_rag_queries(state: Dict[str, Any]) -> List[str]:
    explicit = state.get("rag_queries")
    if explicit:
        return [str(x) for x in explicit]

    objective = state.get("objective") or ""
    latest = _latest_user_message(state)
    jobp = extract_job_profile(state)
    resp = extract_resume_profile(state)

    queries = []
    if objective:
        queries.append(f"evidence for objective: {objective}")
    if latest:
        queries.append(f"user_intent: {latest}")
    if jobp["title"]:
        queries.append(f"industry context for: {jobp['title']}")
    if resp["summary"]:
        queries.append(f"resume summary: {resp['summary'][:150]}")

    return queries or ["general background"]


class RAGReasoner:
    """Builds retrieval intents and metadata."""

    def plan(self, state: Dict[str, Any]) -> PlanObject:
        jobp = extract_job_profile(state)
        resp = extract_resume_profile(state)
        objective = str(state.get("objective") or "unspecified-objective")

        queries = _build_rag_queries(state)
        filters = state.get("rag_filters") or {}
        ranking = {
            "strategy": state.get("rag_ranking_strategy", "hybrid"),
            "limit": state.get("rag_limit", 5),
            "enable_hyde": state.get("rag_enable_hyde", True),
        }

        risk_checks = [
            "tie_results_to_resume_source",
            "avoid_conflicting_evidence",
            "ensure_relevance_to_jd",
        ]

        plan = PlanObject({
            "layer": "l1",
            "mode": "rag",
            "objective": objective,
            "job_profile": jobp,
            "resume_profile": {
                "has_summary": bool(resp["summary"]),
                "experience_count": len(resp["experiences"]),
            },
            "retrieval": {
                "queries": queries,
                "filters": filters,
                "ranking": ranking,
                "metadata": {
                    "use_hyde": ranking["enable_hyde"],
                    "fusion_strategy": "query_rank_merge",
                },
            },
            "risk_checks": risk_checks,
            "handoff": {
                "target_layer": "l2",
                "preferred_executor": "rag",
            },
        })
        return plan


# =============================================================================
# Drafting Reasoner
# =============================================================================

class DraftingReasoner:
    """L1 planning for structured multi-section narratives."""

    def plan(self, state: Dict[str, Any]) -> PlanObject:
        jobp = extract_job_profile(state)
        resp = extract_resume_profile(state)
        objective = state.get("objective") or "unspecified-objective"

        sections = (
            state.get("outline")
            or ["Introduction", "Experience", "Conclusion"]
        )
        tone = state.get("tone", "Professional")
        audience = state.get("audience", "general")

        key_messages = [
            f"Position candidate as ideal {jobp['title']}" if jobp["title"] else "",
            f"Align narrative with {jobp['company']}" if jobp["company"] else "",
        ]
        key_messages = [m for m in key_messages if m]

        review_gates = [
            "coherence_review",
            "quantitative_impact_audit",
            "tone_alignment",
        ]

        risks = []
        if jobp["requirements"]:
            for r in jobp["requirements"][:3]:
                risks.append(f"Missing evidence for requirement '{r}'")

        plan = PlanObject({
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
            },
        })
        return plan


# =============================================================================
# QA Coordinator Planner
# =============================================================================

def _basic_qa_checks() -> List[str]:
    return [
        "content_not_empty",
        "no_forbidden_phrases",
        "narrative
