---
plan_id: l7-auditability-overlap-cleanup-4f8c2d
plan_type: platform_core_change
touches_agentic_core: true
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: "PENDING: required before execution touches agentic_core runtime or L7 contracts"
dod_exempt: false
---

# L7 auditability overlap cleanup

Harden the artifact and evidence boundary between `agentic_core` L7 audit surfaces and `apps_rg` section-lane evidence without redesigning the runtime.

> **plan_id discipline:** `plan_id` = filename stem `l7-auditability-overlap-cleanup-4f8c2d`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-06-07

PLAN_CREATED: slug=l7-auditability-overlap-cleanup-4f8c2d path=.cursor/plans/l7-auditability-overlap-cleanup-4f8c2d.md status=Not Started

---

## Context (SCQA)

- **Situation** - The repo already separates the integrated `agentic_core` spine from `apps_rg` product and section evidence. Core owns canonical L7 audit artifacts such as `agentic_core_how_trace.json`, `agentic_core_l7_route_family_coverage.json`, `agentic_core_spine_proof.json`, and `integrated_runtime_artifact_manifest.json`. `apps_rg` owns product recipe outputs, section audit packages, X2 gate outputs, and app-domain evidence.
- **Complication** - Some compatibility aliases and section-lane filenames overlap with core names, which makes otherwise-valid refs-only behavior harder to audit. A reader can confuse normalized core projection inputs or app shims for independent app-produced L7 proof.
- **Question** - How do we make the artifact ownership boundary auditable, regression-resistant, and obvious to humans without redesigning the runtime?
- **Answer** - Freeze the ownership decision first, add explicit provenance to core aliases, harden section L7 trust classification, add negative-control guardrails, clarify evidence-package and bundle-index roles, then dual-write app-scoped section names before any legacy cleanup.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.1-W0.2 | Baseline ownership decision record | ~4k | Existing repo direction is refs-only for section L7 binding | TODO | `docs/architecture/apps_rg_l7_artifact_ownership.md` exists with artifact-owner table |
| W1 | W1.1-W1.3 | Core compatibility alias provenance | ~8k | Alias payloads are generated in integrated spine entrypoint | TODO | Every L7 projection alias identifies itself as core-owned compatibility input |
| W3 | W3.1-W3.3 | Section L7 trust firewall | ~9k | Binding manifest remains the authority for section refs | TODO | Fake local core L7 artifacts from `apps_rg` classify as drift/untrusted |
| W6 | W6.1-W6.3 | Negative-control ownership verifier | ~10k | Contract tests can cover representative fake artifacts | TODO | CI/test guard fails on shadow L7 emission or overclaiming proof |
| W4 | W4.1-W4.2 | Section evidence package entrypoint | ~6k | `evidence_package_index.json` remains section audit entrypoint | TODO | Section package explicitly denies core L7 and 99 proof authority |
| W5 | W5.1-W5.2 | Run bundle role-label cleanup | ~5k | `RUN_BUNDLE_INDEX.json` is catalog/index only | TODO | Role labels are refs/catalog labels, not proof authority labels |
| W2 | W2.1-W2.4 | App-scoped section shim dual-write | ~12k | Dual-write is safer than immediate rename | TODO | Indexes prefer app-scoped names while legacy reads continue |
| W7 | W7.1-W7.2 | Legacy shim cleanup and migration | ~6k | Only after dual-write stability is proven | TODO | Ambiguous section shim names stop being written by default |
| W8 | W8.1-W8.3 | End-to-end proof run and receipt | ~8k | Representative integrated and section runs are available | TODO | Final certification receipt records all boundary invariants true |

