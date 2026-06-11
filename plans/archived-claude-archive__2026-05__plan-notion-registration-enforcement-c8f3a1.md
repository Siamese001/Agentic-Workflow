---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\plan-notion-registration-enforcement-c8f3a1.md'
original_relative_path: '_archive\\2026-05\\plan-notion-registration-enforcement-c8f3a1.md'
source_sha256: 5b14b61911d239f6df8a5b1b7c68e6d655e2fb0c89a4412e0b04b89fd7e5a8ab
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: Plan–Notion Registration Enforcement

**Slug:** `plan-notion-registration-enforcement-c8f3a1`
**Status:** ✅ DONE (2026-05-03, single session)
**Owner:** Cursor Agent
**Created:** 2026-05-03
**Constitutional anchor:** new §36 (proposed) · siblings §24, §25, §31, §35
**Parent doctrine:** `AGENTS.md` auto-routing rule "On new plan file creation … create Plans row"

---

## 1. Problem Statement

Two distinct failure modes occurred in the same session (2026-05-03):

1. **False-negative claim.** Cursor Agent told the user a plan was "not registered in Notion" without actually querying the Plans DB. The plan **was** registered (`35527693-f55c-8188-8cc2-db4d69806b3c`, Status=Live, AI Summary populated). Root cause: answered from session memory instead of querying the authoritative source.
2. **Historical drift risk.** The AGENTS.md auto-routing rule for `new plan file → Plans DB row` is advisory only — no hook, gate, or CI check enforces it. A future plan authored mid-wave can silently skip registration, and nothing detects the drift until a human asks.

Both modes share a common root: **Notion Plans DB registration has no deterministic enforcement layer.** Cursor Agent is trusted to do the right thing; when it doesn't (either by omission or by false claim), nothing catches it.

## 2. Goal

Make Plan↔Notion registration a **mechanically enforced invariant**, not a behavioral hope. Specifically:

- Every `.cursor/plans/<slug>-<6hex>.md` that exists on disk with no Archived/Retired status MUST have a corresponding Notion Plans row with non-empty `AI Summary `.
- Wave execution (`wave_execution_state.py start`) MUST be blocked on unregistered plans.
- Cursor Agent MUST query the Plans DB (never guess) before making any claim about a plan's registration status.
- Drift (on-disk without Notion, or Notion Live without on-disk) is detected within one commit cycle.

## 3. Non-Goals

- Retroactive backfill of historical plans (existing 220 plan files are assumed registered; a one-shot audit is a deferred item, not part of this plan).
- Replacing or weakening the existing NP1 `check_notion_plans_ai_summary.py` gate — this plan extends it, does not duplicate.
- Auto-generating AI Summary content — Cursor Agent still authors the summary from the plan file; enforcement only verifies presence.
- Changing the Plans DB schema.

## 4. Files In Scope

**New:**
- `.cursor/rules/plan-registration-enforcement.md` (conditional rule, procedural detail)
- `.cursor/scripts/_plan_registration.py` (pure helper — SSOT logic)
- `.cursor/scripts/post_cursor_agent_plan_registration_capture.py` (post-hook — marker → queue)
- `.cursor/scripts/pre_user_prompt_plan_registration_surface.py` (pre-hook — surface pending)
- `ops_scripts/ci/check_plan_registration_freshness.py` (pre-commit gate T7u)
- `ops_scripts/calibration/plan_registration_weekly_report.py` (weekly drift)
- `tests/unit/windsurf_scripts/test_plan_registration.py`
- `.cursor/state/plan_registration_queue.jsonl` (append-only, gitignored)
- `.cursor/state/plan_registration_cache.json` (Notion Plans DB snapshot, TTL 1h, gitignored)

**Edited:**
- `.cursor/scripts/pre_mcp_gate.py` (add `check_plan_registration()` hook for wave-start calls)
- `.cursor/rules/constitutional.md` (add §36)
- `.cursor/hooks.json` (register new post/pre hooks)
- `.pre-commit-config.yaml` (register T7u)
- `ops_scripts/ci/run_contract_gates.py` (register PR1 gate)
- `AGENTS.md` (upgrade auto-routing row from advisory to enforced)

