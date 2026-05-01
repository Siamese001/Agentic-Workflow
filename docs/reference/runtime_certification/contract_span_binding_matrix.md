# Contract-to-Span Binding Matrix — Runtime Certification Design (v2, Phase-B.1 reconciled)

**Status**: DESIGN v2 — requirements only. No implementation. No
runtime behavior change. No app is certified by this document.
Reconciled against the Phase A trace inventory.
**Generated**: 2026-04-30 (v1); **reconciled**: 2026-04-30 (v2, Phase B.1)
**Parent doctrine**: `docs/reference/APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md`
**Predecessor**: `docs/reports/apps_static_scorecard_post_w14.md`
(closed-cohort static evidence)
**SSOT for route-shape taxonomy**: `tools/analysis/apps_spine_coverage.py`
**Trace inventory input**: `docs/reports/runtime_certification/phase_a_trace_inventory.md`

---

## 0. Delta from v1 (Phase B.1 reconciliation summary)

This v2 revision is **documentation-only**. No span was renamed,
no emitter was modified, no Python was written, no CI gate was added,
no app's certification status changed.

What v2 changes vs v1:

- **§4 R3 matrix** — adds 5 columns capturing the Phase A finding for
  each of the 8 R3 contracts: **Phase A status**, **existing emitter
  / Tier-1 category**, **normalized cert alias**, **attribute
  hardening needed**, **live trace required?**. The v1 "Proposed span
  name" column is renamed to **Normalized cert alias** and demoted
  from "what the emitter must emit" to "what the cert harness
  internally binds to".
- **§5 build_time_compiler** — reflects Phase A's
  `UNKNOWN_NEEDS_RUNTIME_RUN` status for apps_qna's `build.pack_artifact`
  emission, keeps the forbidden-R3-assertion guardrail.
- **§6.3 CC-SHARED-05** — updates status to `NOT_FOUND` (per Phase A)
  and enumerates the three acceptable evidence mechanisms.
- **§7 Span naming** — inverts the v1 framing. v1 said: "emitters
  must emit `app.<app_name>.<layer>.<contract_surface>`". v2 says:
  "the cert harness binds to existing emitter categories and OTel
  GenAI semconv spans; canonical names are **normalized cert aliases**
  internal to the harness, not required span names at the emitter."
- **§11 Phase B** split into **B.1 … B.6** matching the Phase A
  recommendation.
- **§12 Q1** marked **resolved by Phase A**.
- **Provenance** — bumped to v2, references Phase A report.

What v2 deliberately does NOT change:

- **§8 required trace attributes** — unchanged. The attribute contract
  is orthogonal to span naming and remains the hard cert requirement.
- **§9 fail-closed gate logic** — unchanged (still fail-closed on
  missing spans, missing attributes, and the R3-vs-R3R4 discriminator).
- **§10 negative controls** — unchanged conceptually; the specific
  "missing L1 span" text is retained because the gate works on
  normalized cert aliases, not emitter names.
- **§13 final statement** — unchanged; no app is certified.

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
  remove, or rename any OTel span. §7 v2 explicitly binds the cert
  harness to **existing** emitter categories (Tier-1 signal matching,
  GenAI semconv, L2 canonical registry, etc.). Proposed canonical
  names are **normalized cert aliases**, internal to the harness; they
  are NOT required span names at the emitter.

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

### 4.1 Span contract table (v2 — Phase A reconciled)

Legend for Phase A status column:
`EXISTS_MATCHES_MATRIX` (EM),
`EXISTS_NEEDS_ATTRIBUTE_HARDENING` (EAH),
`EXISTS_NAME_MISMATCH` (ENM — but cert harness binds via signal, so
no emitter change required),
`UNKNOWN_NEEDS_RUNTIME_RUN` (UNR),
`NOT_FOUND` (NF).

