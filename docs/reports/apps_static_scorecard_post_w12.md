# `apps_*` Static Scorecard — Post-W12 Audit

**Generated**: 2026-04-30 (post-W12 migration cohort closure)
**Scanner**: `tools/analysis/apps_spine_coverage.py`
**Snapshot source**: live workspace (`python -m tools.analysis.apps_spine_coverage --json`)

> ⚠️ **CAVEAT — NO APP IS RUNTIME-CERTIFIED.** Every classification on this
> scorecard is **STATIC EVIDENCE ONLY** — derived from the manifest +
> import-graph delegation surface. It does NOT prove that the runtime
> path actually exercises every contract on every call. Runtime
> certification requires OTel-trace ingest binding contract surfaces to
> live spans, which is **out of scope for this audit and the W7–W12
> migration cohort**. The `runtime_certification_status` column is
> deliberately `NOT_CERTIFIED` for every row.

---

## Final scorecard — all 9 `apps_*`

| App | Route shape | Bucket | `manifest_present` | `claimed_routes` | `required` | `direct_imports` | `missing` | `formal_exception_reason` | `legacy_any_contract_path` | `runtime_certification_status` |
|---|---|---|:---:|---|:---:|:---:|:---:|---|:---:|:---:|
| **`apps_qna`** | `build_time_compiler` | ✅ APP_OVERLAY_STATIC_EVIDENCE | ✅ | `[build_time_compiler]` | 0 | 1 (`ValidatedRequest`) | [] | — | ❌ | NOT_CERTIFIED |
| **`apps_research`** | `R3_grounded_read` | ✅ APP_OVERLAY_STATIC_EVIDENCE | ✅ | `[R3_grounded_read]` | 8 | 8 | [] | — | ❌ | NOT_CERTIFIED |
| **`apps_exec`** | `R3_grounded_read` | ✅ APP_OVERLAY_STATIC_EVIDENCE | ✅ | `[R3_grounded_read]` | 8 | 8 | [] | — | ❌ | NOT_CERTIFIED |
| **`apps_lic`** | `R3_grounded_read` | ✅ APP_OVERLAY_STATIC_EVIDENCE | ✅ | `[R3_grounded_read]` | 8 | 8 | [] | — | ❌ | NOT_CERTIFIED |
| **`apps_rfp`** | `R3_grounded_read` | ✅ APP_OVERLAY_STATIC_EVIDENCE | ✅ | `[R3_grounded_read]` | 8 | 8 | [] | — | ❌ | NOT_CERTIFIED |
| **`apps_eval`** | `evaluator_only` | 📜 FORMAL_EXCEPTION_STATIC_EVIDENCE | ✅ | `[evaluator_only]` | 0 (empty by design) | 0 | [] | `circular_dependency` (4 CC-EVAL-* compensating controls) | ❌ | NOT_CERTIFIED |
| **`apps_underwriting_ai`** | `core_adjacent_utility` | 📜 FORMAL_EXCEPTION_STATIC_EVIDENCE | ✅ | `[core_adjacent_utility]` | 0 (empty by design) | 0 | [] | `regulatory_domain` (4 CC-UW-* compensating controls) | ❌ | NOT_CERTIFIED |
| **`apps_rg`** | (undeclared) | ✅ APP_OVERLAY_STATIC_EVIDENCE | ❌ | — | n/a | 1 (`PromptEnvelope`) | [] | — | ⚠️ **YES** | NOT_CERTIFIED |
| **`apps_shared`** | (undeclared) | ✅ APP_OVERLAY_STATIC_EVIDENCE | ❌ | — | n/a | 1 (`SealedArtifact`) | [] | — | ⚠️ **YES** | NOT_CERTIFIED |

### Cohort summary