## 5. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | P1.1, P1.2 | Helper + marker convention | ~6k | Notion API stable; `NOTION_API_KEY` available offline-safe | ✅ DONE | `_plan_registration.py` 31/31 tests green; `PLAN_CREATED:` shape documented in rule |
| W2 | P2.1, P2.2 | Post-hook + queue | ~5k | Marker parsing mirrors `post_cursor_agent_ag_queue_seed_capture.py` | ✅ DONE | Marker → queue roundtrip verified; fail-soft on empty stdin confirmed |
| W3 | P3.1 | Wave-start chokepoint block (in CLI, not pre_mcp_gate) | ~6k | `wave_execution_state.py start` is the canonical entry | ✅ DONE | Unregistered plan → BLOCKED exit 2; registered plan → allow exit 0; `PLAN_REGISTRATION_BYPASS=1` verified (logged) |
| W4 | P4.1 | Pre-user-prompt surface | ~3k | Mirrors `pre_user_prompt_ag_queue_surface.py` | ✅ DONE | Emits `PLAN_REGISTRATION_PENDING:` per pending queue row |
| W5 | P5.1, P5.2 | Pre-commit freshness gate + weekly drift | ~7k | Advisory by default; fail-closed via env var | ✅ DONE | T7u registered in `.pre-commit-config.yaml`; PR1 in `run_contract_gates.py`; `--all` drift scan verified; weekly report module importable |
| W6 | P6.1, P6.2 | Constitutional §36 + rule file + AGENTS.md upgrade | ~4k | Two-tier compliance (always-on budget) | ✅ DONE | §36 live; `plan-registration-enforcement.md` conditional; AGENTS.md row upgraded. **Note:** always-on +570 bytes over §33 threshold — captured as deferred-scope P2 |
| W7 | P7.1 | Query-before-claim doctrine | ~3k | Behavioral rule in conditional file; no hook | ✅ DONE | Rule §"Query Before Claim" documents incident + required posture |
| W8 | P8.1 | End-to-end verification | ~3k | All prior waves green | ✅ DONE | Block/allow paths exercised against live CLI; all 6 new Python files `py_compile` clean |

**Total estimate:** ~37k tokens across 8 waves, 11 phases.

## 6. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | Helper module | `_plan_registration.py` | Notion API paginate + offline-safe fallback | ~3k | 📝 |
| P1.2 | Marker convention doc | `plan-registration-enforcement.md` (partial) | Marker shape parity with `AG_QUEUE_SEED:` / `DEFERRED_SCOPE:` | ~3k | 📝 |
| P2.1 | Post-hook | `post_cursor_agent_plan_registration_capture.py` | Regex parity with sibling capture hooks | ~3k | 📝 |
| P2.2 | Queue schema + tests | `plan_registration_queue.jsonl` shape, unit tests | Append-only semantics, dedup on slug | ~2k | 📝 |
| P3.1 | Pre-MCP wave-start block | `pre_mcp_gate.py` | Chokepoint identification — ONLY block on `wave_execution_state start`, not on arbitrary MCP calls | ~6k | 📝 |
| P4.1 | Session-start surface | `pre_user_prompt_plan_registration_surface.py` | Emit format matches AG queue surface | ~3k | 📝 |
| P5.1 | Pre-commit gate | `check_plan_registration_freshness.py` | Offline-safe (skip when `NOTION_API_KEY` unset); uses cache | ~4k | 📝 |
| P5.2 | Weekly drift report | `plan_registration_weekly_report.py` | Report orphans both directions | ~3k | 📝 |
| P6.1 | Constitutional §36 | `constitutional.md` | Stay under always-on budget (§33) | ~2k | 📝 |
| P6.2 | Conditional rule + AGENTS.md | `plan-registration-enforcement.md`, AGENTS.md | Upgrade auto-routing row to "enforced by §36" | ~2k | 📝 |
| P7.1 | Query-before-claim rule | `plan-registration-enforcement.md` §"Query Before Claim" | Behavioral discipline, no hook — document precedent (2026-05-03 false-negative) | ~3k | 📝 |
| P8.1 | E2E verification | — | Requires temp scratch plan; cleanup after | ~3k | 📝 |

## 7. Marker Conventions

**Author-time marker (emitted in the same response that writes the plan file):**

```
PLAN_CREATED: slug=<slug-6hex> path=.cursor/plans/<slug>-<6hex>.md status=Draft|Live
```

**Session-start surface line (emitted by pre-user-prompt hook when queue non-empty):**

```
PLAN_REGISTRATION_PENDING: <slug-6hex> (created <ISO8601>)
```

**Block message (emitted by pre-MCP gate):**

```
BLOCKED: plan <slug-6hex> not registered in Notion Plans DB.
Required: API-post-page to Plans DB (slug, Status=Live|Draft, Exists On Disk=true, Plan File Path, Summary, AI Summary) before wave execution.
Bypass: PLAN_REGISTRATION_BYPASS=1
```

## 8. Enforcement Layers (same pattern as §24 / §31 / §35)

