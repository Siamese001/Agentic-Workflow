# Prompt Assembly — Line-by-Line Requirement Matrix

Doctrine corpus:

- **PARENT** — `docs/reference/03B_PA_Prompt_Assembly/Prompt_Assembly.md`
- **PA.0** — `docs/reference/03B_PA_Prompt_Assembly/PA.0_Boundary_Check.md`
- **PA.1** — `docs/reference/03B_PA_Prompt_Assembly/PA.1_Load_Resolve_Prompt_BOM.md`
- **PA.2** — `docs/reference/03B_PA_Prompt_Assembly/PA.2_Slot_Composition.md`
- **PA.3** — `docs/reference/03B_PA_Prompt_Assembly/PA.3_Airlock_Security_Pass.md`
- **PA.4** — `docs/reference/03B_PA_Prompt_Assembly/PA.4_Validate_Slot_Contract.md`
- **PA.5** — `docs/reference/03B_PA_Prompt_Assembly/PA.5_Token_Budget_Determinism.md`
- **PA.6** — `docs/reference/03B_PA_Prompt_Assembly/PA.6_Provider_Aware_Rendering.md`
- **PA.7** — `docs/reference/03B_PA_Prompt_Assembly/PA.7_Final_Emit_Compiled_Prompt_Artifact.md`
- **PA.8** — `docs/reference/03B_PA_Prompt_Assembly/PA.8_Authority_RedTeam_Slot_Verification.md`

**Tally:** 1426 PASS / 0 FAIL (of 1426 line-level requirements)

**Generated:** 2026-04-27T02:03:56.144041+00:00

## Per-stage roll-up

| Stage | Total | PASS | FAIL |
|---|---:|---:|---:|
| PA.0 | 142 | 142 | 0 |
| PA.1 | 152 | 152 | 0 |
| PA.2 | 142 | 142 | 0 |
| PA.3 | 156 | 156 | 0 |
| PA.4 | 138 | 138 | 0 |
| PA.5 | 156 | 156 | 0 |
| PA.6 | 143 | 143 | 0 |
| PA.7 | 180 | 180 | 0 |
| PA.8 | 46 | 46 | 0 |
| PARENT | 171 | 171 | 0 |

## Evidence-source legend

- `runtime_symbol` — token is a public name in `agentic_core.prompt_governance.prompt_assembly`
- `receipt_key` — token is a key (any depth) in one of the 8 doctrine receipt envelopes
- `status_value` — token is a member of `PAStatus`
- `forbidden_token` — token is a member of `FORBIDDEN_DISPOSITIONS ∪ FORBIDDEN_EXECUTION_VERBS`
- `source_file` — token appears in `agentic_core/prompt_governance/**/*.py` source corpus
- `test_corpus` — token appears in PA test files / their filenames
- `doctrine_xref` — token appears in another PA doctrine file (cross-reference)
- `prose_keyword` — the requirement text contains a documented prose keyword that maps to a known runtime artefact


## PA.0

| # | Line | Section | Sub-section | Requirement | Status | Evidence |
|---:|---:|---|---|---|:---:|---|
| 1 | 10 | GLOBAL NO-OVERLAP LAW |  | 00A L5 owns governance certification evidence, not live runtime dispositions and not durable write admission. | **PASS** | doctrine_xref, source_file, test_corpus |
| 2 | 11 | GLOBAL NO-OVERLAP LAW |  | 00B L4/UWG owns durable system-of-record state and durable write admission, not planning, routing, retrieval, execution, Exit disposition, or L6 learning mechanics. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 3 | 12 | GLOBAL NO-OVERLAP LAW |  | 00C Runtime Gates owns G01-G29 current-run GateVerdict law, not final Exit X3 aggregation and not L5 certification evidence. | **PASS** | doctrine_xref, source_file, test_corpus |
| 4 | 13 | GLOBAL NO-OVERLAP LAW |  | 00X owns traceability and no-loss mapping only. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 5 | 14 | GLOBAL NO-OVERLAP LAW |  | 01 Intake owns request envelope validation and identity/session/tenant baseline only. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 6 | 15 | GLOBAL NO-OVERLAP LAW |  | 02 L1 owns advisory interpretation and planning only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 7 | 16 | GLOBAL NO-OVERLAP LAW |  | 03 L0/L3 owns deterministic route selection and optional workflow orchestration only. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 8 | 17 | GLOBAL NO-OVERLAP LAW |  | C0 owns retrieval/evidence contracts only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 9 | 18 | GLOBAL NO-OVERLAP LAW |  | PA owns prompt packet construction only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 10 | 19 | GLOBAL NO-OVERLAP LAW |  | 04 L2 owns bounded execution and sealing only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 11 | 20 | GLOBAL NO-OVERLAP LAW |  | 05 Exit owns current-run checkout aggregation and exactly one X3 disposition only. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 12 | 21 | GLOBAL NO-OVERLAP LAW |  | 06 L6 owns completed-run evaluation, RCA, and future-run learning proposals only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 13 | 22 | GLOBAL NO-OVERLAP LAW |  | 99 owns proof harnesses only; it does not own runtime behavior. | **PASS** | doctrine_xref, source_file, test_corpus |
| 14 | 25 | REFERENCE POINTERS |  | Cross-cutting governance/certification evidence: 00A_L5_Governance_Safety/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 15 | 26 | REFERENCE POINTERS |  | Durable state and Universal Write Gateway: 00B_L4_State_Archive_and_UWG/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 16 | 27 | REFERENCE POINTERS |  | Current-run reusable gate mesh: 00C_Runtime_Gates_Current_Run_Mesh/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 17 | 28 | REFERENCE POINTERS |  | Traceability and zero-loss proof: 00X_Requirements_Traceability_and_No_Loss_Map.md | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 18 | 29 | REFERENCE POINTERS |  | End-to-end runtime proof harness: 99_End_to_End_Runtime_Proof_and_Acceptance/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 19 | 45 | UNIQUE OWNERSHIP SURFACE |  | Prompt Assembly eligibility and upstream input boundary only | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 20 | 48 | THIS FILE OWNS |  | PAAssemblyInput, BoundaryCheckReceipt, required-input inventory, upstream reference map, assembly gap reports | **PASS** | doctrine_xref, prose_keyword, runtime_symbol, source_file, test_corpus |
| 21 | 51 | THIS FILE DOES NOT OWN |  | PromptBOM resolution, slot composition, security pass, token budget, provider rendering, final signing, retrieval, routing, execution | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 22 | 54 | GLOBAL NO-OVERLAP LOCK |  | L1 owns intent interpretation, task_spec, query_spec, ambiguity register, and planning recommendations. | **PASS** | doctrine_xref, source_file, test_corpus |
| 23 | 55 | GLOBAL NO-OVERLAP LOCK |  | L0 owns route selection, RouteContract, execution_form, provider lane, route risk, and route authority. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 24 | 56 | GLOBAL NO-OVERLAP LOCK |  | C0 owns retrieval, hydration, graph expansion, evidence shaping, verification, support scoring, and FinalEvidenceContract. | **PASS** | doctrine_xref, source_file, test_corpus |
| 25 | 57 | GLOBAL NO-OVERLAP LOCK |  | L5 owns policy, authority context, origin trust, egress, replay, audit, HITL re-clearance, and certification evidence. | **PASS** | doctrine_xref, source_file, test_corpus |
| 26 | 58 | GLOBAL NO-OVERLAP LOCK |  | Prompt Assembly owns only bounded prompt-packet composition and signed prompt artifact emission. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 27 | 59 | GLOBAL NO-OVERLAP LOCK |  | L2 owns bounded execution, SovereignLLMGateway dispatch, provider/model/tool calls, and sealed work artifacts. | **PASS** | doctrine_xref, source_file, test_corpus |
| 28 | 60 | GLOBAL NO-OVERLAP LOCK |  | Runtime Gates and Exit Eval own current-run dispositions. | **PASS** | doctrine_xref, source_file, test_corpus |
| 29 | 61 | GLOBAL NO-OVERLAP LOCK |  | UWG/L4 owns durable write admission and system-of-record mutation. | **PASS** | doctrine_xref, source_file, test_corpus |
| 30 | 62 | GLOBAL NO-OVERLAP LOCK |  | L6 owns completed-run evaluation, root-cause analysis, promotion proposals, and future-run learning. | **PASS** | doctrine_xref, source_file, test_corpus |
| 31 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ALLOW | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 32 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | DENY | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 33 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | CLARIFY | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 34 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ABSTAIN | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 35 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | REROUTE | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 36 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | SHRINK_SCOPE | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 37 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | RETRY | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 38 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | HEAL | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 39 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ESCALATE_HITL | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 40 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | QUARANTINE | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 41 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | REDACT | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 42 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | SAFE_FALLBACK | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 43 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | MARK_DEGRADED | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 44 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | COMMIT_REQUEST | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 45 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | BLOCK_COMMIT | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 46 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ALLOW_FINISH | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 47 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | approve_execution | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 48 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | approve_output | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 49 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | approve_write | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 50 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | call_provider | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 51 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | execute_tool | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 52 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | mutate_l4 | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 53 | 70 | ALLOWED OUTPUT STYLE |  | receipts, manifests, hashes, validation statuses, assembly statuses, gap reports, artifact refs, replay/audit refs | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 54 | 76 | END OVERWRITE RECONCILIATION HEADER | PARENT | Prompt_Assembly.md | **PASS** | doctrine_xref, source_file, test_corpus |
| 55 | 79 | END OVERWRITE RECONCILIATION HEADER | ROLE | Detailed child file for PA.0 BOUNDARY CHECK. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 56 | 80 | END OVERWRITE RECONCILIATION HEADER | ROLE | Defines the implementation-grade requirements for its unique Prompt Assembly surface. | **PASS** | doctrine_xref, source_file, test_corpus |
| 57 | 81 | END OVERWRITE RECONCILIATION HEADER | ROLE | Emits Prompt Assembly evidence only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 58 | 82 | END OVERWRITE RECONCILIATION HEADER | ROLE | Does not emit runtime dispositions. | **PASS** | doctrine_xref, source_file, test_corpus |
| 59 | 83 | END OVERWRITE RECONCILIATION HEADER | ROLE | Does not retrieve, route, execute, call providers, write durable state, or promote learning. | **PASS** | doctrine_xref, source_file, test_corpus |
| 60 | 87 | WHY THIS FILE EXISTS |  | Prompt Assembly is a high-risk boundary because it binds rules, evidence, task text, schema, tools, provider metadata, | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 61 | 89 | WHY THIS FILE EXISTS |  | This child isolates one Prompt Assembly surface so the parent stays doctrinal and no other layer inherits prompt assembly | **PASS** | doctrine_xref, source_file, test_corpus |
| 62 | 91 | WHY THIS FILE EXISTS |  | This child is intentionally detailed enough for implementation, tests, traces, and replay evidence. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 63 | 95 | PRIMARY QUESTION |  | "Prompt Assembly eligibility and upstream input boundary only?" | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 64 | 99 | SOURCE OWNERSHIP BOUNDARY |  | This file may emit assembly receipts, manifests, hashes, statuses, and gap reports for its unique surface. | **PASS** | doctrine_xref, source_file, test_corpus |
| 65 | 100 | SOURCE OWNERSHIP BOUNDARY |  | This file must not fetch missing data. | **PASS** | doctrine_xref, source_file, test_corpus |
| 66 | 101 | SOURCE OWNERSHIP BOUNDARY |  | This file must not modify RouteContract, PlanContract, FinalEvidenceContract, policy, registry, capability, sandbox, or L4 state. | **PASS** | doctrine_xref, source_file, test_corpus |
| 67 | 102 | SOURCE OWNERSHIP BOUNDARY |  | This file must not approve L2 execution. It only prepares evidence for L2 validation. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 68 | 104 | SOURCE OWNERSHIP BOUNDARY | PAAssemblyInput | 1. PAAssemblyInput | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 69 | 107 | SOURCE OWNERSHIP BOUNDARY | PURPOSE | Normalize all upstream references into one assembly request. | **PASS** | doctrine_xref, source_file, test_corpus |
| 70 | 108 | SOURCE OWNERSHIP BOUNDARY | PURPOSE | Preserve the difference between references and payloads. | **PASS** | doctrine_xref, source_file, test_corpus |
| 71 | 109 | SOURCE OWNERSHIP BOUNDARY | PURPOSE | Prevent Prompt Assembly from being invoked as a hidden retriever, router, executor, or policy authority. | **PASS** | doctrine_xref, source_file, test_corpus |
| 72 | 112 | SOURCE OWNERSHIP BOUNDARY | FIELDS | assembly_request_id | **PASS** | doctrine_xref, prose_keyword |
| 73 | 113 | SOURCE OWNERSHIP BOUNDARY | FIELDS | request_id / run_id / trace_id | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 74 | 114 | SOURCE OWNERSHIP BOUNDARY | FIELDS | route_id / plan_id | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 75 | 115 | SOURCE OWNERSHIP BOUNDARY | FIELDS | L1PlanContract_ref | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 76 | 116 | SOURCE OWNERSHIP BOUNDARY | FIELDS | L0RouteContract_ref | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 77 | 117 | SOURCE OWNERSHIP BOUNDARY | FIELDS | C0FinalEvidenceContract_ref if grounding_required | **PASS** | doctrine_xref, prose_keyword, runtime_symbol, source_file, test_corpus |
| 78 | 118 | SOURCE OWNERSHIP BOUNDARY | FIELDS | governance_artifact_refs[] | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 79 | 119 | SOURCE OWNERSHIP BOUNDARY | FIELDS | AgentSpec_ref | **PASS** | doctrine_xref, prose_keyword, source_file |
| 80 | 120 | SOURCE OWNERSHIP BOUNDARY | FIELDS | response_schema_contract_ref | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 81 | 121 | SOURCE OWNERSHIP BOUNDARY | FIELDS | raw_user_task_ref | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 82 | 122 | SOURCE OWNERSHIP BOUNDARY | FIELDS | neutralized_user_task_candidate_ref if already available | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 83 | 123 | SOURCE OWNERSHIP BOUNDARY | FIELDS | provider_target_ref | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 84 | 124 | SOURCE OWNERSHIP BOUNDARY | FIELDS | model_policy_ref | **PASS** | doctrine_xref, prose_keyword |
| 85 | 125 | SOURCE OWNERSHIP BOUNDARY | FIELDS | replay_key | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 86 | 126 | SOURCE OWNERSHIP BOUNDARY | FIELDS | policy_hash | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 87 | 127 | SOURCE OWNERSHIP BOUNDARY | FIELDS | blueprint_hash | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 88 | 128 | SOURCE OWNERSHIP BOUNDARY | FIELDS | route_digest | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 89 | 129 | SOURCE OWNERSHIP BOUNDARY | FIELDS | idempotency_nonce | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 90 | 130 | SOURCE OWNERSHIP BOUNDARY | FIELDS | expected_artifact_type | **PASS** | doctrine_xref, prose_keyword |
| 91 | 131 | SOURCE OWNERSHIP BOUNDARY | FIELDS | assembly_budget_hint | **PASS** | doctrine_xref, prose_keyword |
| 92 | 134 | MUST CHECK |  | request_id, run_id, trace_id exist. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 93 | 135 | MUST CHECK |  | L1PlanContract_ref exists. | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 94 | 136 | MUST CHECK |  | L0RouteContract_ref exists. | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 95 | 137 | MUST CHECK |  | route_id matches RouteContract. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 96 | 138 | MUST CHECK |  | plan_id matches PlanContract. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 97 | 139 | MUST CHECK |  | policy_hash is present. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 98 | 140 | MUST CHECK |  | replay_key is present when route requires replay. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 99 | 141 | MUST CHECK |  | provider lane is declared when model execution is expected. | **PASS** | doctrine_xref, source_file, test_corpus |
| 100 | 142 | MUST CHECK |  | response schema contract exists when structured output is required. | **PASS** | doctrine_xref, source_file, test_corpus |
| 101 | 143 | MUST CHECK |  | C0FinalEvidenceContract_ref exists when grounding_required = true. | **PASS** | doctrine_xref, prose_keyword, runtime_symbol, source_file, test_corpus |
| 102 | 144 | MUST CHECK |  | C0FinalEvidenceContract_ref is absent or marked not_applicable when route is terminal R1/R5. | **PASS** | doctrine_xref, prose_keyword, runtime_symbol, source_file, test_corpus |
| 103 | 145 | MUST CHECK | Boundary Checklist | 2. Boundary Checklist | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 104 | 148 | MUST CHECK | CHECKS | C0 already retrieved if grounding is required. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 105 | 149 | MUST CHECK | CHECKS | L0 already selected the route. | **PASS** | doctrine_xref, source_file, test_corpus |
| 106 | 150 | MUST CHECK | CHECKS | L1 already produced the task/plan contract. | **PASS** | doctrine_xref, source_file, test_corpus |
| 107 | 151 | MUST CHECK | CHECKS | L5 evidence refs are present where the RouteContract requires them. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 108 | 152 | MUST CHECK | CHECKS | PA is not being asked to retrieve, route, execute, write, or approve output. | **PASS** | doctrine_xref, source_file, test_corpus |
| 109 | 153 | MUST CHECK | CHECKS | Terminal short-circuit routes do not accidentally enter model prompt assembly unless explicitly converted by a governed contract. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 110 | 154 | MUST CHECK | CHECKS | Managed workflow steps include current step context but not authority to expand the workflow. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 111 | 155 | MUST CHECK | Gap Handling | 3. Gap Handling | **PASS** | doctrine_xref, source_file, test_corpus |
| 112 | 158 | MUST CHECK | Gap Handling | emit PA_INPUT_INCOMPLETE or PA_BOUNDARY_MISMATCH. | **PASS** | doctrine_xref, prose_keyword, source_file, status_value, test_corpus |
| 113 | 159 | MUST CHECK | Gap Handling | attach missing_required_refs[]. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file |
| 114 | 160 | MUST CHECK | Gap Handling | attach mismatched_refs[]. | **PASS** | doctrine_xref, prose_keyword |
| 115 | 161 | MUST CHECK | Gap Handling | attach upstream_owner_hint = L1 \| L0 \| C0 \| L5 \| AgentSpec \| unknown. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 116 | 162 | MUST CHECK | Gap Handling | do not fill gaps from user text. | **PASS** | doctrine_xref, source_file, test_corpus |
| 117 | 163 | MUST CHECK | Gap Handling | do not fetch missing evidence. | **PASS** | doctrine_xref, source_file, test_corpus |
| 118 | 164 | MUST CHECK | Gap Handling | do not proceed to PA.1. | **PASS** | doctrine_xref, source_file, test_corpus |
| 119 | 169 | STATUS VALUES |  | PA_READY | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 120 | 170 | STATUS VALUES |  | PA_INPUT_INCOMPLETE | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 121 | 171 | STATUS VALUES |  | PA_BOUNDARY_MISMATCH | **PASS** | doctrine_xref, prose_keyword, source_file, status_value, test_corpus |
| 122 | 172 | STATUS VALUES |  | PA_REQUIRES_UPSTREAM_REPAIR | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 123 | 176 | MUST EMIT |  | PAAssemblyInput | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 124 | 177 | MUST EMIT |  | BoundaryCheckReceipt | **PASS** | doctrine_xref, prose_keyword |
| 125 | 178 | MUST EMIT |  | required_input_inventory | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 126 | 179 | MUST EMIT |  | upstream_reference_map | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 127 | 180 | MUST EMIT |  | assembly_gap_report | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 128 | 181 | MUST EMIT |  | boundary_status_receipt | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 129 | 185 | MUST NOT |  | retrieve evidence | **PASS** | doctrine_xref, source_file, test_corpus |
| 130 | 186 | MUST NOT |  | route or reroute | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 131 | 187 | MUST NOT |  | call a model provider | **PASS** | doctrine_xref, source_file, test_corpus |
| 132 | 188 | MUST NOT |  | execute a tool | **PASS** | doctrine_xref, source_file, test_corpus |
| 133 | 189 | MUST NOT |  | approve the final answer | **PASS** | doctrine_xref, source_file, test_corpus |
| 134 | 190 | MUST NOT |  | commit durable state | **PASS** | doctrine_xref, source_file, test_corpus |
| 135 | 191 | MUST NOT |  | emit runtime dispositions | **PASS** | doctrine_xref, source_file, test_corpus |
| 136 | 192 | MUST NOT |  | silently drop mandatory evidence, authority, schema, or replay metadata | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 137 | 196 | ACCEPTANCE TESTS |  | No code path in this child retrieves evidence, routes, executes, calls providers, writes L4, or emits runtime disposition. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 138 | 197 | ACCEPTANCE TESTS |  | All emitted receipts preserve request_id, run_id, trace_id, route_id, policy_hash, and replay_key when available. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 139 | 198 | ACCEPTANCE TESTS |  | All gap conditions are explicit and replayable. | **PASS** | doctrine_xref, source_file, test_corpus |
| 140 | 199 | ACCEPTANCE TESTS |  | Missing L0 RouteContract produces PA_INPUT_INCOMPLETE. | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 141 | 200 | ACCEPTANCE TESTS |  | grounding_required=true without C0FinalEvidenceContract_ref produces PA_INPUT_INCOMPLETE. | **PASS** | doctrine_xref, prose_keyword, runtime_symbol, source_file, status_value, test_corpus |
| 142 | 201 | ACCEPTANCE TESTS |  | RouteContract terminal short-circuit plus provider prompt request produces PA_BOUNDARY_MISMATCH. | **PASS** | doctrine_xref, prose_keyword, source_file, status_value, test_corpus |

## PA.1

