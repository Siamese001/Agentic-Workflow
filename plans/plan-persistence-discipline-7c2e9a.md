---
plan_format: v2
slug: plan-persistence-discipline-7c2e9a
status: Completed
dod_exempt: true
---

# Plan-Persistence Discipline — mandate a persisted SSOT plan for complex single-session work

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: W2
LAST_COMPLETED_WAVE: W2
TOTAL_WAVES: 2
LAST_UPDATED: 2026-06-14

## Context (SCQA)

**Situation:** Plan-*first* is enforced (native plan mode), but plan-*persistence* to the repo `plans/`
SSOT is opt-in and friction-loaded (`pre_write_plan_mint_gate` blocks disk-plan minting without
`PLAN_MINT_OK=1`; the operating model discourages plan files).
**Complication:** a 7-wave, ~230-file T3 change (notion-wave-enforcement-removal, ADR-104) ran to
completion with its plan only in the native plan-mode scratch file — never in SSOT — because
`work-item-classification` keys `PLAN_MULTI_WAVE` on "≥2 waves **and spans sessions**", so a large
single-session change falls through the crack and native plan mode (non-persistent) is the default.
**Question:** how do we guarantee genuinely complex work gets a durable SSOT record without recreating
the 145-plans/0-shipped proliferation?
**Answer:** decouple the trigger from "spans sessions" (RCA fix #2) and add a best-effort advisory
backstop that flags multi-wave execution with no minted plan (RCA fix #3). SSOT only — Notion stays
removed.

## Status Tables

### Wave Progress
| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | P1 | Doctrine: decouple PLAN_MULTI_WAVE trigger | ~8k | work-item-classification is the right SSOT | DONE | Rule mandates a disk plan for >=2 waves OR a large/cross-layer single-session T3 |
| W2 | P2 | Advisory backstop + test | ~12k | a Stop-hook response-text heuristic is sufficient (no session file tally exists) | DONE | auditor flags unpersisted multi-wave execution; suppresses when a plan IS minted; test passes |

### Phase Progress
| Phase | Status |
|---|---|
| P1 — work-item-classification doctrine | DONE |
| P2 — auditor extension + unit test | DONE |

## Wave 1 — Doctrine fix

WAVE_STATUS: DONE
WAVE_COMPLETE: YES
Edit `.claude/rules/work-item-classification.md`: change the `PLAN_MULTI_WAVE` condition from
"≥2 waves, spans sessions" to "≥2 waves **OR** a large single-session change (≥~10 files / cross-layer
T3) — single-session no longer exempts". Add the complexity→persisted-plan note; clarify native plan
mode persists nowhere durable; update the Plan-Correction table, anti-reflex rule #4, and the decision
flow. SSOT only (Notion stays removed).

## Wave 2 — Advisory backstop

WAVE_STATUS: DONE
WAVE_COMPLETE: YES
Extend `.claude/governance/scripts/post_agent_work_classification_audit.py` with a second, independent
check (`missing_plan_persistence`): if the response shows multi-wave execution (≥2 distinct wave
markers) + execution evidence (FILES_CHANGED / STATUS / commit / push) AND references no minted
`plans/<slug>-<6hex>.md`, log an advisory (fail-open, never blocks). Add a unit test. No new hook and
no `settings.json` change — reuse the already-wired auditor (lower machinery, consistent with the
de-bloating direction).

## Definition of Done
| # | Criterion | Verify |
|---|---|---|
| 1 | PLAN_MULTI_WAVE trigger no longer requires "spans sessions" | read work-item-classification.md |
| 2 | Complexity→persisted-plan note + native-mode-insufficient note added | read rule |
| 3 | Auditor flags unpersisted multi-wave execution | run auditor on synthetic multi-wave response |
| 4 | Auditor suppresses when a minted plan IS referenced | run auditor on response citing plans/<slug>.md |
| 5 | Unit test passes | pytest the new test |
| 6 | No new hook / no settings.json change (reuse wired auditor) | git diff |

Verification-vs-Deferral: all six verified this session; nothing deferred.
