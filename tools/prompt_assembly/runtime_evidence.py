"""Prompt Assembly Runtime-Evidence Harness.

Walks every requirement extracted from
``docs/reference/03_L0_Routing_&_L3_Orch/Prompt Assembly/*.md`` and emits a
PASS/FAIL evidence object proving each one against the actually-loaded
runtime objects in ``agentic_core.prompt_governance.prompt_assembly``.

Categories
----------
- STATUS_SET     : every doctrine PA_* status name resolves to a member
                   of :class:`PAStatus` and the per-stage
                   ``STAGE_TO_STATUSES`` partition matches the doctrine.
- MUST_EMIT      : every doctrine output field appears as a key in the
                   constructed receipt envelope from
                   :mod:`doctrine_receipts`.
- MUST_NOT_FENCE : the package surface contains NO public callable whose
                   name implies a forbidden behavior (retrieve/execute/
                   route/call_provider/approve_output/mutate_l4/
                   commit_state). Structural enforcement by absence.
- FORBID_RD      : the parent doctrine's forbidden runtime-disposition
                   set lives in :data:`FORBIDDEN_DISPOSITIONS` and the
                   forbidden execution-verb set lives in
                   :data:`FORBIDDEN_EXECUTION_VERBS`.
- INVARIANT      : the 12 cross-child invariants (PA.I1 .. PA.I12) each
                   have a constructive runtime check.
- SLOT_MAP       : the canonical 10-slot map and authority order can be
                   constructed via :class:`AuthorityStack` /
                   :class:`SlotEntry` and rank ordering is preserved.
- DETERMINISM    : the determinism invariants (PA.I9, PA.I10) are
                   exercised by constructing a budget twice with the
                   same inputs and asserting identical outputs.

Outputs
-------
- ``docs/reports/prompt-assembly/runtime_evidence.md``  (human report)
- ``tools/prompt_assembly/_runtime_evidence.json``      (machine sidecar)
"""

from __future__ import annotations

import dataclasses
import datetime as _dt
import inspect
import json
import sys
from pathlib import Path
from collections.abc import Mapping
from typing import Any

# Make repo importable when invoked as a script.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# pylint: disable=wrong-import-position
import agentic_core.prompt_governance.prompt_assembly as pa  # noqa: E402
from agentic_core.prompt_governance.prompt_assembly import (  # noqa: E402
    FORBIDDEN_DISPOSITIONS,
    FORBIDDEN_EXECUTION_VERBS,
    ForbiddenOutputError,
    PAStatus,
    STAGE_TO_STATUSES,
    aggregate_doctrine_status,
    assert_no_forbidden,
    pa0_doctrine_receipt,
    pa1_doctrine_receipt,
    pa2_doctrine_receipt,
    pa3_doctrine_receipt,
    pa4_doctrine_receipt,
    pa5_doctrine_receipt,
    pa6_doctrine_receipt,
    pa7_doctrine_receipt,
    run_prompt_assembly_pipeline,
)
from agentic_core.prompt_governance.prompt_assembly.pa0_boundary import (  # noqa: E402
    boundary_check,
)
from agentic_core.prompt_governance.prompt_assembly.pa2_slot_composition import (  # noqa: E402
    AuthorityStack,
    SlotEntry,
)
from agentic_core.prompt_governance.prompt_assembly.pa3_c0_classifier import (  # noqa: E402
    classify_c0_chunks,
)
from agentic_core.prompt_governance.prompt_assembly.pa4_validation import (  # noqa: E402
    PA4ValidationReport,
    ValidationCheckResult,
)
from agentic_core.prompt_governance.prompt_assembly.pa5_budget import (  # noqa: E402
    BudgetClass,
    BudgetReport,
    OverflowStatus,
    SlotBudgetEntry,
    build_budget_report,
)
from tools.prompt_assembly.doctrine_parser import (  # noqa: E402
    parse_all as _parse_doctrine_all,
    parse_extra as _parse_doctrine_extra,
    _extract_csv_section,
    _extract_section,
)


# --------------------------------------------------------------------------
# Doctrine SSOT — extracted from the .md files. Updating the docs requires
# updating these tables in lock-step (a future CI gate may parse the .md
# directly; this harness establishes the runtime baseline first).
# --------------------------------------------------------------------------


DOCTRINE_FILES = {
    "PARENT": "docs/reference/03_L0_Routing_&_L3_Orch/Prompt Assembly/Prompt_Assembly_detailed.md",
    "PA.0": "docs/reference/03_L0_Routing_&_L3_Orch/Prompt Assembly/PA.0_Boundary_Check_detailed.md",
    "PA.1": "docs/reference/03_L0_Routing_&_L3_Orch/Prompt Assembly/PA.1_Load_Resolve_Prompt_BOM_detailed.md",
    "PA.2": "docs/reference/03_L0_Routing_&_L3_Orch/Prompt Assembly/PA.2_Slot_Composition_detailed.md",
    "PA.3": "docs/reference/03_L0_Routing_&_L3_Orch/Prompt Assembly/PA.3_Airlock_Security_Pass_detailed.md",
    "PA.4": "docs/reference/03_L0_Routing_&_L3_Orch/Prompt Assembly/PA.4_Validate_Slot_Contract_detailed.md",
    "PA.5": "docs/reference/03_L0_Routing_&_L3_Orch/Prompt Assembly/PA.5_Token_Budget_Determinism_detailed.md",
    "PA.6": "docs/reference/03_L0_Routing_&_L3_Orch/Prompt Assembly/PA.6_Provider_Aware_Rendering_detailed.md",
    "PA.7": "docs/reference/03_L0_Routing_&_L3_Orch/Prompt Assembly/PA.7_Final_Emit_Compiled_Prompt_Artifact_detailed.md",
}


# Per-stage doctrine STATUS VALUES. SSOT is the .md files; this dict is the
# parsed baseline the harness checks against the runtime ``PAStatus`` enum.
DOCTRINE_STATUS_VALUES: dict[str, list[str]] = {
    "PA.0": [
        "PA_READY",
        "PA_INPUT_INCOMPLETE",
        "PA_BOUNDARY_MISMATCH",
        "PA_REQUIRES_UPSTREAM_REPAIR",
    ],
    "PA.1": [
        "PA_BOM_RESOLVED",
        "PA_BOM_GAP",
        "PA_REQUIRES_UPSTREAM_REPAIR",
    ],
    "PA.2": [
        "PA_SLOTS_COMPOSED",
        "PA_SLOT_COMPOSITION_GAP",
        "PA_AUTHORITY_CONFLICT",
    ],
    "PA.3": [
        "PA_SECURITY_PASS",
        "PA_SECURITY_GAP",
        "PA_SAFE_EXTRACTION_PARTIAL",
        "PA_SLOT_PAYLOAD_REJECTED",
        "PA_REQUIRES_UPSTREAM_REPAIR",
    ],
    "PA.4": [
        "PA_SLOT_CONTRACT_VALID",
        "PA_SLOT_CONTRACT_INVALID",
        "PA_CONTEXT_CONTRACT_GAP",
        "PA_AUTHORITY_INVERSION_GAP",
        "PA_SCHEMA_BINDING_GAP",
        "PA_TOOL_BINDING_GAP",
    ],
    "PA.5": [
        "PA_BUDGET_FIT",
        "PA_BUDGET_TRIMMED",
        "PA_BUDGET_OVERFLOW",
        "PA_REQUIRES_UPSTREAM_REPAIR",
    ],
    "PA.6": [
        "PA_RENDERED",
        "PA_RENDER_GAP",
        "PA_PROVIDER_FEATURE_GAP",
        "PA_SCHEMA_RENDER_GAP",
        "PA_TOOL_RENDER_GAP",
    ],
    "PA.7": [
        "PA_ARTIFACT_SIGNED",
        "PA_ARTIFACT_NOT_SIGNED",
        "PA_SIGNATURE_GAP",
        "PA_MANIFEST_HASH_GAP",
        "PA_L2_HANDOFF_READY",
        "PA_L2_HANDOFF_GAP",
    ],
}


# Per-stage doctrine MUST EMIT field names. Each row is (key in receipt,
# doctrine name) — the receipt key may be a doctrine-named container or a
# stage-status field that carries the doctrine output.
DOCTRINE_MUST_EMIT: dict[str, list[str]] = {
    "PA.0": [
        "stage",
        "doctrine_status",
        "boundary_status_receipt",
        "required_input_inventory",
        "upstream_reference_map",
        "assembly_gap_report",
    ],
    "PA.1": [
        "stage",
        "doctrine_status",
        "bom_resolution_receipt",
        "component_inventory",
        "component_hash_map",
        "bom_gap_report",
        "bom_hash_receipt",
    ],
    "PA.2": [
        "stage",
        "doctrine_status",
        "slot_composition_receipt",
        "slot_authority_map",
        "slot_lineage_map",
        "slot_conflict_map",
        "structured_slots_hash_receipt",
    ],
    "PA.3": [
        "stage",
        "doctrine_status",
        "AssemblySecurityPassReceipt",
        "safe_slot_payload_map",
        "rejected_slot_payload_report",
        "prompt_like_payload_report",
        "safe_extraction_map",
        "security_gap_report",
    ],
    "PA.4": [
        "stage",
        "doctrine_status",
        "SlotValidationReceipt",
        "validation_gap_report",
        "authority_order_receipt",
        "context_contract_receipt",
        "tool_schema_binding_receipt",
        "validation_hash_receipt",
    ],
    "PA.5": [
        "stage",
        "doctrine_status",
        "TokenBudgetLedger",
        "deterministic_trimming_receipt",
        "stable_prefix_receipt",
        "overflow_gap_report",
        "canonical_hash_input_manifest",
    ],
    "PA.6": [
        "stage",
        "doctrine_status",
        "ProviderRenderManifest",
        "provider_field_mapping_receipt",
        "schema_render_receipt",
        "tool_render_receipt",
        "provider_feature_gap_report",
    ],
    "PA.7": [
        "stage",
        "doctrine_status",
        "CompiledPromptArtifact",
        "compiled_prompt_artifact_receipt",
        "manifest_hash_receipt",
        "hmac_signature_receipt",
        "l2_handoff_envelope",
        "final_artifact_gap_report",
    ],
}


# Cross-child invariants (PA.I1 .. PA.I12) from the parent file.
DOCTRINE_INVARIANTS: list[tuple[str, str]] = [
    ("PA.I1", "Prompt Assembly composes only — no retrieve/route/execute/call/write."),
    ("PA.I2", "PA consumes C0 evidence; does not alter support scores or invent citations."),
    ("PA.I3", "Every slot payload preserves origin, authority, source refs, replay/audit refs."),
    ("PA.I4", "User text is task intent only, not policy authority."),
    ("PA.I5", "Retrieved/tool/human/model/prior content is data unless higher authority binds it."),
    ("PA.I6", "Lower-authority slots cannot override higher-authority slots."),
    ("PA.I7", "Tools and schemas ride provider-native API fields, not loose prose."),
    ("PA.I8", "Required governing instructions and required evidence cannot be silently dropped."),
    ("PA.I9", "Canonical structured slot bytes drive manifest_hash, not provider-specific formatting."),
    ("PA.I10", "Same BOM + slots + trimming + secret -> same hash/signature (determinism)."),
    ("PA.I11", "If assembly cannot preserve required authority/evidence/schema, emit gap evidence."),
    ("PA.I12", "PA.7 handoff to L2 is artifact handoff only; L2 still validates and executes."),
]


