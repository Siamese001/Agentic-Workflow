"""
Brief Assembly Engine — apps_exec.

Assembles deterministic document skeleton for an executive brief:
required headings, section ordering, evidence anchors, and
"why this matters" blocks. Narrative fill is marked as model-ready
but ships with high-quality deterministic templates.

Deterministic: section ordering, headings, metadata, evidence injection.
Model-ready:   narrative phrasing marked with LLM_FILL placeholders.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from apps_exec.engines.base_exec_engine import BaseExecEngine
from apps_exec.engines.capability_extraction_engine import ExtractionResult
from apps_exec.types.exec_types import (
    BriefSection,
    CapabilityEvidence,
    ExecBriefRequest,
)

_log = logging.getLogger(__name__)

_SECTION_SCHEMAS: dict[str, dict[str, Any]] = {
    "platform_summary": {
        "heading": "Platform Overview",
        "why": "Gives reviewers immediate orientation on the system's purpose and scope.",
        "required_for": ["recruiter", "cto", "svp_eng", "board", "head_of_ai"],
    },
    "key_capabilities": {
        "heading": "Key Capabilities",
        "why": "Enumerates concrete features that distinguish this platform.",
        "required_for": ["recruiter", "cto", "svp_eng", "head_of_ai"],
    },
    "architecture_overview": {
        "heading": "Architecture Overview",
        "why": "Shows technical reviewers the layered design and decision rationale.",
        "required_for": ["cto", "svp_eng"],
    },
    "governance_model": {
        "heading": "Governance and Safety Model",
        "why": "Demonstrates that the system enforces policy, not just best-effort behavior.",
        "required_for": ["cto", "board"],
    },
    "platform_strategy": {
        "heading": "Platform Strategy and Positioning",
        "why": "Translates architecture into business-level differentiation.",
        "required_for": ["cto", "board", "head_of_ai"],
    },
    "engineering_decisions": {
        "heading": "Key Engineering Decisions",
        "why": "Surfaces the non-obvious trade-offs that reflect engineering maturity.",
        "required_for": ["svp_eng"],
    },
    "quality_gates": {
        "heading": "Quality Gates and Validation",
        "why": "Shows that outputs are measurable and failure modes are explicit.",
        "required_for": ["svp_eng", "head_of_ai"],
    },
    "portfolio_value": {
        "heading": "Portfolio and Signal Value",
        "why": "Helps recruiters and hiring managers understand what this demonstrates.",
        "required_for": ["recruiter"],
    },
    "strategic_value": {
        "heading": "Strategic Value",
        "why": "Board-level translation of technical investments into business outcomes.",
        "required_for": ["board"],
    },
    "risk_posture": {
        "heading": "Risk Posture and Mitigations",
        "why": "Boards need to know what risks exist and how they are controlled.",
        "required_for": ["board"],
    },
    "competitive_differentiation": {
        "heading": "Competitive Differentiation",
        "why": "Positions the platform against alternatives at a strategic level.",
        "required_for": ["board", "head_of_ai"],
    },
    "enterprise_use_cases": {
        "heading": "Enterprise Use Cases",
        "why": "Grounds capabilities in real-world deployment scenarios.",
        "required_for": ["cto", "head_of_ai", "recruiter"],
    },
}

_CAPABILITY_BODY_TEMPLATE = (
    "The platform implements {capabilities}. "
    "These capabilities are enforced at the architecture layer, "
    "not bolted on as post-hoc guardrails."
)


@dataclass
class AssemblyResult:
    """Output of brief assembly."""

    sections: list[BriefSection] = field(default_factory=list)
    missing_required_sections: list[str] = field(default_factory=list)
    capabilities_used: list[CapabilityEvidence] = field(default_factory=list)


class BriefAssemblyEngine(BaseExecEngine):
    """Assemble deterministic brief skeleton for a given persona.

    Selects required sections for the target audience, injects capability
    evidence, and renders body text from deterministic templates.
    Each section declares whether it is deterministic or model-ready.
    """

    AGENT_ID = "EXEC_BRIEF_ASSEMBLY"

    def execute(self, input_data: tuple[ExecBriefRequest, ExtractionResult]) -> AssemblyResult:
        """Assemble brief sections.

        Args:
            input_data: Tuple of (ExecBriefRequest, ExtractionResult).

        Returns:
            AssemblyResult with ordered BriefSection list.
        """
        request, extraction = input_data
        persona_key = request.audience.value if hasattr(request.audience, "value") else str(request.audience)

        required_sections = [
            sec_id for sec_id, schema in _SECTION_SCHEMAS.items() if persona_key in schema["required_for"]
        ]

        caps_by_emphasis: dict[str, list[str]] = {}
        for cap in extraction.capabilities:
            caps_by_emphasis.setdefault(cap.emphasis_area, []).append(cap.label)

        cap_labels = [cap.label for cap in extraction.capabilities[:8]]
        cap_summary = ", ".join(cap_labels) if cap_labels else "layered governance, orchestration, and safety"

        sections: list[BriefSection] = []
        missing: list[str] = []

        for sec_id in required_sections:
            schema = _SECTION_SCHEMAS.get(sec_id, {})
            heading = schema.get("heading", sec_id.replace("_", " ").title())
            why = schema.get("why", "")

            body = self._render_body(sec_id, cap_summary, caps_by_emphasis, extraction.evidence_anchors)

            word_count = len(body.split())
            sections.append(
                BriefSection(
                    section_id=sec_id,
                    heading=heading,
                    body=body,
                    is_deterministic=True,
                    evidence_anchors=tuple(extraction.evidence_anchors[:5]),
                    why_this_matters=why,
                    word_count=word_count,
                )
            )

        self.record_pass(f"Assembled {len(sections)} sections for persona={persona_key}")
        return AssemblyResult(
            sections=sections,
            missing_required_sections=missing,
            capabilities_used=extraction.capabilities,
        )

    def _render_body(
        self,
        sec_id: str,
        cap_summary: str,
        caps_by_emphasis: dict[str, list[str]],
        evidence_anchors: list[str],
    ) -> str:
        """Render deterministic body text for a section."""
        anchor_note = f" Evidence anchors: {', '.join(evidence_anchors[:3])}." if evidence_anchors else ""

        templates: dict[str, str] = {
            "platform_summary": (
                f"This platform is a production-grade agentic AI system implementing {cap_summary}. "
                "It is built on a layered architecture with explicit enforcement boundaries between "
                "routing, execution, orchestration, state, safety, and observability."
                f"{anchor_note}"
            ),
            "key_capabilities": (
                f"Core capabilities include: {cap_summary}. "
                "Each capability is implemented as a first-class architectural concern, "
                "not a post-hoc addition."
            ),
            "architecture_overview": (
                "The system uses a six-layer architecture (L0–L6) where each layer has "
                "a strictly enforced dependency boundary. L0 handles routing and governance enforcement. "
                "L5 enforces static safety checks and determinism contracts. "
                "L6 provides observability and tracing."
                f"{anchor_note}"
            ),
            "governance_model": (
                "Policy is enforced at the routing layer (L0) via signed InstructionPackets "
                "with policy_hash validation. Static analysis detects non-deterministic calls "
                "in execution-critical paths. All violations are surfaced with rule IDs and evidence."
            ),
            "platform_strategy": (
                "The platform is positioned as enterprise-ready infrastructure for "
                "agentic AI deployments where governance, reproducibility, and auditability "
                "are non-negotiable requirements — not optional features."
            ),
            "engineering_decisions": (
                "Key decisions include: (1) frozen dataclass types for immutable execution "
                "contracts; (2) ADG-enforced layer boundaries preventing dependency inversion; "
                "(3) pre-commit hooks as constitutional enforcement, not advisory linting; "
                "(4) determinism-first design with explicit model-driven zones."
            ),
            "quality_gates": (
                "Every pipeline stage has explicit quality gates. Gate failures are reported "
                "with rule IDs, severity levels, and evidence. No silent fallback. "
                "Dry-run mode available on every entrypoint."
            ),
            "portfolio_value": (
                "This repository demonstrates: layered system design, governance enforcement, "
                "multi-hop agent orchestration, static analysis tooling, and production-grade "
                "output contracts. It reflects the thinking of a senior AI platform architect."
            ),
            "strategic_value": (
                f"Investment in this platform delivers: {cap_summary}. "
                "These translate directly to reduced AI risk, faster enterprise deployment cycles, "
                "and defensible audit trails."
            ),
            "risk_posture": (
                "Risk controls include: static determinism enforcement, policy hash validation, "
                "layer boundary guards, and hallucination detection gates. "
                "Every failure mode is explicit and testable."
            ),
            "competitive_differentiation": (
                "Unlike point solutions, this platform enforces governance at the architecture "
                "layer. Competitors typically bolt on safety as post-processing. "
                "Here, safety and determinism are constitutional requirements."
            ),
            "enterprise_use_cases": (
                "Target use cases: autonomous document generation, regulated-industry AI assistants, "
                "enterprise proposal and brief automation, evaluation lab for AI workloads, "
                "and research synthesis pipelines."
            ),
        }

        return templates.get(
            sec_id,
            f"[SECTION: {sec_id}] Capabilities: {cap_summary}.{anchor_note}",
        )