| # | Line | Section | Sub-section | Requirement | Status | Evidence |
|---:|---:|---|---|---|:---:|---|
| 1 | 10 | GLOBAL NO-OVERLAP LAW |  | 00A L5 owns governance certification evidence, not live runtime dispositions and not durable write admission. | **PASS** | doctrine_xref, source_file, test_corpus |
| 2 | 11 | GLOBAL NO-OVERLAP LAW |  | 00B L4/UWG owns durable system-of-record state and durable write admission, not planning, routing, retrieval, execution, Exit disposition, or L6 learning mechanics. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 3 | 12 | GLOBAL NO-OVERLAP LAW |  | 00C Runtime Gates owns G01-G29 current-run GateVerdict law, not final Exit X3 aggregation and not L5 certification evidence. | **PASS** | doctrine_xref, source_file, test_corpus |
| 4 | 13 | GLOBAL NO-OVERLAP LAW |  | 00X owns traceability and no-loss mapping only. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 5 | 14 | GLOBAL NO-OVERLAP LAW |  | 01 Intake owns request envelope validation and identity/session/tenant baseline only. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 6 | 15 | GLOBAL NO-OVERLAP LAW |  | 02 L1 owns advisory interpretation and planning only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 7 | 16 | GLOBAL NO-OVERLAP LAW |  | 03 L0/L3 owns deterministic route selection and optional workflow orchestration only. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 8 | 17 | GLOBAL NO-OVERLAP LAW |  | C0 owns retrieval/evidence contracts only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 9 | 18 | GLOBAL NO-OVERLAP LAW |  | PA owns prompt packet construction only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 10 | 19 | GLOBAL NO-OVERLAP LAW |  | 04 L2 owns bounded execution and sealing only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 11 | 20 | GLOBAL NO-OVERLAP LAW |  | 05 Exit owns current-run checkout aggregation and exactly one X3 disposition only. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 12 | 21 | GLOBAL NO-OVERLAP LAW |  | 06 L6 owns completed-run evaluation, RCA, and future-run learning proposals only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 13 | 22 | GLOBAL NO-OVERLAP LAW |  | 99 owns proof harnesses only; it does not own runtime behavior. | **PASS** | doctrine_xref, source_file, test_corpus |
| 14 | 25 | REFERENCE POINTERS |  | Cross-cutting governance/certification evidence: 00A_L5_Governance_Safety/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 15 | 26 | REFERENCE POINTERS |  | Durable state and Universal Write Gateway: 00B_L4_State_Archive_and_UWG/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 16 | 27 | REFERENCE POINTERS |  | Current-run reusable gate mesh: 00C_Runtime_Gates_Current_Run_Mesh/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 17 | 28 | REFERENCE POINTERS |  | Traceability and zero-loss proof: 00X_Requirements_Traceability_and_No_Loss_Map.md | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 18 | 29 | REFERENCE POINTERS |  | End-to-end runtime proof harness: 99_End_to_End_Runtime_Proof_and_Acceptance/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 19 | 45 | UNIQUE OWNERSHIP SURFACE |  | PromptBOM resolution only | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 20 | 48 | THIS FILE OWNS |  | PromptBOM, component resolver receipts, selected component refs, system/fence/instruction/exemplar/context/schema/execution metadata inventory | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 21 | 51 | THIS FILE DOES NOT OWN |  | slot ordering, airlock/security sanitization, token budgeting, provider rendering, final artifact signing, execution | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 22 | 54 | GLOBAL NO-OVERLAP LOCK |  | L1 owns intent interpretation, task_spec, query_spec, ambiguity register, and planning recommendations. | **PASS** | doctrine_xref, source_file, test_corpus |
| 23 | 55 | GLOBAL NO-OVERLAP LOCK |  | L0 owns route selection, RouteContract, execution_form, provider lane, route risk, and route authority. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 24 | 56 | GLOBAL NO-OVERLAP LOCK |  | C0 owns retrieval, hydration, graph expansion, evidence shaping, verification, support scoring, and FinalEvidenceContract. | **PASS** | doctrine_xref, source_file, test_corpus |
| 25 | 57 | GLOBAL NO-OVERLAP LOCK |  | L5 owns policy, authority context, origin trust, egress, replay, audit, HITL re-clearance, and certification evidence. | **PASS** | doctrine_xref, source_file, test_corpus |
| 26 | 58 | GLOBAL NO-OVERLAP LOCK |  | Prompt Assembly owns only bounded prompt-packet composition and signed prompt artifact emission. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 27 | 59 | GLOBAL NO-OVERLAP LOCK |  | L2 owns bounded execution, SovereignLLMGateway dispatch, provider/model/tool calls, and sealed work artifacts. | **PASS** | doctrine_xref, source_file, test_corpus |
| 28 | 60 | GLOBAL NO-OVERLAP LOCK |  | Runtime Gates and Exit Eval own current-run dispositions. | **PASS** | doctrine_xref, source_file, test_corpus |
| 29 | 61 | GLOBAL NO-OVERLAP LOCK |  | UWG/L4 owns durable write admission and system-of-record mutation. | **PASS** | doctrine_xref, source_file, test_corpus |
| 30 | 62 | GLOBAL NO-OVERLAP LOCK |  | L6 owns completed-run evaluation, root-cause analysis, promotion proposals, and future-run learning. | **PASS** | doctrine_xref, source_file, test_corpus |
| 31 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ALLOW | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 32 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | DENY | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 33 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | CLARIFY | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 34 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ABSTAIN | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 35 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | REROUTE | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 36 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | SHRINK_SCOPE | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 37 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | RETRY | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 38 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | HEAL | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 39 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ESCALATE_HITL | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 40 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | QUARANTINE | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 41 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | REDACT | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 42 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | SAFE_FALLBACK | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 43 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | MARK_DEGRADED | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 44 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | COMMIT_REQUEST | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 45 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | BLOCK_COMMIT | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 46 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ALLOW_FINISH | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 47 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | approve_execution | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 48 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | approve_output | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 49 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | approve_write | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 50 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | call_provider | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 51 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | execute_tool | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 52 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | mutate_l4 | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 53 | 70 | ALLOWED OUTPUT STYLE |  | receipts, manifests, hashes, validation statuses, assembly statuses, gap reports, artifact refs, replay/audit refs | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 54 | 76 | END OVERWRITE RECONCILIATION HEADER | PARENT | Prompt_Assembly.md | **PASS** | doctrine_xref, source_file, test_corpus |
| 55 | 79 | END OVERWRITE RECONCILIATION HEADER | ROLE | Detailed child file for PA.1 LOAD / RESOLVE PROMPT BOM. | **PASS** | doctrine_xref, source_file, test_corpus |
| 56 | 80 | END OVERWRITE RECONCILIATION HEADER | ROLE | Defines the implementation-grade requirements for its unique Prompt Assembly surface. | **PASS** | doctrine_xref, source_file, test_corpus |
| 57 | 81 | END OVERWRITE RECONCILIATION HEADER | ROLE | Emits Prompt Assembly evidence only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 58 | 82 | END OVERWRITE RECONCILIATION HEADER | ROLE | Does not emit runtime dispositions. | **PASS** | doctrine_xref, source_file, test_corpus |
| 59 | 83 | END OVERWRITE RECONCILIATION HEADER | ROLE | Does not retrieve, route, execute, call providers, write durable state, or promote learning. | **PASS** | doctrine_xref, source_file, test_corpus |
| 60 | 87 | WHY THIS FILE EXISTS |  | Prompt Assembly is a high-risk boundary because it binds rules, evidence, task text, schema, tools, provider metadata, | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 61 | 89 | WHY THIS FILE EXISTS |  | This child isolates one Prompt Assembly surface so the parent stays doctrinal and no other layer inherits prompt assembly | **PASS** | doctrine_xref, source_file, test_corpus |
| 62 | 91 | WHY THIS FILE EXISTS |  | This child is intentionally detailed enough for implementation, tests, traces, and replay evidence. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 63 | 95 | PRIMARY QUESTION |  | "PromptBOM resolution only?" | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 64 | 99 | SOURCE OWNERSHIP BOUNDARY |  | This file may emit assembly receipts, manifests, hashes, statuses, and gap reports for its unique surface. | **PASS** | doctrine_xref, source_file, test_corpus |
| 65 | 100 | SOURCE OWNERSHIP BOUNDARY |  | This file must not fetch missing data. | **PASS** | doctrine_xref, source_file, test_corpus |
| 66 | 101 | SOURCE OWNERSHIP BOUNDARY |  | This file must not modify RouteContract, PlanContract, FinalEvidenceContract, policy, registry, capability, sandbox, or L4 state. | **PASS** | doctrine_xref, source_file, test_corpus |
| 67 | 102 | SOURCE OWNERSHIP BOUNDARY |  | This file must not approve L2 execution. It only prepares evidence for L2 validation. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 68 | 104 | SOURCE OWNERSHIP BOUNDARY | PromptBOM Schema | 1. PromptBOM Schema | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 69 | 107 | SOURCE OWNERSHIP BOUNDARY | FIELDS | prompt_bom_id | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 70 | 108 | SOURCE OWNERSHIP BOUNDARY | FIELDS | assembly_request_id | **PASS** | doctrine_xref, prose_keyword |
| 71 | 109 | SOURCE OWNERSHIP BOUNDARY | FIELDS | request_id / run_id / trace_id / route_id / plan_id | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 72 | 110 | SOURCE OWNERSHIP BOUNDARY | FIELDS | system_component_ref | **PASS** | doctrine_xref, prose_keyword |
| 73 | 111 | SOURCE OWNERSHIP BOUNDARY | FIELDS | system_version_hash | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 74 | 112 | SOURCE OWNERSHIP BOUNDARY | FIELDS | fence_component_refs[] | **PASS** | doctrine_xref, prose_keyword |
| 75 | 113 | SOURCE OWNERSHIP BOUNDARY | FIELDS | policy_posture_ref | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 76 | 114 | SOURCE OWNERSHIP BOUNDARY | FIELDS | instruction_mixin_refs[] | **PASS** | doctrine_xref, prose_keyword |
| 77 | 115 | SOURCE OWNERSHIP BOUNDARY | FIELDS | AgentSpec_ref | **PASS** | doctrine_xref, prose_keyword, source_file |
| 78 | 116 | SOURCE OWNERSHIP BOUNDARY | FIELDS | exemplar_refs[] | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 79 | 117 | SOURCE OWNERSHIP BOUNDARY | FIELDS | exemplar_selection_reason[] | **PASS** | doctrine_xref, prose_keyword |
| 80 | 118 | SOURCE OWNERSHIP BOUNDARY | FIELDS | C0FinalEvidenceContract_ref | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 81 | 119 | SOURCE OWNERSHIP BOUNDARY | FIELDS | context_component_refs[] | **PASS** | doctrine_xref, prose_keyword |
| 82 | 120 | SOURCE OWNERSHIP BOUNDARY | FIELDS | response_schema_contract_ref | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 83 | 121 | SOURCE OWNERSHIP BOUNDARY | FIELDS | tool_schema_refs[] | **PASS** | doctrine_xref, prose_keyword, source_file |
| 84 | 122 | SOURCE OWNERSHIP BOUNDARY | FIELDS | execution_metadata_ref | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 85 | 123 | SOURCE OWNERSHIP BOUNDARY | FIELDS | provider_target_ref | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 86 | 124 | SOURCE OWNERSHIP BOUNDARY | FIELDS | model_settings_ref | **PASS** | doctrine_xref, prose_keyword |
| 87 | 125 | SOURCE OWNERSHIP BOUNDARY | FIELDS | replay_key | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 88 | 126 | SOURCE OWNERSHIP BOUNDARY | FIELDS | policy_hash | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 89 | 127 | SOURCE OWNERSHIP BOUNDARY | FIELDS | blueprint_hash | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 90 | 128 | SOURCE OWNERSHIP BOUNDARY | FIELDS | component_hashes{} | **PASS** | doctrine_xref, prose_keyword |
| 91 | 129 | SOURCE OWNERSHIP BOUNDARY | FIELDS | bom_hash | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 92 | 130 | SOURCE OWNERSHIP BOUNDARY | FIELDS | bom_gap_report_ref | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 93 | 133 | MUST CHECK |  | every selected component has a stable ref. | **PASS** | doctrine_xref, source_file, test_corpus |
| 94 | 134 | MUST CHECK |  | every selected component has a hash or immutable version. | **PASS** | doctrine_xref, source_file, test_corpus |
| 95 | 135 | MUST CHECK |  | system component matches system_version_hash. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 96 | 136 | MUST CHECK |  | fences match policy posture and route risk. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 97 | 137 | MUST CHECK |  | instructions match AgentSpec and task class. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 98 | 138 | MUST CHECK |  | exemplars are allowed for task class and budget posture. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 99 | 139 | MUST CHECK |  | C0 context ref matches route grounding requirement. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 100 | 140 | MUST CHECK |  | R0 schema ref exists when structured output is required. | **PASS** | doctrine_xref, source_file, test_corpus |
| 101 | 141 | MUST CHECK |  | tool schema refs match allowed tool posture. | **PASS** | doctrine_xref, source_file, test_corpus |
| 102 | 142 | MUST CHECK |  | execution metadata carries replay_key and policy_hash. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 103 | 143 | MUST CHECK | Resolution Steps | 2. Resolution Steps | **PASS** | doctrine_xref, source_file, test_corpus |
| 104 | 146 | MUST CHECK | Resolution Steps | Select by system_version_hash. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 105 | 147 | MUST CHECK | Resolution Steps | Load constitution, identity floor, and safety invariants as references. | **PASS** | doctrine_xref, prose_keyword, runtime_symbol, source_file, test_corpus |
| 106 | 148 | MUST CHECK | Resolution Steps | Emit system_component_receipt. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 107 | 151 | MUST CHECK | Resolution Steps | Select by policy posture, route risk, task class, tenant/region/data class, and tool posture. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 108 | 152 | MUST CHECK | Resolution Steps | Bind injection fences, role boundaries, scope limits, and anti-injection controls. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 109 | 155 | MUST CHECK | Resolution Steps | Select by AgentSpec, task type, artifact type, and route execution form. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 110 | 156 | MUST CHECK | Resolution Steps | Bind capability instructions and operating manuals. | **PASS** | doctrine_xref, source_file, test_corpus |
| 111 | 159 | MUST CHECK | Resolution Steps | Select only approved examples compatible with task class, schema, policy, and token budget. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 112 | 160 | MUST CHECK | Resolution Steps | If examples are unsafe or unneeded, omit with reason, not silent drop. | **PASS** | doctrine_xref, source_file, test_corpus |
| 113 | 163 | MUST CHECK | Resolution Steps | Consume C0 FinalEvidenceContract only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 114 | 164 | MUST CHECK | Resolution Steps | Map verified chunks, citations, source limits, contradiction flags, and gap metadata into context refs. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 115 | 167 | MUST CHECK | Resolution Steps | Select from AgentSpec / task contract / route output target. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 116 | 168 | MUST CHECK | Resolution Steps | Preserve provider-native schema binding intent. | **PASS** | doctrine_xref, source_file, test_corpus |
| 117 | 171 | MUST CHECK | Resolution Steps | Bind replay_key, policy_hash, plan_id, idempotency nonce, model_id, temperature, thinking_level, provider lane. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 118 | 172 | MUST CHECK | BOM Gaps | 3. BOM Gaps | **PASS** | doctrine_xref, source_file, test_corpus |
| 119 | 175 | GAP TYPES |  | missing_system_component | **PASS** | doctrine_xref, prose_keyword |
| 120 | 176 | GAP TYPES |  | missing_fence_component | **PASS** | doctrine_xref, prose_keyword |
| 121 | 177 | GAP TYPES |  | missing_instruction_mixin | **PASS** | doctrine_xref, prose_keyword |
| 122 | 178 | GAP TYPES |  | exemplar_conflict | **PASS** | doctrine_xref, prose_keyword |
| 123 | 179 | GAP TYPES |  | c0_context_missing_for_grounded_route | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 124 | 180 | GAP TYPES |  | response_schema_missing | **PASS** | doctrine_xref, prose_keyword |
| 125 | 181 | GAP TYPES |  | tool_schema_missing | **PASS** | doctrine_xref, prose_keyword |
| 126 | 182 | GAP TYPES |  | execution_metadata_missing | **PASS** | doctrine_xref, prose_keyword |
| 127 | 183 | GAP TYPES |  | policy_hash_mismatch | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 128 | 184 | GAP TYPES |  | stale_component_ref | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 129 | 185 | GAP TYPES |  | unsupported_provider_target | **PASS** | doctrine_xref, prose_keyword |
| 130 | 190 | STATUS VALUES |  | PA_BOM_RESOLVED | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 131 | 191 | STATUS VALUES |  | PA_BOM_GAP | **PASS** | doctrine_xref, prose_keyword, source_file, status_value, test_corpus |
| 132 | 192 | STATUS VALUES |  | PA_REQUIRES_UPSTREAM_REPAIR | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 133 | 196 | MUST EMIT |  | PromptBOM | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 134 | 197 | MUST EMIT |  | bom_resolution_receipt | **PASS** | doctrine_xref, receipt_key, source_file |
| 135 | 198 | MUST EMIT |  | component_inventory | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 136 | 199 | MUST EMIT |  | component_hash_map | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 137 | 200 | MUST EMIT |  | bom_gap_report | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 138 | 201 | MUST EMIT |  | bom_hash_receipt | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 139 | 205 | MUST NOT |  | retrieve evidence | **PASS** | doctrine_xref, source_file, test_corpus |
| 140 | 206 | MUST NOT |  | route or reroute | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 141 | 207 | MUST NOT |  | call a model provider | **PASS** | doctrine_xref, source_file, test_corpus |
| 142 | 208 | MUST NOT |  | execute a tool | **PASS** | doctrine_xref, source_file, test_corpus |
| 143 | 209 | MUST NOT |  | approve the final answer | **PASS** | doctrine_xref, source_file, test_corpus |
| 144 | 210 | MUST NOT |  | commit durable state | **PASS** | doctrine_xref, source_file, test_corpus |
| 145 | 211 | MUST NOT |  | emit runtime dispositions | **PASS** | doctrine_xref, source_file, test_corpus |
| 146 | 212 | MUST NOT |  | silently drop mandatory evidence, authority, schema, or replay metadata | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 147 | 216 | ACCEPTANCE TESTS |  | No code path in this child retrieves evidence, routes, executes, calls providers, writes L4, or emits runtime disposition. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 148 | 217 | ACCEPTANCE TESTS |  | All emitted receipts preserve request_id, run_id, trace_id, route_id, policy_hash, and replay_key when available. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 149 | 218 | ACCEPTANCE TESTS |  | All gap conditions are explicit and replayable. | **PASS** | doctrine_xref, source_file, test_corpus |
| 150 | 219 | ACCEPTANCE TESTS |  | Same PAAssemblyInput resolves same PromptBOM and bom_hash. | **PASS** | doctrine_xref, prose_keyword, receipt_key, runtime_symbol, source_file, test_corpus |
| 151 | 220 | ACCEPTANCE TESTS |  | Grounded route without C0 contract produces bom_gap_report. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 152 | 221 | ACCEPTANCE TESTS |  | Exemplar conflicting with R0 schema is excluded with reason. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |

## PA.2

