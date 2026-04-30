# Contract-to-Span Binding Matrix — Runtime Certification Design (Draft v1)

**Status**: DESIGN DRAFT — requirements only. No implementation. No
runtime behavior change. No app is certified by this document.
**Generated**: 2026-04-30
**Parent doctrine**: `docs/reference/APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md`
**Predecessor**: `docs/reports/apps_static_scorecard_post_w14.md`
(closed-cohort static evidence)
**SSOT for route-shape taxonomy**: `tools/analysis/apps_spine_coverage.py`

---

## 1. Purpose and non-goals

**Purpose**: define the evidence requirements, span contract, attribute
schema, and fail-closed gate logic that runtime certification of any
`apps_*` would require — BEFORE any code is written, any runtime
emitter is changed, any scanner code is modified, or any app is
claimed to be runtime certified.

**Non-goals (hard, constitutional)**:

- **Static evidence is NOT runtime certification.** Every `apps_*`
  manifest-honored classification today (`APP_OVERLAY_STATIC_EVIDENCE`,
  `FORMAL_EXCEPTION_STATIC_EVIDENCE`) reads `runtime_certification_status:
  NOT_CERTIFIED` and this document does not change that.
- **Runtime certification requires OTel trace evidence** bound to the
  declared contract surface of each app via deterministic span names
  and required attributes. Static imports alone are insufficient.
- **No app becomes runtime-certified by this document.** This is a
  requirements artifact. Certification happens when (a) all seven
  prerequisites in the post-W14 scorecard are met AND (b) the
  fail-closed gate defined in §9 passes for the app.
- **No runtime behavior is changed.** This document does not add,
  remove, or rename any OTel span. §7 proposes names; §12 acknowledges
  that current emitters may differ.

---

## 2. Route shapes in scope

Four route shapes are in scope for runtime certification, mirroring
the closed static cohort:

| Route shape | Static count (post-W14) | Certification archetype |
|---|:---:|---|
| `build_time_compiler` | 1 (apps_qna) | Compile-time pack build + validated intake; NOT the full L1→L0→C0→PA→L2→Exit chain |
| `R3_grounded_read` | 5 (apps_research, apps_exec, apps_lic, apps_rfp, apps_rg) | Full 8-span chain: intake → plan → route → retrieve → evidence → prompt → seal → exit |
| `evaluator_only` | 1 (apps_eval) | Formal exception; verifies circular-dependency bypass controls (CC-EVAL-*) |
| `core_adjacent_utility` | 2 (apps_underwriting_ai, apps_shared) | Formal exception; verifies domain-specific OR shared-library compensating controls |

`R3R4_managed_workflow` is **not in scope** in the closed cohort
because no app has a proven durable-write surface. If a future app
declares `R3R4`, the matrix in §4 extends with a mandatory
`commit_request` span — see §9 fail-closed logic.

---

## 3. Certification levels

The classification ladder has four levels. Promotion is monotonic —
an app can move up only with additional evidence; demotion requires
loss of required evidence.

| Level | Evidence required | Where recorded today |
|---|---|---|
| **STATIC_EVIDENCE** | A manifest declares `claimed_routes`; the scanner confirms direct imports match the route's contract requirements (or a formal exception charter with compensating controls is recorded). | `tools/analysis/apps_spine_coverage.py` + per-app `spine_manifest.yaml` |
| **TRACE_OBSERVED** | In addition to STATIC_EVIDENCE, at least one qualifying OTel trace has been captured in a dev/staging environment showing the required spans for the declared route. Does NOT require sustained coverage or production-environment evidence. Useful as a smoke signal before RUNTIME_CERTIFIED. | *(not yet implemented — future trace collector)* |
| **RUNTIME_CERTIFIED** | TRACE_OBSERVED **plus** all four sustained-coverage conditions: (a) ≥ N qualifying traces across a representative request distribution (N TBD, see §12), (b) every required span present on every trace, (c) no extra durable-write spans unless route permits, (d) fail-closed CI gate (§9) reports PASS. Applies to `build_time_compiler` and `R3_grounded_read` apps. | *(future — requires §11 phases)* |
| **FORMAL_EXCEPTION_VERIFIED** | Parallel to RUNTIME_CERTIFIED for formal-exception apps. Requires negative evidence proving each compensating control. Verification shape differs per exception (§6). | *(future)* |