| # | Contract | **Phase A status** | **Existing emitter / Tier-1 category** | **Normalized cert alias** *(harness-internal; not an emitter rename)* | **Attribute hardening needed** | **Live trace required?** | Required attributes | Parent expectation | Failure condition |
|:---:|---|:---:|---|---|---|:---:|---|---|---|
| 1 | `ValidatedRequest` | **ENM** | `agentic_core/L5_safety/enforcement/ingress_telemetry_otel.py` (ingress span) | `app.<app_name>.intake.validated_request` | Add `contract_name`, `contract_id`, `manifest_hash`, `app_name`, `route_shape`, `run_id` attributes. | No (emitter confirmed by Phase A) | standard set + `contract_id` (request_id) | Root; no parent | Span missing from matching category, `contract_name` mismatched, or `contract_id` empty |
| 2 | `L1PlanContract` | **EAH** | `agentic_core/L1_cognition/planning/otel.py` + `L1_cognition/c0_context/observability.py` | `app.<app_name>.l1.plan_contract` | Add `contract_name=L1PlanContract`, `contract_id=plan_id`, `parent_contract_id`, `sub_query_count`. | No | standard + `plan_id` | Parent: span #1 | Missing, or `parent_contract_id` ≠ request_id |
| 3 | `RouteContract` | **EM** (via Tier-1 signal) | Tier-1 `L0.route.select` category in `system_learning/runtime_adg/span_contracts.py` — matches `heal_router.v1.route`, `router.`, `route.select`, `l0.route`, `route.contract`, `.v1.route` via multi-signal scoring (name + kind + layer + attrs). Emitter: `agentic_core/L6_observability/heal_router_otel.py` et al. | `app.<app_name>.l0.route_contract` | Add `contract_name=RouteContract`, `contract_id=route_id`, `parent_contract_id`. (Attributes `selected_route`, `routing.target_model`, `routing.confidence_score`, `routing.tier`, `cache_decision` already present.) | No | standard + `route_id` + `route_target` + `l0_confidence` (present as `routing.*`) | Parent: span #2 | Missing, or route_target not in manifest's declared routing targets |
| 4 | `RetrievalPlan` | **EAH** | `agentic_core/L0_routing/c0_retrieval/c0_3_enhanced/otel.py` (partial coverage) | `app.<app_name>.c0.retrieval_plan` | Add `contract_name=RetrievalPlan`, `contract_id=retrieval_plan_id`, `collection`, `k`. Attribute audit across all 5 R3 apps needed — attributes may not be emitted uniformly. | Partial (attribute audit benefits from live trace) | standard + `retrieval_plan_id` + `collection` + `k` | Parent: span #3 | Missing, or `k ≤ 0` |
| 5 | `FinalEvidenceContract` | **UNR** | Likely in C0 retrieval layer; no cleanly-labeled span in Phase A inventory | `app.<app_name>.c0.final_evidence_contract` | Unknown until live trace. If emitter exists: add `contract_name`, `contract_id`, `evidence_hash`, `citation_count`, `support_coverage`. If not: extend an existing C0 span with these attrs (NO new emitter). | **Yes** (blocking — Phase C needs a live trace to resolve) | standard + `evidence_id` + `evidence_hash` | Parent: span #4 | Missing, or `evidence_hash` empty |
| 6 | `CompiledPromptArtifact` **or** `PromptEnvelope` | **EAH** | `agentic_core/L2_execution/observability/l2_otel_emitter.py` canonical L2 registry + `agentic_core/L6_observability/semconv/gen_ai.py` (OTel GenAI semconv `invoke_agent` / `execute_tool`) | `app.<app_name>.pa.compiled_prompt_artifact` | Standardize `contract_name ∈ {CompiledPromptArtifact, PromptEnvelope}`, `contract_id=prompt_artifact_id`, `abstain_recommended`. The equivalence group resolution uses `CONTRACT_EQUIVALENT_GROUPS` already defined in the scanner — no new concept. | No | standard + `prompt_artifact_id` | Parent: span #5 | Missing; contract_name not in equivalence group |
| 7 | `SealedArtifact` | **EM** (via Tier-1 signal) | Tier-1 `L2.step.seal` category in `system_learning/runtime_adg/span_contracts.py` — matches `l2.step.seal`, `step.seal`, `execution.seal`, `.seal` via multi-signal scoring. Emitter: the canonical L2 registry + L2 resolution spans. | `app.<app_name>.l2.sealed_artifact` | Add `contract_name=SealedArtifact`, `contract_id=sealed_artifact_id`, `artifact_hash`, `grounded`, `gate_disposition`. | No | standard + `sealed_artifact_id` + `artifact_hash` + `grounded` + `gate_disposition` | Parent: span #6 | Missing, or `artifact_hash` empty, or `grounded=False` with `gate_disposition=allow` |
| 8 | `ExitReviewPacket` | **EM** | `agentic_core/L3_orchestration/exit_eval/otel_sdk_sink.py` + `v6/otel.py` + `v6/return_payload.py` + Tier-1 `Exit.disposition` category | `app.<app_name>.exit.review_packet` | Add `contract_name=ExitReviewPacket`, `contract_id=exit_packet_id`, `exit_disposition`, `l6_ingested`. | No | standard + `exit_packet_id` + `exit_disposition` | Parent: span #7 | Missing; or emitted **without** span #7 (§10 negative control) |

**How to read this table**: the cert harness does NOT require the
"Normalized cert alias" as an emitted span name. It binds the
harness-internal alias to the "Existing emitter / Tier-1 category"
via signal matching (the same multi-signal approach already used by
`system_learning/runtime_adg/span_contracts.py`). The attribute
contract in §8 is enforced on whichever emitter matched.

**Phase A summary**: 5 of 8 contracts are `EM` or `EM (via signal)`.
2 of 8 are `EAH`. 1 of 8 (`FinalEvidenceContract`) is `UNR` and blocks
on Phase C evidence. **Zero contracts require new emitter creation.**

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

