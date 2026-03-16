"""Phase 6: RAG / Embedding Sovereignty C0 enforcement.

Policy: ADG::Policy::RAG_C0_INFORMATIONAL_ONLY

Decision point nodes:
  ADG::Decision::RoutingDecision
  ADG::Decision::SafetyThreshold
  ADG::Decision::TierSelection

Retrieval output node:
  ADG::Retrieval::C0Context

Enforcement:
  - C0Context may be consumed by PromptAssembly only
  - No influences relation from retrieval or C0Context to any decision node
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agentic_core.adg.client.mcp_client import ADGMCPClient
from agentic_core.adg.schema import canonical_name
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "rag_sovereignty")
_emit_applies_guardrail("p0", "rag_sovereignty", "p0_governance")
_emit_snapshots_state("p0", "rag_sovereignty", "state_snapshot")
emit_replay_key("p0", "rag_sovereignty")
emit_determinism_digest("p0", "rag_sovereignty")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult
logger = logging.getLogger(__name__)
_POLICY_ID = "ADG::Policy::RAG_C0_INFORMATIONAL_ONLY"
_DECISION_NODES: frozenset[str] = frozenset(
    {
        canonical_name("Decision", "RoutingDecision"),
        canonical_name("Decision", "SafetyThreshold"),
        canonical_name("Decision", "TierSelection"),
    }
)
_C0_CONTEXT_NODE = canonical_name("Retrieval", "C0Context")
_RAG_MODULE_PATTERNS: frozenset[str] = frozenset(
    {
        "SovereignRAGManager",
        "SovereignRAGManagerAgent",
        "knowledge/reasoning",
        "EmbeddingSovereignAgent",
        "bmg_embedding_similarity",
        "healing_contexts",
        "retrieval",
    }
)
_DECISION_MODULE_PATTERNS: frozenset[str] = frozenset(
    {
        "shadow_router_classifier",
        "path_router",
        "reasoning_policy_engine",
        "escalation_router",
        "timeshift_router",
        "assembly_stage",
    }
)


def _module_rel(adg_name: str) -> str:
    prefix = "ADG::Module::"
    return adg_name[len(prefix) :] if adg_name.startswith(prefix) else adg_name


def _is_rag_module(rel: str) -> bool:
    return any(pat in rel for pat in _RAG_MODULE_PATTERNS)


def _is_decision_module(rel: str) -> bool:
    return any(pat in rel for pat in _DECISION_MODULE_PATTERNS)


@dataclass
class RAGSovereigntyViolation:
    """A RAG C0 sovereignty violation."""

    violation_type: str
    from_module: str
    to_module: str
    source_file: str
    line_no: int
    policy_id: str = _POLICY_ID

    def format(self) -> str:
        return f"RAG-C0-VIOLATION [{self.violation_type}] policy={self.policy_id}\n  from:  {self.from_module}\n  to:    {self.to_module}\n  file:  {self.source_file}:{self.line_no}"


@dataclass
class RAGSovereigntyReport:
    """Result of RAG sovereignty enforcement check."""

    violations: list[RAGSovereigntyViolation] = field(default_factory=list)
    rag_edges_count: int = 0
    decision_edges_count: int = 0
    snapshot_digest: str = ""

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0


def check_rag_sovereignty(
    result: ScanResult, client: ADGMCPClient | None = None, extra_edges: list[dict] | None = None
) -> RAGSovereigntyReport:
    """Enforce RAG C0 informational-only policy.

    extra_edges: optional synthetic edges for negative-control tests.
      Format: [{"from": adg_name, "relation": "influences", "to": adg_name}]
    """
    rag_edges = []
    decision_edges = []
    for edge in result.edges:
        from_rel = _module_rel(edge.from_name)
        to_rel = _module_rel(edge.to_name)
        if _is_rag_module(from_rel):
            rag_edges.append(edge)
        if _is_rag_module(from_rel) and _is_decision_module(to_rel):
            decision_edges.append(edge)
    violations: list[RAGSovereigntyViolation] = []
    for edge in decision_edges:
        violations.append(
            RAGSovereigntyViolation(
                violation_type="RAG_INFLUENCES_DECISION",
                from_module=_module_rel(edge.from_name),
                to_module=_module_rel(edge.to_name),
                source_file=edge.source_file,
                line_no=edge.line_no,
            )
        )
    if extra_edges:
        for ee in extra_edges:
            from_adg = ee.get("from", "")
            relation = ee.get("relation", "")
            to_adg = ee.get("to", "")
            if relation == "influences" and to_adg in _DECISION_NODES:
                violations.append(
                    RAGSovereigntyViolation(
                        violation_type="C0_CONTEXT_INFLUENCES_DECISION",
                        from_module=from_adg,
                        to_module=_module_rel(to_adg),
                        source_file="<synthetic>",
                        line_no=0,
                    )
                )
    proof_digest = _compute_proof_digest(result, violations)
    report = RAGSovereigntyReport(
        violations=violations,
        rag_edges_count=len(rag_edges),
        decision_edges_count=len(decision_edges),
        snapshot_digest=proof_digest,
    )
    if client is not None:
        _persist_proof(result, report, client)
        _ensure_graph_nodes(client)
    return report


def _compute_proof_digest(result: ScanResult, violations: list[RAGSovereigntyViolation]) -> str:
    lines = [result.digest]
    for v in sorted(violations, key=lambda x: (x.from_module, x.to_module, x.line_no)):
        lines.append(f"{v.from_module}|{v.to_module}|{v.violation_type}|{v.line_no}")
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def _persist_proof(result: ScanResult, report: RAGSovereigntyReport, client: ADGMCPClient) -> None:
    if not result.commit_sha:
        return
    proof_node = canonical_name("Snapshot", result.commit_sha, "rag_sovereignty_proof")
    client.upsert_entity(
        proof_node,
        "snapshot",
        [
            f"commit:{result.commit_sha}",
            f"snapshot_digest:{report.snapshot_digest}",
            f"rag_edges:{report.rag_edges_count}",
            f"decision_edges:{report.decision_edges_count}",
            f"violation_count:{len(report.violations)}",
            f"policy_id:{_POLICY_ID}",
        ],
    )


def _ensure_graph_nodes(client: ADGMCPClient) -> None:
    client.upsert_entity(
        _C0_CONTEXT_NODE, "retrieval_component", ["component:C0Context", f"policy_id:{_POLICY_ID}"]
    )
    for dn in sorted(_DECISION_NODES):
        client.upsert_entity(dn, "decision_point", [f"policy_id:{_POLICY_ID}"])


__all__ = ["check_rag_sovereignty", "RAGSovereigntyReport", "RAGSovereigntyViolation"]
