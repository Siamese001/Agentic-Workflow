# Runtime Cert — Phase E.1 Fail-Closed CI Gate (Planning Only)

- **Plan ID**: `runtime-cert-e1-fail-closed-ci-gate-c71f3d`
- **Status**: Planning — Author-Gate pending
- **Authored**: 2026-05-01
- **Branch**: `rtc-w2b-live-provider-allow-proof-clean`
- **ADR anchor**: [ADR-080 §11 E](../../docs/architecture/adr/ADR-080-runtime-cert-phase-d-planning.md)
- **Predecessors** (all complete on this branch):
  - **D.1** schema — `tools/runtime_cert/decisions/cert_decision_record.py` (54 tests)
  - **D.2** evaluator — `tools/runtime_cert/decisions/cert_decision_evaluator.py` (50 tests)
  - **D.3** ledger writer — `tools/runtime_cert/decisions/cert_decision_ledger.py` + `.windsurf/schemas/cert_decision_ledger.schema.sql` (35 tests)
  - **D.4** smoke harness — `tools/runtime_cert/smoke/cert_decision_smoke.py` restored at commit `26ffc52791` (27 tests)
  - **D.5** closeout report — `docs/reports/runtime_cert/phase_d_closeout/2026-W18.md` restored at commit `40ef8da391`; ADR-080 §11 D.5 ✅ and binding matrix D.5 row restored at commit `bdbefa29c2`
  - Combined test sweep: **191 passing** (`tests/unit/tools/runtime_cert/decisions/` + `tests/unit/tools/runtime_cert/smoke/`)

> **Planning pass only.** This file authorizes **no** Python code, **no** CI gate, **no** pre-commit hook, **no** workflow edit, **no** scanner change, **no** emitter change, **no** app behavior change, **no** ledger write, and **no** certification claim. Phase E.1 implementation begins only after a separate Author-Gate approves this plan. `runtime_certification_status` for every app remains `NOT_CERTIFIED` throughout and after this plan.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| E1.W1 | E1.P1 | Author-Gate approval of this plan | ~1 200 | ADR-080 §11 permits per-sub-phase gating | Pending | User approves five E-AGs in §10 |
| E1.W2 | E1.P2, E1.P3 | Implement `check_runtime_certification.py` + unit tests | ~7 000 | D.1–D.5 remain ✅ on disk at implementation time | Blocked on E1.W1 | `ops_scripts/ci/check_runtime_certification.py` + 12+ unit tests; no scanner / emitter / app imports; gate runs **report-only** (exit 0) by default per §5 |
| E1.W3 | E1.P4 | Optional baseline file + docs | ~1 500 | W2 landed | Blocked on E1.W2 | Baseline file shape decided by E-AG-2; Phase E.1 evidence-summary doc at `docs/reports/runtime_cert/phase_e_runs/<YYYY-Www>.md` cadence |
| E1.W4 | E1.P5 | Author-Gate to flip gate from advisory to fail-closed in CI | ~800 | W2 + W3 stable | Blocked on E1.W3 | Separate Author-Gate approves wiring into `.pre-commit-config.yaml` / GitHub Actions with `strict` mode |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---:|---|---|
| E1.P1 | Author-Gate approval | This plan file | Five trade-offs in §10 need explicit sign-off | ~1 200 | Pending |
| E1.P2 | Core gate module | `ops_scripts/ci/check_runtime_certification.py` (new) | Gate must compose D.2 + D.3 read-back WITHOUT promoting anything; must emit exit codes that downstream CI interprets as pass/fail but NOT as certification signal | ~4 500 | Blocked |
| E1.P3 | Gate tests | `tests/unit/ops_scripts/ci/test_check_runtime_certification.py` (new) | Full fixture coverage for 6+ fail modes + 2+ pass modes + no-forbidden-imports audit; tests use `tmp_path` ledgers — never real repo | ~2 500 | Blocked |
| E1.P4 | Baseline file + evidence doc | optional `docs/reference/runtime_certification/cert_baseline.toml` (or equivalent); `docs/reports/runtime_cert/phase_e_runs/<YYYY-Www>.md` | Baseline shape depends on E-AG-2; evidence doc explicitly non-promoting | ~1 500 | Blocked |
| E1.P5 | Advisory → fail-closed flip | `.pre-commit-config.yaml`, `.github/workflows/<name>.yml` | **Separate Author-Gate required**; this phase only ships the wiring when the user decides E.1 has accumulated enough evidence | ~800 | Blocked |

---

## 1. Purpose and Non-Goals

### Purpose

Plan a **fail-closed CI gate** that checks runtime-certification decision evidence at pre-commit / CI time and fails the build when that evidence is inconsistent or insufficient. The gate composes D.2 (pure evaluator) + D.3 (per-app ledger read-back) + optional baseline into a single read-only verdict. It never writes to any ledger. It never mutates app state. It never promotes any app's `runtime_certification_status`.

### Non-goals (explicit)

