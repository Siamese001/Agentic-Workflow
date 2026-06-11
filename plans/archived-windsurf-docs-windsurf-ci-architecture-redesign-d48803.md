---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\windsurf-ci-architecture-redesign-d48803.md'
original_relative_path: 'windsurf-ci-architecture-redesign-d48803.md'
source_sha256: 1d4fa6bcc4fd2e04bdb6250edb275529e60a0173150ab102f01157b51751bd91
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-11'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Windsurf Rules + CI Gates: Two-Layer Enforcement Architecture

Redesign the enforcement architecture to give every rule exactly one home — Windsurf skills for AI-time guidance, pre-commit CI gates for structural/observable facts — eliminating misplaced gates, closing the timing gap, and publishing a clear responsibility contract.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## The Core Problem

```
CURRENT STATE (broken)
─────────────────────
Windsurf skills   →  "guidance" (soft, AI reads at start of session)
Pre-commit gates  →  mix of good gates + misfits that run too late

EXAMPLE MISFIT: check_ast_first_gate.py
  Runs at commit time → refactoring is already done
  Cannot reverse bad decisions already made
  Gives false sense of enforcement
```

---

## Responsibility Contract (North Star)

```
┌─────────────────────────────────────────────────────────────────┐
│  WINDSURF RULES  (AI-time, BEFORE any work)                    │
│  Responsibility: BEHAVIOURAL rules — HOW the AI must work      │
│  ─────────────────────────────────────────────────────────────  │
│  ✅ AST-first gate (builds graph BEFORE first edit)            │
│  ✅ Scope guard (declares scope BEFORE first edit)             │
│  ✅ Rollback gate (records checkpoint BEFORE phase starts)     │
│  ✅ Dedup guard (searches BEFORE creating new symbol)          │
│  ✅ ADG repair discipline (protocol DURING repair loop)        │
│  ✅ Script sprawl guard (decision BEFORE creating file)        │
│  ✅ Shim discipline (protocol BEFORE module move)              │
│  These CANNOT be checked at commit — they are process rules    │
└─────────────────────────────────────────────────────────────────┘
                         ↓ work happens ↓
┌─────────────────────────────────────────────────────────────────┐
│  PRE-COMMIT CI GATES  (commit-time, AFTER work is done)        │
│  Responsibility: STRUCTURAL rules — WHAT ended up in code      │
│  ─────────────────────────────────────────────────────────────  │
│  ✅ Import hygiene (dead/forbidden imports — observable)       │
│  ✅ Layer boundary violations (GV edges — observable)          │
│  ✅ Plan location (file path — observable)                     │
│  ✅ Pytest skip in UNIT_STRICT (marker in code — observable)   │
│  ✅ Anti-pattern landmines (code patterns — observable)        │
│  ✅ Script sprawl (new file in tools/ — observable)            │
│  ✅ Shim compliance (shim file has deprecation warning — obs.) │
│  ✅ Module collision (duplicate module paths — observable)     │
│  ✅ Dedup (new Agent class added — observable as proxy)        │
│  ✅ Rollback artifacts (checkpoint file present — observable)  │
│  These are NOT process rules — they check RESULTS only         │
└─────────────────────────────────────────────────────────────────┘
```

---

## What Changes

### Phase 1 — Remove Misfits from Pre-Commit

