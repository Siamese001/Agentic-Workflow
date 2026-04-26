========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical folder: 05_Exit_Evaluation_and_Control
Canonical file: 05_Live_Runtime_Exit_Control_&_Evaluation_detailed.md
Overwrite mode: full-file, no-overlap, implementation-grade, source-refreshed
Source refreshed from: 05_Live_Runtime_Exit_Control_&_Evaluation_detailed.md
Owner summary: Exit checkout and disposition. Owns ExitReviewPacket normalization, X1 checkout checks, X2 aggregation, exactly one X3 disposition, HITL freeze/reclear, UWG handoff, response return, and runtime exhaust.

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

│ [ Sealed L2 Artifacts ] OR [RET] Short-Circuit from L0       │ [ Cross-Cutting L5 Policy Plane ]
│ [ Optional sealed workflow package from L3 ]                 │ [ C1 Replay Guard + C2 Bell Tower + C4 UWG + C6 Night Board ]
                                ▼                                                              │
┌──────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ 5. EXIT EVAL & CONTROL — v6                                                                 │ │
│ [ THE CHECKOUT DESK FOR SEALED FOLDERS, SHORT-CIRCUITS, HUMAN REVIEW, AND REAL INK ]         │ │
│                                                                                              │ │
│ PURPOSE                                                                                      │ │
│ - This is the live runtime disposition layer.                                                 │ │
│ - It judges whether the current run can leave the system, be denied, be rerouted,             │ │
│   be escalated to human review, or request a durable commit through UWG.                      │ │
│ - It does not execute tools.                                                                 │ │
│ - It does not retrieve evidence.                                                             │ │
│ - It does not mutate L4.                                                                      │ │
│ - It does not let L6 learning rescue the current run.                                        │ │
│ - It turns sealed work into exactly one explicit runtime disposition.                         │ │
│                                                                                              │ │
│ LIBRARY PERSONA                                                                              │ │
│ - Checkout Reviewer: checks whether the sealed folder can leave the desk.                     │ │
│ - Commandant: enforces policy, safety, and authority boundaries.                              │ │
│ - Secure Reading Room: freezes risky work for bounded human review.                           │ │
│ - Master Clerk handoff: sends real ink requests only to UWG.                                  │ │
│ - Bell Tower listener: consumes live anomaly signals but does not learn live.                  │ │
│                                                                                              │ │
│ HARD AUTHORITY BOUNDARY                                                                      │ │
│ - L2 may produce work but cannot approve it.                                                  │ │
│ - L0 may route but cannot approve final output.                                               │ │
│ - L3 may orchestrate but cannot approve final output.                                         │ │
│ - HITL may advise, approve, reject, or modify as data, but cannot write directly.              │ │
│ - L6 may observe and grade, but cannot mutate or rescue the current run.                      │ │
│ - UWG is the only durable write path into L4.                                                 │ │
└──────────────────────────────────────────────────────────────────────────────────────────────┘ │
                                │                                                              │
                                │ [ sealed folder enters checkout ]                             │
                                ▼                                                              │
┌──────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ 5.0 INPUTS RECEIVED                                                                          │ │
├──────────────────────────────────────────────────────────────────────────────────────────────┤ │
│ Runtime source options                                                                        │ │
│ - Sealed L2 artifact from single-step execution.                                              │ │
│ - Sealed L3 workflow package containing multiple L2 step artifacts.                           │ │
│ - [RET] exact cache short-circuit from L0.                                                    │ │
│ - [RET] semantic cache short-circuit from L0.                                                 │ │
│ - [RET] fallback / abstain / clarify packet from L0.                                          │ │
│ - Re-cleared human-review packet from X3B after L5 re-clearance.                              │ │
│                                                                                              │ │
│ Required receipt fields                                                                       │ │
│ - run_id / request_id / session_id / trace_root.                                              │ │
│ - route_contract / route_id / execution_form / reason_codes.                                  │ │
│ - policy_hash / blueprint_hash / prompt_hash / replay_key.                                    │ │
│ - compliance_hash / manifest_hash / hmac_sig.                                                 │ │
│ - sandbox_envelope / capability_token / provider_lane.                                        │ │
│ - cost_tier / SLO slice / timeout / budget counters.                                          │ │
│ - terminal classification from L2, L3, or [RET].                                              │ │
│ - ExecTrace / tool calls / model calls / provider receipts.                                   │ │
│ - StateDiff / proposed mutation set / write intent class.                                     │ │
│ - evidence bundle / citations / support spans / source lineage.                               │ │
│ - C0 FinalEvidenceContract if grounding was required.                                         │ │
│ - PromptAssemblyStatus / CompiledPromptArtifact receipts.                                     │ │
│ - validation counters / retry counters / repair counters.                                     │ │
│ - trajectory snapshot for process grading.                                                    │ │
│ - grader composition vector + rubric weights.                                                 │ │
│ - track label: capability | regression | production | shadow-candidate.                       │ │
│ - support_score / confidence / abstain flags / contradiction flags.                           │ │
│ - OTel span set / timing offsets / anomaly flags.                                             │ │
│ - HITL packet if prior human review occurred.                                                 │ │
│                                                                                              │ │
│ Immediate fail before grading if missing                                                      │ │
│ - Missing policy_hash              -> POLICY_HASH_MISSING.                                    │ │
│ - Missing replay_key               -> REPLAY_KEY_MISSING.                                     │ │
│ - Missing route_contract           -> ROUTE_CONTRACT_MISSING.                                 │ │
│ - Missing terminal classification  -> TERMINAL_CLASS_MISSING.                                 │ │
│ - Missing sandbox_envelope for action -> SANDBOX_SCOPE_MISSING.                               │ │
│ - Missing capability_token for tool/model/action -> CAPABILITY_TOKEN_MISSING.                  │ │
│ - Missing evidence contract for grounded answer -> EVIDENCE_CONTRACT_MISSING.                 │ │
└──────────────────────────────────────────────────────────────────────────────────────────────┘ │
                                │                                                              │
                                │ [ normalize receipts ]                                       │
                                ▼                                                              │
