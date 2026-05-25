# Agentic Requirements — REQ_ID Registry, Per-Layer Contracts, and E2E Evidence Compiler

Refreshed: 2026-04-26 — REQ_ID-first overwrite (predecessor preserved at `README.md.pre-reqid-rewrite.bak`).

This pack is no longer a prose-grade architecture document. It is a **requirements-to-runtime-evidence contract**:
every layer parent declares stable `REQ_ID` rows whose runtime evidence, OTEL span, validator, negative control,
expected fail reason, replay check, and release-gate status are enforced.

## Foundation files (read these first)

- **`00X_Requirements_Traceability_and_No_Loss_Map.md`** — global REQ_ID registry: grammar, namespace map, status / evidence / fail-reason vocabularies, anti-cheat encodings, no-overlap law.
- **`99_End_to_End_Runtime_Proof_and_Acceptance/99.11_E2E_Requirements_To_Runtime_Evidence_Compiler.md`** — the compiler contract that consumes `00X` and emits the 10-report release bundle.
- `99_End_to_End_Runtime_Proof_and_Acceptance/99_End_to_End_Runtime_Proof_and_Acceptance.md` — scenario-level cross-layer proof contract.

## REQ_ID namespace map (binding — defined in 00X §3.1)

| Pack | Namespace | Parent file |
|---|---|---|
| `00A_L5_Governance_Safety/` | `REQ-L5-*` | `00A_L5_Governance_Safety.md` |
| `00B_L4_State_Archive_and_UWG/` | `REQ-L4-*`, `REQ-UWG-*` | `00B_L4_State_Archive_and_UWG.md` |
| `00C_Runtime_Gates_Current_Run_Mesh/` | `REQ-GATE-G01-*` … `REQ-GATE-G29-*` | `00C_Runtime_Gates_Current_Run_Mesh.md` |
| `01_Request_Intake/` | `REQ-U0-*` | `01_request_intake.md` |
| `02_L1_Reasoning_Plan/` | `REQ-L1-*` | `02_L1_Reasoning_Plan_Generation.md` |
| `03_L0_Route_Decision_and_L3_Orchestration/` | `REQ-L0-*`, `REQ-L3-*` | `03_L0_Route_Decision_Switching_L3.md` |
| `03A_C0_Context_Engine/` | `REQ-C0-*` | `C0_Context_Engine.md` |
| `03B_PA_Prompt_Assembly/` | `REQ-PA-*` | `PA_Prompt_Assembly.md` |
| `04_L2_Execute/` | `REQ-L2-*` | `04_L2_Execute.md` |
| `05_Exit_Evaluation_and_Control/` | `REQ-EXIT-*` | `05_Live_Runtime_Exit_Control_&_Evaluation.md` |
| `06_L6_Observability_and_System_Learning/` | `REQ-L6-*` | `06_Shadow_Evaluation_System_Learning.md` |
| `99_End_to_End_Runtime_Proof_and_Acceptance/` | `REQ-E2E-*`, `REQ-TRACE-*`, `REQ-COMPILER-*` | `99_End_to_End_Runtime_Proof_and_Acceptance.md`, `99.11_*.md` |

## Status vocabulary (binding — defined in 00X §5)

`PASS` · `PARTIAL` · `MISSING` · `DOC_ONLY` · `MOCK_ONLY` · `FAKE` · `UNVERIFIED` · `NOT_APPLICABLE`

The set `{PARTIAL, MISSING, DOC_ONLY, MOCK_ONLY, FAKE, UNVERIFIED}` is **release-blocking**.
Release passes only when every row is `PASS` or `NOT_APPLICABLE` with a written reason.

## What changed on 2026-04-26 (REQ_ID-first overwrite)

- `00X` rewritten from a prose ledger into the global REQ_ID **registry contract** (rules, vocabularies, anti-cheat encodings, traceability matrix schema).
- `99.11` created as the **E2E evidence compiler** contract producing the 10 release reports.
- All 12 layer parent files (00A, 00B, 00C, 01, 02, 03, 03A, 03B, 04, 05, 06, 99) overwritten to the **13-section REQ_ID contract template** with starter atomic REQ_ID rows, runtime evidence contract, OTEL span contract, validator contract, negative-control contract, replay contract, release-gate contract, and no-overlap lock.
- Predecessors preserved beside each rewritten file as `*.pre-reqid-rewrite.bak`.
- Per-stage **sub-children (~80 files)** retain their existing prose ownership content; their conversion to per-stage REQ_ID Atomic Requirements Tables is staged as deferred follow-up waves (W4–W10) — see `00X §13 superseded ledger` and the parent file's child map for the per-stage REQ_ID prefix each child will own.

## Anti-cheat invariants (binding)

The pack explicitly forbids these failure modes (see `00X §11`):

