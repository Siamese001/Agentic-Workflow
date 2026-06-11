---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\windsurfrules-audit-03242026.md'
original_relative_path: 'windsurfrules-audit-03242026.md'
source_sha256: 5825c3d0bef62a09b5cc6f89ca47dd1e4390b849afd5d22dd01dbf006e6a9dcf
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-24'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Windsurf Rules, Skills & Workflows — Full Audit

**Date**: 2026-03-24
**Scope**: Complete review of `.windsurfrules` (905 lines, 9 sections), 17 skills, 6 workflows
**Question**: Are the rules helping or hurting now that ADG is mature?

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


## TL;DR

The rules system has **three layers of problems**:

1. **Redundancy** — The same mandate is restated 4-6 times across rules, skills, and workflows, burning context window tokens and confusing priority
2. **No proportionality** — A one-line typo fix and a 50-file architectural refactor trigger identical ceremony
3. **Stale assumptions** — Rules were written when ADG was immature and unreliable; now that ADG is hot-cached (891K edges, 9K nodes, <3h age), many guardrails solve problems that no longer exist

**Net assessment**: The rules prevented real damage during ADG buildout. Now they cost more than they save on ~80% of interactions.

---

## Part 1: Rules Inventory — What Exists

| Asset | Count | Total Lines |
|-------|-------|-------------|
| `.windsurfrules` sections (§0–§9 + Maxim) | 11 | 905 |
| Skills (`.windsurf/skills/`) | 17 | ~1,800 |
| Workflows (`.windsurf/workflows/`) | 6 | ~1,100 |
| **Total governance text** | **34 artifacts** | **~3,800 lines** |

Every Cascade session must parse all of this as system-level context. That's **~15K tokens** of instructions before the first user message arrives.

---

## Part 2: Per-Rule Verdict

### §0 DEFAULT ANALYSIS MODE (AST-First Gate)

**Verdict: 🔴 HURTING more than helping**

The rule says: *"For ANY code investigation, analysis, or modification task, build AST dependency graph FIRST."* The skill (`ast-first-gate`) has 246-line `pre_analysis_gate.md` + 183-line `ast_first_checklist.md` that demand a 6-step gate, 15-item checklist, and a mandatory `## DEPENDENCY_GRAPH` evidence section for every interaction touching code.

**What it prevents**: Cascade answering "what uses X?" with grep instead of graph data.

**What it costs**:
- Blocks trivially scoped work (fix a typo, add an assertion, update a docstring)
- Forces a full ADG rebuild ceremony even when the hot cache already has the answer
- The "FORBIDDEN: responding to user without building graph first" clause means Cascade can't answer a simple question about one file without first documenting graph roots, node types, edge types, upstream/downstream, cross-layer edges, cycles, and scope justification
- The `dependency-graph-analysis` skill (4 files, 68-line SKILL.md) is 90% redundant with §0

**Recommendation**:
- **Collapse** `ast-first-gate` + `dependency-graph-analysis` into one lightweight skill
- **Add proportionality**: If ADG Redis cache is HOT and query touches ≤3 files → use cache directly, no ceremony. If query touches >3 files or crosses layers → full protocol.
- **Drop** the mandatory `## DEPENDENCY_GRAPH` evidence section for non-repair interactions. Keep it for repair/refactor phases only.
- **Drop** the "BLOCK all work until graph built" language. Replace with "prefer graph-backed answers; document when using text search as fallback."

---

### §1 TESTING FRAMEWORK

**Verdict: 🟡 MOSTLY HELPING, some excess**

Test-first discipline, deterministic tests, skip management, and test count invariants are genuinely valuable. The `test-rigor-enforcement` skill (4 files) and `pytest-integrity` skill (2 files) encode real lessons learned.

**What hurts**:
- §1.1 "Every changed line of logic MUST have deterministic tests. No exceptions." is aspirational, not operational. Cascade can't generate tests for every single-line config change — the rule creates guilt without value.
- §1.4 zero-tolerance skip management is correct in CI but over-specifies the Cascade interaction model. Cascade doesn't need to know the full skip registry protocol for every conversation.
- §1.6 Agent Deletion Policy (50+ lines, example commit message) is a rare event encoded as always-loaded rules. This should be a workflow invoked on demand, not permanent context.