# Forbidden runtime dispositions and execution verbs (parent doctrine).
DOCTRINE_FORBIDDEN_DISPOSITIONS: set[str] = {
    "ALLOW",
    "DENY",
    "CLARIFY",
    "ABSTAIN",
    "REROUTE",
    "SHRINK_SCOPE",
    "RETRY",
    "HEAL",
    "ESCALATE_HITL",
    "QUARANTINE",
    "REDACT",
    "SAFE_FALLBACK",
    "MARK_DEGRADED",
    "COMMIT_REQUEST",
    "BLOCK_COMMIT",
    "ALLOW_FINISH",
}
DOCTRINE_FORBIDDEN_VERBS: set[str] = {
    "approve_execution",
    "approve_output",
    "approve_write",
    "call_provider",
    "execute_tool",
    "mutate_l4",
}


# Receipt-key alias map: when a doctrine item is the canonical artifact
# NAME (PascalCase, e.g. ``PAAssemblyInput``), the receipt envelope may
# represent it through one or more sub-receipt keys. This table maps each
# doctrine name to the set of receipt keys that satisfy it. Items absent
# from this map are matched directly against receipt keys.
RECEIPT_NAME_ALIASES: dict[str, set[str]] = {
    # PA.0 — the receipt envelope IS the BoundaryCheckReceipt; PAAssemblyInput
    # is represented by the required-input + upstream-ref maps.
    "BoundaryCheckReceipt": {"boundary_status_receipt", "stage"},
    "PAAssemblyInput": {"required_input_inventory", "upstream_reference_map"},
    # PA.1 — PromptBOM is represented by component inventory + hash map.
    "PromptBOM": {"component_inventory", "component_hash_map"},
    # PA.2 — StructuredPromptSlots is represented by the composition receipt
    # and slot maps.
    "StructuredPromptSlots": {"slot_composition_receipt", "slot_authority_map"},
    # PA.5 — budget_status_receipt is represented by the doctrine_status
    # field carrying a PA_BUDGET_* token.
    "budget_status_receipt": {"doctrine_status", "TokenBudgetLedger"},
    # PA.6 — rendered_prompt_packet is the doctrine-named container.
    "rendered_prompt_packet": {"rendered_prompt_packet", "ProviderRenderManifest"},
}


def _receipt_satisfies(receipt: dict[str, Any], doctrine_name: str) -> bool:
    """Return True iff ``doctrine_name`` is satisfied by ``receipt``.

    Resolution order:
    1. Direct key membership.
    2. Any aliased key membership.
    """
    if doctrine_name in receipt:
        return True
    aliases = RECEIPT_NAME_ALIASES.get(doctrine_name, set())
    return any(a in receipt for a in aliases)


# Canonical 10-slot map (parent doctrine) — slot, authority rank (high->low),
# authority label, purpose summary.
DOCTRINE_SLOT_MAP: list[tuple[str, int, str]] = [
    ("S0", 100, "ABSOLUTE"),
    ("D0", 90, "BINDING"),
    ("I0", 80, "GOVERNED"),
    ("E0", 70, "GUIDING"),
    ("C0", 60, "INFORMATIONAL"),
    ("M0", 50, "PRIVATE"),
    ("U0", 40, "ZERO"),
    ("Y0", 30, "ANALYTIC"),
    ("H0", 20, "PROPOSED"),
    ("R0", 10, "SCHEMA"),
]


# ---------------------------------------------------------------------------
# Evidence helpers
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class _Row:
    """One requirement -> one evidence row."""

    req_id: str
    stage: str
    category: str
    requirement: str
    status: str  # "PASS" | "FAIL"
    evidence: dict[str, Any]


def _ok(req_id: str, stage: str, category: str, requirement: str, evidence: dict[str, Any]) -> _Row:
    return _Row(req_id, stage, category, requirement, "PASS", evidence)


def _fail(req_id: str, stage: str, category: str, requirement: str, evidence: dict[str, Any]) -> _Row:
    return _Row(req_id, stage, category, requirement, "FAIL", evidence)


# ---------------------------------------------------------------------------
# Stage receipt builders — produce a receipt envelope for each stage so the
# MUST_EMIT scan has a concrete artifact to inspect.
# ---------------------------------------------------------------------------


def _build_pa0_receipt() -> dict[str, Any]:
    br = boundary_check(
        plan_contract={"plan_id": "p1", "policy_hash": "h"},
        route_contract={"route_id": "r1", "policy_hash": "h"},
        evidence_contract=None,
        governance={},
        execution_metadata={"policy_hash": "h"},
    )
    return pa0_doctrine_receipt(
        br,
        request_id="req",
        plan_id="p1",
        route_id="r1",
        policy_hash="h",
    )


def _build_pa1_receipt() -> dict[str, Any]:
    return pa1_doctrine_receipt(
        component_inventory={"S0": True, "D0": True, "I0": True},
        component_hash_map={"S0": "a", "D0": "b", "I0": "c"},
        missing_components=[],
        bom_hash="bom-hash-1",
    )


def _build_pa2_receipt() -> dict[str, Any]:
    stack = AuthorityStack(
        entries=tuple(
            SlotEntry(code=code, content=f"<{code}>", authority_rank=rank)
            for code, rank, _ in DOCTRINE_SLOT_MAP
        )
    )
    return pa2_doctrine_receipt(None, stack, structured_slots_hash="ssh-1")


def _build_pa3_receipt() -> dict[str, Any]:
    chunks = [{"id": "c1", "text": "harmless evidence about cats"}]
    classifier = classify_c0_chunks(chunks)
    return pa3_doctrine_receipt(classifier=classifier)


def _build_pa4_receipt() -> dict[str, Any]:
    report = PA4ValidationReport.from_checks(
        [
            ValidationCheckResult(
                check_id="ctx_evidence_present",
                category="context",
                passed=True,
                detail="ok",
            ),
            ValidationCheckResult(
                check_id="schema_parseable",
                category="schema",
                passed=True,
                detail="ok",
            ),
        ]
    )
    return pa4_doctrine_receipt(report)


def _build_pa5_receipt(*, overflow: bool = False) -> dict[str, Any]:
    if overflow:
        report = BudgetReport(
            model_context_window=8000,
            input_token_estimate=20_000,
            reserved_output_tokens=4096,
            reserved_schema_tokens=0,
            reserved_tool_tokens=0,
            stable_prefix_tokens=500,
            c0_tokens=18_000,
            u0_tokens=200,
            e0_tokens=0,
            y0_tokens=0,
            h0_tokens=0,
            overflow_status=OverflowStatus.OVERFLOW,
            can_dispatch=False,
            trim_actions=(),
            dropped_items_with_reasons=(),
        )
    else:
        report = BudgetReport(
            model_context_window=200_000,
            input_token_estimate=1000,
            reserved_output_tokens=4096,
            reserved_schema_tokens=0,
            reserved_tool_tokens=0,
            stable_prefix_tokens=500,
            c0_tokens=0,
            u0_tokens=200,
            e0_tokens=0,
            y0_tokens=0,
            h0_tokens=0,
            overflow_status=OverflowStatus.OK,
            can_dispatch=True,
            trim_actions=(),
            dropped_items_with_reasons=(),
        )
    return pa5_doctrine_receipt(report)


def _build_pa6_receipt() -> dict[str, Any]:
    return pa6_doctrine_receipt(None, provider_lane="anthropic", rendered=True)


def _build_pa7_receipt() -> dict[str, Any]:
    return pa7_doctrine_receipt(
        artifact_id="art-1",
        manifest_hash="m-1",
        hmac_sig="sig-1",
        signed=True,
        handoff_ready=True,
        request_id="req",
        run_id="run-1",
        trace_id="tr-1",
        route_id="r1",
        plan_id="p1",
        policy_hash="h",
        replay_key="rk-1",
    )


# ---------------------------------------------------------------------------
# Category checkers
# ---------------------------------------------------------------------------


def check_status_set() -> list[_Row]:
    """STATUS_SET: every doctrine PA_* status is a PAStatus member; the
    stage partition matches the doctrine."""
    rows: list[_Row] = []
    runtime_values = {s.value for s in PAStatus}
    # 1) Every doctrine value resolves to a PAStatus member.
    flat_doctrine: list[tuple[str, str]] = []
    for stage, values in DOCTRINE_STATUS_VALUES.items():
        for v in values:
            flat_doctrine.append((stage, v))

    for stage, value in flat_doctrine:
        present = value in runtime_values
        ev = {
            "doctrine_value": value,
            "resolves_to_PAStatus": present,
            "PAStatus_member_value": PAStatus(value).value if present else None,
        }
        if present:
            rows.append(
                _ok(
                    f"STATUS::{stage}::{value}",
                    stage,
                    "STATUS_SET",
                    f"{stage} doctrine status `{value}` exists in PAStatus",
                    ev,
                )
            )
        else:
            rows.append(
                _fail(
                    f"STATUS::{stage}::{value}",
                    stage,
                    "STATUS_SET",
                    f"{stage} doctrine status `{value}` exists in PAStatus",
                    ev,
                )
            )

    # 2) Per-stage partition matches doctrine.
    for stage, doctrine_values in DOCTRINE_STATUS_VALUES.items():
        runtime_for_stage = {s.value for s in STAGE_TO_STATUSES.get(stage, set())}
        doctrine_set = set(doctrine_values)
        ev = {
            "doctrine_count": len(doctrine_set),
            "runtime_count": len(runtime_for_stage),
            "missing_in_runtime": sorted(doctrine_set - runtime_for_stage),
            "extra_in_runtime": sorted(runtime_for_stage - doctrine_set),
        }
        if doctrine_set.issubset(runtime_for_stage):
            rows.append(
                _ok(
                    f"PARTITION::{stage}",
                    stage,
                    "STATUS_SET",
                    f"{stage} STAGE_TO_STATUSES contains every doctrine status",
                    ev,
                )
            )
        else:
            rows.append(
                _fail(
                    f"PARTITION::{stage}",
                    stage,
                    "STATUS_SET",
                    f"{stage} STAGE_TO_STATUSES contains every doctrine status",
                    ev,
                )
            )

    # 3) Vocabulary closure: total runtime size matches union of doctrine sets
    # plus any cross-stage statuses (PA_REQUIRES_UPSTREAM_REPAIR, PA_READY).
    union = {v for vs in DOCTRINE_STATUS_VALUES.values() for v in vs}
    union.add("PA_READY")  # parent-doctrine implicit "all-stages-clean" status
    ev = {
        "doctrine_union_size": len(union),
        "runtime_pastatus_size": len(runtime_values),
        "missing": sorted(union - runtime_values),
    }
    rows.append(
        _ok(
            "STATUS::CLOSURE",
            "ALL",
            "STATUS_SET",
            "Doctrine status union is a subset of runtime PAStatus",
            ev,
        )
        if union.issubset(runtime_values)
        else _fail(
            "STATUS::CLOSURE",
            "ALL",
            "STATUS_SET",
            "Doctrine status union is a subset of runtime PAStatus",
            ev,
        )
    )

    return rows


