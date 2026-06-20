---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\runtime-cert-d5-phase-d-closeout-5e9d2a.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\runtime-cert-d5-phase-d-closeout-5e9d2a.md'
source_sha256: 0b2f5ae9c75a772d4721f6825e3ab4ddcda639106cc12900719e7097712e979b
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Runtime Cert — Phase D.5 Closeout Report (Planning Only)

- **Plan ID**: `runtime-cert-d5-phase-d-closeout-5e9d2a`
- **Status**: Completed — 2026-05-01
- **Authored**: 2026-05-01
- **ADR anchor**: [ADR-080 §11 D.5](../../docs/architecture/adr/ADR-080-runtime-cert-phase-d-planning.md)
- **Predecessors** (all complete on `rtc-w2b-live-provider-allow-proof-b24f8e` / `rtc-w2-clean`):
  - D.1 schema — `tools/runtime_cert/decisions/cert_decision_record.py` (54 tests)
  - D.2 evaluator — `tools/runtime_cert/decisions/cert_decision_evaluator.py` (50 tests)
  - D.3 ledger writer — `tools/runtime_cert/decisions/cert_decision_ledger.py` + `.windsurf/schemas/cert_decision_ledger.schema.sql` (35 tests)
  - D.4 smoke harness — `tools/runtime_cert/smoke/cert_decision_smoke.py` (27 tests)

> **Planning pass only.** This file authorizes **no** closeout-report writing, **no** Python code, **no** new ledger, **no** schema change, **no** scanner edit, **no** CI gate, **no** emitter change, **no** app behavior change, and **no** certification claim. D.5 report authoring begins only after a separate Author-Gate approves this plan. `runtime_certification_status` for every app remains `NOT_CERTIFIED` throughout and after this plan.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| D5.W1 | D5.P1 | Author-Gate approval of this plan | ~800 | ADR-080 §11 permits per-sub-phase gating | Pending | User approves §10 AGs |
| D5.W2 | D5.P2 | Author the Markdown closeout report | ~3 500 | D.1–D.4 remain ✅ on disk at author time | Blocked on D5.W1 | `docs/reports/runtime_cert/phase_d_closeout/<YYYY-Www>.md` lands with all §3 required sections and every status invariant explicitly stated |
| D5.W3 | D5.P3 | Mark ADR-080 §11 D.5 ✅ + binding matrix row | ~400 | D5.W2 merged | Blocked on D5.W2 | ADR row marked ✅; §14 disclaimer preserved verbatim; binding matrix D.5 row added with report path |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---:|---|---|
| D5.P1 | Author-Gate approval | This plan file | Two trade-offs in §10 need explicit sign-off | ~800 | Pending |
| D5.P2 | Write closeout Markdown | `docs/reports/runtime_cert/phase_d_closeout/<YYYY-Www>.md` (new) | Must faithfully summarize D.1–D.4 code + tests without re-implementing them; every disclaimer verbatim from predecessor artifacts | ~3 500 | Blocked |
| D5.P3 | Doc updates | ADR-080 §11 D.5 row, binding matrix D.5 row | Preserve §14 / §16 disclaimers verbatim | ~400 | Blocked |

---

## 1. Purpose and Non-Goals

### Purpose

Plan a **documentation-only Phase D closeout report** that consolidates the D.1→D.2→D.3→D.4 chain into a single operator-facing Markdown artifact. The report is the human-readable handoff from Phase D to Phase E planning; it contains no new logic, no new ledger, no schema change, and no promotion signal.

### Non-goals

- **No scanner `runtime_mode` change.** Phase F owns that; D.5 never touches scanner code.
- **No CI gate.** Phase E owns that; D.5 never adds a pre-commit hook, workflow, or check-script.
- **No emitter change.** Runtime-ADG span emitters are untouched.
- **No certification promotion.** `runtime_certification_status` remains `NOT_CERTIFIED` everywhere the report references it.
- **No live runtime-ADG snapshot dependency.** The report is authored from code + committed test counts; no snapshot load, no C.8 closeout-Markdown parse, no D.4 smoke run is required to write it.
- **No Markdown→JSON duplication.** D.4's JSON smoke report remains the canonical machine-readable surface; D.5 is the human-readable surface only. The two do not share a writer.
- **No new ADR.** ADR-080 (Phase D design) is the anchor; ADR-050 is the cross-reference for the intelligence-ledger family pattern. No ADR-081 is proposed here.
- **No new dataclass, no new function, no new module.** Not one line of Python lands in D5.W2.
- **No app behavior change.** Every `apps_*` package is read-only.
- **No batching / automation.** One Markdown file per calendar week folder, authored by hand from the predecessor artifacts.

---

