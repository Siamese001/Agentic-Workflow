---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\runtime-cert-d3-cert-decision-ledger-85989c.md'
original_relative_path: '_archive\\2026-05\\runtime-cert-d3-cert-decision-ledger-85989c.md'
source_sha256: efbdf020a4801516c21adfb920a172fb93565d06f4bb9670c1e7dfd9321d4fac
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Runtime Cert — Phase D.3 Cert-Decision Ledger Writer (Planning Only)

- **Plan ID**: `runtime-cert-d3-cert-decision-ledger-85989c`
- **Status**: Planning — Author-Gate pending
- **Authored**: 2026-05-01
- **ADR anchor**: [ADR-080 §6 + §11 D.3](../../docs/architecture/adr/ADR-080-runtime-cert-phase-d-planning.md)
- **Predecessors (shipped)**:
  - D.1 schema — commit `193ab15cd5` (clean commit)
  - D.2 evaluator — committed under an attribution anomaly; see §3 below

> **Planning pass only.** This file authorizes **no** Python code, **no**
> SQLite creation, **no** ledger files on disk, **no** scanner edits, **no**
> CI gates, **no** emitter changes, **no** app behavior changes, and **no**
> certification claim. D.3 implementation begins only after a separate
> Author-Gate approves this plan. `runtime_certification_status` for every
> app remains `NOT_CERTIFIED` throughout and after this plan.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| D3.W1 | D3.P1 | Author-Gate approval of this plan | ~1 200 | ADR-080 §11 permits per-sub-phase gating | Pending | User approves one of AG options in §11 |
| D3.W2 | D3.P2, D3.P3 | DDL + writer module + ≥16 unit tests | ~9 000 | D.1/D.2 stable; existing ledger helper NOT reused (see §6) | Blocked on D3.W1 | Module under `tools/runtime_cert/decisions/cert_decision_ledger.py`, DDL file under `.cursor/schemas/`, tests use `tmp_path` exclusively |
| D3.W3 | D3.P4 | Minimal doc updates: ADR-080 §11 ✅ D.3, binding matrix footnote | ~700 | D3.W2 merged | Blocked on D3.W2 | ADR row marked ✅; §14 disclaimer preserved verbatim |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---:|---|---|
| D3.P1 | Author-Gate approval | This plan file | Five trade-offs in §11 need explicit sign-off | ~1 200 | Pending |
| D3.P2 | DDL + ensure-ledger helper | `.cursor/schemas/cert_decision_<app>.schema.sql` (template), `cert_decision_ledger.py::ensure_cert_decision_ledger()` | First use of per-app SQLite file pattern in this repo; must not clash with `.cursor/schemas/` conventions for LEDGER_REGISTRY | ~3 000 | Blocked |
| D3.P3 | Writer + reader + result object + tests | `cert_decision_ledger.py` full surface + `test_cert_decision_ledger.py` | Idempotency on `decision_id`; fail-soft vs. fail-hard toggle; `tmp_path`-only tests; no scanner/CI coupling | ~6 000 | Blocked |
| D3.P4 | Doc updates | ADR-080 §11, binding matrix footnote | Preserve §14 disclaimer verbatim | ~700 | Blocked |

---

## 1. Purpose and Non-Goals

### Purpose

Plan a **pure, local, stdlib-only SQLite writer** that persists
`CertificationDecisionRecord` objects (from D.1, produced by D.2) to a
per-app ledger file, append-only, idempotent on `decision_id`, fail-soft
by default. Provide matching read-back for auditors and for future D.5
calibration.

### Non-goals

- **No scanner `runtime_mode` change.** The scanner never reads these
  ledgers in Phase D.
- **No CI gate.** No pre-commit hook, no workflow, no check-script.
- **No emitter change.** Runtime-ADG span emitters are untouched.
- **No certification promotion.** Even when `record.verdict == "certify"`,
  the writer persists `runtime_certification_status_after = NOT_CERTIFIED`
  verbatim. Promotion is Phase F (explicitly out of scope).
- **No `CertificationDecisionRecord` schema change.** D.3 writes what D.1
  produces; it does not re-shape the record.
- **No batch / bulk API.** One record per call in D.3. A batch helper
  (if needed) is a D.5+ concern.
- **No cross-app aggregation.** The per-app file pattern preserves
  isolation; aggregation is the analyst's job.

---

## 2. Files Inspected

