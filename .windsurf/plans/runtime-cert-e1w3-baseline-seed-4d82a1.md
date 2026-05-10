# Runtime Cert — E1.W3 Baseline Seed + First Evidence Report (Planning Only)

- **Plan ID**: `runtime-cert-e1w3-baseline-seed-4d82a1`
- **Status**: Completed 2026-05-10
- **Authored**: 2026-05-01
- **Branch**: `rtc-w2b-scenario-a-local-qwen-proof`
- **Parent plan**: [`runtime-cert-e1-fail-closed-ci-gate-c71f3d.md`](./runtime-cert-e1-fail-closed-ci-gate-c71f3d.md) — E-AG-1…5 APPROVED at commit `14c4e9eb5b`
- **Predecessor plan**: [`runtime-cert-e1w2-gate-module-9a4b2e.md`](./runtime-cert-e1w2-gate-module-9a4b2e.md) (plan commit `321938d681`)
- **Predecessor implementation**: E1.W2 advisory gate at commit `d59ce88ba9` — `ops_scripts/ci/check_runtime_certification.py` + tests; **36/36** gate tests pass, **175/175** combined sweep
- **ADR anchor**: [ADR-080 §11 E](../../docs/architecture/adr/ADR-080-runtime-cert-phase-d-planning.md)

> **Planning pass only.** This file authorizes **no** baseline TOML, **no** evidence report, **no** Python code, **no** CI gate, **no** pre-commit hook, **no** GitHub Actions edit, **no** scanner change, **no** emitter change, **no** app-behavior change, **no** ledger write, and **no** certification claim. E1.W3 implementation begins only after a separate scoped Author-Gate approves this plan. `runtime_certification_status` for every app remains `NOT_CERTIFIED` throughout and after this plan.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| W3.A | W3.P1 | Author-Gate approval of this plan | ~600 | E1.W2 gate committed and passing | ✅ DONE | User approves §10 decisions |
| W3.B | W3.P2 | Author baseline TOML | ~400 | W3.A approved; no prior baseline file exists | ✅ DONE | `docs/reference/runtime_certification/cert_baseline.toml` matches §2 verbatim |
| W3.C | W3.P3 | Author first weekly advisory evidence report | ~1 200 | W3.B landed; baseline parses through the gate | ✅ DONE | `docs/reports/runtime_cert/phase_e_runs/2026-W18.md` present; gate exits 0 advisory, LEDGER_MISSING as expected |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---:|---|---|
| W3.P1 | Plan approval | this plan file | Seed-only choice must be explicit; evidence-report content must not imply certification | ~600 | ✅ DONE |
| W3.P2 | Baseline TOML seed | `docs/reference/runtime_certification/cert_baseline.toml` (new) | Content must match E1.W2 schema exactly; `mode="advisory"` is load-bearing (overrides future `--strict`) | ~400 | ✅ DONE |
| W3.P3 | First evidence report | `docs/reports/runtime_cert/phase_e_runs/2026-W18.md` (new) | No-certification disclaimer verbatim; must show observed gate output honestly — including the expected LEDGER_MISSING case | ~1 200 | ✅ DONE |

---

## 1. Initial Baseline App Scope

**⭐ Recommended**: seed **only `apps_research`** in the first baseline.

Rationale:

- **First approved smoke app.** `apps_research` is the only app the C.6 live-trace smoke harness exercised end-to-end, and the only app with a confirmed R3-grounded-read route shape in the current binding matrix.
- **R3 route is the cleanest evidence class.** R3 grounded reads have a well-defined contract (`R3GroundedReadContract` + required attributes) and a populated C.6 pipeline. BTC and formal-exception routes are legitimate but introduce additional moving parts (CC-SHARED-05 full-stack assertion, formal-control static checks) that add noise to a first advisory baseline.
- **Avoid HITL / noise classes on day one.** `apps_eval`, `apps_underwriting_ai`, and `apps_shared` all carry formal-exception or evaluator-only route shapes whose baseline thresholds are not yet calibrated. Forcing them into the advisory baseline now risks spurious advisory failures and alarm fatigue (E1.W2 §14 open question 5).
- **Easy to extend.** `[[apps]]` is an array of tables; subsequent E1.W3+ turns append entries without schema churn.

### What this plan DOES NOT include in the seed

