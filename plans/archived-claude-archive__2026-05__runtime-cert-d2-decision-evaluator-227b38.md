---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\runtime-cert-d2-decision-evaluator-227b38.md'
original_relative_path: '_archive\\2026-05\\runtime-cert-d2-decision-evaluator-227b38.md'
source_sha256: d9f94f04c23e4c0b5f8756f36d0e879b666e6e47166a8a129c5e301f17f1196b
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Runtime Cert — Phase D.2 Decision Evaluator (Planning Only)

- **Plan ID**: `runtime-cert-d2-decision-evaluator-227b38`
- **Status**: Planning — Author-Gate pending
- **Authored**: 2026-05-01
- **ADR anchor**: [ADR-080 §11 D.2](../../docs/architecture/adr/ADR-080-runtime-cert-phase-d-planning.md)
- **Predecessor (shipped)**: Phase D.1 — `CertificationDecisionRecord` schema (commit `193ab15cd5`)

> **Planning pass only.** This file authorizes **no** Python code, **no**
> ledger writes, **no** scanner edits, **no** CI gates, **no** emitter
> changes, **no** app behavior changes, and **no** certification claim. All
> D.2 implementation begins only after a separate Author-Gate approves this
> plan. `runtime_certification_status` for every app remains `NOT_CERTIFIED`
> throughout and after this plan.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| D2.W1 | D2.P1 | Author-Gate approval of this plan | ~1 000 | ADR-080 §11 allows per-sub-phase gating | Pending | User approves one of AG options in §10 |
| D2.W2 | D2.P2, D2.P3 | Pure evaluator module + `wilson_lower_bound` helper | ~7 000 | D.1 schema stable; no scipy dep | Blocked on D2.W1 | Module under `tools/runtime_cert/decisions/cert_decision_evaluator.py` with ≥14 unit tests passing |
| D2.W3 | D2.P4 | Minimal doc updates: ADR-080 §11 ✅ D.2, binding matrix footnote | ~800 | D2.W2 merged | Blocked on D2.W2 | ADR row marked ✅; no disclaimer regression |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---:|---|---|
| D2.P1 | Author-Gate approval | This plan file | Five trade-offs need explicit sign-off (§10) | ~1 000 | Pending |
| D2.P2 | `wilson_lower_bound` pure helper | `cert_decision_evaluator.py` (new — one function + constants) | Numerical-edge cases at `n=0`, `p=0`, `p=1`; z=1.96 default | ~2 000 | Blocked |
| D2.P3 | `evaluate_phase_c_closeout` pure evaluator | same module | Closed-ontology failure reasons; history-window semantics on `manifest_hash` drift; deterministic verdict mapping | ~5 000 | Blocked |
| D2.P4 | Doc updates | `docs/architecture/adr/ADR-080-runtime-cert-phase-d-planning.md`, `docs/reference/runtime_certification/contract_span_binding_matrix.md` | Preserve §14 disclaimer verbatim | ~800 | Blocked |

---

## 1. Purpose and Non-Goals

### Purpose

Plan a **pure function** that converts a `PhaseCCloseoutReport` plus an
in-memory iterable of prior `CertificationDecisionRecord` objects into a
tuple of new `CertificationDecisionRecord` objects (one per app the
closeout covers). No I/O; no side effects; no promotion.

### Non-goals

- **No ledger writes.** That is Phase D.3, separately gated.
- **No filesystem or SQLite reads.** `history` is an in-memory iterable.
- **No scanner edits.** `runtime_mode` classification is untouched.
- **No CI gate.** No pre-commit or workflow additions.
- **No emitter changes.** Runtime-ADG span emitters are untouched.
- **No app behavior changes.** Every `apps_*` package is read-only here.
- **No runtime certification.** `status_after = NOT_CERTIFIED` invariant
  from D.1 is inherited at construction. Even `verdict="certify"` produces
  a record whose `runtime_certification_status_after == NOT_CERTIFIED`.