| Bucket | Count | Apps |
|---|---:|---|
| ✅ APP_OVERLAY_STATIC_EVIDENCE — manifest-honored | 5 | `apps_qna`, `apps_research`, `apps_exec`, `apps_lic`, `apps_rfp` |
| 📜 FORMAL_EXCEPTION_STATIC_EVIDENCE — recorded charter | 2 | `apps_eval`, `apps_underwriting_ai` |
| ⚠️ Legacy any-contract path — manifest absent | 2 | `apps_rg`, `apps_shared` |
| 🟠 PARTIAL_SPINE_STATIC_ONLY | 0 | (cohort closed) |
| 🔴 APP_STANDALONE_FORBIDDEN | 0 | — |
| ❔ UNKNOWN_NEEDS_RUNTIME_TRACE | 0 | — |

---

## §1. `apps_rg` audit

### Files inspected (4 of 5)

1. `apps_rg/integrations/governed_rg_run.py` — runner header (`GovernedRgRun(GovernedAppRunner)`, imports `ResumeRequest`, `GovernedAppRunRecord`)
2. `apps_rg/integrations/` directory listing (confirms full R3 family shape: `governed_rg_run.py`, `rg_ingress_runner.py`, `execution_adapter.py`, `observability_adapter.py`)
3. `apps_rg/utils/anthropic_rag_entrypoint.py` — the file importing `PromptEnvelope` from `agentic_core.knowledge.retrieval.prompt_envelope`
4. `apps_rg/` package root listing (entrypoints: `__main__.py` + `bootstrap_runtime.py` + `scripts/`)

### Likely route shape

**`R3_grounded_read`** — confidence **high (0.88)**. Same family shape as `apps_research` / `apps_exec` / `apps_lic` / `apps_rfp`:

- `GovernedRgRun(GovernedAppRunner)` subclass — uses the shared L1→L0→C0→L2→L5+L6 substrate
- Standard family layout: `governed_rg_run.py`, `rg_ingress_runner.py`, `execution_adapter.py`, `observability_adapter.py`
- Required input: `ResumeRequest` from `apps_rg.types.rg_types` (resume-generation app)
- No durable-write surface visible in the audited files (no `CommitRequest`, no `StateDiffCandidate`); a focused pre-migration audit (mirror of the apps_lic / apps_rfp audits) would close to 0.95+ before migration.

### Is the current `PromptEnvelope` import a real handoff or type-only?

**Real handoff.** `apps_rg/utils/anthropic_rag_entrypoint.py:48` imports `PromptEnvelope` from `agentic_core.knowledge.retrieval.prompt_envelope` and **consumes its typed fields at runtime**:

- `build_anthropic_rag_payload(envelope: PromptEnvelope, query: str, ...) -> AnthropicRagPayload` builds an Anthropic Messages API request from a completed `PromptEnvelope`
- It reads `envelope.abstain_recommended`, `envelope.envelope_id`, `envelope.contradiction_status` and other typed fields
- It raises `AbstainRecommendedError` based on envelope state

This is the **single load-bearing R3 contract** apps_rg currently surfaces directly. The other 7 R3 contracts are reached transitively via `apps_shared.integrations.governed_app_runner.GovernedAppRunner` (the same situation `apps_research` / `apps_exec` / `apps_lic` / `apps_rfp` were in pre-migration).

### Should a direct manifest be added?

**Yes — recommended, but not in this audit pass.** Adding `apps_rg/spine_manifest.yaml` + `apps_rg/integrations/spine_handoff.py` mirroring the apps_research W9 / apps_rfp W12 shape would:

- Promote `apps_rg` from the legacy any-contract path to manifest-honored APP_OVERLAY_STATIC_EVIDENCE for `R3_grounded_read`
- Surface all 8 R3 contracts as direct imports (currently 1 of 8: `PromptEnvelope`)
- Eliminate the legacy-path warning (`"declare a manifest to enable route-typed validation"`)
- Match the rest of the R3 cohort, reducing future-maintainer cognitive load

### Is runtime trace needed before changing classification?

