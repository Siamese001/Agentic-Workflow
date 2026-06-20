---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\notion-sync-enforcement-hardening-f5a2c1.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\notion-sync-enforcement-hardening-f5a2c1.md'
source_sha256: d965fe88061c010c8c20adc999b5d70181aafc449376891a777d8229c2dda944
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: notion-sync-enforcement-hardening-f5a2c1
plan_type: governance
# governance: gates, schemas, CI, rule changes — ADG graph-layer evidence skipped per §22
dod_exempt: false
---

# Notion Sync Enforcement Hardening — Bidirectional Consistency & Failure Recovery

Closes enforcement gaps in Cascade→Notion write pipeline: adds bidirectional sync validation, automatic retry with backoff, conflict detection, and sync health observability. Aligns with constitutional §25 (MCP serialization), §36 (plan registration), and existing NP1-NP10 gate family.

---

## Context (SCQA)

**Situation**: The current Notion integration has strong write-time validation (NP2 status taxonomy, NP9 registration, NP10 Waiting For) and post-cascade audits, but operates as a unidirectional "fire-and-forget" pipeline. Wave lifecycle writes via `wave_lifecycle_writer.py` are fail-soft (log + exit 0 on HTTP error), with no retry, no reconciliation, and no detection of external Notion changes that create drift from on-disk state.

**Complication**: Production incidents reveal three failure modes: (1) Notion writes fail silently during high-volume operations (rate limits, transient 5xx) and remain failed because no retry exists; (2) manual edits in Notion UI create drift that Cascade never detects; (3) bulk operations (e.g., retiring 50 plans) are slow and brittle because no batch API exists in the tooling. Data consistency is eventually-consistent by accident, not by design.

**Question**: How do we harden the Cascade→Notion sync pipeline to guarantee at-least-once delivery, detect and reconcile drift automatically, and provide observability into sync health?

**Answer**: Introduce a four-layer enforcement stack: (W1) pre-flight schema validation + rate-limit aware batching; (W2) exponential-backoff retry with circuit breaker; (W3) bidirectional drift detection + reconciliation loop; (W4) sync health ledger + alerting. Each layer adds a gate (NP11-NP14), a hook, and CI enforcement.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `.windsurf/rules/notion-plans-taxonomy.md` | NP1-NP10 precedent, canonical Status strings | ✅ |
| `.windsurf/rules/plan-registration-enforcement.md` | §36 chokepoint pattern | ✅ |
| `tools/notion/wave_lifecycle_writer.py` | Current fail-soft write path | ✅ |
| `tools/notion/_wave_lifecycle_helpers.py` | Marker parsing, patch specs | ✅ |
| Web research: Notion webhook patterns, API rate limits | External validation patterns | ✅ |
| Notion API docs (via tavily) | Rate limit headers, retry guidance | ✅ |

---

## Wave Structure

| Waves | Focus | Checkpoint | Est. Tokens | Status |
|-------|-------|------------|-------------|--------|
| W0 | Baseline: audit current fail-soft patterns, enumerate failure modes | Pre-flight | ~3K | 🔲 |
| W1 | Schema validation pre-flight + property existence checks | NP11 gate | ~8K | 🔲 |
| W2 | Exponential-backoff retry + circuit breaker for Notion writes | NP12 gate | ~10K | 🔲 |
| W3 | Bidirectional drift detection + reconciliation loop | NP13 gate | ~12K | 🔲 |
| W4 | Sync health ledger + dashboard + alerting hooks | NP14 gate | ~8K | 🔲 |
| W5 | Integration tests + CI registration + documentation | CI pass | ~6K | 🔲 |

**Total: ~47K tokens across 5 waves + W0 baseline**

---

## Out Of Scope

