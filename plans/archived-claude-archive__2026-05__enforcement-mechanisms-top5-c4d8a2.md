---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\enforcement-mechanisms-top5-c4d8a2.md'
original_relative_path: '_archive\\2026-05\\enforcement-mechanisms-top5-c4d8a2.md'
source_sha256: f68e9b5b1a4990a231d794d7cd7e5f515b12046c5df142fb4f80579f80e3c85a
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: enforcement-mechanisms-top5-c4d8a2
plan_type: governance
dod_exempt: false
---

# Top 5 Enforcement Mechanisms — Wave 2 Implementation

Implements the five highest-impact Notion/Cursor Agent enforcement gaps identified from prior session analysis: NP9 new-plan status enforcement, NP10 waiting-for completeness, MCP config schema validation, plan-wave lifecycle sync, and deferred scope capture compliance.

---

## Context (SCQA)

**Situation** — The repository has a mature enforcement stack with 40+ CI gates covering ADG, Author-Gate, apps_rg, OTEL, and plan structure. Key gates operational: NP2 (status canonical), NP1 (AI summary), PR1 (plan registration), PLAN-DOD (definition of done), AG-WIRE (hook wiring).

**Complication** — Five enforcement gaps remain unimplemented despite being specified in rules:
1. NP9: New plans can be created with non-"Not Started" statuses (no gate validates)
2. NP10: Plans in "Waiting" status lack mandatory "Waiting For" field (no gate validates)
3. MCP config: No schema validation for `.windsurf/mcp_config.json` (risk of silent breakage)
4. Wave lifecycle: No freshness check that wave markers sync to Notion Summary
5. Deferred scope: No validation that DEFERRED_SCOPE markers are present when plans mention deferred work

**Question** — How do we close these five gaps with minimal blast radius following the established "helper + hook + CI gate + tests" pattern?

**Answer** — Implement all five gates following SSOT patterns from prior plans (notion-plans-status-enforcement-7a1e2d, ssot-folder-enforcement-d4a7d9a, etc.): pure helpers in `.cursor/scripts/`, CI gates in `ops_scripts/ci/`, post-cursor-agent audits where applicable, registration in `run_contract_gates.py` assurance_gates list.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `.cursor/rules/notion-plans-taxonomy.md` | Defines NP9/NP10 requirements | ✅ Loaded |
| `ops_scripts/ci/run_contract_gates.py` | Verify gate registration pattern | ✅ Loaded |
| ADG SQLite snapshot | Check for existing gate patterns | 🔲 W1 |
| `.windsurf/mcp_config.json` | Current schema baseline | 🔲 W2 |
| `.cursor/plans/*.md` corpus | Deferred scope pattern analysis | 🔲 W5 |

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|--------|
| Wave 0 | 0 gates | Baseline verification — 4 of 5 gaps already exist | Pre-flight | ~2K ✅ |
| Wave 1 | 1 gate | MCP Config Schema Validation (NEW) | MCP-SCHEMA green | ~5K ✅ |
| Wave 2 | 1 fix | Deferred Scope CI Registration (GAP-5 close) | DEFER-CI green | ~1K ✅ |
| Wave 3 | 1 verify | Full CI sweep + regression check | All gates green | ~2K ✅ |
| Wave 4 | 1 harden | Fail-closed activation + test expansion | Hardened | ~2K ✅ |

**Total: ~10K tokens across 4 waves (extended from 2, completed)**

**Status tracking**: Notion Status flips "Not Started" → "In Progress" at Wave 1 start.

---

## Out Of Scope

- Modifying existing gates (NP2, PR1, etc.) — only new gates
- Frontend/UI changes to Notion (API-only)
- Pre-commit hook wiring (separate concern)
- Rule file frontmatter validation (deferred to future wave)
- Real-time cascade interception (post-cursor-agent audits only)

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | MCP Config Schema Gate | 2 files | New gate, 12 required servers, §27 compliance | ~3K | ✅ DONE |
| 1.2 | MCP Tests + Registration | 2 files | 27 test cases, CI registration | ~2K | ✅ DONE |
| 2.1 | Deferred Scope CI Registration | 1 file | Add --all mode, CI auto-detect, register in assurance_gates | ~0.5K | ✅ DONE |
| 3.1 | Full CI Verification Sweep | 1 run | Verify all gates pass in run_contract_gates.py | ~1K | ✅ DONE |
| 3.2 | Regression Test Check | 1 run | pytest full suite, zero regressions | ~1K | ✅ DONE |
| 4.1 | Fail-Closed Mode Activation | 2 gates | MCP-SCHEMA pass, DEFER exits 1 with 12 violations ✓ | ~1K | ✅ DONE |
| 4.2 | Test Coverage Expansion | 2 files | 5 edge case tests added (32 total) | ~1K | ✅ DONE |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-1: NP9 New-Plan Status Enforcement**
- [EXISTING] Gate `check_notion_plans_new_status.py` already implemented and registered as NP9
- Discovery: Fully operational with 24h window, bypass, and fail-closed modes

