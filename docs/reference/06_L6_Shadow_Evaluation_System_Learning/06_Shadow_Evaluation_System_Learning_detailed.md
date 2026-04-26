========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical folder: 06_L6_Shadow_Evaluation_System_Learning
Canonical file: 06_Shadow_Evaluation_System_Learning_detailed.md
Overwrite mode: full-file, no-overlap, implementation-grade, source-refreshed
Source refreshed from: 06_Shadow_Evaluation_System_Learning_detailed.md
Owner summary: L6 after-runtime shadow evaluation and future-run learning only. Owns sealed exhaust ingest, evaluation, calibration, RCA, proposals, gauntlet, and UWG promotion requests.

GLOBAL NO-OVERLAP LAW
- 00A L5 owns governance certification evidence, not live runtime dispositions and not durable write admission.
- 00B L4/UWG owns durable system-of-record state and durable write admission, not planning, routing, retrieval, execution, Exit disposition, or L6 learning mechanics.
- 00C Runtime Gates owns G01-G29 current-run GateVerdict law, not final Exit X3 aggregation and not L5 certification evidence.
- 00X owns traceability and no-loss mapping only.
- 01 Intake owns request envelope validation and identity/session/tenant baseline only.
- 02 L1 owns advisory interpretation and planning only.
- 03 L0/L3 owns deterministic route selection and optional workflow orchestration only.
- C0 owns retrieval/evidence contracts only.
- PA owns prompt packet construction only.
- 04 L2 owns bounded execution and sealing only.
- 05 Exit owns current-run checkout aggregation and exactly one X3 disposition only.
- 06 L6 owns completed-run evaluation, RCA, and future-run learning proposals only.
- 99 owns proof harnesses only; it does not own runtime behavior.

REFERENCE POINTERS
- Cross-cutting governance/certification evidence: 00A_L5_Governance_Safety/
- Durable state and Universal Write Gateway: 00B_L4_State_Archive_and_UWG/
- Current-run reusable gate mesh: 00C_Runtime_Gates_Current_Run_Mesh/
- Traceability and zero-loss proof: 00X_Requirements_Traceability_and_No_Loss_Map.md
- End-to-end runtime proof harness: 99_End_to_End_Runtime_Proof_and_Acceptance/
========================================================================================================================

========================================================================================================================
06_Shadow_Evaluation_System_Learning_detailed.md
PARENT L6 SHADOW EVALUATION -> FUTURE-RUN LEARNING DOCTRINE
NO-OVERLAP FULL OVERWRITE
========================================================================================================================

PURPOSE
------------------------------------------------------------------------------------------------------------------------
This parent file defines L6 as the completed-run shadow evaluation and future-run learning plane.

L6 reads sealed runtime exhaust after the current run has already crossed the runtime boundary. It normalizes evidence,
evaluates outcomes and trajectories, calibrates graders, detects drift, isolates root causes, drafts future-run improvement
proposals, proves those proposals under replay/regression gauntlets, and hands approved promotion packets to UWG for
future-run materialization into L4.

L6 is not a live runtime layer. L6 does not rescue the current run. L6 does not directly mutate L4. L6 does not route,
retrieve, assemble prompts, execute tools, decide current-run gates, certify L5 evidence, or approve current-run egress.

CANONICAL SEQUENCE LAW
------------------------------------------------------------------------------------------------------------------------
Observe completed run exhaust only
  -> Normalize and bind lineage
  -> Evaluate outcome, trajectory, governance, and calibration
  -> Seal eval records
  -> Fuse evaluated signals
  -> RCA and pattern synthesis
  -> Draft proposal packets
  -> Admit complete proposals to gauntlet
  -> Prove through replay/regression/safety checks
  -> Approve, reject, or hold
  -> UWG writes approved future-run state to L4
  -> BUS U activates only at future run_start

NEVER:
- Observe -> mutate live run.
- Raw trace -> learning promotion.
- Human preference -> policy without rubric/calibration.
- Failed run -> silent prompt patch.
- L6 proposal -> direct L4 write.
- After-hours analysis -> retroactive current-run disposition.

SOURCE OWNERSHIP BOUNDARY
------------------------------------------------------------------------------------------------------------------------
L6 owns after-runtime learning mechanics only. It consumes sealed exhaust after Exit/HITL/UWG have completed their
current-run work. It may analyze, grade, calibrate, root-cause, propose, prove, and package future-run updates.

