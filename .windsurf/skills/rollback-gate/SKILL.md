---
name: rollback-gate
description: Enforces explicit rollback checkpoints before every multi-file phase and blocks partial commits when phase validation fails. Use before starting any phase touching more than 3 files, before any refactor that spans multiple modules, and after phase execution when validation fails. Prevents the repository from being left in a broken intermediate state.
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

## Constitutional Requirements Enforced

- **§2.1:** Evidence MUST contain baseline hash and rollback command
- **§3.1:** Scope contamination detected → rollback mandatory
- **§1.2:** Tests MUST pass before commit (rollback if they don't)