1. `caught=true` without `expected_fail_reason` match → `FAKE` / `UNVERIFIED`.
2. Index-only artifact validation without referenced payload `content_hash` → `FAKE`.
3. OTEL trace exists but required spans / parent-child links missing → `PARTIAL` / `UNVERIFIED`.
4. Validator catches by accident (wrong reason path) → `FAKE`.
5. Tests pass but reference no REQ_ID → `OrphanTests` (not proof).
6. Implementation exists but no runtime artifact proves execution → `UNVERIFIED`.
7. Markdown declares requirement but no code/validator/span/artifact/test references it → `DOC_ONLY`.
8. Mock-only test satisfies row → `MOCK_ONLY`.
9. Generated artifact missing one of `content_hash` / `lineage` / `trace_id` / `policy_hash` / `replay_key` / `validator_receipt` → `UNVERIFIED`.
10. Negative control without `expected_fail_reason` → `PARTIAL` (release-blocking).

## No-overlap law (binding — defined in 00X §9)

| Pack | Owns | Forbidden |
|---|---|---|
| 00A | L5 certification statuses | live runtime dispositions, durable writes |
| 00B | L4 durable state, UWG sole admission | routing, gate verdicts, retrieval, prompt, exec, exit |
| 00C | G01–G29 GateVerdict law | final disposition, certification, durable writes |
| 01 | U0 envelope validation, identity baseline | reasoning, retrieval, routing, exec, mutation |
| 02 | L1 plan + advisory route hints | route authority, retrieval, exec, mutation |
| 03 | L0 RouteContract, L3 workflow shaping | retrieval, prompt, exec, durable mutation |
| 03A | C0 retrieval and FinalEvidenceContract | answering, routing, exec, mutation |
| 03B | PA PromptEnvelope construction | retrieval, exec, mutation |
| 04 | L2 bounded exec, sealed_l2_artifact | re-routing, durable mutation, eval, certify |
| 05 | Exactly one X3 disposition, CommitRequest emission | tool exec, retrieval, durable mutation, L6 rescue |
| 06 | Eval, RCA, gauntlet, future-run promotion (via UWG) | live mutation, direct L4 writes |
| 99 | E2E proof harnesses | runtime authority |

## Canonical folder map

- `00A_L5_Governance_Safety/` — L5 certification (8 children + 5 supporting docs)
- `00B_L4_State_Archive_and_UWG/` — L4 + UWG (11 children)
- `00C_Runtime_Gates_Current_Run_Mesh/` — G01–G29 (9 children)
- `01_Request_Intake/` — U0 (6 canonical children + dedup'd duplicates)
- `02_L1_Reasoning_Plan/` — L1 (6 children)
- `03_L0_Route_Decision_and_L3_Orchestration/` — L0 + L3 (9 children)
- `03A_C0_Context_Engine/` — C0 (8 children + supporting docs)
- `03B_PA_Prompt_Assembly/` — PA (9 children)
- `04_L2_Execute/` — L2 (12 children)
- `05_Exit_Evaluation_and_Control/` — Exit (8 children + 4 supporting docs)
- `06_L6_Observability_and_System_Learning/` — L6 (9 canonical children + dedup'd duplicates)
- `99_End_to_End_Runtime_Proof_and_Acceptance/` — E2E (10 children + the 99.11 compiler contract)

## Root files

- `00X_Requirements_Traceability_and_No_Loss_Map.md` — REQ_ID registry contract (foundation).
- `00Y_April2026_Gap_Closure_Reconciliation.md` — historical gap closure log.
- `00Z_Source_Alignment_Best_Practices.md` — historical alignment notes.
- `MANIFEST.json` — file inventory with sha256 (auto-regenerable).
- `UPDATED_MANIFEST.json` — historical manifest variant; canonical is `MANIFEST.json`.
- `PARENT_THINNING_ZERO_LOSS_REPORT.md` — historical 2026-04-26 parent-thinning move log.

## Quality bar (binding)

This pack must make the following claim impossible:

> "pytest passed and full proof passed, therefore architecture is proven."

It must force the stronger claim:

> "Every applicable REQ_ID has mapped runtime artifact evidence, OTEL span evidence, validator evidence, negative-control evidence with `expected_fail_reason`, replay evidence, and release-gate `PASS` (or `NOT_APPLICABLE` with reason)."

## How to use this pack

1. To **add a new requirement**: pick the owning pack from the namespace map; add a new row to that pack's parent or child Atomic Requirements Table; fill all 13 schema cells; the negative control and `expected_fail_reason` are mandatory unless the row is `NOT_APPLICABLE` with a reason.
2. To **prove a release**: run the compiler at `99.11` and inspect `RequirementsCoverageMatrix`, `Top25GapsBySeverity`, `OrphanRuntimeSurfaces`, `OrphanTests`, `FakeOrMockOnlyClaims`, `MissingOTELSpanReport`, `MissingArtifactReport`, `NegativeControlReasonMismatchReport`, `ReplayCoverageReport`, and `release_decision.json`. The `release_blocking` flag is authoritative.
3. To **diagnose a release-blocking row**: read the row's `gap_reason` and `required_fix`; cross-reference the row's parent file for the runtime evidence contract.
4. To **deduplicate or rename** a REQ_ID: not allowed — REQ_IDs are immutable. Supersession proceeds via a new REQ_ID and the registry's superseded ledger.
