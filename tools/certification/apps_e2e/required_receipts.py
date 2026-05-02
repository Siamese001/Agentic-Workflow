"""Required-receipt resolver for apps_e2e two-gate certification.

Plan: apps-e2e-two-gate-certification-d8b3a1 §6 + §6.5

Pure function `required_receipts(spec)` returns a list of `ReceiptRequirement`
tuples — one per `(ref_field, expected_kind)` slot the bundle MUST occupy
for the spec to be `SPINE_COMPLETE_CERTIFIED`. The strict verifier consumes
this list to drive S3, S9, S10 (presence-on-disk + sha256 + manifest-row +
artifact-kind binding).

The `otel_or_runtime_trace_ref` slot accepts EITHER `otel_trace` OR
`runtime_adg_trace` — represented as a frozenset value in the kind field.

Replaces the legacy `_required_runtime_refs` helper inside shared_verifier.py
once W2.4 wires in this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from tools.certification.apps_e2e.app_specs import (
    AppSpec,
    L3_PATH_BYPASSED,
    L3_PATH_RAN,
    effective_c0_required,
    effective_l2_required,
    effective_l6_exhaust_required,
    effective_otel_required,
    effective_prompt_assembly_required,
    effective_uwg_required,
)
from tools.certification.apps_e2e.artifact_kinds import (
    TRACE_SLOT_KINDS,
    ArtifactKind,
)


@dataclass(frozen=True)
class ReceiptRequirement:
    """One required receipt: a bundle field name + the artifact kind that MUST occupy it.

    `expected_kind` may be:
      - a single ArtifactKind for slots with one acceptable kind (e.g. route_contract)
      - a frozenset[ArtifactKind] for slots that accept any of several kinds
        (e.g. otel_or_runtime_trace_ref accepts otel_trace OR runtime_adg_trace)
    """

    ref_field: str
    expected_kind: ArtifactKind | frozenset[ArtifactKind]

    @property
    def is_kind_set(self) -> bool:
        return isinstance(self.expected_kind, frozenset)

    def kind_matches(self, kind_value: str | None) -> bool:
        """True if ``kind_value`` matches this requirement's expected kind(s)."""
        if kind_value is None:
            return False
        if self.is_kind_set:
            return kind_value in {k.value for k in self.expected_kind}  # type: ignore[union-attr]
        return kind_value == self.expected_kind.value  # type: ignore[union-attr]


# Always-required receipts for any spec where certification_required=True.
_ALWAYS_REQUIRED: tuple[ReceiptRequirement, ...] = (
    ReceiptRequirement("runtime_route_contract_ref", ArtifactKind.route_contract),
    ReceiptRequirement("runtime_l1_plan_ref", ArtifactKind.l1_plan_contract),
    # Exit is implicit-always per amendment 1; not gated by l6_exhaust_required.
    ReceiptRequirement("runtime_exit_disposition_ref", ArtifactKind.exit_x3_disposition),
)


def required_receipts(spec: AppSpec) -> tuple[ReceiptRequirement, ...]:
    """Return the tuple of receipts required for ``spec`` to be SPINE_COMPLETE_CERTIFIED.

    Empty tuple is NEVER returned for a runnable certification-required spec —
    `_ALWAYS_REQUIRED` provides a non-empty floor.
    """
    items: list[ReceiptRequirement] = list(_ALWAYS_REQUIRED)

    # OTEL / runtime-ADG trace — slot accepts either kind.
    if effective_otel_required(spec):
        items.append(
            ReceiptRequirement("otel_or_runtime_trace_ref", TRACE_SLOT_KINDS)
        )

    # L3 path — receipt vs bypass receipt are mutually exclusive.
    if spec.expected_l3_path == L3_PATH_RAN:
        items.append(
            ReceiptRequirement("runtime_l3_receipt_ref", ArtifactKind.l3_runtime_receipt)
        )
    elif spec.expected_l3_path == L3_PATH_BYPASSED:
        items.append(
            ReceiptRequirement("runtime_l3_bypass_ref", ArtifactKind.l3_bypass_receipt)
        )
    # UNKNOWN expected_l3_path under certification is rejected by S12 in the
    # verifier; required_receipts simply does not add an L3 entry here.

    # L6 exhaust — separate from Exit.
    if effective_l6_exhaust_required(spec):
        items.append(
            ReceiptRequirement("runtime_exhaust_ref", ArtifactKind.runtime_exhaust_bundle)
        )

    # Optional spine surfaces.
    if effective_c0_required(spec):
        items.append(
            ReceiptRequirement("runtime_c0_receipt_ref", ArtifactKind.c0_grounding_receipt)
        )
    if effective_prompt_assembly_required(spec):
        items.append(
            ReceiptRequirement("runtime_prompt_assembly_ref", ArtifactKind.prompt_assembly_receipt)
        )
    if effective_l2_required(spec):
        items.append(
            ReceiptRequirement("runtime_l2_artifact_ref", ArtifactKind.l2_sealed_artifact)
        )
    if effective_uwg_required(spec):
        items.append(
            ReceiptRequirement("runtime_uwg_receipt_ref", ArtifactKind.uwg_durable_write_receipt)
        )
    if spec.expects_static_dag:
        items.append(
            ReceiptRequirement("static_dag_ref", ArtifactKind.static_l3_dag_proof)
        )

    return tuple(items)


def required_ref_fields(spec: AppSpec) -> tuple[str, ...]:
    """Convenience: just the ref_field names required by ``spec``."""
    return tuple(r.ref_field for r in required_receipts(spec))


def find_requirement(spec: AppSpec, ref_field: str) -> ReceiptRequirement | None:
    for r in required_receipts(spec):
        if r.ref_field == ref_field:
            return r
    return None


__all__ = [
    "ReceiptRequirement",
    "required_receipts",
    "required_ref_fields",
    "find_requirement",
]
