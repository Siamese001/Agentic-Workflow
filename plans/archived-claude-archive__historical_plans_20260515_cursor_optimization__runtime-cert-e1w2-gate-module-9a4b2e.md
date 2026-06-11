---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\runtime-cert-e1w2-gate-module-9a4b2e.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\runtime-cert-e1w2-gate-module-9a4b2e.md'
source_sha256: d9287924a5d78cda2f6e1761ab03b4dc606be40d4828ebcbe120a3aafff34e04
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Runtime Cert — E1.W2 Advisory Gate Module (Planning Only)

- **Plan ID**: `runtime-cert-e1w2-gate-module-9a4b2e`
- **Status**: Completed 2026-05-10 (gate+37 tests at commit d59ce88ba9)
- **Authored**: 2026-05-01
- **Branch**: `rtc-w2b-scenario-a-local-qwen-proof`
- **Parent plan**: [`runtime-cert-e1-fail-closed-ci-gate-c71f3d.md`](./runtime-cert-e1-fail-closed-ci-gate-c71f3d.md) — E-AG-1…5 APPROVED at commit `14c4e9eb5b`
- **ADR anchor**: [ADR-080 §11 E](../../docs/architecture/adr/ADR-080-runtime-cert-phase-d-planning.md)
- **Phase D state**: D.1–D.5 complete; 191/191 combined decisions + smoke tests passing at E.1 approval time
- **Predecessor approval commit**: `14c4e9eb5b` (`plan(runtime_cert): approve Phase E.1 gate decisions`)

> **Planning pass only.** This file authorizes **no** Python code, **no** baseline TOML, **no** CI gate, **no** pre-commit hook, **no** GitHub Actions edit, **no** scanner change, **no** emitter change, **no** app-behavior change, **no** ledger write, and **no** certification claim. E1.W2 implementation begins only after a separate scoped Author-Gate approves this plan. `runtime_certification_status` for every app remains `NOT_CERTIFIED` throughout and after this plan.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| E1.W2.A | W2.P1 | Author-Gate approval of this plan | ~800 | E-AG-1…5 already APPROVED | Pending | User approves §14 open questions |
| E1.W2.B | W2.P2 | Implement `check_runtime_certification.py` (advisory only) | ~5 500 | D.1–D.5 remain ✅ | Blocked on W2.A | Module passes all §10 tests; advisory-mode CLI exit 0 default; no scanner/emitter/app imports |
| E1.W2.C | W2.P3 | Implement unit tests | ~3 000 | W2.B landed | Blocked on W2.B | ≥15 tests; all use `tmp_path`; no real-repo ledger writes; no-forbidden-imports audit |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---:|---|---|
| W2.P1 | Approval of this plan | this file | Baseline schema shape + advisory-mode CLI contract need sign-off | ~800 | Pending |
| W2.P2 | Gate module | `ops_scripts/ci/check_runtime_certification.py` (new) | Must consume D.3 read-back API without triggering writes; must keep advisory exit-0 invariant separate from `passed=False` data | ~5 500 | Blocked |
| W2.P3 | Gate tests | `tests/unit/ops_scripts/ci/test_check_runtime_certification.py` (new) | Fixture setup uses D.3 writer under `tmp_path` only; strict vs advisory CLI modes both covered | ~3 000 | Blocked |

---

## 1. Purpose and Non-Goals

### Purpose

Plan the **advisory** runtime-certification gate module: a read-only Python tool that loads a TOML baseline, reads per-app D.3 cert-decision ledgers, and emits a structured `RuntimeCertGateResult`. The gate runs in **advisory mode by default** — failures are reported but the CLI exits 0 — so it can accumulate observation data without blocking commits. A `--strict` CLI flag exists but is NOT wired into CI by this plan.

### Non-goals (explicit)