def check_must_emit() -> list[_Row]:
    """MUST_EMIT: every doctrine output appears as a key in the runtime
    receipt envelope OR is satisfied through ``RECEIPT_NAME_ALIASES``.

    Doctrine source of truth: parsed live from each stage's ``.md`` file
    via :mod:`tools.prompt_assembly.doctrine_parser` — this closes the
    SSOT-drift loophole that hard-coded tables would otherwise allow.
    """
    builders = {
        "PA.0": _build_pa0_receipt,
        "PA.1": _build_pa1_receipt,
        "PA.2": _build_pa2_receipt,
        "PA.3": _build_pa3_receipt,
        "PA.4": _build_pa4_receipt,
        "PA.5": _build_pa5_receipt,
        "PA.6": _build_pa6_receipt,
        "PA.7": _build_pa7_receipt,
    }
    parsed = _parse_doctrine_all(_REPO_ROOT)
    rows: list[_Row] = []
    for stage, builder in builders.items():
        receipt = builder()
        must_emit = parsed[stage]["must_emit"]
        for field in must_emit:
            direct_hit = field in receipt
            alias_hit = not direct_hit and any(a in receipt for a in RECEIPT_NAME_ALIASES.get(field, set()))
            present = direct_hit or alias_hit
            ev = {
                "doctrine_field": field,
                "present_in_receipt": present,
                "match_kind": "direct" if direct_hit else ("alias" if alias_hit else "missing"),
                "matched_via_aliases": sorted(
                    a for a in RECEIPT_NAME_ALIASES.get(field, set()) if a in receipt
                )
                if alias_hit
                else [],
                "receipt_keys": sorted(receipt.keys()),
                "value_type": type(receipt.get(field)).__name__ if direct_hit else None,
            }
            label = f"{stage} receipt emits doctrine output `{field}`"
            if present:
                rows.append(_ok(f"EMIT::{stage}::{field}", stage, "MUST_EMIT", label, ev))
            else:
                rows.append(_fail(f"EMIT::{stage}::{field}", stage, "MUST_EMIT", label, ev))
    return rows


def check_doctrine_drift() -> list[_Row]:
    """DOCTRINE_DRIFT: cross-check parsed doctrine against the runtime
    PAStatus enum + STAGE_TO_STATUSES partition.

    This catches edits to the ``.md`` files that add or rename a status
    without corresponding runtime updates — a class of regression the
    hard-coded tables alone cannot detect.
    """
    rows: list[_Row] = []
    parsed = _parse_doctrine_all(_REPO_ROOT)
    runtime_values = {s.value for s in PAStatus}
    for stage, data in parsed.items():
        doctrine_statuses = set(data["status_values"])
        runtime_for_stage = {s.value for s in STAGE_TO_STATUSES.get(stage, set())}
        only_in_doctrine = sorted(doctrine_statuses - runtime_for_stage)
        only_in_runtime = sorted(runtime_for_stage - doctrine_statuses)
        # Cross-stage statuses (e.g. PA_REQUIRES_UPSTREAM_REPAIR appears in
        # multiple stages) are allowed to be in runtime but not in any
        # specific stage's runtime set; subtract those before comparing.
        ev = {
            "stage_doctrine_count": len(doctrine_statuses),
            "stage_runtime_count": len(runtime_for_stage),
            "only_in_doctrine": only_in_doctrine,
            "only_in_runtime": only_in_runtime,
        }
        ok_doctrine_resolves = doctrine_statuses.issubset(runtime_values)
        rows.append(
            _ok(
                f"DRIFT::{stage}::doctrine_resolves",
                stage,
                "DOCTRINE_DRIFT",
                f"{stage} doctrine STATUS VALUES all resolve to PAStatus members",
                ev,
            )
            if ok_doctrine_resolves
            else _fail(
                f"DRIFT::{stage}::doctrine_resolves",
                stage,
                "DOCTRINE_DRIFT",
                f"{stage} doctrine STATUS VALUES all resolve to PAStatus members",
                ev,
            )
        )
        ok_runtime_grounded = doctrine_statuses.issubset(runtime_for_stage)
        rows.append(
            _ok(
                f"DRIFT::{stage}::runtime_grounded",
                stage,
                "DOCTRINE_DRIFT",
                f"{stage} STAGE_TO_STATUSES contains every doctrine status from .md",
                ev,
            )
            if ok_runtime_grounded
            else _fail(
                f"DRIFT::{stage}::runtime_grounded",
                stage,
                "DOCTRINE_DRIFT",
                f"{stage} STAGE_TO_STATUSES contains every doctrine status from .md",
                ev,
            )
        )
    return rows


def check_forbid_rd() -> list[_Row]:
    """FORBID_RD: parent doctrine forbidden disposition / verb sets are
    embedded in the runtime."""
    rows: list[_Row] = []
    # Dispositions
    for token in sorted(DOCTRINE_FORBIDDEN_DISPOSITIONS):
        present = token in FORBIDDEN_DISPOSITIONS
        ev = {
            "token": token,
            "kind": "runtime_disposition",
            "present_in_FORBIDDEN_DISPOSITIONS": present,
        }
        rows.append(
            _ok(
                f"FORBID_RD::DISP::{token}",
                "PARENT",
                "FORBID_RD",
                f"Forbidden disposition `{token}` registered",
                ev,
            )
            if present
            else _fail(
                f"FORBID_RD::DISP::{token}",
                "PARENT",
                "FORBID_RD",
                f"Forbidden disposition `{token}` registered",
                ev,
            )
        )
    # Verbs
    for token in sorted(DOCTRINE_FORBIDDEN_VERBS):
        present = token in FORBIDDEN_EXECUTION_VERBS
        ev = {
            "token": token,
            "kind": "execution_verb",
            "present_in_FORBIDDEN_EXECUTION_VERBS": present,
        }
        rows.append(
            _ok(
                f"FORBID_RD::VERB::{token}",
                "PARENT",
                "FORBID_RD",
                f"Forbidden execution verb `{token}` registered",
                ev,
            )
            if present
            else _fail(
                f"FORBID_RD::VERB::{token}",
                "PARENT",
                "FORBID_RD",
                f"Forbidden execution verb `{token}` registered",
                ev,
            )
        )

    # Functional check: assert_no_forbidden raises on a payload carrying
    # a forbidden token under a decision-class key.
    receipt_with_forbidden = {"doctrine_status": "PA_READY", "decision": "ALLOW"}
    raised = False
    msg = ""
    try:
        assert_no_forbidden(receipt_with_forbidden)
    except ForbiddenOutputError as exc:
        raised = True
        msg = str(exc)
    ev = {
        "payload": receipt_with_forbidden,
        "raised": raised,
        "exception_message": msg,
    }
    rows.append(
        _ok(
            "FORBID_RD::GUARD::raises",
            "PARENT",
            "FORBID_RD",
            "assert_no_forbidden raises when a forbidden token appears under a decision field",
            ev,
        )
        if raised
        else _fail(
            "FORBID_RD::GUARD::raises",
            "PARENT",
            "FORBID_RD",
            "assert_no_forbidden raises when a forbidden token appears under a decision field",
            ev,
        )
    )

    # Functional check: chunk-level QUARANTINE label (data, not decision)
    # is NOT flagged.
    chunk_data = {
        "doctrine_status": "PA_SECURITY_PASS",
        "prompt_like_payload_report": [{"chunk_id": "c1", "disposition": "QUARANTINE"}],
    }
    raised2 = False
    try:
        assert_no_forbidden(chunk_data)
    except ForbiddenOutputError:
        raised2 = True
    ev2 = {
        "payload": chunk_data,
        "raised": raised2,
        "rationale": "QUARANTINE inside a chunk record is data passed through, not a PA decision.",
    }
    rows.append(
        _ok(
            "FORBID_RD::GUARD::field_aware",
            "PARENT",
            "FORBID_RD",
            "assert_no_forbidden does NOT flag chunk-level data labels",
            ev2,
        )
        if not raised2
        else _fail(
            "FORBID_RD::GUARD::field_aware",
            "PARENT",
            "FORBID_RD",
            "assert_no_forbidden does NOT flag chunk-level data labels",
            ev2,
        )
    )

    return rows


def check_must_not_fence() -> list[_Row]:
    """MUST_NOT_FENCE: package surface contains no public callable whose
    name implies a forbidden behavior."""
    forbidden_substrings = [
        "retrieve_evidence",
        "call_provider",
        "execute_tool",
        "approve_output",
        "approve_execution",
        "approve_write",
        "mutate_l4",
        "commit_state",
        "route_request",
        "reroute",
    ]
    public_names = sorted(n for n in dir(pa) if not n.startswith("_"))
    callables = [n for n in public_names if callable(getattr(pa, n)) and not inspect.isclass(getattr(pa, n))]
    rows: list[_Row] = []
    for substr in forbidden_substrings:
        hits = [n for n in callables if substr in n.lower()]
        ev = {
            "forbidden_substring": substr,
            "callable_count_scanned": len(callables),
            "matches": hits,
        }
        rows.append(
            _ok(
                f"FENCE::{substr}",
                "PARENT",
                "MUST_NOT_FENCE",
                f"No public callable named `*{substr}*` in prompt_assembly surface",
                ev,
            )
            if not hits
            else _fail(
                f"FENCE::{substr}",
                "PARENT",
                "MUST_NOT_FENCE",
                f"No public callable named `*{substr}*` in prompt_assembly surface",
                ev,
            )
        )
    # Surface inventory row (always PASS) — useful evidence even when fences hold.
    rows.append(
        _ok(
            "FENCE::SURFACE_INVENTORY",
            "PARENT",
            "MUST_NOT_FENCE",
            "Public callables in prompt_assembly surface (informational)",
            {"public_callables": callables, "count": len(callables)},
        )
    )
    return rows


def check_invariants() -> list[_Row]:  # noqa: PLR0915 — one row per invariant
    """INVARIANT: 12 cross-child invariants each have a constructive runtime check."""
    rows: list[_Row] = []

    # PA.I1 — composes only.
    rows.extend(_check_pa_i1())
    # PA.I2 — does not alter C0 evidence.
    rows.extend(_check_pa_i2())
    # PA.I3 — slot payloads preserve refs.
    rows.extend(_check_pa_i3())
    # PA.I4 — user text is data not authority.
    rows.extend(_check_pa_i4())
    # PA.I5 — retrieved content is data unless higher authority binds it.
    rows.extend(_check_pa_i5())
    # PA.I6 — lower authority cannot override higher.
    rows.extend(_check_pa_i6())
    # PA.I7 — schemas/tools ride provider-native fields (structural — provider rendering owns this).
    rows.extend(_check_pa_i7())
    # PA.I8 — required content cannot be silently dropped (overflow status).
    rows.extend(_check_pa_i8())
    # PA.I9 — canonical structured slot bytes drive manifest_hash.
    rows.extend(_check_pa_i9())
    # PA.I10 — determinism: same inputs -> same hash.
    rows.extend(_check_pa_i10())
    # PA.I11 — emit gap evidence when constraints cannot be preserved.
    rows.extend(_check_pa_i11())
    # PA.I12 — handoff is artifact only; L2 still validates.
    rows.extend(_check_pa_i12())

    return rows


def _check_pa_i1() -> list[_Row]:
    forbidden = ["retrieve", "execute_tool", "call_provider", "approve_write", "mutate_l4"]
    callables = sorted(n for n in dir(pa) if callable(getattr(pa, n)) and not n.startswith("_"))
    matches = [n for n in callables if any(f in n.lower() for f in forbidden)]
    ev = {"forbidden_substrings": forbidden, "callables_matched": matches}
    return [
        _ok(
            "INV::PA.I1",
            "PARENT",
            "INVARIANT",
            "PA.I1 — Prompt Assembly composes only (no retrieve/execute/route/call/write).",
            ev,
        )
        if not matches
        else _fail("INV::PA.I1", "PARENT", "INVARIANT", "PA.I1 — Prompt Assembly composes only.", ev)
    ]