An app may hold `STATIC_EVIDENCE` indefinitely without being promoted
— the post-W14 state is exactly this.

---

## 4. R3_grounded_read contract-to-span matrix

Each R3 app must emit the following **eight required spans** per
governed request. Absence of any required span is a certification
failure (§9).

### 4.1 Span contract table

| # | Contract | Proposed span name | Required attributes | Required contract ID | Parent expectation | Failure condition |
|:---:|---|---|---|---|---|---|
| 1 | `ValidatedRequest` | `app.<app_name>.intake.validated_request` | `app_name`, `route_shape=R3_grounded_read`, `run_id`, `contract_name=ValidatedRequest`, `contract_id`, `manifest_hash` | `request_id` (uuid4) | Root of the run; no parent | Span missing, `contract_name` mismatched, or `contract_id` empty |
| 2 | `L1PlanContract` | `app.<app_name>.l1.plan_contract` | standard + `contract_name=L1PlanContract`, `contract_id=plan_id`, `parent_contract_id=<request_id>`, `sub_query_count` | `plan_id` | Parent: span #1 | Missing, or `parent_contract_id` ≠ request_id |
| 3 | `RouteContract` | `app.<app_name>.l0.route_contract` | standard + `contract_name=RouteContract`, `contract_id=route_id`, `parent_contract_id=<plan_id>`, `route_target`, `l0_confidence` | `route_id` | Parent: span #2 | Missing, or route_target not in manifest's declared routing targets |
| 4 | `RetrievalPlan` | `app.<app_name>.c0.retrieval_plan` | standard + `contract_name=RetrievalPlan`, `contract_id=retrieval_plan_id`, `parent_contract_id=<route_id>`, `collection`, `k` | `retrieval_plan_id` | Parent: span #3 | Missing, or `k ≤ 0` |
| 5 | `FinalEvidenceContract` | `app.<app_name>.c0.final_evidence_contract` | standard + `contract_name=FinalEvidenceContract`, `contract_id=evidence_id`, `parent_contract_id=<retrieval_plan_id>`, `evidence_hash`, `citation_count`, `support_coverage` | `evidence_id` | Parent: span #4 | Missing, or `evidence_hash` empty |
| 6 | `CompiledPromptArtifact` **or** `PromptEnvelope` | `app.<app_name>.pa.compiled_prompt_artifact` | standard + `contract_name ∈ {CompiledPromptArtifact, PromptEnvelope}`, `contract_id=prompt_artifact_id`, `parent_contract_id=<evidence_id>`, `abstain_recommended` | `prompt_artifact_id` | Parent: span #5 | Missing; both names forbidden — must match manifest's declared equivalent |
| 7 | `SealedArtifact` | `app.<app_name>.l2.sealed_artifact` | standard + `contract_name=SealedArtifact`, `contract_id=sealed_artifact_id`, `parent_contract_id=<prompt_artifact_id>`, `artifact_hash`, `grounded` (bool), `gate_disposition` | `sealed_artifact_id` | Parent: span #6 | Missing, or `artifact_hash` empty, or `grounded=False` with `gate_disposition=allow` |
| 8 | `ExitReviewPacket` | `app.<app_name>.exit.review_packet` | standard + `contract_name=ExitReviewPacket`, `contract_id=exit_packet_id`, `parent_contract_id=<sealed_artifact_id>`, `exit_disposition`, `l6_ingested` (bool) | `exit_packet_id` | Parent: span #7 | Missing; or emitted **without** span #7 (see §10 negative control) |

### 4.2 Example evidence record shape

