"""App-domain contract records (Fort Knox apps_* domain contract system).

Implements the schema mandated by the user's Fort Knox app-domain contract
objective (plan: ``docs/archive/windsurf/legacy-tree/plans/apps-domain-contract-fortknox-c4d8e2.md``).

Sibling to ``records.py`` rather than an extension of it: the existing
``RubricRecord`` / ``ThresholdProfileRecord`` are minimal id-bearing pointers
used by the broader L4 ecosystem (00.2 doctrine). The records below are
**rich, per-app, deterministic contract bundles** the runtime resolves from
L4 to govern Exit evaluation, retrieval, prompting, and capability scope.

Hard invariants:

- Every record is ``frozen=True`` and ships a ``deterministic_digest`` field
  populated by :func:`agentic_core.L4_state.contracts.records.stamp_digest`.
- ``app_id`` and ``task_class`` are mandatory primary-key components.
- ``status`` ∈ {``draft``, ``active``, ``deprecated``}.
- ``created_by_surface`` defaults to ``"UWG"`` — only UWG creates these
  records (anti-bypass posture).
- ``source_app_config_ref`` cites the on-disk YAML the record was derived
  from (lineage, not authority).

Authority order at runtime:

    L4 record (canonical)  >  apps_<name>/config/domain_contract/*.yaml (proposal)

After UWG registration completes, the runtime reads ONLY the L4 records.
Direct YAML reads from the runtime hot path are forbidden by Phase 4 of the
plan.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Mapping, Tuple

from agentic_core.L4_state.contracts.records import (
    L4_CONTRACT_SCHEMA_VERSION,
    _empty_tuple,
)

# ----------------------------------------------------------------------------
# Closed vocabularies
# ----------------------------------------------------------------------------

CONTRACT_STATUS_VOCAB: frozenset[str] = frozenset({"draft", "active", "deprecated"})
GRADER_TYPE_VOCAB: frozenset[str] = frozenset(
    {
        # Legacy/baseline grader types.
        "deterministic",
        "llm_as_judge",
        "hybrid",
        # Canonical Anthropic grader types added in
        # apps-eval-harness-deferred-e4a1b7 W3.P1 — covers agent-eval
        # parity per Anthropic's "Demystifying evals for AI agents".
        "tool_calls",       # W3.P1 — trajectory-match grader
        "state_check",      # W3.P2 — outcome-truth against app-specific state
        "transcript",       # W3.P3 — tracked-metric grader with bounds
        "trajectory_match", # W3.P3 — explicit trajectory match-mode handle
    },
)

# Trajectory match-modes for grader_type=tool_calls / trajectory_match.
# Optional; dims can omit the mode and rely on the default "unordered".
TRAJECTORY_MATCH_MODE_VOCAB: frozenset[str] = frozenset(
    {"strict", "unordered", "subset", "superset", "none"},
)

# W5.P3 — capability-vs-regression taxonomy (apps-eval-harness-closeout-b7c9d2).
# Empty string means "unannotated" and is always accepted; the gate emits
# an INFO-severity TAXONOMY_COVERAGE finding so operators can track adoption.
TAXONOMY_CLASS_VOCAB: frozenset[str] = frozenset(
    {"capability", "regression", "tracked_metric"},
)
OUTPUT_TYPE_VOCAB: frozenset[str] = frozenset(
    {"markdown", "json", "html", "text", "composite", "structured_record"},
)
FRESHNESS_CLASS_VOCAB: frozenset[str] = frozenset(
    {"realtime", "bounded", "stale_ok", "snapshot_only"},
)
SIDE_EFFECT_CLASS_VOCAB: frozenset[str] = frozenset(
    {"none", "read_only", "external_write", "user_action", "billing", "egress"},
)
FIXTURE_TYPE_VOCAB: frozenset[str] = frozenset(
    {"golden", "negative_control", "regression", "edge_case"},
)
TASK_CLASS_KIND_VOCAB: frozenset[str] = frozenset(
    {"generation", "classification", "extraction", "decisioning", "ranking", "selection"},
)
APPROVED_JUDGE_USE_VOCAB: frozenset[str] = frozenset(
    {
        "ALLOW_FOR_EVAL",
        "ALLOW_ADVISORY_ONLY",
        "REQUIRE_HYBRID",
        "REQUIRE_HUMAN_REVIEW",
        "DISABLE_FOR_SURFACE",
    }
)


class AppDomainContractError(ValueError):
    """Raised when an app-domain contract record fails its invariants."""


# ----------------------------------------------------------------------------
# Building blocks
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class ScoreDimension:
    """Per-dimension entry inside an :class:`AppEvalRubricRecord`.

    ``min_required_score`` of ``-1.0`` means "no minimum"; any value in
    ``[0.0, 1.0]`` is enforced by Exit (per-dimension minimum, not just
    overall score). ``fail_closed_if_unknown=True`` forces Exit to
    refuse PASS when the grader returns UNKNOWN for this dimension.
    """

    dimension_id: str
    description: str
    weight: float
    grader_type: str  # one of GRADER_TYPE_VOCAB
    min_required_score: float = -1.0
    evidence_required: bool = True
    fail_closed_if_unknown: bool = True
    # W3.P3 — optional trajectory match-mode for tool_calls / trajectory_match
    # grader types. Default "" = not applicable. When set, must be one of
    # TRAJECTORY_MATCH_MODE_VOCAB.
    trajectory_match_mode: str = ""
    # W4.P1 — optional categorical score bands. When set, overrides
    # min_required_score with band-index gating (see AppSpecificEvaluator).
    # Tuple of ascending-threshold band labels, e.g.
    # ("BAD", "WEAK", "OK", "GOOD", "EXCELLENT"). Empty = disabled.
    score_bands: Tuple[str, ...] = field(default_factory=_empty_tuple)
    # W5.P3 (apps-eval-harness-closeout-b7c9d2 W2) — capability-vs-regression
    # taxonomy. Empty = not annotated (gate emits INFO). Values:
    #   "capability"     — core ability the app MUST demonstrate
    #   "regression"     — watchdog against known failure modes (guardrail)
    #   "tracked_metric" — observed but not gated; surfaces in telemetry
    taxonomy_class: str = ""

    def __post_init__(self) -> None:
        if not self.dimension_id:
            raise AppDomainContractError("ScoreDimension.dimension_id is required")
        if self.grader_type not in GRADER_TYPE_VOCAB:
            raise AppDomainContractError(
                f"ScoreDimension.grader_type {self.grader_type!r} not in {sorted(GRADER_TYPE_VOCAB)}",
            )
        if not 0.0 <= self.weight <= 1.0:
            raise AppDomainContractError(
                f"ScoreDimension.weight must be in [0,1], got {self.weight}",
            )
        if self.min_required_score != -1.0 and not 0.0 <= self.min_required_score <= 1.0:
            raise AppDomainContractError(
                f"ScoreDimension.min_required_score must be -1 or in [0,1], got {self.min_required_score}",
            )
        if self.trajectory_match_mode and self.trajectory_match_mode not in TRAJECTORY_MATCH_MODE_VOCAB:
            raise AppDomainContractError(
                f"ScoreDimension.trajectory_match_mode {self.trajectory_match_mode!r} "
                f"not in {sorted(TRAJECTORY_MATCH_MODE_VOCAB)}",
            )
        if self.taxonomy_class and self.taxonomy_class not in TAXONOMY_CLASS_VOCAB:
            raise AppDomainContractError(
                f"ScoreDimension.taxonomy_class {self.taxonomy_class!r} "
                f"not in {sorted(TAXONOMY_CLASS_VOCAB)}",
            )


@dataclass(frozen=True)
class TaskClassEntry:
    """Per-task-class declaration inside the manifest.

    A single app may declare multiple task classes, such as generation and
    classification surfaces. Each task class
    binds to its own rubric / threshold / grader / capability profile.
    """

    task_class: str
    kind: str  # one of TASK_CLASS_KIND_VOCAB
    description: str
    risk_tier: str = "standard"  # standard | elevated | high
    hitl_required: bool = False

    def __post_init__(self) -> None:
        if not self.task_class:
            raise AppDomainContractError("TaskClassEntry.task_class is required")
        if self.kind not in TASK_CLASS_KIND_VOCAB:
            raise AppDomainContractError(
                f"TaskClassEntry.kind {self.kind!r} not in {sorted(TASK_CLASS_KIND_VOCAB)}",
            )


# ----------------------------------------------------------------------------
# Subcontract records
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class AppInputContractRecord:
    """Per-(app, task_class) input contract — what the app expects to receive."""

    input_contract_id: str
    app_id: str
    task_class: str
    version: str
    status: str
    missing_input_behavior: str  # fail_closed | ask_clarification | allow_default
    ambiguity_behavior: str  # fail_closed | escalate | prompt_user
    policy_hash: str = ""
    blueprint_hash: str = ""
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    required_inputs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    optional_inputs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    forbidden_inputs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    input_normalization_rules: Tuple[str, ...] = field(default_factory=_empty_tuple)
    data_boundary_rules: Tuple[str, ...] = field(default_factory=_empty_tuple)
    origin_trust_requirements: Tuple[str, ...] = field(default_factory=_empty_tuple)
    validation_rules: Tuple[str, ...] = field(default_factory=_empty_tuple)
    source_app_config_ref: str = ""
    created_by_surface: str = "UWG"
    created_at: str = ""
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    lineage_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)

    def __post_init__(self) -> None:
        _validate_status(self.status, "AppInputContractRecord")
        _validate_app_task(self.app_id, self.task_class, "AppInputContractRecord")


@dataclass(frozen=True)
class AppOutputSchemaRecord:
    """Per-(app, task_class) output schema — what the app may produce."""

    output_schema_id: str
    app_id: str
    task_class: str
    version: str
    status: str
    output_type: str
    policy_hash: str = ""
    blueprint_hash: str = ""
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    required_sections: Tuple[str, ...] = field(default_factory=_empty_tuple)
    optional_sections: Tuple[str, ...] = field(default_factory=_empty_tuple)
    field_constraints: Mapping[str, str] = field(default_factory=dict)
    formatting_constraints: Mapping[str, str] = field(default_factory=dict)
    prohibited_outputs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    schema_validation_rules: Tuple[str, ...] = field(default_factory=_empty_tuple)
    source_app_config_ref: str = ""
    created_by_surface: str = "UWG"
    created_at: str = ""
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    lineage_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)

    def __post_init__(self) -> None:
        _validate_status(self.status, "AppOutputSchemaRecord")
        _validate_app_task(self.app_id, self.task_class, "AppOutputSchemaRecord")
        if self.output_type not in OUTPUT_TYPE_VOCAB:
            raise AppDomainContractError(
                f"AppOutputSchemaRecord.output_type {self.output_type!r} not in {sorted(OUTPUT_TYPE_VOCAB)}",
            )


@dataclass(frozen=True)
class AppEvalRubricRecord:
    """Rich per-(app, task_class) eval rubric — distinct from simple RubricRecord."""

    eval_rubric_id: str
    app_id: str
    task_class: str
    version: str
    status: str
    policy_hash: str = ""
    blueprint_hash: str = ""
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    score_dimensions: Tuple[ScoreDimension, ...] = field(default_factory=_empty_tuple)
    shared_base_ref: str = ""
    app_override_ref: str = ""
    source_app_config_ref: str = ""
    created_by_surface: str = "UWG"
    created_at: str = ""
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    lineage_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)

    def __post_init__(self) -> None:
        _validate_status(self.status, "AppEvalRubricRecord")
        _validate_app_task(self.app_id, self.task_class, "AppEvalRubricRecord")
        if not self.score_dimensions:
            raise AppDomainContractError(
                f"AppEvalRubricRecord({self.eval_rubric_id}) requires at least one score_dimension",
            )
        # Closed-vocabulary dimension_id uniqueness
        seen: set[str] = set()
        for dim in self.score_dimensions:
            if dim.dimension_id in seen:
                raise AppDomainContractError(
                    f"duplicate dimension_id {dim.dimension_id!r} in {self.eval_rubric_id}",
                )
            seen.add(dim.dimension_id)


@dataclass(frozen=True)
class AppThresholdProfileRecord:
    """Per-(app, task_class) threshold profile — distinct from simple ThresholdProfileRecord."""

    threshold_profile_id: str
    app_id: str
    task_class: str
    version: str
    status: str
    overall_pass_threshold: float
    risk_tier: str = "standard"
    route_id: str = ""
    unknown_policy: str = "fail_closed"  # fail_closed | abstain | escalate
    abstain_policy: str = "soft"  # soft | hard
    hitl_policy: str = "none"  # none | required_on_low | required_always
    policy_hash: str = ""
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    dimension_minimums: Mapping[str, float] = field(default_factory=dict)
    source_app_config_ref: str = ""
    created_by_surface: str = "UWG"
    created_at: str = ""
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    lineage_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)

    def __post_init__(self) -> None:
        _validate_status(self.status, "AppThresholdProfileRecord")
        _validate_app_task(self.app_id, self.task_class, "AppThresholdProfileRecord")
        if not 0.0 <= self.overall_pass_threshold <= 1.0:
            raise AppDomainContractError(
                f"overall_pass_threshold must be in [0,1], got {self.overall_pass_threshold}",
            )
        for dim, val in self.dimension_minimums.items():
            if not 0.0 <= float(val) <= 1.0:
                raise AppDomainContractError(
                    f"dimension_minimums[{dim!r}]={val} not in [0,1]",
                )
        if self.unknown_policy not in {"fail_closed", "abstain", "escalate"}:
            raise AppDomainContractError(
                f"unknown_policy {self.unknown_policy!r} invalid",
            )


@dataclass(frozen=True)
class AppGraderRosterRecord:
    """Per-(app, task_class) grader roster — names the graders Exit must invoke."""

    grader_roster_id: str
    app_id: str
    task_class: str
    version: str
    status: str
    fallback_behavior: str = "fail_closed"  # fail_closed | use_deterministic_only
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    deterministic_graders: Tuple[str, ...] = field(default_factory=_empty_tuple)
    llm_judge_graders: Tuple[str, ...] = field(default_factory=_empty_tuple)
    ensemble_or_consensus_graders: Tuple[str, ...] = field(default_factory=_empty_tuple)
    calibration_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    source_app_config_ref: str = ""
    created_by_surface: str = "UWG"
    created_at: str = ""
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    lineage_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)

    def __post_init__(self) -> None:
        _validate_status(self.status, "AppGraderRosterRecord")
        _validate_app_task(self.app_id, self.task_class, "AppGraderRosterRecord")
        # At least one grader of any kind is required (allows deterministic-only apps)
        if not (
            self.deterministic_graders
            or self.llm_judge_graders
            or self.ensemble_or_consensus_graders
        ):
            raise AppDomainContractError(
                f"AppGraderRosterRecord({self.grader_roster_id}) requires at least one grader",
            )


@dataclass(frozen=True)
class AppRetrievalProfileRecord:
    """Per-(app, task_class) retrieval profile — what evidence sources C0 may use."""

    retrieval_profile_id: str
    app_id: str
    task_class: str
    version: str
    status: str
    freshness_class: str  # one of FRESHNESS_CLASS_VOCAB
    source_lineage_required: bool = True
    policy_hash: str = ""
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    allowed_sources: Tuple[str, ...] = field(default_factory=_empty_tuple)
    prohibited_sources: Tuple[str, ...] = field(default_factory=_empty_tuple)
    required_evidence_for: Tuple[str, ...] = field(default_factory=_empty_tuple)
    acl_requirements: Tuple[str, ...] = field(default_factory=_empty_tuple)
    source_app_config_ref: str = ""
    created_by_surface: str = "UWG"
    created_at: str = ""
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    lineage_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)

    def __post_init__(self) -> None:
        _validate_status(self.status, "AppRetrievalProfileRecord")
        _validate_app_task(self.app_id, self.task_class, "AppRetrievalProfileRecord")
        if self.freshness_class not in FRESHNESS_CLASS_VOCAB:
            raise AppDomainContractError(
                f"freshness_class {self.freshness_class!r} not in {sorted(FRESHNESS_CLASS_VOCAB)}",
            )


@dataclass(frozen=True)
class AppPromptProfileRecord:
    """Per-(app, task_class) prompt profile — slot shape and forbidden content."""

    prompt_profile_id: str
    app_id: str
    task_class: str
    version: str
    status: str
    output_schema_ref: str
    policy_hash: str = ""
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    required_slots: Tuple[str, ...] = field(default_factory=_empty_tuple)
    optional_slots: Tuple[str, ...] = field(default_factory=_empty_tuple)
    forbidden_content: Tuple[str, ...] = field(default_factory=_empty_tuple)
    prompt_boundary_rules: Tuple[str, ...] = field(default_factory=_empty_tuple)
    source_app_config_ref: str = ""
    created_by_surface: str = "UWG"
    created_at: str = ""
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    lineage_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)

    def __post_init__(self) -> None:
        _validate_status(self.status, "AppPromptProfileRecord")
        _validate_app_task(self.app_id, self.task_class, "AppPromptProfileRecord")


@dataclass(frozen=True)
class AppCapabilityProfileRecord:
    """Per-(app, task_class) capability profile — what L2 may do."""

    capability_profile_id: str
    app_id: str
    task_class: str
    version: str
    status: str
    side_effect_class: str  # one of SIDE_EFFECT_CLASS_VOCAB
    policy_hash: str = ""
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    allowed_tools: Tuple[str, ...] = field(default_factory=_empty_tuple)
    forbidden_tools: Tuple[str, ...] = field(default_factory=_empty_tuple)
    allowed_connectors: Tuple[str, ...] = field(default_factory=_empty_tuple)
    forbidden_connectors: Tuple[str, ...] = field(default_factory=_empty_tuple)
    hitl_required_for: Tuple[str, ...] = field(default_factory=_empty_tuple)
    sandbox_requirements: Tuple[str, ...] = field(default_factory=_empty_tuple)
    source_app_config_ref: str = ""
    created_by_surface: str = "UWG"
    created_at: str = ""
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    lineage_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)

    def __post_init__(self) -> None:
        _validate_status(self.status, "AppCapabilityProfileRecord")
        _validate_app_task(self.app_id, self.task_class, "AppCapabilityProfileRecord")
        if self.side_effect_class not in SIDE_EFFECT_CLASS_VOCAB:
            raise AppDomainContractError(
                f"side_effect_class {self.side_effect_class!r} not in {sorted(SIDE_EFFECT_CLASS_VOCAB)}",
            )


@dataclass(frozen=True)
class AppRouteProfileRecord:
    """Per-(app, task_class) route profile — which routes the app may use."""

    route_profile_id: str
    app_id: str
    task_class: str
    version: str
    status: str
    default_route_id: str
    grounding_required: bool = True
    managed_workflow_allowed: bool = True
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    allowed_route_ids: Tuple[str, ...] = field(default_factory=_empty_tuple)
    l3_dag_ref: str = ""
    source_app_config_ref: str = ""
    created_by_surface: str = "UWG"
    created_at: str = ""
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    lineage_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)

    def __post_init__(self) -> None:
        _validate_status(self.status, "AppRouteProfileRecord")
        _validate_app_task(self.app_id, self.task_class, "AppRouteProfileRecord")
        if not self.default_route_id:
            raise AppDomainContractError(
                f"AppRouteProfileRecord({self.route_profile_id}) requires default_route_id",
            )


@dataclass(frozen=True)
class AppOrchestrationProfileRecord:
    """Per-(app, task_class) orchestration profile — DAG / HOP shape (optional).

    Only HOP / DAG-based app domains populate this. Linear apps may omit the
    contract reference and rely solely on
    AppRouteProfileRecord.
    """

    orchestration_profile_id: str
    app_id: str
    task_class: str
    version: str
    status: str
    orchestration_kind: str  # linear | hop | dag | managed_workflow
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    hop_sequence: Tuple[str, ...] = field(default_factory=_empty_tuple)
    dag_node_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    blueprint_ref: str = ""
    source_app_config_ref: str = ""
    created_by_surface: str = "UWG"
    created_at: str = ""
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    lineage_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)

    def __post_init__(self) -> None:
        _validate_status(self.status, "AppOrchestrationProfileRecord")
        _validate_app_task(self.app_id, self.task_class, "AppOrchestrationProfileRecord")
        if self.orchestration_kind not in {"linear", "hop", "dag", "managed_workflow"}:
            raise AppDomainContractError(
                f"orchestration_kind {self.orchestration_kind!r} invalid",
            )


@dataclass(frozen=True)
class AppFixtureRecord:
    """Per-(app, task_class) fixture — golden, regression, edge_case."""

    fixture_id: str
    app_id: str
    task_class: str
    fixture_type: str  # one of FIXTURE_TYPE_VOCAB
    version: str
    status: str
    input_ref: str
    expected_disposition: str  # ALLOW | DENY | SAFE_ABSTAIN | ESCALATE
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    expected_gate_results: Mapping[str, str] = field(default_factory=dict)
    expected_output_assertions: Tuple[str, ...] = field(default_factory=_empty_tuple)
    source_app_config_ref: str = ""
    created_by_surface: str = "UWG"
    created_at: str = ""
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    lineage_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)

    def __post_init__(self) -> None:
        _validate_status(self.status, "AppFixtureRecord")
        _validate_app_task(self.app_id, self.task_class, "AppFixtureRecord")
        if self.fixture_type not in FIXTURE_TYPE_VOCAB:
            raise AppDomainContractError(
                f"fixture_type {self.fixture_type!r} not in {sorted(FIXTURE_TYPE_VOCAB)}",
            )


@dataclass(frozen=True)
class AppNegativeControlRecord:
    """Per-(app, task_class) negative control — must FAIL for a specific reason."""

    negative_control_id: str
    app_id: str
    task_class: str
    version: str
    status: str
    expected_failure_dimension: str
    expected_failure_reason: str
    input_ref: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    expected_gate_results: Mapping[str, str] = field(default_factory=dict)
    source_app_config_ref: str = ""
    created_by_surface: str = "UWG"
    created_at: str = ""
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    lineage_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)

    def __post_init__(self) -> None:
        _validate_status(self.status, "AppNegativeControlRecord")
        _validate_app_task(self.app_id, self.task_class, "AppNegativeControlRecord")
        if not self.expected_failure_dimension:
            raise AppDomainContractError(
                f"AppNegativeControlRecord({self.negative_control_id}) requires expected_failure_dimension",
            )


@dataclass(frozen=True)
class ApprovedJudgeCalibrationBaseline:
    """UWG-created reliability baseline that may affect future runs only."""

    baseline_id: str
    app_id: str
    task_class: str
    status: str
    judge_id: str
    judge_version: str
    rubric_hash: str
    rubric_version: str
    provider_profile_ref: str
    dataset_id: str
    dataset_version: str
    n: int
    spearman_rho: float
    p_value: float
    threshold: float
    approved_use: str
    approved_at: str
    expires_at: str
    promotion_receipt_ref: str
    uwg_receipt_ref: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    source_app_config_ref: str = ""
    created_by_surface: str = "UWG"
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    lineage_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)

    def __post_init__(self) -> None:
        _validate_status(self.status, "ApprovedJudgeCalibrationBaseline")
        _validate_app_task(
            self.app_id,
            self.task_class,
            "ApprovedJudgeCalibrationBaseline",
        )
        if self.approved_use not in APPROVED_JUDGE_USE_VOCAB:
            raise AppDomainContractError(
                f"approved_use {self.approved_use!r} not in "
                f"{sorted(APPROVED_JUDGE_USE_VOCAB)}"
            )
        if self.n <= 0:
            raise AppDomainContractError("calibration baseline requires n > 0")
        required_identity = {
            "baseline_id": self.baseline_id,
            "judge_id": self.judge_id,
            "judge_version": self.judge_version,
            "rubric_hash": self.rubric_hash,
            "rubric_version": self.rubric_version,
            "provider_profile_ref": self.provider_profile_ref,
            "dataset_id": self.dataset_id,
            "dataset_version": self.dataset_version,
        }
        missing_identity = sorted(
            key for key, value in required_identity.items() if not str(value).strip()
        )
        if missing_identity:
            raise AppDomainContractError(
                "calibration baseline missing identity: " + ",".join(missing_identity)
            )
        if not -1.0 <= self.spearman_rho <= 1.0:
            raise AppDomainContractError("spearman_rho must be in [-1,1]")
        if not -1.0 <= self.threshold <= 1.0:
            raise AppDomainContractError("threshold must be in [-1,1]")
        if self.spearman_rho < self.threshold:
            raise AppDomainContractError("approved baseline must meet its rho threshold")
        if not 0.0 <= self.p_value <= 1.0:
            raise AppDomainContractError("p_value must be in [0,1]")
        if not self.promotion_receipt_ref or not self.uwg_receipt_ref:
            raise AppDomainContractError(
                "promotion_receipt_ref and uwg_receipt_ref are required"
            )
        if self.created_by_surface != "UWG":
            raise AppDomainContractError("calibration baseline must be UWG-created")
        try:
            approved_at = datetime.fromisoformat(self.approved_at)
            expires_at = datetime.fromisoformat(self.expires_at)
        except ValueError as exc:
            raise AppDomainContractError(
                "approved_at and expires_at must be ISO-8601 timestamps"
            ) from exc
        if approved_at.tzinfo is None or expires_at.tzinfo is None:
            raise AppDomainContractError(
                "approved_at and expires_at must include timezone offsets"
            )
        if expires_at <= approved_at:
            raise AppDomainContractError("expires_at must be after approved_at")


# ----------------------------------------------------------------------------
# Top-level manifest
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class AppDomainContractRecord:
    """Top-level per-app domain contract — the entry point at L4.

    Aggregates references to every subcontract record. The runtime resolver
    fetches this by ``(app_id, task_class)`` and then dereferences each ref
    into the typed subcontract record. ``registry_digest_set`` is the tuple
    of all subcontract digests; together with ``deterministic_digest`` of
    this record it forms the replay key.
    """

    app_domain_contract_id: str
    app_id: str
    app_version: str
    domain: str
    owner_surface: str  # always "apps_<name>"
    status: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    deterministic_digest: str = ""
    task_classes: Tuple[TaskClassEntry, ...] = field(default_factory=_empty_tuple)
    input_contract_ref: str = ""
    output_schema_ref: str = ""
    eval_rubric_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    threshold_profile_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    grader_roster_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    retrieval_profile_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    prompt_profile_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    capability_profile_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    route_profile_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    orchestration_profile_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    fixture_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    negative_control_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    # apps-core-contract-rectification-a8f3c2 Phase 1.4 — repair menu contracts.
    # Optional: apps that have not yet defined repair scenarios omit this field.
    repair_profile_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    # apps-core-contract-rectification-a8f3c2 Phase 3.4 — cache and learning policy contracts.
    # Optional: apps may omit when caching is permanently disabled (e.g. underwriting).
    cache_profile_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    # Optional: apps may omit during initial rollout; L6 promotion gate falls back
    # to global defaults when absent.
    learning_profile_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    judge_calibration_baseline_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    policy_hash: str = ""
    blueprint_hash: str = ""
    registry_digest_set: Tuple[str, ...] = field(default_factory=_empty_tuple)
    source_app_config_ref: str = ""
    created_by_surface: str = "UWG"
    created_at: str = ""
    audit_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    lineage_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)

    def __post_init__(self) -> None:
        _validate_status(self.status, "AppDomainContractRecord")
        if not self.app_id:
            raise AppDomainContractError("AppDomainContractRecord.app_id is required")
        if not self.app_id.startswith("apps_"):
            raise AppDomainContractError(
                f"AppDomainContractRecord.app_id {self.app_id!r} must start with 'apps_'",
            )
        if not self.domain:
            raise AppDomainContractError("AppDomainContractRecord.domain is required")
        if self.owner_surface != self.app_id:
            raise AppDomainContractError(
                f"owner_surface {self.owner_surface!r} must equal app_id {self.app_id!r}",
            )
        if self.status == "active" and not self.task_classes:
            raise AppDomainContractError(
                f"active AppDomainContractRecord({self.app_id}) requires at least one task_class",
            )
        if self.status == "active" and not self.negative_control_refs:
            raise AppDomainContractError(
                f"active AppDomainContractRecord({self.app_id}) requires at least one negative_control_ref",
            )


# ----------------------------------------------------------------------------
# Validators
# ----------------------------------------------------------------------------


def _validate_status(status: str, ctx: str) -> None:
    if status not in CONTRACT_STATUS_VOCAB:
        raise AppDomainContractError(
            f"{ctx}.status {status!r} not in {sorted(CONTRACT_STATUS_VOCAB)}",
        )


def _validate_app_task(app_id: str, task_class: str, ctx: str) -> None:
    if not app_id:
        raise AppDomainContractError(f"{ctx}.app_id is required")
    if not app_id.startswith("apps_"):
        raise AppDomainContractError(
            f"{ctx}.app_id {app_id!r} must start with 'apps_'",
        )
    if not task_class:
        raise AppDomainContractError(f"{ctx}.task_class is required")


# ----------------------------------------------------------------------------
# Identity / digest helpers
# ----------------------------------------------------------------------------


def app_domain_record_kind(record: object) -> str:
    """Return the canonical record kind string for a registered record type."""
    return type(record).__name__


APP_DOMAIN_RECORD_TYPES: Tuple[type, ...] = (
    AppDomainContractRecord,
    AppInputContractRecord,
    AppOutputSchemaRecord,
    AppEvalRubricRecord,
    AppThresholdProfileRecord,
    AppGraderRosterRecord,
    AppRetrievalProfileRecord,
    AppPromptProfileRecord,
    AppCapabilityProfileRecord,
    AppRouteProfileRecord,
    AppOrchestrationProfileRecord,
    AppFixtureRecord,
    AppNegativeControlRecord,
    ApprovedJudgeCalibrationBaseline,
)


__all__ = [
    # Errors / vocab
    "AppDomainContractError",
    "CONTRACT_STATUS_VOCAB",
    "GRADER_TYPE_VOCAB",
    "TRAJECTORY_MATCH_MODE_VOCAB",
    "TAXONOMY_CLASS_VOCAB",
    "OUTPUT_TYPE_VOCAB",
    "FRESHNESS_CLASS_VOCAB",
    "SIDE_EFFECT_CLASS_VOCAB",
    "FIXTURE_TYPE_VOCAB",
    "TASK_CLASS_KIND_VOCAB",
    "APPROVED_JUDGE_USE_VOCAB",
    # Building blocks
    "ScoreDimension",
    "TaskClassEntry",
    # Subcontract records
    "AppInputContractRecord",
    "AppOutputSchemaRecord",
    "AppEvalRubricRecord",
    "AppThresholdProfileRecord",
    "AppGraderRosterRecord",
    "AppRetrievalProfileRecord",
    "AppPromptProfileRecord",
    "AppCapabilityProfileRecord",
    "AppRouteProfileRecord",
    "AppOrchestrationProfileRecord",
    "AppFixtureRecord",
    "AppNegativeControlRecord",
    "ApprovedJudgeCalibrationBaseline",
    # Top-level
    "AppDomainContractRecord",
    # Helpers
    "APP_DOMAIN_RECORD_TYPES",
    "app_domain_record_kind",
]
