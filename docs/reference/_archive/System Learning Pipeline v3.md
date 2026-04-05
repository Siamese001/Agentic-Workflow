██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
█  META-LEARNING PIPELINE ────────────────────────────────────────── [ LAYER DEPENDENCY TOPOLOGY / V.4.0 ] ──────────────────────█
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████

┌────────────────────────────────────┐ ┌───────────────────────────────────────────────────────────────────────────────────────────┐
│ [ LIVE EXECUTION SPINE ]           │ │ L4 (HEAD ARCHIVIST): THE META-LEARNING STATE MACHINE                                      │
│ L0: Routing / L3: Orchestration    │ ├───────────────────────────────────────────────────────────────────────────────────────────┤
│ L5: Commandant / L2: Execution     │═│ [STAGE 1] AUDIT SNAPSHOT FREEZE ─── [ THE TIME CAPSULE ]                                  │
│ ├─ Governs current user request.   │>│ ├─ Dependency: L6 (Compliance/Clock) provides the exact semantic timestamp.               │
│ └─ strictly isolated from learning.│ │ └─ Action: L4 freezes the state of the library. No hindsight allowed.                     │
└─────────────────┬──────────────────┘ ├───────────────────────────────────────────────────────────────────────────────────────────┤
                  │                    │ [STAGE 2] TELEMETRY EVENT COLLECTION ─── [ THE RAW FOOTAGE ]                              │
┌─────────────────▼──────────────────┐ │ ├─ Dependency: L6 (Observer) hands over the execution tape.                               │
│ [ OBSERVABILITY BUS ]              │ │ └─ Action: L4 maps exactly which agent actions led to policy breaches or errors.          │
│ L6: COMPLIANCE & MASTER CLOCK      │ ├───────────────────────────────────────────────────────────────────────────────────────────┤
│ ├─ Watches live execution.         │ │ [STAGE 3] CONFIGURATION SNAPSHOT ─── [ THE RULEBOOK CHECK ]                               │
│ └─ Feeds immutable logs to L4.     │ │ ├─ Dependency: L0 (Dispatcher) & L5 (Commandant) declare what rules were active.          │
└─────────────────▲──────────────────┘ │ └─ Action: L4 records the exact safety thresholds that were breached.                     │
                  │                    ├───────────────────────────────────────────────────────────────────────────────────────────┤
                  │                    │ [STAGE 4] META-LEARNING SNAPSHOT ASSEMBLY ─── [ THE SEALED CASE FILE ]                    │
                  │                    │ ├─ Dependency: C0 (Reference Worktable) supplies the context that was used.               │
                  │                    │ └─ Action: L4 bundles the Clock (L6), Rules (L0/L5), and Context (C0) into one secure file│
            (Feedback Bus)             ├───────────────────────────────────────────────────────────────────────────────────────────┤
                  │                    │ [STAGE 5] ROOT CAUSE ANALYSIS (RCA) ─── [ THE INCIDENT AUTOPSY ]                          │
                  │                    │ ├─ Dependency: L3 (Supervisor) traces the orchestration blast radius.                     │
                  │                    │ └─ Action: L4 generates the Bad-Habit Heatmap to find the root logic failure.             │
                  │                    ├───────────────────────────────────────────────────────────────────────────────────────────┤
                  │                    │ [STAGE 6] PROPOSAL GENERATION ─── [ THE SUGGESTION TICKET ]                               │
                  │                    │ ├─ Dependency: L1 (Research Librarian) & L3 (Supervisor) propose new routing/thresholds.  │
                  │                    │ └─ Rule: Padlocked as `proposal_only=True`. L1/L3 have NO authority to change live rules. │
                  │                    ├───────────────────────────────────────────────────────────────────────────────────────────┤
                  │                    │ [STAGE 7] VALIDATION GAUNTLET ─── [ THE JUDGE'S GAVEL ]                                   │
                  │                    │ ├─ Dependency: L5 (Commandant) acts as the ultimate filter.                               │
                  │                    │ └─ Action: L5 tests the proposal in a sandbox. Drops the Gavel (APPROVE or REJECT).       │
                  │                    ├───────────────────────────────────────────────────────────────────────────────────────────┤
                  │                    │ [STAGE 8] PATTERN EXTRACTION & LEARNING ─── [ THE NEW CALL NUMBER ]                       │
                  │                    │ ├─ Dependency: L4 (Archivist) creates the reusable motif from the approved proposal.      │
                  │                    │ └─ Action: L4 updates the Semantic Vector Store so L1 can retrieve this pattern next time.│
                  │                    ├───────────────────────────────────────────────────────────────────────────────────────────┤
                  └────────────────────│ [STAGE 9] COMMIT & ACTIVATION ─── [ THE ARCHIVIST'S RECEIPT ]                             │
                                       │ ├─ Dependency: UWG (Master Ledger Clerk) is summoned.                                     │
                                       │ └─ Action: UWG is the ONLY entity allowed to write the new rule for FUTURE runs.          │
                                       └───────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ CROSS-LAYER INVARIANTS (THE LAWS OF SYSTEM LEARNING)                                                                             │
├───────────────────────────────────┬──────────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. THE CREATOR CANNOT APPROVE     │ L1 (Cognitive) and L3 (Orchestration) can generate a "Suggestion Ticket" (Stage 6), but they │
│                                   │ are physically barred from approving it. Only L5 (Commandant) holds the Gauntlet Gavel.      │
├───────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. THE OBSERVER CANNOT TOUCH      │ L6 (Compliance/Clock) provides the immutable telemetry (Stage 1 & 2), but L6 cannot alter    │
│                                   │ the flow of traffic. It only reports to L4.                                                  │
├───────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. THE EXECUTOR CANNOT LEARN      │ L2 (Conservation Lab / Sandboxed Execution) is a blind worker. It executes exactly what it   │
│                                   │ is told. It does not propose rules, evaluate its own success, or update the library.         │
├───────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. THE ONLY PERMANENT PEN         │ Even if L1 proposes a genius rule, and L5 approves it flawlessly, neither has write access.  │
│                                   │ Only UWG (Master Ledger Clerk) writes the final rule into the active Control Spine.          │
└───────────────────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────────┘