**Remove `check_ast_first_gate.py` from pre-commit** (it's a pure process rule — unobservable at commit time).

**Re-home it**: strengthen the `ast-first-gate` Windsurf skill with a mandatory `DEPENDENCY_GRAPH` section that the skill enforces as a blocker before ANY tool call proceeds.

**Remove from pre-commit** (same reason — behavioural, not structural):
| Hook | Reason misplaced | Correct home |
|------|-----------------|--------------|
| `check-ast-first-gate` | Process rule, can't reverse | Windsurf skill §0 |
| `check-rollback-checkpoints` (current weak form) | "Is artifact present?" — too weak | Windsurf skill pre-phase |
| `adg-phase-gate` (promoted prematurely) | Repair phase state = session context | Windsurf `.windsurf/rules/` |

### Phase 2 — Strengthen Windsurf Skills (Close the Timing Gap)

Each behavioural skill gets a **mandatory pre-condition block** in its `SKILL.md` that the AI is constitutionally required to execute before any tool call:

| Skill | Current | Hardened |
|-------|---------|----------|
| `ast-first-gate` | Guidance text | BLOCKS first tool call until `DEPENDENCY_GRAPH` section is written |
| `scope-guard` | Guidance text | BLOCKS first file edit until scope declaration artifact exists |
| `rollback-gate` | Guidance text | BLOCKS phase start until `git rev-parse HEAD` checkpoint recorded |
| `dedup-guard` | Guidance text | BLOCKS symbol creation until 4-step search documented |
| `adg-repair-discipline` | Guidance text | BLOCKS repair edit until 4 litmus answers documented |

Format for hardened pre-condition block (added to each SKILL.md):
```
## MANDATORY PRE-CONDITION (Constitutional — no bypass)
BEFORE any tool call in this context:
1. Execute: <specific command>
2. Write output to: <specific section/artifact>
3. Verify: <specific check>
IF any step fails → STOP. Do not proceed.
```

### Phase 3 — Fix the Remaining Pre-Commit Gates

**Keep but tighten** (structural, observable, correctly placed):
| Hook | Tightening needed |
|------|------------------|
| `check_script_sprawl.py` | Tighten: detect runners more precisely, avoid false positives on legitimate CI scripts |
| `check_dedup_violations.py` | Tighten: proxy check only (new Agent class = flag, not block) — full dedup stays in Windsurf |
| `check_shim_discipline.py` | Good as-is — shim content is observable |
| `check_rollback_checkpoints.py` | Change role: only verify artifact exists if commit message says "phase complete" |

**Revert `adg-phase-gate` back to manual stage** — repair phase state is a session-level context variable, not something a pre-commit script can reliably read from files.

### Phase 4 — Add `ENFORCEMENT_LAYER` Metadata to Every Rule

Each Windsurf skill `SKILL.md` gets a frontmatter field:
```yaml
enforcement_layer: windsurf        # behavioural — AI must enforce BEFORE work
# or
enforcement_layer: pre-commit      # structural — CI gate enforces AFTER work
# or
enforcement_layer: both            # genuine dual enforcement (e.g. import hygiene)
```

Update `RULES_INDEX.md` with a column: `Layer | Timing | Type`.

### Phase 5 — Document the Contract

Produce `docs/rules/enforcement_architecture.md`:
- The two-layer contract diagram
- Decision tree: "Should this rule be Windsurf or CI?"
- Maintenance protocol: how to add a new rule correctly
- List of all rules correctly assigned to their layer

---

## Decision Tree for New Rules

```
Is the rule about HOW the AI should work (process)?
  YES → Windsurf skill only. No pre-commit gate.
        Examples: ast-first, scope-guard, rollback, dedup

Is the rule about WHAT ended up in code (structure)?
  YES → Pre-commit gate only. Windsurf skill optional.
        Examples: import hygiene, layer violations, anti-patterns

Is the rule about both (e.g. "don't create shims wrong")?
  BOTH → Windsurf skill (prevent) + pre-commit gate (detect if it slipped)
         Examples: shim discipline, script sprawl

Can the rule be verified by inspecting a file or git diff?
  YES → Pre-commit gate is appropriate
  NO  → Windsurf rule only (trust the AI to follow it)
```

---

## Files Affected

| File | Change |
|------|--------|
| `.pre-commit-config.yaml` | Remove `check-ast-first-gate`; revert `adg-phase-gate` to manual; tighten remaining new gates |
| `.windsurf/rules/adg-repair-discipline.md` | Add `MANDATORY PRE-CONDITION` block |
| `.windsurf/skills/ast-first-gate/SKILL.md` | Add `MANDATORY PRE-CONDITION` block with tool-call blocker |
| `.windsurf/skills/scope-guard/SKILL.md` | Add `MANDATORY PRE-CONDITION` block |
| `.windsurf/skills/rollback-gate/SKILL.md` | Add `MANDATORY PRE-CONDITION` block |
| `.windsurf/skills/dedup-guard/SKILL.md` | Add `MANDATORY PRE-CONDITION` block |
| `ops_scripts/ci/check_ast_first_gate.py` | Delete (misplaced) |
| `ops_scripts/ci/check_rollback_checkpoints.py` | Narrow scope: only check when commit message says "phase complete" |
| `ops_scripts/ci/check_dedup_violations.py` | Narrow scope: proxy flag only, not hard block |
| `.windsurf/RULES_INDEX.md` | Add `Layer` and `Timing` columns |
| `docs/rules/enforcement_architecture.md` | New — canonical contract document |

---

## Outcome

| Metric | Before | After |
|--------|--------|-------|
| Rules in wrong layer | 3 (ast-first, rollback, phase-gate) | 0 |
| Windsurf rules with enforcement teeth | 0 (guidance only) | 5 (mandatory pre-conditions) |
| False sense of CI coverage | Yes | No |
| Clear responsibility contract | No | Yes (decision tree + arch doc) |
| Pre-commit noise from misfits | Yes | No |

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

