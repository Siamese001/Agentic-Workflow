---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\runtime-cert-e-ci-gate-e7b3f1.md'
original_relative_path: '_archive\\2026-05\\runtime-cert-e-ci-gate-e7b3f1.md'
source_sha256: 061d563ce3bb8a37bb4dc5be5a7b7be18d09c7e8fff1f8f052b9cd21000b7f29
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: runtime-cert-e-ci-gate-e7b3f1
plan_type: governance
---

# Runtime Cert — Phase E CI Gate (Planning Only)

- **Plan ID**: `runtime-cert-e-ci-gate-e7b3f1`
- **Status**: Planning — Author-Gate pending
- **Authored**: 2026-05-02
- **ADR anchor**: [ADR-080 §11 Phase E](../../docs/architecture/adr/ADR-080-runtime-cert-phase-d-planning.md)
- **Predecessor (complete)**: Phase D.1–D.5 on `main` — D.5 closeout at `docs/reports/runtime_cert/phase_d_closeout/2026-W18.md`, ADR-080 §11 D.5 ✅ delivered 2026-05-01
- **Successor (gated)**: Phase F — scanner `runtime_mode` bucket extension + promotion workflow (separate Author-Gate)

> **Planning pass only.** This file authorizes **no** Python code, **no** pre-commit wiring, **no** CI workflow edits, **no** scanner change, **no** emitter change, **no** promotion logic, and **no** certification claim. Phase E implementation begins only after a separate Author-Gate approves the trade-offs in §10. `runtime_certification_status` for every app remains `NOT_CERTIFIED` throughout and after this plan.

---

## Context (SCQA)

- **Situation** — Phase D.1–D.5 delivered 2026-05-01. The cert-decision schema (D.1), evaluator (D.2), ledger writer (D.3), and smoke harness (D.4) all land with 166 tests passing; D.5 closeout report in `docs/reports/runtime_cert/phase_d_closeout/2026-W18.md` cites them. ADR-080 §11 D.5 is ✅. Four P1 Notion rows (`00C.9 runtime gates`, `00A.8 L5 bindings`, `00B.9 L4 blueprint migration`, `03.9 L3-L2 handoff`) have been triage-gated on Phase E since 2026-05-01.
- **Complication** — Phase E is the fail-closed CI gate that promotes the D.2 evaluator from "invoked only in the test suite" to "invoked in pre-commit / CI against real evidence". Without E, the D pipeline works in lab but never runs against a real closeout, and the 4 P1 rows stay gated indefinitely.
- **Question** — How do we wire a fail-closed CI gate that consumes Phase C/D artifacts, enforces the §7 Wilson/z/uplift thresholds, and adds zero scanner/emitter/app-behavior change?
- **Answer** — Introduce `ops_scripts/ci/check_runtime_certification.py` as a pure D.2/D.3 consumer. It reads the current week's C.8 closeout report and a per-app decision ledger, re-runs D.2 in verify-mode, and fails the build iff any app making a `TRACE_OBSERVED`-or-higher evidence claim either (a) has no corresponding decision record or (b) has a decision record whose `verdict != certify` but the C.8 report asserts the threshold floor. Wire via `.pre-commit-config.yaml` at a new hook id `runtime-certification` (tier `T8r` — runtime claim verification). No promotion, no scanner change; Phase F owns those.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `.cursor/rules/ssot-folder-enforcement.md` (§31) | `check_*` / `*_gate.py` must land in `ops_scripts/ci/` | ✅ read |
| `.cursor/rules/fortknox-certification-discipline.md` (§32) | cert claims emerge ONLY from compile_requirement_signoff.py — gate must NOT assert certification, only threshold compliance | 🔲 re-read at D5.W1 approval time |
| `docs/architecture/adr/ADR-080-runtime-cert-phase-d-planning.md` §11 + §7 + §4 non-goals | Primary design anchor; Phase F boundary | ✅ read |
| `docs/reports/runtime_cert/phase_d_closeout/2026-W18.md` §5.12 | Phase E/F boundary statement (verbatim) | ✅ read |
| `tools/runtime_cert/decisions/cert_decision_evaluator.py` | D.2 public surface: `evaluate_phase_c_closeout(report, history=(), *, closeout_report_id=None, closeout_report_hash=None)` | 🔲 inspect before E.P1 |
| `tools/runtime_cert/decisions/cert_decision_ledger.py` | D.3 read surface: `read_cert_decision_records(app_name, *, repo_root=None)` | 🔲 inspect before E.P1 |
| `tools/runtime_cert/reports/phase_c_closeout.py` | C.8 `PhaseCCloseoutReport` dataclass; need `read_phase_c_closeout` equivalent or glob loader | 🔲 inspect before E.P1 |
| `.pre-commit-config.yaml` | Where the new hook lands; inspect existing `T7*` hook tier convention | 🔲 inspect before E.P3 |
| `ops_scripts/ci/run_contract_gates.py` | Dispatcher — new gate must be callable from there too | 🔲 inspect before E.P3 |

