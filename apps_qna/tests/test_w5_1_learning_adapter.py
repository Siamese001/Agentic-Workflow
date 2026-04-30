"""W5.1 tests — RehearsalOutcome capture + bandit replay.

Covers:
    - RehearsalOutcome dataclass: success property semantics
    - load_session_from_json: schema validation, error paths
    - record_rehearsal_outcomes: ledger emission + bandit update
    - replay_outcomes_into_bandit: rebuilds posterior from ledger
    - End-to-end: feedback CLI subcommand transitions bandit out of cold-start
"""

from __future__ import annotations

import json
import sqlite3
from io import StringIO
from pathlib import Path

import pytest

from apps_qna.config.route_registry import Route, RouteRegistry
from apps_qna.integrations.learning_adapter import (
    RehearsalOutcome,
    RehearsalSession,
    load_session_from_json,
    record_rehearsal_outcomes,
    replay_outcomes_into_bandit,
)
from apps_qna.router.route_bandit import AppsQnaRouteBandit, _hash_signal


def _mock_registry() -> RouteRegistry:
    return RouteRegistry(
        version="v1",
        routes=[
            Route(
                id="executive_fit",
                number=1,
                name="Executive Fit",
                triggers=["leadership"],
                answer_shape=["headline"],
                primary_card="13_EXECUTIVE_FIT.md",
            ),
            Route(
                id="architecture",
                number=2,
                name="Architecture",
                triggers=["system design"],
                answer_shape=["headline"],
                primary_card="05_ARCHITECTURE_CORE.md",
            ),
            Route(
                id="rca",
                number=3,
                name="RCA",
                triggers=["root cause"],
                answer_shape=["timeline"],
                primary_card="15_RCA.md",
            ),
        ],
        tie_breaker_rules=[],
    )


# --------------------------------------------------------------------------
# RehearsalOutcome dataclass
# --------------------------------------------------------------------------


def test_rehearsal_outcome_success_requires_both_asked_and_landed() -> None:
    assert RehearsalOutcome("r1", "card.md", asked=True, landed=True).success is True
    assert RehearsalOutcome("r1", "card.md", asked=True, landed=False).success is False
    assert RehearsalOutcome("r1", "card.md", asked=False, landed=True).success is False
    assert RehearsalOutcome("r1", "card.md", asked=False, landed=False).success is False


def test_rehearsal_outcome_is_immutable() -> None:
    """Frozen dataclass — assignment must raise."""
    o = RehearsalOutcome("r1", "card.md", asked=True, landed=True)
    with pytest.raises((AttributeError, Exception)):
        o.asked = False  # type: ignore[misc]


# --------------------------------------------------------------------------
# load_session_from_json
# --------------------------------------------------------------------------


def test_load_session_from_json_minimal_valid_input(tmp_path: Path) -> None:
    payload = {
        "namespace": "qna_signal_abc123",
        "interviewer": "Vrinda Khurjekar",
        "outcomes": [
            {
                "asked_route": "executive_fit",
                "card_id": "13_EXECUTIVE_FIT.md",
                "asked": True,
                "landed": True,
                "notes": "Landed cleanly on first try",
            },
            {
                "asked_route": "architecture",
                "card_id": "05_ARCHITECTURE_CORE.md",
                "asked": True,
                "landed": False,
                "notes": "Card too dense, had to extemporize",
            },
        ],
    }
    fp = tmp_path / "outcomes.json"
    fp.write_text(json.dumps(payload), encoding="utf-8")
    session = load_session_from_json("test-slug", fp)
    assert session.slug == "test-slug"
    assert session.namespace == "qna_signal_abc123"
    assert session.interviewer == "Vrinda Khurjekar"
    assert len(session.outcomes) == 2
    assert session.outcomes[0].success is True
    assert session.outcomes[1].success is False


def test_load_session_from_json_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_session_from_json("slug", tmp_path / "does-not-exist.json")


def test_load_session_from_json_missing_namespace_raises(tmp_path: Path) -> None:
    fp = tmp_path / "outcomes.json"
    fp.write_text(json.dumps({"interviewer": "X", "outcomes": []}), encoding="utf-8")
    with pytest.raises(ValueError, match="namespace"):
        load_session_from_json("slug", fp)


