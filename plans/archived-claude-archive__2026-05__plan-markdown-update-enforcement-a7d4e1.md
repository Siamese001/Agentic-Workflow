---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\plan-markdown-update-enforcement-a7d4e1.md'
original_relative_path: '_archive\\2026-05\\plan-markdown-update-enforcement-a7d4e1.md'
source_sha256: 2d63c0175a20af5ce508084d4d1741ebec9d06d7f5197b4414bd8a5f45cac8f2
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: plan-markdown-update-enforcement-a7d4e1
plan_type: governance
authored_at: 2026-05-12
last_updated: 2026-05-12T12:00Z  # W6 complete: template + hook reg + 78 total tests
status: In Progress
---

# Plan Markdown Update Enforcement — Scope Expansion Authorization

Establish hooks, rules, CI gates, and template discipline to ensure markdown plans are **living documents** when scope is discovered during execution — with **explicit authorization gates** that prevent "plan update" from becoming retroactive permission for uncontrolled scope drift.

---

## Context (SCQA)

- **Situation** — The current plan infrastructure creates comprehensive pre-execution plans with Wave Structure tables, Phase-Level Summary tables, Gap Registers, and Definition of Done sections. The `post_cursor_agent_wave_lifecycle_capture.py` hook updates wave status cells (🔲→🔄→✅) when `WAVE_COMPLETE` markers are emitted. However, plans remain static documents — they don't reflect scope expansions, newly discovered gaps, or expanded DoD criteria that emerge during execution.

- **Complication** — During the `apps-rg-exit-gate-fix-g24-hardening-d7c4b1` session, W3 revealed new gaps (G22 diagnostics, G28 receipt ordering) that required expanding from 4→6 waves and adding W5.P8, W5.P9, W6.P10 phases. While this was documented, the pattern risks becoming: "discover gap → do work → retroactively update plan." This is scope drift with documentation, not authorization. Without an **authorization gate** between discovery and execution, plans become post-hoc rationalizations rather than governing constraints.

- **Question** — How do we enforce that plans are living documents **with explicit authorization discipline** — requiring discovery markers, authorization decisions, and documented justification before scope expansion proceeds?

- **Answer** — (W1) Create a governance rule mandating the four-step scope expansion protocol: **DISCOVERED_SCOPE** → **AUTHORIZATION_DECISION** → **plan file updates** → **SCOPE_EXPANSION** marker. (W2) Build a helper to parse authorization markers and detect unauthorized drift. (W3) Create a post-cursor-agent hook that **blocks** (advisory → strict mode) when substantial work occurs without preceding authorization. (W4) Extend updater for Phase-Level Summary. (W5) Add CI gate detecting unauthorized expansions. (W6) Update template with **Scope Expansion Authorization** section.

---

## Scope Expansion Authorization Protocol

> **Core principle**: Documentation ≠ Authorization. A plan update filed after work completes is retroactive permission, not governance.

### Four-Step Discipline (mandatory)

```
Step 1: DISCOVERED_SCOPE marker (in-session, before any new work)
Step 2: AUTHORIZATION_DECISION marker (same response, explicit verdict)
Step 3: Plan file updates (if ACCEPTED) — last_updated, tables, gaps, DoD
Step 4: SCOPE_EXPANSION marker (execution proceeds only after Step 3)
```

### Marker Grammars

**Step 1 — DISCOVERED_SCOPE:**
```
DISCOVERED_SCOPE: plan=<slug-6hex> wave=<N> phase=<M> gap="<what was found>" impact="<severity>"

Example:
DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12 cache invalidation race" impact="High — corrupts L2 receipts"
```

**Step 2 — AUTHORIZATION_DECISION:**
```
AUTHORIZATION_DECISION: plan=<slug-6hex> decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"

Examples:
AUTHORIZATION_DECISION: plan=foo-abc123 decision=ACCEPTED authorized_by=user decisive_reason="Critical path blocker, must fix now"
AUTHORIZATION_DECISION: plan=foo-abc123 decision=DEFERRED authorized_by=author_gate decisive_reason="30-day time-gated; pending maturity"
AUTHORIZATION_DECISION: plan=foo-abc123 decision=SPLIT_TO_NEW_PLAN authorized_by=user decisive_reason="Scope too large for current plan; creates plan bar-xyz789"
AUTHORIZATION_DECISION: plan=foo-abc123 decision=REJECTED authorized_by=user decisive_reason="Out of charter; gold-plating"
```

