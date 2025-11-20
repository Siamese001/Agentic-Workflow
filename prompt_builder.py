# FILE: 10_10/prompt_builder.py
"""
Prompt Builder Layer (v10_10 · Phase 2)
=======================================

This module implements the Phase 2 prompt builder responsible for:

    • Constructing rich, multi-section prompt envelopes for:
          – Strategy reasoning
          – Retrieval evidence
          – Drafting sections
          – QA summary
          – Safety summary
    • Enforcing prompt ACL metadata (layer / agent / model tier).
    • Routing all prompt construction through the central prompt registry
      defined in ``prompt_system_v10_10.py`` – no inline, ad-hoc templates.
    • Emitting ``PromptInstance`` objects that L2 can hand off to
      cognitive agents / LLM clients.

Design notes
------------

    • This module is **pure L2** – it does not perform any LLM calls.
      It only prepares structured prompt objects.
    • It intentionally depends only on Phase-0 models and the prompt
      registry / ACL primitives; it does not invent new core types.
    • Context-budget hints are attached as metadata but no actual
      token counting is performed yet (G27–G28 hook).
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
from prompt_system_v10_10 import PROMPT_ACLS, PROMPT_REGISTRY, PromptACL
from registry import get_prompt, get_prompt_acl


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

        The order is **semantic**, not lexical; callers that want to
        render a textual prompt should iterate over these keys in the
        order defined by ``SECTION_ORDER`` below.
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

    This type is intentionally simple: it wraps the registry definition,
    the rendered text, and the governance metadata needed for L2 calls.
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


def _extract_acl_metadata(defn: PromptDefinition) -> Dict[str, List[str]]:
    """
    Extract ACL metadata from a PromptDefinition.

    Expected shape (stored in defn.metadata["acl"]):

        {
            "layers": ["L1", "L2", ...],
            "agents": ["strategy", "rag", "drafting", "qa", "safety"],
            "model_tiers": ["cheap", "balanced", "premium"],
        }

    All fields are optional; missing fields are treated as "no
    additional restriction" for that dimension.
    """
    raw_acl = {}
    if defn.metadata and isinstance(defn.metadata, dict):
        raw_acl = defn.metadata.get("acl", {}) or {}

    layers = list(raw_acl.get("layers", []))
    agents = list(raw_acl.get("agents", []))
    tiers = list(raw_acl.get("model_tiers", []))

    return {
        "layers": layers,
        "agents": agents,
        "model_tiers": tiers,
    }


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
    ``None`` (allowed) or raises ``PermissionError`` for violations.
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

    The default templates shipped in ``prompt_system_v10_10`` follow the
    pattern:

        "## CONTEXT\\n\\n## INSTRUCTIONS\\n\\n## OUTPUT_FORMAT\\n"

    This helper injects the envelope contents into those anchors while
    also adding the richer sections (Framing, Reasoning, Safety).
    """
    template = (defn.template or "").strip()

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
        prefix_parts.append(f"## FRAMING\n{sections['Framing']}")

    if sections["Reasoning"]:
        prefix_parts.append(f"## REASONING\n{sections['Reasoning']}")

    if sections["Safety Signals"]:
        prefix_parts.append(f"## SAFETY_SIGNALS\n{sections['Safety Signals']}")

    prefix = "\n\n".join(prefix_parts).strip()

    if prefix:
        return prefix + "\n\n" + body
    return body


def _build_context_budget_hints_from_plan(plan: Any) -> Dict[str, Any]:
    """
    Derive coarse context-budget hints from a plan.

    These hints are **advisory only** – Phase 2 does not perform
    token counting or hard enforcement.
    """
    hints: Dict[str, Any] = {}

    # Strategy: more steps → more budget for reasoning.
    if isinstance(plan, StrategyPlan):
        hints["max_reasoning_sections"] = len(plan.steps)
        hints["priority"] = "strategy"

    # RAG: number of hints informs evidence cap.
    if isinstance(plan, RAGPlan):
        hints["max_evidence_items"] = max(5, len(plan.hints) * 2)
        hints["priority"] = "rag"

    # Drafting: number of sections informs per-section budget.
    if isinstance(plan, DraftingPlan):
        hints["max_sections"] = len(plan.sections)
        hints["priority"] = "drafting"

    # QA: number / severity of checks informs analysis depth.
    if isinstance(plan, QAPlan):
        hints["max_checks"] = len(plan.checks)
        hints["priority"] = "qa"

    # Safety: similar to QA but for policy/PII checks.
    if isinstance(plan, SafetyPlan):
        hints["max_checks"] = len(plan.checks)
        hints["priority"] = "safety"

    return hints


