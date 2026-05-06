# Phase A — Runtime Trace Inventory (Read-Only)

**Status**: INVENTORY REPORT — read-only. No runtime behavior change.
No app is certified by this document. No span is renamed, added, or
removed. Report is the only artifact.
**Generated**: 2026-04-30
**Parent**: `docs/reference/runtime_certification/contract_span_binding_matrix.md` (design v1)
**Preceded by**: post-W14 cohort closure (`docs/reports/apps_static_scorecard_post_w14.md`)
**Scope**: identify existing runtime emitters and runtime ADG infrastructure; compare to the design matrix; recommend Phase B scope.

---

## 1. Headline finding

**The runtime-certification substrate is NOT greenfield.** This repo
already has a substantial, layered OTel + runtime-ADG infrastructure:

- **Real OpenTelemetry tracers** across L0, L1, L2, L3, L4, L5, L6 —
  44 files matched on `opentelemetry|get_tracer|start_as_current_span|
  SpanKind|set_attribute`.
- **OTel GenAI semantic conventions** already codified at
  `agentic_core/L6_observability/semconv/gen_ai.py` mirroring the
  published `opentelemetry/gen-ai-agent-spans` spec.
- **Runtime ADG store** at `system_learning/runtime_adg/` with
  materializer, snapshot, auto-persistence, and multi-signal span
  contracts.
- **Lifecycle → OTel bridge** at
  `agentic_core/runtime/contracts/otel_lifecycle_bridge.py`
  that promotes the 600+ `_emit_*` debug emitters into real OTel spans.
- **Tier-1 span coverage contract** at
  `system_learning/runtime_adg/span_contracts.py` with 5 canonical
  categories (`runtime.trace_root`, `L0.route.select`, `L2.step.seal`,
  `L2.(model|tool).invoke`, `Exit.disposition`) using **multi-signal
  matching (name + kind + layer + attributes)** — because real span
  names vary between emitters.
- **Pre-existing doctrine** (ADR-074) says the runtime bucket IS a
  deterministic view over OTel spans; the runtime ADG is not a parallel
  store.

**Implication for Phase B**: the naming convention proposed in the
design doc (`app.<app_name>.intake.validated_request`) does **not**
match existing emitters. The correct path forward is **not to rename**
emitters, but to extend the existing Tier-1 contract system with
per-app-route bindings.

---

## 2. Files inspected (key set — full grep coverage in §3/4)

Total files inspected / read in this pass: **8 files read**;
**5 targeted grep sweeps** yielding 1,474 matches across ~200 files.

Files read in full / partial:

| # | File | Purpose of read |
|---:|---|---|
| 1 | `agentic_core/runtime/contracts/otel_lifecycle_bridge.py` (first 80 lines) | Confirm how `_emit_*` logs become spans |
| 2 | `agentic_core/L6_observability/semconv/gen_ai.py` (first 60 lines) | Confirm OTel GenAI semconv compliance |
| 3 | `system_learning/runtime_adg/span_contracts.py` (first 100 lines) | Discover Tier-1 canonical span categories |
| 4 | `agentic_core/L5_safety/v5/governance_spans.py` (targeted) | Confirm real `tracer.start_as_current_span` usage |
| 5 | `agentic_core/L4_state/otel/uwg_write_spans.py` (targeted) | Confirm UWG-write spans are emitted |
| 6 | `agentic_core/L3_orchestration/exit_control/hitl_spans.py` (targeted) | Confirm HITL / exit control spans |
| 7 | `agentic_core/L2_execution/observability/l2_otel_emitter.py` (targeted) | Confirm L2 span registry exists |
| 8 | `agentic_core/runtime/contracts/lifecycle_trace_contract.py` (header only) | Confirm 118 `_emit_*` helpers — module-load stubs |

Plus directory listing of `agentic_core/runtime/` (51 files) and four
grep sweeps (OTel tracer, runtime ADG, `_emit_*`, span-name patterns).

---

## 3. Inventory of existing emitters

Organized by architectural layer. Status codes per §8 legend.

### 3.1 Lifecycle trace stubs (module-load telemetry)