| # | Line | Section | Sub-section | Requirement | Status | Evidence |
|---:|---:|---|---|---|:---:|---|
| 1 | 10 | GLOBAL NO-OVERLAP LAW |  | 00A L5 owns governance certification evidence, not live runtime dispositions and not durable write admission. | **PASS** | doctrine_xref, source_file, test_corpus |
| 2 | 11 | GLOBAL NO-OVERLAP LAW |  | 00B L4/UWG owns durable system-of-record state and durable write admission, not planning, routing, retrieval, execution, Exit disposition, or L6 learning mechanics. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 3 | 12 | GLOBAL NO-OVERLAP LAW |  | 00C Runtime Gates owns G01-G29 current-run GateVerdict law, not final Exit X3 aggregation and not L5 certification evidence. | **PASS** | doctrine_xref, source_file, test_corpus |
| 4 | 13 | GLOBAL NO-OVERLAP LAW |  | 00X owns traceability and no-loss mapping only. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 5 | 14 | GLOBAL NO-OVERLAP LAW |  | 01 Intake owns request envelope validation and identity/session/tenant baseline only. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 6 | 15 | GLOBAL NO-OVERLAP LAW |  | 02 L1 owns advisory interpretation and planning only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 7 | 16 | GLOBAL NO-OVERLAP LAW |  | 03 L0/L3 owns deterministic route selection and optional workflow orchestration only. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 8 | 17 | GLOBAL NO-OVERLAP LAW |  | C0 owns retrieval/evidence contracts only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 9 | 18 | GLOBAL NO-OVERLAP LAW |  | PA owns prompt packet construction only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 10 | 19 | GLOBAL NO-OVERLAP LAW |  | 04 L2 owns bounded execution and sealing only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 11 | 20 | GLOBAL NO-OVERLAP LAW |  | 05 Exit owns current-run checkout aggregation and exactly one X3 disposition only. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 12 | 21 | GLOBAL NO-OVERLAP LAW |  | 06 L6 owns completed-run evaluation, RCA, and future-run learning proposals only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 13 | 22 | GLOBAL NO-OVERLAP LAW |  | 99 owns proof harnesses only; it does not own runtime behavior. | **PASS** | doctrine_xref, source_file, test_corpus |
| 14 | 25 | REFERENCE POINTERS |  | Cross-cutting governance/certification evidence: 00A_L5_Governance_Safety/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 15 | 26 | REFERENCE POINTERS |  | Durable state and Universal Write Gateway: 00B_L4_State_Archive_and_UWG/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 16 | 27 | REFERENCE POINTERS |  | Current-run reusable gate mesh: 00C_Runtime_Gates_Current_Run_Mesh/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 17 | 28 | REFERENCE POINTERS |  | Traceability and zero-loss proof: 00X_Requirements_Traceability_and_No_Loss_Map.md | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 18 | 29 | REFERENCE POINTERS |  | End-to-end runtime proof harness: 99_End_to_End_Runtime_Proof_and_Acceptance/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 19 | 45 | UNIQUE OWNERSHIP SURFACE |  | canonical authority-tiered slot construction only | **PASS** | doctrine_xref, source_file, test_corpus |
| 20 | 48 | THIS FILE OWNS |  | StructuredPromptSlots, canonical slot order, slot authority map, slot lineage map, slot conflict map | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 21 | 51 | THIS FILE DOES NOT OWN |  | BOM resolution, security pass, validation, token budgeting, provider rendering, final signing, execution | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 22 | 54 | GLOBAL NO-OVERLAP LOCK |  | L1 owns intent interpretation, task_spec, query_spec, ambiguity register, and planning recommendations. | **PASS** | doctrine_xref, source_file, test_corpus |
| 23 | 55 | GLOBAL NO-OVERLAP LOCK |  | L0 owns route selection, RouteContract, execution_form, provider lane, route risk, and route authority. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 24 | 56 | GLOBAL NO-OVERLAP LOCK |  | C0 owns retrieval, hydration, graph expansion, evidence shaping, verification, support scoring, and FinalEvidenceContract. | **PASS** | doctrine_xref, source_file, test_corpus |
| 25 | 57 | GLOBAL NO-OVERLAP LOCK |  | L5 owns policy, authority context, origin trust, egress, replay, audit, HITL re-clearance, and certification evidence. | **PASS** | doctrine_xref, source_file, test_corpus |
| 26 | 58 | GLOBAL NO-OVERLAP LOCK |  | Prompt Assembly owns only bounded prompt-packet composition and signed prompt artifact emission. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 27 | 59 | GLOBAL NO-OVERLAP LOCK |  | L2 owns bounded execution, SovereignLLMGateway dispatch, provider/model/tool calls, and sealed work artifacts. | **PASS** | doctrine_xref, source_file, test_corpus |
| 28 | 60 | GLOBAL NO-OVERLAP LOCK |  | Runtime Gates and Exit Eval own current-run dispositions. | **PASS** | doctrine_xref, source_file, test_corpus |
| 29 | 61 | GLOBAL NO-OVERLAP LOCK |  | UWG/L4 owns durable write admission and system-of-record mutation. | **PASS** | doctrine_xref, source_file, test_corpus |
| 30 | 62 | GLOBAL NO-OVERLAP LOCK |  | L6 owns completed-run evaluation, root-cause analysis, promotion proposals, and future-run learning. | **PASS** | doctrine_xref, source_file, test_corpus |
| 31 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ALLOW | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 32 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | DENY | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 33 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | CLARIFY | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 34 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ABSTAIN | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 35 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | REROUTE | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 36 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | SHRINK_SCOPE | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 37 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | RETRY | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 38 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | HEAL | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 39 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ESCALATE_HITL | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 40 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | QUARANTINE | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 41 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | REDACT | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 42 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | SAFE_FALLBACK | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 43 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | MARK_DEGRADED | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 44 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | COMMIT_REQUEST | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 45 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | BLOCK_COMMIT | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 46 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ALLOW_FINISH | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 47 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | approve_execution | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 48 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | approve_output | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 49 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | approve_write | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 50 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | call_provider | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 51 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | execute_tool | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 52 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | mutate_l4 | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 53 | 70 | ALLOWED OUTPUT STYLE |  | receipts, manifests, hashes, validation statuses, assembly statuses, gap reports, artifact refs, replay/audit refs | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 54 | 76 | END OVERWRITE RECONCILIATION HEADER | PARENT | Prompt_Assembly.md | **PASS** | doctrine_xref, source_file, test_corpus |
| 55 | 79 | END OVERWRITE RECONCILIATION HEADER | ROLE | Detailed child file for PA.2 SLOT COMPOSITION. | **PASS** | doctrine_xref, source_file, test_corpus |
| 56 | 80 | END OVERWRITE RECONCILIATION HEADER | ROLE | Defines the implementation-grade requirements for its unique Prompt Assembly surface. | **PASS** | doctrine_xref, source_file, test_corpus |
| 57 | 81 | END OVERWRITE RECONCILIATION HEADER | ROLE | Emits Prompt Assembly evidence only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 58 | 82 | END OVERWRITE RECONCILIATION HEADER | ROLE | Does not emit runtime dispositions. | **PASS** | doctrine_xref, source_file, test_corpus |
| 59 | 83 | END OVERWRITE RECONCILIATION HEADER | ROLE | Does not retrieve, route, execute, call providers, write durable state, or promote learning. | **PASS** | doctrine_xref, source_file, test_corpus |
| 60 | 87 | WHY THIS FILE EXISTS |  | Prompt Assembly is a high-risk boundary because it binds rules, evidence, task text, schema, tools, provider metadata, | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 61 | 89 | WHY THIS FILE EXISTS |  | This child isolates one Prompt Assembly surface so the parent stays doctrinal and no other layer inherits prompt assembly | **PASS** | doctrine_xref, source_file, test_corpus |
| 62 | 91 | WHY THIS FILE EXISTS |  | This child is intentionally detailed enough for implementation, tests, traces, and replay evidence. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 63 | 95 | PRIMARY QUESTION |  | "canonical authority-tiered slot construction only?" | **PASS** | doctrine_xref, source_file, test_corpus |
| 64 | 99 | SOURCE OWNERSHIP BOUNDARY |  | This file may emit assembly receipts, manifests, hashes, statuses, and gap reports for its unique surface. | **PASS** | doctrine_xref, source_file, test_corpus |
| 65 | 100 | SOURCE OWNERSHIP BOUNDARY |  | This file must not fetch missing data. | **PASS** | doctrine_xref, source_file, test_corpus |
| 66 | 101 | SOURCE OWNERSHIP BOUNDARY |  | This file must not modify RouteContract, PlanContract, FinalEvidenceContract, policy, registry, capability, sandbox, or L4 state. | **PASS** | doctrine_xref, source_file, test_corpus |
| 67 | 102 | SOURCE OWNERSHIP BOUNDARY |  | This file must not approve L2 execution. It only prepares evidence for L2 validation. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 68 | 104 | SOURCE OWNERSHIP BOUNDARY | StructuredPromptSlots | 1. StructuredPromptSlots | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 69 | 107 | SOURCE OWNERSHIP BOUNDARY | FIELDS | structured_slots_id | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 70 | 108 | SOURCE OWNERSHIP BOUNDARY | FIELDS | prompt_bom_id | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 71 | 109 | SOURCE OWNERSHIP BOUNDARY | FIELDS | slot_order[] | **PASS** | doctrine_xref, prose_keyword, runtime_symbol, source_file, test_corpus |
| 72 | 110 | SOURCE OWNERSHIP BOUNDARY | FIELDS | S0_slot | **PASS** | doctrine_xref, receipt_key, runtime_symbol, source_file, test_corpus |
| 73 | 111 | SOURCE OWNERSHIP BOUNDARY | FIELDS | D0_slot | **PASS** | doctrine_xref, receipt_key, runtime_symbol, source_file, test_corpus |
| 74 | 112 | SOURCE OWNERSHIP BOUNDARY | FIELDS | I0_slot | **PASS** | doctrine_xref, receipt_key, runtime_symbol, source_file, test_corpus |
| 75 | 113 | SOURCE OWNERSHIP BOUNDARY | FIELDS | E0_slot | **PASS** | doctrine_xref, receipt_key, runtime_symbol, source_file, test_corpus |
| 76 | 114 | SOURCE OWNERSHIP BOUNDARY | FIELDS | C0_slot | **PASS** | doctrine_xref, receipt_key, runtime_symbol, source_file, test_corpus |
| 77 | 115 | SOURCE OWNERSHIP BOUNDARY | FIELDS | M0_slot | **PASS** | doctrine_xref, receipt_key, runtime_symbol, source_file, test_corpus |
| 78 | 116 | SOURCE OWNERSHIP BOUNDARY | FIELDS | U0_slot | **PASS** | doctrine_xref, receipt_key, runtime_symbol, source_file, test_corpus |
| 79 | 117 | SOURCE OWNERSHIP BOUNDARY | FIELDS | Y0_slot optional | **PASS** | doctrine_xref, prose_keyword, receipt_key, runtime_symbol, source_file, test_corpus |
| 80 | 118 | SOURCE OWNERSHIP BOUNDARY | FIELDS | H0_slot optional | **PASS** | doctrine_xref, prose_keyword, receipt_key, runtime_symbol, source_file, test_corpus |
| 81 | 119 | SOURCE OWNERSHIP BOUNDARY | FIELDS | R0_binding | **PASS** | doctrine_xref, receipt_key, runtime_symbol, source_file, test_corpus |
| 82 | 120 | SOURCE OWNERSHIP BOUNDARY | FIELDS | tool_bindings[] | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 83 | 121 | SOURCE OWNERSHIP BOUNDARY | FIELDS | slot_authority_map | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 84 | 122 | SOURCE OWNERSHIP BOUNDARY | FIELDS | slot_origin_map | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 85 | 123 | SOURCE OWNERSHIP BOUNDARY | FIELDS | slot_lineage_map | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 86 | 124 | SOURCE OWNERSHIP BOUNDARY | FIELDS | slot_hashes{} | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 87 | 125 | SOURCE OWNERSHIP BOUNDARY | FIELDS | slot_conflict_map | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 88 | 126 | SOURCE OWNERSHIP BOUNDARY | FIELDS | slot_omission_reasons{} | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 89 | 127 | SOURCE OWNERSHIP BOUNDARY | FIELDS | structured_slots_hash | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 90 | 132 | REQUIRED ORDER | Slot Payload Requirements | 2. Slot Payload Requirements | **PASS** | doctrine_xref, source_file, test_corpus |
| 91 | 135 | REQUIRED ORDER | S0 | system identity and invariant refs, system_version_hash, immutable authority label. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 92 | 138 | REQUIRED ORDER | D0 | role fences, scope limits, anti-injection controls, allowed/disallowed posture refs. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 93 | 141 | REQUIRED ORDER | I0 | task operating instructions, AgentSpec capability refs, procedure constraints. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 94 | 144 | REQUIRED ORDER | E0 | approved examples, style/format guidance, exemplar origin refs, conflict screening refs. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 95 | 147 | REQUIRED ORDER | C0 | verified evidence, citations, source lineage, support limits, contradictions, gaps, abstain recommendation metadata if present. | **PASS** | doctrine_xref, forbidden_token, prose_keyword, receipt_key, source_file, test_corpus |
| 96 | 150 | REQUIRED ORDER | M0 | private provider-safe control hints, reasoning discipline metadata, no chain-of-thought disclosure instructions. | **PASS** | doctrine_xref, source_file, test_corpus |
| 97 | 153 | REQUIRED ORDER | U0 | neutralized task intent candidate, user constraints, requested output, no policy authority. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 98 | 156 | REQUIRED ORDER | Y0 | approved prior patterns only if current policy permits, with promotion receipt refs. | **PASS** | doctrine_xref, source_file, test_corpus |
| 99 | 159 | REQUIRED ORDER | H0 | bounded repair hint only, same policy_hash / blueprint_hash requirement for same-run repair. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 100 | 162 | REQUIRED ORDER | R0 | schema binding object, provider-native response_schema / response_format target, not freeform prose where structured output exists. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 101 | 163 | REQUIRED ORDER | Authority Composition Rules | 3. Authority Composition Rules | **PASS** | doctrine_xref, source_file, test_corpus |
| 102 | 166 | MUST CHECK |  | no lower-authority slot modifies higher-authority slot fields. | **PASS** | doctrine_xref, source_file, test_corpus |
| 103 | 167 | MUST CHECK |  | no C0 text becomes instruction. | **PASS** | doctrine_xref, source_file, test_corpus |
| 104 | 168 | MUST CHECK |  | no U0 text becomes policy. | **PASS** | doctrine_xref, source_file, test_corpus |
| 105 | 169 | MUST CHECK |  | no E0 exemplar overrides schema or safety posture. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 106 | 170 | MUST CHECK |  | no H0 hint changes route, provider, tool, scope, policy, or blueprint. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 107 | 171 | MUST CHECK |  | no Y0 prior appears without promotion/evidence refs. | **PASS** | doctrine_xref, source_file, test_corpus |
| 108 | 172 | MUST CHECK |  | R0 schema is not contradicted by examples or task prose. | **PASS** | doctrine_xref, source_file, test_corpus |
| 109 | 173 | MUST CHECK |  | tool binding is not redefined by user or retrieved text. | **PASS** | doctrine_xref, source_file, test_corpus |
| 110 | 176 | SLOT CONFLICT TYPES |  | lower_authority_override_attempt | **PASS** | doctrine_xref, prose_keyword |
| 111 | 177 | SLOT CONFLICT TYPES |  | c0_instruction_like_payload | **PASS** | doctrine_xref, runtime_symbol, source_file |
| 112 | 178 | SLOT CONFLICT TYPES |  | u0_policy_override_attempt | **PASS** | doctrine_xref, prose_keyword |
| 113 | 179 | SLOT CONFLICT TYPES |  | exemplar_schema_conflict | **PASS** | doctrine_xref, prose_keyword |
| 114 | 180 | SLOT CONFLICT TYPES |  | h0_scope_widening_attempt | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 115 | 181 | SLOT CONFLICT TYPES |  | y0_missing_promotion_receipt | **PASS** | doctrine_xref, prose_keyword |
| 116 | 182 | SLOT CONFLICT TYPES |  | r0_schema_conflict | **PASS** | doctrine_xref, prose_keyword |
| 117 | 183 | SLOT CONFLICT TYPES |  | tool_binding_conflict | **PASS** | doctrine_xref, prose_keyword |
| 118 | 184 | SLOT CONFLICT TYPES |  | slot_order_violation | **PASS** | doctrine_xref, prose_keyword, runtime_symbol, source_file, test_corpus |
| 119 | 185 | SLOT CONFLICT TYPES |  | missing_origin_label | **PASS** | doctrine_xref, prose_keyword |
| 120 | 190 | STATUS VALUES |  | PA_SLOTS_COMPOSED | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 121 | 191 | STATUS VALUES |  | PA_SLOT_COMPOSITION_GAP | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 122 | 192 | STATUS VALUES |  | PA_AUTHORITY_CONFLICT | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 123 | 196 | MUST EMIT |  | StructuredPromptSlots | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 124 | 197 | MUST EMIT |  | slot_composition_receipt | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 125 | 198 | MUST EMIT |  | slot_authority_map | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 126 | 199 | MUST EMIT |  | slot_lineage_map | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 127 | 200 | MUST EMIT |  | slot_conflict_map | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 128 | 201 | MUST EMIT |  | structured_slots_hash_receipt | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 129 | 205 | MUST NOT |  | retrieve evidence | **PASS** | doctrine_xref, source_file, test_corpus |
| 130 | 206 | MUST NOT |  | route or reroute | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 131 | 207 | MUST NOT |  | call a model provider | **PASS** | doctrine_xref, source_file, test_corpus |
| 132 | 208 | MUST NOT |  | execute a tool | **PASS** | doctrine_xref, source_file, test_corpus |
| 133 | 209 | MUST NOT |  | approve the final answer | **PASS** | doctrine_xref, source_file, test_corpus |
| 134 | 210 | MUST NOT |  | commit durable state | **PASS** | doctrine_xref, source_file, test_corpus |
| 135 | 211 | MUST NOT |  | emit runtime dispositions | **PASS** | doctrine_xref, source_file, test_corpus |
| 136 | 212 | MUST NOT |  | silently drop mandatory evidence, authority, schema, or replay metadata | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 137 | 216 | ACCEPTANCE TESTS |  | No code path in this child retrieves evidence, routes, executes, calls providers, writes L4, or emits runtime disposition. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 138 | 217 | ACCEPTANCE TESTS |  | All emitted receipts preserve request_id, run_id, trace_id, route_id, policy_hash, and replay_key when available. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 139 | 218 | ACCEPTANCE TESTS |  | All gap conditions are explicit and replayable. | **PASS** | doctrine_xref, source_file, test_corpus |
| 140 | 219 | ACCEPTANCE TESTS |  | User text saying ignore system remains in U0 and cannot alter S0/D0/I0. | **PASS** | doctrine_xref, source_file, test_corpus |
| 141 | 220 | ACCEPTANCE TESTS |  | Retrieved chunk containing instructions remains C0 data and is flagged for PA.3 security handling. | **PASS** | doctrine_xref, source_file, test_corpus |
| 142 | 221 | ACCEPTANCE TESTS |  | Same BOM produces same structured_slots_hash. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |

## PA.3

| # | Line | Section | Sub-section | Requirement | Status | Evidence |
|---:|---:|---|---|---|:---:|---|
| 1 | 10 | GLOBAL NO-OVERLAP LAW |  | 00A L5 owns governance certification evidence, not live runtime dispositions and not durable write admission. | **PASS** | doctrine_xref, source_file, test_corpus |
| 2 | 11 | GLOBAL NO-OVERLAP LAW |  | 00B L4/UWG owns durable system-of-record state and durable write admission, not planning, routing, retrieval, execution, Exit disposition, or L6 learning mechanics. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 3 | 12 | GLOBAL NO-OVERLAP LAW |  | 00C Runtime Gates owns G01-G29 current-run GateVerdict law, not final Exit X3 aggregation and not L5 certification evidence. | **PASS** | doctrine_xref, source_file, test_corpus |
| 4 | 13 | GLOBAL NO-OVERLAP LAW |  | 00X owns traceability and no-loss mapping only. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 5 | 14 | GLOBAL NO-OVERLAP LAW |  | 01 Intake owns request envelope validation and identity/session/tenant baseline only. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 6 | 15 | GLOBAL NO-OVERLAP LAW |  | 02 L1 owns advisory interpretation and planning only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 7 | 16 | GLOBAL NO-OVERLAP LAW |  | 03 L0/L3 owns deterministic route selection and optional workflow orchestration only. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 8 | 17 | GLOBAL NO-OVERLAP LAW |  | C0 owns retrieval/evidence contracts only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 9 | 18 | GLOBAL NO-OVERLAP LAW |  | PA owns prompt packet construction only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 10 | 19 | GLOBAL NO-OVERLAP LAW |  | 04 L2 owns bounded execution and sealing only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 11 | 20 | GLOBAL NO-OVERLAP LAW |  | 05 Exit owns current-run checkout aggregation and exactly one X3 disposition only. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 12 | 21 | GLOBAL NO-OVERLAP LAW |  | 06 L6 owns completed-run evaluation, RCA, and future-run learning proposals only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 13 | 22 | GLOBAL NO-OVERLAP LAW |  | 99 owns proof harnesses only; it does not own runtime behavior. | **PASS** | doctrine_xref, source_file, test_corpus |
| 14 | 25 | REFERENCE POINTERS |  | Cross-cutting governance/certification evidence: 00A_L5_Governance_Safety/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 15 | 26 | REFERENCE POINTERS |  | Durable state and Universal Write Gateway: 00B_L4_State_Archive_and_UWG/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 16 | 27 | REFERENCE POINTERS |  | Current-run reusable gate mesh: 00C_Runtime_Gates_Current_Run_Mesh/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 17 | 28 | REFERENCE POINTERS |  | Traceability and zero-loss proof: 00X_Requirements_Traceability_and_No_Loss_Map.md | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 18 | 29 | REFERENCE POINTERS |  | End-to-end runtime proof harness: 99_End_to_End_Runtime_Proof_and_Acceptance/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 19 | 45 | UNIQUE OWNERSHIP SURFACE |  | assembly-time airlock and slot payload security pass only | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 20 | 48 | THIS FILE OWNS |  | U0 airlock receipts, C0 payload classifier receipts, H0 re-entry validation receipts, safe slot payload map, rejected payload reports | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 21 | 51 | THIS FILE DOES NOT OWN |  | L5 origin-trust doctrine, C0 retrieval/scoring, Runtime Gate security decisions, L2 execution validation, Exit final safety decision | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 22 | 54 | GLOBAL NO-OVERLAP LOCK |  | L1 owns intent interpretation, task_spec, query_spec, ambiguity register, and planning recommendations. | **PASS** | doctrine_xref, source_file, test_corpus |
| 23 | 55 | GLOBAL NO-OVERLAP LOCK |  | L0 owns route selection, RouteContract, execution_form, provider lane, route risk, and route authority. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 24 | 56 | GLOBAL NO-OVERLAP LOCK |  | C0 owns retrieval, hydration, graph expansion, evidence shaping, verification, support scoring, and FinalEvidenceContract. | **PASS** | doctrine_xref, source_file, test_corpus |
| 25 | 57 | GLOBAL NO-OVERLAP LOCK |  | L5 owns policy, authority context, origin trust, egress, replay, audit, HITL re-clearance, and certification evidence. | **PASS** | doctrine_xref, source_file, test_corpus |
| 26 | 58 | GLOBAL NO-OVERLAP LOCK |  | Prompt Assembly owns only bounded prompt-packet composition and signed prompt artifact emission. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 27 | 59 | GLOBAL NO-OVERLAP LOCK |  | L2 owns bounded execution, SovereignLLMGateway dispatch, provider/model/tool calls, and sealed work artifacts. | **PASS** | doctrine_xref, source_file, test_corpus |
| 28 | 60 | GLOBAL NO-OVERLAP LOCK |  | Runtime Gates and Exit Eval own current-run dispositions. | **PASS** | doctrine_xref, source_file, test_corpus |
| 29 | 61 | GLOBAL NO-OVERLAP LOCK |  | UWG/L4 owns durable write admission and system-of-record mutation. | **PASS** | doctrine_xref, source_file, test_corpus |
| 30 | 62 | GLOBAL NO-OVERLAP LOCK |  | L6 owns completed-run evaluation, root-cause analysis, promotion proposals, and future-run learning. | **PASS** | doctrine_xref, source_file, test_corpus |
| 31 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ALLOW | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 32 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | DENY | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 33 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | CLARIFY | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 34 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ABSTAIN | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 35 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | REROUTE | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 36 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | SHRINK_SCOPE | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 37 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | RETRY | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 38 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | HEAL | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 39 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ESCALATE_HITL | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 40 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | QUARANTINE | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 41 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | REDACT | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 42 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | SAFE_FALLBACK | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 43 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | MARK_DEGRADED | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 44 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | COMMIT_REQUEST | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 45 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | BLOCK_COMMIT | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 46 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ALLOW_FINISH | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 47 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | approve_execution | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 48 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | approve_output | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 49 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | approve_write | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 50 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | call_provider | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 51 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | execute_tool | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 52 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | mutate_l4 | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 53 | 70 | ALLOWED OUTPUT STYLE |  | receipts, manifests, hashes, validation statuses, assembly statuses, gap reports, artifact refs, replay/audit refs | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 54 | 76 | END OVERWRITE RECONCILIATION HEADER | PARENT | Prompt_Assembly.md | **PASS** | doctrine_xref, source_file, test_corpus |
| 55 | 79 | END OVERWRITE RECONCILIATION HEADER | ROLE | Detailed child file for PA.3 AIRLOCK / SECURITY PASS. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 56 | 80 | END OVERWRITE RECONCILIATION HEADER | ROLE | Defines the implementation-grade requirements for its unique Prompt Assembly surface. | **PASS** | doctrine_xref, source_file, test_corpus |
| 57 | 81 | END OVERWRITE RECONCILIATION HEADER | ROLE | Emits Prompt Assembly evidence only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 58 | 82 | END OVERWRITE RECONCILIATION HEADER | ROLE | Does not emit runtime dispositions. | **PASS** | doctrine_xref, source_file, test_corpus |
| 59 | 83 | END OVERWRITE RECONCILIATION HEADER | ROLE | Does not retrieve, route, execute, call providers, write durable state, or promote learning. | **PASS** | doctrine_xref, source_file, test_corpus |
| 60 | 87 | WHY THIS FILE EXISTS |  | Prompt Assembly is a high-risk boundary because it binds rules, evidence, task text, schema, tools, provider metadata, | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 61 | 89 | WHY THIS FILE EXISTS |  | This child isolates one Prompt Assembly surface so the parent stays doctrinal and no other layer inherits prompt assembly | **PASS** | doctrine_xref, source_file, test_corpus |
| 62 | 91 | WHY THIS FILE EXISTS |  | This child is intentionally detailed enough for implementation, tests, traces, and replay evidence. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 63 | 95 | PRIMARY QUESTION |  | "assembly-time airlock and slot payload security pass only?" | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 64 | 99 | SOURCE OWNERSHIP BOUNDARY |  | This file may emit assembly receipts, manifests, hashes, statuses, and gap reports for its unique surface. | **PASS** | doctrine_xref, source_file, test_corpus |
| 65 | 100 | SOURCE OWNERSHIP BOUNDARY |  | This file must not fetch missing data. | **PASS** | doctrine_xref, source_file, test_corpus |
| 66 | 101 | SOURCE OWNERSHIP BOUNDARY |  | This file must not modify RouteContract, PlanContract, FinalEvidenceContract, policy, registry, capability, sandbox, or L4 state. | **PASS** | doctrine_xref, source_file, test_corpus |
| 67 | 102 | SOURCE OWNERSHIP BOUNDARY |  | This file must not approve L2 execution. It only prepares evidence for L2 validation. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 68 | 104 | SOURCE OWNERSHIP BOUNDARY | Security Pass Input | 1. Security Pass Input | **PASS** | doctrine_xref, source_file, test_corpus |
| 69 | 107 | SOURCE OWNERSHIP BOUNDARY | FIELDS | security_pass_id | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 70 | 108 | SOURCE OWNERSHIP BOUNDARY | FIELDS | structured_slots_id | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 71 | 109 | SOURCE OWNERSHIP BOUNDARY | FIELDS | origin_trust_manifest_ref if available | **PASS** | doctrine_xref, source_file, test_corpus |
| 72 | 110 | SOURCE OWNERSHIP BOUNDARY | FIELDS | slot_origin_map | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 73 | 111 | SOURCE OWNERSHIP BOUNDARY | FIELDS | slot_authority_map | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 74 | 112 | SOURCE OWNERSHIP BOUNDARY | FIELDS | slot_payload_hashes | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 75 | 113 | SOURCE OWNERSHIP BOUNDARY | FIELDS | policy_hash | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 76 | 114 | SOURCE OWNERSHIP BOUNDARY | FIELDS | blueprint_hash | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 77 | 115 | SOURCE OWNERSHIP BOUNDARY | FIELDS | route_id | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 78 | 116 | SOURCE OWNERSHIP BOUNDARY | FIELDS | task_class | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 79 | 117 | SOURCE OWNERSHIP BOUNDARY | FIELDS | data_class | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 80 | 118 | SOURCE OWNERSHIP BOUNDARY | FIELDS | provider_lane | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 81 | 119 | SOURCE OWNERSHIP BOUNDARY | FIELDS | security_profile_ref | **PASS** | doctrine_xref, prose_keyword |
| 82 | 122 | MUST CHECK |  | every slot has origin label. | **PASS** | doctrine_xref, source_file, test_corpus |
| 83 | 123 | MUST CHECK |  | every lower-authority content item has data/intent/proposal label. | **PASS** | doctrine_xref, source_file, test_corpus |
| 84 | 124 | MUST CHECK |  | every C0 payload has source lineage and citation/gap labels. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 85 | 125 | MUST CHECK |  | every H0 payload has repair scope and same-run hash refs. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 86 | 126 | MUST CHECK |  | every tool/schema payload is separated from prose content. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 87 | 127 | MUST CHECK |  | no slot contains unreviewed instruction-like text from untrusted content. | **PASS** | doctrine_xref, source_file, test_corpus |
| 88 | 128 | MUST CHECK | U0 Airlock | 2. U0 Airlock | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 89 | 131 | MUST CHECK | PURPOSE | Preserve actual user task while neutralizing illegal control claims. | **PASS** | doctrine_xref, source_file, test_corpus |
| 90 | 134 | MUST CHECK | CHECKS | role override language. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 91 | 135 | MUST CHECK | CHECKS | policy override language. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 92 | 136 | MUST CHECK | CHECKS | system/developer instruction override attempts. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 93 | 137 | MUST CHECK | CHECKS | tool/provider/credential authority claims. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 94 | 138 | MUST CHECK | CHECKS | durable write claims. | **PASS** | doctrine_xref, source_file, test_corpus |
| 95 | 139 | MUST CHECK | CHECKS | hidden target/action ambiguity. | **PASS** | doctrine_xref, source_file, test_corpus |
| 96 | 140 | MUST CHECK | CHECKS | malicious delimiter or instruction smuggling. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 97 | 143 | MUST CHECK | OUTPUTS | neutralized_user_task. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 98 | 144 | MUST CHECK | OUTPUTS | u0_airlock_receipt. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 99 | 145 | MUST CHECK | OUTPUTS | stripped_control_claims[]. | **PASS** | doctrine_xref, prose_keyword |
| 100 | 146 | MUST CHECK | OUTPUTS | preserved_task_intent_summary. | **PASS** | doctrine_xref, prose_keyword |
| 101 | 147 | MUST CHECK | OUTPUTS | u0_security_notes[]. | **PASS** | doctrine_xref, prose_keyword |
| 102 | 148 | MUST CHECK | C0 Retrieved-Content Classifier | 3. C0 Retrieved-Content Classifier | **PASS** | doctrine_xref, source_file, test_corpus |
| 103 | 151 | MUST CHECK | PURPOSE | Ensure retrieved chunks enter as evidence, not instructions. | **PASS** | doctrine_xref, source_file, test_corpus |
| 104 | 154 | MUST CHECK | CHECKS | instruction-like payloads in retrieved text. | **PASS** | doctrine_xref, source_file, test_corpus |
| 105 | 155 | MUST CHECK | CHECKS | coercive UI text. | **PASS** | doctrine_xref, source_file, test_corpus |
| 106 | 156 | MUST CHECK | CHECKS | embedded jailbreak text. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 107 | 157 | MUST CHECK | CHECKS | credential exfiltration language. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 108 | 158 | MUST CHECK | CHECKS | tool-call imitation. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 109 | 159 | MUST CHECK | CHECKS | fake policy text presented as live system authority. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 110 | 160 | MUST CHECK | CHECKS | stale or contradicted evidence flags from C0. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 111 | 163 | MUST CHECK | OUTPUTS | c0_payload_security_receipt. | **PASS** | doctrine_xref, prose_keyword |
| 112 | 164 | MUST CHECK | OUTPUTS | safe_c0_payload_map. | **PASS** | doctrine_xref, prose_keyword |
| 113 | 165 | MUST CHECK | OUTPUTS | rejected_c0_payload_report. | **PASS** | doctrine_xref, prose_keyword |
| 114 | 166 | MUST CHECK | OUTPUTS | safe_extraction_receipts[]. | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 115 | 167 | MUST CHECK | OUTPUTS | citation_preservation_receipt. | **PASS** | doctrine_xref, prose_keyword |
| 116 | 168 | MUST CHECK | H0 Healer Re-entry Validation | 4. H0 Healer Re-entry Validation | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 117 | 171 | MUST CHECK | CHECKS | same policy_hash. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 118 | 172 | MUST CHECK | CHECKS | same blueprint_hash. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 119 | 173 | MUST CHECK | CHECKS | same route/step scope. | **PASS** | doctrine_xref, source_file, test_corpus |
| 120 | 174 | MUST CHECK | CHECKS | no provider/tool/model substitution. | **PASS** | doctrine_xref, source_file, test_corpus |
| 121 | 175 | MUST CHECK | CHECKS | no scope widening. | **PASS** | doctrine_xref, source_file, test_corpus |
| 122 | 176 | MUST CHECK | CHECKS | no new facts without C0 support. | **PASS** | doctrine_xref, source_file, test_corpus |
| 123 | 177 | MUST CHECK | CHECKS | no bypass of L5/UWG/Exit. | **PASS** | doctrine_xref, source_file, test_corpus |
| 124 | 180 | MUST CHECK | OUTPUTS | h0_reentry_validation_receipt. | **PASS** | doctrine_xref, prose_keyword |
| 125 | 181 | MUST CHECK | OUTPUTS | h0_allowed_payload_map. | **PASS** | doctrine_xref, prose_keyword |
| 126 | 182 | MUST CHECK | OUTPUTS | h0_rejected_payload_report. | **PASS** | doctrine_xref, prose_keyword |
| 127 | 183 | MUST CHECK | Tool / Schema Text Safety | 5. Tool / Schema Text Safety | **PASS** | doctrine_xref, source_file, test_corpus |
| 128 | 186 | MUST CHECK | CHECKS | tool definitions are structured bindings, not untrusted text. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 129 | 187 | MUST CHECK | CHECKS | schema definitions are structured bindings, not loose prose. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 130 | 188 | MUST CHECK | CHECKS | user/retrieved text cannot define tools or schema fields. | **PASS** | doctrine_xref, source_file, test_corpus |
| 131 | 189 | MUST CHECK | CHECKS | provider-specific tool/schema fields are not polluted by U0/C0 content. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 132 | 194 | STATUS VALUES |  | PA_SECURITY_PASS | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 133 | 195 | STATUS VALUES |  | PA_SECURITY_GAP | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 134 | 196 | STATUS VALUES |  | PA_SAFE_EXTRACTION_PARTIAL | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 135 | 197 | STATUS VALUES |  | PA_SLOT_PAYLOAD_REJECTED | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 136 | 198 | STATUS VALUES |  | PA_REQUIRES_UPSTREAM_REPAIR | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 137 | 202 | MUST EMIT |  | AssemblySecurityPassReceipt | **PASS** | doctrine_xref, receipt_key, source_file |
| 138 | 203 | MUST EMIT |  | safe_slot_payload_map | **PASS** | doctrine_xref, receipt_key, source_file |
| 139 | 204 | MUST EMIT |  | rejected_slot_payload_report | **PASS** | doctrine_xref, receipt_key, source_file |
| 140 | 205 | MUST EMIT |  | prompt_like_payload_report | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 141 | 206 | MUST EMIT |  | safe_extraction_map | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 142 | 207 | MUST EMIT |  | security_gap_report | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 143 | 211 | MUST NOT |  | retrieve evidence | **PASS** | doctrine_xref, source_file, test_corpus |
| 144 | 212 | MUST NOT |  | route or reroute | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 145 | 213 | MUST NOT |  | call a model provider | **PASS** | doctrine_xref, source_file, test_corpus |
| 146 | 214 | MUST NOT |  | execute a tool | **PASS** | doctrine_xref, source_file, test_corpus |
| 147 | 215 | MUST NOT |  | approve the final answer | **PASS** | doctrine_xref, source_file, test_corpus |
| 148 | 216 | MUST NOT |  | commit durable state | **PASS** | doctrine_xref, source_file, test_corpus |
| 149 | 217 | MUST NOT |  | emit runtime dispositions | **PASS** | doctrine_xref, source_file, test_corpus |
| 150 | 218 | MUST NOT |  | silently drop mandatory evidence, authority, schema, or replay metadata | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 151 | 222 | ACCEPTANCE TESTS |  | No code path in this child retrieves evidence, routes, executes, calls providers, writes L4, or emits runtime disposition. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 152 | 223 | ACCEPTANCE TESTS |  | All emitted receipts preserve request_id, run_id, trace_id, route_id, policy_hash, and replay_key when available. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 153 | 224 | ACCEPTANCE TESTS |  | All gap conditions are explicit and replayable. | **PASS** | doctrine_xref, source_file, test_corpus |
| 154 | 225 | ACCEPTANCE TESTS |  | U0 injection attempt is neutralized without losing legitimate task intent. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 155 | 226 | ACCEPTANCE TESTS |  | Retrieved text containing ignore prior instructions remains data or is rejected from C0 slot. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 156 | 227 | ACCEPTANCE TESTS |  | H0 repair hint trying to change provider or tool is rejected. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |

## PA.4

| # | Line | Section | Sub-section | Requirement | Status | Evidence |
|---:|---:|---|---|---|:---:|---|
| 1 | 10 | GLOBAL NO-OVERLAP LAW |  | 00A L5 owns governance certification evidence, not live runtime dispositions and not durable write admission. | **PASS** | doctrine_xref, source_file, test_corpus |
| 2 | 11 | GLOBAL NO-OVERLAP LAW |  | 00B L4/UWG owns durable system-of-record state and durable write admission, not planning, routing, retrieval, execution, Exit disposition, or L6 learning mechanics. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 3 | 12 | GLOBAL NO-OVERLAP LAW |  | 00C Runtime Gates owns G01-G29 current-run GateVerdict law, not final Exit X3 aggregation and not L5 certification evidence. | **PASS** | doctrine_xref, source_file, test_corpus |
| 4 | 13 | GLOBAL NO-OVERLAP LAW |  | 00X owns traceability and no-loss mapping only. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 5 | 14 | GLOBAL NO-OVERLAP LAW |  | 01 Intake owns request envelope validation and identity/session/tenant baseline only. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 6 | 15 | GLOBAL NO-OVERLAP LAW |  | 02 L1 owns advisory interpretation and planning only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 7 | 16 | GLOBAL NO-OVERLAP LAW |  | 03 L0/L3 owns deterministic route selection and optional workflow orchestration only. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 8 | 17 | GLOBAL NO-OVERLAP LAW |  | C0 owns retrieval/evidence contracts only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 9 | 18 | GLOBAL NO-OVERLAP LAW |  | PA owns prompt packet construction only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 10 | 19 | GLOBAL NO-OVERLAP LAW |  | 04 L2 owns bounded execution and sealing only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 11 | 20 | GLOBAL NO-OVERLAP LAW |  | 05 Exit owns current-run checkout aggregation and exactly one X3 disposition only. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 12 | 21 | GLOBAL NO-OVERLAP LAW |  | 06 L6 owns completed-run evaluation, RCA, and future-run learning proposals only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 13 | 22 | GLOBAL NO-OVERLAP LAW |  | 99 owns proof harnesses only; it does not own runtime behavior. | **PASS** | doctrine_xref, source_file, test_corpus |
| 14 | 25 | REFERENCE POINTERS |  | Cross-cutting governance/certification evidence: 00A_L5_Governance_Safety/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 15 | 26 | REFERENCE POINTERS |  | Durable state and Universal Write Gateway: 00B_L4_State_Archive_and_UWG/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 16 | 27 | REFERENCE POINTERS |  | Current-run reusable gate mesh: 00C_Runtime_Gates_Current_Run_Mesh/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 17 | 28 | REFERENCE POINTERS |  | Traceability and zero-loss proof: 00X_Requirements_Traceability_and_No_Loss_Map.md | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 18 | 29 | REFERENCE POINTERS |  | End-to-end runtime proof harness: 99_End_to_End_Runtime_Proof_and_Acceptance/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 19 | 45 | UNIQUE OWNERSHIP SURFACE |  | assembled slot contract validation only | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 20 | 48 | THIS FILE OWNS |  | SlotValidationReceipt, authority-order validation, context contract validation, schema/tool binding validation, validation gap reports | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 21 | 51 | THIS FILE DOES NOT OWN |  | token budgeting, provider rendering, final signing, L2 execution validation, Exit/Runtimes Gates final output validation | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 22 | 54 | GLOBAL NO-OVERLAP LOCK |  | L1 owns intent interpretation, task_spec, query_spec, ambiguity register, and planning recommendations. | **PASS** | doctrine_xref, source_file, test_corpus |
| 23 | 55 | GLOBAL NO-OVERLAP LOCK |  | L0 owns route selection, RouteContract, execution_form, provider lane, route risk, and route authority. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 24 | 56 | GLOBAL NO-OVERLAP LOCK |  | C0 owns retrieval, hydration, graph expansion, evidence shaping, verification, support scoring, and FinalEvidenceContract. | **PASS** | doctrine_xref, source_file, test_corpus |
| 25 | 57 | GLOBAL NO-OVERLAP LOCK |  | L5 owns policy, authority context, origin trust, egress, replay, audit, HITL re-clearance, and certification evidence. | **PASS** | doctrine_xref, source_file, test_corpus |
| 26 | 58 | GLOBAL NO-OVERLAP LOCK |  | Prompt Assembly owns only bounded prompt-packet composition and signed prompt artifact emission. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 27 | 59 | GLOBAL NO-OVERLAP LOCK |  | L2 owns bounded execution, SovereignLLMGateway dispatch, provider/model/tool calls, and sealed work artifacts. | **PASS** | doctrine_xref, source_file, test_corpus |
| 28 | 60 | GLOBAL NO-OVERLAP LOCK |  | Runtime Gates and Exit Eval own current-run dispositions. | **PASS** | doctrine_xref, source_file, test_corpus |
| 29 | 61 | GLOBAL NO-OVERLAP LOCK |  | UWG/L4 owns durable write admission and system-of-record mutation. | **PASS** | doctrine_xref, source_file, test_corpus |
| 30 | 62 | GLOBAL NO-OVERLAP LOCK |  | L6 owns completed-run evaluation, root-cause analysis, promotion proposals, and future-run learning. | **PASS** | doctrine_xref, source_file, test_corpus |
| 31 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ALLOW | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 32 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | DENY | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 33 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | CLARIFY | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 34 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ABSTAIN | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 35 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | REROUTE | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 36 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | SHRINK_SCOPE | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 37 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | RETRY | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 38 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | HEAL | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 39 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ESCALATE_HITL | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 40 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | QUARANTINE | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 41 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | REDACT | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 42 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | SAFE_FALLBACK | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 43 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | MARK_DEGRADED | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 44 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | COMMIT_REQUEST | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 45 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | BLOCK_COMMIT | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 46 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ALLOW_FINISH | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 47 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | approve_execution | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 48 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | approve_output | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 49 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | approve_write | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 50 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | call_provider | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 51 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | execute_tool | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 52 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | mutate_l4 | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 53 | 70 | ALLOWED OUTPUT STYLE |  | receipts, manifests, hashes, validation statuses, assembly statuses, gap reports, artifact refs, replay/audit refs | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 54 | 76 | END OVERWRITE RECONCILIATION HEADER | PARENT | Prompt_Assembly.md | **PASS** | doctrine_xref, source_file, test_corpus |
| 55 | 79 | END OVERWRITE RECONCILIATION HEADER | ROLE | Detailed child file for PA.4 VALIDATE SLOT CONTRACT. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 56 | 80 | END OVERWRITE RECONCILIATION HEADER | ROLE | Defines the implementation-grade requirements for its unique Prompt Assembly surface. | **PASS** | doctrine_xref, source_file, test_corpus |
| 57 | 81 | END OVERWRITE RECONCILIATION HEADER | ROLE | Emits Prompt Assembly evidence only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 58 | 82 | END OVERWRITE RECONCILIATION HEADER | ROLE | Does not emit runtime dispositions. | **PASS** | doctrine_xref, source_file, test_corpus |
| 59 | 83 | END OVERWRITE RECONCILIATION HEADER | ROLE | Does not retrieve, route, execute, call providers, write durable state, or promote learning. | **PASS** | doctrine_xref, source_file, test_corpus |
| 60 | 87 | WHY THIS FILE EXISTS |  | Prompt Assembly is a high-risk boundary because it binds rules, evidence, task text, schema, tools, provider metadata, | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 61 | 89 | WHY THIS FILE EXISTS |  | This child isolates one Prompt Assembly surface so the parent stays doctrinal and no other layer inherits prompt assembly | **PASS** | doctrine_xref, source_file, test_corpus |
| 62 | 91 | WHY THIS FILE EXISTS |  | This child is intentionally detailed enough for implementation, tests, traces, and replay evidence. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 63 | 95 | PRIMARY QUESTION |  | "assembled slot contract validation only?" | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 64 | 99 | SOURCE OWNERSHIP BOUNDARY |  | This file may emit assembly receipts, manifests, hashes, statuses, and gap reports for its unique surface. | **PASS** | doctrine_xref, source_file, test_corpus |
| 65 | 100 | SOURCE OWNERSHIP BOUNDARY |  | This file must not fetch missing data. | **PASS** | doctrine_xref, source_file, test_corpus |
| 66 | 101 | SOURCE OWNERSHIP BOUNDARY |  | This file must not modify RouteContract, PlanContract, FinalEvidenceContract, policy, registry, capability, sandbox, or L4 state. | **PASS** | doctrine_xref, source_file, test_corpus |
| 67 | 102 | SOURCE OWNERSHIP BOUNDARY |  | This file must not approve L2 execution. It only prepares evidence for L2 validation. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 68 | 104 | SOURCE OWNERSHIP BOUNDARY | Validation Input | 1. Validation Input | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 69 | 107 | SOURCE OWNERSHIP BOUNDARY | FIELDS | validation_id | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 70 | 108 | SOURCE OWNERSHIP BOUNDARY | FIELDS | structured_slots_id | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 71 | 109 | SOURCE OWNERSHIP BOUNDARY | FIELDS | security_pass_receipt_ref | **PASS** | doctrine_xref, receipt_key, source_file |
| 72 | 110 | SOURCE OWNERSHIP BOUNDARY | FIELDS | PromptBOM_ref | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 73 | 111 | SOURCE OWNERSHIP BOUNDARY | FIELDS | PAAssemblyInput_ref | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 74 | 112 | SOURCE OWNERSHIP BOUNDARY | FIELDS | slot_hashes{} | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 75 | 113 | SOURCE OWNERSHIP BOUNDARY | FIELDS | policy_hash | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 76 | 114 | SOURCE OWNERSHIP BOUNDARY | FIELDS | blueprint_hash | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 77 | 115 | SOURCE OWNERSHIP BOUNDARY | FIELDS | replay_key | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 78 | 116 | SOURCE OWNERSHIP BOUNDARY | FIELDS | provider_lane | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 79 | 117 | SOURCE OWNERSHIP BOUNDARY | FIELDS | response_schema_contract_ref | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 80 | 118 | SOURCE OWNERSHIP BOUNDARY | FIELDS | tool_schema_refs[] | **PASS** | doctrine_xref, prose_keyword, source_file |
| 81 | 119 | SOURCE OWNERSHIP BOUNDARY | FIELDS | C0FinalEvidenceContract_ref if applicable | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 82 | 120 | SOURCE OWNERSHIP BOUNDARY | Slot Order Validation | 2. Slot Order Validation | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 83 | 123 | MUST CHECK |  | canonical slot order is preserved. | **PASS** | doctrine_xref, source_file, test_corpus |
| 84 | 124 | MUST CHECK |  | S0 before D0 before I0 before E0 before C0 before M0 before U0 before H0. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 85 | 125 | MUST CHECK |  | Y0 only included where policy permits and with promotion refs. | **PASS** | doctrine_xref, source_file, test_corpus |
| 86 | 126 | MUST CHECK |  | R0 exists as a binding outside loose prose where possible. | **PASS** | doctrine_xref, source_file, test_corpus |
| 87 | 127 | MUST CHECK |  | no slot is duplicated. | **PASS** | doctrine_xref, source_file, test_corpus |
| 88 | 128 | MUST CHECK |  | no required slot is missing for the route class. | **PASS** | doctrine_xref, source_file, test_corpus |
| 89 | 129 | MUST CHECK | Authority Validation | 3. Authority Validation | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 90 | 132 | MUST CHECK |  | U0 cannot override S0/D0/I0. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 91 | 133 | MUST CHECK |  | C0 cannot introduce instructions that override D0/I0. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 92 | 134 | MUST CHECK |  | E0 cannot override R0 schema. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 93 | 135 | MUST CHECK |  | H0 cannot widen repair scope. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 94 | 136 | MUST CHECK |  | Y0 cannot override current policy or route. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 95 | 137 | MUST CHECK |  | tool/schema definitions cannot be supplied by lower-authority text. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 96 | 138 | MUST CHECK |  | all authority labels are present. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 97 | 139 | MUST CHECK | Context Contract Validation | 4. Context Contract Validation | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 98 | 142 | MUST CHECK WHEN GROUNDING REQUIRED |  | C0FinalEvidenceContract_ref exists. | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 99 | 143 | MUST CHECK WHEN GROUNDING REQUIRED |  | verified chunks are present unless C0 status allows abstain/gap output. | **PASS** | doctrine_xref, forbidden_token, prose_keyword, receipt_key, source_file, test_corpus |
| 100 | 144 | MUST CHECK WHEN GROUNDING REQUIRED |  | citations are preserved. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 101 | 145 | MUST CHECK WHEN GROUNDING REQUIRED |  | support gaps are preserved. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 102 | 146 | MUST CHECK WHEN GROUNDING REQUIRED |  | contradiction flags are preserved. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 103 | 147 | MUST CHECK WHEN GROUNDING REQUIRED |  | abstain recommendation is preserved if present. | **PASS** | doctrine_xref, forbidden_token, prose_keyword, receipt_key, source_file, test_corpus |
| 104 | 148 | MUST CHECK WHEN GROUNDING REQUIRED |  | source lineage is not flattened. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 105 | 149 | MUST CHECK WHEN GROUNDING REQUIRED |  | C0 status is not inflated by PA. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 106 | 150 | MUST CHECK WHEN GROUNDING REQUIRED | Tool and Schema Validation | 5. Tool and Schema Validation | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 107 | 153 | MUST CHECK |  | tools are bound through provider tools field or equivalent structured binding. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 108 | 154 | MUST CHECK |  | R0 schema is bound through response_schema / response_format or equivalent structured binding. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 109 | 155 | MUST CHECK |  | tool schema is not inline prose when provider-native field is available. | **PASS** | doctrine_xref, source_file, test_corpus |
| 110 | 156 | MUST CHECK |  | response schema is not contradicted by examples or U0 task text. | **PASS** | doctrine_xref, source_file, test_corpus |
| 111 | 157 | MUST CHECK |  | required output fields are present in schema binding. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 112 | 158 | MUST CHECK |  | prohibited output fields are represented where required. | **PASS** | doctrine_xref, source_file, test_corpus |
| 113 | 163 | STATUS VALUES |  | PA_SLOT_CONTRACT_VALID | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 114 | 164 | STATUS VALUES |  | PA_SLOT_CONTRACT_INVALID | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 115 | 165 | STATUS VALUES |  | PA_CONTEXT_CONTRACT_GAP | **PASS** | doctrine_xref, prose_keyword, source_file, status_value, test_corpus |
| 116 | 166 | STATUS VALUES |  | PA_AUTHORITY_INVERSION_GAP | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 117 | 167 | STATUS VALUES |  | PA_SCHEMA_BINDING_GAP | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 118 | 168 | STATUS VALUES |  | PA_TOOL_BINDING_GAP | **PASS** | doctrine_xref, prose_keyword, source_file, status_value, test_corpus |
| 119 | 172 | MUST EMIT |  | SlotValidationReceipt | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file |
| 120 | 173 | MUST EMIT |  | validation_gap_report | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file |
| 121 | 174 | MUST EMIT |  | authority_order_receipt | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file |
| 122 | 175 | MUST EMIT |  | context_contract_receipt | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 123 | 176 | MUST EMIT |  | tool_schema_binding_receipt | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file |
| 124 | 177 | MUST EMIT |  | validation_hash_receipt | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file |
| 125 | 181 | MUST NOT |  | retrieve evidence | **PASS** | doctrine_xref, source_file, test_corpus |
| 126 | 182 | MUST NOT |  | route or reroute | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 127 | 183 | MUST NOT |  | call a model provider | **PASS** | doctrine_xref, source_file, test_corpus |
| 128 | 184 | MUST NOT |  | execute a tool | **PASS** | doctrine_xref, source_file, test_corpus |
| 129 | 185 | MUST NOT |  | approve the final answer | **PASS** | doctrine_xref, source_file, test_corpus |
| 130 | 186 | MUST NOT |  | commit durable state | **PASS** | doctrine_xref, source_file, test_corpus |
| 131 | 187 | MUST NOT |  | emit runtime dispositions | **PASS** | doctrine_xref, source_file, test_corpus |
| 132 | 188 | MUST NOT |  | silently drop mandatory evidence, authority, schema, or replay metadata | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 133 | 192 | ACCEPTANCE TESTS |  | No code path in this child retrieves evidence, routes, executes, calls providers, writes L4, or emits runtime disposition. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 134 | 193 | ACCEPTANCE TESTS |  | All emitted receipts preserve request_id, run_id, trace_id, route_id, policy_hash, and replay_key when available. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 135 | 194 | ACCEPTANCE TESTS |  | All gap conditions are explicit and replayable. | **PASS** | doctrine_xref, source_file, test_corpus |
| 136 | 195 | ACCEPTANCE TESTS |  | Wrong slot order fails validation. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 137 | 196 | ACCEPTANCE TESTS |  | C0 evidence missing on grounded route fails context contract validation. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 138 | 197 | ACCEPTANCE TESTS |  | Tool schema included as loose prose when provider tool field exists fails tool binding validation. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |

