====================================================================================================================================================================================================================
                                                              PROMPT LIFECYCLE & TAXONOMY — AUTHORITY GRADIENT & FLOW DEPENDENCIES (ADG-ENHANCED)
====================================================================================================================================================================================================================
  AUTHORITY GRADIENT: ZERO (Unprivileged) ──────> INFORMATIONAL (Data) ──────> GOVERNED (Capabilities) ──────> BINDING (Constraints) ──────> ABSOLUTE (Invariants)
====================================================================================================================================================================================================================
  [ STAGE 1: INGESTION & INTENT FORMATION ]        [ STAGE 2: ROUTING & SLOT ASSEMBLY ]                                                [ STAGE 3: VALIDATION & EXECUTION ]
+-------------------------------+         +-------------------------------------------------------------------------+         +-------------------------------+         +-------------------------------+
| L1: COGNITIVE STUDIO          |         | L0: ROUTING (PROMPT TRAFFIC CONTROL)                                    |         | L5: SAFETY GUARDIAN           |         | L2: EXECUTION SANDBOX         |
|-------------------------------|         |-------------------------------------------------------------------------|         |-------------------------------|         |-------------------------------|
| INGESTION:                    |         | CLASSIFICATION:                                                         |         | PRE-FLIGHT VALIDATION:        |         | EXECUTION:                    |
| - Raw NL / UI inputs          |-------->| - Receives [U0] + [C0] from L1                                          |-------->| - Evaluates assembled prompt  |-------->| - Applies approved change set |
| - Creates [U0] Intent (ZERO)  |         | - Classifies vs. L4 routing state                                       |         | - Checks vs. L4 policy        |         | - AST surgery / FS mutation   |
| - Pulls [C0] RAG Context      |         | - Selects path (A/B/C/D)                                                |         | - Budget enforcement          |         | - SOLE durable write authority|
|                               |         | - Triggers Elevator Shaft (L0<->L5)                                     |         | - BLOCKS or ALLOWS            |         |                               |
| ADG: generates_prompt (215)   |         |                                                                         |         | ADG: applies_guardrail (68)   |         | SUCCESS → L4 versioning       |
+-------------------------------+         | ASSEMBLY ORDER (Hierarchy of Authority):                                |         +-------------------------------+         | FAILURE → Healer Loop         |
                                          | 1. [S0: SYSTEM] - Constitutions (ABSOLUTE)                              |                                                 +-------------------------------+
                                          | 2. [I0: INSTRUCTIONAL] - Mixins (GOVERNED)                              |
                                          | 3. [D0: INJECTIONS] - Fences (BINDING)                                  |
                                          | 4. [C0: DEPENDENCY] - RAG/Context (INFORMATIONAL)                       |
                                          | 5. [U0: USER PROMPT] - Raw intent (ZERO)                                |
                                          |                                                                         |
                                          | SAFETY CHECKS:                                                          |
                                          | - Prompt injection scan (U0 for S0/I0 override attempts)               |
                                          | - Token budget calculation (Truncates C0/U0 if S0+I0 maxed)            |
                                          |                                                                         |
                                          | OUTPUT: CompiledPromptArtifact (HMAC-SHA256 signed)                    |
                                          | ADG: consumes_prompt (11), prompt_template_used_by (45)                |
                                          +-------------------------------------------------------------------------+
====================================================================================================================================================================================================================
  [ SLOT TAXONOMY — AUTHORITY GRADIENT DETAIL ]
====================================================================================================================================================================================================================
+-------------------------------------------------------------------------------------------------------------------------------------------------+
| SLOT S0: SYSTEM / STATE (ABSOLUTE AUTHORITY)                                                                                                    |
+-------------------------------------------------------------------------------------------------------------------------------------------------+
| PURPOSE: Hard-coded constitutions + invariants (Determinism, Safety, No Upward Imports)                                                        |
| SOURCE: L4 Master State / L5 Policy Blueprints                                                                                                 |
| AUTHORITY: ABSOLUTE — Immutable anchor for all reasoning                                                                                       |
| EXAMPLES: "Never mutate routing decisions", "Layer gravity must be preserved", "All writes via UWG"                                            |
| ADG: reads_policy_state (1,317 edges) — L0/L1/L2 read S0 policy state                                                                          |
+-------------------------------------------------------------------------------------------------------------------------------------------------+
                                                                           |
                                                                           V (Foundational directive)