## 2. Report Input — Decision Captured

**Recommendation** (AG-1): D.5 is authored from **code + committed test evidence** in D.1–D.4 plus ADR-080 and the approved D.1–D.4 plan files. **No real C.8 closeout artifact is required** before writing D.5.

Rationale:

- **D.5 documents Phase D, not any specific certification decision.** The report summarizes what shipped (the schema, the evaluator, the ledger writer, the smoke harness), not the output of running them against a real app. A real C.8 closeout is an *input* to the D.1–D.3 pipeline; D.5 is a *narrative about that pipeline existing*.
- **C.8 already has its own closeout artifact.** `write_phase_c_closeout_markdown` emits `docs/reports/runtime_cert/phase_c_closeout/<YYYY-Www>.md`. Re-parsing or re-wrapping it in D.5 would duplicate content with no downstream consumer.
- **D.4's smoke runs prove the wiring end-to-end, and those runs already happen in the test suite.** Test counts from `tests/unit/tools/runtime_cert/decisions/` + `tests/unit/tools/runtime_cert/smoke/` (191 passing as of 2026-05-01) are sufficient evidence the chain composes correctly.
- **Keeping D.5 free of C.8 input decouples the doc cadence from app-readiness cadence.** A Phase D closeout can be authored immediately; a real C.8 closeout per-week is a separate operational rhythm.

Tests 1–27 in `test_cert_decision_smoke.py` — especially `test_smoke_certify_verdict_still_not_certified`, `test_smoke_idempotent_second_run`, and `test_smoke_does_not_write_to_real_artifacts_ledgers` — are the load-bearing evidence cited by the report.

---

## 3. Report Format — Decision Captured

**Recommendation** (AG-2): **Markdown only.** No JSON writer. No new code.

Rationale:

- **Matches C.6/C.7/C.8 weekly-report precedent.** Every existing Phase C closeout artifact is Markdown; Phase D's closeout should follow the same convention.
- **D.4 already emits the machine-readable surface.** `write_cert_decision_smoke_report` emits JSON with `schema_version="d4-smoke-v1"`; future D.5-consumer tooling parses that, not the closeout Markdown. Closeout Markdown is for humans.
- **No code change means no test change.** Zero risk of regression in D.1–D.4; zero new attack surface.
- **Target path follows the C.8 closeout pattern**:
  ```
  docs/reports/runtime_cert/phase_d_closeout/<YYYY-Www>.md
  ```
  `<YYYY-Www>` is ISO week-of-year (e.g. `2026-W18` for the week of 2026-05-01). First D.5 report: `2026-W18.md`.

---

## 4. Proposed Target File

```
docs/reports/runtime_cert/phase_d_closeout/<YYYY-Www>.md
```

First expected path: `docs/reports/runtime_cert/phase_d_closeout/2026-W18.md`.

Sibling to `docs/reports/runtime_cert/phase_c_closeout/` (when that directory exists). Respects the `validate_report_location.py` SSOT contract (`docs/reports/` for all human-readable reports — `.windsurf/rules/plan-location.md` companion invariant).

No new test is added. No existing test touches `docs/reports/`; if a docs-lint step exists elsewhere in pre-commit, the Markdown must pass it (link-check, heading levels).

---

## 5. Required Report Content (§3 of the prompt)

The report MUST include all of the following sections, in this order. Every section references the predecessor artifact by absolute path or line range — no narrative is invented beyond what predecessor artifacts prove.

### 5.1 Front matter

```markdown
# Phase D Runtime-Certification Closeout — Week of <YYYY-MM-DD>

- **Week**: <YYYY-Www>
- **Author**: Cascade (documentation pass only)
- **Status**: Reporting
- **Scope**: Phase D — cert-decision schema, evaluator, ledger writer, smoke harness
- **Certification outcome**: **NONE**. Phase D does not certify apps.
- **ADR anchor**: ADR-080
- **Related ADR**: ADR-050 (intelligence-ledger family pattern)
- **Phase E boundary**: out of scope (fail-closed CI gate)
- **Phase F boundary**: out of scope (scanner `runtime_mode` promotion)
```

### 5.2 Phase D scope and non-goals

- Verbatim restate of ADR-080 §4 non-goals.
- Explicit call-out: D.1–D.4 are *infrastructure*, not certification decisions.
- Triple-check layers of non-promotion enforcement:
  - C.8 `PhaseCCloseoutReport.__post_init__`
  - D.1 `CertificationDecisionRecord.__post_init__`
  - D.3 SQL `CHECK (runtime_certification_status_before = 'NOT_CERTIFIED')` + `CHECK (runtime_certification_status_after = 'NOT_CERTIFIED')`
  - D.3 read-back re-validation via D.1 `__post_init__` + `decision_id` integrity check
  - D.4 `CertDecisionSmokeReport.__post_init__`

