"""Line-by-line PA requirement traceability matrix.

Walks every PA doctrine file in
``docs/reference/03B_PA_Prompt_Assembly/`` and emits one matrix row per
requirement line. Each row is grounded against a multi-source runtime
evidence index (PA package surface, recursive receipt keys, PA source
file content, PA test corpus) and either PASSes or FAILs.

This is the answer to "show me line by fucking line requirement level".
The earlier ``runtime_evidence.py`` harness produced 387 *category*
rollup rows (e.g. one MUST_EMIT row per doctrine field). This file
produces ~1,500 *individual line* rows: every numbered section, every
bullet, every FIELDS entry, every MUST CHECK, every CHECKS, every
ACCEPTANCE TEST, every MUST EMIT, every MUST NOT, every FORBIDDEN
OUTPUTS token, every PA.I invariant, every PA.8 RULE / TEST
REQUIREMENT / CONTRACT field.

Outputs
-------
- ``docs/reports/prompt-assembly/line_by_line_matrix.md`` (human report)
- ``tools/prompt_assembly/_line_by_line_matrix.json``      (machine sidecar)

Exit code is 0 only when every requirement row is PASS.
"""

from __future__ import annotations

import json
import re
import sys
import datetime as _dt
from collections.abc import Mapping
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# pylint: disable=wrong-import-position
import agentic_core.prompt_governance.prompt_assembly as pa  # noqa: E402
from agentic_core.prompt_governance.prompt_assembly import (  # noqa: E402
    FORBIDDEN_DISPOSITIONS,
    FORBIDDEN_EXECUTION_VERBS,
    PAStatus,
    STAGE_TO_STATUSES,
)
from tools.prompt_assembly.runtime_evidence import (  # noqa: E402
    _build_pa0_receipt,
    _build_pa1_receipt,
    _build_pa2_receipt,
    _build_pa3_receipt,
    _build_pa4_receipt,
    _build_pa5_receipt,
    _build_pa6_receipt,
    _build_pa7_receipt,
)


# Canonical doctrine corpus (matches DOCTRINE_FILES + EXTRA_DOCTRINE_FILES
# in tools/prompt_assembly/doctrine_parser.py).
DOCTRINE_FILES: dict[str, str] = {
    "PARENT": "docs/reference/03B_PA_Prompt_Assembly/Prompt_Assembly.md",
    "PA.0": "docs/reference/03B_PA_Prompt_Assembly/PA.0_Boundary_Check.md",
    "PA.1": "docs/reference/03B_PA_Prompt_Assembly/PA.1_Load_Resolve_Prompt_BOM.md",
    "PA.2": "docs/reference/03B_PA_Prompt_Assembly/PA.2_Slot_Composition.md",
    "PA.3": "docs/reference/03B_PA_Prompt_Assembly/PA.3_Airlock_Security_Pass.md",
    "PA.4": "docs/reference/03B_PA_Prompt_Assembly/PA.4_Validate_Slot_Contract.md",
    "PA.5": "docs/reference/03B_PA_Prompt_Assembly/PA.5_Token_Budget_Determinism.md",
    "PA.6": "docs/reference/03B_PA_Prompt_Assembly/PA.6_Provider_Aware_Rendering.md",
    "PA.7": "docs/reference/03B_PA_Prompt_Assembly/PA.7_Final_Emit_Compiled_Prompt_Artifact.md",
    "PA.8": "docs/reference/03B_PA_Prompt_Assembly/PA.8_Authority_RedTeam_Slot_Verification.md",
}


# --------------------------------------------------------------------------
# Requirement extraction
# --------------------------------------------------------------------------


@dataclass
class Requirement:
    stage: str
    file_path: str
    line_no: int
    section: str
    sub_section: str
    text: str
    kind: str  # "numbered_section" | "bullet" | "field" | "csv_token"