- **No Wilson-threshold retune.** D.2 consumes ADR-080 §7 global defaults
  (`n ≥ 30`, `wilson_lower ≥ 0.60`, `z ≥ 1.96`, `uplift > 0`). Per-route
  thresholds are explicitly deferred to D.5 calibration (ADR-080 §0 Q2).
- **No uplift baseline switch.** D.2 uses prior-weekly closeout (ADR-080
  §0 Q3 provisional default). Rolling-window baselines deferred to D.5.

---

## 2. Inputs and Outputs

### Input A — `report: PhaseCCloseoutReport`

From `tools/runtime_cert/reports/phase_c_closeout.py`. Contains:

- `app_summaries: tuple[AppCloseoutSummary, ...]`, each with:
  - `app_name` (must start with `apps_`)
  - `route_shape`
  - `evidence_kind ∈ {r3, btc, formal_exception, skipped}`
  - `manifest_hash` (64-hex)
  - `passed_trace_observed_n` / `failed_trace_observed_n` / `unknown_needs_runtime_run_n` (or the formal-exception equivalents)
  - `forbidden_span_violations: tuple[...]`
  - `blockers: tuple[str, ...]`
  - any embedded gap-report references
- `generated_at_utc: str`
- `closeout_report_id: str` — source identifier (filesystem path or UUID)
- `closeout_report_hash: str` — 64-hex SHA-256 of the C.8 Markdown bytes

**Contract**: every `AppCloseoutSummary` carries `runtime_certification_status = NOT_CERTIFIED`; D.2 re-asserts this invariant on input (defensive check; raises `ValueError` otherwise).

### Input B — `history: Iterable[CertificationDecisionRecord] = ()`

Caller-supplied in-memory iterable. Default empty tuple. D.2 **never** opens a file, socket, or SQLite connection to obtain history. History is consumed at most once (coerced to tuple internally) and filtered per app.

### Output — `tuple[CertificationDecisionRecord, ...]`

One record per app in `report.app_summaries`, in the same order as the input summaries. Each record:

- uses `compute_decision_id(app_name, manifest_hash, closeout_report_hash)` from D.1 (deterministic hash, PK-idempotent)
- carries the exact 19 fields validated by the D.1 `__post_init__`
- has `runtime_certification_status_before == runtime_certification_status_after == NOT_CERTIFIED` — **unconditionally**, even when `verdict == "certify"`

No record is skipped silently; every app in the closeout produces exactly one decision record (verdict may be `hold` with `failure_reasons=("CLOSEOUT_MISSING",)` when summary data is inadequate).

---

## 3. Proposed Target File

```
tools/runtime_cert/decisions/cert_decision_evaluator.py
```

Sibling to the D.1 schema. Package `__init__.py` already exists. No new packages introduced.

Tests:

```
tests/unit/tools/runtime_cert/decisions/test_cert_decision_evaluator.py
```

Both paths respect constitutional §31 (SSOT folder routing).

---

## 4. Public API Proposal

Exactly two public symbols. No classes. No factory. No side effects.

```python
def wilson_lower_bound(successes: int, n: int, z: float = 1.96) -> float:
    """Wilson score interval lower bound.

    Pure; no external deps. Formula:

        phat = successes / n
        denom = 1 + z**2 / n
        centre = (phat + z**2 / (2*n)) / denom
        halfwidth = z * sqrt((phat*(1-phat) + z**2/(4*n)) / n) / denom
        return max(0.0, centre - halfwidth)

    Edge cases:
        n == 0                 -> 0.0
        successes == 0         -> 0.0
        successes == n         -> computed normally (may equal 1.0 at high n)
        z < 0 or z == 0        -> raises ValueError
        successes < 0 or > n   -> raises ValueError
    """


def evaluate_phase_c_closeout(
    report: PhaseCCloseoutReport,
    history: Iterable[CertificationDecisionRecord] = (),
) -> tuple[CertificationDecisionRecord, ...]:
    """Convert a C.8 closeout + history into D.1 decision records.

    Pure. No I/O. One record per app in report.app_summaries. Every
    record has runtime_certification_status_after == NOT_CERTIFIED.
    """
```

