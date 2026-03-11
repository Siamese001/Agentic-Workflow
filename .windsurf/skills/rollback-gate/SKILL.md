---
name: rollback-gate
description: Enforces explicit rollback checkpoints before every multi-file phase and blocks partial commits when phase validation fails. Use before starting any phase touching more than 3 files, before any refactor that spans multiple modules, and after phase execution when validation fails. Prevents the repository from being left in a broken intermediate state.
enforcement_layer: both
enforcement_timing: before_work
enforcement_type: behavioural_primary_structural_secondary
---

# Rollback Gate Skill

Enforces checkpoint discipline before multi-file phases and automatic rollback on validation failure.

## Files

- **`pre_phase_checkpoint.md`** — Mandatory checkpoint protocol before any phase begins. Records baseline commit hash, declares rollback command, and defines phase acceptance criteria that must pass before the phase can be committed.

- **`rollback_protocol.md`** — Exact steps to execute when phase validation fails. Covers git reset, scope verification after reset, evidence documentation of failure, and STOP before proceeding to next phase.

## When to use

- Before ANY phase touching more than 3 files
- Before any refactor spanning multiple modules or layers
- Before any import path migration affecting >1 consumer
- Immediately when post-phase validation fails (automatic trigger)
- When a phase plan has no explicit rollback command documented

## Checkpoint Protocol (MANDATORY)

Before every phase:
1. Record baseline: `git rev-parse HEAD` → store as `BASELINE_HASH`
2. Declare rollback command: `git reset --hard <BASELINE_HASH>`
3. Declare acceptance criteria (what must pass for phase to be committed)
4. Document both in evidence BEFORE executing any edits

After every phase:
1. Run acceptance criteria
2. If ALL pass → commit
3. If ANY fail → execute rollback immediately, no partial commit

## Hard Rules

- **NO partial commits.** A phase either passes fully or is fully rolled back.
- **NO "we'll fix it in the next phase."** Fix now or roll back.
- Rollback command MUST be documented BEFORE phase starts (not after failure).

## MANDATORY PRE-CONDITION (Constitutional — no bypass)

**BEFORE starting any phase that modifies >3 files:**

1. **Execute**: `git rev-parse HEAD`
2. **Record output**: Store as `BASELINE_HASH` in evidence
3. **Declare rollback command**: `git reset --hard <BASELINE_HASH>`
4. **Define acceptance criteria**: List specific tests/checks that must pass for phase to be committed
5. **Write to**: Evidence section titled `## ROLLBACK_CHECKPOINT`

**Format required**:
```
## ROLLBACK_CHECKPOINT
Baseline: <git_hash>
Rollback command: git reset --hard <git_hash>
Acceptance criteria:
  - pytest <scoped_tests> passes
  - No new layer violations
  - Scope matches declaration
Phase: <phase_name>
Files to modify: N
```

**IF any step fails → STOP. Do not start the phase.**

After phase execution:
1. Run ALL acceptance criteria
2. If ALL pass → commit
3. If ANY fail → execute rollback command immediately
4. NO partial commits allowed

## Constitutional Requirements Enforced

- **§2.1:** Evidence MUST contain baseline hash and rollback command
- **§3.1:** Scope contamination detected → rollback mandatory
- **§1.2:** Tests MUST pass before commit (rollback if they don't)