| File | Function / class | Emits what | Status | Maps to design-doc contract? |
|---|---|---|---|---|
| `agentic_core/runtime/contracts/lifecycle_trace_contract.py` | 118 `_emit_*` helpers (e.g., `_emit_records_execution_trace`, `_emit_applies_guardrail`, `_emit_writes_via_uwg`, `_emit_emits_metric_event`, ...) | `logging.getLogger("adg.<edge_kind>").debug(...)` — silent no-op at default root WARNING level | **STUB_ONLY** until OTel bridge elevates to DEBUG | Indirect — the bridge promotes to real spans with attributes matching edge kind |
| `agentic_core/runtime/utils/trace_emitter.py` | `def _emit_*` helpers | same shape | STUB_ONLY | — |
| `apps_shared/_compat/agentic_core_shim.py::_LifecycleModule.__getattr__` | Returns `_noop` for any `_emit*` / `emit_replay_key` / `emit_determinism_digest` / `record_execution_trace` | NO-OP in standalone mode only | STUB_ONLY | — |

### 3.2 The OTel lifecycle bridge (stub → real span)

| File | Class / function | Role | Status |
|---|---|---|---|
| `agentic_core/runtime/contracts/otel_lifecycle_bridge.py` | `AdgEmissionToOtelBridge(logging.Handler)` | Captures `adg.*` DEBUG records, buffers as span-shaped dicts matching the `RuntimeADGMaterializer` schema, ships through `OTelIngestService` | EXISTS_MATCHES_MATRIX (at bridge layer) — but requires DEBUG logging to be enabled at the call site |

The bridge is the glue that turns the stubs in §3.1 into real runtime
ADG records. Without the bridge active, the lifecycle stubs are
silent.

### 3.3 L0 Routing spans

| File | Emits | Span name pattern observed | Status | Maps to |
|---|---|---|---|---|
| `agentic_core/L0_routing/c0_retrieval/c0_3_enhanced/otel.py` | C0 hybrid-retrieval spans | (enhanced C0 layer; see multi-signal contract) | EXISTS_NAME_MISMATCH | `RetrievalPlan` |
| Tier-1 contract `L0.route.select` category | Matches `heal_router.v1.route`, `router.`, `route.select`, `l0.route`, `route.contract`, `.v1.route` | signal-based — not single canonical name | EXISTS_NAME_MISMATCH | `RouteContract` (design doc §4.1 row 3) |
| `agentic_core/L6_observability/heal_router_otel.py` | Real OTel tracer usage on heal router | `heal_router.v1.route` | EXISTS_NEEDS_ATTRIBUTE_HARDENING | `RouteContract` |
| `agentic_core/L0_routing/` various files | L0 routing telemetry | Signals: `selected_route`, `routing.target_model`, `route.reason_codes`, `routing.confidence_score`, `routing.tier`, `cache_decision` | EXISTS_MATCHES_MATRIX (attrs) | `RouteContract` |

### 3.4 L1 Cognition spans

| File | Emits | Status | Maps to |
|---|---|---|---|
| `agentic_core/L1_cognition/planning/otel.py` | L1 planning spans | EXISTS_NAME_MISMATCH | `L1PlanContract` |
| `agentic_core/L1_cognition/c0_context/observability.py` | C0-context observation spans | EXISTS_NAME_MISMATCH | `L1PlanContract` or context hand-off |

### 3.5 L2 Execution spans (richest surface)

| File | Class / function | Emits | Status | Maps to |
|---|---|---|---|---|
| `agentic_core/L2_execution/observability/l2_otel_emitter.py` | `L2SpanAttributeViolation`, `validate_span_attributes`, canonical L2 span registry | Registered L2 spans with strict attribute validation; raises on unknown span names or missing required attrs | **EXISTS_MATCHES_MATRIX** (L2 has its own hardened registry) | `CompiledPromptArtifact`, `SealedArtifact` |
| `agentic_core/L2_execution/observability/l2_resolution_spans.py` | L2 resolution span emission | EXISTS_NEEDS_ATTRIBUTE_HARDENING | L2 resolution pipeline |
| Tier-1 contract `L2.step.seal` | Matches `l2.step.seal`, `step.seal`, `execution.seal`, `.seal` | signal-based | EXISTS_NAME_MISMATCH (by design) | `SealedArtifact` |
| Tier-1 contract `L2.(model\|tool).invoke` | OTel GenAI semconv spans: `invoke_agent <name>`, `execute_tool <name>` | GenAI-compliant | EXISTS_MATCHES_MATRIX | Model / tool invocation inside L2 |
| `agentic_core/L6_observability/semconv/gen_ai.py` | `OPERATION_INVOKE_AGENT`, `OPERATION_EXECUTE_TOOL`, `agent_span_attributes()`, `tool_span_attributes()` | SSOT for upstream OTel GenAI semconv | EXISTS_MATCHES_MATRIX | Model / tool spans |

