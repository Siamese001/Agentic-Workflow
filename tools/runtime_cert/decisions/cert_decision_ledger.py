"""Phase D.3 — cert-decision ledger writer (ADR-080 §11 D.3).

Per-app, append-only, idempotent-on-`decision_id` SQLite writer for
:class:`CertificationDecisionRecord` objects produced by D.2. Stdlib
only (``sqlite3``, ``json``, ``pathlib``, ``datetime``, ``threading``).
Fail-soft by default; programmer errors (``TypeError`` / ``ValueError``)
always raise.

Plan: ``docs/archive/windsurf/legacy-tree/plans/runtime-cert-d3-cert-decision-ledger-85989c.md``.

Boundaries — what D.3 DOES NOT do
---------------------------------
- No scanner classification change. Scanner never reads these files.
- No CI gate. No pre-commit hook. No workflow.
- No emitter change. Runtime-ADG span emitters are untouched.
- No runtime certification of any app. Every persisted record carries
  ``runtime_certification_status_after = NOT_CERTIFIED`` verbatim —
  enforced at two layers: D.1's ``__post_init__`` at construction time,
  and SQL ``CHECK`` constraints at persistence time.
- No ``LEDGER_REGISTRY`` registration (see ``cert_decision_ledger.schema.sql``
  header). ``tools/ledgers/apply_schema.py`` iterates the registry only
  (verified 2026-05-01) — this DDL will never be auto-applied.
- No batch / bulk API. One record per call.

Bypass: ``CERT_DECISION_LEDGER_BYPASS=1`` env var. Distinct from
``LEDGER_WRITER_BYPASS`` so router work and cert-decision work pause
independently. Bypass returns ``skipped=True, error='bypass'``.

A ``verdict == "certify"`` record is NOT a certification. Phase F owns
scanner promotion to ``RUNTIME_CERTIFIED``. Phase F is not implemented.
"""

from __future__ import annotations

# ADR-079 consumer mode declaration. D.3 does not consume the ADG;
# the tag follows the sibling-module convention in runtime_cert/ and
# is evaluated at module load by the ADR-079 gate.
__adg_consumer_mode__ = "runtime_cert_read"

import json
import os
import sqlite3
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Union

from tools.runtime_cert.decisions.cert_decision_record import (
    CertificationDecisionRecord,
    NOT_CERTIFIED,
    compute_decision_id,
)

# ---------------------------------------------------------------------------
# Module-level constants.
# ---------------------------------------------------------------------------

APP_PREFIX: str = "apps_"
LEDGER_DIR_REL: str = "artifacts/ledgers"
DDL_PATH_REL: str = ".cursor/schemas/cert_decision_ledger.schema.sql"
BYPASS_ENV_VAR: str = "CERT_DECISION_LEDGER_BYPASS"

# Repo root relative to this module: tools/runtime_cert/decisions/<this>
# -> parents[3] lands on the repo root (verified 2026-05-01).
_MODULE_PATH = Path(__file__).resolve()
_DEFAULT_REPO_ROOT: Path = _MODULE_PATH.parents[3]

# In-process lock table keyed by absolute db_path. Pattern ported from
# tools.ledgers.writer but NOT imported from it (AG-1: local writer).
_DB_LOCKS: dict[str, threading.Lock] = {}
_LOCKS_LOCK: threading.Lock = threading.Lock()


def _lock_for(db_path: Path) -> threading.Lock:
    """Return the shared lock for ``db_path``. Thread-safe lazy init."""
    key = str(db_path.resolve())
    with _LOCKS_LOCK:
        lock = _DB_LOCKS.get(key)
        if lock is None:
            lock = threading.Lock()
            _DB_LOCKS[key] = lock
        return lock


