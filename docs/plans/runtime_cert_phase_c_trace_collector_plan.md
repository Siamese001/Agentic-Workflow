# Phase C Plan — Trace Collector / Runtime ADG Ingest

**Status**: DESIGN PLAN — planning only. No code. No emitter change.
No scanner change. No CI gate. No app certified.
**Plan version**: v1 (2026-04-30, initial plan); **v2** (2026-04-30, Author-Gate decisions captured — this revision adds §0 and updates §12 / Provenance)
**Generated**: 2026-04-30
**Predecessors**:
- Phase A report: `docs/reports/runtime_certification/phase_a_trace_inventory.md`
- Design matrix v2: `docs/reference/runtime_certification/contract_span_binding_matrix.md`
- Phase B.2 schema: `system_learning/runtime_adg/app_route_contracts.py`
- Phase B.3 hash: `system_learning/runtime_adg/manifest_hash.py`
- Phase B.4 evidence: `system_learning/runtime_adg/formal_exception_evidence.py`
- Phase B.5 helpers: `tools/runtime_cert/negative_controls.py`

---

## 0. Author-Gate Decisions Captured (plan v2)

All 9 Author-Gate decisions (AG-C-1 through AG-C-9) are **APPROVED**
as of 2026-04-30. The implementation details in §§1-14 are
unchanged — this section records outcomes only.

### 0.1 Approved decisions

| # | Decision | Outcome | Captured rationale |
|:---:|---|:---:|---|
| **AG-C-1** | Use runtime ADG (`system_learning/runtime_adg/`) as the evidence store | ✅ **APPROVED** | ADR-074 codifies the runtime bucket as a deterministic view over OTel spans. Phase A confirmed the store is already load-bearing. Reusing it avoids a parallel-store maintenance burden. |
| **AG-C-2** | **No** parallel evidence store | ✅ **APPROVED** | Corollary of AG-C-1. Any Phase C code that writes to a new store is out of scope and will be rejected at sub-phase Author-Gate. |
| **AG-C-3** | The 18-field Phase C row schema in §3.1 is frozen for C.1–C.7 | ✅ **APPROVED** | Schema is minimal, compatible with Phase B.2 `ContractSpanBinding`, Phase B.4 `SharedShimEvidence`, and Phase B.5 defensive `_row_*` accessors. |
| **AG-C-4** | **No** scanner classification changes during C.1–C.7 | ✅ **APPROVED** | B.6 standing invariant preserved. Scanner changes belong exclusively to Phase F (promotion workflow). |
| **AG-C-5** | **No** emitter renaming during C.1–C.7 | ✅ **APPROVED** | Design matrix v2 §7 signal-based binding absorbs span-name drift without renames. Attribute hardening (via §3.1 row normalization) is a separate, additive concern. |
| **AG-C-6** | Choose the first live-trace smoke app for C.6 | ✅ **APPROVED — apps_research** | See §0.2 below for the multi-point rationale. |
| **AG-C-7** | Require `AGENTIC_CORE_STACK=full` during C.6 smoke runs | ✅ **APPROVED** | Matches Phase B.4's "redundant evidence" posture (option b). Trivially enforced at the smoke harness entry point; adds zero runtime-emitter cost. |
| **AG-C-8** | Approve the fail-closed status vocabulary: `TRACE_GAP`, `ATTRIBUTE_HARDENING_REQUIRED`, `UNKNOWN_NEEDS_RUNTIME_RUN`, `FORBIDDEN_SPAN_VIOLATION`, `FORMAL_EXCEPTION_VIOLATION`, `CC_SHARED_05_NOT_PASSED` | ✅ **APPROVED** | Phase D will consume these identifiers verbatim. Changing them later churns both phases. Also pins the invariant that Phase C never writes `runtime_certification_status` other than `NOT_CERTIFIED`. |
| **AG-C-9** | Sub-phase ordering: C.1 → C.2 → (C.3 ∥ C.4 ∥ C.5) → C.6 → C.7 | ✅ **APPROVED** | Maximizes parallelism after C.2 lands (the row normalizer is the gating artifact) while keeping the foundational adapter (C.1) and normalizer (C.2) strictly sequential. C.6 and C.7 depend on all three extractors. |

### 0.2 AG-C-6 — first smoke app = `apps_research` (rationale)

`apps_research` was chosen for C.6 over the alternative (`apps_exec`)
for these six reasons:

1. **Route shape** — `apps_research` is `R3_grounded_read`, the cleanest R3 surface.
2. **No HITL complication** — `apps_research`'s `GovernedAppRunner` subclass does not declare `HITL_ENABLED`, so the smoke harness does not need to simulate human-in-the-loop branches.
3. **No durable-write ambiguity** — output artifacts are local JSON, not routed through any `CommitRequest` path. Lowers the risk of mis-classifying an artifact write as a durable write.
4. **No formal-exception harness** — `apps_research` is not a formal-exception app; C.6 exercises the pure R3 path without CC-* evidence plumbing interleaved.
5. **Clean static pilot precedent** — `apps_research` was the first app migrated to `APP_OVERLAY_STATIC_EVIDENCE` in W9. Its manifest and `spine_handoff` module are the smallest and best-documented across the cohort.
6. **Lower risk of output-vs-durable-write confusion** — unlike apps_rfp (portal submission concerns) or apps_lic (license generation), apps_research produces research outputs with unambiguous artifact semantics.

**Alternative (not chosen)**: `apps_exec` is a fine backup if unforeseen blockers appear during C.6 wiring — its shape is similar. Switching requires a **follow-up Author-Gate** (AG-C-6-bis) amending this section; do NOT silently re-pick the smoke app.

### 0.3 Scope and limits of these approvals

These approvals authorize Phase C **planning continuity** toward C.1.
They explicitly do NOT authorize the following:

- ❌ They do NOT authorize starting C.1 implementation directly. **C.1 requires its own scoped Author-Gate prompt** with its own plan file (target: `.codex/plans/runtime-cert-c1-query-adapter-<6hex>.md`) before any Python is written.
- ❌ They do NOT certify any `apps_*` app. All 9 apps remain `NOT_CERTIFIED`. The cohort classification is unchanged: 6 `APP_OVERLAY_STATIC_EVIDENCE` + 3 `FORMAL_EXCEPTION_STATIC_EVIDENCE` + 0 `RUNTIME_CERTIFIED` + 0 `FORMAL_EXCEPTION_VERIFIED`.
- ❌ They do NOT authorize scanner classification changes during C.1–C.7 (AG-C-4 is explicit).
- ❌ They do NOT authorize new CI gates during C.1–C.7 (§1 non-goals preserved; the Phase E CI gate is a separate phase).
- ❌ They do NOT authorize emitter renames during C.1–C.7 (AG-C-5 is explicit).
- ❌ They do NOT authorize any app behavior change.
- ❌ They do NOT authorize writing `runtime_certification_status` values other than `NOT_CERTIFIED` anywhere in Phase C outputs (AG-C-8 invariant).

### 0.4 Open follow-up items

| # | Item | Notes |
|:---:|---|---|
| **AG-C-6-bis** | Authorize a switch of C.6 smoke app away from `apps_research` if C.6 wiring hits an unforeseen blocker | Not triggered today; future decision, not approved in advance. |
| **AG-C-7-bis** | Decide whether `AGENTIC_CORE_STACK=full` remains required in Phase D/E (beyond C.6) | Out of scope today. Will surface at Phase D Author-Gate. |

---

## 1. Purpose and non-goals

**Purpose**: define how Phase C will **collect / query** existing
runtime trace evidence from the OTel + runtime-ADG substrate and
transform it into per-app trace records consumable by the Phase B
schema and negative-control helpers.

**Non-goals (hard)**:

- **Phase C does NOT certify apps.** Every app remains at its
  post-W14 classification: 6 `APP_OVERLAY_STATIC_EVIDENCE`, 3
  `FORMAL_EXCEPTION_STATIC_EVIDENCE`, 0 `RUNTIME_CERTIFIED`, 0
  `FORMAL_EXCEPTION_VERIFIED`. Every app stays `NOT_CERTIFIED`.
- **Phase C does NOT modify scanner classification logic.** No change
  to `tools/analysis/apps_spine_coverage.py`.
- **Phase C MUST use the existing runtime-ADG / OTel infrastructure.**
  Per ADR-074, the runtime bucket IS a deterministic view over OTel
  spans. Phase C is a query layer on top of that view, not a new store.
- **No parallel evidence store.** `system_learning/runtime_adg/`
  remains the SSOT.
- **No span renaming.** Attribute hardening on existing emitters MAY
  be required; span-name renaming is a separately-approved operation.
- **No runtime behavior change.** Phase C is read-only against the
  existing store.

---

## 2. Current infrastructure inventory (read-only reconnaissance)

Inspected before writing this plan:

| File | Role | Key facts |
|---|---|---|
| `tools/adg/runtime_query.py` | **Query API over runtime ADG** — `RuntimeADGQuery` class | SQLite read-only (`uri=True&mode=ro&immutable=1`), per-call connection, tiny LRU, snapshot-provenance every return. Already exposes `blast_radius`, `hotspot_info`, `upstream_callers`, `downstream_targets`, `swallow_sites_reaching`, `pview_contains`. Phase C adds per-app-trace helpers on top of this surface. |
| `system_learning/runtime_adg/snapshot.py` | Snapshot types | `RuntimeADGNode` (`node_id`, `name`, `kind`, `layer`, `component`, `started_at_utc`, `duration_ms`, `status`, `attributes_json` as compact sorted JSON string) + `RuntimeADGSnapshot`. Content-addressed via SHA-256 of canonical_bytes. |
| `system_learning/runtime_adg/span_contracts.py` | Tier-1 multi-signal span categorization | `_CategoryContract(name_patterns, kinds, layers, required_any_attr)`, `SIGNAL_THRESHOLD=2`. 5 canonical Tier-1 categories (`runtime.trace_root`, `L0.route.select`, `L2.step.seal`, `L2.(model\|tool).invoke`, `Exit.disposition`). |
| `system_learning/runtime_adg/materializer.py` | Snapshot builder | Converts in-memory span buffers into `RuntimeADGSnapshot` objects. Phase C reuses without modification. |
| `system_learning/runtime_adg/store.py` | Persistence | `FileBackedVersionStore` (L4). No new storage subsystem in Phase C. |
| `system_learning/runtime_adg/auto_persistence.py` | Wiring | Auto-persist hook. Read-only from Phase C's perspective. |
| `agentic_core/L6_observability/otel_runtime_ingest.py` | OTel → runtime ADG bridge | Ingest pipeline used by tests and live sessions. Phase C calls this as a supplier, not a modifier. |
| `agentic_core/runtime/contracts/otel_lifecycle_bridge.py` | Stub-to-OTel bridge | `AdgEmissionToOtelBridge` elevates `adg.*` DEBUG logs to real spans, ships through `OTelIngestService`. Read-only consumer for Phase C. |
| `ops_scripts/ci/check_runtime_adg_coverage.py` | Existing CI gate | Enforces Tier-1 coverage. Phase C's CI gate (Phase E, out of scope here) will be **complementary**, not a replacement. |
| `docs/reports/runtime_certification/phase_a_trace_inventory.md` | Phase A output | R3 coverage: 5/8 EM, 2/8 EAH, 1/8 UNR (`FinalEvidenceContract`), 0/8 require new emitter. |
| `docs/reference/runtime_certification/contract_span_binding_matrix.md` v2 | Binding matrix | §4.1 R3 matrix, §5.1 BTC matrix, §6.3 CC-SHARED-05, §7 normalized-cert-alias convention, §8 10 required attrs, §9 fail-closed gate. |

**Takeaway**: the substrate is rich and already load-bearing. Phase C
bolts a per-app-trace query helper onto an existing, tested surface.

---

## 3. Data model proposal

### 3.1 Trace record row (Phase C normalized shape)

Each row is a `dict[str, Any]` consumable by:

- `tools/runtime_cert/negative_controls.py` (already field-compatible
  per B.5 design — defensive `_row_*` helpers read top-level OR nested
  `attributes`)
- Future Phase D harness (not yet written)
- Future JSON archival at `docs/reports/runtime_cert/<app>/<YYYY-Www>.md`

**Required fields**:

| Field | Type | Source | Notes |
|---|---|---|---|
| `app_name` | `str` | span attribute OR inferred from file path | Must start with `apps_` |
| `route_shape` | `str` | app's `spine_manifest.yaml::claimed_routes` (read at collection time) | One of the 4 valid `RouteShape` values |
| `trace_id` | `str` | OTel trace id | Non-empty |
| `span_id` | `str` | OTel span id | Non-empty |
| `parent_span_id` | `str \| None` | OTel | `None` / `""` for root |
| `span_name` | `str` | `RuntimeADGNode.name` | Raw emitter name |
| `contract_name` | `str \| None` | span attribute OR mapped from Tier-1 category | Via B.5 helpers resolves to R3 / R3R4 / `None` |
| `normalized_cert_alias` | `str` | resolved by mapping (§4 below) | Harness-internal alias |
| `manifest_hash` | `str` | `compute_manifest_hash_for_app(app_name)` | 64-char lowercase hex |
| `static_runtime_mode` | `str` | scanner output (read-only consultation of `apps_spine_coverage`) | `APP_OVERLAY_STATIC_EVIDENCE` / `FORMAL_EXCEPTION_STATIC_EVIDENCE` |
| `runtime_certification_status` | `str` | always `NOT_CERTIFIED` in Phase C (Phase D upgrades) | Writing any other value here is a Phase C bug |
| `artifact_id` / `contract_id` | `str \| None` | span attribute | Required for EAH contracts; may be absent pre-hardening |
| `source_path` / `file_path` | `str \| None` | OTel `code.filepath` or emitter metadata | Required for CC-SHARED-03 discrimination |
| `attributes` | `dict[str, Any]` | `json.loads(RuntimeADGNode.attributes_json)` | Nested attrs preserved |
| `timestamp` | `int` | `RuntimeADGNode.started_at_utc` | Unix milliseconds |
| `evidence_source` | `str` | provenance — e.g., `"runtime_adg.snapshot.<snapshot_id>"` | Required for audit |