> **v2 clarification**: The `name` fields in this JSON are the
> **normalized cert aliases** (harness-internal), not the literal
> emitted span names. The cert collector translates from emitted name
> to normalized alias via the binding rules in §4.1 column 4.
> Actually-emitted names today for apps_rfp are captured in Phase A
> report §3 and include `heal_router.v1.route` (for
> `l0.route_contract`), signal-matched `l2.step.seal` variants, and
> `agentic_core/L3_orchestration/exit_eval/v6/otel.py`-produced exit
> spans.

---

## 5. `build_time_compiler` matrix (apps_qna)

apps_qna's runtime shape is materially different from R3 apps. It
compiles a paste-pack at build time, validates the intake envelope,
and emits a ledger event. It does **NOT** run the L1 → L0 → C0 → PA →
L2 → Exit chain — making it share the R3 matrix would be contract
theater.

### 5.1 Required spans (v2 — Phase A reconciled)

| # | Role | **Phase A status** | **Existing emitter** | **Normalized cert alias** | **Attribute hardening needed** | Required attributes | Required contract ID |
|:---:|---|:---:|---|---|---|---|---|
| 1 | Intake envelope | **ENM** (same emitter as R3 intake) | `agentic_core/L5_safety/enforcement/ingress_telemetry_otel.py` (shared ingress telemetry) | `app.apps_qna.intake.validated_request` | Add `app_name=apps_qna`, `route_shape=build_time_compiler`, `contract_name=ValidatedRequest`, `contract_id`, `manifest_hash`. | standard set + `contract_id=request_id` | `request_id` |
| 2 | Build-artifact identity | **UNR** (apps_qna-specific; not confirmed in Phase A) | TBD — requires apps_qna-specific inspection OR live trace | `app.apps_qna.build.pack_artifact` | Unknown until Phase A.1 apps_qna walk. Required payload: `build_artifact_id`, `source_pack_id`, `output_pack_hash`, `parent_contract_id`. | standard + `build_artifact_id`, `source_pack_id`, `output_pack_hash` | `build_artifact_id` |
| 3 | Ledger emission (governance signal) | **TELEMETRY_MARKER_ONLY → likely promotable** | Constitutional §29 requires all routers emit `ROUTER_DECISION:` ledger events; apps_qna router-side ledger events exist. Promotion to a real OTel span is additive. | `app.apps_qna.ledger.emit` | Add `ledger_name=apps_qna_build`, `ledger_event_id`, `parent_contract_id`, terminal-event enum. | standard + `ledger_name` + `ledger_event_id` + terminal-event enum | `ledger_event_id` |

**v2 note**: apps_qna was **not exhaustively audited** in Phase A.
The `build.pack_artifact` emitter existence is an open Phase B
item — see §12 Q11.

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
| **CC-SHARED-05** | **Phase A status: `NOT_FOUND` — no trace-level evidence exists today that the shim early-returned vs installed 12 fallbacks.** Handled as a negative-evidence check with three acceptable mechanisms, any one of which satisfies the gate: **(a)** an additive boot-time telemetry event in `apps_shared/_compat/agentic_core_shim.py::install()` — a single `logging.info()` line recording which branch executed (`shim.early_return_full_stack` vs `shim.installed_12_fallbacks`); **(b)** an environment-variable assertion at cert-harness startup (`AGENTIC_CORE_STACK=full`) *plus* a post-run `sys.modules` inspection confirming absence of the 12 shimmed entries — redundant evidence for a safety-critical control; **(c)** the three-evidence packaging / CI / deployment audit already specified in the post-W14 scorecard addendum proving standalone mode is unsupported and unused in this deployment. Certification MUST be denied if the cert harness cannot distinguish full-stack from standalone. **Phase B.4** (see §11) is the design task that decides which mechanism ships. |

**Core principle**: FORMAL_EXCEPTION_VERIFIED for apps_shared certifies
the *absence* of risk-bearing execution in the shimmed branch, not
the *presence* of a contract chain. This is a structurally different
harness from the R3 apps' positive contract-chain verification.

---

## 7. Span binding convention (v2 — existing emitters are primary)

Phase A resolved the v1 open question "do current emitters match the
proposed naming pattern?" with a clear **no** — and also with a clear
**this is fine**, because the repo already uses multi-signal
category-based binding in
`system_learning/runtime_adg/span_contracts.py`. v2 therefore
reframes §7 around that reality.

### 7.1 Primary concept: cert harness binds to existing categories

The cert harness does NOT require emitters to emit a particular
span name. It binds via the following precedence:

| Priority | Source of truth | Example |
|:---:|---|---|
| **1** | Tier-1 signal category (`system_learning/runtime_adg/span_contracts.py`) — multi-signal match on name + kind + layer + attributes. | `L0.route.select` matches `heal_router.v1.route` and `route.select` |
| **2** | OTel GenAI semconv (`agentic_core/L6_observability/semconv/gen_ai.py`) — `invoke_agent <name>`, `execute_tool <name>` with registered attributes. | L2 model / tool invocation spans |
| **3** | Canonical L2 registry (`agentic_core/L2_execution/observability/l2_otel_emitter.py`) — strict span-name + required-attribute validation. | L2 emitters already raise `L2SpanAttributeViolation` on drift |
| **4** | Existing named emitters (ingress, L1 plan, C0 retrieval, exit_eval v6, UWG). | `ingress_telemetry_otel`, `planning/otel.py`, `v6/otel.py` |