---

## Wave Structure

| Wave | Phase IDs | Focus | Tokens | Status | Checkpoint |
|---|---|---|---:|---|---|
| E.W1 | E.P0 | Author-Gate approval of this plan | ~800 🟢 | Pending | User approves §10 AGs |
| E.W2 | E.P1, E.P2 | Implement `ops_scripts/ci/check_runtime_certification.py` + unit tests | ~10 000 🟡 | Blocked on E.W1 | Gate green on synthetic fixtures; red on tampered fixtures |
| E.W3 | E.P3 | Wire hook into `.pre-commit-config.yaml` + `run_contract_gates.py` dispatcher | ~2 000 🟢 | Blocked on E.W2 | Hook fires on `pre-commit run --all-files`; exit-code 1 on bad fixture |
| E.W4 | E.P4 | Mark ADR-080 §11 E row ✅; update binding matrix; flip 4 gated Notion P1 rows (00A.8 / 00B.9 / 00C.9 / 03.9) from "E-gated" to "in-scope for Phase F tests" | ~1 500 🟢 | Blocked on E.W3 | ADR-080 row ✅; matrix row added; 4 Notion rows updated |

**Total: ~14 300 tokens across 4 waves.**

---

## Out Of Scope

> Explicit guardrail per scope-containment rule.