### 3.2 Record-set envelope

```python
{
    "snapshot_id": "<sha256>",
    "snapshot_path": "<path/to/sqlite>",
    "collected_at_utc": <unix_ms>,
    "app_name": "apps_rfp",
    "route_shape": "R3_grounded_read",
    "manifest_hash": "<sha256-raw-bytes>",
    "rows": [ <row>, <row>, ... ],
    "gap_report": {
        "contracts_missing": [...],
        "contracts_needing_attribute_hardening": [...],
        "contracts_unknown_after_collection": [...],
    },
}
```

The envelope carries provenance explicitly so Phase D and Phase E can
reason about sample freshness (design matrix §12 Q2 defaults — reuse
runtime ADG; no parallel store).

---

## 4. Mapping strategy (Phase B.2 `ContractSpanBinding` → runtime row)

Each incoming `RuntimeADGNode` is classified into at most one
`contract_name` via the following precedence (mirrors binding matrix
v2 §7.1):

| Priority | Match signal | Source |
|:---:|---|---|
| **1** | Tier-1 signal category match (≥2 of 4 signals: name / kind / layer / attrs) | `system_learning/runtime_adg/span_contracts.py::_TIER1_CONTRACTS` |
| **2** | OTel GenAI semconv: `invoke_agent <name>` → `CompiledPromptArtifact` equivalence; `execute_tool <name>` → tool span | `agentic_core/L6_observability/semconv/gen_ai.py` |
| **3** | Explicit `ContractSpanBinding.accepted_span_name_patterns` substring match | Per-app B.2 contract |
| **4** | Explicit `accepted_emitter_files` file-path match on `attributes["code.filepath"]` | Per-app B.2 contract |
| **5** | `attributes["contract_name"]` direct assertion (post-hardening) | Set by the emitter when Phase C.7 attribute hardening lands |

Rules:

- A single node MAY match multiple contracts via priorities 3-4; the
  **highest-priority** match wins. Ties fail closed (row flagged as
  ambiguous, `contract_name=None`, logged in `gap_report`).
- `normalized_cert_alias` is derived from the winning contract via
  `ContractSpanBinding.normalized_cert_alias`.
- Priority 5 (direct attribute assertion) is preferred once Phase C.7
  attribute hardening ships — it removes ambiguity entirely.

---

## 5. Phase C sub-phases

Seven sub-phases, each its own plan file and Author-Gate decision.
Sub-phase boundaries keep each change-set ≤ ~250 lines so Author-Gate
review stays tractable.

| Sub | Name | Output | Size |
|:---:|---|---|---|
| **C.1** | Read-only runtime-ADG query adapter | `tools/runtime_cert/runtime_adg_query_adapter.py` — thin wrapper that accepts a snapshot path or a live `RuntimeADGQuery` instance, yields `RuntimeADGNode` iterables filtered by `trace_id` / `app_name` / `time_window`. No schema mutation. Tests use synthetic `RuntimeADGSnapshot` fixtures. | ~150 + ~60 tests |
| **C.2** | Trace row normalizer | `tools/runtime_cert/trace_row_normalizer.py` — converts `RuntimeADGNode` → Phase C row (§3.1). Implements the §4 mapping precedence. Purity-enforced: no I/O, deterministic. | ~180 + ~100 tests |
| **C.3** | R3 per-app evidence extractor | `tools/runtime_cert/extractors/r3_evidence.py` — orchestrates C.1 + C.2 for a single R3 app; returns envelope + gap report identifying missing / EAH / UNR contracts per §3.2. | ~200 + ~120 tests |
| **C.4** | `build_time_compiler` evidence extractor | `tools/runtime_cert/extractors/btc_evidence.py` — apps_qna-specific. Emits forbidden-R3-assertion guardrail from binding matrix §5.2. | ~120 + ~80 tests |
| **C.5** | Formal-exception evidence extractor | `tools/runtime_cert/extractors/formal_exception_evidence.py` — orchestrates B.4 `collect_cc_shared_05_evidence()` + B.5 negative-control helpers for apps_eval / apps_underwriting_ai / apps_shared. | ~150 + ~100 tests |
| **C.6** | Live-trace smoke report | `tools/runtime_cert/smoke/live_trace_smoke.py` + `docs/reports/runtime_cert/<app>/smoke_<YYYY-MM-DD>.md` — runs C.3/C.4/C.5 against ONE chosen app (Author-Gate picks apps_research OR apps_exec first). Prints gap report. **DOES NOT promote the app's certification.** | ~150 + ~80 tests |
| **C.7** | Attribute-hardening gap report | `tools/runtime_cert/reports/attribute_hardening_gap.py` + `docs/reports/runtime_cert/attribute_hardening_backlog.md` — enumerates missing attributes per emitter identified across C.6 runs. Emitters are NOT edited by Phase C; the report feeds a separate future Author-Gate session. | ~100 + ~50 tests |