### Phase Progress

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0.1 | Freeze artifact ownership table | `docs/architecture/apps_rg_l7_artifact_ownership.md` | Establishes human-readable authority before code edits | ~2k | TODO |
| W0.2 | Baseline relevant code paths | `agentic_core/L7_auditability/**`, `agentic_core/runtime/entrypoints/integrated_single_action_spine_run.py`, `apps_rg/runtime/**`, contract tests | Requires ADG/blast-radius confirmation before execution | ~2k | TODO |
| W1.1 | Add alias provenance envelope fields | `agentic_core/runtime/entrypoints/integrated_single_action_spine_run.py` | Avoids apps/core authority ambiguity | ~3k | TODO |
| W1.2 | Cover all compatibility aliases | Runtime identity, L1 plan, route, bypass, exhaust, trace aliases | Must avoid changing canonical artifact semantics | ~2k | TODO |
| W1.3 | Add alias provenance tests | `tests/_apps_contract/test_integrated_l7_alias_provenance.py` | Need strong negative assertions against app authority claims | ~3k | TODO |
| W3.1 | Enforce core L7 producer trust | `apps_rg/runtime/section_l7_binding_manifest.py` | Local fake files must not become trusted refs | ~3k | TODO |
| W3.2 | Tighten external-ref locality rules | Binding manifest + tests | Verified external refs should not have copied local core paths | ~2k | TODO |
| W3.3 | Add trust firewall tests | `tests/_apps_contract/test_section_l7_binding_contracts.py` | Must prevent product certification upgrades through section binding | ~4k | TODO |
| W6.1 | Implement ownership verifier | `tools/cert/verify_apps_rg_l7_ownership_boundary.py` | Verifier must inspect artifacts without inventing new proof semantics | ~4k | TODO |
| W6.2 | Add negative-control tests | `tests/_apps_contract/test_apps_rg_l7_ownership_boundary.py`, namespace/no-shadow tests | Fake artifacts need realistic fixture shapes | ~4k | TODO |
| W6.3 | Wire scoped CI/check command | Existing contract test path or cert tooling | Avoid broad governance CI churn | ~2k | TODO |
| W4.1 | Make evidence package role explicit | `apps_rg/runtime/section_evidence_package.py` | Entry point must be canonical for section only | ~3k | TODO |
| W4.2 | Preserve and centralize non-claims | Evidence package tests/docs | Durable write claims require UWG/L4 evidence | ~3k | TODO |
| W5.1 | Rename integrated bundle roles | `apps_rg/runtime/run_bundle_index.py` | Labels must say ref/catalog, not proof authority | ~2k | TODO |
| W5.2 | Rename lane bundle roles | Bundle index tests | X2 is not 00C; section proof bundle is not 99 proof | ~3k | TODO |
| W2.1 | Add preferred app-scoped shim names | `apps_rg/runtime/section_binding_taxonomy.py`, section lane writers | Dual-write must not break existing readers | ~4k | TODO |
| W2.2 | Update indexes to prefer new names | `run_bundle_index.py`, `section_evidence_package.py` | Legacy compatibility remains for one release window | ~3k | TODO |
| W2.3 | Update section tests | `tests/unit/apps_rg/**`, `tests/_apps_contract/**` | Need assertions for new preferred names and legacy reads | ~3k | TODO |
| W2.4 | Document legacy migration window | Runtime docs/runbooks as discovered | Do not rename core L7 artifacts | ~2k | TODO |
| W7.1 | Stop default legacy shim writes | Section lane writers | Requires prior dual-write proof | ~3k | TODO |
| W7.2 | Keep read compatibility and docs | Readers/docs/tests | Migration window must be explicit | ~3k | TODO |
| W8.1 | Run integrated and section proof matrix | Representative `apps_rg` integrated and section runs | Requires real artifact outputs | ~3k | TODO |
| W8.2 | Validate fake-artifact drift cases | Verifier + tests | Fake HOW trace/proof must be untrusted | ~2k | TODO |
| W8.3 | Emit final boundary receipt | `artifacts/certification/apps_rg_l7_boundary_hardening_receipt.json` | Receipt must reflect actual verified results | ~3k | TODO |

---

## Out Of Scope

- Redesigning `agentic_core` L7 projection or spine semantics.
- Renaming canonical core/integrated artifact filenames:
  - `agentic_core_how_trace.json`
  - `agentic_core_l7_route_family_coverage.json`
  - `agentic_core_spine_proof.json`
  - `integrated_runtime_artifact_manifest.json`
  - `runtime_trace_snapshot.json`
  - `runtime_gate_verdict_bundle.json`
- Treating section-lane artifacts as canonical 99 proof, 00C gate verdicts, or durable vector persistence proof.
- Notion/database reshaping beyond required plan registration and normal status updates.
- Immediate deletion of legacy section shim names before dual-write proof.

---

## Gap Register

**GAP-1: Compatibility aliases lack obvious provenance**
- Integrated spine compatibility files are acceptable L7 projection inputs, but their role is not explicit enough for audit readers.
- Impact: Core-owned normalized inputs can look like independent app evidence.

