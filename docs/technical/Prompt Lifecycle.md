================================================================================================================================================
                                     AGENTIC SYSTEM — ISOLATED PROMPT COMPOSITION & LIFECYCLE ARCHITECTURE
================================================================================================================================================
  [ THE TOP LAYER: INGESTION & OBSERVABILITY ]                                [ THE SIDE LAYER: PROMPT STATE BUS (L4) ]
+---------------------------------------------------+                         +------------------------------------------------------------------------+
| L1: COGNITIVE STUDIO / L6: OBSERVABILITY          |                         | L4: STATE, MEMORY & PERSISTENCE [ COGNITIVE REGISTRY ]                 |
|---------------------------------------------------|                         |------------------------------------------------------------------------|
| - [L1] Ingests Raw Natural Language / UI Inputs.  |======(U0/C0 Proposals)=>| - Central SSOT for System (S0) and Instructional (I0) prompts.         |
| - [L1] Creates [U0] Intent (Zero Auth).           |                         | - Stores [TMPL] REASONING TEMPLATES (Jinja/Handlebars).                |
| - [L1] Pulls [C0] RAG Context.                    |                         | - Stores active few-shot matrices and calibration examples.            |
+---------------------------------------------------+                         | - [RULES] L4 never compiles. L4 only serves versioned strings.         |
                          |                                                   |           Direct strings in code are BLOCKED by AST Scanner.           |
                          |                                                   +------------------------------------------------------------------------+
                          v (Pulls Active S0/I0/D0 versions)                                             ||
=========================================================================================================||======================================
  [ THE CONTROL SPINE: ROUTING & ASSEMBLY ]                                                              ||
+-----------------------------------------------------------------------------------------+              ||
| L0 – ROUTING (PROMPT TRAFFIC CONTROL)                                                   |<=============||
|-----------------------------------------------------------------------------------------|              ||
| - Receives [U0] + [C0] from L1. Determines required [I0] mixins.                        |              ||
| - Packages Prompt BOM for Assembly. Packages pointers, NO strings.                      |              ||
+-----------------------------------------------------------------------------------------+              ||
                          |                                                                              ||
                          v (Dispatches Prompt BOM)                                                      ||
+-----------------------------------------------------------------------------------------+              ||
| ASSEMBLY STAGE (DETERMINISTIC COMPOSITION)                                              |              ||
|-----------------------------------------------------------------------------------------|              ||
| [ COMPILE ORDER IS STRICTLY ENFORCED - HIERARCHY OF AUTHORITY ]                         |              ||
| 1. [S0: SYSTEM]        - Hard-coded constitutions & invariants.  (HIGHEST AUTH)         |              ||
| 2. [I0: INSTRUCTIONAL] - Identity & "Mixin" agent behaviors.     (DOMAIN AUTH)          |              ||
| 3. [D0: INJECTIONS]    - Semantic fences, schemas, context caps. (BOUNDARY AUTH)        |              ||
| 4. [C0: DEPENDENCY]    - Elevator Shaft/RAG injected knowledge.  (INFO ONLY)            |              ||
| 5. [U0: USER PROMPT]   - Raw intent. Wrapped in delimiters.      (ZERO AUTH)            |              ||
|                                                                                         |              ||
| => [BLOCK] PROMPT INJECTION SCAN (Scans U0 for S0/I0 override attempts)                 |              ||
| => [TOKEN] TOKEN BUDGET CALCULATION (Truncates C0/U0 if S0+I0 maxed)                    |              ||
+-----------------------------------------------------------------------------------------+              ||
                          |                                                                              ||
                          v (Passes Compiled Prompt Artifact)                                            ||
=========================================================================================================||======================================
  [ THE BOTTOM LAYER: SOVEREIGN LLM GATEWAY ]                                                            ||
+-----------------------------------------------------------------------------------------+              ||
| SOVEREIGN LLM GATEWAY (THE ONLY OUTBOUND PROMPT SEAM)                                   |              ||
|-----------------------------------------------------------------------------------------|              ||
| - Consumes the CompiledPromptArtifact (Hash-signed).                                    |              ||
| - Translates S0/I0/U0 stack into provider-specific API formats.                         |              ||
| - Maps tool schemas to provider native tool-calling formats (OpenAI/Gemini).            |              ||
| - Injects mandatory stop-sequences from [D0].                                           |              ||
| - Logs EXACT final payload to Telemetry Ledger for determinism/replay validation.       |              ||
+-----------------------------------------------------------------------------------------+              ||
                          |                                                                              ||
                          v (To L2 Execution Core / Sandbox)                                             \/
================================================================================================================================================
  CORE PROMPT DATA CONTRACTS
================================================================================================================================================
| [1] PromptBOM (L0 -> Assembly)        : [trace_id, system_version_hash, mixins_required[], raw_u0, raw_c0, template_args]                    |
| [2] CompiledPromptArtifact (Assembly) : [final_system_string, final_user_string, allowed_tools_schema[], token_estimate,                     |
|                                          signature(HMAC-SHA256)] -> Signature prevents tampering between Assembly and LLM Gateway.           |
| [3] TemplateManifest (L4 Registry)    : [template_id, version, git_commit_hash, required_variables[], schema_version]                        |
================================================================================================================================================