| Path | Purpose | Relevance to D.3 |
|---|---|---|
| `tools/ledgers/hook_helpers.py` | `emit_ledger_event(...)` convenience wrapper | **Unsuitable**; see §6 |
| `tools/ledgers/writer.py` | Thread-safe idempotent row writer with bypass env | **Unsuitable**; schema-fixed to router/event shape |
| `tools/ledgers/schema_registry.py` | `LEDGER_REGISTRY` central mapping of ledger name → single SQLite file | **Unsuitable**; does not support per-app file pattern |
| `tools/ledgers/apply_schema.py` | Migrator that applies every DDL in one pass | Not reused; D.3's DDL lives adjacent to the writer |
| `tools/ledgers/consulter.py` | Read surface for registered ledgers | Reference only; D.3 ships its own read helper |
| `tools/runtime_cert/decisions/cert_decision_record.py` (D.1) | Frozen dataclass + `compute_decision_id` + `to_dict` / `to_json` | **Canonical input shape** |
| `tools/runtime_cert/decisions/cert_decision_evaluator.py` (D.2) | `evaluate_phase_c_closeout` producing tuples of records | **Upstream producer** — dictates D.3 input volume (one per app per closeout) |
| `docs/architecture/adr/ADR-080-runtime-cert-phase-d-planning.md` §6 | Ledger design + unique-index guidance | **Authoritative spec** |
| `artifacts/ledgers/*.sqlite` | Existing ledger files (router_l2_cascade, router_l6_promo, etc.) | Confirms per-ledger-per-file convention; D.3 uses per-app variant |

---

## 3. Attribution Anomaly — Audit Note

**D.2 files landed inside unrelated commit `9a51a4dfa9`** titled *"hygiene:
fix 18 HIGH violations — collapse getattr to inline, use
allow-broad-exception"*. The file contents are correct (104 D.1+D.2 tests
pass against the committed SHA; verified 2026-05-01) but the commit
message does not describe D.2. Root cause: a concurrent automated
hygiene-sweep process committed between `git add` and `git commit` in the
D.2 landing turn, stuffing the three D.2 files into its commit alongside
26 unrelated hygiene changes.

**Decision**: history was NOT rewritten. Rewriting via `reset --soft` +
`amend` would have orphaned the legitimate hygiene work across
`graph_aware_router.py`, `integrated_safe_reuse_run.py`, certification
reports, etc. The attribution issue is cosmetic; the audit trail is
intact via `git show --stat 9a51a4dfa9`.

**Action for this plan**: the D.3 landing MUST use an explicit staged
commit sequence with no background processes running (hygiene sweeps
paused, pre-commit hooks audited for concurrent-write behavior) to
prevent a repeat. If the commit race cannot be eliminated, D.3 files
will be committed via `--only` on explicit paths to forbid the inclusion
of unrelated working-tree changes.

This anomaly is recorded here so future auditors reading
`git log --oneline --grep="Phase D"` understand why D.2 does not appear
under a D.2-titled commit.

---

## 4. Inputs and Outputs

### Input — `CertificationDecisionRecord`