- ❌ **No scanner change.** `tools/spine/scanner/` is Phase F. Phase E does not recognize `RUNTIME_CERTIFIED` or `FORMAL_EXCEPTION_VERIFIED` buckets — those do not exist yet.
- ❌ **No promotion workflow.** Scorecard, Notion ADR promotion, memory writeback on cert flip — all Phase F.
- ❌ **No emitter change.** `tools/runtime_adg/` and all span emitters are untouched.
- ❌ **No new ledger.** Phase E reads the D.3 per-app ledger; it does not write one.
- ❌ **No app behavior change.** Every `apps_*` package is read-only.
- ❌ **No new ADR.** ADR-080 is the anchor; no ADR-081+ is proposed here.
- ❌ **No certification claim.** `runtime_certification_status` remains `NOT_CERTIFIED` everywhere. A gate-green build does NOT mean an app is certified — it means the app's D.2 evaluator is consistent with its D.3 ledger record.
- ❌ **No modification of D.1–D.4 surfaces.** Phase E consumes them; it does not extend their public API.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| E.P0 | Author-Gate approval | This plan file | 4 trade-offs in §10 need explicit sign-off | ~800 | 🔲 Pending |
| E.P1 | Implement gate core | `ops_scripts/ci/check_runtime_certification.py` (new) | Must be pure D.2/D.3 consumer; no SQL other than D.3 reads; no imports of `agentic_core.*` / `tools.spine.scanner.*` / `tools.runtime_adg.*`; SSOT-folder-compliant per §31 | ~7 000 | 🔲 Blocked on E.W1 |
| E.P2 | Unit tests | `tests/unit/ops_scripts/ci/test_check_runtime_certification.py` (new) | Fixtures covering (a) no apps claim TRACE_OBSERVED → green, (b) app claims TRACE_OBSERVED + D.3 record `certify` → green, (c) app claims TRACE_OBSERVED but no D.3 record → red, (d) app claims TRACE_OBSERVED + D.3 record `hold` with `WILSON_BELOW_THRESHOLD` → red, (e) manifest_hash drift → red, (f) tampered D.3 row → red. Use `tmp_path` + in-memory sqlite; no real `artifacts/ledgers/` writes. | ~3 000 | 🔲 Blocked on E.W1 |
| E.P3 | Wire into pre-commit | `.pre-commit-config.yaml` (edit — add `runtime-certification` hook), `ops_scripts/ci/run_contract_gates.py` (edit — add `T8r` tier dispatch) | Hook must run fast (<10s on no-op); new tier ID must not clash with T7* | ~2 000 | 🔲 Blocked on E.W2 |
| E.P4 | Doc + row updates | `docs/architecture/adr/ADR-080-runtime-cert-phase-d-planning.md` (edit — §11 Phase E row ✅), `docs/reference/runtime_certification/contract_span_binding_matrix.md` (edit — add Phase E row), 4 Notion row status/blocker notes | Preserve ADR-080 §14/§16 disclaimers verbatim | ~1 500 | 🔲 Blocked on E.W3 |

---

## Gap Register

**GAP-E-1: No `read_phase_c_closeout` loader exists.**
- Phase C.8 writes `docs/reports/runtime_cert/phase_c_closeout/<YYYY-Www>.md`. No reader exists to hydrate those back into `PhaseCCloseoutReport`.
- Impact: gate must either (a) add a minimal loader (out of Phase E scope per §Out Of Scope "no extension of D.1–D.4 surfaces"), or (b) accept a different input form (e.g., a JSON sidecar that C.8 could emit in a future revision).
- Resolution at E.P1: AG-2 trade-off — either vendor a read-only parser in `ops_scripts/ci/` (NOT part of `tools.runtime_cert.*` surface) OR assert C.8 emits a JSON sidecar as a precondition. **Recommended**: vendor a parser local to the gate script. The gate owns its input parsing.

**GAP-E-2: D.3 ledgers may not yet exist on a first-time repo.**
- First-run, no app has a cert-decision ledger file.
- Impact: gate must treat "no ledger" as "no TRACE_OBSERVED claim yet" → green, not red.
- Resolution at E.P1: gate enumerates `apps_*/` packages, for each checks `artifacts/ledgers/cert_decision_<app>.sqlite`; absence ≡ "no claim yet" ≡ green. Red only if C.8 report asserts TRACE_OBSERVED for an app AND its ledger is missing OR its ledger lacks a decision for that manifest_hash.

**GAP-E-3: `run_contract_gates.py` tier convention unknown.**
- Assumed tier naming `T7*` for existing gates; Phase E needs a free tier ID.
- Impact: naming clash breaks CI.
- Resolution at E.P3: read `run_contract_gates.py` before editing; pick next free `T8*` or `T7r+1` per existing convention; document in commit message.

---

## Execution Plan

### E.P1 — Implement `ops_scripts/ci/check_runtime_certification.py`

**Scope**: Single file `ops_scripts/ci/check_runtime_certification.py`. No new modules, no edits to `tools/runtime_cert/*`.

**Public surface** (single CLI entrypoint):
```
python ops_scripts/ci/check_runtime_certification.py [--report PATH] [--apps-root apps_] [--repo-root .] [--fail-fast]
```

**Imports allowed**:
- `tools.runtime_cert.decisions.cert_decision_evaluator` (D.2)
- `tools.runtime_cert.decisions.cert_decision_ledger` (D.3 read surface only)
- `tools.runtime_cert.decisions.cert_decision_record` (D.1 schema)
- Standard library + `argparse`