# ---------------------------------------------------------------------------
# Result dataclass.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CertDecisionLedgerWriteResult:
    """Result of one ``write_cert_decision_record`` call.

    Exactly one of ``written`` / ``already_exists`` / ``skipped`` is
    ``True``. ``error`` is non-empty iff ``skipped`` is ``True``.
    """

    app_name: str
    ledger_path: Path
    decision_id: str
    written: bool = False
    already_exists: bool = False
    skipped: bool = False
    error: Optional[str] = None
    notes: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.app_name, str) or not self.app_name.startswith(
            APP_PREFIX
        ):
            raise ValueError(
                "CertDecisionLedgerWriteResult: app_name must start with "
                f"{APP_PREFIX!r}; got {self.app_name!r}"
            )
        if not isinstance(self.decision_id, str) or not self.decision_id:
            raise ValueError(
                "CertDecisionLedgerWriteResult: decision_id must be a "
                "non-empty string"
            )
        if not isinstance(self.ledger_path, Path):
            raise ValueError(
                "CertDecisionLedgerWriteResult: ledger_path must be a "
                "pathlib.Path"
            )
        if str(self.ledger_path) == "":
            raise ValueError(
                "CertDecisionLedgerWriteResult: ledger_path must be non-empty"
            )
        flags = (bool(self.written), bool(self.already_exists), bool(self.skipped))
        if sum(flags) != 1:
            raise ValueError(
                "CertDecisionLedgerWriteResult: exactly one of "
                "(written, already_exists, skipped) must be True; got "
                f"written={self.written}, already_exists={self.already_exists}, "
                f"skipped={self.skipped}"
            )
        if self.skipped and (not isinstance(self.error, str) or not self.error):
            raise ValueError(
                "CertDecisionLedgerWriteResult: skipped=True requires a "
                "non-empty error string"
            )
        if not self.skipped and self.error not in (None, ""):
            raise ValueError(
                "CertDecisionLedgerWriteResult: error must be None when "
                "skipped=False"
            )


# ---------------------------------------------------------------------------
# Path helpers.
# ---------------------------------------------------------------------------


def _resolve_repo_root(repo_root: Union[str, Path, None]) -> Path:
    if repo_root is None:
        return _DEFAULT_REPO_ROOT
    return Path(repo_root).resolve()


def _validate_app_name(app_name: str) -> None:
    if not isinstance(app_name, str):
        raise TypeError(
            f"app_name must be str; got {type(app_name).__name__}"
        )
    if not app_name.startswith(APP_PREFIX):
        raise ValueError(
            f"app_name must start with {APP_PREFIX!r}; got {app_name!r}"
        )


def ledger_path_for_app(
    app_name: str,
    repo_root: Union[str, Path, None] = None,
) -> Path:
    """Return the canonical per-app ledger path.

    Validates ``app_name.startswith("apps_")``. Does NOT create the file
    or its parent directory. Resolves ``repo_root=None`` to the repo
    root inferred from this module's location.
    """
    _validate_app_name(app_name)
    root = _resolve_repo_root(repo_root)
    return root / LEDGER_DIR_REL / f"cert_decision_{app_name}.sqlite"


# ---------------------------------------------------------------------------
# Schema application.
# ---------------------------------------------------------------------------


def _ddl_sql() -> str:
    """Load DDL text from the repo's ``.cursor/schemas/``.

    The DDL source is installation-fixed at ``_DEFAULT_REPO_ROOT`` (the
    repo this module was imported from). The ``repo_root`` argument on
    public functions controls where ledger FILES are WRITTEN, not where
    the DDL is READ. Tests may redirect ledger output via ``repo_root``
    without needing to copy the DDL into a tmp tree.
    """
    ddl_path = _DEFAULT_REPO_ROOT / DDL_PATH_REL
    if not ddl_path.exists():
        raise FileNotFoundError(f"Cert-decision DDL not found: {ddl_path}")
    return ddl_path.read_text(encoding="utf-8")


