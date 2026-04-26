"""03.4 L0 Grounded and Action Route Handoffs.

Realizes:

- ``R3GroundedReadHandoff``         — 03.4 PHASE 1 §1
- ``R4SingleActionHandoff``         — 03.4 PHASE 1 §2
- ``R3R4ArgumentGroundingHandoff``  — 03.4 PHASE 1 §3
- ``DownstreamLayerRequirementMap`` — 03.4 PHASE 1 §4
- ``C0Budget``                      — 03.4 §c0_budget block
- Builder functions                 — 03.4 §PHASE 2

These are SINGLE_STEP handoff packets. None executes; they declare downstream
obligations only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from . import DoctrineContractError

_MAX_STR = 512
_MAX_LIST = 64
_MAX_REASON = 32


def _need_str(value: object, name: str, *, allow_empty: bool = False) -> None:
    if not isinstance(value, str):
        raise DoctrineContractError(f"{name} must be str, got {type(value).__name__}")
    if len(value) > _MAX_STR:
        raise DoctrineContractError(f"{name} exceeds {_MAX_STR} chars")
    if not allow_empty and not value:
        raise DoctrineContractError(f"{name} must be non-empty")


def _need_str_tuple(values: object, name: str, *, max_len: int = _MAX_LIST) -> None:
    if not isinstance(values, tuple):
        raise DoctrineContractError(f"{name} must be tuple")
    if len(values) > max_len:
        raise DoctrineContractError(f"{name} exceeds {max_len}")
    for idx, item in enumerate(values):
        if not isinstance(item, str) or not item or len(item) > _MAX_STR:
            raise DoctrineContractError(f"{name}[{idx}] must be non-empty str <= {_MAX_STR}")


def _need_bool(value: object, name: str) -> None:
    if not isinstance(value, bool):
        raise DoctrineContractError(f"{name} must be bool, got {type(value).__name__}")


def _need_pos_int(value: object, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise DoctrineContractError(f"{name} must be int")
    if value < 0:
        raise DoctrineContractError(f"{name} must be >= 0")


class SingleStepExecutionForm(str, Enum):
    SINGLE_STEP = "SINGLE_STEP"


class CitationMode(str, Enum):
    NONE = "NONE"
    INLINE = "INLINE"
    FOOTNOTE = "FOOTNOTE"
    SUPPORT_BLOCK = "SUPPORT_BLOCK"


class FreshnessClass(str, Enum):
    """03.5 freshness; restated here for self-consistency."""

    STATIC = "STATIC"
    SLOW_CHANGING = "SLOW_CHANGING"
    RECENT = "RECENT"
    CURRENT = "CURRENT"
    LIVE = "LIVE"


class SupportTarget(str, Enum):
    """03.5 support_target; restated here for self-consistency."""

    NONE = "NONE"
    EXACT_QUOTE = "EXACT_QUOTE"
    SOURCE_BACKED_SUMMARY = "SOURCE_BACKED_SUMMARY"
    POLICY_CLAUSE = "POLICY_CLAUSE"
    CODE_LOCATION = "CODE_LOCATION"
    INCIDENT_EVIDENCE = "INCIDENT_EVIDENCE"
    RANKED_CAUSE = "RANKED_CAUSE"
    ACTION_ARGUMENT_GROUNDING = "ACTION_ARGUMENT_GROUNDING"


class ReversibilityClass(str, Enum):
    """03.4 §R4 reversibility_class."""

    REVERSIBLE_LOCAL = "REVERSIBLE_LOCAL"
    REVERSIBLE_REMOTE = "REVERSIBLE_REMOTE"
    LOW_RISK = "LOW_RISK"
    IRREVERSIBLE = "IRREVERSIBLE"


class CapabilityClass(str, Enum):
    READ_ONLY = "READ_ONLY"
    READ_WRITE = "READ_WRITE"
    ACTION = "ACTION"
    REFLECT_ONLY = "REFLECT_ONLY"


class SandboxClass(str, Enum):
    NO_SANDBOX = "NO_SANDBOX"
    PROCESS_SANDBOX = "PROCESS_SANDBOX"
    NETWORK_SANDBOX = "NETWORK_SANDBOX"
    FULL_SANDBOX = "FULL_SANDBOX"


class SideEffectClass(str, Enum):
    PURE = "PURE"
    LOCAL_REVERSIBLE = "LOCAL_REVERSIBLE"
    REMOTE_REVERSIBLE = "REMOTE_REVERSIBLE"
    IRREVERSIBLE = "IRREVERSIBLE"


class WriteAuthority(str, Enum):
    NONE_UNTIL_UWG = "NONE_UNTIL_UWG"


@dataclass(frozen=True)
class C0Budget:
    """03.4 §R3GroundedReadHandoff.c0_budget block."""

    max_k: int
    max_graph_hops: int
    max_refine_attempts: int
    max_latency_ms: int
    max_token_context: int

    def __post_init__(self) -> None:
        for name in (
            "max_k",
            "max_graph_hops",
            "max_refine_attempts",
            "max_latency_ms",
            "max_token_context",
        ):
            _need_pos_int(getattr(self, name), f"C0Budget.{name}")
        if self.max_k == 0:
            raise DoctrineContractError("C0Budget.max_k must be > 0 (at least one retrieval pass)")
        if self.max_token_context == 0:
            raise DoctrineContractError("C0Budget.max_token_context must be > 0")


@dataclass(frozen=True)
class R3GroundedReadHandoff:
    """03.4 PHASE 1 §1."""

    request_id: str
    run_id: str
    trace_root: str
    l1_plan_ref: str
    query_spec_ref: str
    task_spec_ref: str
    support_target: SupportTarget
    citation_mode: CitationMode
    freshness_class: FreshnessClass
    tenant_scope: str
    acl_scope: tuple[str, ...]
    region_scope: str
    c0_budget: C0Budget
    fallback_chain: tuple[str, ...]
    route_digest_ref: str
    allowed_source_classes: tuple[str, ...] = field(default_factory=tuple)
    disallowed_source_classes: tuple[str, ...] = field(default_factory=tuple)
    route_id: str = "R3_SIMPLE_GROUNDED_READ"
    execution_form: SingleStepExecutionForm = SingleStepExecutionForm.SINGLE_STEP
    pa_required: bool = True
    l2_required: bool = True
    l3_required: bool = False

    def __post_init__(self) -> None:
        for name in (
            "request_id",
            "run_id",
            "trace_root",
            "l1_plan_ref",
            "query_spec_ref",
            "task_spec_ref",
            "tenant_scope",
            "region_scope",
            "route_digest_ref",
            "route_id",
        ):
            _need_str(getattr(self, name), f"R3GroundedReadHandoff.{name}")
        if self.route_id != "R3_SIMPLE_GROUNDED_READ":
            raise DoctrineContractError(
                f"R3GroundedReadHandoff.route_id must be R3_SIMPLE_GROUNDED_READ, got {self.route_id}",
            )
        if not isinstance(self.support_target, SupportTarget):
            raise DoctrineContractError("R3GroundedReadHandoff.support_target must be SupportTarget")
        # 03.4 §VALIDATION RULES — R3 must include support_target (not NONE).
        if self.support_target == SupportTarget.NONE:
            raise DoctrineContractError(
                "R3GroundedReadHandoff.support_target=NONE invalid; R3 requires real support_target",
            )
        if not isinstance(self.citation_mode, CitationMode):
            raise DoctrineContractError("R3GroundedReadHandoff.citation_mode must be CitationMode")
        if not isinstance(self.freshness_class, FreshnessClass):
            raise DoctrineContractError("R3GroundedReadHandoff.freshness_class must be FreshnessClass")
        _need_str_tuple(self.acl_scope, "R3GroundedReadHandoff.acl_scope")
        if not isinstance(self.c0_budget, C0Budget):
            raise DoctrineContractError("R3GroundedReadHandoff.c0_budget must be C0Budget")
        _need_str_tuple(
            self.fallback_chain,
            "R3GroundedReadHandoff.fallback_chain",
            max_len=_MAX_REASON,
        )
        _need_str_tuple(self.allowed_source_classes, "R3GroundedReadHandoff.allowed_source_classes")
        _need_str_tuple(
            self.disallowed_source_classes,
            "R3GroundedReadHandoff.disallowed_source_classes",
        )
        if not isinstance(self.execution_form, SingleStepExecutionForm):
            raise DoctrineContractError(
                "R3GroundedReadHandoff.execution_form must be SingleStepExecutionForm",
            )
        for name in ("pa_required", "l2_required", "l3_required"):
            _need_bool(getattr(self, name), f"R3GroundedReadHandoff.{name}")
        # 03.4 §VALIDATION — R3 must set l3_required=False.
        if self.l3_required:
            raise DoctrineContractError(
                "R3GroundedReadHandoff.l3_required must be False (R3 bypasses L3)",
            )
        if not self.l2_required:
            raise DoctrineContractError(
                "R3GroundedReadHandoff.l2_required must be True (R3 requires one bounded L2 step)",
            )


@dataclass(frozen=True)
class PTCPermissionMetadata:
    """03.4 §PTC-CAPABLE SINGLE STEP — downstream-only PTC flags."""

    ptc_candidate: bool = False
    ptc_batch_reason: str = ""
    ptc_requires_l2_sandbox: bool = True
    ptc_requires_l5_egress_certification: bool = True
    ptc_raw_tool_results_must_not_enter_l1_or_l3_context: bool = True
    ptc_stdout_summary_only_to_model_context: bool = True

    def __post_init__(self) -> None:
        for name in (
            "ptc_candidate",
            "ptc_requires_l2_sandbox",
            "ptc_requires_l5_egress_certification",
            "ptc_raw_tool_results_must_not_enter_l1_or_l3_context",
            "ptc_stdout_summary_only_to_model_context",
        ):
            _need_bool(getattr(self, name), f"PTCPermissionMetadata.{name}")
        _need_str(self.ptc_batch_reason, "PTCPermissionMetadata.ptc_batch_reason", allow_empty=True)
        # 03.4 §PTC ROUTING RULE — when ptc_candidate is True, sandbox + cert MUST be True.
        if self.ptc_candidate:
            if not self.ptc_requires_l2_sandbox:
                raise DoctrineContractError(
                    "ptc_candidate=True requires ptc_requires_l2_sandbox=True",
                )
            if not self.ptc_requires_l5_egress_certification:
                raise DoctrineContractError(
                    "ptc_candidate=True requires ptc_requires_l5_egress_certification=True",
                )


@dataclass(frozen=True)
class R4SingleActionHandoff:
    """03.4 PHASE 1 §2."""

    action_spec_ref: str
    action_kind: str
    side_effect_class: SideEffectClass
    reversibility_class: ReversibilityClass
    capability_class: CapabilityClass
    sandbox_class: SandboxClass
    capability_token_required: bool
    sandbox_envelope_required: bool
    action_args_status: str
    hitl_required: bool
    uwg_required_if_write: bool
    fallback_chain: tuple[str, ...]
    ptc_permission_metadata: PTCPermissionMetadata = field(default_factory=PTCPermissionMetadata)
    route_id: str = "R4_SINGLE_ACTION"
    execution_form: SingleStepExecutionForm = SingleStepExecutionForm.SINGLE_STEP
    l2_required: bool = True
    l3_required: bool = False
    c0_required: bool = False

    def __post_init__(self) -> None:
        for name in ("action_spec_ref", "action_kind", "action_args_status", "route_id"):
            _need_str(getattr(self, name), f"R4SingleActionHandoff.{name}")
        if self.route_id != "R4_SINGLE_ACTION":
            raise DoctrineContractError(
                f"R4SingleActionHandoff.route_id must be R4_SINGLE_ACTION, got {self.route_id}",
            )
        if not isinstance(self.side_effect_class, SideEffectClass):
            raise DoctrineContractError("R4SingleActionHandoff.side_effect_class must be SideEffectClass")
        if not isinstance(self.reversibility_class, ReversibilityClass):
            raise DoctrineContractError(
                "R4SingleActionHandoff.reversibility_class must be ReversibilityClass",
            )
        if not isinstance(self.capability_class, CapabilityClass):
            raise DoctrineContractError("R4SingleActionHandoff.capability_class must be CapabilityClass")
        if not isinstance(self.sandbox_class, SandboxClass):
            raise DoctrineContractError("R4SingleActionHandoff.sandbox_class must be SandboxClass")
        for name in (
            "capability_token_required",
            "sandbox_envelope_required",
            "hitl_required",
            "uwg_required_if_write",
            "l2_required",
            "l3_required",
            "c0_required",
        ):
            _need_bool(getattr(self, name), f"R4SingleActionHandoff.{name}")
        # 03.4 §VALIDATION — R4 must include capability/sandbox requirements.
        if not self.capability_token_required:
            raise DoctrineContractError(
                "R4SingleActionHandoff.capability_token_required must be True",
            )
        if not self.sandbox_envelope_required:
            raise DoctrineContractError(
                "R4SingleActionHandoff.sandbox_envelope_required must be True",
            )
        # 03.4 §VALIDATION — R4 must not include direct write authority.
        # Caller must NOT escalate; uwg_required_if_write True if action is a write.
        # 03.4 §VALIDATION — R4 must set l3_required=False.
        if self.l3_required:
            raise DoctrineContractError("R4SingleActionHandoff.l3_required must be False (R4 bypasses L3)")
        if not self.l2_required:
            raise DoctrineContractError("R4SingleActionHandoff.l2_required must be True")
        # IRREVERSIBLE actions MUST require HITL.
        if self.reversibility_class == ReversibilityClass.IRREVERSIBLE and not self.hitl_required:
            raise DoctrineContractError(
                "R4 IRREVERSIBLE reversibility_class requires hitl_required=True",
            )
        _need_str_tuple(self.fallback_chain, "R4SingleActionHandoff.fallback_chain", max_len=_MAX_REASON)
        if not isinstance(self.ptc_permission_metadata, PTCPermissionMetadata):
            raise DoctrineContractError(
                "R4SingleActionHandoff.ptc_permission_metadata must be PTCPermissionMetadata",
            )
        if not isinstance(self.execution_form, SingleStepExecutionForm):
            raise DoctrineContractError(
                "R4SingleActionHandoff.execution_form must be SingleStepExecutionForm",
            )


@dataclass(frozen=True)
class R3R4ArgumentGroundingHandoff:
    """03.4 PHASE 1 §3."""

    action_spec_ref: str
    c0_argument_targets: tuple[str, ...]
    required_argument_fields: tuple[str, ...]
    citation_or_source_requirements: tuple[str, ...]
    action_args_from_evidence_policy: str
    pa_or_argument_packet_required: bool = True
    l2_required: bool = True
    l3_required: bool = False
    argument_grounding_required: bool = True
    support_target: SupportTarget = SupportTarget.ACTION_ARGUMENT_GROUNDING
    route_id: str = "R4_SINGLE_ACTION"
    execution_form: SingleStepExecutionForm = SingleStepExecutionForm.SINGLE_STEP

    def __post_init__(self) -> None:
        _need_str(self.action_spec_ref, "R3R4ArgumentGroundingHandoff.action_spec_ref")
        _need_str(
            self.action_args_from_evidence_policy,
            "R3R4ArgumentGroundingHandoff.action_args_from_evidence_policy",
        )
        _need_str(self.route_id, "R3R4ArgumentGroundingHandoff.route_id")
        if self.route_id != "R4_SINGLE_ACTION":
            raise DoctrineContractError(
                f"R3R4ArgumentGroundingHandoff.route_id must be R4_SINGLE_ACTION, got {self.route_id}",
            )
        for name in (
            "c0_argument_targets",
            "required_argument_fields",
            "citation_or_source_requirements",
        ):
            _need_str_tuple(getattr(self, name), f"R3R4ArgumentGroundingHandoff.{name}")
        # 03.4 §VALIDATION — R3+R4 argument grounding must not become managed workflow.
        for name in ("pa_or_argument_packet_required", "l2_required", "argument_grounding_required"):
            if not getattr(self, name):
                raise DoctrineContractError(
                    f"R3R4ArgumentGroundingHandoff.{name} must be True",
                )
        if self.l3_required:
            raise DoctrineContractError(
                "R3R4ArgumentGroundingHandoff.l3_required must be False",
            )
        # support_target must be ACTION_ARGUMENT_GROUNDING.
        if self.support_target != SupportTarget.ACTION_ARGUMENT_GROUNDING:
            raise DoctrineContractError(
                "R3R4ArgumentGroundingHandoff.support_target must be ACTION_ARGUMENT_GROUNDING",
            )
        if not isinstance(self.execution_form, SingleStepExecutionForm):
            raise DoctrineContractError(
                "R3R4ArgumentGroundingHandoff.execution_form must be SingleStepExecutionForm",
            )


@dataclass(frozen=True)
class DownstreamLayerRequirementMap:
    """03.4 PHASE 1 §4."""

    requires_c0: bool = False
    requires_prompt_assembly: bool = False
    requires_l2: bool = True
    requires_l3: bool = False
    requires_l5_certification: bool = True
    requires_exit_review: bool = True
    requires_uwg_if_commit: bool = True
    requires_hitl_reclearance_if_human_modified: bool = True
    requires_ptc_sandbox_if_ptc_candidate: bool = True

    def __post_init__(self) -> None:
        from dataclasses import fields as _fields

        for f in _fields(self):
            _need_bool(getattr(self, f.name), f"DownstreamLayerRequirementMap.{f.name}")
        if not self.requires_exit_review:
            raise DoctrineContractError(
                "DownstreamLayerRequirementMap.requires_exit_review must be True (Exit always reviews)",
            )


__all__ = [
    "C0Budget",
    "CapabilityClass",
    "CitationMode",
    "DownstreamLayerRequirementMap",
    "FreshnessClass",
    "PTCPermissionMetadata",
    "R3GroundedReadHandoff",
    "R3R4ArgumentGroundingHandoff",
    "R4SingleActionHandoff",
    "ReversibilityClass",
    "SandboxClass",
    "SideEffectClass",
    "SingleStepExecutionForm",
    "SupportTarget",
    "WriteAuthority",
]