- **E1.W2 does not wire CI.** `.pre-commit-config.yaml` and `.github/workflows/` are untouched. The advisory-to-strict CI flip is E1.W4 under a separate Author-Gate per E-AG-5.
- **E1.W2 does not create the baseline TOML.** `docs/reference/runtime_certification/cert_baseline.toml` does not exist on disk; its creation is deferred to a later E1.W3 scoped prompt. The gate MUST handle the missing-baseline case gracefully (`BASELINE_MISSING`).
- **E1.W2 does not certify apps.** Every `RuntimeCertGateResult` carries `runtime_certification_status = "NOT_CERTIFIED"`. The gate cannot promote, mutate, or write any certification state.
- **E1.W2 does not modify scanner `runtime_mode`.** No `tools/spine/scanner/` code is touched; no new `runtime_mode` bucket is introduced. That remains Phase F.
- **E1.W2 does not create `RUNTIME_CERTIFIED` / `FORMAL_EXCEPTION_VERIFIED` buckets.** Phase F scope.
- **E1.W2 does not write to any ledger.** D.3 `write_cert_decision_record` is NOT imported by the gate; only `read_cert_decision_records`.
- **E1.W2 does not change app behavior.** No `apps_*` package is imported or read.
- **E1.W2 does not emit markers.** No `CERT_DECISION:` / `ROUTER_DECISION:` / `DEFERRED_SCOPE:` events ship via this plan.

---

## 2. Proposed Files

Future implementation (E1.W2.B / W2.C). **NOT created by this plan.**

| File | Role | Size estimate |
|---|---|---|
| `ops_scripts/ci/check_runtime_certification.py` | Advisory gate module + CLI entrypoint | ~250–350 lines |
| `tests/unit/ops_scripts/ci/test_check_runtime_certification.py` | Unit tests (≥15) | ~400–550 lines |

Naming complies with SSOT-folder rule (`check_*.py` in `ops_scripts/ci/`, constitutional §31). No other files are created by E1.W2.

---

## 3. Gate Input Model

The gate accepts three inputs, all resolved at CLI invocation / function call:

| Input | Source | Type | Default | Required |
|---|---|---|---|---|
| `repo_root` | CLI positional arg or function kwarg | `Path` | current working directory | yes |
| `baseline_path` | `--baseline` CLI flag / function kwarg | `Path` | `<repo_root>/docs/reference/runtime_certification/cert_baseline.toml` | no (but `BASELINE_MISSING` fails when absent) |
| `strict` | `--strict` CLI flag / function kwarg | `bool` | `False` (advisory) | no |

### 3.1 Per-app ledger access

Read-only consumption via D.3's public API:

```
from tools.runtime_cert.decisions.cert_decision_ledger import read_cert_decision_records
rows = read_cert_decision_records(app_name, repo_root=repo_root)
```

- Returns `tuple[CertificationDecisionRecord, ...]` ordered by `generated_at_utc` ASC
- Empty tuple means "no prior decisions" — distinguished from "file missing" via `ledger_path_for_app(app_name, repo_root=repo_root).exists()`
- D.3's read-back re-validates every row through D.1 `__post_init__` — tamper surfaces as `ValueError` → caught by the gate and mapped to `LEDGER_READ_ERROR`

### 3.2 Advisory mode (E-AG-5 default)

- `strict=False` by default (CLI and function)
- Advisory mode: gate ALWAYS returns a fully-populated `RuntimeCertGateResult` with `advisory=True`; CLI exit code is `0` regardless of `passed`
- Strict mode: CLI exit code is `0` when `passed=True`, `1` when `passed=False`, `2` on a hard abstain class (e.g., `NO_BASELINE_APPS`)
- The function-level API returns the same `RuntimeCertGateResult` in either mode; `strict` only affects CLI exit-code translation

### 3.3 No forbidden inputs

The gate does NOT:
- Load live runtime-ADG snapshots (C.6 scope)
- Parse Markdown closeout artifacts (view layer)
- Re-run `evaluate_phase_c_closeout` on the fly (E-AG-1: ledger-read only)
- Import from `agentic_core.L*`, `tools.spine.scanner`, or any `apps_*` package (audited by test)
- Invoke subprocess, network I/O, or environment-mutating operations
- Write any file outside the caller-provided `report_path` (if JSON reporting is enabled; optional for E1.W2)

---

## 4. Baseline TOML Schema (design only — file NOT created)

Per E-AG-2, baseline lives at `docs/reference/runtime_certification/cert_baseline.toml` with schema version `e1-baseline-v1`. This plan designs the schema; it does NOT create the file.

### 4.1 Example (illustrative, not committed)

