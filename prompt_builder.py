# FILE: 10_10/prompt_builder.py
"""
Prompt Builder Layer (v10_10 · Phase 3)
=======================================

This module builds PromptInstance objects for all major agents:

    • Strategy reasoning
    • Retrieval evidence / RAG reasoning
    • HYDE query expansion
    • Drafting
    • QA
    • Safety

It:

    • Enforces prompt ACL metadata (layer / agent / model tier).
    • Routes all prompt construction through the central prompt registry
      defined in ``prompt_system_v10_10.py`` – no inline templates.
    • Emits ``PromptInstance`` objects that L2 can hand off to
      cognitive agents / LLM clients.

Design constraints:

    • Pure L2: no LLM calls.
    • Depends only on models + prompt_system for registry/ACL.
    • No direct provider SDK or routing logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from models import (
    ContextBudget,
    DraftingPlan,
    DraftingResult,
    Evidence,
    ExecutionContext,
    QAPlan,
    QAResult,
    RAGPlan,
    RAGResult,
    SafetyPlan,
    SafetyResult,
    StrategyPlan,
    StrategyResult,
    WorkflowPlanBundle,
    PromptDefinition,
    PromptVersion,
)
from prompt_system_v10_10 import PROMPT_ACLS, PROMPT_REGISTRY, PromptACL, get_prompt
from infra.context_engine.assembly import assemble_context
from infra.context_engine.pinned import PinnedItem
from infra.context_engine.relevance import ContextItem
from infra.context_engine.slots import ContextSlot


# =============================================================================
# Envelope & PromptInstance Types
# =============================================================================


@dataclass
class PromptEnvelope:
    """
    Structured container for deterministic prompt assembly.

    Sections map directly to the v10_8 envelope design, with explicit
    naming so that downstream rendering and logging can reason about
    each component separately.
    """

    framing: str = ""
    context: str = ""
    reasoning: str = ""
    instructions: str = ""
    safety_signals: str = ""
    output_schema: str = ""

    def to_sections(self) -> Dict[str, str]:
        """
        Return an ordered mapping of envelope sections.

        The order is semantic; callers that render a textual prompt
        should iterate using SECTION_ORDER.
        """
        return {
            "Framing": self.framing.strip(),
            "Context": self.context.strip(),
            "Reasoning": self.reasoning.strip(),
            "Instructions": self.instructions.strip(),
            "Safety Signals": self.safety_signals.strip(),
            "Output Schema": self.output_schema.strip(),
        }


SECTION_ORDER: Tuple[str, ...] = (
    "Framing",
    "Context",
    "Reasoning",
    "Instructions",
    "Safety Signals",
    "Output Schema",
)


@dataclass
class PromptInstance:
    """
    Concrete prompt ready for LLM invocation.
    """

    prompt_id: str
    definition: PromptDefinition
    version: PromptVersion
    role: str
    rendered: str
    envelope: PromptEnvelope
    variables: Dict[str, Any]
    layer: str
    agent: str
    model_tier: str
    context_budget_hints: Dict[str, Any]


# =============================================================================
# Internal helpers – ACL, envelopes, and template merging
# =============================================================================


def _extract_acl_metadata(defn: PromptDefinition) -> Dict[str, List[str]]:
    """
    Extract ACL metadata from a PromptDefinition.

    Expected shape (stored in defn.metadata["acl"]):

        {
            "layers": ["L1", "L2", ...],
            "agents": ["strategy", "rag", "drafting", "qa", "safety"],
            "model_tiers": ["cheap", "balanced", "premium"],
        }

    All fields are optional; missing fields are treated as "no restriction".
    """
    raw_acl = {}
    try:
        raw_acl = defn.metadata.get("acl", {}) or {}
    except Exception:
        raw_acl = {}

    layers = list(raw_acl.get("layers", []))
    agents = list(raw_acl.get("agents", []))
    tiers = list(raw_acl.get("model_tiers", []))

    return {
        "layers": layers,
        "agents": agents,
        "model_tiers": tiers,
    }


def _get_prompt_definition(prompt_id: str) -> PromptDefinition:
    """
    Retrieve a PromptDefinition from the central registry.

    This is a thin wrapper around ``PROMPT_REGISTRY`` / ``get_prompt``
    so that all lookups live in one place.
    """
    # Prefer the public bridge if available; fall back to raw map.
    try:
        return get_prompt(prompt_id)
    except Exception:
        if prompt_id not in PROMPT_REGISTRY:
            raise KeyError(f"Unknown prompt id: {prompt_id}")
        return PROMPT_REGISTRY[prompt_id]


def _check_prompt_acl(
    *,
    prompt_id: str,
    layer: str,
    agent: str,
    model_tier: str,
) -> None:
    """
    Enforce both registry-level ACLs and per-prompt ACL metadata.

    This function is intentionally side-effect free; it either returns
    or raises PermissionError.
    """
    # 1) Registry-level ACL (PromptACL)
    acl_obj = PROMPT_ACLS.get(prompt_id)
    if isinstance(acl_obj, PromptACL):
        if not acl_obj.engine_can_use:
            raise PermissionError(f"Engine is not allowed to use prompt '{prompt_id}'")

    # 2) PromptDefinition-level ACL metadata
    defn = _get_prompt_definition(prompt_id)
    acl_meta = _extract_acl_metadata(defn)

    allowed_layers = acl_meta.get("layers") or []
    allowed_agents = acl_meta.get("agents") or []
    allowed_tiers = acl_meta.get("model_tiers") or []

    if allowed_layers and layer not in allowed_layers:
        raise PermissionError(
            f"Prompt '{prompt_id}' not allowed for layer '{layer}' "
            f"(allowed: {allowed_layers})"
        )

    if allowed_agents and agent not in allowed_agents:
        raise PermissionError(
            f"Prompt '{prompt_id}' not allowed for agent '{agent}' "
            f"(allowed: {allowed_agents})"
        )

    if allowed_tiers and model_tier not in allowed_tiers:
        raise PermissionError(
            f"Prompt '{prompt_id}' not allowed for model tier '{model_tier}' "
            f"(allowed: {allowed_tiers})"
        )


def _render_envelope_with_template(
    defn: PromptDefinition,
    envelope: PromptEnvelope,
) -> str:
    """
    Merge a PromptEnvelope with the registry template into a final string.

    Default templates follow the pattern:

        "## CONTEXT\\n\\n## INSTRUCTIONS\\n\\n## OUTPUT_FORMAT\\n"

    This helper injects the envelope contents into those anchors while
    also adding the richer sections (Framing, Reasoning, Safety).
    """
    template = (defn.text or "").strip()
    sections = envelope.to_sections()

    # Inject into known anchors if present.
    body = template

    if "## CONTEXT" in body:
        body = body.replace(
            "## CONTEXT",
            "## CONTEXT\n" + sections["Context"] if sections["Context"] else "## CONTEXT",
        )

    if "## INSTRUCTIONS" in body:
        body = body.replace(
            "## INSTRUCTIONS",
            "## INSTRUCTIONS\n" + sections["Instructions"]
            if sections["Instructions"]
            else "## INSTRUCTIONS",
        )

    if "## OUTPUT_FORMAT" in body:
        body = body.replace(
            "## OUTPUT_FORMAT",
            "## OUTPUT_FORMAT\n" + sections["Output Schema"]
            if sections["Output Schema"]
            else "## OUTPUT_FORMAT",
        )

    # Prepend framing / reasoning / safety sections to the template body.
    prefix_parts: List[str] = []

    if sections["Framing"]:
        prefix_parts.append("### FRAMING\n" + sections["Framing"])
    if sections["Reasoning"]:
        prefix_parts.append("### REASONING\n" + sections["Reasoning"])
    if sections["Safety Signals"]:
        prefix_parts.append("### SAFETY\n" + sections["Safety Signals"])

    if prefix_parts:
        return "\n\n".join(prefix_parts + [body])
    return body


def _build_context_budget_hints_from_plan(plan: Any) -> Dict[str, Any]:
    """
    Extract context-budget hints from a plan object if it carries them.

    This is intentionally shallow and structure-agnostic.
    """
    if plan is None:
        return {}
    hints = {}
    if hasattr(plan, "context_budget") and isinstance(plan.context_budget, ContextBudget):
        cb = plan.context_budget
        hints = {
            "total_tokens": getattr(cb, "total_tokens", None),
            "planning_tokens": getattr(cb, "planning_tokens", None),
            "rag_tokens": getattr(cb, "rag_tokens", None),
            "drafting_tokens": getattr(cb, "drafting_tokens", None),
            "qa_tokens": getattr(cb, "qa_tokens", None),
            "safety_tokens": getattr(cb, "safety_tokens", None),
        }
    return {k: v for k, v in hints.items() if v is not None}


def _make_prompt_instance(
    *,
    prompt_id: str,
    layer: str,
    agent: str,
    model_tier: str,
    envelope: PromptEnvelope,
    variables: Dict[str, Any],
) -> PromptInstance:
    """
    Core helper to build a PromptInstance with ACL enforcement.
    """
    _check_prompt_acl(prompt_id=prompt_id, layer=layer, agent=agent, model_tier=model_tier)
    defn = _get_prompt_definition(prompt_id)

    rendered = _render_envelope_with_template(defn, envelope)
    context_budget_hints = _build_context_budget_hints_from_plan(variables.get("plan"))

    role = defn.metadata.get("role", "system") if isinstance(defn.metadata, dict) else "system"

    return PromptInstance(
        prompt_id=prompt_id,
        definition=defn,
        version=defn.version,
        role=role,
        rendered=rendered,
        envelope=envelope,
        variables=variables,
        layer=layer,
        agent=agent,
        model_tier=model_tier,
        context_budget_hints=context_budget_hints,
    )


# =============================================================================
# Formatting helpers
# =============================================================================


def _format_evidence(evidence: Sequence[Evidence]) -> str:
    parts: List[str] = []
    for idx, ev in enumerate(evidence or [], start=1):
        parts.append(f"[{idx}] ({ev.source}) score={ev.score:.3f}\n{ev.text}")
    return "\n\n".join(parts)


def _build_curated_context_for_rag(
    ctx: ExecutionContext,
    evidence: Sequence[Evidence],
) -> str:
    try:
        query = getattr(ctx.job, "posting_text", "") or getattr(ctx.resume, "summary", "") or ""
        pinned = [
            PinnedItem(
                id="job_resume_summary",
                text=_summarize_job_and_resume(ctx),
                metadata={},
            )
        ]
        candidates = [
            ContextItem(
                id=str(idx),
                text=getattr(ev, "text", ""),
                metadata={"source": getattr(ev, "source", None)},
            )
            for idx, ev in enumerate(evidence or [], start=1)
        ]
        if not candidates:
            return ""
        slots = [ContextSlot(id="rag", max_items=min(len(candidates), 8), metadata={})]
        assembled = assemble_context(query, pinned, candidates, slots)
        return "\n\n".join(assembled or [])
    except Exception:
        return ""


def _build_curated_context_for_drafting(
    ctx: ExecutionContext,
    strategy: StrategyResult,
    rag: RAGResult,
) -> str:
    try:
        chosen_id = getattr(strategy, "chosen_branch_id", None)
        branches = list(getattr(strategy, "branches", []) or [])
        chosen_desc = ""
        for br in branches:
            if getattr(br, "id", None) == chosen_id:
                chosen_desc = getattr(br, "description", "")
                break
        query = chosen_desc or getattr(ctx.resume, "summary", "") or ""

        pinned = [
            PinnedItem(
                id="job_resume_summary",
                text=_summarize_job_and_resume(ctx),
                metadata={},
            )
        ]
        candidates = [
            ContextItem(
                id=str(idx),
                text=getattr(ev, "text", ""),
                metadata={"source": getattr(ev, "source", None)},
            )
            for idx, ev in enumerate(getattr(rag, "evidence", []) or [], start=1)
        ]
        slots = [ContextSlot(id="drafting", max_items=min(len(candidates), 8) or 4, metadata={})]
        assembled = assemble_context(query, pinned, candidates, slots)
        return "\n\n".join(assembled or [])
    except Exception:
        return ""


def _summarize_job_and_resume(ctx: ExecutionContext) -> str:
    """
    Compact textual summary of the job + resume inputs for use in prompts.
    """
    job = ctx.job
    resume = ctx.resume

    job_lines = [
        f"Job Title: {getattr(job, 'title', '')}",
        f"Role Type: {getattr(job, 'role_type', '')}",
        f"Seniority: {getattr(job, 'seniority', '')}",
        "",
        "Key Requirements:",
    ] + [f"- {req}" for req in getattr(job, "requirements", []) or []]

    resume_lines = [
        f"Candidate: {getattr(resume, 'name', '')}",
        f"Summary: {getattr(resume, 'summary', '') or 'N/A'}",
        "",
        "Skills:",
    ] + [f"- {s}" for s in getattr(resume, "skills", []) or []]

    return "\n".join(job_lines + ["", "----", ""] + resume_lines)


# =============================================================================
# Public builder functions
# =============================================================================


def build_strategy_prompt(
    plan: StrategyPlan,
    ctx: ExecutionContext,
    *,
    prompt_id: str = "system.resume.planner",
    layer: str = "L2",
    agent: str = "strategy",
    model_tier: str = "balanced",
) -> PromptInstance:
    """Build a strategy planning prompt."""

    envelope = PromptEnvelope(
        framing=(
            "You are the Strategy Planning agent (Layer {layer}). "
            "You design a plan to tailor the resume to the job."
        ).format(layer=layer),
        context=_summarize_job_and_resume(ctx),
        reasoning="Propose several strategy branches and select the best one.",
        instructions=(
            "Produce a small set of strategy branches and then select a "
            "single branch id as the chosen strategy."
        ),
        safety_signals="Avoid fabricating experience or skills.",
        output_schema="Return structured branches with ids and rationales.",
    )

    variables = {
        "plan": plan,
        "job": ctx.job,
        "resume": ctx.resume,
        "config": ctx.config,
    }

    return _make_prompt_instance(
        prompt_id=prompt_id,
        layer=layer,
        agent=agent,
        model_tier=model_tier,
        envelope=envelope,
        variables=variables,
    )


def build_rag_prompt(
    plan: RAGPlan,
    ctx: ExecutionContext,
    evidence: Sequence[Evidence],
    *,
    prompt_id: str = "system.resume.drafter",
    layer: str = "L2",
    agent: str = "rag",
    model_tier: str = "balanced",
) -> PromptInstance:
    """Build a retrieval / evidence fusion prompt.

    Used by the Phase-3 RAG reasoning stage between retrieval and drafting.
    """

    base_context = (
        _summarize_job_and_resume(ctx)
        + "\n\nRetrieved Evidence:\n"
        + _format_evidence(evidence)
    )
    curated_context = _build_curated_context_for_rag(ctx, evidence) or base_context

    envelope = PromptEnvelope(
        framing=(
            "You are the Retrieval & Evidence Fusion agent (Layer {layer}). "
            "You summarize and interpret retrieval results to support "
            "downstream drafting and QA."
        ).format(layer=layer),
        context=curated_context,
        reasoning=(
            "Identify which evidence items are most relevant for tailoring "
            "the resume to this job. Highlight overlaps between job "
            "requirements and candidate experience."
        ),
        instructions=(
            "Analyze the evidence and produce a concise reasoning summary that "
            "captures the most important overlaps and gaps. Do not rewrite the "
            "resume; instead, describe what the drafting agent should focus on."
        ),
        safety_signals="Do not infer skills or experience not supported by evidence.",
        output_schema=(
            "Return a short reasoning summary plus a bullet list of key evidence "
            "references (by index) the drafting agent should respect."
        ),
    )

    variables = {
        "plan": plan,
        "job": ctx.job,
        "resume": ctx.resume,
        "config": ctx.config,
        "evidence": list(evidence or []),
    }

    return _make_prompt_instance(
        prompt_id=prompt_id,
        layer=layer,
        agent=agent,
        model_tier=model_tier,
        envelope=envelope,
        variables=variables,
    )


def build_hyde_prompt(
    plan: RAGPlan,
    ctx: ExecutionContext,
    *,
    prompt_id: str = "system.rag.hyde_query",
    layer: str = "L2",
    agent: str = "rag",
    model_tier: str = "balanced",
) -> PromptInstance:
    """
    Build a HYDE prompt: generate an ideal answer for use as a retrieval proxy.

    The output is a synthetic, idealized answer to the user's (implicit) query
    for the job/resume pair, which retrieval.py will treat as a dense query.
    """
    envelope = PromptEnvelope(
        framing=(
            "You are the HYDE (Hypothetical Document) generator for retrieval."
        ),
        context=_summarize_job_and_resume(ctx),
        reasoning=(
            "Imagine the ideal, well-written answer that would perfectly match "
            "this job and candidate. This answer will be used as a semantic "
            "query to retrieve similar documents."
        ),
        instructions=(
            "Write a single, coherent paragraph that describes the ideal "
            "candidate's experience and impact for this role, grounded in the "
            "provided job and resume information."
        ),
        safety_signals="Do not fabricate credentials or experience not hinted in the resume.",
        output_schema="Return only the hypothetical answer paragraph.",
    )

    variables = {
        "plan": plan,
        "job": ctx.job,
        "resume": ctx.resume,
        "config": ctx.config,
    }

    return _make_prompt_instance(
        prompt_id=prompt_id,
        layer=layer,
        agent=agent,
        model_tier=model_tier,
        envelope=envelope,
        variables=variables,
    )


def build_drafting_prompt(
    plan: DraftingPlan,
    ctx: ExecutionContext,
    strategy: StrategyResult,
    rag: RAGResult,
    *,
    prompt_id: str = "system.resume.drafter",
    layer: str = "L2",
    agent: str = "drafting",
    model_tier: str = "balanced",
) -> PromptInstance:
    """Build a drafting prompt for resume sections."""

    base_context = _summarize_job_and_resume(ctx)
    curated_context = _build_curated_context_for_drafting(ctx, strategy, rag) or base_context

    envelope = PromptEnvelope(
        framing=(
            "You are the Drafting agent (Layer {layer}). "
            "You generate resume sections tailored to the job."
        ).format(layer=layer),
        context=curated_context,
        reasoning=(
            "Use the chosen strategy and the RAG reasoning summary to decide "
            "what to emphasize and how to structure the resume."
        ),
        instructions=(
            "Produce well-structured resume sections with bullet points that "
            "highlight impact and alignment with job requirements."
        ),
        safety_signals="Do not claim experiences not grounded in the candidate's history.",
        output_schema="Return a set of sections with titles and bullet points.",
    )

    variables = {
        "plan": plan,
        "job": ctx.job,
        "resume": ctx.resume,
        "config": ctx.config,
        "strategy": strategy,
        "rag": rag,
    }

    return _make_prompt_instance(
        prompt_id=prompt_id,
        layer=layer,
        agent=agent,
        model_tier=model_tier,
        envelope=envelope,
        variables=variables,
    )


def build_qa_prompt(
    plan: QAPlan,
    ctx: ExecutionContext,
    drafting: DraftingResult,
    rag: RAGResult,
    *,
    prompt_id: str = "system.qa.agent",
    layer: str = "L3",
    agent: str = "qa",
    model_tier: str = "balanced",
) -> PromptInstance:
    """
    Build a QA prompt for validating drafted content.
    """
    envelope = PromptEnvelope(
        framing=(
            "You are the QA agent (Layer {layer}). "
            "You check the drafted resume for correctness, coherence, and "
            "alignment with the job."
        ).format(layer=layer),
        context=_summarize_job_and_resume(ctx),
        reasoning=(
            "Cross-check the drafted content with the job description and "
            "retrieved evidence to detect hallucinations or misalignment."
        ),
        instructions=(
            "Identify issues such as unsupported claims, missing key "
            "requirements, or unclear phrasing. Suggest concrete fixes."
        ),
        safety_signals="Flag any content that could be misleading or unethical.",
        output_schema="Return a list of QA findings with severity and recommendations.",
    )

    variables = {
        "plan": plan,
        "job": ctx.job,
        "resume": ctx.resume,
        "config": ctx.config,
        "draft": drafting,
        "rag": rag,
    }

    return _make_prompt_instance(
        prompt_id=prompt_id,
        layer=layer,
        agent=agent,
        model_tier=model_tier,
        envelope=envelope,
        variables=variables,
    )


def build_safety_prompt(
    plan: SafetyPlan,
    ctx: ExecutionContext,
    drafting: DraftingResult,
    qa: QAResult,
    *,
    prompt_id: str = "system.safety.agent",
    layer: str = "L5",
    agent: str = "safety",
    model_tier: str = "balanced",
) -> PromptInstance:
    """
    Build a safety prompt for final policy / safety review.
    """
    envelope = PromptEnvelope(
        framing=(
            "You are the Safety agent (Layer {layer}). "
            "You ensure the final resume output complies with policies."
        ).format(layer=layer),
        context=_summarize_job_and_resume(ctx),
        reasoning=(
            "Consider the drafted content and QA findings to assess risk "
            "and ensure compliance with internal and external policies."
        ),
        instructions=(
            "Identify any content that may violate safety policies, "
            "privacy, or fairness considerations. Suggest required edits "
            "or blocks."
        ),
        safety_signals="Err on the side of caution; escalate ambiguous cases.",
        output_schema="Return a list of safety findings with severity and required actions.",
    )

    variables = {
        "plan": plan,
        "job": ctx.job,
        "resume": ctx.resume,
        "config": ctx.config,
        "draft": drafting,
        "qa": qa,
    }

    return _make_prompt_instance(
        prompt_id=prompt_id,
        layer=layer,
        agent=agent,
        model_tier=model_tier,
        envelope=envelope,
        variables=variables,
    )
