"""Semantic Memory Types — ADG-backed embedding use-case types.

Frozen, deterministic dataclasses for the six embedding use-cases:
  1. IncidentBundle      — composite trace+violation+route+heal+policy object
  2. MutationDiffRecord  — RFC 6902 diff, state_diff, rollback context
  3. HealerOutcomeRecord — change packages V1→V2→V3, fix rationale, outcome
  4. PathDPreferencePair — DPO-style human patch + approve/reject reason
  5. GraphNeighborhood   — local ADG subgraph node with structural context
  6. PolicyGuardrailCase — blocked payload + remediation + drift annotation

All types are influence_class='C0_INFORMATIONAL'.
All hashing uses SHA-256 over canonical JSON (sort_keys, no whitespace).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Literal


def _sha256_json(obj: dict) -> str:
    canonical = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# 1. Incident Bundle
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IncidentBundle:
    """Composite incident object for case-based reasoning retrieval.

    Embeds together: trace summary, violations, route path, tool/capability,
    state_diff summary, healer used, outcome, and policy hash so that
    nearest-neighbour search operates over the full execution context.

    influence_class is always C0_INFORMATIONAL.
    """

    trace_id: str
    trace_summary: str
    violations: tuple[str, ...]
    route_path: str
    tool_capability: str
    state_diff_summary: str
    healer_id: str
    outcome: Literal["success", "failure", "partial"]
    policy_hash: str
    timestamp_utc: int
    bundle_hash: str = field(default="", init=False)
    influence_class: Literal["C0_INFORMATIONAL"] = field(default="C0_INFORMATIONAL", init=False)

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("trace_id must not be empty")
        if self.outcome not in ("success", "failure", "partial"):
            raise ValueError(f"outcome must be success/failure/partial, got {self.outcome!r}")
        h = _sha256_json(self._canonical_dict())
        object.__setattr__(self, "bundle_hash", h)

    def _canonical_dict(self) -> dict:
        return {
            "healer_id": self.healer_id,
            "outcome": self.outcome,
            "policy_hash": self.policy_hash,
            "route_path": self.route_path,
            "state_diff_summary": self.state_diff_summary,
            "timestamp_utc": self.timestamp_utc,
            "tool_capability": self.tool_capability,
            "trace_id": self.trace_id,
            "trace_summary": self.trace_summary,
            "violations": sorted(self.violations),
        }

    def to_embedding_text(self) -> str:
        """Canonical flat text for embedding — deterministic field order."""
        parts = [
            f"trace:{self.trace_summary}",
            f"violations:{' | '.join(sorted(self.violations))}",
            f"route:{self.route_path}",
            f"tool:{self.tool_capability}",
            f"diff:{self.state_diff_summary}",
            f"healer:{self.healer_id}",
            f"outcome:{self.outcome}",
            f"policy:{self.policy_hash}",
        ]
        return " ## ".join(parts)


# ---------------------------------------------------------------------------
# 2. Mutation Diff Record
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MutationDiffRecord:
    """RFC 6902-style diff packaged with rollback context for retrieval.

    Enables pre-commit nearest-neighbour checks, post-commit healing retrieval,
    and rollback refinement from similar failed mutations.
    """

    mutation_id: str
    target_resource: str
    operations: tuple[str, ...]
    state_diff_summary: str
    rollback_context: str
    commit_outcome: Literal["committed", "rolled_back", "pending"]
    trace_id: str
    policy_hash: str
    timestamp_utc: int
    diff_hash: str = field(default="", init=False)
    influence_class: Literal["C0_INFORMATIONAL"] = field(default="C0_INFORMATIONAL", init=False)

    def __post_init__(self) -> None:
        if not self.mutation_id:
            raise ValueError("mutation_id must not be empty")
        if self.commit_outcome not in ("committed", "rolled_back", "pending"):
            raise ValueError(
                f"commit_outcome must be committed/rolled_back/pending, got {self.commit_outcome!r}"
            )
        h = _sha256_json(self._canonical_dict())
        object.__setattr__(self, "diff_hash", h)

    def _canonical_dict(self) -> dict:
        return {
            "commit_outcome": self.commit_outcome,
            "mutation_id": self.mutation_id,
            "operations": sorted(self.operations),
            "policy_hash": self.policy_hash,
            "rollback_context": self.rollback_context,
            "state_diff_summary": self.state_diff_summary,
            "target_resource": self.target_resource,
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
        }

    def to_embedding_text(self) -> str:
        """Canonical flat text for embedding."""
        parts = [
            f"mutation:{self.mutation_id}",
            f"resource:{self.target_resource}",
            f"ops:{' | '.join(sorted(self.operations))}",
            f"diff:{self.state_diff_summary}",
            f"rollback:{self.rollback_context}",
            f"outcome:{self.commit_outcome}",
            f"policy:{self.policy_hash}",
        ]
        return " ## ".join(parts)


# ---------------------------------------------------------------------------
# 3. Healer Outcome Record
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HealerOutcomeRecord:
    """Healer playbook record: change packages V1→V2→V3, rationale, outcome.

    High-quality training memory because the healer-validator architecture
    enforces lineage and replay validation on these cases.
    """

    healer_id: str
    failure_type: str
    violation_text: str
    fix_rationale: str
    change_summary: str
    package_version: str
    outcome: Literal["success", "failure", "partial"]
    tier: str
    trace_id: str
    timestamp_utc: int
    outcome_hash: str = field(default="", init=False)
    influence_class: Literal["C0_INFORMATIONAL"] = field(default="C0_INFORMATIONAL", init=False)

    def __post_init__(self) -> None:
        if not self.healer_id:
            raise ValueError("healer_id must not be empty")
        if not self.failure_type:
            raise ValueError("failure_type must not be empty")
        if self.outcome not in ("success", "failure", "partial"):
            raise ValueError(f"outcome must be success/failure/partial, got {self.outcome!r}")
        h = _sha256_json(self._canonical_dict())
        object.__setattr__(self, "outcome_hash", h)

    def _canonical_dict(self) -> dict:
        return {
            "change_summary": self.change_summary,
            "failure_type": self.failure_type,
            "fix_rationale": self.fix_rationale,
            "healer_id": self.healer_id,
            "outcome": self.outcome,
            "package_version": self.package_version,
            "tier": self.tier,
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
            "violation_text": self.violation_text,
        }

    def to_embedding_text(self) -> str:
        """Canonical flat text for embedding."""
        parts = [
            f"healer:{self.healer_id}",
            f"failure:{self.failure_type}",
            f"violation:{self.violation_text}",
            f"rationale:{self.fix_rationale}",
            f"change:{self.change_summary}",
            f"pkg:{self.package_version}",
            f"tier:{self.tier}",
            f"outcome:{self.outcome}",
        ]
        return " ## ".join(parts)


# ---------------------------------------------------------------------------
# 4. Path D Preference Pair
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PathDPreferencePair:
    """DPO-style human preference pair from Path D HITL decisions.

    Embeds original plan, human patch, approve/reject reason, and resulting
    outcome to enable retrieval of human preference precedents.
    """

    decision_id: str
    original_plan: str
    human_patch: str
    decision: Literal["approved", "rejected", "modified"]
    reason: str
    resulting_outcome: str
    agent: str
    trace_id: str
    timestamp_utc: int
    pair_hash: str = field(default="", init=False)
    influence_class: Literal["C0_INFORMATIONAL"] = field(default="C0_INFORMATIONAL", init=False)

    def __post_init__(self) -> None:
        if not self.decision_id:
            raise ValueError("decision_id must not be empty")
        if self.decision not in ("approved", "rejected", "modified"):
            raise ValueError(f"decision must be approved/rejected/modified, got {self.decision!r}")
        h = _sha256_json(self._canonical_dict())
        object.__setattr__(self, "pair_hash", h)

    def _canonical_dict(self) -> dict:
        return {
            "agent": self.agent,
            "decision": self.decision,
            "decision_id": self.decision_id,
            "human_patch": self.human_patch,
            "original_plan": self.original_plan,
            "reason": self.reason,
            "resulting_outcome": self.resulting_outcome,
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
        }

    def to_embedding_text(self) -> str:
        """Canonical flat text for embedding."""
        parts = [
            f"plan:{self.original_plan}",
            f"patch:{self.human_patch}",
            f"decision:{self.decision}",
            f"reason:{self.reason}",
            f"outcome:{self.resulting_outcome}",
            f"agent:{self.agent}",
        ]
        return " ## ".join(parts)


# ---------------------------------------------------------------------------
# 5. Graph Neighborhood
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GraphNeighborhood:
    """Local ADG subgraph around a node for architectural motif search.

    Encodes: node identity, layer, inbound/outbound relation types,
    governance edges, mutation/determinism edges, and ownership territory.
    Enables semantic search over architectural patterns.
    """

    node_id: str
    node_type: str
    layer: str
    inbound_relations: tuple[str, ...]
    outbound_relations: tuple[str, ...]
    governance_edges: tuple[str, ...]
    mutation_edges: tuple[str, ...]
    ownership_territory: str
    risk_label: str
    neighborhood_hash: str = field(default="", init=False)
    influence_class: Literal["C0_INFORMATIONAL"] = field(default="C0_INFORMATIONAL", init=False)

    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("node_id must not be empty")
        if not self.layer:
            raise ValueError("layer must not be empty")
        h = _sha256_json(self._canonical_dict())
        object.__setattr__(self, "neighborhood_hash", h)

    def _canonical_dict(self) -> dict:
        return {
            "governance_edges": sorted(self.governance_edges),
            "inbound_relations": sorted(self.inbound_relations),
            "layer": self.layer,
            "mutation_edges": sorted(self.mutation_edges),
            "node_id": self.node_id,
            "node_type": self.node_type,
            "outbound_relations": sorted(self.outbound_relations),
            "ownership_territory": self.ownership_territory,
            "risk_label": self.risk_label,
        }

    def to_embedding_text(self) -> str:
        """Canonical flat text for embedding."""
        parts = [
            f"node:{self.node_id}",
            f"type:{self.node_type}",
            f"layer:{self.layer}",
            f"in:{' | '.join(sorted(self.inbound_relations))}",
            f"out:{' | '.join(sorted(self.outbound_relations))}",
            f"gov:{' | '.join(sorted(self.governance_edges))}",
            f"mut:{' | '.join(sorted(self.mutation_edges))}",
            f"territory:{self.ownership_territory}",
            f"risk:{self.risk_label}",
        ]
        return " ## ".join(parts)


# ---------------------------------------------------------------------------
# 6. Policy Guardrail Case
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PolicyGuardrailCase:
    """Blocked payload case for guardrail drift retrieval.

    Captures blocked payloads, remediation text, false-positive/negative
    annotations, and policy hash to enable calibration of strictness via
    semantic retrieval of similar past blocks.
    """

    case_id: str
    blocked_payload_summary: str
    remediation_text: str
    policy_hash: str
    policy_root: str
    verdict: Literal["true_positive", "false_positive", "false_negative"]
    strictness_level: str
    trace_id: str
    timestamp_utc: int
    case_hash: str = field(default="", init=False)
    influence_class: Literal["C0_INFORMATIONAL"] = field(default="C0_INFORMATIONAL", init=False)

    def __post_init__(self) -> None:
        if not self.case_id:
            raise ValueError("case_id must not be empty")
        if self.verdict not in ("true_positive", "false_positive", "false_negative"):
            raise ValueError(
                f"verdict must be true_positive/false_positive/false_negative, got {self.verdict!r}"
            )
        h = _sha256_json(self._canonical_dict())
        object.__setattr__(self, "case_hash", h)

    def _canonical_dict(self) -> dict:
        return {
            "blocked_payload_summary": self.blocked_payload_summary,
            "case_id": self.case_id,
            "policy_hash": self.policy_hash,
            "policy_root": self.policy_root,
            "remediation_text": self.remediation_text,
            "strictness_level": self.strictness_level,
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
            "verdict": self.verdict,
        }

    def to_embedding_text(self) -> str:
        """Canonical flat text for embedding."""
        parts = [
            f"payload:{self.blocked_payload_summary}",
            f"remediation:{self.remediation_text}",
            f"policy:{self.policy_hash}",
            f"root:{self.policy_root}",
            f"verdict:{self.verdict}",
            f"strictness:{self.strictness_level}",
        ]
        return " ## ".join(parts)


__all__ = [
    "IncidentBundle",
    "MutationDiffRecord",
    "HealerOutcomeRecord",
    "PathDPreferencePair",
    "GraphNeighborhood",
    "PolicyGuardrailCase",
]