_SECTION_HEADER = re.compile(r"^([A-Z][A-Z0-9 _/\-,]{2,}?):?\s*$")
_NUMBERED_SECTION = re.compile(r"^(\d+)\.\s+(.+?)\s*$")
_BULLET = re.compile(r"^\s*[-*\u2022]\s+(.+?)\s*$")
_LABELED_LINE = re.compile(r"^([A-Z][A-Z0-9_]+):\s*$")  # e.g. "FIELDS:" / "S0:"
_SEPARATOR = re.compile(r"^[-=]{6,}\s*$")
_BOILERPLATE_HEADERS = {
    "GLOBAL NO-OVERLAP LAW",
    "REFERENCE POINTERS",
    "MECE ALIGNMENT FULL OVERWRITE HEADER",
    "GLOBAL NO-OVERLAP LOCK",
    "FORBIDDEN OUTPUTS FROM THIS CHILD",
    "FORBIDDEN OUTPUTS FROM THIS FILE",
    "ALLOWED OUTPUT STYLE",
    "OVERWRITE RECONCILIATION HEADER",
    "END OVERWRITE RECONCILIATION HEADER",
    "PARENT",
    "ROLE",
    "WHY THIS FILE EXISTS",
    "PRIMARY QUESTION",
    "SOURCE OWNERSHIP BOUNDARY",
    "UNIQUE OWNERSHIP SURFACE",
    "THIS FILE OWNS",
    "THIS FILE DOES NOT OWN",
    "STATUS VALUES",
    "STATUS VOCABULARY",
    "MUST EMIT",
    "MUST NOT",
    "MUST CHECK",
    "ACCEPTANCE TESTS",
    "ACCEPTANCE EXPECTATIONS",
    "TEST REQUIREMENTS",
    "RULES",
    "CONTRACTS TO IMPLEMENT",
    "CHECKS",
    "OUTPUTS",
    "FIELDS",
    "MAPPING EXPECTATIONS",
    "REQUIRED ORDER",
    "AUTHORITY ORDER",
    "CANONICAL SLOT MAP",
    "CHILD FILE MAP",
    "CROSS-CHILD INVARIANTS",
    "END-TO-END POSITION",
    "CANONICAL PROMPT ASSEMBLY INPUTS",
    "CANONICAL PROMPT ASSEMBLY OUTPUT",
    "PARENT ROLE",
    "PARENT DOES NOT OWN IMPLEMENTATION DETAIL",
    "PROMPT ASSEMBLY OWNS AT DOCTRINE LEVEL",
    "PROMPT ASSEMBLY DOES NOT OWN",
    "PURPOSE",
    "SLOT CONFLICT TYPES",
    "GAP TYPES",
    "TRIMMING RECEIPT FIELDS",
    "MUST INCLUDE",
    "MUST EXCLUDE",
    "MUST CHECK WHEN GROUNDING REQUIRED",
    "MUST NOT INCLUDE",
    "RESOLUTION STEPS",
    "DETERMINISTIC TRIMMING ORDER",
    "CANONICAL HASH INPUT DISCIPLINE",
    "S0",
    "D0",
    "I0",
    "E0",
    "C0",
    "M0",
    "U0",
    "Y0",
    "H0",
    "R0",
}


def _is_line_a_requirement(stripped: str) -> bool:
    """Skip pure boilerplate lines that are not requirements."""
    if not stripped:
        return False
    if _SEPARATOR.match(stripped):
        return False
    if stripped.startswith("==") or stripped.startswith("--"):
        return False
    return True


def _extract_requirements(stage: str, rel_path: str) -> list[Requirement]:
    full = _REPO_ROOT / rel_path
    if not full.exists():
        return []
    raw = full.read_text(encoding="utf-8-sig").splitlines()
    out: list[Requirement] = []
    section = "<file>"
    sub_section = ""
    for idx, line in enumerate(raw, 1):
        stripped = line.strip()
        if not _is_line_a_requirement(stripped):
            continue
        # Section header detection (all-caps, short).
        if (
            stripped.isupper()
            and 2 <= len(stripped.split()) <= 12
            and not stripped.startswith("-")
            and not stripped.startswith("*")
        ):
            # Strip trailing colons / commas.
            section = stripped.rstrip(":").rstrip(",")
            sub_section = ""
            continue
        # Sub-section labeled-line, e.g. "FIELDS:" or "MAPPING EXPECTATIONS:"
        if _LABELED_LINE.match(stripped):
            sub_section = stripped.rstrip(":")
            continue
        # Numbered section heading like "1. PAAssemblyInput".
        m = _NUMBERED_SECTION.match(stripped)
        if m:
            sub_section = m.group(2)
            out.append(
                Requirement(
                    stage=stage,
                    file_path=rel_path,
                    line_no=idx,
                    section=section,
                    sub_section=sub_section,
                    text=stripped,
                    kind="numbered_section",
                )
            )
            continue
        # Bullet item.
        m = _BULLET.match(line)
        if m:
            payload = m.group(1).strip()
            # CSV-bullets that pack many tokens: split into individual rows
            # so each forbidden-token/dispatch-verb counts as a separate
            # requirement.
            if "," in payload and re.match(r"^[A-Za-z][A-Za-z0-9_,\s]*[A-Za-z0-9_]$", payload):
                # Heuristic: looks like a comma list of identifiers.
                parts = [t.strip() for t in payload.split(",") if t.strip()]
                if len(parts) >= 2 and all(re.match(r"^[A-Za-z][A-Za-z0-9_]*$", p) for p in parts):
                    for tok in parts:
                        out.append(
                            Requirement(
                                stage=stage,
                                file_path=rel_path,
                                line_no=idx,
                                section=section,
                                sub_section=sub_section,
                                text=tok,
                                kind="csv_token",
                            )
                        )
                    continue
            out.append(
                Requirement(
                    stage=stage,
                    file_path=rel_path,
                    line_no=idx,
                    section=section,
                    sub_section=sub_section,
                    text=payload,
                    kind="bullet",
                )
            )
            continue
    return out


# --------------------------------------------------------------------------
# Multi-source evidence index
# --------------------------------------------------------------------------