**Imports FORBIDDEN**:
- `agentic_core.*`
- `tools.spine.scanner.*`
- `tools.runtime_adg.*`
- `tools.ledgers.*` (D.3 is self-contained; gate does not touch the general ledger family)

**Logic**:
1. Resolve current ISO week → find `docs/reports/runtime_cert/phase_c_closeout/<YYYY-Www>.md`. If missing → green (no claims to verify this week).
2. Parse closeout for per-app `runtime_certification_status` claims. (See GAP-E-1 — local parser in this file.)
3. For each app claiming `TRACE_OBSERVED` or higher:
   a. Load `artifacts/ledgers/cert_decision_<app>.sqlite` via D.3 `read_cert_decision_records`. Missing → red.
   b. Select the record whose `manifest_hash` matches the closeout's current manifest_hash. No match → red (manifest drift).
   c. Re-run D.2 `evaluate_phase_c_closeout(report, history)` → produces a fresh record.
   d. Compare fresh record's `verdict` and `reasons` against the D.3 ledger record. Disagreement → red (tamper detection).
4. Exit 0 (green) if all apps pass; exit 1 (red) and print structured diagnostic per failing app.

**Acceptance**:
- Unit tests E.P2 cover 6 fixture scenarios (see Phase-Level Summary E.P2).
- `ruff check ops_scripts/ci/check_runtime_certification.py` clean.
- `python ops_scripts/ci/check_runtime_certification.py --help` exits 0 with usage.

### E.P2 — Unit tests

**Scope**: `tests/unit/ops_scripts/ci/test_check_runtime_certification.py` (new).

**Fixture shape**: synthetic `PhaseCCloseoutReport` in-memory + `tmp_path` sqlite ledgers seeded via D.3 writer.

**Test count target**: 12–15 tests (one per scenario + edge cases).

**Acceptance**: all pass under `pytest -p no:xdist`; no real `artifacts/ledgers/` writes (verified by `test_gate_does_not_write_to_real_artifacts_ledgers`).

### E.P3 — Wire into pre-commit

**Scope**:
- Edit `.pre-commit-config.yaml` — add one hook entry:
  ```yaml
  - id: runtime-certification
    name: runtime-certification — T8r — Phase E fail-closed gate
    entry: python ops_scripts/ci/check_runtime_certification.py
    language: system
    pass_filenames: false
    stages: [pre-commit, manual]
  ```
- Edit `ops_scripts/ci/run_contract_gates.py` — add `T8r` tier dispatch entry invoking the same script.

**Acceptance**:
- `pre-commit run runtime-certification --all-files` → exit 0 on current repo state (no TRACE_OBSERVED claims yet).
- `python ops_scripts/ci/run_contract_gates.py --tier T8r` → exit 0.
- Adding a deliberately bad fixture (stashed, not committed) → exit 1.

### E.P4 — Doc + row updates

**Scope**:
- `docs/architecture/adr/ADR-080-runtime-cert-phase-d-planning.md` §11 — change Phase E row from (current) pending to:
  ```
  | **E** ✅ | Fail-closed CI gate (`ops_scripts/ci/check_runtime_certification.py`) + pre-commit hook `runtime-certification` at tier T8r. **Delivered <YYYY-MM-DD>.** Gate verifies every app claiming TRACE_OBSERVED-or-higher has a consistent D.3 ledger record and re-runs D.2 for tamper detection. No scanner change, no emitter change, no certification promotion. Phase F remains gated. | No apps certified; gate verifies consistency only |
  ```
- `docs/reference/runtime_certification/contract_span_binding_matrix.md` — add row binding Phase E to the CI check and its hook ID.
- 4 Notion rows (`00A.8`, `00B.9`, `00C.9`, `03.9`) — patch Blocking Items from "Phase D.5-gated" to "Phase E complete 2026-<week>; Phase F tests can now be authored under a separate Author-Gate".