Internal helpers (module-private, leading `_`):

- `_count_successes(summary) -> tuple[int, int]` — returns `(successes, n)` with source chosen by `evidence_kind`
- `_collect_history_for_app(app, manifest_hash, history) -> tuple[...]` — filters history tuple to the same `(app_name, manifest_hash)` window
- `_compute_uplift(current_rate, prior_history) -> float` — prior-weekly delta or 0.0 baseline
- `_derive_verdict(ctx) -> tuple[str, tuple[str, ...]]` — deterministic verdict + failure_reasons
- `_next_review_utc(generated_at_utc, verdict) -> str` — 7 days for hold, 30 for certify, 14 for reject (provisional; subject to D2.P1 review)

---

## 5. Decision Rules

All thresholds from ADR-080 §7 global defaults. No route-specific branch.

### Step 1 — Blocker pre-check (verdict = `reject` if ANY fire)

| Failure Reason | Trigger |
|---|---|
| `CLOSEOUT_MISSING` | `AppCloseoutSummary` exists but has zero observed rows AND non-empty blockers naming "closeout not produced" — note: this is ALSO a `hold` candidate in Step 3 if no blockers |
| `CRITICAL_BLOCKERS_PRESENT` | `len(summary.blockers) > 0` with severity tag `critical` (the C.8 report already classifies these) |
| `FORBIDDEN_SPAN_VIOLATION` | `len(summary.forbidden_span_violations) > 0` |
| `FORMAL_CONTROL_MISSING_OR_FAILED` | `evidence_kind == "formal_exception"` AND any `FormalControlEvidence.passed` is `False` OR a required control is absent |
| `MANIFEST_HASH_DRIFT` | Current `manifest_hash` differs from every prior history entry's `manifest_hash` for the same app AND the prior history is non-empty AND `trace_observed_n` in the current summary is below threshold — the history is incompatible with the current window |
| `AMBIGUOUS_EVIDENCE` | `evidence_kind == "skipped"` AND `summary.blockers` claim runnable work exists OR `passed_trace_observed_n > 0` while `evidence_kind == "skipped"` |

If any reject reason fires, verdict is `reject` and the record lists **all** firing reasons (not just the first).

### Step 2 — Certify pre-check (verdict = `certify` if ALL of these pass, and no reject reason fired)

| Condition | Source |
|---|---|
| `trace_observed_n ≥ 30` | summed from current summary + history for matching `(app_name, manifest_hash)` |
| `wilson_lower ≥ 0.60` | `wilson_lower_bound(success_n, n, 1.96)` |
| `z_score ≥ 1.96` | standard normal score of `evidence_rate` vs. baseline |
| `uplift > 0` | `evidence_rate - baseline_rate` |

If all four pass and no Step-1 reject fired, `verdict = "certify"` and `failure_reasons = ()`.

### Step 3 — Hold (fallback)

If no Step-1 reject fires and Step-2 does not fully pass, `verdict = "hold"` with specific failure reasons:

| Failure Reason | Trigger |
|---|---|
| `SAMPLE_SIZE_TOO_SMALL` | `trace_observed_n < 30` |
| `WILSON_BELOW_THRESHOLD` | `wilson_lower < 0.60` |
| `Z_SCORE_BELOW_THRESHOLD` | `z_score < 1.96` |
| `UPLIFT_NOT_POSITIVE` | `uplift <= 0.0` |
| `NOT_TRACE_OBSERVED_READY` | `evidence_kind == "r3"` or `"btc"` but `passed_trace_observed_n + failed_trace_observed_n == 0` and `unknown_needs_runtime_run_n > 0` |
| `NOT_FORMAL_EXCEPTION_OBSERVED_READY` | `evidence_kind == "formal_exception"` but formal-control observations are still `UNKNOWN_NEEDS_RUNTIME_RUN` |

Multiple hold reasons may fire together; all are recorded.

### Invariant across all paths