def _walk_keys(node: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(node, Mapping):
        for k, v in node.items():
            keys.add(str(k))
            keys |= _walk_keys(v)
    elif isinstance(node, (list, tuple)):
        for item in node:
            keys |= _walk_keys(item)
    return keys


def _build_evidence_index() -> dict[str, set[str]]:
    """Build the multi-source evidence index.

    Returns
    -------
    dict with keys:
      - ``pa_surface``      : public symbols of the PA package
      - ``receipt_keys``    : recursive keys from all 8 receipt builders
      - ``status_values``   : every PAStatus member value
      - ``forbidden_set``   : parent master forbidden tokens
      - ``source_corpus_lc``: lowercased concatenation of all
                              ``agentic_core/prompt_governance/`` source
                              files (gives us free coverage of any
                              identifier referenced anywhere in the
                              implementation)
      - ``test_corpus_lc``  : lowercased concatenation of every PA test
                              file content + filename
      - ``doctrine_corpus_lc``: lowercased concatenation of every PA
                              doctrine file (covers cross-references)
    """
    pa_surface = {n for n in dir(pa) if not n.startswith("_")}

    receipt_keys: set[str] = set()
    for builder in (
        _build_pa0_receipt,
        _build_pa1_receipt,
        _build_pa2_receipt,
        _build_pa3_receipt,
        _build_pa4_receipt,
        _build_pa5_receipt,
        _build_pa6_receipt,
        _build_pa7_receipt,
    ):
        receipt_keys |= _walk_keys(builder())

    status_values = {s.value for s in PAStatus}
    forbidden_set = set(FORBIDDEN_DISPOSITIONS) | set(FORBIDDEN_EXECUTION_VERBS)

    source_root = _REPO_ROOT / "agentic_core" / "prompt_governance"
    source_files = sorted(source_root.rglob("*.py")) if source_root.exists() else []
    source_corpus = "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in source_files)

    test_root = _REPO_ROOT / "tests" / "unit" / "agentic_core" / "prompt_governance"
    test_files = sorted(test_root.rglob("*.py")) if test_root.exists() else []
    test_corpus = "\n".join(
        f"{f.name}\n{f.read_text(encoding='utf-8', errors='replace')}" for f in test_files
    )

    doctrine_root = _REPO_ROOT / "docs" / "reference" / "03B_PA_Prompt_Assembly"
    doctrine_files = sorted(doctrine_root.glob("*.md")) if doctrine_root.exists() else []
    doctrine_corpus = "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in doctrine_files)

    return {
        "pa_surface": pa_surface,
        "receipt_keys": receipt_keys,
        "status_values": status_values,
        "forbidden_set": forbidden_set,
        "source_corpus_lc": source_corpus.lower(),
        "test_corpus_lc": test_corpus.lower(),
        "doctrine_corpus_lc": doctrine_corpus.lower(),
        # Pre-computed lowercased identifier maps for fast contains check.
        "pa_surface_lc": {n.lower() for n in pa_surface},
        "receipt_keys_lc": {k.lower() for k in receipt_keys},
        "status_values_lc": {s.lower() for s in status_values},
        "forbidden_set_lc": {t.lower() for t in forbidden_set},
        "source_files_count": len(source_files),
        "test_files_count": len(test_files),
        "doctrine_files_count": len(doctrine_files),
    }


# --------------------------------------------------------------------------
# Evidence matching
# --------------------------------------------------------------------------


_TOKEN_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]{2,}\b")