**Acceptance**: ADR row renders ✅; binding matrix row lints clean; 4 Notion rows reflect new blocker.

---

## Rules

- **No `git add -A` / `git commit -a`.** Explicit path staging per D.5 plan §8 discipline; known unrelated working-tree churn (apps-folder-taxonomy refactor in progress) must not be staged.
- **Constitutional §31 — SSOT folder routing.** `check_runtime_certification.py` MUST land in `ops_scripts/ci/`. `pre_write_gate.py` will block any other path.
- **Constitutional §32 — Fort Knox discipline.** Phase E gate is a *threshold consistency check*, not a certification producer. It does NOT emit `SIGNED_OFF`, does NOT touch `certification/evidence_assertions.jsonl`, does NOT invoke `compile_requirement_signoff.py`. Those remain Fort Knox's exclusive surface.
- **Constitutional §29 — closed-loop router.** Phase E's decision path does not trigger a `ROUTER_DECISION:` marker (the gate is structural, not routed). A `CERT_DECISION:` marker at D.3 write time is still out of scope per D.5 §5.11 known gap.
- **No extension of D.1–D.4 public surfaces.** Gate consumes existing D.2 / D.3 / D.1 APIs. If it needs something those don't offer, that's a separate D.N+1 Author-Gate, not in-line scope creep.
- **Test doubles for ledger I/O.** All E.P2 tests use `tmp_path`; zero writes to real `artifacts/ledgers/*.sqlite`.

---

## Success Criteria

- [ ] `ops_scripts/ci/check_runtime_certification.py` exists, ≤600 LOC, imports only allowed modules (§E.P1).
- [ ] 12+ unit tests pass; zero real-ledger writes.
- [ ] `pre-commit run runtime-certification --all-files` green on current repo state.
- [ ] Deliberate-fault fixture (tampered D.3 row) → exit 1.
- [ ] ADR-080 §11 E row shows ✅ with delivery date.
- [ ] Binding matrix shows Phase E row.
- [ ] 4 Notion rows (`00A.8`, `00B.9`, `00C.9`, `03.9`) Blocking Items updated.
- [ ] No scanner / emitter / app-behavior change; `git diff --stat` confined to `ops_scripts/ci/`, `tests/unit/ops_scripts/ci/`, `.pre-commit-config.yaml`, `docs/architecture/adr/`, `docs/reference/runtime_certification/`.
- [ ] Commit discipline verified: `git diff --cached --name-only` shows only intended paths before each commit.

---

## Rollback Strategy

Each wave is atomic-revertable via `git`.

| Wave | Rollback action | Detection signal |
|---|---|---|
| E.W2 (code) | `git revert` the commit adding `check_runtime_certification.py` + tests | Gate false-positives against current repo state |
| E.W3 (wiring) | Remove hook entry from `.pre-commit-config.yaml`; remove T8r dispatch | Hook hangs / blocks every commit |
| E.W4 (doc) | Revert ADR / matrix edits; restore Notion row blocker text | ADR row content is wrong or premature |

---

## 10. Author-Gate Trade-offs (AG-10 shape)

Four decisions requiring explicit sign-off before E.W2 begins.

### AG-1: Fail mode from day 1

- **⭐ Recommended**: **fail-closed from first commit after E.W3 lands.** Gate exits 1 on any violation; no advisory grace period.
- **Alternative A**: fail-soft for first week (`exit 0` + warn-to-stderr), flip to fail-closed after operator review. **Rejected** — violates §32 Fort Knox discipline's "compile-is-the-only-status-authority" principle by creating a silent-warning window; evidence of the "fail-closed first day" precedent exists at `run_contract_gates.py` T7s.4 (apps_fortknox_signed_proof gate).
- **Alternative B**: fail-closed only in CI; fail-soft in local pre-commit. **Rejected** — creates drift between CI and local; violates pre-commit SSOT doctrine.