```
runtime_certification_status_before = NOT_CERTIFIED
runtime_certification_status_after  = NOT_CERTIFIED  # ALWAYS — enforced by D.1 __post_init__
```

A `verdict = "certify"` record is still a `NOT_CERTIFIED` app. Promotion to `RUNTIME_CERTIFIED` / `FORMAL_EXCEPTION_VERIFIED` happens only in Phase F (out of scope).

---

## 6. Failure Reason Ontology (Closed Set)

Module-level constants; no string-by-hand construction:

```python
CLOSEOUT_MISSING                      = "CLOSEOUT_MISSING"
SAMPLE_SIZE_TOO_SMALL                 = "SAMPLE_SIZE_TOO_SMALL"
WILSON_BELOW_THRESHOLD                = "WILSON_BELOW_THRESHOLD"
Z_SCORE_BELOW_THRESHOLD               = "Z_SCORE_BELOW_THRESHOLD"
UPLIFT_NOT_POSITIVE                   = "UPLIFT_NOT_POSITIVE"
CRITICAL_BLOCKERS_PRESENT             = "CRITICAL_BLOCKERS_PRESENT"
FORBIDDEN_SPAN_VIOLATION              = "FORBIDDEN_SPAN_VIOLATION"
FORMAL_CONTROL_MISSING_OR_FAILED      = "FORMAL_CONTROL_MISSING_OR_FAILED"
MANIFEST_HASH_DRIFT                   = "MANIFEST_HASH_DRIFT"
AMBIGUOUS_EVIDENCE                    = "AMBIGUOUS_EVIDENCE"
NOT_TRACE_OBSERVED_READY              = "NOT_TRACE_OBSERVED_READY"
NOT_FORMAL_EXCEPTION_OBSERVED_READY   = "NOT_FORMAL_EXCEPTION_OBSERVED_READY"

FAILURE_REASONS = frozenset({...})  # all 12 above
```

Tests assert every emitted `failure_reasons` element is `in FAILURE_REASONS`.

---

## 7. Evidence Counting Semantics

| Evidence Kind | Success source | Total source |
|---|---|---|
| `r3` | `passed_trace_observed_n` | `passed_trace_observed_n + failed_trace_observed_n` (excludes `unknown_needs_runtime_run_n`) |
| `btc` | `passed_trace_observed_n` | same as r3 |
| `formal_exception` | count of `FormalControlEvidence` with `passed == True` | count of controls with a resolved observation (pass or fail; excludes unknown) |
| `skipped` | 0 | 0 (forces `hold` or `reject`) |

### History accumulation

```
(successes, n) = (current_summary_successes, current_summary_n)
for prior in history:
    if prior.app_name == summary.app_name and prior.manifest_hash == summary.manifest_hash:
        successes += prior.trace_observed_success_n
        n         += prior.trace_observed_n
```

**`manifest_hash` drift resets the window.** If the current summary's `manifest_hash` does not match any history entry's `manifest_hash` for the same app, the history contributes zero rows — the window starts fresh. This is the intended semantics from ADR-080 §13: "Apps must have a stable manifest before they can be certified."

---

## 8. Uplift Baseline (ADR-080 §0 Q3 provisional)

```
# Pick the most recent prior decision for the same app, regardless of manifest.
prior = most_recent_by_generated_at_utc(
    [h for h in history if h.app_name == summary.app_name]
)
if prior is None:
    baseline_rate = 0.0
else:
    baseline_rate = prior.evidence_rate

uplift = current_evidence_rate - baseline_rate
```

Rationale:

- Captures the "is this week better than last week?" intent.
- Cross-manifest comparison is intentional — it detects regressions that follow manifest churn.
- Defaulting to `0.0` when no prior exists means the first-ever decision for an app has `uplift == evidence_rate`, which is positive when any evidence exists at all.

D.5 calibration may switch to rolling-4-week, at which point D.2 will accept a second optional arg. That change will carry its own Author-Gate.

---

## 9. Z-Score Computation