One qualifying R3 trace record must conform to this JSON shape for the
trace collector to accept it:

```json
{
  "app_name": "apps_rfp",
  "route_shape": "R3_grounded_read",
  "manifest_hash": "<sha256 of apps_rfp/spine_manifest.yaml>",
  "run_id": "rfp-abc123",
  "trace_id": "<otel trace id>",
  "static_runtime_mode": "APP_OVERLAY_STATIC_EVIDENCE",
  "runtime_certification_status": "TRACE_OBSERVED",
  "spans": [
    {"name": "app.apps_rfp.intake.validated_request",
     "contract_name": "ValidatedRequest", "contract_id": "req-...",
     "parent_contract_id": null},
    {"name": "app.apps_rfp.l1.plan_contract",
     "contract_name": "L1PlanContract", "contract_id": "plan-...",
     "parent_contract_id": "req-..."},
    {"name": "app.apps_rfp.l0.route_contract",
     "contract_name": "RouteContract", "contract_id": "route-...",
     "parent_contract_id": "plan-..."},
    {"name": "app.apps_rfp.c0.retrieval_plan",
     "contract_name": "RetrievalPlan", "contract_id": "rp-...",
     "parent_contract_id": "route-..."},
    {"name": "app.apps_rfp.c0.final_evidence_contract",
     "contract_name": "FinalEvidenceContract", "contract_id": "evid-...",
     "parent_contract_id": "rp-...", "evidence_hash": "<sha256>"},
    {"name": "app.apps_rfp.pa.compiled_prompt_artifact",
     "contract_name": "CompiledPromptArtifact", "contract_id": "pa-...",
     "parent_contract_id": "evid-..."},
    {"name": "app.apps_rfp.l2.sealed_artifact",
     "contract_name": "SealedArtifact", "contract_id": "sealed-...",
     "parent_contract_id": "pa-...", "artifact_hash": "<sha256>",
     "grounded": true, "gate_disposition": "allow"},
    {"name": "app.apps_rfp.exit.review_packet",
     "contract_name": "ExitReviewPacket", "contract_id": "exit-...",
     "parent_contract_id": "sealed-...", "exit_disposition": "accepted"}
  ]
}
```

All 8 entries are mandatory for an R3 trace to be qualifying. An
`apps_rg` trace with only 7 spans (e.g., missing `RetrievalPlan`
because `rg_docs` degraded gracefully) is **not qualifying** — the
contract surface requires the full chain even when the retrieval
collection is empty.

---

## 5. `build_time_compiler` matrix (apps_qna)

apps_qna's runtime shape is materially different from R3 apps. It
compiles a paste-pack at build time, validates the intake envelope,
and emits a ledger event. It does **NOT** run the L1 → L0 → C0 → PA →
L2 → Exit chain — making it share the R3 matrix would be contract
theater.

### 5.1 Required spans

| # | Role | Proposed span name | Required attributes | Required contract ID |
|:---:|---|---|---|---|
| 1 | Intake envelope | `app.apps_qna.intake.validated_request` | `app_name=apps_qna`, `route_shape=build_time_compiler`, `run_id`, `contract_name=ValidatedRequest`, `contract_id=request_id`, `manifest_hash` | `request_id` |
| 2 | Build-artifact identity | `app.apps_qna.build.pack_artifact` | standard + `build_artifact_id`, `source_pack_id`, `output_pack_hash`, `parent_contract_id=<request_id>` | `build_artifact_id` |
| 3 | Ledger emission (governance signal) | `app.apps_qna.ledger.emit` | standard + `ledger_name=apps_qna_build`, `ledger_event_id`, `parent_contract_id=<build_artifact_id>` | `ledger_event_id` |

### 5.2 Forbidden claims

Until empirical trace evidence confirms otherwise, the runtime-cert
harness for apps_qna **MUST NOT** assert the presence of:

- `l1.plan_contract`, `l0.route_contract`, `c0.retrieval_plan`,
  `c0.final_evidence_contract`, `pa.compiled_prompt_artifact`,
  `l2.sealed_artifact`, `exit.review_packet`