- `apps_knowledge_capture` — defer to a later E1.W3.2 scoped prompt once a successful `apps_research` run exists
- `apps_eval` / `apps_underwriting_ai` / `apps_shared` — Phase F-adjacent; baseline entries for these require threshold calibration first
- Any app without a committed manifest or without a known route shape

### Alternative considered

- **Seed 2–3 R3-grounded-read apps**. Rejected for first baseline — harder to distinguish genuine signals from calibration noise. Adding the second app is a trivial `[[apps]]` append under its own scoped prompt.

---

## 2. Proposed Baseline TOML Content (to be authored in W3.B)

**Target path**: `docs/reference/runtime_certification/cert_baseline.toml`

**Content** (exact; W3.B implementation must match this verbatim):

```toml
# Phase E.1 runtime-certification baseline — advisory seed.
#
# SCOPE
#   This file declares which apps the Phase E.1 advisory gate at
#   ops_scripts/ci/check_runtime_certification.py reads evidence for.
#   Apps absent from this file are INVISIBLE to the gate.
#
# NON-CERTIFICATION
#   This file does NOT certify any app. Every entry pins
#   expected_runtime_certification_status = "NOT_CERTIFIED" as a
#   defense-in-depth check against accidental drift. The advisory gate
#   reads the Phase D cert-decision ledgers in read-only fashion and
#   returns a build signal, NEVER a certification signal.
#
# MODE
#   mode = "advisory" forbids the CLI --strict flag from taking effect
#   regardless of who sets it. Flipping to "strict_allowed" requires the
#   separate E1.W4 Author-Gate.
#
# CONSUMERS
#   - ops_scripts/ci/check_runtime_certification.py
#   - docs/reports/runtime_cert/phase_e_runs/<YYYY-Www>.md (evidence)
#
# REFERENCES
#   - Phase E.1 plan: .windsurf/plans/runtime-cert-e1-fail-closed-ci-gate-c71f3d.md
#   - E1.W2 plan:     .windsurf/plans/runtime-cert-e1w2-gate-module-9a4b2e.md
#   - E1.W3 plan:     .windsurf/plans/runtime-cert-e1w3-baseline-seed-4d82a1.md
#   - ADR anchor:     docs/architecture/adr/ADR-080-runtime-cert-phase-d-planning.md

schema_version = "e1-baseline-v1"
mode = "advisory"

[[apps]]
app_name = "apps_research"
route_shape = "R3_grounded_read"
expected_runtime_certification_status = "NOT_CERTIFIED"
min_verdict = "hold"
require_ledger = true
manifest_hash = ""
notes = "Initial advisory baseline. Empty manifest_hash skips hash check until stable weekly evidence is available."
```

### Field-by-field rationale

| Field | Value | Why |
|---|---|---|
| `schema_version` | `"e1-baseline-v1"` | Matches E1.W2 gate's `SCHEMA_VERSION` constant exactly |
| `mode` | `"advisory"` | Pins gate to advisory behavior; any CLI `--strict` is downgraded (E1.W2 `WARNING_STRICT_DOWNGRADED_BY_BASELINE`) |
| `app_name` | `"apps_research"` | First C.6 smoke-validated app; only app with a committed R3 contract in the current binding matrix |
| `route_shape` | `"R3_grounded_read"` | Matches the R3 contract class in `tools/runtime_cert/contracts/r3_grounded_read.py`; in `_ALLOWED_ROUTE_SHAPES` |
| `expected_runtime_certification_status` | `"NOT_CERTIFIED"` | Pinned defense-in-depth; any other value → `BASELINE_APP_INVALID` |
| `min_verdict` | `"hold"` | Hold is the realistic floor for early Phase D evidence; `reject` accepts everything (pointless); `certify` too aggressive without calibration |
| `require_ledger` | `true` | Declares that apps_research MUST have a cert-decision ledger for the gate to pass. Absent ledger → `LEDGER_MISSING` (advisory-suppressed) |
| `manifest_hash` | `""` | Empty string = skip manifest-hash check per E1.W2 §3. Prevents early-rollout false positives while D.4 smoke hasn't been exercised against a pinned manifest |
| `notes` | see content | Human rationale; not parsed by the gate |

### Known runtime behavior of the seed with zero ledger evidence