```toml
schema_version = "e1-baseline-v1"
mode = "advisory"   # advisory | strict_allowed — see §4.3

[[apps]]
app_name = "apps_research"
route_shape = "R3_grounded_read"
expected_runtime_certification_status = "NOT_CERTIFIED"
min_verdict = "hold"
require_ledger = true
manifest_hash = ""   # optional; empty means "do not check manifest hash"
notes = "Initial Phase E.1 coverage; baseline floor set to hold."

[[apps]]
app_name = "apps_knowledge_capture"
route_shape = "R3_grounded_read"
expected_runtime_certification_status = "NOT_CERTIFIED"
min_verdict = "hold"
require_ledger = true
manifest_hash = ""
notes = "Follows apps_research; baseline floor hold."
```

### 4.2 Field-level contract

| Field | Type | Required | Values | Purpose |
|---|---|---|---|---|
| `schema_version` | str | yes | exactly `"e1-baseline-v1"` | Version dispatch; anything else → `BASELINE_SCHEMA_INVALID` |
| `mode` | str | yes | `"advisory"` \| `"strict_allowed"` | Advisory baseline-level flag; `strict_allowed` = this baseline has been vetted for use with `--strict` (still requires separate CI Author-Gate per E-AG-5) |
| `[[apps]].app_name` | str | yes | non-empty; `apps_*` namespace expected | Match key for ledger path + manifest lookup |
| `[[apps]].route_shape` | str | yes | `R3_grounded_read` \| `build_time_compiler` \| `evaluator_only` \| `core_adjacent_utility` | Route-shape class from C.8 / binding matrix |
| `[[apps]].expected_runtime_certification_status` | str | yes | exactly `"NOT_CERTIFIED"` | Structural pin — any other value → `BASELINE_APP_INVALID` (defense in depth against drift) |
| `[[apps]].min_verdict` | str | yes | `"reject"` \| `"hold"` \| `"certify"` | Floor; latest ledger verdict strictly below this → `LATEST_DECISION_BELOW_BASELINE` |
| `[[apps]].require_ledger` | bool | yes | `true` \| `false` | When true, missing ledger → `LEDGER_MISSING`; empty ledger → `LEDGER_EMPTY`. When false, absent/empty ledger is a warning, not a failure |
| `[[apps]].manifest_hash` | str | yes | empty string or 64-hex | Empty = do not check; non-empty = exact match required, mismatch → `MANIFEST_HASH_MISMATCH` |
| `[[apps]].notes` | str | yes | free text | Human rationale; not interpreted by the gate |

### 4.3 `mode` field semantics

| `mode` value | Meaning |
|---|---|
| `"advisory"` | Baseline is for observation only; CLI `--strict` is ignored → always advisory behavior |
| `"strict_allowed"` | Baseline has been vetted for strict CI use (separate E1.W4 Author-Gate marked this); CLI `--strict` takes effect |

This decoupling means the baseline file itself declares whether it's ready for strict use, independently of the CLI flag.

### 4.4 Schema validation

Strict whitelist. Unknown top-level keys or unknown `[[apps]]` keys → `BASELINE_SCHEMA_INVALID`. No silent forward-compatibility — every future Phase E sub-phase must bump `schema_version`.

---

## 5. Gate Result Model

```
@dataclass(frozen=True)
class RuntimeCertAppResult:
    app_name: str
    baseline_status: str                 # "gated" | "absent_from_baseline" | "baseline_invalid"
    latest_verdict: str | None           # "reject" | "hold" | "certify" | None if no ledger row
    latest_decision_id: str | None       # D.1 compute_decision_id result
    ledger_present: bool                 # True if cert_decision_<app>.sqlite exists
    passed: bool
    failures: tuple[str, ...]            # subset of §6 failure codes
    warnings: tuple[str, ...]            # non-fatal observations

@dataclass(frozen=True)
class RuntimeCertGateResult:
    mode: str                            # "advisory" | "strict"
    baseline_path: str                   # resolved absolute path
    checked_apps: int                    # count of apps considered from baseline
    passed: bool                         # overall gate verdict
    advisory: bool                       # True when mode=="advisory"
    failure_count: int                   # sum of failures across app_results
    failures: tuple[str, ...]            # gate-level failure codes (BASELINE_MISSING etc.)
    warnings: tuple[str, ...]            # gate-level warnings
    app_results: tuple[RuntimeCertAppResult, ...]
    runtime_certification_status: str    # STRUCTURALLY pinned to "NOT_CERTIFIED"
    disclaimer: str                      # pinned to the non-promotion phrase
```

