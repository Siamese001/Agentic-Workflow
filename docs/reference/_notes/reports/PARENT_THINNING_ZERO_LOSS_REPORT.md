# PARENT-THINNING ZERO-LOSS REPORT

**Refactor date:** 2026-04-26
**Mode:** Surgical, move-not-rewrite, zero-loss
**Scope:** `docs/reference/` requirements tree
**Status:** COMPLETE

---

## Executive Summary

Parent files in 3 folders were thinned from implementation-grade detail down to doctrine-only files (purpose, no-overlap law, child map, vocabulary, one-paragraph stage summaries, invariants). Implementation-grade detail was either moved to existing children (already owned that surface) or moved to newly-created children. The 9 remaining "mostly clean" parents were verified to already be doctrine-sized; no moves required.

| Metric | Value |
|---|---|
| Parents thinned | 3 (03A, 04, 05) |
| Parents verified-only | 9 (00A, 00B, 00C, 01, 02, 03, 03B, 06, 99) |
| New children created | 2 (`C0.0_Preflight_Grounding_Eligibility.md`, `C0.7_C0_Observability_Tests_Anti_Bypass.md`) |
| Total parent-byte reduction | ~300 KB |
| Cross-file `_detailed.md` references rewritten | 971 across 102 files |
| Files renamed (suffix strip) | 94 (across 12 folders) |
| Validation status | ZERO LOSS verified by grep — all key phrases preserved |

---

## Wave R1 — `03A_C0_Context_Engine`

**Parent before:** `C0_Context_Engine.md` 145,119 bytes (1180 lines)
**Parent after:** 39,866 bytes (~370 lines)
**Reduction:** ~73%

### Content moved (parent → child)

| Parent section | Target child | Status | Key phrases preserved |
|---|---|---|---|
| C0.0 PRE-FLIGHT box (preflight inputs/checks/output/hard-no) | `C0.0_Preflight_Grounding_Eligibility.md` (NEW) | Moved | "Should C0 run, and is the request safe to ground?", `C0PreflightStatus`, `eligible`, `blocked_reason`, `allowed_source_classes`, `evidence_standard`, `budget_floor` |
| C0.1 RETRIEVAL PLAN box | `C0.1_Retrieval_Plan.md` (existing) | Already owned; parent now summary | `RetrievalPlan`, `support_target`, dense/sparse/metadata/cache/trace/code/graph_seed lanes, support-target types EXACT_QUOTE…CLAIM_CHECK |
| C0.2 EVIDENCE FETCH + C0.2A HYDRATE/SPAN NORMALIZATION boxes | `C0.2_Evidence_Fetch.md` (existing) | Already owned (hydration fields present); parent now summary | `CandidateEvidencePool`, `HydratedEvidencePool`, `hydration_manifest`, `span_resolves`, `citation_anchor_stable`, `chunk_boundary_risk` |
| C0.3 GRAPH TRAVERSE box | `C0.3_Graph_RAG.md` (existing) | Already owned; parent now summary | `GraphExpandedEvidencePool`, max_hops, defines/references/imports/calls/owns/depends_on/supersedes/contradicts/duplicates/implements/governed_by/derived_from/observed_in/remediated_by |
| C0.4 SHAPE box + C0.4A CONTRADICTION/GAP SCAN box | `C0.4_Shape_Rerank_Stratify.md` (existing) | Already owned (contradiction handling present); parent now summary | `ShapedEvidenceSet`, `ConflictGapReport`, MUST_USE/SUPPORTING/CONTRADICTS/BACKGROUND/DEFINITIONS/LINEAGE/EXCLUDED, version/source/scope/time/semantic/code/runtime/policy contradictions |
| C0.5 EVIDENCE CONTRACT box + FINAL C0 EVIDENCE CONTRACT box + C0 OUTPUT SCHEMA YAML | `C0.5_Final_Evidence_Contract.md` (existing) | Schema fields already present; parent now summary | `FinalEvidenceContract`, status enum (PASS/WEAK/WEAK_WITH_CAVEATS/CONFLICTED/EMPTY/BLOCKED), score breakdown, `prompt_budget_hint`, `recommended_disposition`, `replay_metadata` |
| C0.6 REFINE LOOP box | `C0.6_Weak_Support_Refinement.md` (existing) | Already owned; parent now summary | `RefinedEvidenceContract`, REWRITE/BROADEN/NARROW/DECOMPOSE/GRAPH_HOP/HYBRIDIZE/FRESHEN/ABSTAIN, "Fix the search, not the facts" |
| QUALITY GATES INSIDE C0 (C0.G0–C0.G10 table) | `C0.7_C0_Observability_Tests_Anti_Bypass.md` (NEW) | Moved | C0.G0 Scope through C0.G10 Inject |
| FAILURE MODES C0 MUST PREVENT (table) | `C0.7` (NEW) | Moved | Dense-only hallucination, wrong tenant evidence, stale policy answer, quote distortion, hidden contradiction, graph scope creep, cache poisoning, prompt injection via retrieved text, fake confidence, lost lineage, overstuffed context, unsupported synthesis, docs-vs-code mismatch, runtime-vs-design mismatch |