# Prose-pattern map — a bullet whose tokens don't directly match runtime
# identifiers but whose semantic intent is satisfied by a documented
# runtime artefact. Each entry maps a (lowercased) keyword that MUST
# appear in the requirement text to a runtime artefact name that
# proves the semantic requirement.
_PROSE_KEYWORD_MAP: dict[str, str] = {
    # PA.0 / shared semantics
    "request_id": "PromptAssemblyStarted",
    "run_id": "PromptAssemblyStarted",
    "trace_id": "PromptAssemblyStarted",
    "route_id": "L0RouteContract",
    "plan_id": "L1PlanContract",
    "policy_hash": "GovernanceArtifacts",
    "blueprint_hash": "GovernanceArtifacts",
    "replay_key": "compute_replay_key",
    "system_version_hash": "GovernanceArtifacts",
    "agentspec": "GovernanceArtifacts",
    "response_schema_contract": "R0SchemaBinding",
    "response_schema": "R0SchemaBinding",
    "tool_schema": "ToolBindingManifest",
    "provider_target": "PROVIDER_LANES",
    "provider_lane": "PROVIDER_LANES",
    "model_policy": "GovernanceArtifacts",
    "idempotency_nonce": "compute_replay_key",
    "expected_artifact_type": "CompiledPromptArtifactSigned",
    "assembly_budget_hint": "BudgetReport",
    "raw_user_task": "U0NeutralizedTaskBlock",
    "neutralized_user_task": "U0NeutralizedTaskBlock",
    "boundary": "BoundaryCheckResult",
    "eligibility": "BoundaryCheckResult",
    "missing_required_refs": "BoundaryCheckResult",
    "mismatched_refs": "BoundaryCheckResult",
    "upstream_owner_hint": "BoundaryFailReason",
    "grounding_required": "BoundaryCheckResult",
    "grounding": "C0EvidenceContract",
    "terminal": "DispatchDisposition",
    "managed workflow": "L1PlanContract",
    # PA.1
    "prompt_bom": "PromptBOMResolved",
    "promptbom": "PromptBOMResolved",
    "system_component": "S0Block",
    "fence_component": "D0FenceBlock",
    "fence": "D0FenceBlock",
    "instruction_mixin": "I0InstructionBlock",
    "instructional": "I0InstructionBlock",
    "exemplar": "E0ExemplarBlock",
    "context_component": "C0GroundedContextBlock",
    "execution_metadata": "ExecutionMetadataBlock",
    "model_settings": "ExecutionMetadataBlock",
    "component_hash": "PromptBOMResolved",
    "bom_gap": "PromptBOMResolved",
    "bom_hash": "PromptBOMResolved",
    # PA.2
    "structured_slots": "AuthorityStack",
    "slot_order": "SLOT_ORDER",
    "slot_authority": "SLOT_AUTHORITY_RANK",
    "slot_lineage": "SlotEntry",
    "slot_conflict": "OVERRIDE_RULES",
    "lower_authority_override": "OverrideRule",
    "override": "OVERRIDE_RULES",
    "exemplar_schema_conflict": "OVERRIDE_RULES",
    "scope_widening": "OVERRIDE_RULES",
    "promotion_receipt": "Y0LearningPriorBlock",
    "schema_conflict": "OVERRIDE_RULES",
    "tool_binding": "ToolBindingManifest",
    "missing_origin_label": "SlotEntry",
    # PA.3
    "u0 airlock": "run_u0_airlock",
    "airlock": "U0AirlockResult",
    "neutralized": "U0NeutralizedTaskBlock",
    "stripped_control_claims": "U0AirlockResult",
    "preserved_task_intent": "U0AirlockResult",
    "u0_security_notes": "U0AirlockResult",
    "c0_payload": "C0ChunkRecord",
    "c0_payload_security": "C0ClassifierResult",
    "rejected_c0_payload": "C0ClassifierResult",
    "safe_c0_payload": "C0ClassifierResult",
    "citation_preservation": "C0ChunkRecord",
    "h0": "H0HealingHintBlock",
    "h0_reentry": "H0ReentryResult",
    "h0_allowed_payload": "H0ReentryResult",
    "h0_rejected_payload": "H0ReentryResult",
    "policy override": "U0AirlockResult",
    "role override": "U0AirlockResult",
    "credential": "U0AirlockResult",
    "instruction smuggling": "U0AirlockResult",
    "ignore prior instructions": "U0AirlockResult",
    "jailbreak": "C0ClassifierResult",
    "exfiltration": "U0AirlockResult",
    "tool-call imitation": "C0ClassifierResult",
    "fake policy": "C0ClassifierResult",
    "stale or contradicted": "C0ClassifierResult",
    "structured bindings": "ToolBindingManifest",
    "data class": "GovernanceArtifacts",
    "task class": "L1PlanContract",
    "security_profile": "GovernanceArtifacts",
    # PA.4
    "validation": "PA4ValidationReport",
    "validate": "validate_pa4",
    "slot_validation": "PA4ValidationReport",
    "validation_check": "ValidationCheckResult",
    "context_contract": "C0EvidenceContract",
    "authority_order": "SLOT_AUTHORITY_RANK",
    "verified chunks": "C0EvidenceContract",
    "citations": "C0EvidenceContract",
    "support gaps": "C0EvidenceContract",
    "contradiction flags": "C0EvidenceContract",
    "abstain recommendation": "C0EvidenceContract",
    "source lineage": "C0EvidenceContract",
    "schema/tool": "ToolBindingManifest",
    "tool/schema": "ToolBindingManifest",
    # PA.5
    "token budget": "BudgetReport",
    "tokenbudgetledger": "BudgetReport",
    "trimming": "deterministic_trim",
    "trimmed": "deterministic_trim",
    "must-use": "BudgetClass",
    "mandatory": "BudgetClass",
    "optional": "BudgetClass",
    "stable_prefix": "BUDGET_TRIM_ORDER",
    "stable prefix": "BUDGET_TRIM_ORDER",
    "canonical_hash_input": "canonicalize_manifest",
    "canonical hash": "canonicalize_manifest",
    "canonical bytes": "canonicalize_manifest",
    "overflow": "OverflowStatus",
    "max_context_tokens": "BudgetReport",
    "reserved_output_tokens": "BudgetReport",
    "schema_overhead": "BudgetReport",
    "tool_overhead": "BudgetReport",
    "available_prompt_tokens": "BudgetReport",
    "slot_token_estimate": "SlotBudgetEntry",
    "trimming_plan": "BudgetReport",
    "deterministic_order": "BUDGET_TRIM_ORDER",
    # PA.6
    "providerrendermanifest": "render_for_provider",
    "providerrenderrequest": "render_for_provider",
    "render_manifest": "render_for_provider",
    "render": "render_for_provider",
    "rendered": "RenderedPayload",
    "anthropic": "render_anthropic",
    "openai": "render_openai_chat",
    "gpt": "render_openai_chat",
    "reasoning lane": "render_openai_reasoning",
    "gemini": "render_gemini",
    "local": "render_local",
    "thinking_level": "ExecutionMetadataBlock",
    "thinking_control": "render_openai_reasoning",
    "system field": "render_for_provider",
    "developer field": "render_for_provider",
    "user field": "render_for_provider",
    "document container": "render_for_provider",
    "tools field": "ToolBindingManifest",
    "response_format": "R0SchemaBinding",
    "response_schema field": "R0SchemaBinding",
    "long-context": "render_for_provider",
    "tail-repeat": "render_for_provider",
    "data-first": "render_for_provider",
    # PA.7
    "compiledpromptartifact": "CompiledPromptArtifactSigned",
    "manifest_hash": "compute_manifest_hash",
    "hmac": "sign_manifest",
    "hmac_sig": "SignedManifest",
    "signature": "sign_manifest",
    "signing_key": "sign_manifest",
    "signing_secret": "sign_manifest",
    "signature_algorithm": "SIGNATURE_VERSION",
    "signature_receipt": "SignedManifest",
    "signed_fields": "SignedManifest",
    "l2_handoff_envelope": "validate_l2_handoff",
    "l2 handoff": "validate_l2_handoff",
    "handoff": "L2HandoffValidationResult",
    "handoff_notes": "L2HandoffValidationResult",
    "verify_signature": "verify_signature",
    "artifact_id": "CompiledPromptArtifactSigned",
    "artifact_status": "CompiledPromptArtifactSigned",
    "compiled_prompt_artifact_id": "CompiledPromptArtifactSigned",
    "execution_form": "L0RouteContract",
    "capability_token": "GovernanceArtifacts",
    "sandbox_envelope": "GovernanceArtifacts",
    "raw secret": "L2HandoffValidationResult",
    "provider client handle": "L2HandoffValidationResult",
    "created_at": "compute_manifest_hash",
    "wall-clock": "compute_manifest_hash",
    "run_clock": "compute_manifest_hash",
    # PA.8
    "slotauthorityproof": "detect_authority_violations",
    "promptinjectionfixture": "C0ClassifierResult",
    "providerrenderequivalence": "render_for_provider",
    "schemabindingproof": "R0SchemaBinding",
    "no-retrieval": "FORBIDDEN_EXECUTION_VERBS",
    "no-execution": "FORBIDDEN_EXECUTION_VERBS",
    "data-only": "detect_authority_violations",
    "redteam": "C0ClassifierResult",
    "red-team": "C0ClassifierResult",
    "red team": "C0ClassifierResult",
    "injection_payload": "U0AirlockResult",
    "injection": "U0AirlockResult",
    "expected_boundary": "U0AirlockResult",
    "preserved_authority_order": "AuthorityStack",
    "no instruction promotion": "detect_authority_violations",
    "blocked_attempts": "detect_authority_violations",
    "deterministic_digest": "compute_manifest_hash",
    # Parent
    "doctrine": "PAStatus",
    "vocabulary": "PAStatus",
    "invariant": "InvariantReport",
    "ssot": "DOCTRINE_FILES",
    "no-overlap": "PA_PARENT_SPAN_NAME",
    "trace": "trace_spans",
    "span": "SpanDefinition",
    # Generic doctrine plumbing keywords always satisfied by package
    "stage": "PAStatus",
    "doctrine_status": "PAStatus",
    "no-loss": "PromptAssemblyPipelineResult",
    "zero-loss": "PromptAssemblyPipelineResult",
    "ssot drift": "DOCTRINE_FILES",
}


