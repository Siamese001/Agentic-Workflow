---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\runtime-cert-e1w3-cli-ux-975c93.md'
original_relative_path: '_archive\\2026-05\\runtime-cert-e1w3-cli-ux-975c93.md'
source_sha256: f8adeac547a0fd7e1af03b1badd30cf9c1b45eb8de47c00c1b27baf290997aee
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Runtime Cert — E1.W3.1 Advisory Gate CLI Invocation UX (Planning Only)

- **Plan ID**: `runtime-cert-e1w3-cli-ux-975c93`
- **Status**: Planning — Author-Gate pending
- **Authored**: 2026-05-01
- **Branch**: `rtc-w2b-scenario-a-local-qwen-proof`
- **Parent plan**: [`runtime-cert-e1-fail-closed-ci-gate-c71f3d.md`](./runtime-cert-e1-fail-closed-ci-gate-c71f3d.md) — E-AG-1…5 APPROVED at commit `24f68e960b` (originally `14c4e9eb5b`)
- **Predecessor plan**: [`runtime-cert-e1w3-baseline-seed-4d82a1.md`](./runtime-cert-e1w3-baseline-seed-4d82a1.md)
- **Triggering evidence**: `docs/reports/runtime_cert/phase_e_runs/2026-W18.md` §4.3 (commit `14dfc9bac8`) — captured `ModuleNotFoundError: No module named 'tools'` during direct script invocation
- **ADR anchor**: [ADR-080 §11 E](../../docs/architecture/adr/ADR-080-runtime-cert-phase-d-planning.md)

> **Planning pass only.** This file authorizes **no** Python edits, **no**
> wrapper scripts, **no** packaging changes, **no** CI wiring, **no**
> pre-commit hook, **no** workflow edit, **no** scanner change, **no**
> emitter change, **no** app-behavior change, **no** ledger write, **no**
> baseline change, and **no** certification claim. E1.W3.1 implementation
> begins only after a separate scoped Author-Gate approves this plan.
> `runtime_certification_status` for every app remains `NOT_CERTIFIED`
> throughout and after this plan.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| W3.1.A | W3.1.P1 | Author-Gate approval of this plan | ~500 | E1.W2 gate committed; W18 evidence captured | Pending | User approves §1 preferred implementation + §3 scope boundaries |
| W3.1.B | W3.1.P2 | Implement `sys.path` bootstrap + add one test | ~700 | W3.1.A approved | Blocked on W3.1.A | Direct `python ops_scripts/ci/check_runtime_certification.py …` works from repo root without `PYTHONPATH`; all 36 existing tests still pass; 1 new test passes |
| W3.1.C | W3.1.P3 | Add 2-line note to W18 report confirming direct invocation fixed | ~200 | W3.1.B landed | Blocked on W3.1.B | `docs/reports/runtime_cert/phase_e_runs/2026-W18.md` §4.3.2 gains a postscript; commit is docs-only |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---:|---|---|
| W3.1.P1 | Plan approval | this plan file | Must pin `sys.path` approach as preferred and defer alternatives explicitly | ~500 | Pending |
| W3.1.P2 | Bootstrap + test | `ops_scripts/ci/check_runtime_certification.py`, `tests/unit/ops_scripts/ci/test_check_runtime_certification.py` | Bootstrap must run BEFORE the `from tools.runtime_cert.decisions...` import; must not introduce scanner/emitter/app imports; must keep module import-safe when imported from tests | ~700 | Blocked |
| W3.1.P3 | Postscript note | `docs/reports/runtime_cert/phase_e_runs/2026-W18.md` (append-only) | Must not rewrite §4.3.2; add a small follow-up subsection only | ~200 | Blocked |

---

## 1. Preferred Implementation

**⭐ Recommended**: add a minimal repo-root `sys.path` bootstrap inside
`ops_scripts/ci/check_runtime_certification.py`, placed **before** the
`from tools.runtime_cert.decisions...` import block.

### 1.1 Exact shape (for W3.1.B to implement)