One record per `write_cert_decision_record()` call. Produced upstream by
D.2's `evaluate_phase_c_closeout()`. Every record carries
`runtime_certification_status_before == runtime_certification_status_after
== NOT_CERTIFIED` (enforced structurally by D.1's `__post_init__`).

### Output — `CertDecisionLedgerWriteResult` (new dataclass, D.3-local)

```python
@dataclass(frozen=True)
class CertDecisionLedgerWriteResult:
    app_name: str
    ledger_path: Path
    decision_id: str
    written: bool         # True iff a new row was inserted
    already_exists: bool  # True iff decision_id already persisted
    skipped: bool         # True iff fail_soft=True absorbed a SQLite error
    error: Optional[str]  # string form of any suppressed exception
    notes: str            # human-readable detail (deterministic)
```

**Invariant**: exactly one of `{written, already_exists, skipped}` is
`True`; `error` is non-empty iff `skipped` is `True`.

### Side effect

One SQLite file written per app, at:
```
artifacts/ledgers/cert_decision_<app_name>.sqlite
```

The file is created on first write; subsequent writes open-and-append.
**Never read by the scanner.** **Never read by any runtime emitter.**

---

## 5. Proposed Target File

```
tools/runtime_cert/decisions/cert_decision_ledger.py
```

Sibling to D.1 (`cert_decision_record.py`) and D.2
(`cert_decision_evaluator.py`). Package `__init__.py` already exists.

Tests:
```
tests/unit/tools/runtime_cert/decisions/test_cert_decision_ledger.py
```

DDL file (new):
```
.cursor/schemas/cert_decision_ledger.schema.sql
```

The DDL lives under `.cursor/schemas/` to match the repo-wide
convention established by `tools/ledgers/schema_registry.py`, **but is
NOT registered in `LEDGER_REGISTRY`** — see §6 for why.

All three paths respect constitutional §31 (SSOT folder routing).

---

## 6. Existing Ledger Helper — Reuse Declined

**Recommendation: do NOT reuse `tools.ledgers.hook_helpers.emit_ledger_event`
or `tools.ledgers.writer.writer_for(...)`. Ship a local SQLite writer
in `cert_decision_ledger.py` with the reasons documented below.**

Plan §5 of the task permits local writer when the existing helper
distorts the schema. It does.

### Why the existing helper does not fit

| Dimension | Existing `tools.ledgers.writer` | D.3 requirement | Gap |
|---|---|---|---|
| **Schema shape** | Flat audit-event row: `event_kind`, `prediction_json`, `outcome_json`, `score_band`, `latency_ms`, `metadata_json` | Typed domain row: 20 explicit columns (19 record fields + `inserted_at_utc`) | Force-fit would push the entire `CertificationDecisionRecord` into `prediction_json`, losing typed columns for `app_name`, `manifest_hash`, `evidence_rate`, `wilson_lower`, `z_score`, `verdict`, etc. |
| **Indexes** | No per-column indexes defined on the audit row | Plan §4: index on `(app_name, manifest_hash)`, `closeout_report_hash`, `generated_at_utc` | Would have to be added out-of-band or emulated via JSON-scans — unacceptable at D.5 calibration scale |
| **Idempotency key** | SHA-256 of `event_kind + ts + repo_area + prediction_json` | `decision_id` — deterministic SHA-256 over `(app_name, manifest_hash, closeout_report_hash)` from D.1 | Two incompatible idempotency keys; a record rewritten from an iterator that re-serializes JSON differently (field order, whitespace) would NOT dedupe |
| **File layout** | Single SQLite per ledger name: `artifacts/ledgers/<name>.sqlite` via `LEDGER_REGISTRY` | Per-app file: `artifacts/ledgers/cert_decision_<app_name>.sqlite` (ADR-080 §6) | `LEDGER_REGISTRY` hard-codes name→path; adding N apps would require N registry entries and N schema files, creating maintenance burden and breaking the ADR's per-app boundary |
| **Registry coupling** | Every registered ledger appears in the CI coverage check, calibration poller, consulter skill registry, fleet health reports | D.3 is **non-promoting domain data**, not an intelligence ledger; adding it to `LEDGER_REGISTRY` conflates two concerns | Registry was built for §29 closed-loop router enforcement; cert-decisions are orthogonal |
| **Writer layer** | Part of `tools/ledgers/`; writer-hook field in `LedgerSpec` points at Windsurf hook scripts | D.3 writer is called from analyst tooling (evaluator output persistence), not a Windsurf hook | No Windsurf hook invokes D.3 in Phase D — the registry's `writer_hook` field would be empty or fabricated |

### Benefits of the local writer

- **Typed SQL**: explicit columns → Python dataclass round-trip with no JSON-blob shuffling.
- **Independent bypass**: `CERT_DECISION_LEDGER_BYPASS=1` env var, distinct from `LEDGER_WRITER_BYPASS` so router work and cert-decision work can be paused independently.
- **No registry footprint**: not listed in `LEDGER_REGISTRY`, so CI gates that sweep "every registered ledger" do not inadvertently touch cert-decision files. Alignment with ADR-050 (intelligence ledger family) is preserved by keeping cert-decisions explicitly out of it.
- **Stdlib-only**: `sqlite3`, `json`, `pathlib`, `datetime` — identical dependency footprint to the existing writer without carrying the audit-event schema.

### Shared disciplines (ported verbatim)

D.3 WILL inherit these disciplines from `tools.ledgers.writer` via
**patterned imitation** (not import):

- Threading lock keyed on `db_path` to serialize concurrent writes in-process
- `LEDGER_WRITER_BYPASS`-style env var (`CERT_DECISION_LEDGER_BYPASS`) for scripted batch runs
- `sqlite3.Error`-only catch in fail-soft path (never bare `except Exception`)
- Timestamps in ISO-8601 UTC with milliseconds
- `sqlite3` connection parameters: `isolation_level=None` (autocommit) with explicit `BEGIN` / `COMMIT` per write

---

## 7. Ledger Schema (DDL)

File: `.cursor/schemas/cert_decision_ledger.schema.sql`

```sql
-- Phase D.3 cert-decision ledger. Per-app SQLite file. Append-only.
-- NEVER read by scanner. NEVER read by runtime emitter. Persists Phase D
-- certification DECISIONS, not certifications. Every row carries
-- runtime_certification_status_after = NOT_CERTIFIED by structural
-- invariant of the D.1 schema.
CREATE TABLE IF NOT EXISTS cert_decisions (
    decision_id                          TEXT    PRIMARY KEY,
    generated_at_utc                     TEXT    NOT NULL,
    app_name                             TEXT    NOT NULL,
    route_shape                          TEXT    NOT NULL,
    manifest_hash                        TEXT    NOT NULL,
    evidence_kind                        TEXT    NOT NULL,
    closeout_report_id                   TEXT    NOT NULL,
    closeout_report_hash                 TEXT    NOT NULL,
    trace_observed_n                     INTEGER NOT NULL,
    trace_observed_success_n             INTEGER NOT NULL,
    evidence_rate                        REAL    NOT NULL,
    wilson_lower                         REAL    NOT NULL,
    z_score                              REAL    NOT NULL,
    uplift                               REAL    NOT NULL,
    verdict                              TEXT    NOT NULL,
    failure_reasons_json                 TEXT    NOT NULL,
    next_review_utc                      TEXT    NOT NULL,
    runtime_certification_status_before  TEXT    NOT NULL CHECK (runtime_certification_status_before = 'NOT_CERTIFIED'),
    runtime_certification_status_after   TEXT    NOT NULL CHECK (runtime_certification_status_after  = 'NOT_CERTIFIED'),
    record_json                          TEXT    NOT NULL,
    inserted_at_utc                      TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cert_decisions_app_manifest
    ON cert_decisions (app_name, manifest_hash);
CREATE INDEX IF NOT EXISTS idx_cert_decisions_closeout_hash
    ON cert_decisions (closeout_report_hash);
CREATE INDEX IF NOT EXISTS idx_cert_decisions_generated_at
    ON cert_decisions (generated_at_utc);
```

Notes:

- SQLite `CHECK` constraints enforce `NOT_CERTIFIED` at the **persistence**
  layer in addition to the D.1 `__post_init__` enforcement at the
  **construction** layer. Belt-and-suspenders; if D.1 ever evolves, the
  ledger remains honest.
- `record_json` is the full `record.to_json()` verbatim, so future
  schema evolutions can re-hydrate old rows via D.1's deserialiser.
- `failure_reasons_json` is the tuple rendered as a JSON list for
  queryability (SQLite 3.38+ `->>` operator).
- No foreign keys (per-app file pattern makes them pointless).
- No triggers — all invariants are enforced by `CHECK` or by D.1.

---

## 8. Public API (to be implemented in D.3)

```python
# tools/runtime_cert/decisions/cert_decision_ledger.py

from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from tools.runtime_cert.decisions.cert_decision_record import (
    CertificationDecisionRecord,
)


APP_PREFIX = "apps_"


def ledger_path_for_app(
    app_name: str,
    repo_root: Optional[str | Path] = None,
) -> Path:
    """Return the canonical ledger path. Validates app_name starts with 'apps_'.

    Raises ValueError if app_name does not start with 'apps_'. Does NOT
    create the file.
    """


def ensure_cert_decision_ledger(path: str | Path) -> None:
    """Apply the DDL idempotently. Creates parent dirs.

    Reads .cursor/schemas/cert_decision_ledger.schema.sql and executes
    it. Safe to call repeatedly (all statements are IF NOT EXISTS).
    """


@dataclass(frozen=True)
class CertDecisionLedgerWriteResult:
    app_name: str
    ledger_path: Path
    decision_id: str
    written: bool
    already_exists: bool
    skipped: bool
    error: Optional[str]
    notes: str


def write_cert_decision_record(
    record: CertificationDecisionRecord,
    *,
    repo_root: Optional[str | Path] = None,
    fail_soft: bool = True,
) -> CertDecisionLedgerWriteResult:
    """Persist one record. Idempotent on record.decision_id.

    Behavior matrix:
      | Situation                             | written | already_exists | skipped | error       |
      | ---                                   | ---     | ---            | ---     | ---         |
      | new decision_id                       | True    | False          | False   | None        |
      | existing decision_id                  | False   | True           | False   | None        |
      | sqlite3.Error + fail_soft=True        | False   | False          | True    | str(exc)    |
      | sqlite3.Error + fail_soft=False       | (raise) |                |         |             |
      | CERT_DECISION_LEDGER_BYPASS=1         | False   | False          | True    | "bypass"    |

    TypeError on non-record input (programmer error; fail_soft does NOT
    absorb this).
    """


def read_cert_decision_records(
    app_name: str,
    *,
    repo_root: Optional[str | Path] = None,
) -> tuple[CertificationDecisionRecord, ...]:
    """Read back all records for an app, ordered by inserted_at_utc ASC.

    Returns empty tuple when the ledger file does not exist. Never
    raises on a missing file — raises only on corrupt SQLite.
    Round-trips via record.to_json() + reconstruction (defensive validate).
    """
```

---

## 9. Write & Read Algorithm

### Write

```
ensure_cert_decision_ledger(ledger_path_for_app(record.app_name))
with sqlite3.connect(path, isolation_level=None) as conn:
    with _lock_for(path):  # in-process serialization
        conn.execute("BEGIN")
        try:
            conn.execute(
                "INSERT OR IGNORE INTO cert_decisions (...) VALUES (...)",
                row_tuple,
            )
            if conn.total_changes == 0:
                conn.execute("COMMIT")
                return Result(already_exists=True, ...)
            conn.execute("COMMIT")
            return Result(written=True, ...)
        except sqlite3.Error as exc:
            conn.execute("ROLLBACK")
            if fail_soft:
                return Result(skipped=True, error=str(exc), ...)
            raise
```

Notes:

- `INSERT OR IGNORE` + `total_changes == 0` is the canonical SQLite
  idempotency pattern on a `PRIMARY KEY`. No need for a prior `SELECT`.
- Threading lock keyed on absolute `path` string; module-level dict
  pattern ported from `tools.ledgers.writer`.
- `BEGIN` + explicit `COMMIT` / `ROLLBACK` despite `isolation_level=None`
  — explicit transactions guard against partial writes under concurrent
  pressure.

### Read

```
if not path.exists():
    return ()
with sqlite3.connect(path) as conn:
    rows = conn.execute(
        "SELECT record_json FROM cert_decisions ORDER BY inserted_at_utc ASC"
    ).fetchall()
records = []
for (blob,) in rows:
    d = json.loads(blob)
    records.append(_from_dict(d))   # validates via D.1 __post_init__
return tuple(records)
```

`_from_dict` uses `make_certification_decision_record` from D.1 after
converting `failure_reasons` list back to tuple. Validation is thus
structurally re-enforced on read, so any row corrupted at the SQL
layer (e.g. someone manually ran `UPDATE cert_decisions SET
runtime_certification_status_after = 'RUNTIME_CERTIFIED'`) is caught
on readback via the D.1 invariant — the ledger cannot silently carry
a promoted status even if the SQLite file is tampered with, because
the CHECK constraint + D.1 constructor form a two-layer guard.

---

## 10. Fail-Soft Semantics (Plan §3 recommendation)

### `fail_soft=True` (default)

- `sqlite3.Error` (operational failures: disk full, locked DB, schema
  mismatch) → return `Result(skipped=True, error=str(exc), notes=...)`
- `CERT_DECISION_LEDGER_BYPASS=1` env var → return
  `Result(skipped=True, error="bypass", notes="CERT_DECISION_LEDGER_BYPASS set")`
- All other exceptions (ImportError, OSError, JSONDecodeError) → **still
  re-raise** — these are programmer / environment errors, not
  operational DB failures, and fail-soft would hide bugs.

### `fail_soft=False`

- `sqlite3.Error` → re-raise verbatim
- `TypeError` on non-record input → re-raise (programmer error)
- `ValueError` on app_name validation → re-raise

### Invariants across both modes

- `TypeError` on non-`CertificationDecisionRecord` input → always raised
  (never absorbed)
- Pre-write `app_name` validation (`startswith("apps_")`) → always raised
  (never absorbed)
- Successful new insert and idempotent already-exists paths → never
  raise; always return Result

---

## 11. Author-Gate Trade-offs Requiring Explicit Approval (AG-10 shape)

Five decisions the plan must get explicit sign-off on before D.3
implementation begins.

### AG-1: Writer strategy

- **⭐ Recommended**: local SQLite writer in
  `tools/runtime_cert/decisions/cert_decision_ledger.py`, patterned after
  `tools.ledgers.writer` but not importing from it. Rationale: §6 table.
- **Alternative A**: force-fit via `emit_ledger_event` with the D.1
  record serialised to `prediction_json`. Rejected — loses typed columns
  and per-app file boundary.
- **Alternative B**: extend `tools.ledgers.writer` with a "domain
  ledger" mode that accepts arbitrary schemas. Rejected for D.3 — too
  large a refactor for a single-app-file use case; if multiple future
  domain ledgers need it, bring back as a dedicated ADR.

### AG-2: File layout

- **⭐ Recommended**: one SQLite file per app at
  `artifacts/ledgers/cert_decision_<app_name>.sqlite`. Rationale: matches
  ADR-080 §6 + preserves app isolation (forensic containment when one
  app misbehaves).
- **Alternative A**: one shared file `cert_decisions.sqlite` with
  `app_name` column + index. Rejected — violates ADR-080 §6; locks one
  app can spread to others.
- **Alternative B**: one shared file + per-app views. Rejected — views
  do not isolate write locks.

### AG-3: Fail-soft default

- **⭐ Recommended**: `fail_soft=True` default (per plan §3). Matches the
  `tools.ledgers.writer` fail-soft contract and the ADR-050 intelligence
  ledger family discipline. Programmer errors (TypeError, ValueError)
  still raise.
- **Alternative A**: `fail_soft=False` default; callers opt into the
  soft mode. Rejected — the evaluator upstream (D.2) is itself pure and
  its callers will want persistence to never block them on a transient
  SQLite issue.

### AG-4: DDL location

- **⭐ Recommended**: `.cursor/schemas/cert_decision_ledger.schema.sql`
  (convention-aligned with existing ledger schemas) but NOT registered
  in `LEDGER_REGISTRY`. Ensure-ledger helper reads and applies this file.
- **Alternative A**: inline DDL as a Python string constant in
  `cert_decision_ledger.py`. Rejected — DDL in SQL files is more
  auditable and grep-friendly.
- **Alternative B**: register in `LEDGER_REGISTRY` as the 11th entry.
  Rejected — see §6 "Registry coupling" row.

### AG-5: Read-back validation strategy

- **⭐ Recommended**: re-validate every row on read through D.1's
  `make_certification_decision_record`. Catches SQL-layer tampering.
- **Alternative A**: trust SQL CHECK constraints; skip D.1 validation
  on read for speed. Rejected — read volumes in Phase D are small
  (one analyst per week), speed is not a concern, and the double-guard
  materially strengthens the audit story.
- **Alternative B**: validate only structural fields, not the
  `decision_id` hash. Rejected — omitting the hash check would allow
  rows with `decision_id` recomputed under a different algorithm to
  round-trip silently.

---

## 12. Test Plan

Target: `tests/unit/tools/runtime_cert/decisions/test_cert_decision_ledger.py`.
**Pytest `tmp_path` fixture used throughout; no repo-tree writes, no
shared temp dir.**

### Required coverage (≥16 cases)

| # | Test | Assertion |
|---|---|---|
| 1 | `test_ledger_path_validates_apps_prefix` | `ledger_path_for_app("research")` raises ValueError; `ledger_path_for_app("apps_research")` returns a path under `artifacts/ledgers/` |
| 2 | `test_ledger_path_uses_supplied_repo_root` | `repo_root=tmp_path` produces path under `tmp_path/artifacts/ledgers/cert_decision_apps_X.sqlite` |
| 3 | `test_ensure_ledger_creates_schema` | After `ensure_cert_decision_ledger(p)`, querying `sqlite_master` shows table `cert_decisions` with PK `decision_id` and three indexes |
| 4 | `test_ensure_ledger_is_idempotent` | Calling twice does not raise; table count unchanged |
| 5 | `test_write_valid_record_returns_written_true` | New record → `result.written is True`, `already_exists is False`, `skipped is False`, `error is None` |
| 6 | `test_duplicate_decision_id_returns_already_exists` | Second write of same record → `result.already_exists is True`, `written is False` |
| 7 | `test_duplicate_decision_id_does_not_modify_row` | Second write with same `decision_id` but different field values does not mutate the existing row (INSERT OR IGNORE semantics) |
| 8 | `test_write_then_read_round_trip` | `read_cert_decision_records(app_name)` returns tuple with the exact record written, validated via D.1 `__post_init__` |
| 9 | `test_read_returns_empty_tuple_for_missing_ledger` | `read_cert_decision_records("apps_never_written")` returns `()` without raising |
| 10 | `test_read_ordered_by_inserted_at_utc` | Write three records with staggered `generated_at_utc` — read order matches insertion order |
| 11 | `test_fail_soft_absorbs_sqlite_error` | Monkeypatch `sqlite3.connect` to raise `sqlite3.OperationalError`; `result.skipped is True`, `result.error` contains error text |
| 12 | `test_fail_soft_false_raises` | Same monkeypatch; `fail_soft=False` re-raises `sqlite3.OperationalError` |
| 13 | `test_bypass_env_var` | `CERT_DECISION_LEDGER_BYPASS=1` → write returns `skipped=True`, `error="bypass"` |
| 14 | `test_write_rejects_non_record_input` | `write_cert_decision_record(object())` raises `TypeError` in both fail_soft modes |
| 15 | `test_certify_verdict_still_writes_not_certified_status_after` | Construct a record with `verdict=certify` (via D.1 helper); write + read; assert persisted `runtime_certification_status_after == "NOT_CERTIFIED"` |
| 16 | `test_no_scanner_ci_emitter_imports` | Import module; assert its `sys.modules` deltas do not include anything under `agentic_core.L*` or `ops_scripts.ci.` or `tools.spine.scanner.*` |
| 17 | `test_ddl_check_constraint_rejects_bad_status` | Directly INSERT a row with `runtime_certification_status_after='RUNTIME_CERTIFIED'` via raw sqlite3 → `sqlite3.IntegrityError` (CHECK constraint guards tampering) |
| 18 | `test_read_revalidates_via_d1` | Directly UPDATE a persisted `record_json` to flip status to `RUNTIME_CERTIFIED`; `read_cert_decision_records` raises ValueError from D.1 `__post_init__` on the tampered row |
| 19 | `test_multiple_apps_write_to_separate_files` | Write records for `apps_research` and `apps_eval`; two distinct files exist; cross-app read shows isolation |
| 20 | `test_concurrent_writes_serialized_via_lock` | Two threads writing distinct records to same file both complete; final row count = 2 |
| 21 | `test_write_result_invariant_one_flag_true` | For every outcome path (written / already_exists / skipped), assert exactly one of the three boolean flags is True |

### Forbidden in tests

- Writes outside `tmp_path` (no repo-tree pollution)
- Real `artifacts/ledgers/` paths
- Network calls
- Subprocess / `run_command`
- Any import of `agentic_core.L*`, `ops_scripts.ci.*`, or
  `tools.spine.scanner.*`

---

## 13. Stop Conditions

Implementation halts and surfaces the issue back for Author-Gate review
if any of these is detected during D3.W2:

- The plan's "INSERT OR IGNORE + total_changes" idempotency pattern
  turns out to not work as expected on the installed SQLite version
  (unlikely — SQLite 3.x has supported this since 3.0)
- The `CHECK (runtime_certification_status_after = 'NOT_CERTIFIED')`
  constraint conflicts with some future D.1 field addition (if D.1
  changes, re-plan before D.3 ships)
- The per-app SQLite file creates cross-app file-handle exhaustion
  in any test (unlikely at N<20 apps)
- `tools.ledgers.writer`'s threading-lock pattern turns out to be
  insufficient under pytest-xdist (tests must be xdist-disabled anyway
  per plan §12, so this is a non-issue by design)
- The DDL file at `.cursor/schemas/` conflicts with
  `tools/ledgers/apply_schema.py`'s sweep behavior (need to verify
  `apply_schema.py` iterates `LEDGER_REGISTRY`, not the schemas directory
  — if it sweeps the directory, the D.3 DDL filename must be chosen to
  avoid accidental registration)