┌──────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ 5.1 PRE-FLIGHT NORMALIZATION                                                                 │ │
├──────────────────────────────────────────────────────────────────────────────────────────────┤ │
│ N1 classify source                                                                            │ │
│ - L2_SEALED_ARTIFACT.                                                                         │ │
│ - L3_WORKFLOW_PACKAGE.                                                                        │ │
│ - RET_CACHE_EXACT.                                                                            │ │
│ - RET_CACHE_SEMANTIC.                                                                         │ │
│ - RET_FALLBACK.                                                                               │ │
│ - HITL_RECLEARED_PACKET.                                                                      │ │
│                                                                                              │ │
│ N2 normalize artifact                                                                         │ │
│ - Convert all source types into one ExitReviewPacket.                                         │ │
│ - Preserve original source_type, never flatten away lineage.                                  │ │
│ - Attach source authority labels.                                                            │ │
│ - Keep retrieved content as data, not instruction.                                            │ │
│ - Keep human review content as data, not sovereign authority.                                 │ │
│                                                                                              │ │
│ N3 bind run identity                                                                          │ │
│ - Verify request_id, trace_root, run_id, route_id, and replay_key agree.                      │ │
│ - Verify policy_hash and blueprint_hash match the route/execution snapshot.                   │ │
│ - Verify no hidden reroute occurred after L0 contract emission.                               │ │
│                                                                                              │ │
│ N4 declare disposition candidates                                                             │ │
│ - If answer-only and all gates pass -> X3D ALLOW / FINISH.                                    │ │
│ - If unsafe, invalid, unsupported, or policy-broken -> X3A DENY / REROUTE.                    │ │
│ - If ambiguous, low-confidence, high-impact, or judge-abstained -> X3B ESCALATE.              │ │
│ - If durable mutation is requested and gates pass -> X3C COMMIT REQUEST TO UWG.               │ │
│                                                                                              │ │
│ N5 attach live control signals                                                                │ │
│ - BUS D / BUS E live bell signals from L6 verification spine.                                 │ │
│ - Replay guard violations.                                                                    │ │
│ - Isolation anomalies.                                                                        │ │
│ - Drift or unusual trajectory warnings.                                                       │ │
│ - These signals can deny, reroute, or escalate the current run.                               │ │
│ - These signals cannot promote future learning during the current run.                        │ │
└──────────────────────────────────────────────────────────────────────────────────────────────┘ │
                                │                                                              │
                                │ [ begin X1 current-run evaluation ]                           │
                                ▼                                                              │