| Layer | Artifact | Trigger | Blocks? |
|-------|----------|---------|---------|
| Rule | `§36` + `plan-registration-enforcement.md` | Always-on | No (advisory) |
| Marker | `PLAN_CREATED:` | Plan file write | No |
| Helper | `_plan_registration.py` | Called by hooks/gates | No |
| Post-hook | `post_cursor_agent_plan_registration_capture.py` | Cursor Agent response | No (fail-soft) |
| Pre-hook | `pre_user_prompt_plan_registration_surface.py` | Session/prompt start | No (surfaces) |
| Pre-MCP gate | `pre_mcp_gate.check_plan_registration()` | Before `wave_execution_state start` | **Yes** |
| Pre-commit | `check_plan_registration_freshness.py` (T7u) | New plan file staged | Configurable via `PLAN_REGISTRATION_FAIL_CLOSED=1` |
| Weekly | `plan_registration_weekly_report.py` | Cron / manual | No (reports) |

## 9. Query-Before-Claim Doctrine (Failure Mode #2)

Encoded in `plan-registration-enforcement.md` §"Query Before Claim":

> Cursor Agent MUST NOT assert that a plan is or is not registered in the Notion Plans DB without having called `API-query-data-source` against data source `ac53d31b-3068-4039-9ebe-856c12caab32` in the current response. Session memory and cached responses are not authoritative. If `NOTION_API_KEY` is unset or the call fails, Cursor Agent MUST say "I cannot verify registration status right now" rather than guess.

This is a behavioral rule with no hook (Notion is remote, §25-serialized; a pre-check hook would stall every turn). Enforced by:
1. The rule text itself.
2. The weekly drift report surfacing any "claimed not registered but actually registered" incident via diff against response logs (stretch goal — P8 deferred item).

## 10. Proposed Constitutional §36 Text

```
36. **Plan–Notion registration mandatory.** Every new `.cursor/plans/<slug>-<6hex>.md`
    MUST emit `PLAN_CREATED:` marker in the authoring response AND be posted as a Plans DB row
    (Status, Exists On Disk, Plan File Path, Summary, AI Summary) before any wave execution
    (`wave_execution_state.py start`). Wave-start is blocked on unregistered plans.
    Cursor Agent MUST NOT claim registration status without a live `API-query-data-source` call
    in the same response. SSOT helper: `_plan_registration.py`. Detail:
    `plan-registration-enforcement.md`. Bypass: `PLAN_REGISTRATION_BYPASS=1`.
```

Estimated size: ~600 bytes. Fits under §33 always-on budget.

## 11. Gap Register

| Gap | Severity | Mitigation |
|-----|----------|------------|
| Notion API offline → cache staleness lets unregistered plan through | Medium | Cache TTL 1h; fail-soft pre-MCP gate logs WARNING but does not block when cache stale AND `NOTION_API_KEY` unset |
| `PLAN_CREATED:` marker forgotten | Low | Pre-commit gate T7u catches on next commit of the plan file |
| Query-before-claim is behavioral only | Medium | No hook possible (remote-MCP serialization); mitigated by weekly report + rule text |
| Existing 220 plans may have undetected drift | Low | One-shot audit deferred to follow-up plan (see §12) |
| Wave-start block chokepoint assumes Cursor Agent uses `wave_execution_state.py start` | Medium | Rule §36 reiterates this is the canonical entry; existing wave-deferral rule already depends on it |

## 12. Deferred Scope

- `DEFERRED_SCOPE: priority=P2 item=one-shot-audit-existing-220-plans rationale=backfill-is-orthogonal-to-forward-enforcement`
- `DEFERRED_SCOPE: priority=P3 item=response-log-diff-for-false-negative-claims rationale=requires-response-capture-plumbing-not-yet-built`
- `DEFERRED_SCOPE: priority=P3 item=auto-generate-ai-summary-from-plan-file rationale=content-authoring-is-cascades-job-not-the-gates`
- `DEFERRED_SCOPE: priority=P2 item=always-on-budget-compaction-after-36 rationale=adding-§36-put-always-on-570-bytes-over-51200-threshold-needs-targeted-trim-elsewhere`

### P2 · Always-on budget compaction (post-§36)

**Observed 2026-05-03 at plan completion.** Adding §36 (~380 bytes net) pushed the combined `trigger: always_on` corpus to 51,770 bytes — 570 bytes over the §33 threshold of 51,200 bytes. `ops_scripts/ci/check_always_on_token_budget.py` exits 1 (advisory failure; `ALWAYS_ON_BUDGET_BYPASS=1` available but not a permanent solution).