**GAP-2: NP10 Waiting-For Completeness**
- [EXISTING] Gate `check_notion_plans_waiting_for.py` already implemented and registered as NP10
- Discovery: Live-DB query with ERROR reporting for blank Waiting For fields

**GAP-3: MCP Config Schema Validation**
- [CLOSED THIS WAVE] Created `check_mcp_config_schema.py` — validates required servers, §27 key compliance, server structure
- 27 tests pass, registered in run_contract_gates.py as "MCP-SCHEMA (advisory)"

**GAP-4: Plan-Wave Lifecycle Sync Freshness**
- [EXISTING] Gate `check_plan_notion_wave_freshness.py` already implemented and registered as NP4
- Discovery: Drift detection between on-disk markers and Notion Summary

**GAP-5: Deferred Scope Capture Compliance**
- [CLOSED THIS WAVE] Added `--all` mode and CI auto-detection to `check_deferred_scope_markers.py`
- Registered in run_contract_gates.py assurance_gates as "DEFER (advisory baseline)"
- Baseline: 12 existing violations tracked, gate advisory by default

---

## Execution Plan

### Phase 1.1 — NP9 Helper + CI Gate
**Scope**: Create canonical status checker and new-plan detection gate

**Files**:
- `.cursor/scripts/_notion_plans_new_status_check.py` — helper with `decide_new_plan_status()`
- `ops_scripts/ci/check_notion_plans_new_status.py` — CI gate with 24h window logic

**Commands**:
```bash
# Create helper following _notion_plans_status_check.py pattern
cat > .cursor/scripts/_notion_plans_new_status_check.py << 'EOF'
"""Pure helper for NP9 new-plan status validation."""
CANONICAL_NEW_STATUSES = {"Not Started"}
NEW_PLAN_WINDOW_HOURS = 24
EOF

# Gate follows check_notion_plans_status_canonical.py pattern
```

**Acceptance**:
- Helper exposes `decide(db_row) -> Violation|None`
- Gate exits 0 when all plans <24h have Status="Not Started"
- Gate exits 1 in fail-closed mode with violations

### Phase 1.2 — NP9 Tests + Registration
**Scope**: Unit tests and run_contract_gates.py registration

**Files**:
- `tests/unit/windsurf_scripts/test_notion_plans_new_status_check.py`
- Update `ops_scripts/ci/run_contract_gates.py` assurance_gates list

**Acceptance**:
- 12+ test cases: within window OK, outside window exempt, non-Not Started flagged
- Registered as "NP9 New-Plan Status (advisory)"
- Bypass: `NOTION_PLANS_NEW_STATUS_BYPASS=1`
- Fail-closed: `NOTION_PLANS_NEW_STATUS_FAIL_CLOSED=1`

### Phase 2.1 — NP10 Helper + Audit Hook
**Scope**: Cross-field validation between Status and Waiting For

**Files**:
- `.cursor/scripts/_notion_plans_waiting_for_check.py` — helper
- Update `.cursor/scripts/post_cursor_agent_notion_plans_status_audit.py` — add WAITING_EMPTY_WAITING_FOR detection

**Acceptance**:
- Helper validates: Status="Waiting" implies Waiting For non-blank
- Post-cursor-agent audit logs violations to existing `notion_plans_status_violations.jsonl`
- Rejects "TBD", "unknown", empty string as invalid Waiting For values

### Phase 2.2 — NP10 CI Gate + Tests
**Scope**: Live-DB query gate and test surface

**Files**:
- `ops_scripts/ci/check_notion_plans_waiting_for.py` — queries Notion for Waiting rows
- `tests/unit/ops_scripts/ci/test_check_notion_plans_waiting_for.py`

**Acceptance**:
- Gate queries live DB via Notion API for Status="Waiting" rows
- Reports ERROR for any with blank/invalid Waiting For
- Advisory by default; fail-closed via `NOTION_PLANS_WAITING_FOR_FAIL_CLOSED=1`
- Registered as "NP10 Waiting-For Completeness (advisory)"

### Phase 3.1 — MCP Schema Definition
**Scope**: JSON Schema for mcp_config.json validation

**Files**:
- `.cursor/schemas/mcp_config.schema.json` — formal schema
- `.cursor/scripts/_mcp_config_validate.py` — pure validation helper

**Schema requirements**:
- `mcpServers` object with required keys: `GitKraken`, `adg_sqlite`, `memory`, `notion`
- Each server: `command`, `args` array, optional `env` object
- Stable server IDs preserved (per AGENTS.md Quick Reference)
- No unknown keys at root level

