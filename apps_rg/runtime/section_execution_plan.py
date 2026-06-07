"""Canonical apps_rg section execution contract.

The plan is intentionally declarative: it names the generated content lanes,
their dependency order, SC/attempt caps, and failure classes that retries cannot
repair. Generation and validation remain in lane modules.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class SectionExecutionPolicy:
    section_id: str
    execution_order: int
    dependency_level: str
    reasoning_intensity: str
    sc_paths: int
    attempts: int
    mode: str
    dependencies: tuple[str, ...] = ()
    composite_judge_default: bool = False
    optional_adjudicator: bool = False


MAX_SECTION_ATTEMPTS: Final[int] = 2
DEFAULT_ACTIVE_SC_PATHS: Final[int] = 4

HARD_NO_RETRY_RUNTIME_STATUSES: Final[frozenset[str]] = frozenset(
    {
        "BLOCKED_UPSTREAM_NOT_FINALIZED",
        "UPSTREAM_EVIDENCE_MISSING",
        "FEC_NOT_FINALIZED",
        "REQUIRED_PROOF_ABSENT",
        "REQUIRED_DEPENDENCY_EMPTY",
    }
)

BULLET_LANES: Final[tuple[str, ...]] = (
    "unify_bullets",
    "ibm_bullets",
)

NARRATIVE_LANES: Final[tuple[str, ...]] = (
    "unify_narrative",
    "ibm_narrative",
)

NARRATIVE_UPSTREAM_BULLET_LANE: Final[dict[str, str]] = {
    "unify_narrative": "unify_bullets",
    "ibm_narrative": "ibm_bullets",
}

SECTION_EXECUTION_POLICIES: Final[dict[str, SectionExecutionPolicy]] = {
    "competencies": SectionExecutionPolicy(
        section_id="competencies",
        execution_order=10,
        dependency_level="upstream_proof",
        reasoning_intensity="low",
        sc_paths=DEFAULT_ACTIVE_SC_PATHS,
        attempts=MAX_SECTION_ATTEMPTS,
        mode="deterministic_selection_grouping",
    ),
    "unify_bullets": SectionExecutionPolicy(
        section_id="unify_bullets",
        execution_order=20,
        dependency_level="upstream_proof",
        reasoning_intensity="medium_high",
        sc_paths=DEFAULT_ACTIVE_SC_PATHS,
        attempts=MAX_SECTION_ATTEMPTS,
        mode="angle_diverse_bullet_generation",
        composite_judge_default=True,
        optional_adjudicator=True,
    ),
    "ibm_bullets": SectionExecutionPolicy(
        section_id="ibm_bullets",
        execution_order=30,
        dependency_level="upstream_proof",
        reasoning_intensity="medium",
        sc_paths=DEFAULT_ACTIVE_SC_PATHS,
        attempts=MAX_SECTION_ATTEMPTS,
        mode="metric_locked_bullet_generation",
        composite_judge_default=True,
        optional_adjudicator=True,
    ),
    "unify_narrative": SectionExecutionPolicy(
        section_id="unify_narrative",
        execution_order=40,
        dependency_level="consumes_unify_bullets",
        reasoning_intensity="medium",
        sc_paths=DEFAULT_ACTIVE_SC_PATHS,
        attempts=MAX_SECTION_ATTEMPTS,
        mode="upstream_bullet_narrative",
        dependencies=("unify_bullets",),
    ),
    "ibm_narrative": SectionExecutionPolicy(
        section_id="ibm_narrative",
        execution_order=50,
        dependency_level="consumes_ibm_bullets",
        reasoning_intensity="medium",
        sc_paths=DEFAULT_ACTIVE_SC_PATHS,
        attempts=MAX_SECTION_ATTEMPTS,
        mode="upstream_bullet_narrative",
        dependencies=("ibm_bullets",),
    ),
    "executive_summary": SectionExecutionPolicy(
        section_id="executive_summary",
        execution_order=60,
        dependency_level="downstream_synthesis",
        reasoning_intensity="high",
        sc_paths=5,
        attempts=MAX_SECTION_ATTEMPTS,
        mode="downstream_synthesis",
        dependencies=(
            "competencies",
            "unify_bullets",
            "ibm_bullets",
            "unify_narrative",
            "ibm_narrative",
        ),
    ),
    "headline": SectionExecutionPolicy(
        section_id="headline",
        execution_order=70,
        dependency_level="final_positioning",
        reasoning_intensity="standard",
        sc_paths=1,
        attempts=MAX_SECTION_ATTEMPTS,
        mode="final_positioning",
        dependencies=("executive_summary",),
    ),
}

GENERATED_CONTENT_LANES: Final[tuple[str, ...]] = tuple(
    sid
    for sid, _policy in sorted(
        SECTION_EXECUTION_POLICIES.items(),
        key=lambda item: item[1].execution_order,
    )
)


def section_policy(section_id: str) -> SectionExecutionPolicy:
    sid = str(section_id or "").strip().lower().replace("-", "_")
    try:
        return SECTION_EXECUTION_POLICIES[sid]
    except KeyError as exc:
        raise KeyError(f"Unknown apps_rg content section: {section_id!r}") from exc


def dependencies_for_section(section_id: str) -> tuple[str, ...]:
    return section_policy(section_id).dependencies


def is_generated_content_lane(section_id: str) -> bool:
    return str(section_id or "").strip().lower().replace("-", "_") in SECTION_EXECUTION_POLICIES


def is_hard_no_retry_runtime_status(runtime_generation_status: str | None) -> bool:
    """True when retrying the same section cannot create missing upstream proof."""
    return str(runtime_generation_status or "").strip().upper() in HARD_NO_RETRY_RUNTIME_STATUSES


__all__ = [
    "BULLET_LANES",
    "DEFAULT_ACTIVE_SC_PATHS",
    "GENERATED_CONTENT_LANES",
    "HARD_NO_RETRY_RUNTIME_STATUSES",
    "MAX_SECTION_ATTEMPTS",
    "NARRATIVE_LANES",
    "NARRATIVE_UPSTREAM_BULLET_LANE",
    "SECTION_EXECUTION_POLICIES",
    "SectionExecutionPolicy",
    "dependencies_for_section",
    "is_generated_content_lane",
    "is_hard_no_retry_runtime_status",
    "section_policy",
]