---

## 14. Decisions Captured in This Plan

| # | Decision | Source | Status |
|---|---|---|---|
| 1 | Local SQLite writer (not `tools.ledgers.writer`) | §6, §11 AG-1 | Recommended; pending AG |
| 2 | Per-app file at `artifacts/ledgers/cert_decision_<app>.sqlite` | ADR-080 §6, §11 AG-2 | Inherited + reaffirmed |
| 3 | `decision_id` as PRIMARY KEY — idempotency via INSERT OR IGNORE | §9, plan spec §2 | Recommended; pending AG |
| 4 | `fail_soft=True` default; returns `CertDecisionLedgerWriteResult` | §10, §11 AG-3 | Recommended; pending AG |
| 5 | DDL in `.cursor/schemas/cert_decision_ledger.schema.sql`, **not** in `LEDGER_REGISTRY` | §5, §11 AG-4 | Recommended; pending AG |
| 6 | `CHECK` constraints on both status columns (belt-and-suspenders with D.1) | §7 | Recommended; pending AG |
| 7 | Read-back re-validates every row via D.1 | §9, §11 AG-5 | Recommended; pending AG |
| 8 | `CERT_DECISION_LEDGER_BYPASS=1` env var (distinct from `LEDGER_WRITER_BYPASS`) | §6, §10 | Recommended; pending AG |
| 9 | Non-promotion: writer persists `NOT_CERTIFIED` verbatim; never mutates scanner state | §1, ADR-080 §14 | Hard constraint |