**Current always-on byte budget (top contributors):**

| Bytes | File |
|-------|------|
| 15,263 | `.cursor/rules/constitutional.md` |
| 8,425 | `.cursor/rules/scope-containment.md` |
| 6,590 | `.cursor/rules/global_rules.md` |
| 5,073 | `.cursor/rules/adg-canonical-invariants.md` |
| 5,031 | `.cursor/rules/mcp-serialization.md` |
| 3,164 | `.cursor/rules/notion-plan-wave-deferral.md` |
| 3,044 | `.cursor/rules/ssot-folder-enforcement.md` |
| 2,596 | `.cursor/rules/plan-location.md` |
| 2,584 | `.cursor/rules/author-gate-queue-drain.md` |

**Remediation candidates (do not pick in this plan — sized for a followup):**

1. `scope-containment.md` (8,425 b) — the largest non-constitutional rule. Procedural examples and the "Summarize-Before-Return" / "Scope-Reset Marker" sections could move to a `scope-containment` skill, leaving only invariants in the rule. Rough recovery: 2–3 kB.
2. `adg-canonical-invariants.md` (5,073 b) — §7 (Zero-Loss Propagation Pipeline) + §11 (Provenance Stamp) are procedural and could be referenced out to the `adg-sqlite` skill. Rough recovery: 1–2 kB.
3. `mcp-serialization.md` (5,031 b) — the remote-MCP allowlist table + SQLite-direct fallback block is procedural detail that belongs in the `mcp-serialization` skill already cited from the rule. Rough recovery: 1.5–2 kB.

Any ONE of these three reclaims more than the 570-byte overage on its own. No constitutional rule numbers change; only body text migrates.

**Non-goals for the followup plan:**

- Do NOT change rule numbers or enforcement semantics.
- Do NOT weaken §36 or any other rule to fit the budget.
- Do NOT bypass `check_always_on_token_budget.py` as a long-term solution; bypass is acceptable only during the followup plan's execution window.

**Success criteria for the followup:**

- `check_always_on_token_budget.py` exits 0 without `ALWAYS_ON_BUDGET_BYPASS=1`.
- No enforcement regression (same CI gates green, same behavioral invariants).
- The demoted procedural content lives in a conditional skill / rule that auto-loads on the same triggers the original rule served.

**Ownership:** Cursor Agent drafts as a T2 plan. Estimate ~4–6k tokens.

## 13. Author-Gate Seeds

```
AG_QUEUE_SEED: plan=plan-notion-registration-enforcement-c8f3a1 id=AG-W3-wave-start-chokepoint depends_on=P2.2 title="Confirm wave-start is the only pre-MCP chokepoint"
AG_QUEUE_SEED: plan=plan-notion-registration-enforcement-c8f3a1 id=AG-W5-fail-closed-default depends_on=P5.1 title="Should pre-commit T7u default to fail-closed or advisory"
AG_QUEUE_SEED: plan=plan-notion-registration-enforcement-c8f3a1 id=AG-W6-always-on-budget-impact depends_on=P6.1 title="Confirm §36 addition stays under always-on token budget"
```

## 14. Success Criteria (plan-level)

1. All 8 waves Status=✅ DONE.
2. Synthetic unregistered plan file → `wave_execution_state.py start` BLOCKED with correct message.
3. Registering the plan (post Notion row) → wave-start unblocked on next call.
4. NP1 + new PR1 gates both green on main.
5. Constitutional §36 live; `plan-registration-enforcement.md` discoverable via RULES_INDEX.
6. `AGENTS.md` auto-routing row upgraded from "should create Plans row" to "enforced by §36 + `check_plan_registration_freshness.py`".
7. Unit tests ≥95% line coverage on `_plan_registration.py`.
8. Weekly drift report runs clean (zero orphans either direction) on first execution.

## 15. References

- Constitutional: §24 (DEFERRED_SCOPE capture — pattern reuse), §25 (MCP serialization), §31 (SSOT folder routing — pattern reuse), §33 (always-on budget), §35 (AG queue drain — pattern reuse)
- Rules: `ssot-folder-enforcement.md`, `author-gate-queue-drain.md`, `deferred-scope-capture.md`
- AGENTS.md: Notion Workspace Map → Plans DB row · Auto-Routing Rules table
- Sibling gate: `ops_scripts/ci/check_notion_plans_ai_summary.py` (NP1)
- Incident: 2026-05-03 false-negative on `apps-runtime-domain-enforcement-a7e9d4` (plan **was** registered; Cursor Agent claimed otherwise without querying)
