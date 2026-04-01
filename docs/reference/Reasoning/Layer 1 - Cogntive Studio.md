====================================================================================================================================================================================
[ LAYER 1: COGNITIVE STUDIO ] ── PROGRAMMATIC BATCHING CONTROL PLANE
STRATEGY: Context Isolation │ Bounded Iterative Loop │ Sandbox Enforcement │ Zero Raw-Data Pollution
====================================================================================================================================================================================

                                    [ CUMULATIVE CONTEXT BUS ] ──(Maintains "Clean Desk" reasoning state)────────────────┐
                                    │                             │                                │               │
  ┌─────────────────────────────────▼┐   ┌────────────────────────▼─────────┐   ┌────────────────────▼─────────────┐   ┌────────────────────▼─────────────┐
  │ [Phase 1] INGESTION & PRIMING    │   │ [Phase 2] INTENT EXTRACTION      │   │ [Phase 3] PROGRAMMATIC PLANNING  │   │ [Phase 4] CONTRACT GENERATION    │
  │ Role: Intake Librarian           │   │ Role: Classification Librarian   │   │ Role: Lead Architect Librarian   │   │ Role: Precision Specifier        │
  └────────────────┬─────────────────┘   └────────────────┬─────────────────┘   └────────────────┬─────────────────┘   └────────────────┬─────────────────┘
                   │                                      │                                      │                                      │
        [ Validated Request ]                  [ Intent + Constraint Mapping ]         [ Next Step Plan + Tool Budget ]       [ Programmatic Task Contract ]
                   │                                      │                                      │                                      │
  ╔════════════════▼═════════════════╗   ╔════════════════▼═════════════════╗   ╔════════════════▼═════════════════╗   ╔════════════════▼═════════════════╗
  ║ TRANSFORMER NEURAL NETWORK x N   ║   ║ TRANSFORMER NEURAL NETWORK x N   ║   ║ TRANSFORMER NEURAL NETWORK x N   ║   ║ TRANSFORMER NEURAL NETWORK x N   ║
  ║ (Standard Attention Mechanisms)  ║   ║ (Standard Attention Mechanisms)  ║   ║ (Standard Attention Mechanisms)  ║   ║ (Standard Attention Mechanisms)  ║
  ╚════════════════┬═════════════════╝   ╚════════════════▼═════════════════╝   ╚════════════════▼═════════════════╝   ╚════════════════▼═════════════════╝
                   │                                      │                                      │                                      │
  ┌────────────────▼─────────────────┐   ┌────────────────▼─────────────────┐   ┌────────────────▼─────────────────┐   ┌────────────────▼─────────────────┐
  │ » Normalized Request             │══╗│ » Intent Core + Gaps             │══╗│ » Atomic Operation Strategy      │══╗│ 📄 [ THE P.T.C. WORK ORDER ]     │
  │ » Session Identity               │  ║│ » Policy/Safety Flags            │  ║│ » Confidence Score Matrix        │  ║│ » Target Tool: (e.g., Python)    │
  └──────────────────────────────────┘  ║└──────────────────────────────────┘  ║└──────────────────────────────────┘  ║│ » Payload: Exact Code/Query      │
                                        ║                                      ║                                      ║│ » Constraints: Timeout/Memory    │
     (Feeds Forward as Next State) ═════╝   (Feeds Forward as Next State) ═════╝  (Feeds Forward as Next State) ══════╝│ » Promise: Expected Return Schema│
                                                                                                                       └────────────────┬─────────────────┘
                                                                                                                                        │
                                                                             ┌──────────────────────────────────────────────────────────┘
                                                                             │
                                             ╔═══════════════════════▼═══════▼══════════════╗
                                             ║ [ GOVERNANCE GATE - PTC EVALUATION ]         ║
                                             ║ Evaluates the PTC parameters strictly:       ║
                                             ║ IF Target/Payload violates Policy = Escalate ║───[ ESCALATE TO HUMAN REVIEW ]
                                             ║ IF Constraints > Budget = Reject & Retry     ║
                                             ║ ELSE -> FREEZE LAYER 1 CONTEXT               ║
                                             ╚═══════════════════════┬══════════════════════╝
                                                                     │
                                                                     ▼ (Authenticated & Gated PTC)

====================================================================================================================================================================================
[ LAYER 0: PROGRAMMATIC SANDBOX EXECUTION ] ── Isolation Environment
PROCESS: Atomic Execution (Private Room) │ Filtering │ Structured Schema │ Enriched Distillation
====================================================================================================================================================================================

                                                                     │
          ┌──────────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────┐
          │  [ SANDBOX OPERATIONS (Driven strictly by the PTC) ]                                                                │
          │  1. Ingest PTC (Read Target Tool, Payload, and Constraints from the Work Order)                                     │
          │                                                                                                                     │
          │  2. Execute Atomic Payload (Run the code/query strictly within the PTC's requested limits)                          │
          │                                                                                                                     │
          │  3. Trap & Format Results (Force the raw execution output into the PTC's required "Expected Return Schema")         │
          │                                                                                                                     │
          │  4. Emit Enriched Output (Return the clean Schema + Metadata: Success flag, execution time, errors)                 │
          └──────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────┘
                                                                     │
                                                                     ▼ (Distilled "Index Card" Result + Metadata)
                                             ╔════════════════════════════════════════════════════════╗
                                             ║ [ UNFREEZE CONTEXT & EVALUATE ]                        ║
                                             ║ Return Schema-Compliant Signal to Layer 1 Reasoning    ║
                                             ║                                                        ║
                                             ║ ↻ IMPLICIT LOOP: Observe -> Plan -> Execute -> Repeat  ║
                                             ║   (Feeds back into Phase 3: Programmatic Planning)     ║
                                             ║                                                        ║
                                             ║ 🛑 EXIT CONDITIONS:                                    ║
                                             ║    • Task Complete      • Max Iterations Reached       ║
                                             ║    • Failure Threshold  • Escalation Trigger           ║
                                             ╚════════════════════════════════════════════════════════╝