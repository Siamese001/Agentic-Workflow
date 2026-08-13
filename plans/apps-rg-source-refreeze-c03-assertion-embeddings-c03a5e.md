---
plan_id: apps-rg-source-refreeze-c03-assertion-embeddings-c03a5e
plan_format: v2
plan_type: platform_core_change
touches_agentic_core: true
touches_governance_ci: false
core_addition_author_gate_required: true
author_gate_receipt_ref: artifacts/apps_rg_source_refreeze/sr0h/contract_authority_receipt.json
dod_exempt: false
preserves_completed_runtime_baseline: true
---

# Apps RG Source Freeze And Standalone Product

Finish the source Apps RG product, certify one exact source baseline, and then create a compact independent `C:\Git\apps_rg` repository.

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: IN_PROGRESS
CURRENT_WAVE: S2
BLOCKED_WAVE: NONE
LAST_COMPLETED_WAVE: S1
LAST_UPDATED: 2026-07-19
STARTING_BRANCH: origin/main
STARTING_COMMIT: fc7039821148151e08459f8473cc8428df39bc8b
STARTING_TREE: 8e3fa68878aef4224f781335850a9eab7ff2c6c9
SOURCE_BRANCH: codex-apps-rg-source-refreeze
SOURCE_HEAD: 716168da9413edf17df658f8a9bc8251c4be6f72
SOURCE_TREE: 2213f28d835c1b7094add47b30f56e343923cdae
SOURCE_REFREEZE_COMPLETE: false
STANDALONE_TARGET: ABSENT
BLOCKER: NONE
S0_STATUS: PASS
S1_STATUS: PASS
S2_STATUS: READY
T1_STATUS: NOT_STARTED
T2_STATUS: NOT_STARTED
SOURCE_IMPLEMENTATION_AUTHORIZED: true
GRAPH_WORK_AUTHORIZED: true
ASSERTION_WORK_AUTHORIZED: true
EMBEDDING_WORK_AUTHORIZED: true
TARGET_CREATION_AUTHORIZED: true
TARGET_CREATION_GATED_ON_SOURCE_REFREEZE: true
PUSH_AUTHORIZED: false
PR_AUTHORIZED: false
MERGE_AUTHORIZED: false
NO_ADG: true
NO_QWEN_OR_VLLM: true

## Fixed Product Contract

- Runtime ingestion loading is read-only and fails closed.
- Offline ingestion receives explicit canonical payload bytes and publishes immutable generations atomically.
- Active configuration binds exact declared component bytes once and exposes immutable precomputed hashes.
- Canonical graph data and candidate facts remain authority; retrieval never manufactures claim proof.
- Standalone v1 requires one pinned BGE-M3 vector per eligible atomic skill assertion.
- Runtime uses one 11-lane registry, one SectionRunner, one serial coordinator, one optional DAG coordinator, and one root Exit/X3.
- UWG is the only durable writer; L6 runs after the current-run boundary.
- The standalone repository has no Agentic-Workflow, apps_shared, graph-tool, Qwen, vLLM, hidden Chroma, or network-download dependency.

## Status Tables

### Wave Progress

Repository-format `W#` aliases are execution ordinals only; the directive wave IDs remain `S0`, `S1`, `S2`, `T1`, and `T2`.

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | S0 | Source ingestion and active-config contracts | Bounded | Approved fixed contracts | PASS | `artifacts/apps_rg_source_refreeze/s0/implementation-20260719-fixed-contracts/sr0_implementation_receipt.json` |
| W2 | S1 | Canonical graph quality, atomic assertions, BGE-M3 qualification and projection | Bounded | S0 PASS | PASS | `artifacts/apps_rg_source_refreeze/s1/graph-assertion-embeddings-20260719/s1_implementation_receipt.json` |
| W3 | S2 | Embedding-enabled source 11-lane certification and source refreeze | Bounded | S1 PASS | READY | Exact source refreeze follows required source certification |
| W4 | T1 | Create compact standalone repository and port certified product | Bounded | Approved source merge and exact refreeze | NOT STARTED | Certified product is ported without source or legacy-spine dependency |
| W5 | T2 | Standalone serial, cache, wheel, independence, and DAG certification | Bounded | T1 parity PASS | NOT STARTED | Standalone product passes all required certification markers |

### Phase Progress

| Phase | Required outcome | Status |
|---|---|---|
| S0 | `SR0_SOURCE_CONTRACTS_PASS` | PASS |
| S1 | Graph data, assertion corpus, BGE-M3 qualification, vector parity | PASS |
| S2 | Source serial 11/11, Apps Eval/L5, root X3/UWG, product certification | READY |
| T1 | Standalone creation and exact graph/assertion/vector parity | NOT STARTED |
| T2 | Standalone serial/DAG E2E, cache/patch, promotion, wheel, independence | NOT STARTED |

## Wave S0 - Source Contracts

Status: PASS

Implemented:

- `IngestionSnapshotLoaderV1` as a read-only explicit-root loader.
- Deterministic offline ingestion packaging with exact payload-byte preservation.
- `ActiveConfigSnapshotProviderV1` with exact-byte component bindings and instance-local load-once semantics.
- Deterministic active-config manifest canonicalization and immutable precomputed hashes.
- Manifest-integrity injection through one snapshot bound at gateway construction.
- Fail-closed removal of runtime ingestion rebuild and default mutable routing configuration.

