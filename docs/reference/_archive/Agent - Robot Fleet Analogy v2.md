========================================================================================================================
   ZERO-LOSS ARCHITECTURE: THE AGENT LIBRARY & ROBOT FLEET (FULL FIDELITY)
========================================================================================================================

========================================================================================================================
  1. THE FOUNDATION & THE SHELF (STATIC ARCHITECTURE / L0 + L4 + L5)
========================================================================================================================

+----------------------------------------------------------------------------------------------------------------------+
| THE MASTER SKELETON (SovereignBaseAgent / L0)                                                                        |
|----------------------------------------------------------------------------------------------------------------------|
| "I define what every robot must be able to do."                               |
| • Defines `def heal(...)` and `def heal_repository(...)`.                     |
| • Contains NO repair logic; it is the chassis blueprint every robot MUST be built on.|
+----------------------------------------------------------------------------------------------------------------------+

+----------------------------------------------------------------------------------------------------------------------+
| THE SHARED LIBRARY SHELF (MIXINS & CONTRACTS)                                                                        |
|----------------------------------------------------------------------------------------------------------------------|
| 📚 THE BOOKS (Mixins = Capabilities that robots can borrow):                  |
|                                                                                                                      |
| +-----------------------------+-----------------------------+-----------------------------+                          |
| | [BOOK] RepositoryMixin      | [BOOK] HealMixin            | [BOOK] TelemetryMixin       |                          |
| | "Repair the workshop."      | "Repair techniques."        | "Emit structured events."   |                          |
| | - repo scan                 | - helpers                   | - outcome events            |                          |
| | - deterministic transforms  | - validators                | - cost/latency counters     |                          |
| | - idempotent fixes          | - plan construction         | - stable event schema       |                          |
| +-----------------------------+-----------------------------+-----------------------------+                          |
| | [BOOK] ConfigStoreMixin     | [BOOK] RetrievalMixin       | [BOOK] CacheMixin           |                          |
| | "Read/write configs."       | "Look things up."           | "Remember short-term."      |                          |
| | - versioned config read     | - semantic recall           | - session memoization       |                          |
| | - safe defaults             | - top-k context             | - fast local fallback       |                          |
| | - feature flags             | - citations/anchors         | - TTL / eviction rules      |                          |
| +-----------------------------+-----------------------------+-----------------------------+                          |
|                                                                                                                      |
| ⚖️ THE RULEBOOKS (Contracts = Constraints that limit what robots may do):     |
|                                                                                                                      |
| +-----------------------------+-----------------------------+-----------------------------+                          |
| | [CONTRACT] EscalationPolicy | [CONTRACT] GovernanceApply  | [CONTRACT] Determinism      |                          |
| | "When to think harder."     | "What may change."          | "Replay must match."        |                          |
| | - enable_llm hard gate      | - capability tokens         | - stable hashing            |                          |
| | - LOW first                 | - guarded apply seam        | - idempotent transforms     |                          |
| | - HIGH only if justified    | - rollback rules            | - versioned schemas         |                          |
| +-----------------------------+-----------------------------+-----------------------------+                          |
+----------------------------------------------------------------------------------------------------------------------+

========================================================================================================================
  2. A FINISHED AGENT (CONCRETE ASSEMBLY)
========================================================================================================================

+----------------------------------------------------------------------------------------------------------------------+
| ROBOT A (CONCRETE AGENT)                                                                                             |
|----------------------------------------------------------------------------------------------------------------------|
| ASSEMBLY:                                                                     |
| • Built from: SovereignBaseAgent + Repository, Heal, Telemetry, and ConfigStore Mixins.                              |
| • Governed by: EscalationPolicy, GovernanceApply, and Determinism Contracts.                                         |
| • Personal Tools: StopwatchTool, SpeedSensorTool.                                                                    |
|                                                                                                                      |
| EXECUTION SCOPE (The robot strictly uses the universal workflow):             |
| • PERSONAL REPAIR: `def heal(issue) -> standard_heal(...)` (Detects issue with itself).                              |
| • WORKSHOP REPAIR: `def heal_repository(repo) -> standard_heal(..., repo_mode=True)` (Inspects entire workshop).     |
+----------------------------------------------------------------------------------------------------------------------+

========================================================================================================================
  3. THE FULL REPAIR & LEARN LIFECYCLE (THE ZERO-LOSS LOOP)
========================================================================================================================

         [ THE ROBOT IN ACTION ]                                          [ THE SYSTEM LEARNING BACKBONE ]

   Robot Detects Failure / Issue (via `standard_heal`)
                │                                                                  ┌───────────────────────────────────┐
                ▼                                                                  │                                   │
  ┌─────────────────────────────────────┐                                          │   GOVERNED SHELF / CONFIG UPDATE  │
  │ ORCHESTRATION & POLICY (L3/L5)      │ ◄────────────────────────────────────────┴─┐ Future robots act more          │
  │-------------------------------------│                                            │ intelligently.        │
  │ Reads EscalationPolicy contract:    │                                            │                                 │
  │                                     │                                            │                                 │
  │      ├──────────┼──────────┐        │                                            │                                 │
  │   NO TIER    LOW TIER   HIGH TIER   │                                            │                                 │
  │ (Plan only) (Light)     (Deep)      │     │                                 │
  └──────┬──────────┴──────────┴────────┘                                            │                                 │
         │                                                                           │                                 │
         ▼                                                                           │                                 │
  ┌─────────────────────────────────────┐                                            │                                 │
  │ DETERMINISTIC EXECUTION (L2)        │                                            │                                 │
  │-------------------------------------│                                            │                                 │
  │ `execute_healing_plan(...)`         │                                            │                                 │
  │ `apply_heal(...)` -> Fixed System   │     │                                 │
  └──────┬──────────────────────────────┘                                            │                                 │
         │                                                                           │                                 │
         ▼                                                                           │                                 │
  ┌─────────────────────────────────────┐      WRITE       ┌───────────┴───────────────────────────────┐               │
  │ THE INCIDENT REPORT DESK (L6)       │ ═══════════════► │ THE ARCHIVE VAULT (L4)                    │               │
  │-------------------------------------│                  │-------------------------------------------│               │
  │ Learning Contract (Mandatory)       │                  │ DEFINITION: Memory systems.                  │               │
  │ includes:                        │                  │ • Pinecone (semantic recall)              │               │
  │ • who acted                         │                  │ • Feature DB (structured evaluation)      │               │
  │ • what the input looked like        │                  └───────────┬───────────────────────────────┘               │
  │ • what decision was made            │                              │                                               │
  │ • which escalation tier was used    │                              │ (Reads Archive)                               │
  │ • what the outcome was              │                              ▼                                               │
  │ • how confident the robot was       │                  ┌───────────────────────────────────────────┐               │
  │ • what it cost                      │                  │ THE HISTORIAN (ML AGENT)                  │               │
  │                                     │                  │-------------------------------------------│               │
  │ "No report -> no memory ->          │                  │ `MetaLearningAgent` studies patterns      │               │
  │  no learning."                      │                  │:   │               │
  └─────────────────────────────────────┘                  │ • Which strategies succeed most?          │               │
                                                           │ • When does HIGH escalation help?         │               │
                                                           │ • Where does cost spike?                  │               │
                                                           │                                           │               │
                                                           │ Proposes governed config improvements.    │               │
                                                           │ DOES NOT repair directly.                 │               │
                                                           └───────────┬───────────────────────────────┘               │
                                                                       │                                               │
                                                                       └───────────────────────────────────────────────┘
                                                                                 (Feedback Loop Closure)
