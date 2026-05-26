"""Shared PA helpers for Unify/IBM W7 mechanical migration (strategic_tailor_v1 shell)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


def pa_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        marker = (
            parent
            / "apps_rg"
            / "prompt_assembly"
            / "templates"
            / "w7_strategic_tailor_shell_slots.yaml"
        )
        if marker.is_file():
            return parent
    raise FileNotFoundError("Cannot resolve repo root (w7_strategic_tailor_shell_slots.yaml missing)")


SHELL_PATH = pa_repo_root() / "apps_rg/prompt_assembly/templates/w7_strategic_tailor_shell_slots.yaml"


def load_w7_shell_slot_bodies() -> dict[str, str]:
    raw = yaml.safe_load(SHELL_PATH.read_text(encoding="utf-8"))
    bodies = raw.get("slot_bodies") or {}
    return {str(k): str(v) for k, v in bodies.items() if isinstance(v, str)}


def jd_non_proof_block(payload: dict[str, Any]) -> str:
    return (
        f"Target title (context only): {payload['target_title']}\n"
        f"Target company (context only): {payload['target_company']}\n"
        f"JD (context only): {payload['jd_text']}\n"
        f"Briefing (context only): {payload['briefing']}\n\n"
        "These lines are targeting context only — not proof of candidate experience."
    )


NARRATIVE_JD_ALIGNMENT_SCHEMA = {
    "type": "object",
    "required": [
        "selected_jd_themes",
        "selected_briefing_themes",
        "targeting_rationale",
        "jd_used_as_proof",
        "briefing_used_as_proof",
    ],
    "properties": {
        "selected_jd_themes": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string"},
        },
        "selected_briefing_themes": {"type": "array", "items": {"type": "string"}},
        "targeting_rationale": {"type": "string", "minLength": 1},
        "jd_used_as_proof": {"type": "boolean"},
        "briefing_used_as_proof": {"type": "boolean"},
        "targeting_only": {"type": "boolean"},
    },
}

NARRATIVE_R0 = json.dumps(
    {
        "type": "object",
        "required": [
            "narrative_sentence",
            "selected_fact_plan",
            "claim_ledger",
            "jd_alignment",
            "gap_notes",
            "change_log",
            "self_check",
        ],
        "properties": {
            "narrative_sentence": {"type": "string"},
            "selected_fact_plan": {"type": "object"},
            "claim_ledger": {
                "type": "array",
                "description": (
                    "Each row: non-empty claim_text and source_fact_ids from ALLOWED_SOURCE_FACT_IDS. "
                    "Gate x2_claim_ledger_claim_text_non_empty."
                ),
                "items": {
                    "type": "object",
                    "required": ["claim_text", "source_fact_ids"],
                    "properties": {
                        "claim_text": {"type": "string", "minLength": 1},
                        "claim": {
                            "type": "string",
                            "description": "Legacy alias normalized to claim_text upstream.",
                        },
                        "source_fact_ids": {
                            "type": "array",
                            "minItems": 1,
                            "items": {"type": "string"},
                        },
                    },
                },
            },
            "jd_alignment": NARRATIVE_JD_ALIGNMENT_SCHEMA,
            "gap_notes": {"type": "array"},
            "change_log": {"type": "array"},
            "self_check": {"type": "object"},
        },
    },
    sort_keys=True,
)

BULLETS_R0 = json.dumps(
    {
        "type": "object",
        "required": [
            "bullets",
            "selected_fact_plan",
            "claim_ledger",
            "jd_alignment",
            "gap_notes",
            "change_log",
            "self_check",
        ],
        "properties": {
            "bullets": {
                "type": "array",
                "description": "Optional bullet_theme per item carries taxonomy; never prefix bullet_text.",
                "items": {
                    "type": "object",
                    "properties": {
                        "bullet_theme": {
                            "type": "string",
                            "description": "Optional taxonomy/theme label — not copied into bullet_text prefix.",
                        },
                    },
                },
            },
            "selected_fact_plan": {"type": "object"},
            "claim_ledger": {
                "type": "array",
                "description": (
                    "Each row must include non-empty claim_text and source_fact_ids copied exactly "
                    "from ALLOWED_SOURCE_FACT_IDS. Missing/empty/null/whitespace-only claim_text fails "
                    "deterministic gate x2_claim_ledger_claim_text_non_empty."
                ),
                "items": {
                    "type": "object",
                    "required": ["claim_text", "source_fact_ids"],
                    "properties": {
                        "claim_text": {
                            "type": "string",
                            "minLength": 1,
                            "description": "Non-empty material claim prose; whitespace-only invalid.",
                        },
                        "claim": {
                            "type": "string",
                            "description": "Legacy alias normalized to claim_text upstream when present.",
                        },
                        "source_fact_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 1,
                        },
                    },
                },
            },
            "jd_alignment": {"type": "object"},
            "gap_notes": {"type": "array"},
            "change_log": {"type": "array"},
            "self_check": {"type": "object"},
        },
    },
    sort_keys=True,
)

__all__ = [
    "BULLETS_R0",
    "NARRATIVE_JD_ALIGNMENT_SCHEMA",
    "NARRATIVE_R0",
    "SHELL_PATH",
    "jd_non_proof_block",
    "load_w7_shell_slot_bodies",
    "pa_repo_root",
]