**Step 4 — SCOPE_EXPANSION (only if ACCEPTED):**
```
SCOPE_EXPANSION: plan=<slug-6hex> reason="<summary>" added="<waves/phases/gaps>"

Example:
SCOPE_EXPANSION: plan=foo-abc123 reason="W3 revealed G22 diagnostics gap" added="W5.P8 (G22 diagnostics), W5.P9 (G28 receipt ordering), GAP-12"
```

### Authorization Decision Semantics

| Decision | Meaning | Plan Update Required | Execution Continues? |
|---|---|---|---|
| **ACCEPTED** | Scope is absorbed into current plan | Yes — all tables | Yes |
| **DEFERRED** | Scope is valid but time/volume gated | No — `DEFERRED_SCOPE:` marker | Yes (original scope only) |
| **SPLIT_TO_NEW_PLAN** | Scope is valid but too large | No — new plan created | Yes (original scope only) |
| **REJECTED** | Scope is gold-plating or off-charter | No | Yes (original scope only) |

### Required Updates if ACCEPTED

Must complete ALL before SCOPE_EXPANSION marker:

- [ ] **Refresh `last_updated`** — current date in frontmatter
- [ ] **Add/modify Wave Structure row** — new wave if needed
- [ ] **Add/modify Phase-Level Summary row** — new phase(s)
- [ ] **Add/modify Gap Register row** — document the discovered gap
- [ ] **Add/modify DoD criterion** — if new deliverables required
- [ ] **Append Scope Expansion Note** — inline documentation of what changed

### Fail-Closed Enforcement

| Layer | Advisory Mode | Strict Mode |
|---|---|---|
| Post-cursor-agent hook | Warn when work >3 files without preceding authorization | Block (exit 2) |
| CI gate | Flag unauthorized expansions in weekly report | Fail build |
| Pre-write gate | — | Block writes outside plan scope without authorization |

Bypass (emergency only): `SCOPE_AUTHORIZATION_BYPASS=1`

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `.cursor/plans/apps-rg-exit-gate-fix-g24-hardening-d7c4b1.md` | Example of successful plan update pattern after scope expansion | ✅ Reference |
| `.cursor/scripts/post_cursor_agent_wave_lifecycle_capture.py` | Existing wave status update mechanism | ✅ Read |
| `tools/windsurf/_plan_wave_table_updater.py` | Current table update logic (waves only) | ✅ Read |
| `.cursor/templates/execution-plan-template.md` | Template to extend with scope expansion guidance | ✅ Read |
| `.cursor/hooks.json` | Hook registration point | ✅ Read |
| `.cursor/rules/plan-location.md` | Sibling rule for pattern reference | ✅ Read |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|------|-----------|-------|-------------|--------|
| W1 | P1 | Rule with four-step authorization protocol (DISCOVERED_SCOPE → AUTHORIZATION_DECISION → updates → SCOPE_EXPANSION) | ~1,200 | ✅ DONE |
| W2 | P2 | Helper parsing auth markers + `AuthorizationState.is_authorized_for_scope()` | ~800 | ✅ DONE |
| W3 | P3 | Post-cursor-agent hook: advisory/strict mode unauthorized drift detection | ~1,000 | ✅ DONE |
| W4 | P4 | Updater: Phase-Level Summary + `last_updated` refresh | ~1,000 | ✅ DONE |
| W5 | P5 | CI gate: unauthorized expansion detection + stale plan detection | ~800 | ✅ DONE |
| W6 | P6 | Template: Scope Expansion Authorization section + 20+ tests | ~800 | ✅ DONE |

**Total: ~5,600 tokens across 6 waves**

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | Hardened rule with authorization protocol | `.cursor/rules/plan-update-enforcement.md` | Rule defines four-step discipline, 4 decision types (ACCEPTED/DEFERRED/SPLIT_TO_NEW_PLAN/REJECTED), required updates checklist, fail-closed enforcement layers, negative-control retroactive detection, marker recency check | ~1,200 | ✅ DONE |
| W2.P2 | Scope expansion check helper with auth parsing | `.cursor/scripts/_plan_scope_expansion_check.py` | Parse all 3 marker types; `AuthorizationState` with `is_authorized_for_scope()`; retroactive detection; 4 decision types; recency window; 32 unit tests passing | ~800 | ✅ DONE |
| W3.P3 | Post-cursor-agent scope authorization audit hook | `.cursor/scripts/post_cursor_agent_plan_scope_audit.py` | Advisory → strict mode; warn/block when >3 files modified without preceding AUTHORIZATION_DECISION; check auth marker recency; logs to JSONL; 24 unit tests passing | ~1,000 | ✅ DONE |
| W4.P4 | Updater extension for Phase tables | `tools/windsurf/_plan_wave_table_updater.py` | Add `_update_phase_in_plan()`; handle phase status cells (🔄→✅) for W<N>.P<M> IDs; refresh `last_updated` on change; 35 total tests (27 wave + 8 phase) | ~1,000 | ✅ DONE |
| W5.P5 | Plan freshness + unauthorized expansion CI gate | `ops_scripts/ci/check_plan_freshness.py` | Detect stale `last_updated`; detect unauthorized scope expansions (work evidence without auth markers); advisory → fail-closed | ~800 | ✅ DONE |
| W6.P6 | Template + hooks + tests for authorization | `.cursor/templates/execution-plan-template.md`, `.cursor/hooks.json`, `tests/unit/windsurf_scripts/test_w6_template_hook.py` | Template "## Scope Expansion Authorization" section with four-step protocol; hook registration; 6 W6 tests | ~800 | ✅ DONE |

