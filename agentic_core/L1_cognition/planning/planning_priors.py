"""Stage 02.2 — Planning Priors & Rule Bundle.

Doctrine: ``docs/reference/02_L1_Reasoning/02.2_Planning_Priors_and_Rule_Bundle_detailed.md``.

This module wraps the existing
:func:`agentic_core.L1_cognition.reasoning.plan_bundle_loader.load_plan_bundle`
and :func:`derive_rule_aware_frame` into the v6 :class:`PlanBundlePacket`,
adding:

* :class:`PlanningPriorReader` interface (read-only, no retrieval, no
  tool calls) plus a :class:`StaticPlanningPriorReader` that returns
  caller-supplied priors for tests and offline planning.
* Closed-list :class:`ReferenceClass` enum.
* :class:`PlanningPriorReadPlan` and :class:`PlanningReferenceManifest`.
* :class:`PlanningPriorGapReport`.
* OTEL span emission for stage 02.2.
* Deterministic ``bundle_digest``.
"""

from __future__ import annotations

import abc
from typing import Mapping, Sequence

from agentic_core.L1_cognition.reasoning.plan_bundle_loader import (
    derive_rule_aware_frame,
    load_plan_bundle,
)
from agentic_core.L1_cognition.types.intent_frame_types import (
    IntentFrame,
)
from agentic_core.L1_cognition.planning.contracts import (
    L1ContractViolation,
    PlanBundlePacket,
    PlanBundleSnapshot,
    PlanningPriorGapReport,
    PlanningPriorReadInput,
    PlanningPriorReadPlan,
    PlanningReferenceManifest,
    ReferenceClass,
    freeze_plan_bundle_snapshot,
)
from agentic_core.L1_cognition.planning.digests import stable_digest
from agentic_core.L1_cognition.planning.otel import SpanSink, emit_stage_spans

__all__ = [
    "PlanningPriorReader",
    "StaticPlanningPriorReader",
    "build_plan_bundle",
]


# ---------------------------------------------------------------------------
# Reader interface
# ---------------------------------------------------------------------------


class PlanningPriorReader(abc.ABC):
    """Read-only interface to the L4-managed planning prior store.

    Implementations MUST be read-only with respect to L4 and MUST NOT
    issue C0 retrieval calls. The reader's job is to return planning
    references (schemas, route heuristics, output contracts, etc.) — not
    answer evidence.
    """

    @abc.abstractmethod
    def list_available_reference_classes(self, scope: str) -> tuple[ReferenceClass, ...]:
        """Return the classes that the caller's scope is allowed to read."""

    @abc.abstractmethod
    def read_planning_references(self, read_plan: PlanningPriorReadPlan) -> PlanningReferenceManifest:
        """Read approved planning references for the given plan."""

    def validate_reference_scope(self, reference: str, scope: str) -> bool:
        """Default: any reference is allowed; subclasses tighten as needed."""
        del reference, scope
        return True

    def get_snapshot_manifest(self) -> dict:
        """Return the underlying L4 snapshot identity (caller-supplied)."""
        return {}


class StaticPlanningPriorReader(PlanningPriorReader):
    """In-memory reader fed from a static dict of references-by-class.

    Useful for offline planning, tests, and the v6 pipeline default. The
    dict keys are :class:`ReferenceClass` values (or their ``str``
    forms); values are tuples of human-readable predicates. Anything not
    keyed in is treated as a gap.
    """

    def __init__(
        self,
        references_by_class: Mapping[ReferenceClass | str, Sequence[str]] | None = None,
        *,
        snapshot_manifest: Mapping[str, str] | None = None,
        max_steps: int = 10,
        max_wallclock_ms: int = 60_000,
    ) -> None:
        normalized: dict[ReferenceClass, tuple[str, ...]] = {}
        for k, v in (references_by_class or {}).items():
            cls = k if isinstance(k, ReferenceClass) else ReferenceClass(k)
            normalized[cls] = tuple(v)
        self._refs = normalized
        self._snapshot = dict(snapshot_manifest or {})
        self._max_steps = int(max_steps)
        self._max_wallclock_ms = int(max_wallclock_ms)

    def list_available_reference_classes(self, scope: str) -> tuple[ReferenceClass, ...]:
        del scope
        return tuple(self._refs.keys())

    def read_planning_references(self, read_plan: PlanningPriorReadPlan) -> PlanningReferenceManifest:
        loaded: list[str] = []
        blocked: list[str] = []
        labels: list[str] = []
        hashes: list[str] = []
        missing: list[str] = []

        for raw_cls in read_plan.reference_classes_requested:
            cls = raw_cls if isinstance(raw_cls, ReferenceClass) else ReferenceClass(raw_cls)
            items = self._refs.get(cls, ())
            if not items:
                missing.append(cls.value)
                continue
            cap = max(read_plan.max_items_by_class, 0)
            for item in items[:cap] if cap > 0 else items:
                tag = f"{cls.value}::{item}"
                loaded.append(tag)
                labels.append(f"l4_planning_prior:{cls.value}")
                hashes.append(stable_digest(tag, prefix="prior"))

        return PlanningReferenceManifest(
            manifest_id=f"prm::{stable_digest(read_plan.to_dict(), prefix='prm')[:16]}",
            references_loaded=tuple(loaded),
            references_blocked=tuple(blocked),
            stale_references=(),
            missing_reference_classes=tuple(missing),
            l4_snapshot_refs=tuple(self._snapshot.values()),
            source_authority_labels=tuple(labels),
            reference_hashes=tuple(hashes),
            read_scope_receipt={
                "scope": "static_test_reader",
                "items_requested": len(read_plan.reference_classes_requested),
                "items_loaded": len(loaded),
            },
            no_answer_evidence_assertion=True,
        )

    def get_snapshot_manifest(self) -> dict:
        return dict(self._snapshot)

    @property
    def max_steps(self) -> int:
        return self._max_steps

    @property
    def max_wallclock_ms(self) -> int:
        return self._max_wallclock_ms