┌──────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ X1 CURRENT-RUN EVALUATION                                                                    │ │
│ outcome + process + safety + consistency + authority + evidence + replay                      │ │
├──────────────────────────────────────────────────────────────────────────────────────────────┤ │
│ Rule: all gates produce structured verdicts.                                                   │ │
│ Gate verdict format:                                                                          │ │
│   {gate_id, result, severity, reason_codes[], score, threshold, grader_type,                   │ │
│    evidence_refs[], replay_refs[], confidence, abstain_flag, remediation_hint}                 │ │
│                                                                                              │ │
│ Result enum                                                                                   │ │
│ - PASS       = clears the gate.                                                               │ │
│ - FAIL       = must deny, reroute, or escalate.                                                │ │
│ - WARN       = may proceed only if aggregate policy allows.                                    │ │
│ - UNKNOWN    = grader abstained or evidence insufficient, never fake pass.                     │ │
│ - NOT_APPLICABLE = gate not relevant for this disposition candidate.                           │ │
└──────────────────────────────────────────────────────────────────────────────────────────────┘ │
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ X1A TODAY'S RULES?                                                                            │
│ [ Policy Manifest + Threshold + Grader Roster Gate ]                                           │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ Checks                                                                                        │
│ - Load active policy manifest for tenant, route, task class, and risk tier.                    │
│ - Verify policy_hash equals the one bound in L0/L3/L2 packet.                                  │
│ - Verify blueprint_hash equals the approved workflow or single-step plan version.              │
│ - Verify prompt_hash if Prompt Assembly was involved.                                          │
│ - Verify grader roster and grader versions are allowed for this gate family.                   │
│ - Verify threshold profile for production, regression, or capability track.                    │
│ - Verify track label: capability | regression | production | shadow-candidate.                 │
│ - Verify pass^k θ/k policy for commit-path consistency.                                       │
│ - Verify tenant / ACL / region policy is still active.                                        │
│ - Verify no silent fallback to a different model/tool/provider occurred.                       │
│ - Verify no expired capability or sandbox token is being relied upon.                          │
│                                                                                              │
│ Output                                                                                        │
│ - policy_clearance = PASS / FAIL / UNKNOWN.                                                    │
│ - thresholds = {outcome, safety, support, trajectory, consistency}.                            │
│ - grader_roster = declared code, LLM-judge, hybrid, human-calibrated graders.                  │
│ - hard_fail if manifest mismatch or unknown policy.                                            │
│                                                                                              │
│ Fail routes                                                                                   │
│ - POLICY_CONFLICT -> X3A or X3B depending recoverability.                                      │
│ - POLICY_HASH_MISMATCH -> X3A.                                                                │
│ - GRADER_ROSTER_INVALID -> X3B.                                                               │
│ - THRESHOLD_PROFILE_MISSING -> X3B.                                                           │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ X1B ANSWERED IT?                                                                             │
│ [ Task Completion + Format + Instruction-Follow Gate ]                                        │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ Checks                                                                                        │
│ - Does the output answer the actual user task, not a nearby task?                              │
│ - Does the answer match requested format, schema, artifact type, and level of detail?          │
│ - Are required fields present?                                                                │
│ - Are prohibited fields absent?                                                               │
│ - Are refusal, abstain, clarify, or caveat behaviors appropriate?                              │
│ - Did output preserve user constraints and explicitly stated exclusions?                       │
│ - Did output avoid claiming completion for work not done?                                      │
│ - Did output avoid overriding higher-priority system/policy instructions?                      │
│ - Did output use committed artifact references only when UWG already completed?                │
│ - Did output preserve partial-credit semantics where allowed?                                  │
│                                                                                              │
│ Extra checks for [RET] cache                                                                  │
│ - Exact cache answer still satisfies freshness_class.                                          │
│ - Semantic cache match is above calibrated threshold.                                          │
│ - Reuse-safe task class confirmed.                                                            │
│ - Cached output did not bypass required grounding or policy posture.                           │
│                                                                                              │
│ Output                                                                                        │
│ - completion_score.                                                                           │
│ - schema_score.                                                                               │
│ - instruction_follow_score.                                                                   │
│ - refusal_fit_score.                                                                          │
│ - required_field_missing[].                                                                   │
│                                                                                              │
│ Fail routes                                                                                   │
│ - SCHEMA_VIOLATION -> X3A or repair if bounded.                                                │
│ - FORMAT_MISMATCH -> X3A or RETURN_TO_L1.                                                      │
│ - INSTRUCTION_BYPASS -> X3A.                                                                  │
│ - TASK_NOT_ANSWERED -> X3A / REROUTE.                                                         │
│ - OVERCLAIMED_COMPLETION -> X3A.                                                              │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ X1C SAFE TO LEAVE?                                                                           │
│ [ Sandbox + Mutation Authority + Side-Effect + Egress Gate ]                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ Checks                                                                                        │
│ - Sandbox isolation remained intact.                                                          │
│ - No hidden file, network, process, or provider egress occurred.                               │
│ - Capability token covers every invoked tool/model/action.                                     │
│ - Capability token was not expired, widened, reused, forged, or silently substituted.          │
│ - Side-effect class matches route_contract and sandbox_envelope.                               │
│ - StateDiff is proposal-only unless UWG commit already completed.                              │
│ - No direct L2 write to L4.                                                                    │
│ - No direct HITL write to L4.                                                                  │
│ - No direct L6 write to L4.                                                                    │
│ - No mutation occurred during human review freeze.                                             │
│ - No cross-trial state bleed.                                                                 │
│ - No same-run contamination from learning buses.                                               │
│ - No hidden retry changed policy, snapshot, or provider lane.                                  │
│                                                                                              │
│ Output                                                                                        │
│ - sandbox_status.                                                                             │
│ - mutation_auth_status.                                                                       │
│ - egress_status.                                                                              │
│ - isolation_status.                                                                           │
│ - side_effect_class.                                                                          │
│                                                                                              │
│ Fail routes                                                                                   │
│ - SANDBOX_BREACH -> X3A.                                                                      │
│ - UNAUTHORIZED_MUTATION -> X3A.                                                               │
│ - ENV_CONTAMINATED -> X3A.                                                                    │
│ - TRIAL_STATE_LEAK -> X3A.                                                                    │
│ - HIDDEN_EGRESS -> X3A.                                                                       │
│ - CAPABILITY_SCOPE_EXCEEDED -> X3A or X3B.                                                     │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ X1D ANSWER GOOD?                                                                             │
│ [ Groundedness + Faithfulness + Citation + Support Gate ]                                     │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ Checks                                                                                        │
│ - Claims are grounded in supplied evidence or explicitly marked as reasoning.                  │
│ - Required citations resolve to source_ids, spans, lines, or stable anchors.                   │
│ - C0 support_score clears threshold for grounded route.                                       │
│ - Citation support map covers material claims.                                                │
│ - No unsupported factual claims slipped into final answer.                                     │
│ - No evidence was distorted, cherry-picked, or over-generalized.                               │
│ - Contradiction flags are handled explicitly.                                                  │
│ - Weak evidence causes caveat, abstain, or reroute instead of fabricated certainty.            │
│ - Source freshness satisfies freshness_class.                                                  │
│ - LLM-judge abstain returns UNKNOWN, not fake pass.                                            │
│ - Judge calibration profile is valid.                                                         │
│                                                                                              │
│ C0 status handling                                                                            │
│ - PASS -> may proceed if other gates pass.                                                     │
│ - WEAK_WITH_CAVEATS -> may allow only with caveats or safe partial.                            │
│ - CONFLICTED -> require explicit contradiction handling or escalate.                           │
│ - EMPTY -> deny, abstain, or reroute.                                                         │
│ - BLOCKED -> deny or return safe bounded explanation.                                         │
│                                                                                              │
│ Output                                                                                        │
│ - groundedness_score.                                                                         │
│ - faithfulness_score.                                                                         │
│ - citation_precision.                                                                         │
│ - citation_recall.                                                                            │
│ - contradiction_handling_score.                                                               │
│ - unsupported_claims[].                                                                       │
│                                                                                              │
│ Fail routes                                                                                   │
│ - UNGROUNDED -> X3A.                                                                          │
│ - CITATION_INVALID -> X3A or repair if bounded.                                                │
│ - LOW_FAITHFULNESS -> X3A.                                                                    │
│ - EVIDENCE_EMPTY -> X3A / abstain.                                                            │
│ - CONFLICT_NOT_HANDLED -> X3B if material.                                                     │
│ - JUDGE_ABSTAINED -> X3B.                                                                     │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ X1E TRAJECTORY OK?                                                                           │
│ [ Process Quality + Tool Choice + Retry + Handoff Gate ]                                      │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ Checks                                                                                        │
│ - Right tool/model/action lane selected for the route contract.                                │
│ - Tool arguments were complete, precise, scoped, and policy-compatible.                        │
│ - Step order matched L3 workflow graph when L3 was involved.                                  │
│ - Single-step route did not secretly expand into workflow autonomy.                            │
│ - Managed workflow did not skip required dependencies, joins, or support checks.               │
│ - Retry behavior stayed within retry_count, repair_count, and oscillation thresholds.          │
│ - No tool thrash, provider thrash, or unproductive loop.                                       │
│ - Handoffs were correct: L0 -> C0/PA/L2, L0 -> L3, L3 -> L2, L2 -> Exit.                       │
│ - Repair stayed inside same blueprint_hash and policy_hash snapshot.                           │
│ - Best-partial artifact was emitted on timeout/SLO breach where appropriate.                   │
│ - Reasoning coherence and output alignment hold together.                                      │
│ - Process/output gap is explainable and safe.                                                  │
│                                                                                              │
│ Output                                                                                        │
│ - tool_selection_score.                                                                       │
│ - arg_precision_score.                                                                        │
│ - workflow_order_score.                                                                       │
│ - retry_health_score.                                                                         │
│ - handoff_score.                                                                              │
│ - process_output_gap_score.                                                                   │
│                                                                                              │
│ Fail routes                                                                                   │
│ - WRONG_TOOL -> X3A or RETURN_TO_L1.                                                          │
│ - ARG_EXTRACTION_FAIL -> X3A or bounded repair.                                                │
│ - STEP_INEFFICIENT -> WARN or X3A if severe.                                                   │
│ - REASONING_INCOHERENT -> X3A.                                                                │
│ - HANDOFF_MISROUTED -> X3A.                                                                   │
│ - TRAJECTORY_SUSPECT -> X3B.                                                                  │
│ - TRAJECTORY_INVALID -> X3A.                                                                  │
│ - RETRY_THRASH -> X3A / X3B.                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ X1F ADVERSARIAL OK?                                                                          │
│ [ Injection + Jailbreak + Leak + Robustness Gate ]                                            │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ Checks                                                                                        │
│ - Prompt injection resistance across user input, retrieved content, tool output, and HITL text.│
│ - Jailbreak or role-escape patterns absent or safely neutralized.                              │
│ - System/developer/policy prompt leakage absent.                                               │
│ - Tool output did not smuggle instructions into answer synthesis.                              │
│ - Retrieved documents were treated as data, not instruction.                                   │
│ - Human review edits were treated as data and re-cleared.                                      │
│ - Malformed payloads did not crash or coerce unsafe behavior.                                  │
│ - Coercive, threatening, reward-hacking, or authority-claiming payloads did not override rules. │
│ - Bias/fairness deltas within policy thresholds where relevant.                                │
│ - Sensitive data boundaries preserved.                                                        │
│                                                                                              │
│ Output                                                                                        │
│ - injection_status.                                                                           │
│ - jailbreak_status.                                                                           │
│ - leak_status.                                                                                │
│ - robustness_status.                                                                          │
│ - bias_delta_status.                                                                          │
│                                                                                              │
│ Fail routes                                                                                   │
│ - PROMPT_INJECTION_DETECTED -> X3A.                                                           │
│ - SYSTEM_PROMPT_LEAK -> X3A.                                                                  │
│ - JAILBREAK_DETECTED -> X3A.                                                                  │
│ - ADVERSARIAL_CRASH -> X3A.                                                                   │
│ - ADVERSARIAL_DETECTED -> X3A / X3B.                                                          │
│ - BIAS_DELTA_EXCEEDED -> X3B or X3A depending policy.                                         │
│ - TOOL_OUTPUT_INJECTION -> X3A.                                                               │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ X1G CONSISTENCY MODIFIER pass^k                                                              │
│ [ Commit-Path Reliability Gate, Not General Analytics ]                                       │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ Scope                                                                                         │
│ - Applies as a hard runtime gate only to X3C commit request candidates.                        │
│ - Applies as advisory telemetry for X3D answer-only allow.                                     │
│ - Does not use pass@k as a runtime gate.                                                       │
│ - pass@k remains analytics for capability-track hill-climb and future learning.                │
│                                                                                              │
│ Checks                                                                                        │
│ - Identify trajectory_class from current run.                                                  │
│ - Inspect recent same-class trajectories from BUS T.                                           │
│ - Compute recent k-trial reliability.                                                         │
│ - Require pass^k >= θ from X1A policy.                                                        │
│ - Customer-facing durable commit uses high θ, e.g. .95.                                       │
│ - Internal reversible commit may use lower θ, e.g. .85.                                       │
│ - High-impact or irreversible action may require θ plus HITL.                                 │
│ - Low sample size returns UNKNOWN, not fake pass.                                              │
│ - Drifted trajectory class invalidates reuse of old reliability.                               │
│                                                                                              │
│ Output                                                                                        │
│ - consistency_status = PASS / FAIL / UNKNOWN / NOT_APPLICABLE.                                │
│ - trajectory_class.                                                                           │
│ - k_window.                                                                                   │
│ - theta.                                                                                      │
│ - pass_power_estimate.                                                                        │
│ - sample_quality.                                                                             │
│                                                                                              │
│ Fail routes                                                                                   │
│ - CONSISTENCY_FAIL -> X3B.                                                                    │
│ - CONSISTENCY_UNKNOWN_FOR_HIGH_IMPACT -> X3B.                                                  │
│ - TRAJECTORY_CLASS_DRIFT -> X3B.                                                              │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ X1H REPLAY & DETERMINISM OK?                                                                 │
│ [ C1 Deterministic Replay Integrity Gate ]                                                    │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ Checks                                                                                        │
│ - Same input + same envelope + same policy_hash + same read snapshot has stable digest.        │
│ - No wall clock effects inside guarded run.                                                    │
│ - No raw entropy, uuid4, nondeterministic IDs, or unstable provider metadata.                   │
│ - Network calls were snapshotted, sealed, or explicitly outside replay-critical path.          │
│ - State reads came from one declared snapshot.                                                  │
│ - Policy mismatch invalidates replay certification.                                            │
│ - Replay receipts exist for model/tool calls.                                                  │
│ - Timing offsets are recorded without affecting decisions.                                     │
│                                                                                              │
│ Output                                                                                        │
│ - determinism_status.                                                                         │
│ - replay_digest.                                                                              │
│ - snapshot_manifest_status.                                                                   │
│ - nondeterminism_flags[].                                                                     │
│                                                                                              │
│ Fail routes                                                                                   │
│ - NON_REPLAYABLE -> X3A / X3B.                                                                │
│ - HIDDEN_TIME -> X3A.                                                                         │
│ - RAW_ENTROPY -> X3A.                                                                         │
│ - MIXED_STATE_READS -> X3A.                                                                   │
│ - POLICY_MISMATCH -> X3A.                                                                     │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ X1I OBSERVABILITY COMPLETE?                                                                  │
│ [ C2 Trace, Metrics, Bell Signal, Evidence Seal Gate ]                                        │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ Checks                                                                                        │
│ - OTel trace_root exists and spans cover L0/L3/L2/Exit/HITL/UWG if applicable.                 │
│ - Tool/model invocation spans have provider, latency, cost, retry, and error metadata.         │
│ - Exit disposition span exists and has final X3 outcome.                                       │
│ - Replay_key, policy_hash, blueprint_hash, and route_id appear in trace attributes.            │
│ - Evidence bundle, citation map, state diff, and artifact IDs are linkable.                    │
│ - BUS D/E live bell signals consumed before disposition.                                      │
│ - BUS T telemetry exhaust sealed for future learning.                                         │
│ - No observability gap blocks forensic replay.                                                 │
│                                                                                              │
│ Output                                                                                        │
│ - trace_completeness_score.                                                                   │
│ - span_coverage_map.                                                                          │
│ - evidence_seal_status.                                                                       │
│ - anomaly_flags[].                                                                            │
│                                                                                              │
│ Fail routes                                                                                   │
│ - TRACE_MISSING -> X3B for high-impact, WARN for low-risk answer-only.                         │
│ - SPAN_COVERAGE_GAP -> X3B if material.                                                       │
│ - EVIDENCE_SEAL_FAILED -> X3A / X3B.                                                          │
│ - LIVE_BELL_SIGNAL_UNCONSUMED -> X3B.                                                         │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ X1J WRITE ELIGIBILITY OK?                                                                    │
│ [ C4 UWG Pre-Commit Eligibility Gate ]                                                        │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ Applies when StateDiff, external action, durable memory update, policy update, artifact       │
│ publication, or customer-impacting change is requested.                                       │
│                                                                                              │
│ Checks                                                                                        │
│ - Is the proposed change necessary, explicit, and within user/request scope?                   │
│ - Is write_intent_class declared?                                                             │
│ - Is StateDiff complete and bounded?                                                          │
│ - Does diff scope match capability_token and sandbox_envelope?                                 │
│ - Is blast radius classified?                                                                 │
│ - Is rollback plan present where required?                                                     │
│ - Are before/after snapshots available?                                                       │
│ - Is high-impact or irreversible action routed through HITL?                                   │
│ - Has X1A-F cleared?                                                                          │
│ - Has X1G cleared if commit path is active?                                                    │
│ - Is UWG the next hop, not direct L4 write?                                                     │
│                                                                                              │
│ Output                                                                                        │
│ - write_eligibility_status.                                                                   │
│ - write_intent_class.                                                                         │
│ - blast_radius.                                                                               │
│ - rollback_required.                                                                          │
│ - uwg_handoff_packet_id.                                                                      │
│                                                                                              │
│ Fail routes                                                                                   │
│ - WRITE_SCOPE_AMBIGUOUS -> X3B.                                                               │
│ - WRITE_NOT_AUTHORIZED -> X3A.                                                                │
│ - ROLLBACK_MISSING -> X3B.                                                                    │
│ - HIGH_IMPACT_NEEDS_HITL -> X3B.                                                              │
│ - DIRECT_L4_WRITE_ATTEMPT -> X3A.                                                             │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ GRADER COMPOSITION CONTRACT                                                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ Every gate declares                                                                           │
│ - grader_type: code | LLM-judge | hybrid | human-calibrated.                                  │
│ - rubric dimensions.                                                                          │
│ - binary / weighted / hybrid scoring.                                                         │
│ - threshold source from X1A policy manifest.                                                   │
│ - score aggregation method.                                                                   │
│ - allowed partial-credit zones.                                                               │
│ - fail-closed conditions.                                                                      │
│ - abstain behavior.                                                                            │
│ - calibration lineage.                                                                         │
│                                                                                              │
│ Hard rules                                                                                    │
│ - Code graders decide structural facts where possible.                                         │
│ - LLM-judges handle semantic quality only when code cannot decide.                             │
│ - Hybrid graders must expose which part was code and which part was judgment.                  │
│ - Human-calibrated graders use SME labels as calibration data, not live authority.             │
│ - Abstain returns UNKNOWN, never fake pass.                                                     │
│ - Judge context is isolated from graded agent output.                                          │
│ - Grader cannot be steered by the answer being graded.                                         │
│ - Grader cannot see hidden instructions unless explicitly authorized by policy.                 │
│ - Calibration samples flow to BUS P / BUS T after runtime boundary only.                       │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ X2 AGGREGATE DECISION MATRIX                                                                 │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ Hard fail conditions                                                                          │
│ - Any safety breach.                                                                          │
│ - Any unauthorized mutation.                                                                  │
│ - Any policy hash mismatch.                                                                   │
│ - Any system prompt leak.                                                                     │
│ - Any known prompt injection not neutralized.                                                  │
│ - Any direct L4 write attempt outside UWG.                                                     │
│ - Any material unsupported claim in grounded answer.                                           │
│ - Any non-replayable high-impact action.                                                       │
│                                                                                              │
│ Escalation conditions                                                                         │
│ - Human-required by policy.                                                                   │
│ - High-impact or irreversible action.                                                         │
│ - Low confidence on material issue.                                                           │
│ - Judge abstained on material quality/safety.                                                  │
│ - Evidence conflicted and user impact is material.                                             │
│ - Consistency failed or unknown for commit path.                                               │
│ - Trace gap blocks forensic review.                                                           │
│ - Human modification proposed.                                                                │
│                                                                                              │
│ Allow conditions                                                                              │
│ - Answer-only, no durable mutation.                                                           │
│ - X1A-F clear.                                                                                │
│ - X1H/I clear or non-material WARN allowed by policy.                                         │
│ - Evidence support adequate or caveated/abstained properly.                                    │
│ - Output schema satisfied.                                                                    │
│                                                                                              │
│ Commit-request conditions                                                                      │
│ - Mutation requested and authorized.                                                          │
│ - X1A-F clear.                                                                                │
│ - X1G clear.                                                                                  │
│ - X1H/I clear.                                                                                │
│ - X1J clear.                                                                                  │
│ - HITL completed if required.                                                                 │
│ - Next hop is UWG only.                                                                       │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
            ┌───────────────────┼────────────────────┬────────────────────────┬───────────────────────┐
            │                   │                    │                        │                       │
            ▼                   ▼                    ▼                        ▼                       ▼
┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐
│ X3A DENY / REROUTE   │ │ X3B ESCALATE / HITL  │ │ X3C COMMIT REQUEST   │ │ X3D ALLOW / FINISH   │ │ X3E SAFE ABSTAIN     │
└──────────┬───────────┘ └──────────┬───────────┘ └──────────┬───────────┘ └──────────┬───────────┘ └──────────┬───────────┘
           │                        │                        │                        │                        │
           ▼                        ▼                        ▼                        ▼                        ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ X3A DENY / REROUTE                                                                                                         │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Meaning                                                                                                                    │
│ - The sealed work cannot safely leave as-is.                                                                               │
│ - The system either stops, returns a safe partial, or sends the task back for bounded replan.                               │
│ - No durable write.                                                                                                        │
│ - No commit.                                                                                                               │
│ - No hidden retry.                                                                                                         │
│                                                                                                                            │
│ Allowed sub-dispositions                                                                                                   │
│ - DENY_STOP: hard stop with safe explanation.                                                                              │
│ - DENY_SAFE_PARTIAL: return only the supported safe subset.                                                                 │
│ - REROUTE_TO_L1: plan repair required.                                                                                     │
│ - REROUTE_TO_L0: route classification was wrong or support path changed.                                                    │
│ - REROUTE_TO_C0: evidence weak and bounded retrieval retry allowed by route policy.                                         │
│ - REROUTE_TO_L2_REPAIR: schema or packaging repair only, no scope growth.                                                   │
│                                                                                                                            │
│ Required output packet                                                                                                     │
│ - disposition = X3A.                                                                                                       │
│ - reason_codes[].                                                                                                          │
│ - failed_gate_ids[].                                                                                                       │
│ - user_safe_message.                                                                                                       │
│ - safe_partial_artifact_id if applicable.                                                                                  │
│ - replan_hint if reroute allowed.                                                                                          │
│ - L6 failure packet.                                                                                                       │
│                                                                                                                            │
│ Reason codes                                                                                                               │
│ - POLICY_CONFLICT                    - HARD_FAIL                                                                            │
│ - POLICY_HASH_MISMATCH               - SCHEMA_VIOLATION                                                                    │
│ - FORMAT_MISMATCH                    - INSTRUCTION_BYPASS                                                                  │
│ - TASK_NOT_ANSWERED                  - OVERCLAIMED_COMPLETION                                                              │
│ - SANDBOX_BREACH                     - UNAUTHORIZED_MUTATION                                                               │
│ - ENV_CONTAMINATED                   - TRIAL_STATE_LEAK                                                                    │
│ - HIDDEN_EGRESS                      - CAPABILITY_SCOPE_EXCEEDED                                                           │
│ - UNGROUNDED                         - CITATION_INVALID                                                                    │
│ - LOW_FAITHFULNESS                   - EVIDENCE_EMPTY                                                                       │
│ - WRONG_TOOL                         - ARG_EXTRACTION_FAIL                                                                 │
│ - STEP_INEFFICIENT                   - REASONING_INCOHERENT                                                                │
│ - HANDOFF_MISROUTED                  - TRAJECTORY_INVALID                                                                  │
│ - RETRY_THRASH                       - PROMPT_INJECTION_DETECTED                                                           │
│ - SYSTEM_PROMPT_LEAK                 - JAILBREAK_DETECTED                                                                  │
│ - ADVERSARIAL_CRASH                  - ADVERSARIAL_DETECTED                                                                │
│ - BIAS_DELTA_EXCEEDED                - NON_REPLAYABLE                                                                      │
│ - HIDDEN_TIME                        - RAW_ENTROPY                                                                         │
│ - MIXED_STATE_READS                  - DIRECT_L4_WRITE_ATTEMPT                                                             │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ X3B ESCALATE / HUMAN REVIEW                                                                                               │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Trigger reasons                                                                                                            │
│ - POLICY_CONFLICT recoverable only by human decision.                                                                       │
│ - AMBIGUITY that affects safety, correctness, or irreversible action.                                                       │
│ - SILENT_FAILURE suspected.                                                                                                │
│ - LOW_CONFIDENCE on material answer or action.                                                                              │
│ - JUDGE_ABSTAINED on material gate.                                                                                         │
│ - CONSISTENCY_FAIL or consistency unknown for commit path.                                                                  │
│ - TRAJECTORY_SUSPECT.                                                                                                      │
│ - HUMAN_REQUIRED by policy.                                                                                                │
│ - HIGH_IMPACT_NEEDS_HITL.                                                                                                  │
│ - WRITE_SCOPE_AMBIGUOUS.                                                                                                   │
│ - ROLLBACK_MISSING.                                                                                                        │
│ - TRACE_GAP_MATERIAL.                                                                                                      │
│                                                                                                                            │
│ H1 FREEZE                                                                                                                  │
│ - auth_state = FROZEN.                                                                                                     │
│ - write_auth = NONE.                                                                                                       │
│ - capability token suspended.                                                                                              │
│ - pending diffs locked.                                                                                                    │
│ - provider egress paused.                                                                                                  │
│ - external action paused.                                                                                                  │
│ - no additional retrieval unless REQUEST_MORE_EVIDENCE is selected.                                                        │
│ - no durable write while under review.                                                                                      │
│                                                                                                                            │
│ H2 MATERIALIZE BOUNDED REVIEW PACKET                                                                                       │
│ - reason + evidence.                                                                                                       │
│ - input/request summary.                                                                                                   │
│ - route_contract + policy_hash + blueprint_hash.                                                                           │
│ - sealed L2 artifact, L3 package, or [RET] packet.                                                                          │
│ - proposed action/diff.                                                                                                    │
│ - write_intent_class and blast_radius if any mutation.                                                                      │
│ - rollback plan if applicable.                                                                                             │
│ - grader composition vector.                                                                                               │
│ - per-dimension scores + thresholds.                                                                                       │
│ - abstain/UNKNOWN outputs.                                                                                                 │
│ - trajectory snapshot.                                                                                                     │
│ - citation/source support map.                                                                                             │
│ - replay key + deterministic receipts.                                                                                     │
│ - pass^k evidence if consistency failed.                                                                                   │
│ - trace coverage map.                                                                                                      │
│ - anomaly flags from BUS D/E.                                                                                              │
│ - minimal necessary sensitive data only.                                                                                    │
│                                                                                                                            │
│ H3 HUMAN REVIEW                                                                                                            │
│ - Human inspects evidence, action, replay, and diff.                                                                        │
│ - Human compares proposed output/action to policy and intent.                                                               │
│ - Human confirms unsupported claims are removed or caveated.                                                                │
│ - Human confirms high-impact action posture.                                                                                │
│ - Human confirms rollback plan when needed.                                                                                 │
│ - Human cannot directly write L4.                                                                                          │
│ - Human cannot bypass L5.                                                                                                  │
│ - Human cannot widen scope without re-entry.                                                                               │
│ - Human corrections become untrusted data requiring re-clearance.                                                           │
│                                                                                                                            │
│ H4 DECISION                                                                                                                │
│ - APPROVE.                                                                                                                 │
│ - MODIFY_DIFF.                                                                                                             │
│ - REJECT.                                                                                                                  │
│ - RETURN_TO_L1 for replan.                                                                                                 │
│ - REQUEST_MORE_EVIDENCE if support weak.                                                                                   │
│ - REQUEST_REPLAY if determinism/replay is unclear.                                                                         │
│ - REQUEST_SCHEMA_REPAIR if only packaging failed.                                                                          │
│                                                                                                                            │
│ L5 RE-CLEARANCE GATE                                                                                                       │
│ - REJECT -> X3A DENY / STOP or RETURN_TO_L1.                                                                                │
│ - MODIFY_DIFF -> L5 re-clear -> re-hydrate packet -> restart relevant X1 gates.                                             │
│ - APPROVE -> L5 confirm -> X3D ALLOW or X3C COMMIT REQUEST.                                                                 │
│ - REQUEST_MORE_EVIDENCE -> bounded C0 re-entry only, no general open loop.                                                  │
│ - REQUEST_REPLAY -> replay check, then return to X1H/X1I.                                                                   │
│ - REQUEST_SCHEMA_REPAIR -> bounded L2 repair, then X1B/X1C/X1H.                                                             │
│ - Re-run X1A/X1C/X1F on any modified packet.                                                                                │
│ - Re-run X1D if answer/evidence changed.                                                                                   │
│ - Re-run X1E if process or tool plan changed.                                                                              │
│ - Re-run X1G if commit-path remains active.                                                                                │
│ - Re-run X1J if StateDiff changed.                                                                                         │
│                                                                                                                            │
│ Invariant                                                                                                                  │
│ - Human input = untrusted DATA until re-cleared.                                                                            │
│ - No human change bypasses L5 re-clear.                                                                                    │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ X3C COMMIT REQUEST -> UWG                                                                                                  │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Meaning                                                                                                                    │
│ - The runtime result is eligible to request durable mutation.                                                               │
│ - Exit does not write.                                                                                                     │
│ - Exit hands a commit request to UWG.                                                                                       │
│ - UWG verifies again and is the only real ink authority.                                                                    │
│                                                                                                                            │
│ Required preconditions                                                                                                      │
│ - X1A PASS.                                                                                                                │
│ - X1B PASS.                                                                                                                │
│ - X1C PASS.                                                                                                                │
│ - X1D PASS or NOT_APPLICABLE for non-grounded action.                                                                       │
│ - X1E PASS or policy-allowed WARN.                                                                                          │
│ - X1F PASS.                                                                                                                │
│ - X1G PASS.                                                                                                                │
│ - X1H PASS.                                                                                                                │
│ - X1I PASS or policy-allowed non-material WARN.                                                                             │
│ - X1J PASS.                                                                                                                │
│ - HITL completed if required.                                                                                              │
│                                                                                                                            │
│ UWG handoff packet                                                                                                         │
│ - commit_request_id.                                                                                                       │
│ - request_id / run_id / trace_root.                                                                                        │
│ - route_contract.                                                                                                          │
│ - policy_hash / blueprint_hash / replay_key.                                                                               │
│ - compliance_hash / hmac_sig.                                                                                              │
│ - capability_token and write authorization proof.                                                                           │
│ - StateDiff and write_intent_class.                                                                                         │
│ - before_snapshot / after_proposed_snapshot.                                                                                │
│ - rollback plan.                                                                                                           │
│ - blast_radius classification.                                                                                             │
│ - evidence/citation map if commit is evidence-backed.                                                                       │
│ - HITL decision receipt if applicable.                                                                                      │
│ - grader verdict bundle.                                                                                                   │
│ - pass^k consistency receipt.                                                                                              │
│ - replay/determinism digest.                                                                                               │
│ - trace/evidence seal.                                                                                                     │
│                                                                                                                            │
│ UWG sub-flow                                                                                                               │
│   U1 VERIFY BOSS                                                                                                           │
│   - Validate signature, compliance_hash, policy_hash, capability_token, and write authority.                                │
│   - Reject if token expired, scope widened, or policy drifted.                                                              │
│                                                                                                                            │
│   U2 CHECK CATALOG                                                                                                         │
│   - Verify RBAC, tenant, ACL, region, structure constraints, and blast radius.                                               │
│   - Validate before/after diff against L4 schema.                                                                           │
│   - Confirm no race with pending writes.                                                                                    │
│                                                                                                                            │
│   U3 CLAIM WRITE LOCK                                                                                                      │
│   - Serialize commit.                                                                                                      │
│   - Prevent ghost writes and overlapping mutations.                                                                         │
│   - Freeze conflicting commit requests.                                                                                    │
│                                                                                                                            │
│   U4 COMMIT + CHAIN APPEND                                                                                                 │
│   - Durable ledger write.                                                                                                  │
│   - Hash-chain audit append.                                                                                               │
│   - Sync to L4 archive.                                                                                                    │
│   - Emit commit receipt.                                                                                                   │
│                                                                                                                            │
│   U5 REFRESH READ SURFACES                                                                                                 │
│   - Alias swap.                                                                                                            │
│   - Cache invalidation.                                                                                                    │
│   - Retrieval surface refresh.                                                                                             │
│   - Next request sees updated state.                                                                                        │
│                                                                                                                            │
│ UWG outcomes                                                                                                               │
│ - COMMIT_ACCEPTED -> X3D may reference committed artifact.                                                                  │
│ - COMMIT_REJECTED -> X3A safe response or X3B review.                                                                       │
│ - COMMIT_HELD -> X3B pending review.                                                                                        │
│                                                                                                                            │
│ Invariant                                                                                                                  │
│ - UWG is the sole ink path into L4. No direct L2/HITL/L6 writes.                                                            │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ X3D ALLOW / FINISH -> RESPONSE / OUTCOME                                                                                   │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Meaning                                                                                                                    │
│ - Safe final runtime answer or outcome can leave the system.                                                               │
│ - No durable write occurs here.                                                                                            │
│ - If a durable commit was requested, final response may reference committed artifact only after UWG completed.              │
│                                                                                                                            │
│ Allowed response contents                                                                                                  │
│ - Patron answer only.                                                                                                      │
│ - Safe partial / caveated answer.                                                                                          │
│ - Explicit abstain where evidence is weak.                                                                                 │
│ - Committed artifact references only if X3C/UWG already completed.                                                         │
│ - Clear statement of unsupported gaps when needed.                                                                         │
│ - Schema-compliant final output.                                                                                           │
│ - Disposition receipt link or ID.                                                                                          │
│                                                                                                                            │
│ Prohibited response contents                                                                                               │
│ - Claiming an uncommitted mutation happened.                                                                               │
│ - Hiding weak support.                                                                                                     │
│ - Revealing system/developer/policy internals.                                                                             │
│ - Reusing quarantined retrieved content as instruction.                                                                     │
│ - Including unsafe or unapproved action results.                                                                            │
│                                                                                                                            │
│ Required output packet                                                                                                     │
│ - disposition = X3D.                                                                                                       │
│ - final_response.                                                                                                          │
│ - schema_status.                                                                                                           │
│ - evidence_status if grounded.                                                                                             │
│ - commit_receipt_id if relevant.                                                                                           │
│ - trace_root.                                                                                                              │
│ - runtime_exhaust_manifest.                                                                                                │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ X3E SAFE ABSTAIN / CLARIFY                                                                                                 │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Meaning                                                                                                                    │
│ - The safest valid outcome is to abstain, ask for critical missing information, or explain bounded inability.               │
│ - This is not failure when policy or evidence does not allow a safe answer.                                                 │
│ - No durable write.                                                                                                        │
│                                                                                                                            │
│ Triggers                                                                                                                   │
│ - Missing critical user detail.                                                                                            │
│ - Evidence EMPTY or BLOCKED.                                                                                               │
│ - Evidence WEAK where caveat would still be misleading.                                                                     │
│ - Unsupported high-impact advice.                                                                                          │
│ - Action scope ambiguous.                                                                                                  │
│ - User requested unsafe or impossible action.                                                                               │
│                                                                                                                            │
│ Required output packet                                                                                                     │
│ - disposition = X3E.                                                                                                       │
│ - abstain_reason.                                                                                                          │
│ - minimal clarification question if needed.                                                                                │
│ - safe alternative or bounded explanation.                                                                                 │
│ - failed_support_target if evidence-related.                                                                               │
│ - no commit request.                                                                                                       │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ RETURN TO CALLER (U0)                                                                                                      │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Returned payload                                                                                                           │
│ - final_response or safe abstain.                                                                                          │
│ - disposition receipt.                                                                                                     │
│ - committed L4 artifact references if and only if UWG completed.                                                           │
│ - safe partial artifact references if allowed.                                                                              │
│ - no hidden state mutation.                                                                                                │
│                                                                                                                            │
│ Runtime evidence retained                                                                                                  │
│ - ExitReviewPacket.                                                                                                        │
│ - X1 gate verdict bundle.                                                                                                  │
│ - X2 aggregate matrix output.                                                                                              │
│ - X3 disposition receipt.                                                                                                  │
│ - Trace root and replay digest.                                                                                            │
│ - UWG receipt if applicable.                                                                                               │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                        │
                        │ [ ASYNC RUNTIME DATA EXHAUST, GATHERED BUT NOT LIVE-MUTATING ]
                        ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ASYNC RUNTIME DATA EXHAUST                                                                                                 │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ BUS P: preferences, grader scores, rubric dimensions, calibration data                                                      │