## PA.5

| # | Line | Section | Sub-section | Requirement | Status | Evidence |
|---:|---:|---|---|---|:---:|---|
| 1 | 10 | GLOBAL NO-OVERLAP LAW |  | 00A L5 owns governance certification evidence, not live runtime dispositions and not durable write admission. | **PASS** | doctrine_xref, source_file, test_corpus |
| 2 | 11 | GLOBAL NO-OVERLAP LAW |  | 00B L4/UWG owns durable system-of-record state and durable write admission, not planning, routing, retrieval, execution, Exit disposition, or L6 learning mechanics. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 3 | 12 | GLOBAL NO-OVERLAP LAW |  | 00C Runtime Gates owns G01-G29 current-run GateVerdict law, not final Exit X3 aggregation and not L5 certification evidence. | **PASS** | doctrine_xref, source_file, test_corpus |
| 4 | 13 | GLOBAL NO-OVERLAP LAW |  | 00X owns traceability and no-loss mapping only. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 5 | 14 | GLOBAL NO-OVERLAP LAW |  | 01 Intake owns request envelope validation and identity/session/tenant baseline only. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 6 | 15 | GLOBAL NO-OVERLAP LAW |  | 02 L1 owns advisory interpretation and planning only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 7 | 16 | GLOBAL NO-OVERLAP LAW |  | 03 L0/L3 owns deterministic route selection and optional workflow orchestration only. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 8 | 17 | GLOBAL NO-OVERLAP LAW |  | C0 owns retrieval/evidence contracts only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 9 | 18 | GLOBAL NO-OVERLAP LAW |  | PA owns prompt packet construction only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 10 | 19 | GLOBAL NO-OVERLAP LAW |  | 04 L2 owns bounded execution and sealing only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 11 | 20 | GLOBAL NO-OVERLAP LAW |  | 05 Exit owns current-run checkout aggregation and exactly one X3 disposition only. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 12 | 21 | GLOBAL NO-OVERLAP LAW |  | 06 L6 owns completed-run evaluation, RCA, and future-run learning proposals only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 13 | 22 | GLOBAL NO-OVERLAP LAW |  | 99 owns proof harnesses only; it does not own runtime behavior. | **PASS** | doctrine_xref, source_file, test_corpus |
| 14 | 25 | REFERENCE POINTERS |  | Cross-cutting governance/certification evidence: 00A_L5_Governance_Safety/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 15 | 26 | REFERENCE POINTERS |  | Durable state and Universal Write Gateway: 00B_L4_State_Archive_and_UWG/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 16 | 27 | REFERENCE POINTERS |  | Current-run reusable gate mesh: 00C_Runtime_Gates_Current_Run_Mesh/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 17 | 28 | REFERENCE POINTERS |  | Traceability and zero-loss proof: 00X_Requirements_Traceability_and_No_Loss_Map.md | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 18 | 29 | REFERENCE POINTERS |  | End-to-end runtime proof harness: 99_End_to_End_Runtime_Proof_and_Acceptance/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 19 | 45 | UNIQUE OWNERSHIP SURFACE |  | token budgeting and deterministic prompt-packet shaping only | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 20 | 48 | THIS FILE OWNS |  | TokenBudgetLedger, deterministic trimming receipt, stable prefix receipt, canonical hash input manifest, overflow gap reports | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 21 | 51 | THIS FILE DOES NOT OWN |  | provider rendering, final signing, L2 replay execution/comparison, runtime budget gate dispositions | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 22 | 54 | GLOBAL NO-OVERLAP LOCK |  | L1 owns intent interpretation, task_spec, query_spec, ambiguity register, and planning recommendations. | **PASS** | doctrine_xref, source_file, test_corpus |
| 23 | 55 | GLOBAL NO-OVERLAP LOCK |  | L0 owns route selection, RouteContract, execution_form, provider lane, route risk, and route authority. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 24 | 56 | GLOBAL NO-OVERLAP LOCK |  | C0 owns retrieval, hydration, graph expansion, evidence shaping, verification, support scoring, and FinalEvidenceContract. | **PASS** | doctrine_xref, source_file, test_corpus |
| 25 | 57 | GLOBAL NO-OVERLAP LOCK |  | L5 owns policy, authority context, origin trust, egress, replay, audit, HITL re-clearance, and certification evidence. | **PASS** | doctrine_xref, source_file, test_corpus |
| 26 | 58 | GLOBAL NO-OVERLAP LOCK |  | Prompt Assembly owns only bounded prompt-packet composition and signed prompt artifact emission. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 27 | 59 | GLOBAL NO-OVERLAP LOCK |  | L2 owns bounded execution, SovereignLLMGateway dispatch, provider/model/tool calls, and sealed work artifacts. | **PASS** | doctrine_xref, source_file, test_corpus |
| 28 | 60 | GLOBAL NO-OVERLAP LOCK |  | Runtime Gates and Exit Eval own current-run dispositions. | **PASS** | doctrine_xref, source_file, test_corpus |
| 29 | 61 | GLOBAL NO-OVERLAP LOCK |  | UWG/L4 owns durable write admission and system-of-record mutation. | **PASS** | doctrine_xref, source_file, test_corpus |
| 30 | 62 | GLOBAL NO-OVERLAP LOCK |  | L6 owns completed-run evaluation, root-cause analysis, promotion proposals, and future-run learning. | **PASS** | doctrine_xref, source_file, test_corpus |
| 31 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ALLOW | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 32 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | DENY | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 33 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | CLARIFY | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 34 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ABSTAIN | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 35 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | REROUTE | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 36 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | SHRINK_SCOPE | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 37 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | RETRY | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 38 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | HEAL | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 39 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ESCALATE_HITL | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 40 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | QUARANTINE | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 41 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | REDACT | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 42 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | SAFE_FALLBACK | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 43 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | MARK_DEGRADED | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 44 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | COMMIT_REQUEST | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 45 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | BLOCK_COMMIT | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 46 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ALLOW_FINISH | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 47 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | approve_execution | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 48 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | approve_output | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 49 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | approve_write | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 50 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | call_provider | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 51 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | execute_tool | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 52 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | mutate_l4 | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 53 | 70 | ALLOWED OUTPUT STYLE |  | receipts, manifests, hashes, validation statuses, assembly statuses, gap reports, artifact refs, replay/audit refs | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 54 | 76 | END OVERWRITE RECONCILIATION HEADER | PARENT | Prompt_Assembly.md | **PASS** | doctrine_xref, source_file, test_corpus |
| 55 | 79 | END OVERWRITE RECONCILIATION HEADER | ROLE | Detailed child file for PA.5 TOKEN BUDGET / DETERMINISM. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 56 | 80 | END OVERWRITE RECONCILIATION HEADER | ROLE | Defines the implementation-grade requirements for its unique Prompt Assembly surface. | **PASS** | doctrine_xref, source_file, test_corpus |
| 57 | 81 | END OVERWRITE RECONCILIATION HEADER | ROLE | Emits Prompt Assembly evidence only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 58 | 82 | END OVERWRITE RECONCILIATION HEADER | ROLE | Does not emit runtime dispositions. | **PASS** | doctrine_xref, source_file, test_corpus |
| 59 | 83 | END OVERWRITE RECONCILIATION HEADER | ROLE | Does not retrieve, route, execute, call providers, write durable state, or promote learning. | **PASS** | doctrine_xref, source_file, test_corpus |
| 60 | 87 | WHY THIS FILE EXISTS |  | Prompt Assembly is a high-risk boundary because it binds rules, evidence, task text, schema, tools, provider metadata, | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 61 | 89 | WHY THIS FILE EXISTS |  | This child isolates one Prompt Assembly surface so the parent stays doctrinal and no other layer inherits prompt assembly | **PASS** | doctrine_xref, source_file, test_corpus |
| 62 | 91 | WHY THIS FILE EXISTS |  | This child is intentionally detailed enough for implementation, tests, traces, and replay evidence. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 63 | 95 | PRIMARY QUESTION |  | "token budgeting and deterministic prompt-packet shaping only?" | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 64 | 99 | SOURCE OWNERSHIP BOUNDARY |  | This file may emit assembly receipts, manifests, hashes, statuses, and gap reports for its unique surface. | **PASS** | doctrine_xref, source_file, test_corpus |
| 65 | 100 | SOURCE OWNERSHIP BOUNDARY |  | This file must not fetch missing data. | **PASS** | doctrine_xref, source_file, test_corpus |
| 66 | 101 | SOURCE OWNERSHIP BOUNDARY |  | This file must not modify RouteContract, PlanContract, FinalEvidenceContract, policy, registry, capability, sandbox, or L4 state. | **PASS** | doctrine_xref, source_file, test_corpus |
| 67 | 102 | SOURCE OWNERSHIP BOUNDARY |  | This file must not approve L2 execution. It only prepares evidence for L2 validation. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 68 | 104 | SOURCE OWNERSHIP BOUNDARY | Token Budget Input | 1. Token Budget Input | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 69 | 107 | SOURCE OWNERSHIP BOUNDARY | FIELDS | budget_request_id | **PASS** | doctrine_xref, prose_keyword |
| 70 | 108 | SOURCE OWNERSHIP BOUNDARY | FIELDS | SlotValidationReceipt_ref | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file |
| 71 | 109 | SOURCE OWNERSHIP BOUNDARY | FIELDS | structured_slots_id | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 72 | 110 | SOURCE OWNERSHIP BOUNDARY | FIELDS | provider_lane | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 73 | 111 | SOURCE OWNERSHIP BOUNDARY | FIELDS | symbolic_model_id | **PASS** | doctrine_xref, runtime_symbol, source_file |
| 74 | 112 | SOURCE OWNERSHIP BOUNDARY | FIELDS | max_context_tokens | **PASS** | doctrine_xref, prose_keyword |
| 75 | 113 | SOURCE OWNERSHIP BOUNDARY | FIELDS | reserved_output_tokens | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 76 | 114 | SOURCE OWNERSHIP BOUNDARY | FIELDS | response_schema_overhead_estimate | **PASS** | doctrine_xref, prose_keyword |
| 77 | 115 | SOURCE OWNERSHIP BOUNDARY | FIELDS | tool_call_overhead_estimate | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 78 | 116 | SOURCE OWNERSHIP BOUNDARY | FIELDS | stable_prefix_policy_ref | **PASS** | doctrine_xref, prose_keyword |
| 79 | 117 | SOURCE OWNERSHIP BOUNDARY | FIELDS | route_budget_ref | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 80 | 118 | SOURCE OWNERSHIP BOUNDARY | FIELDS | C0_priority_order_ref | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 81 | 119 | SOURCE OWNERSHIP BOUNDARY | FIELDS | replay_key | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 82 | 120 | SOURCE OWNERSHIP BOUNDARY | FIELDS | policy_hash | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 83 | 121 | SOURCE OWNERSHIP BOUNDARY | Token Budget Ledger | 2. Token Budget Ledger | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 84 | 124 | SOURCE OWNERSHIP BOUNDARY | FIELDS | token_budget_ledger_id | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 85 | 125 | SOURCE OWNERSHIP BOUNDARY | FIELDS | input_token_budget | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 86 | 126 | SOURCE OWNERSHIP BOUNDARY | FIELDS | reserved_output_tokens | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 87 | 127 | SOURCE OWNERSHIP BOUNDARY | FIELDS | schema_overhead_tokens | **PASS** | doctrine_xref, prose_keyword |
| 88 | 128 | SOURCE OWNERSHIP BOUNDARY | FIELDS | tool_overhead_tokens | **PASS** | doctrine_xref, prose_keyword |
| 89 | 129 | SOURCE OWNERSHIP BOUNDARY | FIELDS | available_prompt_tokens | **PASS** | doctrine_xref, prose_keyword |
| 90 | 130 | SOURCE OWNERSHIP BOUNDARY | FIELDS | slot_token_estimates{} | **PASS** | doctrine_xref, prose_keyword |
| 91 | 131 | SOURCE OWNERSHIP BOUNDARY | FIELDS | mandatory_token_total | **PASS** | doctrine_xref, prose_keyword |
| 92 | 132 | SOURCE OWNERSHIP BOUNDARY | FIELDS | optional_token_total | **PASS** | doctrine_xref, prose_keyword |
| 93 | 133 | SOURCE OWNERSHIP BOUNDARY | FIELDS | trimming_needed | **PASS** | doctrine_xref, prose_keyword |
| 94 | 134 | SOURCE OWNERSHIP BOUNDARY | FIELDS | trimming_plan_ref | **PASS** | doctrine_xref, prose_keyword |
| 95 | 135 | SOURCE OWNERSHIP BOUNDARY | FIELDS | overflow_status | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 96 | 136 | SOURCE OWNERSHIP BOUNDARY | FIELDS | budget_hash | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 97 | 139 | MUST CHECK |  | output token reserve exists. | **PASS** | doctrine_xref, source_file, test_corpus |
| 98 | 140 | MUST CHECK |  | response schema reserve exists when structured output is required. | **PASS** | doctrine_xref, source_file, test_corpus |
| 99 | 141 | MUST CHECK |  | tool overhead reserve exists when tool use is possible. | **PASS** | doctrine_xref, source_file, test_corpus |
| 100 | 142 | MUST CHECK |  | S0/D0/I0 fit before optional content. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 101 | 143 | MUST CHECK |  | R0 schema binding fits or provider supports out-of-band schema without prompt token impact. | **PASS** | doctrine_xref, source_file, test_corpus |
| 102 | 144 | MUST CHECK |  | C0 must-use evidence fits for grounded answer or overflow is raised. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 103 | 145 | MUST CHECK | Deterministic Trimming Order | 3. Deterministic Trimming Order | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 104 | 148 | MUST CHECK | Remove/compress oldest optional conversation history if present. | 1. Remove/compress oldest optional conversation history if present. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 105 | 149 | MUST CHECK | Remove lowest-ranked optional E0 exemplars. | 2. Remove lowest-ranked optional E0 exemplars. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 106 | 150 | MUST CHECK | Remove lowest-ranked optional C0 chunks that are not must-use and not citation anchors. | 3. Remove lowest-ranked optional C0 chunks that are not must-use and not citation anchors. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 107 | 151 | MUST CHECK | Compress optional Y0/H0 hints if allowed. | 4. Compress optional Y0/H0 hints if allowed. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 108 | 152 | MUST CHECK | Preserve S0/D0/I0 intact. | 5. Preserve S0/D0/I0 intact. | **PASS** | doctrine_xref, source_file, test_corpus |
| 109 | 153 | MUST CHECK | Preserve must-use evidence and citation anchors. | 6. Preserve must-use evidence and citation anchors. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 110 | 154 | MUST CHECK | Preserve R0 binding. | 7. Preserve R0 binding. | **PASS** | doctrine_xref, source_file, test_corpus |
| 111 | 155 | MUST CHECK | If mandatory content still cannot fit, emit PA_BUDGET_OVERFLOW. | 8. If mandatory content still cannot fit, emit PA_BUDGET_OVERFLOW. | **PASS** | doctrine_xref, prose_keyword, source_file, status_value, test_corpus |
| 112 | 158 | TRIMMING RECEIPT FIELDS |  | trimming_receipt_id | **PASS** | doctrine_xref, prose_keyword, source_file |
| 113 | 159 | TRIMMING RECEIPT FIELDS |  | removed_items[] | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 114 | 160 | TRIMMING RECEIPT FIELDS |  | compressed_items[] | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 115 | 161 | TRIMMING RECEIPT FIELDS |  | preserved_mandatory_items[] | **PASS** | doctrine_xref, prose_keyword |
| 116 | 162 | TRIMMING RECEIPT FIELDS |  | reason_codes[] | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 117 | 163 | TRIMMING RECEIPT FIELDS |  | before_token_estimate | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 118 | 164 | TRIMMING RECEIPT FIELDS |  | after_token_estimate | **PASS** | doctrine_xref, receipt_key, source_file |
| 119 | 165 | TRIMMING RECEIPT FIELDS |  | deterministic_order_version | **PASS** | doctrine_xref, prose_keyword |
| 120 | 166 | TRIMMING RECEIPT FIELDS |  | trimming_hash | **PASS** | doctrine_xref, prose_keyword, source_file |
| 121 | 167 | TRIMMING RECEIPT FIELDS | Canonical Hash Input Discipline | 4. Canonical Hash Input Discipline | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 122 | 170 | TRIMMING RECEIPT FIELDS | Canonical Hash Input Discipline | selected slot IDs. | **PASS** | doctrine_xref, source_file, test_corpus |
| 123 | 171 | TRIMMING RECEIPT FIELDS | Canonical Hash Input Discipline | canonical slot order. | **PASS** | doctrine_xref, source_file, test_corpus |
| 124 | 172 | TRIMMING RECEIPT FIELDS | Canonical Hash Input Discipline | normalized slot payloads after trimming. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 125 | 173 | TRIMMING RECEIPT FIELDS | Canonical Hash Input Discipline | schema binding refs. | **PASS** | doctrine_xref, source_file, test_corpus |
| 126 | 174 | TRIMMING RECEIPT FIELDS | Canonical Hash Input Discipline | tool binding refs. | **PASS** | doctrine_xref, source_file, test_corpus |
| 127 | 175 | TRIMMING RECEIPT FIELDS | Canonical Hash Input Discipline | provider lane metadata that affects rendered meaning. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 128 | 176 | TRIMMING RECEIPT FIELDS | Canonical Hash Input Discipline | policy_hash / blueprint_hash / replay_key where required. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 129 | 179 | TRIMMING RECEIPT FIELDS | Canonical Hash Input Discipline | idempotency nonce. | **PASS** | doctrine_xref, source_file, test_corpus |
| 130 | 180 | TRIMMING RECEIPT FIELDS | Canonical Hash Input Discipline | wall-clock created_at if not run-clock normalized. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 131 | 181 | TRIMMING RECEIPT FIELDS | Canonical Hash Input Discipline | transient object memory addresses. | **PASS** | doctrine_xref, source_file, test_corpus |
| 132 | 182 | TRIMMING RECEIPT FIELDS | Canonical Hash Input Discipline | provider request IDs not known until execution. | **PASS** | doctrine_xref, source_file, test_corpus |
| 133 | 187 | STATUS VALUES |  | PA_BUDGET_FIT | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 134 | 188 | STATUS VALUES |  | PA_BUDGET_TRIMMED | **PASS** | doctrine_xref, prose_keyword, source_file, status_value, test_corpus |
| 135 | 189 | STATUS VALUES |  | PA_BUDGET_OVERFLOW | **PASS** | doctrine_xref, prose_keyword, source_file, status_value, test_corpus |
| 136 | 190 | STATUS VALUES |  | PA_REQUIRES_UPSTREAM_REPAIR | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 137 | 194 | MUST EMIT |  | TokenBudgetLedger | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file |
| 138 | 195 | MUST EMIT |  | deterministic_trimming_receipt | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file |
| 139 | 196 | MUST EMIT |  | stable_prefix_receipt | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 140 | 197 | MUST EMIT |  | overflow_gap_report | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file |
| 141 | 198 | MUST EMIT |  | canonical_hash_input_manifest | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file |
| 142 | 199 | MUST EMIT |  | budget_status_receipt | **PASS** | doctrine_xref, receipt_key, source_file |
| 143 | 203 | MUST NOT |  | retrieve evidence | **PASS** | doctrine_xref, source_file, test_corpus |
| 144 | 204 | MUST NOT |  | route or reroute | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 145 | 205 | MUST NOT |  | call a model provider | **PASS** | doctrine_xref, source_file, test_corpus |
| 146 | 206 | MUST NOT |  | execute a tool | **PASS** | doctrine_xref, source_file, test_corpus |
| 147 | 207 | MUST NOT |  | approve the final answer | **PASS** | doctrine_xref, source_file, test_corpus |
| 148 | 208 | MUST NOT |  | commit durable state | **PASS** | doctrine_xref, source_file, test_corpus |
| 149 | 209 | MUST NOT |  | emit runtime dispositions | **PASS** | doctrine_xref, source_file, test_corpus |
| 150 | 210 | MUST NOT |  | silently drop mandatory evidence, authority, schema, or replay metadata | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 151 | 214 | ACCEPTANCE TESTS |  | No code path in this child retrieves evidence, routes, executes, calls providers, writes L4, or emits runtime disposition. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 152 | 215 | ACCEPTANCE TESTS |  | All emitted receipts preserve request_id, run_id, trace_id, route_id, policy_hash, and replay_key when available. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 153 | 216 | ACCEPTANCE TESTS |  | All gap conditions are explicit and replayable. | **PASS** | doctrine_xref, source_file, test_corpus |
| 154 | 217 | ACCEPTANCE TESTS |  | Optional exemplar is removed before must-use C0 citation anchor. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 155 | 218 | ACCEPTANCE TESTS |  | Required evidence overflow emits PA_BUDGET_OVERFLOW. | **PASS** | doctrine_xref, prose_keyword, source_file, status_value, test_corpus |
| 156 | 219 | ACCEPTANCE TESTS |  | Idempotency nonce does not change canonical manifest hash. | **PASS** | doctrine_xref, source_file, test_corpus |

## PA.6

