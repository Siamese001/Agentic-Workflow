---
name: operational-gates
description: Use this skill when executing destructive, state-changing, migration, deletion, or multi-file operations that need an explicit recovery point, validated tool contract, bounded phase gate, or failure-recovery procedure.
metadata:
  owner: platform-team
  version: "2.0"
---

# Operational gates

Use this procedure for operations where a partial result would be costly or hard to reverse. Ordinary
read-only analysis and small edits do not need checkpoint ceremony.

## Pre-operation gate

1. Confirm the exact files, remote resources, and side effects in scope.
2. Verify the working state and establish a recoverable baseline. Prefer a clean branch, commit, or
   isolated worktree over copying every file by hand.
3. Record the intended recovery command and the condition that triggers it. Read
   [rollback_checkpoint_protocol.md](rollback_checkpoint_protocol.md) for non-Git state.
4. Inspect the current tool schema or official documentation. Validate required names, types, ranges,
   and authorization before invoking a write operation.
5. Identify focused validation and a stop condition for the phase.
6. Execute one bounded phase, validate it, then continue.

Use [phase_gate_validation.md](phase_gate_validation.md) for multi-phase migrations.

## Tool-contract validation

Validate a tool without mutating production state merely to prove its parameters. Use schema discovery,
read-only health calls, dry-run support, or a disposable fixture when the tool provides one.

Check:

- The tool exists in the currently exposed namespace.
- Required arguments are present and correctly typed.
- Optional defaults are understood.
- No undocumented arguments are supplied.
- The caller has the minimum required authority.
- Timeout, retry, idempotency, and duplicate-execution behavior are known.

Read [mcp_tool_validation_checklist.md](mcp_tool_validation_checklist.md) for MCP-specific calls.

## Recovery

When a gate or validation step fails:

1. Stop further mutation.
2. Preserve the failure output and current state.
3. Execute the declared rollback or compensating action.
4. Verify restoration before retrying.
5. Correct the root cause; do not repeat the same operation unchanged.

Use [recovery_procedures.md](recovery_procedures.md) for partial downstream failures and
[gate_evidence_template.md](gate_evidence_template.md) for formal evidence.

## Validation

```bash
git status --short
python ops_scripts/ci/run_contract_gates.py
```

The final report must name the baseline, mutations performed, validation result, and usable rollback or
repair path.