```
# Normal approximation against the baseline.
# Assumes baseline_rate is treated as a known proportion.
if n == 0 or baseline_rate in (0.0, 1.0):
    z_score = 0.0
else:
    std_err = sqrt(baseline_rate * (1 - baseline_rate) / n)
    z_score = max(0.0, (evidence_rate - baseline_rate) / std_err)
```

`z_score` is clamped to `>= 0.0` to match the D.1 invariant. Negative observed regressions produce `z_score = 0.0` and surface through the verdict as `UPLIFT_NOT_POSITIVE`.

---

## 10. Author-Gate Trade-offs Requiring Explicit Approval (AG-10 shape)

These are the five decisions the plan must get explicit sign-off on before D.2 implementation begins.

### AG-1: Wilson lower-bound implementation

- **⭐ Recommended**: local pure helper in `cert_decision_evaluator.py`; z=1.96 default; no scipy dependency; formula documented in a test's docstring
- **Alternative A**: depend on `scipy.stats.binom.interval` — rejected (new dep, overkill, and import cost for a one-line formula)
- **Alternative B**: reuse `agentic_core.L6_observability.promotion_gates.wilson_lower_bound` if present — investigate during implementation; if the existing helper is identical, use it; otherwise the local helper ships

### AG-2: History input shape

- **⭐ Recommended**: `Iterable[CertificationDecisionRecord] = ()` — caller owns retrieval; D.2 stays pure
- **Alternative A**: `history: HistoryReader` protocol — rejected for D.2 (I/O contract leakage)
- **Alternative B**: pull from SQLite directly inside D.2 — rejected (violates plan §1 non-goals)

### AG-3: Failure reason ontology closed vs. open

- **⭐ Recommended**: closed 12-constant set with `FAILURE_REASONS` frozenset validation
- **Alternative A**: open string set, validate only that reasons are non-empty strings — rejected (loses telemetry value, breaks weekly calibration report aggregation)

### AG-4: Verdict rule evaluation order

- **⭐ Recommended**: Step 1 (reject pre-check collects ALL firing reasons) → Step 2 (certify gate) → Step 3 (hold fallback with specific reasons)
- **Alternative A**: first-firing-wins reject — rejected (loses diagnostic detail; same cost to collect all)

### AG-5: `manifest_hash` drift handling