### 5.1 `__post_init__` invariants (same pattern as D.4)

- `mode ∈ {"advisory", "strict"}`
- `advisory == (mode == "advisory")`
- `runtime_certification_status == "NOT_CERTIFIED"` — raises `ValueError` otherwise
- `disclaimer` contains `"no runtime certification performed"`
- `failure_count == sum(len(r.failures) for r in app_results) + len(failures)` (consistency check)
- `passed == (failure_count == 0)` — derived invariant
- All `failures` / `warnings` entries drawn from closed ontology (§6)

### 5.2 `to_dict()` / `to_json()` serializers

Following D.1 convention: tuple → list; deterministic JSON (`sort_keys=True, separators=(",", ":")`). Output shape is stable for downstream consumption.

---

## 6. Failure-Code Ontology (closed set)

| Code | Level | Trigger |
|---|---|---|
| `BASELINE_MISSING` | gate-level | `baseline_path` does not exist |
| `BASELINE_SCHEMA_INVALID` | gate-level | `schema_version` wrong, unknown keys, malformed TOML |
| `BASELINE_APP_INVALID` | app-level | app entry fails field-level validation (e.g., `min_verdict` outside {reject, hold, certify}) |
| `LEDGER_MISSING` | app-level | `require_ledger=true` AND no `cert_decision_<app>.sqlite` file |
| `LEDGER_EMPTY` | app-level | `require_ledger=true` AND ledger file exists but `read_cert_decision_records(...)` returns `()` |
| `LATEST_DECISION_BELOW_BASELINE` | app-level | Latest row's `verdict` strictly below baseline `min_verdict` per §7 ordering |
| `MANIFEST_HASH_MISMATCH` | app-level | Baseline `manifest_hash` non-empty AND latest row's `manifest_hash` ≠ baseline value |
| `STATUS_NOT_NOT_CERTIFIED` | app-level | Latest row's `runtime_certification_status_before` or `_after` ≠ `NOT_CERTIFIED` (defense in depth — structurally impossible via D.1) |
| `LEDGER_READ_ERROR` | app-level | D.3 read-back raised `ValueError` / `sqlite3.Error` — tamper or corruption |
| `NO_BASELINE_APPS` | gate-level | `[[apps]]` table empty |

**Closed set.** No new codes introduced without a schema-version bump. First failure does NOT short-circuit — the gate collects ALL failures across all apps before returning.

### 6.1 Warnings (non-fatal, disjoint set)

| Warning | Trigger |
|---|---|
| `LEDGER_ABSENT_OPTIONAL` | `require_ledger=false` AND ledger file missing |
| `LEDGER_EMPTY_OPTIONAL` | `require_ledger=false` AND ledger present but empty |
| `ADVISORY_FAILURES_SUPPRESSED` | advisory mode AND `failure_count > 0` (informational; emitted once at gate level) |

---

## 7. Verdict Ordering

Total order over `verdict` values:

```
reject (0) < hold (1) < certify (2)
```

`min_verdict` comparison: latest ledger row's `verdict` must be `>= min_verdict` in the ordering above. Examples:

| Baseline `min_verdict` | Latest ledger `verdict` | Result |
|---|---|---|
| `hold` | `reject` | **FAIL** — `LATEST_DECISION_BELOW_BASELINE` |
| `hold` | `hold` | pass |
| `hold` | `certify` | pass (still `NOT_CERTIFIED` — see §7.1) |
| `certify` | `hold` | **FAIL** — `LATEST_DECISION_BELOW_BASELINE` |
| `reject` | any verdict | pass (accepts everything; use sparingly) |

### 7.1 `certify` remains non-promoting (load-bearing)

> A latest ledger `verdict == "certify"` that meets a baseline `min_verdict` is **still** non-promoting. `RuntimeCertGateResult.runtime_certification_status` remains `"NOT_CERTIFIED"`. The app's `runtime_certification_status_before` and `_after` on that row are `NOT_CERTIFIED` (D.1 + D.3 CHECK). The gate's passed=True is a consistency signal, not a promotion signal. Phase F is the only layer that can promote.

Defense in depth: `STATUS_NOT_NOT_CERTIFIED` fires (app-level failure) if any row somehow reaches the gate with status ≠ `NOT_CERTIFIED`, even though D.1/D.3 make this structurally impossible.

---

## 8. Advisory Behavior (E-AG-5)

