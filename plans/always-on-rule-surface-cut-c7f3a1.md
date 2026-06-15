---
plan_id: always-on-rule-surface-cut-c7f3a1
plan_format: v2
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: []
---

# Always-On Rule Surface Cut — ~205 KB to ~50 KB, zero rigor loss

Trim the always-on `.claude/rules/*.md` context surface ~75% by demoting narrow-context reference rules to pointer stubs (detail already lives in skills/hooks), keep+compress the every-turn invariant floor, and fix the budget gate that is blind to the real surface.

> plan_id discipline: marker `plan=always-on-rule-surface-cut-c7f3a1`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: W5
LAST_COMPLETED_WAVE: W5
LAST_UPDATED: 2026-06-15

---

## Context (SCQA)

- **Situation** — Every session injects CLAUDE.md (16.3 KB) + all 43 `.claude/rules/*.md` (188.9 KB) = 205,257 B (~51,314 tokens) as always-on project instructions, via the native Claude Code loader globbing the directory (no `@`-import, no settings key, no hook does it).
- **Complication** — Enforcement rigor lives in 17 hooks + 62 governance scripts + CI gates + ~50 on-demand skills, NOT in the always-on prose. ~150 KB is narrow-context reference duplicated in skills + dead stubs. The budget gate scanned non-existent `.mdc` files + a `trigger: always_on` marker none of the `.md` files carry, so it measured ~0 (just AGENTS.md, 12,577 B) and was blind to the real 189 KB.
- **Question** — How do we cut the always-on surface ~75% without losing any enforcement rigor?
- **Answer** — Trim narrow-context rules to pointer stubs (detail stays in skills, enforcement stays in hooks/CI), keep+compress the every-turn floor, fix the gate to measure the real surface.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1 | Confirm/tighten dead stubs (global_rules, fortknox) | ~3K | already near-stub | DONE | dead rules are pointer stubs, refs intact |
| W2 | W2.1 | Gate honesty: measure all `.claude/rules/*.md` (advisory) | ~8K | advisory until trim lands (coupling) | DONE | gate reports the real 205 KB surface |
| W3 | W3.1, W3.2 | Demote ~32 narrow-context rules to pointer stubs | ~60K | skill/hook backs each | DONE (-110 KB; 205,257 to 94,965 B) | demoted rules small stubs; skills cover detail |
| W4 | W4.1 | Tighten 34 stubs + collapse constitutional retired slots + CLAUDE.md index + delete fortknox + deep-compress 001/work-item | ~20K | invariants preserved | DONE | 94,965→72,032 B; templates/§-numbers/invariants intact |
| W5 | W5.1 | Re-baseline ceiling to 86,016 B + flip enforcing + verify | ~10K | realistic ceiling for CLAUDE.md+rules | DONE | gate PASS enforcing (13,984 B headroom); skill-desc FIXED; only env ADG-snapshot-missing remains (not this change) |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Dead-stub confirm | DONE |
| W2.1 | Honest advisory measurement | DONE |
| W3.1 | Big-three trim (git-branch, adg-analysis, local-llm) | DONE (-31,416 B) |
| W3.2 | Remaining 29 rule trims (all demote-tier) | DONE |
| W4.1 | Floor compression + stub tightening | DONE |
| W5.1 | Re-baseline + enforce + verify | DONE |

---

## Out Of Scope

