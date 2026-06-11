---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\always-on-budget-compression-ds2-c7f4a3.md'
original_relative_path: 'always-on-budget-compression-ds2-c7f4a3.md'
source_sha256: 8023da9f0c315a7a827248019ecb1b1c3ea50b8d0b6d1b647ee18159ae4eb6c0
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-09'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: always-on-budget-compression-ds2-c7f4a3
plan_type: governance
---

# Always-On Budget Compression for DS-2 Author-Gate Promotion

Free ≥9,579 bytes from existing always_on rules to promote `author-gate-enforcement.md` (9,941 bytes) from `model_decision` to `always_on`, completing DS-2 of plan `author-gate-pipeline-hardening-deferred-b3e1d7`.

---

## Context (SCQA)

- **Situation** — The §33 always-on token budget cap is 51,200 bytes. Current total is 50,838 bytes across 10 rules, leaving only 362 bytes free. `author-gate-enforcement.md` (9,941 bytes, trigger `model_decision`) should be `always_on` so the pipeline-completion invariant, four-requirement contract, and canonical-emitter invariant are enforced every turn — not just when the model guesses an Author-Gate context.
- **Complication** — Promoting the rule as-is would exceed the cap by 9,579 bytes. No single rule is removable; all encode load-bearing invariants. The excess must come from compressing narrative/rationale/tables out of existing rules into skills (no budget cap) while keeping invariants inline.
- **Question** — How do we free ≥9,579 bytes from existing always-on rules without losing any behavioral invariant?
- **Answer** — Compress 4 always-on rules by moving narrative rationale, incident history, detailed tables, and enforcement-layer lists into their existing sibling skills. Then compress the promotion target itself to ~7,000 bytes. Flip the trigger. Verify budget gate passes with ≥500 bytes margin.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `ops_scripts/ci/check_always_on_token_budget.py` | Budget gate — verification after each wave | 🔲 |
| `.windsurf/rules/apps-rg-interactive-discipline.md` (5,914 bytes) | Compression target #1 | 🔲 |
| `.windsurf/rules/mcp-serialization.md` (5,031 bytes) | Compression target #2 | 🔲 |
| `.windsurf/rules/notion-plan-wave-deferral.md` (3,164 bytes) | Compression target #3 | 🔲 |
| `.windsurf/rules/adg-canonical-invariants.md` (5,073 bytes) | Compression target #4 | 🔲 |
| `.windsurf/rules/author-gate-enforcement.md` (9,941 bytes) | Promotion target — also compress | 🔲 |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | P1.1 | Compress `apps-rg-interactive-discipline.md` | ~3k | Skill absorbs narrative | ✅ DONE | 5,914→1,992 bytes (3,922 saved); budget 4,284 free |
| W2 | P2.1 | Compress `mcp-serialization.md` | ~2k | Skill absorbs rationale + allowlist detail | ✅ DONE | 5,031→1,213 bytes (3,818 saved); budget 8,102 free |
| W3 | P3.1, P3.2 | Compress `notion-plan-wave-deferral.md` + `adg-canonical-invariants.md` | ~3k | Skills absorb enforcement + detail sections | ✅ DONE | 3,164→854 + 5,073→1,865 (5,518 saved); budget 13,620 free |
| W4 | P4.1 | Compress `author-gate-enforcement.md` | ~2k | Procedural detail → skill | ⏭️ SKIPPED | 13,620 free > 9,941 needed; compression unnecessary |
| W5 | P5.1 | Flip trigger + verify | ~1k | All prior waves done | ✅ DONE | trigger flipped; budget PASS 47,321/51,200 (3,879 margin) |

**Total: ~11k tokens across 5 waves.**

---

## Out Of Scope

- Changing the §33 budget cap (51,200 bytes) itself
- Compressing `constitutional.md` or `global_rules.md` (highest-value always-on rules; compression risk too high)
- Compressing `scope-containment.md`, `ssot-folder-enforcement.md`, `plan-location.md`, `author-gate-queue-drain.md` (smaller rules with less compressible content)
- Creating new skills — only existing sibling skills absorb overflow
- Changing rule behavioral semantics — only moving prose, not invariants

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1.1 | Compress apps-rg-interactive-discipline | `apps-rg-interactive-discipline.md` | 5,914→1,992 bytes | ~3k | ✅ DONE |
| P2.1 | Compress mcp-serialization | `mcp-serialization.md` | 5,031→1,213 bytes | ~2k | ✅ DONE |
| P3.1 | Compress notion-plan-wave-deferral | `notion-plan-wave-deferral.md` | 3,164→854 bytes | ~1.5k | ✅ DONE |
| P3.2 | Compress adg-canonical-invariants | `adg-canonical-invariants.md` | 5,073→1,865 bytes | ~1.5k | ✅ DONE |
| P4.1 | Compress author-gate-enforcement | `author-gate-enforcement.md` | SKIPPED — headroom sufficient without compression | ~0 | ⏭️ SKIPPED |
| P5.1 | Flip trigger + verify | `author-gate-enforcement.md` frontmatter | Budget PASS 47,321/51,200 (3,879 margin) | ~1k | ✅ DONE |

---

## Gap Register

