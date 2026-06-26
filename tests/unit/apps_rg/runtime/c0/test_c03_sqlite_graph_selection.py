"""apps-test-model: APP CONTRACT.

SQLite-backed C0.3 graph selection tests.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
    materialize_augmented_skills_graph_sqlite,
)
from apps_rg.runtime.c0.c03_sqlite_graph_selection import (
    SCHEMA_VERSION,
    select_c03_sqlite_graph_candidates,
)

REPO = Path(__file__).resolve().parents[5]


@pytest.fixture
def sqlite_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "c03_selection.sqlite"
    materialize_augmented_skills_graph_sqlite(repo_root=REPO, db_path=db_path)
    return db_path


def test_select_c03_sqlite_graph_candidates_returns_ranked_bindings(sqlite_db: Path) -> None:
    out = select_c03_sqlite_graph_candidates(
        section_id="executive_summary",
        selected_fact_ids=["fact_engineering_platform_001"],
        role_family_key="SVP_ENGINEERING_AI_PLATFORM",
        pillar_hints=["pillar_agentic_runtime_governance"],
        repo_root=REPO,
        db_path=sqlite_db,
    )

    assert out["schema_version"] == SCHEMA_VERSION
    assert out["graph_source"] == "augmented_skills_graph_sqlite"
    assert out["graph_hash"]
    assert out["selected_candidates"]
    assert out["selected_by_fact"]["fact_engineering_platform_001"]
    assert out["metric_bucket_counts"]
    assert all(c["skill_id"].startswith("skill_") for c in out["selected_candidates"])
    assert all(c["path_signature"] for c in out["selected_candidates"])
    assert out["sibling_alternative_count"] > 0
    assert any(c["sibling_alternatives"] for c in out["selected_candidates"])


def test_select_c03_sqlite_graph_candidates_receipts_rejected_siblings(
    sqlite_db: Path,
) -> None:
    out = select_c03_sqlite_graph_candidates(
        section_id="executive_summary",
        selected_fact_ids=["fact_engineering_platform_001"],
        role_family_key="SVP_ENGINEERING_AI_PLATFORM",
        pillar_hints=["pillar_agentic_runtime_governance"],
        repo_root=REPO,
        db_path=sqlite_db,
        max_skills_per_fact=1,
    )

    rejected = out["rejected_by_fact"]["fact_engineering_platform_001"]
    assert rejected
    assert out["rejected_sibling_skill_count"] == len(out["rejected_siblings"])
    assert {r["failed_gate"] for r in rejected}
    assert {r["rejection_reason"] for r in rejected}
    assert out["rejection_receipts"]
    assert {
        "candidate_node_id",
        "candidate_node_type",
        "rejected_reason",
        "rejected_at_stage",
        "competing_selected_node_id",
        "path_signature",
    }.issubset(out["rejection_receipts"][0])


def test_select_c03_sqlite_graph_candidates_applies_repeat_penalties(
    sqlite_db: Path,
) -> None:
    out = select_c03_sqlite_graph_candidates(
        section_id="executive_summary",
        selected_fact_ids=[
            "fact_engineering_platform_001",
            "fact_engineering_platform_003",
            "fact_engineering_platform_004",
        ],
        role_family_key="SVP_ENGINEERING_AI_PLATFORM",
        pillar_hints=["pillar_agentic_runtime_governance"],
        repo_root=REPO,
        db_path=sqlite_db,
        max_skills_per_fact=3,
    )

    selected_with_penalties = [
        c for c in out["selected_candidates"] if c.get("penalties")
    ]
    assert out["selected_candidates"]
    assert out["metric_bucket_counts"]
    assert out["penalty_count"] == len(selected_with_penalties)
    assert selected_with_penalties, "expected repeat penalties across overlapping graph neighborhoods"


def test_select_c03_sqlite_graph_candidates_applies_metric_usage_memory(
    sqlite_db: Path,
) -> None:
    conn = sqlite3.connect(str(sqlite_db))
    try:
        conn.execute(
            """
            INSERT INTO resume_metric_usage (
                run_id, resume_section, metric_id, metric_value, fact_id, skill_id,
                role_family_key, usage_count, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "prior_run",
                "executive_summary",
                "metric_prior_runtime_governance",
                "prior runtime governance metric",
                "fact_engineering_platform_001",
                "skill_runtime_gate_mesh_design",
                "SVP_ENGINEERING_AI_PLATFORM",
                3,
                "2026-06-25T00:00:00Z",
            ),
        )
        conn.commit()
    finally:
        conn.close()

    out = select_c03_sqlite_graph_candidates(
        section_id="executive_summary",
        selected_fact_ids=["fact_engineering_platform_001"],
        role_family_key="SVP_ENGINEERING_AI_PLATFORM",
        pillar_hints=["pillar_agentic_runtime_governance"],
        repo_root=REPO,
        db_path=sqlite_db,
        max_skills_per_fact=3,
    )

    assert out["prior_metric_usage_penalty_count"] > 0
    assert any(
        "prior_metric_usage_penalty" in (c.get("penalties") or {})
        for c in out["selected_candidates"]
    )