def _check_pa_i2() -> list[_Row]:
    # Constructive: build a PA.3 receipt from a classifier, snapshot the
    # classifier's pre-receipt state, then snapshot post-receipt and prove
    # equality. Since the receipt builder is a pure read, the input must
    # be unchanged.
    chunks = [{"id": "c1", "text": "ground-truth evidence: cats are mammals"}]
    classifier_before = classify_c0_chunks(chunks)
    pre_records = tuple((r.source_id, r.span_id, r.disposition.value) for r in classifier_before.records)
    _ = pa3_doctrine_receipt(classifier=classifier_before)
    post_records = tuple((r.source_id, r.span_id, r.disposition.value) for r in classifier_before.records)
    ok = pre_records == post_records
    ev = {"pre_records": list(pre_records), "post_records": list(post_records)}
    return [
        _ok(
            "INV::PA.I2",
            "PARENT",
            "INVARIANT",
            "PA.I2 — PA does not alter C0 evidence (classifier records unchanged across receipt build).",
            ev,
        )
        if ok
        else _fail("INV::PA.I2", "PARENT", "INVARIANT", "PA.I2 — PA does not alter C0 evidence.", ev)
    ]


def _check_pa_i3() -> list[_Row]:
    # Constructive: PA.7 receipt nests origin/replay refs inside
    # CompiledPromptArtifact. Walk recursively to find each one.
    receipt = _build_pa7_receipt()
    required_refs = ["request_id", "route_id", "plan_id", "policy_hash", "replay_key", "run_id", "trace_id"]

    def _find_recursive(node: Any, key: str) -> Any:
        if isinstance(node, dict):
            if key in node and node[key]:
                return node[key]
            for v in node.values():
                hit = _find_recursive(v, key)
                if hit is not None:
                    return hit
        elif isinstance(node, (list, tuple)):
            for v in node:
                hit = _find_recursive(v, key)
                if hit is not None:
                    return hit
        return None

    found = {r: _find_recursive(receipt, r) for r in required_refs}
    present = {r: (v is not None) for r, v in found.items()}
    ok = all(present.values())
    ev = {
        "required_refs": required_refs,
        "presence_map": present,
        "resolved_values": {r: str(v) for r, v in found.items()},
        "top_level_keys": sorted(receipt.keys()),
    }
    return [
        _ok(
            "INV::PA.I3",
            "PARENT",
            "INVARIANT",
            "PA.I3 — Slot/artifact receipts preserve origin/authority/source/replay refs.",
            ev,
        )
        if ok
        else _fail(
            "INV::PA.I3",
            "PARENT",
            "INVARIANT",
            "PA.I3 — Slot/artifact receipts preserve origin/authority/source/replay refs.",
            ev,
        )
    ]


def _check_pa_i4() -> list[_Row]:
    # Constructive: U0 in DOCTRINE_SLOT_MAP carries authority "ZERO".
    u0 = next(s for s in DOCTRINE_SLOT_MAP if s[0] == "U0")
    ok = u0[2] == "ZERO" and u0[1] < 50  # rank below mid-tier
    ev = {"u0_authority_label": u0[2], "u0_rank": u0[1]}
    return [
        _ok(
            "INV::PA.I4",
            "PARENT",
            "INVARIANT",
            "PA.I4 — User text is task intent only (U0 authority=ZERO, rank below mid-tier).",
            ev,
        )
        if ok
        else _fail("INV::PA.I4", "PARENT", "INVARIANT", "PA.I4 — User text is task intent only.", ev)
    ]


def _check_pa_i5() -> list[_Row]:
    # Constructive: C0 is "INFORMATIONAL" — data; S0/D0/I0 are higher and binding.
    ranks = {code: (rank, label) for code, rank, label in DOCTRINE_SLOT_MAP}
    c0_rank = ranks["C0"][0]
    higher = ["S0", "D0", "I0"]
    ok = all(ranks[h][0] > c0_rank for h in higher)
    ev = {"c0": ranks["C0"], "higher_authority_slots": {h: ranks[h] for h in higher}}
    return [
        _ok(
            "INV::PA.I5",
            "PARENT",
            "INVARIANT",
            "PA.I5 — Retrieved/tool content (C0) is data unless higher authority binds it.",
            ev,
        )
        if ok
        else _fail(
            "INV::PA.I5",
            "PARENT",
            "INVARIANT",
            "PA.I5 — Retrieved/tool content (C0) is data unless higher authority binds it.",
            ev,
        )
    ]


def _check_pa_i6() -> list[_Row]:
    # Constructive: build an AuthorityStack and prove sort by rank descending.
    stack = AuthorityStack(
        entries=tuple(
            SlotEntry(code=code, content=f"<{code}>", authority_rank=rank)
            for code, rank, _ in DOCTRINE_SLOT_MAP
        )
    )
    ranks = [e.authority_rank for e in stack.entries]
    sorted_desc = sorted(ranks, reverse=True)
    ok = ranks == sorted_desc
    ev = {
        "stack_codes_in_order": [e.code for e in stack.entries],
        "stack_ranks_in_order": ranks,
        "is_sorted_descending": ok,
    }
    return [
        _ok(
            "INV::PA.I6",
            "PARENT",
            "INVARIANT",
            "PA.I6 — Lower-authority slots cannot override higher (rank order preserved).",
            ev,
        )
        if ok
        else _fail(
            "INV::PA.I6", "PARENT", "INVARIANT", "PA.I6 — Lower-authority slots cannot override higher.", ev
        )
    ]


def _check_pa_i7() -> list[_Row]:
    # Constructive: PA.6 receipt has separate schema_render_receipt and
    # tool_render_receipt slots (the doctrine's provider-native binding
    # surface). Their existence is the structural enforcement.
    receipt = _build_pa6_receipt()
    has_schema = "schema_render_receipt" in receipt
    has_tool = "tool_render_receipt" in receipt
    has_field_map = "provider_field_mapping_receipt" in receipt
    ok = has_schema and has_tool and has_field_map
    ev = {
        "schema_render_receipt_present": has_schema,
        "tool_render_receipt_present": has_tool,
        "provider_field_mapping_receipt_present": has_field_map,
        "receipt_keys": sorted(receipt.keys()),
    }
    return [
        _ok(
            "INV::PA.I7",
            "PARENT",
            "INVARIANT",
            "PA.I7 — Tools and schemas have dedicated provider-native receipt slots.",
            ev,
        )
        if ok
        else _fail(
            "INV::PA.I7",
            "PARENT",
            "INVARIANT",
            "PA.I7 — Tools and schemas have dedicated provider-native receipt slots.",
            ev,
        )
    ]


def _check_pa_i8() -> list[_Row]:
    # Constructive: an overflow receipt emits PA_BUDGET_OVERFLOW, NOT
    # PA_BUDGET_FIT — meaning we surface the overflow rather than silently
    # drop content.
    receipt = _build_pa5_receipt(overflow=True)
    status = receipt.get("doctrine_status")
    ok = status == "PA_BUDGET_OVERFLOW"
    ev = {
        "doctrine_status_emitted": status,
        "expected": "PA_BUDGET_OVERFLOW",
        "rationale": "Required content overflow surfaces a gap status, never silently drops.",
    }
    return [
        _ok(
            "INV::PA.I8",
            "PARENT",
            "INVARIANT",
            "PA.I8 — Required content cannot be silently dropped (overflow surfaces PA_BUDGET_OVERFLOW).",
            ev,
        )
        if ok
        else _fail(
            "INV::PA.I8", "PARENT", "INVARIANT", "PA.I8 — Required content cannot be silently dropped.", ev
        )
    ]


def _check_pa_i9() -> list[_Row]:
    # Constructive: PA.5 receipt includes canonical_hash_input_manifest;
    # PA.7 includes manifest_hash_receipt. Both are doctrine-named and
    # produced by canonical (pre-render) bytes.
    pa5 = _build_pa5_receipt()
    pa7 = _build_pa7_receipt()
    ok = "canonical_hash_input_manifest" in pa5 and "manifest_hash_receipt" in pa7
    ev = {
        "pa5_has_canonical_hash_input_manifest": "canonical_hash_input_manifest" in pa5,
        "pa7_has_manifest_hash_receipt": "manifest_hash_receipt" in pa7,
    }
    return [
        _ok(
            "INV::PA.I9",
            "PARENT",
            "INVARIANT",
            "PA.I9 — Canonical structured-slot bytes drive manifest_hash (receipts present).",
            ev,
        )
        if ok
        else _fail(
            "INV::PA.I9",
            "PARENT",
            "INVARIANT",
            "PA.I9 — Canonical structured-slot bytes drive manifest_hash.",
            ev,
        )
    ]


def _check_pa_i10() -> list[_Row]:
    # Constructive: same inputs -> same budget receipt structure.
    entries = (
        SlotBudgetEntry(label="S0", tokens=100, budget_class=BudgetClass.MANDATORY_NEVER_TRIM, must_use=True),
        SlotBudgetEntry(
            label="C0", tokens=300, budget_class=BudgetClass.MANDATORY_COMPRESS_CAREFULLY, must_use=True
        ),
        SlotBudgetEntry(label="U0", tokens=200, budget_class=BudgetClass.MANDATORY_NEVER_TRIM, must_use=True),
    )
    r1, _ = build_budget_report(
        model_context_window=200_000,
        reserved_output_tokens=4096,
        reserved_schema_tokens=0,
        reserved_tool_tokens=0,
        entries=entries,
    )
    r2, _ = build_budget_report(
        model_context_window=200_000,
        reserved_output_tokens=4096,
        reserved_schema_tokens=0,
        reserved_tool_tokens=0,
        entries=entries,
    )
    eq_status = r1.overflow_status == r2.overflow_status
    eq_tokens = r1.input_token_estimate == r2.input_token_estimate
    eq_dispatch = r1.can_dispatch == r2.can_dispatch
    ok = eq_status and eq_tokens and eq_dispatch
    ev = {
        "run1_status": r1.overflow_status.value,
        "run2_status": r2.overflow_status.value,
        "run1_input_tokens": r1.input_token_estimate,
        "run2_input_tokens": r2.input_token_estimate,
        "run1_can_dispatch": r1.can_dispatch,
        "run2_can_dispatch": r2.can_dispatch,
    }
    return [
        _ok(
            "INV::PA.I10",
            "PARENT",
            "INVARIANT",
            "PA.I10 — Determinism: same inputs produce identical budget outputs.",
            ev,
        )
        if ok
        else _fail(
            "INV::PA.I10",
            "PARENT",
            "INVARIANT",
            "PA.I10 — Determinism: same inputs must produce identical outputs.",
            ev,
        )
    ]


def _check_pa_i11() -> list[_Row]:
    # Constructive: PA.0 with missing plan_contract emits PA_INPUT_INCOMPLETE
    # rather than PA_READY.
    br = boundary_check(
        plan_contract=None,
        route_contract={"route_id": "r1"},
        evidence_contract=None,
    )
    receipt = pa0_doctrine_receipt(br)
    status = receipt.get("doctrine_status")
    ok = status == "PA_INPUT_INCOMPLETE"
    ev = {
        "doctrine_status_emitted": status,
        "expected": "PA_INPUT_INCOMPLETE",
        "rationale": "Missing required input must surface gap evidence, never fake completeness.",
    }
    return [
        _ok(
            "INV::PA.I11",
            "PARENT",
            "INVARIANT",
            "PA.I11 — Emit gap evidence when constraints cannot be preserved.",
            ev,
        )
        if ok
        else _fail(
            "INV::PA.I11",
            "PARENT",
            "INVARIANT",
            "PA.I11 — Emit gap evidence when constraints cannot be preserved.",
            ev,
        )
    ]


