---
plan_id: plan-markdown-update-enforcement-a7d4e1
plan_type: governance
authored_at: 2026-05-12
last_updated: 2026-05-12T08:50Z  # W4 complete: Phase-Level Summary updater + 35 total tests
status: In Progress
---

# Plan Markdown Update Enforcement — Scope Expansion Authorization

Establish hooks, rules, CI gates, and template discipline to ensure markdown plans are **living documents** when scope is discovered during execution — with **explicit authorization gates** that prevent "plan update" from becoming retroactive permission for uncontrolled scope drift.

---

## Context (SCQA)

- **Situation** — The current plan infrastructure creates comprehensive pre-execution plans with Wave Structure tables, Phase-Level Summary tables, Gap Registers, and Definition of Done sections. The `post_cascade_wave_lifecycle_capture.py` hook updates wave status cells (🔲→🔄→✅) when `WAVE_COMPLETE` markers are emitted. However, plans remain static documents — they don't reflect scope expansions, newly discovered gaps, or expanded DoD criteria that emerge during execution.

- **Complication** — During the `apps-rg-exit-gate-fix-g24-hardening-d7c4b1` session, W3 revealed new gaps (G22 diagnostics, G28 receipt ordering) that required expanding from 4→6 waves and adding W5.P8, W5.P9, W6.P10 phases. While this was documented, the pattern risks becoming: "discover gap → do work → retroactively update plan." This is scope drift with documentation, not authorization. Without an **authorization gate** between discovery and execution, plans become post-hoc rationalizations rather than governing constraints.

- **Question** — How do we enforce that plans are living documents **with explicit authorization discipline** — requiring discovery markers, authorization decisions, and documented justification before scope expansion proceeds?

- **Answer** — (W1) Create a governance rule mandating the four-step scope expansion protocol: **DISCOVERED_SCOPE** → **AUTHORIZATION_DECISION** → **plan file updates** → **SCOPE_EXPANSION** marker. (W2) Build a helper to parse authorization markers and detect unauthorized drift. (W3) Create a post-cascade hook that **blocks** (advisory → strict mode) when substantial work occurs without preceding authorization. (W4) Extend updater for Phase-Level Summary. (W5) Add CI gate detecting unauthorized expansions. (W6) Update template with **Scope Expansion Authorization** section.

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
| Post-cascade hook | Warn when work >3 files without preceding authorization | Block (exit 2) |
| CI gate | Flag unauthorized expansions in weekly report | Fail build |
| Pre-write gate | — | Block writes outside plan scope without authorization |

Bypass (emergency only): `SCOPE_AUTHORIZATION_BYPASS=1`

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `.windsurf/plans/apps-rg-exit-gate-fix-g24-hardening-d7c4b1.md` | Example of successful plan update pattern after scope expansion | ✅ Reference |
| `.windsurf/scripts/post_cascade_wave_lifecycle_capture.py` | Existing wave status update mechanism | ✅ Read |
| `tools/windsurf/_plan_wave_table_updater.py` | Current table update logic (waves only) | ✅ Read |
| `.windsurf/templates/execution-plan-template.md` | Template to extend with scope expansion guidance | ✅ Read |
| `.windsurf/hooks.json` | Hook registration point | ✅ Read |
| `.windsurf/rules/plan-location.md` | Sibling rule for pattern reference | ✅ Read |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|------|-----------|-------|-------------|--------|
| W1 | P1 | Rule with four-step authorization protocol (DISCOVERED_SCOPE → AUTHORIZATION_DECISION → updates → SCOPE_EXPANSION) | ~1,200 | ✅ DONE |
| W2 | P2 | Helper parsing auth markers + `AuthorizationState.is_authorized_for_scope()` | ~800 | ✅ DONE |
| W3 | P3 | Post-cascade hook: advisory/strict mode unauthorized drift detection | ~1,000 | ✅ DONE |
| W4 | P4 | Updater: Phase-Level Summary + `last_updated` refresh | ~1,000 | ✅ DONE |
| W5 | P5 | CI gate: unauthorized expansion detection + stale plan detection | ~800 | 🔲 TODO |
| W6 | P6 | Template: Scope Expansion Authorization section + 20+ tests | ~800 | 🔲 TODO |

**Total: ~5,600 tokens across 6 waves**

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | Hardened rule with authorization protocol | `.windsurf/rules/plan-update-enforcement.md` | Rule defines four-step discipline, 4 decision types (ACCEPTED/DEFERRED/SPLIT_TO_NEW_PLAN/REJECTED), required updates checklist, fail-closed enforcement layers, negative-control retroactive detection, marker recency check | ~1,200 | ✅ DONE |
| W2.P2 | Scope expansion check helper with auth parsing | `.windsurf/scripts/_plan_scope_expansion_check.py` | Parse all 3 marker types; `AuthorizationState` with `is_authorized_for_scope()`; retroactive detection; 4 decision types; recency window; 32 unit tests passing | ~800 | ✅ DONE |
| W3.P3 | Post-cascade scope authorization audit hook | `.windsurf/scripts/post_cascade_plan_scope_audit.py` | Advisory → strict mode; warn/block when >3 files modified without preceding AUTHORIZATION_DECISION; check auth marker recency; logs to JSONL; 24 unit tests passing | ~1,000 | ✅ DONE |
| W4.P4 | Updater extension for Phase tables | `tools/windsurf/_plan_wave_table_updater.py` | Add `_update_phase_in_plan()`; handle phase status cells (🔄→✅) for W<N>.P<M> IDs; refresh `last_updated` on change; 35 total tests (27 wave + 8 phase) | ~1,000 | ✅ DONE |
| W5.P5 | Plan freshness + unauthorized expansion CI gate | `ops_scripts/ci/check_plan_freshness.py` | Detect stale `last_updated`; detect unauthorized scope expansions (work evidence without auth markers); advisory → fail-closed | ~800 | 🔲 TODO |
| W6.P6 | Template + hooks + tests for authorization | `.windsurf/templates/execution-plan-template.md`, `.windsurf/hooks.json`, `tests/unit/windsurf_scripts/test_plan_scope_expansion*.py` | Template "## Scope Expansion Authorization" section with four-step protocol; hook registration; 20+ unit tests | ~800 | 🔲 TODO |

