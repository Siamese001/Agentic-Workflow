"""Canonical contracts for apps_rg C0.3 resume-graph selection.

The module is deliberately pure-Python and dependency-light. It owns the JSON
shape for pre-target authority decisions, terminal candidate decisions,
replayable traversal events, and canonical section plan digests. Targeting
signals may affect ranking only after an authority decision has passed.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

AUTHORITY_SCHEMA_VERSION = "c03_pretarget_authority_v1"
CANDIDATE_DECISION_SCHEMA_VERSION = "graph_candidate_decision_v2"
TRAVERSAL_EVENT_SCHEMA_VERSION = "graph_traversal_event_v1"
TRAVERSAL_RECEIPT_SCHEMA_VERSION = "graph_traversal_receipt_v1"
CANONICAL_PLAN_SCHEMA_VERSION = "c03_canonical_section_graph_plan_v1"
CANONICAL_AUTHORITY_SOURCE = "augmented_skills_graph"
SELECTION_POLICY_SCHEMA_VERSION = "resume_graph_selection_policy_v2"
ALLOCATION_PLAN_SCHEMA_VERSION = "resume_graph_allocation_plan_v1"
USAGE_LEDGER_SCHEMA_VERSION = "resume_graph_usage_ledger_v1"
GRAPH_CLAIM_BINDING_SCHEMA_VERSION = "graph_claim_binding_v1"
WHOLE_RESUME_CONTRACT_SCHEMA_VERSION = "whole_resume_graph_evidence_contract_v1"

TERMINAL_DECISIONS = frozenset({"selected", "rejected"})
ACTIVE_STATUSES = frozenset({"ACTIVE", "ACTIVE_CONFIRMED"})
BLOCKED_ACTIVATION_STATUSES = frozenset(
    {
        "DRAFT",
        "INTERNAL_ONLY",
        "ACTIVE_INTERNAL_ONLY",
        "DO_NOT_PROMOTE",
        "BLOCKED",
        "USER_CONFIRMED_PENDING_SOURCE",
    }
)
BLOCKED_SUPPORT_LEVELS = frozenset(
    {
        "INTERNAL_ONLY",
        "REPO_EVIDENCE_PORTFOLIO",
        "TARGETING_ONLY",
        "STYLE_ONLY",
        "BLOCKED",
        "USER_CONFIRMED_PENDING_SOURCE",
    }
)
BLOCKED_POLICY_TOKENS = (
    "internal_only",
    "pending_source",
    "weak_snippet",
    "repo_portfolio",
    "targeting_only",
    "style_only",
    "do_not_promote",
    "blocked",
    "forbidden",
)


def stable_digest(value: Any) -> str:
    """Return a deterministic SHA-256 digest for JSON-compatible data."""
    body = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class ResumeGraphSelectionPolicyV2:
    """Immutable policy input for section traversal and whole-resume allocation."""

    graph_snapshot_digest: str
    graph_version: str
    final_output_mode: str = "bullets_canonical_narratives_derived"
    max_hops: int = 2
    max_nodes: int = 20000
    max_edges: int = 20000
    max_candidates: int = 20000
    max_fact_reuse: int = 3
    max_source_family_share: float = 0.5
    hard_uniqueness_rules: tuple[str, ...] = (
        "skill_id",
        "metric_outcome_id",
        "normalized_metric_signature",
    )
    confidence_policy_version: str = "resume_graph_confidence_v1"
    bounded_refinement_attempts: int = 1
    section_budgets: Mapping[str, Mapping[str, int]] = field(default_factory=dict)
    authority_filters: tuple[str, ...] = (
        "authority_pass",
        "external_claim_eligible",
        "section_route_eligible",
        "source_lineage_present",
        "graph_path_present",
    )
    target_alignment_weights: Mapping[str, float] = field(
        default_factory=lambda: {"proof": 1.0, "target": 1.0}
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SELECTION_POLICY_SCHEMA_VERSION,
            "graph_snapshot_digest": self.graph_snapshot_digest,
            "graph_version": self.graph_version,
            "final_output_mode": self.final_output_mode,
            "section_budgets": {
                str(section): dict(sorted(dict(budget).items()))
                for section, budget in sorted(self.section_budgets.items())
            },
            "authority_filters": list(self.authority_filters),
            "traversal_budgets": {
                "max_hops": self.max_hops,
                "max_nodes": self.max_nodes,
                "max_edges": self.max_edges,
                "max_candidates": self.max_candidates,
            },
            "hard_uniqueness_rules": list(self.hard_uniqueness_rules),
            "max_fact_reuse": self.max_fact_reuse,
            "max_source_family_share": self.max_source_family_share,
            "target_alignment_weights": dict(sorted(self.target_alignment_weights.items())),
            "confidence_policy_version": self.confidence_policy_version,
            "bounded_refinement_attempts": self.bounded_refinement_attempts,
        }

    @property
    def policy_digest(self) -> str:
        return stable_digest(self.to_dict())


@dataclass(frozen=True, slots=True)
class ResumeGraphAllocationPlanV1:
    """Immutable serialization boundary for one section or whole-resume allocation."""

    allocation_scope: str
    graph_digest: str
    policy_digest: str
    assignments: tuple[Mapping[str, Any], ...]
    candidate_decisions: tuple[Mapping[str, Any], ...]
    section_plan_digests: Mapping[str, str] = field(default_factory=dict)
    representation_policy: Mapping[str, Any] = field(default_factory=dict)
    solver_metadata: Mapping[str, Any] = field(default_factory=dict)
    hard_constraints: Mapping[str, Any] = field(default_factory=dict)
    uniqueness_receipt: Mapping[str, Any] = field(default_factory=dict)
    budget_receipt: Mapping[str, Any] = field(default_factory=dict)
    candidate_conservation_receipt: Mapping[str, Any] = field(default_factory=dict)
    durable_graph_state_mutated: bool = False

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema_version": ALLOCATION_PLAN_SCHEMA_VERSION,
            "allocation_scope": self.allocation_scope,
            "global_uniqueness_claimed": self.allocation_scope == "WHOLE_RESUME",
            "graph_digest": self.graph_digest,
            "policy_digest": self.policy_digest,
            "section_plan_digests": dict(sorted(self.section_plan_digests.items())),
            "representation_policy": dict(self.representation_policy),
            "assignments": [dict(row) for row in self.assignments],
            "candidate_decisions": [dict(row) for row in self.candidate_decisions],
            "solver_metadata": dict(self.solver_metadata),
            "hard_constraints": dict(self.hard_constraints),
            "uniqueness_receipt": dict(self.uniqueness_receipt),
            "budget_receipt": dict(self.budget_receipt),
            "candidate_conservation_receipt": dict(
                self.candidate_conservation_receipt
            ),
            "durable_graph_state_mutated": bool(self.durable_graph_state_mutated),
        }
        digest = stable_digest(payload)
        payload["allocation_plan_digest"] = digest
        payload["allocation_plan_id"] = f"resume_graph_allocation:{digest[:20]}"
        return payload


@dataclass(frozen=True, slots=True)
class ResumeGraphUsageLedgerV1:
    """Current-run-only reservations derived from a frozen allocation plan."""

    allocation_plan_digest: str
    allocation_scope: str
    reservations: tuple[Mapping[str, Any], ...]
    current_run_only: bool = True
    durable_graph_state_mutated: bool = False

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema_version": USAGE_LEDGER_SCHEMA_VERSION,
            "allocation_plan_digest": self.allocation_plan_digest,
            "allocation_scope": self.allocation_scope,
            "current_run_only": bool(self.current_run_only),
            "durable_graph_state_mutated": bool(self.durable_graph_state_mutated),
            "reservations": [dict(row) for row in self.reservations],
            "reservation_count": len(self.reservations),
        }
        payload["usage_ledger_digest"] = stable_digest(payload)
        return payload


@dataclass(frozen=True, slots=True)
class GraphClaimBindingV1:
    """Exact visible-claim binding to one frozen allocation assignment."""

    section_id: str
    claim_unit_id: str
    visible_claim_text: str
    allocation_plan_digest: str
    skill_ids: tuple[str, ...]
    fact_ids: tuple[str, ...]
    graph_path_ids: tuple[str, ...]
    edge_ids: tuple[str, ...]
    citation_refs: tuple[str, ...]
    metric_outcome_id: str = ""
    metric_value: str = ""
    metric_unit: str = ""
    normalized_metric_signature: str = ""
    proof_strength_raw: float = 0.0
    target_alignment_score: float = 0.0
    claim_entailment_score: float = 0.0
    metric_binding_score: float = 0.0
    path_confidence_raw: float = 0.0
    source_independence_score: float = 0.0
    selection_margin: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        text = str(self.visible_claim_text or "").strip()
        return {
            "schema_version": GRAPH_CLAIM_BINDING_SCHEMA_VERSION,
            "section_id": self.section_id,
            "claim_unit_id": self.claim_unit_id,
            "visible_claim_text": text,
            "visible_claim_hash": stable_digest({"text": text}),
            "allocation_plan_digest": self.allocation_plan_digest,
            "skill_ids": list(self.skill_ids),
            "fact_ids": list(self.fact_ids),
            "metric_outcome_id": self.metric_outcome_id,
            "metric_value": self.metric_value,
            "metric_unit": self.metric_unit,
            "normalized_metric_signature": self.normalized_metric_signature,
            "graph_path_ids": list(self.graph_path_ids),
            "edge_ids": list(self.edge_ids),
            "citation_refs": list(self.citation_refs),
            "proof_strength_raw": round(float(self.proof_strength_raw), 6),
            "target_alignment_score": round(float(self.target_alignment_score), 6),
            "claim_entailment_score": round(float(self.claim_entailment_score), 6),
            "metric_binding_score": round(float(self.metric_binding_score), 6),
            "path_confidence_raw": round(float(self.path_confidence_raw), 6),
            "source_independence_score": round(float(self.source_independence_score), 6),
            "selection_margin": round(float(self.selection_margin), 6),
        }


@dataclass(frozen=True, slots=True)
class WholeResumeGraphEvidenceContractV1:
    """Release-gate result for the materialized whole-resume graph contract."""

    allocation_plan_digest: str
    section_ids: tuple[str, ...]
    section_parity_pass: bool
    rendered_claim_reconciliation_pass: bool
    zero_reuse_pass: bool
    traversal_conservation_pass: bool
    confidence_calibration_status: str
    digest_parity_pass: bool
    alternative_representation_pass: bool
    failures: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        status = str(self.confidence_calibration_status or "UNKNOWN").upper()
        pass_ = (
            self.section_parity_pass
            and self.rendered_claim_reconciliation_pass
            and self.zero_reuse_pass
            and self.traversal_conservation_pass
            and status == "PASS"
            and self.digest_parity_pass
            and self.alternative_representation_pass
            and not self.failures
        )
        return {
            "schema_version": WHOLE_RESUME_CONTRACT_SCHEMA_VERSION,
            "allocation_plan_digest": self.allocation_plan_digest,
            "section_ids": list(self.section_ids),
            "section_parity_pass": self.section_parity_pass,
            "rendered_claim_reconciliation_pass": self.rendered_claim_reconciliation_pass,
            "zero_reuse_pass": self.zero_reuse_pass,
            "traversal_conservation_pass": self.traversal_conservation_pass,
            "confidence_calibration_status": status,
            "digest_parity_pass": self.digest_parity_pass,
            "alternative_representation_pass": self.alternative_representation_pass,
            "failures": list(self.failures),
            "pass": pass_,
        }


def _strings(values: Iterable[Any] | None) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for raw in values or ():
        text = str(raw or "").strip()
        if text and text not in seen:
            seen.add(text)
            out.append(text)
    return out


def _policy_blocked(value: str) -> bool:
    text = str(value or "").strip().casefold()
    return bool(text) and any(token in text for token in BLOCKED_POLICY_TOKENS)


def evaluate_pretarget_authority(
    *,
    candidate_id: str,
    candidate_type: str,
    section_id: str,
    section_allowed: bool,
    activation_status: str = "",
    support_level: str = "",
    external_claim_policy: str = "",
    external_eligible: bool | None = None,
    claim_eligible: bool | None = None,
    source_refs: Iterable[Any] | None = None,
    path_present: bool = True,
    approved: bool | None = None,
    approval_status: str = "",
    extra_reason_codes: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Evaluate authority without consulting target role, JD, or briefing text.

    Empty optional metadata is treated as unknown rather than implicitly blocked;
    explicit negative metadata is fail-closed. Callers that know a field is
    mandatory should pass its explicit boolean value.
    """

    cid = str(candidate_id or "").strip()
    ctype = str(candidate_type or "").strip() or "unknown"
    activation = str(activation_status or "").strip().upper()
    support = str(support_level or "").strip().upper()
    policy = str(external_claim_policy or "").strip()
    sources = _strings(source_refs)
    reasons = _strings(extra_reason_codes)

    if not cid:
        reasons.append("missing_candidate_id")
    if not section_allowed:
        reasons.append("section_not_allowed")
    if activation:
        if activation in BLOCKED_ACTIVATION_STATUSES or activation not in ACTIVE_STATUSES:
            reasons.append(f"activation_status_blocked:{activation}")
    if support in BLOCKED_SUPPORT_LEVELS:
        reasons.append(f"support_level_blocked:{support}")
    if _policy_blocked(policy):
        reasons.append(f"external_claim_policy_blocked:{policy}")
    if external_eligible is False:
        reasons.append("external_eligible_false")
    if claim_eligible is False:
        reasons.append("claim_eligible_false")
    if approved is False:
        reasons.append("approved_false")
    approval = str(approval_status or "").strip().upper()
    if approval and not approval.startswith("APPROVED"):
        reasons.append(f"approval_status_not_approved:{approval}")
    if not path_present:
        reasons.append("missing_graph_path")
    if ctype in {"role_episode_root", "leaf_skill", "source_fact", "metric_outcome"} and not sources:
        reasons.append("missing_source_lineage")

    reasons = _strings(reasons)
    return {
        "schema_version": AUTHORITY_SCHEMA_VERSION,
        "candidate_id": cid,
        "candidate_type": ctype,
        "section_id": str(section_id or ""),
        "authority_source": CANONICAL_AUTHORITY_SOURCE,
        "authority_pass": not reasons,
        "reason_codes": reasons,
        "section_allowed": bool(section_allowed),
        "activation_status": activation,
        "support_level": support,
        "external_claim_policy": policy,
        "external_eligible": external_eligible,
        "claim_eligible": claim_eligible,
        "approved": approved,
        "approval_status": approval,
        "source_refs": sources,
        "path_present": bool(path_present),
        "targeting_consulted": False,
        "authority_evaluated_before_targeting": True,
    }


