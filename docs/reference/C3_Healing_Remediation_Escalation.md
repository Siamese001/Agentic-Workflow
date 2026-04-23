==============================================================================================================================
[C3] 🩹 HEALING, REMEDIATION & ESCALATION
     Library Persona: 🛠️ Repair Bench Staff + 🧭 Floor Supervisor + 👥 Secure Reading Room
     Spans: 🛠️ L2 repair core + 🌐 Sovereign Gateway + 🏛️ L4 audit + 👁️ L6 tuning
==============================================================================================================================

      🛠️ L2 run hits a problem
                 │
                 │ [ error detected ]
                 ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🚨 FAILURE SIGNAL                                                                                                          │
│ - Build from context only: no external "hallucinated" state allowed                                                        │
│ - Metadata: check_id / retry_count / specific error_code / lineage_hash / policy_hash                                                    │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                         │
                                                         │ [ hands report ]
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🔍 LOCAL HEAL FIRST?                                                                                                       │
│ - Attempt deterministic rule fix (e.g., schema repair, known type casting)                                                 │
│ - If exception exceeds local rules -> flag for LLM-based reasoning path                                                    │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                         │
                                    ┌────────────────────┴────────────────────┐
                                    │                                         │
                             yes [ fixed ]                            no / failed [ escalate ]
                                    │                                         │
                                    ▼                                         ▼
==============================================================================================================================
                                     🧭 HEALING TIER ROUTER   [ choke point ]
==============================================================================================================================

      ALLOWLIST GATE:
      Detects: drift_detection | import_boundary | layer_inversion | ssot_drift | capability_mismatch
                 │
                 │ [ classified failure ]
                 ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🧮 SCORE HEAL CONFIDENCE                                                                                                   │
│ - High confidence  -> Local Agent (Fast, rule-based)                                                                       │
│ - Medium confid.   -> Qwen_vLLM (Tuned for structured repair)                                                              │
│ - Low confidence   -> Gemini_2.5_Pro (Deep reasoning/complex dependencies)                                                 │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                         │
                                                         │ [ symbolic model_id ]
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🚚 TIER DISPATCHER                                                                                                         │
│ - Single production point for repair requests                                                                              │
│ - Chooses provider lane based on cost/latency/confidence balance                                                           │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                         │
          ┌──────────────────────────────┬───────────────┴───────────────┬──────────────────────────────┐
          │                              │                               │                              │
    [ 🛠️ local ]                 [ 🤖 qwen_vllm ]                [ 🌟 gemini_2_5_pro ]          [ 👥 human review ]
          │                              │                               │                              │
          └──────────────┬───────────────┴───────────────┬───────────────┴───────────────┬──────────────┘
                         │                               │                               │
                         ▼                               ▼                               ▼
      ┌────────────────────────────────────┐          ┌────────────────────────────────────┐
      │ 🌐 SOVEREIGN GATEWAY               │          │ 👥 SECURE READING ROOM             │
      │ - Provider-only operations         │          │ - Bounded packet ONLY (Privacy)    │
      │ - Mandatory invocation record      │          │ - No free-form bypass to live ops  │
      │ - Sealed repair artifact           │          │ - Decision: Approve/Modify/Reject  │
      └──────────────────┬─────────────────┘          └──────────────────┬─────────────────┘
                         │                                               │
                         │ [ repair result ]                             │ [ review verdict ]
                         ▼                                               ▼
                [ REPAIR COMPLETE ]                              [ HUMAN DISPOSITION ]
                         │                                               │
                         └───────────────────────┬───────────────────────┘
                                                 │
                                                 ▼
                                  [ BACK TO 🛡️ SAFETY / THEN RETRY ]

==============================================================================================================================
                                     ZERO-LOSS FAILURE CONTAINMENT
==============================================================================================================================

   Sovereignty error / logic violation / ghost write attempt detected
                               │
                               │ [ trigger lockdown ]
                               ▼
                    [ ❄️ FREEZE IMMEDIATELY ]
                               │
                               │ [ status: suspended ]
                               ▼
                    [ 🏛️ UWG LOCKS PENDING DIFFS ]
                               │
                               │ [ state integrity preserved ]
                               ▼
                    [ FAILED STATUS TO HEALING ROUTER ]
                               │
                               │ [ audit handoff ]
                               ▼
                    [ 🏛️ L4 AUDIT NOTE ] + [ 👁️ L6 TUNES FUTURE THRESHOLDS ]

==============================================================================================================================
[!] MANDATE: Fix if safe -> Escalate by rule -> Record every step -> Never mutate in secret.
==============================================================================================================================