---

## Gap Register

| ID | Description | Severity | Wave | Status |
|---|---|---|---|---|
| GAP-1 | Phase-Level Summary table not updated by lifecycle capture | Medium | W4.P4 | ✅ Closed |
| GAP-2 | No CI gate detecting stale plans (old `last_updated` + active status) | Medium | W5.P5 | 🔲 Open |
| GAP-3 | No authorization protocol for scope expansion — risk of retroactive plan updates | **High** | W1.P1 | 🔲 Open |
| GAP-4 | No mechanism to detect unauthorized scope drift (work before authorization) | **High** | W3.P3 | ✅ Closed |
| GAP-5 | Plan template lacks "Scope Expansion Authorization" section | Medium | W6.P6 | 🔲 Open |

---

## Definition of Done

| ID | Criterion | Verification | Status |
|---|---|---|---|
| DoD-1 | Rule `plan-update-enforcement.md` exists with four-step authorization protocol | `grep -q "DISCOVERED_SCOPE.*AUTHORIZATION_DECISION" .windsurf/rules/plan-update-enforcement.md` | ✅ |
| DoD-2 | Helper exports `AuthorizationState` with `is_authorized_for_scope()` method | `pytest tests/unit/windsurf_scripts/test_plan_scope_expansion_check.py -v` → 32 passed | ✅ |
| DoD-3 | Hook `post_cascade_plan_scope_audit.py` detects unauthorized work | `pytest tests/unit/windsurf_scripts/test_post_cascade_plan_scope_audit.py -v` → 24 passed | ✅ |
| DoD-4 | Hook strict mode blocks writes without authorization | `test_strict_blocks_unauthorized` passes: strict mode → exit 2 | ✅ |
| DoD-5 | Updater handles Phase-Level Summary AND refreshes `last_updated` | 8 phase tests pass incl. `test_phase_update_refreshes_last_updated` | ✅ |
| DoD-6 | CI gate detects unauthorized scope expansions | Gate flags work evidence without DISCOVERED_SCOPE → AUTHORIZATION_DECISION chain | 🔲 |
| DoD-7 | Plan template includes "## Scope Expansion Authorization" section | Template has four-step protocol, decision vocab, required updates checklist | 🔲 |
| DoD-8 | All 20+ unit tests pass | `pytest tests/unit/windsurf_scripts/test_plan_scope_expansion*.py -v` → 65 passed (41 W2 + 24 W3) | ✅ |
| DoD-9 | This plan uses its own discipline | Has DISCOVERED_SCOPE, AUTHORIZATION_DECISION, SCOPE_EXPANSION markers if expanded | 🔲 |
| DoD-10 | **Negative-control: retroactive authorization blocked** | `test_retroactive_detected_advisory` + `test_retroactive_blocks_strict` pass → `RETROACTIVE_AUTHORIZATION_DETECTED` fires correctly | ✅ |

---

## Rollback Strategy

If enforcement is too noisy:
1. Set `PLAN_SCOPE_AUDIT_BYPASS=1` — disables post-cascade hook entirely
2. Set `PLAN_SCOPE_AUDIT_STRICT=0` — keeps advisory mode only (default)
3. Set `SCOPE_AUTHORIZATION_BYPASS=1` — emergency override for all authorization checks
4. Set `PLAN_FRESHNESS_BYPASS=1` — disables CI gate staleness check
5. Revert hooks.json to remove the hook entry
6. Archive rule to `.windsurf/rules/_archive/`

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
- 2026-05-12 08:35Z: **W1 COMPLETE** — Rule `.windsurf/rules/plan-update-enforcement.md` implemented with four-step authorization protocol
- 2026-05-12 08:40Z: **W2 COMPLETE** — Helper `.windsurf/scripts/_plan_scope_expansion_check.py` + 32 unit tests passing
  - Exports: `AuthorizationState`, parse functions, retroactive detection
  - Tests cover: valid expansion, missing markers, 4 decision types, retroactive detection, recency window, malformed markers, multiple discoveries
- 2026-05-12 08:45Z: **W3 COMPLETE** — Post-cascade hook `.windsurf/scripts/post_cascade_plan_scope_audit.py` + 24 unit tests passing
  - Uses W2 `check_scope_authorization()` API — zero marker parsing reimplemented
  - Advisory mode: warnings + JSONL logging; Strict mode: exit 2 on unauthorized drift
  - Detects: MISSING_DISCOVERED_SCOPE, MISSING_AUTHORIZATION_DECISION, RETROACTIVE_AUTHORIZATION_DETECTED
  - Configurable: MIN_FILES_FOR_AUDIT (default 3), AUTH_MARKER_RECENCY_SEC (default 300), PLAN_SCOPE_AUDIT_STRICT, PLAN_SCOPE_AUDIT_BYPASS
- 2026-05-12 08:50Z: **W4 COMPLETE** — Phase-Level Summary updater in `tools/windsurf/_plan_wave_table_updater.py`
  - New `_update_phase_in_plan()` function for phase status cells (W1.P1, W5.P8, W10.P12)
  - Status transitions: 🔲 TODO → 🔄 IN PROGRESS → ✅ DONE
  - `last_updated` auto-refreshes on phase changes
  - All 27 existing wave tests pass + 8 new phase tests = 35 total tests green
