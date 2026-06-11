---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\runtime-cert-d4-cert-decision-smoke-7acad5.md'
original_relative_path: '_archive\\2026-05\\runtime-cert-d4-cert-decision-smoke-7acad5.md'
source_sha256: c57fb756117bb84efad6322d8bc936561967d1f457416278125d342d6a0ae246
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Runtime Cert — Phase D.4 Cert-Decision Smoke Harness (Planning Only)

- **Plan ID**: `runtime-cert-d4-cert-decision-smoke-7acad5`
- **Status**: Planning — Author-Gate pending
- **Authored**: 2026-05-01
- **ADR anchor**: [ADR-080 §11 D.4](../../docs/architecture/adr/ADR-080-runtime-cert-phase-d-planning.md)
- **Predecessors (per task context)**:
  - D.1 schema — `tools/runtime_cert/decisions/cert_decision_record.py`
  - D.2 evaluator — `tools/runtime_cert/decisions/cert_decision_evaluator.py`
  - D.3 ledger writer — `tools/runtime_cert/decisions/cert_decision_ledger.py` with `write_cert_decision_record` + `read_cert_decision_records` + per-app SQLite files under `artifacts/ledgers/cert_decision_<app>.sqlite`

> **Planning pass only.** This file authorizes **no** Python code, **no**
> smoke execution, **no** real ledger writes, **no** scanner edits, **no**
> CI gates, **no** emitter changes, **no** app behavior changes, and **no**
> certification claim. D.4 implementation begins only after a separate
> Author-Gate approves this plan. `runtime_certification_status` for every
> app remains `NOT_CERTIFIED` throughout and after this plan.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| D4.W1 | D4.P1 | Author-Gate approval of this plan | ~1 000 | ADR-080 §11 permits per-sub-phase gating | Pending | User approves one of AG options in §10 |
| D4.W2 | D4.P2, D4.P3 | Smoke module + report writer + tests | ~6 500 | D.1/D.2/D.3 stable on disk at implementation time | Blocked on D4.W1 | `tools/runtime_cert/smoke/cert_decision_smoke.py` with 10+ unit tests, all tests use `tmp_path` for ledger output |
| D4.W3 | D4.P4 | ADR-080 §11 ✅ D.4 + binding matrix footnote | ~600 | D4.W2 merged | Blocked on D4.W2 | ADR row marked ✅; §14 disclaimer preserved verbatim |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---:|---|---|
| D4.P1 | Author-Gate approval | This plan file | Four trade-offs in §10 need explicit sign-off | ~1 000 | Pending |
| D4.P2 | `run_cert_decision_smoke` + `CertDecisionSmokeReport` | `cert_decision_smoke.py` (new) | End-to-end wiring pure evaluator → ledger writer → read-back; every step must preserve `NOT_CERTIFIED` | ~3 500 | Blocked |
| D4.P3 | Report writer + tests | same module + `test_cert_decision_smoke.py` | JSON disclaimer line always present; `tmp_path`-only test writes; monkeypatch-driven failure injection | ~3 000 | Blocked |
| D4.P4 | Doc updates | ADR-080 §11, binding matrix footnote | Preserve §14 disclaimer verbatim | ~600 | Blocked |

---

## 1. Purpose and Non-Goals

### Purpose

Plan an **end-to-end non-promoting smoke harness** that wires the Phase D
pipeline together for a single invocation:

```
PhaseCCloseoutReport  →  evaluate_phase_c_closeout  →  write_cert_decision_record  →  read_cert_decision_records
       (D.2 input)           (D.2 produces records)    (D.3 persists each)             (D.3 reads back)
```

Output is a `CertDecisionSmokeReport` that documents what was written,
what already existed, what was skipped, and what was read back — plus
failure reasons when invariants did not hold. The harness exists to
prove that the D.1→D.2→D.3 chain composes correctly under realistic
inputs **without certifying any app**.

### Non-goals

