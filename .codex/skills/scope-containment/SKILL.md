---
name: scope-containment
description: Use this skill when a task risks silent scope expansion, crosses topics or modules, requires bounded retrieval, or needs a clear distinction between files that may be read and files that may be changed.
metadata:
  owner: platform-team
  version: "2.0"
---

# Scope containment

Use this procedure to keep investigation broad enough to establish evidence while keeping edits limited
to the approved outcome. The always-on scope rule remains authoritative.

## Workflow

1. Restate the requested outcome and the exact change surface already approved.
2. Separate files into:
   - **edit scope**: explicitly named, approved by the plan, or required for build/test correctness;
   - **read-only evidence**: consulted to understand dependencies or behavior;
   - **deferred**: relevant improvements that are not required for the requested outcome.
3. Use exact reads and structural queries before broad retrieval.
4. State any transitive file that must enter edit scope and why before changing it.
5. After each edit batch, compare the diff with the declared scope.
6. Report deferred work once without turning it into an unrequested implementation wave.

## Retrieval discipline

- Use ADG for dependencies, consumers, layers, and blast radius.
- Use literal search for comments, TODOs, and exact strings.
- Retain paths and evidence summaries; discard large retrieval chunks after extracting what is needed.
- Stop broadening retrieval when results converge or the decision is supported.

## Topic changes

When the user changes the objective, explicitly drop stale assumptions and establish the new scope in
plain language. Do not rely on custom marker syntax as the only indication of a scope reset.

## Validation

```bash
git diff --name-only
```

Every changed file must have a direct outcome, build, test, or graph-backed reason for being in scope.

## References

- Always-on rule: `.codex/rules/scope-containment.md`
- Structural scope: `.codex/skills/graph-analysis/SKILL.md`
- Destructive phases: `.codex/skills/operational-gates/SKILL.md`
