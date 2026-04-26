"""03.3 L0 Cache, Fallback, and HITL Posture Routes.

Realizes:

- ``ExactCacheRouteDecision``    — 03.3 PHASE 1 §1
- ``SemanticCacheRouteDecision`` — 03.3 PHASE 1 §2
- ``FallbackRouteDecision``      — 03.3 PHASE 1 §3
- ``HITLPostureAnnotation``      — 03.3 PHASE 1 §4
- ``TerminalRetPacket``          — 03.3 §TERMINAL [RET] PACKET REQUIREMENTS

All terminal routes return [RET] packets. None invoke C0, Prompt Assembly, L3, or L2.
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


class TerminalExecutionForm(str, Enum):
    """Only TERMINAL_SHORTCIRCUIT permitted on these routes."""

    TERMINAL_SHORTCIRCUIT = "TERMINAL_SHORTCIRCUIT"


class SafeResponseType(str, Enum):
    """03.3 PHASE 1 §3 FallbackRouteDecision.safe_response_type."""

    CLARIFY = "CLARIFY"
    ABSTAIN = "ABSTAIN"
    REFUSE = "REFUSE"
    SAFE_PARTIAL = "SAFE_PARTIAL"
    UNSUPPORTED_SOURCE = "UNSUPPORTED_SOURCE"
    POLICY_SAFE_EXPLANATION = "POLICY_SAFE_EXPLANATION"


# ---------------------------------------------------------------------------
# R1A Exact cache
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ExactCacheRouteDecision:
    """03.3 PHASE 1 §1 ExactCacheRouteDecision."""

    cache_key: str
    normalized_request_hash: str
    prior_answer_ref: str
    prior_policy_hash: str
    current_policy_hash: str
    freshness_status: str
    tenant_scope_status: str
    schema_compatibility_status: str
    source_snapshot_status: str
    cache_hit_basis: str
    exact_cache_guard_receipt: str
    ret_packet_ref: str
    prior_evidence_contract_ref: str = ""
    route_id: str = "R1A_EXACT_CACHE"
    execution_form: TerminalExecutionForm = TerminalExecutionForm.TERMINAL_SHORTCIRCUIT

    def __post_init__(self) -> None:
        for name in (
            "cache_key",
            "normalized_request_hash",
            "prior_answer_ref",
            "prior_policy_hash",
            "current_policy_hash",
            "freshness_status",
            "tenant_scope_status",
            "schema_compatibility_status",
            "source_snapshot_status",
            "cache_hit_basis",
            "exact_cache_guard_receipt",
            "ret_packet_ref",
            "route_id",
        ):
            _need_str(getattr(self, name), f"ExactCacheRouteDecision.{name}")
        _need_str(
            self.prior_evidence_contract_ref,
            "ExactCacheRouteDecision.prior_evidence_contract_ref",
            allow_empty=True,
        )
        if self.route_id != "R1A_EXACT_CACHE":
            raise DoctrineContractError(
                f"ExactCacheRouteDecision.route_id must be R1A_EXACT_CACHE, got {self.route_id}",
            )
        if not isinstance(self.execution_form, TerminalExecutionForm):
            raise DoctrineContractError(
                "ExactCacheRouteDecision.execution_form must be TerminalExecutionForm",
            )
        # 03.3 §RULES R1A hard no — caller must filter before constructing.
        # We at minimum verify policy compatibility wasn't claimed across mismatched hashes.
        if self.prior_policy_hash and self.current_policy_hash:
            if (
                self.prior_policy_hash != self.current_policy_hash
                and self.cache_hit_basis == "policy_compatible"
            ):
                raise DoctrineContractError(
                    "Cannot claim policy_compatible cache_hit_basis when prior_policy_hash != current_policy_hash",
                )


# ---------------------------------------------------------------------------
# R1B Semantic cache
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SemanticCacheRouteDecision:
    """03.3 PHASE 1 §2 SemanticCacheRouteDecision."""

    semantic_match_id: str
    query_vec_model_id: str
    cached_query_ref: str
    cached_answer_ref: str
    similarity_score: float
    calibrated_threshold: float
    task_class_compatibility: str
    output_contract_compatibility: str
    freshness_risk_status: str
    source_specificity_risk_status: str
    policy_compatibility_status: str
    tenant_scope_status: str
    semantic_cache_guard_receipt: str
    ret_packet_ref: str
    route_id: str = "R1B_SEMANTIC_CACHE"
    execution_form: TerminalExecutionForm = TerminalExecutionForm.TERMINAL_SHORTCIRCUIT

    def __post_init__(self) -> None:
        for name in (
            "semantic_match_id",
            "query_vec_model_id",
            "cached_query_ref",
            "cached_answer_ref",
            "task_class_compatibility",
            "output_contract_compatibility",
            "freshness_risk_status",
            "source_specificity_risk_status",
            "policy_compatibility_status",
            "tenant_scope_status",
            "semantic_cache_guard_receipt",
            "ret_packet_ref",
            "route_id",
        ):
            _need_str(getattr(self, name), f"SemanticCacheRouteDecision.{name}")
        if self.route_id != "R1B_SEMANTIC_CACHE":
            raise DoctrineContractError(
                f"SemanticCacheRouteDecision.route_id must be R1B_SEMANTIC_CACHE, got {self.route_id}",
            )
        if not isinstance(self.execution_form, TerminalExecutionForm):
            raise DoctrineContractError(
                "SemanticCacheRouteDecision.execution_form must be TerminalExecutionForm",
            )
        for name in ("similarity_score", "calibrated_threshold"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise DoctrineContractError(f"SemanticCacheRouteDecision.{name} must be float")
            if value != value:  # NaN
                raise DoctrineContractError(f"SemanticCacheRouteDecision.{name} must not be NaN")
            if value < 0.0 or value > 1.0:
                raise DoctrineContractError(
                    f"SemanticCacheRouteDecision.{name} must be in [0,1], got {value}",
                )
        # 03.3 §RULES R1B — similarity must clear threshold.
        if self.similarity_score < self.calibrated_threshold:
            raise DoctrineContractError(
                f"R1B similarity_score {self.similarity_score} below calibrated_threshold "
                f"{self.calibrated_threshold}; route is invalid",
            )


# ---------------------------------------------------------------------------
# R5 Fallback
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FallbackRouteDecision:
    """03.3 PHASE 1 §3 FallbackRouteDecision."""

    safe_response_type: SafeResponseType
    reason_codes: tuple[str, ...]
    fallback_guard_receipt: str
    ret_packet_ref: str
    missing_critical_fields: tuple[str, ...] = field(default_factory=tuple)
    unsupported_source_expectations: tuple[str, ...] = field(default_factory=tuple)
    safety_or_policy_blockers: tuple[str, ...] = field(default_factory=tuple)
    weak_support_notes: tuple[str, ...] = field(default_factory=tuple)
    fallback_chain_terminal_entry: str = "R5_FALLBACK"
    route_id: str = "R5_FALLBACK"
    execution_form: TerminalExecutionForm = TerminalExecutionForm.TERMINAL_SHORTCIRCUIT

    def __post_init__(self) -> None:
        if not isinstance(self.safe_response_type, SafeResponseType):
            raise DoctrineContractError(
                "FallbackRouteDecision.safe_response_type must be SafeResponseType",
            )
        # 03.3 §RULES R5 hard no — no vague success: at least one reason_code required.
        _need_str_tuple(
            self.reason_codes,
            "FallbackRouteDecision.reason_codes",
            max_len=_MAX_REASON,
        )
        if len(self.reason_codes) == 0:
            raise DoctrineContractError(
                "R5 FallbackRouteDecision requires at least one reason_code (no silent fallback)",
            )
        for name in ("fallback_guard_receipt", "ret_packet_ref", "fallback_chain_terminal_entry", "route_id"):
            _need_str(getattr(self, name), f"FallbackRouteDecision.{name}")
        for name in (
            "missing_critical_fields",
            "unsupported_source_expectations",
            "safety_or_policy_blockers",
            "weak_support_notes",
        ):
            _need_str_tuple(getattr(self, name), f"FallbackRouteDecision.{name}", max_len=_MAX_REASON)
        if self.fallback_chain_terminal_entry != "R5_FALLBACK":
            raise DoctrineContractError(
                "FallbackRouteDecision.fallback_chain_terminal_entry must be R5_FALLBACK",
            )
        if self.route_id != "R5_FALLBACK":
            raise DoctrineContractError(
                f"FallbackRouteDecision.route_id must be R5_FALLBACK, got {self.route_id}",
            )
        if not isinstance(self.execution_form, TerminalExecutionForm):
            raise DoctrineContractError(
                "FallbackRouteDecision.execution_form must be TerminalExecutionForm",
            )


# ---------------------------------------------------------------------------
# HITL posture
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HITLPostureAnnotation:
    """03.3 PHASE 1 §4 HITLPostureAnnotation.

    NOT sovereign authority. Pure annotation requiring downstream re-clearance.
    """

    hitl_required: bool
    hitl_reason_codes: tuple[str, ...]
    human_review_packet_required: bool = True
    freeze_before_review: bool = True
    re_clearance_required: bool = True
    human_input_origin_trust: str = "untrusted_human_data"
    l5_reclearance_required: bool = True
    exit_review_required: bool = True
    uwg_required_for_write: bool = True
    hitl_not_sovereign_assertion: bool = True

    def __post_init__(self) -> None:
        for name in (
            "hitl_required",
            "human_review_packet_required",
            "freeze_before_review",
            "re_clearance_required",
            "l5_reclearance_required",
            "exit_review_required",
            "uwg_required_for_write",
            "hitl_not_sovereign_assertion",
        ):
            _need_bool(getattr(self, name), f"HITLPostureAnnotation.{name}")
        _need_str(
            self.human_input_origin_trust,
            "HITLPostureAnnotation.human_input_origin_trust",
        )
        _need_str_tuple(
            self.hitl_reason_codes,
            "HITLPostureAnnotation.hitl_reason_codes",
            max_len=_MAX_REASON,
        )
        if self.hitl_required and len(self.hitl_reason_codes) == 0:
            raise DoctrineContractError(
                "HITLPostureAnnotation.hitl_required=True requires at least one reason_code",
            )
        # 03.3 §HITL hard no — non-sovereign assertion must be True.
        if not self.hitl_not_sovereign_assertion:
            raise DoctrineContractError(
                "HITLPostureAnnotation.hitl_not_sovereign_assertion must be True; "
                "human input is data, not sovereign authority",
            )
        if self.human_input_origin_trust != "untrusted_human_data":
            raise DoctrineContractError(
                "HITLPostureAnnotation.human_input_origin_trust must be 'untrusted_human_data'",
            )


# ---------------------------------------------------------------------------
# Terminal [RET] packet
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TerminalRetPacket:
    """03.3 §TERMINAL [RET] PACKET REQUIREMENTS.

    Emitted to Exit Eval & Control by terminal routes (R1A/R1B/R5).
    """

    request_id: str
    run_id: str
    trace_root: str
    route_id: str
    route_digest_ref: str
    policy_hash: str
    blueprint_hash: str
    replay_key: str
    reason_codes: tuple[str, ...]
    confidence: float
    support_status: str
    freshness_status: str
    tenant_scope_status: str
    safe_response_ref: str = ""
    cached_answer_ref: str = ""
    prior_evidence_contract_ref: str = ""
    execution_form: TerminalExecutionForm = TerminalExecutionForm.TERMINAL_SHORTCIRCUIT
    exit_review_required: bool = True
    no_l2_execution_assertion: bool = True
    no_l4_write_assertion: bool = True

    def __post_init__(self) -> None:
        for name in (
            "request_id",
            "run_id",
            "trace_root",
            "route_id",
            "route_digest_ref",
            "policy_hash",
            "blueprint_hash",
            "replay_key",
            "support_status",
            "freshness_status",
            "tenant_scope_status",
        ):
            _need_str(getattr(self, name), f"TerminalRetPacket.{name}")
        for name in ("safe_response_ref", "cached_answer_ref", "prior_evidence_contract_ref"):
            _need_str(getattr(self, name), f"TerminalRetPacket.{name}", allow_empty=True)
        if self.route_id not in ("R1A_EXACT_CACHE", "R1B_SEMANTIC_CACHE", "R5_FALLBACK"):
            raise DoctrineContractError(
                f"TerminalRetPacket.route_id must be R1A/R1B/R5; got {self.route_id}",
            )
        if not isinstance(self.execution_form, TerminalExecutionForm):
            raise DoctrineContractError(
                "TerminalRetPacket.execution_form must be TerminalExecutionForm",
            )
        for name in (
            "exit_review_required",
            "no_l2_execution_assertion",
            "no_l4_write_assertion",
        ):
            _need_bool(getattr(self, name), f"TerminalRetPacket.{name}")
        if not (self.exit_review_required and self.no_l2_execution_assertion and self.no_l4_write_assertion):
            raise DoctrineContractError(
                "TerminalRetPacket assertions must all be True (Exit must review; no L2/L4)",
            )
        _need_str_tuple(self.reason_codes, "TerminalRetPacket.reason_codes", max_len=_MAX_REASON)
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
            raise DoctrineContractError("TerminalRetPacket.confidence must be float")
        if self.confidence != self.confidence or self.confidence < 0.0 or self.confidence > 1.0:
            raise DoctrineContractError("TerminalRetPacket.confidence must be in [0,1]")


__all__ = [
    "ExactCacheRouteDecision",
    "FallbackRouteDecision",
    "HITLPostureAnnotation",
    "SafeResponseType",
    "SemanticCacheRouteDecision",
    "TerminalExecutionForm",
    "TerminalRetPacket",
]