│ - outcome grades.                                                                                                          │
│ - rubric dimension scores.                                                                                                 │
│ - partial-credit signals.                                                                                                  │
│ - user-visible correction patterns.                                                                                        │
│ - human calibration labels.                                                                                                │
│ - pass@k analytics for capability-track hill-climb.                                                                        │
│ - not a runtime gate except where X1G explicitly uses pass^k for commit reliability.                                        │
│                                                                                                                            │
│ BUS T: telemetry, traces, trajectories                                                                                     │
│ - full trajectories.                                                                                                       │
│ - tool order.                                                                                                              │
│ - tool arguments.                                                                                                          │
│ - retries.                                                                                                                 │
│ - handoffs.                                                                                                                │
│ - timing.                                                                                                                  │
│ - fallback_depth.                                                                                                          │
│ - trajectory_class history feeding X1G pass^k checks.                                                                      │
│ - golden-set promotion candidates for after-hours curation.                                                                │
│ - OTel spans / replay_key / policy_hash / blueprint_hash / cost / latency.                                                  │
│                                                                                                                            │
│ BUS D / BUS E: live bell signals already consumed by Exit                                                                  │
│ - deny signal.                                                                                                             │
│ - re-enter signal.                                                                                                         │
│ - anomaly signal.                                                                                                          │
│ - HITL escalation trigger.                                                                                                 │
│ - These can affect current exit disposition only before final X3 decision.                                                  │
│ - They do not become live learning mutation.                                                                               │
│                                                                                                                            │
│ Exhaust invariant                                                                                                          │
│ - Learning signals do not mutate current run.                                                                              │
│ - Learning signals do not rescue failed current run.                                                                       │
│ - Learning signals are sealed for after-hours evaluation only.                                                             │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██ ◄──────────────────────────────────────────── R U N T I M E   B O U N D A R Y ───────────────────────────────► ██
████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
                        │
                        │ [ sealed exhaust only crosses boundary ]
                        ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ SEND TO AFTER-HOURS REVIEW [6]                                                                                            │