### 5.3 D.1 schema summary

- Module: `tools/runtime_cert/decisions/cert_decision_record.py`
- Public surface: `CertificationDecisionRecord` (19 fields, frozen); `NOT_CERTIFIED`, `VERDICT_CERTIFY`/`VERDICT_HOLD`/`VERDICT_REJECT`, `EVIDENCE_KIND_R3`/`EVIDENCE_KIND_BTC`/`EVIDENCE_KIND_FORMAL_EXCEPTION`/`EVIDENCE_KIND_SKIPPED`; `compute_decision_id(app_name, manifest_hash, closeout_report_hash)`; `make_certification_decision_record`; `to_dict` / `to_json`.
- Invariants enforced at construction (verbatim from `__post_init__`).
- Test count: 54 in `tests/unit/tools/runtime_cert/decisions/test_cert_decision_record.py`.
- Hard rule: **schema only — no business logic, no I/O, no ledger writes.**

### 5.4 D.2 evaluator summary

- Module: `tools/runtime_cert/decisions/cert_decision_evaluator.py`
- Public surface: `evaluate_phase_c_closeout(report, history=(), *, closeout_report_id=None, closeout_report_hash=None) -> tuple[CertificationDecisionRecord, ...]`; `wilson_lower_bound(successes, n, z=1.96)`; `derive_closeout_report_hash(report)`.
- Closed 12-reason ontology: `CLOSEOUT_MISSING`, `SAMPLE_SIZE_TOO_SMALL`, `WILSON_BELOW_THRESHOLD`, `Z_SCORE_BELOW_THRESHOLD`, `UPLIFT_NOT_POSITIVE`, `CRITICAL_BLOCKERS_PRESENT`, `FORBIDDEN_SPAN_VIOLATION`, `FORMAL_CONTROL_MISSING_OR_FAILED`, `MANIFEST_HASH_DRIFT`, `AMBIGUOUS_EVIDENCE`, `NOT_TRACE_OBSERVED_READY`, `NOT_FORMAL_EXCEPTION_OBSERVED_READY`.
- Thresholds (ADR-080 §7): `MIN_N=30`, `MIN_WILSON_LOWER=0.60`, `MIN_Z_SCORE=1.96`, `MIN_UPLIFT=0.0` strict.
- Verdict semantics — `certify` is NOT a certification; every record carries `runtime_certification_status_after == NOT_CERTIFIED` regardless of verdict, enforced structurally by D.1.
- Test count: 50 in `test_cert_decision_evaluator.py`; load-bearing coverage: `test_certify_when_all_thresholds_pass`, `test_certify_still_keeps_status_after_not_certified`, `test_no_filesystem_or_sqlite_access`.
- Hard rule: **pure — no I/O, no sqlite, no subprocess.**

### 5.5 D.3 ledger writer summary

- Module: `tools/runtime_cert/decisions/cert_decision_ledger.py`
- DDL: `.windsurf/schemas/cert_decision_ledger.schema.sql` (21 columns, 3 indexes, 2 `CHECK` constraints)
- Public surface: `CertDecisionLedgerWriteResult` (frozen); `ledger_path_for_app(app_name, *, repo_root=None)`; `ensure_cert_decision_ledger(path)`; `write_cert_decision_record(record, *, repo_root=None, fail_soft=True)`; `read_cert_decision_records(app_name, *, repo_root=None)`.
- Per-app file layout: `artifacts/ledgers/cert_decision_<app_name>.sqlite` — one file per app, not a shared ledger.
- Idempotency: `INSERT OR IGNORE` on `decision_id` + `total_changes==0` pattern.
- Fail-soft: `sqlite3.Error` absorbed into `skipped=True`; `TypeError`/`ValueError` always raise. `CERT_DECISION_LEDGER_BYPASS=1` env var.
- Tamper detection: read-back re-validates via D.1 `__post_init__` + re-computes `compute_decision_id` — any direct SQL UPDATE to status or record_json surfaces as `ValueError` on read.
- Registry discipline (per ADR-050): **NOT registered in `tools/ledgers/schema_registry.py` LEDGER_REGISTRY** — `apply_schema.py` iterates the registry only and never auto-applies the D.3 DDL. Verified by `test_ddl_not_registered_in_ledger_registry`.
- Test count: 35 in `test_cert_decision_ledger.py`.

### 5.6 D.4 smoke harness summary