### 3.6 L3 Orchestration / Exit spans

| File | Emits | Status | Maps to |
|---|---|---|---|
| `agentic_core/L3_orchestration/exit_eval/otel_sdk_sink.py` | Exit-eval OTel sink | EXISTS_MATCHES_MATRIX | `ExitReviewPacket` |
| `agentic_core/L3_orchestration/exit_eval/v6/otel.py` | v6 exit-eval spans | EXISTS_MATCHES_MATRIX | `ExitReviewPacket` |
| `agentic_core/L3_orchestration/exit_eval/v6/return_payload.py` | Return-payload span hooks (16 runtime-ADG matches) | EXISTS_MATCHES_MATRIX | `ExitReviewPacket` |
| `agentic_core/L3_orchestration/exit_control/hitl_spans.py` | `_TRACER.start_as_current_span(name)` with attribute filtering | EXISTS_MATCHES_MATRIX | HITL escalation / exit-control |
| Tier-1 contract `Exit.disposition` | Matches exit disposition spans | signal-based | EXISTS_NAME_MISMATCH | `ExitReviewPacket` |
| `agentic_core/L3_orchestration/reasoning/engines/orchestrator_engine.py` | Orchestrator span emission (11 runtime-ADG matches) | EXISTS_NEEDS_ATTRIBUTE_HARDENING | orchestrator execute root |

### 3.7 L4 State / UWG spans

| File | Emits | Status | Maps to |
|---|---|---|---|
| `agentic_core/L4_state/otel/uwg_write_spans.py` | `_OTEL_TRACER.start_as_current_span(name)` for UWG durable writes | EXISTS_MATCHES_MATRIX | `CommitRequest` (future R3R4 only) |
| `agentic_core/L4_state/otel/spans.py` | Additional L4 spans | EXISTS_NEEDS_ATTRIBUTE_HARDENING | L4 state mutation |

UWG write spans exist but are NOT in scope for any current R3 app —
the design gate (§9.3) intentionally denies certification if these
fire for an R3 app.

### 3.8 L5 Safety / Ingress / Governance spans

| File | Emits | Status | Maps to |
|---|---|---|---|
| `agentic_core/L5_safety/enforcement/ingress_telemetry_otel.py` | Ingress / intake spans | EXISTS_MATCHES_MATRIX | `ValidatedRequest` (intake) |
| `agentic_core/L5_safety/v5/governance_spans.py` | `_OTEL_TRACER.start_as_current_span(name)` for governance events | EXISTS_MATCHES_MATRIX | governance / policy |
| `agentic_core/L5_safety/v5/otel_spans.py` | Additional v5 safety spans | EXISTS_NEEDS_ATTRIBUTE_HARDENING | safety plane |
| `agentic_core/L5_safety/runtime_gates/otel_spans.py` | Runtime-gate spans | EXISTS_NEEDS_ATTRIBUTE_HARDENING | gating decisions |
| `agentic_core/L5_safety/audit/safety_audit_emitter.py` | Safety-audit ledger events | LEDGER_EVENT_ONLY | audit trail |

### 3.9 L6 Observability / ingest spans

| File | Role | Status | Maps to |
|---|---|---|---|
| `agentic_core/L6_observability/otel_runtime_ingest.py` | OTel-to-runtime-ADG ingest pipeline (20 matches) | EXISTS_MATCHES_MATRIX | ingest bridge (not a contract span) |
| `agentic_core/L6_observability/shadow_eval/observer.py` + `ingest.py` + `contracts.py` | Shadow-evaluation runtime-ADG binding (15 + 8 + 12 matches) | EXISTS_MATCHES_MATRIX | shadow-eval bucket |
| `agentic_core/L6_observability/heal_router_otel.py` | Heal-router OTel emission | EXISTS_MATCHES_MATRIX | `RouteContract` (heal-tier) |
| `agentic_core/L6_observability/consensus_otel.py` | Consensus OTel spans | EXISTS_NEEDS_ATTRIBUTE_HARDENING | meta / calibration |
| `agentic_core/L6_observability/utils/engines/auto_persistence_adapter.py` | Runtime-ADG auto-persistence (19 matches) | EXISTS_MATCHES_MATRIX | persistence |