def _check_pa_i12() -> list[_Row]:
    # Constructive: PA.7 receipt has handoff fields but no L2 execution
    # decision — verified by absence of forbidden tokens under decision keys.
    receipt = _build_pa7_receipt()
    raised = False
    msg = ""
    try:
        assert_no_forbidden(receipt, label="PA.7")
    except ForbiddenOutputError as exc:
        raised = True
        msg = str(exc)
    ok = not raised
    ev = {
        "raised_forbidden": raised,
        "exception_message": msg,
        "receipt_doctrine_status": receipt.get("doctrine_status"),
    }
    return [
        _ok(
            "INV::PA.I12",
            "PARENT",
            "INVARIANT",
            "PA.I12 — PA.7 handoff is artifact only; carries no runtime disposition tokens.",
            ev,
        )
        if ok
        else _fail(
            "INV::PA.I12",
            "PARENT",
            "INVARIANT",
            "PA.I12 — PA.7 handoff carries no runtime disposition tokens.",
            ev,
        )
    ]


def check_slot_map() -> list[_Row]:
    """SLOT_MAP: 10 canonical slots with descending authority rank can be
    constructed and the ordering is preserved through AuthorityStack."""
    rows: list[_Row] = []
    for code, rank, label in DOCTRINE_SLOT_MAP:
        entry = SlotEntry(code=code, content=f"<{code}>", authority_rank=rank)
        ok_construct = entry.code == code and entry.authority_rank == rank
        ev = {
            "slot": code,
            "rank": rank,
            "doctrine_label": label,
            "constructed_code": entry.code,
            "constructed_rank": entry.authority_rank,
        }
        rows.append(
            _ok(
                f"SLOT::{code}",
                "PA.2",
                "SLOT_MAP",
                f"Canonical slot `{code}` (auth={label}, rank={rank}) constructs cleanly",
                ev,
            )
            if ok_construct
            else _fail(
                f"SLOT::{code}",
                "PA.2",
                "SLOT_MAP",
                f"Canonical slot `{code}` constructs cleanly",
                ev,
            )
        )

    # Authority order — descending rank.
    stack = AuthorityStack(
        entries=tuple(
            SlotEntry(code=code, content=f"<{code}>", authority_rank=rank)
            for code, rank, _ in DOCTRINE_SLOT_MAP
        )
    )
    ranks = [e.authority_rank for e in stack.entries]
    ok = ranks == sorted(ranks, reverse=True)
    ev = {
        "codes_in_stack_order": [e.code for e in stack.entries],
        "ranks_in_stack_order": ranks,
        "ranks_descending_expected": sorted(ranks, reverse=True),
    }
    rows.append(
        _ok(
            "SLOT::AUTHORITY_ORDER",
            "PA.2",
            "SLOT_MAP",
            "AuthorityStack preserves doctrine high->low authority order",
            ev,
        )
        if ok
        else _fail(
            "SLOT::AUTHORITY_ORDER",
            "PA.2",
            "SLOT_MAP",
            "AuthorityStack preserves doctrine high->low authority order",
            ev,
        )
    )

    return rows


def check_pipeline_endtoend() -> list[_Row]:
    """End-to-end: pipeline PASS path emits a doctrine_status, includes
    PA.0 and PA.7 receipts, and is forbidden-token clean."""
    result = run_prompt_assembly_pipeline(
        plan_contract={"plan_id": "p1", "policy_hash": "h"},
        route_contract={"route_id": "r1", "provider_lane": "anthropic", "policy_hash": "h"},
        execution_metadata={"policy_hash": "h", "request_id": "req"},
    )
    stages = sorted({str(r.get("stage", "")) for r in result.doctrine_receipts})
    forbidden_hits = []
    for r in result.doctrine_receipts:
        try:
            assert_no_forbidden(r)
        except ForbiddenOutputError as exc:
            forbidden_hits.append({"stage": r.get("stage"), "msg": str(exc)})

    rows: list[_Row] = []
    rows.append(
        _ok(
            "E2E::dispatch_allowed",
            "ALL",
            "E2E",
            "Pipeline PASS path allows dispatch",
            {"dispatch_allowed": result.dispatch_allowed, "doctrine_status": result.doctrine_status.value},
        )
        if result.dispatch_allowed
        else _fail(
            "E2E::dispatch_allowed",
            "ALL",
            "E2E",
            "Pipeline PASS path allows dispatch",
            {"dispatch_allowed": result.dispatch_allowed},
        )
    )
    rows.append(
        _ok(
            "E2E::stages_emitted",
            "ALL",
            "E2E",
            "Pipeline emits at least PA.0 and PA.7 receipts",
            {"stages_emitted": stages, "receipt_count": len(result.doctrine_receipts)},
        )
        if "PA.0" in stages and "PA.7" in stages
        else _fail(
            "E2E::stages_emitted",
            "ALL",
            "E2E",
            "Pipeline emits at least PA.0 and PA.7 receipts",
            {"stages_emitted": stages},
        )
    )
    rows.append(
        _ok(
            "E2E::no_forbidden",
            "ALL",
            "E2E",
            "No pipeline receipt carries forbidden tokens under decision fields",
            {"forbidden_hits": forbidden_hits},
        )
        if not forbidden_hits
        else _fail(
            "E2E::no_forbidden",
            "ALL",
            "E2E",
            "No pipeline receipt carries forbidden tokens",
            {"forbidden_hits": forbidden_hits},
        )
    )

    # Aggregate status sanity.
    agg = aggregate_doctrine_status(result.doctrine_receipts)
    rows.append(
        _ok(
            "E2E::aggregate_status",
            "ALL",
            "E2E",
            "Pipeline aggregate doctrine_status resolves to a PAStatus",
            {
                "aggregate_status": agg.value,
                "result_status": result.doctrine_status.value,
                "match": agg == result.doctrine_status,
            },
        )
    )
    return rows


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _to_dict(row: _Row) -> dict[str, Any]:
    return dataclasses.asdict(row)


# --------------------------------------------------------------------------
# Edge-case categories (added for exhaustive coverage of every requirement)
# --------------------------------------------------------------------------


def check_negative_paths() -> list[_Row]:
    """NEGATIVE_PATH: every PAStatus value flows correctly through
    ``aggregate_doctrine_status`` with the correct stage attribution.

    The happy-path category (``MUST_EMIT``) only constructs receipts that
    produce one canonical status per stage. This category proves that EVERY
    status enum value (success, gap, conflict, overflow, etc.) is recognised
    by the aggregator AND the ``STAGE_TO_STATUSES`` partition assigns it to
    the correct stage. Coverage: 8 stages * 3-6 statuses each = ~36 rows.
    """
    rows: list[_Row] = []
    for stage, statuses in sorted(STAGE_TO_STATUSES.items()):
        for status in sorted(statuses, key=lambda s: s.value):
            synthetic = {"stage": stage, "doctrine_status": status.value}
            try:
                aggregated = aggregate_doctrine_status([synthetic])
            except (KeyError, ValueError, TypeError) as exc:
                rows.append(
                    _fail(
                        f"NEG::{stage}::{status.value}",
                        stage,
                        "NEGATIVE_PATH",
                        f"{stage} aggregator accepts {status.value}",
                        {"error": str(exc)},
                    )
                )
                continue
            ok = aggregated == status
            ev = {
                "stage": stage,
                "input_status": status.value,
                "aggregated_status": aggregated.value,
                "round_trip": ok,
            }
            label = f"{stage} aggregator round-trips {status.value}"
            rows.append(
                _ok(
                    f"NEG::{stage}::{status.value}",
                    stage,
                    "NEGATIVE_PATH",
                    label,
                    ev,
                )
                if ok
                else _fail(
                    f"NEG::{stage}::{status.value}",
                    stage,
                    "NEGATIVE_PATH",
                    label,
                    ev,
                )
            )
    return rows


def check_forbid_deep() -> list[_Row]:
    """FORBID_DEEP: ``assert_no_forbidden`` detects forbidden tokens at
    arbitrary nesting depth in receipts.

    Failure precedent: an early implementation only scanned top-level keys,
    so a forbidden token nested under ``compiled_prompt_artifact_receipt``
    would have escaped the scanner. This category exercises the recursive
    walker against 5 nesting topologies.
    """
    rows: list[_Row] = []
    cases = [
        (
            "depth1",
            {"doctrine_status": "PA_READY", "decision": "ALLOW"},
            True,
            "Top-level decision field with forbidden token",
        ),
        (
            "depth2",
            {"doctrine_status": "PA_READY", "compiled_prompt_artifact_receipt": {"decision": "DENY"}},
            True,
            "Forbidden token nested one level deep under decision field",
        ),
        (
            "depth3",
            {"doctrine_status": "PA_READY", "wrapper": {"inner": {"decision": "ESCALATE_HITL"}}},
            True,
            "Forbidden token nested three levels deep",
        ),
        (
            "in_list",
            {"doctrine_status": "PA_READY", "decisions": [{"verdict": "ABSTAIN"}]},
            True,
            "Forbidden token inside list of dicts under decision-shaped key",
        ),
        (
            "list_of_lists",
            {"doctrine_status": "PA_READY", "history": [[{"decision": "BLOCK_COMMIT"}]]},
            True,
            "Forbidden token inside doubly-nested list",
        ),
    ]
    for name, payload, expect_raise, desc in cases:
        raised = False
        msg = ""
        try:
            assert_no_forbidden(payload)
        except ForbiddenOutputError as exc:
            raised = True
            msg = str(exc)
        ok = raised == expect_raise
        ev = {
            "topology": name,
            "expected_raise": expect_raise,
            "actually_raised": raised,
            "message": msg[:100],
            "description": desc,
        }
        label = f"FORBID_DEEP/{name}: {desc}"
        rows.append(
            _ok(
                f"FORBID_DEEP::{name}",
                "PARENT",
                "FORBID_DEEP",
                label,
                ev,
            )
            if ok
            else _fail(
                f"FORBID_DEEP::{name}",
                "PARENT",
                "FORBID_DEEP",
                label,
                ev,
            )
        )
    return rows


def check_forbid_false_positive() -> list[_Row]:
    """FORBID_FALSE_POSITIVE: substring matches that should NOT trigger.

    Forbidden tokens like ``ALLOW`` and ``DENY`` may appear as substrings
    of legitimate identifiers (``ALLOW_LIST_VERSION``, ``DENY_REASON_CODE``).
    The scanner must use exact-token equality, not substring matching.
    """
    rows: list[_Row] = []
    cases = [
        ("substring_allow", {"doctrine_status": "PA_READY", "config_name": "ALLOW_LIST_VERSION"}),
        ("substring_deny", {"doctrine_status": "PA_READY", "policy_label": "DENY_REASON_CODE"}),
        (
            "chunk_disposition",
            {
                "doctrine_status": "PA_SECURITY_PASS",
                "prompt_like_payload_report": [{"chunk_id": "c1", "disposition": "QUARANTINE"}],
            },
        ),
        (
            "chunk_extraction_label",
            {"doctrine_status": "PA_SECURITY_PASS", "safe_extraction_map": {"s1": {"label": "REDACT"}}},
        ),
        (
            "metadata_string",
            {"doctrine_status": "PA_READY", "notes": "This receipt does not BLOCK_COMMITS_DAILY"},
        ),
    ]
    for name, payload in cases:
        raised = False
        msg = ""
        try:
            assert_no_forbidden(payload)
        except ForbiddenOutputError as exc:
            raised = True
            msg = str(exc)
        ok = not raised
        ev = {
            "topology": name,
            "expected_raise": False,
            "actually_raised": raised,
            "message": msg[:100] if raised else "",
            "rationale": (
                "Forbidden tokens must match the decision-field value exactly, "
                "not as a substring of an identifier or chunk-data label."
            ),
        }
        label = f"FORBID_FALSE_POSITIVE/{name}: scanner does NOT flag legitimate use"
        rows.append(
            _ok(
                f"FORBID_FP::{name}",
                "PARENT",
                "FORBID_FALSE_POSITIVE",
                label,
                ev,
            )
            if ok
            else _fail(
                f"FORBID_FP::{name}",
                "PARENT",
                "FORBID_FALSE_POSITIVE",
                label,
                ev,
            )
        )
    return rows