- **No scanner `runtime_mode` change.** Smoke runs never mutate scanner state.
- **No CI gate.** No pre-commit hook, no workflow, no check-script ships with D.4.
- **No emitter change.** Runtime-ADG span emitters are untouched.
- **No certification promotion.** `runtime_certification_status_after` remains `NOT_CERTIFIED` everywhere — in every produced `CertificationDecisionRecord`, every persisted SQL row, every read-back record, and the `CertDecisionSmokeReport` itself.
- **No live runtime-ADG snapshot dependency.** D.4 consumes synthetic `PhaseCCloseoutReport` fixtures (see §2 AG-1). The C.1→C.2→C.3→C.8 pipeline is exercised elsewhere (C.6 smoke) and does not need to re-run here.
- **No Markdown closeout parsing.** The in-memory report shape is the contract; Markdown is a view, not an input to D.4.
- **No real `artifacts/ledgers/` writes in tests.** Every test uses `tmp_path` for `repo_root`. The harness module *can* write to the real path when called by a human operator outside pytest, but tests never do.
- **No app behavior change.** Every `apps_*` package is read-only.
- **No batch / parallel-run API.** One `PhaseCCloseoutReport` per call. Operators needing multi-report runs loop externally.
- **No outcome binding.** D.4 does not bind a Phase F promotion outcome back to the ledger; that's an out-of-scope downstream concern.

---

## 2. Smoke Input — Decision Captured

**Recommendation** (AG-1): D.4 consumes a **synthetic
`PhaseCCloseoutReport` fixture** constructed directly via the C.8 frozen
dataclass. No live runtime-ADG snapshot is required. No Markdown is
parsed.

Rationale:

- **Decouples D.4 from C.1 instability.** A live snapshot adds a dependency on `otel_mcp` / runtime-ADG availability; D.4 should run on any dev machine, in any CI lane, with zero external state.
- **Matches D.2 pattern.** D.2 already consumes the in-memory report dataclass as its canonical input; D.4 extends the same contract.
- **Markdown is a view, not an interface.** `write_phase_c_closeout_markdown` produces a human-readable artifact. The source-of-truth is the dataclass. Parsing the Markdown back into a dataclass would duplicate C.8 validation logic and introduce a second failure surface.
- **C.6 already exercises the live-trace path.** Phase C.6 (`live_trace_smoke.py`) is the wiring that consumes a real runtime-ADG snapshot and produces a `LiveTraceSmokeReport`. D.4 starts where C.6 ends — at the in-memory closeout shape.

D.4 MAY accept a pre-built C.8 report object from any source (fixture, C.6 output, pickled test artifact). The harness does not care how the report was built, only that its dataclass invariants hold (`runtime_certification_status == NOT_CERTIFIED`, `app_summaries` non-empty, etc.).

### Fixture construction patterns (for tests; implementation left to D4.P2)

Tests will construct `PhaseCCloseoutReport` fixtures using C.8's public dataclass constructor with carefully chosen `AppCloseoutSummary` values that drive each of the three verdicts (`certify`, `reject`, `hold`) through the D.2 evaluator — exactly the approach already used by `test_cert_decision_evaluator.py`. No new fixture infrastructure is introduced.

---

## 3. Ledger Location — Decision Captured

**Recommendation** (AG-2): D.4 accepts `repo_root` as a **required
keyword argument**. Tests pass `tmp_path` (or a subdirectory). The
harness never writes to the repo's real `artifacts/ledgers/` tree
during tests.

Rationale:

- **Matches D.3's existing contract.** `ledger_path_for_app(app_name, repo_root=...)` already accepts and honors `repo_root`. D.4 simply forwards it.
- **Zero test-pollution risk.** `tmp_path` is per-test and is wiped by pytest; no risk of stale SQLite files across runs, no accidental cross-test contamination via shared-state.
- **No ledger-path magic in D.4.** The harness does not compute paths itself; it delegates to `ledger_path_for_app`. This keeps path logic in exactly one place (D.3) and eliminates D.4 as a source of path drift.

When a human operator runs the smoke against the real repo (e.g., for manual verification), they pass `repo_root=Path.cwd()` or the repo root explicitly. That is outside test scope and is documented in the module docstring.

---

## 4. Proposed Target File

```
tools/runtime_cert/smoke/cert_decision_smoke.py
```

Lives alongside `live_trace_smoke.py` (C.6). The `smoke/` package already exists; no new `__init__.py` needed beyond re-exporting `CertDecisionSmokeReport`.

Tests:

```
tests/unit/tools/runtime_cert/smoke/test_cert_decision_smoke.py
```

Adjacent to `test_live_trace_smoke.py`. Both paths respect constitutional §31 (SSOT folder routing).

---

## 5. Public API Proposal

Exactly two public functions + one frozen dataclass. No classes. No side effects beyond ledger SQL writes (which go through D.3).