- **Phase E does not certify apps.** No app's `runtime_certification_status` is written by the gate. Every file the gate reads carries `NOT_CERTIFIED` per D.1/D.3; the gate's exit code is a build-pass/build-fail signal, not a certification signal.
- **Phase E does not modify scanner `runtime_mode`.** The spine scanner's `runtime_mode` classification is untouched. Phase F owns any extension.
- **Phase E does not introduce `RUNTIME_CERTIFIED` / `FORMAL_EXCEPTION_VERIFIED` buckets.** The scanner's bucket list stays as-is through all of Phase E.
- **Phase E only gates consistency / evidence sufficiency.** The gate answers: *"Given the Phase D artifacts on disk + the claimed baseline, is this commit coherent or does it contradict itself?"* — not *"Is this app certified?"*.
- **Phase F owns promotion and scanner bucket extension.** That includes the scorecard update, Notion ADR auto-post, memory writeback, and any scanner recognition of new buckets. Phase E feeds Phase F with evidence; Phase F decides and acts.
- **Phase E does not emit `CERT_DECISION:` markers.** ADR-080 §6 mentions a possible marker; D.3 / D.4 do not emit one today, and Phase E.1 does not either. That is deferred to a later Phase E sub-phase or to Phase F.
- **Phase E does not change app behavior.** No `apps_*` package is read or modified. The gate reads ledger files, manifests, and closeout artifacts — not app code.
- **Phase E does not create new intelligence ledgers.** It consumes D.3's per-app cert-decision ledgers read-only. No new ledger-family entry.

---

## 2. Current Inputs (inspected)

The gate is built against the following existing artifacts. Each has been inspected as part of this planning pass; no edits are proposed in this plan.

| Path | Role in Phase E | Contract surface |
|---|---|---|
| `tools/runtime_cert/decisions/cert_decision_record.py` | Hydrate rows read back from the ledger into `CertificationDecisionRecord`; construct new records for "would-have-been" verdict checks | `CertificationDecisionRecord`, `NOT_CERTIFIED`, `VERDICT_*`, `EVIDENCE_KIND_*`, `compute_decision_id`, `make_certification_decision_record`, `to_dict`, `to_json` |
| `tools/runtime_cert/decisions/cert_decision_evaluator.py` | Pure evaluator. Gate calls `evaluate_phase_c_closeout(report, history)` to compute the current-week verdict without writing | `evaluate_phase_c_closeout`, `wilson_lower_bound`, `derive_closeout_report_hash`, closed 12-reason failure ontology, ADR-080 §7 thresholds |
| `tools/runtime_cert/decisions/cert_decision_ledger.py` | Read-only consumer: `read_cert_decision_records(app_name, repo_root=...)` per app; no write path invoked | `CertDecisionLedgerWriteResult` (as type hint only), `ledger_path_for_app`, `read_cert_decision_records` |
| `.windsurf/schemas/cert_decision_ledger.schema.sql` | Schema constraint reference; gate does **not** run DDL | DDL not executed by gate |
| `tools/runtime_cert/smoke/cert_decision_smoke.py` | **Reference only.** The smoke harness is the proof-of-wiring for D.2 → D.3 → read-back. The gate reuses the same read-back path but does not call the smoke harness | `run_cert_decision_smoke`, `CertDecisionSmokeReport` — not invoked by the gate; cited as the contract reference |
| `docs/reports/runtime_cert/phase_d_closeout/2026-W18.md` | Handoff doc; informs gate design | Human-readable; not parsed by the gate |
| `docs/architecture/adr/ADR-080-runtime-cert-phase-d-planning.md` | Source of truth for thresholds (§7), non-promotion invariants, and Phase E scope (§11) | No code dependency |
| `docs/reference/runtime_certification/contract_span_binding_matrix.md` | Maps apps to R3 / BTC / formal-exception route shapes; gate reads app route-shape to know which evidence class to check | Read-only reference; parsed by gate only if §E-AG-2 picks "manifest-derived baseline" |
| `tools/runtime_cert/reports/phase_c_closeout.py` (optional dependency) | If gate re-evaluates closeout on-the-fly (E-AG-1 alternative), it calls `PhaseCCloseoutReport` / `AppCloseoutSummary` dataclasses | Read-only construction |

### What the gate does NOT read

- Any `agentic_core.L*` module (forbidden import — verified by test)
- Any `apps_*` package (forbidden — Phase E does not touch app behavior)
- Any `tools.spine.scanner.*` module (forbidden — Phase F concern)
- Any `ops_scripts.ci.*` module beyond its own (no cross-gate composition)
- Live runtime-ADG snapshot JSON (out of scope — C.6 owns that)
- Markdown closeout artifacts (C.8 output) — view layer, not interface

---

## 3. Proposed Gate Target

```
ops_scripts/ci/check_runtime_certification.py
```

SSOT-folder-compliant (constitutional §31 / `ssot-folder-enforcement.md`). The filename matches the naming pattern `check_*.py` used by every existing contract gate.

**Do not create in this planning turn.** Implementation is E1.P2, which is blocked on Author-Gate approval of this plan.

### Tests target

```
tests/unit/ops_scripts/ci/test_check_runtime_certification.py
```

Adjacent to other CI-gate tests (same directory tree pattern used by `ops_scripts/ci/check_*.py` unit tests across the repo).

### Optional baseline file target (gated on E-AG-2)

```
docs/reference/runtime_certification/cert_baseline.toml
```

…or whichever shape E-AG-2 selects. File is created in E1.P4, after E1.P2/E1.P3 have proven the gate logic.

---

## 4. Gate Input Model

The gate consumes **four** input classes. Each has a precise on-disk shape.

