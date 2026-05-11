"""ManagedPromptArtifact — W7 Prompt Assembly contract for managed workflow nodes.

Plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 W7

This contract is emitted by ManagedWorkflowPAResolver and consumed by:
  - ManagedWorkflowRunner (attaches refs into L3ToL2StepContract.carried_prompt_refs)
  - EnsembleModelLane (reads prompt refs for generator context)

Design invariants:
  - No compiled prompt text — only refs, digests, authority order, and boundary metadata.
  - app_id and prompt_profile_ref are the only app-specific fields.
  - All data-boundary decisions are encoded in data_boundary_classes (data-only, not
    instruction-authority content).
  - Missing required template or output schema → artifact.is_valid=False (fail-closed).
  - No provider names. No model names. No L4 writes. No X3.
  - Does not import apps_rg.prompt_assembly.rg_pa_compiler.
  - Does not import apps_rg.prompt_assembly.contracts.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


# ── Sentinel constants ────────────────────────────────────────────────────────

PROMPT_REF_UNKNOWN = "PROMPT_REF::UNKNOWN::NOT_RESOLVED"
DATA_BOUNDARY_DATA_ONLY = "DATA_ONLY"
DATA_BOUNDARY_INSTRUCTION = "INSTRUCTION"


@dataclass(frozen=True)
class PromptComponentHash:
    """SHA-256 digest over one contributing config component."""

    component_id: str       # e.g. "prompt_bom", "prompt_registry", "section_prompt::header_block"
    digest: str             # sha256 hex
    source_path: str = ""   # repo-relative path, empty if resolved from inline


@dataclass(frozen=True)
class ManagedPromptArtifact:
    """Lightweight prompt artifact for managed workflow node execution.

    Carries refs, digests, authority order, boundary classifications, and
    output schema binding.  Does NOT carry compiled prompt text — text
    compilation happens at L2 execution time from these refs.

    Invariants
    ----------
    - prompt_profile_ref: registry key from apps_rg/config/domain_contract/prompt_profiles.yaml
    - prompt_bom_ref:     ref to apps_rg/prompt_assembly/prompt_bom.yaml
    - prompt_registry_ref: ref to apps_rg/prompt_assembly/prompt_registry.yaml
    - section_prompt_ref: ref to apps_rg/config/section_prompts/<node_id>.yaml
    - authority_order:    canonical slot order from BOM (e.g. ["S0","D0","I0","E0","C0","M0","U0","H0","R0"])
    - output_schema_ref:  bound from section prompt / profile (R0 authority)
    - data_boundary_classes: maps slot → DATA_ONLY | INSTRUCTION for boundary enforcement
    - component_hashes:   per-component sha256 for replay/audit
    - prompt_digest:      sha256 over canonical artifact fields (for provenance chain)
    - is_valid:           False when required template or output_schema_ref is missing
    - failure_reason:     populated when is_valid=False
    - runtime_gate_refs:  UNKNOWN when harness not wired (inherited from W6)
    """

    # ── Identity ──────────────────────────────────────────────────────────────
    artifact_id: str = ""
    request_id: str = ""
    run_id: str = ""
    trace_root: str = ""
    app_context: str = ""          # e.g. "apps_rg"
    task_class: str = ""           # e.g. "resume_generation"

    # ── DAG / workflow provenance ─────────────────────────────────────────────
    workflow_ref: str = ""
    node_id: str = ""

    # ── Profile / BOM / registry refs ─────────────────────────────────────────
    prompt_profile_ref: str = ""   # e.g. "app::apps_rg::resume_generation::v1"
    prompt_bom_ref: str = ""       # e.g. "bom::apps_rg::v1"
    prompt_registry_ref: str = ""  # e.g. "reg::apps_rg::v1"
    section_prompt_ref: str = ""   # e.g. "sp::apps_rg::header_block::v1"

    # ── Authority / boundary ──────────────────────────────────────────────────
    authority_order: tuple[str, ...] = field(default_factory=tuple)
    # slot_code -> DATA_ONLY | INSTRUCTION
    data_boundary_classes: dict[str, str] = field(default_factory=dict)
    slots_required: tuple[str, ...] = field(default_factory=tuple)
    slots_optional: tuple[str, ...] = field(default_factory=tuple)

    # ── Output schema binding (R0 authority) ──────────────────────────────────
    output_schema_ref: str = ""    # e.g. "aos::apps_rg::resume_generation::v1#header_block"
    tool_schema_refs: tuple[str, ...] = field(default_factory=tuple)

    # ── Prompt injection neutralization records ───────────────────────────────
    # Each entry records a detected injection attempt that was blocked:
    # "slot:<slot_code>:blocked:<reason>"
    injection_block_records: tuple[str, ...] = field(default_factory=tuple)
    # Whether any injection was detected (summarizes injection_block_records)
    injection_detected: bool = False

    # ── Provenance / replay ───────────────────────────────────────────────────
    component_hashes: tuple[PromptComponentHash, ...] = field(default_factory=tuple)
    prompt_digest: str = ""        # sha256 over canonical fields
    replay_key: str = ""
    policy_hash: str = ""
    blueprint_hash: str = ""
    created_at: str = ""

    # ── Validity ──────────────────────────────────────────────────────────────
    is_valid: bool = True
    failure_reason: str = ""

    # ── Runtime gate refs (UNKNOWN when harness not wired) ────────────────────
    runtime_gate_refs: tuple[str, ...] = field(default_factory=tuple)

    schema_version: str = "W7.a3f7e2"

    def compute_digest(self) -> str:
        """Compute sha256 over canonical identity + ref fields."""
        payload = {
            "artifact_id": self.artifact_id,
            "request_id": self.request_id,
            "run_id": self.run_id,
            "workflow_ref": self.workflow_ref,
            "node_id": self.node_id,
            "prompt_profile_ref": self.prompt_profile_ref,
            "prompt_bom_ref": self.prompt_bom_ref,
            "prompt_registry_ref": self.prompt_registry_ref,
            "section_prompt_ref": self.section_prompt_ref,
            "authority_order": list(self.authority_order),
            "output_schema_ref": self.output_schema_ref,
            "policy_hash": self.policy_hash,
            "schema_version": self.schema_version,
        }
        blob = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def as_prompt_ref(self) -> str:
        """Return a single opaque prompt ref string for L3ToL2StepContract.carried_prompt_refs."""
        return (
            f"prompt::{self.app_context}::{self.node_id}"
            f"::{self.prompt_profile_ref}::{self.prompt_digest[:16]}"
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "request_id": self.request_id,
            "run_id": self.run_id,
            "trace_root": self.trace_root,
            "app_context": self.app_context,
            "task_class": self.task_class,
            "workflow_ref": self.workflow_ref,
            "node_id": self.node_id,
            "prompt_profile_ref": self.prompt_profile_ref,
            "prompt_bom_ref": self.prompt_bom_ref,
            "prompt_registry_ref": self.prompt_registry_ref,
            "section_prompt_ref": self.section_prompt_ref,
            "authority_order": list(self.authority_order),
            "data_boundary_classes": dict(self.data_boundary_classes),
            "slots_required": list(self.slots_required),
            "slots_optional": list(self.slots_optional),
            "output_schema_ref": self.output_schema_ref,
            "tool_schema_refs": list(self.tool_schema_refs),
            "injection_block_records": list(self.injection_block_records),
            "injection_detected": self.injection_detected,
            "component_hashes": [
                {"component_id": h.component_id, "digest": h.digest, "source_path": h.source_path}
                for h in self.component_hashes
            ],
            "prompt_digest": self.prompt_digest,
            "replay_key": self.replay_key,
            "policy_hash": self.policy_hash,
            "blueprint_hash": self.blueprint_hash,
            "created_at": self.created_at,
            "is_valid": self.is_valid,
            "failure_reason": self.failure_reason,
            "runtime_gate_refs": list(self.runtime_gate_refs),
            "schema_version": self.schema_version,
        }

    def as_json(self) -> str:
        return json.dumps(self.as_dict(), separators=(",", ":"))


__all__ = [
    "ManagedPromptArtifact",
    "PromptComponentHash",
    "PROMPT_REF_UNKNOWN",
    "DATA_BOUNDARY_DATA_ONLY",
    "DATA_BOUNDARY_INSTRUCTION",
]
