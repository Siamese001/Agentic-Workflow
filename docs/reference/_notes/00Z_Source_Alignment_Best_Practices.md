========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical folder: 00Z_Source_Alignment_Best_Practices
Canonical file: 00Z_Source_Alignment_Best_Practices.md
Overwrite mode: full-file, no-overlap, implementation-grade, source-refreshed
Owner summary: External best-practice alignment notes from OpenAI, Google, and Anthropic. Owns source-derived deltas only, not runtime requirements.

GLOBAL NO-OVERLAP LAW
- 00A L5 owns governance certification evidence, not live runtime dispositions and not durable write admission.
- 00B L4/UWG owns durable system-of-record state and durable write admission, not planning, routing, retrieval, execution, Exit disposition, or L6 learning mechanics.
- 00C Runtime Gates owns G01-G29 current-run GateVerdict law, not final Exit X3 aggregation and not L5 certification evidence.
- 00X owns traceability and no-loss mapping only.
- 01 Intake owns request envelope validation and identity/session/tenant baseline only.
- 02 L1 owns advisory interpretation and planning only.
- 03 L0/L3 owns deterministic route selection and optional workflow orchestration only.
- C0 owns retrieval/evidence contracts only.
- PA owns prompt packet construction only.
- 04 L2 owns bounded execution and sealing only.
- 05 Exit owns current-run checkout aggregation and exactly one X3 disposition only.
- 06 L6 owns completed-run evaluation, RCA, and future-run learning proposals only.
- 99 owns proof harnesses only; it does not own runtime behavior.

REFERENCE POINTERS
- Cross-cutting governance/certification evidence: 00A_L5_Governance_Safety/
- Durable state and Universal Write Gateway: 00B_L4_State_Archive_and_UWG/
- Current-run reusable gate mesh: 00C_Runtime_Gates_Current_Run_Mesh/
- Traceability and zero-loss proof: 00X_Requirements_Traceability_and_No_Loss_Map.md
- End-to-end runtime proof harness: 99_End_to_End_Runtime_Proof_and_Acceptance/
========================================================================================================================

# 00Z Source Alignment and Best-Practice Shift Notes

## OpenAI alignment
- Guardrails split by workflow boundary into input, output, and tool guardrails.
- Tracing must capture agent runs, LLM generations, tool calls, handoffs, guardrails, and custom events.
- Structured outputs should use schema-bound provider mechanisms rather than prose-only format instructions.

## Google alignment
- Agent evaluation should include final response evaluation and trajectory/tool-use evaluation.
- Tracing is modeled as a request trace with individual operation spans.
- Callbacks provide hook points to observe, customize, and control execution at defined points.

## Anthropic alignment
- Prefer deterministic workflow first, single agent next, and multi-agent only when complexity earns it.
- Tool definitions need clear parameters, examples, edge cases, and misuse-resistant shapes.
- Security guidance favors read-only defaults, explicit approval for side-effecting actions, and care around untrusted content/MCP servers.

## Applied shifts
- 00C owns G01-G29 GateVerdict law; 05 owns X1/X2/X3 checkout and final disposition.
- 00B owns durable state and UWG; no layer writes L4 directly.
- 00A owns certification evidence; Runtime Gates and Exit own live outcomes.
- C0 and PA are sibling runtime surfaces, not subfolders owned by 03.
- 99 owns proof that every layer ran, emitted contracts, traced spans, replayed deterministically, and respected no-bypass constraints.