**GAP-2: Section shim filenames overlap with core contract names**
- Section lanes use filenames such as `route_contract.json` and `runtime_exhaust_bundle.json`.
- Impact: Correct taxonomy still requires mental cross-checking to avoid overclaiming authority.

**GAP-3: Trust classification needs stronger negative controls**
- Fake local core L7 artifacts produced inside `apps_rg` must always be drift/untrusted.
- Impact: Regressions could let section folders appear to emit core L7 proof.

**GAP-4: Evidence entrypoints and bundle indexes can over-suggest authority**
- `evidence_package_index.json` and `RUN_BUNDLE_INDEX.json` should guide audit, not certify core proof.
- Impact: Role labels and entrypoint flags can mislead downstream readers.

**GAP-5: Durable persistence claims require explicit governed receipts**
- Chroma/vector/cache persistence must not be inferred from section package presence.
- Impact: Section evidence could accidentally imply durable write authority without CommitRequest/UWG/L4 proof.

---

## Wave 0 - Baseline and freeze the boundary

WAVE_ID: W0
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Purpose**: Lock the current truth before changing code or artifact names.

**Ownership baseline**:

| Artifact family | Canonical owner | Allowed producer | Forbidden producers |
|---|---|---|---|
| `agentic_core_how_trace.json` | `agentic_core` | Core integrated spine / L7 projection | `apps_rg` section lanes |
| `agentic_core_l7_route_family_coverage.json` | `agentic_core` | Core integrated spine / L7 projection | `apps_rg` section lanes |
| `agentic_core_spine_proof.json` | `agentic_core` | Core integrated spine | `apps_rg` section lanes |
| `integrated_runtime_artifact_manifest.json` | `agentic_core` / integrated spine | Integrated runtime | Standalone section lanes |
| `x2_gate_outputs.json` | `apps_rg` app-domain evidence | `apps_rg` | Core 00C GateVerdict producer |
| `section_runtime_proof_bundle.json` | `apps_rg` section shim | `apps_rg` section lane | 99 runtime proof producer |
| `evidence_package_index.json` | `apps_rg` section audit entrypoint | `apps_rg` | Core L7 proof producer |
| `RUN_BUNDLE_INDEX.json` | Catalog/index only | `apps_rg` indexer | Any proof authority |

**Phases**:
- **W0.1** - Create `docs/architecture/apps_rg_l7_artifact_ownership.md` with artifact -> canonical owner -> allowed producer -> forbidden producers.
- **W0.2** - Baseline inspect/freeze the relevant code and contract tests before edits.

**Acceptance**:
- Decision record exists and matches the ownership table above.
- Execution notes identify the current producers/readers for all listed artifact families.

**Suggested commands**:
```bash
python -m pytest tests/_apps_contract/test_section_l7_binding_contracts.py -q
python -m pytest tests/_apps_contract -q --tb=short
```

---

## Wave 1 - Add explicit provenance to core compatibility aliases

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: B

**Purpose**: Make compatibility files emitted for L7 projection visibly core-owned aliases, not app evidence.

**Target file**:
- `agentic_core/runtime/entrypoints/integrated_single_action_spine_run.py`

**Alias provenance fields**:
```json
{
  "producer_component": "agentic_core.runtime.entrypoints.integrated_single_action_spine_run",
  "artifact_role": "core_compat_alias_for_l7_projection",
  "canonical_source_artifact": "r4_run_manifest.json",
  "runtime_subject": "agentic_core",
  "app_subject": "apps_rg"
}
```

**Apply to**:
- `runtime_identity_envelope.json`
- `l1_plan_contract.json`
- `route_contract.json`
- `c0_bypass_receipt.json`
- `runtime_exhaust_bundle.json`
- `runtime_trace_snapshot.json`

**Phases**:
- **W1.1** - Add provenance fields to each generated compatibility alias.
- **W1.2** - Confirm no alias claims `apps_rg` runtime authority.
- **W1.3** - Add/extend `tests/_apps_contract/test_integrated_l7_alias_provenance.py`.

**Acceptance**:
- Every compatibility alias has `producer_component` starting with `agentic_core`.
- Every compatibility alias has `artifact_role = core_compat_alias_for_l7_projection`.
- Alias provenance does not change canonical core L7 output names or semantics.

---

## Wave 3 - Strengthen the binding manifest as the authority firewall

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: C