| Property | Advisory (default) | Strict (`--strict`) |
|---|---|---|
| Function returns `RuntimeCertGateResult` | yes | yes |
| `result.passed` reflects failures | yes | yes |
| `result.advisory` | `True` | `False` |
| `result.mode` | `"advisory"` | `"strict"` |
| CLI exit code | `0` always (warning log on failures) | `0` if passed, `1` on app-level failures, `2` on gate-level abstain (`NO_BASELINE_APPS`, `BASELINE_MISSING`) |
| Emits `ADVISORY_FAILURES_SUPPRESSED` warning | yes when `failure_count > 0` | no |

### 8.1 Key invariants

- **Advisory mode exists to accumulate data**, not to be useless. `passed=False` is visible in the result; only the CLI exit-code translation differs.
- **CI wiring is DEFERRED.** This plan does not touch `.pre-commit-config.yaml` or `.github/workflows/`. E1.W4 is the Author-Gate that flips advisory→strict in CI; E1.W2 only ships the toggle, never activates it.
- **`--strict` is respected even when `mode="advisory"` in the baseline**: NO. If baseline `mode=="advisory"`, the gate overrides any `--strict` request and falls back to advisory. This prevents accidental enforcement of an un-vetted baseline.
- **Tests must assert default advisory behavior**: CLI run with no flags over a failing fixture → exit 0, warning logged (§10 test coverage).

---

## 9. Public API

```python
# ops_scripts/ci/check_runtime_certification.py

def load_runtime_cert_baseline(path: str | Path) -> RuntimeCertBaseline:
    """Load and validate the TOML baseline. Raises BaselineError subclasses on failure."""

def check_runtime_certification(
    repo_root: str | Path,
    baseline_path: str | Path | None = None,
    *,
    strict: bool = False,
) -> RuntimeCertGateResult:
    """Run the advisory gate. Always returns a result; never raises on failures."""

def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint. Returns the exit code per §8 table."""

# Module-level constants (closed ontologies)
FAILURE_CODES: frozenset[str]    # §6
WARNING_CODES: frozenset[str]    # §6.1
VERDICT_ORDER: dict[str, int]    # §7
NOT_CERTIFIED: str               # re-exported from D.1 for clarity
DISCLAIMER: str                  # canonical phrase
SCHEMA_VERSION: str              # "e1-baseline-v1"
```

### 9.1 `RuntimeCertBaseline` helper dataclass (internal; not exported)

- Frozen
- Fields: `schema_version: str`, `mode: str`, `apps: tuple[BaselineApp, ...]`
- Validates at `__post_init__`

### 9.2 Import surface (what the module imports)

```
# Standard library
import argparse, json, sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Sequence
try:
    import tomllib
except ImportError:
    import tomli as tomllib   # fallback for Python < 3.11

# Project imports (READ-ONLY)
from tools.runtime_cert.decisions.cert_decision_ledger import (
    read_cert_decision_records,
    ledger_path_for_app,
)
from tools.runtime_cert.decisions.cert_decision_record import (
    NOT_CERTIFIED,
    VERDICT_CERTIFY,
    VERDICT_HOLD,
    VERDICT_REJECT,
    CertificationDecisionRecord,
)
```

### 9.3 Forbidden imports (enforced by test)

- `agentic_core.L0_*` / `agentic_core.L1_*` / … / `agentic_core.L6_*` — no layer code
- `apps_research` / `apps_knowledge_capture` / `apps_eval` / `apps_underwriting_ai` / `apps_shared` — no app code
- `tools.spine.scanner` / any scanner surface
- `tools.runtime_adg` emit paths
- `tools.runtime_cert.decisions.cert_decision_ledger.write_cert_decision_record` — explicit read-only contract
- `tools.runtime_cert.smoke.cert_decision_smoke` — the gate does NOT invoke the D.4 smoke harness
- Any `ops_scripts.ci.*` beyond itself (no cross-gate composition)

---

## 10. Test Plan (≥15 tests required at W2.P3 time)

All tests use `tmp_path` for `repo_root` and `baseline_path`. Fixtures construct synthetic ledger content via D.3's writer invoked from test setup, NEVER from the gate itself.