### 4.1 Per-app cert-decision ledgers

- **Path**: `<repo_root>/artifacts/ledgers/cert_decision_<app_name>.sqlite`
- **Access**: `read_cert_decision_records(app_name, repo_root=<resolved_repo>)`
- **Shape**: tuple of `CertificationDecisionRecord` (D.1), ordered by `generated_at_utc` ASC
- **Missing-file semantics**: D.3 returns `()` when the file is absent — the gate treats that as "no prior cert-decision evidence for this app"
- **Tamper detection**: D.3's read-back re-runs D.1 `__post_init__` and recomputes `compute_decision_id` — if a row has been tampered, the gate surfaces a `ValueError` and fails fail-closed with `TAMPERED_LEDGER_ROW`

### 4.2 Current-week closeout evidence (C.8 or D.2 input)

Two possible inputs, resolved by E-AG-1:

| Option | Mechanism | Freshness |
|---|---|---|
| **(a)** latest C.8 closeout Markdown at `docs/reports/runtime_cert/phase_c_closeout/<YYYY-Www>.md` | The gate re-evaluates on-the-fly by rebuilding `PhaseCCloseoutReport` from the fresh C.8 run and passing it to `evaluate_phase_c_closeout` | Real-time — reflects the current commit's evidence |
| **(b)** pre-computed latest cert-decision-ledger row per app | The gate reads `read_cert_decision_records(app, repo_root=...)[-1]` for each app and treats that as the "current" verdict | Stale — reflects only what was previously persisted |

**Recommendation** (E-AG-1): **(b)** ledger-read. The gate does NOT re-run D.2 on-the-fly; it trusts what's already written. Rationale in §10 AG-1.

### 4.3 App manifests + `manifest_hash`

- **Path**: `apps_*/apps_*_manifest.json` (per-app canonical manifest)
- **Access**: read via stdlib `json.loads` + deterministic hash (same algorithm as the C.6 / C.8 pipelines) — see `tools/runtime_cert/manifest_hash.py` if present
- **Use**: cross-check that every D.3 ledger row's `manifest_hash` matches the current-commit manifest hash. If a ledger row says "evidence for `manifest_hash = X`" but the current commit's manifest hashes to `Y ≠ X`, the gate fails with `MANIFEST_HASH_DRIFT`.

### 4.4 Optional baseline file

See §6 Baseline model. If E-AG-2 picks "explicit static baseline file", the file shape is TOML (or JSON) with per-app minimum-acceptable `verdict` + `evidence_kind`. Default for E.1 is to emit a *warning* on missing baseline entry, not a failure — see E-AG-4.

---

## 5. Gate Verdict Behavior (fail-closed semantics)

The gate returns **one** of three exit codes:

| Exit code | Meaning | Downstream CI behavior |
|---|---|---|
| `0` | **pass** — all consistency checks hold; evidence is sufficient | build continues |
| `1` | **fail (hard)** — one or more fail-closed conditions fire | build stops (when gate is in strict mode) |
| `2` | **abstain** — inputs missing / degraded; gate cannot evaluate | build continues with warning in advisory mode; build stops in strict mode (E-AG-5) |

The distinction between hard-fail and abstain matters because a missing ledger file is not the same as an adverse decision.

### 5.1 Hard-fail conditions (exit 1)

Each of the following triggers exit 1 with a specific reason code logged to stdout + an optional JSON report at `artifacts/runtime_cert/gate/<YYYY-Www>.json`:

| Reason code | Trigger |
|---|---|
| `MISSING_LEDGER_FOR_REQUIRED_APP` | An app is listed in the baseline as requiring cert evidence AND no `cert_decision_<app>.sqlite` exists OR `read_cert_decision_records(app, ...)` returns `()` |
| `MISSING_CLOSEOUT_EVIDENCE` | No C.8 closeout-derived evidence OR no D.2-reconstructible evidence for the apps the baseline demands |
| `MANIFEST_HASH_DRIFT` | `latest_ledger_row.manifest_hash != current_commit_manifest_hash(app)` |
| `LATEST_VERDICT_IS_REJECT` | Latest ledger row for a required app has `verdict == "reject"` |
| `LATEST_VERDICT_WORSE_THAN_BASELINE` | Latest row's verdict is strictly worse than the baseline's minimum (e.g., baseline says `hold` min; ledger says `reject`) |
| `FORBIDDEN_SPAN_VIOLATION` | Latest row carries `FORBIDDEN_SPAN_VIOLATION` in its D.1 `failure_reasons` |
| `FORMAL_CONTROL_MISSING_OR_FAILED` | Latest row for a formal-exception app carries `FORMAL_CONTROL_MISSING_OR_FAILED` |
| `TAMPERED_LEDGER_ROW` | D.3's read-back raises `ValueError` (tamper detection fires) |
| `APP_CLAIMS_HIGHER_STATUS_THAN_EVIDENCE` | App's manifest or declared-status file claims `TRACE_OBSERVED` / `FORMAL_EXCEPTION_OBSERVED` but ledger evidence does not support it |
| `STATUS_NOT_NOT_CERTIFIED` | Any ledger row or any gate-internal record ever shows `runtime_certification_status != NOT_CERTIFIED` — structurally impossible via D.1/D.3 but caught defensively |