---

## 15. Unresolved Questions

1. **Does `tools/ledgers/apply_schema.py` sweep `.cursor/schemas/` or
   iterate `LEDGER_REGISTRY`?** If the former, the D.3 DDL filename must
   not match an existing pattern that triggers registration. Verification
   step, not a design change. Resolve at D3.P2 start.
2. **ADR-079 consumer mode for the writer.** Existing runtime-cert
   tools declare `__adg_consumer_mode__ = "runtime_cert_read"`. The
   writer writes to a ledger but never reads the ADG. Options: keep
   `runtime_cert_read` (ledger is not ADG), introduce
   `runtime_cert_ledger_write`, or omit the declaration since it is
   not an ADG-consumer. Resolve at D3.P2 start; default to
   `runtime_cert_read` for consistency unless the ADR-079 gate objects.
3. **Transaction isolation level.** `isolation_level=None` + explicit
   `BEGIN` matches `tools.ledgers.writer`. Confirm this is the intended
   pattern or whether default (deferred) is preferable for write
   throughput. Low stakes — write volume is ~1 record per app per
   weekly closeout.
4. **Should `ledger_path_for_app` accept a `repo_root=None` default
   that resolves to CWD?** Alternative: require explicit `repo_root`.
   Recommendation: resolve to `Path(__file__).resolve().parents[3]`
   (repo root) when `None`, matching `tools/ledgers/schema_registry.py`
   convention.
