# `apps_*` Static Scorecard — Post-W14 (Cohort Closure)

**Generated**: 2026-04-30 (post-W14 migration cohort closure)
**Scanner**: `tools/analysis/apps_spine_coverage.py`
**Snapshot source**: live workspace (`python -m tools.analysis.apps_spine_coverage --json`)

> ⚠️ **CAVEAT — NO APP IS RUNTIME-CERTIFIED.** Every classification
> on this scorecard is **STATIC EVIDENCE ONLY** — derived from the
> manifest + import-graph delegation surface. It does NOT prove that
> the runtime path actually exercises every contract on every call.
> Runtime certification requires OTel-trace ingest binding contract
> surfaces to live spans, which is **out of scope for the W7–W14
> migration cohort**. The `runtime_certification_status` column is
> deliberately `NOT_CERTIFIED` for every row.

---

## Final scorecard — all 9 `apps_*`, zero legacy paths

| App | Route shape | Bucket | `manifest_present` | `claimed_routes` | `required` | `direct_imports` | `missing` | `formal_exception_reason` | `legacy_any_contract_path` | `runtime_certification_status` |
|---|---|---|:---:|---|:---:|:---:|:---:|---|:---:|:---:|
| **`apps_qna`** | `build_time_compiler` | ✅ APP_OVERLAY_STATIC_EVIDENCE | ✅ | `[build_time_compiler]` | 0 | 1 (`ValidatedRequest`) | [] | — | ❌ | NOT_CERTIFIED |
| **`apps_research`** | `R3_grounded_read` | ✅ APP_OVERLAY_STATIC_EVIDENCE | ✅ | `[R3_grounded_read]` | 8 | 8 | [] | — | ❌ | NOT_CERTIFIED |
| **`apps_exec`** | `R3_grounded_read` | ✅ APP_OVERLAY_STATIC_EVIDENCE | ✅ | `[R3_grounded_read]` | 8 | 8 | [] | — | ❌ | NOT_CERTIFIED |
| **`apps_lic`** | `R3_grounded_read` | ✅ APP_OVERLAY_STATIC_EVIDENCE | ✅ | `[R3_grounded_read]` | 8 | 8 | [] | — | ❌ | NOT_CERTIFIED |
| **`apps_rfp`** | `R3_grounded_read` | ✅ APP_OVERLAY_STATIC_EVIDENCE | ✅ | `[R3_grounded_read]` | 8 | 8 | [] | — | ❌ | NOT_CERTIFIED |
| **`apps_rg`** ⭐ | `R3_grounded_read` | ✅ APP_OVERLAY_STATIC_EVIDENCE | ✅ | `[R3_grounded_read]` | 8 | **9** (8 + preserved `PromptEnvelope`) | [] | — | ❌ | NOT_CERTIFIED |
| **`apps_eval`** | `evaluator_only` | 📜 FORMAL_EXCEPTION_STATIC_EVIDENCE | ✅ | `[evaluator_only]` | 0 (empty by design) | 0 | [] | `circular_dependency` (4 CC-EVAL-* compensating controls) | ❌ | NOT_CERTIFIED |
| **`apps_underwriting_ai`** | `core_adjacent_utility` | 📜 FORMAL_EXCEPTION_STATIC_EVIDENCE | ✅ | `[core_adjacent_utility]` | 0 (empty by design) | 0 | [] | `regulatory_domain` (4 CC-UW-* compensating controls) | ❌ | NOT_CERTIFIED |
| **`apps_shared`** ⭐ | `core_adjacent_utility` | 📜 FORMAL_EXCEPTION_STATIC_EVIDENCE | ✅ | `[core_adjacent_utility]` | 0 (empty by design) | 1 (`SealedArtifact`, proof-harness only) | [] | `shared_library_surface` (4 CC-SHARED-* compensating controls) | ❌ | NOT_CERTIFIED |

⭐ = new / changed since post-W12

### Cohort summary