def build_candidate_decision(
    *,
    section_id: str,
    candidate_id: str,
    candidate_type: str,
    candidate_path_id: str,
    decision: str,
    reason_codes: Iterable[str],
    authority: Mapping[str, Any],
    hop_depth: int,
    parent_id: str = "",
    root_id: str = "",
    employer_lane: str = "",
    proof_strength_raw: float = 0.0,
    target_alignment_score: float = 0.0,
    ranking_score: float = 0.0,
    path_signature: str = "",
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build one terminal candidate-decision row."""
    terminal = str(decision or "").strip().lower()
    if terminal not in TERMINAL_DECISIONS:
        raise ValueError(f"candidate decision must be terminal, got {decision!r}")
    row: dict[str, Any] = {
        "schema_version": CANDIDATE_DECISION_SCHEMA_VERSION,
        "section_id": str(section_id or ""),
        "candidate_id": str(candidate_id or ""),
        "candidate_type": str(candidate_type or ""),
        "candidate_path_id": str(candidate_path_id or ""),
        "parent_id": str(parent_id or ""),
        "root_id": str(root_id or ""),
        "employer_lane": str(employer_lane or ""),
        "hop_depth": int(hop_depth),
        "decision": terminal,
        "reason_codes": _strings(reason_codes),
        "authority": dict(authority),
        "authority_pass": bool(authority.get("authority_pass")),
        "proof_strength_raw": round(float(proof_strength_raw or 0.0), 6),
        "target_alignment_score": round(float(target_alignment_score or 0.0), 6),
        "ranking_score": round(float(ranking_score or 0.0), 6),
        "path_signature": str(path_signature or ""),
    }
    if extra:
        row.update(dict(extra))
    return row


@dataclass(slots=True)
class TraversalRecorder:
    """Bounded event recorder for an actual C0.3 graph walk."""

    section_id: str
    max_hop_depth: int = 3
    max_events: int = 20000
    events: list[dict[str, Any]] = field(default_factory=list)

    def record(
        self,
        *,
        event_type: str,
        hop_depth: int,
        source_node_id: str = "",
        target_node_id: str = "",
        edge_type: str = "",
        candidate_path_id: str = "",
        authority_pass: bool | None = None,
        decision: str = "",
        reason_codes: Iterable[str] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        depth = int(hop_depth)
        if depth < 0 or depth > self.max_hop_depth:
            raise ValueError(f"traversal hop depth {depth} exceeds bound {self.max_hop_depth}")
        if len(self.events) >= self.max_events:
            raise ValueError(f"traversal event budget exceeded: {self.max_events}")
        event: dict[str, Any] = {
            "schema_version": TRAVERSAL_EVENT_SCHEMA_VERSION,
            "event_index": len(self.events),
            "section_id": self.section_id,
            "event_type": str(event_type or ""),
            "hop_depth": depth,
            "source_node_id": str(source_node_id or ""),
            "target_node_id": str(target_node_id or ""),
            "edge_type": str(edge_type or ""),
            "candidate_path_id": str(candidate_path_id or ""),
            "reason_codes": _strings(reason_codes),
        }
        if authority_pass is not None:
            event["authority_pass"] = bool(authority_pass)
        if decision:
            terminal = str(decision).lower()
            if terminal not in TERMINAL_DECISIONS:
                raise ValueError(f"non-terminal traversal decision: {decision!r}")
            event["decision"] = terminal
        if metadata:
            event["metadata"] = dict(metadata)
        self.events.append(event)
        return event

    def build_receipt(
        self,
        *,
        decisions: Sequence[Mapping[str, Any]],
        selected_root_ids: Iterable[str] = (),
        rejected_root_ids: Iterable[str] = (),
        target_role_profile: str = "",
    ) -> dict[str, Any]:
        rows = [dict(row) for row in decisions]
        candidate_paths = [str(row.get("candidate_path_id") or "") for row in rows]
        duplicate_paths = sorted(
            path for path, count in Counter(candidate_paths).items() if path and count > 1
        )
        terminal_count = sum(1 for row in rows if row.get("decision") in TERMINAL_DECISIONS)
        unexplained = len(rows) - terminal_count
        by_type = Counter(str(row.get("candidate_type") or "unknown") for row in rows)
        selected_by_type = Counter(
            str(row.get("candidate_type") or "unknown")
            for row in rows
            if row.get("decision") == "selected"
        )
        rejected_by_type = Counter(
            str(row.get("candidate_type") or "unknown")
            for row in rows
            if row.get("decision") == "rejected"
        )
        frontier_by_hop = Counter(int(row.get("hop_depth") or 0) for row in rows)
        visited_edges = sum(1 for event in self.events if event.get("event_type") == "edge_traversed")
        authority_events = sum(
            1 for event in self.events if event.get("event_type") == "authority_evaluated"
        )
        event_digest = stable_digest(self.events)
        pass_ = not duplicate_paths and unexplained == 0 and authority_events >= len(rows)
        return {
            "schema_version": TRAVERSAL_RECEIPT_SCHEMA_VERSION,
            "event_schema_version": TRAVERSAL_EVENT_SCHEMA_VERSION,
            "producer": "apps_rg.runtime.c0.c03_resume_graph_contracts.TraversalRecorder",
            "section_id": self.section_id,
            "target_role_profile": str(target_role_profile or ""),
            "traversal_mode": "bounded_event_log",
            "max_hop_depth": self.max_hop_depth,
            "max_events": self.max_events,
            "event_count": len(self.events),
            "events_digest": event_digest,
            "events": list(self.events),
            "visited_edges_count": visited_edges,
            "authority_event_count": authority_events,
            "frontier_size_by_hop_depth": {
                str(depth): count for depth, count in sorted(frontier_by_hop.items())
            },
            "candidate_conservation": {
                "candidate_count": len(rows),
                "terminal_decision_count": terminal_count,
                "unexplained_candidate_count": unexplained,
                "duplicate_candidate_path_ids": duplicate_paths,
                "count_by_candidate_type": dict(sorted(by_type.items())),
                "selected_by_candidate_type": dict(sorted(selected_by_type.items())),
                "rejected_by_candidate_type": dict(sorted(rejected_by_type.items())),
                # Compatibility fields consumed by existing shared-lane tests.
                "role_episode_roots_total": by_type.get("role_episode_root", 0),
                "role_episode_roots_selected": selected_by_type.get("role_episode_root", 0),
                "role_episode_roots_rejected": rejected_by_type.get("role_episode_root", 0),
                "role_episode_roots_unexplained": 0
                if pass_
                else max(
                    by_type.get("role_episode_root", 0)
                    - selected_by_type.get("role_episode_root", 0)
                    - rejected_by_type.get("role_episode_root", 0),
                    0,
                ),
                "pass": pass_,
            },
            "selected_root_ids": _strings(selected_root_ids),
            "rejected_root_ids": _strings(rejected_root_ids),
            "replayable": True,
            "pass": pass_,
        }


def build_candidate_receipt(
    *, section_id: str, decisions: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    rows = [dict(row) for row in decisions]
    selected = sum(1 for row in rows if row.get("decision") == "selected")
    rejected = sum(1 for row in rows if row.get("decision") == "rejected")
    duplicate_paths = sorted(
        path
        for path, count in Counter(
            str(row.get("candidate_path_id") or "") for row in rows
        ).items()
        if path and count > 1
    )
    terminal = selected + rejected
    return {
        "schema_version": "graph_candidate_receipt_v1",
        "section_id": str(section_id or ""),
        "candidate_decision_count": len(rows),
        "selected_candidate_count": selected,
        "rejected_candidate_count": rejected,
        "unexplained_candidate_count": len(rows) - terminal,
        "duplicate_candidate_path_ids": duplicate_paths,
        "candidate_conservation_pass": terminal == len(rows) and not duplicate_paths,
        "decision_ledger_digest": stable_digest(rows),
    }


def validate_canonical_section_plan(plan: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    if str(plan.get("schema_version") or "") != CANONICAL_PLAN_SCHEMA_VERSION:
        failures.append("canonical_plan_schema_version")
    if not str(plan.get("section_id") or ""):
        failures.append("section_id")
    authority_contract = plan.get("source_authority_contract")
    if not isinstance(authority_contract, Mapping):
        failures.append("source_authority_contract")
    elif authority_contract.get("targeting_inputs_are_non_authority") is not True:
        failures.append("targeting_inputs_are_non_authority")
    decisions = plan.get("graph_candidate_decision_ledger")
    if not isinstance(decisions, list) or not decisions:
        failures.append("graph_candidate_decision_ledger")
        decisions = []
    for index, row in enumerate(decisions):
        if not isinstance(row, Mapping):
            failures.append(f"decision_{index}_shape")
            continue
        if row.get("decision") not in TERMINAL_DECISIONS:
            failures.append(f"decision_{index}_nonterminal")
        if row.get("decision") == "selected" and row.get("authority_pass") is not True:
            failures.append(f"decision_{index}_selected_without_authority")
        auth = row.get("authority")
        if not isinstance(auth, Mapping) or auth.get("targeting_consulted") is not False:
            failures.append(f"decision_{index}_authority_targeting_boundary")
    traversal = plan.get("graph_traversal_receipt")
    if not isinstance(traversal, Mapping) or traversal.get("pass") is not True:
        failures.append("graph_traversal_receipt")
    candidate_receipt = plan.get("graph_candidate_receipt")
    if not isinstance(candidate_receipt, Mapping) or candidate_receipt.get(
        "candidate_conservation_pass"
    ) is not True:
        failures.append("graph_candidate_receipt")
    return failures


def finalize_canonical_section_plan(plan: Mapping[str, Any]) -> dict[str, Any]:
    """Stamp one immutable canonical plan digest across nested receipts."""
    out = deepcopy(dict(plan))
    out["schema_version"] = CANONICAL_PLAN_SCHEMA_VERSION
    out.pop("plan_id", None)
    out.pop("plan_digest", None)
    for row in out.get("graph_candidate_decision_ledger") or []:
        if isinstance(row, dict):
            row.pop("plan_id", None)
            row.pop("plan_digest", None)
    for key in ("graph_candidate_receipt", "graph_traversal_receipt"):
        receipt = out.get(key)
        if isinstance(receipt, dict):
            receipt.pop("plan_id", None)
            receipt.pop("plan_digest", None)
    digest = stable_digest(out)
    section_id = str(out.get("section_id") or "")
    out["plan_digest"] = digest
    out["plan_id"] = f"{section_id}:{digest[:16]}"
    for key in ("graph_candidate_decision_ledger",):
        rows = out.get(key)
        if isinstance(rows, list):
            for row in rows:
                if isinstance(row, dict):
                    row["plan_id"] = out["plan_id"]
                    row["plan_digest"] = digest
    for key in ("graph_candidate_receipt", "graph_traversal_receipt"):
        receipt = out.get(key)
        if isinstance(receipt, dict):
            receipt["plan_id"] = out["plan_id"]
            receipt["plan_digest"] = digest
    failures = validate_canonical_section_plan(out)
    if failures:
        raise ValueError(
            f"{section_id or 'unknown'} canonical C0.3 plan invalid: {', '.join(failures)}"
        )
    return out


__all__ = [
    "ACTIVE_STATUSES",
    "ALLOCATION_PLAN_SCHEMA_VERSION",
    "AUTHORITY_SCHEMA_VERSION",
    "BLOCKED_ACTIVATION_STATUSES",
    "BLOCKED_SUPPORT_LEVELS",
    "CANONICAL_AUTHORITY_SOURCE",
    "CANONICAL_PLAN_SCHEMA_VERSION",
    "CANDIDATE_DECISION_SCHEMA_VERSION",
    "GRAPH_CLAIM_BINDING_SCHEMA_VERSION",
    "GraphClaimBindingV1",
    "ResumeGraphAllocationPlanV1",
    "ResumeGraphSelectionPolicyV2",
    "ResumeGraphUsageLedgerV1",
    "SELECTION_POLICY_SCHEMA_VERSION",
    "TRAVERSAL_EVENT_SCHEMA_VERSION",
    "TRAVERSAL_RECEIPT_SCHEMA_VERSION",
    "USAGE_LEDGER_SCHEMA_VERSION",
    "WHOLE_RESUME_CONTRACT_SCHEMA_VERSION",
    "WholeResumeGraphEvidenceContractV1",
    "TraversalRecorder",
    "build_candidate_decision",
    "build_candidate_receipt",
    "evaluate_pretarget_authority",
    "finalize_canonical_section_plan",
    "stable_digest",
    "validate_canonical_section_plan",
]