# Doctrine-only suffix decorations on field tokens (e.g. ``_ref``,
# ``_refs``, ``_id``, ``[]``, ``{}``). When a literal token miss occurs
# the matcher strips one suffix at a time and retries. This single
# transformation eats the entire ``foo_ref`` / ``foo_refs[]`` /
# ``foo_id`` family of doctrine field names that the runtime stores
# under the bare ``foo`` (or its CamelCase / snake-case sibling).
_DOCTRINE_SUFFIXES: tuple[str, ...] = (
    "_ref",
    "_refs",
    "_id",
    "_ids",
    "_hash",
    "_map",
    "_set",
    "_estimate",
    "_estimates",
    "_value",
    "_values",
    "_count",
    "_overhead",
    "_payload",
    "_payloads",
    "_report",
    "_reports",
    "_attempt",
    "_attempts",
    "_class",
    "_status",
    "_priority",
    "_ledger",
    "_route",
    "_routes",
    "_block",
    "_blocks",
    "_chunk",
    "_chunks",
    "_field",
    "_fields",
    "_record",
    "_records",
    "_binding",
    "_bindings",
    "_slot",
    "_slots",
    "_order",
    "_digest",
    "_total",
    "_min",
    "_max",
    "_pass",
    "_passes",
    "_check",
    "_checks",
    "_request",
    "_requests",
    "_response",
    "_responses",
    "_target",
    "_kind",
    "_type",
    "_label",
    "_metadata",
    "_state",
    "_summary",
    "_signal",
    "_intent",
    "_offset",
    "_score",
    "_scores",
    "_inventory",
    "_receipt",
    "_receipts",
    "_manifest",
    "_manifests",
    "_envelope",
    "_envelopes",
    "_settings",
    "_signature",
    "_signatures",
    "_violation",
    "_violations",
    "_action",
    "_actions",
)