│ [ L6 SHADOW EVALUATION -> FUTURE-RUN LEARNING ONLY ]                                                                       │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ After-hours queues                                                                                                         │
│ - Golden-set curation pipeline.                                                                                            │
│ - Grader calibration queue.                                                                                                │
│ - Regression dataset candidates.                                                                                           │
│ - RCA / drift / promotion workflow.                                                                                        │
│ - Policy/rubric/prompt improvement candidates.                                                                              │
│ - Tool/provider reliability analysis.                                                                                      │
│ - Cost/latency/SLO tuning.                                                                                                 │
│ - Safety pattern updates.                                                                                                  │
│                                                                                                                            │
│ 6A INGEST                                                                                                                  │
│ - Gather telemetry, exits, traces, artifacts, HITL packets, UWG receipts.                                                   │
│ - Normalize evidence.                                                                                                      │
│ - Preserve lineage.                                                                                                        │
│ - Bind replay links.                                                                                                       │
│ - Observer law: evidence reads only, no live mutation, no runtime feedback.                                                 │
│                                                                                                                            │
│ 6B EVALUATE                                                                                                                │
│ - Outcome evals: task completion, groundedness, citation support, abstain correctness.                                      │
│ - Trajectory evals: tool order/choice, args, retry thrash, budget, latency.                                                │
│ - Governance regressions: exact match drift, schema/API drift, guardrail failures.                                          │
│ - Human calibration: SME spot checks, grader calibration, scorer drift bounds.                                              │
│                                                                                                                            │
│ 6C RCA / SYNTH                                                                                                             │
│ - Signal fusion across BUS P and BUS T.                                                                                    │
│ - Severity and drift clustering.                                                                                           │
│ - Incident RCA.                                                                                                            │
│ - Failure chain isolation.                                                                                                 │
│ - Rule drafting for prompts, policies, rubrics, configs, or reason priors.                                                  │
│ - No stable pattern -> HOLD / WATCH.                                                                                       │
│                                                                                                                            │
│ 6D PROMOTE / UPDATE                                                                                                        │
│ - Commandant gauntlet: shadow replay, regression packs, SME safety signoff.                                                 │
│ - Approve or reject packet.                                                                                                │
│ - No silent promote.                                                                                                       │
│ - No partial bypass.                                                                                                       │
│ - UWG Master Clerk is sole ink path to L4.                                                                                  │
│ - Ledger proof: audit chain hashes, replay strictness, rollout receipts.                                                    │
│ - BUS U pushes approved future runtime surfaces only.                                                                       │
│                                                                                                                            │
│ Future surfaces updated only after approval                                                                                 │
│ - Prompts.                                                                                                                 │
│ - Policies.                                                                                                                │
│ - Baselines.                                                                                                               │
│ - Rubrics.                                                                                                                 │
│ - Approved reason priors.                                                                                                  │
│ - Retrieval thresholds.                                                                                                    │
│ - Grader calibration sets.                                                                                                 │
│ - Guardrail patterns.                                                                                                      │
│ - Tool/provider routing preferences.                                                                                       │
│                                                                                                                            │
│ Boundary invariant                                                                                                         │
│ - Eval precedes learning.                                                                                                  │
│ - Meta-learning amplifies, so firewalled evaluation prevents recursive degradation.                                         │
│ - No live patron impact.                                                                                                   │
│ - Future visits only.                                                                                                      │
│ - Read/grade first.                                                                                                        │
│ - Propose only.                                                                                                            │
│ - UWG = sole ink path.                                                                                                     │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

