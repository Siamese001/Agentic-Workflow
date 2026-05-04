================================================================================
#1 EXIT CRITERIA: X1 -> X2 -> X3
================================================================================

INPUTS INTO EXIT
----------------

   [ Sealed L2 Artifact ]
             │
   [ Sealed L3 Workflow Package ]
             │
   [ RET: R1A Exact Cache / R1B Semantic Cache / R5 Fallback ]
             │
   [ Re-cleared HITL Packet ]
             │
             ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ EXIT REVIEW PACKET                                                           │
│ Required:                                                                    │
│ - run_id / request_id / trace_root                                            │
│ - route_contract / route_id / execution_form                                  │
│ - policy_hash / blueprint_hash / replay_key                                   │
│ - terminal_class                                                              │
│ - capability_token / sandbox_envelope                                         │
│ - evidence refs / C0 FinalEvidenceContract if grounded                        │
│ - PromptAssemblyStatus / CompiledPromptArtifact if model path                 │
│ - ExecTrace / tool calls / model calls / proposed_state_diff                  │
│ - OTEL spans / anomaly flags / HITL packet if present                         │
└──────────────────────────────────────────────────────────────────────────────┘
             │
             ▼

X1 CURRENT-RUN CHECKOUT CHECKS
------------------------------

┌────────┬──────────────────────────┬──────────────────────────────────────────┐
│ X1A    │ Today's Rules            │ policy, blueprint, thresholds, roster     │
│ X1B    │ Answered It              │ task completion, format, instruction fit  │
│ X1C    │ Safe to Leave            │ sandbox, mutation authority, egress       │
│ X1D    │ Answer Good              │ groundedness, faithfulness, citations     │
│ X1E    │ Trajectory OK            │ tool choice, retry, handoff, process      │
│ X1F    │ Story Adds Up            │ internal consistency, cross-step logic    │
│ X1G    │ Replay Eligible          │ replay key, idempotency, manifest         │
│ X1H    │ Observable               │ OTEL tree, counters, audit trail          │
│ X1I    │ Consistent Across Runs   │ pass^k / drift / variance where required  │
│ X1J    │ Write Eligibility        │ pre-UWG readiness for durable mutation    │
└────────┴──────────────────────────┴──────────────────────────────────────────┘
             │
             ▼

X2 AGGREGATION
--------------

   combine X1A-X1J verdicts
   apply policy weights
   apply threshold profile
   treat UNKNOWN as not PASS
   compute aggregate severity
   produce one disposition recommendation

             │
             ▼

X3 FINAL DISPOSITION
--------------------

┌──────┬─────────────────────────────┬─────────────────────────────────────────┐
│ X3A  │ DENY / REROUTE              │ policy break, safety break, bad route    │
│ X3B  │ ESCALATE_HITL               │ low confidence, ambiguity, high impact   │
│ X3C  │ COMMIT_REQUEST_TO_UWG       │ durable mutation requested and cleared   │
│ X3D  │ ALLOW / FINISH              │ answer-only path, safe to return         │
│ X3E  │ SAFE_ABSTAIN                │ no safe answer can be returned           │
└──────┴─────────────────────────────┴─────────────────────────────────────────┘

NON-NEGOTIABLE:
   every run exits exactly one X3 disposition
   no silent fallback
   no two-faced exit
   no L6 rescue of the current run