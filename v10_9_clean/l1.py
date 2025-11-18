# FILE: v10_9_clean/l1.py
"""
Unified L1 Cognition Layer (v10_9)

Contains ALL L1 responsibilities:
    • StrategyReasoner
    • RAGReasoner
    • DraftingReasoner
    • QA Planning (L1)
    • Safety Planning (L1)
    • Shared planning utilities
    • Mode router
    • Plan router
    • Injection profiles
    • Meta profile
    • Plan contracts

Pure cognition: NO execution, NO orchestration, NO state mutation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Iterable

from models import PlanObject
from constants import WorkflowPhase


# ============================================================================
# META PROFILE
# ============================================================================

@dataclass
class MetaProfile:
    planning_bias: Dict[str, Any] = field(default_factory=lambda: {"conservative": False})
    routing_bias: Dict[str, Any] = field(default_factory=lambda: {})

META_PROFILE = MetaProfile()


# ============================================================================
# INJECTION PROFILES
# ============================================================================

@dataclass
class FramingProfile:
    global_goal: str = "Solve the user's objective effectively."
    success_criteria: str = "Produce clear, correct, context-aligned outputs."
    task_mode: str = "general"
    scope_boundaries: str = "Avoid unsafe or irrelevant content."
    cost_latency: str = "Balance cost and latency sensibly."
    extra: Dict[str, Any] = field(default_factory=dict)

DEFAULT_FRAMING_PROFILE = FramingProfile()

@dataclass
class InjectionConfig:
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

DEFAULT_INJECTION_CONFIG = InjectionConfig()


# ============================================================================
# PLAN CONTRACTS (lightweight helpers)
# ============================================================================

def _as_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, Iterable):
        return [str(v) for v in value]
    return [str(value)]


# ============================================================================
# SHARED PLANNING UTILITIES
# ============================================================================

def extract_job_profile(state: Dict[str, Any]) -> Dict[str, Any]:
    job = state.get("job") or {}

    def _first(*keys):
        for k in keys:
            v = job.get(k)
            if v:
                return str(v)
        return ""

    raw = (
        job.get("top_requirements")
        or job.get("required_skills")
        or job.get("keywords")
        or job.get("skills")
        or []
    )

    if isinstance(raw, str):
        requirements = [x.strip() for x in raw.split(",") if x.strip()]
    elif isinstance(raw, Iterable):
        requirements = [str(x).strip() for x in raw if str(x).strip()]
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
    title = exp.get("title") or exp.get("role") or "Role"
    company = exp.get("company") or exp.get("employer") or "Company"
    scope = (
        exp.get("impact_summary")
        or exp.get("summary")
        or exp.get("description")
        or ""
    )
    s = f"{title} @ {company}"
    if scope:
        s += f" – {scope}"
    return s.strip()


def detect_metrics(exps: List[Dict[str, Any]]) -> List[str]:
    metrics = []
    for e in exps:
        parts = []
        for key in ("impact_summary", "summary", "description"):
            if e.get(key):
                parts.append(str(e[key]))
        bullets = e.get("bullet_pool")
        if isinstance(bullets, list):
            parts.extend(str(x) for x in bullets)
        combined = " ".join(parts)
        if any(ch.isdigit() for ch in combined):
            metrics.append(f"Quantify results from {describe_experience(e)}")
    if not metrics:
        metrics.append("Quantify at least one measurable outcome")
    return metrics


def collect_sections(state: Dict[str, Any]) -> List[str]:
    draft = state.get("draft") or {}
    sections = draft.get("sections")
    if isinstance(sections, dict) and sections:
        return list(sections.keys())
    return ["summary", "experience", "skills"]


# ============================================================================
# BASE L1 REASONER CLASS
# ============================================================================

class Reasoner(ABC):
    @abstractmethod
    def plan(self, state: Dict[str, Any]) -> PlanObject:
        ...


# ============================================================================
# STRATEGY REASONER
# ============================================================================

def _objective_from_state(state: Dict[str, Any]) -> str:
    for k in ("objective", "task", "goal"):
        v = state.get(k)
        if v:
            return str(v)
    return "unspecified-objective"


class StrategyReasoner(Reasoner):
    def plan(self, state: Dict[str, Any]) -> PlanObject:
        objective = _objective_from_state(state)
        constraints = sorted(_as_list(state.get("constraints")))
        dependencies = sorted(_as_list(state.get("dependencies")))
        deliverables = sorted(_as_list(state.get("deliverables"))) or ["summary", "next-actions"]

        if META_PROFILE.planning_bias.get("conservative"):
            deliverables = deliverables[:2]

        steps = [
            {"id": "clarify", "action": "analyze_objective", "details": objective},
            {"id": "context", "action": "assess_context", "summary": state.get("summary", ""), "dependencies": dependencies},
            {"id": "structure", "action": "outline_deliverables", "deliverables": deliverables, "constraints": constraints},
        ]

        if META_PROFILE.planning_bias.get("conservative"):
            steps = steps[:2]

        plan = PlanObject({
            "layer": "l1",
            "mode": "strategy",
            "objective": objective,
            "constraints": constraints,
            "dependencies": dependencies,
            "deliverables": deliverables,
            "steps": steps,
            "handoff": {"target_layer": "l2", "preferred_executor": "strategy"},
        })

        plan["injection_framing"] = DEFAULT_FRAMING_PROFILE.__dict__
        plan["injection_reasoning"] = DEFAULT_INJECTION_CONFIG.as_dict()
        plan["safety_metadata"] = {
            "objective": objective,
            "audience": state.get("audience", "general"),
            "tags": ["planning"],
            "sensitivity": "low",
        }

        return plan


# ============================================================================
# RAG REASONER
# ============================================================================

def _latest_user_message(state: Dict[str, Any]) -> str:
    for m in reversed(state.get("messages") or []):
        if isinstance(m, dict) and m.get("role") == "user" and m.get("content"):
            return str(m["content"])
    return ""


def _build_rag_queries(state: Dict[str, Any]) -> List[str]:
    explicit = state.get("rag_queries")
    if explicit:
        return [str(q) for q in explicit]

    objective = state.get("objective") or "unspecified-objective"
    latest = _latest_user_message(state)
    job = extract_job_profile(state)
    resume = extract_resume_profile(state)

    queries = []
    if objective:
        queries.append(f"evidence supporting: {objective}")
    if latest:
        queries.append(f"user intent: {latest}")
    if job.get("title"):
        queries.append(f"industry context: {job['title']}")
    if resume.get("summary"):
        queries.append(f"match resume summary: {resume['summary'][:120]}")
    return queries or ["general background"]


class RAGReasoner(Reasoner):
    def plan(self, state: Dict[str, Any]) -> PlanObject:
        queries = _build_rag_queries(state)
        filters = state.get("rag_filters") or {}
        objective = str(state.get("objective", "unspecified-objective"))

        ranking = {"strategy": "hybrid", "limit": state.get("rag_limit", 5)}

        retrieval_fragment = {
            "queries": queries,
            "filters": filters,
            "ranking": ranking,
            "metadata": {
                "ranker_strategy": "hybrid",
                "fusion_strategy": "query_rank_merge",
                "hybrid_ranker_enabled": True,
            },
        }

        plan = PlanObject({
            "layer": "l1",
            "mode": "rag",
            "objective": objective,
            "retrieval": retrieval_fragment,
            "ranking": ranking,
            "handoff": {"target_layer": "l2", "preferred_executor": "rag"},
        })

        plan["retrieval_metadata"] = retrieval_fragment["metadata"]
        plan["injection_framing"] = DEFAULT_FRAMING_PROFILE.__dict__
        plan["injection_reasoning"] = DEFAULT_INJECTION_CONFIG.as_dict()
        plan["safety_metadata"] = {
            "objective": objective,
            "audience": state.get("audience", "general"),
            "tags": ["planning"],
            "sensitivity": "low",
        }

        return plan


# ============================================================================
# DRAFTING REASONER
# ============================================================================

class DraftingReasoner(Reasoner):
    def plan(self, state: Dict[str, Any]) -> PlanObject:
        objective = str(state.get("objective", "unspecified-objective"))
        tone = state.get("tone", "neutral")
        audience = state.get("audience", "general")
        sections = collect_sections(state)

        plan = PlanObject({
            "layer": "l1",
            "mode": "drafting",
            "objective": objective,
            "tone": tone,
            "audience": audience,
            "sections": sections,
            "constraints": state.get("constraints", []),
            "handoff": {"target_layer": "l2", "preferred_executor": "drafting"},
        })

        plan["injection_framing"] = DEFAULT_FRAMING_PROFILE.__dict__
        plan["injection_reasoning"] = DEFAULT_INJECTION_CONFIG.as_dict()
        plan["safety_metadata"] = {
            "objective": objective,
            "audience": audience,
            "tags": ["planning"],
            "sensitivity": "low",
        }

        return plan


# ============================================================================
# QA PLANNING
# ============================================================================

def _basic_qa_checks() -> List[str]:
    return [
        "content_not_empty",
        "no_forbidden_phrases",
        "logical_consistency",
        "factual_coherence",
        "format_integrity",
    ]

def _sensitivity_checks(aud: str) -> List[str]:
    return ["child_safe_language"] if aud.lower() == "children" else []


def build_qa_plan(state: Dict[str, Any]) -> PlanObject:
    audience = state.get("audience", "general")
    severity = (
        state.get("qa_severity")
        or state.get("qa", {}).get("severity")
        or "normal"
    )

    checks = _basic_qa_checks() + _sensitivity_checks(audience)
    objective = state.get("objective") or "qa-validation"

    plan = PlanObject({
        "layer": "l1",
        "mode": "qa",
        "objective": objective,
        "steps": [{
            "id": "qa_validate",
            "action": "execute_qa",
            "checks": checks,
            "severity": severity,
            "audience": audience,
        }],
        "deliverables": ["qa_report"],
        "handoff": {"target_layer": "l2", "preferred_executor": "qa"},
    })

    plan["injection_framing"] = DEFAULT_FRAMING_PROFILE.__dict__
    plan["injection_reasoning"] = DEFAULT_INJECTION_CONFIG.as_dict()
    plan["safety_metadata"] = {
        "objective": objective,
        "audience": audience,
        "sensitivity": severity,
        "tags": ["planning"],
    }

    return plan


# ============================================================================
# SAFETY PLANNING
# ============================================================================

def _base_safety_rules() -> List[str]:
    return [
        "pii_redaction",
        "forbidden_content_scan",
        "bias_scan",
        "toxicity_scan",
    ]

def _audience_safety_rules(aud: str) -> List[str]:
    return ["child_protection_rules"] if aud.lower() == "children" else []


def build_safety_plan(state: Dict[str, Any]) -> PlanObject:
    audience = state.get("audience", "general")
    sensitivity = (
        state.get("safety_sensitivity")
        or state.get("safety", {}).get("mode")
        or "normal"
    )

    rules = _base_safety_rules() + _audience_safety_rules(audience)
    objective = state.get("objective") or "safety-validation"

    plan = PlanObject({
        "layer": "l1",
        "mode": "safety",
        "objective": objective,
        "steps": [{
            "id": "safety_validate",
            "action": "execute_safety",
            "rules": rules,
            "sensitivity": sensitivity,
            "audience": audience,
        }],
        "deliverables": ["safety_report", "sanitized_content"],
        "handoff": {"target_layer": "l2", "preferred_executor": "safety"},
    })

    plan["injection_framing"] = DEFAULT_FRAMING_PROFILE.__dict__
    plan["injection_reasoning"] = DEFAULT_INJECTION_CONFIG.as_dict()
    plan["safety_metadata"] = {
        "objective": objective,
        "audience": audience,
        "sensitivity": sensitivity,
        "tags": ["planning"],
    }

    return plan


# ============================================================================
# MODE ROUTER
# ============================================================================

def route_mode(state: Dict[str, Any]) -> str:
    if isinstance(state.get("mode"), str) and state["mode"].strip():
        return state["mode"].strip().lower()

    if isinstance(state.get("task_mode"), str) and state["task_mode"].strip():
        return state["task_mode"].strip().lower()

    text = str(state.get("objective") or "").lower()

    if any(k in text for k in ("retrieve", "search", "evidence", "cite")):
        return "rag"
    if "bullet" in text:
        return "bullets"
    if any(k in text for k in ("draft", "rewrite", "narrative", "write")):
        return "drafting"
    if any(k in text for k in ("qa", "validate", "quality")):
        return "qa"
    if any(k in text for k in ("safety", "sanitize", "redact", "filter")):
        return "safety"

    return "strategy"


# ============================================================================
# PLAN ROUTER
# ============================================================================

def route_plan(state: Dict[str, Any]) -> PlanObject:
    mode = route_mode(state)

    if mode == "rag":
        return RAGReasoner().plan(state)
    if mode == "bullets":
        return build_bullet_plan(state)
    if mode == "drafting":
        return DraftingReasoner().plan(state)
    if mode == "qa":
        return build_qa_plan(state)
    if mode == "safety":
        return build_safety_plan(state)

    return StrategyReasoner().plan(state)