These are R3-shape spans that `build_time_compiler` does not promise
to emit. If a future apps_qna implementation grows into R3 shape, its
manifest must first change `claimed_routes` from
`[build_time_compiler]` to include `R3_grounded_read`, and only then
do the R3 spans become required.

### 5.3 Success criteria

An apps_qna trace is qualifying when:

- All 3 spans in §5.1 are present with correct attributes
- `output_pack_hash` is a non-empty hex digest (64 chars if SHA-256)
- `source_pack_id` resolves to a known source pack in the build registry
- The `ledger.emit` span records a terminal governance event (build completed, build rejected, or build skipped — enumerated values only)

---

## 6. Formal exception verification

Formal exceptions have empty required-contract sets **by design**.
Empty-set does not mean "no runtime evidence needed" — it means the
evidence shape is different. Each exception requires **negative
evidence** demonstrating its compensating controls are active.

### 6.1 `evaluator_only` — apps_eval

| CC | Evidence required at runtime |
|---|---|
| **CC-EVAL-01** | apps_eval runs MUST NOT be re-routed through an evaluator-of-evaluator loop. Negative check: **no trace whose root span `app_name=apps_eval` has a descendant span with `app_name=apps_eval`**. |
| **CC-EVAL-02** | apps_eval MUST NOT import or invoke R3 contracts at runtime. Negative check: no `contract_name ∈ {ValidatedRequest, L1PlanContract, RouteContract, ...}` span with `app_name=apps_eval` outside the explicitly-allowed evaluator-only evaluation surface. |
| **CC-EVAL-03** | apps_eval evaluation outputs MUST be stable under the charter (see `apps_eval/spine_manifest.yaml` CC-EVAL-03). Positive check: a dedicated evaluator stability span must emit with a deterministic `evaluation_id`. |
| **CC-EVAL-04** | apps_eval runs are reviewed annually. Positive check: not runtime-observable (governance, not trace); out of scope for FORMAL_EXCEPTION_VERIFIED. |

### 6.2 `core_adjacent_utility` + `regulatory_domain` — apps_underwriting_ai

| CC | Evidence required at runtime |
|---|---|
| **CC-UW-01** | apps_underwriting_ai handles credit decisions as a regulated domain library surface. Positive check: every call path that emits a credit decision must also emit `app.apps_underwriting_ai.governance.regulated_decision` with `decision_id`, `regulation_bundle_id`, and `audit_link`. |
| **CC-UW-02** | apps_underwriting_ai MUST NOT inherit arbitrary R3 contracts. Negative check as in CC-EVAL-02 but scoped to `app_name=apps_underwriting_ai`. |
| **CC-UW-03** | apps_underwriting_ai calls are bounded by the `regulatory_domain` charter's permitted operations list. Positive check: every span with `app_name=apps_underwriting_ai` must have `operation_kind ∈ <charter-permitted set>`. |
| **CC-UW-04** | apps_underwriting_ai review cadence is annual (governance, not trace). Out of scope for FORMAL_EXCEPTION_VERIFIED. |

### 6.3 `core_adjacent_utility` + `shared_library_surface` — apps_shared

apps_shared has NO runtime entrypoint (no `__main__.py`). Its
verification shape is different from apps_eval and apps_underwriting_ai —
it verifies the **absence** of certain trace conditions and the
specific behavior of CC-SHARED-05.