**Recommendation**:
- Keep §1.1–§1.3 (core test discipline)
- Move §1.4 skip management details to a skill (invoked when skips detected)
- Move §1.6 Agent Deletion to a workflow (invoked when deleting agents)
- Trim §1.5 test count invariants to 3 lines (the CI enforces this, not Cascade)

---

### §2 ADG FRAMEWORK

**Verdict: 🟡 CORE IS GOOD, bloated with implementation details**

§2.1–§2.3 (graph requirements, schema management, fail-closed) are solid architectural principles. §2.5 (repair discipline with 5 gates, repair classifications, cluster IDs) encodes hard-won lessons.

**What hurts**:
- §2.2 Schema Management (canonical field names table) — this is reference data, not a behavioral rule. It belongs in a lookup file, not always-loaded rules.
- §2.4 Evidence Requirements + §2.6 Accelerator Tools — these are ~120 lines of CLI examples and forbidden substitution tables. Useful as reference, wasteful as always-loaded context.
- §2.7 Custom Memory MCP (~70 lines) and §2.8 MCP Server Health Gate (~50 lines) — these are operational setup docs, not behavioral rules. They belong in a README.

**Recommendation**:
- Keep §2.1–§2.3, §2.5 (core ADG + repair discipline)
- Move §2.2 schema table, §2.4 proof artifacts, §2.6 accelerator CLI reference to `docs/reference/adg_quick_ref.md`
- Move §2.7–§2.8 MCP server docs to `docs/operations/mcp_setup.md`
- Net savings: ~200 lines removed from always-loaded context

---

### §3 EVIDENCE & DOCUMENTATION

**Verdict: 🟡 PRINCIPLE GOOD, over-specified**

Three-tier fact classification and evidence contracts are genuinely valuable discipline. But the rules specify 9 mandatory sections, 4 conditional sections, and exact section ordering for every evidence file.

**Recommendation**:
- Keep the three-tier classification (§3.3) and forbidden patterns (§3.4)
- Trim §3.2 to a short checklist; move full template to `evidence-bundle` skill (which already has it)
- Drop §3.5 (artifact links backtick rule) — this is a formatting preference, not a constitutional rule
- Drop §3.7 (RCA auto-closure) from here — it's already in §8.6 (duplicated!)

---

### §4 SCOPE & DETERMINISM

**Verdict: 🟢 HELPING**

Scope declaration, contamination detection, and the `scope-guard` skill are genuinely valuable. The four-tier scope record catches real problems.

**Recommendation**: Keep as-is. Minor trim: §4.4 (no low-signal search) is fully redundant with §0 — remove the duplicate.

---

### §5 CI ENFORCEMENT FRAMEWORK