- Module: `tools/runtime_cert/smoke/cert_decision_smoke.py`
- Public surface: `CertDecisionSmokeReport` (frozen, 17 fields); `run_cert_decision_smoke(report, *, repo_root, history=(), fail_soft=True) -> CertDecisionSmokeReport`; `write_cert_decision_smoke_report(report, output_path) -> Path`.
- Pipeline: C.8 input → D.2 evaluate → D.3 write (per record) → D.3 read-back (per distinct app, first-seen order).
- Closed 6-reason ontology: `WRITE_COUNT_MISMATCH`, `LEDGER_WRITE_SKIPPED`, `MISSING_READBACK`, `STATUS_NOT_NOT_CERTIFIED`, `DECISION_COUNT_DOES_NOT_MATCH_INPUT`, `READBACK_DECISION_ID_MISMATCH`.
- Diagnostics-not-errors: `failure_reasons` is informational; the harness never raises on partial failure.
- JSON writer: `schema_version="d4-smoke-v1"`, `disclaimer` containing "no runtime certification performed", `runtime_certification_status="NOT_CERTIFIED"`. `Path` → `str`; `write_results` + `read_back_records` → nested dicts.
- `repo_root` is a REQUIRED keyword argument. Tests use `tmp_path`; no real `artifacts/ledgers/` writes in the test suite (verified by `test_smoke_does_not_write_to_real_artifacts_ledgers`).
- Non-promotion triple/quintuple check: five independent enforcement layers (see §5.2).
- Test count: 27 in `test_cert_decision_smoke.py`.

### 5.7 Test-count table

| Phase | Module | Tests | Status |
|---|---|---:|---|
| D.1 | `tools/runtime_cert/decisions/cert_decision_record.py` | 54 | ✅ passing |
| D.2 | `tools/runtime_cert/decisions/cert_decision_evaluator.py` | 50 | ✅ passing |
| D.3 | `tools/runtime_cert/decisions/cert_decision_ledger.py` + DDL | 35 | ✅ passing |
| D.4 | `tools/runtime_cert/smoke/cert_decision_smoke.py` | 27 | ✅ passing |
| **Total (Phase D)** | | **166** | **✅** |
| (Reference: Phase D + pre-existing C.6 live-trace smoke) | combined sweep | **191** | ✅ |

Verification command: `python -m pytest tests/unit/tools/runtime_cert/decisions/ tests/unit/tools/runtime_cert/smoke/ -p no:xdist`.

### 5.8 No-certification disclaimer (verbatim)

> **This report authorises no certification.** Every `CertificationDecisionRecord` produced by the D.2 evaluator, persisted by the D.3 writer, or read back by the D.4 harness carries `runtime_certification_status_before == runtime_certification_status_after == NOT_CERTIFIED`. This is enforced at **five layers**: C.8 input construction, D.1 `__post_init__` at decision construction, D.3 SQL `CHECK` constraint at persistence, D.3 read-back re-validation via D.1's invariants, and `CertDecisionSmokeReport.__post_init__` on the smoke report itself.
>
> A `verdict == "certify"` row in any ledger or smoke report is **not** a certification. It is a statement that, if this codebase were at Phase F, the Phase F promotion workflow would promote the app. Phase F does not exist. No scanner `runtime_mode` is changed. No CI gate is added. No runtime emitter is modified. No app behavior changes.

### 5.9 Status invariant table

| Layer | Enforcement | File / Location | Mechanism |
|---|---|---|---|
| C.8 input | `PhaseCCloseoutReport.__post_init__` | `tools/runtime_cert/reports/phase_c_closeout.py` | `runtime_certification_status != NOT_CERTIFIED` → `ValueError` |
| D.1 construction | `CertificationDecisionRecord.__post_init__` | `tools/runtime_cert/decisions/cert_decision_record.py` | Both status fields must equal `NOT_CERTIFIED` |
| D.2 evaluator | Structural — every record it constructs goes through D.1 | `tools/runtime_cert/decisions/cert_decision_evaluator.py` | Inherits D.1 guard; cross-checks input `report.runtime_certification_status` |
| D.3 SQL | `CHECK` constraints | `.windsurf/schemas/cert_decision_ledger.schema.sql` | `CHECK (runtime_certification_status_before = 'NOT_CERTIFIED')` + same for `_after` |
| D.3 read-back | `_hydrate_one` + D.1 `__post_init__` + `compute_decision_id` recheck | `tools/runtime_cert/decisions/cert_decision_ledger.py` | Direct SQL tamper surfaces as `ValueError` on read |
| D.4 smoke | `CertDecisionSmokeReport.__post_init__` | `tools/runtime_cert/smoke/cert_decision_smoke.py` | Smoke report status pin + read-back row status pin + disclaimer phrase pin |

### 5.10 Negative evidence — what did NOT change

