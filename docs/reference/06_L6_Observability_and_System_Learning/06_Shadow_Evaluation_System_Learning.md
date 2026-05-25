========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical filename: 06_Shadow_Evaluation_System_Learning.md
Layer / subsystem: 06 — L6 Shadow Evaluation and System Learning (parent)
Parent file: docs/reference/README.md
Ownership surface: Completed-run runtime-exhaust ingest; observer-law / surface isolation; outcome and governance evaluation; human calibration; signal fusion / RCA / pattern synthesis; proposal drafting and admission gate; gauntlet approval; UWG promotion for future-run learning; memory promotion interface; L6-specific observability and KPI tests.
Overwrite mode: full-file, no-overlap, executable contract
No-overlap boundary: L6 observes and proposes only. It does not mutate the current run, write L4 directly, or rescue any active run. L6 promotes only through UWG for **future** runs.
Source authority notes: Anchored on `00X` REQ_ID registry; aligned with constitutional §22, §23, §24.
Predecessor preserved at: `06_Shadow_Evaluation_System_Learning.md.pre-reqid-rewrite.bak`
========================================================================================================================

1. PURPOSE
------------------------------------------------------------------------------------------------------------------------
This parent uniquely owns:
- the rule that L6 consumes only sealed `RuntimeExhaustBundle` from completed runs
- the rule that L6 mutates nothing in the current run
- the rule that L6 promotes only through UWG, only for future runs
- the eval-before-learning contract (no proposal without prior evaluation)
- the gauntlet-approval contract before any UWG-promoted learning artifact

It does **not** own:
- per-stage detail (lives in `06.1`..`06.9`)
- runtime gates (00C), Exit (05), durable state (00B), certification (00A)

2. AUTHORITY BOUNDARY
------------------------------------------------------------------------------------------------------------------------
**Upstream inputs**: sealed `RuntimeExhaustBundle` from Exit; historical eval records; calibration inputs.
**Downstream outputs**: eval records, RCA records, proposals (drafts), gauntlet packets, promoted learning artifacts (via UWG).
**Forbidden behaviors**: mutating current run, writing L4 directly, promoting raw telemetry without eval, rescuing any active run.
**Allowed outputs only**: `EvalRecord`, `RCARecord`, `LearningProposal`, `GauntletPacket`, `LearningPromotionRequest` (to UWG only).

3. REQ_ID NAMESPACE
------------------------------------------------------------------------------------------------------------------------
This pack owns rows under `REQ-L6-*`.

4. ATOMIC REQUIREMENTS TABLE (PARENT-LEVEL INVARIANTS)
------------------------------------------------------------------------------------------------------------------------