### Phase 3.2 — MCP Validator + CI Gate
**Scope**: Integration and CI registration

**Files**:
- `ops_scripts/ci/check_mcp_config_schema.py` — validates against schema
- `tests/unit/ops_scripts/ci/test_check_mcp_config_schema.py`

**Acceptance**:
- Gate validates current `.windsurf/mcp_config.json` against schema
- Fails if required servers missing or structure invalid
- Advisory by default; fail-closed via `MCP_CONFIG_SCHEMA_FAIL_CLOSED=1`
- Registered as "MCP-CONFIG schema validation (advisory)"

### Phase 4.1 — Wave Lifecycle Helper
**Scope**: Pattern matching for wave markers vs Notion Summary

**Files**:
- `.cursor/scripts/_wave_lifecycle_sync_check.py` — helper
- Parses `WAVE_START:`, `WAVE_COMPLETE:`, `PHASE_COMPLETE:` markers
- Parses Notion Summary column for `[Wave-Log <ts>] W{N} DONE` entries

**Acceptance**:
- Helper exposes `check_sync(plan_slug, notion_summary, disk_markers) -> DriftReport`
- Detects: marker present but not in Summary, Summary entry without marker
- Handles timestamp tolerance (±1 minute)

### Phase 4.2 — Wave Freshness Gate + Tests
**Scope**: CI gate comparing on-disk state to Notion

**Files**:
- `ops_scripts/ci/check_plan_notion_wave_freshness.py` — drift detection
- `tests/unit/ops_scripts/ci/test_check_plan_notion_wave_freshness.py`

**Acceptance**:
- Gate scans `.cursor/plans/*.md` for wave markers
- Queries Notion for corresponding plan rows
- Reports drift where markers don't match Summary entries
- Advisory by default; fail-closed via `PLAN_WAVE_FRESHNESS_FAIL_CLOSED=1`
- Registered as "NP4 Plan-Wave Freshness (advisory)"

### Phase 5.1 — Deferred Scope Scanner
**Scope**: Detect deferred work mentions and marker presence

**Files**:
- `.cursor/scripts/_deferred_scope_scanner.py` — helper

**Pattern matching**:
- Deferred indicators: "deferred", "future work", "out of scope", "we'll handle X later"
- Marker pattern: `DEFERRED_SCOPE:` line in same response
- Validates marker format: `DEFERRED_SCOPE: [P1-P5] <description> -> <tracking>`

### Phase 5.2 — Deferred Compliance Gate
**Scope**: CI gate validating marker compliance

**Files**:
- `ops_scripts/ci/check_deferred_scope_markers.py` — validates plans
- `tests/unit/ops_scripts/ci/test_check_deferred_scope_markers.py`

**Acceptance**:
- Gate scans `.cursor/plans/*.md` for deferred indicators
- Verifies corresponding `DEFERRED_SCOPE:` marker exists in file
- Reports violations where prose mentions deferral without marker
- Advisory by default; fail-closed via `DEFERRED_SCOPE_MARKER_FAIL_CLOSED=1`
- Registered as "DEFERRED_SCOPE marker compliance (advisory)"

---

## Rules

- All gates follow SSOT folder routing: helpers to `.cursor/scripts/`, gates to `ops_scripts/ci/`
- All gates have bypass env var and fail-closed env var
- All gates emit JSON reports to `artifacts/ci/<gate_name>.json`
- All gates have 8+ test cases following existing patterns
- All helpers are pure functions with no side effects
- Post-cursor-agent audits (where applicable) log to `artifacts/cursor/*_violations.jsonl`

---

## Success Criteria

- [ ] 5 new CI gates registered in run_contract_gates.py assurance_gates list
- [ ] All gates have bypass: `*_BYPASS=1` and fail-closed: `*_FAIL_CLOSED=1` env vars
- [ ] All gates have 8+ passing unit tests
- [ ] NP9 gate detects non-"Not Started" new plans within 24h window
- [ ] NP10 gate detects blank "Waiting For" on "Waiting" status plans
- [ ] MCP gate validates required servers exist in mcp_config.json
- [ ] Wave freshness gate detects drift between markers and Notion Summary
- [ ] Deferred scope gate validates DEFERRED_SCOPE: markers present

---

## Implementation Commands