L6 DOES NOT OWN:
- current-run request validation, planning, routing, retrieval, prompt assembly, execution, exit disposition, live runtime
  gates, L5 certification, UWG durable write admission, or L4 system-of-record storage.

SOURCE FILES TO RESPECT WITHOUT RESTATING THEIR DETAIL:
- agentic_system_process_map_exec.md: top-level runtime map and cross-cutting planes.
- 00A_L5_Governance_Safety/00A_L5_Governance_Safety_detailed.md and children: certification evidence, policy/auth/egress/replay evidence.
- 00B_L4_State_Archive_and_UWG/00B_L4_State_Archive_and_UWG_detailed.md and children: durable state, UWG write admission, read-surface refresh.
- 01_request_intake_detailed.md and children: validated request envelope only.
- 02_L1_Reasoning_Plan_Generation_detailed.md and children: notepad plan only.
- 03_L0_Route_Decision_Switching_L3_detailed.md and children: route and managed workflow authority.
- C0_Context_Engine_detailed.md and children: evidence retrieval and FinalEvidenceContract.
- Prompt_Assembly_detailed.md and children: signed prompt packet assembly.
- 04_L2_Execute_detailed.md and children: bounded execution and sealed artifacts.
- 05_Live_Runtime_Exit_Control_&_Evaluation_detailed.md and children: current-run checkout and X3 disposition.
- 00C_Runtime_Gates_Current_Run_Mesh/: G01-G29 live runtime gate verdicts.

GLOBAL NO-OVERLAP LOCK
------------------------------------------------------------------------------------------------------------------------
- U0 / Intake owns request envelope validation and request identity stamping.
- L1 owns intent interpretation, task_spec, query_spec, ambiguity register, and plan recommendation.
- L0 owns route selection and RouteContract authority.
- C0 owns evidence retrieval, shaping, verification, support score, and FinalEvidenceContract.
- Prompt Assembly owns signed provider-ready PromptEnvelope / CompiledPromptArtifact construction.
- L3 owns managed workflow shaping, ready-node selection, joins, retries, and workflow checkpoints.
- L2 owns bounded execution, local repair, proposed_state_diff creation, and sealed execution artifacts.
- Runtime Gates own G01-G29 live gate verdicts and bounded runtime gate dispositions.
- Exit Eval owns current-run checkout, X1/X2/X3 disposition, HITL review flow, and CommitRequest handoff.
- L5 owns policy, authority, origin-trust, egress, HITL re-clearance, replay/audit certification evidence.
- UWG owns durable write admission, write locks, atomic commit, rollback, and commit receipts.
- L4 owns durable system-of-record state and read surfaces.
- L6 owns completed-run exhaust ingestion, shadow evaluation, calibration, RCA, proposal drafting, gauntlet proof,
  promotion request packaging, and future-run learning activation attempts only.


CHILD FILE MAP
------------------------------------------------------------------------------------------------------------------------
06.1_L6_Runtime_Exhaust_Ingest_and_Normalization_detailed.md
- Owns: completed-run exhaust collection, RuntimeExhaustBundle, NormalizedEvidenceRecord, StageMap, ArtifactInventory.
- Does not own: observer-law enforcement, scoring, RCA, proposal, promotion, UWG commit.

06.2_L6_Observer_Law_Isolation_Eval_Readiness.md
- Owns: ObserverComplianceReceipt, denied-write detection, StageBarrierReceipt, EvalReadinessReceipt.
- Does not own: evaluation scoring, Exit dispositions, durable write admission, policy publishing.

06.3_L6_Outcome_Trajectory_Governance_Eval.md
- Owns: OutcomeEvalRecord, TrajectoryEvalRecord, GovernanceRegressionRecord.
- Does not own: live X1 gates, Runtime Gate verdicts, proposal drafting, promotion.

06.4_L6_Human_Calibration_and_Eval_Record_Seal_detailed.md
- Owns: CalibrationRecord, JudgeReliabilitySignal, CompletedEvalRecord, EvalRecordSealReceipt.
- Does not own: live HITL review, L5 re-clearance, rubric/policy publishing.

06.5_L6_Signal_Fusion_RCA_and_Pattern_Synthesis_detailed.md
- Owns: FusedSignalBundle, RCAPacket, FailureChain, PatternSynthesisRecord.
- Does not own: proposal drafting, gauntlet proof, writes, live remediation.