### AG-2: Closeout-report input format

- **⭐ Recommended**: **gate owns its own Markdown parser** (vendored locally in `check_runtime_certification.py`, ≤80 LOC). Read-only, regex-based, no new `tools.runtime_cert.*` surface.
- **Alternative A**: extend C.8 to emit a JSON sidecar alongside the Markdown. **Rejected as Phase E scope** — touches `tools/runtime_cert/reports/phase_c_closeout.py`, which is D.1–D.4 surface; per §Out Of Scope "No modification of D.1–D.4 surfaces". May be proposed as a separate Author-Gate.
- **Alternative B**: make the gate consume D.4 smoke JSON (`schema_version="d4-smoke-v1"`) instead of C.8 Markdown. **Rejected** — smoke JSON is internal D.4 artifact, not a persisted operator input; using it as a gate input blurs the boundary between "we ran the pipeline in testing" and "we verified a real weekly claim".

### AG-3: Hook trigger — pre-commit vs CI-only

- **⭐ Recommended**: **both.** Pre-commit `stages: [pre-commit, manual]` + dispatch from `run_contract_gates.py` T8r. Mirrors existing gate precedent.
- **Alternative A**: CI-only (no pre-commit). **Rejected** — lets a bad commit land before CI catches it; defeats the fail-closed principle.
- **Alternative B**: manual-only (run on demand via `pre-commit run runtime-certification --hook-stage manual`). **Rejected** — no enforcement.

### AG-4: Tier naming

- **⭐ Recommended**: **`T8r`** — next free tier after `T7s.4` (last allocated fortknox gate). `r` suffix denotes runtime-cert.
- **Alternative A**: `T7t` (next letter after existing T7 suffixes). **Deferred** — requires reading `run_contract_gates.py` convention first; pick at E.P3 time and record choice in commit message.
- **Alternative B**: no tier (raw hook only). **Rejected** — `run_contract_gates.py` is the SSOT dispatcher; every gate belongs to a tier.

---

## 11. Stop Conditions

Implementation halts and surfaces back for Author-Gate review if any of these is detected during E.W2 or later:

- `tools/runtime_cert/decisions/cert_decision_evaluator.py` public surface has drifted from `evaluate_phase_c_closeout(report, history=(), *, closeout_report_id=None, closeout_report_hash=None)` → **stop**.
- `tools/runtime_cert/decisions/cert_decision_ledger.py` `read_cert_decision_records` signature has drifted → **stop**.
- Gate logic begins to require a new function in `tools/runtime_cert/*` → **stop**; propose separate sub-phase.
- Gate logic begins to require `agentic_core.*` or `tools.spine.scanner.*` imports → **stop**; violates §Out Of Scope.
- Pre-commit hook runtime exceeds 30s on no-op case → **stop and optimize**; likely indicates gate is doing too much.
- `python -m pytest tests/unit/tools/runtime_cert/` fails at E.W2 start → **stop**; D.1–D.4 must be green before E lands.

---

## 12. Decisions Captured

| # | Decision | Source | Status |
|---|---|---|---|
| 1 | Fail-closed from first day | §10 AG-1 | Recommended; pending AG |
| 2 | Gate owns its own C.8 Markdown parser (~80 LOC local) | §10 AG-2 | Recommended; pending AG |
| 3 | Both pre-commit + CI dispatch via `run_contract_gates.py` | §10 AG-3 | Recommended; pending AG |
| 4 | Tier `T8r` (confirm at E.P3) | §10 AG-4 | Recommended; pending AG |
| 5 | Single file `ops_scripts/ci/check_runtime_certification.py`, ≤600 LOC | §E.P1 | Hard constraint |
| 6 | No scanner/emitter/app-behavior change | §Out Of Scope | Hard constraint |
| 7 | No new ADR; ADR-080 is anchor | §Out Of Scope | Hard constraint |
| 8 | No cert claim; `NOT_CERTIFIED` preserved | §Out Of Scope, §15 | Hard constraint |
| 9 | Explicit commit staging, no `git add -A` | §Rules | Hard constraint |