| # | Line | Section | Sub-section | Requirement | Status | Evidence |
|---:|---:|---|---|---|:---:|---|
| 1 | 10 | GLOBAL NO-OVERLAP LAW |  | 00A L5 owns governance certification evidence, not live runtime dispositions and not durable write admission. | **PASS** | doctrine_xref, source_file, test_corpus |
| 2 | 11 | GLOBAL NO-OVERLAP LAW |  | 00B L4/UWG owns durable system-of-record state and durable write admission, not planning, routing, retrieval, execution, Exit disposition, or L6 learning mechanics. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 3 | 12 | GLOBAL NO-OVERLAP LAW |  | 00C Runtime Gates owns G01-G29 current-run GateVerdict law, not final Exit X3 aggregation and not L5 certification evidence. | **PASS** | doctrine_xref, source_file, test_corpus |
| 4 | 13 | GLOBAL NO-OVERLAP LAW |  | 00X owns traceability and no-loss mapping only. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 5 | 14 | GLOBAL NO-OVERLAP LAW |  | 01 Intake owns request envelope validation and identity/session/tenant baseline only. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 6 | 15 | GLOBAL NO-OVERLAP LAW |  | 02 L1 owns advisory interpretation and planning only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 7 | 16 | GLOBAL NO-OVERLAP LAW |  | 03 L0/L3 owns deterministic route selection and optional workflow orchestration only. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 8 | 17 | GLOBAL NO-OVERLAP LAW |  | C0 owns retrieval/evidence contracts only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 9 | 18 | GLOBAL NO-OVERLAP LAW |  | PA owns prompt packet construction only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 10 | 19 | GLOBAL NO-OVERLAP LAW |  | 04 L2 owns bounded execution and sealing only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 11 | 20 | GLOBAL NO-OVERLAP LAW |  | 05 Exit owns current-run checkout aggregation and exactly one X3 disposition only. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 12 | 21 | GLOBAL NO-OVERLAP LAW |  | 06 L6 owns completed-run evaluation, RCA, and future-run learning proposals only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 13 | 22 | GLOBAL NO-OVERLAP LAW |  | 99 owns proof harnesses only; it does not own runtime behavior. | **PASS** | doctrine_xref, source_file, test_corpus |
| 14 | 25 | REFERENCE POINTERS |  | Cross-cutting governance/certification evidence: 00A_L5_Governance_Safety/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 15 | 26 | REFERENCE POINTERS |  | Durable state and Universal Write Gateway: 00B_L4_State_Archive_and_UWG/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 16 | 27 | REFERENCE POINTERS |  | Current-run reusable gate mesh: 00C_Runtime_Gates_Current_Run_Mesh/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 17 | 28 | REFERENCE POINTERS |  | Traceability and zero-loss proof: 00X_Requirements_Traceability_and_No_Loss_Map.md | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 18 | 29 | REFERENCE POINTERS |  | End-to-end runtime proof harness: 99_End_to_End_Runtime_Proof_and_Acceptance/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 19 | 45 | UNIQUE OWNERSHIP SURFACE |  | provider-specific rendering of canonical slots only | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 20 | 48 | THIS FILE OWNS |  | ProviderRenderRequest, ProviderRenderManifest, provider adapter mappings, provider field placement, render gap reports | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 21 | 51 | THIS FILE DOES NOT OWN |  | provider invocation, L5 egress certification, model/tool execution, final artifact signing, output approval | **PASS** | doctrine_xref, source_file, test_corpus |
| 22 | 54 | GLOBAL NO-OVERLAP LOCK |  | L1 owns intent interpretation, task_spec, query_spec, ambiguity register, and planning recommendations. | **PASS** | doctrine_xref, source_file, test_corpus |
| 23 | 55 | GLOBAL NO-OVERLAP LOCK |  | L0 owns route selection, RouteContract, execution_form, provider lane, route risk, and route authority. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 24 | 56 | GLOBAL NO-OVERLAP LOCK |  | C0 owns retrieval, hydration, graph expansion, evidence shaping, verification, support scoring, and FinalEvidenceContract. | **PASS** | doctrine_xref, source_file, test_corpus |
| 25 | 57 | GLOBAL NO-OVERLAP LOCK |  | L5 owns policy, authority context, origin trust, egress, replay, audit, HITL re-clearance, and certification evidence. | **PASS** | doctrine_xref, source_file, test_corpus |
| 26 | 58 | GLOBAL NO-OVERLAP LOCK |  | Prompt Assembly owns only bounded prompt-packet composition and signed prompt artifact emission. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 27 | 59 | GLOBAL NO-OVERLAP LOCK |  | L2 owns bounded execution, SovereignLLMGateway dispatch, provider/model/tool calls, and sealed work artifacts. | **PASS** | doctrine_xref, source_file, test_corpus |
| 28 | 60 | GLOBAL NO-OVERLAP LOCK |  | Runtime Gates and Exit Eval own current-run dispositions. | **PASS** | doctrine_xref, source_file, test_corpus |
| 29 | 61 | GLOBAL NO-OVERLAP LOCK |  | UWG/L4 owns durable write admission and system-of-record mutation. | **PASS** | doctrine_xref, source_file, test_corpus |
| 30 | 62 | GLOBAL NO-OVERLAP LOCK |  | L6 owns completed-run evaluation, root-cause analysis, promotion proposals, and future-run learning. | **PASS** | doctrine_xref, source_file, test_corpus |
| 31 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ALLOW | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 32 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | DENY | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 33 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | CLARIFY | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 34 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ABSTAIN | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 35 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | REROUTE | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 36 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | SHRINK_SCOPE | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 37 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | RETRY | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 38 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | HEAL | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 39 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ESCALATE_HITL | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 40 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | QUARANTINE | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 41 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | REDACT | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 42 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | SAFE_FALLBACK | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 43 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | MARK_DEGRADED | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 44 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | COMMIT_REQUEST | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 45 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | BLOCK_COMMIT | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 46 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ALLOW_FINISH | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 47 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | approve_execution | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 48 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | approve_output | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 49 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | approve_write | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 50 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | call_provider | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 51 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | execute_tool | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 52 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | mutate_l4 | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 53 | 70 | ALLOWED OUTPUT STYLE |  | receipts, manifests, hashes, validation statuses, assembly statuses, gap reports, artifact refs, replay/audit refs | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 54 | 76 | END OVERWRITE RECONCILIATION HEADER | PARENT | Prompt_Assembly.md | **PASS** | doctrine_xref, source_file, test_corpus |
| 55 | 79 | END OVERWRITE RECONCILIATION HEADER | ROLE | Detailed child file for PA.6 PROVIDER-AWARE RENDERING. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 56 | 80 | END OVERWRITE RECONCILIATION HEADER | ROLE | Defines the implementation-grade requirements for its unique Prompt Assembly surface. | **PASS** | doctrine_xref, source_file, test_corpus |
| 57 | 81 | END OVERWRITE RECONCILIATION HEADER | ROLE | Emits Prompt Assembly evidence only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 58 | 82 | END OVERWRITE RECONCILIATION HEADER | ROLE | Does not emit runtime dispositions. | **PASS** | doctrine_xref, source_file, test_corpus |
| 59 | 83 | END OVERWRITE RECONCILIATION HEADER | ROLE | Does not retrieve, route, execute, call providers, write durable state, or promote learning. | **PASS** | doctrine_xref, source_file, test_corpus |
| 60 | 87 | WHY THIS FILE EXISTS |  | Prompt Assembly is a high-risk boundary because it binds rules, evidence, task text, schema, tools, provider metadata, | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 61 | 89 | WHY THIS FILE EXISTS |  | This child isolates one Prompt Assembly surface so the parent stays doctrinal and no other layer inherits prompt assembly | **PASS** | doctrine_xref, source_file, test_corpus |
| 62 | 91 | WHY THIS FILE EXISTS |  | This child is intentionally detailed enough for implementation, tests, traces, and replay evidence. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 63 | 95 | PRIMARY QUESTION |  | "provider-specific rendering of canonical slots only?" | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 64 | 99 | SOURCE OWNERSHIP BOUNDARY |  | This file may emit assembly receipts, manifests, hashes, statuses, and gap reports for its unique surface. | **PASS** | doctrine_xref, source_file, test_corpus |
| 65 | 100 | SOURCE OWNERSHIP BOUNDARY |  | This file must not fetch missing data. | **PASS** | doctrine_xref, source_file, test_corpus |
| 66 | 101 | SOURCE OWNERSHIP BOUNDARY |  | This file must not modify RouteContract, PlanContract, FinalEvidenceContract, policy, registry, capability, sandbox, or L4 state. | **PASS** | doctrine_xref, source_file, test_corpus |
| 67 | 102 | SOURCE OWNERSHIP BOUNDARY |  | This file must not approve L2 execution. It only prepares evidence for L2 validation. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 68 | 104 | SOURCE OWNERSHIP BOUNDARY | Provider Render Request | 1. Provider Render Request | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 69 | 107 | SOURCE OWNERSHIP BOUNDARY | FIELDS | render_request_id | **PASS** | doctrine_xref, prose_keyword |
| 70 | 108 | SOURCE OWNERSHIP BOUNDARY | FIELDS | TokenBudgetLedger_ref | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file |
| 71 | 109 | SOURCE OWNERSHIP BOUNDARY | FIELDS | canonical_hash_input_manifest_ref | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file |
| 72 | 110 | SOURCE OWNERSHIP BOUNDARY | FIELDS | structured_slots_ref | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 73 | 111 | SOURCE OWNERSHIP BOUNDARY | FIELDS | provider_lane | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 74 | 112 | SOURCE OWNERSHIP BOUNDARY | FIELDS | symbolic_model_id | **PASS** | doctrine_xref, runtime_symbol, source_file |
| 75 | 113 | SOURCE OWNERSHIP BOUNDARY | FIELDS | resolved_model_id if known | **PASS** | doctrine_xref, source_file, test_corpus |
| 76 | 114 | SOURCE OWNERSHIP BOUNDARY | FIELDS | provider_capabilities_ref | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 77 | 115 | SOURCE OWNERSHIP BOUNDARY | FIELDS | tool_binding_refs[] | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 78 | 116 | SOURCE OWNERSHIP BOUNDARY | FIELDS | response_schema_binding_ref | **PASS** | doctrine_xref, prose_keyword |
| 79 | 117 | SOURCE OWNERSHIP BOUNDARY | FIELDS | policy_hash | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 80 | 118 | SOURCE OWNERSHIP BOUNDARY | FIELDS | replay_key | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 81 | 119 | SOURCE OWNERSHIP BOUNDARY | Provider Render Manifest | 2. Provider Render Manifest | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 82 | 122 | SOURCE OWNERSHIP BOUNDARY | FIELDS | render_manifest_id | **PASS** | doctrine_xref, prose_keyword |
| 83 | 123 | SOURCE OWNERSHIP BOUNDARY | FIELDS | provider_lane | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 84 | 124 | SOURCE OWNERSHIP BOUNDARY | FIELDS | adapter_version | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 85 | 125 | SOURCE OWNERSHIP BOUNDARY | FIELDS | canonical_slot_hashes{} | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 86 | 126 | SOURCE OWNERSHIP BOUNDARY | FIELDS | rendered_message_refs[] | **PASS** | doctrine_xref, prose_keyword |
| 87 | 127 | SOURCE OWNERSHIP BOUNDARY | FIELDS | system_field_ref if applicable | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 88 | 128 | SOURCE OWNERSHIP BOUNDARY | FIELDS | developer_field_ref if applicable | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 89 | 129 | SOURCE OWNERSHIP BOUNDARY | FIELDS | user_field_ref if applicable | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 90 | 130 | SOURCE OWNERSHIP BOUNDARY | FIELDS | document_container_refs[] if applicable | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 91 | 131 | SOURCE OWNERSHIP BOUNDARY | FIELDS | tools_field_ref if applicable | **PASS** | doctrine_xref, runtime_symbol, source_file |
| 92 | 132 | SOURCE OWNERSHIP BOUNDARY | FIELDS | response_schema_field_ref if applicable | **PASS** | doctrine_xref, prose_keyword |
| 93 | 133 | SOURCE OWNERSHIP BOUNDARY | FIELDS | thinking_control_ref if applicable | **PASS** | doctrine_xref, prose_keyword |
| 94 | 134 | SOURCE OWNERSHIP BOUNDARY | FIELDS | render_warnings[] | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file |
| 95 | 135 | SOURCE OWNERSHIP BOUNDARY | FIELDS | unsupported_feature_reports[] | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 96 | 136 | SOURCE OWNERSHIP BOUNDARY | FIELDS | render_hash | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 97 | 137 | SOURCE OWNERSHIP BOUNDARY | Anthropic Lane | 3. Anthropic Lane | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 98 | 140 | MAPPING EXPECTATIONS |  | system field carries high-authority instructions. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 99 | 141 | MAPPING EXPECTATIONS |  | document containers may carry context/evidence where supported. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 100 | 142 | MAPPING EXPECTATIONS |  | long-context ordering may hoist data and tail-repeat bounded task reminder when adapter policy allows. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 101 | 143 | MAPPING EXPECTATIONS |  | tool definitions use provider-native tool structure. | **PASS** | doctrine_xref, source_file, test_corpus |
| 102 | 144 | MAPPING EXPECTATIONS |  | schema requirements use available structured-output/tool patterns where supported. | **PASS** | doctrine_xref, source_file, test_corpus |
| 103 | 145 | MAPPING EXPECTATIONS |  | hidden reasoning guidance is not exposed as chain-of-thought request. | **PASS** | doctrine_xref, source_file, test_corpus |
| 104 | 146 | MAPPING EXPECTATIONS | OpenAI GPT Lane | 4. OpenAI GPT Lane | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 105 | 149 | MAPPING EXPECTATIONS |  | system/developer/user roles are used according to provider rules. | **PASS** | doctrine_xref, source_file, test_corpus |
| 106 | 150 | MAPPING EXPECTATIONS |  | headings may separate Role, Instructions, Context, Examples, Final Instructions. | **PASS** | doctrine_xref, source_file, test_corpus |
| 107 | 151 | MAPPING EXPECTATIONS |  | tool schemas ride API tools field. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 108 | 152 | MAPPING EXPECTATIONS |  | response schema rides response_format / structured output field where available. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 109 | 153 | MAPPING EXPECTATIONS |  | C0 is not placed in a higher-authority instruction slot. | **PASS** | doctrine_xref, source_file, test_corpus |
| 110 | 154 | MAPPING EXPECTATIONS | OpenAI Reasoning Lane | 5. OpenAI Reasoning Lane | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 111 | 157 | MAPPING EXPECTATIONS |  | thinking controls ride provider-native reasoning metadata where supported. | **PASS** | doctrine_xref, source_file, test_corpus |
| 112 | 158 | MAPPING EXPECTATIONS |  | do not ask the model to reveal chain-of-thought. | **PASS** | doctrine_xref, source_file, test_corpus |
| 113 | 159 | MAPPING EXPECTATIONS |  | preserve concise answer discipline and private control hints in safe form. | **PASS** | doctrine_xref, source_file, test_corpus |
| 114 | 160 | MAPPING EXPECTATIONS |  | reasoning effort / temperature metadata matches RouteContract. | **PASS** | doctrine_xref, source_file, test_corpus |
| 115 | 161 | MAPPING EXPECTATIONS | Gemini Lane | 6. Gemini Lane | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 116 | 164 | MAPPING EXPECTATIONS |  | data-first or instruction-after-data patterns may be used for long context if adapter policy requires it. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 117 | 165 | MAPPING EXPECTATIONS |  | structured outputs ride response_schema field where available. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 118 | 166 | MAPPING EXPECTATIONS |  | authority labels must remain clear when provider roles differ. | **PASS** | doctrine_xref, source_file, test_corpus |
| 119 | 171 | STATUS VALUES |  | PA_RENDERED | **PASS** | doctrine_xref, prose_keyword, source_file, status_value, test_corpus |
| 120 | 172 | STATUS VALUES |  | PA_RENDER_GAP | **PASS** | doctrine_xref, prose_keyword, source_file, status_value, test_corpus |
| 121 | 173 | STATUS VALUES |  | PA_PROVIDER_FEATURE_GAP | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 122 | 174 | STATUS VALUES |  | PA_SCHEMA_RENDER_GAP | **PASS** | doctrine_xref, prose_keyword, source_file, status_value, test_corpus |
| 123 | 175 | STATUS VALUES |  | PA_TOOL_RENDER_GAP | **PASS** | doctrine_xref, prose_keyword, source_file, status_value, test_corpus |
| 124 | 179 | MUST EMIT |  | ProviderRenderManifest | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file |
| 125 | 180 | MUST EMIT |  | rendered_prompt_packet | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file |
| 126 | 181 | MUST EMIT |  | provider_field_mapping_receipt | **PASS** | doctrine_xref, receipt_key, source_file |
| 127 | 182 | MUST EMIT |  | provider_feature_gap_report | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 128 | 183 | MUST EMIT |  | schema_render_receipt | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 129 | 184 | MUST EMIT |  | tool_render_receipt | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 130 | 188 | MUST NOT |  | retrieve evidence | **PASS** | doctrine_xref, source_file, test_corpus |
| 131 | 189 | MUST NOT |  | route or reroute | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 132 | 190 | MUST NOT |  | call a model provider | **PASS** | doctrine_xref, source_file, test_corpus |
| 133 | 191 | MUST NOT |  | execute a tool | **PASS** | doctrine_xref, source_file, test_corpus |
| 134 | 192 | MUST NOT |  | approve the final answer | **PASS** | doctrine_xref, source_file, test_corpus |
| 135 | 193 | MUST NOT |  | commit durable state | **PASS** | doctrine_xref, source_file, test_corpus |
| 136 | 194 | MUST NOT |  | emit runtime dispositions | **PASS** | doctrine_xref, source_file, test_corpus |
| 137 | 195 | MUST NOT |  | silently drop mandatory evidence, authority, schema, or replay metadata | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 138 | 199 | ACCEPTANCE TESTS |  | No code path in this child retrieves evidence, routes, executes, calls providers, writes L4, or emits runtime disposition. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 139 | 200 | ACCEPTANCE TESTS |  | All emitted receipts preserve request_id, run_id, trace_id, route_id, policy_hash, and replay_key when available. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 140 | 201 | ACCEPTANCE TESTS |  | All gap conditions are explicit and replayable. | **PASS** | doctrine_xref, source_file, test_corpus |
| 141 | 202 | ACCEPTANCE TESTS |  | Same canonical slots render differently per provider but preserve same canonical hash input manifest. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 142 | 203 | ACCEPTANCE TESTS |  | C0 evidence is never rendered as system/developer instruction. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 143 | 204 | ACCEPTANCE TESTS |  | Unsupported provider feature emits PA_PROVIDER_FEATURE_GAP. | **PASS** | doctrine_xref, source_file, status_value, test_corpus |

## PA.7