def ensure_cert_decision_ledger(path: Union[str, Path]) -> None:
    """Create ledger file + apply DDL idempotently.

    Parent directory created if missing. All DDL statements are
    ``IF NOT EXISTS``, so repeat calls are no-ops. Does not insert rows.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    ddl = _ddl_sql()
    conn = sqlite3.connect(str(p))
    try:
        conn.executescript(ddl)
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Write.
# ---------------------------------------------------------------------------


def _iso_now_utc() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _row_tuple(
    record: CertificationDecisionRecord, inserted_at_utc: str
) -> tuple:
    failure_reasons_json = json.dumps(
        list(record.failure_reasons),
        separators=(",", ":"),
        ensure_ascii=True,
    )
    record_json = record.to_json()
    return (
        record.decision_id,
        record.generated_at_utc,
        record.app_name,
        record.route_shape,
        record.manifest_hash,
        record.evidence_kind,
        record.closeout_report_id,
        record.closeout_report_hash,
        record.trace_observed_n,
        record.trace_observed_success_n,
        record.evidence_rate,
        record.wilson_lower,
        record.z_score,
        record.uplift,
        record.verdict,
        failure_reasons_json,
        record.next_review_utc,
        record.runtime_certification_status_before,
        record.runtime_certification_status_after,
        record_json,
        inserted_at_utc,
    )


_INSERT_SQL = (
    "INSERT OR IGNORE INTO cert_decisions ("
    "decision_id, generated_at_utc, app_name, route_shape, manifest_hash, "
    "evidence_kind, closeout_report_id, closeout_report_hash, "
    "trace_observed_n, trace_observed_success_n, evidence_rate, "
    "wilson_lower, z_score, uplift, verdict, failure_reasons_json, "
    "next_review_utc, runtime_certification_status_before, "
    "runtime_certification_status_after, record_json, inserted_at_utc"
    ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
)


def write_cert_decision_record(
    record: CertificationDecisionRecord,
    *,
    repo_root: Union[str, Path, None] = None,
    fail_soft: bool = True,
) -> CertDecisionLedgerWriteResult:
    """Persist one record. Idempotent on ``record.decision_id``.

    Behaviour matrix:

    ======================================  =======  ===============  =======  ============
    Situation                                written  already_exists  skipped  error
    ======================================  =======  ===============  =======  ============
    new ``decision_id``                      True     False            False    None
    existing ``decision_id``                 False    True             False    None
    ``sqlite3.Error`` + ``fail_soft=True``   False    False            True     ``str(exc)``
    ``sqlite3.Error`` + ``fail_soft=False``  (raise)                            (raise)
    ``CERT_DECISION_LEDGER_BYPASS=1``        False    False            True     "bypass"
    ======================================  =======  ===============  =======  ============

    ``TypeError`` on non-record input is always raised regardless of
    ``fail_soft`` (programmer error, not an operational failure).
    """
    if not isinstance(record, CertificationDecisionRecord):
        raise TypeError(
            "write_cert_decision_record: record must be "
            "CertificationDecisionRecord; got "
            f"{type(record).__name__}"
        )

    # Validate app_name shape up-front (fail-hard — programmer error).
    _validate_app_name(record.app_name)

    path = ledger_path_for_app(record.app_name, repo_root=repo_root)

    # Bypass short-circuit — no DB touch at all.
    if os.environ.get(BYPASS_ENV_VAR) == "1":
        return CertDecisionLedgerWriteResult(
            app_name=record.app_name,
            ledger_path=path,
            decision_id=record.decision_id,
            skipped=True,
            error="bypass",
            notes=f"{BYPASS_ENV_VAR}=1 set; no write attempted",
        )

    # Operational path. sqlite3.Error is the only class absorbed in
    # fail-soft mode; everything else (FileNotFoundError on DDL, etc.)
    # re-raises — those are environment / programmer errors, not
    # transient DB failures.
    try:
        ensure_cert_decision_ledger(path)
        row = _row_tuple(record, _iso_now_utc())
        with _lock_for(path):
            conn = sqlite3.connect(str(path), isolation_level=None)
            try:
                conn.execute("BEGIN IMMEDIATE")
                try:
                    conn.execute(_INSERT_SQL, row)
                    inserted = conn.total_changes > 0
                    conn.execute("COMMIT")
                except sqlite3.Error:
                    conn.execute("ROLLBACK")
                    raise
            finally:
                conn.close()
    except sqlite3.Error as exc:
        if fail_soft:
            return CertDecisionLedgerWriteResult(
                app_name=record.app_name,
                ledger_path=path,
                decision_id=record.decision_id,
                skipped=True,
                error=str(exc),
                notes="sqlite3.Error absorbed in fail-soft mode",
            )
        # guardian: allow-raise -- fail_soft=False explicitly opts in
        raise

    if inserted:
        return CertDecisionLedgerWriteResult(
            app_name=record.app_name,
            ledger_path=path,
            decision_id=record.decision_id,
            written=True,
            notes="new row inserted",
        )
    return CertDecisionLedgerWriteResult(
        app_name=record.app_name,
        ledger_path=path,
        decision_id=record.decision_id,
        already_exists=True,
        notes="decision_id already present; INSERT OR IGNORE no-op",
    )


# ---------------------------------------------------------------------------
# Read.
# ---------------------------------------------------------------------------

_SELECT_SQL = (
    "SELECT record_json FROM cert_decisions "
    "ORDER BY generated_at_utc ASC, decision_id ASC"
)


def _hydrate_one(record_json: str) -> CertificationDecisionRecord:
    """Rebuild a record from its persisted JSON. Re-validates via D.1.

    Raises ``ValueError`` when the JSON is corrupt, fails D.1
    ``__post_init__`` invariants, or carries a ``decision_id`` that does
    not match ``compute_decision_id((app, manifest, closeout_hash))`` —
    i.e. the row was tampered with at the SQL layer or the record_json
    blob was mutated.
    """
    try:
        d = json.loads(record_json)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"cert_decision ledger row: record_json is not valid JSON: {exc}"
        ) from exc

    if not isinstance(d, dict):
        raise ValueError(
            "cert_decision ledger row: record_json must be a JSON object"
        )

    # failure_reasons round-trips as list → convert to tuple for dataclass.
    failure_reasons = tuple(d.get("failure_reasons", ()))

    try:
        record = CertificationDecisionRecord(
            decision_id=d["decision_id"],
            generated_at_utc=d["generated_at_utc"],
            app_name=d["app_name"],
            route_shape=d["route_shape"],
            manifest_hash=d["manifest_hash"],
            evidence_kind=d["evidence_kind"],
            closeout_report_id=d["closeout_report_id"],
            closeout_report_hash=d["closeout_report_hash"],
            trace_observed_n=d["trace_observed_n"],
            trace_observed_success_n=d["trace_observed_success_n"],
            evidence_rate=d["evidence_rate"],
            wilson_lower=d["wilson_lower"],
            z_score=d["z_score"],
            uplift=d["uplift"],
            verdict=d["verdict"],
            failure_reasons=failure_reasons,
            next_review_utc=d["next_review_utc"],
            runtime_certification_status_before=d[
                "runtime_certification_status_before"
            ],
            runtime_certification_status_after=d[
                "runtime_certification_status_after"
            ],
        )
    except KeyError as exc:
        raise ValueError(
            f"cert_decision ledger row: record_json missing key {exc}"
        ) from exc

    # Tamper check: decision_id must be derivable from the three-field tuple.
    expected = compute_decision_id(
        record.app_name, record.manifest_hash, record.closeout_report_hash
    )
    if record.decision_id != expected:
        raise ValueError(
            "cert_decision ledger row: decision_id does not match "
            "compute_decision_id(app_name, manifest_hash, "
            "closeout_report_hash) — row tampered with or written by an "
            "incompatible D.1 version"
        )

    # Status double-check at the read layer too (belt-and-suspenders with
    # D.1's __post_init__, which already enforced both values).
    if (
        record.runtime_certification_status_before != NOT_CERTIFIED
        or record.runtime_certification_status_after != NOT_CERTIFIED
    ):
        raise ValueError(
            "cert_decision ledger row: runtime_certification_status must "
            f"be {NOT_CERTIFIED!r} on both sides"
        )

    return record


def read_cert_decision_records(
    app_name: str,
    *,
    repo_root: Union[str, Path, None] = None,
) -> tuple[CertificationDecisionRecord, ...]:
    """Read back all records for ``app_name``.

    Ordered by ``generated_at_utc`` ASC, tie-broken by ``decision_id``.
    Returns empty tuple if the ledger file does not exist. Raises
    ``ValueError`` on row-level tampering (via :func:`_hydrate_one`).
    """
    _validate_app_name(app_name)
    path = ledger_path_for_app(app_name, repo_root=repo_root)
    if not path.exists():
        return ()

    with _lock_for(path):
        conn = sqlite3.connect(str(path))
        try:
            rows = conn.execute(_SELECT_SQL).fetchall()
        finally:
            conn.close()

    return tuple(_hydrate_one(r[0]) for r in rows)


__all__ = [
    "APP_PREFIX",
    "LEDGER_DIR_REL",
    "DDL_PATH_REL",
    "BYPASS_ENV_VAR",
    "CertDecisionLedgerWriteResult",
    "ledger_path_for_app",
    "ensure_cert_decision_ledger",
    "write_cert_decision_record",
    "read_cert_decision_records",
]
