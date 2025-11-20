# FILE: 10_10/registry.py
"""
Prompt Registry (v10_10) — GOVERNANCE & CONFIGURATION

This module implements centralized prompt governance for v10_10.

Responsibilities:
    • Define PromptBundle (ID, version, description, template, params).
    • Provide PromptRegistry for lookup by ID (+ optional version).
    • Host the default v10_10 prompt set used by cognitive agents.

Non-Responsibilities:
    • No tool definitions (sandbox/runtime_utils handle that).
    • No safety policies (L5 handles that).
    • No model routing logic (routing.RoutingPolicy handles that).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import json


# =============================================================================
# Prompt Bundle
# =============================================================================


@dataclass
class PromptBundle:
    """
    A single prompt definition with governance metadata.

    Fields:
        id:          logical ID (e.g., "strategy_generate_branch").
        version:     semantic version string (e.g., "v1").
        description: human-readable description of the use case.
        template:    text template with Python .format-style placeholders.
        temperature: default sampling temperature for this task.
        max_tokens:  default max_tokens for this task.
    """

    id: str
    version: str
    description: str
    template: str
    temperature: float = 0.2
    max_tokens: int = 1024

    def render(self, variables: Dict[str, Any]) -> str:
        """
        Render the template to a final prompt string using variables.

        Complex objects (dict, list) are converted to JSON strings and exposed
        as both 'key' and 'key_json' where appropriate.
        """
        ctx: Dict[str, Any] = {}

        for key, value in variables.items():
            if isinstance(value, (dict, list)):
                ctx[key] = value
                ctx[f"{key}_json"] = json.dumps(value, indent=2, ensure_ascii=False)
            else:
                ctx[key] = value

        class SafeDict(dict):
            def __missing__(self, k: str) -> str:
                # Preserve unknown placeholders; safer than crashing
                return "{" + k + "}"

        try:
            return self.template.format_map(SafeDict(ctx))
        except Exception:
            # Fallback if formatting fails
            return self.template


# =============================================================================
# Prompt Registry
# =============================================================================


class PromptRegistry:
    """
    Central registry for prompts used by the 10_10 cognitive agents.

    Features:
        • Multi-version support per prompt ID.
        • Lookup by (id, optional version).
        • Clean extension path for adding new prompts or A/B versions.
    """

    def __init__(self, bundles: Optional[List[PromptBundle]] = None):
        self._registry: Dict[str, List[PromptBundle]] = {}
        if bundles:
            for b in bundles:
                self.register(b)

    def register(self, bundle: PromptBundle) -> None:
        """
        Register a new PromptBundle (or a new version of an existing prompt).
        """
        versions = self._registry.setdefault(bundle.id, [])
        versions.append(bundle)
        versions.sort(key=lambda x: x.version)

    def get_prompt(self, prompt_id: str, version: Optional[str] = None) -> PromptBundle:
        """
        Retrieve a prompt bundle by ID and optional version.

        If version is None, returns the latest version.
        """
        if prompt_id not in self._registry:
            raise KeyError(f"Unknown prompt id: {prompt_id}")

        versions = self._registry[prompt_id]
        if not versions:
            raise KeyError(f"No versions registered for prompt id: {prompt_id}")

        if version is None:
            return versions[-1]

        for b in versions:
            if b.version == version:
                return b

        raise KeyError(f"No prompt '{prompt_id}' with version '{version}'")

    def __getitem__(self, prompt_id: str) -> PromptBundle:
        return self.get_prompt(prompt_id)


# =============================================================================
# Default Prompt Definitions (v10_10)
# =============================================================================

def _strategy_generate_branch() -> PromptBundle:
    return PromptBundle(
        id="strategy_generate_branch",
        version="v1",
        description="Generate a single candidate strategy branch for tailoring the resume.",
        temperature=0.4,
        max_tokens=1024,
        template=(
            "You are a senior career strategist helping a candidate tailor their resume.\n\n"
            "Job (JSON):\n{job_json}\n\n"
            "Candidate resume (JSON):\n{resume_json}\n\n"
            "Current high-level strategy plan (JSON):\n{plan_json}\n\n"
            "Branch index: {branch_index}\n"
            "Complexity: {complexity}\n\n"
            "Propose ONE coherent strategy branch that answers:\n"
            "  - How should the candidate position themselves?\n"
            "  - Which strengths should be highlighted?\n"
            "  - Which job requirements can be addressed strongly?\n"
            "  - Any trade-offs or risks?\n\n"
            "Output a single paragraph describing this strategy branch.\n"
        ),
    )


def _strategy_select_branch() -> PromptBundle:
    return PromptBundle(
        id="strategy_select_branch",
        version="v1",
        description="Select the best strategy branch index given multiple candidates.",
        temperature=0.1,
        max_tokens=64,
        template=(
            "You are evaluating multiple candidate strategies for tailoring a resume.\n\n"
            "Job (JSON):\n{job_json}\n\n"
            "Candidate resume (JSON):\n{resume_json}\n\n"
            "Strategies (branches_json):\n{branches_json}\n\n"
            "Each element is a string describing a candidate strategy.\n\n"
            "Choose the SINGLE best branch index (0-based) based on:\n"
            "  - Fit with the role and seniority\n"
            "  - Ability to highlight true strengths\n"
            "  - Coverage of key job requirements\n\n"
            "Respond with ONLY an integer (0, 1, 2, ...). No extra text.\n"
        ),
    )


def _drafting_structure() -> PromptBundle:
    return PromptBundle(
        id="drafting_structure",
        version="v1",
        description="Structure specialist: propose resume sections and outlines.",
        temperature=0.4,
        max_tokens=768,
        template=(
            "You are the STRUCTURE specialist of a drafting guild.\n"
            "Your job is to design the section structure and outline for a tailored resume.\n\n"
            "Job (JSON):\n{job_json}\n\n"
            "Candidate resume (JSON):\n{resume_json}\n\n"
            "Drafting plan (JSON):\n{drafting_plan_json}\n\n"
            "Chosen strategy branch:\n{strategy_branch}\n\n"
            "RAG evidence snippets (array):\n{rag_evidence_json}\n\n"
            "OUTPUT FORMAT (JSON array):\n"
            "[\n"
            '  {"title": "Executive Summary", "outline": "High-level positioning"},\n'
            '  {"title": "Experience", "outline": "Role, company, 2–4 bullet achievements per role"},\n'
            '  ...\n'
            "]\n"
            "Only output valid JSON. No commentary.\n"
        ),
    )


def _drafting_narrative() -> PromptBundle:
    return PromptBundle(
        id="drafting_narrative",
        version="v1",
        description="Narrative specialist: write text for a single resume section.",
        temperature=0.6,
        max_tokens=1024,
        template=(
            "You are the NARRATIVE specialist of a drafting guild.\n"
            "Your job is to write the content for a specific resume section.\n\n"
            "Section title: {section}\n"
            "Section outline: {outline}\n\n"
            "Job (JSON):\n{job_json}\n\n"
            "Candidate resume (JSON):\n{resume_json}\n\n"
            "Drafting plan (JSON):\n{drafting_plan_json}\n\n"
            "Guidelines:\n"
            "  - Use concise, impact-focused language.\n"
            "  - Prefer strong verbs and measurable outcomes.\n"
            "  - Do not fabricate details that contradict the resume.\n\n"
            "Output ONLY the section text.\n"
        ),
    )


def _drafting_compliance() -> PromptBundle:
    return PromptBundle(
        id="drafting_compliance",
        version="v1",
        description="Compliance specialist: critique a drafted section.",
        temperature=0.3,
        max_tokens=512,
        template=(
            "You are the COMPLIANCE specialist of a drafting guild.\n"
            "Your job is to review a drafted resume section for:\n"
            "  - Tone alignment (target tone: {target_tone})\n"
            "  - Clarity and concision\n"
            "  - Structural issues (missing or duplicate content)\n\n"
            "Section title: {section_title}\n"
            "Section text:\n{section_text}\n\n"
            "Drafting plan (JSON):\n{drafting_plan_json}\n\n"
            "Provide 2–5 bullet points of critique.\n"
            "If the section is strong, say so explicitly.\n"
        ),
    )


def _qa_semantic_check() -> PromptBundle:
    return PromptBundle(
        id="qa_semantic_check",
        version="v1",
        description="Semantic QA: evaluate one QA check on the draft.",
        temperature=0.2,
        max_tokens=512,
        template=(
            "You are a semantic QA agent validating a single QA check.\n\n"
            "QA check (JSON):\n{check_json}\n\n"
            "Draft (JSON):\n{draft_json}\n\n"
            "RAG evidence (array):\n{rag_evidence_json}\n\n"
            "Job (JSON):\n{job_json}\n\n"
            "Resume (JSON):\n{resume_json}\n\n"
            "Determine whether this check passes.\n\n"
            "OUTPUT FORMAT (JSON ONLY):\n"
            "{\n"
            '  "passed": true or false,\n'
            '  "reason": "short explanation",\n'
            '  "severity": 1 | 2 | 3\n'
            "}\n"
            "No extra commentary.\n"
        ),
    )


def _safety_check() -> PromptBundle:
    return PromptBundle(
        id="safety_check",
        version="v1",
        description="Constitutional safety review for PII / policy / professionalism.",
        temperature=0.2,
        max_tokens=640,
        template=(
            "You are a SAFETY and POLICY reviewer.\n"
            "You will evaluate a drafted resume section for safety risks.\n\n"
            "Safety check (JSON):\n{check_json}\n\n"
            "Draft (JSON):\n{draft_json}\n\n"
            "QA results (JSON):\n{qa_json}\n\n"
            "Job (JSON):\n{job_json}\n\n"
            "Resume (JSON):\n{resume_json}\n\n"
            "Consider:\n"
            "  - PII leakage (if category == 'pii')\n"
            "  - Harmful/disallowed content (if category == 'policy')\n"
            "  - Professionalism (if category == 'professionalism')\n\n"
            "OUTPUT FORMAT (JSON ONLY):\n"
            "{\n"
            '  "category": "<repeat the category string from check>",\n'
            '  "blocking": true or false,\n'
            '  "reason": "short explanation"\n'
            "}\n"
            "No extra commentary.\n"
        ),
    )


# =============================================================================
# Default Registry Builder
# =============================================================================

def build_default_prompt_registry() -> PromptRegistry:
    """
    Build a PromptRegistry pre-populated with the v10_10 prompt set.
    """
    bundles = [
        _strategy_generate_branch(),
        _strategy_select_branch(),
        _drafting_structure(),
        _drafting_narrative(),
        _drafting_compliance(),
        _qa_semantic_check(),
        _safety_check(),
    ]
    return PromptRegistry(bundles=bundles)
