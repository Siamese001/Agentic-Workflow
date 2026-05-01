# ADR-080 — Runtime Certification Phase D Decision Ledger and Promotion Design

**Status**: Proposed
**Date**: 2026-05-01
**Plan**: handoff input is the Phase C closeout artifact at `tools/runtime_cert/reports/phase_c_closeout.py`
**Pairs with**: ADR-074 (Runtime Bucket as OTel View), ADR-079 (L2 Agent ↔ ADG Graph-Layer Contract)
**Predecessors**: Phase A (binding matrix), Phase B (formal exception evidence helpers), Phase C.1–C.8 (runtime-cert evidence pipeline)

> ⛔ **This ADR designs Phase D only. It does not certify any app, change scanner `runtime_mode`, add CI gates, or modify runtime behavior.** Implementation is gated on the Author-Gate decisions captured immediately below.

---

## 0. Author-Gate Decisions Captured

> Captured 2026-05-01 as a documentation-only Author-Gate pass. These
> decisions resolve enough of §12 to unblock **Phase D.1 schema work only**.
> They do **not** authorize ledger writing, scanner changes, CI gates, or
> certification promotion. Phases D.2 / D.3 / D.4 / D.5 each remain gated on
> their own Author-Gate per §11.

### Resolved

#### Q1 — Exact ADR number → **RESOLVED: `ADR-080`**

Local verification on 2026-05-01: directory scan of `docs/architecture/adr/`
matched exactly one file with the `ADR-080` prefix (this file). 68 total
ADRs on disk; the prior maximum was `ADR-079`. No registry conflict found
through local inspection. External systems (Notion ADR Registry) were not
queried in this capture pass — if a downstream conflict surfaces, this ADR
will be renumbered and cross-references in
`closed-loop-router-enforcement.md`, `intelligence-ledger-family.md`,
`docs/reports/runtime_cert/phase_c_closeout/*`, and any future Phase D
modules will be updated in lockstep.

#### Q5 — Deterministic `decision_id` → **RESOLVED: deterministic SHA-256**

`decision_id` is a deterministic SHA-256 hash of the canonicalized input
tuple `(app_name, manifest_hash, closeout_report_hash)`. The canonical
input is **JSON with sorted keys, UTF-8 encoded**:

```python
import hashlib
import json

def compute_decision_id(
    *,
    app_name: str,
    manifest_hash: str,           # 64-hex SHA-256 from compute_manifest_hash_for_app
    closeout_report_hash: str,    # 64-hex SHA-256 of the C.8 Markdown bytes
) -> str:
    payload = json.dumps(
        {
            "app_name": app_name,
            "manifest_hash": manifest_hash,
            "closeout_report_hash": closeout_report_hash,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
```

Why JSON-with-sorted-keys instead of a delimiter-joined string:

- **Delimiter-injection safety.** No app name, hash, or report hash can
  contain `:` or `|` and accidentally collide with a different tuple. JSON
  escapes any such bytes deterministically.
- **Field-shape evolution.** If a future Phase D.x adds a fourth canonical
  input (e.g. `evidence_window_start`), the JSON shape grows backwards-
  compatibly; old IDs remain valid hashes of the three-field shape.
- **External regeneration.** Any auditor with a Python interpreter can
  recompute `decision_id` from the three input strings without parsing a
  custom delimiter format.