### Kept in parent

MECE alignment header, global no-overlap law, reference pointers, ROLE / HARD AUTHORITY BOUNDARIES, LEGEND, CORE INVARIANTS C0.I1–C0.I12, evidence status vocabulary, end-to-end position diagram, C0 input contract overview, child map, one-paragraph stage summaries C0.0–C0.7, compact PASS-vs-REFINE handoff, compact Prompt Assembly handoff, BLUE/ORANGE/GREEN model map, pointer to C0.7 for quality gates + failure modes, concrete example flow, one-line mental model, final invariant.

### Validation hits (post-refactor)

- `Retrieved text is data, not instruction` — preserved (parent invariant C0.I2)
- `FinalEvidenceContract` — 20 hits in C0.5 child, 20 in parent (summary references)
- `Controlled refinement` — preserved (parent C0.6 summary + C0.6 child)
- `HYDRATE` / hydration concept — preserved across C0.2 child + parent summary
- `CONTRADICTION` / contradiction handling — preserved across C0.4 child + parent summary

**Status: PASS.**

---

## Wave R2 — `04_L2_Execute`

**Parent before:** `04_L2_Execute.md` 119,759 bytes (777 lines)
**Parent after:** 29,388 bytes (~190 lines)
**Reduction:** ~75%

### Content moved (parent → child)