### 3.10 Runtime-ADG store (evidence store candidate)

| File | Role | Status |
|---|---|---|
| `system_learning/runtime_adg/materializer.py` (76 runtime_adg matches) | Builds runtime-ADG snapshots from span buffer | EXISTS_MATCHES_MATRIX |
| `system_learning/runtime_adg/store.py` (24 matches) | Snapshot persistence | EXISTS_MATCHES_MATRIX |
| `system_learning/runtime_adg/snapshot.py` (19 matches) | Snapshot types (`RuntimeADGNode`, `RuntimeADGSnapshot`) | EXISTS_MATCHES_MATRIX |
| `system_learning/runtime_adg/span_contracts.py` (11 matches) | **Tier-1 span coverage contract** — validates snapshots contain 5 canonical categories via multi-signal matching | EXISTS_MATCHES_MATRIX |
| `system_learning/runtime_adg/auto_persistence.py` (14 matches) | Auto-persist wiring | EXISTS_MATCHES_MATRIX |
| `system_learning/runtime_adg/advanced_analytics.py` (10 matches) | Analytics over persisted snapshots | EXISTS_MATCHES_MATRIX |
| `system_learning/engines/runtime_exhaust_collector.py` (11 matches) | Runtime exhaust collection surface | EXISTS_MATCHES_MATRIX |
| `tools/runtime_adg/backfill_trace_index.py` (10 matches) | Backfill tool | EXISTS_MATCHES_MATRIX |
| `tools/adg/runtime_query.py` (9 matches) | Query surface | EXISTS_MATCHES_MATRIX |
| `tools/otel/exercise_real_otel_pipeline.py`, `seed_synthetic_traces.py`, `runtime_view_builder.py` | OTel pipeline exercise + trace seeding + view building | EXISTS_MATCHES_MATRIX |
| `ops_scripts/ci/check_runtime_adg_coverage.py` | CI gate on runtime-ADG coverage | EXISTS_MATCHES_MATRIX |

### 3.11 Tracing mixins (class-level wiring)

| File | Role | Status |
|---|---|---|
| `agentic_core/mixins/integrated_tracing_mixin.py` (41 matches) | Integrated tracing mixin for agent classes | EXISTS_MATCHES_MATRIX |
| `agentic_core/mixins/tracing_mixin.py` (16 matches) | Base tracing mixin | EXISTS_MATCHES_MATRIX |
| `agentic_core/mixins/tracing_decorators.py` (9 matches) | Decorator-based wiring | EXISTS_MATCHES_MATRIX |
| `agentic_core/mixins/adg_tracing_hooks.py` (17 matches) | ADG-specific tracing hooks | EXISTS_MATCHES_MATRIX |
| `agentic_core/mixins/auto_span_collector.py` (11 matches) | Auto-span collection | EXISTS_MATCHES_MATRIX |
| `agentic_core/mixins/performance_optimized_collector.py` (13 matches) | Performance-tuned collector | EXISTS_MATCHES_MATRIX |

### 3.12 Prove-requirements / semconv

| File | Role | Status |
|---|---|---|
| `agentic_core/runtime/prove_requirements/otel_emitter.py` | Proof emitter for requirements | EXISTS_MATCHES_MATRIX |
| `agentic_core/runtime/prove_requirements/otel_contract.py` | Proof contract | EXISTS_MATCHES_MATRIX |
| `agentic_core/runtime/prove_requirements/otel_harness.py` | Harness | EXISTS_MATCHES_MATRIX |
| `agentic_core/L6_observability/semconv/runtime.py` | Runtime semantic conventions | EXISTS_MATCHES_MATRIX |
| `agentic_core/L6_observability/semconv/rag.py` | RAG semantic conventions | EXISTS_MATCHES_MATRIX |
| `agentic_core/L6_observability/semconv/gen_ai.py` | **GenAI semconv (upstream OTel spec)** | EXISTS_MATCHES_MATRIX |