def test_load_session_from_json_outcomes_must_be_list(tmp_path: Path) -> None:
    fp = tmp_path / "outcomes.json"
    fp.write_text(
        json.dumps({"namespace": "qna_signal_x", "outcomes": "not a list"}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="outcomes"):
        load_session_from_json("slug", fp)


def test_load_session_from_json_skips_non_dict_outcome_entries(tmp_path: Path) -> None:
    payload = {
        "namespace": "qna_signal_x",
        "outcomes": [
            {"asked_route": "r1", "card_id": "c.md", "asked": True, "landed": True},
            "not a dict",
            42,
            {"asked_route": "r2", "card_id": "c2.md", "asked": False, "landed": False},
        ],
    }
    fp = tmp_path / "outcomes.json"
    fp.write_text(json.dumps(payload), encoding="utf-8")
    session = load_session_from_json("slug", fp)
    assert len(session.outcomes) == 2  # malformed entries skipped


# --------------------------------------------------------------------------
# record_rehearsal_outcomes
# --------------------------------------------------------------------------


def _ledger_path() -> Path | None:
    """Resolve the apps_qna_pack_lifecycle ledger DB path (same as adapter)."""
    try:
        from tools.ledgers.schema_registry import get
        return get("apps_qna_pack_lifecycle").db_path
    except (ImportError, KeyError):
        return None


@pytest.fixture
def ledger_db() -> Path:
    p = _ledger_path()
    if p is None or not p.is_file():
        pytest.skip("apps_qna_pack_lifecycle ledger not materialized")
    return p


def test_record_rehearsal_outcomes_persists_rows(ledger_db: Path) -> None:
    bandit = AppsQnaRouteBandit(_mock_registry(), seed=42)
    namespace = "qna_signal_test_record"
    session = RehearsalSession(
        slug="test-w5-1-record",
        namespace=namespace,
        interviewer="Test Interviewer",
        outcomes=[
            RehearsalOutcome("executive_fit", "13.md", asked=True, landed=True),
            RehearsalOutcome("architecture", "05.md", asked=True, landed=False),
            RehearsalOutcome("rca", "15.md", asked=False, landed=False),
        ],
    )
    persisted = record_rehearsal_outcomes(session, bandit=bandit)
    assert persisted == 3

    # Confirm rows exist in the ledger.
    con = sqlite3.connect(ledger_db)
    try:
        cur = con.cursor()
        cur.execute(
            """SELECT score_band, prediction_json, outcome_json
               FROM events
               WHERE event_kind = 'interview_outcome'
                 AND repo_area = ?""",
            (f"reports/qna/{session.slug}",),
        )
        rows = cur.fetchall()
    finally:
        con.close()
    assert len(rows) >= 3
    bands = {row[0] for row in rows}
    assert "hit" in bands  # the success outcome
    assert "miss" in bands  # the two failure outcomes


def test_record_rehearsal_outcomes_updates_bandit_posterior(ledger_db: Path) -> None:
    bandit = AppsQnaRouteBandit(_mock_registry(), seed=42)
    namespace = "qna_signal_test_bandit_update"
    assert bandit.total_observations(namespace) == 0

    session = RehearsalSession(
        slug="test-w5-1-bandit-update",
        namespace=namespace,
        interviewer="X",
        outcomes=[
            RehearsalOutcome("executive_fit", "13.md", asked=True, landed=True),
            RehearsalOutcome("executive_fit", "13.md", asked=True, landed=True),
            RehearsalOutcome("architecture", "05.md", asked=True, landed=False),
        ],
    )
    record_rehearsal_outcomes(session, bandit=bandit)
    # After 3 outcomes the namespace should have ≥3 observations
    # (the spine bandit's n_observations property counts observations
    # so the total should reflect what we recorded).
    assert bandit.total_observations(namespace) >= 3
    # The success-only arm should have a higher posterior mean than the
    # failure-only arm.
    exec_post = bandit._bandit.posterior(namespace, "executive_fit")
    arch_post = bandit._bandit.posterior(namespace, "architecture")
    assert exec_post.mean > arch_post.mean


def test_record_rehearsal_outcomes_works_without_bandit(ledger_db: Path) -> None:
    """Calling without a bandit must still persist ledger rows."""
    session = RehearsalSession(
        slug="test-w5-1-no-bandit",
        namespace="qna_signal_test_no_bandit",
        interviewer="X",
        outcomes=[
            RehearsalOutcome("executive_fit", "13.md", asked=True, landed=True),
        ],
    )
    persisted = record_rehearsal_outcomes(session, bandit=None)
    assert persisted == 1


# --------------------------------------------------------------------------
# replay_outcomes_into_bandit
# --------------------------------------------------------------------------


def test_replay_outcomes_into_bandit_rebuilds_posterior(ledger_db: Path) -> None:
    """Persist outcomes via session A; replay them into a fresh bandit B."""
    bandit_a = AppsQnaRouteBandit(_mock_registry(), seed=42)
    namespace = "qna_signal_test_replay"
    session = RehearsalSession(
        slug="test-w5-1-replay",
        namespace=namespace,
        interviewer="X",
        outcomes=[
            RehearsalOutcome("rca", "15.md", asked=True, landed=True),
            RehearsalOutcome("rca", "15.md", asked=True, landed=True),
            RehearsalOutcome("rca", "15.md", asked=True, landed=False),
        ],
    )
    record_rehearsal_outcomes(session, bandit=bandit_a)

    # Fresh bandit; posterior must be empty initially.
    bandit_b = AppsQnaRouteBandit(_mock_registry(), seed=42)
    assert bandit_b.total_observations(namespace) == 0

    replayed = replay_outcomes_into_bandit(bandit_b, namespace=namespace)
    assert replayed >= 3
    assert bandit_b.total_observations(namespace) >= 3


def test_replay_outcomes_into_bandit_handles_missing_db(tmp_path: Path) -> None:
    """When the ledger DB doesn't exist, replay returns 0 and does not raise."""
    bandit = AppsQnaRouteBandit(_mock_registry(), seed=42)
    fake_db = tmp_path / "not_a_real_db.sqlite"
    replayed = replay_outcomes_into_bandit(bandit, db_path=fake_db)
    assert replayed == 0


# --------------------------------------------------------------------------
# CLI integration
# --------------------------------------------------------------------------


def test_feedback_cli_round_trip(tmp_path: Path, ledger_db: Path) -> None:
    """End-to-end: write outcomes JSON, run feedback CLI, verify ledger row."""
    from apps_qna.scripts.run_qna import main

    namespace = "qna_signal_test_cli_round_trip"
    payload = {
        "namespace": namespace,
        "interviewer": "Vrinda CLI Test",
        "outcomes": [
            {
                "asked_route": "executive_fit",
                "card_id": "13_EXECUTIVE_FIT.md",
                "asked": True,
                "landed": True,
                "notes": "CLI roundtrip test",
            },
        ],
    }
    fp = tmp_path / "outcomes.json"
    fp.write_text(json.dumps(payload), encoding="utf-8")

    rc = main(
        [
            "feedback",
            "--slug",
            "test-w5-1-cli",
            "--outcomes",
            str(fp),
        ]
    )
    assert rc == 0

    # Confirm the row landed.
    con = sqlite3.connect(ledger_db)
    try:
        cur = con.cursor()
        cur.execute(
            """SELECT prediction_json FROM events
               WHERE event_kind = 'interview_outcome'
                 AND repo_area = 'reports/qna/test-w5-1-cli'""",
        )
        rows = cur.fetchall()
    finally:
        con.close()
    assert len(rows) >= 1


def test_feedback_cli_missing_outcomes_returns_2(tmp_path: Path) -> None:
    from apps_qna.scripts.run_qna import main

    rc = main(
        [
            "feedback",
            "--slug",
            "test-slug",
            "--outcomes",
            str(tmp_path / "does-not-exist.json"),
        ]
    )
    assert rc == 2