Sub-phase ordering: **C.1 → C.2 → (C.3 ∥ C.4 ∥ C.5) → C.6 → C.7**. C.3/C.4/C.5 are parallel-safe after C.2 lands.

---

## 6. FinalEvidenceContract — resolving `UNKNOWN_NEEDS_RUNTIME_RUN`

Phase A flagged `FinalEvidenceContract` as `UNR` — the one R3 contract
whose emitter is not yet confirmed by static inspection.

**Phase C resolution plan**:

| Step | Action |
|:---:|---|
| 1 | C.3 R3 extractor attempts to match a C0-retrieval-layer span carrying `evidence_hash` + `citation_count` + `support_coverage` attributes. |
| 2 | If the match succeeds AND all 3 attributes are present → status upgrades from `UNR` to `EM` (noted in the gap report; binding matrix v2 §4.1 amended in a follow-up doc change). |
| 3 | If the match succeeds but attributes missing → status becomes `EAH` (attribute hardening needed; feeds C.7 backlog). |
| 4 | If no candidate span is found across 10 qualifying live traces → status **remains `UNR`**. The gap report records `contracts_unknown_after_collection: [FinalEvidenceContract]` and the app's R3 cert is blocked until the contract is either found or reclassified. |

**Failure form**: `TRACE_GAP` in §9 fail-closed rules. Never
`certification = DENIED` in Phase C — that's Phase D's vocabulary.

**Required attributes** (if emitter exists):
- `contract_name` ∈ {`FinalEvidenceContract`} OR matched via Tier-1 + span-name heuristic
- `contract_id` (evidence_id)
- `evidence_hash` (64-char lowercase hex SHA-256)
- `citation_count` (int ≥ 0)
- `support_coverage` (float in [0.0, 1.0])
- `parent_contract_id` referring to the parent `RetrievalPlan`'s `contract_id`

**Fallback status if no span appears**: `UNR` retained, gap report
populated, Phase D blocked for the affected app.

---

## 7. apps_qna `build.pack_artifact` — resolving `UNKNOWN_NEEDS_RUNTIME_RUN`

Phase A did not audit apps_qna internals. Phase C.4 resolves via a
1-hour apps_qna walk AND live-trace inspection.

**Required intake evidence** (ValidatedRequest):
- Same shape as R3 ValidatedRequest (binding matrix §5.1 row 1) —
  shared ingress via `agentic_core/L5_safety/enforcement/ingress_telemetry_otel.py`
- Must carry `app_name=apps_qna`, `route_shape=build_time_compiler`,
  `run_id`, `contract_name=ValidatedRequest`, `contract_id`, `manifest_hash`

**Required build artifact evidence** (`build.pack_artifact`):
- `build_artifact_id` (non-empty)
- `source_pack_id` (resolves to a known source pack in the build registry)
- `output_pack_hash` (64-char lowercase hex SHA-256)
- `parent_contract_id` referring to the `ValidatedRequest.contract_id`

**Required ledger emission** (`ledger.emit`):
- `ledger_name="apps_qna_build"` (or explicitly declared alternative)
- `ledger_event_id` (non-empty)
- terminal-event enum ∈ {`build_completed`, `build_rejected`, `build_skipped`}
- `parent_contract_id` referring to the `build_artifact_id`