| # | Line | Section | Sub-section | Requirement | Status | Evidence |
|---:|---:|---|---|---|:---:|---|
| 1 | 10 | GLOBAL NO-OVERLAP LAW |  | 00A L5 owns governance certification evidence, not live runtime dispositions and not durable write admission. | **PASS** | doctrine_xref, source_file, test_corpus |
| 2 | 11 | GLOBAL NO-OVERLAP LAW |  | 00B L4/UWG owns durable system-of-record state and durable write admission, not planning, routing, retrieval, execution, Exit disposition, or L6 learning mechanics. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 3 | 12 | GLOBAL NO-OVERLAP LAW |  | 00C Runtime Gates owns G01-G29 current-run GateVerdict law, not final Exit X3 aggregation and not L5 certification evidence. | **PASS** | doctrine_xref, source_file, test_corpus |
| 4 | 13 | GLOBAL NO-OVERLAP LAW |  | 00X owns traceability and no-loss mapping only. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 5 | 14 | GLOBAL NO-OVERLAP LAW |  | 01 Intake owns request envelope validation and identity/session/tenant baseline only. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 6 | 15 | GLOBAL NO-OVERLAP LAW |  | 02 L1 owns advisory interpretation and planning only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 7 | 16 | GLOBAL NO-OVERLAP LAW |  | 03 L0/L3 owns deterministic route selection and optional workflow orchestration only. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 8 | 17 | GLOBAL NO-OVERLAP LAW |  | C0 owns retrieval/evidence contracts only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 9 | 18 | GLOBAL NO-OVERLAP LAW |  | PA owns prompt packet construction only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 10 | 19 | GLOBAL NO-OVERLAP LAW |  | 04 L2 owns bounded execution and sealing only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 11 | 20 | GLOBAL NO-OVERLAP LAW |  | 05 Exit owns current-run checkout aggregation and exactly one X3 disposition only. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 12 | 21 | GLOBAL NO-OVERLAP LAW |  | 06 L6 owns completed-run evaluation, RCA, and future-run learning proposals only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 13 | 22 | GLOBAL NO-OVERLAP LAW |  | 99 owns proof harnesses only; it does not own runtime behavior. | **PASS** | doctrine_xref, source_file, test_corpus |
| 14 | 25 | REFERENCE POINTERS |  | Cross-cutting governance/certification evidence: 00A_L5_Governance_Safety/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 15 | 26 | REFERENCE POINTERS |  | Durable state and Universal Write Gateway: 00B_L4_State_Archive_and_UWG/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 16 | 27 | REFERENCE POINTERS |  | Current-run reusable gate mesh: 00C_Runtime_Gates_Current_Run_Mesh/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 17 | 28 | REFERENCE POINTERS |  | Traceability and zero-loss proof: 00X_Requirements_Traceability_and_No_Loss_Map.md | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 18 | 29 | REFERENCE POINTERS |  | End-to-end runtime proof harness: 99_End_to_End_Runtime_Proof_and_Acceptance/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 19 | 45 | UNIQUE OWNERSHIP SURFACE |  | final signed prompt artifact emission only | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 20 | 48 | THIS FILE OWNS |  | CompiledPromptArtifact, manifest_hash, HMAC signature, artifact receipt, L2 handoff envelope | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 21 | 51 | THIS FILE DOES NOT OWN |  | provider dispatch, model/tool execution, output approval, durable writes, completed-run learning | **PASS** | doctrine_xref, source_file, test_corpus |
| 22 | 54 | GLOBAL NO-OVERLAP LOCK |  | L1 owns intent interpretation, task_spec, query_spec, ambiguity register, and planning recommendations. | **PASS** | doctrine_xref, source_file, test_corpus |
| 23 | 55 | GLOBAL NO-OVERLAP LOCK |  | L0 owns route selection, RouteContract, execution_form, provider lane, route risk, and route authority. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 24 | 56 | GLOBAL NO-OVERLAP LOCK |  | C0 owns retrieval, hydration, graph expansion, evidence shaping, verification, support scoring, and FinalEvidenceContract. | **PASS** | doctrine_xref, source_file, test_corpus |
| 25 | 57 | GLOBAL NO-OVERLAP LOCK |  | L5 owns policy, authority context, origin trust, egress, replay, audit, HITL re-clearance, and certification evidence. | **PASS** | doctrine_xref, source_file, test_corpus |
| 26 | 58 | GLOBAL NO-OVERLAP LOCK |  | Prompt Assembly owns only bounded prompt-packet composition and signed prompt artifact emission. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 27 | 59 | GLOBAL NO-OVERLAP LOCK |  | L2 owns bounded execution, SovereignLLMGateway dispatch, provider/model/tool calls, and sealed work artifacts. | **PASS** | doctrine_xref, source_file, test_corpus |
| 28 | 60 | GLOBAL NO-OVERLAP LOCK |  | Runtime Gates and Exit Eval own current-run dispositions. | **PASS** | doctrine_xref, source_file, test_corpus |
| 29 | 61 | GLOBAL NO-OVERLAP LOCK |  | UWG/L4 owns durable write admission and system-of-record mutation. | **PASS** | doctrine_xref, source_file, test_corpus |
| 30 | 62 | GLOBAL NO-OVERLAP LOCK |  | L6 owns completed-run evaluation, root-cause analysis, promotion proposals, and future-run learning. | **PASS** | doctrine_xref, source_file, test_corpus |
| 31 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ALLOW | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 32 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | DENY | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 33 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | CLARIFY | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 34 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ABSTAIN | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 35 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | REROUTE | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 36 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | SHRINK_SCOPE | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 37 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | RETRY | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 38 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | HEAL | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 39 | 65 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ESCALATE_HITL | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 40 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | QUARANTINE | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 41 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | REDACT | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 42 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | SAFE_FALLBACK | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 43 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | MARK_DEGRADED | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 44 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | COMMIT_REQUEST | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 45 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | BLOCK_COMMIT | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 46 | 66 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ALLOW_FINISH | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 47 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | approve_execution | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 48 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | approve_output | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 49 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | approve_write | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 50 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | call_provider | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 51 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | execute_tool | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 52 | 67 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | mutate_l4 | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 53 | 70 | ALLOWED OUTPUT STYLE |  | receipts, manifests, hashes, validation statuses, assembly statuses, gap reports, artifact refs, replay/audit refs | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 54 | 76 | END OVERWRITE RECONCILIATION HEADER | PARENT | Prompt_Assembly.md | **PASS** | doctrine_xref, source_file, test_corpus |
| 55 | 79 | END OVERWRITE RECONCILIATION HEADER | ROLE | Detailed child file for PA.7 FINAL EMIT / COMPILED PROMPT ARTIFACT. | **PASS** | doctrine_xref, source_file, test_corpus |
| 56 | 80 | END OVERWRITE RECONCILIATION HEADER | ROLE | Defines the implementation-grade requirements for its unique Prompt Assembly surface. | **PASS** | doctrine_xref, source_file, test_corpus |
| 57 | 81 | END OVERWRITE RECONCILIATION HEADER | ROLE | Emits Prompt Assembly evidence only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 58 | 82 | END OVERWRITE RECONCILIATION HEADER | ROLE | Does not emit runtime dispositions. | **PASS** | doctrine_xref, source_file, test_corpus |
| 59 | 83 | END OVERWRITE RECONCILIATION HEADER | ROLE | Does not retrieve, route, execute, call providers, write durable state, or promote learning. | **PASS** | doctrine_xref, source_file, test_corpus |
| 60 | 87 | WHY THIS FILE EXISTS |  | Prompt Assembly is a high-risk boundary because it binds rules, evidence, task text, schema, tools, provider metadata, | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 61 | 89 | WHY THIS FILE EXISTS |  | This child isolates one Prompt Assembly surface so the parent stays doctrinal and no other layer inherits prompt assembly | **PASS** | doctrine_xref, source_file, test_corpus |
| 62 | 91 | WHY THIS FILE EXISTS |  | This child is intentionally detailed enough for implementation, tests, traces, and replay evidence. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 63 | 95 | PRIMARY QUESTION |  | "final signed prompt artifact emission only?" | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 64 | 99 | SOURCE OWNERSHIP BOUNDARY |  | This file may emit assembly receipts, manifests, hashes, statuses, and gap reports for its unique surface. | **PASS** | doctrine_xref, source_file, test_corpus |
| 65 | 100 | SOURCE OWNERSHIP BOUNDARY |  | This file must not fetch missing data. | **PASS** | doctrine_xref, source_file, test_corpus |
| 66 | 101 | SOURCE OWNERSHIP BOUNDARY |  | This file must not modify RouteContract, PlanContract, FinalEvidenceContract, policy, registry, capability, sandbox, or L4 state. | **PASS** | doctrine_xref, source_file, test_corpus |
| 67 | 102 | SOURCE OWNERSHIP BOUNDARY |  | This file must not approve L2 execution. It only prepares evidence for L2 validation. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 68 | 104 | SOURCE OWNERSHIP BOUNDARY | CompiledPromptArtifact Schema | 1. CompiledPromptArtifact Schema | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 69 | 107 | SOURCE OWNERSHIP BOUNDARY | FIELDS | compiled_prompt_artifact_id | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file |
| 70 | 108 | SOURCE OWNERSHIP BOUNDARY | FIELDS | assembly_request_id | **PASS** | doctrine_xref, prose_keyword |
| 71 | 109 | SOURCE OWNERSHIP BOUNDARY | FIELDS | prompt_bom_id | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 72 | 110 | SOURCE OWNERSHIP BOUNDARY | FIELDS | structured_slots_id | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 73 | 111 | SOURCE OWNERSHIP BOUNDARY | FIELDS | render_manifest_id | **PASS** | doctrine_xref, prose_keyword |
| 74 | 112 | SOURCE OWNERSHIP BOUNDARY | FIELDS | request_id / run_id / trace_id / route_id / plan_id | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 75 | 113 | SOURCE OWNERSHIP BOUNDARY | FIELDS | step_id if workflow step | **PASS** | doctrine_xref, source_file, test_corpus |
| 76 | 114 | SOURCE OWNERSHIP BOUNDARY | FIELDS | provider_lane | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 77 | 115 | SOURCE OWNERSHIP BOUNDARY | FIELDS | symbolic_model_id | **PASS** | doctrine_xref, runtime_symbol, source_file |
| 78 | 116 | SOURCE OWNERSHIP BOUNDARY | FIELDS | resolved_model_id if known | **PASS** | doctrine_xref, source_file, test_corpus |
| 79 | 117 | SOURCE OWNERSHIP BOUNDARY | FIELDS | model_settings.temperature | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 80 | 118 | SOURCE OWNERSHIP BOUNDARY | FIELDS | model_settings.thinking_level | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 81 | 119 | SOURCE OWNERSHIP BOUNDARY | FIELDS | model_settings.max_output_tokens | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 82 | 120 | SOURCE OWNERSHIP BOUNDARY | FIELDS | model_settings.tool_choice if applicable | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 83 | 121 | SOURCE OWNERSHIP BOUNDARY | FIELDS | final_provider_payload_ref | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 84 | 122 | SOURCE OWNERSHIP BOUNDARY | FIELDS | structured_slots_used[] | **PASS** | doctrine_xref, prose_keyword |
| 85 | 123 | SOURCE OWNERSHIP BOUNDARY | FIELDS | allowed_tools_schema_ref via provider tools field | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 86 | 124 | SOURCE OWNERSHIP BOUNDARY | FIELDS | response_schema_ref via provider response_schema / response_format field | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 87 | 125 | SOURCE OWNERSHIP BOUNDARY | FIELDS | C0FinalEvidenceContract_ref if grounded | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 88 | 126 | SOURCE OWNERSHIP BOUNDARY | FIELDS | source_lineage_refs[] | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 89 | 127 | SOURCE OWNERSHIP BOUNDARY | FIELDS | security_pass_receipt_ref | **PASS** | doctrine_xref, receipt_key, source_file |
| 90 | 128 | SOURCE OWNERSHIP BOUNDARY | FIELDS | slot_validation_receipt_ref | **PASS** | doctrine_xref, prose_keyword |
| 91 | 129 | SOURCE OWNERSHIP BOUNDARY | FIELDS | token_budget_ledger_ref | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 92 | 130 | SOURCE OWNERSHIP BOUNDARY | FIELDS | deterministic_trimming_receipt_ref if trimming occurred | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file |
| 93 | 131 | SOURCE OWNERSHIP BOUNDARY | FIELDS | provider_render_manifest_ref | **PASS** | doctrine_xref, prose_keyword |
| 94 | 132 | SOURCE OWNERSHIP BOUNDARY | FIELDS | policy_hash | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 95 | 133 | SOURCE OWNERSHIP BOUNDARY | FIELDS | blueprint_hash | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 96 | 134 | SOURCE OWNERSHIP BOUNDARY | FIELDS | route_digest | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 97 | 135 | SOURCE OWNERSHIP BOUNDARY | FIELDS | replay_key | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 98 | 136 | SOURCE OWNERSHIP BOUNDARY | FIELDS | canonical_hash_input_manifest_ref | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file |
| 99 | 137 | SOURCE OWNERSHIP BOUNDARY | FIELDS | manifest_hash | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 100 | 138 | SOURCE OWNERSHIP BOUNDARY | FIELDS | hmac_sig | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 101 | 139 | SOURCE OWNERSHIP BOUNDARY | FIELDS | idempotency_nonce | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 102 | 140 | SOURCE OWNERSHIP BOUNDARY | FIELDS | created_at_run_clock_offset | **PASS** | doctrine_xref, prose_keyword |
| 103 | 141 | SOURCE OWNERSHIP BOUNDARY | FIELDS | artifact_status | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 104 | 142 | SOURCE OWNERSHIP BOUNDARY | Manifest Hash | 2. Manifest Hash | **PASS** | doctrine_xref, source_file, test_corpus |
| 105 | 145 | MUST INCLUDE |  | canonical structured slot bytes after PA.5 trimming. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 106 | 146 | MUST INCLUDE |  | provider lane and render-affecting metadata. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 107 | 147 | MUST INCLUDE |  | schema binding refs. | **PASS** | doctrine_xref, source_file, test_corpus |
| 108 | 148 | MUST INCLUDE |  | tool binding refs. | **PASS** | doctrine_xref, source_file, test_corpus |
| 109 | 149 | MUST INCLUDE |  | policy_hash. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 110 | 150 | MUST INCLUDE |  | blueprint_hash. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 111 | 151 | MUST INCLUDE |  | route_digest. | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 112 | 152 | MUST INCLUDE |  | replay_key when required. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 113 | 153 | MUST INCLUDE |  | C0 evidence contract ref when grounded. | **PASS** | doctrine_xref, source_file, test_corpus |
| 114 | 154 | MUST INCLUDE |  | security/validation receipt refs. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 115 | 157 | MUST EXCLUDE |  | idempotency nonce when designated non-deterministic by PA.5. | **PASS** | doctrine_xref, source_file, test_corpus |
| 116 | 158 | MUST EXCLUDE |  | wall-clock created_at unless normalized as run-clock offset. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 117 | 159 | MUST EXCLUDE |  | provider runtime response IDs. | **PASS** | doctrine_xref, source_file, test_corpus |
| 118 | 160 | MUST EXCLUDE |  | L2 execution receipts not yet created. | **PASS** | doctrine_xref, source_file, test_corpus |
| 119 | 161 | MUST EXCLUDE | HMAC Signature | 3. HMAC Signature | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 120 | 164 | MUST CHECK |  | signing secret / key ref is available through approved signing mechanism. | **PASS** | doctrine_xref, source_file, test_corpus |
| 121 | 165 | MUST CHECK |  | manifest_hash exists. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 122 | 166 | MUST CHECK |  | required metadata is included. | **PASS** | doctrine_xref, source_file, test_corpus |
| 123 | 167 | MUST CHECK |  | signature algorithm is declared. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 124 | 168 | MUST CHECK |  | signature is reproducible for same canonical inputs and same signing key. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 125 | 169 | MUST CHECK |  | artifact cannot be mutated without invalidating signature. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 126 | 172 | MUST CHECK | FIELDS | signature_algorithm = HMAC-SHA256 or approved equivalent. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 127 | 173 | MUST CHECK | FIELDS | signing_key_ref. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 128 | 174 | MUST CHECK | FIELDS | signed_fields[]. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 129 | 175 | MUST CHECK | FIELDS | hmac_sig. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 130 | 176 | MUST CHECK | FIELDS | signature_receipt. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 131 | 177 | MUST CHECK | L2 Handoff Envelope | 4. L2 Handoff Envelope | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 132 | 180 | MUST CHECK | FIELDS | l2_handoff_envelope_id | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file |
| 133 | 181 | MUST CHECK | FIELDS | compiled_prompt_artifact_ref | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 134 | 182 | MUST CHECK | FIELDS | route_id | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 135 | 183 | MUST CHECK | FIELDS | execution_form | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 136 | 184 | MUST CHECK | FIELDS | provider_lane | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 137 | 185 | MUST CHECK | FIELDS | model_settings_ref | **PASS** | doctrine_xref, prose_keyword |
| 138 | 186 | MUST CHECK | FIELDS | tool_schema_refs[] | **PASS** | doctrine_xref, prose_keyword, source_file |
| 139 | 187 | MUST CHECK | FIELDS | response_schema_ref | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 140 | 188 | MUST CHECK | FIELDS | capability_token_ref if already bound upstream | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 141 | 189 | MUST CHECK | FIELDS | sandbox_envelope_ref if already bound upstream | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 142 | 190 | MUST CHECK | FIELDS | policy_hash | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 143 | 191 | MUST CHECK | FIELDS | blueprint_hash | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 144 | 192 | MUST CHECK | FIELDS | replay_key | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 145 | 193 | MUST CHECK | FIELDS | prompt_hash / manifest_hash | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 146 | 194 | MUST CHECK | FIELDS | hmac_sig | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 147 | 195 | MUST CHECK | FIELDS | handoff_notes[] | **PASS** | doctrine_xref, prose_keyword |
| 148 | 198 | MUST NOT INCLUDE |  | direct provider client handle. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 149 | 199 | MUST NOT INCLUDE |  | raw secret material. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 150 | 200 | MUST NOT INCLUDE |  | authority invented by user/retrieved/tool/model/human text. | **PASS** | doctrine_xref, source_file, test_corpus |
| 151 | 201 | MUST NOT INCLUDE |  | durable write command. | **PASS** | doctrine_xref, source_file, test_corpus |
| 152 | 202 | MUST NOT INCLUDE |  | final output disposition. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 153 | 207 | STATUS VALUES |  | PA_ARTIFACT_SIGNED | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 154 | 208 | STATUS VALUES |  | PA_ARTIFACT_NOT_SIGNED | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 155 | 209 | STATUS VALUES |  | PA_SIGNATURE_GAP | **PASS** | doctrine_xref, prose_keyword, source_file, status_value, test_corpus |
| 156 | 210 | STATUS VALUES |  | PA_MANIFEST_HASH_GAP | **PASS** | doctrine_xref, prose_keyword, source_file, status_value, test_corpus |
| 157 | 211 | STATUS VALUES |  | PA_L2_HANDOFF_READY | **PASS** | doctrine_xref, prose_keyword, source_file, status_value, test_corpus |
| 158 | 212 | STATUS VALUES |  | PA_L2_HANDOFF_GAP | **PASS** | doctrine_xref, prose_keyword, source_file, status_value, test_corpus |
| 159 | 216 | MUST EMIT |  | CompiledPromptArtifact | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 160 | 217 | MUST EMIT |  | compiled_prompt_artifact_receipt | **PASS** | doctrine_xref, receipt_key, source_file |
| 161 | 218 | MUST EMIT |  | manifest_hash_receipt | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 162 | 219 | MUST EMIT |  | hmac_signature_receipt | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file |
| 163 | 220 | MUST EMIT |  | l2_handoff_envelope | **PASS** | doctrine_xref, prose_keyword, receipt_key, runtime_symbol, source_file, test_corpus |
| 164 | 221 | MUST EMIT |  | final_artifact_gap_report | **PASS** | doctrine_xref, receipt_key, source_file |
| 165 | 225 | MUST NOT |  | retrieve evidence | **PASS** | doctrine_xref, source_file, test_corpus |
| 166 | 226 | MUST NOT |  | route or reroute | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 167 | 227 | MUST NOT |  | call a model provider | **PASS** | doctrine_xref, source_file, test_corpus |
| 168 | 228 | MUST NOT |  | execute a tool | **PASS** | doctrine_xref, source_file, test_corpus |
| 169 | 229 | MUST NOT |  | approve the final answer | **PASS** | doctrine_xref, source_file, test_corpus |
| 170 | 230 | MUST NOT |  | commit durable state | **PASS** | doctrine_xref, source_file, test_corpus |
| 171 | 231 | MUST NOT |  | emit runtime dispositions | **PASS** | doctrine_xref, source_file, test_corpus |
| 172 | 232 | MUST NOT |  | silently drop mandatory evidence, authority, schema, or replay metadata | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 173 | 236 | ACCEPTANCE TESTS |  | No code path in this child retrieves evidence, routes, executes, calls providers, writes L4, or emits runtime disposition. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 174 | 237 | ACCEPTANCE TESTS |  | All emitted receipts preserve request_id, run_id, trace_id, route_id, policy_hash, and replay_key when available. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 175 | 238 | ACCEPTANCE TESTS |  | All gap conditions are explicit and replayable. | **PASS** | doctrine_xref, source_file, test_corpus |
| 176 | 239 | ACCEPTANCE TESTS |  | Same canonical inputs and signing key produce same manifest_hash and HMAC. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 177 | 240 | ACCEPTANCE TESTS |  | Changing C0 evidence ref changes manifest_hash. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 178 | 241 | ACCEPTANCE TESTS |  | Changing idempotency nonce alone does not change manifest_hash when excluded by PA.5. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 179 | 242 | ACCEPTANCE TESTS |  | Unsigned artifact cannot be marked PA_L2_HANDOFF_READY. | **PASS** | doctrine_xref, prose_keyword, source_file, status_value, test_corpus |
| 180 | 243 | ACCEPTANCE TESTS |  | L2 handoff envelope contains no provider client handle or raw secret. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |

## PA.8

| # | Line | Section | Sub-section | Requirement | Status | Evidence |
|---:|---:|---|---|---|:---:|---|
| 1 | 17 | GLOBAL NO-OVERLAP LOCK |  | U0 / Intake owns request envelope validation and request identity stamping. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 2 | 18 | GLOBAL NO-OVERLAP LOCK |  | L1 owns intent interpretation, task_spec, query_spec, ambiguity register, and plan recommendation. | **PASS** | doctrine_xref, source_file, test_corpus |
| 3 | 19 | GLOBAL NO-OVERLAP LOCK |  | L0 owns route selection and RouteContract authority. | **PASS** | doctrine_xref, source_file, test_corpus |
| 4 | 20 | GLOBAL NO-OVERLAP LOCK |  | L3 owns managed workflow shaping, readiness, checkpointing, and step handoff when the route is workflow-managed. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 5 | 21 | GLOBAL NO-OVERLAP LOCK |  | 03A C0 owns retrieval, evidence shaping, verification, support score, and FinalEvidenceContract. | **PASS** | doctrine_xref, source_file, test_corpus |
| 6 | 22 | GLOBAL NO-OVERLAP LOCK |  | 03B Prompt Assembly owns signed provider-ready PromptEnvelope / CompiledPromptArtifact construction. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 7 | 23 | GLOBAL NO-OVERLAP LOCK |  | L2 owns bounded execution of exactly one approved packet or current L3 step, including local validation, execution, repair, seal, and receipts. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 8 | 24 | GLOBAL NO-OVERLAP LOCK |  | 00C Runtime Gates own reusable current-run gate law, GateVerdict schema, live gate invocation map, and gate observability. | **PASS** | doctrine_xref, source_file, test_corpus |
| 9 | 25 | GLOBAL NO-OVERLAP LOCK |  | 05 Exit owns current-run checkout, aggregation, X3 disposition, HITL freeze/review flow, and CommitRequest handoff to UWG. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 10 | 26 | GLOBAL NO-OVERLAP LOCK |  | 00A L5 owns governance certification evidence and re-clearance evidence, not live dispositions. | **PASS** | doctrine_xref, source_file, test_corpus |
| 11 | 27 | GLOBAL NO-OVERLAP LOCK |  | 00B L4/UWG owns durable state and durable write admission. | **PASS** | doctrine_xref, source_file, test_corpus |
| 12 | 28 | GLOBAL NO-OVERLAP LOCK |  | 06 L6 owns completed-run evaluation, RCA, proposal drafting, gauntlet proof, and future-run learning attempts only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 13 | 29 | GLOBAL NO-OVERLAP LOCK |  | 99 owns end-to-end acceptance proof that the whole chain actually ran and respected boundaries. | **PASS** | doctrine_xref, source_file, test_corpus |
| 14 | 44 | THIS FILE OWNS |  | SlotAuthorityProof. | **PASS** | doctrine_xref, prose_keyword |
| 15 | 45 | THIS FILE OWNS |  | PromptInjectionFixtureSet for PA-local slot tests. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 16 | 46 | THIS FILE OWNS |  | ProviderRenderEquivalenceReceipt. | **PASS** | doctrine_xref, prose_keyword |
| 17 | 47 | THIS FILE OWNS |  | SchemaBindingProof for R0 provider-native schemas. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 18 | 48 | THIS FILE OWNS |  | PA no-retrieval/no-execution assertions. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 19 | 53 | CONTRACTS TO IMPLEMENT |  | proof_id | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 20 | 54 | CONTRACTS TO IMPLEMENT |  | prompt_bom_ref | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 21 | 55 | CONTRACTS TO IMPLEMENT |  | compiled_prompt_artifact_ref | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 22 | 56 | CONTRACTS TO IMPLEMENT |  | slot_order | **PASS** | doctrine_xref, prose_keyword, runtime_symbol, source_file, test_corpus |
| 23 | 57 | CONTRACTS TO IMPLEMENT |  | slot_hashes | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 24 | 58 | CONTRACTS TO IMPLEMENT |  | higher_authority_override_map | **PASS** | doctrine_xref, prose_keyword |
| 25 | 59 | CONTRACTS TO IMPLEMENT |  | lower_authority_override_attempts[] | **PASS** | doctrine_xref, prose_keyword |
| 26 | 60 | CONTRACTS TO IMPLEMENT |  | blocked_attempts[] | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 27 | 61 | CONTRACTS TO IMPLEMENT |  | provider_render_hash | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 28 | 62 | CONTRACTS TO IMPLEMENT |  | response_schema_binding_ref | **PASS** | doctrine_xref, prose_keyword |
| 29 | 63 | CONTRACTS TO IMPLEMENT |  | hmac_sig | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 30 | 64 | CONTRACTS TO IMPLEMENT |  | deterministic_digest | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 31 | 67 | CONTRACTS TO IMPLEMENT |  | fixture_id | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 32 | 68 | CONTRACTS TO IMPLEMENT |  | injected_slot = U0 \| C0 \| E0 \| H0 \| tool_output \| human_text | **PASS** | doctrine_xref, prose_keyword, source_file |
| 33 | 69 | CONTRACTS TO IMPLEMENT |  | injection_payload_ref | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 34 | 70 | CONTRACTS TO IMPLEMENT |  | expected_boundary = data_only \| quarantine \| redact \| reject_packet | **PASS** | doctrine_xref, forbidden_token, prose_keyword, source_file, test_corpus |
| 35 | 71 | CONTRACTS TO IMPLEMENT |  | expected_preserved_authority_order | **PASS** | doctrine_xref, prose_keyword |
| 36 | 72 | CONTRACTS TO IMPLEMENT |  | expected_no_instruction_promotion | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 37 | 76 | CONTRACTS TO IMPLEMENT |  | C0, tool output, and human text are data-only slots. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 38 | 77 | CONTRACTS TO IMPLEMENT |  | R0 schema is bound to provider-native schema fields where supported, not merely prose. | **PASS** | doctrine_xref, source_file, test_corpus |
| 39 | 78 | CONTRACTS TO IMPLEMENT |  | Provider rendering must not reorder authority slots silently. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 40 | 79 | CONTRACTS TO IMPLEMENT |  | Token trimming must never drop S0, D0, required policy refs, or R0 schema binding. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 41 | 83 | TEST REQUIREMENTS |  | test_pa_blocks_c0_instruction_promotion | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 42 | 84 | TEST REQUIREMENTS |  | test_pa_blocks_human_text_as_authority | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 43 | 85 | TEST REQUIREMENTS |  | test_pa_schema_bound_native_not_only_prose | **PASS** | doctrine_xref, runtime_symbol, source_file |
| 44 | 86 | TEST REQUIREMENTS |  | test_pa_provider_render_preserves_slot_order | **PASS** | doctrine_xref, prose_keyword |
| 45 | 87 | TEST REQUIREMENTS |  | test_pa_token_trim_preserves_required_authority_slots | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 46 | 88 | TEST REQUIREMENTS |  | test_pa_never_calls_retrieval_or_execution | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |

## PARENT

