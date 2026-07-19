"""apps-test-model: APP CONTRACT.

SQLite-backed C0.3 graph selection tests.
"""

from __future__ import annotations

import hashlib
import shutil
import sqlite3
from pathlib import Path
from typing import Any

import pytest

import apps_rg.runtime.c0.c03_sqlite_graph_selection as selection_module
import apps_rg.runtime.c03_graph_sqlite_context as context_module
from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
    materialize_augmented_skills_graph_sqlite,
)
from apps_rg.runtime.c0.c03_errors import C03GraphProjectionUnavailableError
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
    assert all(c["authority_pass"] for c in out["selected_candidates"])
    assert out["pretarget_authority_receipt"]["targeting_consulted_count"] == 0
    assert out["candidate_conservation_pass"] is True
    assert len(out["candidate_decision_ledger"]) == out["candidate_count"]
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
        candidate for candidate in out["selected_candidates"] if candidate.get("penalties")
    ]
    assert out["selected_candidates"]
    assert out["metric_bucket_counts"]
    assert out["penalty_count"] == len(selected_with_penalties)
    assert selected_with_penalties


def test_metric_usage_memory_is_scoped_to_current_run(sqlite_db: Path) -> None:
    conn = sqlite3.connect(str(sqlite_db))
    try:
        for run_id in ("prior_run", "current_run"):
            conn.execute(
                """
                INSERT INTO resume_metric_usage (
                    run_id, resume_section, metric_id, metric_value, fact_id, skill_id,
                    role_family_key, usage_count, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    "executive_summary",
                    f"metric_{run_id}_runtime_governance",
                    "runtime governance metric",
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

    no_run = select_c03_sqlite_graph_candidates(
        section_id="executive_summary",
        selected_fact_ids=["fact_engineering_platform_001"],
        role_family_key="SVP_ENGINEERING_AI_PLATFORM",
        pillar_hints=["pillar_agentic_runtime_governance"],
        repo_root=REPO,
        db_path=sqlite_db,
        max_skills_per_fact=3,
    )
    assert no_run["prior_metric_usage_penalty_count"] == 0
    assert no_run["run_id_scope"] == ""

    current = select_c03_sqlite_graph_candidates(
        section_id="executive_summary",
        selected_fact_ids=["fact_engineering_platform_001"],
        role_family_key="SVP_ENGINEERING_AI_PLATFORM",
        pillar_hints=["pillar_agentic_runtime_governance"],
        repo_root=REPO,
        db_path=sqlite_db,
        max_skills_per_fact=3,
        run_id="current_run",
    )
    assert current["prior_metric_usage_penalty_count"] > 0
    assert current["run_id_scope"] == "current_run"
    assert any(
        "prior_metric_usage_penalty" in (candidate.get("penalties") or {})
        for candidate in current["selected_candidates"]
    )


def test_run_scoped_usage_digest_changes_without_changing_graph_binding(
    sqlite_db: Path,
) -> None:
    selection_before = select_c03_sqlite_graph_candidates(
        section_id="executive_summary",
        selected_fact_ids=["fact_engineering_platform_001"],
        role_family_key="SVP_ENGINEERING_AI_PLATFORM",
        pillar_hints=["pillar_agentic_runtime_governance"],
        repo_root=REPO,
        db_path=sqlite_db,
        run_id="digest_run",
    )

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
                "digest_run",
                "executive_summary",
                "metric_digest_runtime_governance",
                "digest binding marker",
                "fact_engineering_platform_001",
                "skill_runtime_gate_mesh_design",
                "SVP_ENGINEERING_AI_PLATFORM",
                2,
                "2026-07-19T00:00:00Z",
            ),
        )
        conn.commit()
    finally:
        conn.close()

    selection_after = select_c03_sqlite_graph_candidates(
        section_id="executive_summary",
        selected_fact_ids=["fact_engineering_platform_001"],
        role_family_key="SVP_ENGINEERING_AI_PLATFORM",
        pillar_hints=["pillar_agentic_runtime_governance"],
        repo_root=REPO,
        db_path=sqlite_db,
        run_id="digest_run",
    )
    context_after = context_module.assemble_c03_graph_sqlite_context(
        role_family_key="SVP_ENGINEERING_AI_PLATFORM",
        section_id="executive_summary",
        selected_fact_ids=["fact_engineering_platform_001"],
        repo_root=REPO,
        db_path=sqlite_db,
        run_id="digest_run",
    )["receipt"]

    assert selection_before["canonical_ledger_hash"] == selection_after["canonical_ledger_hash"]
    assert selection_before["sqlite_logical_digest"] == selection_after["sqlite_logical_digest"]
    assert selection_before["sqlite_schema_digest"] == selection_after["sqlite_schema_digest"]
    assert (
        selection_before["resume_metric_usage_ranking_input_digest"]
        != (selection_after["resume_metric_usage_ranking_input_digest"])
    )
    assert context_after["canonical_ledger_hash"] == selection_after["canonical_ledger_hash"]
    assert context_after["sqlite_logical_digest"] == selection_after["sqlite_logical_digest"]
    assert context_after["sqlite_schema_digest"] == selection_after["sqlite_schema_digest"]
    assert (
        context_after["resume_metric_usage_ranking_input_digest"]
        == (selection_after["resume_metric_usage_ranking_input_digest"])
    )


def test_sibling_alternatives_exclude_blocked_activation_and_support() -> None:
    conn = sqlite3.connect(":memory:")
    try:
        conn.executescript(
            """
            CREATE TABLE graph_nodes (
                node_id TEXT PRIMARY KEY,
                node_type TEXT NOT NULL,
                label TEXT NOT NULL,
                activation_status TEXT NOT NULL,
                support_level TEXT NOT NULL,
                external_eligible INTEGER NOT NULL
            );
            CREATE TABLE graph_sibling_links (
                node_id TEXT NOT NULL,
                sibling_node_id TEXT NOT NULL,
                sibling_reason TEXT NOT NULL,
                shared_parent_node_id TEXT NOT NULL,
                shared_edge_type TEXT NOT NULL,
                sibling_score REAL NOT NULL
            );
            """
        )
        node_rows = [
            ("skill_allowed", "skill", "Allowed", "ACTIVE", "FACT_BACKED", 1),
            ("skill_blocked", "skill", "Blocked", "BLOCKED", "FACT_BACKED", 1),
            (
                "skill_internal_activation",
                "skill",
                "Internal activation",
                "INTERNAL_ONLY",
                "FACT_BACKED",
                1,
            ),
            (
                "skill_active_internal_only",
                "skill",
                "Active internal only",
                "ACTIVE_INTERNAL_ONLY",
                "FACT_BACKED",
                1,
            ),
            (
                "skill_internal_support",
                "skill",
                "Internal support",
                "ACTIVE",
                "INTERNAL_ONLY",
                1,
            ),
            (
                "skill_targeting_support",
                "skill",
                "Targeting support",
                "ACTIVE",
                "TARGETING_ONLY",
                1,
            ),
        ]
        conn.executemany(
            "INSERT INTO graph_nodes VALUES (?, ?, ?, ?, ?, ?)",
            node_rows,
        )
        conn.executemany(
            "INSERT INTO graph_sibling_links VALUES (?, ?, ?, ?, ?, ?)",
            [
                (
                    "skill_source",
                    node_id,
                    "shared_parent",
                    "pillar_parent",
                    "pillar_contains_skill",
                    1.0,
                )
                for node_id, *_rest in node_rows
            ],
        )

        alternatives = selection_module._query_sibling_alternatives(
            conn=conn,
            selected_skill_ids=["skill_source"],
        )["skill_source"]
    finally:
        conn.close()

    assert [row["skill_id"] for row in alternatives] == ["skill_allowed"]


def test_selection_translates_post_validation_query_errors(
    sqlite_db: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_query(**_kwargs: Any) -> Any:
        raise sqlite3.OperationalError("simulated query failure")

    monkeypatch.setattr(selection_module, "_query_candidates", fail_query)

    with pytest.raises(
        C03GraphProjectionUnavailableError,
        match="selection query failed.*OperationalError",
    ):
        select_c03_sqlite_graph_candidates(
            section_id="executive_summary",
            selected_fact_ids=["fact_engineering_platform_001"],
            role_family_key="SVP_ENGINEERING_AI_PLATFORM",
            pillar_hints=["pillar_agentic_runtime_governance"],
            repo_root=REPO,
            db_path=sqlite_db,
        )


def test_selection_pins_one_validated_snapshot_across_reopen_replacement_race(
    sqlite_db: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    replacement_db = tmp_path / "replacement.sqlite"
    shutil.copy2(sqlite_db, replacement_db)
    conn = sqlite3.connect(str(replacement_db))
    try:
        conn.execute(
            """
            INSERT INTO resume_metric_usage (
                run_id, resume_section, metric_id, metric_value, fact_id, skill_id,
                role_family_key, usage_count, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "replacement_run",
                "executive_summary",
                "metric_replacement_runtime_governance",
                "replacement generation marker",
                "fact_engineering_platform_001",
                "skill_runtime_gate_mesh_design",
                "SVP_ENGINEERING_AI_PLATFORM",
                3,
                "2026-07-18T00:00:00Z",
            ),
        )
        conn.commit()
    finally:
        conn.close()

    replacement_out = select_c03_sqlite_graph_candidates(
        section_id="executive_summary",
        selected_fact_ids=["fact_engineering_platform_001"],
        role_family_key="SVP_ENGINEERING_AI_PLATFORM",
        pillar_hints=["pillar_agentic_runtime_governance"],
        repo_root=REPO,
        db_path=replacement_db,
        max_skills_per_fact=3,
        run_id="replacement_run",
    )
    assert replacement_out["prior_metric_usage_penalty_count"] > 0

    original_digest = hashlib.sha256(sqlite_db.read_bytes()).hexdigest()
    real_open = context_module.open_graph_sqlite
    real_validate = context_module._validate_c03_graph_sqlite_connection
    real_query_candidates = selection_module._query_candidates
    real_query_siblings = selection_module._query_sibling_alternatives
    open_modes: list[bool] = []
    snapshot_steps: list[tuple[str, int, bool]] = []

    def racing_open_graph_sqlite(**kwargs: Any) -> Any:
        open_modes.append(bool(kwargs.get("read_only")))
        if len(open_modes) == 2:
            replacement_db.replace(sqlite_db)
        return real_open(**kwargs)

    def record_validation_transaction_state(
        connection: Any,
        **kwargs: Any,
    ) -> dict[str, Any]:
        snapshot_steps.append(("validation", id(connection), bool(connection.in_transaction)))
        return real_validate(connection, **kwargs)

    def record_candidate_query(*, conn: Any, **kwargs: Any) -> Any:
        snapshot_steps.append(("candidates", id(conn), bool(conn.in_transaction)))
        return real_query_candidates(conn=conn, **kwargs)

    def record_sibling_query(*, conn: Any, **kwargs: Any) -> Any:
        snapshot_steps.append(("siblings", id(conn), bool(conn.in_transaction)))
        return real_query_siblings(conn=conn, **kwargs)

    monkeypatch.setattr(context_module, "open_graph_sqlite", racing_open_graph_sqlite)
    monkeypatch.setattr(
        context_module,
        "_validate_c03_graph_sqlite_connection",
        record_validation_transaction_state,
    )
    monkeypatch.setattr(
        selection_module,
        "open_graph_sqlite",
        racing_open_graph_sqlite,
        raising=False,
    )
    monkeypatch.setattr(selection_module, "_query_candidates", record_candidate_query)
    monkeypatch.setattr(
        selection_module,
        "_query_sibling_alternatives",
        record_sibling_query,
    )

    out = select_c03_sqlite_graph_candidates(
        section_id="executive_summary",
        selected_fact_ids=["fact_engineering_platform_001"],
        role_family_key="SVP_ENGINEERING_AI_PLATFORM",
        pillar_hints=["pillar_agentic_runtime_governance"],
        repo_root=REPO,
        db_path=sqlite_db,
        max_skills_per_fact=3,
        run_id="replacement_run",
    )

    assert open_modes == [True]
    assert [step for step, _connection_id, _in_transaction in snapshot_steps] == [
        "validation",
        "candidates",
        "siblings",
    ]
    assert all(in_transaction for _step, _connection_id, in_transaction in snapshot_steps)
    assert len({connection_id for _step, connection_id, _state in snapshot_steps}) == 1
    assert out["prior_metric_usage_penalty_count"] == 0
    assert replacement_db.is_file()
    assert hashlib.sha256(sqlite_db.read_bytes()).hexdigest() == original_digest