**Forbidden R3-assertion guardrail** (binding matrix §5.2):
- C.4 MUST flag ANY span matching an R3-chain contract
  (`L1PlanContract`, `RouteContract`, `RetrievalPlan`,
  `FinalEvidenceContract`, `CompiledPromptArtifact`, `PromptEnvelope`,
  `SealedArtifact`, `ExitReviewPacket`, `CommitRequest`) with
  `app_name=apps_qna` as a **`FORBIDDEN_SPAN` violation**. This is a
  hard R3-vs-BTC discriminator.

**Fallback**: if `build.pack_artifact` emitter does not exist, C.4
proposes a minimal emitter spec (attribute list + suggested span name,
matching Tier-1 shape) in the C.7 attribute-hardening gap report. **No
emitter is added in Phase C.**

---

## 8. Formal-exception evidence wiring

C.5 orchestrates the B.4 + B.5 helpers:

| App | Sub-phase call | Control(s) |
|---|---|---|
| `apps_shared` | `formal_exception_evidence.collect_cc_shared_05_evidence()` | CC-SHARED-05 (B.4) |
| `apps_shared` | `negative_controls.check_apps_shared_sealed_artifact_proof_only(rows)` | CC-SHARED-03 (B.5) |
| `apps_eval` | `negative_controls.check_no_eval_of_evaluator_circularity(rows)` | CC-EVAL-01 (B.5) |
| `apps_eval` | `negative_controls.check_apps_eval_no_r3_contract_leak(rows)` | CC-EVAL-02 (B.5) |
| `apps_underwriting_ai` | `negative_controls.check_underwriting_no_r3_contract_leak(rows)` | CC-UW-02 (B.5) |
| all 3 | (manually composed — CC-EVAL-04, CC-UW-04, CC-SHARED-04 are governance-only, not runtime-observable) | governance cadence |

Evidence envelope additions for formal-exception apps:

```python
{
    "formal_exception_evidence": {
        "CC-SHARED-05": <SharedShimEvidence.to_dict()>,
        "CC-SHARED-03": <NegativeControlResult.to_dict()>,
        "CC-EVAL-01":   <NegativeControlResult.to_dict()>,
        "CC-EVAL-02":   <NegativeControlResult.to_dict()>,
        "CC-UW-02":     <NegativeControlResult.to_dict()>,
    }
}
```

Per-row details come from each helper's existing `to_dict()`. No new
schema is introduced in C.5.

---

## 9. Fail-closed rules (Phase C evidence collection)

Phase C uses the following statuses — NOT certification verdicts:

| Condition | Phase C status | Downstream (Phase D) behavior |
|---|---|---|
| All required spans present + all required attributes hardened | `EVIDENCE_COMPLETE` | Eligible for Phase D pass evaluation |
| ≥1 required span missing | `TRACE_GAP` | Phase D returns `certification = DENIED` |
| All spans present but ≥1 required attribute missing | `ATTRIBUTE_HARDENING_REQUIRED` | Phase D returns `certification = DENIED` |
| Span match ambiguous (multiple contract matches OR tied priorities) | `UNKNOWN_NEEDS_RUNTIME_RUN` | Phase D returns `certification = DENIED` |
| `CommitRequest` span observed for R3 app | `FORBIDDEN_SPAN_VIOLATION` | Phase D returns `certification = DENIED` with R3-vs-R3R4 reason |
| apps_qna emits any R3-chain contract | `FORBIDDEN_SPAN_VIOLATION` | Phase D returns `certification = DENIED` with BTC-purity reason |
| Any formal-exception CC negative-control fails | `FORMAL_EXCEPTION_VIOLATION` | Phase D returns `certification = DENIED` |
| `SharedShimEvidence.passed == False` | `CC_SHARED_05_NOT_PASSED` | Phase D blocks `FORMAL_EXCEPTION_VERIFIED` for apps_shared |

**Invariants**:
- Phase C **never** writes `runtime_certification_status` other than
  `NOT_CERTIFIED`. Any code path that tries is a Phase C bug.
- Phase C **never** promotes an app to `TRACE_OBSERVED` — that's Phase
  D's first promotable level.
- Ambiguous evidence always fails closed (no inference, no default values).

---

## 10. Testing strategy

**Narrow tests only — no live DB required**:

| Sub | Test class | Fixture |
|:---:|---|---|
| C.1 | `test_runtime_adg_query_adapter.py` | Synthetic `RuntimeADGSnapshot` dicts; no real sqlite file |
| C.2 | `test_trace_row_normalizer.py` | Synthetic `RuntimeADGNode` inputs; each of the 5 mapping priorities exercised |
| C.3 | `test_r3_evidence_extractor.py` | Synthetic row sets: full 8-span pass, missing L1, missing Retrieval (apps_rg degraded), FinalEvidenceContract UNR |
| C.4 | `test_btc_evidence_extractor.py` | apps_qna synthetic traces: 3-span pass; R3-leak variant; missing `output_pack_hash` |
| C.5 | `test_formal_exception_evidence_extractor.py` | Synthetic rows for each CC-*-0N; exercises wiring of B.4 + B.5 helpers |
| C.6 | `test_live_trace_smoke.py` | **Optional integration smoke** — gated behind `RUNTIME_CERT_SMOKE=1`; defaults to skip. Uses an existing OTel test fixture if one exists; otherwise synthetic |
| C.7 | `test_attribute_hardening_gap.py` | Reports over synthetic rows; no emitter touched |

**Allowed fixtures**:
- `system_learning/runtime_adg/snapshot.py::RuntimeADGNode` — construct directly, no I/O
- Existing test helpers in `tests/e2e/agentic_core/test_runtime_adg_e2e.py` — read-only, if they already build synthetic snapshots

**Forbidden**:
- Real-process OTel exporters (too noisy for unit tests)
- Removing the real `agentic_core` from the interpreter global state
- Modifying emitters to enable testing

---

## 11. Risks

| # | Risk | Mitigation |
|:---:|---|---|
| **R1** | Existing emitter span names differ from the design matrix's normalized cert aliases → false misses during mapping | Priority 1 (Tier-1 signal) + priority 2 (GenAI semconv) + priority 3 (accepted_span_name_patterns) precedence absorbs naming drift without requiring renames. Matrix v2 §7 already acknowledged this. |
| **R2** | Runtime-ADG schema mismatch — `RuntimeADGNode.attributes_json` is a JSON string, not a dict | Normalizer (C.2) parses it once at the boundary; downstream helpers see a dict as defined in §3.1. |
| **R3** | Overfitting the helpers to **static** grep patterns rather than live trace shape | C.6 smoke explicitly runs against live traces (single chosen app) before C.7 generalizes. C.1 tests use synthetic rows shaped like real `RuntimeADGNode` instances, not static file scrapes. |
| **R4** | Formal-exception evidence ambiguous because rows lack `code.filepath` | CC-SHARED-03 already handles this via `rows_with_unknown_source` note (B.5 design); Phase C.7 may escalate the backlog to request `code.filepath` attribute hardening on L5-ingress, UWG, and L6 emitters. |
| **R5** | Accidental certification claim in a Phase C output (e.g., a `runtime_certification_status: RUNTIME_CERTIFIED` leaking into a report) | §9 invariant pinned as a test (`test_phase_c_never_writes_RUNTIME_CERTIFIED`). Every C.6 smoke report MUST include the no-cert disclaimer at the top. |
| **R6** | Scope creep — Phase C accidentally adding a CI gate | §1 non-goals + §11 this row. The CI gate is Phase E; any proposal to add one during C.1–C.7 MUST be rejected at Author-Gate. |
| **R7** | Sub-phase interlock failures — C.3 depends on C.2's row shape being stable | C.2 ships with ≥100 tests pinning the row schema (§3.1) before C.3 begins. Row schema changes require bumping a `PHASE_C_ROW_SCHEMA_VERSION` constant — tests will flag C.3 regressions. |

---

## 12. Author-Gate decisions needed before implementation

> **v2 update (2026-04-30)**: All 9 decisions below are ✅ **APPROVED** and
> recorded in §0. The table is preserved verbatim as the as-drafted
> recommendation record; outcomes and rationale live in §0.1–§0.2.
> Any sub-phase plan (C.1 onward) citing AG-C-N decisions should link to §0.

The following decisions MUST be resolved (in an explicit Author-Gate
session, per `author-gate-enforcement.md`) before any Phase C code is
written:

| # | Decision | Recommended | Rationale |
|:---:|---|---|---|
| **AG-C-1** | Use runtime ADG (`system_learning/runtime_adg/`) as the evidence store for Phase C/D/E | ✅ Yes | ADR-074 + Phase A confirmation. Building a parallel store would be duplicative and break the "runtime bucket is a view over OTel" invariant. |
| **AG-C-2** | Approve **no** parallel evidence store | ✅ Yes | Same as AG-C-1; make it explicit. |
| **AG-C-3** | Approve the Phase C row schema in §3.1 (18 fields) | ✅ Yes | The schema is minimal and compatible with B.2/B.4/B.5. |
| **AG-C-4** | Approve **no** scanner classification changes during C.1–C.7 | ✅ Yes | B.6 standing invariant. Scanner changes belong to Phase F. |
| **AG-C-5** | Approve **no** emitter renaming during C.1–C.7 | ✅ Yes | Matrix v2 §7 already says signal-based binding handles drift. |
| **AG-C-6** | Choose the first live-trace smoke app for C.6 | **apps_research** or **apps_exec** (2-option Author-Gate) | `apps_research` is the simplest R3 app (5 R3 apps available; `apps_rg` is trickier because of its `PromptEnvelope` equivalence-group wrinkle). `apps_exec` is a fine alternative if CLI invocation is simpler. |
| **AG-C-7** | Decide whether CC-SHARED-05 env-var assertion (`AGENTIC_CORE_STACK=full`) is **required** during C.6 smoke | **Required** (recommended) | Matches B.4 option (b) "redundant evidence" posture. Trivially enforced at the smoke harness entry point. |
| **AG-C-8** | Approve the `TRACE_GAP` / `ATTRIBUTE_HARDENING_REQUIRED` / `UNKNOWN_NEEDS_RUNTIME_RUN` / `FORBIDDEN_SPAN_VIOLATION` / `FORMAL_EXCEPTION_VIOLATION` / `CC_SHARED_05_NOT_PASSED` status vocabulary in §9 | ✅ Yes | Phase D will consume these exactly; changing them later churns both phases. |
| **AG-C-9** | Approve the C.1 → C.2 → (C.3 ∥ C.4 ∥ C.5) → C.6 → C.7 ordering | ✅ Yes | Maximizes parallelism after C.2 lands while keeping foundations sequential. |

Each Author-Gate decision is its own prompt, per house style — this
plan does not resolve them.

---

## 13. Deliverables and stop conditions

**Phase C deliverables**:

1. Read-only runtime-ADG query adapter (C.1)
2. Pure trace-row normalizer (C.2)
3. Three extractors (C.3 R3, C.4 BTC, C.5 formal exception)
4. One live-trace smoke report against one app (C.6)
5. Attribute-hardening gap report across all covered emitters (C.7)

**Phase C does NOT produce**:

- Any per-app `RUNTIME_CERTIFIED` status
- Any per-app `FORMAL_EXCEPTION_VERIFIED` status
- Any CI gate
- Any scanner modification
- Any promotion workflow

**Stop conditions** (Phase C ends when ALL hold):

- C.1–C.7 sub-phase deliverables merged
- C.6 smoke report passes against the chosen app
- C.7 attribute-hardening backlog is published and linked from the
  design matrix §11 Phase table
- Every app remains `NOT_CERTIFIED` (pinned by a test in each
  sub-phase)

**After Phase C**:

- **Phase D** — certification report generator. Consumes Phase C row
  envelopes and the §9 statuses to produce `docs/reports/runtime_cert/<app>/<YYYY-Www>.md`.
  **This is the first phase where `TRACE_OBSERVED` or higher becomes writable.**
- **Phase E** — fail-closed CI gate at `ops_scripts/ci/check_runtime_certification.py` running Phase D on last-N-days traces.
- **Phase F** — scanner extension + promotion workflow updating scorecard + Notion ADR + memory.

No runtime-certification promotion occurs before Phase D/E.

---

## 14. Final statement

> **Phase C is a planning artifact.** No code has been written. No
> emitter has been modified. No scanner has changed. No CI gate has
> been added. No app has been certified. The `apps_*` cohort remains
> at its post-W14 state:
>
> - 6 apps in `APP_OVERLAY_STATIC_EVIDENCE`
> - 3 apps in `FORMAL_EXCEPTION_STATIC_EVIDENCE`
> - 0 apps in `RUNTIME_CERTIFIED`
> - 0 apps in `FORMAL_EXCEPTION_VERIFIED`
> - Every app reads `runtime_certification_status: NOT_CERTIFIED`

---

## Provenance

| Item | Value |
|---|---|
| Plan version | **v2** (Author-Gate decisions captured) |
| v1 generated | 2026-04-30 (initial planning draft) |
| v2 reconciled | 2026-04-30 (§0 added; §12 intro + Provenance updated) |
| Author-Gate status | ✅ **resolved** — all 9 decisions (AG-C-1…9) APPROVED on 2026-04-30; outcomes recorded in §0.1, AG-C-6 rationale in §0.2, scope limits in §0.3, follow-ups in §0.4 |
| Predecessor phases | A, B.1, B.2, B.3, B.4, B.5 (all complete) |
| Successor phases | D (report generator), E (CI gate), F (promotion) — blocked on Phase C |
| Files inspected for this plan | 11 |
| Files modified by this plan | 0 |
| Apps affected by this plan | 0 (read-only planning) |