Consequence: the §6 ledger schema's `(app_name, manifest_hash,
closeout_report_hash)` unique index becomes structurally redundant with
the `decision_id` PK — the index is the same hash projected onto three
columns. Phase D.1 schema MAY drop the unique index in favor of the PK
alone, OR keep both for query convenience. That micro-decision is
deferred to D.1.

#### Q4 — Ledger format → **RESOLVED: SQLite only for Phase D**

The per-app cert ledger at
`artifacts/ledgers/cert_decision_<app_name>.sqlite` is SQLite-only for the
entire Phase D lifecycle (D.1 through D.5). No JSONL mirror, no parallel
write path, no dual-format invariant.

Rationale:

- **Single source of truth.** Mirrored writes double the surface area for
  divergence and drift, both of which the §29 closed-loop router
  enforcement explicitly tries to prevent.
- **JSONL is downstream-tooling-only.** No current consumer needs JSONL
  during Phase D. If Phase E (CI gate) or Phase F (scanner extension)
  later requires a JSONL view for ad-hoc grep / cross-system import, it
  ships as a separate **export script** (`tools/runtime_cert/decisions/
  export_to_jsonl.py`) that reads SQLite and emits JSONL — never a
  parallel writer.
- **Pattern alignment.** All ten existing intelligence ledgers (ADR-050)
  are SQLite-only; cert-decision joins as the 11th family member with the
  same shape.

A JSONL mirror MAY be revisited in Phase E or Phase F if a real downstream
consumer requires it. The trigger is "named consumer with concrete
requirement", not "could be useful someday".

### Deferred to D.5 calibration

#### Q2 — Route-specific Wilson thresholds → **DEFERRED**

Phase D.1 / D.2 / D.3 / D.4 use the **ADR-080 §7 global defaults** for
all evidence kinds (`r3`, `btc`, `formal_exception`):

| Threshold | Default |
|---|---:|
| `n` | `≥ 30` |
| `wilson_lower` | `≥ 0.60` |
| `z_score` | `≥ 1.96` |
| `uplift` | `> 0` |

D.5 calibration produces the first weekly Wilson-CI miss report. If that
report shows that one or more route shapes systematically over- or
under-fire on the global defaults, Phase D.5 OR a follow-up
`ROUTER_DECISION:`-style Author-Gate may introduce per-route columns.
Until calibration evidence exists, the global defaults are the floor.

#### Q3 — Uplift baseline → **DEFERRED with provisional default**

Phase D.1 / D.2 / D.3 / D.4 use **prior weekly closeout** as the
provisional uplift baseline:

```
uplift = evidence_rate(this_week) - evidence_rate(last_week)
```

Where `last_week` is the most recent prior closeout for the same
`(app_name, manifest_hash)` tuple. If no prior closeout exists (first
ever run for an app), `baseline_rate = 0.0` and `uplift = evidence_rate`
on the current run.

This is provisional because:

- Single-week baselines are volatile when `n` is small.
- A rolling 4-week mean (option (c) in §12.3) is theoretically smoother
  but adds complexity and a window-resize parameter that itself needs
  calibration data to set sensibly.

D.5 calibration will produce the empirical evidence to choose between
prior-weekly and rolling-4-week. Until then, prior-weekly ships.

### Scope statement

> These decisions **unblock Phase D.1 (`CertificationDecisionRecord`
> schema) only.** They do **not** authorize:
>
> - Ledger writing (Phase D.3)
> - Closeout-to-decision evaluator implementation (Phase D.2)
> - Smoke harness execution against real apps (Phase D.4)
> - Scanner `runtime_mode` modification (Phase F — out of scope)
> - CI gate addition (Phase E — out of scope)
> - Any change to `runtime_certification_status` (still `NOT_CERTIFIED`
>   for every app)
>
> No app is certified by these decisions. No app will be certified by
> Phase D.1's implementation either — D.1 produces a Python dataclass
> definition with constructor invariants, nothing else.

---

## 1. Context

### Where we are

- **Static `apps_*` governance is closed.** Layer-gravity rules, manifest discipline, spine-delegation contracts (ADR-078) are stable. The static surface no longer changes app-by-app.
- **The Phase A/B/C runtime-certification evidence pipeline is complete.** Eight sub-phases, each non-promoting:

  | Phase | Module | Output |
  |---|---|---|
  | C.1 | `tools/runtime_cert/runtime_adg_query_adapter.py` | `PhaseC1Row` (read-only adapter) |
  | C.2 | `tools/runtime_cert/trace_row_normalizer.py` | `NormalizedTraceRow` |
  | C.3 | `tools/runtime_cert/extractors/r3_evidence.py` | `R3EvidenceReport` |
  | C.4 | `tools/runtime_cert/extractors/btc_evidence.py` | `BTCEvidenceReport` |
  | C.5 | `tools/runtime_cert/extractors/formal_exception_evidence.py` | `FormalExceptionEvidenceReport` |
  | C.6 | `tools/runtime_cert/smoke/live_trace_smoke.py` | `LiveTraceSmokeReport` |
  | C.7 | `tools/runtime_cert/reports/attribute_hardening_gap.py` | `AttributeHardeningGapReport` |
  | C.8 | `tools/runtime_cert/reports/phase_c_closeout.py` | `PhaseCCloseoutReport` |

- **Phase C produces only readiness and gap evidence.** Every output pins `runtime_certification_status = NOT_CERTIFIED`. Constructors reject any other value. Markdown emitters refuse to write a non-`NOT_CERTIFIED` report.
- **No app is certified yet.** `passed_trace_observed` and `passed_formal_exception_observed` are readiness signals only — they never promote a certification status.

### Why Phase D is needed now

Phase C answers "is the evidence in good enough shape to consider certifying?" but it cannot answer "should this app be certified?". The latter requires:

1. **A separable decision record** — distinct from the evidence — that captures verdict, statistical bounds, and reviewer attribution.
2. **An auditable ledger** — append-only, idempotent, queryable across weeks.
3. **A formal gate** — a documented promotion math that anyone can re-derive from the ledger.

Phase D introduces the **records and the math**. It does **not** wire those records into the scanner, into CI, or into runtime behavior. Phase D's only durable side effect on the system is the addition of a new ledger family file per app.

### Constraints inherited from prior phases

- **§29 closed-loop router evidence** (constitutional). Every certification decision must emit a structured `CERT_DECISION:` event AND a paired `emit_ledger_event` call in the same code path. The 10-router family pattern in `closed-loop-router-enforcement.md` is the template.
- **ADR-050 intelligence-ledger family.** Per-app cert ledgers join the existing ten ledgers as a new family, sharing the writer contract, fail-soft discipline, and consulting-skill discoverability rules.
- **Phase B/C honesty rule.** No fake-pass. If a control is unimplemented, the verdict must reflect that — not silently default to `certify`.

---

## 2. Decision

We adopt the following Phase D design (subject to implementation Author-Gate per §12):

1. **`CertificationDecisionRecord` shape** — see §5
2. **Per-app certification ledger** at `artifacts/ledgers/cert_decision_<app_name>.sqlite` — see §6
3. **Promotion verdict vocabulary**: `certify`, `reject`, `hold` — see §5
4. **Promotion gate math** — Wilson lower bound + z-score + uplift + minimum sample size, all on top of evidence-rate counts derived from C.8 closeouts — see §7
5. **Phase boundary rules** — Phase D never modifies scanner `runtime_mode`, never adds CI gates, never edits emitters, never changes app behavior — see §9

The decision is intentionally minimal: design the records and the math, defer all enforcement to Phase E (CI gate) and Phase F (scanner bucket extension + promotion workflow).

---

## 3. Status (effective)

`runtime_certification_status` for every app **remains `NOT_CERTIFIED` after Phase D ships**. The Phase D ledger captures decisions; it does not write those decisions back into the scanner's runtime-mode field. Promotion to `RUNTIME_CERTIFIED` or `FORMAL_EXCEPTION_VERIFIED` happens only after Phase F is implemented and a separate operator-driven promotion workflow runs.

This is a deliberate two-phase split:

- **Phase D** — make the decision and record it
- **Phase F** — propagate the decision into the scanner's runtime mode

The split exists so that the decision ledger can accumulate weeks of records, undergo Wilson-CI calibration drift checks, and be reviewed by humans before the scanner ever changes its observed-runtime-mode answer for any app.

---

## 4. Phase D scope (explicit boundaries)

### In scope

- Schema design for `CertificationDecisionRecord`
- Per-app SQLite ledger schema and writer contract (mirroring `intelligence-ledger-family.md`)
- Promotion gate math definition (Wilson + z-score + uplift)
- A *future* `evaluate_phase_c_closeout(report) -> CertificationDecisionRecord` evaluator function (Phase D.2)
- A *future* `write_cert_decision(record, ledger_path)` writer (Phase D.3)
- A *future* smoke harness that runs C.8 → D.2 → D.3 end-to-end without certifying anything (Phase D.4)
- A Phase D closeout doc summarizing the new ledger family entries (Phase D.5)

### Out of scope (forbidden in Phase D)

- Any change to `runtime_certification_status` written by the scanner
- Any new CI gate
- Any change to emitters, scanners, classifiers, or app behavior
- Any promotion workflow that updates the `MCP Registry` Notion DB or the scorecard
- Any modification of `passed_trace_observed` / `passed_formal_exception_observed` semantics

---

## 5. CertificationDecisionRecord shape

A frozen record produced by the *future* evaluator. JSON-serialisable; persisted as one row per call.

| Field | Type | Description |
|---|---|---|
| `decision_id` | str (uuid4 OR deterministic hash — open question §12) | Unique per decision; idempotency key for the ledger |
| `generated_at_utc` | str (ISO-8601, second precision) | When the decision was made |
| `app_name` | str | The app being decided about |
| `route_shape` | str (`R3_grounded_read` / `build_time_compiler` / `evaluator_only` / `core_adjacent_utility`) | From `AppRouteContract.route_shape` |
| `manifest_hash` | str (sha256, 64 hex) | From `compute_manifest_hash_for_app`; pins the static evidence floor |
| `evidence_kind` | str (`r3` / `btc` / `formal_exception` / `skipped`) | From C.8 `AppCloseoutSummary.evidence_kind` |
| `closeout_report_id` | str (uuid4 or filesystem path) | C.8 source report identifier |
| `closeout_report_hash` | str (sha256 of the C.8 Markdown bytes) | Canonical content hash; survives renames |
| `trace_observed_n` | int ≥ 0 | Total runs in the evidence window |
| `trace_observed_success_n` | int ≥ 0 | Runs with `passed_trace_observed=True` (or formal-exception equivalent) |
| `evidence_rate` | float ∈ [0, 1] | `trace_observed_success_n / trace_observed_n` (defined as 0.0 when n=0) |
| `wilson_lower` | float ∈ [0, 1] | Wilson lower bound on `evidence_rate` at z=1.96 |
| `z_score` | float | Standard score against the prior baseline (see uplift) |
| `uplift` | float | `evidence_rate - baseline_rate` (baseline definition is open §12) |
| `verdict` | str (`certify` / `reject` / `hold`) | Output of the gate math + blocker check |
| `failure_reasons` | tuple[str, ...] | Empty when `verdict=certify`; populated for `reject` / `hold` |
| `next_review_utc` | str (ISO-8601) | When this decision becomes stale; default 7 days for `hold`, 30 for `certify` |
| `runtime_certification_status_before` | str (always `NOT_CERTIFIED` in Phase D) | Status as observed in the scanner before this decision |
| `runtime_certification_status_after` | str (always `NOT_CERTIFIED` in Phase D) | Status the scanner will report after Phase D persists this decision — **deliberately unchanged** |

### Verdict vocabulary

- **`certify`** — gate passed; record claims the app *should* be certified once Phase F runs. **Does not** modify scanner state in Phase D.
- **`reject`** — gate failed with confidence. Forbidden span violations, failed compensating controls, or unrecoverable evidence inconsistency.
- **`hold`** — gate is inconclusive. Sample too small, evidence-rate close to the boundary, or open blocker that may resolve. Re-evaluate at `next_review_utc`.

### Status invariant

Both `runtime_certification_status_before` and `runtime_certification_status_after` are **always `NOT_CERTIFIED`** for the entire duration of Phase D. The record carries the `verdict` separately. Promotion of `runtime_certification_status_after` to `RUNTIME_CERTIFIED` / `FORMAL_EXCEPTION_VERIFIED` is a Phase F change, gated on Phase E's fail-closed CI gate landing first.

---

## 6. Per-app certification ledger design

### Location

```
artifacts/ledgers/cert_decision_<app_name>.sqlite
```

One file per app. Joins the intelligence-ledger family (ADR-050).

### Schema (sketch — finalized in Phase D.1)

```sql
CREATE TABLE IF NOT EXISTS decisions (
    decision_id            TEXT PRIMARY KEY,        -- uuid4 OR det-hash (§12)
    generated_at_utc       TEXT NOT NULL,
    app_name               TEXT NOT NULL,
    route_shape            TEXT NOT NULL,
    manifest_hash          TEXT NOT NULL,
    evidence_kind          TEXT NOT NULL,
    closeout_report_id     TEXT NOT NULL,
    closeout_report_hash   TEXT NOT NULL,
    trace_observed_n       INTEGER NOT NULL,
    trace_observed_success_n INTEGER NOT NULL,
    evidence_rate          REAL NOT NULL,
    wilson_lower           REAL NOT NULL,
    z_score                REAL NOT NULL,
    uplift                 REAL NOT NULL,
    verdict                TEXT NOT NULL CHECK (verdict IN ('certify', 'reject', 'hold')),
    failure_reasons_json   TEXT NOT NULL DEFAULT '[]',
    next_review_utc        TEXT NOT NULL,
    runtime_certification_status_before TEXT NOT NULL,
    runtime_certification_status_after  TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_decision_dedup
    ON decisions (app_name, manifest_hash, closeout_report_hash);
```

### Requirements

- **Append-only.** Existing rows are never updated; a new decision always becomes a new row.
- **Idempotent by `decision_id`.** Re-emitting the same decision is a no-op (PRIMARY KEY constraint).
- **One decision per (app, closeout report).** The `(app_name, manifest_hash, closeout_report_hash)` unique index prevents accidental duplicates within a single closeout.
- **Uses `tools/ledgers/hook_helpers.py::emit_ledger_event` if available.** Same writer contract as `intelligence-ledger-family.md` §1 — no direct `sqlite3.connect()` from the cert-decision evaluator.
- **Fail-soft on writes.** A ledger write failure must not raise; it must log a `WARNING` and continue. The `CERT_DECISION:` marker still appears in stdout/OTEL so the audit trail is preserved even when the durable record fails. Subsequent runs idempotently retry.
- **No scanner promotion.** The ledger writer never modifies any scanner-visible state. Phase F is the propagation layer.

### Marker contract

Mirroring §29 router decisions:

```
CERT_DECISION: app=<app_name> route=<route_shape> evidence=<evidence_kind> verdict=<certify|reject|hold> n=<N> wilson_lower=<F> z=<F> uplift=<F> decision_id=<id> closeout_hash=<sha256-12>
```

Plain text, one per line, emitted at decision time. Required for forensic re-binding when the durable write fails.

---

## 7. Promotion gate math

### Proposed thresholds (design defaults)

A decision becomes `verdict = certify` only when **all** of the following hold:

| Threshold | Default | Rationale |
|---|---|---|
| `n ≥ 30` | 30 | Wilson CI tightens around 30 samples; below this the lower bound is too loose to mean anything |
| `wilson_lower ≥ 0.60` | 0.60 | Lower bound, not point estimate — prevents tiny-sample optimism |
| `z_score ≥ 1.96` | 1.96 | Two-sided 95% confidence vs. baseline |
| `uplift > 0` | 0 | The evidence-rate must be strictly higher than the baseline |
| no critical blockers | — | C.8 `blocker_count` for this app must be zero, AND `AppCloseoutSummary.has_blocker` must be `False` |
| no forbidden span violations | — | C.3/C.4 `forbidden_violations` must be empty (length zero) |
| `manifest_hash` unchanged | — | The static evidence floor must be the same across every closeout in the evidence window — see "manifest pinning" below |

If any threshold fails:
- **All blockers / violations** present → `verdict = reject`; `failure_reasons` enumerates which
- **Sample size or Wilson bound short, no blockers** → `verdict = hold`; `next_review_utc` = +7 days
- **Mixed (e.g. low n + one resolvable hardening gap)** → `verdict = hold`

### Wilson lower bound rationale

For evidence rate `p_hat = success / n` at confidence z = 1.96:

```
denominator = 1 + z² / n
center      = (p_hat + z² / (2n)) / denominator
margin      = (z * sqrt(p_hat * (1 - p_hat) / n + z² / (4n²))) / denominator
wilson_lower = center - margin
```

This is the same lower-bound used by `agentic_core/L6_observability/promotion_gates.py` for the `L6/promo` router. Phase D reuses the math; it does **not** reimplement it. (`promotion_gates.py` will likely be lifted into a small shared `tools/stats/wilson.py` so cert-decision and `L6/promo` can share — but that refactor is itself an Author-Gate, not a Phase D mandate.)

### Manifest pinning

The `(app_name, manifest_hash)` tuple defines the static evidence floor. If `manifest_hash` changes mid-window:

1. The evidence window resets — prior runs no longer count toward `n`
2. A `hold` is emitted with `failure_reason = "manifest_hash changed; evidence window reset"`
3. Subsequent closeouts begin a fresh accumulation against the new `manifest_hash`

This ensures certification is anchored to a specific spine-manifest content hash; any change to that content (including comments — see ADR-B.3 / `compute_manifest_hash_for_app`) requires re-certification.

### Calibration

Thresholds above are **design defaults**. Final values require Author-Gate approval per §12 and are subject to the same intelligence-ledger calibration cadence as the 10-router family — weekly Wilson-CI miss reports, drift detection, route-specific tuning. The `wilson_lower ≥ 0.60` floor is intentionally conservative for a system that has never certified anything.

---

## 8. Formal exception verification (`FORMAL_EXCEPTION_VERIFIED` vs `RUNTIME_CERTIFIED`)

Phase D distinguishes two terminal certified states. Phase F implements the scanner buckets; Phase D defines the gate-math semantics.

### `RUNTIME_CERTIFIED`

- Source: `evidence_kind ∈ {r3, btc}`
- Evidence: `passed_trace_observed=True` from C.3 (R3) or C.4 (BTC) across the evidence window
- Gate: full §7 math (n, Wilson, z, uplift, no blockers, no forbidden violations, manifest-hash-pinned)

### `FORMAL_EXCEPTION_VERIFIED`

- Source: `evidence_kind = formal_exception`
- Evidence: `passed_formal_exception_observed=True` from C.5 across the evidence window
- Gate: §7 math **plus** all of the following:
  - **`evaluator_only` apps** use formal exception controls (CC-EVAL-01, CC-EVAL-02, …) — **not** R3 evidence. The R3 contract surface is irrelevant for these apps; the gap report is correctly skipped in C.8.
  - **`core_adjacent_utility` apps** use formal exception controls — **not** R3 evidence, **not** BTC evidence. Same gap-report skip.
  - **Unimplemented compensating controls cannot pass.** C.5 honestly reports any control listed in the manifest's `compensating_controls` but lacking a Phase B helper as `missing_controls`. Such an app cannot reach `verdict = certify` — its `failure_reasons` will list every missing control.
  - **CC-SHARED-05 must pass before `apps_shared` can be considered verified.** The B.4 `collect_cc_shared_05_evidence()` helper is canonical: `AGENTIC_CORE_STACK=full` must be set AND the strong-identity `sys.modules` checks must succeed. A `risk_bearing_allowed=True` outcome is structurally impossible (the helper hard-pins it to `False`).

### Asymmetric verdict semantics

`certify` for `RUNTIME_CERTIFIED` ≠ `certify` for `FORMAL_EXCEPTION_VERIFIED`. The `verdict` field is the same vocabulary (`certify` / `reject` / `hold`), but the *target* status differs based on `evidence_kind`. Phase F uses the (`evidence_kind`, `verdict`) pair to compute the scanner's promotion target. Phase D records both fields; it does not interpret them.

### Honesty rule

If C.5 reports `missing_controls = (CC-EVAL-01,)` for `apps_eval`, Phase D MUST emit `verdict = reject` (not `hold`) with `failure_reason = "missing implemented compensating control: CC-EVAL-01"`. Holding on missing-implementation is forbidden — it is not the kind of gap that "may resolve over time". Implementation gaps are blockers, not noise.

---

## 9. Phase boundaries

| Phase | What it does | Status |
|---|---|---|
| **A / B / C** | Evidence pipeline (binding matrix → formal-exception helpers → trace extractors → closeout) | Complete |
| **D** | Decision records + per-app cert ledger + promotion gate math | **This ADR** — design only |
| **E** | Fail-closed CI gate (`ops_scripts/ci/check_runtime_certification.py`) running Phase D math against the most recent N closeouts; refuses to merge changes that flip a previously-certifiable app to `reject` or `hold` | Pending — blocked on Phase D implementation |
| **F** | Scanner extension recognizing `RUNTIME_CERTIFIED` / `FORMAL_EXCEPTION_VERIFIED` runtime-mode buckets, plus a promotion workflow that updates Notion (MCP Registry, ADR Registry) and memory MCP from the cert ledger | Pending — blocked on Phase E |

### Strict invariants for Phase D implementation

- **Phase D may create decision records and ledgers after implementation is approved (§12).**
- **Phase D MUST NOT change scanner `runtime_mode` buckets.** That is exclusively Phase F.
- **Phase D MUST NOT add CI gates.** That is exclusively Phase E.
- **Phase D MUST NOT modify emitters, normalizers, extractors, or the C.8 closeout.** Those are stable inputs.
- **Phase D MUST NOT alter app behavior in any way.**
- **No app is certified by this ADR.** No app will be certified by the *implementation* of Phase D either — Phase D produces decision records, not certification effects.

---

## 10. Failure modes (and how Phase D handles each)

| Failure mode | Detection | Verdict | Notes |
|---|---|---|---|
| Closeout report missing | C.8 input absent or unreadable | `hold` (inconclusive — operator action required) | Cannot infer evidence without the report |
| `manifest_hash` mismatch across window | Hash drift between closeouts | `hold` + window reset (§7 manifest pinning) | Failure reason explains the reset |
| Sample size too small (`n < 30`) | C.8 evidence accumulation incomplete | `hold` | `next_review_utc` = +7 days |
| `wilson_lower < 0.60` with `n ≥ 30` | Genuine low success rate | `reject` (with high confidence) OR `hold` (if uplift trending positive — open §12) | Honest call; do not over-tune |
| Critical blockers present | `AppCloseoutSummary.has_blocker == True` | `reject` | One row per blocker in `failure_reasons` |
| Forbidden span violation | `len(forbidden_violations) > 0` | `reject` | Listed by contract name in `failure_reasons` |
| Formal-exception control missing | `len(missing_controls) > 0` for formal-exception app | `reject` | Listed by control ID in `failure_reasons`; never `hold` (§8 honesty rule) |
| Ledger write failure | `emit_ledger_event` raises; SQLite unreachable; disk full | Verdict computed but durable record missing | `CERT_DECISION:` marker still emitted to stdout/OTEL; subsequent run idempotently retries via the unique-index dedup |
| Ambiguous evidence (e.g. C.5 reports `passed_formal_exception_observed=True` but C.3 reports `passed_trace_observed=False` for an evaluator_only app — should not happen) | Cross-extractor inconsistency | `reject` with `failure_reason = "ambiguous evidence: extractors disagree"` | This is a Phase C bug, not a Phase D outcome — Phase D refuses to certify on internal inconsistency |
| Phase F not implemented yet (during D + E + early F window) | All decisions persisted, scanner unchanged | All decisions are recorded but `runtime_certification_status_after = NOT_CERTIFIED` | This is the *intended* steady state of Phase D |

---

## 11. Implementation plan (future sub-phases — not implemented now)

Future sub-phases land one-by-one through the standard Author-Gate cadence. **No implementation begins until §12 open questions are resolved.**

| Sub-phase | Output | Hard rule |
|---|---|---|
| **D.1** ✅ | Decision-record schema module (`tools/runtime_cert/decisions/cert_decision_record.py`) — frozen dataclass + `to_dict` / `to_json` + constructor invariants matching §5. **Implemented 2026-05-01** with 54 unit tests in `tests/unit/tools/runtime_cert/decisions/test_cert_decision_record.py`. No app certified; `runtime_certification_status` invariant enforced at construction. | No business logic — schema only |
| **D.2** | Closeout-to-decision evaluator (`tools/runtime_cert/decisions/cert_decision_evaluator.py`) — pure function `evaluate_phase_c_closeout(report, history) -> CertificationDecisionRecord` | Pure; no I/O; no ledger writes |
| **D.3** | Cert-ledger writer (`tools/runtime_cert/decisions/cert_decision_ledger.py`) — wraps `emit_ledger_event` with the unique-index dedup + fail-soft contract | Append-only; idempotent; no scanner promotion |
| **D.4** | Phase D smoke harness (`tools/runtime_cert/smoke/cert_decision_smoke.py`) — end-to-end C.8 → D.2 → D.3 against a single test app, asserting `runtime_certification_status_after == NOT_CERTIFIED` and the ledger row exists | No real apps certified; smoke-only |
| **D.5** | Phase D closeout doc (`docs/reports/runtime_cert/phase_d_closeout/<YYYY-Www>.md`) summarizing the new ledger family entries; references to ADR-050 | Documentation only |

Each sub-phase requires its own Author-Gate decision per §29 closed-loop router enforcement and §28 SQLite-direct fallback. Phase D as a whole is not "approved" by this ADR — only the *design* is approved (or Proposed).

---

## 12. Open questions

> ⚙️ **Status update 2026-05-01**: three of the five questions are now
> **RESOLVED** and two are **DEFERRED to D.5 calibration** with provisional
> defaults. The captured outcomes appear in §0 ("Author-Gate Decisions
> Captured") above. The original question text is preserved here for
> historical context and to make the rationale traceable.

| # | Question | Status | Outcome |
|---:|---|---|---|
| Q1 | Exact ADR number | ✅ **RESOLVED** | `ADR-080` confirmed via local directory scan (§0) |
| Q2 | Are Wilson thresholds route-specific? | ⏸ **DEFERRED to D.5 calibration** | Provisional global defaults (§0) |
| Q3 | Uplift baseline | ⏸ **DEFERRED to D.5 calibration** | Provisional default = prior weekly closeout (§0) |
| Q4 | SQLite-only or JSONL mirror? | ✅ **RESOLVED** | SQLite only for entire Phase D (§0) |
| Q5 | Deterministic `decision_id`? | ✅ **RESOLVED** | SHA-256 over canonical-JSON of three-field tuple (§0) |

### Original question rationale (for historical reference)

1. **Exact ADR number.** Currently provisionally `ADR-080`. Verify no conflicting allocation has happened; if the next ADR has been claimed by another stream, renumber and update cross-references in `closed-loop-router-enforcement.md`, `intelligence-ledger-family.md`, and the C.8 doc. *(Resolution: scan `docs/architecture/adr/` directory and the Notion ADR Registry; pick the next free number.)*
2. **Are Wilson thresholds route-specific?** The §7 defaults (`n≥30`, `wilson_lower≥0.60`) treat R3 / BTC / formal-exception apps identically. Formal-exception apps may legitimately have smaller sample sizes (low-traffic evaluators) and may need lower `n` thresholds. Counter-argument: lower `n` undermines the Wilson floor's whole point. *(Resolution: carry both default and per-route columns in the ledger; let Phase D.5 calibration data answer empirically.)*
3. **What is the uplift baseline?** Two candidates:
   - **(a)** Static evidence — the `passed_static_evidence` floor implied by `manifest_hash`. Stable, but the comparison is between runtime evidence and a static assertion which is an apples-to-oranges check.
   - **(b)** Prior weekly closeout — `evidence_rate(this_week) - evidence_rate(last_week)`. Symmetric and self-correcting, but volatile when N is small.
   - **(c)** Rolling 4-week mean, excluding the current week. Smoother, but adds complexity. *(Resolution: option (b) for the first six weeks of Phase D operation, then re-evaluate against the calibration log.)*
4. **SQLite-only or also JSONL mirror?** SQLite is the canonical ledger (`intelligence-ledger-family.md` mandate). A JSONL mirror at `artifacts/ledgers/cert_decision_<app_name>.jsonl` would simplify ad-hoc grep / external tooling but doubles write paths and risks divergence. *(Resolution: SQLite only; export-to-JSONL as a one-shot script if needed downstream.)*
5. **Should `decision_id` be a deterministic hash?** Two candidates:
   - **(a)** uuid4 — simple, opaque, requires the unique-index dedup to prevent duplicates
   - **(b)** Deterministic hash of `(app_name, manifest_hash, closeout_report_hash)` — same row idempotency without the secondary index, easier external regeneration
   *(Resolution: option (b) — the unique index in §6 *is* exactly that hash projected onto three columns; making `decision_id` itself the hash collapses it to one constraint and one PK. Trade-off is opaqueness for external observers, which is mitigated by the marker.)*

With Q1, Q4, Q5 resolved and Q2, Q3 carrying provisional defaults that
calibration will refine, **Phase D.1 schema work is unblocked**. D.2, D.3,
D.4, D.5 each remain gated on their own Author-Gate per §11.

---

## 13. Consequences

### Positive

- **Separates evidence from decision.** C.8 produces facts; Phase D produces verdicts. Different change cadences, different reviewers, different ledgers.
- **Keeps Phase D non-promoting.** The scanner does not learn about certifications until Phase F. Operators get weeks of decision-ledger evidence to review before any system surface flips. This preserves the rollback path: if Phase D's math is wrong, Phase F simply doesn't ship.
- **Provides a complete audit trail.** Every certification claim is bound to a `CertificationDecisionRecord` with a closeout report hash, statistical bounds, and a failure-reason list when applicable. Forensic re-binding is straightforward.
- **Reuses existing patterns.** The closed-loop router enforcement (§29), intelligence-ledger family (ADR-050), and `L6/promo` Wilson-CI math all exist. Phase D adds an 11th ledger family (one per app) without inventing new infrastructure.
- **Honest about formal exceptions.** The §8 distinction between `RUNTIME_CERTIFIED` and `FORMAL_EXCEPTION_VERIFIED`, and the §10 honesty rule that missing-implementation is `reject` not `hold`, are explicit guardrails against fake-pass.

### Negative

- **More machinery before the first certification.** The shortest path to certifying `apps_research` now goes through C.8 → D.1–D.5 → E → F, not through a one-off promotion script. This is intentional — every short-circuit historically created an audit gap — but it means the first certification is months away.
- **Requires evidence windows and repeated closeouts.** A Phase D `verdict = certify` requires `n ≥ 30` runs over a stable `manifest_hash`. If the manifest changes weekly (typical during active development) the window resets and `n` never accumulates. Apps must have a *stable* manifest before they can be certified — which is itself a useful invariant, but it is a new constraint that did not previously exist.
- **Two new failure modes**: ledger write failures and manifest-hash drift mid-window. Both are explicitly handled in §10, but they are real operational complexity that did not exist before Phase D.
- **Expands the intelligence-ledger family.** ADR-050 currently lists ten ledgers; Phase D adds N new ledgers (one per app). The family schema, calibration cadence, and consulting-skill discoverability all need to scale to per-app entries. This is a small but real expansion of operational surface area.

### Neutral

- **No app behavior change.** This is the explicit non-consequence — Phase D ships without any user-visible change to runtime, scanner output, or app-level functionality.

---

## 14. Final disclaimer

> **This ADR designs Phase D only. It does not certify any app, change scanner `runtime_mode`, add CI gates, or modify runtime behavior.**
>
> Implementation of Phase D requires a separate Author-Gate decision resolving §12 open questions. Even after Phase D ships, no app is certified — `runtime_certification_status` for every app remains `NOT_CERTIFIED`. Promotion to `RUNTIME_CERTIFIED` or `FORMAL_EXCEPTION_VERIFIED` happens only after Phase E (CI gate) and Phase F (scanner bucket extension + promotion workflow) ship, both of which are explicitly out of scope for this ADR.