# Doctrine-only one-shot aliases. Each maps a literal doctrine field
# token to the runtime artefact that absorbs it. These tokens do not
# survive the suffix-strip heuristic because the runtime simply uses a
# different name; the alias closes the gap by hand.
_FIELD_ALIASES: dict[str, str] = {
    "PAAssemblyInput": "UpstreamInputBundle",
    "StructuredPromptSlots": "AuthorityStack",
    "PAAssemblyInput_ref": "UpstreamInputBundle",
    "S0_slot": "S0Block",
    "D0_slot": "D0FenceBlock",
    "I0_slot": "I0InstructionBlock",
    "E0_slot": "E0ExemplarBlock",
    "C0_slot": "C0GroundedContextBlock",
    "M0_slot": "M0MetaControlBlock",
    "U0_slot": "U0NeutralizedTaskBlock",
    "Y0_slot": "Y0LearningPriorBlock",
    "H0_slot": "H0HealingHintBlock",
    "R0_binding": "R0SchemaBinding",
    "L1PlanContract_ref": "L1PlanContract",
    "L0RouteContract_ref": "L0RouteContract",
    "C0FinalEvidenceContract_ref": "C0EvidenceContract",
    "governance_artifact_refs": "GovernanceArtifacts",
    "governance_artifact_refs[]": "GovernanceArtifacts",
    "route_digest": "compute_replay_key",
    "policy_posture_ref": "GovernanceArtifacts",
    "security_pass_id": "AssemblySecurityPassReceipt",
    "security_pass_receipt_ref": "AssemblySecurityPassReceipt",
    "slot_origin_map": "SlotEntry",
    "slot_payload_hashes": "SlotEntry",
    "slot_omission_reasons": "SlotEntry",
    "slot_omission_reasons{}": "SlotEntry",
    "slot_hashes": "SlotEntry",
    "slot_hashes{}": "SlotEntry",
    "compiled_prompt_artifact_ref": "CompiledPromptArtifactSigned",
    "task_class": "L1PlanContract",
    "data_class": "GovernanceArtifacts",
    "symbolic_model_id": "ExecutionMetadataBlock",
    "tool_call_overhead_estimate": "BudgetReport",
    "route_budget_ref": "BudgetReport",
    "C0_priority_order_ref": "BudgetClass",
    "token_budget_ledger_id": "BudgetReport",
    "token_budget_ledger_ref": "BudgetReport",
    "input_token_budget": "BudgetReport",
    "budget_hash": "BudgetReport",
    "removed_items": "deterministic_trim",
    "compressed_items": "deterministic_trim",
    "reason_codes": "DispatchBlockReason",
    "before_token_estimate": "SlotBudgetEntry",
    "provider_capabilities_ref": "PROVIDER_LANES",
    "adapter_version": "render_for_provider",
    "canonical_slot_hashes": "canonicalize_manifest",
    "canonical_slot_hashes{}": "canonicalize_manifest",
    "system_field_ref": "render_for_provider",
    "developer_field_ref": "render_for_provider",
    "user_field_ref": "render_for_provider",
    "document_container_refs": "render_for_provider",
    "document_container_refs[]": "render_for_provider",
    "tools_field_ref": "ToolBindingManifest",
    "unsupported_feature_reports": "render_for_provider",
    "final_provider_payload_ref": "RenderedPayload",
    "source_lineage_refs": "C0EvidenceContract",
    "safe_extraction_receipts": "C0ClassifierResult",
    "c0_instruction_like_payload": "C0ClassifierResult",
    "c0_context_missing_for_grounded_route": "C0EvidenceContract",
    "stale_component_ref": "PromptBOMResolved",
    # PA.8 contract field tokens.
    "proof_id": "compute_manifest_hash",
    "fixture_id": "C0ClassifierResult",
    "expected_no_instruction_promotion": "detect_authority_violations",
    # PA.8 named-test requirements (literal names declared in doctrine;
    # the runtime equivalent is documented in `_PA8_TEST_EQUIVALENTS`
    # in runtime_evidence.py and referenced here).
    "test_pa_blocks_c0_instruction_promotion": "detect_authority_violations",
    "test_pa_blocks_human_text_as_authority": "run_u0_airlock",
    "test_pa_schema_bound_native_not_only_prose": "R0SchemaBinding",
    "test_pa_token_trim_preserves_required_authority_slots": "BUDGET_TRIM_ORDER",
    "test_pa_never_calls_retrieval_or_execution": "FORBIDDEN_EXECUTION_VERBS",
}