| Surface | Expected in D.1–D.4 | What actually happened | Evidence |
|---|---|---|---|
| Scanner classification | no change | no change | No file under `tools/spine/scanner/` or `agentic_core/` was modified across the D.1–D.4 commits; verified by `git log --name-only` across the commits that landed D.1, D.2, D.3, D.4 |
| CI gate | no new gate | no new gate | No file added or modified under `ops_scripts/ci/`; `.pre-commit-config.yaml` untouched |
| Emitter | no change | no change | No runtime-ADG span emitter modified; `tools/runtime_adg/` untouched |
| App behavior | no change | no change | No file under `apps_*/` modified |
| LEDGER_REGISTRY | D.3 DDL stays out of the registry | out | `tools/ledgers/schema_registry.py` unchanged; verified by `test_ddl_not_registered_in_ledger_registry` |
| Real-repo `artifacts/ledgers/` | no test-time writes | no writes | Verified by `test_smoke_does_not_write_to_real_artifacts_ledgers`; manual check via `Get-ChildItem artifacts/ledgers/cert_decision_*.sqlite` shows zero files after the full D.1–D.4 sweep |
| Forbidden imports in D.4 | no `agentic_core.L*` / `ops_scripts.ci` / `tools.spine.scanner` | none | Verified by `test_smoke_no_scanner_ci_emitter_imports` (regex-scanning module source) |

### 5.11 Known limitations

The report explicitly acknowledges these gaps so Phase E and Phase F planning starts with honest context:

1. **No real-app dry-run evidence.** The D.4 smoke harness has not been exercised against a real C.8 closeout report outside pytest. That is an operator task and belongs to a later ad-hoc D-review, not to D.5.
2. **Thresholds are provisional.** ADR-080 §12 Q2 and Q3 remain deferred to D.5 calibration. The `MIN_N=30 / MIN_WILSON_LOWER=0.60 / MIN_Z_SCORE=1.96` floor comes from calibration-report precedent (`intelligence-ledger-family.md` §5) but has not been validated against a real Phase D cohort. The report notes this as "provisional — needs calibration data before any Phase F promotion cycle".
3. **The `uplift` baseline uses the most-recent prior for the same app regardless of manifest_hash.** That is a deliberate D.2 choice (captured in the D.2 plan) but it means manifest-drifted history reduces baseline signal. Calibration to watch for.
4. **No router-event emission.** Constitutional rule §29 requires `ROUTER_DECISION:` markers for routing decisions; Phase D is not a router but **is** a decision pipeline. ADR-080 §6 mentions a possible `CERT_DECISION:` marker per decision. D.3 does NOT emit such a marker today; D.4 does NOT emit one either. Whether to add one is deferred — the closeout report notes it as "open design question; not a D.5 code change".
5. **No ledger-rotation / archival policy.** Per-app SQLite files grow forever. Not a D.5 concern, but documented for Phase E/F operational planning.
6. **No concurrent cross-process locking.** D.3 uses an in-process `threading.Lock` keyed on `db_path`. Two processes writing the same ledger file race at the SQLite layer; `INSERT OR IGNORE` absorbs duplicates but other transient errors fall through to `fail_soft`. Documented; not a D.5 code change.

### 5.12 Phase E/F boundary (explicit)

Verbatim language the report MUST include:

> **Phase E owns the fail-closed CI gate.** `ops_scripts/ci/check_runtime_certification.py` (SSOT-folder-compliant name) will run D.2 on the last-N-days of traces for any app claiming `TRACE_OBSERVED` or higher. Phase D does NOT add a CI gate.
>
> **Phase F owns scanner `runtime_mode` bucket extension and the promotion workflow.** Scanner extension recognizing new buckets (`RUNTIME_CERTIFIED`, `FORMAL_EXCEPTION_VERIFIED`) and the promotion workflow updating scorecard + Notion ADR + memory are Phase F, not Phase D.
>
> **Phase D does not certify apps.** Phase D does not modify scanner `runtime_mode`. Phase D does not add CI gates. Phase D does not change app behavior. Every decision record carries `runtime_certification_status_after == NOT_CERTIFIED`, persisted verbatim by D.3's SQL `CHECK`, re-validated on every read-back.

### 5.13 Next-phase boundary

The report closes with:

> **Next step: Phase E planning only.** Phase E is a separate Author-Gate. No Phase E work is authorized by this closeout.
>
> **Phase F remains gated on Phase E completion.** No Phase F work is authorized by this closeout.

---

## 6. ADR References — Decision Captured

**Recommendation** (AG-3): cite **ADR-080** (primary) and **ADR-050** (cross-reference).

