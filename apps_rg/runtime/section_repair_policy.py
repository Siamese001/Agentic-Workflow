"""Product repair policy — mechanical vs counted regen vs forbidden deterministic rewrite."""

from __future__ import annotations

from apps_rg.runtime.product_output_policy import product_fail_closed_runtime

# Bounded counted regen (replaces L2 + re-runs X2/X3) per section/operation.
REGEN_MAX_BY_OPERATION: dict[str, int] = {
    "synthesis_regen": 2,
    "judge_remediation_regen": 1,
    "headline_proof_shape_retry": 1,
    "headline_format_repair": 1,
    "parse_json_retry": 1,
    "companion_metric_budget_regen": 1,
    "companion_metric_budget_trim": 0,  # mechanical trim only; 0 = disallow LLM regen here
}


def deterministic_rewrite_allowed() -> bool:
    """Graph-only reformat, SRFS judge-safe, display authority graph fallback."""
    return not product_fail_closed_runtime()


def graph_only_reformat_allowed() -> bool:
    """Allow graph-only fact-tight rewrite only in explicit repair mode."""
    from apps_rg.runtime.sections.executive_summary_repair_policy import (
        RELEASE_GRAPH_ONLY_DETERMINISTIC_REFORMAT_ENABLED,
        graph_only_repair_mode_enabled,
    )

    return bool(
        RELEASE_GRAPH_ONLY_DETERMINISTIC_REFORMAT_ENABLED
        and graph_only_repair_mode_enabled()
    )


def synthesis_regen_allowed() -> bool:
    from apps_rg.runtime.sections.executive_summary_repair_policy import (
        synthesis_regeneration_enabled,
    )

    return synthesis_regeneration_enabled()


def judge_remediation_regen_allowed() -> bool:
    from apps_rg.runtime.sections.executive_summary_repair_policy import (
        judge_regeneration_enabled,
    )

    return judge_regeneration_enabled()


def regen_max_attempts(operation: str) -> int:
    return max(0, REGEN_MAX_BY_OPERATION.get(operation, 0))


def mechanical_parse_retry_allowed() -> bool:
    """JSON parse recovery only — same semantic authority, new parse."""
    return True


def exec_summary_display_graph_fallback_allowed() -> bool:
    return graph_only_reformat_allowed()


__all__ = [
    "REGEN_MAX_BY_OPERATION",
    "deterministic_rewrite_allowed",
    "graph_only_reformat_allowed",
    "synthesis_regen_allowed",
    "judge_remediation_regen_allowed",
    "regen_max_attempts",
    "mechanical_parse_retry_allowed",
    "exec_summary_display_graph_fallback_allowed",
]
