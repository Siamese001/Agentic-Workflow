"""W1.4 tests — apps_qna_pack_lifecycle ledger registration + writer.

Covers:
    - Schema registry: ledger is registered, db_path / schema_path resolve,
      apply_schema can find it
    - On-disk DB: events / events_fts / event_scope tables exist; both base
      (v1) and extension (v114) schema_version rows present
    - emit_pack_lifecycle_event: writes a row, returns event_id, fail-soft
      on bad input
    - card_pack_builder: pack_build event lands in the ledger after a
      smoke build
    - Consulting skill: SKILL.md exists with correct frontmatter
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from tools.ledgers.schema_registry import LEDGER_REGISTRY, get


# --------------------------------------------------------------------------
# Schema registry surface
# --------------------------------------------------------------------------


def test_apps_qna_pack_lifecycle_is_registered() -> None:
    """The ledger appears in LEDGER_REGISTRY by name."""
    spec = get("apps_qna_pack_lifecycle")
    assert spec.name == "apps_qna_pack_lifecycle"
    assert spec.wave == "W1.4"
    assert "pack" in spec.purpose.lower()
    assert spec.schema_file == "apps_qna_pack_lifecycle_ledger.schema.sql"


def test_ledger_schema_file_exists() -> None:
    spec = get("apps_qna_pack_lifecycle")
    assert spec.schema_path.is_file(), f"missing schema file: {spec.schema_path}"


def test_ledger_writer_hook_path_documented() -> None:
    """Writer hook points to the actual builder file."""
    spec = get("apps_qna_pack_lifecycle")
    # Writer hook is repo-relative; the file MUST exist.
    repo_root = Path(__file__).resolve().parents[2]
    hook_path = repo_root / spec.writer_hook
    assert hook_path.is_file(), f"writer_hook does not exist: {hook_path}"


def test_consulting_skill_exists_with_frontmatter() -> None:
    spec = get("apps_qna_pack_lifecycle")
    repo_root = Path(__file__).resolve().parents[2]
    skill_path = repo_root / spec.consulting_skill
    assert skill_path.is_file(), f"missing skill: {skill_path}"
    text = skill_path.read_text(encoding="utf-8")
    # YAML frontmatter required for ledger-consulter skills.
    assert text.startswith("---\n"), "skill must start with YAML frontmatter"
    assert "name: ledger-consulter-apps-qna-pack-lifecycle" in text
    assert "trigger: model_decision" in text


# --------------------------------------------------------------------------
# On-disk database
# --------------------------------------------------------------------------


def _ledger_db_path() -> Path:
    spec = get("apps_qna_pack_lifecycle")
    return spec.db_path


@pytest.fixture
def ledger_db() -> Path:
    """Return the ledger DB path; skip if the migration hasn't run yet."""
    p = _ledger_db_path()
    if not p.is_file():
        pytest.skip("Ledger DB not materialized (run apply_schema)")
    return p


def test_ledger_db_has_base_schema_tables(ledger_db: Path) -> None:
    con = sqlite3.connect(ledger_db)
    try:
        cur = con.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = {row[0] for row in cur.fetchall()}
    finally:
        con.close()
    # Base schema (v1) tables.
    assert "events" in tables
    assert "event_scope" in tables
    assert "schema_version" in tables
    # FTS5 virtual table from base.
    assert "events_fts" in tables


def test_ledger_db_has_both_schema_versions(ledger_db: Path) -> None:
    """Migration applies both base (v1) and extension (v114) records."""
    con = sqlite3.connect(ledger_db)
    try:
        rows = list(con.execute("SELECT version FROM schema_version ORDER BY version"))
    finally:
        con.close()
    versions = {r[0] for r in rows}
    assert 1 in versions, "base schema_version=1 missing"
    assert 114 in versions, "apps_qna_pack_lifecycle schema_version=114 missing"


def test_ledger_db_has_extension_indexes(ledger_db: Path) -> None:
    """The extension schema declares indexes specific to apps_qna queries."""
    con = sqlite3.connect(ledger_db)
    try:
        rows = list(
            con.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_apps_qna_%'"
            )
        )
    finally:
        con.close()
    names = {r[0] for r in rows}
    assert "idx_apps_qna_kind_band" in names
    assert "idx_apps_qna_repo_area_kind" in names


# --------------------------------------------------------------------------
# emit_pack_lifecycle_event surface
# --------------------------------------------------------------------------