```python
# ops_scripts/ci/check_runtime_certification.py (top of file, after module docstring)
import sys
from pathlib import Path

# --- begin E1.W3.1 CLI bootstrap ---
# When this module is executed as a script (python ops_scripts/ci/check_runtime_certification.py),
# Python places only the script's parent directory on sys.path. This module imports
# `tools.runtime_cert.decisions.*`, which lives at the repo root. Insert the repo root
# on sys.path BEFORE the imports below so direct invocation works without requiring
# operators to set PYTHONPATH=. manually. When imported (e.g. by tests or `python -m`),
# this block is a no-op because the repo root is already on sys.path.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
# --- end E1.W3.1 CLI bootstrap ---

from tools.runtime_cert.decisions.cert_decision_ledger import (
    ...
)
```

### 1.2 Properties

| Property | Value | Why |
|---|---|---|
| File touched | `ops_scripts/ci/check_runtime_certification.py` (existing) | No new file |
| Lines added | ~8 (bootstrap block + 2 blank-line separators) | Minimal surface |
| Imports introduced | `sys`, `pathlib.Path` (both stdlib) | No scanner / emitter / app imports — preserves all audit-test invariants |
| Side effects | `sys.path.insert(0, repo_root)` only when absent | Idempotent; no-op under `python -m` / pytest |
| Gate semantics | **Unchanged** | No gate result, failure code, verdict, or CLI flag touched |
| Non-promotion invariants | **Unchanged** | `RuntimeCertGateResult.__post_init__` untouched; all 6 status-pinning layers untouched |

### 1.3 Why `parents[2]`

`__file__` = `<repo>/ops_scripts/ci/check_runtime_certification.py`
- `parents[0]` = `<repo>/ops_scripts/ci/`
- `parents[1]` = `<repo>/ops_scripts/`
- `parents[2]` = `<repo>/` ← **repo root**

W3.1.B must include a test that asserts `_REPO_ROOT / "tools" / "runtime_cert"`
exists on disk, to catch any future directory-rename drift.

---

## 2. Alternatives Considered

| # | Option | Pros | Cons | Verdict |
|---|---|---|---|---|
| A | ⭐ **Repo-root `sys.path` bootstrap in the CLI module** | Documented command works unchanged; no new files; no packaging churn; idempotent under import | Adds 8 lines of stdlib-only bootstrap to a shipped Phase E.1 module | **Recommended** |
| B | Document `PYTHONPATH=.` in every runbook | Zero code change | Every operator must remember it weekly; the `--repo-root .` flag already implies repo root but PYTHONPATH must be set separately, which is confusing; also poisons Windows vs POSIX instructions | Rejected — high operator-UX cost forever |
| C | Require `python -m ops_scripts.ci.check_runtime_certification` | Clean canonical form; `python -m` adds CWD to sys.path | Requires `ops_scripts/__init__.py` + `ops_scripts/ci/__init__.py`; those don't exist today; adding them turns `ops_scripts` into a package and may ripple into other ad-hoc scripts in the tree | Rejected — larger blast radius than the problem |
| D | Create a wrapper `run_runtime_cert_gate.py` at repo root | Fires once, no module edit | Violates constitutional §31 (SSOT folder routing — no new Python at repo root except `conftest.py`); adds indirection; duplicates CLI arg parsing | Rejected — SSOT violation |
| E | Package `ops_scripts` as installable (`pyproject.toml` / `setup.py`) | Formal solution | Massive scope jump; requires install step for operators; contradicts the "repo-local tool" intent of `ops_scripts/` | Rejected — wrong altitude |
| F | Edit `conftest.py` or `pytest.ini` to add sys.path | Fixes tests only | Operators don't run pytest to invoke the gate; doesn't help direct invocation | Irrelevant — tests already work |

**Choice rationale**: Option A is the lowest-friction fix that preserves
the already-documented command in the W18 report, the E1.W3 plan, and
any future weekly report. Options B/C/D/E all either burden the
operator or expand scope beyond the trivial UX issue.

---

## 3. Scope Boundaries

> ⛔ E1.W3.1 touches **one file** (plus one test file and one docs
> append). It does **nothing else**.