| # | Test | Assertion |
|---|---|---|
| 1 | `test_baseline_missing_produces_failure` | `baseline_path` not present → `failures == ("BASELINE_MISSING",)`, `passed=False` |
| 2 | `test_baseline_invalid_schema_version` | `schema_version = "wrong"` → `BASELINE_SCHEMA_INVALID` |
| 3 | `test_baseline_unknown_top_level_key` | TOML with unexpected key → `BASELINE_SCHEMA_INVALID` |
| 4 | `test_baseline_unknown_app_key` | `[[apps]]` with extra field → `BASELINE_SCHEMA_INVALID` |
| 5 | `test_no_baseline_apps` | Empty `apps = []` → `NO_BASELINE_APPS`, `checked_apps == 0` |
| 6 | `test_app_missing_ledger_when_required` | `require_ledger=true` + no file → `LEDGER_MISSING`, app `passed=False` |
| 7 | `test_app_empty_ledger` | `require_ledger=true` + file exists + 0 rows → `LEDGER_EMPTY` |
| 8 | `test_latest_reject_below_hold_fails` | Latest verdict `reject`, `min_verdict="hold"` → `LATEST_DECISION_BELOW_BASELINE` |
| 9 | `test_latest_hold_meets_hold_passes` | Latest `hold`, `min_verdict="hold"` → app passes |
| 10 | `test_latest_certify_meets_hold_passes_but_status_not_certified` | Latest `certify`, `min_verdict="hold"` → app passes AND `runtime_certification_status == "NOT_CERTIFIED"` on every row AND on gate result |
| 11 | `test_manifest_hash_mismatch_fails` | Baseline `manifest_hash=A`, latest row `B` → `MANIFEST_HASH_MISMATCH` |
| 12 | `test_manifest_hash_empty_skipped` | Baseline `manifest_hash=""` → no hash check, app evaluated only on verdict |
| 13 | `test_advisory_cli_returns_zero_on_failures` | Fixture with failing app; CLI `main([...])` (no `--strict`) → exit `0`, warning in logs |
| 14 | `test_strict_cli_returns_one_on_failures` | Same fixture; CLI `main(["--strict", ...])` → exit `1` |
| 15 | `test_strict_overridden_by_advisory_baseline` | Baseline `mode="advisory"` + CLI `--strict` → gate falls back to advisory; CLI exit `0` |
| 16 | `test_gate_has_no_scanner_imports` | Module source regex-scan for `tools.spine.scanner` / `agentic_core.L\d_` → empty |
| 17 | `test_gate_has_no_emitter_imports` | Module source regex-scan for `tools.runtime_adg` emit paths → empty |
| 18 | `test_gate_has_no_app_package_imports` | Module source regex-scan for `apps_research` / `apps_underwriting_ai` / etc. as import statements → empty |
| 19 | `test_gate_does_not_import_write_cert_decision_record` | Module source does not contain `write_cert_decision_record` |
| 20 | `test_gate_result_has_non_certification_disclaimer` | Every `RuntimeCertGateResult.disclaimer` contains `"no runtime certification performed"`; `runtime_certification_status == "NOT_CERTIFIED"` |
| 21 | `test_gate_does_not_write_real_repo_ledgers` | After full gate run on `tmp_path`, no new `cert_decision_*.sqlite` under real repo's `artifacts/ledgers/` |
| 22 | `test_ledger_read_error_caught` | Corrupt SQLite file → `LEDGER_READ_ERROR`, app `passed=False`, no exception raised to caller |
| 23 | `test_toml_parsing_uses_stdlib_tomllib` | `import tomllib` preferred; test imports confirm the preference chain |
| 24 | `test_first_failure_does_not_short_circuit` | Two apps both failing → both collected in `failures` / `app_results` |

### 10.1 Forbidden in tests

- Any write outside `tmp_path`
- Real `artifacts/ledgers/` access
- Network / subprocess / `run_command`
- Import of `agentic_core.L*` / `apps_*` / `tools.spine.scanner.*`
- Real runtime-ADG snapshot loading

### 10.2 Verification command (future W2.P3)

```powershell
python -m pytest tests/unit/ops_scripts/ci/test_check_runtime_certification.py -p no:xdist --timeout=60
```

---

## 11. Stop Conditions

Implementation halts and surfaces back for a fresh Author-Gate if ANY of these is detected during W2.P2 or W2.P3:

- Gate would need scanner `runtime_mode` change → **stop** (Phase F)
- Gate would need to import from any `apps_*` package → **stop** (app-behavior boundary)
- Gate would need to import from `tools.runtime_adg` emitters → **stop** (Phase F/C scope)
- Gate would need to create `docs/reference/runtime_certification/cert_baseline.toml` during W2 → **stop** (E1.W3 scope)
- Gate would need to edit `.pre-commit-config.yaml` or `.github/workflows/` → **stop** (E1.W4 Author-Gate)
- Gate would need a new `CERT_DECISION:` marker or new ledger entry → **stop** (deferred beyond E.1)
- Gate would need to invoke `write_cert_decision_record` → **stop** (read-only contract violated)
- Gate would need to call `run_cert_decision_smoke` → **stop** (D.4 is not a gate input)
- Phase D state (`cert_decision_smoke.py`, D.5 report, ADR-080 D.4/D.5 ✅) reverts → **stop**; restore via cherry-pick before W2.P2
- `tomllib` unavailable AND `tomli` fallback fails → **stop**; document minimum-Python requirement

---

## 12. Commit Discipline (for E1.W2.B / W2.C implementation turns)

The future implementation turn MUST honor:

1. **Explicit `git add <path>` only** — never `git add -A` / `git commit -a`
2. **Expected staged set for W2.B**:
   - `ops_scripts/ci/check_runtime_certification.py` (new)
3. **Expected staged set for W2.C**:
   - `tests/unit/ops_scripts/ci/test_check_runtime_certification.py` (new)
4. Verify `git diff --cached --name-only` before each commit; only the intended path(s) must appear
5. Unrelated working-tree items (rtc-w2b byproducts, other plan files) mentioned in commit body but **NOT staged**
6. If any unrelated path is staged, **stop and report** — do not commit
7. Commit messages (suggested):
   - W2.B: `feat(runtime_cert): E1.W2 advisory runtime-certification gate module`
   - W2.C: `test(runtime_cert): E1.W2 advisory gate unit tests`

### 12.1 This plan's commit

- Staged set: **only** `.windsurf/plans/runtime-cert-e1w2-gate-module-9a4b2e.md`
- Commit subject: `plan(runtime_cert): E1.W2 advisory gate module`

---

## 13. Decisions Captured in This Plan

| # | Decision | Source | Status |
|---|---|---|---|
| 1 | Advisory default; `--strict` exists but is not CI-wired | E-AG-5, §8 | Hard constraint |
| 2 | Baseline TOML schema = `e1-baseline-v1`; closed field set | E-AG-2, §4 | Hard constraint |
| 3 | Baseline `mode` field gates `--strict` activation (defense in depth) | §8.1 | Proposed |
| 4 | Closed failure ontology: 10 codes; first failure does NOT short-circuit | §6 | Hard constraint |
| 5 | Verdict ordering: `reject < hold < certify`; `certify` is still non-promoting | §7 | Hard constraint |
| 6 | Read-only D.3 consumption via `read_cert_decision_records` | E-AG-1, §3.1, §9.2 | Hard constraint |
| 7 | No import of `write_cert_decision_record` | §9.3, §10 tests 19 | Hard constraint |
| 8 | No forbidden imports (scanner / emitter / app / `agentic_core.L*`) | §9.3, §10 tests 16–18 | Hard constraint |
| 9 | `runtime_certification_status == "NOT_CERTIFIED"` preserved throughout | §5.1, §7.1 | Hard constraint |
| 10 | TOML parsing via stdlib `tomllib`; `tomli` fallback only | §9.2, §10 test 23 | Hard constraint |
| 11 | Baseline file NOT created in E1.W2 | §1, E1.W3 deferral | Hard constraint |

---

## 14. Open Questions (for W2.P1 Author-Gate discussion)

None block implementation; all are optional refinements.

1. **JSON report output** — should the gate write `artifacts/runtime_cert/gate/<YYYY-Www>.json` on every run, or only when `--report <path>` is given? Recommendation: **only on explicit `--report`** — advisory mode should not accumulate disk artifacts by default. Resolve at W2.P2 start.
2. **`tomli` fallback minimum Python** — current repo baseline is Python 3.11 (has `tomllib`); should we drop the `tomli` fallback entirely? Recommendation: **keep fallback** for forward-portability with minimal cost (~2 lines). Resolve at W2.P2 start.
3. **`manifest_hash = ""` semantics** — empty string = skip check. Alternative: require field absence instead. Recommendation: **empty string**; TOML omits awkward on array-of-table entries. Already codified in §4.2.
4. **Per-app failures collection ordering** — within a single `RuntimeCertAppResult.failures`, the ordering is: (a) baseline-app validation, (b) ledger presence/emptiness, (c) status invariant, (d) verdict, (e) manifest hash. Deterministic. Confirmed at §10 test 24.
5. **Advisory-mode CLI verbosity** — should failures print to stderr or stdout? Recommendation: **stderr for failures, stdout for the pretty-printed summary**. Matches conventional CLI discipline. Resolve at W2.P2 start.