| REQ_ID | Requirement | Owner | Inputs | Outputs | Runtime Evidence | OTEL Span | Artifact / Receipt | Validator | Negative Control | Expected Fail Reason | Replay Check | Release Gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `REQ-L6-NO-LIVE-MUTATION-001` | L6 MUST NOT mutate the current run; it observes only after Exit boundary. | 06 | (governance) | (none) | trace shows no `l6.*` spans inside any active `exit.run` | NOT_APPLICABLE: anti-pattern detection | `compiler_anti_cheat_findings.json` | `validator: l6_no_live_mutation_validator` (release-gate) | `NC-L6-LIVE-MUTATE-001`: L6 spans appear inside an active run | `l6_live_mutation_attempt` | `byte_identical` per fixture | DOC_ONLY |
| `REQ-L6-NO-DIRECT-L4-WRITE-001` | L6 MUST NOT write L4 directly. Promotions go through UWG. | 06 | (governance) | (none) | trace shows no `uwg.commit` originating from L6 modules; promotions emit `LearningPromotionRequest` to UWG | NOT_APPLICABLE | `compiler_anti_cheat_findings.json` | `validator: l6_no_direct_l4_write_validator` (release-gate) | `NC-L6-DIRECT-L4-WRITE-001`: L6 mutates L4 directly | `direct_l4_write_attempt` | `byte_identical` | DOC_ONLY |
| `REQ-L6-EXHAUST-INGEST-001` | L6 MUST consume only sealed `RuntimeExhaustBundle`; rejected/non-sealed inputs are FAIL. | 06.1 | sealed bundle | normalized eval input | bundle `sealed=true` and `content_hash` verified | `l6.exhaust_ingest` parent span | `l6_exhaust_ingest_receipt.json` | `validator: l6_exhaust_ingest_validator` (release-gate) | `NC-L6-INGEST-NONSEAL-001`: L6 ingests an unsealed bundle | `l6_ingested_unsealed_bundle` | `byte_identical` | DOC_ONLY |
| `REQ-L6-OBSERVER-ISOLATION-001` | L6 MUST run in a surface-isolated observer context: no shared mutable state with current runs. | 06.2 | exhaust input | (governance) | observer process boundaries enforced; cross-run isolation receipt | `l6.observer_isolation` span | `l6_isolation_receipt.json` | `validator: l6_observer_isolation_validator` (release-gate) | `NC-L6-CROSS-RUN-MUTATION-001`: L6 reads/writes a current-run state | `cross_run_state_access` | `byte_identical` | DOC_ONLY |
| `REQ-L6-EVAL-BEFORE-LEARN-001` | L6 MUST run an evaluation pass before any learning proposal; raw-telemetry promotion is FAIL. | 06.3, 06.6 | exhaust input | `EvalRecord` | every `LearningProposal.lineage` must include `eval_record_id` | `l6.eval` span | `eval_record.json` | `validator: l6_eval_before_learn_validator` (release-gate) | `NC-L6-RAW-PROMOTE-001`: proposal references no eval | `raw_telemetry_promotion` | `byte_identical` | DOC_ONLY |
| `REQ-L6-CALIBRATION-001` | L6 MUST support human calibration; eval seal MUST include calibration receipt when calibration was applied. | 06.4 | calibration input | calibrated eval | `eval_record.calibration_receipt_id?` | `l6.calibration` span | `calibration_receipt.json` | `validator: l6_calibration_validator` (release-gate) | `NC-L6-CALIB-FORGE-001`: calibration applied without human input | `calibration_forged` | `byte_identical` | DOC_ONLY |
| `REQ-L6-RCA-PATTERN-SYNTHESIS-001` | RCA records MUST link to evidence in the exhaust bundle and to the eval record; pattern synthesis MUST not invent unseen failure modes. | 06.5 | eval + exhaust | `RCARecord` | `rca_record` carries `evidence_refs[]` resolvable to exhaust | `l6.rca` span | `rca_record.json` | `validator: l6_rca_validator` (release-gate) | `NC-L6-RCA-FAB-001`: RCA cites unseen evidence | `rca_evidence_fabrication` | `byte_identical` | DOC_ONLY |
| `REQ-L6-PROPOSAL-ADMISSION-001` | L6 proposals MUST pass an admission gate (drafting + scope + safety preview) before reaching the gauntlet. | 06.6 | RCA + eval | `LearningProposal` | proposal carries `admission_receipt_id`, `scope_kind`, `safety_preview` | `l6.proposal_admit` span | `learning_proposal.json` | `validator: l6_admission_validator` (release-gate) | `NC-L6-PROPOSAL-SCOPE-LEAK-001`: proposal touches L5 cert authority | `proposal_scope_violation` | `byte_identical` | DOC_ONLY |
| `REQ-L6-GAUNTLET-APPROVAL-001` | A `LearningProposal` MUST pass the gauntlet (regression suite, replay tests, safety probes) before promotion. | 06.7 | proposal | `GauntletPacket` | gauntlet packet carries pass/fail per probe; promotion requires all-pass | `l6.gauntlet` span | `gauntlet_packet.json` | `validator: l6_gauntlet_validator` (release-gate) | `NC-L6-GAUNTLET-SKIP-001`: promotion without all-pass gauntlet | `gauntlet_bypass` | `byte_identical` | DOC_ONLY |
| `REQ-L6-PROMOTE-VIA-UWG-001` | L6 MUST promote learning artifacts only through UWG by emitting `LearningPromotionRequest`; UWG admits or rejects. | 06.7 | passed gauntlet | `LearningPromotionRequest` | request carries `gauntlet_packet_id`, `promotion_target_run` (a future run window) | `l6.promote_uwg` span | `learning_promotion_request.json` | `validator: l6_promote_uwg_validator` (release-gate) | `NC-L6-PROMOTE-DIRECT-001`: L6 writes promotion to L4 directly | `l6_direct_promotion_attempt` | `byte_identical` | DOC_ONLY |
| `REQ-L6-FUTURE-RUN-ONLY-001` | The promotion target MUST be a future run window; mid-run promotions are FAIL. | 06.7 | promotion request | UWG receipt | `promotion_target_run.kind=future_run`; current `run_id` excluded | `l6.future_window` event | `learning_promotion_request.json` | `validator: l6_future_run_validator` (release-gate) | `NC-L6-MID-RUN-PROMO-001`: promotion targets the active run | `mid_run_promotion_attempt` | `byte_identical` | DOC_ONLY |
| `REQ-L6-MEMORY-PROMOTION-IFACE-001` | The L6 memory promotion interface MUST present typed inputs/outputs and never bypass UWG. | 06.9 | memory promotion request | UWG receipt | `memory_promotion_iface.schema_id` validated | `l6.memory_promote` span | `memory_promotion_record.json` | `validator: l6_memory_promotion_validator` (release-gate) | `NC-L6-MEM-DIRECT-001`: memory promoted without UWG | `memory_direct_write_attempt` | `byte_identical` | DOC_ONLY |
| `REQ-L6-OBSERVABILITY-001` | L6 MUST emit observability and KPI signals on every ingest, eval, RCA, proposal, gauntlet, promotion event. | 06.8 | every L6 stage | observability stream | every event logged | `l6.observability` span | `l6_observability.json` | `validator: l6_observability_validator` (release-gate) | `NC-L6-DARK-PROMOTION-001`: promotion not logged | `l6_dark_promotion` | `byte_identical` | DOC_ONLY |