| Bucket | Count | Apps |
|---|---:|---|
| ✅ APP_OVERLAY_STATIC_EVIDENCE — manifest-honored | **6** | `apps_qna`, `apps_research`, `apps_exec`, `apps_lic`, `apps_rfp`, `apps_rg` |
| 📜 FORMAL_EXCEPTION_STATIC_EVIDENCE — recorded charter | **3** | `apps_eval`, `apps_underwriting_ai`, `apps_shared` |
| 🟠 PARTIAL_SPINE_STATIC_ONLY | **0** | — |
| 🔴 APP_STANDALONE_FORBIDDEN | **0** | — |
| ❔ UNKNOWN_NEEDS_RUNTIME_TRACE | **0** | — |
| ⚠️ Legacy any-contract path | **0** ← was 2 at post-W12 | — |

**The cohort is fully closed.** Every classification is backed by an
explicit `spine_manifest.yaml` — either a route declaration with all
required contracts surfaced, or a formal-exception charter with
`reason_code` and compensating controls.

---

## What changed since post-W12

### 1. `apps_rg` — legacy any-contract path → manifest-honored `R3_grounded_read` (W13)

- **Before W13**: no manifest; on the legacy any-contract path; scanner detected 1 canonical contract (`PromptEnvelope` from `apps_rg/utils/anthropic_rag_entrypoint.py:48`).
- **After W13**: `apps_rg/spine_manifest.yaml` declares `claimed_routes: [R3_grounded_read]`; `apps_rg/integrations/spine_handoff.py` directly imports the 8 canonical R3 contracts (`ValidatedRequest`, `L1PlanContract`, `RouteContract`, `RetrievalPlan`, `FinalEvidenceContract`, `CompiledPromptArtifact`, `SealedArtifact`, `ExitReviewPacket`). Total `contract_count` is **9** because the pre-existing `PromptEnvelope` consumer in `apps_rg/utils/anthropic_rag_entrypoint.py` was **preserved unchanged** — the migration adds `CompiledPromptArtifact` (canonical name) via the new spine_handoff while keeping `PromptEnvelope` (equivalent) intact as the real Anthropic API payload-builder handoff.
- **`CommitRequest` intentionally not imported** — pre-migration audit found zero durable-write surface (ATS scoring is an output metric, LinkedIn references are read-side pattern-mining, `ml_cache_ats_compatibility` is cross-run meta-learning cache, `generated_resume_*.json` files are local artifacts). Adding `CommitRequest` would be contract theater.
- **HITL posture unchanged**: `GovernedRgRun` does not declare `HITL_ENABLED` (defaults False). Matches apps_research / apps_rfp; weaker than apps_lic / apps_exec. HITL is orthogonal to route shape.
- **Git reference**: commit `0812a51` (shared with W14).

### 2. `apps_shared` — legacy any-contract path → `FORMAL_EXCEPTION_STATIC_EVIDENCE` (W14)