# ---------------------------------------------------------------------------
# Read plan construction
# ---------------------------------------------------------------------------


_DEFAULT_REQUESTED_CLASSES: tuple[ReferenceClass, ...] = (
    ReferenceClass.TASK_SCHEMAS,
    ReferenceClass.ROUTE_HEURISTICS,
    ReferenceClass.OUTPUT_CONTRACTS,
    ReferenceClass.VALIDATION_RUBRICS,
    ReferenceClass.COMPLIANCE_BOUNDS,
    ReferenceClass.ESCALATION_THRESHOLDS,
    ReferenceClass.SAFE_DECOMPOSITION_PATTERNS,
    ReferenceClass.APPROVED_PLAN_EXAMPLES,
    ReferenceClass.ANTI_PATTERNS,
    ReferenceClass.FALLBACK_TEMPLATES,
)


def _build_read_plan(input_: PlanningPriorReadInput) -> PlanningPriorReadPlan:
    requested = (
        tuple(input_.allowed_planning_reference_classes)
        if input_.allowed_planning_reference_classes
        else _DEFAULT_REQUESTED_CLASSES
    )
    blocked = set(
        c.value if isinstance(c, ReferenceClass) else c for c in input_.blocked_planning_reference_classes
    )
    final = tuple(
        (c if isinstance(c, ReferenceClass) else ReferenceClass(c))
        for c in requested
        if (c.value if isinstance(c, ReferenceClass) else c) not in blocked
    )
    return PlanningPriorReadPlan(
        read_plan_id=f"ppp::{input_.request_id}",
        reference_classes_requested=final,
        max_items_by_class=8,
        max_tokens_by_class=512,
        no_answer_evidence_assertion=True,
    )


def _categorize_loaded(
    manifest: PlanningReferenceManifest,
) -> dict[ReferenceClass, list[str]]:
    out: dict[ReferenceClass, list[str]] = {}
    for tag in manifest.references_loaded:
        cls_str, _, body = tag.partition("::")
        try:
            cls = ReferenceClass(cls_str)
        except ValueError:
            continue
        out.setdefault(cls, []).append(body)
    return out


# ---------------------------------------------------------------------------
# Public entrypoint
# ---------------------------------------------------------------------------