+-------------------------------------------------------------------------------------------------------------------------------------------------+
| SLOT I0: INSTRUCTIONAL (GOVERNED AUTHORITY)                                                                                                     |
+-------------------------------------------------------------------------------------------------------------------------------------------------+
| PURPOSE: Identity and "Mixin" behaviors (HealMixin, ValidateMixin, MCPHardenedMixin)                                                           |
| SOURCE: L4 State (Mixins) / Step 1 Capability Definitions                                                                                      |
| AUTHORITY: GOVERNED — Defines "How" an agent operates                                                                                          |
| EXAMPLES: "When healing, analyze blast radius first", "Validate all imports via ADG", "Emit determinism digest"                                |
| INHERITANCE: Inherited from [[SovereignBaseAgent]] root SSOT                                                                                   |
| ADG: prompt_template_used_by (45 edges) — Templates instantiated by agents                                                                     |
+-------------------------------------------------------------------------------------------------------------------------------------------------+
                                                                           |
                                                                           V (Capability boundaries)
+-------------------------------------------------------------------------------------------------------------------------------------------------+
| SLOT D0: INJECTIONS (BINDING AUTHORITY)                                                                                                        |
+-------------------------------------------------------------------------------------------------------------------------------------------------+
| PURPOSE: Semantic fences, tool constraints, scope boundaries                                                                                   |
| SOURCE: L5 Safety (Active Guardian) policy evaluators                                                                                          |
| AUTHORITY: BINDING — Constraints applied before commit                                                                                         |
| EXAMPLES: "Max file size: 10KB", "Allowed tools: [read, write, analyze]", "Forbidden imports: [os.system, eval]"                               |
| ENFORCEMENT: Post-retrieval redaction, context budget enforcement, stop-sequence injection                                                     |
| ADG: applies_guardrail (68 edges) — Guardrails applied at assembly time                                                                        |
+-------------------------------------------------------------------------------------------------------------------------------------------------+
                                                                           |
                                                                           V (Enforced constraints)
+-------------------------------------------------------------------------------------------------------------------------------------------------+
| SLOT C0: DEPENDENCY (INFORMATIONAL AUTHORITY)                                                                                                  |
+-------------------------------------------------------------------------------------------------------------------------------------------------+
| PURPOSE: RAG / Elevator Shaft injected knowledge and citations                                                                                 |
| SOURCE: L4 Knowledge Index / L2.1 boundary_snapshot.json                                                                                       |
| AUTHORITY: INFORMATIONAL — Grounding data, no execution authority                                                                              |
| EXAMPLES: "Previous healing: ImportError resolved via dependency_repair", "ADG shows 52 retrieves_via edges", "Test coverage: 78%"             |
| CONTENT: High-fidelity artifacts (JSON Manifests, AST Snapshots, RAG chunks)                                                                   |
| SOVEREIGNTY: Cannot mutate routing, cannot escalate tiers, cannot alter thresholds                                                             |
+-------------------------------------------------------------------------------------------------------------------------------------------------+
                                                                           |
                                                                           V (Grounding data)
+-------------------------------------------------------------------------------------------------------------------------------------------------+
| SLOT U0: USER PROMPT (ZERO AUTHORITY)                                                                                                          |
+-------------------------------------------------------------------------------------------------------------------------------------------------+
| PURPOSE: Raw "What" — User intent without authority                                                                                            |
| SOURCE: L1 Thinking / Natural language input                                                                                                   |
| AUTHORITY: ZERO — Non-mutant proposal, wrapped in delimiters                                                                                   |
| EXAMPLES: "Fix the ImportError in module X", "Analyze test coverage gaps", "Refactor layer violations"                                         |
| AIRLOCK: Cannot pass L1→L0 without wrapping in authority hierarchy                                                                             |
| INJECTION PROTECTION: Scanned for S0/I0 override attempts before assembly                                                                      |
+-------------------------------------------------------------------------------------------------------------------------------------------------+
====================================================================================================================================================================================================================
  [ DEPENDENCY FLOW PATTERNS ]