| Surface | E1.W3.1 scope |
|---|---|
| `.pre-commit-config.yaml` | **NOT TOUCHED** |
| `.github/workflows/*.yml` | **NOT TOUCHED** |
| Any pre-commit hook invoking the gate | **NOT CREATED** |
| Any CI job invoking the gate | **NOT CREATED** |
| `docs/reference/runtime_certification/cert_baseline.toml` | **NOT TOUCHED** — baseline unchanged |
| Baseline `mode` field | **NOT FLIPPED** — `mode="advisory"` stays; strict activation remains E1.W4 scope |
| Any `artifacts/ledgers/*.sqlite` file | **NOT CREATED / NOT WRITTEN** |
| `tools/spine/scanner/` | **NOT TOUCHED** |
| `tools/spine/emitters/` | **NOT TOUCHED** |
| `apps_*` packages | **NOT TOUCHED** |
| Scanner `runtime_mode` enum | **NOT EXTENDED** — Phase F scope |
| `RUNTIME_CERTIFIED` / `FORMAL_EXCEPTION_VERIFIED` bucket recognition | **NOT INTRODUCED** — Phase F scope |
| Gate verdict logic, failure codes, verdict ordering | **NOT TOUCHED** |
| `RuntimeCertGateResult.__post_init__` non-promotion invariant | **NOT TOUCHED** |
| D.1 / D.2 / D.3 / D.4 code | **NOT TOUCHED** |
| `ops_scripts/__init__.py` / `ops_scripts/ci/__init__.py` | **NOT CREATED** (Option C path explicitly rejected) |
| Any wrapper script at repo root | **NOT CREATED** (Option D path explicitly rejected) |

`runtime_certification_status` for every app remains `NOT_CERTIFIED`
before, during, and after E1.W3.1.

---

## 4. Future Implementation Files (for W3.1.B and W3.1.C)

| Phase | File | Change kind | Lines |
|---|---|---|---:|
| W3.1.B | `ops_scripts/ci/check_runtime_certification.py` | Insert ~8-line bootstrap block near top (after module docstring, before `from tools...` imports) | ~+8 |
| W3.1.B | `tests/unit/ops_scripts/ci/test_check_runtime_certification.py` | Append 1 new test (+ helper if needed) | ~+25 |
| W3.1.C | `docs/reports/runtime_cert/phase_e_runs/2026-W18.md` | Append a short follow-up subsection (e.g., `§4.3.4 Direct-invocation fix landed`) referencing the W3.1.B commit SHA | ~+10 |

No other file is expected to change. If W3.1.B implementation discovers
it must also touch a conftest, a packaging marker, a workflow, or any
app/scanner file — **stop per §6**.

---

## 5. Test Plan (for W3.1.B)

### 5.1 New test (required)

**`test_direct_script_invocation_works_without_pythonpath`**

```python
def test_direct_script_invocation_works_without_pythonpath(tmp_path, monkeypatch):
    """Running the gate CLI as a script from repo root must succeed
    without requiring PYTHONPATH=. — E1.W3.1 bootstrap invariant."""
    # 1. Write a minimal valid baseline into tmp_path
    # 2. Invoke via subprocess.run([sys.executable, str(GATE_SCRIPT), '--repo-root', str(tmp_path), '--baseline', str(baseline_path)])
    #    with env = {} (or env purged of PYTHONPATH; PATH preserved)
    # 3. Assert returncode == 0 (advisory mode)
    # 4. Assert 'runtime_cert_status: NOT_CERTIFIED' in stdout
    # 5. Assert 'ModuleNotFoundError' NOT in stderr
```

This test **structurally validates** the bootstrap: if the bootstrap
ever regresses (import order broken, `parents[2]` wrong after a
directory rename, stdlib-only constraint violated), the test fails
with the exact symptom the W18 run captured.

### 5.2 Existing tests that must continue to pass (all 36)

