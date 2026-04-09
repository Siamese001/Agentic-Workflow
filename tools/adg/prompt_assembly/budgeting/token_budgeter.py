"""Token Budgeter — allocation, stratification, and overflow handling.

Token budgeting ensures every PromptEnvelope stays within its allocated
budget. The budgeter NEVER trims system_block, policy_block, task_block,
contradiction_flags, abstain_instructions, or output_schema. Only evidence
blocks are trimmed, and must-use is trimmed last (after optional).

Overflow strategies (applied in order):
    1. Summarize — condense low-priority items into summary counts
    2. Narrow   — restrict to top-N by severity or fan-in
    3. Split    — emit follow-on packet with remaining evidence
    4. Abstain  — emit abstain with scope refinement suggestion

Token estimation uses character-based heuristics from config/token_budget.yaml.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal

from tools.adg.prompt_assembly.packets.registry import TokenBudget


# ---------------------------------------------------------------------------
# Token estimation
# ---------------------------------------------------------------------------

# Default token rates (chars per token) — conservative estimates
_DEFAULT_RATES = {
    "json": 3.0,
    "text": 4.0,
    "code": 3.5,
}


def estimate_tokens(content: str, content_type: str = "json") -> int:
    """Estimate token count from string content.

    Args:
        content: String content to estimate.
        content_type: Content type for rate selection ("json", "text", "code").

    Returns:
        Estimated token count.
    """
    rate = _DEFAULT_RATES.get(content_type, 3.5)
    return max(1, int(len(content) / rate))


def estimate_dict_tokens(data: Any, content_type: str = "json") -> int:
    """Estimate token count from a dict/list by serializing to JSON."""
    serialized = json.dumps(data, indent=2, sort_keys=False)
    return estimate_tokens(serialized, content_type)


# ---------------------------------------------------------------------------
# Budget check result
# ---------------------------------------------------------------------------

OverflowAction = Literal["none", "summarized", "narrowed", "split", "abstained"]


@dataclass
class BudgetResult:
    """Result of applying token budget to evidence blocks."""

    must_use_evidence: list[dict[str, Any]]
    optional_evidence: list[dict[str, Any]]
    overflow_action: OverflowAction
    budget_status: Literal["within_budget", "trimmed", "split"]
    tokens_used: int
    tokens_available: int
    trimmed_count: int = 0
    summary_note: str = ""


# ---------------------------------------------------------------------------
# Stratification helpers
# ---------------------------------------------------------------------------


def _severity_key(item: dict[str, Any]) -> int:
    """Sort key: higher severity = lower number (sorted first)."""
    severity_map = {"critical": 0, "HIGH": 1, "high": 1, "MEDIUM": 2, "medium": 2, "LOW": 3, "low": 3}
    sev = item.get("severity")
    if sev is None:
        data = item.get("data")
        if isinstance(data, dict):
            sev = data.get("severity", "low")
        else:
            sev = "low"
    return severity_map.get(str(sev), 4)


def _fanin_key(item: dict[str, Any]) -> int:
    """Sort key: higher fan-in = lower number (sorted first)."""
    fan_in = item.get("fan_in")
    if fan_in is None:
        data = item.get("data")
        if isinstance(data, dict):
            fan_in = data.get("fan_in", 0)
        else:
            fan_in = 0
    return -int(fan_in) if isinstance(fan_in, (int, float)) else 0


def _stratify(items: list[dict[str, Any]], strategy: str = "severity") -> list[dict[str, Any]]:
    """Sort items by stratification strategy."""
    if strategy == "fan_in":
        return sorted(items, key=_fanin_key)
    return sorted(items, key=_severity_key)


# ---------------------------------------------------------------------------
# Summarize overflow
# ---------------------------------------------------------------------------


def _summarize_overflow(items: list[dict[str, Any]], keep_count: int) -> tuple[list[dict[str, Any]], str]:
    """Keep top items, summarize the rest into a note."""
    if len(items) <= keep_count:
        return items, ""
    kept = items[:keep_count]
    overflow_count = len(items) - keep_count
    summary_note = f"[{overflow_count} additional items summarized — showing top {keep_count} by priority]"
    return kept, summary_note


# ---------------------------------------------------------------------------
# Main budget application
# ---------------------------------------------------------------------------


def apply_budget(
    must_use_evidence: list[dict[str, Any]],
    optional_evidence: list[dict[str, Any]],
    fixed_tokens: int,
    budget: TokenBudget,
    stratification: str = "severity",
) -> BudgetResult:
    """Apply token budget to evidence blocks.

    Args:
        must_use_evidence: Canonical evidence items (trimmed last).
        optional_evidence: Derived/augmenting evidence (trimmed first).
        fixed_tokens: Tokens already consumed by system/policy/task/meta blocks.
        budget: Token budget allocation for this packet type.
        stratification: Stratification strategy ("severity" or "fan_in").

    Returns:
        BudgetResult with trimmed evidence and overflow metadata.
    """
    available_for_evidence = budget.total - fixed_tokens - budget.contradiction_meta
    if available_for_evidence <= 0:
        return BudgetResult(
            must_use_evidence=[],
            optional_evidence=[],
            overflow_action="abstained",
            budget_status="trimmed",
            tokens_used=fixed_tokens,
            tokens_available=budget.total,
            trimmed_count=len(must_use_evidence) + len(optional_evidence),
            summary_note="Token budget exhausted by fixed blocks — no room for evidence.",
        )

    # Stratify both lists
    must_sorted = _stratify(must_use_evidence, stratification)
    opt_sorted = _stratify(optional_evidence, stratification)

    # Estimate current token usage
    must_tokens = estimate_dict_tokens(must_sorted)
    opt_tokens = estimate_dict_tokens(opt_sorted)
    total_evidence_tokens = must_tokens + opt_tokens

    # Case 1: Within budget
    if total_evidence_tokens <= available_for_evidence:
        return BudgetResult(
            must_use_evidence=must_sorted,
            optional_evidence=opt_sorted,
            overflow_action="none",
            budget_status="within_budget",
            tokens_used=fixed_tokens + total_evidence_tokens,
            tokens_available=budget.total,
        )

    # Case 2: Trim optional first
    trimmed_count = 0
    overflow_action: OverflowAction = "none"
    summary_note = ""

    if must_tokens <= available_for_evidence:
        remaining = available_for_evidence - must_tokens
        if remaining > 0 and opt_sorted:
            # Narrow optional to fit
            kept_opt: list[dict[str, Any]] = []
            running = 0
            for item in opt_sorted:
                item_tokens = estimate_dict_tokens(item)
                if running + item_tokens <= remaining:
                    kept_opt.append(item)
                    running += item_tokens
                else:
                    trimmed_count += 1
            opt_sorted = kept_opt
            overflow_action = "narrowed" if trimmed_count > 0 else "none"
        else:
            trimmed_count = len(opt_sorted)
            opt_sorted = []
            overflow_action = "narrowed"

        return BudgetResult(
            must_use_evidence=must_sorted,
            optional_evidence=opt_sorted,
            overflow_action=overflow_action,
            budget_status="trimmed" if trimmed_count > 0 else "within_budget",
            tokens_used=fixed_tokens + must_tokens + estimate_dict_tokens(opt_sorted),
            tokens_available=budget.total,
            trimmed_count=trimmed_count,
        )

    # Case 3: Must-use evidence itself exceeds budget — summarize/narrow
    opt_sorted = []
    trimmed_count = len(optional_evidence)

    # Try narrowing must-use
    keep_count = max(1, len(must_sorted) // 2)
    while keep_count >= 1:
        candidate = must_sorted[:keep_count]
        candidate_tokens = estimate_dict_tokens(candidate)
        if candidate_tokens <= available_for_evidence:
            overflow_count = len(must_sorted) - keep_count
            summary_note = (
                f"[{overflow_count} must-use evidence items summarized — "
                f"showing top {keep_count} by {stratification}]"
            )
            return BudgetResult(
                must_use_evidence=candidate,
                optional_evidence=[],
                overflow_action="summarized",
                budget_status="trimmed",
                tokens_used=fixed_tokens + candidate_tokens,
                tokens_available=budget.total,
                trimmed_count=trimmed_count + overflow_count,
                summary_note=summary_note,
            )
        keep_count = keep_count // 2

    # Case 4: Even a single item doesn't fit — abstain
    return BudgetResult(
        must_use_evidence=[],
        optional_evidence=[],
        overflow_action="abstained",
        budget_status="trimmed",
        tokens_used=fixed_tokens,
        tokens_available=budget.total,
        trimmed_count=len(must_use_evidence) + len(optional_evidence),
        summary_note="Evidence too large for budget — abstaining. Suggest narrower scope.",
    )