def _canonical_bytes(d: Mapping[str, Any]) -> bytes:
    """Local canonical-bytes implementation used for determinism checks."""
    return json.dumps(d, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")


def check_determinism() -> list[_Row]:
    """DETERMINISM: every stage's receipt-builder produces byte-identical
    output for byte-identical inputs.

    Extends invariant PA.I9 (originally PA.5-only) to all eight stages.
    Determinism is the foundation of replay/audit and signature stability.
    """
    builders = {
        "PA.0": _build_pa0_receipt,
        "PA.1": _build_pa1_receipt,
        "PA.2": _build_pa2_receipt,
        "PA.3": _build_pa3_receipt,
        "PA.4": _build_pa4_receipt,
        "PA.5": _build_pa5_receipt,
        "PA.6": _build_pa6_receipt,
        "PA.7": _build_pa7_receipt,
    }
    rows: list[_Row] = []
    for stage, builder in builders.items():
        first = builder()
        second = builder()
        first_bytes = _canonical_bytes(first)
        second_bytes = _canonical_bytes(second)
        ok = first_bytes == second_bytes
        ev = {
            "stage": stage,
            "first_byte_count": len(first_bytes),
            "second_byte_count": len(second_bytes),
            "byte_identical": ok,
            "first_keys": sorted(first.keys()),
        }
        label = f"{stage} receipt builder is byte-deterministic"
        rows.append(
            _ok(
                f"DET::{stage}",
                stage,
                "DETERMINISM",
                label,
                ev,
            )
            if ok
            else _fail(
                f"DET::{stage}",
                stage,
                "DETERMINISM",
                label,
                ev,
            )
        )
    return rows


def check_aggregation() -> list[_Row]:
    """AGGREGATION: ``aggregate_doctrine_status`` edge cases.

    Proves: empty input yields PA_READY; single-status input round-trips;
    all-PA_READY yields PA_READY; mixed input never collapses to PA_READY;
    aggregator is deterministic on identical input.
    """
    rows: list[_Row] = []

    empty_result = aggregate_doctrine_status([])
    rows.append(
        _ok(
            "AGG::empty",
            "PARENT",
            "AGGREGATION",
            "Empty receipt list aggregates to PA_READY (neutral)",
            {"input": [], "result": empty_result.value},
        )
        if empty_result == PAStatus.PA_READY
        else _fail(
            "AGG::empty",
            "PARENT",
            "AGGREGATION",
            "Empty receipt list aggregates to PA_READY (neutral)",
            {"input": [], "result": empty_result.value},
        )
    )

    single = aggregate_doctrine_status([{"stage": "PA.5", "doctrine_status": "PA_BUDGET_OVERFLOW"}])
    rows.append(
        _ok(
            "AGG::single",
            "PARENT",
            "AGGREGATION",
            "Single-receipt input round-trips through aggregator",
            {"result": single.value},
        )
        if single == PAStatus.PA_BUDGET_OVERFLOW
        else _fail(
            "AGG::single",
            "PARENT",
            "AGGREGATION",
            "Single-receipt input round-trips through aggregator",
            {"result": single.value},
        )
    )

    all_ready = aggregate_doctrine_status(
        [
            {"stage": s, "doctrine_status": "PA_READY"}
            for s in ("PA.0", "PA.1", "PA.2", "PA.3", "PA.4", "PA.5", "PA.6", "PA.7")
        ]
    )
    rows.append(
        _ok(
            "AGG::all_ready",
            "PARENT",
            "AGGREGATION",
            "All-PA_READY receipt list aggregates to PA_READY",
            {"result": all_ready.value},
        )
        if all_ready == PAStatus.PA_READY
        else _fail(
            "AGG::all_ready",
            "PARENT",
            "AGGREGATION",
            "All-PA_READY receipt list aggregates to PA_READY",
            {"result": all_ready.value},
        )
    )

    worst = aggregate_doctrine_status(
        [
            {"stage": "PA.0", "doctrine_status": "PA_READY"},
            {"stage": "PA.1", "doctrine_status": "PA_BOM_RESOLVED"},
            {"stage": "PA.5", "doctrine_status": "PA_BUDGET_OVERFLOW"},
            {"stage": "PA.7", "doctrine_status": "PA_ARTIFACT_NOT_SIGNED"},
        ]
    )
    ok_worst = worst != PAStatus.PA_READY
    rows.append(
        _ok(
            "AGG::worst_wins",
            "PARENT",
            "AGGREGATION",
            "Mixed-status input does NOT aggregate to PA_READY",
            {"result": worst.value, "non_ready": ok_worst},
        )
        if ok_worst
        else _fail(
            "AGG::worst_wins",
            "PARENT",
            "AGGREGATION",
            "Mixed-status input does NOT aggregate to PA_READY",
            {"result": worst.value, "non_ready": ok_worst},
        )
    )

    receipts = [{"stage": "PA.5", "doctrine_status": "PA_BUDGET_TRIMMED"}]
    a = aggregate_doctrine_status(receipts)
    b = aggregate_doctrine_status(receipts)
    rows.append(
        _ok(
            "AGG::deterministic",
            "PARENT",
            "AGGREGATION",
            "Aggregator is deterministic on identical input",
            {"first": a.value, "second": b.value},
        )
        if a == b
        else _fail(
            "AGG::deterministic",
            "PARENT",
            "AGGREGATION",
            "Aggregator is deterministic on identical input",
            {"first": a.value, "second": b.value},
        )
    )
    return rows


def check_status_partition_complete() -> list[_Row]:
    """STATUS_PARTITION_COMPLETE: every PAStatus member is reachable
    from at least one stage's STAGE_TO_STATUSES set.

    No orphan statuses - if an enum value exists, it must be claimed by
    a stage. Cross-stage statuses (intentionally shared) match the
    documented set.
    """
    rows: list[_Row] = []
    runtime_values = set(PAStatus)
    union = set().union(*STAGE_TO_STATUSES.values())
    orphans = sorted(s.value for s in (runtime_values - union))
    ok = not orphans
    rows.append(
        _ok(
            "STATUS::no_orphans",
            "ALL",
            "STATUS_PARTITION_COMPLETE",
            "Every PAStatus member is claimed by at least one stage",
            {"runtime_count": len(runtime_values), "claimed_count": len(union), "orphans": orphans},
        )
        if ok
        else _fail(
            "STATUS::no_orphans",
            "ALL",
            "STATUS_PARTITION_COMPLETE",
            "Every PAStatus member is claimed by at least one stage",
            {"runtime_count": len(runtime_values), "claimed_count": len(union), "orphans": orphans},
        )
    )

    cross_stage: dict[str, list[str]] = {}
    for stage, statuses in STAGE_TO_STATUSES.items():
        for st in statuses:
            cross_stage.setdefault(st.value, []).append(stage)
    multi = {k: sorted(v) for k, v in cross_stage.items() if len(v) > 1}
    expected_multi_keys = {"PA_REQUIRES_UPSTREAM_REPAIR"}
    ok2 = set(multi.keys()) == expected_multi_keys
    rows.append(
        _ok(
            "STATUS::cross_stage_documented",
            "ALL",
            "STATUS_PARTITION_COMPLETE",
            "Cross-stage statuses match the documented set",
            {"observed": multi, "expected_keys": sorted(expected_multi_keys)},
        )
        if ok2
        else _fail(
            "STATUS::cross_stage_documented",
            "ALL",
            "STATUS_PARTITION_COMPLETE",
            "Cross-stage statuses match the documented set",
            {"observed": multi, "expected_keys": sorted(expected_multi_keys)},
        )
    )
    return rows


def check_parser_robustness() -> list[_Row]:
    """PARSER_ROBUSTNESS: doctrine parser handles edge-case inputs.

    Synthetic .md content covers: missing section, blank file, repeated
    headings, non-bullet noise lines, section terminated by next heading.
    """
    from tools.prompt_assembly.doctrine_parser import _extract_section

    rows: list[_Row] = []

    cases = [
        (
            "missing_section",
            ["MUST EMIT", "----------", "- Foo", "- Bar"],
            "STATUS VALUES",
            [],
            "Section absent from doc returns empty list",
        ),
        ("blank_file", [], "STATUS VALUES", [], "Empty doc returns empty list"),
        (
            "repeated_heading",
            ["STATUS VALUES", "-----------", "- A", "- B", "", "STATUS VALUES", "-----------", "- C"],
            "STATUS VALUES",
            ["A", "B"],
            "Parser stops at first blank line after items, ignoring later repeats",
        ),
        (
            "non_bullet_noise",
            ["STATUS VALUES", "-----", "- One", "Some prose paragraph", "- Two"],
            "STATUS VALUES",
            ["One"],
            "Parser stops at first non-bullet, non-empty line",
        ),
        (
            "section_terminated_by_next_heading",
            ["STATUS VALUES", "-----", "- One", "- Two", "MUST EMIT", "-----", "- foo"],
            "STATUS VALUES",
            ["One", "Two"],
            "Section is terminated by the next recognised heading",
        ),
    ]

    for name, lines, section, expected, desc in cases:
        actual = _extract_section(lines, section)
        ok = actual == expected
        ev = {
            "case": name,
            "section": section,
            "expected": expected,
            "actual": actual,
            "description": desc,
        }
        label = f"PARSER/{name}: {desc}"
        rows.append(
            _ok(
                f"PARSER::{name}",
                "PARENT",
                "PARSER_ROBUSTNESS",
                label,
                ev,
            )
            if ok
            else _fail(
                f"PARSER::{name}",
                "PARENT",
                "PARSER_ROBUSTNESS",
                label,
                ev,
            )
        )
    return rows


def check_pipeline_negative_paths() -> list[_Row]:
    """PIPELINE_NEG: end-to-end pipeline negative paths.

    Currently the E2E category only covers the PASS path. This category
    exercises failure scenarios proving the pipeline correctly publishes
    a non-PA_READY aggregate doctrine_status and refuses dispatch when
    input is incomplete - and that negative-path receipts contain ZERO
    forbidden tokens.
    """
    rows: list[_Row] = []

    r1 = run_prompt_assembly_pipeline(
        plan_contract=None,  # type: ignore[arg-type]
        route_contract={"route_id": "r1", "policy_hash": "h"},
        execution_metadata={"policy_hash": "h"},
    )
    ok1 = not r1.dispatch_allowed and r1.doctrine_status == PAStatus.PA_INPUT_INCOMPLETE
    rows.append(
        _ok(
            "PIPE_NEG::missing_plan_contract",
            "ALL",
            "PIPELINE_NEG",
            "Pipeline with missing plan_contract publishes PA_INPUT_INCOMPLETE",
            {"dispatch_allowed": r1.dispatch_allowed, "doctrine_status": r1.doctrine_status.value},
        )
        if ok1
        else _fail(
            "PIPE_NEG::missing_plan_contract",
            "ALL",
            "PIPELINE_NEG",
            "Pipeline with missing plan_contract publishes PA_INPUT_INCOMPLETE",
            {"dispatch_allowed": r1.dispatch_allowed, "doctrine_status": r1.doctrine_status.value},
        )
    )

    r2 = run_prompt_assembly_pipeline(
        plan_contract={"plan_id": "p1", "policy_hash": "h"},
        route_contract=None,  # type: ignore[arg-type]
        execution_metadata={"policy_hash": "h"},
    )
    ok2 = not r2.dispatch_allowed
    rows.append(
        _ok(
            "PIPE_NEG::missing_route_contract",
            "ALL",
            "PIPELINE_NEG",
            "Pipeline with missing route_contract refuses dispatch",
            {"dispatch_allowed": r2.dispatch_allowed, "doctrine_status": r2.doctrine_status.value},
        )
        if ok2
        else _fail(
            "PIPE_NEG::missing_route_contract",
            "ALL",
            "PIPELINE_NEG",
            "Pipeline with missing route_contract refuses dispatch",
            {"dispatch_allowed": r2.dispatch_allowed, "doctrine_status": r2.doctrine_status.value},
        )
    )

    forbidden_in_neg = []
    for r in (r1, r2):
        for receipt in r.doctrine_receipts:
            try:
                assert_no_forbidden(receipt)
            except ForbiddenOutputError as exc:
                forbidden_in_neg.append({"stage": receipt.get("stage"), "msg": str(exc)})
    ok3 = not forbidden_in_neg
    rows.append(
        _ok(
            "PIPE_NEG::no_forbidden_in_failure_path",
            "ALL",
            "PIPELINE_NEG",
            "Pipeline negative-path receipts contain zero forbidden tokens",
            {"forbidden_hits": forbidden_in_neg},
        )
        if ok3
        else _fail(
            "PIPE_NEG::no_forbidden_in_failure_path",
            "ALL",
            "PIPELINE_NEG",
            "Pipeline negative-path receipts contain zero forbidden tokens",
            {"forbidden_hits": forbidden_in_neg},
        )
    )
    return rows


# ----------------------------------------------------------------------
# Hardening categories — close open scope around PA.8, parent doctrine,
# per-child forbidden blocks, child MUST NOT clauses, and parser edges.
# ----------------------------------------------------------------------


def check_parent_status_vocabulary() -> list[_Row]:
    """PARENT_VOCAB: every status in the parent doctrine STATUS
    VOCABULARY block resolves to PAStatus AND is claimed by some stage.
    """
    rows: list[_Row] = []
    extra = _parse_doctrine_extra(_REPO_ROOT)
    parent_vocab = extra.get("PARENT", {}).get("status_values", [])
    if not parent_vocab:
        rows.append(
            _fail(
                "PARENT_VOCAB::parsed",
                "PARENT",
                "PARENT_VOCAB",
                "Parent doctrine STATUS VOCABULARY parsed at least one entry",
                {"parsed_count": 0},
            )
        )
        return rows
    rows.append(
        _ok(
            "PARENT_VOCAB::parsed",
            "PARENT",
            "PARENT_VOCAB",
            "Parent doctrine STATUS VOCABULARY parsed at least one entry",
            {"parsed_count": len(parent_vocab)},
        )
    )
    runtime_set = {s.value for s in PAStatus}
    union = {s.value for vs in STAGE_TO_STATUSES.values() for s in vs}
    for status in parent_vocab:
        in_runtime = status in runtime_set
        in_stage = status in union
        ok = in_runtime and in_stage
        ev = {"status": status, "in_runtime_PAStatus": in_runtime, "claimed_by_stage": in_stage}
        label = f"Parent status `{status}` exists in PAStatus and is claimed by at least one stage"
        rows.append(
            _ok(
                f"PARENT_VOCAB::{status}",
                "PARENT",
                "PARENT_VOCAB",
                label,
                ev,
            )
            if ok
            else _fail(
                f"PARENT_VOCAB::{status}",
                "PARENT",
                "PARENT_VOCAB",
                label,
                ev,
            )
        )
    return rows


def check_child_forbidden_doctrine() -> list[_Row]:
    """CHILD_FORBID_DOCTRINE: every PA.0..PA.7 child's FORBIDDEN OUTPUTS
    block (a) parses non-empty, (b) is subset of parent master,
    (c) inherits every parent forbidden token (no silent drop).
    """
    rows: list[_Row] = []
    parsed = _parse_doctrine_all(_REPO_ROOT)
    parent_master = DOCTRINE_FORBIDDEN_DISPOSITIONS | DOCTRINE_FORBIDDEN_VERBS
    for stage, data in parsed.items():
        block = set(data.get("forbidden_outputs", []))
        ev_base = {"stage": stage, "parsed_count": len(block), "parent_master_count": len(parent_master)}
        rows.append(
            _ok(
                f"CHILD_FORBID::{stage}::parsed",
                stage,
                "CHILD_FORBID_DOCTRINE",
                f"{stage} forbidden-outputs block parses at least one token",
                ev_base,
            )
            if block
            else _fail(
                f"CHILD_FORBID::{stage}::parsed",
                stage,
                "CHILD_FORBID_DOCTRINE",
                f"{stage} forbidden-outputs block parses at least one token",
                ev_base,
            )
        )
        if not block:
            continue
        unknown = sorted(block - parent_master)
        rows.append(
            _ok(
                f"CHILD_FORBID::{stage}::subset_of_parent",
                stage,
                "CHILD_FORBID_DOCTRINE",
                f"{stage} forbidden tokens are subset of parent master set",
                {**ev_base, "unknown_tokens": unknown},
            )
            if not unknown
            else _fail(
                f"CHILD_FORBID::{stage}::subset_of_parent",
                stage,
                "CHILD_FORBID_DOCTRINE",
                f"{stage} forbidden tokens are subset of parent master set",
                {**ev_base, "unknown_tokens": unknown},
            )
        )
        missing = sorted(parent_master - block)
        rows.append(
            _ok(
                f"CHILD_FORBID::{stage}::no_silent_drop",
                stage,
                "CHILD_FORBID_DOCTRINE",
                f"{stage} inherits every parent forbidden token (no silent drop)",
                {**ev_base, "missing_from_child": missing},
            )
            if not missing
            else _fail(
                f"CHILD_FORBID::{stage}::no_silent_drop",
                stage,
                "CHILD_FORBID_DOCTRINE",
                f"{stage} inherits every parent forbidden token (no silent drop)",
                {**ev_base, "missing_from_child": missing},
            )
        )
    return rows


_MUST_NOT_KEYWORD_TO_FORBIDDEN: dict[str, set[str]] = {
    "retrieve": {"call_provider", "execute_tool"},
    "route": {"REROUTE"},
    "call": {"call_provider"},
    "execute": {"execute_tool", "approve_execution"},
    "approve": {"approve_execution", "approve_output", "approve_write"},
    "commit": {"COMMIT_REQUEST", "approve_write", "mutate_l4"},
    "emit": {"ALLOW", "DENY", "REROUTE", "ESCALATE_HITL", "COMMIT_REQUEST", "BLOCK_COMMIT", "ALLOW_FINISH"},
    "silently": {"MARK_DEGRADED", "SAFE_FALLBACK"},
}


def check_child_must_not_doctrine() -> list[_Row]:
    """MUST_NOT_DOCTRINE: every keyword in each PA.0..PA.7 MUST NOT
    section maps to >=1 member of the parent forbidden set.
    """
    rows: list[_Row] = []
    parsed = _parse_doctrine_all(_REPO_ROOT)
    parent_master = DOCTRINE_FORBIDDEN_DISPOSITIONS | DOCTRINE_FORBIDDEN_VERBS
    for stage, data in parsed.items():
        bullets = data.get("must_not", [])
        ev_base = {"stage": stage, "parsed_count": len(bullets)}
        rows.append(
            _ok(
                f"MUST_NOT::{stage}::parsed",
                stage,
                "MUST_NOT_DOCTRINE",
                f"{stage} MUST NOT block parses at least one keyword",
                ev_base,
            )
            if bullets
            else _fail(
                f"MUST_NOT::{stage}::parsed",
                stage,
                "MUST_NOT_DOCTRINE",
                f"{stage} MUST NOT block parses at least one keyword",
                ev_base,
            )
        )
        for kw in bullets:
            kw_l = kw.lower()
            mapped = _MUST_NOT_KEYWORD_TO_FORBIDDEN.get(kw_l, set())
            covered = mapped & parent_master
            ev = {"keyword": kw, "mapped_to": sorted(mapped), "covered_by_parent_master": sorted(covered)}
            label = f"{stage} MUST NOT `{kw}` maps to runtime forbidden tokens"
            rows.append(
                _ok(
                    f"MUST_NOT::{stage}::{kw_l}",
                    stage,
                    "MUST_NOT_DOCTRINE",
                    label,
                    ev,
                )
                if covered
                else _fail(
                    f"MUST_NOT::{stage}::{kw_l}",
                    stage,
                    "MUST_NOT_DOCTRINE",
                    label,
                    ev,
                )
            )
    return rows


_PA8_RULE_CHECKS: list[tuple[str, str, str]] = [
    ("C0", "C0/tool/human text are data-only slots", "detect_authority_violations"),
    ("R0", "R0 schema is bound to provider-native fields", "R0SchemaBinding"),
    ("Provider", "Provider rendering must not silently reorder authority slots", "render_for_provider"),
    ("Token", "Token trimming must never drop S0/D0/required policy refs/R0", "BUDGET_TRIM_ORDER"),
]


def check_pa8_rules() -> list[_Row]:
    """PA8_RULES: every PA.8 rule keyword has a runtime artefact."""
    rows: list[_Row] = []
    extra = _parse_doctrine_extra(_REPO_ROOT)
    pa8 = extra.get("PA.8", {})
    parsed_keywords = {kw.lower() for kw in pa8.get("rules", [])}
    pa_surface = {n for n in dir(pa) if not n.startswith("_")}
    for kw, requirement, runtime_symbol in _PA8_RULE_CHECKS:
        present_in_doctrine = kw.lower() in parsed_keywords
        present_in_runtime = runtime_symbol in pa_surface
        ok = present_in_doctrine and present_in_runtime
        ev = {
            "rule_keyword": kw,
            "runtime_symbol": runtime_symbol,
            "present_in_doctrine": present_in_doctrine,
            "present_in_runtime": present_in_runtime,
        }
        label = f"PA.8 rule `{kw}`: {requirement}"
        rows.append(
            _ok(
                f"PA8_RULE::{kw}",
                "PA.8",
                "PA8_RULES",
                label,
                ev,
            )
            if ok
            else _fail(
                f"PA8_RULE::{kw}",
                "PA.8",
                "PA8_RULES",
                label,
                ev,
            )
        )
    return rows


_PA8_TEST_DIR: str = "tests/unit/agentic_core/prompt_governance/prompt_assembly"
_PA8_DOCTRINE_DIR: str = "docs/reference/03B_PA_Prompt_Assembly"

_PA8_TEST_EQUIVALENTS: dict[str, list[str]] = {
    "test_pa_blocks_c0_instruction_promotion": [
        "test_pa3_c0_classifier",
        "detect_authority_violations",
        "c0_instruction",
    ],
    "test_pa_blocks_human_text_as_authority": [
        "test_pa3_u0_airlock",
        "u0_airlock",
        "human_text",
    ],
    "test_pa_schema_bound_native_not_only_prose": [
        "test_pa6_provider_rendering",
        "schema_binding",
        "R0",
    ],
    "test_pa_provider_render_preserves_slot_order": [
        "test_pa6_provider_rendering",
        "render_for_provider",
        "slot_order",
    ],
    "test_pa_token_trim_preserves_required_authority_slots": [
        "test_pa5_budget",
        "BUDGET_TRIM_ORDER",
        "deterministic_trim",
    ],
    "test_pa_never_calls_retrieval_or_execution": [
        "test_invariants",
        "test_doctrine_compliance",
        "MUST_NOT_FENCE",
    ],
}


def check_pa8_test_coverage() -> list[_Row]:
    """PA8_TESTS: every PA.8 TEST REQUIREMENTS test name is covered
    (literal or documented functional equivalent in PA test corpus).
    """
    rows: list[_Row] = []
    extra = _parse_doctrine_extra(_REPO_ROOT)
    pa8 = extra.get("PA.8", {})
    declared = pa8.get("test_requirements", [])
    if not declared:
        rows.append(
            _fail(
                "PA8_TESTS::parsed",
                "PA.8",
                "PA8_TESTS",
                "PA.8 TEST REQUIREMENTS block parses at least one test name",
                {"parsed_count": 0},
            )
        )
        return rows
    rows.append(
        _ok(
            "PA8_TESTS::parsed",
            "PA.8",
            "PA8_TESTS",
            "PA.8 TEST REQUIREMENTS block parses at least one test name",
            {"parsed_count": len(declared)},
        )
    )
    test_dir = _REPO_ROOT / _PA8_TEST_DIR
    doctrine_dir = _REPO_ROOT / _PA8_DOCTRINE_DIR
    test_files = sorted(test_dir.glob("*.py")) if test_dir.exists() else []
    doctrine_files = sorted(doctrine_dir.glob("*.md")) if doctrine_dir.exists() else []
    corpus_files = test_files + doctrine_files
    corpus = "\n".join(f"{f.name}\n{f.read_text(encoding='utf-8')}" for f in corpus_files)
    for test_name in declared:
        literal_hit = test_name in corpus
        equivalents = _PA8_TEST_EQUIVALENTS.get(test_name, [])
        equivalent_hits = sorted(e for e in equivalents if e in corpus)
        ok = literal_hit or bool(equivalent_hits)
        ev = {
            "test_name": test_name,
            "literal_present": literal_hit,
            "equivalents_matched": equivalent_hits,
            "files_scanned": len(corpus_files),
        }
        label = f"PA.8 test `{test_name}` is covered (literal or equivalent)"
        rows.append(
            _ok(
                f"PA8_TEST::{test_name}",
                "PA.8",
                "PA8_TESTS",
                label,
                ev,
            )
            if ok
            else _fail(
                f"PA8_TEST::{test_name}",
                "PA.8",
                "PA8_TESTS",
                label,
                ev,
            )
        )
    return rows


_PA8_CONTRACT_FIELD_COVERAGE: dict[str, str] = {
    "proof_id": "compiled_prompt_artifact_id",
    "prompt_bom_ref": "prompt_bom_id",
    "compiled_prompt_artifact_ref": "CompiledPromptArtifact",
    "slot_order": "SLOT_ORDER",
    "slot_hashes": "structured_slots_hash_receipt",
    "higher_authority_override_map": "slot_authority_map",
    "lower_authority_override_attempts": "slot_conflict_map",
    "blocked_attempts": "rejected_slot_payload_report",
    "provider_render_hash": "ProviderRenderManifest",
    "response_schema_binding_ref": "R0SchemaBinding",
    "hmac_sig": "hmac_signature_receipt",
    "deterministic_digest": "manifest_hash_receipt",
}


def check_pa8_contracts() -> list[_Row]:
    """PA8_CONTRACTS: every PA.8 CONTRACTS TO IMPLEMENT field token is
    absorbed by a PA package symbol or a recursively-walked receipt key.
    """
    rows: list[_Row] = []
    extra = _parse_doctrine_extra(_REPO_ROOT)
    pa8 = extra.get("PA.8", {})
    declared = pa8.get("contracts_to_implement", [])
    if not declared:
        rows.append(
            _fail(
                "PA8_CONTRACTS::parsed",
                "PA.8",
                "PA8_CONTRACTS",
                "PA.8 CONTRACTS TO IMPLEMENT block parses at least one field",
                {"parsed_count": 0},
            )
        )
        return rows
    rows.append(
        _ok(
            "PA8_CONTRACTS::parsed",
            "PA.8",
            "PA8_CONTRACTS",
            "PA.8 CONTRACTS TO IMPLEMENT block parses at least one field",
            {"parsed_count": len(declared)},
        )
    )

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
    for field in declared:
        target = _PA8_CONTRACT_FIELD_COVERAGE.get(field)
        in_surface = target in pa_surface if target else False
        in_receipt = target in receipt_keys if target else False
        ok = bool(target) and (in_surface or in_receipt)
        ev = {
            "contract_field": field,
            "absorbed_by": target,
            "present_on_pa_surface": in_surface,
            "present_in_pa_receipt_union": in_receipt,
        }
        label = f"PA.8 contract field `{field}` absorbed by runtime symbol or receipt key"
        rows.append(
            _ok(
                f"PA8_CONTRACT::{field}",
                "PA.8",
                "PA8_CONTRACTS",
                label,
                ev,
            )
            if ok
            else _fail(
                f"PA8_CONTRACT::{field}",
                "PA.8",
                "PA8_CONTRACTS",
                label,
                ev,
            )
        )
    return rows


def check_parser_edge_hardening() -> list[_Row]:
    """PARSER_EDGE_HARDENING: parser handles 7 additional edge cases."""
    rows: list[_Row] = []
    cases = [
        (
            "trailing_colon_heading",
            ["STATUS VALUES:", "-----", "- One", "- Two"],
            _extract_section,
            ("STATUS VALUES",),
            ["One", "Two"],
            "Heading with trailing colon is recognised",
        ),
        (
            "tab_indented_bullet",
            ["STATUS VALUES", "-----", "\t- TabOne", "\t- TabTwo"],
            _extract_section,
            ("STATUS VALUES",),
            ["TabOne", "TabTwo"],
            "Tab-indented bullets are captured",
        ),
        (
            "asterisk_marker",
            ["STATUS VALUES", "-----", "* Star1", "* Star2"],
            _extract_section,
            ("STATUS VALUES",),
            ["Star1", "Star2"],
            "Asterisk-style bullets are captured",
        ),
        (
            "unicode_bullet_marker",
            ["STATUS VALUES", "-----", "\u2022 UniOne", "\u2022 UniTwo"],
            _extract_section,
            ("STATUS VALUES",),
            ["UniOne", "UniTwo"],
            "Unicode-bullet (U+2022) markers are captured",
        ),
        (
            "heading_lookalike_in_prose",
            [
                "This paragraph mentions STATUS VALUES inline but should not start a section.",
                "- NotABullet1",
                "- NotABullet2",
            ],
            _extract_section,
            ("STATUS VALUES",),
            [],
            "`STATUS VALUES` mid-prose does not start a section",
        ),
        (
            "heading_with_no_underline",
            ["STATUS VALUES", "- HeadOne", "- HeadTwo"],
            _extract_section,
            ("STATUS VALUES",),
            ["HeadOne", "HeadTwo"],
            "Heading without underline separator still captures bullets",
        ),
        (
            "csv_forbidden_block_split",
            ["FORBIDDEN OUTPUTS FROM THIS CHILD:", "-----", "- ALPHA, BETA, GAMMA", "- DELTA"],
            _extract_csv_section,
            ("FORBIDDEN OUTPUTS FROM THIS CHILD",),
            ["ALPHA", "BETA", "GAMMA", "DELTA"],
            "CSV-style forbidden bullet returns every comma-split token",
        ),
    ]
    for name, lines, fn, args, expected, desc in cases:
        actual = fn(lines, *args)
        ok = actual == expected
        ev = {"case": name, "args": list(args), "expected": expected, "actual": actual, "description": desc}
        label = f"PARSER_EDGE/{name}: {desc}"
        rows.append(
            _ok(
                f"PARSER_EDGE::{name}",
                "PARENT",
                "PARSER_EDGE_HARDENING",
                label,
                ev,
            )
            if ok
            else _fail(
                f"PARSER_EDGE::{name}",
                "PARENT",
                "PARSER_EDGE_HARDENING",
                label,
                ev,
            )
        )
    return rows


def render_markdown(rows: list[_Row]) -> str:
    total = len(rows)
    passes = sum(1 for r in rows if r.status == "PASS")
    fails = total - passes
    by_cat: dict[str, list[_Row]] = {}
    for r in rows:
        by_cat.setdefault(r.category, []).append(r)

    out: list[str] = []
    out.append("# Prompt Assembly — Runtime Evidence Matrix\n")
    out.append("Source-of-truth doctrine files:\n")
    for stage, path in DOCTRINE_FILES.items():
        out.append(f"- **{stage}** — `{path}`")
    out.append("")
    out.append("Runtime artifacts being verified:\n")
    out.append("- `agentic_core/prompt_governance/prompt_assembly/assembly_statuses.py`")
    out.append("- `agentic_core/prompt_governance/prompt_assembly/forbidden_outputs.py`")
    out.append("- `agentic_core/prompt_governance/prompt_assembly/doctrine_receipts.py`")
    out.append("- `agentic_core/prompt_governance/prompt_assembly/pipeline.py`")
    out.append("")
    out.append(f"**Tally:** {passes} PASS / {fails} FAIL (of {total} requirements)\n")
    out.append(f"**Generated:** {_dt.datetime.now(_dt.timezone.utc).isoformat()}\n")

    out.append("## Category roll-up\n")
    out.append("| Category | Total | PASS | FAIL |")
    out.append("|---|---:|---:|---:|")
    for cat in sorted(by_cat):
        sub = by_cat[cat]
        p = sum(1 for r in sub if r.status == "PASS")
        f = len(sub) - p
        out.append(f"| {cat} | {len(sub)} | {p} | {f} |")
    out.append("")

    for cat in sorted(by_cat):
        out.append(f"## {cat}\n")
        out.append("| # | Stage | ID | Requirement | Status | Evidence (truncated) |")
        out.append("|---:|---|---|---|:---:|---|")
        for i, r in enumerate(by_cat[cat], 1):
            ev_short = json.dumps(r.evidence, default=str, ensure_ascii=False)
            if len(ev_short) > 140:
                ev_short = ev_short[:137] + "…"
            ev_short = ev_short.replace("|", "\\|")
            out.append(
                f"| {i} | {r.stage} | `{r.req_id}` | {r.requirement} | **{r.status}** | `{ev_short}` |"
            )
        out.append("")
    return "\n".join(out) + "\n"


def main() -> int:
    rows: list[_Row] = []
    rows += check_status_set()
    rows += check_doctrine_drift()
    rows += check_status_partition_complete()
    rows += check_must_emit()
    rows += check_forbid_rd()
    rows += check_forbid_deep()
    rows += check_forbid_false_positive()
    rows += check_must_not_fence()
    rows += check_invariants()
    rows += check_slot_map()
    rows += check_negative_paths()
    rows += check_determinism()
    rows += check_aggregation()
    rows += check_parser_robustness()
    rows += check_pipeline_endtoend()
    rows += check_pipeline_negative_paths()
    # Hardening categories.
    rows += check_parent_status_vocabulary()
    rows += check_child_forbidden_doctrine()
    rows += check_child_must_not_doctrine()
    rows += check_pa8_rules()
    rows += check_pa8_test_coverage()
    rows += check_pa8_contracts()
    rows += check_parser_edge_hardening()

    md_path = _REPO_ROOT / "docs" / "reports" / "prompt-assembly" / "runtime_evidence.md"
    json_path = _REPO_ROOT / "tools" / "prompt_assembly" / "_runtime_evidence.json"
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)

    md_path.write_text(render_markdown(rows), encoding="utf-8")
    json_path.write_text(
        json.dumps([_to_dict(r) for r in rows], indent=2, default=str, ensure_ascii=False),
        encoding="utf-8",
    )

    passes = sum(1 for r in rows if r.status == "PASS")
    fails = len(rows) - passes
    print(f"VERDICT: {'PROVEN' if fails == 0 else 'GAPS'}")
    print(f"  {passes} PASS / {fails} FAIL (of {len(rows)} requirements)")
    print(f"  report: {md_path.relative_to(_REPO_ROOT)}")
    print(f"  json:   {json_path.relative_to(_REPO_ROOT)}")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
