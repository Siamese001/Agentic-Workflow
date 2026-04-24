# ADR-039 — Output-Contract Validator at §5

- **Status:** Proposed
- **Date:** 2026-04-23
- **Deciders:** Safety Officer (L5), Architecture, Eval Lab
- **Impact Layers:** Ingress (E3), L5, §5 exit
- **Relates to:** ADR-036 (trace-grader), ADR-038 (budget envelope)

## 1. Context

v33 §5 bullet "Answered the request in the required form" is prose-only. There is
no structured step that validates the final artifact against the output contract
declared at ingress (JSON schema, markdown section list, tool-result envelope,
proposal template, etc.). OpenAI and Google both treat this as a named grader.

## 2. Decision

Add an **Output-Contract Validator** step at §5, fed by:

- the **declared output contract** (stamped at ingress E3 alongside the budget
  envelope — may be `null` when no contract applies), AND
- the **sealed final artifact** (from L2 or [RET]).

### 2.1 Contract-kind registry

| kind | validator |
|---|---|
| `json_schema` | JSON Schema 2020-12 validation on the artifact payload |
| `markdown_sections` | presence/order of required headings |
| `tool_result_envelope` | L2 ToolResult shape (success, payload, reason, schema_version) |
| `proposal_template` | app-level template (RFP / LIC / RG domain-specific) |
| `text_constraints` | length caps, regex denylist, language, etc. |
| `none` | no contract — validator emits `required_form_satisfied = true` trivially |

A request may declare **zero or one** contract. Multi-contract composition is
out of scope.

### 2.2 Output shape

Populates `ExitDecision.output_contract`:

```
{
  "required_form_satisfied": bool,
  "contract_ref":            string | null,
  "violations":              [string, ...]   # human-readable, ordered
}
```

### 2.3 Disposition coupling

- `required_form_satisfied == false` AND contract was declared →
  `reason_code = grader.output_contract_fail`. Default disposition depends on
  severity:
  - **Schema-level mismatch** (JSON-Schema, tool_result_envelope) →
    `deny_reroute` (agent must retry).
  - **Soft mismatch** (missing optional section, exceeds length cap) →
    `allow_finish` with `quality.verdict = warn`.
- `contract == none` → field always `true`; cannot block disposition.

### 2.4 Relationship to trace-grader

- ADR-036 trace-grader emits narrative instruction-adherence scores.
- This validator emits **deterministic** boolean + violation list.
- Both feed `ExitDecision`; on conflict (validator says true, grader says
  instruction_violation), the escalation path is taken (safety first).

## 3. Consequences

- **Positive:** §5 "required form" bullet becomes machine-checkable. Tight
  contract with UWG (a contract-failing artifact is never committed).
- **Negative:** ingress now owns one more stamp (the contract).
- **Risk:** contract drift between declaration and validator. Mitigated by
  shipping the contract reference (not inline payload) and resolving it against
  a versioned registry.

## 4. Alternatives Considered

- **Delegate to trace-grader.** Rejected — non-deterministic for what should be
  a crisp schema check.
- **Delegate to UWG.** Rejected — UWG is write-authority, not quality gate;
  also doesn't apply when disposition is `allow_finish` (no commit path).

## 5. Open Items

- Code execution plan: validator module + ingress stamp wiring.
- Contract registry schema + storage (likely under `config/contracts/`).
- CI gate: declared contract refs must resolve.