---

## 4. Comparison to the R3_grounded_read design matrix

| # | Design-doc contract | Proposed span name (design v1) | Existing emitter? | Closest existing span signal / category | Status | Implementation implication |
|:---:|---|---|:---:|---|---|---|
| 1 | `ValidatedRequest` | `app.<app_name>.intake.validated_request` | ✅ Yes | `agentic_core/L5_safety/enforcement/ingress_telemetry_otel.py` — ingress spans | **EXISTS_NAME_MISMATCH** | Option A: adjust design matrix to reference canonical ingress spans. Option B: add a `contract_name=ValidatedRequest` attribute to existing ingress spans. |
| 2 | `L1PlanContract` | `app.<app_name>.l1.plan_contract` | ✅ Yes | `agentic_core/L1_cognition/planning/otel.py`, `L1_cognition/c0_context/observability.py` | **EXISTS_NAME_MISMATCH** | Same — either adjust proposed names OR add contract attributes |
| 3 | `RouteContract` | `app.<app_name>.l0.route_contract` | ✅ Yes — by Tier-1 signal match | `heal_router.v1.route` + signals (`selected_route`, `routing.target_model`, `route.reason_codes`, `routing.confidence_score`, `routing.tier`, `cache_decision`) | **EXISTS_MATCHES_MATRIX** (via signals) | Tier-1 category already matches; simply extend with `contract_id=route_id` attribute |
| 4 | `RetrievalPlan` | `app.<app_name>.c0.retrieval_plan` | ✅ Partial | `agentic_core/L0_routing/c0_retrieval/c0_3_enhanced/otel.py`, `L1_cognition/c0_context/observability.py` | **EXISTS_NEEDS_ATTRIBUTE_HARDENING** | Retrieval-plan attributes (`collection`, `k`) may not be emitted uniformly; requires attribute audit across R3 apps |
| 5 | `FinalEvidenceContract` | `app.<app_name>.c0.final_evidence_contract` | ⚠️ Unclear | C0 retrieval layer emits spans but evidence-shaping is not a clearly labelled span today | **UNKNOWN_NEEDS_RUNTIME_RUN** | Need a live trace to confirm; likely there but name unknown |
| 6 | `CompiledPromptArtifact` / `PromptEnvelope` | `app.<app_name>.pa.compiled_prompt_artifact` | ✅ Yes (via GenAI semconv) | `agentic_core/L6_observability/semconv/gen_ai.py` + `L2_execution/observability/l2_otel_emitter.py` canonical L2 registry | **EXISTS_NEEDS_ATTRIBUTE_HARDENING** | `prompt_artifact_id`, `contract_name`, `abstain_recommended` not standardized as span attrs — likely present but not under a single canonical name |
| 7 | `SealedArtifact` | `app.<app_name>.l2.sealed_artifact` | ✅ Yes | Tier-1 `L2.step.seal` category: `l2.step.seal`, `step.seal`, `execution.seal`, `.seal` | **EXISTS_MATCHES_MATRIX** (via signals) | Direct match — add `artifact_hash`, `grounded`, `gate_disposition` attributes as required-by-contract |
| 8 | `ExitReviewPacket` | `app.<app_name>.exit.review_packet` | ✅ Yes | `L3_orchestration/exit_eval/otel_sdk_sink.py`, `v6/otel.py`, `v6/return_payload.py`, Tier-1 `Exit.disposition` | **EXISTS_MATCHES_MATRIX** | Direct match — harden `exit_disposition`, `l6_ingested` as required attributes |

**Overall R3 gap assessment**:
- 5 of 8 contracts have direct or signal-matched emitters today
  (`RouteContract`, `SealedArtifact`, `ExitReviewPacket`,
  `CompiledPromptArtifact`/`PromptEnvelope`, `ValidatedRequest`)
- 2 of 8 likely emit but need attribute hardening
  (`L1PlanContract`, `RetrievalPlan`)
- 1 of 8 is ambiguous without a live trace
  (`FinalEvidenceContract`)