**GAP-1: Compression may be insufficient**
- If achieved savings < 9,579 bytes after W1-W4, W5 cannot proceed.
- Mitigation: each wave runs budget gate; if cumulative savings track below target, expand compression scope to `scope-containment.md` (5,280 bytes, ~1,000 bytes compressible).

**GAP-2: Behavioral regression from over-compression**
- Moving too much from rules to skills risks the model not loading the skill when needed.
- Mitigation: every ⛔ callout and hard rule stays in the always-on rule. Only narrative, rationale, tables-of-enforcement-layers, and incident history move.

---

## Execution Plan

### Phase 1.1 — Compress `apps-rg-interactive-discipline.md`

**Scope**: Remove "Why this rule exists" section (~400 bytes), incident narrative §"Empirical incident" (~250 bytes), defense-in-depth table (~350 bytes), forbidden-patterns table (~400 bytes), sibling-apps section (~150 bytes), "Non-TTY contexts" section (~200 bytes). Keep: ⛔ callout, single-prompt template, hard rules 1-3, stale-file rule 4, references.

**Acceptance**: Rule ≤2,200 bytes; `check_always_on_token_budget.py` passes; all content preserved in Cursor Agent memory (the rule already has a memory entry `aa3e66d1` covering full detail).

### Phase 2.1 — Compress `mcp-serialization.md`

**Scope**: Remove "Why scoped to remote" rationale paragraph (~500 bytes), remote MCP allowlist table detail rows (~400 bytes, keep server names only), "Local MCP Servers" paragraph (~200 bytes, keep one-line list), SQLite fallback section detail (~500 bytes, keep one-line pointer to `adg-sqlite` skill). Keep: ⛔ invariant, 5 hard rules, bypass, sunset line.

**Acceptance**: Rule ≤2,400 bytes; budget gate passes.

### Phase 3.1 — Compress `notion-plan-wave-deferral.md`

**Scope**: Remove "When This Applies" exemption list (~300 bytes), forbidden patterns section (~250 bytes), enforcement layers table (~350 bytes). Keep: ⛔ callout, 4-step protocol, bypass line, references.

**Acceptance**: Rule ≤1,600 bytes; budget gate passes.

### Phase 3.2 — Compress `adg-canonical-invariants.md`

**Scope**: Remove §4 "4 Deadly Catch-Site Antipatterns" detail (~350 bytes), §5 archetype descriptions (~300 bytes), §6 multiplier formula block (~200 bytes), §7 pipeline detail (~300 bytes), §12 doctrinal references list (~200 bytes). Keep: §1 hierarchy, §2 "ADG wins", §3 surfaces, §8 static-vs-runtime table, §9 ADG-vs-hardcoded, §10 required plan sections, §11 provenance stamp. Compact §4-§7 to one-line pointers.

**Acceptance**: Rule ≤3,200 bytes; budget gate passes.

### Phase 4.1 — Compress `author-gate-enforcement.md`

**Scope**: Remove "Where the procedural detail lives" table (~500 bytes, already lives in the skill), canonical-emitter narrative paragraphs (~400 bytes, keep one ⛔ line), calibration-driven triggers section (~250 bytes), marker grammar code block (~200 bytes). Keep: pipeline steps 1-9, four-requirement table, pipeline-completion invariant, continuous-execution invariant, bypass conditions, silent-marker invariant, constitutional cross-reference.

**Acceptance**: Rule ≤7,000 bytes.

### Phase 5.1 — Flip trigger + verify

**Scope**: Change `trigger: model_decision` → `trigger: always_on` in `author-gate-enforcement.md` frontmatter. Run `check_always_on_token_budget.py`. Verify ≥500 bytes margin.

**Acceptance**: Budget gate PASS; new total ≤50,700 bytes.

---

## Rules

- §21 Zero-loss overwrite discipline: every invariant/constraint/script-reference must survive in compressed rule or receiving skill
- §33 Two-tier compliance: always_on rules ≤51,200 bytes
- §18 No hidden scope expansion: only touch the 5 named rules

---

## Success Criteria

- [ ] `author-gate-enforcement.md` has `trigger: always_on`
- [ ] `check_always_on_token_budget.py` passes with ≥500 bytes margin
- [ ] All ⛔ callouts and hard rules preserved verbatim in compressed rules
- [ ] Moved content preserved in skills or Cursor Agent memories
- [ ] No behavioral regression: Author-Gate pipeline still fires correctly

---

## Rollback Strategy

If things go wrong:
1. `git checkout -- .windsurf/rules/` restores all rules to pre-compression state
2. Revert `author-gate-enforcement.md` frontmatter to `trigger: model_decision`
3. Budget gate will pass again (returns to 362 bytes free)

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Always-on budget total | ≤50,700 bytes | `python ops_scripts/ci/check_always_on_token_budget.py` |
| Free headroom | ≥500 bytes | Same gate output |
| author-gate-enforcement trigger | `always_on` | `head -3 .windsurf/rules/author-gate-enforcement.md` |
| Invariant preservation | 100% ⛔ blocks retained | Manual diff audit per wave |

## Cursor Agent Alignment Checks

- Keep always-on rules lean; place detailed procedures in skills or workflows.
- Retrieve local or scoped evidence before synthesis.
- Prefer exact or structural matches before broad semantic expansion.
- For high-risk outputs, extract evidence or quotes before summarizing.
- Reserve deterministic enforcement for hooks or scripts, not template prose.