def build_plan_bundle(
    input_: PlanningPriorReadInput,
    prior_reader: PlanningPriorReader,
    *,
    intent_frame: IntentFrame | None = None,
    span_sink: SpanSink | None = None,
) -> PlanBundlePacket:
    """02.2 entrypoint — read priors and assemble the PlanBundle packet.

    Args:
        input_: Validated :class:`PlanningPriorReadInput`.
        prior_reader: A :class:`PlanningPriorReader` implementation.
        intent_frame: Optional live :class:`IntentFrame` from stage 02.1
            (used only to derive the rule-aware frame). When ``None``,
            the packet's rule-aware frame is computed without high-risk
            promotion.
        span_sink: Optional sink for OTEL span events.
    """
    if not isinstance(input_, PlanningPriorReadInput):
        raise L1ContractViolation(f"input_ must be PlanningPriorReadInput, got {type(input_)}")
    if not isinstance(prior_reader, PlanningPriorReader):
        raise L1ContractViolation(f"prior_reader must be PlanningPriorReader, got {type(prior_reader)}")

    read_plan = _build_read_plan(input_)
    manifest = prior_reader.read_planning_references(read_plan)
    grouped = _categorize_loaded(manifest)

    # Map ReferenceClass groups onto load_plan_bundle keyword args.
    bundle = load_plan_bundle(
        schemas=grouped.get(ReferenceClass.TASK_SCHEMAS, ()),
        route_heuristics=grouped.get(ReferenceClass.ROUTE_HEURISTICS, ()),
        output_contracts=grouped.get(ReferenceClass.OUTPUT_CONTRACTS, ()),
        validation_rubric=grouped.get(ReferenceClass.VALIDATION_RUBRICS, ()),
        policy_bounds=grouped.get(ReferenceClass.COMPLIANCE_BOUNDS, ()),
        escalation_thresholds=grouped.get(ReferenceClass.ESCALATION_THRESHOLDS, ()),
        disallowed_actions=grouped.get(ReferenceClass.REFUSAL_TAXONOMY, ()),
        hitl_triggers=grouped.get(ReferenceClass.ESCALATION_THRESHOLDS, ()),
        exemplars=grouped.get(ReferenceClass.APPROVED_PLAN_EXAMPLES, ()),
        edge_cases=grouped.get(ReferenceClass.ANTI_PATTERNS, ()),
        approved_templates=grouped.get(ReferenceClass.SAFE_DECOMPOSITION_PATTERNS, ()),
        stopping_rules=grouped.get(ReferenceClass.GROUNDING_CRITERIA, ()),
        retry_boundaries=grouped.get(ReferenceClass.FALLBACK_TEMPLATES, ()),
        abstain_patterns=grouped.get(ReferenceClass.FALLBACK_TEMPLATES, ()),
        max_steps=getattr(prior_reader, "max_steps", 10),
        max_wallclock_ms=getattr(prior_reader, "max_wallclock_ms", 60_000),
    )

    # Rule-aware frame: if the caller passed the live intent frame, use it.
    if intent_frame is None:
        from agentic_core.L1_cognition.types.intent_frame_types import (
            OutputTargetKind,
            WorkClass,
        )

        stub = IntentFrame(
            request_id=input_.request_id,
            goal=input_.intent_frame.normalized_goal or "stub",
            success_condition="stub",
            constraints=tuple(),  # type: ignore[arg-type]
            details=tuple(),  # type: ignore[arg-type]
            output_target_kind=OutputTargetKind.ANSWER,
            work_class=(
                WorkClass(input_.intent_frame.work_class)
                if input_.intent_frame.work_class
                else WorkClass.UNKNOWN
            ),
            high_risk=input_.intent_frame.high_risk,
        )
        rule_frame = derive_rule_aware_frame(stub, bundle)
    else:
        rule_frame = derive_rule_aware_frame(intent_frame, bundle)

    snapshot = freeze_plan_bundle_snapshot(bundle, rule_frame)

    # Gap report.
    gap_report = PlanningPriorGapReport(
        missing_classes=manifest.missing_reference_classes,
        degraded_planning_quality=bool(manifest.missing_reference_classes),
        fallback_strategy="abstain_or_clarify_if_critical_class_missing"
        if manifest.missing_reference_classes
        else "",
    )

    # Deterministic input/output digests.
    input_digest = stable_digest(input_.to_dict(), prefix="l1.02.2.input")
    output_payload = {
        "plan_bundle": snapshot.to_dict(),
        "planning_prior_read_plan": read_plan.to_dict(),
        "planning_reference_manifest": manifest.to_dict(),
        "planning_prior_gap_report": gap_report.to_dict(),
    }
    output_digest = stable_digest(output_payload, prefix="l1.02.2.output")
    bundle_digest = stable_digest(snapshot.to_dict(), prefix="l1.02.2.bundle")

    packet = PlanBundlePacket(
        plan_bundle=snapshot,
        planning_prior_read_plan=read_plan,
        planning_reference_manifest=manifest,
        planning_prior_gap_report=gap_report,
        rule_aware_planning_frame=rule_frame.to_dict(),
        bundle_digest=bundle_digest,
        request_id=input_.request_id,
        trace_root=input_.trace_root,
    )

    emit_stage_spans(
        stage="02.2",
        request_id=input_.request_id,
        trace_root=input_.trace_root,
        policy_hash_observed=input_.policy_hash_observed,
        instruction_hash_observed=input_.instruction_hash_observed,
        input_digest=input_digest,
        output_digest=output_digest,
        span_sink=span_sink,
        extra={"bundle_digest": bundle_digest},
    )

    return packet