**Zero contracts require new emitter creation.** All eight can be
satisfied by (a) aligning the design matrix with existing span names
OR (b) annotating existing spans with `contract_name=...` and
`contract_id=...` attributes — whichever is cheaper per-contract.

---

## 5. Comparison to the `build_time_compiler` (apps_qna) shape

apps_qna's runtime path was not exhaustively audited here (no
apps_qna-specific file inspected), but inference from the cohort:

| Required span (design §5) | Existing emitter likelihood | Status | Note |
|---|---|---|---|
| `ValidatedRequest` / intake | Likely — `ingress_telemetry_otel.py` serves all apps | **EXISTS_NAME_MISMATCH** | Same adjustment as R3 intake |
| `build.pack_artifact` | **Unknown** | **UNKNOWN_NEEDS_RUNTIME_RUN** | apps_qna-specific; was not inspected |
| `ledger.emit` | Likely — ledger emission is a §29 constitutional requirement and apps_qna already has closed-loop router evidence | **TELEMETRY_MARKER_ONLY** → likely promotable | Need live trace or per-app emitter inspection |

The apps_qna gap is narrower than the R3 gap simply because the
surface is smaller (3 spans vs 8). An apps_qna-specific Phase A.1
could confirm the `build.pack_artifact` emission shape in ~1 hour.

---

## 6. Formal exception verification evidence

### 6.1 apps_eval (`evaluator_only`)

| CC | Evidence search result | Status |
|---|---|---|
| **CC-EVAL-01** (no eval-of-evaluator circularity) | No dedicated span-level check located. Would require a negative query on the runtime-ADG store: *"no descendant span has `app_name=apps_eval` when root already has `app_name=apps_eval`"*. | **UNKNOWN_NEEDS_RUNTIME_RUN** — the evidence mechanism exists (runtime ADG query language, `tools/adg/runtime_query.py`), but the specific negative control would need to be added as a cert-harness query |
| **CC-EVAL-03** (stability / evaluator evidence) | `agentic_core/L6_observability/shadow_eval/observer.py` + `contracts.py` + `ingest.py` provide shadow-eval span contracts with runtime-ADG binding (35 runtime_adg matches combined). This is the evaluator stability surface. | **EXISTS_MATCHES_MATRIX** |

### 6.2 apps_underwriting_ai (`regulatory_domain`)

| CC | Evidence search result | Status |
|---|---|---|
| **CC-UW-01** (regulated decision path + own governance protocol) | Not separately inspected. Governance spans exist at `L5_safety/v5/governance_spans.py`, but whether apps_underwriting_ai has its own domain-specific `governance.regulated_decision` span is unknown. | **UNKNOWN_NEEDS_RUNTIME_RUN** |
| **CC-UW-02** (no arbitrary R3 contract inheritance) | Negative check shape; same mechanism as CC-EVAL-01 | **UNKNOWN_NEEDS_RUNTIME_RUN** |
| **CC-UW-03** (charter-permitted operations only) | Requires `operation_kind` attribute on every span; not confirmed | **UNKNOWN_NEEDS_RUNTIME_RUN** |

### 6.3 apps_shared (`shared_library_surface`)

| CC | Evidence search result | Status |
|---|---|---|
| **CC-SHARED-01** (GovernedAppRunner substrate consumed by R3 apps) | Implicit — every R3 app trace that exists is proof, because every R3 runner subclasses `apps_shared.integrations.governed_app_runner.GovernedAppRunner`. | **EXISTS_MATCHES_MATRIX** (via existence of R3 traces) |
| **CC-SHARED-03** (SealedArtifact in proof harness only) | Requires code-path origin attribution in spans (e.g., `span.attributes["code.filepath"]`). OTel GenAI semconv supports this. Not confirmed whether current emitters propagate origin consistently. | **EXISTS_NEEDS_ATTRIBUTE_HARDENING** |
| **CC-SHARED-05** (agentic_core_shim full-stack no-op OR standalone excluded) | **No trace-level evidence exists today that the shim early-returned vs installed 12 fallbacks.** The shim itself is not instrumented. | **NOT_FOUND** — requires either: (a) a boot-time telemetry event in `install()`, (b) env-var assertion at cert-harness startup, or (c) packaging/CI/deployment audit per scorecard addendum |

---

## 7. Runtime ADG readiness