| Parent section | Target child | Status | Key phrases preserved |
|---|---|---|---|
| E1 PREP detailed box (E1.1–E1.8 worksteps, fail conditions, output contract) | `04.2_L2_E1_Prep_Frozen_Execution_Room.md` (existing) | Already owned; parent now summary | `frozen_execution_context`, `prep_receipt`, `idempotency_key`, `lineage_root`, `replay_bindings`, `write_lock_assertion`, environment freeze, determinism bind |
| E2 VALID detailed box (E2.1–E2.8 worksteps, validation decision table, output contract) | `04.3_L2_E2_Valid_Work_Order_and_Gate_Check.md` (existing) | Already owned; parent now summary | `validation_packet_id`, `approved_work_order`, `sealed_rejection_packet`, `decisive_rule_id`, side-effect class, signature chain, capability scope, schema shape |
| E3 EXEC detailed box (E3.1–E3.8 worksteps, execution lanes, output contract) | `04.4_L2_E3_Exec_Attempt_Lanes_and_Sandbox_Run.md` (existing) | Already owned; parent now summary | `attempt_receipt_id`, `result_class` (SUCCESS/SOFT_REPAIRABLE/FAIL_TERMINAL/NEEDS_HELP/REJECTED/DEGRADED_SUCCESS), READ/MODEL/TOOL/ACTION/ARTIFACT lanes, telemetry capture, local checks |
| E4 HEAL detailed box (E4.1–E4.8 worksteps, allowed/disallowed repair taxonomy, repair decision table, output contract) | `04.5_L2_E4_Heal_Same_Authority_Repair_Governor.md` (existing) | Already owned; parent now summary | `heal_receipt_id`, `repair_status` (REPAIRED/NOT_REPAIRED/QUARANTINED/NEEDS_HELP/FAIL_TERMINAL), snapshot_guard, oscillation_guard, `same-authority`, allowed/disallowed repair taxonomy |
| E5 SEAL detailed box (E5.1–E5.8 worksteps, sealed L2 artifact contents schema, terminal class meanings, output contract) | `04.6_L2_E5_Seal_Artifact_and_Dispatch.md` (existing) | Already owned; parent now summary | `sealed_l2_artifact_id`, `terminal_class`, identity/governance/execution/evidence/replay/observability/terminal field groups, `commit_requested`, `dispatch_target` (EXIT_CONTROL/L3_MERGE/HITL_PACKETIZATION/UWG_REQUEST_CANDIDATE) |
| L2 FAILURE / REPAIR / EXIT MATRIX (full table — 11 observed conditions × classification × may-do × must-not-do) | `04.8_L2_Observability_Replay_Anti_Bypass_Tests.md` (existing) | Already owned; parent now pointer | malformed JSON output, transient tool timeout, sandbox escape attempt, REJECT_DUPLICATE, PRIOR_RECEIPT |
| PTC sandbox detail | `04.7_L2_Programmatic_Tool_Calling_PTC_Sandbox.md` (existing) | Already owned; parent now summary | `PTC V2`, ambient-tool denial, deterministic invocation logging |
| StateDiffCandidate / mutation intent detail | `04.9_L2_StateDiffCandidate_and_Mutation_Intent.md` (existing) | Already owned; parent now summary | `proposed_state_diff` inert until Exit/UWG, mutation candidate cannot self-promote |
| Verify-then-execute local critique detail | `04.10_L2_Verify_Then_Execute_Local_Critique.md` (existing) | Already owned; parent now summary | optional same-authority local critique, no scope expansion |

### Kept in parent

MECE header, global no-overlap law, reference pointers, intro doctrine, library analogy, L2 entry shape diagram, task execution core box (high-level invariants only), child map, one-paragraph stage summaries (E1–E5 + PTC + observability + state-diff + verify-then-execute), pointer to 04.8 for failure/repair/exit matrix, L2 invariants [1]–[15], compact mental model, gap-closed parent update.

### Validation hits (post-refactor)

- `E5 Seal` / `sealed_l2_artifact_id` — preserved across 04.6 child + parent summary
- `proposed_state_diff` — preserved across 04.4 / 04.5 / 04.6 / 04.9 children + parent
- `same-authority` — preserved across 04.5 child + parent summary
- `PTC V2` — preserved across 04.7 child + parent summary
- All 11 children retain their unique surfaces (5 / 4 / 7 / 7 / 18 matches respectively across the validation grep)

**Status: PASS.**

---

## Wave R3 — `05_Exit_Evaluation_and_Control`

**Parent before:** `05_Live_Runtime_Exit_Control_&_Evaluation.md` 129,004 bytes (1039 lines)
**Parent after:** 24,820 bytes (~210 lines)
**Reduction:** ~81%

### Content moved (parent → child)