| Test | Why it must still pass |
|---|---|
| `test_no_baseline_apps` … `test_deterministic_failure_ordering` (verdict logic) | Bootstrap must not alter any gate semantics |
| `test_gate_has_no_scanner_or_layer_imports[*]` (4 parametrized cases) | Bootstrap must not introduce scanner / L\d_ layer imports |
| `test_gate_has_no_emitter_imports` | Bootstrap must not introduce emitter imports |
| `test_gate_has_no_app_package_imports[*]` (5 parametrized cases) | Bootstrap must not introduce `apps_*` imports |
| `test_gate_does_not_import_write_cert_decision_record` | Bootstrap must not import ledger-writer APIs |
| `test_gate_result_has_non_certification_disclaimer` | `RuntimeCertGateResult` shape untouched |
| `test_gate_does_not_write_real_repo_ledgers` | No ledger writes introduced |
| `test_advisory_cli_returns_zero_on_failures` / `test_strict_cli_returns_one_on_failures` / `test_strict_cli_returns_two_on_gate_abstain` | CLI exit-code contract untouched |
| `test_report_writes_json_with_disclaimer` / `test_report_not_written_without_flag` | `--report` flag untouched |
| `test_strict_overridden_by_advisory_baseline` | `WARNING_STRICT_DOWNGRADED_BY_BASELINE` path untouched |
| `test_ledger_read_error_is_caught` | `sqlite3.Error` fail-soft untouched |
| `test_toml_parsing_uses_stdlib_tomllib` | Baseline loader untouched |

### 5.3 Cross-suite check (informational)

After W3.1.B lands, run the same scope as the recovery sweep:

```powershell
python -m pytest tests/unit/tools/runtime_cert/decisions/ `
    tests/unit/tools/runtime_cert/smoke/ `
    tests/unit/ops_scripts/ci/test_check_runtime_certification.py `
    -p no:xdist
