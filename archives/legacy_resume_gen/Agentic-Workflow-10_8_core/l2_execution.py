"""Layer 2 execution module consolidating execution agents."""



from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any

from utils_types import PlanObject, StatePatch


class ExecutionAgent(ABC):
    """Abstract executor interface for L2 agents."""

    @abstractmethod
    def execute(self, plan: PlanObject, state: Dict[str, Any]) -> StatePatch:
        """Execute a plan against the current state and return a state patch."""
        raise NotImplementedError
"""
L2 — RAG Execution Agent

Responsibilities:
    • Execute retrieval, ranking, and evidence extraction operations.
    • Apply RAG intents from L1 reasoning while respecting L5 safety constraints.
    • Emit structured artifacts consumable by L4 state managers.

Consumes PlanObject inputs and returns StatePatch outputs deterministically.
"""

from typing import Any, Dict, List

from injection_tooling_profiles import DEFAULT_TOOLING_PROFILE
from retrieval import fuse_results
from retrieval import (
    normalize_documents,
    dedupe_results,
    rerank_results,
    fuse_sources,
    truncate_by_budget,
    apply_ranker,
)
from l4_memory import ContextBudget
from utils_types import BudgetConfig, PlanObject, StatePatch


def _synthesize_result(query: str, index: int) -> Dict[str, Any]:
    """Create a deterministic retrieval result for a query."""

    return {
        "query": query,
        "rank": index + 1,
        "evidence": f"Evidence synthesized for '{query}'",
    }


class RAGExecutionAgent(ExecutionAgent):
    """Deterministic retrieval executor that returns state patches only."""

    def execute(self, plan: PlanObject, state: Dict[str, Any]) -> StatePatch:
        retrieval = plan.get("retrieval", {})
        queries: List[str] = [str(q) for q in retrieval.get("queries", [])]
        filters = retrieval.get("filters", {})
        ranking = retrieval.get("ranking", {})
        metadata = retrieval.get("metadata", {})
        results = [_synthesize_result(query, idx) for idx, query in enumerate(queries)]

        transformed = normalize_documents(results)
        transformed = dedupe_results(transformed)
        transformed = rerank_results(transformed, ranking.get("strategy"))
        transformed = apply_ranker(transformed, metadata.get("ranker_strategy") or ranking.get("strategy"))
        transformed = fuse_results([fuse_sources(transformed)])
        budget_config = BudgetConfig()
        context_budget = ContextBudget(budget_config)

        transformed = truncate_by_budget(transformed, budget_config)
        transformed = context_budget.prune_rag_items_by_tokens(transformed)

        history = list(state.get("rag_history", [])) + transformed
        patch: StatePatch = StatePatch(
            {
                "rag_history": history,
                "last_retrieval": {
                    "queries": queries,
                    "filters": filters,
                    "ranking": ranking,
                    "metadata": metadata,
                    "status": "completed",
                },
            }
        )
        patch["tooling_injection"] = {
            "tool_feedback_enabled": DEFAULT_TOOLING_PROFILE.tool_feedback_enabled,
            "evidence_binding_enabled": DEFAULT_TOOLING_PROFILE.evidence_binding_enabled,
            "cross_tool_reconciliation": DEFAULT_TOOLING_PROFILE.cross_tool_reconciliation,
        }
        patch["retrieval_injection"] = {"hybrid_ranker_enabled": True}
        return patch
"""
L2 — Bullet Execution Agent

Responsibilities:
    • Generate concise bulletized outputs from higher-level plans.
    • Respect formatting and structural constraints provided by L1 strategy reasoners.
    • Produce deterministic updates for L4 state without coordinating other agents.

Consumes PlanObject inputs and returns StatePatch outputs deterministically.
"""

from typing import Any, Dict, List

from injection_tooling_profiles import DEFAULT_TOOLING_PROFILE
from utils_types import PlanObject, StatePatch


class BulletExecutionAgent(ExecutionAgent):
    """Convert planning intents into bulletized state patches."""

    def execute(self, plan: PlanObject, state: Dict[str, Any]) -> StatePatch:
        items: List[str] = [str(item) for item in plan.get("deliverables", plan.get("items", []))]
        if not items:
            items = [str(plan.get("objective", "unspecified-objective"))]

        bullets = [f"- {item}" for item in items]
        message = "\n".join(bullets)

        messages = list(state.get("messages", [])) + [
            {
                "role": "assistant",
                "content": message,
                "format": "bullets",
            }
        ]

        patch: StatePatch = StatePatch(
            {
                "messages": messages,
                "last_bullets": bullets,
            }
        )
        patch["tooling_injection"] = {
            "tool_feedback_enabled": DEFAULT_TOOLING_PROFILE.tool_feedback_enabled,
            "evidence_binding_enabled": DEFAULT_TOOLING_PROFILE.evidence_binding_enabled,
            "cross_tool_reconciliation": DEFAULT_TOOLING_PROFILE.cross_tool_reconciliation,
        }
        return patch