- Notion webhook inbound handling (receive Notion events) — requires external endpoint, out of current architecture
- Real-time sync (<1s latency) — Notion API limitations make this infeasible
- Conflict resolution UI — Author-Gate on every conflict would overwhelm; automated policy suffices
- Multi-workspace sync — single workspace (Amit Ayer's Space) only
- Database schema migrations — assumes existing Plans/Backlog DB structure

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0.P1 | Failure mode enumeration | wave_lifecycle_writer.py, artifacts logs | GAP-1: no retry visible | ~3K | 🔲 TODO |
| W1.P1 | Property existence validator | _notion_property_validator.py | GAP-2: schema drift undetected | ~4K | 🔲 TODO |
| W1.P2 | Pre-flight schema check gate | ops_scripts/ci/check_notion_schema_preflight.py | GAP-3: late failure | ~4K | 🔲 TODO |
| W2.P1 | Retry decorator with backoff | _notion_retry.py | GAP-4: fail-soft is terminal | ~5K | 🔲 TODO |
| W2.P2 | Circuit breaker state machine | _notion_circuit_breaker.py | GAP-5: cascade failure risk | ~5K | 🔲 TODO |
| W3.P1 | Drift detector engine | _notion_drift_detector.py | GAP-6: external edits invisible | ~6K | 🔲 TODO |
| W3.P2 | Reconciliation policy + apply | _notion_reconciler.py | GAP-7: manual drift repair | ~6K | 🔲 TODO |
| W4.P1 | Sync health ledger schema | .windsurf/schemas/sync_health_ledger.schema.sql | GAP-8: no metrics | ~3K | 🔲 TODO |
| W4.P2 | Sync telemetry emitter | _notion_sync_telemetry.py | GAP-9: blind to failure rate | ~3K | 🔲 TODO |
| W4.P3 | Health dashboard + weekly report | ops_scripts/calibration/notion_sync_weekly_report.py | GAP-10: operational visibility | ~2K | 🔲 TODO |
| W5.P1 | Integration test suite | tests/_notion_contract/ | GAP-11: untested paths | ~4K | 🔲 TODO |
| W5.P2 | CI gate registration | run_contract_gates.py + hooks.json | GAP-12: enforcement gap | ~2K | 🔲 TODO |

---

## Gap Register

**GAP-1: No Retry on Transient Failures**
- `wave_lifecycle_writer.py` logs HTTP errors and exits 0; writes that fail stay failed
- Impact: Wave completion markers never reach Notion; plan status drift undetected

**GAP-2: No Schema Validation Before Write**
- Cascade can attempt to write to renamed/deleted properties; Notion returns 400 but no pre-flight check exists
- Impact: Wasted API calls, late failure discovery, retry on non-retryable errors

**GAP-3: No Rate Limit Awareness**
- Notion API returns 429 with `Retry-After` header; current code ignores it
- Impact: Burst writes (bulk retire) hit rate limits, no backoff logic

**GAP-4: No Bidirectional Drift Detection**
- Manual Notion UI edits (status flips, summary edits) create divergent state Cascade never sees
- Impact: Source of truth becomes unclear; "what's the real status?" confusion

**GAP-5: No Circuit Breaker for Cascade Failures**
- If Notion API is degraded, every Cascade turn attempts writes, all fail, no degradation path
- Impact: Log spam, false-positives in other gates, wasted compute

**GAP-6: No Sync Health Observability**
- No metrics on write success rate, latency, drift frequency
- Impact: Cannot distinguish healthy from degraded sync; no alerting

---

## Execution Plan

### W0.P1 — Failure Mode Enumeration
**Scope**: Audit `wave_lifecycle_writer.py`, `_wave_lifecycle_helpers.py`, existing logs

**Tasks**:
1. Parse `artifacts/windsurf/wave_lifecycle_notion.jsonl` for error patterns
2. Categorize failures: rate limit (429), auth (401), not found (404), validation (400), server (5xx)
3. Document retryability matrix per HTTP status code

**Acceptance**: Spreadsheet of last 30 days failures with categorization

---

### W1.P1 — Property Existence Validator
**Scope**: New helper `tools/notion/_notion_property_validator.py`

**Contract**:
```python
def validate_properties(page_id: str, expected_props: set[str]) -> ValidationResult:
    """Query Notion page, verify all expected properties exist."""
```

**Features**:
- Caches property schema for 5 minutes (TTL)
- Returns missing properties + suggested canonical names (levenshtein match)
- Pure logic, no I/O at import

---

### W1.P2 — Pre-flight Schema Check Gate (NP11)
**Scope**: New CI gate `ops_scripts/ci/check_notion_schema_preflight.py`

**Invariants**:
- NP11-1: Before any `API-post-page`/`API-patch-page`, properties referenced must exist in target DB schema
- NP11-2: Renamed properties (e.g., "AI Summary" → "AI Summary ") detected via fuzzy match
- NP11-3: Stale property names logged with canonical suggestion

**Bypass**: `NOTION_SCHEMA_PREFLIGHT_BYPASS=1`
**Fail-closed**: `NOTION_SCHEMA_PREFLIGHT_FAIL_CLOSED=1`

---

### W2.P1 — Retry Decorator with Backoff
**Scope**: New helper `tools/notion/_notion_retry.py`

**Policy**:
- Max 3 attempts for retryable errors (429, 502, 503, 504)
- Exponential backoff: 1s, 2s, 4s (respects `Retry-After` if present)
- Non-retryable (400, 401, 404, 409): fail fast
- Idempotency key header on PATCH operations

**Integration**: Wrap `urllib.request` calls in `wave_lifecycle_writer.py`

---

### W2.P2 — Circuit Breaker (NP12)
**Scope**: New helper `tools/notion/_notion_circuit_breaker.py` + gate

**States**: CLOSED (normal), OPEN (failing), HALF-OPEN (testing recovery)

**Transitions**:
- 5 consecutive failures → OPEN (skip Notion writes, log only)
- 30s timeout → HALF-OPEN (probe with next write)
- 3 consecutive successes → CLOSED

**Gate NP12**: `ops_scripts/ci/check_notion_circuit_state.py`
- Reports circuit state: healthy, degraded, open
- Advisory by default; fail-closed mode for certification

---

### W3.P1 — Drift Detector (NP13)
**Scope**: New helper `tools/notion/_notion_drift_detector.py`

**Drift Types**:
1. Status drift: Notion Status ≠ expected from last marker
2. Property drift: AI Summary, Summary, Waiting For changed externally
3. Existence drift: Plan file on disk but Notion row missing (or vice versa)

**Detection Trigger**: `pre_user_prompt` hook `pre_user_prompt_notion_drift_check.py`

**Reconciliation Policy** (Author-Gate if manual intervention needed):
- Trivial drift (Status only): auto-reconcile via `wave_lifecycle_writer.py`
- Content drift (Summary edits): log conflict, surface in `PLAN_REGISTRATION_PENDING` style

---

### W3.P2 — Reconciliation Engine
**Scope**: `tools/notion/reconcile_plan_drift.py` CLI

**Modes**:
- `--dry-run`: Show diffs, no changes
- `--auto-trivial`: Fix Status-only drift automatically
- `--interactive`: Prompt per conflict (Author-Gate style)
- `--force-disk`: Notion state overwritten from disk
- `--force-notion`: Disk state overwritten from Notion (rare, emergency)

---

### W4.P1 — Sync Health Ledger
**Scope**: SQLite schema `.windsurf/schemas/sync_health_ledger.schema.sql`

**Tables**:
- `sync_attempts`: timestamp, page_id, operation, status_code, latency_ms, retry_count
- `sync_failures`: failure_type, error_message, resolution_status
- `drift_events`: drift_type, detected_at, reconciliation_action

---

### W4.P2 — Sync Telemetry Emitter
**Scope**: `tools/notion/_notion_sync_telemetry.py`

**Hooks into**: `post_cascade_wave_lifecycle_capture.py`

**Emits**: Per-write structured log to `artifacts/windsurf/sync_telemetry.jsonl`

---

### W4.P3 — Weekly Sync Health Report
**Scope**: `ops_scripts/calibration/notion_sync_weekly_report.py`

**Metrics**:
- Write success rate (target: >99%)
- Average latency p50/p99
- Drift events per week
- Circuit breaker transitions
- Top failure reasons

**Output**: `docs/reports/notion_sync/<YYYY-Www>.md`

---

### W5.P1 — Integration Tests
**Scope**: `tests/_notion_contract/test_notion_sync_hardening.py`

**Test matrix**:
1. Retry succeeds on 2nd attempt
2. Circuit opens after 5 failures
3. Drift detected when Notion Status manually flipped
4. Schema preflight blocks write to non-existent property
5. Telemetry captured for every write path

---

### W5.P2 — CI Registration
**Scope**: `run_contract_gates.py` + `hooks.json`

**New gates**:
- NP11: `check_notion_schema_preflight.py` — Schema validation
- NP12: `check_notion_circuit_state.py` — Circuit health
- NP13: `check_notion_drift_freshness.py` — Drift age alert (>7 days)
- NP14: `check_notion_sync_health.py` — Telemetry-based health score

---

## Rules

1. **Fail-soft remains default** — sync must never block wave execution
2. **Retry is bounded** — max 3 attempts, max 7s total delay
3. **Drift detection is advisory** — auto-reconcile trivial, surface content drift
4. **Circuit breaker protects** — when Notion is down, log only, don't spam
5. **Observability first** — every sync attempt logged, metrics aggregated weekly

---

## Success Criteria

| Metric | Target | Verification |
|---|---|---|
| Write success rate | >99% | `select rate from sync_health_ledger where week = current` |
| Drift detection latency | <24h | `drift_events.detected_at - drift_events.created_at` |
| Retry recovery rate | >90% | Failed → Succeeded on retry ≥1 |
| Circuit breaker accuracy | 0 false OPEN | Manual audit of transitions |
| Schema preflight catch | 100% | Unit tests with renamed properties |

---

## Implementation Commands

```bash
# W0: Baseline audit
python tools/notion/audit_sync_failures.py --since 30d --output artifacts/reports/sync_baseline.json

# W1: Schema validation check (advisory)
python ops_scripts/ci/check_notion_schema_preflight.py --plan notion-sync-enforcement-hardening-f5a2c1

# W2: Retry + circuit integration test
pytest tests/_notion_contract/test_notion_sync_hardening.py::test_retry_succeeds_second_attempt -v

# W3: Drift detection dry-run
python tools/notion/reconcile_plan_drift.py --dry-run --plan notion-sync-enforcement-hardening-f5a2c1

# W4: Weekly report (ad hoc)
python ops_scripts/calibration/notion_sync_weekly_report.py --regenerate

# W5: Full gate suite
python ops_scripts/ci/run_contract_gates.py --category notion
```

---

## Rollback Strategy

If W2 retry logic causes latency issues:
1. Set `NOTION_RETRY_BYPASS=1` — disables retry, reverts to fail-soft
2. If circuit breaker false-positive: `NOTION_CIRCUIT_BYPASS=1`
3. If drift detection noise: increase detection threshold in `_notion_drift_detector.py`

Emergency: Revert `wave_lifecycle_writer.py` to pre-retry version (git revert).

---

## Definition of Done

| # | Criterion | Verification | Status |
|---|---|---|---|
| DoD-1 | 4-layer enforcement stack operational | NP11-NP14 gates all green | 🔲 |
| DoD-2 | Smoke run: `python tools/notion/wave_lifecycle_writer.py --slug test-f5a2c1 --kind plan_complete` exits 0 with retry telemetry | `grep retry_count artifacts/windsurf/sync_telemetry.jsonl` | 🔲 |
| DoD-3 | Integration tests: 20+ pass, zero regressions in existing tests | `pytest tests/_notion_contract/ -v` | 🔲 |
| DoD-4 | CI gates registered: NP11-NP14 appear in run_contract_gates.py | `grep -E "NP1[1-4]" ops_scripts/ci/run_contract_gates.py` | 🔲 |
| DoD-5 | Documentation: Notion sync discipline added to `.windsurf/skills/notion/SKILL.md` | Skill updated with retry/circuit/reconcile patterns | 🔲 |

**Verification-vs-Deferral**:

| Item | Why deferred | Tracked in |
|---|---|---|
| Webhook inbound (receive Notion events) | Requires external endpoint, architecture change | `NEXT_STEP: notion-webhook-inbound-receiver` |
| Real-time sync (<1s) | Notion API limitations | Not feasible; won't fix |
| Multi-workspace support | Single workspace sufficient | Future plan if needed |

---

## Cascade Alignment Checks

- **Hook pattern**: Pure helpers + pre/post hooks + CI gates (matches NP1-NP10)
- **Bypass discipline**: Every new gate has `*_BYPASS=1` and `*_FAIL_CLOSED=1`
- **Fail-soft default**: Retry adds latency but never blocks; circuit breaker preserves this
- **Telemetry discipline**: All writes logged to `artifacts/windsurf/*.jsonl` per §24/§30

---

PLAN_CREATED: slug=notion-sync-enforcement-hardening-f5a2c1 path=.windsurf/plans/notion-sync-enforcement-hardening-f5a2c1.md status=Not Started