If the first advisory gate run happens **before** any `apps_research` cert-decision ledger row exists:

| Gate field | Value |
|---|---|
| `result.passed` | `False` |
| `result.failures` | `()` (gate-level) |
| `result.warnings` | `("ADVISORY_FAILURES_SUPPRESSED",)` |
| `result.app_results[0].failures` | `("LEDGER_MISSING",)` |
| `result.checked_apps` | `1` |
| CLI exit code | `0` (advisory) |
| `result.runtime_certification_status` | `"NOT_CERTIFIED"` |
| `result.disclaimer` | `"no runtime certification performed …"` |

This is **honest non-green** — same pattern as the Phase D.5 closeout. The evidence report (§3) documents this outcome verbatim.

---

## 3. First Weekly Advisory Evidence Report (to be authored in W3.C)

**Target path**: `docs/reports/runtime_cert/phase_e_runs/2026-W18.md`

Sibling to `docs/reports/runtime_cert/phase_d_closeout/2026-W18.md` (existing D.5 report). First-week folder: `phase_e_runs/`. Subsequent weekly runs populate additional `<YYYY-Www>.md` siblings.

### 3.1 Required sections (W3.C implementation must produce all)

| # | Section | Content |
|---|---|---|
| 1 | Front matter | week, status, branch, commit SHAs for E1.W2 + E1.W3 baseline, ADR anchor, explicit "no runtime certification performed" disclaimer line |
| 2 | Baseline contents (verbatim) | Full copy of `cert_baseline.toml` inside a fenced code block, with explicit note that this is the advisory-seed version |
| 3 | Manual gate command | The exact `python ops_scripts/ci/check_runtime_certification.py …` invocation + env expectations (§4) |
| 4 | Expected advisory behavior | Full table from §2.last — what `passed`, `failures`, exit code, disclaimer look like in both the "no ledger" and "ledger present with verdict=hold" cases |
| 5 | No-certification disclaimer (verbatim) | Phase E.1 version of the Phase D.5 / D closeout disclaimer, pinning `runtime_certification_status = NOT_CERTIFIED`, restating that a `verdict == certify` row is non-promoting |
| 6 | Known blocker | If no `apps_research` ledger exists yet, advisory gate reports `LEDGER_MISSING`, CLI exits 0, and the weekly evidence is technically observable but empty. This is expected, not a defect. |
| 7 | Path forward to first non-blocker run | Short runbook: operator may produce a ledger row either via (a) the D.4 smoke harness with a tmp-repo-root-equivalent override, OR (b) a real C.8 closeout feeding D.2 → D.3 in sequence. **The evidence report does NOT execute either of these** — it describes them so the next weekly run can reach non-blocker state. |
| 8 | Phase E / F boundary | Verbatim reminder: Phase E.1 is advisory-only; Phase E.1 does not certify; Phase E.1 does not wire CI; Phase F is independently gated |
| 9 | Next-step recommendation | "Run the gate weekly. Replace this file sibling with `2026-W19.md` next week. Transition from `mode="advisory"` to `mode="strict_allowed"` is gated on the E1.W4 Author-Gate and requires 4 consecutive clean advisory weeks per E-AG-5 graduation criterion." |

### 3.2 What the evidence report MUST NOT contain

- No claim that any app is certified
- No claim that Phase E is "complete" — Phase E.1 is one sub-phase; E.1 only ships the advisory gate
- No JSON sidecar (report is Markdown-only, mirroring C.6/C.7/C.8/D.5 convention)
- No live-trace invocation; no D.4 smoke invocation; no C.8 closeout invocation
- No reference to `RUNTIME_CERTIFIED` / `FORMAL_EXCEPTION_VERIFIED` buckets (Phase F)
- No scanner state reference

### 3.3 Authoring discipline (for W3.C)

- Markdown-only; heading levels 1–3 mirror existing runtime-cert reports
- Every fenced code block uses realistic shell / Python / TOML — never hypothetical paths that don't exist post-W3.B
- The manual command block quotes **the exact** §4 command string; a weekly operator must be able to copy-paste

---

## 4. Manual Command (for operator + W3.C evidence report)

```powershell
python ops_scripts/ci/check_runtime_certification.py `
    --repo-root . `
    --baseline docs/reference/runtime_certification/cert_baseline.toml
```

