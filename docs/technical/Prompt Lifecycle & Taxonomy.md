========================================================================================================================
PROMPT LIFECYCLE & TAXONOMY (ADG-ENHANCED) — NON-LINEAR FLOW & FEEDBACK
========================================================================================================================
AUTHORITY: [ZERO] Unprivileged -> [INFORMATIONAL] Data -> [GOVERNED] Caps -> [BINDING] Rules -> [ABSOLUTE] Invariants
------------------------------------------------------------------------------------------------------------------------
1. PARALLEL INGESTION & CONTEXT LOADING (L1)
------------------------------------------------------------------------------------------------------------------------
• L1 INTENT: Raw NL/UI inputs -> [U0] Intent (ZERO) | ADG: generates_prompt (215)
• L1 RAG: Vector search (K=20), completeness scoring -> [C0] Context | ADG: retrieves_via (52)

------------------------------------------------------------------------------------------------------------------------
2. ROUTING & ASSEMBLY (L0)
------------------------------------------------------------------------------------------------------------------------
• CLASSIFY: Evaluates [U0]+[C0] vs L4 routing state.
• BRANCHING: Path A (High/Strict), Path B (Med/Std), Path C (Low/Fast), Path D (Novel/Learning).
• SLOT ASSEMBLY (Order): 1. S0 (Absolute) | 2. I0 (Governed) | 3. D0 (Binding) | 4. C0 (Info) | 5. U0 (Zero).
• SAFETY/CHECKS: Concurrent Injection Scan (U0 vs S0/I0), Token Budget, Authority Hierarchy Validation.
• OUTPUT: CompiledPromptArtifact (HMAC-SHA256) | ADG: consumes_prompt (11), prompt_template_used_by (45).

------------------------------------------------------------------------------------------------------------------------
3. VALIDATION & EXECUTION (L5 / L2)
------------------------------------------------------------------------------------------------------------------------
• L5 SAFETY: Pre-flight budget, policy compliance, injection scan, budget enforcement | ADG: applies_guardrail (68).
• L2 SANDBOX:
  - IF ALLOW: AST surgery, FS mutation -> SUCCESS (L4 version).
  - IF BLOCK: Log rejection, emit feedback to L4, NO mutation.
  - IF FAILURE: Rollback to snapshot -> HEALER LOOP -> Re-enter assembly with modified proposal.

------------------------------------------------------------------------------------------------------------------------
4. SLOT TAXONOMY & AUTHORITY GRADIENT
------------------------------------------------------------------------------------------------------------------------
SLOT | AUTHORITY | PURPOSE (Source) & EXAMPLES                          | ADG / EDGE DATA             | FEEDBACK LOOP
-----|-----------|------------------------------------------------------|-----------------------------|------------------
S0   | ABSOLUTE  | Constitutions/Invariants (L4 State/L5 Policy).       | reads_policy_state (1,317)  | Meta-learn failure ->
     |           | e.g., "Layer gravity", "Writes via UWG".             | Anchor for all reasoning.   | Update S0 policy.
-----|-----------|------------------------------------------------------|-----------------------------|------------------
I0   | GOVERNED  | Identity/Mixins (L4 State/Cap Defs).                 | prompt_template_used_by (45)| Low success ->
     |           | e.g., HealMixin, ValidateMixin, MCPHardened.         | Defines "How" agent acts.   | Revise/AB test.
-----|-----------|------------------------------------------------------|-----------------------------|------------------
D0   | BINDING   | Semantic Fences (L5 Active Guardian).                | applies_guardrail (68)      | High rejection ->
     |           | e.g., "Max file: 10KB", "No os.system".              | Constraints before commit.  | Relax/Tune thresholds.
-----|-----------|------------------------------------------------------|-----------------------------|------------------
C0   | INFO      | Grounding/RAG (L4 Index/L2.1 Snapshot).              | retrieves_via (52)          | Low groundedness ->
     |           | e.g., "ImportError resolved", AST snapshots.         | Grounding; no execution auth| Tune RAG/reranking.
-----|-----------|------------------------------------------------------|-----------------------------|------------------
U0   | ZERO      | Raw Intent (L1 Thinking/NL Input).                   | generates_prompt (215)      | Injection detected ->
     |           | e.g., "Fix module X", "Analyze coverage".            | Scanned for S0/I0 overrides | Strengthen S0 rules.

------------------------------------------------------------------------------------------------------------------------
5. DEPENDENCY FLOW PATTERNS
------------------------------------------------------------------------------------------------------------------------
• PARALLEL: L1 Intent + L1 RAG concurrent; L0 Assembly + L5 Validation parallel; L4 slot loading.
• CONDITIONAL: L0 routing branches (A/B/C/D); L5 outcomes (Allow/Block/Defer); L2 success/fail branches.
• FEEDBACK: Success -> Reinforce I0; Fail -> Healer Loop; Rejection -> D0 tuning; Meta-Learning (N>=100).
• CROSS-LAYER: L1->L0 (generates_prompt: 215); L0->L4 (reads_policy: 1,317); L5->L0 (applies_guardrail: 68).

------------------------------------------------------------------------------------------------------------------------
6. SOVEREIGN LLM GATEWAY (THE OUTBOUND SEAM)
------------------------------------------------------------------------------------------------------------------------
• RESPONSIBILITIES: Consume signed artifact, translate S0/I0/U0 to provider API (OpenAI/Gemini/Anthropic),
  map tool schemas, inject D0 stop-sequences, log final payload to Telemetry Ledger (determinism/replay).
• ENFORCEMENT: Single seam (prevents leakage), Signature verification (no tampering), Provider abstraction.

------------------------------------------------------------------------------------------------------------------------
7. CORE DATA CONTRACTS
------------------------------------------------------------------------------------------------------------------------
[1] PromptBOM: [trace_id, system_version_hash, mixins_required[], raw_u0, raw_c0, template_args]
[2] CompiledPromptArtifact: [final_system_string, final_user_string, allowed_tools_schema[], tokens, HMAC-SHA256]
[3] TemplateManifest: [template_id, version, git_commit_hash, required_variables[], schema_version]
[4] AuthoritySlot: [slot_type: S0|I0|D0|C0|U0, content, authority_level, source_layer]
[5] InjectionScanResult: [detected: bool, override_attempts[], risk_score, blocked: bool]
[6] RoutingDecision: [path: A|B|C|D, risk: H|M|L|N, rationale, confidence]
INVARIANT: C0/U0 slots carry NO route_mode, safety_threshold, execution_tier, or auth_token fields.

------------------------------------------------------------------------------------------------------------------------
METADATA & TOPOLOGY (LATEST REDIS HOT CACHE)
------------------------------------------------------------------------------------------------------------------------
TIMESTAMP: 03132026_1424 | DIGEST: ab160598f0aeab8e | ADG NODES: 8,253 | ADG EDGES: 225,857
LAYER DISTRIBUTION: L0: 372 | L1: 106 | L2: 326 | L4: 156 | L5: 627 | L6: 53
PROMPT EDGES: generates_prompt(215), consumes_prompt(11), prompt_template_used_by(45), reads_policy_state(1,317), applies_guardrail(68), retrieves_via(52)
CROSS-LAYER I/O: reads_from(66,985), writes_to(4,882)
LAST UPDATED: 2026-03-14 08:46 UTC — Non-linear flow with parallel execution, conditional branching, and cross-prompt learning
========================================================================================================================
