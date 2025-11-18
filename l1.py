# FILE: v10_9_clean/l1.py
"""
Unified L1 Cognition Layer (v10_9) - PRODUCTION READY

This module consolidates ALL L1 planning responsibilities, porting the
sophisticated deterministic planners from v10.7 (Planning Stacks).

Capabilities Restored:
    • Complexity-based Strategy Selection (CoT vs ToT)
    • Heuristic RAG Query Generation (Job vs Resume Gap)
    • Draft Structure Planning (Section mapping)
    • Bullet Impact Planning (Metrics detection)
    • QA & Safety Rule Configuration

Pure cognition:
    • NO execution (L2) - Plans are instructions for L2
    • NO orchestration (L3)
    • NO state mutation (L4)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Iterable, Optional

from models import PlanObject

# ============================================================================
# 1. SHARED PLANNING UTILITIES (Ported from 10.7 planning_utils.py)
# ============================================================================

def extract_job_profile(state: Dict[str, Any]) -> Dict[str, Any]:
    job = state.get("job") or {}

    def _first(*keys):
        for k in keys:
            v = job.get(k)
            if v: return str(v)
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
    return f"{title} @ {company}".strip()

def detect_metrics(exps: List[Dict[str, Any]]) -> List[str]:
    metrics = []
    for e in exps:
        parts = []
        for key in ("impact_summary", "summary", "description"):
            if e.get(key): parts.append(str(e[key]))
        bullets = e.get("bullet_pool")
        if isinstance(bullets, list):
            parts.extend(str(x) for x in bullets)
        combined = " ".join(parts)
        # Simple heuristic: presence of digits often implies metrics
        if any(ch.isdigit() for ch in combined):
            metrics.append(f"Quantify results from {describe_experience(e)}")
    if not metrics:
        metrics.append("Quantify at least one measurable outcome per role")
    return metrics

def collect_sections(state: Dict[str, Any]) -> List[str]:
    # Default structure if not defined
    return ["executive_summary", "professional_experience", "core_competencies"]

# ============================================================================
# 2. BASE REASONER
# ============================================================================

class Reasoner(ABC):
    @abstractmethod
    def plan(self, state: Dict[str, Any]) -> PlanObject:
        ...

# ============================================================================
# 3. STRATEGY REASONER (Ported logic to config ToT)
# ============================================================================

class StrategyReasoner(Reasoner):
    def plan(self, state: Dict[str, Any]) -> PlanObject:
        job = extract_job_profile(state)
        objective = state.get("objective") or f"Optimize resume for {job['title']} at {job['company']}"
        
        # Complexity Heuristic (Simple version of 10.7 classifier)
        # If JD is long or high-level title, assume complex
        is_complex = len(job['summary']) > 1000 or "senior" in job['title'].lower() or "lead" in job['title'].lower()
        
        mode = "tot" if is_complex else "cot"
        branching_factor = 3 if is_complex else 1
        
        return PlanObject({
            "layer": "l1",
            "mode": "strategy",
            "objective": objective,
            "execution_strategy": mode,
            "branching_factor": branching_factor,
            "constraints": ["Align with JD keywords", "Maintain factual accuracy"],
            "handoff": {"target_layer": "l2", "model": "gpt-4.1" if is_complex else "gpt-4o-mini"}
        })

# ============================================================================
# 4. RAG REASONER (Ported from rag_planning.py)
# ============================================================================

class RAGReasoner(Reasoner):
    def plan(self, state: Dict[str, Any]) -> PlanObject:
        job = extract_job_profile(state)
        resume = extract_resume_profile(state)
        exps = resume["experiences"]
        reqs = job["requirements"]
        
        # 1. Goal Statement
        goal = f"Surface evidence for {job['title']} at {job['company']}"
        
        # 2. Query Generation Logic (10.7 heuristic)
        queries = []
        base_role = job["title"] or "target role"
        
        # Keyword suffix
        keyword_suffix = " ".join(reqs[:2]) if reqs else "impact metrics"
        queries.append(f"{base_role} {keyword_suffix}")
        
        # Experience-specific queries
        if exps:
            queries.append(f"{describe_experience(exps[0])} evidence for {base_role}")
        if len(exps) > 1:
            queries.append(f"Leadership examples from {describe_experience(exps[1])}")
            
        # 3. Prioritization
        prioritization = ["Match JD keywords first"]
        if exps:
            prioritization.append("Favor most recent quantified roles")

        return PlanObject({
            "layer": "l1",
            "mode": "rag",
            "objective": goal,
            "retrieval": {
                "queries": queries,
                "filters": {"recency": "5y"},
                "ranking": {"strategy": "hybrid", "prioritization": prioritization}
            },
            "handoff": {"target_layer": "l2", "model": "gpt-4o-mini"} # RAG is usually fast
        })

# ============================================================================
# 5. DRAFTING REASONER (Ported from draft_planning.py)
# ============================================================================

class DraftingReasoner(Reasoner):
    def plan(self, state: Dict[str, Any]) -> PlanObject:
        job = extract_job_profile(state)
        resume = extract_resume_profile(state)
        strat = state.get("strategy_result", {}).get("selected_strategy", {})
        
        tone = strat.get("tone") or "Professional"
        focus_areas = strat.get("focus_areas") or []
        
        # 1. Key Messages
        key_messages = []
        if job["title"]:
            key_messages.append(f"Position candidate as obvious {job['title']}")
        if focus_areas:
            key_messages.append(f"Emphasize: {', '.join(focus_areas[:2])}")
            
        # 2. Structure
        sections = collect_sections(state)
        
        # 3. Hints per section
        hints = []
        if job["requirements"]:
            hints.append(f"Integrate keywords: {', '.join(job['requirements'][:3])}")

        return PlanObject({
            "layer": "l1",
            "mode": "drafting",
            "objective": "Draft resume sections",
            "steps": [{"id": "draft", "sections": sections, "tone": tone, "audience": "recruiter", "hints": hints}],
            "handoff": {"target_layer": "l2", "model": "gpt-4.1"} # Writing needs capability
        })

# ============================================================================
# 6. BULLET REASONER (Ported from bullet_planning.py)
# ============================================================================

class BulletReasoner(Reasoner):
    def plan(self, state: Dict[str, Any]) -> PlanObject:
        job = extract_job_profile(state)
        resume = extract_resume_profile(state)
        exps = resume["experiences"]
        strat = state.get("strategy_result", {}).get("selected_strategy", {})
        
        # 1. Metrics Focus
        metrics_focus = detect_metrics(exps)
        
        # 2. Highlight Order
        highlights = []
        if exps:
            highlights = [describe_experience(e) for e in exps[:3]]
        
        # 3. Style Guidelines
        guidelines = [
            f"Use a {strat.get('tone', 'professional')} tone",
            "Lead with Action -> Metric -> Outcome"
        ]
        if job["requirements"]:
            guidelines.append(f"Mirror keywords: {', '.join(job['requirements'][:3])}")

        return PlanObject({
            "layer": "l1",
            "mode": "bullets",
            "objective": "Generate high-impact bullets",
            "steps": [{
                "id": "generate",
                "target_sections": ["professional_experience"],
                "highlight_order": highlights,
                "metrics_focus": metrics_focus,
                "style_guidelines": guidelines,
                "validation_checks": ["No repeated metrics", "One sentence max"]
            }],
            "handoff": {"target_layer": "l2", "model": "gpt-4.1"}
        })

# ============================================================================
# 7. QA & SAFETY PLANNING
# ============================================================================

class QAReasoner(Reasoner):
    def plan(self, state: Dict[str, Any]) -> PlanObject:
        return PlanObject({
            "layer": "l1",
            "mode": "qa",
            "objective": "Verify draft integrity",
            "steps": [{
                "checks": [
                    "content_not_empty", 
                    "no_forbidden_phrases", 
                    "logical_consistency", 
                    "child_safe_language" if state.get("audience") == "child" else "professional_tone"
                ],
                "audience": state.get("audience", "general")
            }],
            "handoff": {"target_layer": "l2", "model": "gpt-4o-mini"}
        })

class SafetyReasoner(Reasoner):
    def plan(self, state: Dict[str, Any]) -> PlanObject:
        return PlanObject({
            "layer": "l1",
            "mode": "safety",
            "objective": "Enforce safety policies",
            "steps": [{
                "rules": ["pii_redaction", "forbidden_content_scan", "bias_scan", "toxicity_scan"],
                "sensitivity": "high"
            }],
            "handoff": {"target_layer": "l2", "model": "safety-engine"} # Local regex engine
        })

# ============================================================================
# 8. ROUTER
# ============================================================================

def route_mode(state: Dict[str, Any]) -> str:
    # Explicit override
    if state.get("mode"): return state["mode"]
    
    # Contextual heuristics
    obj = str(state.get("objective", "")).lower()
    if "retrieve" in obj or "search" in obj: return "rag"
    if "bullet" in obj: return "bullets"
    if "draft" in obj or "write" in obj: return "drafting"
    if "qa" in obj or "verify" in obj: return "qa"
    if "safe" in obj: return "safety"
    
    return "strategy" # Default

def route_plan(state: Dict[str, Any]) -> PlanObject:
    mode = route_mode(state)
    
    reasoners = {
        "strategy": StrategyReasoner(),
        "rag": RAGReasoner(),
        "bullets": BulletReasoner(),
        "drafting": DraftingReasoner(),
        "qa": QAReasoner(),
        "safety": SafetyReasoner()
    }
    
    reasoner = reasoners.get(mode, StrategyReasoner())
    return reasoner.plan(state)