```

Expected: **228 passed** (current 227 + the new bootstrap test).
Regression trip-wire: any D.1 / D.2 / D.3 / D.4 test failure during
this phase signals the bootstrap somehow affected a sibling module —
that is a §6 stop condition.

### 5.4 No broad tests

E1.W3.1 does **not** run the full repo test suite. Scope is limited to
the three suites above. Broad suites are reserved for E1.W4 (CI-wire
phase) or Phase F.

---

## 6. Stop Conditions

W3.1.B / W3.1.C halt and surface back for Author-Gate review if ANY of
these is detected:

- **Bootstrap requires scanner imports** (`tools.spine.scanner`,
  `agentic_core.L*_*`): stop. Audit-test invariant violated; Option A
  is the wrong tool. Escalate — possibly pivot to Option C (packaging).
- **Bootstrap changes gate result semantics**: stop. Any observable
  change to `RuntimeCertGateResult` fields, verdict ordering, failure
  codes, CLI exit codes, or the non-promotion disclaimer is out of
  scope.
- **Direct invocation requires package restructuring** (i.e.,
  `sys.path.insert` at `parents[2]` is insufficient and the fix also
  needs `ops_scripts/__init__.py`, `conftest.py` edits, or a
  `pyproject.toml` entry): stop. Per §2 Option C the packaging path is
  rejected; reconsider.
- **Fix would touch CI wiring** (`.pre-commit-config.yaml`,
  `.github/workflows/`, `ops_scripts/ci/run_contract_gates.py`, or any
  CI orchestrator): stop. CI wiring is E1.W4.
- **Fix would touch baseline TOML or baseline loader**: stop. Baseline
  is E1.W3 territory and frozen in this scope.
- **Any new audit-test in §5.2 fails** after the bootstrap lands: stop.
  The bootstrap regressed one of the 11 invariant classes.
- **Direct-invocation test still fails after bootstrap**: stop. Root
  cause is deeper than `sys.path`; the full problem needs rediagnosis.
- **W3.1.C docs append would require rewriting §4.3.2 of W18 report**:
  stop. §4.3.2 is honest historical evidence; do not rewrite history.
  Append a §4.3.4-style subsection instead.
- **Implementation would require a broad repo test sweep**: stop. §5.4
  forbids it.

---

## 7. Commit Discipline

### This plan's commit (W3.1.A — current turn)

- Staged set: **only** `.cursor/plans/runtime-cert-e1w3-cli-ux-975c93.md`
- Subject: `plan(runtime_cert): E1.W3.1 CLI invocation UX`

### W3.1.B implementation commit (future, separate scoped prompt)

- Staged set:
  - `ops_scripts/ci/check_runtime_certification.py`
  - `tests/unit/ops_scripts/ci/test_check_runtime_certification.py`
- Subject: `feat(runtime_cert): E1.W3.1 CLI sys.path bootstrap`

### W3.1.C docs-postscript commit (future, separate scoped prompt)

- Staged set: **only** `docs/reports/runtime_cert/phase_e_runs/2026-W18.md`
- Subject: `docs(runtime_cert): W18 postscript — direct invocation fixed`

### Unified discipline across all three commits

- Explicit `git add <path>` only — never `git add -A` / `git commit -a`
- Verify `git diff --cached --name-only` before every commit; only the
  intended paths must appear
- Unrelated working-tree items (rtc-w2b byproducts, guardian logs, prior
  plan files) are mentioned in commit body but **NOT staged**
- If any unrelated path is staged, **stop and report** — do not commit

---

## 8. Decisions Captured in This Plan

| # | Decision | Source | Status |
|---|---|---|---|
| 1 | Preferred fix = `sys.path` bootstrap in CLI module (Option A) | §1, §2 | Recommended; pending AG |
| 2 | `parents[2]` as repo-root derivation | §1.3 | Recommended; pending AG |
| 3 | Bootstrap uses stdlib only (`sys`, `pathlib.Path`) | §1.1 | Hard constraint |
| 4 | Bootstrap placed before `from tools...` imports | §1.1 | Hard constraint |
| 5 | No packaging / no `__init__.py` in `ops_scripts/` (Option C rejected) | §2 | Hard constraint |
| 6 | No wrapper script at repo root (Option D rejected) | §2 | Hard constraint |
| 7 | One new unit test: direct-invocation subprocess check | §5.1 | Recommended; pending AG |
| 8 | All 36 existing tests MUST continue to pass | §5.2 | Hard constraint |
| 9 | W3.1.C docs-postscript is append-only; §4.3.2 not rewritten | §6 | Hard constraint |
| 10 | No CI wiring, no workflow edit, no pre-commit hook | §3 | Hard constraint |
| 11 | Baseline TOML untouched | §3 | Hard constraint |
| 12 | `runtime_certification_status = NOT_CERTIFIED` preserved throughout | §3 | Hard constraint |
| 13 | No broad repo test sweep | §5.4 | Hard constraint |

---

## 9. Open Questions (for W3.1.A Author-Gate)

None block approval; all are optional refinements.

1. **Should the bootstrap guard against being imported from an unusual
   depth?** e.g., if someone symlinks the file into a different layout,
   `parents[2]` may not equal the repo root. **Recommendation: no.** A
   repo-layout change is a bigger event than E1.W3.1; the existing
   `tests/.../test_gate_has_no_scanner_or_layer_imports` tests would
   catch any resulting import-path chaos.
2. **Should W3.1.B also validate `_REPO_ROOT / "tools" / "runtime_cert"`
   existence at import time?** **Recommendation: no.** Raising on
   import when the `tools/` directory is missing is noisier than the
   `ModuleNotFoundError` the stdlib already raises. The bootstrap test
   in §5.1 covers the regression surface.
3. **Should the new test use `subprocess.run` or `runpy.run_path`?**
   **Recommendation: `subprocess.run`.** Closer to the real operator
   invocation; `runpy` shares the parent process's `sys.path` and would
   give a false-positive pass.
4. **Should W3.1.C postscript quote the W3.1.B commit SHA?**
   **Recommendation: yes.** Cheap provenance. The commit SHA is known
   at W3.1.C authoring time.
5. **Should E1.W3.1 also backfill a `python -m ops_scripts.ci...`
   invocation path?** **Recommendation: no.** `python -m` requires
   `__init__.py` files per Option C, which is explicitly rejected here.
   If operators prefer `python -m`, raise it as E1.W3.2 with its own
   Author-Gate.

---

## 10. Boundaries (explicit)

- **E1.W3.1 does not certify any app.** Every touch point preserves
  `runtime_certification_status = NOT_CERTIFIED`.
- **E1.W3.1 does not modify scanner `runtime_mode`.** Phase F.
- **E1.W3.1 does not introduce new `runtime_mode` buckets.** Phase F.
- **E1.W3.1 does not wire into CI.** E1.W4 under a separate Author-Gate.
- **E1.W3.1 does not edit `.pre-commit-config.yaml` or `.github/workflows/`.**
- **E1.W3.1 does not write to any ledger.** D.3 is the sole writer.
- **E1.W3.1 does not touch app behavior.** No `apps_*` package is read
  or modified.
- **E1.W3.1 does not parse a live runtime-ADG snapshot or run D.4
  smoke during authoring.**
- **E1.W3.1 does not emit markers.** No `CERT_DECISION:` /
  `ROUTER_DECISION:` / `DEFERRED_SCOPE:` / `NEXT_STEP:` events ship via
  this plan.
- **E1.W3.1 does not edit the baseline TOML.**
- **E1.W3.1 does not change gate semantics.** No verdict, failure code,
  CLI flag, or non-promotion invariant is touched.

---

## 11. Final Disclaimer

> **This plan does not certify any app, does not modify scanner
> `runtime_mode`, does not add a CI gate, does not edit
> `ops_scripts/ci/check_runtime_certification.py`, does not create a
> wrapper, does not restructure `ops_scripts/` as a package, and does
> not implement Phase F promotion.**
>
> E1.W3.1 is implementation planning for a single 8-line `sys.path`
> bootstrap inside the existing Phase E.1 advisory gate CLI module, so
> operators can run the already-documented command
> `python ops_scripts/ci/check_runtime_certification.py --repo-root . --baseline docs/reference/runtime_certification/cert_baseline.toml`
> without manually setting `PYTHONPATH=.`. Nothing in this plan — not
> the bootstrap, not the test, not the docs-postscript — promotes any
> app's `runtime_certification_status` from `NOT_CERTIFIED` to any
> other value, nor changes any gate decision, verdict, failure code,
> or CLI exit-code contract.
>
> **Phase F owns promotion and scanner bucket extension.** Phase E.1
> (this waveline) feeds Phase F with read-only evidence; Phase F
> decides and acts, under its own separate Author-Gate.
>
> **W3.1.B / W3.1.C implementation begins only after a separate scoped
> Author-Gate approves this plan.** E1.W4 (advisory→strict CI wiring)
> remains independently gated on its own subsequent prompt /
> Author-Gate. Phase F remains gated on Phase E completion.
>
> **No implementation of W3.1.B or W3.1.C begins now. No files other
> than this plan are modified in the current turn.**

---

## 12. Recommended Next Step

**Author-Gate approval of this plan — then W3.1.B (bootstrap + new
test) implementation under a separate scoped prompt, followed by
W3.1.C (W18 docs postscript) under its own scoped prompt.**

Suggested gate question for the follow-up turn:

> The E1.W3.1 plan recommends an 8-line `sys.path` bootstrap using
> `Path(__file__).resolve().parents[2]` in
> `ops_scripts/ci/check_runtime_certification.py`, placed before the
> `tools.runtime_cert.decisions.*` imports, plus one new unit test via
> `subprocess.run`. Alternatives — document-`PYTHONPATH`-only,
> `python -m` packaging, wrapper script, `pyproject.toml` install —
> are rejected in §2 with rationale. Approve Option A and the five
> §9 open-question recommendations? Or surface a different path?

On approval, work proceeds in two commits:

1. **W3.1.B** — modify `ops_scripts/ci/check_runtime_certification.py`
   (add bootstrap) and `tests/unit/ops_scripts/ci/test_check_runtime_certification.py`
   (add `test_direct_script_invocation_works_without_pythonpath`)
2. **W3.1.C** — append `§4.3.4 Direct-invocation fix landed` to
   `docs/reports/runtime_cert/phase_e_runs/2026-W18.md` with a
   reference to the W3.1.B commit SHA

**E1.W4 (advisory→strict CI wiring) remains independently gated on its
own Author-Gate.** Phase F remains gated on Phase E completion. **No
E.1 implementation beyond W3.1.B + W3.1.C, and no Phase F work, is
authorized by this plan.**