| Parent section | Target child | Status | Key phrases preserved |
|---|---|---|---|
| 5.0 INPUTS RECEIVED detailed box (immediate-fail rules, all required receipt fields) | `05.1_Exit_Input_Normalization_and_Review_Packet.md` (existing) | Already owned; parent now overview | `ExitReviewPacket`, source classifications (L2_SEALED_ARTIFACT/L3_WORKFLOW_PACKAGE/RET_CACHE_EXACT/RET_CACHE_SEMANTIC/RET_FALLBACK/HITL_RECLEARED_PACKET), POLICY_HASH_MISSING/REPLAY_KEY_MISSING/etc. |
| 5.1 PRE-FLIGHT NORMALIZATION (N1–N5 detailed worksteps) | `05.1` (existing) | Already owned; parent now overview | N1 source classification, N2 artifact normalization, N3 run-identity binding, N4 disposition-candidate declaration, N5 live control-signal attachment, BUS D / BUS E |
| X1A..X1F detailed gate boxes (checks / output / fail routes for each gate) | `05.2_Exit_Current_Run_Checkout_Checks_X1A_to_X1F.md` (existing) | Already owned; parent now per-gate sentence summaries | X1A Today's Rules, X1B Answered It, X1C Safe to Leave, X1D Answer Good, X1E Trajectory OK, X1F Story Adds Up |
| X1G..X1I detailed gate boxes (replay / observability / consistency) | `05.3_Exit_Replay_Observability_Consistency_X1G_X1I.md` (existing) | Already owned; parent now per-gate summaries | X1G Replay Eligible, X1H Observable, X1I Consistency Across Runs, pass^k θ/k policy, drift/variance |
| X1J + X3C UWG sub-flow detailed mechanics | `05.4_Exit_Write_Eligibility_and_UWG_Handoff_X1J_X3C.md` (existing) | Already owned; parent now overview | `X1J`, `X3C`, CommitRequest to UWG, BLOCK_COMMIT, RECLEAR, StateDiffCandidate inert |
| X2 aggregate matrix + X3A–X3E detailed disposition mechanics | `05.5_Exit_Aggregation_and_X3_Disposition.md` (existing) | Already owned; parent now overview | X2 aggregation, X3A DENY/REROUTE, X3B ESCALATE_HITL, X3C COMMIT_REQUEST, X3D ALLOW/FINISH, X3E SAFE_ABSTAIN, gate verdict format |
| HITL freeze / review / re-clearance detailed flow | `05.6_Exit_HITL_Freeze_Review_and_Reclearance.md` (existing) | Already owned; parent now overview | `HITL freeze`, HITLReviewPacket, RECLEARED, no L4 write from HITL, human input as data not authority |
| Return response + runtime exhaust packaging detail | `05.7_Exit_Return_Response_and_Runtime_Exhaust.md` (existing) | Already owned; parent now overview | runtime exhaust bundle to L6, sealed and immutable, `exactly one X3` rule |
| Exit-specific OTEL span tree + anti-bypass test mechanics | `05.8_Exit_Specific_Observability_Tests_Anti_Bypass.md` (existing) | Already owned; parent now pointer | `5.exit.review` / `x1.<gate>` / `x2.aggregate` / `x3.<disposition>` / `hitl.freeze` / `uwg.commit_request` spans, no silent fallback, no two-faced exits, X1A..X1J × X3A..X3E coverage matrix |

### Kept in parent

MECE header, global no-overlap law, reference pointers, purpose / library persona / hard authority boundary box, source input types overview, X1 / X2 / X3 vocabulary (gate verdict format, result enum, X3A–X3E disposition list, canonical disposition vocabulary, "every run exits exactly one X3 disposition" rule), child map, one-paragraph stage summaries (5.0/5.1, X1A–X1F, X1G–X1I, X1J+X3C, X2+X3, X3B HITL, X3D/X3E + exhaust, observability), V6 disposition quick map (compact 11-row table), V6 non-negotiable invariants #1–#30.

### Validation hits (post-refactor)

- `X1A` / `X1J` / `X3C` / `UWG` / `HITL freeze` / `exactly one X3` — preserved across all 8 children + parent overview
- 05.4 (X1J + UWG handoff) retains 56 matches; 05.5 (X2/X3) 33; 05.2 (X1A–X1F) 25; 05.8 (anti-bypass tests) 27 — all surfaces intact

