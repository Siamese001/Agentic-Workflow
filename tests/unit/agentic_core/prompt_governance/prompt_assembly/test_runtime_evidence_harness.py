"""Pytest wrapper around the Prompt Assembly runtime-evidence harness.

Promotes ``tools/prompt_assembly/runtime_evidence.py`` from a standalone
script to a CI signal: any future regression that breaks doctrine
conformance fails this test, surfacing the offending rows.

The harness itself remains the source of truth for what's checked; this
test only enforces that **every row passes**. New requirements added to
the harness automatically extend coverage with no test changes needed.
"""

from __future__ import annotations

import pytest

from tools.prompt_assembly.runtime_evidence import (
    check_aggregation,
    check_determinism,
    check_doctrine_drift,
    check_forbid_deep,
    check_forbid_false_positive,
    check_forbid_rd,
    check_invariants,
    check_must_emit,
    check_must_not_fence,
    check_negative_paths,
    check_parser_robustness,
    check_pipeline_endtoend,
    check_pipeline_negative_paths,
    check_slot_map,
    check_status_partition_complete,
    check_status_set,
)
from tools.prompt_assembly.doctrine_parser import parse_all
from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parents[5]


@pytest.mark.parametrize(
    "category,fn",
    [
        ("STATUS_SET", check_status_set),
        ("DOCTRINE_DRIFT", check_doctrine_drift),
        ("STATUS_PARTITION_COMPLETE", check_status_partition_complete),
        ("MUST_EMIT", check_must_emit),
        ("FORBID_RD", check_forbid_rd),
        ("FORBID_DEEP", check_forbid_deep),
        ("FORBID_FALSE_POSITIVE", check_forbid_false_positive),
        ("MUST_NOT_FENCE", check_must_not_fence),
        ("INVARIANT", check_invariants),
        ("SLOT_MAP", check_slot_map),
        ("NEGATIVE_PATH", check_negative_paths),
        ("DETERMINISM", check_determinism),
        ("AGGREGATION", check_aggregation),
        ("PARSER_ROBUSTNESS", check_parser_robustness),
        ("E2E", check_pipeline_endtoend),
        ("PIPELINE_NEG", check_pipeline_negative_paths),
    ],
    ids=[
        "status_set", "doctrine_drift", "status_partition_complete",
        "must_emit", "forbid_rd", "forbid_deep", "forbid_false_positive",
        "must_not_fence", "invariant", "slot_map",
        "negative_path", "determinism", "aggregation", "parser_robustness",
        "e2e", "pipeline_neg",
    ],
)
def test_runtime_evidence_category_all_pass(category: str, fn) -> None:
    """Every row in each runtime-evidence category must PASS."""
    rows = fn()
    assert rows, f"category {category} produced no rows"
    failures = [r for r in rows if r.status != "PASS"]
    if failures:
        details = "\n".join(
            f"  - {r.req_id}: {r.requirement}\n    evidence={r.evidence}"
            for r in failures
        )
        pytest.fail(
            f"{category} has {len(failures)} failing rows out of {len(rows)}:\n{details}"
        )


def test_doctrine_parser_finds_all_eight_stages() -> None:
    """The parser must successfully read STATUS VALUES + MUST EMIT for
    every PA.0..PA.7 doctrine file."""
    parsed = parse_all(_REPO_ROOT)
    expected_stages = {"PA.0", "PA.1", "PA.2", "PA.3", "PA.4", "PA.5", "PA.6", "PA.7"}
    assert set(parsed.keys()) == expected_stages
    for stage, data in parsed.items():
        assert data["status_values"], (
            f"{stage} parser returned 0 STATUS VALUES — doctrine file missing or "
            f"section heading changed"
        )
        assert data["must_emit"], (
            f"{stage} parser returned 0 MUST EMIT items — doctrine file missing or "
            f"section heading changed"
        )


def test_doctrine_status_values_resolve_to_PAStatus() -> None:
    """Every STATUS value in every doctrine file must be a member of the
    runtime ``PAStatus`` enum.

    This is the single most important drift check — if a doctrine .md
    adds a new status name, this test fails until the runtime enum
    catches up.
    """
    from agentic_core.prompt_governance.prompt_assembly import PAStatus

    runtime = {s.value for s in PAStatus}
    parsed = parse_all(_REPO_ROOT)
    missing: dict[str, list[str]] = {}
    for stage, data in parsed.items():
        gone = [s for s in data["status_values"] if s not in runtime]
        if gone:
            missing[stage] = gone
    assert not missing, (
        f"Doctrine STATUS VALUES not found in PAStatus enum: {missing}"
    )