| CC | Evidence required at runtime |
|---|---|
| **CC-SHARED-01** | apps_shared hosts the `GovernedAppRunner` substrate consumed by R3 apps. Positive check: the 5 R3 apps' `app.<app_name>.intake.validated_request` → `app.<app_name>.exit.review_packet` chains are emitted by workflows rooted in `apps_shared.integrations.governed_app_runner.GovernedAppRunner`. |
| **CC-SHARED-02** | apps_shared provides `APP_REGISTRY`. Not runtime-observable per-span; verified at cert-harness startup by reading the registry. |
| **CC-SHARED-03** | `SealedArtifact` import in apps_shared is proof-harness only. Negative check: **no production trace contains a `contract_name=SealedArtifact` span originated by `apps_shared/proof/`**. This is a code-path assertion, not a span presence/absence check — requires file-origin attribution in trace metadata. |
| **CC-SHARED-04** | Quarterly platform review. Governance; out of scope for FORMAL_EXCEPTION_VERIFIED. |
| **CC-SHARED-05** | **Handled as a negative-evidence check**. The certification run MUST prove one of: (a) the run was executed in full-stack mode AND `agentic_core_shim.install()` was observed to early-return (captured either via a boot-time telemetry event or by asserting the absence of any of the 12 shimmed `sys.modules` entries at the end of the run), OR (b) the run explicitly excludes standalone mode by environment-variable assertion (`AGENTIC_CORE_STACK=full`), OR (c) standalone mode is empirically ruled out by the three-evidence audit (packaging / CI / deployment) already specified in the post-W14 scorecard. Certification MUST be denied if the cert harness cannot distinguish full-stack from standalone. |

**Core principle**: FORMAL_EXCEPTION_VERIFIED for apps_shared certifies
the *absence* of risk-bearing execution in the shimmed branch, not
the *presence* of a contract chain. This is a structurally different
harness from the R3 apps' positive contract-chain verification.

---

## 7. Span naming convention

All proposed span names follow the deterministic pattern:

```
app.<app_name>.<layer>.<contract_surface>
```

Where:
- `<app_name>` is the `apps_*` directory name verbatim
- `<layer>` is one of: `intake`, `l1`, `l0`, `c0`, `pa`, `l2`, `exit`, `build`, `ledger`, `governance`
- `<contract_surface>` is the snake_case canonical name of the contract, or a role name for non-contract spans

Examples (all proposed, none asserted to exist today):

| Proposed name | Example app |
|---|---|
| `app.apps_rfp.intake.validated_request` | apps_rfp |
| `app.apps_rg.l1.plan_contract` | apps_rg |
| `app.apps_lic.l0.route_contract` | apps_lic |
| `app.apps_exec.c0.retrieval_plan` | apps_exec |
| `app.apps_research.c0.final_evidence_contract` | apps_research |
| `app.apps_rfp.pa.compiled_prompt_artifact` | apps_rfp |
| `app.apps_lic.l2.sealed_artifact` | apps_lic |
| `app.apps_exec.exit.review_packet` | apps_exec |
| `app.apps_qna.build.pack_artifact` | apps_qna |
| `app.apps_qna.ledger.emit` | apps_qna |
| `app.apps_underwriting_ai.governance.regulated_decision` | apps_underwriting_ai |

> ⚠️ **PROPOSED — existing OTel span names may differ.** This document
> does **NOT** rename any existing emitter. The §11 implementation plan
> requires a **trace inventory** phase (Phase A) that audits the actual
> emitted span names across the cohort and reconciles them with this
> proposal. If the current names differ, two routes exist:
> (a) amend this matrix to match the emitted names (doc change only);
> (b) schedule a controlled rename program. Neither happens in this
> document.

---

## 8. Required trace attributes

Every certifying span MUST carry the following attributes. Missing
any of the 10 required attributes is a certification failure.