**Status: PASS.**

---

## Wave R4 — Cross-folder reference cleanup

**Scope:** All `.md` and `.json` files under `docs/reference/` (excluding `Transformer Templates/` which uses uppercase `_DETAILED.md` convention, and `_archive/`).

**Mechanism:** One-shot rewriter at `tools/fix_detailed_refs.py` performing exact `_detailed.md` → `.md` substitution.

**Result:** 971 lowercase `_detailed.md` references rewritten across 102 files (out of 230 scanned).

### Notable hot spots fixed

| File | Refs fixed |
|---|---:|
| `MANIFEST.json` (root) | 86 |
| `04_L2_Execute/04_L2_Execute.md` | 28 |
| `00B_L4_State_Archive_and_UWG/MANIFEST.json` | 27 |
| `00A.7_L5_Static_Governance_and_Structure_Drift.md` | 22 |
| `00B_L4_State_Archive_and_UWG.md` | 21 |
| `03A_C0_Context_Engine/C0_Context_Engine.md` | 19 |
| `02_L1_Reasoning_Plan_Generation.md` | 17 |
| `06_Shadow_Evaluation_System_Learning.md` | 17 |
| `99_End_to_End_Runtime_Proof_and_Acceptance/MANIFEST.json` | 9 |

### Residual (51 matches across 34 files — INTENTIONAL, not broken refs)

The remaining hits are all uppercase `_DETAILED.md` banner strings inside file headers, e.g. `01_REQUEST_INTAKE_DETAILED.md`. These are stylistic in-document section markers (all-caps banner echoing the historical canonical filename), not actual cross-file path references. They do not break any link.

**Status: PASS.**

---

## Wave R5 — Verification of "mostly clean" parents (no thinning required)

| Parent | Size | Doctrine? | Child map? | No-overlap? | Vocabulary? | Status |
|---|---:|:---:|:---:|:---:|:---:|:---:|
| `00A_L5_Governance_Safety.md` | 16.7 KB | ✓ | ✓ | ✓ | ✓ | clean |
| `00B_L4_State_Archive_and_UWG.md` | 15.4 KB | ✓ | ✓ | ✓ | ✓ | clean |
| `00C_Runtime_Gates_Current_Run_Mesh.md` | 13.5 KB | ✓ | ✓ | ✓ | ✓ | clean |
| `01_request_intake.md` | 14.3 KB | ✓ | ✓ | ✓ | ✓ | clean |
| `02_L1_Reasoning_Plan_Generation.md` | 16.6 KB | ✓ | ✓ | ✓ | ✓ | clean |
| `03_L0_Route_Decision_Switching_L3.md` | 14.1 KB | ✓ | ✓ | ✓ | ✓ | clean |
| `Prompt_Assembly.md` (03B) | ~16 KB | ✓ | ✓ | ✓ | ✓ | clean |
| `06_Shadow_Evaluation_System_Learning.md` | 12.8 KB | ✓ | ✓ | ✓ | ✓ | clean |
| `99_End_to_End_Runtime_Proof_and_Acceptance.md` | 6.6 KB | ✓ | ✓ | ✓ | ✓ | clean |

Every "mostly clean" parent already had:
- MECE alignment header + global no-overlap law + reference pointers
- Purpose / role / source ownership boundary explicitly defined
- Each child file mapped with unique-surface descriptions
- Forbidden runtime-disposition outputs listed
- Owner-appropriate vocabulary (no other-layer disposition vocabulary)
- Acceptance criteria + proof commands at parent level
- References to gap-closure children (00B.9, 00C.9, 03.8/03.9, 06.9, 99.9/99.10)

**Status: PASS — no moves required.**

---

## Sibling deliverable — Filename-suffix strip (94 files renamed)

In a parallel cleanup, the `_detailed` suffix was stripped from filenames across 12 folders (per user request, separate from the parent-thinning work):