### 7.2 Binding table — per contract (v2)

| Contract | Existing Tier-1 signal / emitter | Accepted span-name patterns (observed or signal-matched) | Required attributes (added by cert harness) | Normalized cert alias *(harness-internal)* |
|---|---|---|---|---|
| `ValidatedRequest` | `ingress_telemetry_otel.py` ingress span | `ingress.*`, `intake.*`, `*.stamp_trace` | `contract_name`, `contract_id=request_id`, `app_name`, `route_shape`, `run_id`, `manifest_hash` | `app.<app_name>.intake.validated_request` |
| `L1PlanContract` | `L1_cognition/planning/otel.py` + `c0_context/observability.py` | `l1.plan.*`, `planning.*`, `c0_context.*` | + `contract_name=L1PlanContract`, `contract_id=plan_id`, `parent_contract_id`, `sub_query_count` | `app.<app_name>.l1.plan_contract` |
| `RouteContract` | Tier-1 `L0.route.select` (multi-signal) | `heal_router.v1.route`, `router.*`, `route.select`, `l0.route`, `route.contract`, `*.v1.route` — any match on 2+ of 4 signals | + `contract_name=RouteContract`, `contract_id=route_id`, `parent_contract_id`, `route_target`, `l0_confidence` (OR existing `routing.confidence_score`) | `app.<app_name>.l0.route_contract` |
| `RetrievalPlan` | `L0_routing/c0_retrieval/c0_3_enhanced/otel.py` | `c0.retrieval.*`, `c0_3.*`, `retrieval.plan` | + `contract_name=RetrievalPlan`, `contract_id=retrieval_plan_id`, `collection`, `k` | `app.<app_name>.c0.retrieval_plan` |
| `FinalEvidenceContract` | **Unresolved — requires live trace (Phase C)** | TBD | + `contract_name=FinalEvidenceContract`, `contract_id=evidence_id`, `evidence_hash`, `citation_count`, `support_coverage` | `app.<app_name>.c0.final_evidence_contract` |
| `CompiledPromptArtifact` / `PromptEnvelope` | GenAI semconv `invoke_agent <name>` + L2 canonical registry | `invoke_agent *`, `prompt.compile.*`, `l2.prompt.*` | + `contract_name ∈ {CompiledPromptArtifact, PromptEnvelope}`, `contract_id=prompt_artifact_id`, `abstain_recommended` | `app.<app_name>.pa.compiled_prompt_artifact` |
| `SealedArtifact` | Tier-1 `L2.step.seal` (multi-signal) | `l2.step.seal`, `step.seal`, `execution.seal`, `*.seal` | + `contract_name=SealedArtifact`, `contract_id=sealed_artifact_id`, `artifact_hash`, `grounded`, `gate_disposition` | `app.<app_name>.l2.sealed_artifact` |
| `ExitReviewPacket` | `L3_orchestration/exit_eval/otel_sdk_sink.py` + `v6/otel.py` + `v6/return_payload.py` + Tier-1 `Exit.disposition` | `exit.*`, `exit_eval.*`, `disposition.*` | + `contract_name=ExitReviewPacket`, `contract_id=exit_packet_id`, `exit_disposition`, `l6_ingested` | `app.<app_name>.exit.review_packet` |
| `build.pack_artifact` (apps_qna) | **Unresolved — requires apps_qna walk or live trace** | TBD | + `build_artifact_id`, `source_pack_id`, `output_pack_hash`, `parent_contract_id` | `app.apps_qna.build.pack_artifact` |

### 7.3 Implementation implications

- **The cert harness MUST bind via existing emitter categories first.**
  Renaming existing spans is not required and will not be scheduled
  from this document.
- **Normalized cert aliases are harness-internal.** They appear in
  cert reports (`docs/reports/runtime_cert/<app>/<YYYY-Www>.md`) and
  in the evidence record shape (§4.2 `name` field), but they are NOT
  required as the literal span name at the emitter.
- **Attributes are real.** Attribute hardening on existing emitters
  IS required for certification. Phase B.2 defines the per-app-route
  attribute contract; Phase B.2 is the first phase where any code
  (a pydantic schema) is written.
- **If a future controlled-rename program ever renames emitters** to
  match the normalized cert aliases, that is a separate operation
  covered by its own plan + Author-Gate decision. Nothing about v2
  blocks or requires such a program.

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

## 11. Implementation plan (v2 — Phase B split per Phase A recommendation)

**Phase A is COMPLETE**: see
`docs/reports/runtime_certification/phase_a_trace_inventory.md`.