```python
# tools/runtime_cert/smoke/cert_decision_smoke.py

from __future__ import annotations

__adg_consumer_mode__ = "runtime_cert_read"

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from tools.runtime_cert.decisions.cert_decision_record import (
    CertificationDecisionRecord,
    NOT_CERTIFIED,
)
from tools.runtime_cert.decisions.cert_decision_ledger import (
    CertDecisionLedgerWriteResult,
)
from tools.runtime_cert.reports.phase_c_closeout import PhaseCCloseoutReport


DISCLAIMER = (
    "no runtime certification performed — this is Phase D.4 "
    "non-promoting smoke evidence only"
)


@dataclass(frozen=True)
class CertDecisionSmokeReport:
    generated_at_utc: str
    input_app_count: int
    decision_count: int
    written_count: int
    already_exists_count: int
    skipped_count: int
    read_back_count: int
    runtime_certification_status: str  # MUST equal NOT_CERTIFIED
    decision_ids: tuple[str, ...]
    ledger_paths: tuple[Path, ...]
    verdicts: tuple[str, ...]
    write_results: tuple[CertDecisionLedgerWriteResult, ...]
    read_back_records: tuple[CertificationDecisionRecord, ...]
    failure_reasons: tuple[str, ...]
    notes: str


def run_cert_decision_smoke(
    report: PhaseCCloseoutReport,
    *,
    repo_root: str | Path,
    history: Iterable[CertificationDecisionRecord] = (),
) -> CertDecisionSmokeReport:
    """End-to-end non-promoting smoke: C.8 -> D.2 -> D.3 -> D.3 read-back.

    1. evaluator = evaluate_phase_c_closeout(report, history)   # produces records
    2. for each record: write_result = write_cert_decision_record(record, repo_root=repo_root)
    3. for each distinct (app_name): read-back via read_cert_decision_records(app_name, repo_root=repo_root)
    4. verify each written decision_id appears in read-back
    5. verify every read-back record has status_after == NOT_CERTIFIED
    6. return CertDecisionSmokeReport with all counts + failure_reasons
    """


def write_cert_decision_smoke_report(
    report: CertDecisionSmokeReport,
    output_path: str | Path,
) -> Path:
    """Write the smoke report to disk as JSON (primary) with a .md sidecar (optional).

    The written JSON document MUST include a top-level `"disclaimer"`
    field equal to DISCLAIMER and MUST include
    `"runtime_certification_status": "NOT_CERTIFIED"`. The writer never
    omits these two keys regardless of input.
    """
```

Internal helpers (module-private, leading `_`):

- `_distinct_apps(records) -> tuple[str, ...]` — preserve first-seen order per app
- `_readback_map(app_names, repo_root) -> dict[str, tuple[CertificationDecisionRecord, ...]]`
- `_collect_failure_reasons(write_results, written_ids, read_back_ids, statuses) -> tuple[str, ...]` — closed-ontology failure codes per §7
- `_iso_now_utc() -> str` — millisecond-precision UTC

---

## 6. Behavior Specification

### Happy path

1. Input `PhaseCCloseoutReport` with N app summaries.
2. `evaluate_phase_c_closeout(report, history)` returns a tuple of exactly N `CertificationDecisionRecord` objects (D.2 contract).
3. For each record, call `write_cert_decision_record(record, repo_root=repo_root)`. Default is `fail_soft=True` (D.3 default).
4. Each `CertDecisionLedgerWriteResult` is retained in `write_results`.
5. Build a distinct list of `(app_name, repo_root)` pairs; for each, call `read_cert_decision_records(app_name, repo_root=repo_root)`.
6. Concatenate read-back records (order-preserving).
7. Assemble `CertDecisionSmokeReport` with:
   - `decision_count == N`
   - `written_count + already_exists_count + skipped_count == N` (exactly-one-flag invariant from D.3)
   - `read_back_count == sum of read-back records`
   - `runtime_certification_status == NOT_CERTIFIED` unconditionally

### Idempotent second-run

When `run_cert_decision_smoke` is invoked twice with the same `report` and `repo_root` (and no other state changes), the second run produces `CertDecisionSmokeReport` with:

- `written_count == 0`
- `already_exists_count == N`
- `skipped_count == 0`
- `read_back_count == N` (same records as first run)
- no failure reasons

This follows directly from D.3's `INSERT OR IGNORE` idempotency on `decision_id`.

### Fail-soft absorption

