"""Slot mapper for apps_rg prompt assembly.

Maps input data into canonical PA slots with fencing for untrusted content.

Slot contract:
  S0: governance/system refs only (injected by compiler, never from user data)
  I0: selected prompt template instructions
  C0: JD data, master resume data, company brief data, claim/source refs
  U0: neutralized user task / intent ref
  R0: output schema and provenance requirements

No untrusted content may enter S0 or overwrite I0.
"""

from __future__ import annotations

import hashlib
from typing import Any

from apps_rg.prompt_assembly.contracts import (
    AppsRgPromptRequest,
    PromptSlotReceipt,
)

_FENCE_OPEN = "<untrusted_data>"
_FENCE_CLOSE = "</untrusted_data>"


def _fence(data: str) -> str:
    """Wrap untrusted data in fence markers."""
    if not data:
        return ""
    return f"{_FENCE_OPEN}\n{data}\n{_FENCE_CLOSE}"


def _hash_content(content: str) -> str:
    """Compute SHA-256 hash prefix of content."""
    return hashlib.sha256(content.encode("utf-8", errors="replace")).hexdigest()[:16]


def map_slots(
    request: AppsRgPromptRequest,
    template_body: str,
    governance_block: str = "",
    output_schema_block: str = "",
) -> tuple[dict[str, str], list[PromptSlotReceipt]]:
    """Map request data into PA slots and return (slots_dict, receipts).

    Args:
        request: The prompt request with all input data.
        template_body: The loaded template text (I0).
        governance_block: System governance text (S0).
        output_schema_block: Output schema/provenance requirements (R0).

    Returns:
        Tuple of (slot_values_dict, list_of_slot_receipts).
    """
    receipts: list[PromptSlotReceipt] = []

    # S0 — governance/system (trusted, never from user)
    s0 = governance_block or "System governance: apps_rg PA-governed model call."
    receipts.append(PromptSlotReceipt(
        slot_name="S0",
        source="governance",
        char_count=len(s0),
        was_fenced=False,
        validation_passed=True,
    ))

    # I0 — template instructions (trusted, loaded from BOM-referenced template)
    i0 = template_body
    receipts.append(PromptSlotReceipt(
        slot_name="I0",
        source="prompt_template",
        char_count=len(i0),
        was_fenced=False,
        validation_passed=True,
    ))

    # C0 — evidence context (untrusted, fenced)
    c0_jd = _fence(request.jd_data)
    receipts.append(PromptSlotReceipt(
        slot_name="C0_jd",
        source="jd_data",
        char_count=len(request.jd_data),
        was_fenced=True,
        validation_passed=True,
    ))

    c0_resume = _fence(request.master_resume_data)
    receipts.append(PromptSlotReceipt(
        slot_name="C0_resume",
        source="master_resume_data",
        char_count=len(request.master_resume_data),
        was_fenced=True,
        validation_passed=True,
    ))

    c0_brief = _fence(request.company_brief_data)
    receipts.append(PromptSlotReceipt(
        slot_name="C0_brief",
        source="company_brief_data",
        char_count=len(request.company_brief_data),
        was_fenced=True,
        validation_passed=True,
    ))

    c0_refs = _fence(request.claim_source_refs)
    receipts.append(PromptSlotReceipt(
        slot_name="C0_refs",
        source="claim_source_refs",
        char_count=len(request.claim_source_refs),
        was_fenced=True,
        validation_passed=True,
    ))

    # U0 — user intent (untrusted, fenced)
    u0 = _fence(request.user_task)
    receipts.append(PromptSlotReceipt(
        slot_name="U0",
        source="user_task",
        char_count=len(request.user_task),
        was_fenced=True,
        validation_passed=True,
    ))

    # R0 — output schema (trusted)
    r0 = output_schema_block or "Output: generated_resume.json conforming to resume schema."
    receipts.append(PromptSlotReceipt(
        slot_name="R0",
        source="output_schema",
        char_count=len(r0),
        was_fenced=False,
        validation_passed=True,
    ))

    slots = {
        "S0_GOVERNANCE": s0,
        "I0_INSTRUCTIONS": i0,
        "C0_JD_DATA": c0_jd,
        "C0_MASTER_RESUME_DATA": c0_resume,
        "C0_COMPANY_BRIEF_DATA": c0_brief,
        "C0_CLAIM_SOURCE_REFS": c0_refs,
        "U0_USER_TASK": u0,
        "R0_OUTPUT_SCHEMA": r0,
    }

    return slots, receipts


def render_template(template_body: str, slots: dict[str, str]) -> str:
    """Render a template by substituting ``{{SLOT_NAME}}`` placeholders.

    Only replaces known slot keys.  Unknown placeholders are left as-is.
    """
    rendered = template_body
    for key, value in slots.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered


def validate_slot_isolation(slots: dict[str, str]) -> list[str]:
    """Validate that untrusted data did not leak into S0 or I0.

    Returns a list of violation descriptions (empty = pass).
    """
    violations: list[str] = []

    s0 = slots.get("S0_GOVERNANCE", "")
    if _FENCE_OPEN in s0:
        violations.append("S0_GOVERNANCE contains fenced (untrusted) data")

    i0 = slots.get("I0_INSTRUCTIONS", "")
    if _FENCE_OPEN in i0:
        violations.append("I0_INSTRUCTIONS contains fenced (untrusted) data")

    return violations


__all__ = [
    "map_slots",
    "render_template",
    "validate_slot_isolation",
]