06.6_L6_Proposal_Drafting_and_Admission_Gate_detailed.md
- Owns: DraftProposalPacket, ProposedDiffManifest, ProposalAdmissionReceipt.
- Does not own: approval, committing, publishing, changing runtime behavior.

06.7_L6_Gauntlet_Approval_UWG_Promotion_FutureRun.md
- Owns: GauntletReceipt, ApprovalDecisionRecord, PromotionPacket, FutureRunActivationReceipt.
- Does not own: UWG internal write validation, L4 storage implementation, current-run mutation.

06.8_L6_Observability_KPI_Tests_and_Anti_Bypass_detailed.md
- Owns: L6 OTEL spans, KPI board, anti-bypass tests, proof commands, pack-level acceptance.
- Does not own: child business logic internals except black-box acceptance coverage.

FORBIDDEN L6 OUTPUTS / ACTIONS
------------------------------------------------------------------------------------------------------------------------
L6 MUST NOT output or perform any of the following as live runtime authority:
- ALLOW_FINISH, DENY, REROUTE, ESCALATE_HITL, SAFE_FALLBACK, COMMIT_REQUEST_TO_UWG as current-run disposition.
- Live route change, live threshold change, live prompt mutation, live policy mutation, live rubric mutation.
- Direct L4 write, direct cache promotion, direct memory promotion, direct registry update, direct policy publish.
- Current-run rescue, current-run regrade as disposition, retroactive justification of a failed run.
- Human preference as policy, raw telemetry as learning, unscored trace as proposal basis.
- Silent promotion, partial bypass, missing rollback, stale eval on write, disconnected evidence.

ALLOWED L6 OUTPUT STYLE
------------------------------------------------------------------------------------------------------------------------
- RuntimeExhaustBundle, NormalizedEvidenceRecord, ObserverComplianceReceipt, EvalReadinessReceipt.
- OutcomeEvalRecord, TrajectoryEvalRecord, GovernanceRegressionRecord, CalibrationRecord, CompletedEvalRecord.
- FusedSignalBundle, RCAPacket, PatternSynthesisRecord, DraftProposalPacket, ProposalAdmissionReceipt.
- GauntletReceipt, ApprovalDecisionRecord, PromotionPacket, FutureRunActivationReceipt.
- Recommendation hints only when explicitly marked future-run-only and non-authoritative until UWG/L4 materialization.

CANONICAL L6 OUTPUT VOCABULARY
------------------------------------------------------------------------------------------------------------------------
- READY_FOR_EVAL
- PARTIAL_BUT_SCORABLE
- HOLD_FOR_MISSING_EVIDENCE
- NON_EVALUABLE_PACKET
- EVAL_SEALED
- SIGNAL_FUSED
- RCA_COMPLETE
- PATTERN_CONFIRMED
- PROPOSAL_DRAFTED
- ADMIT_TO_GAUNTLET
- HOLD_FOR_MORE_EVIDENCE
- REJECT_WEAK_PROPOSAL
- REQUIRE_SME_REVIEW
- GAUNTLET_PASS
- GAUNTLET_FAIL
- APPROVED_FOR_UWG_REQUEST
- REJECTED_FOR_PROMOTION
- FUTURE_RUN_ACTIVATION_READY

These are L6 pipeline statuses, not live runtime dispositions.

ACCEPTANCE CRITERIA
------------------------------------------------------------------------------------------------------------------------
This L6 pack is complete only when:
- Parent and child ownership boundaries are MECE and aligned to the other requirements files.
- L6 is explicitly after-runtime and future-run-only.
- 6A ingest/normalize is separate from 6B evaluate.
- 6B evaluate is mandatory before 6C RCA/proposal.
- 6C RCA/proposal is separated from 6D promote/update.
- UWG remains the only durable write path into L4.
- Raw telemetry is explicitly not memory or learning.
- Human calibration is signal, not sovereign policy.
- Promotion requires eval, RCA, gauntlet, approval, rollback, audit, and future-run activation receipts.
- OTEL spans, KPIs, failure modes, anti-bypass tests, and proof commands are specified.

END OF PARENT L6 SHADOW EVALUATION -> FUTURE-RUN LEARNING DOCTRINE
========================================================================================================================
========================================================================================================================
GAP-CLOSED PARENT UPDATE | MEMORY PROMOTION INTERFACE
========================================================================================================================
06.9_L6_Memory_Promotion_Interface.md is now the canonical child for evaluated long-term memory promotion proposals. L6 proposes
future-run updates only. L4 stores durable memory only after UWG admission.