5. **Write-throttle / rate-limit.** Not expected to matter at Phase D
   volume (one record per app per closeout = roughly one write per week
   per app). Noted here in case D.5 calibration runs bulk-reprocess
   historical closeouts; defer to D.5.

None block implementation.

---

## 16. Explicit No-Certification Disclaimer

> **This plan authorises no certification.** Every
> `CertificationDecisionRecord` that D.3 will persist carries
> `runtime_certification_status_before == runtime_certification_status_after
> == NOT_CERTIFIED` by the structural invariant of D.1's `__post_init__`.
> The proposed ledger schema **additionally** encodes this as SQL `CHECK`
> constraints so that direct-SQL tampering cannot introduce a promoted
> status without a constraint violation.
>
> A `verdict == "certify"` row in this ledger is **not** a certification.
> It is a statement that, if this codebase were at Phase F, the Phase F
> promotion workflow would promote the app. Phase F does not exist.
> No scanner `runtime_mode` is changed. No CI gate is added. No runtime
> emitter is modified. No app behavior changes.
>
> D.3 implementation begins **only after** a separate Author-Gate
> approves this plan, per ADR-080 §11. Phases D.4 / D.5 each remain
> gated on their own Author-Gate.

---

## 17. Recommended Next Step

**Phase D.3 implementation — but only after Author-Gate approval of this
plan.**