def _format_evidence(evidence: Sequence[Evidence], max_items: int = 10) -> str:
    """
    Render retrieval evidence into a deterministic textual block.
    """
    if not evidence:
        return "No retrieval evidence was provided."

    sorted_items = sorted(evidence, key=lambda e: e.score, reverse=True)[:max_items]

    lines: List[str] = []
    for idx, item in enumerate(sorted_items, start=1):
        source = item.source or "unknown"
        lines.append(f"[{idx}] (score={item.score:.3f}, source={source})\n{item.text}")

    return "\n\n".join(lines)


def _summarize_strategy(plan: StrategyPlan) -> str:
    if not plan.steps:
        return "No strategy steps were provided."

    parts = []
    for step in sorted(plan.steps, key=lambda s: s.order):
        flag = "MUST" if step.must_complete else "OPTIONAL"
        parts.append(f"{step.order}. [{flag}] {step.description}")
    return "\n".join(parts)


def _summarize_qa_plan(plan: QAPlan) -> str:
    if not plan.checks:
        return "No QA checks were specified."

    parts = []
    for chk in plan.checks:
        if not chk.enabled:
            continue
        parts.append(f"- (sev={chk.severity}) {chk.id}: {chk.description}")
    return "\n".join(parts) or "All QA checks are disabled."


def _summarize_safety_plan(plan: SafetyPlan) -> str:
    if not plan.checks:
        return "No safety checks were specified."

    parts = []
    for chk in plan.checks:
        parts.append(f"- {chk.id}: {chk.description}")
    return "\n".join(parts)