**Phase B is NOW SPLIT** into 6 sub-phases (B.1…B.6). Each sub-phase
is a distinct change-set requiring its own Author-Gate approval, plan
file (`.windsurf/plans/<slug>-<6hex>.md`), and wave structure.
**No code is written in the present document.**

| Phase | Name | Status | Output | Blocked by |
|:---:|---|:---:|---|---|
| **A** | Trace inventory | ✅ **DONE** (2026-04-30) | `docs/reports/runtime_certification/phase_a_trace_inventory.md` | — |
| **B.1** | **Doc reconciliation** | ✅ **DONE** (this v2) | This v2 revision of the binding matrix — §0 delta + §4/§5/§6.3/§7/§11/§12 updates | Phase A |
| **B.2** | Tier-2 per-app-route contract schema | ✅ **DONE** (2026-04-30) | `system_learning/runtime_adg/app_route_contracts.py` defines `CertificationLevel`, `PhaseAStatus`, `RouteShape`, `RequiredAttribute`, `ContractSpanBinding`, `AppRouteContract` + factories (`build_r3_grounded_read_contract`, `build_build_time_compiler_contract`, `build_formal_exception_contract`). Tests: `tests/unit/system_learning/runtime_adg/test_app_route_contracts.py` (26 passing). Style: frozen dataclasses matching the repo's existing `_CategoryContract` convention (not pydantic). | Phase B.1 |
| **B.3** | `manifest_hash` convention | ✅ **DONE** (2026-04-30) | `system_learning/runtime_adg/manifest_hash.py` defines `compute_manifest_hash`, `compute_manifest_hash_for_app`, `MANIFEST_HASH_ALGORITHM = "sha256-raw-bytes"`. Tests: `tests/unit/system_learning/runtime_adg/test_manifest_hash.py` (22 passing). Resolves §12 Q6: raw-bytes SHA-256 \u2014 no YAML parse, no line-ending normalization, no comment stripping, no canonicalization. Any manifest change (including comments) invalidates cached cert evidence, which is the intended behavior because comment prose (e.g. CC-SHARED-05) carries compensating-control semantics. | Phase B.2 |
| **B.4** | CC-SHARED-05 evidence mechanism | ✅ **DONE** (2026-04-30) | **Option (b) implemented**: `system_learning/runtime_adg/formal_exception_evidence.py` defines `SharedShimEvidence` (frozen dataclass) + `collect_cc_shared_05_evidence()` + `assert_cc_shared_05_passes()` + constants (`CC_SHARED_05_CONTROL_ID`, `FULL_STACK_ENV_VAR=AGENTIC_CORE_STACK`, `FULL_STACK_ENV_VALUE="full"`, `SHIMMED_MODULE_NAMES` tuple of 13). Uses env-var assertion + `sys.modules` inspection with strong identity checks against the shim's `_LifecycleModule` and `ConfCalibRiskGate` classes plus a structural `__file__`/`__path__` heuristic for plain fallback modules. `risk_bearing_allowed` is a hard invariant (always False). `apps_shared/_compat/agentic_core_shim.py` was **NOT edited**. Tests: `tests/unit/system_learning/runtime_adg/test_formal_exception_evidence.py` (19 passing). Options (a) and (c) remain available future paths \u2014 not required for Phase B.4 completion. | Phase B.2 |
| **B.5** | Formal-exception negative-control query helpers | \u2705 **DONE** (2026-04-30) | `tools/runtime_cert/negative_controls.py` defines `NegativeControlResult` (frozen dataclass) + four checks: `check_no_eval_of_evaluator_circularity` (CC-EVAL-01), `check_apps_eval_no_r3_contract_leak` (CC-EVAL-02), `check_underwriting_no_r3_contract_leak` (CC-UW-02), `check_apps_shared_sealed_artifact_proof_only` (CC-SHARED-03). Constants: `R3_CONTRACT_SET` (9 contracts including the `CompiledPromptArtifact`/`PromptEnvelope` equivalence group). Helpers operate on `Iterable[Mapping[str, Any]]` rows via dependency injection \u2014 no live runtime-ADG database required in tests. Defensive field access: tolerates missing `app_name`, `contract_name`, `source_path`; reads from top level OR nested `attributes` dict. Tests: `tests/unit/tools/runtime_cert/test_negative_controls.py` (28 passing). These helpers produce structured evidence records; they do NOT certify any app \u2014 future cert harnesses (Phase D) will wire them to real runtime-ADG query output. | Phase B.2 |
| **B.6** | Phase B invariants | Standing | **No scanner changes, no CI changes, no app migration during Phase B.** Cert harness design must stabilize before Phase C. | — |
| **C.1** | Read-only runtime-ADG query adapter | ✅ **DONE** (2026-04-30) | `tools/runtime_cert/runtime_adg_query_adapter.py` defines `PhaseC1Row` (18-field frozen dataclass) + `iter_rows_from_snapshot`. `runtime_certification_status` forced to `NOT_CERTIFIED`. Tests: `tests/unit/tools/runtime_cert/test_runtime_adg_query_adapter.py` (38 passing). No emitter/scanner changes. | Phase B.2–B.5 |
| **C.2** | Pure trace-row normalizer | ✅ **DONE** (2026-04-30) | `tools/runtime_cert/trace_row_normalizer.py` defines `NormalizedTraceRow` + `normalize_trace_row` / `normalize_trace_rows`. Five-priority matching (P1 Tier-1 multi-signal, P2 GenAI semconv, P3 span-name patterns glob-aware, P4 emitter files, P5 direct attr). `runtime_certification_status` forced to `NOT_CERTIFIED`. Tests: `tests/unit/tools/runtime_cert/test_trace_row_normalizer.py` (29 passing). No emitter/scanner changes. | Phase C.1 |
| **C.3** | R3 per-app evidence extractor | ✅ **DONE** (2026-04-30) | `tools/runtime_cert/extractors/r3_evidence.py` defines `R3ContractEvidence` + `R3EvidenceReport` + `extract_r3_evidence`. Groups `NormalizedTraceRow` rows by the 8 required R3 contracts, honours `PromptEnvelope`↔`CompiledPromptArtifact` equivalence, flags `CommitRequest` on R3 apps as `FORBIDDEN_SPAN_VIOLATION`, emits `passed_trace_observed=True` only when all 8 contracts observed + no gaps. **This extractor reports trace-observed readiness only and does not certify apps.** `runtime_certification_status` remains `NOT_CERTIFIED` throughout. Tests: `tests/unit/tools/runtime_cert/extractors/test_r3_evidence.py` (23 passing). No emitter/scanner changes. | Phase C.2 |
| **C.4** | `build_time_compiler` evidence extractor | ✅ **DONE** (2026-04-30) | `tools/runtime_cert/extractors/btc_evidence.py` defines `BTCContractEvidence` + `BTCEvidenceReport` + `extract_btc_evidence`. Groups `NormalizedTraceRow` rows by the 3 required BTC contracts (`ValidatedRequest`, `build.pack_artifact`, `ledger.emit`). Flags all R3-chain contracts + `CommitRequest` as `FORBIDDEN_SPAN_VIOLATION` on BTC apps (carve-out: `ValidatedRequest` is required, not forbidden). Honours `PromptEnvelope`↔`CompiledPromptArtifact` equivalence for forbidden detection. Emits `passed_trace_observed=True` only when all 3 contracts observed + no forbidden/hardening/unknown gaps. **This extractor reports trace-observed readiness only and does not certify apps.** `runtime_certification_status` remains `NOT_CERTIFIED` throughout. Tests: `tests/unit/tools/runtime_cert/extractors/test_btc_evidence.py` (33 passing). No emitter/scanner changes. | Phase C.3 |
| **C.5** | Formal-exception evidence extractor | ✅ **DONE** (2026-04-30) | `tools/runtime_cert/extractors/formal_exception_evidence.py` defines `FormalControlEvidence` + `FormalExceptionEvidenceReport` + `extract_formal_exception_evidence`. Wraps B.4 (`collect_cc_shared_05_evidence`) and B.5 (`check_no_eval_of_evaluator_circularity`, `check_apps_eval_no_r3_contract_leak`, `check_underwriting_no_r3_contract_leak`, `check_apps_shared_sealed_artifact_proof_only`) helpers into the common evidence-report shape used by C.3/C.4. Dispatches by `app_name`: `apps_eval` → CC-EVAL-01 + CC-EVAL-02; `apps_underwriting_ai` → CC-UW-02 (CC-UW-01 honestly reported missing — no positive regulated-decision helper in Phase C.5); `apps_shared` → CC-SHARED-03 + CC-SHARED-05 (CC-SHARED-01/02/04 honestly reported missing — static compensating controls not runtime-verifiable in Phase C.5). **This extractor reports formal-exception observed readiness only and does not certify apps.** No fake-pass: `FormalControlEvidence` `__post_init__` rejects `observed=False ∧ passed=True`. `runtime_certification_status` remains `NOT_CERTIFIED` throughout — never promoted to `FORMAL_EXCEPTION_VERIFIED`. Tests: `tests/unit/tools/runtime_cert/extractors/test_formal_exception_evidence.py` (31 passing). No emitter/scanner changes. | Phase C.4 |
| **C.6** | Non-promoting live-trace smoke for `apps_research` | ✅ **DONE** (2026-04-30) | `tools/runtime_cert/smoke/live_trace_smoke.py` defines `LiveTraceSmokeReport` (frozen dataclass; `__post_init__` enforces `NOT_CERTIFIED`) + `run_apps_research_live_trace_smoke(snapshot_path, *, repo_root=None)` + `write_live_trace_smoke_report(report, output_path)`. First end-to-end wiring of the C.1→C.2→C.3 pipeline on a real runtime-ADG snapshot JSON, scoped strictly to `apps_research` per the Phase C.6 Author-Gate. Asserts `AGENTIC_CORE_STACK=full` at entry (CC-SHARED-05 full-stack assertion; `RuntimeError` otherwise). Computes manifest hash via `compute_manifest_hash_for_app`; builds the canonical R3 contract via `build_r3_grounded_read_contract`. Filters C.1 rows to `app_name == "apps_research"` (other-app rows are counted in `notes` only). Normalizes via C.2; evaluates via C.3. Report writer emits JSON with top-level `disclaimer: "no runtime certification performed — this is Phase C.6 non-promoting evidence only"` and always-present `runtime_certification_status: "NOT_CERTIFIED"`. **Honest finding documented by the smoke**: `FinalEvidenceContract` binding ships with `phase_a_status=UNKNOWN_NEEDS_RUNTIME_RUN`, which deterministically forces `passed_trace_observed=False` even for a clean 8-row snapshot — exactly the kind of real-world readiness signal the non-promoting smoke exists to surface (Phase C.7 attribute-hardening gap report will target this). Tests: `tests/unit/tools/runtime_cert/smoke/test_live_trace_smoke.py` (25 passing). No emitter/scanner/CI changes. | Phase C.5 |
| **C.7** | Attribute-hardening gap report | ✅ **DONE** (2026-04-30) | `tools/runtime_cert/reports/attribute_hardening_gap.py` defines `AttributeGap` + `AttributeHardeningGapReport` (both frozen; `__post_init__` enforces `NOT_CERTIFIED`, non-negative row counts, valid gap-type + severity enums, and `gap_count == len(gaps)`) + `build_attribute_hardening_gap_report(rows, contract, *, observed_contracts=None)`. Emits 9 canonical gap types (`MISSING_CONTRACT`, `MISSING_REQUIRED_ATTRIBUTE`, `UNKNOWN_NEEDS_RUNTIME_RUN`, `FORBIDDEN_SPAN_VIOLATION`, `TRACE_GAP`, `NAME_MISMATCH`, `TELEMETRY_MARKER_ONLY`, `LEDGER_EVENT_ONLY`, `STUB_ONLY`) with deterministic 5-band severity (`CRITICAL`/`HIGH`/`MEDIUM`/`LOW`/`INFO`) per task spec §6. Groups rows by canonicalized contract name (honors `CompiledPromptArtifact` ↔ `PromptEnvelope` equivalence — matches C.3/C.4 behavior). Filters rows to `contract.app_name`; other-app rows are counted in `notes` only. Preserves `CommitRequest`/`FORBIDDEN_SPAN_VIOLATION` rows as CRITICAL. Compares observed contracts (derived from rows with non-empty `contract_name` OR provided explicitly via `observed_contracts`) against `contract.required_contracts` and emits one CRITICAL `MISSING_CONTRACT` gap per absent required contract. Generates deterministic per-gap-type recommendation text (task spec §8) and aggregates into a ranked ordered gap list (severity DESC, gap_type ASC, contract_name ASC). Derived projections: `blocked_contracts` (CRITICAL+HIGH), `attribute_hardening_required`, `unknown_needs_runtime_run`, `forbidden_violations`, `missing_contracts`, deduplicated `recommendations`. **This report is operational/actionable backlog ONLY and does NOT certify apps.** `runtime_certification_status` remains `NOT_CERTIFIED` throughout — never promoted to any certification verdict. Tests: `tests/unit/tools/runtime_cert/reports/test_attribute_hardening_gap.py` (32 passing). No emitter/scanner/CI changes. | Phase C.6 |
| **C.8–C.n** | Phase C closeout | Pending | Phase C closeout report (aggregates smoke + gap reports across all certifying apps); Phase D planning. | Phase C.7+ |
| **D** | Certification report generator | Pending | Offline tool running the fail-closed gate (§9) against a sample of traces; produces `docs/reports/runtime_cert/<app>/<YYYY-Www>.md`. | Phase C |
| **E** | Fail-closed CI gate | Pending | `ops_scripts/ci/check_runtime_certification.py` (SSOT-folder-compliant name) running Phase D on the last-N-days of traces for any app claiming `TRACE_OBSERVED` or higher. Complements the existing `ops_scripts/ci/check_runtime_adg_coverage.py`. | Phase D |
| **F** | Promotion process to `RUNTIME_CERTIFIED` | Pending | Scanner extension recognizing new `runtime_mode` buckets (`RUNTIME_CERTIFIED`, `FORMAL_EXCEPTION_VERIFIED`) and a promotion workflow updating scorecard + Notion ADR + memory. | Phase E |

