"""FinalEvidenceContract — C0's only output to Prompt Assembly.

Spec sections (C0 Context Engine.md):
- C0.5 EvidenceContract output (lines 617-622) — verification + scoring
- FINAL C0 EVIDENCE CONTRACT detailed shape (lines 745-803)
- C0 OUTPUT SCHEMA YAML (lines 1010-1133)

Hard invariants enforced in dataclass:
- C0.I11 — output is a contract, not an answer (no answer/route/tool fields)
- C0.I12 — only verified, labeled, budgeted, priority-ranked context
- recommended_disposition only suggests; cannot self-authorize (C0.I10)
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Mapping

from .evidence_contract import ScoreBreakdown
from .evidence_projections import (
    BackgroundEvidence,
    ContradictsEvidence,
    DefinitionEntry,
    ExcludedEntry,
    MustUseEvidence,
    SupportingEvidence,
)
from .hydration import HydratedChunk
from .verdicts import (
    EvidenceClass,
    GapType,
    RecommendedDisposition,
    SupportStatus,
)

# ScoreBreakdown is the canonical definition in evidence_contract.py.
# Re-exported from this module for callers that only import the final contract.


# Fields that MUST NOT appear on FinalEvidenceContract — defense-in-depth.
# Mirrors the intake module's authority-boundary discipline.
FORBIDDEN_CONTRACT_FIELDS: frozenset[str] = frozenset(
    {
        "final_answer",
        "answer_text",
        "route_decision",
        "proposed_route",
        "selected_route",
        "tool_call",
        "tool_invocation",
        "model_execution_result",
        "capability_token",
        "uwg_commit_request",
        "model_response",
        "generated_prose",
        "permitted_next_tool",
    }
)


@dataclass(frozen=True)
class FreshnessReport:
    """Final-contract freshness_report — spec lines 1082-1086."""

    freshness_class: str
    newest_source_age: str = ""
    stale_sources: tuple[str, ...] = ()
    version_mismatches: tuple[str, ...] = ()


@dataclass(frozen=True)
class AclReport:
    """Final-contract acl_report — spec lines 1088-1092."""

    tenant_scope: str
    cleared_sources: tuple[str, ...] = ()
    blocked_sources_count: int = 0
    data_classes_seen: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.blocked_sources_count < 0:
            raise ValueError("blocked_sources_count must be >= 0")


@dataclass(frozen=True)
class PromptBudgetHint:
    """Final-contract prompt_budget_hint — spec lines 1107-1112."""

    pack_order: tuple[str, ...] = ()
    must_keep_evidence_ids: tuple[str, ...] = ()
    trim_first_evidence_ids: tuple[str, ...] = ()
    contradiction_keepers: tuple[str, ...] = ()
    max_context_tokens: int = 0
    estimated_context_tokens: int = 0

    def __post_init__(self) -> None:
        if self.max_context_tokens < 0:
            raise ValueError("max_context_tokens must be >= 0")
        if self.estimated_context_tokens < 0:
            raise ValueError("estimated_context_tokens must be >= 0")


@dataclass(frozen=True)
class BudgetReport:
    """Final-contract budget_report — spec lines 1123-1128."""

    retrieval_passes: int = 0
    graph_hops_used: int = 0
    latency_ms: int = 0
    cost_tier_used: str = "standard"
    token_estimate: int = 0
    budget_remaining: str = ""

    def __post_init__(self) -> None:
        if self.retrieval_passes < 0 or self.graph_hops_used < 0:
            raise ValueError("counters must be non-negative")
        if self.latency_ms < 0 or self.token_estimate < 0:
            raise ValueError("latency/token counters must be non-negative")


@dataclass(frozen=True)
class ReplayMetadata:
    """Final-contract replay_metadata — spec lines 1130-1133."""

    retrieval_snapshot_id: str = ""
    policy_hash: str = ""
    blueprint_hash: str = ""
    route_replay_key: str = ""
    evidence_contract_hash: str = ""
    source_manifest_hash: str = ""


@dataclass(frozen=True)
class LineageEntry:
    """Per-evidence lineage record — spec final-contract 1073-1077."""

    evidence_id: str
    found_by: str  # retrieval lane label
    expanded_by: str = ""
    rerank_reason: str = ""


@dataclass(frozen=True)
class ContradictionFlagOut:
    """Final-contract contradiction record — schema lines 1094-1099."""

    type: str
    source_a: str
    source_b: str
    severity: str = "medium"
    summary: str = ""
    required_downstream_behavior: str = "caveat"


@dataclass(frozen=True)
class UnresolvedGapOut:
    """Final-contract gap record — schema lines 1101-1105."""

    gap_type: GapType
    severity: str = "medium"
    impact_on_answer: str = ""
    suggested_next_step: str = ""


@dataclass(frozen=True)
class FinalEvidenceContract:
    """The C0 output. Read-only. Cannot carry answers, routes, or tools.

    Spec: C0 Context Engine_detailed.md OUTPUT SCHEMA (lines 1010-1133).
    Top-level identity fields (route_replay_key, policy_hash, blueprint_hash)
    are duplicated into ``replay_metadata`` for downstream consumers that read
    only one of the two surfaces — they MUST agree.
    """

    contract_id: str
    route_id: str
    route_replay_key: str = ""
    policy_hash: str = ""
    blueprint_hash: str = ""
    status: SupportStatus = SupportStatus.EMPTY
    support_score: float = 0.0

    score_breakdown: ScoreBreakdown = field(default_factory=ScoreBreakdown)
    # Hydrated-chunk views (kept for replay + back-compat). Typed projections
    # below are the spec-canonical surfaces consumed by Prompt Assembly.
    must_use: tuple[HydratedChunk, ...] = ()
    supporting: tuple[HydratedChunk, ...] = ()
    contradicts: tuple[HydratedChunk, ...] = ()
    background: tuple[HydratedChunk, ...] = ()
    definitions: tuple[HydratedChunk, ...] = ()
    lineage: tuple[LineageEntry, ...] = ()
    excluded: tuple[tuple[str, str], ...] = ()  # (evidence_id, reason)

    # Spec-canonical typed projections (lines 1041-1080).
    must_use_view: tuple[MustUseEvidence, ...] = ()
    supporting_view: tuple[SupportingEvidence, ...] = ()
    contradicts_view: tuple[ContradictsEvidence, ...] = ()
    background_view: tuple[BackgroundEvidence, ...] = ()
    definitions_view: tuple[DefinitionEntry, ...] = ()
    excluded_view: tuple[ExcludedEntry, ...] = ()

    contradiction_flags: tuple[ContradictionFlagOut, ...] = ()
    unresolved_gaps: tuple[UnresolvedGapOut, ...] = ()

    freshness_report: FreshnessReport | None = None
    acl_report: AclReport | None = None
    prompt_budget_hint: PromptBudgetHint = field(default_factory=PromptBudgetHint)
    recommended_disposition: RecommendedDisposition = RecommendedDisposition.PROCEED
    budget_report: BudgetReport = field(default_factory=BudgetReport)
    replay_metadata: ReplayMetadata = field(default_factory=ReplayMetadata)

    refine_attempts: int = 0
    refine_tactic: str = ""
    refine_delta: str = ""
    remaining_gaps: tuple[str, ...] = ()

    blocked_reason: str = ""
    """Populated when status=BLOCKED — explains which gate fired."""

    extras: Mapping[str, str] = field(default_factory=dict)
    """Free-form replay/audit-only fields. Never carries answers."""

    def __post_init__(self) -> None:
        if not (0.0 <= self.support_score <= 1.0):
            raise ValueError(f"support_score={self.support_score} must be in [0,1]")
        if not isinstance(self.status, SupportStatus):
            raise TypeError("status must be SupportStatus")
        if not isinstance(self.recommended_disposition, RecommendedDisposition):
            raise TypeError("recommended_disposition must be RecommendedDisposition")
        # Top-level identity fields must agree with replay_metadata (defense-
        # in-depth: dispatcher always populates both, but we verify in case a
        # caller constructs the contract by hand).
        rm = self.replay_metadata
        if rm.route_replay_key and self.route_replay_key and rm.route_replay_key != self.route_replay_key:
            raise ValueError("route_replay_key drift between top-level and replay_metadata")
        if rm.policy_hash and self.policy_hash and rm.policy_hash != self.policy_hash:
            raise ValueError("policy_hash drift between top-level and replay_metadata")
        if rm.blueprint_hash and self.blueprint_hash and rm.blueprint_hash != self.blueprint_hash:
            raise ValueError("blueprint_hash drift between top-level and replay_metadata")
        # BLOCKED status must include a reason (G0/G1/G10).
        if self.status is SupportStatus.BLOCKED and not self.blocked_reason:
            raise ValueError("BLOCKED contract must include blocked_reason")
        # C0.I7 — CONFLICTED status must surface contradiction_flags.
        if self.status is SupportStatus.CONFLICTED and not self.contradiction_flags:
            raise ValueError(
                "CONFLICTED contract must include contradiction_flags (C0.I7)",
            )
        # C0.I8 — WEAK_WITH_CAVEATS must declare gaps OR contradictions.
        if (
            self.status is SupportStatus.WEAK_WITH_CAVEATS
            and not self.unresolved_gaps
            and not self.contradiction_flags
        ):
            raise ValueError(
                "WEAK_WITH_CAVEATS must surface gaps or contradictions (C0.I8)",
            )
        # C0.I11 — output is a contract, not an answer.
        for forbidden in FORBIDDEN_CONTRACT_FIELDS:
            if forbidden in self.extras:
                raise ValueError(
                    f"extras cannot carry {forbidden!r} — C0 is read-only "
                    "(C0.I11: output is a contract, not an answer)",
                )

    def by_class(self, cls: EvidenceClass) -> tuple[HydratedChunk, ...]:
        if cls is EvidenceClass.MUST_USE:
            return self.must_use
        if cls is EvidenceClass.SUPPORTING:
            return self.supporting
        if cls is EvidenceClass.CONTRADICTS:
            return self.contradicts
        if cls is EvidenceClass.BACKGROUND:
            return self.background
        if cls is EvidenceClass.DEFINITIONS:
            return self.definitions
        return ()

    def to_replay_dict(self) -> dict:
        """Stable serializable view for replay metadata. Strips evidence text."""
        d = asdict(self)
        for cls_key in ("must_use", "supporting", "contradicts", "background", "definitions"):
            for h in d.get(cls_key, []):
                cand = h.get("candidate") if isinstance(h, dict) else None
                if isinstance(cand, dict):
                    cand.pop("text", None)
        return d

    def hash(self) -> str:
        """Content hash for replay_metadata.evidence_contract_hash."""
        payload = json.dumps(self.to_replay_dict(), default=str, sort_keys=True)
        return hashlib.blake2b(payload.encode("utf-8"), digest_size=16).hexdigest()


def seal_final_contract(
    contract: FinalEvidenceContract,
) -> FinalEvidenceContract:
    """Stamp evidence_contract_hash into replay_metadata and return frozen contract.

    Sealing is the final action of the C0 dispatcher; downstream callers
    receive only the sealed contract. Sealing does NOT mutate evidence.
    """
    rm = contract.replay_metadata
    if rm.evidence_contract_hash:
        return contract
    sealed_hash = contract.hash()
    new_rm = ReplayMetadata(
        retrieval_snapshot_id=rm.retrieval_snapshot_id,
        policy_hash=rm.policy_hash,
        blueprint_hash=rm.blueprint_hash,
        route_replay_key=rm.route_replay_key,
        evidence_contract_hash=sealed_hash,
        source_manifest_hash=rm.source_manifest_hash,
    )
    # Use dataclasses.replace via dict route to avoid circular import.
    fields_dict = {f: getattr(contract, f) for f in contract.__dataclass_fields__}  # guardian: allow-hallucinated-tool-name -- getattr is Python stdlib; reads frozen dataclass fields by name
    fields_dict["replay_metadata"] = new_rm
    return FinalEvidenceContract(**fields_dict)


def compute_source_manifest_hash(source_ids: tuple[str, ...]) -> str:
    """Deterministic source_manifest_hash — spec line 1133.

    Hashes the SORTED, DE-DUPED list of source_ids. Empty input -> empty
    hash. Caller passes whatever set of source identities are in the
    final contract (canonical_source_path values).
    """
    if not source_ids:
        return ""
    payload = json.dumps(
        sorted(set(source_ids)), separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.blake2b(payload, digest_size=12).hexdigest()


__all__ = [
    "AclReport",
    "BudgetReport",
    "ContradictionFlagOut",
    "FORBIDDEN_CONTRACT_FIELDS",
    "FinalEvidenceContract",
    "FreshnessReport",
    "LineageEntry",
    "PromptBudgetHint",
    "ReplayMetadata",
    "ScoreBreakdown",
    "UnresolvedGapOut",
    "compute_source_manifest_hash",
    "seal_final_contract",
]