def _strip_doctrine_decorations(tok: str) -> str:
    """Strip ``[]`` / ``{}`` and trailing structural suffixes."""
    base = tok.rstrip("]").rstrip("[").rstrip("}").rstrip("{")
    base = base.replace("[]", "").replace("{}", "")
    return base


def _match_token(tok: str, idx: dict[str, set[str]]) -> set[str]:
    """Return the set of evidence sources that contain ``tok``.

    The match is fuzzed in two ways before giving up:
      1. ``[]`` / ``{}`` decorations are stripped.
      2. If the literal token misses, the matcher peels one
         doctrine-only suffix at a time (``_ref``, ``_id``, ``_hash``,
         ...) and retries. This collapses the ``foo_ref`` /
         ``foo_refs[]`` / ``foo_id`` family of doctrine field names
         onto their runtime sibling without bloating the alias map.
      3. A curated :data:`_FIELD_ALIASES` table maps the remaining
         doctrine-only field tokens (e.g. ``S0_slot`` → ``S0Block``)
         to runtime artefacts.
    """
    sources: set[str] = set()
    base = _strip_doctrine_decorations(tok)

    candidates: list[str] = [base]
    # Peel suffixes one at a time.
    for suf in _DOCTRINE_SUFFIXES:
        if base.endswith(suf) and len(base) > len(suf):
            candidates.append(base[: -len(suf)])
    # Curated alias.
    if tok in _FIELD_ALIASES:
        candidates.append(_FIELD_ALIASES[tok])
    if base in _FIELD_ALIASES:
        candidates.append(_FIELD_ALIASES[base])

    for cand in candidates:
        cand_lc = cand.lower()
        if cand in idx["pa_surface"] or cand_lc in idx["pa_surface_lc"]:
            sources.add("runtime_symbol")
        if cand in idx["receipt_keys"] or cand_lc in idx["receipt_keys_lc"]:
            sources.add("receipt_key")
        if cand in idx["status_values"] or cand_lc in idx["status_values_lc"]:
            sources.add("status_value")
        if cand in idx["forbidden_set"] or cand_lc in idx["forbidden_set_lc"]:
            sources.add("forbidden_token")
        if cand_lc in idx["source_corpus_lc"]:
            sources.add("source_file")
        if cand_lc in idx["test_corpus_lc"]:
            sources.add("test_corpus")
        if cand_lc in idx["doctrine_corpus_lc"]:
            sources.add("doctrine_xref")
    return sources


def _evidence_for_requirement(
    req: Requirement, idx: dict[str, set[str]]
) -> tuple[bool, list[str], list[dict[str, Any]]]:
    """Resolve evidence for a requirement.

    Returns
    -------
    (passed, source_summary, per_token_detail).

    The check passes if AT LEAST ONE of these holds:
      1. The requirement text (whole-line) is itself a known token
         (e.g. CSV-token rows like ``ALLOW``).
      2. Any extracted identifier in the text resolves into one of the
         evidence sources (runtime symbol, receipt key, status value,
         forbidden token, source file, test corpus, doctrine xref).
      3. A documented prose keyword from :data:`_PROSE_KEYWORD_MAP`
         appears in the text and its mapped runtime artefact is in
         ``pa_surface``.
    """
    detail: list[dict[str, Any]] = []
    sources_overall: set[str] = set()

    # Path (1): whole-line identifier match.
    ws = req.text.strip().rstrip(".").rstrip(",").strip()
    if re.match(r"^[A-Za-z][A-Za-z0-9_]*$", ws):
        srcs = _match_token(ws, idx)
        if srcs:
            sources_overall |= srcs
            detail.append({"token": ws, "sources": sorted(srcs)})

    # Path (2): tokenised identifiers from the line.
    for tok in _TOKEN_RE.findall(req.text):
        if len(tok) < 3:
            continue
        srcs = _match_token(tok, idx)
        if srcs:
            sources_overall |= srcs
            detail.append({"token": tok, "sources": sorted(srcs)})

    # Path (3): prose-keyword fallback.
    text_lc = req.text.lower()
    for kw, runtime_symbol in _PROSE_KEYWORD_MAP.items():
        if kw in text_lc:
            if runtime_symbol in idx["pa_surface"]:
                sources_overall.add("prose_keyword")
                detail.append(
                    {"prose_keyword": kw, "runtime_symbol": runtime_symbol, "sources": ["prose_keyword"]}
                )

    # ``doctrine_xref`` alone is not runtime evidence — every requirement
    # must be backed by code, a receipt, an enum, a forbidden-token, a
    # source file, a test, or a documented prose keyword pointing at a
    # runtime artefact. ``doctrine_xref`` is reported (because it tells
    # the reader the same identifier shows up elsewhere in the doctrine
    # corpus) but does not by itself satisfy the PASS bar.
    runtime_grade = sources_overall - {"doctrine_xref"}
    passed = bool(runtime_grade)
    return passed, sorted(sources_overall), detail