| Attribute | Type | Required? | Source of truth |
|---|---|:---:|---|
| `app_name` | string | ✅ | Span emitter |
| `route_shape` | string | ✅ | Manifest's `claimed_routes` (single value per trace) |
| `run_id` | string | ✅ | Request correlation id |
| `trace_id` | string | ✅ | OTel trace identifier |
| `contract_name` | string | ✅ | Canonical contract name (e.g., `ValidatedRequest`) |
| `contract_id` / `artifact_id` | string | ✅ | Per-contract unique id (e.g., `plan_id`, `sealed_artifact_id`) |
| `manifest_hash` | string (sha256) | ✅ | Hash of the app's `spine_manifest.yaml` at run time |
| `static_runtime_mode` | string | ✅ | One of `APP_OVERLAY_STATIC_EVIDENCE` / `FORMAL_EXCEPTION_STATIC_EVIDENCE` (from current scanner output) |
| `runtime_certification_status` | string | ✅ | One of `NOT_CERTIFIED` / `TRACE_OBSERVED` / `RUNTIME_CERTIFIED` / `FORMAL_EXCEPTION_VERIFIED` (from cert harness) |
| `parent_contract_id` | string | ⚠️ conditional | Required for all spans except the root (`intake.validated_request` / `build.pack_artifact`) |
| `evidence_hash` | string | ⚠️ conditional | Required on `final_evidence_contract` |
| `exit_disposition` | enum | ⚠️ conditional | Required on `exit.review_packet` (`accepted` / `rejected_soft` / `rejected_hard` / `deferred`) |

Attributes not in this list MAY be present but MUST NOT be required
by the cert harness. Keeping the cert contract narrow avoids coupling
to incidental telemetry.

---

## 9. Runtime certification gate logic (fail-closed)

The cert harness MUST reject certification in **any** of the following
conditions. All checks are ANDed — every check must PASS for the app
to earn `RUNTIME_CERTIFIED` (or `FORMAL_EXCEPTION_VERIFIED`).

### 9.1 R3_grounded_read gate

```
PASS iff all_of:
  - for each trace in sample:
    - all 8 required spans present (§4.1)
    - each span has all 10 required attributes (§8) with non-empty values
    - parent_contract_id chain is well-formed (root → 8 → exit)
    - route_shape == "R3_grounded_read"
  - no span in any trace has contract_name == "CommitRequest"        ← see §9.3
  - no span has static_runtime_mode != expected bucket
  - manifest_hash matches current manifest-on-disk
  - sample size >= N_R3  (N_R3 TBD — see §12)
```

### 9.2 build_time_compiler gate (apps_qna)

```
PASS iff all_of:
  - for each trace in sample:
    - all 3 required spans present (§5.1)
    - output_pack_hash is a 64-char hex SHA-256
    - ledger.emit span records a terminal event
  - no span has contract_name ∈ {L1PlanContract, RouteContract,
      RetrievalPlan, FinalEvidenceContract, CompiledPromptArtifact,
      SealedArtifact, ExitReviewPacket, CommitRequest}
  - sample size >= N_BTC  (N_BTC TBD — see §12)
```

### 9.3 R3 vs R3R4 discriminator (critical)

```
if any span in the sample has contract_name == "CommitRequest":
  if manifest's claimed_routes does NOT include "R3R4_managed_workflow":
    certification = DENIED
    reason = "CommitRequest emitted but manifest declares R3_grounded_read"
  else:
    (future) R3R4 matrix applies — out of scope for this document
```

This check is how the fail-closed gate prevents contract theater in
the R3 direction AND prevents silent promotion to R3R4 without a
manifest change.

### 9.4 Formal-exception gate

```
PASS iff all_of:
  - no span with app_name == app_under_cert contradicts its charter
  - each compensating control in the manifest has observed evidence
    (positive for CC-EVAL-03 / CC-UW-01 / CC-UW-03 / CC-SHARED-01;
     negative for CC-EVAL-01 / CC-EVAL-02 / CC-UW-02 / CC-SHARED-03 /
     CC-SHARED-05-a|b|c)
  - governance CCs (CC-EVAL-04, CC-UW-04, CC-SHARED-04) are excluded —
    not runtime-observable
```

### 9.5 Ambiguous-evidence default

Any unparseable trace, missing attribute, or inconsistent manifest
hash results in `certification = DENIED`. The gate never "infers" a
missing field, never fills a default value, and never grants partial
credit.

---

## 10. Negative controls

The cert harness MUST include explicit negative-control tests that
force denial. Each test is a synthetic or replayed trace designed to
fail exactly one gate condition.