def test_emit_pack_lifecycle_event_returns_event_id_on_success(ledger_db: Path) -> None:
    from apps_qna.integrations.spine_adapter import emit_pack_lifecycle_event

    event_id = emit_pack_lifecycle_event(
        event_kind="pack_build",
        prediction={
            "interview_slug": "test-w1-4-smoke",
            "interviewer": "Test Interviewer",
            "card_count": 22,
            "routes_covered": ["executive_fit", "architecture"],
            "paste_set_size": 18,
            "paste_exceeds_chatgpt_limit": False,
            "template_set_version": "v2",
            "builder_version": "0.1.0",
        },
        score_band="clean",
        repo_area="reports/qna/test-w1-4-smoke",
    )
    # Successful writes return a non-empty event_id.
    assert event_id, "emit_pack_lifecycle_event returned empty on a valid call"


def test_emit_pack_lifecycle_event_row_lands_in_ledger(ledger_db: Path) -> None:
    """End-to-end: emit a row, then verify it can be read back."""
    from apps_qna.integrations.spine_adapter import emit_pack_lifecycle_event

    event_id = emit_pack_lifecycle_event(
        event_kind="pack_build",
        prediction={
            "interview_slug": "test-w1-4-readback",
            "card_count": 22,
        },
        score_band="clean",
        repo_area="reports/qna/test-w1-4-readback",
    )
    assert event_id

    con = sqlite3.connect(ledger_db)
    try:
        cur = con.cursor()
        cur.execute(
            "SELECT event_kind, repo_area, score_band FROM events WHERE event_id = ?",
            (event_id,),
        )
        row = cur.fetchone()
    finally:
        con.close()
    assert row is not None
    assert row[0] == "pack_build"
    assert row[1] == "reports/qna/test-w1-4-readback"
    assert row[2] == "clean"


def test_emit_pack_lifecycle_event_is_fail_soft_on_bad_ledger_name() -> None:
    """If the underlying writer fails, the helper returns empty string."""
    # We can't easily inject a bad ledger_name through emit_pack_lifecycle_event
    # because it pre-binds the ledger name; instead verify the symmetric
    # contract holds when the underlying writer is invoked with garbage.
    from tools.ledgers.hook_helpers import emit_ledger_event

    result = emit_ledger_event(
        ledger="definitely_not_a_registered_ledger_xyz",
        event_kind="anything",
        prediction={},
        repo_area="test",
    )
    # Fail-soft contract: empty string, no raise.
    assert result == ""


# --------------------------------------------------------------------------
# Builder integration (smoke)
# --------------------------------------------------------------------------


def test_card_pack_builder_emits_pack_build_event_to_ledger(
    tmp_path: Path,
    ledger_db: Path,
) -> None:
    """Run a real build against the Searce YAML and confirm the row lands."""
    import yaml

    from apps_qna.builder.card_pack_builder import CardPackBuilder
    from apps_qna.config.build_config import QnaBuildConfig
    from apps_qna.types.qna_types import Interview

    interview_yaml = Path("reports/qna/searce-applied-ai/interview.yaml")
    if not interview_yaml.is_file():
        pytest.skip("Searce interview YAML not present")
    payload = yaml.safe_load(interview_yaml.read_text(encoding="utf-8"))
    extra_context = payload.pop("extra_context", {})
    interview = Interview.model_validate(payload)

    output_dir = tmp_path / "test-w1-4-build-pack"
    builder = CardPackBuilder(
        config=QnaBuildConfig(force=True),
        route_registry=None,
    )
    manifest = builder.build(interview, output_dir, extra_context=extra_context)
    assert manifest.cards, "builder produced an empty pack"

    # Confirm the row lands. Look for a pack_build event with this output_dir.
    con = sqlite3.connect(ledger_db)
    try:
        cur = con.cursor()
        cur.execute(
            """SELECT event_kind, score_band, prediction_json FROM events
               WHERE event_kind = 'pack_build'
                 AND repo_area = ?
               ORDER BY ts_utc DESC LIMIT 1""",
            (str(output_dir),),
        )
        row = cur.fetchone()
    finally:
        con.close()
    assert row is not None, "no pack_build row landed for the smoke build"
    kind, band, prediction_json = row
    assert kind == "pack_build"
    assert band == "clean"
    assert prediction_json
    assert "interview_slug" in prediction_json