**Purpose**: Make `apps_rg/runtime/section_l7_binding_manifest.py` the strict classifier for trusted, missing, and drifted L7 references.

**Rules to add**:
- If an artifact filename is in `L7_CORE_ARTIFACTS`, it is trusted only when `producer_component` starts with `agentic_core`.
- Otherwise classify it as drift/untrusted, for example `CORE_L7_UNTRUSTED`.
- `local_path` must be null for verified external refs.
- Section folders must not copy core L7 artifacts from integrated runs.
- Integrated refs are hash-only unless produced in the same integrated spine run.

**Phases**:
- **W3.1** - Add producer-based trust rule for core L7 artifacts.
- **W3.2** - Enforce locality/external-ref constraints.
- **W3.3** - Extend `tests/_apps_contract/test_section_l7_binding_contracts.py`.

**Tests to add**:
- `test_local_agentic_core_how_trace_from_apps_rg_is_drift`
- `test_verified_external_ref_must_have_null_local_path`
- `test_l7_core_artifact_requires_agentic_core_producer`
- `test_section_binding_manifest_cannot_upgrade_product_certification`

**Acceptance**:
- A fake local `agentic_core_how_trace.json` produced by `apps_rg` cannot pass as trusted L7.
- Section L7 binding remains refs-only and cannot upgrade product certification.

---

## Wave 6 - Add negative-control CI guardrails

WAVE_ID: W6
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: D

**Purpose**: Prevent regressions once the trust firewall is explicit.

**Verifier to create**:
- `tools/cert/verify_apps_rg_l7_ownership_boundary.py`

**Verifier rules**:
1. `apps_rg` section dirs may not locally emit trusted core L7 files.
2. Any local `L7_CORE_ARTIFACTS` file without `agentic_core` producer is drift.
3. `x2_gate_outputs.json` is never a 00C GateVerdict.
4. `section_runtime_proof_bundle.json` is never `runtime_proof_bundle.json`.
5. `evidence_package_index.json` may reference core L7 only through verified external refs.
6. Durable vector persistence requires CommitRequest plus UWG commit/block plus L4/read-surface evidence.

**Tests to add**:
- `tests/_apps_contract/test_apps_rg_l7_ownership_boundary.py`
- `tests/_apps_contract/test_apps_rg_section_artifact_namespace.py`
- `tests/_apps_contract/test_apps_rg_no_shadow_l7_emission.py`

**Acceptance**:
- CI/scoped contract tests fail if a section lane starts pretending to emit core L7.
- Negative controls include fake HOW trace, fake spine proof, X2/00C confusion, and section/99 proof confusion.

---

## Wave 4 - Make `evidence_package_index.json` the section audit entrypoint

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Purpose**: Make section audit entrypoint semantics explicit and non-overclaiming.

**Target file**:
- `apps_rg/runtime/section_evidence_package.py`

**Fields to add**:
```json
{
  "section_audit_entrypoint": true,
  "canonical_for_section": true,
  "canonical_for_core_spine": false,
  "canonical_for_l7": false,
  "canonical_for_99_runtime_proof": false
}
```

**Non-claims to preserve/centralize**:
- No semantic cache persistence claimed.
- No Chroma persistence claimed.
- No 99 RuntimeProofBundle claimed.
- Core D2 Chroma upsert is `NON_DURABLE_INDEX_WRITE` unless governed UWG refresh chain is proven.

**Phases**:
- **W4.1** - Add first-class section entrypoint flags.
- **W4.2** - Harden and test explicit non-claims.

**Acceptance**:
- `evidence_package_index.json` is the obvious section audit entrypoint.
- It clearly points to app-domain evidence plus external core refs.

---

## Wave 5 - Clean `RUN_BUNDLE_INDEX.json` role labels

WAVE_ID: W5
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: F

**Purpose**: Keep bundle index role labels from implying proof authority.

**Target file**:
- `apps_rg/runtime/run_bundle_index.py`

**Integrated role label replacements**:

| Old role | New role |
|---|---|
| `audit_how_trace` | `core_l7_how_trace_ref` |
| `audit_l7_route_family_coverage` | `core_l7_route_family_coverage_ref` |
| `audit_spine_proof` | `core_spine_proof_ref` |
| `narrative_run_report` | `apps_rg_recipe_run_report` |
| `spine_runtime_exhaust` | `core_runtime_exhaust_ref` |

**Lane role label replacements**:

| Old role | New role |
|---|---|
| `gate_x2_outputs` | `apps_rg_x2_gate_outputs_not_00c` |
| `section_runtime_proof_bundle` | `apps_rg_section_runtime_proof_bundle_not_99` |
| `disposition_x3` | `apps_rg_section_x3_not_core_exit_x3` |

**Phases**:
- **W5.1** - Rename integrated bundle role labels.
- **W5.2** - Rename lane bundle role labels and update tests.

**Acceptance**:
- No `RUN_BUNDLE_INDEX` role name overclaims core authority.
- Existing catalog/index behavior is preserved.

---

## Wave 2 - Harden section-lane naming without breaking everything

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: G

**Purpose**: Dual-write app-scoped section shim names before removing ambiguous legacy names.

**Preferred names**:

| Legacy section shim | Preferred app-scoped shim |
|---|---|
| `validated_request.json` | `apps_rg_section_validated_request.json` |
| `l1_plan_contract.json` | `apps_rg_section_l1_plan_contract.json` |
| `route_contract.json` | `apps_rg_section_route_contract.json` |
| `compiled_prompt_artifact.json` | `apps_rg_section_compiled_prompt_artifact.json` |
| `exit_review_packet.json` | `apps_rg_section_exit_review_packet.json` |
| `runtime_exhaust_bundle.json` | `apps_rg_section_runtime_exhaust_bundle.json` |
| `x3_disposition.json` | `apps_rg_section_x3_disposition.json` |

**Likely files**:
- `apps_rg/runtime/section_binding_taxonomy.py`
- `apps_rg/runtime/run_bundle_index.py`
- `apps_rg/runtime/section_evidence_package.py`
- `apps_rg/runtime/sections/*_lane.py`
- `tests/unit/apps_rg/**`
- `tests/_apps_contract/**`

**Phases**:
- **W2.1** - Add preferred app-scoped names and dual-write support.
- **W2.2** - Update indexes/evidence package to prefer app-scoped names.
- **W2.3** - Update tests for preferred names plus legacy read compatibility.
- **W2.4** - Document the legacy migration window.

**Acceptance**:
- Section runs emit both old and new names during the compatibility window.
- Indexes prefer app-scoped names.
- Core L7 filenames are untouched.

---

## Wave 7 - Legacy cleanup and migration

WAVE_ID: W7
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: H

**Purpose**: Remove old ambiguous section shim writes only after dual-write proves stable.

**Phases**:
- **W7.1** - Stop writing old section shim names by default.
- **W7.2** - Keep read compatibility for one release window and update docs/runbooks.

**Do not remove**:
- `agentic_core_how_trace.json`
- `agentic_core_l7_route_family_coverage.json`
- `agentic_core_spine_proof.json`
- `integrated_runtime_artifact_manifest.json`
- `runtime_trace_snapshot.json`
- `runtime_gate_verdict_bundle.json`

**Acceptance**:
- Section folders are visibly app-scoped.
- Integrated folders are visibly core-spine-scoped.
- Legacy reads remain documented and tested during the migration window.

---

## Wave 8 - End-to-end proof run

WAVE_ID: W8
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: I

**Purpose**: Prove the boundary with real artifacts and a final receipt.

**Run matrix**:

| Run type | Expected result |
|---|---|
| Full `apps_rg` integrated run | Core L7 artifacts emitted by `agentic_core`; product artifacts emitted by `apps_rg` |
| Section `headline` run | No local trusted core L7; refs-only binding package |
| Section `executive_summary` run | No local trusted core L7; refs-only binding package |
| Section `unify_bullets` run | No local trusted core L7; refs-only binding package |
| Fake local `agentic_core_how_trace.json` in section folder | Classified as drift |
| Fake `runtime_proof_bundle.json` in section folder | Classified as drift |
| Missing UWG/L4 receipts | No durable cache/vector persistence claim |

**Final receipt**:
- `artifacts/certification/apps_rg_l7_boundary_hardening_receipt.json`

**Expected receipt shape**:
```json
{
  "core_l7_single_owner": true,
  "apps_rg_section_l7_refs_only": true,
  "section_runtime_proof_not_99": true,
  "x2_not_00c": true,
  "durable_write_claim_requires_uwg": true,
  "fake_l7_artifacts_classified_drift": true
}
```