| # | Line | Section | Sub-section | Requirement | Status | Evidence |
|---:|---:|---|---|---|:---:|---|
| 1 | 10 | GLOBAL NO-OVERLAP LAW |  | 00A L5 owns governance certification evidence, not live runtime dispositions and not durable write admission. | **PASS** | doctrine_xref, source_file, test_corpus |
| 2 | 11 | GLOBAL NO-OVERLAP LAW |  | 00B L4/UWG owns durable system-of-record state and durable write admission, not planning, routing, retrieval, execution, Exit disposition, or L6 learning mechanics. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 3 | 12 | GLOBAL NO-OVERLAP LAW |  | 00C Runtime Gates owns G01-G29 current-run GateVerdict law, not final Exit X3 aggregation and not L5 certification evidence. | **PASS** | doctrine_xref, source_file, test_corpus |
| 4 | 13 | GLOBAL NO-OVERLAP LAW |  | 00X owns traceability and no-loss mapping only. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 5 | 14 | GLOBAL NO-OVERLAP LAW |  | 01 Intake owns request envelope validation and identity/session/tenant baseline only. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 6 | 15 | GLOBAL NO-OVERLAP LAW |  | 02 L1 owns advisory interpretation and planning only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 7 | 16 | GLOBAL NO-OVERLAP LAW |  | 03 L0/L3 owns deterministic route selection and optional workflow orchestration only. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 8 | 17 | GLOBAL NO-OVERLAP LAW |  | C0 owns retrieval/evidence contracts only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 9 | 18 | GLOBAL NO-OVERLAP LAW |  | PA owns prompt packet construction only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 10 | 19 | GLOBAL NO-OVERLAP LAW |  | 04 L2 owns bounded execution and sealing only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 11 | 20 | GLOBAL NO-OVERLAP LAW |  | 05 Exit owns current-run checkout aggregation and exactly one X3 disposition only. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 12 | 21 | GLOBAL NO-OVERLAP LAW |  | 06 L6 owns completed-run evaluation, RCA, and future-run learning proposals only. | **PASS** | doctrine_xref, source_file, test_corpus |
| 13 | 22 | GLOBAL NO-OVERLAP LAW |  | 99 owns proof harnesses only; it does not own runtime behavior. | **PASS** | doctrine_xref, source_file, test_corpus |
| 14 | 25 | REFERENCE POINTERS |  | Cross-cutting governance/certification evidence: 00A_L5_Governance_Safety/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 15 | 26 | REFERENCE POINTERS |  | Durable state and Universal Write Gateway: 00B_L4_State_Archive_and_UWG/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 16 | 27 | REFERENCE POINTERS |  | Current-run reusable gate mesh: 00C_Runtime_Gates_Current_Run_Mesh/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 17 | 28 | REFERENCE POINTERS |  | Traceability and zero-loss proof: 00X_Requirements_Traceability_and_No_Loss_Map.md | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 18 | 29 | REFERENCE POINTERS |  | End-to-end runtime proof harness: 99_End_to_End_Runtime_Proof_and_Acceptance/ | **PASS** | doctrine_xref, source_file, test_corpus |
| 19 | 49 | NO-OVERLAP FULL OVERWRITE |  | PA.0 Boundary Check | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 20 | 50 | NO-OVERLAP FULL OVERWRITE |  | PA.1 Load / Resolve Prompt BOM | **PASS** | doctrine_xref, source_file, test_corpus |
| 21 | 51 | NO-OVERLAP FULL OVERWRITE |  | PA.2 Slot Composition | **PASS** | doctrine_xref, source_file, test_corpus |
| 22 | 52 | NO-OVERLAP FULL OVERWRITE |  | PA.3 Airlock / Security Pass | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 23 | 53 | NO-OVERLAP FULL OVERWRITE |  | PA.4 Validate Slot Contract | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 24 | 54 | NO-OVERLAP FULL OVERWRITE |  | PA.5 Token Budget / Determinism | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 25 | 55 | NO-OVERLAP FULL OVERWRITE |  | PA.6 Provider-Aware Rendering | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 26 | 56 | NO-OVERLAP FULL OVERWRITE |  | PA.7 Final Emit / Compiled Prompt Artifact | **PASS** | doctrine_xref, source_file, test_corpus |
| 27 | 60 | PARENT ROLE |  | Define Prompt Assembly doctrine. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 28 | 61 | PARENT ROLE |  | Define Prompt Assembly-owned vocabulary. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 29 | 62 | PARENT ROLE |  | Define top-level input and output shape. | **PASS** | doctrine_xref, source_file, test_corpus |
| 30 | 63 | PARENT ROLE |  | Define the no-overlap law. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 31 | 64 | PARENT ROLE |  | Define child ownership map. | **PASS** | doctrine_xref, source_file, test_corpus |
| 32 | 65 | PARENT ROLE |  | Define cross-child invariants. | **PASS** | doctrine_xref, prose_keyword, runtime_symbol, source_file, test_corpus |
| 33 | 66 | PARENT ROLE |  | Define traceability expectations. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 34 | 67 | PARENT ROLE |  | Keep implementation-grade mechanics inside the child files. | **PASS** | doctrine_xref, source_file, test_corpus |
| 35 | 74 | GLOBAL NO-OVERLAP LOCK |  | L1 owns intent interpretation, task_spec, query_spec, ambiguity register, and planning recommendations. | **PASS** | doctrine_xref, source_file, test_corpus |
| 36 | 75 | GLOBAL NO-OVERLAP LOCK |  | L0 owns route selection, RouteContract, execution_form, provider lane, route risk, and route authority. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 37 | 76 | GLOBAL NO-OVERLAP LOCK |  | C0 owns retrieval, hydration, graph expansion, evidence shaping, verification, support scoring, and FinalEvidenceContract. | **PASS** | doctrine_xref, source_file, test_corpus |
| 38 | 77 | GLOBAL NO-OVERLAP LOCK |  | L5 owns policy, authority context, origin trust, egress, replay, audit, HITL re-clearance, and certification evidence. | **PASS** | doctrine_xref, source_file, test_corpus |
| 39 | 78 | GLOBAL NO-OVERLAP LOCK |  | Prompt Assembly owns only bounded prompt-packet composition and signed prompt artifact emission. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 40 | 79 | GLOBAL NO-OVERLAP LOCK |  | L2 owns bounded execution, SovereignLLMGateway dispatch, provider/model/tool calls, and sealed work artifacts. | **PASS** | doctrine_xref, source_file, test_corpus |
| 41 | 80 | GLOBAL NO-OVERLAP LOCK |  | Runtime Gates and Exit Eval own current-run dispositions. | **PASS** | doctrine_xref, source_file, test_corpus |
| 42 | 81 | GLOBAL NO-OVERLAP LOCK |  | UWG/L4 owns durable write admission and system-of-record mutation. | **PASS** | doctrine_xref, source_file, test_corpus |
| 43 | 82 | GLOBAL NO-OVERLAP LOCK |  | L6 owns completed-run evaluation, root-cause analysis, promotion proposals, and future-run learning. | **PASS** | doctrine_xref, source_file, test_corpus |
| 44 | 85 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ALLOW | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 45 | 85 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | DENY | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 46 | 85 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | CLARIFY | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 47 | 85 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ABSTAIN | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 48 | 85 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | REROUTE | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 49 | 85 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | SHRINK_SCOPE | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 50 | 85 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | RETRY | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 51 | 85 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | HEAL | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 52 | 85 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ESCALATE_HITL | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 53 | 86 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | QUARANTINE | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 54 | 86 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | REDACT | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 55 | 86 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | SAFE_FALLBACK | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 56 | 86 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | MARK_DEGRADED | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 57 | 86 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | COMMIT_REQUEST | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 58 | 86 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | BLOCK_COMMIT | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 59 | 86 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | ALLOW_FINISH | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 60 | 87 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | approve_execution | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 61 | 87 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | approve_output | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 62 | 87 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | approve_write | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 63 | 87 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | call_provider | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 64 | 87 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | execute_tool | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 65 | 87 | FORBIDDEN OUTPUTS FROM THIS CHILD |  | mutate_l4 | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 66 | 90 | ALLOWED OUTPUT STYLE |  | receipts, manifests, hashes, validation statuses, assembly statuses, gap reports, artifact refs, replay/audit refs | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 67 | 96 | PROMPT ASSEMBLY OWNS AT DOCTRINE LEVEL |  | PromptBOM vocabulary. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 68 | 97 | PROMPT ASSEMBLY OWNS AT DOCTRINE LEVEL |  | canonical slot vocabulary. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 69 | 98 | PROMPT ASSEMBLY OWNS AT DOCTRINE LEVEL |  | authority-tiered slot ordering doctrine. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 70 | 99 | PROMPT ASSEMBLY OWNS AT DOCTRINE LEVEL |  | assembly boundary law. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 71 | 100 | PROMPT ASSEMBLY OWNS AT DOCTRINE LEVEL |  | provider-ready artifact vocabulary. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 72 | 101 | PROMPT ASSEMBLY OWNS AT DOCTRINE LEVEL |  | signed CompiledPromptArtifact expectation. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 73 | 102 | PROMPT ASSEMBLY OWNS AT DOCTRINE LEVEL |  | manifest_hash / HMAC requirement at the prompt-artifact layer. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 74 | 103 | PROMPT ASSEMBLY OWNS AT DOCTRINE LEVEL |  | deterministic prompt packet discipline. | **PASS** | doctrine_xref, source_file, test_corpus |
| 75 | 106 | PROMPT ASSEMBLY DOES NOT OWN |  | request intake. | **PASS** | doctrine_xref, source_file, test_corpus |
| 76 | 107 | PROMPT ASSEMBLY DOES NOT OWN |  | intent interpretation. | **PASS** | doctrine_xref, source_file, test_corpus |
| 77 | 108 | PROMPT ASSEMBLY DOES NOT OWN |  | route authority. | **PASS** | doctrine_xref, source_file, test_corpus |
| 78 | 109 | PROMPT ASSEMBLY DOES NOT OWN |  | evidence retrieval or evidence scoring. | **PASS** | doctrine_xref, source_file, test_corpus |
| 79 | 110 | PROMPT ASSEMBLY DOES NOT OWN |  | graph traversal. | **PASS** | doctrine_xref, source_file |
| 80 | 111 | PROMPT ASSEMBLY DOES NOT OWN |  | runtime gate dispositions. | **PASS** | doctrine_xref, source_file, test_corpus |
| 81 | 112 | PROMPT ASSEMBLY DOES NOT OWN |  | model/tool execution. | **PASS** | doctrine_xref, source_file, test_corpus |
| 82 | 113 | PROMPT ASSEMBLY DOES NOT OWN |  | provider invocation. | **PASS** | doctrine_xref, source_file, test_corpus |
| 83 | 114 | PROMPT ASSEMBLY DOES NOT OWN |  | durable writes. | **PASS** | doctrine_xref, source_file, test_corpus |
| 84 | 115 | PROMPT ASSEMBLY DOES NOT OWN |  | L5 certification doctrine. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 85 | 116 | PROMPT ASSEMBLY DOES NOT OWN |  | completed-run learning. | **PASS** | doctrine_xref, source_file, test_corpus |
| 86 | 120 | CANONICAL PROMPT ASSEMBLY INPUTS | L1PlanContract reference: | 1. L1PlanContract reference: | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 87 | 121 | CANONICAL PROMPT ASSEMBLY INPUTS | L1PlanContract reference: | task_spec, query_spec, output target, support expectation, declared assumptions, unresolved gaps. | **PASS** | doctrine_xref, source_file, test_corpus |
| 88 | 123 | CANONICAL PROMPT ASSEMBLY INPUTS | L0RouteContract reference: | 2. L0RouteContract reference: | **PASS** | doctrine_xref, runtime_symbol, source_file, test_corpus |
| 89 | 124 | CANONICAL PROMPT ASSEMBLY INPUTS | L0RouteContract reference: | selected route, execution_form, provider lane, route risk, policy posture, cache/freshness posture, | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 90 | 127 | CANONICAL PROMPT ASSEMBLY INPUTS | C0 FinalEvidenceContract reference when grounding is required: | 3. C0 FinalEvidenceContract reference when grounding is required: | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 91 | 128 | CANONICAL PROMPT ASSEMBLY INPUTS | C0 FinalEvidenceContract reference when grounding is required: | verified chunks, cited spans, source_ids, lineage, support score, support gaps, contradiction flags, | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 92 | 131 | CANONICAL PROMPT ASSEMBLY INPUTS | Governance artifacts: | 4. Governance artifacts: | **PASS** | doctrine_xref, source_file, test_corpus |
| 93 | 132 | CANONICAL PROMPT ASSEMBLY INPUTS | Governance artifacts: | system_version_hash, policy_hash, role fences, allowed tool posture, AgentSpec, response schema contract, | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 94 | 135 | CANONICAL PROMPT ASSEMBLY INPUTS | User and execution metadata: | 5. User and execution metadata: | **PASS** | doctrine_xref, source_file, test_corpus |
| 95 | 136 | CANONICAL PROMPT ASSEMBLY INPUTS | User and execution metadata: | raw user task reference, neutralized user task candidate, plan_id, idempotency nonce, provider target, | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 96 | 142 | CANONICAL PROMPT ASSEMBLY OUTPUT |  | artifact_id | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 97 | 143 | CANONICAL PROMPT ASSEMBLY OUTPUT |  | request_id / run_id / trace_id / route_id / plan_id | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 98 | 144 | CANONICAL PROMPT ASSEMBLY OUTPUT |  | provider_lane / symbolic_model_id / resolved_model_id if known | **PASS** | doctrine_xref, prose_keyword, receipt_key, runtime_symbol, source_file, test_corpus |
| 99 | 145 | CANONICAL PROMPT ASSEMBLY OUTPUT |  | structured_slots_used | **PASS** | doctrine_xref, prose_keyword |
| 100 | 146 | CANONICAL PROMPT ASSEMBLY OUTPUT |  | provider_specific_messages or prompt fields | **PASS** | doctrine_xref, source_file, test_corpus |
| 101 | 147 | CANONICAL PROMPT ASSEMBLY OUTPUT |  | allowed_tools_schema reference via API tools field | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 102 | 148 | CANONICAL PROMPT ASSEMBLY OUTPUT |  | R0 response_schema binding via provider-native structured output field | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 103 | 149 | CANONICAL PROMPT ASSEMBLY OUTPUT |  | token estimate / budget status | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 104 | 150 | CANONICAL PROMPT ASSEMBLY OUTPUT |  | manifest_hash over canonical structured slot bytes | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 105 | 151 | CANONICAL PROMPT ASSEMBLY OUTPUT |  | hmac_sig over manifest_hash and required metadata | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 106 | 152 | CANONICAL PROMPT ASSEMBLY OUTPUT |  | replay_key / policy_hash / blueprint_hash / route digest refs | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 107 | 153 | CANONICAL PROMPT ASSEMBLY OUTPUT |  | source evidence refs and C0 FinalEvidenceContract ref when grounded | **PASS** | doctrine_xref, source_file, test_corpus |
| 108 | 154 | CANONICAL PROMPT ASSEMBLY OUTPUT |  | origin/security validation receipts | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 109 | 155 | CANONICAL PROMPT ASSEMBLY OUTPUT |  | slot validation receipt | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 110 | 156 | CANONICAL PROMPT ASSEMBLY OUTPUT |  | deterministic trimming receipt if trimming occurred | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 111 | 157 | CANONICAL PROMPT ASSEMBLY OUTPUT |  | render manifest and provider adapter receipt | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 112 | 162 | STATUS VOCABULARY |  | PA_READY | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 113 | 163 | STATUS VOCABULARY |  | PA_INPUT_INCOMPLETE | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 114 | 164 | STATUS VOCABULARY |  | PA_BOUNDARY_MISMATCH | **PASS** | doctrine_xref, prose_keyword, source_file, status_value, test_corpus |
| 115 | 165 | STATUS VOCABULARY |  | PA_BOM_RESOLVED | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 116 | 166 | STATUS VOCABULARY |  | PA_BOM_GAP | **PASS** | doctrine_xref, prose_keyword, source_file, status_value, test_corpus |
| 117 | 167 | STATUS VOCABULARY |  | PA_SLOTS_COMPOSED | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 118 | 168 | STATUS VOCABULARY |  | PA_SECURITY_PASS | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 119 | 169 | STATUS VOCABULARY |  | PA_SECURITY_GAP | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 120 | 170 | STATUS VOCABULARY |  | PA_SLOT_CONTRACT_VALID | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 121 | 171 | STATUS VOCABULARY |  | PA_SLOT_CONTRACT_INVALID | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 122 | 172 | STATUS VOCABULARY |  | PA_BUDGET_FIT | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 123 | 173 | STATUS VOCABULARY |  | PA_BUDGET_TRIMMED | **PASS** | doctrine_xref, prose_keyword, source_file, status_value, test_corpus |
| 124 | 174 | STATUS VOCABULARY |  | PA_BUDGET_OVERFLOW | **PASS** | doctrine_xref, prose_keyword, source_file, status_value, test_corpus |
| 125 | 175 | STATUS VOCABULARY |  | PA_RENDERED | **PASS** | doctrine_xref, prose_keyword, source_file, status_value, test_corpus |
| 126 | 176 | STATUS VOCABULARY |  | PA_RENDER_GAP | **PASS** | doctrine_xref, prose_keyword, source_file, status_value, test_corpus |
| 127 | 177 | STATUS VOCABULARY |  | PA_ARTIFACT_SIGNED | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 128 | 178 | STATUS VOCABULARY |  | PA_ARTIFACT_NOT_SIGNED | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 129 | 179 | STATUS VOCABULARY |  | PA_L2_HANDOFF_READY | **PASS** | doctrine_xref, prose_keyword, source_file, status_value, test_corpus |
| 130 | 180 | STATUS VOCABULARY |  | PA_REQUIRES_UPSTREAM_REPAIR | **PASS** | doctrine_xref, source_file, status_value, test_corpus |
| 131 | 183 | STATUS VOCABULARY |  | runtime dispositions such as ALLOW, DENY, REROUTE, ESCALATE_HITL, COMMIT_REQUEST, BLOCK_COMMIT, ALLOW_FINISH. | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 132 | 184 | STATUS VOCABULARY |  | execution verbs such as call_provider, execute_tool, approve_output, approve_write, mutate_l4. | **PASS** | doctrine_xref, forbidden_token, source_file, test_corpus |
| 133 | 206 | AUTHORITY ORDER | S0 system/state | 1. S0 system/state | **PASS** | doctrine_xref, source_file, test_corpus |
| 134 | 207 | AUTHORITY ORDER | D0 fences/injections | 2. D0 fences/injections | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 135 | 208 | AUTHORITY ORDER | I0 instructional | 3. I0 instructional | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 136 | 209 | AUTHORITY ORDER | E0 exemplars | 4. E0 exemplars | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 137 | 210 | AUTHORITY ORDER | C0 grounded context as data | 5. C0 grounded context as data | **PASS** | doctrine_xref, source_file, test_corpus |
| 138 | 211 | AUTHORITY ORDER | M0 private controls | 6. M0 private controls | **PASS** | doctrine_xref, source_file, test_corpus |
| 139 | 212 | AUTHORITY ORDER | U0 user task intent | 7. U0 user task intent | **PASS** | doctrine_xref, source_file, test_corpus |
| 140 | 213 | AUTHORITY ORDER | Y0 approved analytic priors if included | 8. Y0 approved analytic priors if included | **PASS** | doctrine_xref, source_file, test_corpus |
| 141 | 214 | AUTHORITY ORDER | H0 repair proposal if included | 9. H0 repair proposal if included | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 142 | 215 | AUTHORITY ORDER | R0 output schema bound out-of-band through provider-native structured-output field | 10. R0 output schema bound out-of-band through provider-native structured-output field | **PASS** | doctrine_xref, source_file, test_corpus |
| 143 | 218 | AUTHORITY ORDER | R0 output schema bound out-of-band through provider-native structured-output field | R0 is binding schema, but should be bound through API response_schema / response_format where available. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 144 | 219 | AUTHORITY ORDER | R0 output schema bound out-of-band through provider-native structured-output field | Tools are bound through provider API tool fields, not stringified as loose prompt prose. | **PASS** | doctrine_xref, source_file, test_corpus |
| 145 | 220 | AUTHORITY ORDER | R0 output schema bound out-of-band through provider-native structured-output field | Lower-authority slots may inform content or format only within higher-authority limits. | **PASS** | doctrine_xref, source_file, test_corpus |
| 146 | 221 | AUTHORITY ORDER | R0 output schema bound out-of-band through provider-native structured-output field | Lower-authority slots cannot override higher-authority slots. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 147 | 226 | CHILD FILE MAP |  | Unique surface: assembly eligibility and input completeness. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 148 | 227 | CHILD FILE MAP |  | Owns PAAssemblyInput, boundary checklist, source-of-truth refs, missing-input gap report. | **PASS** | doctrine_xref, prose_keyword, runtime_symbol, source_file, test_corpus |
| 149 | 230 | CHILD FILE MAP |  | Unique surface: PromptBOM resolution. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 150 | 231 | CHILD FILE MAP |  | Owns component refs, selected system/fence/instruction/exemplar/context/schema/execution metadata inventory. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 151 | 234 | CHILD FILE MAP |  | Unique surface: canonical slot construction and authority-tier ordering. | **PASS** | doctrine_xref, source_file, test_corpus |
| 152 | 235 | CHILD FILE MAP |  | Owns StructuredPromptSlots, slot authority map, override-prevention map, slot lineage map. | **PASS** | doctrine_xref, prose_keyword, runtime_symbol, source_file, test_corpus |
| 153 | 238 | CHILD FILE MAP |  | Unique surface: assembly-time security pass. | **PASS** | doctrine_xref, source_file, test_corpus |
| 154 | 239 | CHILD FILE MAP |  | Owns U0 airlock, C0 payload classifier, H0 re-entry validation, safe slot payload map. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 155 | 242 | CHILD FILE MAP |  | Unique surface: final slot contract validation before budgeting/rendering. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 156 | 243 | CHILD FILE MAP |  | Owns authority-order validation, context contract validation, schema/tool binding validation. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 157 | 246 | CHILD FILE MAP |  | Unique surface: token budgeting and deterministic prompt-packet shaping. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 158 | 247 | CHILD FILE MAP |  | Owns token budget ledger, deterministic trimming plan, stable prefix rules, canonical hash input discipline. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 159 | 250 | CHILD FILE MAP |  | Unique surface: provider-specific rendering. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 160 | 251 | CHILD FILE MAP |  | Owns ProviderRenderManifest, adapter mapping, provider field placement, render gap reports. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 161 | 254 | CHILD FILE MAP |  | Unique surface: final signed prompt artifact emission. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 162 | 255 | CHILD FILE MAP |  | Owns CompiledPromptArtifact, manifest_hash, HMAC signature, artifact receipt, L2 handoff envelope. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 163 | 288 | ACCEPTANCE EXPECTATIONS |  | Prompt Assembly refuses to run without required L1/L0 refs. | **PASS** | doctrine_xref, source_file, test_corpus |
| 164 | 289 | ACCEPTANCE EXPECTATIONS |  | Grounded routes require a valid C0 FinalEvidenceContract. | **PASS** | doctrine_xref, source_file, test_corpus |
| 165 | 290 | ACCEPTANCE EXPECTATIONS |  | Slots are built in canonical authority order. | **PASS** | doctrine_xref, source_file, test_corpus |
| 166 | 291 | ACCEPTANCE EXPECTATIONS |  | User and retrieved text cannot override higher-authority slots. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 167 | 292 | ACCEPTANCE EXPECTATIONS |  | Tool schemas and response schemas are provider-native bindings, not loose prompt prose. | **PASS** | doctrine_xref, source_file, test_corpus |
| 168 | 293 | ACCEPTANCE EXPECTATIONS |  | Token overflow emits a deterministic gap status rather than silently dropping mandatory content. | **PASS** | doctrine_xref, prose_keyword, receipt_key, source_file, test_corpus |
| 169 | 294 | ACCEPTANCE EXPECTATIONS |  | Provider rendering preserves canonical manifest hash independence. | **PASS** | doctrine_xref, prose_keyword, source_file, test_corpus |
| 170 | 295 | ACCEPTANCE EXPECTATIONS |  | Final artifact is signed and replay-bound. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
| 171 | 296 | ACCEPTANCE EXPECTATIONS |  | No Prompt Assembly code path retrieves, routes, executes, calls providers, writes L4, or decides final disposition. | **PASS** | doctrine_xref, receipt_key, source_file, test_corpus |