If any `write_cert_decision_record` call returns `skipped=True` (SQLite error absorbed by D.3 fail-soft), the smoke report:

- counts it in `skipped_count`
- includes its `CertDecisionLedgerWriteResult.error` text in a `notes` entry
- adds `"LEDGER_WRITE_SKIPPED"` to `failure_reasons`
- does NOT raise — the harness tolerates partial failure because D.3 tolerates partial failure

The read-back step still runs for all apps; skipped records simply will not appear in the read-back list, which will generate a `"MISSING_READBACK"` failure reason for those decision_ids.

### Non-promotion invariants (triple-checked)

1. **Input**: `report.runtime_certification_status == NOT_CERTIFIED` (enforced by C.8 `__post_init__`).
2. **Decision**: every record has `runtime_certification_status_before == _after == NOT_CERTIFIED` (enforced by D.1 `__post_init__`).
3. **Persistence**: every SQL row has both status columns set to `NOT_CERTIFIED` (enforced by D.3 `CHECK` constraints).
4. **Read-back**: every hydrated record re-validates via D.1 (enforced by D.3 `_hydrate_one`).
5. **Report**: `CertDecisionSmokeReport.runtime_certification_status == NOT_CERTIFIED` (enforced by `__post_init__` — see §7 invariant list).

A verdict of `certify` in any record is **not** a certification. The harness does not interpret verdicts as promotion signals.

---

## 7. Report Invariants + Failure Reason Ontology

### `CertDecisionSmokeReport.__post_init__` invariants