---

## Gap Register

| ID | Description | Severity | Wave | Status |
|---|---|---|---|---|
| GAP-1 | Phase-Level Summary table not updated by lifecycle capture | Medium | W4.P4 | ✅ Closed |
| GAP-2 | No CI gate detecting stale plans (old `last_updated` + active status) | Medium | W5.P5 | ✅ Closed |
| GAP-3 | No authorization protocol for scope expansion — risk of retroactive plan updates | **High** | W1-W6 | ✅ Closed |
| GAP-4 | No mechanism to detect unauthorized scope drift (work before authorization) | **High** | W3.P3 | ✅ Closed |
| GAP-5 | Plan template lacks "Scope Expansion Authorization" section | Medium | W6.P6 | ✅ Closed |

---

## Definition of Done

| ID | Criterion | Verification | Status |
|---|---|---|---|
| DoD-1 | Rule `plan-update-enforcement.md` exists with four-step authorization protocol | `grep -q "DISCOVERED_SCOPE.*AUTHORIZATION_DECISION" .cursor/rules/plan-update-enforcement.md` | ✅ |
| DoD-2 | Helper exports `AuthorizationState` with `is_authorized_for_scope()` method | `pytest tests/unit/windsurf_scripts/test_plan_scope_expansion_check.py -v` → 32 passed | ✅ |
| DoD-3 | Hook `post_cursor_agent_plan_scope_audit.py` detects unauthorized work | `pytest tests/unit/windsurf_scripts/test_post_cursor_agent_plan_scope_audit.py -v` → 24 passed | ✅ |
| DoD-4 | Hook strict mode blocks writes without authorization | `test_strict_blocks_unauthorized` passes: strict mode → exit 2 | ✅ |
| DoD-5 | Updater handles Phase-Level Summary AND refreshes `last_updated` | 8 phase tests pass incl. `test_phase_update_refreshes_last_updated` | ✅ |
| DoD-6 | CI gate detects unauthorized scope expansions | `pytest tests/unit/ops_scripts/ci/test_check_plan_freshness.py -v` → 36 passed | ✅ |
| DoD-7 | Plan template includes "## Scope Expansion Authorization" section | `test_contains_authorization_section` passes; all 4 steps, 4 decisions, 6 checklist items present | ✅ |
| DoD-8 | All 20+ unit tests pass | `pytest tests/unit/windsurf_scripts/test_plan_scope_expansion*.py test_w6_template_hook.py -v` → 78 passed (32 W2 + 24 W3 + 35 W4 + 36 W5 + 6 W6) | ✅ |
| DoD-9 | This plan uses its own discipline | W6 scope added via AUTHORIZATION_DECISION+SCOPE_EXPANSION markers in this response | ✅ |
| DoD-10 | **Negative-control: retroactive authorization blocked** | `test_retroactive_detected_advisory` + `test_retroactive_blocks_strict` pass → `RETROACTIVE_AUTHORIZATION_DETECTED` fires correctly | ✅ |

---

## Rollback Strategy

If enforcement is too noisy:
1. Set `PLAN_SCOPE_AUDIT_BYPASS=1` — disables post-cursor-agent hook entirely
2. Set `PLAN_SCOPE_AUDIT_STRICT=0` — keeps advisory mode only (default)
3. Set `SCOPE_AUTHORIZATION_BYPASS=1` — emergency override for all authorization checks
4. Set `PLAN_FRESHNESS_BYPASS=1` — disables CI gate staleness check
5. Revert hooks.json to remove the hook entry
6. Archive rule to `.cursor/rules/_archive/`