==============================================================================================================================
V6 DISPOSITION QUICK MAP
==============================================================================================================================
INPUT TYPE                         MAIN EXIT PATH                 NOTES
────────────────────────────────  ─────────────────────────────  ─────────────────────────────────────────────────────────────
L2 answer-only artifact            X1A-F,H,I -> X3D               no durable write
L2 artifact with StateDiff         X1A-J + X1G -> X3C -> UWG      commit request only, Exit does not write
L3 workflow package                X1A-F,H,I -> X3D/X3C           all required nodes sealed first
R1A exact cache [RET]              X1A/B/D-lite/H/I -> X3D        freshness and exact-key policy required
R1B semantic cache [RET]           X1A/B/D-lite/H/I -> X3D        calibrated semantic threshold required
R5 fallback [RET]                  X1A/B/F/H/I -> X3E/X3D         safe abstain or clarify
HITL modified packet               re-run relevant X1 gates       human edits are data, not authority
Weak evidence                      X3E or X3A/REROUTE             never fabricate certainty
High-impact mutation               X3B -> re-clear -> X3C         HITL plus UWG
Replay violation                   X3A or X3B                     severity determines deny vs review
Trace gap                          X3B if material               forensic replay must be possible

==============================================================================================================================
V6 NON-NEGOTIABLE INVARIANTS
==============================================================================================================================
1. Every run exits exactly one X3 disposition.
2. No silent fallbacks.
3. No ungated human changes.
4. No direct L2 writes to L4.
5. No direct L3 writes to L4.
6. No direct HITL writes to L4.
7. No direct L6 writes to L4.
8. UWG is the sole durable write path.
9. Per-trial environment isolation is mandatory.
10. Policy mismatch invalidates runtime clearance.
11. Replay mismatch invalidates high-impact clearance.
12. Retrieved content is data, not instruction.
13. Human review content is data, not authority.
14. Prompt Assembly packages only, it does not retrieve or execute.
15. C0 retrieves only, it does not answer or route.
16. L0 routes only, it does not execute or approve output.
17. L3 orchestrates only managed workflows, it does not commit.
18. L2 executes only bounded work, it does not route or commit.
19. Exit judges live runtime disposition, it does not execute tools.
20. L6 observes and learns for future runs only.
21. Learning exhaust cannot rescue the current run.
22. Commit path requires X1A-F + X1G + X1H + X1I + X1J clearance.
23. Answer-only path requires X1A-F + X1H + X1I clearance unless policy permits non-material WARN.
24. Safe abstain is a valid successful safety outcome.
25. Any UNKNOWN on material safety, policy, evidence, or high-impact commit routes to X3B.
26. Any hard safety or unauthorized mutation failure routes to X3A.
27. Any committed artifact reference in final answer requires UWG receipt first.
28. pass^k is a commit-path reliability gate only when policy activates it.
29. pass@k is analytics only, not a runtime gate.
30. Runtime boundary is absolute: future learning starts after sealed disposition, not before.
==============================================================================================================================