| Invariant | Rule |
|---|---|
| Status pin | `runtime_certification_status == NOT_CERTIFIED` — raises `ValueError` otherwise |
| Count balance | `written_count + already_exists_count + skipped_count == decision_count` |
| Decision count floor | `decision_count >= 0` |
| Read-back ceiling | `read_back_count <= written_count + already_exists_count` (can't read back what was never written or what got skipped) |
| App-count consistency | `input_app_count == len(set(decision.app_name for decision in ...))` — derivable from records |
| Frozen collections | `decision_ids`, `ledger_paths`, `verdicts`, `write_results`, `read_back_records`, `failure_reasons` are all tuples |

### Closed failure-reason ontology

Exactly six constants; `failure_reasons` values MUST be drawn from this set:

```python
WRITE_COUNT_MISMATCH                 = "WRITE_COUNT_MISMATCH"
LEDGER_WRITE_SKIPPED                 = "LEDGER_WRITE_SKIPPED"
MISSING_READBACK                     = "MISSING_READBACK"
STATUS_NOT_NOT_CERTIFIED             = "STATUS_NOT_NOT_CERTIFIED"
DECISION_COUNT_DOES_NOT_MATCH_INPUT  = "DECISION_COUNT_DOES_NOT_MATCH_INPUT"
READBACK_DECISION_ID_MISMATCH        = "READBACK_DECISION_ID_MISMATCH"

SMOKE_FAILURE_REASONS = frozenset({...})
```

Trigger conditions:

| Reason | Trigger |
|---|---|
| `WRITE_COUNT_MISMATCH` | `written + already_exists + skipped != decision_count` (a D.3 contract violation; should be structurally impossible but is caught defensively) |
| `LEDGER_WRITE_SKIPPED` | one or more `write_results[i].skipped is True` |
| `MISSING_READBACK` | a decision_id that was written (`written=True`) or already-exists (`already_exists=True`) is NOT present in the read-back set |
| `STATUS_NOT_NOT_CERTIFIED` | any produced, persisted, or read-back record reports `runtime_certification_status_after != NOT_CERTIFIED` — structurally impossible via D.1/D.3 guards but caught defensively |
| `DECISION_COUNT_DOES_NOT_MATCH_INPUT` | `len(records) != len(report.app_summaries)` — a D.2 contract violation; caught defensively |
| `READBACK_DECISION_ID_MISMATCH` | a read-back decision_id does not match any decision_id present in the D.2 evaluator output (indicates unrelated prior ledger rows mixing in — only possible when `repo_root` contains a pre-existing ledger) |

An empty `failure_reasons` tuple means all invariants held. Any non-empty value is a non-fatal diagnostic — the harness does not raise; it reports.

---

## 8. Read-Back Strategy

The harness reads the ledger per distinct `app_name` exactly once, in the order apps first appear in `report.app_summaries`. This preserves determinism without fanning out read calls.

```python
seen: set[str] = set()
distinct_apps: list[str] = []
for rec in records:
    if rec.app_name not in seen:
        seen.add(rec.app_name)
        distinct_apps.append(rec.app_name)

read_back: list[CertificationDecisionRecord] = []
for app in distinct_apps:
    read_back.extend(read_cert_decision_records(app, repo_root=repo_root))
```

Only decision_ids produced by THIS run's D.2 call are expected in the read-back set. Any extra decision_ids (pre-existing ledger rows from prior runs against the same `repo_root`) are tolerated but surface as `READBACK_DECISION_ID_MISMATCH` in `failure_reasons` — this is informational, not an error. The idempotent-second-run test (§9 test 2) explicitly expects the second run to find its own prior rows — that is a MATCH, not a MISMATCH, because the decision_id hashing is deterministic.

---

## 9. Test Plan

Target: `tests/unit/tools/runtime_cert/smoke/test_cert_decision_smoke.py`. **All tests use `tmp_path` for `repo_root`; no writes outside `tmp_path`.**

### Required coverage (≥10 cases)

| # | Test | Assertion |
|---|---|---|
| 1 | `test_smoke_hold_verdict_round_trip` | Synthetic report with one R3 app yielding `verdict=hold` (small n). `smoke.written_count == 1`, `smoke.already_exists_count == 0`, `smoke.skipped_count == 0`, `smoke.read_back_count == 1`, read-back record's `verdict == "hold"` and `status_after == NOT_CERTIFIED` |
| 2 | `test_smoke_certify_verdict_still_not_certified` | Fixture with history + summary driving `verdict=certify`; **assert `read_back_records[0].runtime_certification_status_after == NOT_CERTIFIED`** AND `read_back_records[0].verdict == "certify"`. Proves the non-promotion invariant end-to-end. |
| 3 | `test_smoke_reject_verdict_round_trip` | Fixture with missing contracts driving `verdict=reject`; assert `failure_reasons` in the stored record are non-empty and smoke report has zero `failure_reasons` itself (the harness succeeded; the decision says reject) |
| 4 | `test_smoke_idempotent_second_run` | Run twice with same inputs on same `tmp_path`. First run: `written_count == N, already_exists_count == 0`. Second run: `written_count == 0, already_exists_count == N`, `read_back_count == N` both times, no `failure_reasons` |
| 5 | `test_smoke_fail_soft_skipped_surfaces_in_report` | Monkeypatch `sqlite3.connect` to raise `sqlite3.OperationalError` on the write path only (not the read path); `smoke.skipped_count == N`, `LEDGER_WRITE_SKIPPED` in `failure_reasons`, harness does not raise |
| 6 | `test_smoke_missing_readback_creates_failure_reason` | Monkeypatch `read_cert_decision_records` to return `()` for one app; smoke report contains `MISSING_READBACK` in `failure_reasons` and harness does not raise |
| 7 | `test_smoke_report_writer_includes_disclaimer` | Call `write_cert_decision_smoke_report(report, tmp_path/"smoke.json")`; read JSON; assert `payload["disclaimer"] == DISCLAIMER` and `payload["runtime_certification_status"] == "NOT_CERTIFIED"` |
| 8 | `test_smoke_report_writer_rejects_non_not_certified` | Construct a `CertDecisionSmokeReport` with `runtime_certification_status="RUNTIME_CERTIFIED"`; assert the dataclass `__post_init__` raises `ValueError` (can't even reach the writer) |
| 9 | `test_smoke_does_not_write_to_real_artifacts_ledgers` | After a full run with `repo_root=tmp_path`, assert `(Path.cwd() / "artifacts" / "ledgers" / "cert_decision_apps_smoke.sqlite").exists() is False`. Belt-and-suspenders check that `repo_root` plumbing is honored end-to-end |
| 10 | `test_smoke_no_scanner_ci_emitter_imports` | Import `cert_decision_smoke` module; filter `sys.modules` for keys matching `agentic_core.L*` / `ops_scripts.ci.` / `tools.spine.scanner.*`; assert the set is empty |
| 11 | `test_smoke_multiple_apps_one_call` | 3 app summaries producing 3 records (hold, reject, certify); `decision_count == 3`, `len(distinct ledger_paths) == 3`, `read_back_count == 3` |
| 12 | `test_smoke_count_balance_invariant` | For every outcome path, assert `written + already_exists + skipped == decision_count`; enforce via `__post_init__` of `CertDecisionSmokeReport` (test it directly by constructing invalid counts) |
| 13 | `test_smoke_preserves_input_order` | 5 app summaries; `decision_ids` tuple matches D.2 output order; `verdicts` tuple matches |
| 14 | `test_smoke_empty_report_tolerated` | `PhaseCCloseoutReport` with `app_summaries=()` — impossible via C.8's construction, but if caller bypasses validation, smoke returns `decision_count=0`, `written_count=0`, empty `read_back_records`, no failure reasons |

### Forbidden in tests

- Any write outside `tmp_path`
- Real `artifacts/ledgers/` access
- Network calls, subprocess, `run_command`
- Any import of `agentic_core.L*`, `ops_scripts.ci.*`, `tools.spine.scanner.*`
- Real runtime-ADG snapshot loading
- Markdown file parsing

### Failure injection strategy

Tests 5 and 6 use `monkeypatch.setattr` to swap `sqlite3.connect` or the D.3 `read_cert_decision_records` symbol with a raising/empty variant for the duration of the test. This stays pure (no real disk operations break) and surfaces the exact `failure_reasons` the harness must emit.

---

## 10. Author-Gate Trade-offs Requiring Explicit Approval (AG-10 shape)

Four decisions the plan must get explicit sign-off on before D.4 implementation begins.

### AG-1: Input source

- **⭐ Recommended**: synthetic `PhaseCCloseoutReport` fixtures passed directly into `run_cert_decision_smoke(report, ...)`. No Markdown parsing. No live ADG snapshot.
- **Alternative A**: load a real C.8 closeout Markdown file and re-parse it. Rejected — duplicates C.8 validation logic; Markdown is a view, not an interface.
- **Alternative B**: run the full C.1→C.8 pipeline against a live runtime-ADG snapshot as part of D.4. Rejected — couples D.4 to otel_mcp availability; C.6 already covers this path.
- **Alternative C**: accept `PhaseCCloseoutReport` OR a fixture-file path. Rejected — adds a second input surface without a downstream consumer; YAGNI.

### AG-2: Ledger output location

- **⭐ Recommended**: `repo_root` is a **required keyword argument** on `run_cert_decision_smoke`. Tests use `tmp_path`. Human operators pass the real repo root explicitly.
- **Alternative A**: default `repo_root` to the module's inferred repo root (matching D.3). Rejected — makes it too easy for a test to accidentally write into the real repo's `artifacts/ledgers/`.
- **Alternative B**: hard-code `tmp_path` inside the harness; move to `repo_root` only for the operator-facing path. Rejected — two code paths is worse than one parameter.

### AG-3: Report format

- **⭐ Recommended**: JSON as the primary on-disk format, with a top-level `"disclaimer"` field and explicit `"runtime_certification_status": "NOT_CERTIFIED"` field. `write_cert_decision_smoke_report` returns the written `Path`. **No Markdown sidecar in D.4.**
- **Alternative A**: Markdown primary (matching C.6/C.7/C.8 style). Rejected — smoke reports are consumed by downstream tooling (D.5 calibration), not by humans reading weekly reports; JSON is the correct substrate.
- **Alternative B**: JSON + Markdown dual-output. Rejected — adds a second writer with no active consumer; YAGNI until D.5 asks for it.

### AG-4: Failure handling when a write is skipped

- **⭐ Recommended**: `skipped=True` is a **diagnostic, not an error**. The harness records it in `failure_reasons` and continues — read-back proceeds for all apps, read-back gaps generate `MISSING_READBACK` reasons. Harness does not raise.
- **Alternative A**: raise on any `skipped=True`. Rejected — defeats the purpose of D.3's fail-soft contract.
- **Alternative B**: continue but mark the whole smoke `runtime_certification_status = DENIED_BY_WRITE_FAILURE`. Rejected — ADR-080 explicitly scopes Phase D to `NOT_CERTIFIED` verbatim; inventing a new status breaks the contract.

---

## 11. Test Plan — Summary Table

| # | Theme | Key assertion |
|---|---|---|
| 1 | Hold verdict round-trip | write + read, `status == NOT_CERTIFIED` |
| 2 | Certify verdict non-promotion | `verdict=certify`, `status_after == NOT_CERTIFIED` |
| 3 | Reject verdict round-trip | record carries reject reasons, smoke succeeds |
| 4 | Idempotent second run | first `written`, second `already_exists` |
| 5 | Fail-soft write skipped | `LEDGER_WRITE_SKIPPED` in failure_reasons |
| 6 | Missing read-back | `MISSING_READBACK` in failure_reasons |
| 7 | Report writer disclaimer | JSON has `disclaimer` + `NOT_CERTIFIED` fields |
| 8 | Dataclass status pin | `ValueError` on non-`NOT_CERTIFIED` input |
| 9 | `tmp_path` isolation | real repo ledger untouched |
| 10 | No forbidden imports | no L* / ci / scanner modules |
| 11 | Multi-app single call | 3 verdicts, 3 ledger files, 3 read-backs |
| 12 | Count balance invariant | written+already+skipped==decision_count |
| 13 | Order preservation | decision_ids + verdicts match input order |
| 14 | Empty report tolerated | degenerate case returns empty counts |

---

## 12. Stop Conditions

Implementation halts and surfaces back for Author-Gate review if any of these is detected during D4.W2:

- D.4 begins to require a **live runtime-ADG snapshot** — that belongs to C.6, not D.4.
- D.4 begins to require **Markdown parsing** of C.8 output — that is a view-layer operation, not an interface operation.
- D.4 begins to require **scanner code changes** — that is Phase F, explicitly out of scope.
- D.4 begins to require **real `artifacts/ledgers/` writes in tests** — that is a test-hygiene violation; `tmp_path` is the correct substrate.
- D.4 begins to require a **new CI gate** — that is Phase E, explicitly out of scope.
- D.4 begins to require **writing to the ledger from anywhere other than D.3's `write_cert_decision_record`** — that would duplicate the idempotency + fail-soft contract.
- The `CertDecisionSmokeReport.__post_init__` invariants turn out to conflict with a real-world input shape — e.g., `input_app_count` needs to be computed from the report rather than passed in. Adjust the dataclass shape and re-plan.
- `write_cert_decision_smoke_report` turns out to need more than JSON (e.g., operator requests a Markdown sidecar). That is a D.5 concern; defer.

---

## 13. Decisions Captured in This Plan

| # | Decision | Source | Status |
|---|---|---|---|
| 1 | Input: synthetic `PhaseCCloseoutReport` — no Markdown parse, no live ADG snapshot | §2, §10 AG-1 | Recommended; pending AG |
| 2 | Ledger location: required `repo_root` kwarg; tests use `tmp_path` | §3, §10 AG-2 | Recommended; pending AG |
| 3 | Report format: JSON primary with `disclaimer` + `runtime_certification_status` fields; no Markdown in D.4 | §5, §10 AG-3 | Recommended; pending AG |
| 4 | Fail-soft skip: diagnostic via `LEDGER_WRITE_SKIPPED`; harness never raises | §6, §10 AG-4 | Recommended; pending AG |
| 5 | Closed 6-reason failure ontology | §7 | Recommended; pending AG |
| 6 | Non-promotion triple-check: C.8 input + D.1 construction + D.3 CHECK + read-back re-validate + smoke report `__post_init__` | §6, §7 | Inherited from D.1/D.3 + reaffirmed here |
| 7 | One public function + one report dataclass + one writer; no batch API | §5 | Recommended; pending AG |
| 8 | Read-back order: distinct apps in first-seen order | §8 | Recommended; pending AG |
| 9 | `runtime_certification_status == NOT_CERTIFIED` is an explicit `__post_init__` check on `CertDecisionSmokeReport` | §7 | Hard constraint |

---

## 14. Unresolved Questions

1. **Should `run_cert_decision_smoke` accept an optional `fail_soft: bool = True` that forwards to `write_cert_decision_record`?** Default `True` matches D.3. An operator-facing `fail_soft=False` mode could be useful for CI-like strict runs. Recommend: add the kwarg; default `True`; document in tests but do not require a dedicated test case beyond test 5's coverage of the soft path. Resolve at D4.P2 start.
2. **Should the JSON writer also persist the `write_results` list verbatim?** They are `CertDecisionLedgerWriteResult` dataclasses with a `Path` field (not JSON-native). Options: (a) convert `Path` to `str` and include; (b) include only the summary counters; (c) exclude entirely. Recommend (a) for full auditability. Resolve at D4.P3 start.
3. **Should the harness emit a `CERT_DECISION:` marker per decision (mirroring the §29 router-decision pattern)?** ADR-080 §6 specifies such a marker for the D.3 write path, but D.3 does not currently emit one. If D.4 starts emitting markers, should D.3 too? Plan recommendation: D.4 does NOT emit markers; deferred to ADR-080 §11 D.5 or a later Phase D sub-step. Resolve by confirming D.3's current behavior does not emit; if D.3 emits, D.4 inherits automatically via `write_cert_decision_record`.
4. **JSON schema stability.** If a future Phase D.5 expects to parse these JSON reports, the schema needs versioning. Recommendation: include a top-level `"schema_version": "d4-smoke-v1"` field so future parsers can dispatch. Small addition; worth capturing explicitly in D4.P2.
5. **Should the smoke be callable from a CLI entrypoint (`python -m tools.runtime_cert.smoke.cert_decision_smoke`)?** Plan recommendation: no CLI in D.4. Humans who need to run it interactively can call the function from a one-shot script. Adding a CLI surfaces argparse + file-path coercion concerns that aren't necessary for the smoke contract. Resolve by deferring to D.5 if an operator workflow actually demands it.

None of these block implementation.

---

## 15. Boundaries (explicit)

- **D.4 does not create certification status.** No app gains `RUNTIME_CERTIFIED` or `FORMAL_EXCEPTION_VERIFIED`. Every persisted and read-back status is `NOT_CERTIFIED`.
- **D.4 does not change scanner `runtime_mode`.** Phase F (out of scope) owns that.
- **D.4 does not add a CI gate.** Phase E (out of scope) owns that.
- **D.4 does not touch real app behavior.** No `apps_*` package is read or modified.
- **D.4 does not write to real repo `artifacts/ledgers/` in tests.** `tmp_path` everywhere.
- **D.4 does not emit markers or ledger events beyond what D.3 emits.** (If D.3 does not emit a `CERT_DECISION:` marker, D.4 does not either.)
- **D.4 does not re-evaluate records.** It calls D.2 once; whatever D.2 returns, D.4 persists verbatim.

---

## 16. Explicit No-Certification Disclaimer

> **This plan authorises no certification.** Every
> `CertificationDecisionRecord` produced by the D.2 evaluator, persisted
> by the D.3 writer, or read back by the D.4 harness carries
> `runtime_certification_status_before == runtime_certification_status_after
> == NOT_CERTIFIED`. This is enforced at **five layers**: C.8 input
> construction, D.1 `__post_init__` at decision construction, D.3 SQL
> `CHECK` constraint at persistence, D.3 read-back re-validation via
> D.1's invariants, and `CertDecisionSmokeReport.__post_init__` on the
> smoke report itself.
>
> A `verdict == "certify"` row in any ledger or smoke report is **not** a
> certification. It is a statement that, if this codebase were at Phase
> F, the Phase F promotion workflow would promote the app. Phase F does
> not exist. No scanner `runtime_mode` is changed. No CI gate is added.
> No runtime emitter is modified. No app behavior changes.
>
> D.4 implementation begins **only after** a separate Author-Gate
> approves this plan, per ADR-080 §11. Phase D.5 remains gated on its
> own Author-Gate.

---

## 17. Recommended Next Step

**Phase D.4 implementation — but only after Author-Gate approval of this plan.**

Suggested gate question for the follow-up turn:

> The D.4 plan proposes four trade-offs (AG-1 through AG-4 in §10).
> Approve all four as recommended? Or surface specific alternatives for
> re-scoping?

On approval, work proceeds in three commits per plan §Wave Structure:

1. **D4.W2 commit 1**: `CertDecisionSmokeReport` dataclass +
   `run_cert_decision_smoke` core function + tests 1, 2, 3, 8, 11, 12,
   13, 14.
2. **D4.W2 commit 2**: `write_cert_decision_smoke_report` JSON writer +
   `DISCLAIMER` constant + tests 4, 5, 6, 7, 9, 10.
3. **D4.W3 commit 3**: ADR-080 §11 D.4 ✅ row with test count; binding
   matrix footnote; §14 disclaimer preserved verbatim.

**Commit discipline (lesson from prior D-series attribution anomaly)**:
each commit uses explicit paths via `git add <specific-files>` — no
`git add -A` / `git commit -a`. Before `git commit`, verify working tree
has no unrelated modifications staged via `git diff --cached --name-only`
showing only intended D.4 files. If unrelated files are staged by a
concurrent process, stop and report.

D.5 remains gated on its own Author-Gate per ADR-080 §11.
No implementation of D.4 begins now. No files other than this plan are
modified in the current turn.