---

## 13. Unresolved Questions

None block implementation. These surface for Author-Gate consideration:

1. **`CERT_DECISION:` marker emission**: D.5 §5.11 documented this as a known gap. Should Phase E take the opportunity to emit one per gate-run? **Recommendation**: **no** — E is a *verifier*, not a *decision-maker*; a marker would imply it's producing a new decision record. Defer to Phase F or a dedicated follow-up. Resolve at E.P1 start.
2. **Cadence of gate runtime**: pre-commit fires on every commit; each run enumerates apps and reads ledgers. Should there be a cache? **Recommendation**: **no cache in v1**; gate must be fast enough without one. If >10s becomes chronic, add a cache in a follow-up. Resolve at E.P2 (benchmark in tests).
3. **First-week expected state**: with zero apps claiming `TRACE_OBSERVED`, what does the gate do? **Answer** (not a question): green trivially. Documented in E.P1 logic step 1.

---

## 14. Boundaries (explicit)

- **E does not certify apps.** Every status field the gate touches stays `NOT_CERTIFIED`.
- **E does not modify scanner `runtime_mode`.** Phase F owns that.
- **E does not emit runtime-ADG spans.** Phase D and prior phases own that.
- **E does not write to D.3 ledgers.** Read-only consumer.
- **E does not extend D.1 / D.2 / D.3 / D.4 surfaces.** Imports only; no edits.
- **E does not open Phase F.** Phase F remains gated on its own Author-Gate.

---

## 15. Explicit No-Certification Disclaimer

> **This plan authorises no certification.** The Phase E CI gate verifies that every app's D.3 decision ledger record is consistent with (a) the D.1 schema invariants, (b) the D.2 evaluator's current output on the same input, and (c) the C.8 closeout report's claimed evidence level. A gate-green build means "the D pipeline's internal consistency holds"; it does NOT mean any app is certified. `runtime_certification_status` remains `NOT_CERTIFIED` for every app after this gate is wired, exactly as before.
>
> A `verdict == "certify"` row in any D.3 ledger is still **not** a certification. It remains a statement that, if this codebase were at Phase F, the Phase F promotion workflow would promote the app. Phase F does not exist. Phase E does not add scanner buckets. Phase E does not modify `runtime_mode`. Phase E does not touch `apps_*/`.
>
> Phase E report/implementation begins **only after** a separate Author-Gate approves this plan. Phase F remains gated on Phase E completion *and* Phase F's own Author-Gate.

---

## 16. Recommended Next Step

**Phase E implementation (E.W2) — but only after Author-Gate approval of this plan.**

Suggested gate question for the follow-up turn:

> The E plan proposes four trade-offs (AG-1 through AG-4 in §10).
> Approve all four as recommended? Or surface specific alternatives?

On approval, work proceeds in three commits per Wave Structure:

1. **E.W2 commit**: `ops_scripts/ci/check_runtime_certification.py` + `tests/unit/ops_scripts/ci/test_check_runtime_certification.py`.
2. **E.W3 commit**: `.pre-commit-config.yaml` hook entry + `ops_scripts/ci/run_contract_gates.py` T8r dispatch.
3. **E.W4 commit**: ADR-080 §11 row ✅; binding matrix row; 4 Notion row patches (separate turn — MCP serialization).

**Commit discipline**: each commit uses explicit paths via `git add <specific-files>` — no `git add -A`. Before `git commit`, verify `git diff --cached --name-only`. Unrelated working-tree items (apps-folder-taxonomy refactor, guardian report, untracked plans/rules) are NOT staged.

**Phase F remains gated on its own Author-Gate per ADR-080 §11. No Phase F work is authorized by this plan or its follow-up implementation.**

**No implementation begins now. No files other than this plan are modified in the current turn.**
