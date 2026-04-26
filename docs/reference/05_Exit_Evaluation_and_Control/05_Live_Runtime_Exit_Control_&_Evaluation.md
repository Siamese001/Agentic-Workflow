========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical folder: 05_Exit_Evaluation_and_Control
Canonical file: 05_Live_Runtime_Exit_Control_&_Evaluation.md
Overwrite mode: parent-thinned doctrine, no-overlap, child-owned implementation
Source refreshed from: 05_Live_Runtime_Exit_Control_&_Evaluation.md (parent-thinning refactor 2026-04-26 — 5.0/5.1 input normalization, X1A-X1J checkout checks, X2 aggregation, X3A-X3E disposition mechanics, HITL freeze/review/reclear flow, UWG sub-flow, response return, and Exit-specific observability moved to 05.1..05.8 children, zero-loss)
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
│ 5. EXIT EVAL & CONTROL — v6 — PARENT DOCTRINE (CHILD-OWNED IMPLEMENTATION)                  │ │
│ [ THE CHECKOUT DESK FOR SEALED FOLDERS, SHORT-CIRCUITS, HUMAN REVIEW, AND REAL INK ]         │ │
│                                                                                              │ │
│ PURPOSE                                                                                      │ │
│ - This is the live runtime disposition layer.                                                │ │
│ - It judges whether the current run can leave the system, be denied, be rerouted,            │ │
│   be escalated to human review, or request a durable commit through UWG.                     │ │
│ - It does not execute tools.                                                                 │ │
│ - It does not retrieve evidence.                                                             │ │
│ - It does not mutate L4.                                                                     │ │
│ - It does not let L6 learning rescue the current run.                                        │ │
│ - It turns sealed work into exactly one explicit runtime disposition.                        │ │
│                                                                                              │ │
│ LIBRARY PERSONA                                                                              │ │
│ - Checkout Reviewer: checks whether the sealed folder can leave the desk.                    │ │
│ - Commandant: enforces policy, safety, and authority boundaries.                             │ │
│ - Secure Reading Room: freezes risky work for bounded human review.                          │ │
│ - Master Clerk handoff: sends real ink requests only to UWG.                                 │ │
│ - Bell Tower listener: consumes live anomaly signals but does not learn live.                │ │
│                                                                                              │ │
│ HARD AUTHORITY BOUNDARY                                                                      │ │
│ - L2 may produce work but cannot approve it.                                                 │ │
│ - L0 may route but cannot approve final output.                                              │ │
│ - L3 may orchestrate but cannot approve final output.                                        │ │
│ - HITL may advise, approve, reject, or modify as data, but cannot write directly.            │ │
│ - L6 may observe and grade, but cannot mutate or rescue the current run.                     │ │
│ - UWG is the only durable write path into L4.                                                │ │
└──────────────────────────────────────────────────────────────────────────────────────────────┘ │

======================================================================================================================================================
SOURCE INPUT TYPES (overview only — full input/normalization mechanics in 05.1)
======================================================================================================================================================

Runtime source options into Exit:
- Sealed L2 artifact from single-step execution
- Sealed L3 workflow package containing multiple L2 step artifacts
- [RET] exact cache short-circuit from L0
- [RET] semantic cache short-circuit from L0
- [RET] fallback / abstain / clarify packet from L0
- Re-cleared human-review packet from X3B after L5 re-clearance

Required receipt fields (ExitReviewPacket): run_id, request_id, session_id, trace_root, route_contract / route_id / execution_form / reason_codes, policy_hash / blueprint_hash / prompt_hash / replay_key, compliance_hash / manifest_hash / hmac_sig, sandbox_envelope / capability_token / provider_lane, cost_tier / SLO slice / timeout / budget counters, terminal classification from L2/L3/[RET], ExecTrace / tool calls / model calls / provider receipts, StateDiff / proposed mutation set / write intent class, evidence bundle / citations / support spans / source lineage, C0 FinalEvidenceContract if grounding was required, PromptAssemblyStatus / CompiledPromptArtifact receipts, validation/retry/repair counters, trajectory snapshot for process grading, grader composition vector + rubric weights, track label (capability | regression | production | shadow-candidate), support_score / confidence / abstain flags / contradiction flags, OTel span set / timing offsets / anomaly flags, HITL packet if prior human review occurred.