- **ADR-080** (`docs/architecture/adr/ADR-080-runtime-cert-phase-d-planning.md`) is the Phase D design ADR and the direct anchor. D.5 marks row §11 D.5 ✅ after the report lands.
- **ADR-050** (`docs/architecture/adr/ADR-050-intelligence-ledger-family.md`) is the intelligence-ledger family ADR. It is the relevant runtime/ledger architecture reference because:
  - D.3's per-app cert-decision ledger is *conceptually* a new ledger in the same family (shared fail-soft contract, same idempotency pattern keyed on a domain-specific hash, same bypass-env-var discipline).
  - D.3 deliberately DECLINED to register in `LEDGER_REGISTRY` — that decision is only meaningful when referenced against ADR-050's contract for what "being in the registry" means.
  - Constitutional rule §29 (closed-loop router enforcement) explicitly ties certification decisions to ADR-050's emit-ledger-event contract for future router-style integration.
- **ADR verification step**: before writing the report, confirm `docs/architecture/adr/ADR-050-intelligence-ledger-family.md` exists and describes the ledger-family writer contract. If inspection reveals ADR-050 is *not* in fact the relevant reference, the report author MUST swap in the correct ADR (e.g., ADR-023 for runtime-exit control, ADR-074 for ADG 3-bucket unified, ADR-079 for L2 graph-layer consumption contract) and note the reason for the swap in the report's front-matter `Related ADR:` line.
- **No new ADR**. D.5 is a documentation-only report; if it surfaces a design concern that needs ADR-level capture (e.g., future `CERT_DECISION:` marker schema), that ADR is a *separate* Author-Gate.

---

## 7. Phase E / Phase F Boundary (restated for Cascade clarity)

Repeating the boundary rules so the implementation turn cannot blur them:

- Phase E introduces `ops_scripts/ci/check_runtime_certification.py`. D.5 does not.
- Phase E hooks that gate into `.pre-commit-config.yaml` and CI workflows. D.5 does not.
- Phase F extends the spine scanner to recognize new `runtime_mode` buckets. D.5 does not.
- Phase F introduces the promotion workflow (scorecard, Notion ADR, memory writeback). D.5 does not.
- Phase D does not certify apps. D.5 does not change that.
- Phase D does not modify scanner `runtime_mode`. D.5 does not change that.
- Phase D does not add CI gates. D.5 does not change that.

---

## 8. Commit Discipline (for D5.W2 report-authoring turn)

The next turn (D.5 report authoring, after Author-Gate approval) MUST honor:

1. **Explicit `git add <path>` only** — never `git add -A` / `git commit -a`.
2. **Expected staged set** — exactly these paths:
   - `docs/reports/runtime_cert/phase_d_closeout/<YYYY-Www>.md` (new)
   - `docs/architecture/adr/ADR-080-runtime-cert-phase-d-planning.md` (D.5 row ✅)
   - `docs/reference/runtime_certification/contract_span_binding_matrix.md` (D.5 row added)
