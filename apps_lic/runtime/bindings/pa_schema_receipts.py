"""Prompt Assembly schema receipts for apps_lic.

The PA binding uses this module to keep model-facing output contract text and
runtime receipt hashes aligned with the YAML SSOT files from W1/W2.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml


APPS_LIC_ROOT = Path(__file__).resolve().parents[2]
DOMAIN_CONTRACT_DIR = APPS_LIC_ROOT / "config" / "domain_contract"
PROMPT_ASSEMBLY_DIR = APPS_LIC_ROOT / "prompt_assembly"

SLOT_REGISTRY_PATH = DOMAIN_CONTRACT_DIR / "prompt_slot_registry.v1.yaml"
PROMPT_REGISTRY_PATH = APPS_LIC_ROOT / "config" / "prompt_registry.yaml"
PROMPT_BOM_PATH = PROMPT_ASSEMBLY_DIR / "prompt_bom.yaml"
OUTPUT_SCHEMA_PATH = DOMAIN_CONTRACT_DIR / "output_schema.yaml"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _compact_json(value: Mapping[str, Any]) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )


@dataclass(frozen=True, slots=True)
class PromptSchemaReceipt:
    slot_registry_ref: str
    slot_registry_hash: str
    prompt_registry_hash: str
    prompt_bom_hash: str
    output_schema_hash: str
    output_contract_name: str
    output_contract_fields: tuple[str, ...]
    forbidden_output_fields: tuple[str, ...]
    json_contract: str

    def to_hash_payload(self) -> dict[str, Any]:
        return {
            "slot_registry_ref": self.slot_registry_ref,
            "slot_registry_hash": self.slot_registry_hash,
            "prompt_registry_hash": self.prompt_registry_hash,
            "prompt_bom_hash": self.prompt_bom_hash,
            "output_schema_hash": self.output_schema_hash,
            "output_contract_name": self.output_contract_name,
            "output_contract_fields": list(self.output_contract_fields),
            "forbidden_output_fields": list(self.forbidden_output_fields),
        }


def build_prompt_schema_receipt(
    *,
    channel: str,
    recipient_class: str,
    subject_required: bool,
    hard_cap_chars: int,
    max_sentences: int,
) -> PromptSchemaReceipt:
    """Build the PA receipt and JSON contract from the output schema SSOT."""

    prompt_registry = _load_yaml(PROMPT_REGISTRY_PATH)
    output_schema = _load_yaml(OUTPUT_SCHEMA_PATH)
    generation_contract = output_schema["generation_contract"]
    required_fields = tuple(str(field) for field in generation_contract["required_fields"])
    forbidden_fields = tuple(str(field) for field in generation_contract["forbidden_fields"])

    contract_payload: dict[str, Any] = {
        "contract": generation_contract["name"],
        "channel": channel,
        "recipient_class": recipient_class.lower(),
        "subject": "..." if subject_required else "",
        "message_body": "...",
        "relationship_posture": "...",
        "intended_next_step": "...",
        "claims_used": [],
        "unsupported_claims": [],
        "omitted_claims": [],
        "personalization_confidence": 0.0,
        "tone_risk_flags": [],
        "hitl_questions": [],
        "signature_block": "Amit" if subject_required else "",
        "metadata": {
            "status": "draft_candidate",
            "output_schema_hash": _sha256_file(OUTPUT_SCHEMA_PATH),
        },
        "send_mode": "draft_only",
        "candidates": [
            {
                "candidate_id": "...",
                "subject": "..." if subject_required else "",
                "message_body": "...",
                "claims_used": [],
                "model_call_ref": "...",
                "provider_receipt": "...",
            }
        ],
    }

    return PromptSchemaReceipt(
        slot_registry_ref=str(prompt_registry["slot_registry_ref"]),
        slot_registry_hash=_sha256_file(SLOT_REGISTRY_PATH),
        prompt_registry_hash=_sha256_file(PROMPT_REGISTRY_PATH),
        prompt_bom_hash=_sha256_file(PROMPT_BOM_PATH),
        output_schema_hash=_sha256_file(OUTPUT_SCHEMA_PATH),
        output_contract_name=str(generation_contract["name"]),
        output_contract_fields=required_fields,
        forbidden_output_fields=forbidden_fields,
        json_contract=_compact_json(contract_payload),
    )


def output_contract_guidance(
    *,
    receipt: PromptSchemaReceipt,
    subject_required: bool,
    hard_cap_chars: int,
    max_sentences: int,
) -> list[str]:
    """Return model-facing output guidance derived from the schema receipt."""

    subject_rule = (
        "subject is required and must be non-empty for this channel."
        if subject_required
        else "subject must be an empty string for this channel."
    )
    signature_rule = (
        "signature_block is required and must identify Amit."
        if subject_required
        else "signature_block is optional for this channel."
    )
    return [
        f"  Produce JSON only: {receipt.json_contract}.",
        f"  Output contract: {receipt.output_contract_name}.",
        f"  {subject_rule}",
        f"  {signature_rule}",
        (
            "  message_body must be "
            f"{hard_cap_chars} characters or fewer and {max_sentences} sentences or fewer."
        ),
        "  Channel-specific policy: linkedin_inmail requires subject and signature; linkedin_chat requires empty subject and a body under 300 characters.",
        "  Do not infer channel from length. Use the explicit channel input.",
        "  Provider and model identifiers are runtime routing metadata only; do not include them as output fields.",
    ]


__all__ = [
    "PromptSchemaReceipt",
    "build_prompt_schema_receipt",
    "output_contract_guidance",
]
