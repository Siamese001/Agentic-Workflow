==================================================================================================================================================
                                     AGENTIC SYSTEM — TOPOLOGICAL DEPENDENCY GRAPH
                                        (ZERO-LOSS ARCHITECTURAL RE-ALIGNMENT)
==================================================================================================================================================

[ THE OMNIVORES — ABSOLUTE TOP ] (Outside the application lifecycle. Import everything, imported by nothing.)
==================================================================================================================================================
     +--------------------------------------------------+       +--------------------------------------------------+
     | L_OPS (ops_scripts/)                             |       | L_TEST (tests/)                                  |
     | Imports: ALL LAYERS                              |       | Imports: ALL LAYERS                              |
     | Never imported by production code                |       | Never imported by production code                |
     +--------------------------------------------------+       +--------------------------------------------------+
                                          |
                                          v
[ THE APPLICATION ROOF ] (Entry point. Orchestrates the core but is not the core.)
==================================================================================================================================================
                         +--------------------------------------------------+
                         | L_APP (apps_*) — CLI / UI / Services             |
                         | Can import: L0-L6, L_SHARED, L_SL                |
                         +--------------------------------------------------+
                                          | (imports down)
                                          v
[ THE CORE GRAVITY PILLAR ] (Strict downward static imports)        [ THE SPECIALIZED SATELLITES ] (Utility Sidecars)
==================================================================================================================================================
                         +--------------------------------+
                         | L6: OBSERVABILITY / TELEMETRY  |
                         | Passive Signal Classification  |
                         +--------------------------------+
                                          |
                                          v                             +--------------------------------+
                         +--------------------------------+ <========== | L_PG (prompt_gov/)             |
                         | L5: SAFETY / GOVERNANCE        |             | Highly privileged.             |
                         | structure_blueprint_impl       |             | Imports: L0-L5, L_RUNTIME, L4  |
                         +--------------------------------+             +--------------------------------+
                                          |
                                          v                             +--------------------------------+
                         +--------------------------------+ ==========> | L_TOOLS (tools/, adg/)         |
                         | L4: STATE / KNOWLEDGE / RAG    | (Exception) | ADG/Analysis tooling.          |
                         | Retrieval & Drift State        | ==========> | Imports: L0-L5, L_SHARED, L_SL |
                         +--------------------------------+             +--------------------------------+
                                          |
                                          v                             +--------------------------------+
                         +--------------------------------+ <========== | L_RUNTIME (runtime/)           |
                         | L3: ORCHESTRATION / SUPERVISION|             | Bootstrap assembler.           |
                         | AtomicExecutionMixin           |             | Imports: L0-L5, L_SHARED       |
                         +--------------------------------+             +--------------------------------+
                                          |
                                          v                             +--------------------------------+
                         +--------------------------------+ <========== | L_SL (system_learning)         |
                         | L2: EXECUTION / TOOLS / SANDBOX|             | Feedback loop.                 |
                         | High-Res AST Mutation Env      |             | Imports: L0-L2, L5, L_SHARED   |
                         +--------------------------------+             +--------------------------------+
                                          |
                                          v                             +--------------------------------+
                         +--------------------------------+ <========== | L_SHARED (utils, mixins)       |
                         | L1: COGNITION / REASONING      |             | Cross-cutting utilities.       |
                         | Cognitive Reasoning Base       |             | Imports: L0,L1,L2,L5,L_APP,    |
                         +--------------------------------+             |          L_RUNTIME             |
                                          |                             +--------------------------------+
                                          v
                         +--------------------------------+
                         | L0: ROUTING / FOUNDATION       |
                         | ZERO Static Upward Imports     |
                         | Runtime Seam: Lazy-import L5   |
                         +--------------------------------+

==================================================================================================================================================
                                             RESOLVED ARCHITECTURAL RULES
==================================================================================================================================================
| 1. ABSOLUTE TOP: L_OPS and L_TEST sit entirely above the system. They are the manipulators, not part of the runtime.           |
| 2. CORE GRAVITY: L6 down to L0 forms the unbreakable spine. Gravity only flows downward.                                       |
| 3. SATELLITE PLUG-INS: Satellites do not orbit randomly; they act as distinct, horizontal utility belts for specific layers.   |
| 4. THE ELEVATOR SHAFT: L0 remains at the absolute bottom, utilizing a lazy runtime import to reach L5 without cyclic breaks.   |
| 5. RUNTIME FLOOR: L3 is the architectural floor for L_RUNTIME; layers below it are primitive engine parts.                     |
==================================================================================================================================================