| Control | Expected outcome | Why |
|---|---|---|
| **App missing L1 span** | R3 gate → DENIED (reason: "missing required span `app.<X>.l1.plan_contract`") | Asserts §9.1's "all 8 required spans" check is live |
| **App emits `ExitReviewPacket` without `SealedArtifact`** | R3 gate → DENIED (reason: "exit.review_packet present but l2.sealed_artifact missing; parent_contract_id chain broken") | Asserts §4.1 failure condition on span #8 |
| **App emits `CommitRequest` but manifest declares only `R3_grounded_read`** | Gate → DENIED (reason: "CommitRequest emitted; manifest does not declare R3R4_managed_workflow") | Asserts §9.3 discriminator |
| **apps_shared standalone shim active during cert run** | FORMAL_EXCEPTION_VERIFIED gate → DENIED (reason: "CC-SHARED-05 check failed; 12 shimmed sys.modules entries detected or env flag absent") | Asserts §6.3 CC-SHARED-05 |
| **apps_eval routed through normal runtime causing eval-of-evaluator circularity** | FORMAL_EXCEPTION_VERIFIED gate → DENIED (reason: "CC-EVAL-01 negative check failed; trace contains descendant span with `app_name=apps_eval`") | Asserts §6.1 CC-EVAL-01 |
| **Manifest-on-disk changed after trace emission** | Gate → DENIED (reason: "manifest_hash in trace does not match current manifest on disk") | Asserts §8 `manifest_hash` freshness |
| **Span has all 10 required attributes but `contract_id` is empty string** | Gate → DENIED (reason: "empty contract_id on span <X>") | Asserts non-empty-value requirement from §8 |

Every negative control MUST be runnable as a unit test against the
cert harness without requiring a live app invocation.

---

## 11. Implementation plan (design only — no code in this document)

Six future phases. Each phase is a distinct change-set requiring its
own Author-Gate approval, plan file (`.windsurf/plans/<slug>-<6hex>.md`),
and wave structure. **No code is written in the present document.**

| Phase | Name | Output | Blocked by |
|:---:|---|---|---|
| **A** | Trace inventory | Audit of actual OTel span names / attributes emitted today by each app. Reconcile with §7 proposed naming. Decide: doc change vs controlled rename. | — |
| **B** | Binding schema | Formal schema for the evidence record shape (§4.2) as a pydantic or dataclass. Place under `tools/runtime_cert/schema.py` or `agentic_core/runtime/cert/`. | Phase A |
| **C** | Trace collector / runtime ADG ingest | Pipeline that consumes OTel spans (via `otel_mcp` or direct OTel collector) into the runtime-ADG store. Produces per-app trace records in the schema from Phase B. | Phase B |
| **D** | Certification report generator | Offline tool that runs the fail-closed gate (§9) against a sample of traces and produces a per-app certification report (`docs/reports/runtime_cert/<app>/<YYYY-Www>.md`). | Phase C |
| **E** | Fail-closed CI gate | `ops_scripts/ci/check_runtime_certification.py` that runs Phase D on the last-N-days of traces for any app claiming `TRACE_OBSERVED` or higher, and blocks regression. | Phase D |
| **F** | Promotion process to RUNTIME_CERTIFIED | Scanner extension recognizing a new `runtime_mode` bucket (`RUNTIME_CERTIFIED`, `FORMAL_EXCEPTION_VERIFIED`) and a promotion workflow that updates the scorecard + Notion ADR + memory. | Phase E |

Constitutional note: phases D, E, and F introduce new intelligence
ledgers per §29 — every cert-report emission and every gate decision
must emit a `CERT_DECISION:` event bound to a per-app ledger. That
ledger family is out of scope here (design doc for the binding matrix
only).

---

## 12. Open questions

These questions MUST be resolved before Phase A produces a deliverable
(much less Phase D certifying an app):