The ordering is deterministic and the first hard-fail wins; subsequent conditions are still collected and reported, but exit 1 fires at the first.

### 5.2 Abstain conditions (exit 2)

| Reason code | Trigger |
|---|---|
| `NO_APPS_CLAIM_CERT_EVIDENCE` | No app in the current commit even requests cert evidence — gate has nothing to check |
| `BASELINE_FILE_MISSING` | E-AG-2 picks baseline-file mode AND the baseline file doesn't exist; in E.1 default this is advisory, not a fail |
| `DEGRADED_READ` | SQLite read raises `sqlite3.OperationalError` (e.g., file locked) — treated as transient; abstain + log |

### 5.3 Non-promotion invariant (load-bearing)

> **The gate does NOT write, promote, or mutate any certification state.** It only reads. Its exit code is a build signal, not a certification signal. An exit 0 does NOT mean "this commit certifies app X"; it means "the evidence-sufficiency checks this commit requires all hold". Phase F is the only layer that can promote.

Cross-check enforced at three layers inside the gate:

1. Any `CertificationDecisionRecord` the gate constructs (for "would-have-been" checks) goes through D.1 `__post_init__` → impossible to construct with status ≠ `NOT_CERTIFIED`
2. Any row read back by the gate is re-validated by D.3's `_hydrate_one` → impossible to hydrate a tampered row
3. The gate imports NOTHING from `tools.spine.scanner` / `agentic_core.L*` / `apps_*` — audited by a dedicated no-forbidden-imports test

### 5.4 What the gate explicitly cannot do