**Verdict: 🟢 HELPING (but Cascade doesn't need most of it)**

CI gates are enforced by scripts, not by Cascade. The 13-condition table in §5.4 is valuable for CI but burns tokens in every Cascade session.

**Recommendation**:
- Keep §5.1 (single entrypoint) and §5.2 (fail-closed) as principles
- Move §5.3 timeout ranges and §5.4 gate table to CI documentation
- The `timeout-progress-enforcement` skill (296 lines!) and workflow (131 lines) are absurdly over-specified for a behavioral rule. Reduce to: "long operations need timeouts; use subprocess timeout parameter."

---

### §6 GOVERNANCE FRAMEWORK

**Verdict: 🟢 HELPING**

Policy drift detection, contract conflict escalation, and C0 boundary rules are tight and useful.

**Recommendation**: Keep as-is.

---

### §7 ACCEPTANCE DISCIPLINE

**Verdict: 🟢 HELPING**

Convergence and repair completion criteria are precise and prevent overclaiming.

**Recommendation**: Keep as-is.

---

### §8 ARCHITECTURE LOCKS + HITL

**Verdict: 🟡 MIXED**

§8.1–§8.4 (SSOT, boundary enforcement, tooling boundary, agent discipline) — tight and useful.

§8.5 HITL Framework — the *principle* is excellent but the *specification* is over-engineered:
- 322-line `hitl-decision-gate.md` workflow with 7 templates (architecture, refactoring, test repair, dependency, deletion, error handling, performance)
- Anti-pattern examples that tell Cascade what NOT to say
- This level of detail trains Cascade to be paralyzed, not helpful

§8.6 RCA Auto-Closure — duplicated from §3.7.

**Recommendation**:
- Keep §8.1–§8.4
- Trim HITL to the core principle (10 lines) + triggers list. Drop the 7 templates — Cascade can generate appropriate options without a template for every scenario.
- Remove §8.6 (duplicate of §3.7)

---

### §9 EXECUTION MODALITY

**Verdict: 🟢 HELPING**

Repair gates and stabilize-before-refactor are hard lessons encoded correctly.

**Recommendation**: Keep as-is.

---

### MAXIM section

**Verdict: 🟡 MOSTLY REDUNDANT**

50 lines that restate principles already defined in §0–§9. Burns tokens.

**Recommendation**: Delete entirely. Every principle is already stated in its section.

---

## Part 3: Skills Audit

| Skill | Files | Verdict | Recommendation |
|-------|-------|---------|----------------|
| `ast-first-gate` | 3 | 🔴 Over-blocking | **Merge** into `dependency-graph-analysis`, add proportionality |
| `dependency-graph-analysis` | 5 | 🟡 Redundant with §0 | **Merge** with ast-first-gate into single skill |
| `evidence-bundle` | 5 | 🟡 Useful templates | **Keep**, trim to 2 files (template + post-commit) |
| `test-rigor-enforcement` | 5 | 🟡 Useful but heavy | **Keep**, trim example_usage.md |
| `scope-guard` | 4 | 🟢 Valuable | **Keep** |
| `rollback-gate` | 3 | 🟢 Valuable | **Keep** |
| `dedup-guard` | 3 | 🟢 Valuable | **Keep** |
| `import-hygiene` | 3 | 🟢 Valuable | **Keep** |
| `layer-boundary-guard` | 3 | 🟢 Valuable | **Keep** |
| `shim-discipline` | 3 | 🟢 Valuable (rare) | **Keep** |
| `script-sprawl-guard` | 3 | 🟢 Valuable | **Keep** |
| `ssot-write-gate` | 3 | 🟢 Valuable | **Keep** |
| `mcp-tool-verify` | 3 | 🟡 Stale references | **Update** (references `mcp8_write_file` which doesn't exist) |
| `pytest-integrity` | 3 | 🟢 Valuable | **Keep** |
| `adg-repair-loop` | 1 | 🟡 Redundant with workflow | **Delete** (workflow `/adg-repair-loop` covers this) |
| `redis-hitl-gate` | 2 | 🔴 Over-engineered | **Delete** — ADG Redis is stable now; HITL on every Redis failure is excessive |
| `timeout-progress-enforcement` | 5 | 🔴 Massively over-specified | **Trim** to 1 file with core principle |

**Net recommendation**: Delete 3 skills, merge 2 skills, trim 3 skills = **8 fewer skill files** loaded per session.

---

## Part 4: Workflows Audit

| Workflow | Lines | Verdict | Recommendation |
|----------|-------|---------|----------------|
| `adg-redis-refresh` | 191 | 🟢 Valuable | **Keep** — well-structured operational runbook |
| `adg-repair-loop` | 116 | 🟢 Valuable | **Keep** |
| `adg-timeout-recovery` | 371 | 🔴 Over-engineered | **Trim** to 50 lines — 300 lines of example Python code is reference material, not a workflow |
| `antipattern-hitl-gate` | 71 | 🟢 Valuable | **Keep** |
| `hitl-decision-gate` | 322 | 🔴 Over-specified | **Trim** to 80 lines — drop 7 template examples |
| `timeout-progress-enforcement` | 131 | 🟡 Redundant with skill | **Delete** — consolidated into trimmed skill |

---

## Part 5: The Core Problem — No Proportionality

The entire system treats every interaction the same. There is no concept of "this is a simple question" vs "this is a 50-file refactor." The constitutional language ("BLOCK all work", "FORBIDDEN", "CONSTITUTIONAL VIOLATION", "HARD FAIL") makes no distinction.

### Proposed Tiered Model

```
TIER 0 — QUESTION (no code changes)
  Examples: "what does X do?", "explain this file", "is this rule too strict?"
  Required: Use ADG cache if available. No ceremony.

TIER 1 — TRIVIAL CHANGE (≤1 file, ≤20 lines, obvious scope)
  Examples: typo fix, add assertion, update docstring, config value change
  Required: Verify change with relevant tests. No evidence file. No DEPENDENCY_GRAPH section.

TIER 2 — SCOPED CHANGE (2-5 files, single layer)
  Examples: bug fix with test, small refactor, add new function
  Required: ADG cache query for blast radius. Run scoped tests. Brief scope note.

TIER 3 — ARCHITECTURAL CHANGE (>5 files, cross-layer, or governance)
  Examples: module migration, new visitor, layer restructure
  Required: Full ADG protocol. Evidence file. DEPENDENCY_GRAPH section. HITL gate. Rollback checkpoint.
```

This model preserves ALL existing safety for high-risk work while removing friction from 80% of interactions.

---

## Part 6: Concrete Changes

### Immediate (low risk, high impact)

1. **Delete MAXIM section** from `.windsurfrules` — pure redundancy (-50 lines)
2. **Delete §8.6** — duplicate of §3.7 (-25 lines)
3. **Remove §4.4** — duplicate of §0 (-8 lines)
4. **Delete `redis-hitl-gate` skill** — ADG Redis is stable
5. **Delete `adg-repair-loop` skill** — workflow covers this
6. **Move §2.7–§2.8** (MCP setup docs) to `docs/operations/` (-120 lines)
7. **Move §2.2 schema table** to reference doc (-30 lines)

**Savings: ~250 lines from always-loaded context, 4 fewer skill files**

### Medium-term (moderate risk)

8. **Add tier-awareness to §0** — replace absolute BLOCK language with proportional protocol
9. **Merge `ast-first-gate` + `dependency-graph-analysis`** into one skill with tier logic
10. **Trim `timeout-progress-enforcement`** skill from 296 to ~60 lines
11. **Trim `adg-timeout-recovery`** workflow from 371 to ~80 lines
12. **Trim `hitl-decision-gate`** workflow from 322 to ~80 lines
13. **Move §1.6 Agent Deletion** to on-demand workflow
14. **Move §5.3–§5.4** CI details to CI docs

**Savings: ~800 more lines, 2 fewer skill files, much less token burn per session**

### Long-term (requires validation)

15. **Rewrite `.windsurfrules`** as a two-part document:
    - Part A: **Core Principles** (~150 lines) — always loaded, constitutional floor
    - Part B: **Reference Manual** (~400 lines) — loaded on demand via skill invocation
16. **Add `tier` field to skill frontmatter** so Cascade knows which tier triggers each skill

---

## Part 7: What MUST Stay

Some rules are load-bearing and should never be weakened:

- **Fail-closed discipline** (§2.3) — prevents silent fallbacks
- **Scope guard** — prevents contamination
- **Rollback gate** — prevents broken intermediate states
- **Test-first discipline** (§1.2) — prevents untested code
- **Layer boundary guard** — prevents architectural decay
- **HITL principle** (not the 322-line spec) — prevents unilateral decisions
- **SSOT write gate** — prevents file sprawl
- **Skip management principle** (not the full protocol) — prevents test erosion
- **Repair classification** (§2.5) — prevents misdiagnosed fixes

These are the rules that caught real bugs and prevented real damage. Everything else is ceremony.

---

## Summary

| Category | Current | Recommended | Δ |
|----------|---------|-------------|---|
| `.windsurfrules` lines | 905 | ~500 | -45% |
| Skill files | 52 | ~38 | -27% |
| Workflow files | 6 | 5 | -17% |
| Token cost per session | ~15K | ~8K | -47% |
| Rules blocking trivial work | yes | no (tier-aware) | — |

The rules served their purpose brilliantly during ADG buildout. Now they need to evolve from "wartime constitution" to "peacetime operating procedures."

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