Optional flags covered in the evidence report:

- `--report docs/reports/runtime_cert/phase_e_runs/2026-W18.json` (optional JSON sidecar; NOT authored in W3.C by default)
- `--strict` (downgraded to advisory by the baseline's `mode="advisory"`; documented for transparency only)

### 4.1 Expected advisory behavior

| Precondition | CLI exit | `result.passed` | stdout highlight |
|---|---|---|---|
| No `artifacts/ledgers/cert_decision_apps_research.sqlite` | `0` | `False` | `- apps_research: passed=False latest_verdict=None ledger_present=False failures=['LEDGER_MISSING']` |
| Ledger present with latest `verdict=hold` | `0` | `True` | `- apps_research: passed=True latest_verdict=hold ledger_present=True failures=[]` |
| Ledger present with latest `verdict=reject` | `0` | `False` | `- apps_research: passed=False latest_verdict=reject failures=['LATEST_DECISION_BELOW_BASELINE']` |
| Ledger present with latest `verdict=certify` | `0` | `True` | `- apps_research: passed=True latest_verdict=certify` — AND `runtime_certification_status: NOT_CERTIFIED` remains |

Every case emits stdout human summary + (on failures) stderr failure block. `result.runtime_certification_status == NOT_CERTIFIED` always. Advisory-mode warnings `ADVISORY_FAILURES_SUPPRESSED` fire whenever `failure_count > 0`.

### 4.2 Operator environment

- Python 3.11+ (stdlib `tomllib`); fallback to `tomli` supported
- No network / subprocess / scanner dependencies
- Runs anywhere the repo is checked out

---

## 5. No Strict Wiring — Hard Boundary

> ⛔ **E1.W3 introduces ZERO CI enforcement.**

| Surface | E1.W3 scope |
|---|---|
| `.pre-commit-config.yaml` | **NOT TOUCHED** |
| `.github/workflows/*.yml` | **NOT TOUCHED** |
| Any pre-commit hook invoking the gate | **NOT CREATED** |
| Any CI job invoking the gate | **NOT CREATED** |
| Flipping baseline to `mode="strict_allowed"` | **BLOCKED until E1.W4** |
| Wiring `--strict` flag activation anywhere | **BLOCKED until E1.W4** |

The E1.W4 Author-Gate owns the advisory→strict flip per E-AG-5 graduation criterion (4 consecutive clean advisory weeks + zero unresolved false positives). W3.B and W3.C are purely artifact-authoring phases — the gate itself is invoked only by hand.

---

## 6. Tests

No new tests are required for W3.B or W3.C.

- **W3.B**: the E1.W2 unit tests (`tests/unit/ops_scripts/ci/test_check_runtime_certification.py`, 36 cases) already cover baseline loading, schema validation, and every verdict / failure-code path against synthetic `tmp_path` TOML. A real baseline file on disk does not change gate behavior.
- **W3.C**: the evidence report is Markdown documentation; no test exists.
- **Optional smoke** (recommended, not required): after W3.B lands, run the manual gate command once from the repo root and verify `CLI exit 0` + stdout contains `runtime_cert_status: NOT_CERTIFIED`. Record the observed output verbatim into the evidence report's §4 Expected advisory behavior section as real-world confirmation.

No docs-lint hook targets `docs/reference/runtime_certification/*.toml` or `docs/reports/runtime_cert/phase_e_runs/*.md` today. If future docs-lint adds coverage (e.g., link-check, TOML schema validation), the W3.B content must pass it — but no preemptive test is authored now.

---

## 7. Stop Conditions

W3.B / W3.C halt and surface back for Author-Gate review if ANY of these is detected:

- **Pre-existing baseline file on disk**: `docs/reference/runtime_certification/cert_baseline.toml` already exists and its content conflicts with §2. Recommended action: read the existing file, compare, and escalate before overwriting. Do NOT silently overwrite.
- **`apps_research` manifest state is ambiguous**: no canonical `apps_research` manifest exists OR the manifest route-shape disagrees with `R3_grounded_read`. Escalate.
- **Writing the baseline seed would require scanner or `runtime_mode` changes** (should be structurally impossible, but enforce): stop. Phase F scope.
- **Writing the evidence report requires running live traces**: stop. W3.C must be authored from already-committed Phase D + E1.W2 evidence; no live runtime-ADG snapshot load, no D.4 smoke run, no D.2/D.3 chain invocation during W3.C authoring.
- **E1.W2 gate state reverts** (e.g., branch-switch removes `ops_scripts/ci/check_runtime_certification.py` or its tests): stop; restore via cherry-pick before proceeding.
- **Phase D state reverts** (D.4 / D.5 missing on branch): stop; restore via cherry-pick per prior recovery protocol.
- **The E1.W2 gate CI-runs against the proposed baseline and reports a gate-level `BASELINE_SCHEMA_INVALID` / `BASELINE_APP_INVALID`**: stop; fix the seed content in §2 before landing W3.B.
- **The evidence report begins to claim or imply any certification**: stop and re-author. The non-promotion invariant is load-bearing.

---

## 8. Commit Discipline

### This plan's commit (W3.A — current turn)

- Staged set: **only** `.windsurf/plans/runtime-cert-e1w3-baseline-seed-4d82a1.md`
- Subject: `plan(runtime_cert): E1.W3 baseline seed`

### W3.B implementation commit (future, separate scoped prompt)

- Staged set: **only** `docs/reference/runtime_certification/cert_baseline.toml`
- Subject: `docs(runtime_cert): E1.W3 baseline seed (advisory, apps_research)`

### W3.C implementation commit (future, separate scoped prompt)

- Staged set: **only** `docs/reports/runtime_cert/phase_e_runs/2026-W18.md`
- Subject: `docs(runtime_cert): E1.W3 first advisory evidence report`

### Unified discipline across all three commits

- Explicit `git add <path>` only — never `git add -A` / `git commit -a`
- Verify `git diff --cached --name-only` before every commit; only the intended path must appear
- Unrelated working-tree items (rtc-w2b byproducts, guardian logs, prior plan files) mentioned in commit body but NOT staged
- If any unrelated path is staged, **stop and report** — do not commit

---

## 9. Decisions Captured in This Plan

| # | Decision | Source | Status |
|---|---|---|---|
| 1 | Baseline seed scope = `apps_research` only | §1 | Recommended; pending AG |
| 2 | Baseline TOML content = exact §2 text | §2 | Hard constraint (once approved) |
| 3 | `mode = "advisory"` pin (forbids `--strict` activation) | §2 | Hard constraint |
| 4 | `min_verdict = "hold"` for `apps_research` | §2 | Recommended; pending AG |
| 5 | `require_ledger = true` | §2 | Recommended; pending AG |
| 6 | `manifest_hash = ""` (skip hash check on first seed) | §2 | Recommended; pending AG |
| 7 | First evidence report at `docs/reports/runtime_cert/phase_e_runs/2026-W18.md` | §3 | Hard constraint |
| 8 | Evidence report is Markdown-only (no JSON sidecar by default) | §3.2 | Hard constraint |
| 9 | No new tests in W3.B or W3.C | §6 | Hard constraint |
| 10 | No CI wiring, no pre-commit hook, no workflow edit | §5 | Hard constraint |
| 11 | `runtime_certification_status == NOT_CERTIFIED` preserved throughout | §2, §3 | Hard constraint |
| 12 | Phase F out of scope | §5 | Hard constraint |

---

## 10. Open Questions (for W3.A Author-Gate)

None block implementation; all are optional refinements.

1. **Include or defer `apps_knowledge_capture`** in the first seed? **Recommendation: defer.** Adds noise without observation data. Add in W3.2 once `apps_research` has one clean advisory week.
2. **Pin `manifest_hash` now or later?** **Recommendation: later.** Pinning requires a known-good manifest SHA, which requires a D.2/D.3 chain run against a pinned C.8 closeout — out of W3.B scope. Empty string is the documented E1.W2 "skip check" sentinel.
3. **Should W3.C run the gate manually and paste real output?** **Recommendation: yes** (the "Optional smoke" in §6). Capture-then-commit preserves honest weekly evidence. Operator discretion if D.4 smoke is needed first to produce a non-blocker row.
4. **JSON sidecar (`--report <path>`) for W3.C?** **Recommendation: no for first week.** Markdown-only keeps the report simple and matches the C.6/C.7/D.5 convention. Add later if a downstream tooling consumer emerges.
5. **Evidence-report cadence**: weekly, or one-time-for-E.1? **Recommendation: weekly starting now.** ISO week suffix naming already supports this. 4 clean weeks is also the E1.W4 graduation criterion, so weekly cadence is dual-purpose.

---

## 11. Boundaries (explicit)

- **E1.W3 does not certify any app.** Every reference to `runtime_certification_status` in the baseline and in the evidence report is `NOT_CERTIFIED`.
- **E1.W3 does not modify scanner `runtime_mode`.** Phase F.
- **E1.W3 does not introduce new `runtime_mode` buckets.** Phase F.
- **E1.W3 does not wire into CI.** E1.W4 under a separate Author-Gate.
- **E1.W3 does not edit `.pre-commit-config.yaml` or `.github/workflows/`.** Same as above.
- **E1.W3 does not write to any ledger.** D.3 is the sole writer.
- **E1.W3 does not touch app behavior.** No `apps_*` package is read or modified.
- **E1.W3 does not parse a live runtime-ADG snapshot or run D.4 smoke during authoring.** All content is static, committed-evidence-derived.
- **E1.W3 does not emit markers.** No `CERT_DECISION:` / `ROUTER_DECISION:` / `DEFERRED_SCOPE:` / `NEXT_STEP:` events ship via this plan.
- **E1.W3 does not create Python code.** Both deliverables are data/documentation.

---

## 12. Final Disclaimer

> **This plan does not certify any app, does not modify scanner `runtime_mode`, does not add a CI gate, does not create the baseline TOML, does not create the evidence report, and does not implement Phase F promotion.**
>
> E1.W3 is implementation planning for two documentation artifacts that feed the already-shipped E1.W2 advisory gate: (1) the first runtime-certification baseline TOML at `docs/reference/runtime_certification/cert_baseline.toml` seeding `apps_research` with `mode="advisory"`, and (2) the first weekly evidence report at `docs/reports/runtime_cert/phase_e_runs/2026-W18.md`. Nothing in this plan — not the baseline content, not the evidence-report template, not the operator command, not the cadence recommendation — promotes any app's `runtime_certification_status` from `NOT_CERTIFIED` to any other value.
>
> The baseline TOML's `mode="advisory"` field structurally forbids `--strict` CLI activation via the E1.W2 gate's defense-in-depth downgrade (`WARNING_STRICT_DOWNGRADED_BY_BASELINE`). Flipping to `"strict_allowed"` requires the separate E1.W4 Author-Gate after the E-AG-5 graduation criterion (4 consecutive clean advisory weeks + zero unresolved false positives) is met.
>
> **Phase F owns promotion and scanner bucket extension.** Phase E.1 (this waveline) feeds Phase F with evidence; Phase F decides and acts, under its own separate Author-Gate.
>
> **W3.B / W3.C implementation begins only after a separate scoped Author-Gate approves this plan.** E1.W4 (advisory→strict CI wiring) remains independently gated on its own subsequent prompt / Author-Gate. Phase F remains gated on Phase E completion.
>
> **No implementation of W3.B or W3.C begins now. No files other than this plan are modified in the current turn.**

---

## 13. Recommended Next Step

**Author-Gate approval of this plan — then W3.B (baseline TOML) implementation under a separate scoped prompt, followed by W3.C (evidence report) under its own scoped prompt.**

Suggested gate question for the follow-up turn:

> The E1.W3 plan proposes seeding only `apps_research` with `mode="advisory"` / `min_verdict="hold"` / `require_ledger=true` / empty `manifest_hash`, and authoring the first weekly evidence report at `docs/reports/runtime_cert/phase_e_runs/2026-W18.md` as Markdown-only. Approve the five §10 open-question recommendations? Or surface alternatives (add a second app, pin manifest_hash now, add JSON sidecar, different min_verdict, different cadence)?

On approval, work proceeds in two commits:

1. **W3.B** — create `docs/reference/runtime_certification/cert_baseline.toml` with the exact §2 content
2. **W3.C** — create `docs/reports/runtime_cert/phase_e_runs/2026-W18.md` with the §3 required sections

**E1.W4 (advisory→strict CI wiring) remains independently gated on its own Author-Gate.** Phase F remains gated on Phase E completion. **No E.1 implementation beyond W3.B + W3.C, and no Phase F work, is authorized by this plan.**
