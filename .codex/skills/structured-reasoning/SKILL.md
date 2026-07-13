---
name: structured-reasoning
description: Use this skill when decomposing a multi-file, architectural, ambiguous, or failure-prone task into evidence, decision, execution, and verification phases inside the repository's approved plan-first workflow.
metadata:
  owner: platform-team
  version: "2.0"
---

# Structured reasoning

Use this skill as decomposition and retrieval guidance. The always-on requirement to plan before T2/T3
edits lives in `AGENTS.md` and repository rules, not in skill activation.

## Phase separation

| Phase | Purpose | Permitted work |
|---|---|---|
| Evidence | Establish current facts, constraints, and blast radius | Read-only retrieval and health checks |
| Decision | Compare viable approaches and resolve material uncertainty | Reasoning and one focused user choice when needed |
| Execution | Apply the approved, bounded change | Edits and state-changing tools |
| Verification | Prove behavior and inspect residual risk | Tests, gates, diff, and receipts |

Do not collapse all four phases into one opaque action.

## Workflow

1. Normalize the objective, constraints, assumptions, tier, and stop conditions.
2. Retrieve local instructions and exact named files before broad search.
3. Use structural tools for dependency questions, semantic tools for similarity, and external research
   only when local evidence or freshness requires it.
4. Identify branches in the plan and state the evidence that selects each branch.
5. Resolve material ambiguity from evidence. When a user decision is still necessary, use the native
   structured-input tool if available; otherwise ask one concise plain-text question.
6. Execute the approved steps in order, validating each bounded phase.
7. Revise the remaining plan when evidence or an execution result invalidates an assumption.
8. Close with changed files, validation evidence, unresolved items, and rollback or repair guidance.

Read [plan-template.md](plan-template.md) when a written T2/T3 plan is needed and
[checklist.md](checklist.md) before execution.

## Retrieval order

1. `AGENTS.md`, project memory, applicable rules, and directly named files.
2. Exact path, symbol, command, or artifact lookup.
3. Structured dependency, test, memory, or telemetry retrieval.
4. Semantic search when exact retrieval leaves a real gap.
5. Current external research when the answer depends on changing or upstream information.

Separate retrieval from synthesis on evidence-heavy work. Keep only the paths, facts, and citations
needed for the next decision.

## Failure handling

- Do not retry a failed transport in an unbounded loop.
- Do not replace structural evidence with intuition or literal grep.
- Do not carry an invalidated assumption into later phases.
- Stop before mutation when the plan lacks a safe decision or recoverable boundary.
- Use [failure-template.md](failure-template.md) for a failed phase and
  [verification-template.md](verification-template.md) for closeout.

## Validation

```bash
python ops_scripts/ci/run_skill_contract_gates.py
```

Also run every domain-specific check named in the approved plan.