def _summarize_job_and_resume(ctx: ExecutionContext) -> str:
    """
    Compact textual summary of the job + resume inputs for use in prompts.
    """
    job = ctx.job
    resume = ctx.resume

    job_lines = [
        f"Job Title: {job.title}",
        f"Role Type: {job.role_type}",
        f"Seniority: {job.seniority}",
        "",
        "Key Requirements:",
    ] + [f"- {req}" for req in (job.requirements or [])]

    resume_lines = [
        f"Candidate: {resume.name}",
        f"Summary: {resume.summary or 'N/A'}",
        "",
        "Skills:",
    ] + [f"- {s}" for s in (resume.skills or [])]

    return "\n".join(job_lines + ["", "----", ""] + resume_lines)


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

    return PromptInstance(
        prompt_id=prompt_id,
        definition=defn,
        version=defn.version,
        role=defn.role,
        rendered=rendered,
        envelope=envelope,
        variables=variables,
        layer=layer,
        agent=agent,
        model_tier=model_tier,
        context_budget_hints=context_budget_hints,
    )


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
    """
    Build a strategy reasoning prompt.

    Inputs:
        • plan – L1 StrategyPlan
        • ctx  – ExecutionContext with job / resume / config
    """
    envelope = PromptEnvelope(
        framing=(
            "You are the Strategy LLM agent (Layer {layer}) in a multi-step "
            "job-search workflow. Your role is to refine and extend the "
            "strategy plan produced by L1 while staying within the provided "
            "workflow configuration."
        ).format(layer=layer),
        context=_summarize_job_and_resume(ctx),
        reasoning=(
            "Reason step-by-step over the strategy steps, identifying "
            "gaps, risks, and opportunities. Prefer concise reasoning "
            "that still exposes your key assumptions."
        ),
        instructions=_summarize_strategy(plan),
        safety_signals=(
            "Do not fabricate job requirements or candidate experience. "
            "If information is missing, explicitly call it out instead of "
            "hallucinating."
        ),
        output_schema=(
            "Return an updated strategy narrative in markdown with clear "
            "step numbers and brief justification for each step."
        ),
    )

    variables: Dict[str, Any] = {
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
    """
    Build a retrieval / evidence fusion prompt.

    This prompt conditions the LLM to treat the provided evidence as
    soft constraints and to avoid hallucinating beyond them.
    """
    envelope = PromptEnvelope(
        framing=(
            "You are the Retrieval & Evidence Fusion agent (Layer {layer}). "
            "You summarize and interpret retrieval results to support "
            "downstream drafting and QA."
        ).format(layer=layer),
        context=_summarize_job_and_resume(ctx)
        + "\n\n"
        + "Retrieved Evidence:\n"
        + _format_evidence(evidence),
        reasoning=(
            "Identify which evidence items are most relevant for tailoring "
            "the resume to this job. Highlight overlaps between job "
            "requirements and candidate experience."
        ),
        instructions=(
            "Focus on:\n"
            "- Mapping evidence to specific requirements.\n"
            "- Flagging gaps where evidence is weak or missing.\n"
            "- Avoiding verbatim copying unless explicitly helpful."
        ),
        safety_signals=(
            "Do not invent evidence or claim experience not supported by "
            "the snippets. Treat evidence as soft but primary source."
        ),
        output_schema=(
            "Return a markdown bullet list grouping evidence under job "
            "requirements, plus a short 'Gaps' section."
        ),
    )

    variables: Dict[str, Any] = {
        "plan": plan,
        "job": ctx.job,
        "resume": ctx.resume,
        "config": ctx.config,
        "evidence": list(evidence),
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
    """
    Build a drafting prompt for generating resume sections.

    The prompt conditions the LLM to respect the planned structure and
    align with both strategy and evidence.
    """
    envelope = PromptEnvelope(
        framing=(
            "You are the Drafting Guild (Layer {layer}) responsible for "
            "turning strategy and evidence into polished resume sections."
        ).format(layer=layer),
        context=_summarize_job_and_resume(ctx)
        + "\n\n"
        + "Strategy Summary:\n"
        + strategy.get_chosen_branch_text()
        + "\n\nEvidence Summary:\n"
        + _format_evidence(rag.evidence),
        reasoning=(
            "Plan the narrative for each section before writing. For each "
            "section, decide what impact, scope, and technologies to "
            "emphasize based on the job requirements."
        ),
        instructions=(
            "Generate resume-ready content that:\n"
            "- Is truthful and grounded in the candidate history.\n"
            "- Is tailored to the target job.\n"
            "- Uses concise, impact-focused bullets."
        ),
        safety_signals=(
            "Do not fabricate employers, dates, or titles. If a required "
            "experience is missing, state that it is missing instead of "
            "inventing it."
        ),
        output_schema=(
            "Return markdown sections matching the DraftingPlan structure, "
            "with headings and bullet points for each section."
        ),
    )

    variables: Dict[str, Any] = {
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

    This prompt focuses on logical consistency, alignment to the job,
    and hallucination risk.
    """
    drafted_text_parts: List[str] = []
    for section in drafting.sections:
        drafted_text_parts.append(f"# {section.title}\n{section.text}")
    drafted_text = "\n\n".join(drafted_text_parts)

    envelope = PromptEnvelope(
        framing=(
            "You are the QA Agent (Layer {layer}) reviewing drafted resume "
            "content before it is sent to the user."
        ).format(layer=layer),
        context=_summarize_job_and_resume(ctx)
        + "\n\nDrafted Resume Content:\n"
        + drafted_text,
        reasoning=(
            "Systematically evaluate the draft for correctness, clarity, "
            "and alignment with the job. Pay particular attention to "
            "hallucinated claims and unsupported skills."
        ),
        instructions=_summarize_qa_plan(plan),
        safety_signals=(
            "Flag any potentially misleading or false claims. Flag content "
            "that might leak sensitive personal data beyond what is "
            "expected in a resume."
        ),
        output_schema=(
            "Return a markdown report with sections:\n"
            "- Issues (with severity and location).\n"
            "- Strengths.\n"
            "- Recommended edits."
        ),
    )

    variables: Dict[str, Any] = {
        "plan": plan,
        "job": ctx.job,
        "resume": ctx.resume,
        "config": ctx.config,
        "drafting": drafting,
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
    qa: QAResult,
    *,
    prompt_id: str = "system.safety.agent",
    layer: str = "L5",
    agent: str = "safety",
    model_tier: str = "balanced",
) -> PromptInstance:
    """
    Build a safety / policy prompt to run after QA.

    This prompt focuses on PII, policy constraints, and overall risk.
    """
    qa_summary = qa.summary or ""

    envelope = PromptEnvelope(
        framing=(
            "You are the Constitutional Safety Agent (Layer {layer}) "
            "performing a final review of the resume draft."
        ).format(layer=layer),
        context=_summarize_job_and_resume(ctx)
        + "\n\nQA Summary:\n"
        + qa_summary,
        reasoning=(
            "Evaluate the content strictly against safety and policy "
            "requirements. Consider PII exposure, discriminatory language, "
            "and compliance with general professional norms."
        ),
        instructions=_summarize_safety_plan(plan),
        safety_signals=(
            "Be conservative. If in doubt, flag the issue with an "
            "explanation rather than silently allowing it."
        ),
        output_schema=(
            "Return a markdown report with:\n"
            "- Blockers (must fix).\n"
            "- Warnings (should fix).\n"
            "- Notes (informational)."
        ),
    )

    variables: Dict[str, Any] = {
        "plan": plan,
        "job": ctx.job,
        "resume": ctx.resume,
        "config": ctx.config,
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
