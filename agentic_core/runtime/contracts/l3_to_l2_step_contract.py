"""L3ToL2StepContract — W5 generic managed-workflow step handoff.

Plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 W5

This contract is emitted by the L3 ManagedWorkflowRunner for every executable
node in the workflow DAG. L2 consumes one per node, executes (or stubs) it, and
returns a SealedSectionArtifact.

Scope invariants (non-negotiable):
  - This contract is purely declarative.
  - No provider/model names are hardcoded in core fields.
  - No apps_rg-specific section names are hardcoded in core fields.
  - No L4 write handles.
  - No X3 emission.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class L3ToL2StepContract:
    """Handoff from L3 orchestration to L2 execution for a single DAG node.

    Immutable — frozen dataclass.  All fields have defaults so that tests and
    stubs can construct minimal instances without boilerplate.
    """

    # ── Identity ──────────────────────────────────────────────────────────────
    contract_id: str = ""
    route_contract_ref: str = ""          # RouteContract.request_id or serialised ref
    workflow_ref: str = ""                # e.g. "wfm::apps_rg::resume_generation::v1"
    workflow_manifest_ref: str = ""       # canonical manifest ref
    workflow_id: str = ""                 # short workflow id
    node_id: str = ""                     # e.g. "header_block"
    node_type: str = ""                   # ingestion | analysis | generation | validation | guardrail | render
    node_attempt: int = 1                 # retry counter; 1 = first attempt

    # ── DAG provenance ────────────────────────────────────────────────────────
    parent_node_refs: tuple[str, ...] = field(default_factory=tuple)
    dependency_refs: tuple[str, ...] = field(default_factory=tuple)  # completed predecessor node_ids
    branch_join_state: str = ""           # empty | BRANCH | JOIN
    checkpoint_ref: str = ""             # opaque ref to DAG execution checkpoint
    workflow_ledger_ref: str = ""         # opaque ref to L3 internal ledger entry

    # ── Step inputs ───────────────────────────────────────────────────────────
    step_input_refs: tuple[str, ...] = field(default_factory=tuple)    # upstream SealedSectionArtifact refs
    carried_evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    carried_prompt_refs: tuple[str, ...] = field(default_factory=tuple)

    # ── Execution constraints ─────────────────────────────────────────────────
    capability_token: str = ""            # opaque capability token
    sandbox_envelope: str = ""           # serialised sandbox spec
    side_effect_class: str = "none"       # none | read_only | write_permitted
    allowed_execution_lane: str = "ENSEMBLE_MODEL"
    tool_allowlist: tuple[str, ...] = field(default_factory=tuple)
    model_allowlist: tuple[str, ...] = field(default_factory=tuple)
    provider_allowlist: tuple[str, ...] = field(default_factory=tuple)
    filesystem_scope: str = ""
    network_scope: str = ""
    credential_scope: str = ""

    # ── Budget / policy ───────────────────────────────────────────────────────
    budget: str = ""                      # serialised budget spec (tokens/cost/time)
    retry_policy: str = ""               # serialised retry policy
    heal_policy_ref: str = ""            # pointer to heal policy YAML/JSON
    exit_condition: str = ""             # serialised exit condition

    # ── Replay / tracing ─────────────────────────────────────────────────────
    replay_key: str = ""
    run_id: str = ""
    trace_root: str = ""

    # ── Handoff receipts ─────────────────────────────────────────────────────
    step_handoff_receipt: str = ""       # serialised receipt from L3 emitting this contract

    # ── W6: Ensemble execution parameters ────────────────────────────────────
    provider_profile_ref: str = ""        # registry key, not hardcoded name
    candidate_count: int = 3              # how many candidates to generate
    prompt_profile_ref: str = ""          # compiled prompt artifact ref
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    output_schema_ref: str = ""           # target output schema ref

    # ── W7: Managed prompt artifact fields ───────────────────────────────────
    prompt_artifact_ref: str = ""         # as_prompt_ref() from ManagedPromptArtifact
    prompt_artifact_digest: str = ""      # prompt_digest from ManagedPromptArtifact
    prompt_bom_ref: str = ""              # bom_id from prompt_bom.yaml
    prompt_registry_ref: str = ""         # registry_id from prompt_registry.yaml
    section_prompt_ref: str = ""          # prompt_id from section_prompts/<node>.yaml
    authority_order: tuple[str, ...] = field(default_factory=tuple)  # e.g. ("S0","D0","I0",...)
    pa_is_valid: bool = True              # False when PA resolver returned invalid artifact
    pa_failure_reason: str = ""           # populated when pa_is_valid=False

    # ── Runtime gate refs (UNKNOWN when harness not wired) ────────────────────
    runtime_gate_refs: tuple[str, ...] = field(default_factory=tuple)

    schema_version: str = "W7.a3f7e2"

    def as_dict(self) -> dict:
        return {
            "contract_id": self.contract_id,
            "route_contract_ref": self.route_contract_ref,
            "workflow_ref": self.workflow_ref,
            "workflow_manifest_ref": self.workflow_manifest_ref,
            "workflow_id": self.workflow_id,
            "node_id": self.node_id,
            "node_type": self.node_type,
            "node_attempt": self.node_attempt,
            "parent_node_refs": list(self.parent_node_refs),
            "dependency_refs": list(self.dependency_refs),
            "branch_join_state": self.branch_join_state,
            "checkpoint_ref": self.checkpoint_ref,
            "workflow_ledger_ref": self.workflow_ledger_ref,
            "step_input_refs": list(self.step_input_refs),
            "carried_evidence_refs": list(self.carried_evidence_refs),
            "carried_prompt_refs": list(self.carried_prompt_refs),
            "capability_token": self.capability_token,
            "sandbox_envelope": self.sandbox_envelope,
            "side_effect_class": self.side_effect_class,
            "allowed_execution_lane": self.allowed_execution_lane,
            "tool_allowlist": list(self.tool_allowlist),
            "model_allowlist": list(self.model_allowlist),
            "provider_allowlist": list(self.provider_allowlist),
            "filesystem_scope": self.filesystem_scope,
            "network_scope": self.network_scope,
            "credential_scope": self.credential_scope,
            "budget": self.budget,
            "retry_policy": self.retry_policy,
            "heal_policy_ref": self.heal_policy_ref,
            "exit_condition": self.exit_condition,
            "replay_key": self.replay_key,
            "run_id": self.run_id,
            "trace_root": self.trace_root,
            "step_handoff_receipt": self.step_handoff_receipt,
            "provider_profile_ref": self.provider_profile_ref,
            "candidate_count": self.candidate_count,
            "prompt_profile_ref": self.prompt_profile_ref,
            "evidence_refs": list(self.evidence_refs),
            "output_schema_ref": self.output_schema_ref,
            "prompt_artifact_ref": self.prompt_artifact_ref,
            "prompt_artifact_digest": self.prompt_artifact_digest,
            "prompt_bom_ref": self.prompt_bom_ref,
            "prompt_registry_ref": self.prompt_registry_ref,
            "section_prompt_ref": self.section_prompt_ref,
            "authority_order": list(self.authority_order),
            "pa_is_valid": self.pa_is_valid,
            "pa_failure_reason": self.pa_failure_reason,
            "runtime_gate_refs": list(self.runtime_gate_refs),
            "schema_version": self.schema_version,
        }

    def as_json(self) -> str:
        return json.dumps(self.as_dict(), separators=(",", ":"))


__all__ = ["L3ToL2StepContract"]