- **⭐ Recommended**: drift resets the evidence window to current-summary-only; a `MANIFEST_HASH_DRIFT` reason fires only when the drift leaves `n < 30` AND prior history existed (preventing false-reject on first-ever run)
- **Alternative A**: drift always triggers `MANIFEST_HASH_DRIFT` reject — rejected (would permanently block apps in active development)
- **Alternative B**: drift is silent; history mixes across manifests — rejected (violates ADR-080 §13's stable-manifest-before-cert principle)

---

## 11. Test Plan

Target: `tests/unit/tools/runtime_cert/decisions/test_cert_decision_evaluator.py`. **All tests are pure — no filesystem, no SQLite, no subprocess.**

### Required coverage (≥14 cases)

| # | Test | Assertion |
|---|---|---|
| 1 | `test_wilson_lower_bound_known_vectors` | `wilson_lower_bound(30, 30)` close to ~0.885, `(15, 30)` close to ~0.333, `(0, 0) == 0.0` |
| 2 | `test_wilson_rejects_invalid_inputs` | `n < 0`, `successes < 0`, `successes > n`, `z <= 0` all raise `ValueError` |
| 3 | `test_certify_when_all_thresholds_pass` | Fabricated summary with `n=40, successes=40`, verdict=`certify`, `failure_reasons=()`, **`status_after == NOT_CERTIFIED`** |
| 4 | `test_certify_still_keeps_status_after_not_certified` | Explicit re-assertion that a certify record is still non-promoting |
| 5 | `test_hold_on_small_n` | `n=10`, verdict=`hold`, `SAMPLE_SIZE_TOO_SMALL` in reasons |
| 6 | `test_hold_on_low_wilson` | `n=100, successes=55`, verdict=`hold`, `WILSON_BELOW_THRESHOLD` in reasons |
| 7 | `test_reject_on_critical_blocker` | blocker present → verdict=`reject`, `CRITICAL_BLOCKERS_PRESENT` in reasons, threshold-pass metrics ignored |
| 8 | `test_reject_on_forbidden_span` | one forbidden-span violation → `FORBIDDEN_SPAN_VIOLATION` |
| 9 | `test_reject_on_manifest_hash_drift` | history all on `hash_old`, current `hash_new`, current `n < 30`, history non-empty → `MANIFEST_HASH_DRIFT` |
| 10 | `test_reject_on_formal_control_failure` | formal-exception summary with a failed control → `FORMAL_CONTROL_MISSING_OR_FAILED` |
| 11 | `test_reject_collects_all_firing_reasons` | blocker + forbidden span + formal-control failure all present → three reasons in the tuple |
| 12 | `test_uplift_from_prior_history` | prior decision with `evidence_rate=0.50`, current `0.95` → `uplift == 0.45` |
| 13 | `test_uplift_no_history_uses_zero_baseline` | empty history → `uplift == current evidence_rate` |
| 14 | `test_deterministic_decision_id_via_d1_helper` | Record's `decision_id` equals `compute_decision_id(app_name, manifest_hash, closeout_report_hash)` |
| 15 | `test_no_filesystem_or_sqlite_access` | monkeypatch `builtins.open`, `sqlite3.connect`, `pathlib.Path.open` to raise; evaluator still succeeds |
| 16 | `test_one_record_per_app_summary_preserves_order` | 3 summaries in → 3 records out, same order |
| 17 | `test_skipped_evidence_kind_holds_or_rejects` | `evidence_kind="skipped"` with no blockers → `hold`; with runnable-work blocker → `reject` `AMBIGUOUS_EVIDENCE` |
| 18 | `test_history_accumulates_on_matching_manifest` | Current `n=20`, history two entries on same `manifest_hash` totalling `n=25` → combined `n=45`, certify possible |
| 19 | `test_history_does_not_accumulate_across_manifests` | Current `manifest=A n=20`, history `manifest=B n=100` → combined `n=20`, verdict=`hold` |
| 20 | `test_all_failure_reasons_are_in_closed_set` | Property test over several scenarios: every emitted reason `in FAILURE_REASONS` |

### Forbidden in tests

- Real filesystem paths (use in-memory dataclasses or `dataclasses.replace` on a fixture)
- Subprocess or `run_command`
- SQLite connections
- Network calls
- Reading real C.8 reports from `docs/reports/`

---

## 12. Stop Conditions

Implementation halts and surfaces the issue back for Author-Gate review if any of these is detected during D2.W2:

- `wilson_lower_bound` disagrees with a reference implementation (`statsmodels.stats.proportion.proportion_confint(..., method="wilson")`) by more than `1e-9` on the 10 test vectors
- The pure-function contract is broken by an implementation detail (e.g., accidental module-level state)
- A test case from §11 turns out to require actual I/O to reproduce
- Any `runtime_certification_status_after != NOT_CERTIFIED` leaks through — this should be structurally impossible because D.1 enforces it, but the test suite explicitly re-asserts it
- `tools/runtime_cert/reports/phase_c_closeout.py` or `app_route_contracts.py` have changed shape since this plan was authored and the assumed fields are missing — re-plan before implementing

---

## 13. Decisions Captured in This Plan

| # | Decision | Source | Status |
|---|---|---|---|
| 1 | Wilson lower-bound: local pure helper, z=1.96, no scipy | §4, §10 AG-1, §11 | Recommended; pending AG |
| 2 | History input: `Iterable[CertificationDecisionRecord]`, default `()` | §2, §4, §10 AG-2 | Recommended; pending AG |
| 3 | Failure reason ontology: closed 12-constant set | §6, §10 AG-3 | Recommended; pending AG |
| 4 | Verdict rule order: reject-all-reasons → certify-gate → hold-with-reasons | §5, §10 AG-4 | Recommended; pending AG |
| 5 | `manifest_hash` drift: resets window; `MANIFEST_HASH_DRIFT` fires only when it leaves `n < 30` AND prior history existed | §7, §10 AG-5 | Recommended; pending AG |
| 6 | Uplift baseline: most-recent prior decision for same app; 0.0 when no prior; D.5 may recalibrate | §8, ADR-080 §0 Q3 | Inherited from ADR |
| 7 | Wilson thresholds: global defaults (n≥30, wilson≥0.60, z≥1.96, uplift>0) | §5, ADR-080 §0 Q2 | Inherited from ADR |
| 8 | Evidence counting: successes/totals by `evidence_kind`, exclude `unknown_needs_runtime_run_n` from total | §7 | Recommended; pending AG |
| 9 | Non-promotion: D.2 returns records only; no ledger writes; no scanner/CI/status change | §1, ADR-080 §14 | Hard constraint |

---

## 14. Unresolved Questions

1. **Does a `wilson_lower_bound` already exist in `agentic_core.L6_observability.promotion_gates`?** If yes, and the formula is identical (z=1.96 default, same numerical edges), D.2 should reuse it rather than duplicate. If reuse, update §4 and add an import. Verification step, not a design change.
2. **`next_review_utc` cadence.** §4 proposes 7d (hold) / 30d (certify) / 14d (reject). ADR-080 §5 states "default 7 days for hold, 30 for certify" and is silent on reject. Confirm reject cadence (14d is reasonable; so is 7d — the app is actively broken) or default reject to 7d to match hold.
3. **Formal-control "required set".** For `evidence_kind=formal_exception`, what is the authoritative "required control list" per route shape? C.5 outputs the observed controls, but the evaluator needs to know which controls were *expected* to compute `FORMAL_CONTROL_MISSING_OR_FAILED` correctly. Resolve before D2.P3 begins — likely by consulting `system_learning/runtime_adg/app_route_contracts.py::FormalExceptionContract`.
4. **Baseline-rate z-score when baseline is 0.0 or 1.0.** §9 clamps z=0 at the boundaries. Confirm this is the desired behavior, or whether a small epsilon smoothing (e.g. treating `0.0` as `0.001`) is preferable. Epsilon smoothing complicates the math with little gain for D.2's purposes.
5. **Should `report.app_summaries` order be preserved in the output tuple?** §4 and §11 assume yes. Confirm — downstream Phase D.3 ledger writes will be order-independent (PK is `decision_id`), so preservation is a convenience not a requirement.

Each of these is tractable during D2.P1 review; none block the plan.

---

## 15. Explicit No-Certification Disclaimer

> **This plan authorises no certification.** Every `CertificationDecisionRecord`
> produced by the proposed D.2 evaluator has
> `runtime_certification_status_before == runtime_certification_status_after ==
> NOT_CERTIFIED`. The D.1 schema `__post_init__` enforces this at construction
> time — a record that claims otherwise cannot be constructed.
>
> A `verdict == "certify"` decision is **not** a certification. It is a
> statement that, if this codebase were at Phase F, the Phase F promotion
> workflow would promote the app. Phase F does not exist. No scanner
> `runtime_mode` is changed. No CI gate is added. No ledger is written.
>
> D.2 implementation begins **only after** a separate Author-Gate approves
> this plan, per ADR-080 §11. Phases D.3 / D.4 / D.5 each remain gated on
> their own Author-Gate.

---

## 16. Recommended Next Step

**Phase D.2 implementation — but only after Author-Gate approval of this plan.**

Suggested gate question (for the follow-up turn):

> The D.2 plan proposes five trade-offs (AG-1 through AG-5 in §10). Approve
> all five as recommended? Or surface specific alternatives for re-scoping?

On approval, D2.P2 (`wilson_lower_bound` helper + tests) ships first as a
standalone commit to de-risk the numerical helper, followed by D2.P3
(evaluator + tests) as a second commit. D2.P4 (ADR §11 ✅ + binding matrix
footnote) lands as the third commit once both passes are green.

No implementation begins now. No files other than this plan are modified
in the current turn.
