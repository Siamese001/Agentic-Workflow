███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
█  [ LAYER 1: COGNITIVE STUDIO ] ── PROGRAMMATIC BATCHING CONTROL PLANE                                                                                   █
█  STRATEGY: Context Isolation │ Single-Pass Inference │ Sandbox Enforcement │ Zero Raw-Data Pollution                                                    █
███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████

                                    [ CUMULATIVE CONTEXT BUS ] ──(Maintains "Clean Desk" reasoning state)────────────────┐
                                    │                             │                                  │               │
  ┌─────────────────────────────────▼┐   ┌────────────────────────▼─────────┐   ┌────────────────────▼─────────────┐   ┌────────────────────▼─────────────┐
  │ [Phase 1] INGESTION & PRIMING    │   │ [Phase 2] INTENT EXTRACTION      │   │ [Phase 3] PROGRAMMATIC PLANNING  │   │ [Phase 4] SCRIPT EMISSION        │
  │ Role: Intake Librarian           │   │ Role: Classification Librarian   │   │ Role: Lead Architect Librarian   │   │ Role: Scripting Librarian        │
  └────────────────┬─────────────────┘   └────────────────┬─────────────────┘   └────────────────┬─────────────────┘   └────────────────┬─────────────────┘
                   │                                      │                                      │                                      │
        [ Validated Request ]                  [ Intent + Constraint Mapping ]         [ Full Tool-Sequence Logic ]           [ Executable Logic Script ]
                   │                                      │                                      │                                      │
  ╔════════════════▼═════════════════╗   ╔════════════════▼═════════════════╗   ╔════════════════▼═════════════════╗   ╔════════════════▼═════════════════╗
  ║ TRANSFORMER NEURAL NETWORK x N   ║   ║ TRANSFORMER NEURAL NETWORK x N   ║   ║ TRANSFORMER NEURAL NETWORK x N   ║   ║ TRANSFORMER NEURAL NETWORK x N   ║
  ║ (Standard Attention Mechanisms)  ║   ║ (Standard Attention Mechanisms)  ║   ║ (Standard Attention Mechanisms)  ║   ║ (Standard Attention Mechanisms)  ║
  ╚════════════════┬═════════════════╝   ╚════════════════▼═════════════════╝   ╚════════════════▼═════════════════╝   ╚════════════════▼═════════════════╝
                   │                                      │                                      │                                      │
  ┌────────────────▼─────────────────┐   ┌────────────────▼─────────────────┐   ┌────────────────▼─────────────────┐   ┌────────────────▼─────────────────┐
  │ » Normalized Request             │══╗│ » Intent Core + Gaps             │══╗│ » Batch Operation Strategy       │══╗│ » Programmatic Task Contract      │
  │ » Session Identity               │  ║│ » Policy/Safety Flags            │  ║│ » Confidence Score Matrix        │  ║│ » (Python/Bash/Query Script)     │
  └──────────────────────────────────┘  ║└──────────────────────────────────┘  ║└──────────────────────────────────┘  ║└────────────────┬─────────────────┘
                                        ║                                      ║                                      ║                 │
     (Feeds Forward as Next State) ═════╝   (Feeds Forward as Next State) ═════╝  (Feeds Forward as Next State) ══════╝                 │
                                                                                                                                        │
                                                                         ┌──────────────────────────────────────────────────────────────┘
                                                                         │
                                                 ╔═══════════════════════▼══════════════════════╗
                                                 ║ [ GOVERNANCE GATE ]                          ║
                                                 ║ IF Confidence < Threshold OR Policy = Risk    ║───[ ESCALATE TO HUMAN REVIEW ]
                                                 ║ ELSE -> FREEZE LAYER 1 CONTEXT               ║
                                                 ╚═══════════════════════┬══════════════════════╝
                                                                         │
                                                                         ▼ (Authenticated & Gated Script)
███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
█  [ LAYER 0: PROGRAMMATIC SANDBOX EXECUTION ] ── Isolation Environment                                                                                   █
█  PROCESS: Execution (Private Room) │ Filtering │ Aggregation │ "Index Card" Distillation                                                                █
███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
                                                                         │
          ┌──────────────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────┐
          │  [ SANDBOX OPERATIONS ]                                                                                                 │
          │  1. Execute Script (Batch call to Databases/Application Programming Interfaces/Calculators)                             │
          │  2. Trap Raw Results (Preventing spillover into Layer 1)                                                                │
          │  3. Aggregate & Filter (Logic-based pruning of data)                                                                    │
          │  4. Emit Summary Output (Standard Output stream)                                                                        │
          └──────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────┘
                                                                         │
                                                                         ▼ (Distilled "Index Card" Result Only)
                                                 ╔══════════════════════════════════════════════╗
                                                 ║ [ UNFREEZE CONTEXT ]                         ║
                                                 ║ Return Distilled Signal to Layer 1 Reasoning  ║
                                                 ╚══════════════════════════════════════════════╝