**Phases**:
- **W8.1** - Run integrated and section matrix.
- **W8.2** - Run fake-artifact drift cases.
- **W8.3** - Emit final certification receipt.

**Acceptance**:
- Receipt exists and records all six invariants as verified true.
- Any unverified item is not marked true and is captured as deferred scope.

---

## Recommended Execution Order

1. W0 - Boundary decision record.
2. W1 - Provenance on core compatibility aliases.
3. W3 - Stricter section L7 trust classifier.
4. W6 - Negative-control tests.
5. W4 - Evidence package as section entrypoint.
6. W5 - `RUN_BUNDLE_INDEX` role cleanup.
7. W2 - Dual-write app-scoped names.
8. W7 - Legacy removal.
9. W8 - Final proof run.

Start with provenance and tests, not renaming. That gives safety before changing artifact names.

---

## Definition of Done

DoD-1: Artifact ownership decision record is complete
- Evidence: `docs/architecture/apps_rg_l7_artifact_ownership.md` contains artifact -> canonical owner -> allowed producer -> forbidden producers.
- Status: TODO

DoD-2: Core compatibility aliases have explicit provenance
- Evidence: `python -m pytest tests/_apps_contract/test_integrated_l7_alias_provenance.py -q` exits 0.
- Status: TODO

DoD-3: Section L7 binding rejects fake/local app-produced core artifacts
- Evidence: `python -m pytest tests/_apps_contract/test_section_l7_binding_contracts.py -q` exits 0 with the new negative controls.
- Status: TODO

DoD-4: Ownership-boundary verifier and negative-control tests pass
- Evidence: `python tools/cert/verify_apps_rg_l7_ownership_boundary.py <fixture-or-run-dir>` exits 0 for valid fixtures and fails for fake shadow-L7 fixtures; `python -m pytest tests/_apps_contract/test_apps_rg_l7_ownership_boundary.py tests/_apps_contract/test_apps_rg_section_artifact_namespace.py tests/_apps_contract/test_apps_rg_no_shadow_l7_emission.py -q` exits 0.
- Status: TODO

DoD-5: Section evidence package and bundle index do not overclaim authority
- Evidence: Scoped `apps_rg` unit/contract tests pass and generated/indexed artifacts use the new non-overclaiming flags and roles.
- Status: TODO

DoD-6: Section shim namespace migration is proven before legacy cleanup
- Evidence: Dual-write tests pass, indexes prefer app-scoped names, legacy read compatibility remains documented.
- Status: TODO

DoD-7: End-to-end boundary receipt exists
- Evidence: `artifacts/certification/apps_rg_l7_boundary_hardening_receipt.json` records verified `true` values only for proven invariants.
- Status: TODO

DoD-8: Smoke and regression commands pass for touched executable surfaces
- Evidence: `python -m pytest tests/_apps_contract -q --tb=short` and relevant `tests/unit/apps_rg/**` selectors exit 0; any broader CI gate required by implementation changes is captured in the wave receipt.
- Status: TODO

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```
DISCOVERED_SCOPE: plan=l7-auditability-overlap-cleanup-4f8c2d wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=l7-auditability-overlap-cleanup-4f8c2d decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=l7-auditability-overlap-cleanup-4f8c2d reason="<summary>" added="<waves/phases>" authorized="yes"
```

| Decision | When | Continues? |
|---|---|---|
| ACCEPTED | In-charter, absorbable | Yes, expanded scope |
| DEFERRED | Valid but time-gated | Yes, original scope |
| SPLIT_TO_NEW_PLAN | Too large | Yes, original scope |
| REJECTED | Gold-plating/off-charter | Yes, original scope |

> Documentation is not authorization. Retroactive plan updates are not governance.

---

## Marker Quick Reference

Wave lifecycle markers must be at start of line and use the exact plan id:

```
WAVE_START: plan=l7-auditability-overlap-cleanup-4f8c2d wave=<N>
WAVE_COMPLETE: plan=l7-auditability-overlap-cleanup-4f8c2d wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=l7-auditability-overlap-cleanup-4f8c2d phase=<W1.1>
PLAN_COMPLETE: plan=l7-auditability-overlap-cleanup-4f8c2d note="<final outcome>"
```

---

## Registration Note

Repo policy requires a Notion Plans DB row before wave execution. This plan is created with `PLAN_STATUS: TODO` and should be registered as `Status=Not Started` before any `WAVE_START` or execution work.