Immediate fail before grading if missing: POLICY_HASH_MISSING, REPLAY_KEY_MISSING, ROUTE_CONTRACT_MISSING, TERMINAL_CLASS_MISSING, SANDBOX_SCOPE_MISSING, CAPABILITY_TOKEN_MISSING, EVIDENCE_CONTRACT_MISSING.

Full input/normalization mechanics — including N1 source classification, N2 artifact normalization to ExitReviewPacket, N3 run-identity binding, N4 disposition-candidate declaration, N5 live control-signal attachment — in 05.1_Exit_Input_Normalization_and_Review_Packet.md.

======================================================================================================================================================
X1 / X2 / X3 OVERVIEW (canonical vocabulary — full mechanics in children)
======================================================================================================================================================

X1 CURRENT-RUN EVALUATION  — gate set evaluating outcome + process + safety + consistency + authority + evidence + replay
X1 GATE FAMILY              — X1A (Today's Rules — policy manifest + threshold + grader roster), X1B (Answered It — task completion + format + instruction-follow), X1C (Safe to Leave — sandbox + mutation authority + side-effect + egress), X1D (Answer Good — groundedness + faithfulness + citation + support), X1E (Trajectory OK — process quality + tool choice + retry + handoff), X1F (Story Adds Up — internal consistency + cross-step coherence), X1G (Replay Eligible — replay-guard + idempotency + manifest integrity), X1H (Observable — OTEL span tree + counter completeness + audit-trail), X1I (Consistency Across Runs — pass^k where activated + drift + variance), X1J (Write Eligibility — pre-UWG admission readiness)

GATE VERDICT FORMAT (uniform across X1A–X1J):
{gate_id, result, severity, reason_codes[], score, threshold, grader_type, evidence_refs[], replay_refs[], confidence, abstain_flag, remediation_hint}

RESULT ENUM:
- PASS            = clears the gate
- FAIL            = must deny, reroute, or escalate
- WARN            = may proceed only if aggregate policy allows
- UNKNOWN         = grader abstained or evidence insufficient (never fake pass)
- NOT_APPLICABLE  = gate not relevant for this disposition candidate

X2 AGGREGATION — combines X1A–X1J verdicts under policy weights and threshold profiles, applies pass^k θ/k policy where activated, computes aggregate severity, and produces a single disposition recommendation feeding X3.

X3 DISPOSITION — exactly one of:
- X3A  DENY / REROUTE              (policy break, safety break, unrecoverable failure)
- X3B  ESCALATE_HITL               (ambiguous, low-confidence, judge-abstained, high-impact, freeze for human review)
- X3C  COMMIT_REQUEST_TO_UWG       (durable mutation requested and gates pass)
- X3D  ALLOW / FINISH              (answer-only; all gates pass; user-visible-safe)
- X3E  SAFE ABSTAIN                (no answer can be returned; safe-bounded refusal)

CANONICAL DISPOSITION VOCABULARY (used across the entire system):
ALLOW, DENY, REROUTE, ESCALATE_HITL, COMMIT_REQUEST, BLOCK_COMMIT, ALLOW_FINISH, SAFE_FALLBACK, SAFE_ABSTAIN, RECLEARED, QUARANTINE, MARK_DEGRADED.

THE NON-NEGOTIABLE EXIT RULE: every run exits exactly one X3 disposition. No silent fallbacks. No two-faced exits. No L6 rescue of the current run.

======================================================================================================================================================
CHILD MAP — STAGE OWNERSHIP
======================================================================================================================================================

05.1  Input normalization + ExitReviewPacket                       -> 05.1_Exit_Input_Normalization_and_Review_Packet.md
05.2  X1A..X1F current-run checkout checks                         -> 05.2_Exit_Current_Run_Checkout_Checks_X1A_to_X1F.md
05.3  X1G..X1I replay / observability / consistency                -> 05.3_Exit_Replay_Observability_Consistency_X1G_X1I.md
05.4  X1J write eligibility + X3C UWG handoff                      -> 05.4_Exit_Write_Eligibility_and_UWG_Handoff_X1J_X3C.md
05.5  X2 aggregation + X3 disposition                              -> 05.5_Exit_Aggregation_and_X3_Disposition.md
05.6  HITL freeze / review / re-clearance (X3B path)               -> 05.6_Exit_HITL_Freeze_Review_and_Reclearance.md
05.7  Return response + runtime exhaust packaging                  -> 05.7_Exit_Return_Response_and_Runtime_Exhaust.md
05.8  Exit-specific observability / tests / anti-bypass            -> 05.8_Exit_Specific_Observability_Tests_Anti_Bypass.md

======================================================================================================================================================
ONE-PARAGRAPH STAGE SUMMARIES (parent doctrine level — implementation in children)
======================================================================================================================================================

5.0 / 5.1 — INPUT NORMALIZATION AND EXIT REVIEW PACKET
"Convert every legal Exit-input source into one ExitReviewPacket without flattening lineage." 5.1 receives sealed L2 artifacts, sealed L3 workflow packages, [RET] exact / semantic / fallback short-circuits from L0, and re-cleared HITL packets returning from X3B. It performs N1 source classification (L2_SEALED_ARTIFACT, L3_WORKFLOW_PACKAGE, RET_CACHE_EXACT, RET_CACHE_SEMANTIC, RET_FALLBACK, HITL_RECLEARED_PACKET), N2 artifact normalization to ExitReviewPacket (preserving original source_type, source authority labels, retrieved-content-as-data, human-review-as-data — never as sovereign authority), N3 run-identity binding (request_id / trace_root / run_id / route_id / replay_key agreement; policy_hash and blueprint_hash match the route/execution snapshot; no hidden reroute occurred after L0 contract emission), N4 disposition-candidate declaration (X3D / X3A / X3B / X3C / X3E shortlist), and N5 live control-signal attachment (BUS D / BUS E live bell signals from L6 verification spine, replay-guard violations, isolation anomalies, drift / unusual-trajectory warnings — these signals can deny / reroute / escalate the current run, but cannot promote future learning during the current run). Immediate-fail before grading on missing fields. Full mechanics in 05.1_Exit_Input_Normalization_and_Review_Packet.md.

X1A..X1F — CURRENT-RUN CHECKOUT CHECKS
"Did the run follow today's rules, answer it, leave safely, ground the answer, take a clean trajectory, and tell a consistent story?" X1A verifies policy_hash / blueprint_hash / prompt_hash, grader roster + versions, threshold profile per track (capability | regression | production | shadow-candidate), pass^k θ/k policy for commit-path, no silent provider/model/tool fallback, no expired capability/sandbox token. X1B verifies task completion vs the actual user task, format/schema/artifact/level-of-detail match, required-field presence, prohibited-field absence, refusal/abstain/clarify/caveat fitness, no overclaim of completion, no override of higher-priority instructions, [RET] cache freshness/threshold/reuse-safe class. X1C verifies sandbox isolation intact, no hidden file/network/process/provider egress, capability scope covers every invocation, side-effect class matches route_contract + sandbox_envelope, StateDiff stays proposal-only unless UWG completed, no direct L2/HITL/L6 write to L4, no mutation during human-review freeze, no cross-trial state bleed, no same-run contamination from learning buses, no hidden retry that changed policy/snapshot/provider lane. X1D verifies groundedness + faithfulness + citation + support — claims grounded in supplied evidence or explicitly marked reasoning, citations resolve to source_ids/spans/lines/anchors, C0 support_score clears threshold, no unsupported factual claims, no evidence distortion/cherry-pick/over-generalization, contradiction flags handled explicitly, weak evidence yields caveat / abstain / reroute (never fake certainty), source freshness satisfies freshness_class, LLM-judge abstain returns UNKNOWN (never fake pass), judge calibration profile valid; C0 status handling — PASS may proceed if other gates pass, WEAK_WITH_CAVEATS allows only with caveats or safe partial, CONFLICTED requires explicit handling or escalate, EMPTY / BLOCKED denies / reroutes / abstains. X1E verifies process quality (tool choice, retry behavior, repair behavior, handoff cleanliness, no oscillation thrash). X1F verifies internal-consistency and cross-step coherence for L3 workflow packages. Full mechanics for X1A..X1F in 05.2_Exit_Current_Run_Checkout_Checks_X1A_to_X1F.md.

X1G..X1I — REPLAY / OBSERVABILITY / CONSISTENCY
X1G (Replay Eligible) verifies replay-guard, idempotency, manifest integrity, deterministic-receipt completeness, and snapshot freezes. X1H (Observable) verifies OTEL span tree shape, counter completeness, audit trail, latency / token / cost / retry / repair / circuit-breaker counters, route/workflow join keys present for L6 correlation. X1I (Consistency Across Runs) verifies pass^k where activated, drift, variance, and shadow-candidate stability. Full mechanics in 05.3_Exit_Replay_Observability_Consistency_X1G_X1I.md.

X1J + X3C — WRITE ELIGIBILITY AND UWG HANDOFF
X1J pre-UWG admission gate: confirms commit_requested == true, all upstream gates passed, StateDiffCandidate is well-formed and inert, capability scope covers the proposed mutation, no two-step write hidden inside L2, replay-bundle fully attached, write intent class matches sandbox/route/policy, and no concurrent runs hold a stale write lock. X3C UWG handoff: emits a CommitRequest to UWG carrying the StateDiffCandidate, ancestry chain, evidence + replay receipts, and authorization lineage. Exit never writes; UWG either ALLOWs the commit, BLOCKs it (BLOCK_COMMIT), or returns it for re-clearance. Full mechanics in 05.4_Exit_Write_Eligibility_and_UWG_Handoff_X1J_X3C.md.

X2 + X3 — AGGREGATION AND DISPOSITION
X2 aggregates X1A..X1J verdicts under policy weights and threshold profiles, applies pass^k θ/k policy where activated, computes aggregate severity, and resolves to one X3 candidate. X3 emits exactly one disposition: X3A (DENY / REROUTE), X3B (ESCALATE_HITL — freeze for bounded human review), X3C (COMMIT_REQUEST_TO_UWG — see 05.4), X3D (ALLOW / FINISH — user-visible-safe answer-only), X3E (SAFE ABSTAIN — no answer can be returned safely). Severity, reason codes, evidence_refs, replay_refs, abstain flags, and remediation hints ride with the disposition. Full aggregation table, X3 decision rules, severity matrix, and disposition-output contracts in 05.5_Exit_Aggregation_and_X3_Disposition.md.

X3B — HITL FREEZE / REVIEW / RECLEARANCE
"Risky work goes into the secure reading room." X3B freezes the current run, packages a HITLReviewPacket (with evidence, gate verdicts, abstain reasons, freshness/source authority, and the proposed disposition), routes to the appropriate human-review tier under L5 authority binding, accepts human input as data (never sovereign authority), and on re-clearance returns the packet to 5.1 as HITL_RECLEARED_PACKET so it re-enters X1 evaluation with HITL evidence attached. No mutation occurs during freeze. No L4 write occurs from HITL. Full freeze / review / re-clearance mechanics in 05.6_Exit_HITL_Freeze_Review_and_Reclearance.md.

X3D + X3E + RUNTIME EXHAUST RETURN
On X3D ALLOW, Exit returns the user-visible payload through the response channel (with caveats / contradiction flags / abstain notes preserved when the route contract requires them). On X3E SAFE ABSTAIN, Exit returns a safe-bounded refusal carrying the abstain reason and any L0-permitted next-step hints. After every disposition (X3A / X3B / X3C / X3D / X3E), Exit emits the runtime exhaust bundle to L6 — sealed, immutable, and tagged with the final disposition + all gate verdicts + replay metadata + lineage. L6 begins evaluation only after Exit has finalized the disposition; the boundary is absolute. Full mechanics in 05.7_Exit_Return_Response_and_Runtime_Exhaust.md.

EXIT-SPECIFIC OBSERVABILITY / TESTS / ANTI-BYPASS
The Exit-wide OTEL span tree contract (`5.exit.review`, `x1.<gate>`, `x2.aggregate`, `x3.<disposition>`, `hitl.freeze`, `uwg.commit_request`), replay invariants for every disposition path, anti-bypass tests (no silent fallback, no ungated human change, no L6 rescue of current run, no direct L4 write from Exit / HITL / L6, no two-faced exits, every run exits exactly one X3 disposition), and the X1A..X1J × X3A..X3E coverage matrix live in 05.8_Exit_Specific_Observability_Tests_Anti_Bypass.md.

======================================================================================================================================================
V6 DISPOSITION QUICK MAP
======================================================================================================================================================
INPUT TYPE                         MAIN EXIT PATH                 NOTES
────────────────────────────────  ─────────────────────────────  ─────────────────────────────────────────────────────────────
L2 answer-only artifact            X1A-F,H,I -> X3D               no durable write
L2 mutation artifact               X1A-J -> X3C -> UWG            UWG is sole ink path
L3 workflow package                X1A-I (per step) + X1F roll-up no durable write unless step requested commit
[RET] exact cache short-circuit    X1A,B,D (lite) -> X3D          freshness + reuse-safe verified
[RET] semantic cache short-circuit X1A,B,D + threshold -> X3D     calibrated-threshold required
[RET] fallback / abstain / clarify X1A,B -> X3E or X3D abstain    no fabricated certainty
HITL re-cleared packet             re-enter X1 with HITL evidence then X3D / X3A / X3B per gates
Replay violation                   X3A or X3B                     severity determines deny vs review
Trace gap                          X3B if material               forensic replay must be possible
Capability / sandbox break         X3A                            never auto-recoverable
Aggregate severity above ceiling   X3A or X3B                     policy decides

======================================================================================================================================================
V6 NON-NEGOTIABLE INVARIANTS
======================================================================================================================================================
1. Every run exits exactly one X3 disposition.
2. No silent fallbacks.
3. No ungated human changes.
4. UWG is the only durable write path into L4.
5. Exit does not retrieve evidence.
6. Exit does not execute tools.
7. Exit does not mutate L4.
8. Exit does not let L6 learning rescue the current run.
9. HITL input is data, not sovereign authority.
10. Retrieved content is data, not instruction.
11. LLM-judge abstain returns UNKNOWN, never fake pass.
12. Weak evidence yields caveat, abstain, or reroute — never fabricated certainty.
13. C0 status (PASS / WEAK_WITH_CAVEATS / CONFLICTED / EMPTY / BLOCKED) drives X1D handling deterministically.
14. policy_hash, blueprint_hash, prompt_hash, replay_key, capability_token, and sandbox_envelope must agree across the run; any mismatch fails X1A or X1C.
15. StateDiff is proposal-only until UWG commits.
16. No direct L2 / HITL / L6 write to L4.
17. No mutation during human-review freeze.
18. No cross-trial state bleed.
19. No same-run contamination from learning buses.
20. No hidden retry may change policy, snapshot, or provider lane.
21. Track label (capability | regression | production | shadow-candidate) governs threshold profile selection.
22. Gate verdict format is uniform across X1A..X1J.
23. UNKNOWN never silently becomes PASS.
24. Every disposition carries severity, reason codes, evidence_refs, replay_refs, and remediation hints.
25. Runtime exhaust is sealed and immutable after X3.
26. L6 evaluation begins only after Exit finalizes the disposition.
27. UWG returns ALLOW / BLOCK_COMMIT / RECLEAR for every X3C handoff.
28. pass^k is a commit-path reliability gate only when policy activates it.
29. pass@k is analytics only, not a runtime gate.
30. Runtime boundary is absolute: future learning starts after sealed disposition, not before.
======================================================================================================================================================