| # | Question | Default stance (pending evidence) |
|:---:|---|---|
| **Q1** | Do current emitters produce spans whose names match §7? If not, under what names? | Unknown. Default: assume not; Phase A must inventory. |
| **Q2** | Can the runtime ADG serve as the evidence store for Phases C–E, or does it need a dedicated store? | Default: reuse runtime ADG for Phase C ingest; reconsider for Phase D report cache only if query latency is unacceptable. |
| **Q3** | What is `N_R3` (sample-size threshold for sustained coverage for R3 apps)? | No accepted value. Suggestions: statistical minimum at 95% CI width ≤ 5% → probably ≥ 100 traces. Needs simulation; defer to Phase D design. |
| **Q4** | What is `N_BTC` for apps_qna (`build_time_compiler`)? | Probably smaller than N_R3 because the compile surface is narrower; suggest ≥ 30. Needs Phase D design. |
| **Q5** | Do formal-exception apps need separate cert harnesses, or can one harness with per-shape switches handle all 3? | Default: **separate harnesses** — the positive-chain shape for apps_eval's CC-EVAL-03 and apps_underwriting_ai's CC-UW-01 differs from apps_shared's negative-evidence shape enough that a unified harness would over-couple. Revisit after Phase B. |
| **Q6** | How is `manifest_hash` computed — whole-file SHA-256 of raw bytes, or YAML-canonicalized? | Default: whole-file SHA-256 of raw bytes. Simpler; any change in YAML formatting (comments, spacing) intentionally triggers re-cert. |
| **Q7** | Do R3 apps' `CompiledPromptArtifact` vs `PromptEnvelope` equivalence (apps_rg today) need tracking in the trace, or is either name acceptable? | Default: either name acceptable; cert harness consults the app's declared equivalence group (from `CONTRACT_EQUIVALENT_GROUPS` in the scanner). |
| **Q8** | What is the sunset condition for `STATIC_EVIDENCE` — can an app stay there forever, or must it promote within a time bound? | Default: no time bound. `STATIC_EVIDENCE` is a permanent classification until the app opts into cert work. |
| **Q9** | If an app is `RUNTIME_CERTIFIED` and a regression causes one required span to drop out, what is the demotion path? Immediate demotion to `STATIC_EVIDENCE`, or an intermediate `CERT_DEGRADED` bucket? | Default: immediate demotion to `STATIC_EVIDENCE` with a `cert_loss_reason` attribute. Intermediate bucket adds complexity for marginal benefit. |
| **Q10** | How is apps_shared's CC-SHARED-05 full-stack vs standalone distinction asserted at the trace level — boot-time telemetry event, env-var assertion, or both? | Default: require **both** — env-var assertion at harness startup AND the absence of the 12 shimmed `sys.modules` entries at run end. Redundant evidence for a safety-critical control. |

---

## 13. Final statement

> **This document defines runtime-certification requirements only.
> It does not certify any app.**
>
> The apps_* cohort remains in its post-W14 state:
> - 6 apps in `APP_OVERLAY_STATIC_EVIDENCE`
> - 3 apps in `FORMAL_EXCEPTION_STATIC_EVIDENCE`
> - 0 apps in `RUNTIME_CERTIFIED`
> - 0 apps in `FORMAL_EXCEPTION_VERIFIED`
> - Every app reads `runtime_certification_status: NOT_CERTIFIED`
>
> Runtime certification will happen when (a) the §11 implementation
> phases ship and (b) a specific app's traces clear the §9 fail-closed
> gate. Until both conditions hold, no app is runtime certified.

---

## Provenance

| Item | Value |
|---|---|
| Doc version | v1 (DESIGN DRAFT) |
| Generated | 2026-04-30 |
| Parent SSOT | `tools/analysis/apps_spine_coverage.py`, `docs/reference/APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md` |
| Related | `docs/reports/apps_static_scorecard_post_w14.md` |
| Drafted in response to | Post-W14 scorecard §"Runtime certification remains future work" (7 prerequisites) |
| Implementation status | none — this document is design-only |
| Apps affected by this document | zero (no runtime behavior change) |
