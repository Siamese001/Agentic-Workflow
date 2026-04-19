## 🗺️ HITL PATH D — V20.1 AGENTIC PROCESS ALIGNMENT (ZERO-LOSS OVERWRITE)

### **I. ADG STATE SIGNALS (SQLITE)**
* **Path Routing**: `routes_path=70`
* **Human Intensity**: `requires_human_review=10` | `escalates_to_human=5`
* **Gate Control**: `gated_by_confidence=1` | `freezes_context=1`
* **Execution**: `enters_sandbox=10`
* **Learning**: `builds_dpo_batch=6` | `produces_preference_pair=3`

---

### **II. MACRO FLOW: THE GOVERNED HUMAN DECISION AIRLOCK**

```ascii
[ 🛑 L3 ORCHESTRATION: SHIFT SUPERVISOR ]
* Logic: Path D initiation and state freezing.
* Modules: deterministic_orchestrator.py | handshake_state_machine.py | freeze_unfreeze.py

        ┌────────────────────────────┐      ┌────────────────────────────┐
        │      L3 PATH SELECT        │      │      L3 FREEZE AIRLOCK     │
        │ _orchestrate_path_d        │─────>│   freeze_unfreeze.py       │
        └─────────────┬──────────────┘      └─────────────┬──────────────┘
                      │                                   │
                      v                                   v
        ┌────────────────────────────────────────────────────────────────┐
        │ [ HUMAN DECISION ARTIFACT ] — L3 Generates Review Artifact     │
        │ Options: APPROVE | MODIFY (modify_diff) | REJECT               │
        └───────┬───────────────────────┬────────────────────────┬───────┘
                │                       │                        │
                ▼ [ REJECT ]            ▼ [ MODIFY_DIFF ]        ▼ [ APPROVE ]
        ┌──────────────────┐    ┌────────────────────┐    ┌──────────────────┐
        │ DENY / STOP      │    │ L5 REVIEW QUEUE    │    │ L5 HITL GATE     │
        │ Forced L1 Entry  │    │ queue_enforcer.py  │    │ hitl_gate.py     │
        └──────────────────┘    └────────┬───────────┘    └────────┬─────────┘
                                         │                         │
                                         └───────────┬─────────────┘
                                                     │
                                                     v
        ┌────────────────────────────────────────────────────────────────┐
        │ [ L5 SECURITY RE-CLEARANCE: SECURITY COMMANDANT ]              │
        │ policy_enforcement_point.py -> reenter_safety                  │
        │ INVARIANT: Human input is UNTRUSTED until L5 re-clearance.     │
        └──────────────────────────────┬─────────────────────────────────┘
                                       │
                                       v
        ┌────────────────────────────────────────────────────────────────┐
        │ [ L2 EXECUTION CORE: CONSERVATION LAB ]                        │
        │ execution_guardrail_chokepoint.py | sovereign_sandbox_isolation│
        │ INVARIANT: No direct human -> sandbox bypass.                  │
        └──────────────────────────────┬─────────────────────────────────┘
                                       │
                                       v
        ┌──────────────────────────────┴─────────────────────────────────┐
        │ [ L6 & ML: POST-EXECUTION MANIFOLD ]                           │
        ├──────────────────────────────┬─────────────────────────────────┤
        │ BUS T: TELEMETRY (L6)        │ BUS P: PREFERENCE (L_SL)        │
        │ entropy_telemetry_engine     │ path_d_preference_embedder      │
        │ record_intervention          │ pair_from_hitl_log              │
        └──────────────────────────────┴─────────────────────────────────┘