5. RUNTIME EVIDENCE CONTRACT
------------------------------------------------------------------------------------------------------------------------
`EvalRecord` MUST carry: `eval_record_id`, `source_exhaust_bundle_id`, `eval_kind`, `metrics`, `calibration_receipt_id?`, `policy_hash`, `blueprint_hash`, `replay_key`, `content_hash`, `lineage`.

`LearningProposal` MUST carry: `proposal_id`, `eval_record_ids[]`, `rca_record_ids[]`, `scope_kind`, `admission_receipt_id`, `policy_hash`, `blueprint_hash`, `content_hash`, `lineage`.

`GauntletPacket` MUST carry: `gauntlet_packet_id`, `proposal_id`, `probe_results[]`, `aggregate_status` ∈ {`all_pass`, `fail`}, `content_hash`.

`LearningPromotionRequest` MUST carry: `promotion_request_id`, `gauntlet_packet_id`, `promotion_target_run` (future window descriptor), `staged_diff_hash`, `policy_hash`, `blueprint_hash`, `replay_key`, `content_hash`.

6. OTEL SPAN CONTRACT
------------------------------------------------------------------------------------------------------------------------
Required spans (children of `l6.run`): `l6.exhaust_ingest`, `l6.observer_isolation`, `l6.eval`, `l6.calibration`, `l6.rca`, `l6.proposal_admit`, `l6.gauntlet`, `l6.promote_uwg`, `l6.future_window`, `l6.memory_promote`, `l6.observability`.

Required attributes: `req_id`, `source_run_id`, `eval_record_id?`, `proposal_id?`, `gauntlet_packet_id?`, `policy_hash`, `blueprint_hash`, `replay_key`.

7. VALIDATOR CONTRACT
------------------------------------------------------------------------------------------------------------------------
- `l6_no_live_mutation_validator`, `l6_no_direct_l4_write_validator`, `l6_exhaust_ingest_validator`, `l6_observer_isolation_validator`, `l6_eval_before_learn_validator`, `l6_calibration_validator`, `l6_rca_validator`, `l6_admission_validator`, `l6_gauntlet_validator`, `l6_promote_uwg_validator`, `l6_future_run_validator`, `l6_memory_promotion_validator`, `l6_observability_validator` (all release-gate)

8. NEGATIVE CONTROL CONTRACT
------------------------------------------------------------------------------------------------------------------------
Each `NC-L6-*` row in §4 is mandatory. Critical-severity controls: `NC-L6-LIVE-MUTATE-001`, `NC-L6-DIRECT-L4-WRITE-001`, `NC-L6-RAW-PROMOTE-001`, `NC-L6-GAUNTLET-SKIP-001`, `NC-L6-PROMOTE-DIRECT-001`, `NC-L6-MID-RUN-PROMO-001`, `NC-L6-MEM-DIRECT-001`.