---

## 15. Boundaries (explicit)

- **E1.W2 does not create certification status.** No app gains `RUNTIME_CERTIFIED` or `FORMAL_EXCEPTION_VERIFIED`.
- **E1.W2 does not change scanner `runtime_mode`.** Phase F.
- **E1.W2 does not introduce new `runtime_mode` buckets.** Phase F.
- **E1.W2 does not write to any ledger.** D.3 is the sole writer by design.
- **E1.W2 does not touch app behavior.** No `apps_*` package is read or imported.
- **E1.W2 does not parse a live runtime-ADG snapshot.** C.6 scope.
- **E1.W2 does not emit markers or ledger events.**
- **E1.W2 does not open Phase F.** Phase F is independently gated.
- **E1.W2 does not wire into CI.** E1.W4 under a separate Author-Gate.
- **E1.W2 does not create the baseline TOML.** E1.W3 under a separate scoped prompt.

---

## 16. Final Disclaimer

> **This plan does not certify any app, does not modify scanner `runtime_mode`, does not add a CI gate, does not create the baseline TOML, and does not implement Phase F promotion.**
>
> E1.W2 is implementation planning for a future **advisory** runtime-certification gate module. The module, when eventually built under a separate scoped Author-Gate (W2.B / W2.C), will read Phase D cert-decision evidence in read-only fashion and emit a structured `RuntimeCertGateResult`. Nothing in this plan — not the module design, not the TOML schema, not the CLI contract, not the test plan, not the eventual exit codes — promotes any app's `runtime_certification_status` from `NOT_CERTIFIED` to any other value. The gate's advisory-mode CLI exit code is always `0`; the optional strict-mode exit code is a build signal, not a certification signal.
>
> Every `RuntimeCertGateResult` the future module constructs will carry `runtime_certification_status = "NOT_CERTIFIED"` — enforced through a `__post_init__` invariant. Every ledger row the module reads back will be re-validated by D.3's `_hydrate_one` (which invokes D.1's `__post_init__` + `compute_decision_id` tamper check). No-forbidden-imports tests will audit the module source to ensure it imports nothing from `tools.spine.scanner`, `agentic_core.L*`, or any `apps_*` package.
>
> **Phase F owns promotion and scanner bucket extension.** Phase E.1 (this waveline) feeds Phase F with evidence; Phase F decides and acts, under its own separate Author-Gate.
>
> **W2.B / W2.C implementation begins only after a separate scoped Author-Gate approves this plan.** E1.W3 (baseline seed) and E1.W4 (advisory→strict CI flip) remain independently gated on their own subsequent prompts / Author-Gates. Phase F remains gated on Phase E completion.
>
> **No implementation of W2.B or W2.C begins now. No files other than this plan are modified in the current turn.**

---

## 17. Recommended Next Step

**Author-Gate approval of this plan — then E1.W2.B (gate module) implementation under a separate scoped prompt.**

Suggested gate question:

> The E1.W2 plan proposes §4 baseline schema, §5 result model, §6 failure ontology, §7 verdict ordering, §8 advisory behavior, §9 public API, and §10 test plan (24 test cases). Approve as recommended, or surface specific alternatives (see §14 open questions 1–5) for re-scoping?

On approval, work proceeds in two commits:

1. **W2.B** — `ops_scripts/ci/check_runtime_certification.py` + minimal fixtures
2. **W2.C** — `tests/unit/ops_scripts/ci/test_check_runtime_certification.py` (24 tests)

E1.W3 (baseline TOML seed + first weekly evidence doc) and E1.W4 (advisory→strict CI flip) remain separately gated.

**Phase E.2+ and Phase F remain independently gated on their own Author-Gates. No E/F implementation work is authorized by this plan.**