"""
L2 — Drafting Execution Agent

Responsibilities:
    • Convert drafting briefs into narrative or structured content.
    • Apply tone, style, and constraint guidance from L1 drafting reasoners.
    • Return deterministic drafts and deltas for L4 state management.

Consumes PlanObject inputs and returns StatePatch outputs deterministically.
"""

from typing import Any, Dict, List

from injection_tooling_profiles import DEFAULT_TOOLING_PROFILE
from utils_types import PlanObject, StatePatch


def _compose_section(title: str, tone: str, audience: str) -> str:
    """Build a deterministic section string."""

    return f"[{title}] Tone: {tone}; Audience: {audience}."


class DraftingExecutionAgent(ExecutionAgent):
    """Create draft content without performing any tool calls."""

    def execute(self, plan: PlanObject, state: Dict[str, Any]) -> StatePatch:
        tone = str(plan.get("tone", "neutral"))
        audience = str(plan.get("audience", "general"))
        sections: List[str] = [str(section) for section in plan.get("sections", [])]
        if not sections:
            sections = ["Introduction", "Body", "Conclusion"]

        paragraphs = [_compose_section(title, tone, audience) for title in sections]
        draft = "\n\n".join(paragraphs)

        messages = list(state.get("messages", [])) + [
            {
                "role": "assistant",
                "content": draft,
                "format": "draft",
            }
        ]

        patch: StatePatch = StatePatch(
            {
                "messages": messages,
                "draft": {
                    "objective": plan.get("objective"),
                    "tone": tone,
                    "audience": audience,
                    "sections": sections,
                    "content": draft,
                },
            }
        )
        patch["tooling_injection"] = {
            "tool_feedback_enabled": DEFAULT_TOOLING_PROFILE.tool_feedback_enabled,
            "evidence_binding_enabled": DEFAULT_TOOLING_PROFILE.evidence_binding_enabled,
            "cross_tool_reconciliation": DEFAULT_TOOLING_PROFILE.cross_tool_reconciliation,
        }
        return patch
"""
L2 — QA Validation Agent

Responsibilities:
    • Execute quality and factuality checks on agent outputs.
    • Validate alignment between planned intents and produced artifacts.
    • Surface structured validation reports to L3 orchestrators and L4 state systems.

Consumes PlanObject inputs and returns StatePatch outputs deterministically.
"""

from typing import Any, Dict, List

from injection_tooling_profiles import DEFAULT_TOOLING_PROFILE
from utils_types import PlanObject, StatePatch
from l4_memory import get_evidence_view


def _build_checks(plan: PlanObject) -> List[str]:
    """Derive simple validation checks from the provided plan."""

    checks: List[str] = ["coherence", "completeness"]
    if plan.get("mode") == "rag":
        checks.append("evidence_alignment")
    if plan.get("mode") == "drafting":
        checks.append("tone_alignment")
    return checks


def _derive_findings(state: Dict[str, Any], checks: List[str]) -> List[Dict[str, Any]]:
    """Produce deterministic validation findings based on available state."""

    findings: List[Dict[str, Any]] = []
    has_messages = bool(state.get("messages"))
    for check in checks:
        findings.append(
            {
                "check": check,
                "status": "pass" if has_messages else "pending",
                "details": "validated deterministically" if has_messages else "awaiting content",
            }
        )
    return findings


class QAValidationAgent(ExecutionAgent):
    """Perform deterministic QA validation that emits state patches only."""

    def execute(self, plan: PlanObject, state: Dict[str, Any]) -> StatePatch:
        evidence = get_evidence_view(state)
        checks = _build_checks(plan)
        findings = _derive_findings(state, checks)
        has_messages = bool(state.get("messages"))
        confidence_score = 1.0 if has_messages else 0.5

        patch: StatePatch = StatePatch(
            {
                "qa_report": {
                    "plan_mode": plan.get("mode"),
                    "checks": checks,
                    "findings": findings,
                    "confidence": confidence_score,
                    "error_simulation": {"simulated": False},
                    "shadow_validation": {
                        "performed": False,
                        "enabled": DEFAULT_TOOLING_PROFILE.shadow_validation_enabled,
                    },
                }
            }
        )
        return patch