3. **Verify staging before commit** — run `git diff --cached --name-only` and confirm only those three paths are listed.
4. **Unrelated working-tree changes** — mention in the commit message body but DO NOT stage. Known unrelated state on this branch:
   - `M agentic_core/L0_routing/logs/guardian_report.json` (auto-updated guardian artifact)
   - `?? tests/runtime/test_live_provider_attestation.py`, `?? tests/runtime/test_live_provider_readiness.py` (separate rtc-w2b workflow)
   - `?? .windsurf/plans/rtc-w2b-live-provider-allow-proof-b24f8e.md` (separate plan)
   - Any new `?? .windsurf/plans/runtime-cert-d5-phase-d-closeout-*.md` produced by this current planning turn (will become staged by the *current* turn, not D5.W2's).
5. **If any unrelated path is staged**, stop and report — do not commit.
6. **Commit message** — explicit per-phase summary with test counts and hard-constraint confirmation, mirroring the D.3 / D.4 commit bodies. One-liner subject + structured `-m` body sections: summary, files added, public surface (N/A for D.5), content summary, verification, hard constraints, staging discipline, recommended next phase.

---

## 9. Tests — None Required

Per the prompt: **no tests required** unless a docs-lint hook exists.

- **Docs-lint status**: No dedicated `pre-commit` hook currently lints `docs/reports/runtime_cert/` Markdown beyond generic whitespace checks. If a future hook is added (e.g., a broken-link checker), the D.5 Markdown must pass it; no preemptive test is required now.
- **No Python tests added.** D.5 is not code.
- **No D.4 re-run required.** The 191-passing sweep is treated as settled evidence at the time of report authoring; the report merely cites the count.

---

## 10. Author-Gate Trade-offs (AG-10 shape)

Three decisions the plan must get explicit sign-off on before D.5 report authoring begins.

### AG-1: Report input

- **⭐ Recommended**: author D.5 from **code + committed test evidence in D.1–D.4 + ADR-080 + approved plans**. No real C.8 closeout artifact required.
- **Alternative A**: require a C.8 closeout artifact for the current week as input before writing D.5. **Rejected** — D.5 documents the *pipeline* (the schema, evaluator, writer, smoke), not the output of running it against a specific week's apps. C.8 has its own weekly cadence.
- **Alternative B**: require a D.4 smoke run against a live C.8 closeout before D.5. **Rejected** — smoke runs are exercised in the test suite already; a manual run is an operator task, not a D.5 prerequisite.

### AG-2: Report format

- **⭐ Recommended**: **Markdown only**. No JSON writer. No new code.
- **Alternative A**: JSON sidecar next to the Markdown. **Rejected** — D.4 already emits `schema_version="d4-smoke-v1"` JSON via `write_cert_decision_smoke_report`; adding a second JSON surface duplicates the machine-readable contract.
- **Alternative B**: Markdown primary + YAML front-matter metadata block. **Deferred** — no downstream consumer asks for YAML; can be added later if D.5 calibration tooling materializes.

### AG-3: ADR references

- **⭐ Recommended**: cite **ADR-080** as primary anchor + **ADR-050** as the intelligence-ledger-family cross-reference.
- **Alternative A**: cite only ADR-080. **Rejected** — D.3's registry decision and constitutional §29 ledger-family context are only legible against ADR-050.
- **Alternative B**: add ADR-023 (runtime HITL exit control). **Rejected** — Phase D operates at author/harness layer, not runtime HITL; conflation is forbidden by `author-gate-enforcement.md` front-matter.
- **Pre-flight verification step**: the report-authoring turn MUST open `docs/architecture/adr/ADR-050-intelligence-ledger-family.md` and confirm it describes the ledger-family contract. If inspection reveals ADR-050 is unrelated (e.g. renamed), the author swaps in the correct ADR and documents the swap.

---

## 11. Test Plan — Summary Table

Not applicable — no code, no tests. The "evidence table" that appears in the report is §5.7 (test-count table), which *cites* existing D.1–D.4 test counts rather than adding new ones.

---

## 12. Stop Conditions

Implementation halts and surfaces back for Author-Gate review if any of these is detected during D5.W2:

- Any of `tools/runtime_cert/decisions/cert_decision_record.py`, `cert_decision_evaluator.py`, `cert_decision_ledger.py`, `.windsurf/schemas/cert_decision_ledger.schema.sql`, `tools/runtime_cert/smoke/cert_decision_smoke.py` is missing → **stop**.
- ADR-080 §11 shows any of D.1, D.2, D.3, D.4 NOT marked ✅ → **stop**.
- Writing D.5 begins to require any Python code change → **stop**.
- Writing D.5 begins to require any ledger schema change → **stop**.
- Writing D.5 begins to require any scanner / CI / emitter / app-behavior change → **stop**.
- ADR-050 inspection reveals it is not the relevant runtime/ledger architecture reference AND no suitable alternative exists → **stop and propose a new ADR via a separate Author-Gate**.
- The D.1–D.4 test sweep fails at the time of authoring → **stop**; D.5 cannot cite broken evidence.

---

## 13. Decisions Captured in This Plan

| # | Decision | Source | Status |
|---|---|---|---|
| 1 | Input: code + committed test evidence — no C.8 artifact prerequisite | §2, §10 AG-1 | Recommended; pending AG |
| 2 | Format: Markdown only, no JSON writer, no code | §3, §10 AG-2 | Recommended; pending AG |
| 3 | Target path: `docs/reports/runtime_cert/phase_d_closeout/<YYYY-Www>.md` | §4 | Recommended; pending AG |
| 4 | Content: 13 required sections per §5 | §5 | Hard constraint — all sections MUST appear |
| 5 | ADR references: ADR-080 primary + ADR-050 cross-ref | §6, §10 AG-3 | Recommended; pending AG |
| 6 | Phase E / Phase F boundary statements verbatim | §7, §5.12 | Hard constraint |
| 7 | No new tests | §9 | Hard constraint |
| 8 | Explicit commit discipline: 3 intended files, no `git add -A` | §8 | Hard constraint |
| 9 | No code, no ledger, no schema, no scanner, no CI, no emitter, no app change | prompt | Hard constraint |
| 10 | `runtime_certification_status == NOT_CERTIFIED` preserved throughout | §5.2, §5.8, §5.9 | Hard constraint |

---

## 14. Unresolved Questions

None block implementation. These surface for Author-Gate consideration:

1. **Cadence**: should D.5 be weekly (matching C.8) or one-time-only (Phase D is a fixed infrastructure delivery)? Recommendation: **one-time-only** for the initial Phase D delivery; future operational weekly reports (if they emerge) belong to Phase F's review cadence, not Phase D. Resolve at D5.P2 start.
2. **`CERT_DECISION:` marker emission**: ADR-080 §6 mentions a possible marker per decision; D.3/D.4 do NOT emit one. Should the D.5 closeout explicitly recommend opening a follow-up Author-Gate for that, or leave it to Phase E / Phase F? Recommendation: **note as a "known gap / open design question" in §5.11 and do not schedule it in D.5**. Resolve at D5.P2 start.
3. **Calibration report seeding**: should the D.5 closeout emit a seed row into any calibration-report directory (e.g., `docs/reports/calibration/runtime_cert/`)? Recommendation: **no** — that's Phase F's responsibility once real promotion data exists. Resolve by deferring.
4. **Cross-link to C.8 closeout Markdown**: if a current-week C.8 closeout exists on disk, D.5 should link to it. If none exists (as of 2026-W18), say so. Resolve by inspecting `docs/reports/runtime_cert/phase_c_closeout/` at authoring time.

---

## 15. Boundaries (explicit)

- **D.5 does not create certification status.** No app gains `RUNTIME_CERTIFIED` or `FORMAL_EXCEPTION_VERIFIED`. Every status reference in the closeout report says `NOT_CERTIFIED`.
- **D.5 does not change scanner `runtime_mode`.** Phase F (out of scope) owns that.
- **D.5 does not add a CI gate.** Phase E (out of scope) owns that.
- **D.5 does not touch real app behavior.** No `apps_*` package is read or modified.
- **D.5 does not add Python code, tests, or ledger rows.** Documentation only.
- **D.5 does not parse a C.8 closeout Markdown.** It cites the D.1–D.4 code + tests directly.
- **D.5 does not emit markers or ledger events.** No new `CERT_DECISION:` / `ROUTER_DECISION:` / `DEFERRED_SCOPE:` / `NEXT_STEP:` events ship via this plan.
- **D.5 does not open Phase E or Phase F.** Those are independently gated.

---

## 16. Explicit No-Certification Disclaimer

> **This plan authorises no certification.** Every `CertificationDecisionRecord` produced by the D.2 evaluator, persisted by the D.3 writer, or read back by the D.4 harness carries `runtime_certification_status_before == runtime_certification_status_after == NOT_CERTIFIED`. This is enforced at **five layers**: C.8 input construction, D.1 `__post_init__` at decision construction, D.3 SQL `CHECK` constraint at persistence, D.3 read-back re-validation via D.1's invariants, and `CertDecisionSmokeReport.__post_init__` on the smoke report itself.
>
> A `verdict == "certify"` row in any ledger or smoke report is **not** a certification. It is a statement that, if this codebase were at Phase F, the Phase F promotion workflow would promote the app. Phase F does not exist. No scanner `runtime_mode` is changed. No CI gate is added. No runtime emitter is modified. No app behavior changes.
>
> D.5 report authoring begins **only after** a separate Author-Gate approves this plan, per ADR-080 §11. Phase E remains gated on its own Author-Gate. Phase F remains gated on Phase E completion.

---

## 17. Recommended Next Step

**Phase D.5 report authoring — but only after Author-Gate approval of this plan.**

Suggested gate question for the follow-up turn:

> The D.5 plan proposes three trade-offs (AG-1 through AG-3 in §10).
> Approve all three as recommended? Or surface specific alternatives for
> re-scoping?

On approval, work proceeds in three commits per §Wave Structure:

1. **D5.W2 commit 1**: `docs/reports/runtime_cert/phase_d_closeout/<YYYY-Www>.md` with all 13 required §5 sections, verbatim disclaimers, test-count table citing 191-passing sweep, Phase E / Phase F boundary statements.
2. **D5.W3 commit 2**: ADR-080 §11 D.5 row marked ✅ with report path; binding matrix D.5 row added.
3. **(Optional)** Notion ADR Registry row patch for ADR-080 status update — only if the current workflow mandates Notion writeback; otherwise deferred to operator discretion.

**Commit discipline**: each commit uses explicit paths via `git add <specific-files>` — no `git add -A` / `git commit -a`. Before `git commit`, verify `git diff --cached --name-only` shows only the intended paths. Unrelated working-tree items (guardian report, live-provider untracked tests, rtc-w2b plan, THIS new D.5 plan file) are mentioned in the commit body but NOT staged.

**Phase E remains gated on its own Author-Gate per ADR-080 §11. Phase F remains gated on Phase E completion. No E/F work is authorized by this plan or its follow-up report.**

**No implementation of D.5 begins now. No files other than this plan are modified in the current turn.**