- Cannot promote an app
- Cannot write to any ledger
- Cannot change any SC/AP scanner bucket
- Cannot ask for human approval (no Author-Gate prompt at CI time — that's a developer-loop concern, not a CI concern)
- Cannot mutate any file outside `artifacts/runtime_cert/gate/` (its own report output)

---

## 6. Baseline Model

### 6.1 Four baseline-source options

| Option | Shape | Freshness | Trust model |
|---|---|---|---|
| **(a)** Explicit static baseline file | TOML / JSON at `docs/reference/runtime_certification/cert_baseline.toml` | Human-maintained | Human-curated |
| **(b)** Derived from latest cert-decision-ledger row | Reads `read_cert_decision_records(app, ...)[-1]` and uses that as "own baseline" | Self-referential | Automatic — but circular: baseline is whatever the ledger most recently said |
| **(c)** Derived from app manifest | Each `apps_*_manifest.json` declares `required_verdict_floor = "hold"` | Owned by app authors | Distributed, app-local |
| **(d)** None for E.1 — report-only | No baseline file; gate emits JSON evidence and does not fail on verdict regressions | N/A | No baseline |

### 6.2 Recommendation (E-AG-2)

**(a) explicit static baseline file for E.1** with graceful degradation when the file is absent.

File shape (TOML — matches other repo config conventions):

```toml
# docs/reference/runtime_certification/cert_baseline.toml
# Phase E.1 baseline — per-app minimum-acceptable verdict + evidence kind.
# This file is non-promoting. It declares what the CI gate will fail on,
# not what any app IS. Every app's runtime_certification_status remains
# NOT_CERTIFIED in the scanner regardless of this file's contents.

schema_version = "e1-baseline-v1"
generated_at = "2026-05-01"

[apps.apps_research]
min_verdict = "hold"                # one of: reject, hold, certify
require_evidence_kind = "r3_observed"
require_manifest_hash_match = true
fail_on_forbidden_span_violation = true

[apps.apps_knowledge_capture]
min_verdict = "hold"
require_evidence_kind = "r3_observed"
require_manifest_hash_match = true
fail_on_forbidden_span_violation = true

# Apps not listed here are NOT gated in E.1 — the gate abstains rather than fails.
```

Rationale:

- **(a) over (b)**: (b) is circular — "latest row defines the baseline" means any regression escapes detection because the ledger already accepted it. The baseline must be *external* to the ledger.
- **(a) over (c)**: (c) distributes trust to individual app manifests, which is the eventual Phase F design — but for E.1 a single curated file keeps the scope tight.
- **(a) over (d)**: (d) ("no baseline, report-only") is exactly E-AG-5's advisory mode. Baseline shape still needs to be decided NOW so the file format doesn't change when the gate flips from advisory to strict. (d) is the *mode*, not the *baseline source*.
- **Graceful degradation**: if `cert_baseline.toml` is missing, E.1 abstains (exit 2) with `BASELINE_FILE_MISSING`. In advisory mode (E-AG-5) this is a warning; in strict mode it is a hard stop. Apps not listed in the baseline file are NOT gated — the file is opt-in.

### 6.3 Field semantics (if E-AG-2 approves option (a))

| Field | Type | Meaning |
|---|---|---|
| `schema_version` | string | `"e1-baseline-v1"` — pinned so future Phase E sub-phases can dispatch on version |
| `[apps.<app>].min_verdict` | `"reject"` / `"hold"` / `"certify"` | Hard floor; latest ledger row worse than this = `LATEST_VERDICT_WORSE_THAN_BASELINE` |
| `[apps.<app>].require_evidence_kind` | D.1 `EVIDENCE_KIND_*` value | Latest ledger row must use this evidence kind; mismatch = fail |
| `[apps.<app>].require_manifest_hash_match` | bool | If true, current manifest hash must match latest ledger row's `manifest_hash`; mismatch = `MANIFEST_HASH_DRIFT` |
| `[apps.<app>].fail_on_forbidden_span_violation` | bool | Opt-in hard fail when `FORBIDDEN_SPAN_VIOLATION` in latest row; default true |

---

## 7. Relationship to Phase F

Phase F is **strictly downstream** of Phase E and operates under a separate Author-Gate.

| Concern | Phase E | Phase F |
|---|---|---|
| Reads ledger / evidence | ✅ yes (read-only) | ✅ yes (read-only input) |
| Fails a build on evidence mismatch | ✅ yes | n/a |
| Writes to ledger | ❌ no | ❌ no (Phase F also does not write cert ledgers; it reads them) |
| Modifies scanner `runtime_mode` | ❌ no | ✅ yes (extends bucket list) |
| Recognizes `RUNTIME_CERTIFIED` / `FORMAL_EXCEPTION_VERIFIED` | ❌ no | ✅ yes |
| Updates scorecard / Notion ADR / memory | ❌ no | ✅ yes |
| Requires human Author-Gate sign-off | ❌ no (automated CI decision) | ✅ yes (architectural decision) |

### 7.1 Handoff contract

Phase F reads the same Phase D/E artifacts the gate reads (per-app ledger + baseline file + manifest hash). Phase F treats an exit-0 from the Phase E gate for app *X*, combined with a human Author-Gate approval, as the signal to promote app *X*'s `runtime_mode` in the scanner.

**Phase E cannot short-circuit the Phase F Author-Gate.** An exit-0 from the E.1 gate means "evidence is internally consistent". It does NOT mean "this app should be promoted". Promotion is explicitly, structurally, and procedurally deferred to a separate Phase F decision.

### 7.2 What Phase E.1 does NOT ship that Phase F needs

These are explicitly Phase F scope and do NOT land in E.1 — listing so Phase F planning can pick them up without confusion:

- Scanner-side recognition of new `runtime_mode` buckets (`RUNTIME_CERTIFIED`, `FORMAL_EXCEPTION_VERIFIED`) — scanner code change
- Scorecard writer extension to emit rows for certified apps — scanner / tools change
- Notion ADR auto-post for promotion events — integration work
- Memory writeback for promoted-app status — `memory` MCP writes
- `CERT_DECISION:` marker emission from D.3 / D.4 / E.1 — marker family extension

---

## 8. Test Strategy (for future E1.P3 implementation)

All tests use `tmp_path` for `repo_root` and construct synthetic ledger content via D.3's writer (called from the test setup, NOT from the gate itself).

### Required coverage (≥12 tests)

| # | Test | Assertion |
|---|---|---|
| 1 | `test_gate_fails_when_ledger_missing_for_required_app` | Baseline lists `apps_research`; no ledger file for it → exit 1 with `MISSING_LEDGER_FOR_REQUIRED_APP` |
| 2 | `test_gate_fails_when_manifest_hash_mismatches` | Ledger row has `manifest_hash=A`; current-commit manifest hashes to `B` → exit 1 with `MANIFEST_HASH_DRIFT` |
| 3 | `test_gate_fails_when_latest_decision_is_reject` | Latest row `verdict="reject"` for a baseline-required app → exit 1 with `LATEST_VERDICT_IS_REJECT` |
| 4 | `test_gate_passes_when_latest_decision_meets_baseline` | Latest row `verdict="hold"`; baseline `min_verdict="hold"` → exit 0 |
| 5 | `test_gate_fails_when_app_claims_higher_status_than_evidence` | App manifest declares `TRACE_OBSERVED`; ledger has no supporting row → exit 1 with `APP_CLAIMS_HIGHER_STATUS_THAN_EVIDENCE` |
| 6 | `test_gate_fails_on_forbidden_span_violation` | Latest row carries `FORBIDDEN_SPAN_VIOLATION` in `failure_reasons` → exit 1 |
| 7 | `test_gate_fails_on_formal_control_missing_or_failed` | Latest row (formal-exception app) carries `FORMAL_CONTROL_MISSING_OR_FAILED` → exit 1 |
| 8 | `test_gate_abstains_when_no_baseline_file` | No baseline file on disk → exit 2 in advisory mode; exit 1 with `BASELINE_FILE_MISSING` in strict mode |
| 9 | `test_gate_abstains_when_no_apps_claim_cert_evidence` | Baseline empty → exit 2 with `NO_APPS_CLAIM_CERT_EVIDENCE` |
| 10 | `test_gate_has_no_scanner_imports` | Module source regex-scanned for `tools.spine.scanner` / `agentic_core.L\d_` → empty |
| 11 | `test_gate_has_no_emitter_imports` | Module source regex-scanned for `tools.runtime_adg` emit paths → empty |
| 12 | `test_gate_has_no_app_behavior_imports` | Module source regex-scanned for `apps_research` / `apps_underwriting_ai` / etc. actual app-code imports (not just fixture strings) → empty |
| 13 | `test_gate_json_report_includes_no_certification_disclaimer` | Optional JSON output at `artifacts/runtime_cert/gate/<YYYY-Www>.json` has `disclaimer` key containing `"no runtime certification performed"` and `runtime_certification_status == "NOT_CERTIFIED"` |
| 14 | `test_gate_does_not_write_real_repo_ledgers` | After gate runs, no new `cert_decision_*.sqlite` exists under the real repo's `artifacts/ledgers/` — only `tmp_path`-internal files |
| 15 | `test_gate_never_imports_write_cert_decision_record` | Module source must not contain `write_cert_decision_record` (read-only contract) |
| 16 | `test_gate_first_hard_fail_wins_but_all_collected` | Two hard-fail conditions simultaneously → exit 1 with the first reason, all reasons collected in the optional JSON report |
| 17 | `test_gate_respects_strict_vs_advisory_mode_env` | `RUNTIME_CERT_GATE_MODE=strict` vs `advisory` behaves as E-AG-5 specifies |

### Forbidden in tests

- Any write outside `tmp_path`
- Real `artifacts/ledgers/` access
- Network calls, subprocess, `run_command`
- Any import of `agentic_core.L*`, `ops_scripts.ci.*` (beyond the gate under test), `tools.spine.scanner.*`, `apps_*`
- Real runtime-ADG snapshot loading
- Markdown closeout-artifact parsing

### Verification command (future E1.P3)

```powershell
python -m pytest tests/unit/ops_scripts/ci/test_check_runtime_certification.py -p no:xdist --timeout=60
```

---

## 9. Stop Conditions

E.1 implementation halts and surfaces back for Author-Gate review if any of these is detected during E1.W2 or E1.W3:

- E.1 begins to require **scanner `runtime_mode` changes** → stop (Phase F)
- E.1 begins to require **app behavior changes** → stop (out of scope everywhere)
- E.1 begins to require **emitter changes** (runtime-ADG span emitters) → stop (Phase F concern at earliest)
- E.1 begins to require **creating `RUNTIME_CERTIFIED` / `FORMAL_EXCEPTION_VERIFIED` buckets** → stop (Phase F)
- E.1 **cannot distinguish gate failure from promotion** — i.e., the design starts implying that exit 0 means certified → stop and redesign
- The gate begins to require writing to any `cert_decision_*.sqlite` → stop (D.3 is the only writer by design)
- The gate begins to require live runtime-ADG snapshot loading → stop (C.6 scope)
- The gate begins to need a new intelligence ledger entry → stop (would require an ADR-050 Author-Gate)
- D.1–D.5 state reverts on the branch (e.g., another branch-switch removes D.4/D.5) → stop; restore Phase D via cherry-pick before proceeding
- D.1–D.5 test sweep (`191 passing` baseline) fails at implementation start → stop; fix underlying regression first

---

## 10. Author-Gate Trade-offs (AG-10 shape)

Five decisions the plan must get explicit sign-off on before E1.W2 begins.

### E-AG-1: Gate input source — per-app SQLite ledgers vs on-the-fly re-evaluation

- **⭐ Recommended**: **read-only consumption of per-app `cert_decision_<app>.sqlite` ledgers via `read_cert_decision_records`**. The gate does NOT re-run D.2 on-the-fly; it trusts what's already written.
- **Alternative A**: re-evaluate on the fly from a fresh C.8 closeout run. **Rejected** — couples E.1 to the C.6/C.8 live pipeline + `otel_mcp` availability; inflates CI time; duplicates the D.2 evaluation path.
- **Alternative B**: hybrid — prefer fresh re-eval, fall back to ledger. **Rejected** — two code paths is worse than one; and the fall-back path is exactly what (a) is.
- **Consequence**: E-AG-1 (a) means the gate only catches what's already in the ledger. A commit that *would* produce a new adverse verdict but hasn't yet persisted one escapes the gate. This is acceptable because D.4 smoke in CI already runs D.2 over the committed closeout — the smoke writes the ledger row, then the gate reads it. Order matters; document in E1.P2 the required pre-commit-hook ordering.

### E-AG-2: Baseline file shape and location

- **⭐ Recommended**: **explicit static baseline file at `docs/reference/runtime_certification/cert_baseline.toml`** with schema `e1-baseline-v1` per §6.3.
- **Alternative A**: derive baseline from latest ledger row. **Rejected** — circular; regressions auto-accept.
- **Alternative B**: derive from per-app manifest. **Deferred to Phase F** — distributed trust is the Phase F design; E.1 keeps it centralized.
- **Alternative C**: no baseline in E.1; report-only. **Rejected as default** — that's E-AG-5's advisory mode, not the baseline-source decision.

### E-AG-3: Fail on missing ledger vs warn-only

- **⭐ Recommended**: **hard fail (`exit 1`)** on `MISSING_LEDGER_FOR_REQUIRED_APP` when the app is listed in the baseline AND the baseline's `require_evidence_kind` is set. **Abstain (`exit 2`)** for apps not listed in the baseline.
- **Alternative A**: warn-only in E.1 (`exit 0` + stderr warning). **Rejected** — defeats the purpose of fail-closed. The whole point of E.1 is to refuse commits that don't carry evidence for apps that claim runtime observation.
- **Alternative B**: configurable per-app via a `fail_on_missing: bool` field in the baseline. **Deferred** — if needed, added in a Phase E.2 extension. E.1 keeps the policy uniform.

### E-AG-4: Gate all apps vs only apps with baseline entries

- **⭐ Recommended**: **only apps with baseline entries are gated**. Apps not in the baseline are invisible to the gate (abstain). This keeps E.1 opt-in per-app — critical for a first rollout.
- **Alternative A**: gate all apps detected in the repo. **Rejected** — no baseline data for most apps yet; would fail-closed on legitimate commits that haven't accumulated Phase D evidence.
- **Alternative B**: gate all apps where `apps_*_manifest.json` declares `cert_gate_enabled: true`. **Deferred to Phase F** — that's the eventual design but requires manifest changes that are out of E.1 scope.

### E-AG-5: Advisory (report-only) vs strict (fail-closed CI) rollout

- **⭐ Recommended**: **ship in advisory mode first**. E.1 initial behavior:
  - Gate runs locally via explicit invocation (`python ops_scripts/ci/check_runtime_certification.py`)
  - Gate prints its verdict + optional JSON report
  - Gate's exit code is observable but **NOT wired into `.pre-commit-config.yaml` or GitHub Actions** until E1.W4 (separate Author-Gate)
  - Env var `RUNTIME_CERT_GATE_MODE` toggles between `advisory` (default: exit 0 even on hard-fail, log instead) and `strict` (exit 1 on hard-fail)
- **Alternative A**: wire into CI immediately. **Rejected** — no production-volume evidence that the gate's verdict matches operator expectations. Advisory-first lets the gate run over N weeks and surface false positives before it can block the pipeline.
- **Alternative B**: ship strict-only with no advisory mode. **Rejected** — same reason; higher risk.
- **Graduation criterion** (informs E1.W4 Author-Gate): after 4 consecutive weeks of advisory runs with zero unresolved false positives, flip to strict by wiring into `.pre-commit-config.yaml` via a separate Author-Gate.

---

## 11. Deliverables (future only — NOT shipped by this planning turn)

### E1.P2 deliverables (implementation)

- `ops_scripts/ci/check_runtime_certification.py` (new) — the gate module
- Optional: small helper utility under `tools/runtime_cert/gate/` if the gate module grows beyond one file (only if refactor warrants; E.1 default is single-file)

### E1.P3 deliverables (tests)

- `tests/unit/ops_scripts/ci/test_check_runtime_certification.py` (new) — 12+ tests per §8

### E1.P4 deliverables (baseline + evidence doc)

- `docs/reference/runtime_certification/cert_baseline.toml` (new; per E-AG-2) — initial seed with ≤3 apps (`apps_research` at minimum)
- `docs/reports/runtime_cert/phase_e_runs/<YYYY-Www>.md` (new) — weekly gate-run evidence summary; strict non-promotion disclaimer; non-promoting disclaimer identical to Phase D reports

### E1.P5 deliverables (advisory → strict flip — **separate Author-Gate required**)

- `.pre-commit-config.yaml` addition — new hook entry invoking the gate in strict mode
- `.github/workflows/<name>.yml` addition OR modification — new job or step
- ADR-080 §11 E row update (or new ADR-081 if the scope warrants)

### NOT deliverables (out of E.1 scope)

- Any change to `tools/runtime_cert/decisions/*.py` (Phase D is closed)
- Any change to `tools/spine/scanner/` (Phase F)
- Any change to `agentic_core/` (never)
- Any change to `apps_*/` (never)
- Any new intelligence ledger (would require ADR-050 gate)
- Any `CERT_DECISION:` marker emission (deferred beyond E.1)

---

## 12. Final Disclaimer

> **This plan does not certify any app, does not modify scanner `runtime_mode`, does not add a CI gate, and does not implement Phase F promotion.**
>
> Phase E.1 is infrastructure planning for a future fail-closed CI gate that reads Phase D evidence and fails the build when that evidence is inconsistent or insufficient. Nothing in this plan — not the gate design, not the baseline-file shape, not the test plan, not the eventual exit codes — promotes any app's `runtime_certification_status` from `NOT_CERTIFIED` to any other value. The gate's exit code is a build-pass / build-fail signal, not a certification signal.
>
> Every reference to `runtime_certification_status` in the future gate's output, its report files, and its tests will be `NOT_CERTIFIED` — enforced structurally through D.1's `__post_init__` for any records the gate constructs, and through D.3's read-back re-validation for every row the gate loads.
>
> **Phase F owns promotion and scanner bucket extension.** Phase E.1 feeds Phase F with evidence; Phase F decides and acts, under its own separate Author-Gate.
>
> **E.1 implementation begins only after a separate Author-Gate approves this plan, per ADR-080 §11.** Phase E.2+ and Phase F remain independently gated on their own Author-Gates.
>
> **No implementation of Phase E begins now. No files other than this plan are modified in the current turn.**

---

## 13. Decisions Captured in This Plan

| # | Decision | Source | Status |
|---|---|---|---|
| 1 | Gate target: `ops_scripts/ci/check_runtime_certification.py` (SSOT-compliant naming) | §3 | Hard constraint |
| 2 | Gate input: read-only per-app SQLite ledgers via `read_cert_decision_records` | §4.1, §10 E-AG-1 | Recommended; pending AG |
| 3 | Closeout evidence: pre-computed ledger (b) not on-the-fly re-eval (a) | §4.2, §10 E-AG-1 | Recommended; pending AG |
| 4 | Baseline: explicit static TOML at `docs/reference/runtime_certification/cert_baseline.toml`, schema `e1-baseline-v1` | §6.2, §10 E-AG-2 | Recommended; pending AG |
| 5 | Missing-ledger-for-required-app is a hard fail | §5.1, §10 E-AG-3 | Recommended; pending AG |
| 6 | Apps not in baseline are invisible to the gate (opt-in) | §10 E-AG-4 | Recommended; pending AG |
| 7 | Advisory mode first; strict CI wiring requires separate Author-Gate | §10 E-AG-5 | Recommended; pending AG |
| 8 | Closed failure-reason ontology: 10 hard-fail codes + 3 abstain codes | §5.1, §5.2 | Hard constraint |
| 9 | `runtime_certification_status == NOT_CERTIFIED` preserved throughout | §5.3, §12 | Hard constraint |
| 10 | Phase E does not write any ledger | §5.4, §7 | Hard constraint |
| 11 | Phase F owns scanner `runtime_mode` extension and promotion | §7, §12 | Hard constraint |
| 12 | No forbidden imports (scanner / emitter / app behavior / `agentic_core.L*`) — audited by test | §8 (tests 10–12, 15) | Hard constraint |

---

## 14. Unresolved Questions

None block implementation. These surface for Author-Gate consideration:

1. **Pre-commit ordering**: if the gate runs in pre-commit alongside the D.4 smoke hook, the smoke must run *before* the gate so fresh ledger rows are available. Recommendation: document ordering in `.pre-commit-config.yaml` when E1.W4 lands, and add a test that asserts the gate's first action is a read (not a write-then-read). Resolve at E1.P5.
2. **Manifest hash algorithm**: the gate needs to compute the current-commit manifest hash to compare against ledger rows. Is the canonical helper `tools/runtime_cert/manifest_hash.py` or equivalent already present, or does E.1 need a small local helper? Recommendation: inspect at E1.P2 start; reuse if present, local helper with ~20 lines otherwise. Do NOT add a new module under `tools/` if the helper is ≤20 lines — inline it in the gate.
3. **Baseline evolution**: how does the baseline file get updated when a new app joins the gate? Recommendation: baseline updates are manual, tracked in git, Author-Gate-approved per-addition. No auto-update mechanism in E.1.
4. **Multi-commit ledger rows**: if two developers commit concurrent rows for the same `(app, manifest_hash)`, D.3's `INSERT OR IGNORE` keeps the first and ignores the second. The gate's `[-1]` "latest row" selector might not reflect the most recent actual decision. Recommendation: document this as a known limitation; switch to `ORDER BY generated_at_utc DESC LIMIT 1` selector if multi-writer scenarios materialize. Defer.
5. **Advisory-mode alarm fatigue**: if the gate runs advisory for 4+ weeks and operators stop reading its output, the eventual flip to strict will feel like a surprise. Recommendation: include a weekly summary doc (E1.P4 `docs/reports/runtime_cert/phase_e_runs/<YYYY-Www>.md`) that makes the advisory state visible. Resolve at E1.P4.

---

## 15. Boundaries (explicit)

- **E.1 does not create certification status.** No app gains `RUNTIME_CERTIFIED` or `FORMAL_EXCEPTION_VERIFIED`. The gate's exit 0 does NOT mean certified.
- **E.1 does not change scanner `runtime_mode`.** Phase F owns that.
- **E.1 does not introduce new `runtime_mode` buckets.** Phase F owns that.
- **E.1 does not write to any ledger.** D.3 is the only writer, by design.
- **E.1 does not touch app behavior.** No `apps_*` package is read or modified.
- **E.1 does not parse a live runtime-ADG snapshot.** C.6 owns that.
- **E.1 does not emit markers or ledger events.** No new `CERT_DECISION:` / `ROUTER_DECISION:` events ship via this plan.
- **E.1 does not open Phase F.** Phase F is independently gated.
- **E.1 does not wire into CI automatically.** The advisory → strict flip requires a separate Author-Gate (E1.W4).

---

## 16. Recommended Next Step

**Author-Gate approval of this plan — but not E.1 implementation.**

Suggested gate question for the follow-up turn:

> The Phase E.1 plan proposes five trade-offs (E-AG-1 through E-AG-5 in §10).
> Approve all five as recommended? Or surface specific alternatives for re-scoping?

On approval, work proceeds through four waves per §Wave Structure:

1. **E1.W2** — implement `ops_scripts/ci/check_runtime_certification.py` + ≥12 unit tests
2. **E1.W3** — seed `docs/reference/runtime_certification/cert_baseline.toml` + first weekly evidence doc
3. **E1.W4** — **separate Author-Gate** to flip from advisory to strict; only then wire into `.pre-commit-config.yaml` and CI workflows

**Commit discipline**: each commit uses explicit paths via `git add <specific-files>` — no `git add -A` / `git commit -a`. Before `git commit`, verify `git diff --cached --name-only` shows only the intended paths. Unrelated working-tree items (guardian report, live-provider tests, rtc-w2b byproducts, THIS new E.1 plan file in the current turn) are mentioned in commit bodies but NOT staged.

**Phase E.2+ remains gated on its own Author-Gate. Phase F remains gated on Phase E completion. No E/F implementation work is authorized by this plan.**

**No implementation of E.1 begins now. No files other than this plan are modified in the current turn.**