**No** — same standard as the W9–W12 R3 migrations: the static-surfacing migration is reversible, behavior-preserving, and does not claim runtime certification. Runtime-trace evidence is what moves an app from APP_OVERLAY_STATIC_EVIDENCE to a future runtime-certified bucket; that promotion is out of scope for this audit.

### Recommended next step (do not perform without authorization)

**`apps_rg` W13 R3 static-surfacing migration**, modeled on apps_rfp W12:

1. Pre-migration audit (mirror of apps_lic / apps_rfp audits): confirm zero matches in `apps_rg/` for `CommitRequest`, `commit_request`, `StateDiffCandidate`, `proposed_state_diff`, `MutationIntent`, `durable_write`, `write_gateway`, plus rule out resume-submission / portal-publication paths. **apps_rg deals with résumés — verify there is no LinkedIn-publish or applicant-tracking-system-write surface** (analogous to the apps_rfp portal-submission audit).
2. Add `apps_rg/spine_manifest.yaml` declaring `claimed_routes: [R3_grounded_read]` with an explicit note recording (a) the existing `PromptEnvelope` import, (b) absence of any durable-write surface, (c) HITL posture (verify the `GovernedRgRun` HITL flag).
3. Add `apps_rg/integrations/spine_handoff.py` mirroring apps_rfp W12 with the 8 R3 imports + `R3_CONTRACT_SURFACE` + `validate_rg_r3_contract_surface` + `build_rg_r3_handoff_metadata` + `run_rg_via_spine` thin delegate. **`CommitRequest` intentionally not imported.**
4. Add ~8 tests mirroring the apps_rfp W12 set.

Estimated scope: ~50 lines YAML + ~250 lines Python + ~150 lines tests. Same blast radius as apps_rfp W12.

---

## §2. `apps_shared` audit

### Files inspected (4 of 5)

1. `apps_shared/` package root listing (confirms it has `RUNBOOK.md`, `SLO.md`, `SVP_ENGINEERING_REVIEW.md` — treated like an app, but with library-style internals: `_compat/`, `adapters/`, `integrations/`, `mixins/`, `proof/`)
2. `apps_shared/integrations/governed_app_runner.py` (header) — confirms `GovernedAppRunner` and `GovernedAppRunRecord` are defined HERE, not in any individual app. This is the **shared substrate base class** that all 4 R3 apps (`apps_research`, `apps_exec`, `apps_lic`, `apps_rfp`) subclass.
3. `apps_shared/proof/scenario_base.py` (line 971 region) — the file importing `SealedArtifact`. The import lives inside a `proof` harness method (`evaluate_exit`), inside a try-block, used to construct test-fixture `SealedArtifact(**sealed_kwargs)` instances for the proof scenario. Also imports `BudgetEnvelope` and `ExitEvalPolicy` from the same module. This is a **test/proof-harness use**, not production runtime.
4. `apps_shared/integrations/app_registry.py` (header) — defines `APP_REGISTRY`, the SSOT registry of governed-app adoption status across `apps_*`. Tracks `GOVERNED` / `CANDIDATE` / `EXCEPTION` per app. **This file's purpose is to track OTHER apps**, not to run any app itself.

### Likely classification

**`core_adjacent_utility`** (formal exception) — confidence **high (0.90)**. `apps_shared` is structurally a **shared library surface**, not an app:

- It defines the `GovernedAppRunner` base class consumed by 4 R3 apps
- It defines the `app_registry` SSOT that classifies the rest of the cohort
- It defines `runtime_hitl_integration` that 2 apps opt into (apps_lic, apps_exec)
- It defines `proof/scenario_base.py` and `proof/runtime_drivers/` — test/audit harnesses
- It does NOT have a `__main__.py`, does NOT have its own runtime entrypoint, does NOT subclass `GovernedAppRunner` (it DEFINES it)
- The single canonical contract import (`SealedArtifact`) is inside a `proof` harness, not production code

This is the same architectural shape as `apps_underwriting_ai`: a library surface that **provides** governance primitives rather than **consuming** them. The honest classification is `core_adjacent_utility` with a formal-exception charter.

