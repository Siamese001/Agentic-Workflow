"""Phase D.3 cert-decision ledger writer unit tests — plan §12 (21 cases).

All tests are hermetic: ``tmp_path`` for ledger output; no writes outside
``tmp_path``; no network; no subprocess. No imports from
``agentic_core.L*``, ``ops_scripts.ci.*``, or ``tools.spine.scanner.*``.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import re
import sqlite3
import sys
import threading
from pathlib import Path

import pytest

from tools.runtime_cert.decisions.cert_decision_ledger import (
    APP_PREFIX,
    BYPASS_ENV_VAR,
    CertDecisionLedgerWriteResult,
    ensure_cert_decision_ledger,
    ledger_path_for_app,
    read_cert_decision_records,
    write_cert_decision_record,
)
from tools.runtime_cert.decisions.cert_decision_record import (
    CertificationDecisionRecord,
    NOT_CERTIFIED,
    VERDICT_CERTIFY,
    VERDICT_HOLD,
    VERDICT_REJECT,
    compute_decision_id,
    make_certification_decision_record,
)

# ---------------------------------------------------------------------------
# Fixture helpers.
# ---------------------------------------------------------------------------


def _h(seed: str) -> str:
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


MANIFEST_A = _h("manifest-A")
MANIFEST_B = _h("manifest-B")
CLOSEOUT_HASH = _h("closeout-1")


def _make_record(
    *,
    app_name: str = "apps_research",
    manifest_hash: str = MANIFEST_A,
    closeout_report_hash: str = CLOSEOUT_HASH,
    evidence_kind: str = "r3",
    route_shape: str = "R3_grounded_read",
    verdict: str = VERDICT_HOLD,
    failure_reasons: tuple[str, ...] = ("SAMPLE_SIZE_TOO_SMALL",),
    generated_at_utc: str = "2026-05-01T12:00:00Z",
    next_review_utc: str = "2026-05-08T12:00:00Z",
    trace_observed_n: int = 0,
    trace_observed_success_n: int = 0,
    evidence_rate: float = 0.0,
    wilson_lower: float = 0.0,
    z_score: float = 0.0,
    uplift: float = 0.0,
) -> CertificationDecisionRecord:
    return make_certification_decision_record(
        generated_at_utc=generated_at_utc,
        app_name=app_name,
        route_shape=route_shape,
        manifest_hash=manifest_hash,
        evidence_kind=evidence_kind,
        closeout_report_id="r1",
        closeout_report_hash=closeout_report_hash,
        trace_observed_n=trace_observed_n,
        trace_observed_success_n=trace_observed_success_n,
        evidence_rate=evidence_rate,
        wilson_lower=wilson_lower,
        z_score=z_score,
        uplift=uplift,
        verdict=verdict,
        failure_reasons=failure_reasons,
        next_review_utc=next_review_utc,
    )


@pytest.fixture(autouse=True)
def _clear_bypass_env(monkeypatch):
    """Ensure the bypass env var is not leaked across tests."""
    monkeypatch.delenv(BYPASS_ENV_VAR, raising=False)
    yield


# ===========================================================================
# 1–2. ledger_path_for_app
# ===========================================================================


def test_ledger_path_validates_apps_prefix(tmp_path):
    with pytest.raises(ValueError, match="apps_"):
        ledger_path_for_app("research", repo_root=tmp_path)
    with pytest.raises(ValueError, match="apps_"):
        ledger_path_for_app("eval", repo_root=tmp_path)


def test_ledger_path_returns_canonical_location(tmp_path):
    p = ledger_path_for_app("apps_research", repo_root=tmp_path)
    assert p == tmp_path / "artifacts" / "ledgers" / "cert_decision_apps_research.sqlite"
    # Path returned but file not yet created.
    assert not p.exists()


def test_ledger_path_rejects_non_string_app_name(tmp_path):
    with pytest.raises(TypeError):
        ledger_path_for_app(123, repo_root=tmp_path)  # type: ignore[arg-type]


# ===========================================================================
# 3–4. ensure_cert_decision_ledger
# ===========================================================================


def test_ensure_ledger_creates_schema_and_indexes(tmp_path):
    p = ledger_path_for_app("apps_research", repo_root=tmp_path)
    ensure_cert_decision_ledger(p)
    assert p.exists()
    conn = sqlite3.connect(str(p))
    try:
        tables = {
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        indexes = {
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' "
                "AND name NOT LIKE 'sqlite_autoindex_%'"
            )
        }
        cols = {r[1] for r in conn.execute("PRAGMA table_info(cert_decisions)")}
    finally:
        conn.close()
    assert tables == {"cert_decisions"}
    assert indexes == {
        "idx_cert_decisions_app_manifest",
        "idx_cert_decisions_closeout_report_hash",
        "idx_cert_decisions_generated_at_utc",
    }
    # All 21 plan columns present.
    expected_cols = {
        "decision_id",
        "generated_at_utc",
        "app_name",
        "route_shape",
        "manifest_hash",
        "evidence_kind",
        "closeout_report_id",
        "closeout_report_hash",
        "trace_observed_n",
        "trace_observed_success_n",
        "evidence_rate",
        "wilson_lower",
        "z_score",
        "uplift",
        "verdict",
        "failure_reasons_json",
        "next_review_utc",
        "runtime_certification_status_before",
        "runtime_certification_status_after",
        "record_json",
        "inserted_at_utc",
    }
    assert cols == expected_cols


def test_ensure_ledger_is_idempotent(tmp_path):
    p = ledger_path_for_app("apps_research", repo_root=tmp_path)
    ensure_cert_decision_ledger(p)
    ensure_cert_decision_ledger(p)  # second call must not raise
    ensure_cert_decision_ledger(p)  # third too
    conn = sqlite3.connect(str(p))
    try:
        rows = conn.execute("SELECT COUNT(*) FROM cert_decisions").fetchone()
    finally:
        conn.close()
    assert rows[0] == 0  # no rows inserted by ensure


# ===========================================================================
# 5–7. Write happy path + idempotency.
# ===========================================================================


def test_write_valid_record_returns_written_true(tmp_path):
    rec = _make_record()
    res = write_cert_decision_record(rec, repo_root=tmp_path)
    assert res.written is True
    assert res.already_exists is False
    assert res.skipped is False
    assert res.error is None
    assert res.app_name == "apps_research"
    assert res.decision_id == rec.decision_id
    assert res.ledger_path == ledger_path_for_app("apps_research", repo_root=tmp_path)
    assert res.ledger_path.exists()


def test_duplicate_decision_id_returns_already_exists(tmp_path):
    rec = _make_record()
    first = write_cert_decision_record(rec, repo_root=tmp_path)
    second = write_cert_decision_record(rec, repo_root=tmp_path)
    assert first.written is True
    assert second.already_exists is True
    assert second.written is False
    assert second.skipped is False
    assert second.error is None


def test_duplicate_decision_id_does_not_modify_row(tmp_path):
    """INSERT OR IGNORE semantics — second write does not mutate stored fields."""
    rec_first = _make_record(
        generated_at_utc="2026-05-01T12:00:00Z", verdict=VERDICT_HOLD
    )
    write_cert_decision_record(rec_first, repo_root=tmp_path)

    # Build another record with SAME decision_id inputs (app/manifest/closeout)
    # but different verdict + timestamp. If INSERT OR IGNORE worked
    # correctly, the stored row must still show the first record's data.
    rec_second = _make_record(
        generated_at_utc="2026-06-01T12:00:00Z",
        verdict=VERDICT_CERTIFY,
        trace_observed_n=99,
        trace_observed_success_n=99,
        evidence_rate=1.0,
        failure_reasons=(),
    )
    assert rec_first.decision_id == rec_second.decision_id

    result = write_cert_decision_record(rec_second, repo_root=tmp_path)
    assert result.already_exists is True

    records = read_cert_decision_records("apps_research", repo_root=tmp_path)
    assert len(records) == 1
    assert records[0].verdict == VERDICT_HOLD  # NOT mutated to CERTIFY
    assert records[0].generated_at_utc == "2026-05-01T12:00:00Z"
    assert records[0].trace_observed_n == 0


# ===========================================================================
# 8. Round-trip.
# ===========================================================================


def test_write_then_read_round_trip(tmp_path):
    rec = _make_record(
        trace_observed_n=31,
        trace_observed_success_n=30,
        evidence_rate=30 / 31,
        wilson_lower=0.82,
        z_score=3.5,
        uplift=0.45,
        verdict=VERDICT_CERTIFY,
        failure_reasons=(),
    )
    write_cert_decision_record(rec, repo_root=tmp_path)
    records = read_cert_decision_records("apps_research", repo_root=tmp_path)
    assert len(records) == 1
    got = records[0]
    # Full field parity.
    assert got == rec
    # Status invariants round-trip (D.1 + SQL CHECK).
    assert got.runtime_certification_status_before == NOT_CERTIFIED
    assert got.runtime_certification_status_after == NOT_CERTIFIED


# ===========================================================================
# 9. Missing ledger read.
# ===========================================================================


def test_read_missing_ledger_returns_empty_tuple(tmp_path):
    result = read_cert_decision_records("apps_never_written", repo_root=tmp_path)
    assert result == ()


def test_read_ordered_by_generated_at_then_decision_id(tmp_path):
    # Three records with different manifest/closeout (to get distinct decision_ids)
    # but staggered generated_at_utc. Read order must follow generated_at ASC.
    records = [
        _make_record(
            manifest_hash=_h(f"m-{i}"),
            closeout_report_hash=_h(f"c-{i}"),
            generated_at_utc=ts,
        )
        for i, ts in enumerate(
            ["2026-05-03T00:00:00Z", "2026-05-01T00:00:00Z", "2026-05-02T00:00:00Z"]
        )
    ]
    # Write in scrambled order.
    for rec in records:
        write_cert_decision_record(rec, repo_root=tmp_path)
    got = read_cert_decision_records("apps_research", repo_root=tmp_path)
    assert [r.generated_at_utc for r in got] == [
        "2026-05-01T00:00:00Z",
        "2026-05-02T00:00:00Z",
        "2026-05-03T00:00:00Z",
    ]


# ===========================================================================
# 10–12. Fail-soft / fail-hard / bypass.
# ===========================================================================


def test_fail_soft_absorbs_sqlite_error(tmp_path, monkeypatch):
    rec = _make_record()

    def _boom(*args, **kwargs):
        raise sqlite3.OperationalError("disk I/O error (simulated)")

    monkeypatch.setattr(sqlite3, "connect", _boom)
    result = write_cert_decision_record(rec, repo_root=tmp_path, fail_soft=True)
    assert result.skipped is True
    assert result.written is False
    assert result.already_exists is False
    assert result.error is not None
    assert "disk I/O error" in result.error


def test_fail_soft_false_raises_sqlite_error(tmp_path, monkeypatch):
    rec = _make_record()

    def _boom(*args, **kwargs):
        raise sqlite3.OperationalError("locked (simulated)")

    monkeypatch.setattr(sqlite3, "connect", _boom)
    with pytest.raises(sqlite3.OperationalError, match="locked"):
        write_cert_decision_record(rec, repo_root=tmp_path, fail_soft=False)


def test_bypass_env_var_returns_skipped(tmp_path, monkeypatch):
    rec = _make_record()
    monkeypatch.setenv(BYPASS_ENV_VAR, "1")
    result = write_cert_decision_record(rec, repo_root=tmp_path)
    assert result.skipped is True
    assert result.error == "bypass"
    # Most importantly — nothing written to disk.
    assert not ledger_path_for_app("apps_research", repo_root=tmp_path).exists()


def test_bypass_env_var_false_value_does_not_bypass(tmp_path, monkeypatch):
    rec = _make_record()
    monkeypatch.setenv(BYPASS_ENV_VAR, "0")
    result = write_cert_decision_record(rec, repo_root=tmp_path)
    assert result.written is True


# ===========================================================================
# 13. TypeError on invalid record input.
# ===========================================================================


def test_type_error_on_non_record_input(tmp_path):
    for bad in (object(), {"app_name": "apps_x"}, "not a record", 42, None):
        with pytest.raises(TypeError):
            write_cert_decision_record(bad, repo_root=tmp_path)  # type: ignore[arg-type]


def test_type_error_on_non_record_even_in_fail_hard(tmp_path):
    with pytest.raises(TypeError):
        write_cert_decision_record(
            object(),  # type: ignore[arg-type]
            repo_root=tmp_path,
            fail_soft=False,
        )


# ===========================================================================
# 14. Certify verdict still writes NOT_CERTIFIED.
# ===========================================================================


def test_certify_verdict_still_writes_status_after_not_certified(tmp_path):
    rec = _make_record(
        verdict=VERDICT_CERTIFY,
        failure_reasons=(),
        trace_observed_n=30,
        trace_observed_success_n=30,
        evidence_rate=1.0,
        wilson_lower=0.85,
        z_score=2.5,
        uplift=0.5,
    )
    write_cert_decision_record(rec, repo_root=tmp_path)

    # Inspect the raw SQL row to prove persistence (not just the in-memory
    # record, which D.1 already enforces).
    p = ledger_path_for_app("apps_research", repo_root=tmp_path)
    conn = sqlite3.connect(str(p))
    try:
        row = conn.execute(
            "SELECT verdict, runtime_certification_status_before, "
            "runtime_certification_status_after FROM cert_decisions"
        ).fetchone()
    finally:
        conn.close()
    assert row[0] == VERDICT_CERTIFY
    assert row[1] == NOT_CERTIFIED
    assert row[2] == NOT_CERTIFIED


# ===========================================================================
# 15. SQL CHECK rejects tampered status.
# ===========================================================================


def test_sql_check_rejects_tampered_status_after(tmp_path):
    rec = _make_record()
    write_cert_decision_record(rec, repo_root=tmp_path)

    p = ledger_path_for_app("apps_research", repo_root=tmp_path)
    conn = sqlite3.connect(str(p))
    try:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "UPDATE cert_decisions "
                "SET runtime_certification_status_after = 'RUNTIME_CERTIFIED'"
            )
    finally:
        conn.close()


def test_sql_check_rejects_tampered_status_before(tmp_path):
    rec = _make_record()
    write_cert_decision_record(rec, repo_root=tmp_path)

    p = ledger_path_for_app("apps_research", repo_root=tmp_path)
    conn = sqlite3.connect(str(p))
    try:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "UPDATE cert_decisions "
                "SET runtime_certification_status_before = 'RUNTIME_CERTIFIED'"
            )
    finally:
        conn.close()


# ===========================================================================
# 16. Tampered record_json fails D.1 validation on read.
# ===========================================================================


def test_tampered_record_json_fails_d1_validation_on_read(tmp_path):
    rec = _make_record()
    write_cert_decision_record(rec, repo_root=tmp_path)

    p = ledger_path_for_app("apps_research", repo_root=tmp_path)
    # Mutate record_json to flip status_after — the SQL column still says
    # NOT_CERTIFIED (CHECK constraint), but the blob lies. D.1 hydration
    # must raise.
    tampered = rec.to_dict()
    tampered["runtime_certification_status_after"] = "RUNTIME_CERTIFIED"
    tampered_json = json.dumps(tampered, sort_keys=True)

    conn = sqlite3.connect(str(p))
    try:
        conn.execute(
            "UPDATE cert_decisions SET record_json = ? WHERE decision_id = ?",
            (tampered_json, rec.decision_id),
        )
        conn.commit()
    finally:
        conn.close()

    with pytest.raises(ValueError):
        read_cert_decision_records("apps_research", repo_root=tmp_path)


def test_tampered_decision_id_fails_hydrate(tmp_path):
    """Row-level tamper: decision_id in record_json mismatches derived hash."""
    rec = _make_record()
    write_cert_decision_record(rec, repo_root=tmp_path)
    p = ledger_path_for_app("apps_research", repo_root=tmp_path)

    tampered = rec.to_dict()
    tampered["decision_id"] = "0" * 64  # valid 64-hex but wrong value
    tampered_json = json.dumps(tampered, sort_keys=True)

    conn = sqlite3.connect(str(p))
    try:
        conn.execute(
            "UPDATE cert_decisions SET record_json = ?",
            (tampered_json,),
        )
        conn.commit()
    finally:
        conn.close()

    with pytest.raises(ValueError, match="decision_id"):
        read_cert_decision_records("apps_research", repo_root=tmp_path)


# ===========================================================================
# 17. No scanner/CI/emitter imports.
# ===========================================================================


def test_no_scanner_ci_emitter_imports():
    # Fresh import and check the module's transitive imports.
    mod = importlib.import_module(
        "tools.runtime_cert.decisions.cert_decision_ledger"
    )
    # Inspect every module directly imported (via getattr on the module's __dict__).
    module_set = {
        getattr(v, "__module__", None)
        for v in mod.__dict__.values()
        if hasattr(v, "__module__")
    }
    module_set.discard(None)

    forbidden = re.compile(
        r"^(agentic_core\.L\d|ops_scripts\.ci\.|tools\.spine\.scanner)"
    )
    offenders = {m for m in module_set if forbidden.match(m)}
    assert not offenders, f"forbidden imports leaked in: {sorted(offenders)}"


# ===========================================================================
# 18. CertDecisionLedgerWriteResult invariants.
# ===========================================================================


def test_write_result_enforces_exactly_one_flag_true(tmp_path):
    path = ledger_path_for_app("apps_research", repo_root=tmp_path)
    decision_id = compute_decision_id("apps_research", MANIFEST_A, CLOSEOUT_HASH)

    # Valid combinations.
    CertDecisionLedgerWriteResult(
        app_name="apps_research",
        ledger_path=path,
        decision_id=decision_id,
        written=True,
    )
    CertDecisionLedgerWriteResult(
        app_name="apps_research",
        ledger_path=path,
        decision_id=decision_id,
        already_exists=True,
    )
    CertDecisionLedgerWriteResult(
        app_name="apps_research",
        ledger_path=path,
        decision_id=decision_id,
        skipped=True,
        error="some error",
    )

    # Invalid: zero flags True.
    with pytest.raises(ValueError, match="exactly one"):
        CertDecisionLedgerWriteResult(
            app_name="apps_research",
            ledger_path=path,
            decision_id=decision_id,
        )
    # Invalid: two flags True.
    with pytest.raises(ValueError, match="exactly one"):
        CertDecisionLedgerWriteResult(
            app_name="apps_research",
            ledger_path=path,
            decision_id=decision_id,
            written=True,
            already_exists=True,
        )
    # Invalid: three flags True.
    with pytest.raises(ValueError, match="exactly one"):
        CertDecisionLedgerWriteResult(
            app_name="apps_research",
            ledger_path=path,
            decision_id=decision_id,
            written=True,
            already_exists=True,
            skipped=True,
            error="x",
        )


def test_write_result_requires_apps_prefix(tmp_path):
    path = ledger_path_for_app("apps_research", repo_root=tmp_path)
    decision_id = compute_decision_id("apps_research", MANIFEST_A, CLOSEOUT_HASH)
    with pytest.raises(ValueError, match="apps_"):
        CertDecisionLedgerWriteResult(
            app_name="research",
            ledger_path=path,
            decision_id=decision_id,
            written=True,
        )


def test_write_result_requires_non_empty_decision_id(tmp_path):
    path = ledger_path_for_app("apps_research", repo_root=tmp_path)
    with pytest.raises(ValueError, match="decision_id"):
        CertDecisionLedgerWriteResult(
            app_name="apps_research",
            ledger_path=path,
            decision_id="",
            written=True,
        )


def test_write_result_requires_error_when_skipped(tmp_path):
    path = ledger_path_for_app("apps_research", repo_root=tmp_path)
    decision_id = compute_decision_id("apps_research", MANIFEST_A, CLOSEOUT_HASH)
    with pytest.raises(ValueError, match="error"):
        CertDecisionLedgerWriteResult(
            app_name="apps_research",
            ledger_path=path,
            decision_id=decision_id,
            skipped=True,
            error=None,
        )


def test_write_result_forbids_error_when_not_skipped(tmp_path):
    path = ledger_path_for_app("apps_research", repo_root=tmp_path)
    decision_id = compute_decision_id("apps_research", MANIFEST_A, CLOSEOUT_HASH)
    with pytest.raises(ValueError, match="error"):
        CertDecisionLedgerWriteResult(
            app_name="apps_research",
            ledger_path=path,
            decision_id=decision_id,
            written=True,
            error="unexpected",
        )


# ===========================================================================
# 19. failure_reasons_json and record_json shape checks.
# ===========================================================================


def test_failure_reasons_json_is_a_json_list(tmp_path):
    rec = _make_record(
        failure_reasons=("SAMPLE_SIZE_TOO_SMALL", "WILSON_BELOW_THRESHOLD")
    )
    write_cert_decision_record(rec, repo_root=tmp_path)
    p = ledger_path_for_app("apps_research", repo_root=tmp_path)
    conn = sqlite3.connect(str(p))
    try:
        (blob,) = conn.execute(
            "SELECT failure_reasons_json FROM cert_decisions"
        ).fetchone()
    finally:
        conn.close()
    parsed = json.loads(blob)
    assert isinstance(parsed, list)
    assert parsed == ["SAMPLE_SIZE_TOO_SMALL", "WILSON_BELOW_THRESHOLD"]


def test_failure_reasons_json_empty_for_certify(tmp_path):
    rec = _make_record(verdict=VERDICT_CERTIFY, failure_reasons=())
    write_cert_decision_record(rec, repo_root=tmp_path)
    p = ledger_path_for_app("apps_research", repo_root=tmp_path)
    conn = sqlite3.connect(str(p))
    try:
        (blob,) = conn.execute(
            "SELECT failure_reasons_json FROM cert_decisions"
        ).fetchone()
    finally:
        conn.close()
    assert json.loads(blob) == []


def test_record_json_is_full_json_object(tmp_path):
    rec = _make_record()
    write_cert_decision_record(rec, repo_root=tmp_path)
    p = ledger_path_for_app("apps_research", repo_root=tmp_path)
    conn = sqlite3.connect(str(p))
    try:
        (blob,) = conn.execute("SELECT record_json FROM cert_decisions").fetchone()
    finally:
        conn.close()
    parsed = json.loads(blob)
    assert isinstance(parsed, dict)
    # All 19 D.1 record fields present.
    expected_keys = {
        "decision_id",
        "generated_at_utc",
        "app_name",
        "route_shape",
        "manifest_hash",
        "evidence_kind",
        "closeout_report_id",
        "closeout_report_hash",
        "trace_observed_n",
        "trace_observed_success_n",
        "evidence_rate",
        "wilson_lower",
        "z_score",
        "uplift",
        "verdict",
        "failure_reasons",
        "next_review_utc",
        "runtime_certification_status_before",
        "runtime_certification_status_after",
    }
    assert expected_keys.issubset(set(parsed.keys()))
    assert parsed["runtime_certification_status_after"] == NOT_CERTIFIED


# ===========================================================================
# 20. Multi-app isolation.
# ===========================================================================


def test_multiple_apps_write_to_separate_files(tmp_path):
    rec_a = _make_record(app_name="apps_research")
    rec_b = _make_record(app_name="apps_eval", route_shape="evaluator_only",
                         evidence_kind="formal_exception")
    write_cert_decision_record(rec_a, repo_root=tmp_path)
    write_cert_decision_record(rec_b, repo_root=tmp_path)

    path_a = ledger_path_for_app("apps_research", repo_root=tmp_path)
    path_b = ledger_path_for_app("apps_eval", repo_root=tmp_path)
    assert path_a != path_b
    assert path_a.exists()
    assert path_b.exists()

    # Cross-app read isolation.
    assert len(read_cert_decision_records("apps_research", repo_root=tmp_path)) == 1
    assert len(read_cert_decision_records("apps_eval", repo_root=tmp_path)) == 1
    assert read_cert_decision_records("apps_research", repo_root=tmp_path)[0].app_name == "apps_research"
    assert read_cert_decision_records("apps_eval", repo_root=tmp_path)[0].app_name == "apps_eval"


# ===========================================================================
# 21. DDL not in LEDGER_REGISTRY.
# ===========================================================================


def test_ddl_not_registered_in_ledger_registry():
    from tools.ledgers.schema_registry import LEDGER_REGISTRY

    schema_files = {spec.schema_file for spec in LEDGER_REGISTRY}
    ledger_names = {spec.name for spec in LEDGER_REGISTRY}
    assert "cert_decision_ledger.schema.sql" not in schema_files
    assert "cert_decision" not in ledger_names
    # Also no cert_decision_<app_name> ghost entry.
    assert not any(n.startswith("cert_decision_") for n in ledger_names)


# ===========================================================================
# Extra: concurrent writes serialized via lock.
# ===========================================================================


def test_concurrent_writes_serialized(tmp_path):
    records = [
        _make_record(
            manifest_hash=_h(f"concurrent-{i}"),
            closeout_report_hash=_h(f"concurrent-c-{i}"),
        )
        for i in range(5)
    ]

    errors = []

    def _worker(rec):
        try:
            write_cert_decision_record(rec, repo_root=tmp_path)
        except Exception as exc:  # guardian: allow-broad-exception -- thread error bubbling
            errors.append(exc)

    threads = [threading.Thread(target=_worker, args=(r,)) for r in records]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"thread errors: {errors}"
    got = read_cert_decision_records("apps_research", repo_root=tmp_path)
    assert len(got) == 5
    assert {r.decision_id for r in got} == {r.decision_id for r in records}


# ===========================================================================
# Sanity: write result frozen.
# ===========================================================================


def test_write_result_is_frozen(tmp_path):
    rec = _make_record()
    result = write_cert_decision_record(rec, repo_root=tmp_path)
    with pytest.raises(Exception):
        result.written = False  # type: ignore[misc]