Commits:

- `b259d0d36db8c5092a6cd29931978ec790d41804` - executable contract specification.
- `aefcad36d2681761729349700749234a129d3c44` - implementation and integration.

Completion marker: `SR0_SOURCE_CONTRACTS_PASS`

## Wave S1 - Graph And Assertion Embeddings

Status: PASS

Required outcomes:

- Reconcile every canonical skill identity, lifecycle, topology, source lineage, candidate-fact support, and retrieval eligibility.
- Produce one stable record per independently retrievable atomic skill assertion.
- Bind each assertion to facts, lineage, allowed sections, authority-envelope digest, and assertion-document digest.
- Freeze BGE-M3 model revision/artifact, graph, assertion corpus, qrels, and thresholds.
- Qualify exact, fact-vector, dense, and hybrid retrieval without lowering thresholds.
- Build one immutable vector row per eligible assertion and expose assertion IDs plus similarity only.

Completion markers:

- `C03_GRAPH_DATA_READY`
- `C03_ASSERTION_CORPUS_PASS`
- `GRAPH_EMBEDDINGS_QUALIFIED`
- `GRAPH_SKILL_EMBEDDING_PARITY_PASS`

Failure marker: `GRAPH_EMBEDDING_QUALIFICATION_FAILED`

Implementation commits:

- `3755f5e17c` - executable graph, assertion, and projection contracts.
- `0a86105c2c` - executable qualification contract.
- `dd0d9fa46c` - canonical graph and assertion-authority closure.
- `f6fff16401` - pinned BGE-M3 projection and qualification artifacts.
- `716168da94` - exact-byte Git preservation for all digest-bound inputs.

Receipt: `artifacts/apps_rg_source_refreeze/s1/graph-assertion-embeddings-20260719/s1_implementation_receipt.json`

## Wave S2 - Source Certification And Refreeze

Status: READY

Run the mandatory embedding-enabled serial lane order:

1. competencies
2. unify_bullets
3. ibm_bullets
4. insurtech_bullets
5. ey_bullets
6. unify_narrative
7. ibm_narrative
8. insurtech_narrative
9. ey_narrative
10. executive_summary
11. headline

Freeze graph, assertion corpus, embedding generation, model artifact, allocation, and lane allowlists before generation. Complete deterministic aggregation, final gates, judges, Apps Eval, L5, one root X3, UWG, telemetry/L7, and post-run L6.

Completion markers:

- `SOURCE_SERIAL_11_OF_11_PASS`
- `SOURCE_APPS_EVAL_L5_PASS`
- `SOURCE_ROOT_X3_UWG_PASS`
- `SOURCE_C03_PRODUCT_CERTIFIED`

An approved merge is required before recording the new exact main commit and tree.

## Wave T1 - Standalone Port

Status: NOT STARTED

Create `C:\Git\apps_rg` only after source certification, approved merge, and exact refreeze. Port the compact product surface only: research, providers, graph, assertions, embeddings, cache, evaluation, rendering, one registry/runner pair, serial/DAG coordination, Exit, UWG, telemetry, L7, and L6.

Completion markers:

- `STANDALONE_REPOSITORY_CREATED`
- `ZERO_AGENTIC_WORKFLOW_DEPENDENCY`
- `EXACT_GRAPH_PARITY_PASS`
- `ASSERTION_CORPUS_PARITY_PASS`
- `EMBEDDING_PROJECTION_PARITY_PASS`

## Wave T2 - Standalone Certification

Status: NOT STARTED

Prove serial execution first, then cache and patch behavior, clean-wheel installation with the source unavailable, and finally DAG parity through the same SectionRunner and frozen allocation.

Completion markers:

- `SERIAL_11_OF_11_E2E_PASS`
- `R1A_R1B_PATCH_RUN_PASS`
- `APPS_EVAL_L5_PASS`
- `PROMOTION_PASS`
- `OTEL_L7_PASS`
- `CLEAN_WHEEL_INSTALL_PASS`
- `L3_DAG_11_OF_11_E2E_PASS`
- `PORT_SCOPE_ACCOUNTED`
- `LEGACY_OUTPUTS_ABSENT`

## Definition Of Done

| ID | Requirement | Status |
|---|---|---|
| DoD-1 | Both source snapshot contracts are implemented and deterministic | PASS |
| DoD-2 | Runtime snapshot reads have zero writes, network, provider, graph, Redis, or subprocess side effects | PASS |
| DoD-3 | Canonical graph data is ready with exact canonical/SQLite parity | PASS |
| DoD-4 | Every eligible atomic assertion has exactly one qualified BGE-M3 vector | PASS |
| DoD-5 | Source Apps RG passes embedding-enabled serial 11/11 certification | TODO |
| DoD-6 | Approved source changes are merged and one exact source commit/tree is frozen | TODO |
| DoD-7 | Compact standalone repository has zero source-repository dependency | TODO |
| DoD-8 | Standalone serial, cache/patch, wheel, outputs, and DAG parity pass | TODO |
| DoD-9 | No generic replacement platform or forbidden runtime dependency is introduced | IN PROGRESS |

## Authorization Boundary

Local implementation and local commits are authorized. Push, pull request, merge, release, and source-refreeze claims remain unauthorized until separately approved. Target creation is authorized by the execution directive but remains technically gated on completed source certification, approved merge, and exact refreeze.