```bash
# W1 — NP9 New-Plan Status
python ops_scripts/ci/check_notion_plans_new_status.py --help
python ops_scripts/ci/check_notion_plans_new_status.py --query-notion
NOTION_PLANS_NEW_STATUS_FAIL_CLOSED=1 python ops_scripts/ci/check_notion_plans_new_status.py

# W2 — NP10 Waiting-For
python ops_scripts/ci/check_notion_plans_waiting_for.py --query-notion
NOTION_PLANS_WAITING_FOR_FAIL_CLOSED=1 python ops_scripts/ci/check_notion_plans_waiting_for.py

# W3 — MCP Config
python ops_scripts/ci/check_mcp_config_schema.py
MCP_CONFIG_SCHEMA_FAIL_CLOSED=1 python ops_scripts/ci/check_mcp_config_schema.py

# W4 — Wave Lifecycle
python ops_scripts/ci/check_plan_notion_wave_freshness.py
PLAN_WAVE_FRESHNESS_FAIL_CLOSED=1 python ops_scripts/ci/check_plan_notion_wave_freshness.py

# W5 — Deferred Scope
python ops_scripts/ci/check_deferred_scope_markers.py
DEFERRED_SCOPE_MARKER_FAIL_CLOSED=1 python ops_scripts/ci/check_deferred_scope_markers.py

# Full sweep
python ops_scripts/ci/run_contract_gates.py
```

---

## Rollback Strategy

If gates are too noisy:
1. Set `*_FAIL_CLOSED=0` (advisory mode) for affected gates
2. Add bypass markers to `Summary` field: `[[bypass:NP9]]`, `[[bypass:NP10]]`
3. If fundamental issue: remove gate from run_contract_gates.py assurance_gates list
4. Revert helper changes — pure functions, no side effects on revert

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Gates implemented | 5 | `grep -c "advisory)" ops_scripts/ci/run_contract_gates.py` increases by 5 |
| Test coverage | 40+ cases | `pytest tests/unit/windsurf_scripts/test_notion_plans_new_status_check.py` etc. all pass |
| NP9 detection rate | >95% | Create test plan with "Lower Priority" status, verify flag within 24h |
| NP10 false positive | <5% | Manual audit of 20 "Waiting" plans, verify all true positives |
| MCP schema coverage | 100% | All 10 MCP servers from AGENTS.md validated |
| Wave drift detection | <5 min latency | Markers emitted, gate detects within 5 minutes |
| Deferred marker compliance | 90%+ | Scan all `.cursor/plans/*.md`, verify 90% have markers where needed |

---

## Definition of Done

| # | Criterion | Verification command / evidence | Status |
|---|---|---|---|
| DoD-1 | MCP Config Schema gate operational | `python ops_scripts/ci/check_mcp_config_schema.py` exits 0, shows 12/12 required servers | ✅ |
| DoD-2 | Smoke run: MCP gate exits 0 on clean baseline | `python ops_scripts/ci/check_mcp_config_schema.py` exits 0 with valid config | ✅ |
| DoD-3 | 27+ unit tests, zero regressions | `pytest tests/unit/ops_scripts/ci/test_check_mcp_config_schema.py` shows 27 pass | ✅ |
| DoD-4 | Gate registered in CI | `grep "MCP-SCHEMA" ops_scripts/ci/run_contract_gates.py` shows registration | ✅ |
| DoD-5 | Notion Plans DB row final | Notion Status = Completed, all 4 waves done | ✅ |

**Verification-vs-Deferral table**:

| Item | Why deferred | Tracked in |
|---|---|---|
| Real Notion API integration tests | Requires live token; mock-based unit tests only | Deferred plan: enforcement-deferred-followup-c4d8a2 |
| Rule frontmatter validation | Separate concern; rule schema not yet formalized | Deferred plan: enforcement-deferred-followup-c4d8a2 |
| Pre-commit hook wiring | CI-only rollout first; local pre-commit after burn-in | Deferred plan: enforcement-deferred-followup-c4d8a2 |

**Deferred Scope Plan**: `enforcement-deferred-followup-c4d8a2.md` (Notion: 35c27693-f55c-812a-aed5-c100587234d8)

---

## Cursor Agent Alignment Checks

- Keep always-on rules lean; place detailed procedures in skills or workflows.
- Retrieve local or scoped evidence before synthesis.
- Prefer exact or structural matches before broad semantic expansion.
- For high-risk outputs, extract evidence or quotes before summarizing.
- Reserve deterministic enforcement for hooks or scripts, not template prose.

---

AG_QUEUE_SEED: plan=enforcement-mechanisms-top5-c4d8a2 id=w1-start depends_on=none title="W1 NP9 gate — start with helper pattern"
AG_QUEUE_SEED: plan=enforcement-mechanisms-top5-c4d8a2 id=w2-start depends_on=w1-complete title="W2 NP10 gate — waiting-for completeness"
AG_QUEUE_SEED: plan=enforcement-mechanisms-top5-c4d8a2 id=w3-start depends_on=w2-complete title="W3 MCP config validation"
AG_QUEUE_SEED: plan=enforcement-mechanisms-top5-c4d8a2 id=w4-start depends_on=w3-complete title="W4 Wave lifecycle sync"
AG_QUEUE_SEED: plan=enforcement-mechanisms-top5-c4d8a2 id=w5-start depends_on=w4-complete title="W5 Deferred scope compliance"