Constitutional note (unchanged from v1): phases D, E, and F introduce
new intelligence ledgers per §29 — every cert-report emission and
every gate decision must emit a `CERT_DECISION:` event bound to a
per-app ledger. Ledger family out of scope for this design doc.

---

## 12. Open questions

These questions MUST be resolved before Phase A produces a deliverable
(much less Phase D certifying an app):

| # | Question | Default stance (pending evidence) |
|:---:|---|---|
| **Q1** | Do current emitters produce spans whose names match §7? If not, under what names? | ✅ **RESOLVED BY PHASE A**. Answer: no, the proposed `app.<app_name>.<layer>.<contract>` pattern does not match existing emitters. Instead, emitters use domain-specific names (e.g., `heal_router.v1.route`) with multi-signal Tier-1 matching. v2 §7 reframes the cert harness to bind via existing categories; emitter renaming is NOT scheduled. |
| **Q2** | Can the runtime ADG serve as the evidence store for Phases C–E, or does it need a dedicated store? | Default: reuse runtime ADG for Phase C ingest; reconsider for Phase D report cache only if query latency is unacceptable. |
| **Q3** | What is `N_R3` (sample-size threshold for sustained coverage for R3 apps)? | No accepted value. Suggestions: statistical minimum at 95% CI width ≤ 5% → probably ≥ 100 traces. Needs simulation; defer to Phase D design. |
| **Q4** | What is `N_BTC` for apps_qna (`build_time_compiler`)? | Probably smaller than N_R3 because the compile surface is narrower; suggest ≥ 30. Needs Phase D design. |
| **Q5** | Do formal-exception apps need separate cert harnesses, or can one harness with per-shape switches handle all 3? | Default: **separate harnesses** — the positive-chain shape for apps_eval's CC-EVAL-03 and apps_underwriting_ai's CC-UW-01 differs from apps_shared's negative-evidence shape enough that a unified harness would over-couple. Revisit after Phase B. |
| **Q6** | How is `manifest_hash` computed — whole-file SHA-256 of raw bytes, or YAML-canonicalized? | \u2705 **RESOLVED BY PHASE B.3**. Answer: `sha256-raw-bytes` \u2014 lowercase hex SHA-256 of the raw file bytes with no YAML parse, no line-ending normalization, no comment stripping, no canonicalization. Reified in `system_learning/runtime_adg/manifest_hash.py` with `MANIFEST_HASH_ALGORITHM = "sha256-raw-bytes"`. Rationale: comment prose (e.g. CC-SHARED-05) carries compensating-control semantics, so any byte change \u2014 including comments \u2014 must invalidate cached cert evidence. |
| **Q7** | Do R3 apps' `CompiledPromptArtifact` vs `PromptEnvelope` equivalence (apps_rg today) need tracking in the trace, or is either name acceptable? | Default: either name acceptable; cert harness consults the app's declared equivalence group (from `CONTRACT_EQUIVALENT_GROUPS` in the scanner). |
| **Q8** | What is the sunset condition for `STATIC_EVIDENCE` — can an app stay there forever, or must it promote within a time bound? | Default: no time bound. `STATIC_EVIDENCE` is a permanent classification until the app opts into cert work. |
| **Q9** | If an app is `RUNTIME_CERTIFIED` and a regression causes one required span to drop out, what is the demotion path? Immediate demotion to `STATIC_EVIDENCE`, or an intermediate `CERT_DEGRADED` bucket? | Default: immediate demotion to `STATIC_EVIDENCE` with a `cert_loss_reason` attribute. Intermediate bucket adds complexity for marginal benefit. |
| **Q10** | How is apps_shared's CC-SHARED-05 full-stack vs standalone distinction asserted at the trace level — boot-time telemetry event, env-var assertion, or both? | Default: require **both** — env-var assertion at harness startup AND the absence of the 12 shimmed `sys.modules` entries at run end. Redundant evidence for a safety-critical control. Reified as Phase B.4. |
| **Q11** | Does apps_qna actually emit `build.pack_artifact` and `ledger.emit` spans today, or only ledger events? | **Open (net new in v2).** Phase A did not inspect apps_qna-specific files. Phase B can resolve via a 1-hour apps_qna walk OR by live-trace inspection during Phase C. Default stance: assume not until confirmed; keep the §5.2 forbidden-R3-assertion guardrail. |

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
| Doc version | **v2 (Phase-B.1 reconciliation)** |
| v1 generated | 2026-04-30 |
| v2 reconciled | 2026-04-30 (same day; Phase A completed between v1 and v2) |
| Parent SSOT | `tools/analysis/apps_spine_coverage.py`, `docs/reference/APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md` |
| Phase A input | `docs/reports/runtime_certification/phase_a_trace_inventory.md` |
| Related | `docs/reports/apps_static_scorecard_post_w14.md` |
| Drafted in response to | Post-W14 scorecard §"Runtime certification remains future work" (7 prerequisites) |
| Implementation status | **none** — v2 is doc-only. No Python changed, no emitter renamed, no scanner modified, no CI gate added, no test added. |
| Apps affected by this document | **zero** (no runtime behavior change; all 9 apps remain `NOT_CERTIFIED`) |
| Phase A → B.1 delta | 5 sections updated (§0 added, §4/§5/§6.3/§7/§11/§12/Provenance), zero sections removed |