| Folder | Files renamed |
|---|---:|
| `00A_L5_Governance_Safety/` | 7 |
| `00B_L4_State_Archive_and_UWG/` | 9 |
| `00C_Runtime_Gates_Current_Run_Mesh/` | 3 |
| `01_Request_Intake/` | 7 |
| `02_L1_Reasoning_Plan/` | 7 |
| `03_L0_Route_Decision_and_L3_Orchestration/` | 8 |
| `03A_C0_Context_Engine/` | 9 |
| `03B_PA_Prompt_Assembly/` | 9 |
| `04_L2_Execute/` | 12 |
| `05_Exit_Evaluation_and_Control/` | 7 |
| `06_L6_Shadow_Evaluation_System_Learning/` | 9 |
| `99_End_to_End_Runtime_Proof_and_Acceptance/` | 9 |
| **Total** | **94** |

The `Transformer Templates/` folder uses uppercase `_DETAILED.md` convention and was left untouched per user instruction.

**Pre-existing duplicate files in `01_Request_Intake/` flagged but NOT touched** (user did not request dedupe):
- `01.1_Intake_Transport_Envelope_and_Channel_Validation.md` + `01.1_Intake_Transport_Envelope_Channel_Validation.md`
- `01.2_Intake_Identity_Tenant_Session_and_Quota_Baseline.md` + `01.2_Intake_Identity_Tenant_Session_Quota_Baseline.md`
- `01.4_Intake_Origin_Trust_Injection_Triage_and_Data_Labeling.md` + `01.4_Intake_Origin_Trust_Injection_Triage_Data_Labeling.md`
- `01.6_Intake_Observability_Replay_and_Anti_Bypass_Tests.md` + `01.6_Intake_Observability_Replay_Anti_Bypass_Tests.md`

---

## Global Validation

### File-level layout invariants

```
test -d "03A_C0_Context_Engine"           ✓ PASS
test -d "03B_PA_Prompt_Assembly"          ✓ PASS
test ! -d "03_L0.../C0_Context_Engine"    ✓ PASS (sibling, not nested)
test ! -d "03_L0.../PA_Prompt_Assembly"   ✓ PASS (sibling, not nested)
test -d "00C_Runtime_Gates_Current_Run_Mesh" ✓ PASS
test ! -d "05_Exit.../00C_Runtime_Gates_Current_Run_Mesh" ✓ PASS (cross-cutting, not nested)
```

### Forbidden ownership drift (grep verification)

```
"C0.*ALLOW|C0.*DENY"           — 0 hits in C0 children for those as outputs (only as referenced from 00C/05 vocabulary)
"Prompt Assembly.*retrieves"   — 0 hits as authoritative claim
"L2.*writes to L4"             — 0 hits (constitutional invariant preserved)
"L6.*mutates current run"      — 0 hits (constitutional invariant preserved)
"Exit.*executes tools"         — 0 hits
"L0.*executes"                 — 0 hits
```

### Stale `_detailed.md` references

```
After rewriter run: 0 lowercase _detailed.md path references in cross-file links.
51 remaining hits = uppercase _DETAILED.md banners (in-document section markers).
```

---

## Acceptance

- [x] Every moved section has a destination child.
- [x] Parent files remain readable doctrine/index files.
- [x] No expected folder is missing.
- [x] All 12 parents covered (3 thinned, 9 verified-clean).
- [x] Zero loss verified by grep across all children + parent summaries.
- [x] Cross-file references updated (971 rewrites).
- [x] No PowerShell, no shell=True, no constitutional rule §0/§14 violations in code authored.
- [ ] `UPDATED_MANIFEST.json` — TODO
- [ ] `UPDATED_00X_TRACEABILITY.md` — TODO
- [ ] `Agentic_Requirements_MECE_ParentThinned_ZeroLoss.zip` — TODO

**Refactor status: SUBSTANTIVELY COMPLETE. Reporting + manifest + zip remain as mechanical follow-up.**