9. REPLAY CONTRACT
------------------------------------------------------------------------------------------------------------------------
For fixed `(RuntimeExhaustBundle, eval config, calibration input, policy_hash, blueprint_hash, seed)`, `EvalRecord`, `RCARecord`, `LearningProposal`, `GauntletPacket`, and `LearningPromotionRequest` `content_hash` MUST replay byte-identical. Allowed nondeterminism: ids, span_id, trace_id, timestamps.

10. RELEASE GATE CONTRACT
------------------------------------------------------------------------------------------------------------------------
A 06 row's `Release Gate` is `PASS` only when: no live mutation; no direct L4 write; ingest only sealed bundles; observer isolated; eval before learn; calibration honored; RCA evidence-linked; admission gate run; gauntlet all-pass; promotion via UWG; future-run only; memory interface respects UWG; observability complete.

11. NO-OVERLAP LOCK
------------------------------------------------------------------------------------------------------------------------
**This file owns**: L6 shadow evaluation and learning-promotion invariants.

**Related files own**: per-stage detail in `06.1`..`06.9`; `v6_coverage_matrix.md` is historical (subsumed by `00X` registry per `00X §13`); `06_Shadow_Evaluation_System_Learning_exec.md` is an exec-summary copy and is non-normative.

**Forbidden duplicated ownership**: L6 MUST NOT mutate current run, write L4 directly, replace runtime gates (00C), Exit (05), or certification (00A).

**Forbidden output vocabulary**: `ALLOW_FINISH`, `DENY`, `REROUTE`, `ESCALATE_HITL`, `COMMIT_REQUEST_TO_UWG` (as final), `SAFE_FALLBACK` (as final), `durable_write_committed`, `policy_certified`, `route_changed`, `workflow_expanded`, `evidence_contract_issued`, `prompt_envelope_constructed`. The token `learning_promoted` is allowed only inside a UWG receipt issued for an L6 `LearningPromotionRequest`.

12. CHILD FILE MAP
------------------------------------------------------------------------------------------------------------------------
- `06.1_L6_Runtime_Exhaust_Ingest_and_Normalization.md` — `REQ-L6-INGEST-*`
- `06.2_L6_Observer_Law_Isolation_Eval_Readiness.md` — `REQ-L6-OBSERVER-*`
- `06.3_L6_Outcome_Trajectory_Governance_Eval.md` — `REQ-L6-EVAL-*`
- `06.4_L6_Human_Calibration_and_Eval_Record_Seal.md` — `REQ-L6-CALIB-*`
- `06.5_L6_Signal_Fusion_RCA_and_Pattern_Synthesis.md` — `REQ-L6-RCA-*`
- `06.6_L6_Proposal_Drafting_and_Admission_Gate.md` — `REQ-L6-PROPOSAL-*`, `REQ-L6-ADMISSION-*`
- `06.7_L6_Gauntlet_Approval_UWG_Promotion_FutureRun.md` — `REQ-L6-GAUNTLET-*`, `REQ-L6-PROMOTE-*`
- `06.8_L6_Observability_KPI_Tests_and_Anti_Bypass.md` — `REQ-L6-OBS-*`, `REQ-L6-ANTIBYPASS-*`
- `06.9_L6_Memory_Promotion_Interface.md` — `REQ-L6-MEM-*`

NOTE: Duplicate filenames `06.2_L6_Observer_Law_Surface_Isolation_and_Eval_Readiness.md`, `06.3_L6_Outcome_Trajectory_and_Governance_Evaluation.md`, `06.7_L6_Gauntlet_Approval_UWG_Promotion_and_Future_Run_Publish.md` are deduped: canonical names are the ones above (no `_and_` infix). Duplicates flagged for archive in `00X §13 superseded ledger`.

13. ACCEPTANCE CRITERIA
------------------------------------------------------------------------------------------------------------------------
- Every parent invariant row in §4 has all 13 cells filled.
- Forbidden output vocabulary in §11 reproduces the global ban.
- The 9 child files own per-stage REQ_IDs (deferred for full conversion).
- "No live mutation" rule is binding.
- "Eval before learn" rule is binding.
- "Promote only through UWG" rule is binding.
- "Future-run only" rule is binding.

END OF 06 — L6 SHADOW EVALUATION SYSTEM LEARNING PARENT
========================================================================================================================