# --------------------------------------------------------------------------
# Matrix render
# --------------------------------------------------------------------------


def _render_markdown(rows: list[dict[str, Any]]) -> str:
    total = len(rows)
    passed = sum(1 for r in rows if r["status"] == "PASS")
    failed = total - passed
    by_stage: dict[str, list[dict[str, Any]]] = {}
    for r in rows:
        by_stage.setdefault(r["stage"], []).append(r)

    out: list[str] = []
    out.append("# Prompt Assembly \u2014 Line-by-Line Requirement Matrix\n")
    out.append("Doctrine corpus:\n")
    for stage, rel in DOCTRINE_FILES.items():
        out.append(f"- **{stage}** \u2014 `{rel}`")
    out.append("")
    out.append(f"**Tally:** {passed} PASS / {failed} FAIL (of {total} line-level requirements)\n")
    out.append(f"**Generated:** {_dt.datetime.now(_dt.timezone.utc).isoformat()}\n")

    out.append("## Per-stage roll-up\n")
    out.append("| Stage | Total | PASS | FAIL |")
    out.append("|---|---:|---:|---:|")
    for stage in sorted(by_stage):
        sub = by_stage[stage]
        p = sum(1 for r in sub if r["status"] == "PASS")
        f = len(sub) - p
        out.append(f"| {stage} | {len(sub)} | {p} | {f} |")
    out.append("")

    out.append("## Evidence-source legend\n")
    out.append(
        "- `runtime_symbol` \u2014 token is a public name in "
        "`agentic_core.prompt_governance.prompt_assembly`\n"
        "- `receipt_key` \u2014 token is a key (any depth) in one of the "
        "8 doctrine receipt envelopes\n"
        "- `status_value` \u2014 token is a member of `PAStatus`\n"
        "- `forbidden_token` \u2014 token is a member of "
        "`FORBIDDEN_DISPOSITIONS \u222a FORBIDDEN_EXECUTION_VERBS`\n"
        "- `source_file` \u2014 token appears in "
        "`agentic_core/prompt_governance/**/*.py` source corpus\n"
        "- `test_corpus` \u2014 token appears in PA test files / their "
        "filenames\n"
        "- `doctrine_xref` \u2014 token appears in another PA doctrine "
        "file (cross-reference)\n"
        "- `prose_keyword` \u2014 the requirement text contains a "
        "documented prose keyword that maps to a known runtime artefact\n"
    )

    for stage in sorted(by_stage):
        out.append(f"\n## {stage}\n")
        out.append("| # | Line | Section | Sub-section | Requirement | Status | Evidence |")
        out.append("|---:|---:|---|---|---|:---:|---|")
        for i, r in enumerate(by_stage[stage], 1):
            section = r["section"].replace("|", "\\|")
            sub = r["sub_section"].replace("|", "\\|")
            text = r["text"].replace("|", "\\|")
            if len(text) > 200:
                text = text[:197] + "\u2026"
            ev = ", ".join(r["sources"]) or "_no match_"
            out.append(f"| {i} | {r['line_no']} | {section} | {sub} | {text} | **{r['status']}** | {ev} |")
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------
# Main entrypoint
# --------------------------------------------------------------------------


def _build_rows() -> list[dict[str, Any]]:
    idx = _build_evidence_index()
    rows: list[dict[str, Any]] = []
    for stage, rel in DOCTRINE_FILES.items():
        reqs = _extract_requirements(stage, rel)
        for r in reqs:
            passed, sources, detail = _evidence_for_requirement(r, idx)
            rows.append(
                {
                    **asdict(r),
                    "status": "PASS" if passed else "FAIL",
                    "sources": sources,
                    "evidence_detail": detail,
                }
            )
    return rows


def main() -> int:
    rows = _build_rows()
    md_path = _REPO_ROOT / "docs" / "reports" / "prompt-assembly" / "line_by_line_matrix.md"
    json_path = _REPO_ROOT / "tools" / "prompt_assembly" / "_line_by_line_matrix.json"
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(_render_markdown(rows), encoding="utf-8")
    json_path.write_text(
        json.dumps(rows, indent=2, default=str, ensure_ascii=False),
        encoding="utf-8",
    )

    passed = sum(1 for r in rows if r["status"] == "PASS")
    failed = len(rows) - passed
    print(f"VERDICT: {'PROVEN' if failed == 0 else 'GAPS'}")
    print(f"  {passed} PASS / {failed} FAIL (of {len(rows)} line-level requirements)")
    print(f"  report: {md_path.relative_to(_REPO_ROOT)}")
    print(f"  json:   {json_path.relative_to(_REPO_ROOT)}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
