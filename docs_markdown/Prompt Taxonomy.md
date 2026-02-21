==========================================================================================================================================================================
                                                    ZERO-LOSS ARCHITECTURE — PROMPT TAXONOMY (WIDESCREEN MASTER VIEW)
                                                               (A+++++ ZERO-LOSS WIDESCREEN ASCII OVERWRITE)
==========================================================================================================================================================================

 AUTHORITY GRADIENT  ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────►

 ZERO (Unprivileged)              INFORMATIONAL (Data)              GOVERNED (Capabilities)              BINDING (Constraints)              ABSOLUTE (Invariants)
         │                                  │                                  │                                    │                                  │
         ▼                                  ▼                                  ▼                                    ▼                                  ▼

┌───────────────────────────────┐
│ USER PROMPT (L1 Intent)       │
│ - Raw "What" — ZERO authority │
│ - Generated at L1 Thinking    │
│ - Non-mutant proposal         │
└──────────────┬────────────────┘
               │
               │ (AIRLOCK: Cannot pass L1 -> L0 without wrapping)
               ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ L0 ROUTER (The First Authority Gate)                                                                                                                                   │
│ - Classifies intent vs. L4 Routing State (escalation thresholds / path logic)                                                                                          │
│ - Selects specific path (A / B / C / D) and emits InstructionPacket                                                                                                    │
│ - Triggers context loading via the "Elevator Shaft" (L0 <-> L5 runtime seam)                                                                                           │
└──────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
               │
               ▼
==========================================================================================================================================================================
 ASSEMBLY STAGE (Pre-L2 Execution) — DETERMINISTIC COMPOSITION
==========================================================================================================================================================================

        ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
        │ SLOT S0: SYSTEM / STATE (The Rulebooks)                                                                                        │
        │ - Hard-coded constitutions + invariants (Determinism, Safety, No Upward Imports)                                               │
        │ - Source: L4 Master State / L5 Policy Blueprints                                                                               │
        │ - Authority: ABSOLUTE (Immutable anchor for all reasoning)                                                                     │
        └──────────────────────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                       │ (Injected as the foundational directive)
                                       ▼
        ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
        │ SLOT I0: INSTRUCTIONAL (The Capability Manuals)                                                                                │
        │ - Identity and "Mixin" behaviors (HealMixin, ValidateMixin, MCPHardenedMixin)                                                  │
        │ - Inherited from [[SovereignBaseAgent]] root SSOT                                                                              │
        │ - Source: L4 State (Mixins) / Step 1 Capability Definitions                                                                    │
        │ - Authority: GOVERNED (Defines "How" an agent operates)                                                                         │
        └──────────────────────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                       │ (Defines capability boundaries)
                                       ▼
        ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
        │ SLOT D0: INJECTIONS (The Role Fences)                                                                                          │
        │ - Semantic fences, tool constraints, and scope boundaries                                                                      │
        │ - Post-retrieval redaction and context budget enforcement                                                                      │
        │ - Source: L5 Safety (Active Guardian) policy evaluators                                                                        │
        │ - Authority: BINDING (Constraints applied before commit)                                                                        │
        └──────────────────────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                       │ (Enforced before execution)
                                       ▼
        ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
        │ SLOT C0: DEPENDENCY (Context Widening)                                                                                         │
        │ - RAG / Elevator Shaft injected knowledge and citations                                                                        │
        │ - High-fidelity artifacts (JSON Manifests / AST Snapshots)                                                                     │
        │ - Source: L4 Knowledge Index / L2.1 boundary_snapshot.json                                                                     │
        │ - Authority: INFORMATIONAL (Grounding data)                                                                                    │
        └──────────────────────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                       │ (Grounds the proposal in external state)
                                       ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PROMPT ASSEMBLER (Deterministic Slot Insertion)                                                                                                                        │
│                                                                                                                                                                        │
│   Final Package = [S0: SYSTEM] + [D0: INJECTIONS] + [I0: INSTRUCTIONAL] + [C0: DEPENDENCY] + [U0: USER PROMPT]                                                         │
│                                                                                                                                                                        │
│ - Output: Governed Prompt + Manifest Hash (ensuring data parity)                                                                                                       │
└──────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
               │
               ▼
==========================================================================================================================================================================
 EXECUTION & HEALING LAYER (L2 Sandbox)
==========================================================================================================================================================================

┌─────────────────────────────────────────────────────────────────────────────────────────────┐         ┌──────────────────────────────────────────────────────────────┐
│ L2.1: VALIDATOR (Pre-flight Simulator)                                                      │         │ L5: SAFETY (Active Guardian Gate)                            │
│ - Dry-run simulation and contract checks                                                    │ <=====> │ - Evaluates assembled prompt vs. L4 policy                   │
│ - Emits boundary_snapshot.json for potential healing                                        │ │ - BLOCKS or ALLOWS based on budget/safety                    │
└──────────────┬──────────────────────────────────────────────────────────────────────────────┘         └──────────────────────────────┬───────────────────────────────┘
               │                                                                                                                       │
               │ (IF ALLOWED)                                                                                                          │
               ▼                                                                                                                       │
┌─────────────────────────────────────────────────────────────────────────────────────────────┐                                        │
│ L2.2: EXECUTION (The Singular Mutation Point)                                               │ <======================================┘
│ - Applies approved change set via AST surgery                                               │
│ - SOLE durable write authority (modifies FS/DB)                                             │
└──────────────┬───────────────────────────────┬──────────────────────────────────────────────┘
               │                               │
               │ (SUCCESS)                     │ (FAILURE / ERROR ROOT)
               v                               v
┌──────────────────────────────┐       ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ TASK COMPLETE / LOGGED       │       │ L2.3: HEALER LOOP (The Rollback Engine)                                                                                │
│ - Outcome versioned in L4    │ │ - Reverts to boundary_snapshot and generates HEALING PROPOSAL                                                          │
│ - Exits Zero-Loss Loop       │       │ - MUST re-enter Assembly Gate / L5 Safety Gate before retry (Proposed Authority)                                       │
└──────────────────────────────┘       └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

==========================================================================================================================================================================
 CRITICAL DISSEMINATION GUARANTEES
==========================================================================================================================================================================
| 1. AIRLOCK INTEGRITY: User Prompt (L1) cannot touch L2 Execution without passing L0, L4 state wrapping, and L5 safety gating.                      |
| 2. FENCING ENFORCEMENT: Role fences (Injections) are applied at the Assembly Stage, ensuring L2 never receives an unfenced/ungoverned intent.        |
| 3. CONTEXT LOADING DISCIPLINE: Dependencies are loaded via the Elevator Shaft at runtime (L0 <-> L5), maintaining L0's weightless authority.         |
| 4. RE-ENTRY CONTROL: Healing proposals (L2.3) hold zero durable mutation power; they must recursively pass the Assembly and Safety gates again.       |
| 5. DATA PARITY: The Surgical Manifest ensures high-resolution data is preserved across the Validator -> Healer communication pipe.                    |
==========================================================================================================================================================================