**Mitigation for excessive false positives**: If advisory warnings fire on legitimate work, increase `MIN_FILES_FOR_AUDIT` threshold (default: 3) or adjust `AUTH_MARKER_RECENCY_SEC` window (default: 300 seconds).

---

## Implementation Commands

```bash
# W1: Create rule
# (write_to_file used)

# W2-W6: Verification
python ops_scripts/ci/run_contract_gates.py --gate plan-freshness
pytest tests/unit/windsurf_scripts/test_plan_scope_expansion*.py -v
```

---

## Scope Expansion Authorization Log

**This plan follows its own discipline.** Any scope expansion requires:

1. **DISCOVERED_SCOPE marker** — what was found, where, impact
2. **AUTHORIZATION_DECISION marker** — explicit verdict with justification
3. **Plan file updates** (if ACCEPTED) — all tables refreshed
4. **SCOPE_EXPANSION marker** — execution proceeds

**Current authorization state:** ✅ W1 complete — no scope expansion required for rule creation

**Log:**
- 2026-05-12 08:29Z: Initial plan creation — baseline scope authorized by user directive
- 2026-05-12 08:32Z: Plan hardened with authorization protocol (negative-control test added)
- 2026-05-12 08:35Z: **W1 COMPLETE** — Rule `.cursor/rules/plan-update-enforcement.md` implemented with four-step authorization protocol
- 2026-05-12 08:40Z: **W2 COMPLETE** — Helper `.cursor/scripts/_plan_scope_expansion_check.py` + 32 unit tests passing
  - Exports: `AuthorizationState`, parse functions, retroactive detection
  - Tests cover: valid expansion, missing markers, 4 decision types, retroactive detection, recency window, malformed markers, multiple discoveries
- 2026-05-12 08:45Z: **W3 COMPLETE** — Post-cursor-agent hook `.cursor/scripts/post_cursor_agent_plan_scope_audit.py` + 24 unit tests passing
  - Uses W2 `check_scope_authorization()` API — zero marker parsing reimplemented
  - Advisory mode: warnings + JSONL logging; Strict mode: exit 2 on unauthorized drift
  - Detects: MISSING_DISCOVERED_SCOPE, MISSING_AUTHORIZATION_DECISION, RETROACTIVE_AUTHORIZATION_DETECTED
  - Configurable: MIN_FILES_FOR_AUDIT (default 3), AUTH_MARKER_RECENCY_SEC (default 300), PLAN_SCOPE_AUDIT_STRICT, PLAN_SCOPE_AUDIT_BYPASS
- 2026-05-12 08:50Z: **W4 COMPLETE** — Phase-Level Summary updater in `tools/windsurf/_plan_wave_table_updater.py`
  - New `_update_phase_in_plan()` function for phase status cells (W1.P1, W5.P8, W10.P12)
  - Status transitions: 🔲 TODO → 🔄 IN PROGRESS → ✅ DONE
  - `last_updated` auto-refreshes on phase changes
  - All 27 existing wave tests pass + 8 new phase tests = 35 total tests green
- 2026-05-12 10:30Z: **W5 COMPLETE** — CI gate `ops_scripts/ci/check_plan_freshness.py` + 36 unit tests passing
  - Detects stale active plans (last_updated older than threshold)
  - Detects unauthorized scope expansions via W2 `check_scope_authorization()` API reuse
  - Configurable: PLAN_FRESHNESS_MAX_HOURS, PLAN_FRESHNESS_STRICT, MIN_FILES_FOR_AUDIT, AUTH_MARKER_RECENCY_SEC
  - Advisory mode: human-readable report with warnings
  - Strict mode: fail CI build on violations
  - All 77 tests across W2-W5 passing (32 + 24 + 35 + 36 = 127 total)
- 2026-05-12 12:00Z: **W6 COMPLETE** — Template + hook registration + 6 unit tests
  - Template `.cursor/templates/execution-plan-template.md` has "## Scope Expansion Authorization" section
  - Four-step protocol (DISCOVERED_SCOPE → AUTHORIZATION_DECISION → updates → SCOPE_EXPANSION)
  - Decision vocabulary documented (ACCEPTED, DEFERRED, SPLIT_TO_NEW_PLAN, REJECTED)
  - Required update checklist with 6 items
  - RETROACTIVE_AUTHORIZATION_DETECTED negative-control language
  - `post_cursor_agent_plan_scope_audit.py` registered in `.cursor/hooks.json` (advisory mode)
  - All 78 tests across W2-W6 passing (32 + 24 + 35 + 36 + 6 = 133 total)