Suggested gate question for the follow-up turn:

> The D.3 plan proposes five trade-offs (AG-1 through AG-5 in §11).
> Approve all five as recommended? Or surface specific alternatives for
> re-scoping?

On approval, work proceeds in three commits per plan §Wave Structure:

1. **D3.W2 commit 1**: `.cursor/schemas/cert_decision_ledger.schema.sql`
   DDL + `ensure_cert_decision_ledger` + `ledger_path_for_app` + tests
   1–4, 17, 19.
2. **D3.W2 commit 2**: `CertDecisionLedgerWriteResult` +
   `write_cert_decision_record` + `read_cert_decision_records` + tests
   5–16, 18, 20, 21.
3. **D3.W3 commit 3**: mark ADR-080 §11 D.3 ✅ with test count; add
   binding-matrix footnote; §14 disclaimer preserved verbatim.

**Commit discipline (lesson from D.2 attribution anomaly — see §3)**:
each commit uses explicit paths via `git add <specific-files>` with no
`git add -A` / `git commit -a`. Before invoking `git commit`, verify no
background processes (hygiene sweeps, guardian appliers, ADG regenerators)
are staging changes in the working tree.

D.4 / D.5 each remain gated on their own Author-Gates per ADR-080 §11.
No implementation of D.3 begins now. No files other than this plan are
modified in the current turn.