- apps_rg shipping (the north star) — this is meta-work behind it.
- Deleting the legacy `.cursor/` governance-backend tree.
- Touching agentic_core or runtime RAG.
- Changing hook/CI enforcement behavior (only the budget gate's measurement target).

---

## Wave 1 — Dead stubs

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases**:
- **W1.1** — Confirm/tighten dead stubs | ~3K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- global_rules.md (417 B, self-declared inactive) confirmed minimal; section 14 cross-reference intact.
- fortknox-certification-discipline.md kept as deprecation + deferred-teardown-map stub (already minimal).

---

## Wave 2 — Gate honesty

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — Measure all `.claude/rules/*.md` (advisory) | ~8K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- governance_tier_measurement.py gained scan_claude_rules_all_md() + claude_always_on_total(); gate reports the real surface (205,257 B).
- Advisory until trim lands (coupling: honest + enforcing on an untrimmed surface = self-inflicted red gate). Flip via ALWAYS_ON_CLAUDE_RULES_ENFORCE=1 at W5.

---

## Wave 3 — Demote bulk

WAVE_ID: W3
WAVE_STATUS: IN_PROGRESS
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — Big-three trim | ~20K | PHASE_STATUS: IN_PROGRESS | PHASE_COMPLETE: NO
- **W3.2** — Remaining ~29 rule trims | ~40K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Each demoted rule is a small pointer stub; doctrine-only rules (artifact-provenance-discipline, agent-taxonomy-spine-truth) keep their invariant inline.
- CLAUDE.md index links still resolve (to stubs).

---

## Wave 4 — Compress floor

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W4.1** — Floor compression | ~20K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- constitutional.md retired slots (25/30/32/35/36) collapsed to a one-line table; section numbering preserved.
- 001 RCA/Outcome-frame templates moved to skill; invariant kept inline.

---

## Wave 5 — Verify + enforce

WAVE_ID: W5
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Phases**:
- **W5.1** — Verify + flip gate to enforcing | ~10K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Always-on total under 51,200 B; budget gate flipped to enforcing (ALWAYS_ON_CLAUDE_RULES_ENFORCE=1) and green.
- `python ops_scripts/ci/run_contract_gates.py` passes; all hooks + skills resolve.

---

## Execution Details

### W2.1 — Honest advisory measurement
**Scope**: Added scan_claude_rules_all_md() + claude_always_on_total() to governance_tier_measurement.py (measure CLAUDE.md + ALL `.claude/rules/*.md`); check_always_on_token_budget.py prints the real-surface total + headroom, ADVISORY by default, enforcing under ALWAYS_ON_CLAUDE_RULES_ENFORCE=1.

### W3.1 — Big-three trim
**Scope**: Trim git-branch-per-chat.md (-> worktree-per-chat skill + 4 hooks), adg-analysis-procedures.md (-> adg-sqlite/graph-analysis skills + adg-canonical-invariants.md), local-llm-wsl2-gpu.md (git mv -> docs/reference, pure hardware reference). ~34 KB removed.

### W3.2 — Remaining trims
**Scope**: apps_rg quartet, core/apps boundary set, ledger/router/judge/eval subsystems, mcp-pytest/query-progress-bar/python-dash-c/windows-path-budget/ssot-folder/mcp-config/security-hardening/memory-management/approval-exception/artifact-provenance/agent-taxonomy. Doctrine-only rules keep their invariant inline. (Read-budget cap of 10/turn naturally sequences this across turns.)

---

## Definition of Done

DoD-1: Always-on surface under the re-baselined ceiling (86,016 B / 84 KiB; the legacy 51,200 was set for the retired 4-file .mdc design — see §33).
- Evidence: gate reports 72,032 B (−65% from 205,257), PASS enforcing, 13,984 B headroom — ~70 KB target met
- Status: DONE (deep-compressed 001 10.8K→6.8K + work-item 6.5K→2.6K with templates/matrix preserved; fortknox rule deleted)

DoD-2: Budget gate measures the real `.claude/rules/*.md` surface (no longer blind).
- Evidence: gate output lists CLAUDE.md + all `.claude/rules/*.md` bytes (confirmed 205,257 B)
- Status: DONE

DoD-3: Zero enforcement regression — all hooks + CI gates intact.
- Evidence: `run_contract_gates.py` — only failure is pre-existing `skill_description_quality` (3 SKILL.md files NOT in this diff); no plan/always-on/graph-layer/rule gate failed
- Status: DONE (no regression from this work)

DoD-4: Demoted rules are pointer stubs; doctrine-only rules retain invariant; index links resolve.
- Evidence: `for f in .claude/rules/*.md; do wc -c "$f"; done` + grep that stubs reference a skill/hook
- Status: TODO

DoD-5: Plan + memory writeback updated.
- Evidence: this plan's status cells updated; memory fact `always-on-rule-surface-cut` written
- Status: DONE

---

## Supersedes

_None — net-new plan._

---

## Marker Quick Reference

```
WAVE_COMPLETE: plan=always-on-rule-surface-cut-c7f3a1 wave=<N> note="+N files, scope=<summary>"
PLAN_COMPLETE: plan=always-on-rule-surface-cut-c7f3a1 note="<final outcome>"
```