### Is a formal exception manifest appropriate?

**Yes — recommended.** A formal-exception manifest at `apps_shared/spine_manifest.yaml` would:

- Declare `claimed_routes: [core_adjacent_utility]`
- Declare an `exception:` block with:
  - `reason_code: shared_library_surface` (new) OR `infrastructure_substrate`
  - `compensating_controls`: e.g., "CC-SHARED-01: provides the GovernedAppRunner substrate consumed by all R3 apps", "CC-SHARED-02: provides the APP_REGISTRY single-source-of-truth for governance status", "CC-SHARED-03: SealedArtifact import is in proof/scenario_base.py harness only, not production runtime", "CC-SHARED-04: reviewed quarterly by the platform team"
  - `blocked_layers: []` (apps_shared HAS to touch many layers — it's the substrate; this is a different exception shape than apps_eval/apps_uw)
  - `safe_layers: [substrate, proof_harness]`
  - `review_cadence: quarterly`
  - `owner: platform team`

Note: `shared_library_surface` (or `infrastructure_substrate`) would be a **new** `reason_code` value not currently used by any other manifest. It's a minor extension that doesn't broaden scanner semantics — the scanner already accepts arbitrary `reason_code` strings; the test surface just asserts non-empty.

### Should `apps_shared` be excluded from the apps runtime cohort?

**Soft yes** — the cleaner architectural truth is that `apps_shared` is **infrastructure shared by apps**, not an app itself. Two paths:

| Option | Pros | Cons |
|---|---|---|
| **A. Formal-exception manifest** (`core_adjacent_utility` + `shared_library_surface` reason_code) | No scanner code change. Documents the rationale visibly. Matches the apps_underwriting_ai pattern. Reversible. | Still listed in the apps_* scoreboard (which is structurally accurate even if conceptually misleading). |
| **B. Scanner exclusion** (skip `apps_shared` from the audited set) | Cleaner conceptual truth. Removes apps_shared from the scoreboard. | Requires scanner code change (broadening semantics). Loses the ability to detect drift if apps_shared accidentally starts behaving like an app. The "no scanner weakening" hard constraint of this audit applies. |

**Recommendation: Option A.** The formal-exception manifest is the same shape that worked for apps_underwriting_ai (also a library surface that publishes governance primitives) and avoids any scanner change. The existence of `apps_shared/SVP_ENGINEERING_REVIEW.md`, `apps_shared/RUNBOOK.md`, and `apps_shared/SLO.md` (all treated as if it were an app) suggests the team has historically managed apps_shared on app-style cadences, which Option A preserves.

### Recommended next step (do not perform without authorization)

**`apps_shared` W14 formal-exception manifest pass**, modeled on the apps_underwriting_ai W8 work:

1. Add `apps_shared/spine_manifest.yaml` declaring `claimed_routes: [core_adjacent_utility]` + `exception` block with `reason_code: shared_library_surface` (or similar, after a quick naming review) + 4 compensating controls + quarterly review cadence.
2. Add ~3 tests asserting `apps_shared` classifies as `FORMAL_EXCEPTION_STATIC_EVIDENCE` with the expected reason code.
3. **Do not add a `spine_handoff.py`** — apps_shared is a library, not a runtime app. The 8 R3 contracts already flow through it as the substrate; making it import them directly would understate its role (it's the HOST of the substrate, not a consumer).
4. Optional secondary cleanup: investigate `apps_shared/_compat/` (visible in the directory listing) — likely a vestigial shim similar to the now-retired `apps_rfp/_compat/lifecycle_trace.py`. If so, retire it as a separate precursor PR before the manifest lands.

Estimated scope: ~80 lines YAML + ~80 lines tests. Smaller than W12 because no spine_handoff is needed.

---

## §3. Runtime certification — explicit prerequisites

**No app on this scorecard is runtime-certified.** Every `runtime_certification_status` cell reads `NOT_CERTIFIED`. To move any app from APP_OVERLAY_STATIC_EVIDENCE (or FORMAL_EXCEPTION_STATIC_EVIDENCE) to a future runtime-certified bucket, the following must hold:

### Prerequisites for any runtime-certification work

1. **OTel-trace ingest pipeline operational** — runtime spans must be reliably collected, persisted, and queryable. The `otel_mcp` and `runtime_adg` infrastructure must be green.
2. **Per-contract span coverage** — every contract in an app's `manifest_required_contracts` must have a corresponding OTel span emitted at the runtime touch-point. For R3 apps, this means 8 spans per request: intake → plan → route → retrieve → evidence → prompt → seal → exit.
3. **Span-to-contract binding** — a deterministic mapping from `<contract_name, app_name>` to a stable span name + attribute set, enforced by a runtime-binding gate. Drift between the manifest's required-contract list and the actual span emissions must be detectable.
4. **Sustained empirical coverage** — for a defined evaluation window (suggested: ≥ 100 successful runs across a representative request distribution), every per-contract span must fire on every request. Coverage gaps must be reported per-contract per-app.
5. **Negative-evidence harness** — for formal-exception apps (`apps_eval`, `apps_underwriting_ai`, future `apps_shared`), the runtime-cert work must specifically VERIFY THE COMPENSATING CONTROLS, not the route's empty contract set. This is a different test shape from R3 cert.
6. **A new bucket** — the scanner needs a bucket (e.g., `RUNTIME_CERTIFIED`) distinct from `APP_OVERLAY_STATIC_EVIDENCE`, with explicit evidence requirements. Until that bucket exists in `tools/analysis/apps_spine_coverage.py`, no app can claim runtime certification, even informally.
7. **Fail-closed CI gate** — runtime-cert promotion must be gated by a CI check that runs the cert harness, not by a developer claiming "looks fine to me". Same enforcement-tier pattern as the existing W7–W12 manifest gates.

### What this audit does NOT change

- No app moves from STATIC to runtime-certified
- No new manifest, spine_handoff, or test was authored
- No scanner code was modified
- No `_compat/` cleanup was performed (apps_shared/_compat/ remains for a future precursor pass)
- No CommitRequest was added anywhere
- No app's runtime behavior was altered

---

## §4. Provenance

| Item | Value |
|---|---|
| Scanner version | `tools/analysis/apps_spine_coverage.py` HEAD as of 2026-04-30 |
| Snapshot timestamp | 2026-04-30 |
| Last migration commit | `8e5f1ead4f` (apps_rfp W12) |
| Cohort first commit | `7797ce77f3` (apps_qna W7) |
| Total apps_* in scope | 9 |
| Migrated apps (W7–W12) | 5 |
| Formal exceptions (W8) | 2 |
| Legacy any-contract path | 2 (audited above) |
| Manifests authored | 7 |
| Spine-handoff modules | 5 (`apps_qna`, `apps_research`, `apps_exec`, `apps_lic`, `apps_rfp`) |
| Total tests covering the cohort | 59 (in `tests/unit/tools/analysis/test_apps_spine_coverage.py`) |

---

## §5. Cohort-wide invariants (preserved by this audit)

| Invariant | Status |
|---|:---:|
| `manifest_missing_contracts == []` for every manifest-honored app | ✅ |
| Zero apps in `PARTIAL_SPINE_STATIC_ONLY` | ✅ |
| Zero apps in `APP_STANDALONE_FORBIDDEN` | ✅ |
| Zero apps in `UNKNOWN_NEEDS_RUNTIME_TRACE` | ✅ |
| Every R3 app has 8 direct contract imports | ✅ |
| Every R3 app declares zero CommitRequest in `distinct_contracts` | ✅ |
| Every R3R4_managed_workflow declaration | ❌ (none — by design; no app has a proven durable-write surface in the cohort) |
| Every formal-exception app has `reason_code` + ≥ 1 `compensating_controls` | ✅ |
| Every static evidence claim explicitly disclaims runtime certification | ✅ |