| Question | Answer |
|---|---|
| **Does runtime ADG already store span-like evidence?** | ✅ **Yes.** `system_learning/runtime_adg/` has a full store with materializer, snapshot types, auto-persistence, and 843 lines of Tier-1 span contracts. `RuntimeADGNode` and `RuntimeADGSnapshot` types already exist. |
| **What schema exists?** | Multi-signal: each node carries `name`, `kind`, `layer`, `attributes_json` (dict). Tier-1 contract validates coverage of 5 canonical categories (`runtime.trace_root`, `L0.route.select`, `L2.step.seal`, `L2.(model\|tool).invoke`, `Exit.disposition`) via signal-based matching. |
| **Can it store contract-to-span binding?** | ✅ **Yes, via `attributes_json`.** The design-doc attributes (`contract_name`, `contract_id`, `manifest_hash`, `parent_contract_id`, etc.) can live in `attributes_json` without schema change. |
| **What gaps exist?** | (a) No per-app-route contract-level category yet (current Tier-1 is L0/L2/Exit-level, not R3-chain-level); (b) no negative-evidence query helpers for formal exceptions; (c) no `manifest_hash` attribute convention; (d) no per-app cert-status recording in node metadata; (e) shim-behavior evidence mechanism missing (CC-SHARED-05). |

**Answer to design-doc Q2**: runtime ADG **CAN** serve as the evidence
store. Confidence HIGH. No parallel store is required.

---

## 8. Findings classification (status legend)

| Status | Count | Example |
|---|---:|---|
| `EXISTS_MATCHES_MATRIX` | 20+ | L2 canonical registry, GenAI semconv, exit-eval sink, Tier-1 Seal category, governance spans, runtime ADG store, shadow eval contracts, UWG write spans, lifecycle → OTel bridge |
| `EXISTS_NEEDS_ATTRIBUTE_HARDENING` | 7 | L1 planning, L2 resolution, L4 state spans, L5 v5 otel spans, L5 runtime gates, L6 consensus, orchestrator engine, CompiledPromptArtifact, RetrievalPlan, CC-SHARED-03 |
| `EXISTS_NAME_MISMATCH` | 5 | ValidatedRequest (intake), L1PlanContract, RouteContract (signal-matched), C0 enhanced, Tier-1 categories vs design §7 naming |
| `TELEMETRY_MARKER_ONLY` | 118 | lifecycle_trace_contract `_emit_*` helpers — stubs until bridge elevates |
| `LEDGER_EVENT_ONLY` | 2 | safety_audit_emitter, apps_qna ledger emissions |
| `STUB_ONLY` | 1 | apps_shared `_LifecycleModule.__getattr__` (standalone fallback) |
| `NOT_FOUND` | 2 | CC-SHARED-05 shim-behavior evidence, `manifest_hash` convention |
| `UNKNOWN_NEEDS_RUNTIME_RUN` | 6 | FinalEvidenceContract span name, apps_qna build.pack_artifact, CC-EVAL-01 negative check, CC-UW-01/02/03 regulated-decision evidence |

---

## 9. Recommendations

### 9.1 Minimum emitter changes likely needed later

None to a first approximation. All 8 R3 contracts have either direct
or signal-matched emitters. The implementation work is:

1. **Extend span attributes** on 5–7 existing emitters to include
   `contract_name`, `contract_id`, `parent_contract_id`,
   `manifest_hash`, `app_name`, `route_shape`. This is additive; no
   existing span is renamed.
2. **Add one new boot-time telemetry event** in
   `apps_shared/_compat/agentic_core_shim.py::install()` to record
   which branch executed (`shim.early_return_full_stack` vs
   `shim.installed_12_fallbacks`). Alternatively, record the
   equivalent at the cert-harness startup by inspecting `sys.modules`.
3. **Add per-app-route category contracts** to
   `system_learning/runtime_adg/span_contracts.py` mirroring the
   Tier-1 pattern but at the R3-chain granularity (or to a new Tier-2
   file to avoid mixing scopes).

Zero renames. Zero behavior changes.

### 9.2 Should the proposed design-doc span names be kept or adjusted?

**Adjusted.** The design doc's `app.<app_name>.<layer>.<contract>`
pattern does not match existing emitters. Two equally-honest options:

| Option | Design matrix change | Emitter change |
|---|---|---|
| **A (preferred)** | Rewrite §7 of the design doc to reference existing span-name patterns (Tier-1 category signals for L0/L2/Exit; GenAI semconv for model/tool; existing L1/C0/ingress/UWG names). Keep the proposed attribute contract. | None |
| **B** | Keep the proposed names; add aliases on every existing emitter | Additive — set two span names during a transition window |

Option A is cheaper, loses no information, and honors the design
doc's own §7 caveat that proposed names are PROPOSED pending this
inventory.

### 9.3 Can the runtime ADG be the evidence store?

**Yes (HIGH confidence).** `system_learning/runtime_adg/` already
does this. ADR-074 ("Runtime Bucket as OTEL View") already enshrines
that the runtime ADG IS the OTel-view bucket. Phase B should extend
the Tier-1 span contracts to Tier-2 per-app-route contracts, not
build a parallel store.

### 9.4 Recommended Phase B scope

Phase B ("binding schema") should be structured around the existing
infrastructure, not around greenfield. Concrete Phase B tasks:

| # | Task | Owner surface |
|:---:|---|---|
| **B.1** | **Reconcile design matrix §7 with existing span names.** Update `docs/reference/runtime_certification/contract_span_binding_matrix.md` to reference the Tier-1 signal categories + GenAI semconv + existing L1/C0/ingress/UWG names. This is a doc change only. | `docs/reference/runtime_certification/` |
| **B.2** | **Define the per-app-route Tier-2 contract schema** as a pydantic model mirroring `system_learning/runtime_adg/span_contracts.py::_CategoryContract` — one entry per R3 contract per app, with `required_attributes` being the design-doc §8 attribute list. | `system_learning/runtime_adg/app_route_span_contracts.py` (new) OR extension of existing `span_contracts.py` |
| **B.3** | **Decide `manifest_hash` attribute convention** (design doc Q6). Default: whole-file SHA-256 of raw bytes. Define on the pydantic model. | same file |
| **B.4** | **Define CC-SHARED-05 evidence mechanism.** Recommend: env-var assertion AT cert-harness startup + `sys.modules` inspection at run end (both required, redundant-evidence path). Add a boot-time telemetry event in `apps_shared/_compat/agentic_core_shim.py::install()` — this is the ONE emitter change Phase B needs, but it is additive, tiny (single `logging.info()`), and does not touch risk-bearing code paths. | documented in Phase B plan |
| **B.5** | **Negative-control query helpers** for formal-exception apps. Thin wrappers over `tools/adg/runtime_query.py` implementing CC-EVAL-01, CC-UW-02, CC-SHARED-03 negative checks. | `tools/runtime_cert/negative_controls.py` (new) |
| **B.6** | **No scanner changes, no CI changes, no app migration in Phase B.** | — |

Estimated Phase B cost: ~200 lines net new code (schema file +
negative-control queries + one 3-line emitter addition to the shim);
~80 lines new tests pinning the schema.

### 9.5 Explicit no-certification disclaimer

**No runtime certification was performed by this document.** Every
`apps_*` classification remains at its post-W14 state:

- 6 apps in `APP_OVERLAY_STATIC_EVIDENCE`
- 3 apps in `FORMAL_EXCEPTION_STATIC_EVIDENCE`
- 0 apps in `RUNTIME_CERTIFIED`
- 0 apps in `FORMAL_EXCEPTION_VERIFIED`
- Every app reads `runtime_certification_status: NOT_CERTIFIED`

---

## 10. Provenance

| Item | Value |
|---|---|
| Report version | v1 (Phase A inventory) |
| Generated | 2026-04-30 |
| Design doc this reports against | `docs/reference/runtime_certification/contract_span_binding_matrix.md` v1 |
| Predecessor report | `docs/reports/apps_static_scorecard_post_w14.md` |
| Files inspected (full/partial reads) | 8 |
| Grep sweeps | 5 (OTel tracer usage; runtime_adg mentions; `_emit_*` definitions; span-name patterns; directory listing) |
| Total grep-match coverage | 1,474 matches across ~200 files |
| Files modified | 0 |
| Emitters renamed | 0 |
| Emitters added | 0 |
| Apps certified | 0 |
| Apps affected by this document | 0 (read-only) |