====================================================================================================================================================================================================================
+------------------------------------------+  +------------------------------------------+  +------------------------------------------+  +------------------------------------------+
| PARALLEL DEPENDENCIES                    |  | SEQUENTIAL DEPENDENCIES                  |  | FEEDBACK DEPENDENCIES                    |  | CROSS-LAYER DEPENDENCIES                 |
|------------------------------------------|  |------------------------------------------|  |------------------------------------------|  |------------------------------------------|
| L1 Intent + L1 RAG Context:              |  | INGESTION → ROUTING → ASSEMBLY:          |  | EXECUTION OUTCOME → L4 STATE:            |  | L1 → L0 (Intent):                        |
| - Intent formation independent           |  | 1. L1: Ingest raw input                  |  | - Success → Version in L4                |  | - generates_prompt (215 edges)           |
| - RAG retrieval concurrent               |  | 2. L1: Create U0 + pull C0               |  | - Failure → Healer loop                  |  |                                          |
| - Both feed into L0 routing              |  | 3. L0: Classify + route                  |  | - Healer → Re-enter assembly gate        |  | L0 → L4 (State Read):                    |
|                                          |  | 4. L0: Assemble S0+I0+D0+C0+U0           |  |                                          |  | - reads_policy_state (1,317 edges)       |
| L0 Assembly + L5 Validation:             |  | 5. L5: Validate assembled prompt         |  | META-LEARNING → ROUTING CONFIG:          |  |                                          |
| - Assembly prepares artifact             |  | 6. L2: Execute if allowed                |  | - Analyzes prompt outcomes               |  | L5 → L0 (Guardrails):                    |
| - L5 validates in parallel               |  | 7. L4: Version or trigger heal           |  | - Proposes S0/I0/D0 adjustments          |  | - applies_guardrail (68 edges)           |
| - Join at execution gate                 |  |                                          |  | - Applies to future prompts              |  |                                          |
|                                          |  | CRITICAL: Each step depends on previous  |  |                                          |  | L0 → L2 (Execution):                     |
| L4 Template + L0 Compilation:            |  | - Cannot skip steps                      |  | TEMPLATE EVOLUTION:                      |  | - consumes_prompt (11 edges)             |
| - Templates stored in L4                 |  | - Cannot reorder authority hierarchy     |  | - L4 templates updated based on success  |  |                                          |
| - L0 compiles on-demand                  |  | - S0 always first, U0 always last        |  | - prompt_template_used_by tracks usage   |  | L4 → L0 (Templates):                     |
| - Memoization for repeated prompts       |  |                                          |  | - High-success templates promoted        |  | - prompt_template_used_by (45 edges)     |
+------------------------------------------+  +------------------------------------------+  +------------------------------------------+  +------------------------------------------+
====================================================================================================================================================================================================================
  [ SOVEREIGN LLM GATEWAY — THE ONLY OUTBOUND PROMPT SEAM ]
====================================================================================================================================================================================================================
+-------------------------------------------------------------------------------------------------------------------------------------------------+
| GATEWAY RESPONSIBILITIES:                                                                                                                       |
| 1. Consumes CompiledPromptArtifact (HMAC-SHA256 signed)                                                                                        |
| 2. Translates S0/I0/U0 stack into provider-specific API formats (OpenAI/Gemini/Anthropic)                                                      |
| 3. Maps tool schemas to provider native tool-calling formats                                                                                   |
| 4. Injects mandatory stop-sequences from D0                                                                                                    |
| 5. Logs EXACT final payload to Telemetry Ledger for determinism/replay validation                                                              |
|                                                                                                                                                 |
| SOVEREIGNTY ENFORCEMENT:                                                                                                                        |
| - Single outbound seam prevents prompt leakage                                                                                                 |
| - Signature verification prevents tampering between Assembly and Gateway                                                                       |
| - Telemetry logging enables deterministic replay                                                                                               |
| - Provider abstraction maintains portability                                                                                                   |
+-------------------------------------------------------------------------------------------------------------------------------------------------+
====================================================================================================================================================================================================================
  CORE PROMPT DATA CONTRACTS
====================================================================================================================================================================================================================
| [1] PromptBOM (L0 → Assembly)        : [trace_id, system_version_hash, mixins_required[], raw_u0, raw_c0, template_args]                                                                                     |
| [2] CompiledPromptArtifact (Assembly): [final_system_string, final_user_string, allowed_tools_schema[], token_estimate, signature(HMAC-SHA256)]                                                               |
|                                        → Signature prevents tampering between Assembly and LLM Gateway                                                                                                         |
| [3] TemplateManifest (L4 Registry)   : [template_id, version, git_commit_hash, required_variables[], schema_version]                                                                                          |
| [4] AuthoritySlot                    : [slot_type: S0|I0|D0|C0|U0, content: str, authority_level: int, source_layer: str]                                                                                     |
| [5] PromptInjectionScanResult        : [detected: bool, override_attempts: list[str], risk_score: float, blocked: bool]                                                                                       |
|                                                                                                                                                                                                                |
| SOVEREIGNTY INVARIANT: C0 and U0 slots carry NO route_mode, safety_threshold, execution_tier, or auth_token fields                                                                                            |
====================================================================================================================================================================================================================

ADG CACHE INTEGRATION: Enhanced Redis MCP client enables full prompt lifecycle dependency analysis
TIMESTAMP: 03132026_1424 | ADG NODES: 8,234 | ADG EDGES: 224,969 | L0: 372 modules | L1: 106 modules | L4: 154 modules | L5: 627 modules
PROMPT EDGE TOPOLOGY: generates_prompt(215), consumes_prompt(11), prompt_template_used_by(45), reads_policy_state(1,317), applies_guardrail(68)
LAST UPDATED: 2026-03-14 08:38 UTC — Merged Lifecycle + Taxonomy with flow dependencies and authority gradient