- **Before W14**: no manifest; on the legacy any-contract path; scanner detected 1 canonical contract (`SealedArtifact` at `apps_shared/proof/scenario_base.py:971` — proof-harness use only, not production runtime).
- **After W14**: `apps_shared/spine_manifest.yaml` declares `claimed_routes: [core_adjacent_utility]` with an explicit `exception` block carrying `reason_code: shared_library_surface` (a **new** reason code distinct from apps_underwriting_ai's `regulatory_domain`), 4 compensating controls, `review_cadence: quarterly`, `safe_layers: [substrate, proof_harness, registry]`, and `blocked_layers: []` (apps_shared HAS to touch many layers — it IS the substrate).
- **No `spine_handoff.py` was created for apps_shared**, and this was intentional. apps_shared is the **host** of the `GovernedAppRunner` substrate (it *defines* `GovernedAppRunner`, `GovernedAppRunRecord`, `APP_REGISTRY`, `runtime_hitl_integration`), not a *consumer* of it. Making it import the 8 R3 contracts directly would understate its role and conflict with the formal-exception charter. The empty required-contract set is the architecturally honest classification.
- **`apps_shared/_compat/agentic_core_shim.py` was intentionally NOT touched.** The shim is materially heavier than the retired `apps_rfp/_compat/lifecycle_trace.py` was (5,649 bytes vs 60 lines; it modifies the `agentic_core` import surface at package load via `_install_agentic_core_shim()`). Retiring or modifying it requires a separate focused audit of (a) what `install()` actually does, (b) which `agentic_core` consumers depend on the post-install surface, (c) whether retirement requires touching `agentic_core` itself rather than just apps_shared. This audit is out of scope for W14; the manifest pass is independent of the shim's fate.
- **Git reference**: commit `0812a51` (shared with W13).

### 3. Cohort-wide consequence

The **legacy any-contract path count went from 2 to 0**. Every `apps_*`
classification now flows through an explicit manifest — either a
route declaration (6 apps) or a formal-exception charter (3 apps).
This was the stated goal of the W7–W14 migration arc.

The scanner was **not modified** in W13 or W14. No scanner code
change was required because:

- `R3_grounded_read` was already a recognized route type (W9 precedent)
- `core_adjacent_utility` was already a recognized route type (W8 precedent)
- The `reason_code` field accepts free-form strings, so adding
  `shared_library_surface` required no scanner code change

---

## Runtime certification remains future work

**No app on this scorecard is runtime-certified.** Every
`runtime_certification_status` cell reads `NOT_CERTIFIED`. To move
any app from APP_OVERLAY_STATIC_EVIDENCE (or
FORMAL_EXCEPTION_STATIC_EVIDENCE) to a future runtime-certified
bucket, **all seven** prerequisites below must hold:

| # | Prerequisite | Description |
|:---:|---|---|
| **1** | OTel-trace ingest operational | Runtime spans must be reliably collected, persisted, and queryable. The `otel_mcp` and runtime-ADG infrastructure must be green and producing per-request trace data. |
| **2** | Per-contract span coverage | Every contract in an app's `manifest_required_contracts` must have a corresponding OTel span emitted at the runtime touch-point. For R3 apps: 8 spans per request (intake → plan → route → retrieve → evidence → prompt → seal → exit). |
| **3** | Span-to-contract binding | A deterministic mapping from `<contract_name, app_name>` to a stable span name + attribute set, enforced by a runtime-binding gate. Drift between the manifest's required-contract list and the actual span emissions must be detectable. |
| **4** | Sustained empirical coverage | For a defined evaluation window (suggested: ≥ 100 successful runs across a representative request distribution), every per-contract span must fire on every request. Coverage gaps must be reported per-contract per-app. |
| **5** | Negative-evidence harness for formal exceptions | For the 3 formal-exception apps (`apps_eval`, `apps_underwriting_ai`, `apps_shared`), the runtime-cert work must specifically **verify the compensating controls**, not the route's empty contract set. This is a different test shape from R3 cert and requires per-exception test modules: CC-EVAL-* checks the eval-platform circularity bypass path; CC-UW-* checks the underwriting-ai regulatory-domain governance protocol; CC-SHARED-01..04 check substrate production + registry SSOT + proof-harness segregation + quarterly review compliance. |
| **6** | `RUNTIME_CERTIFIED` scanner bucket | A new runtime-mode bucket in `tools/analysis/apps_spine_coverage.py` distinct from `APP_OVERLAY_STATIC_EVIDENCE` and `FORMAL_EXCEPTION_STATIC_EVIDENCE`, with explicit evidence requirements tied to OTel data, not just source-level imports. Until that bucket exists, no app can claim runtime certification — even informally. |
| **7** | Fail-closed CI gate | Runtime-cert promotion must be gated by a CI check that runs the cert harness, not by a developer claiming "looks fine to me". Same enforcement-tier pattern as the existing W7–W14 manifest gates (`ops_scripts/ci/check_apps_spine_coverage.py`). |

Until these prerequisites are met, the accurate classification ceiling
for every app in this cohort is **static evidence only**. Any claim
otherwise would be contract theater and a constitutional violation of
§22 (graph-layer evidence required) and §29 (closed-loop evidence
required).

---

## Provenance

| Item | Value |
|---|---|
| Scanner version | `tools/analysis/apps_spine_coverage.py` HEAD as of 2026-04-30 |
| Snapshot timestamp | 2026-04-30 |
| Most recent cohort commit | `0812a51` (W13/W14 — cohort closure) |
| Prior cohort commit | `8e5f1ea` (W12 — apps_rfp) |
| First cohort commit | `7797ce7` (W7 — apps_qna) |
| Total apps_* in scope | 9 |
| Manifest-honored apps | 9 (100%) |
| Legacy any-contract-path apps | 0 |
| Formal-exception apps | 3 (apps_eval, apps_underwriting_ai, apps_shared) |
| R3_grounded_read apps | 5 (apps_research, apps_exec, apps_lic, apps_rfp, apps_rg) |
| build_time_compiler apps | 1 (apps_qna) |
| core_adjacent_utility apps | 2 (apps_underwriting_ai, apps_shared) |
| evaluator_only apps | 1 (apps_eval) |
| Spine-handoff modules in cohort | 5 (`apps_qna`, `apps_research`, `apps_exec`, `apps_lic`, `apps_rfp`, `apps_rg`) — 6 in total; apps_shared has none by design |
| Total tests covering the cohort | **76** (in `tests/unit/tools/analysis/test_apps_spine_coverage.py`) |
| Test pass rate | **76/76 (100%)** |

---

## Cohort-wide invariants (all green after W14)

| Invariant | Status |
|---|:---:|
| `manifest_missing_contracts == []` for every manifest-honored app | ✅ |
| Zero apps in `PARTIAL_SPINE_STATIC_ONLY` | ✅ |
| Zero apps in `APP_STANDALONE_FORBIDDEN` | ✅ |
| Zero apps in `UNKNOWN_NEEDS_RUNTIME_TRACE` | ✅ |
| **Zero apps on the legacy any-contract path** | ✅ **(new at W14)** |
| Every R3 app has ≥ 8 direct contract imports | ✅ |
| Every R3 app declares zero `CommitRequest` in `distinct_contracts` | ✅ |
| Zero `R3R4_managed_workflow` declarations in the cohort | ✅ (no app has a proven durable-write surface) |
| Every formal-exception app has `reason_code` + ≥ 4 `compensating_controls` | ✅ |
| Every static-evidence claim explicitly disclaims runtime certification | ✅ |
| apps_rg `PromptEnvelope` import preserved in `utils/anthropic_rag_entrypoint.py` | ✅ (regression-prevention test active) |
| apps_shared has no `spine_handoff.py` (substrate host, not consumer) | ✅ (regression-prevention test active) |
| apps_shared `_compat/agentic_core_shim.py` not modified | ✅ (deferred to separate audit) |
| Scanner code not modified in W13 or W14 | ✅ (no scanner weakening) |

---

## Next natural workstreams (out of scope for this report)

1. **apps_shared `_compat/agentic_core_shim.py` audit** — deep-inspect
   what `install()` does, identify the `agentic_core` consumers that
   depend on the post-install surface, decide whether retirement is
   possible and what the blast radius would be. If yes, ship as a
   focused precursor PR (mirror the apps_rfp `_compat` retirement
   shape but with wider testing). If no, document why it remains.
2. **Runtime-certification program** — stand up the 7 prerequisites
   listed above. This is a multi-wave effort touching OTel
   infrastructure, `tools/analysis/apps_spine_coverage.py`, and
   per-app cert harnesses. Start with the easiest app (apps_qna at
   `build_time_compiler` has the smallest contract surface) to
   validate the harness shape before tackling the 5 R3 apps.
3. **Formal-exception review automation** — set up calendar reminders
   (or a Notion cron / CI check) that fires on the `review_cadence`
   of each formal-exception manifest: annual for apps_eval and
   apps_underwriting_ai, quarterly for apps_shared.
