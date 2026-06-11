---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\author-gate-ledger-hardening-1f4c8a.md'
original_relative_path: 'author-gate-ledger-hardening-1f4c8a.md'
source_sha256: 6514678085eaf3dbaad2d3a3ef076375a550c340c315e84a05bcfcf288d1db99
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-04-29'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_type: governance
---

# Author-Gate Ledger Hardening — W1..W5

**Plan ID**: `author-gate-ledger-hardening-1f4c8a`
**Status**: Active (executing in this session)
**Tier**: T3 (cross-layer harness work, schema + 5 new artifacts)
**Parent context**: See response 2026-04-29 — proof of HITL/Author-Gate persistence + 5 observed gaps.

## Goal

Close the 5 observed gaps in the Author-Gate (refactor-decision) ledger so prediction → outcome → meta-learning loop is fully closed and CI prevents regression.

## Gap Map

| Gap | Observed | Root cause |
|---|---|---|
| 1 | `confidence_top` NULL on 59/63 rows | Pre-W2-marker rows; no CI gate enforces v2 fields going forward |
| 2 | `signature` NULL on 63/63 rows | `AUTHOR_GATE_SIGNING_KEY` was never set; existing `--resign` never invoked |
| 3 | `exit_criteria_json` NULL on 63/63 rows | Column exists but capture writer's `_parse_v2_tail` has no extractor |
| 4 | L5/hitl calibration shows "_Awaiting telemetry_" | Calibration report stale; ledger actually has 14 rows |
| 5 | `outcome_label='undecided'` on 37/37 bound rows | Direct-bind sets `undecided` when no fresh test signal; no retro git-walk classifier |

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---:|---|---|
| W1 | W1.1, W1.2 | Bootstrap (regen calibration report; verify L5/hitl populated) | 2k | Done | Calibration report shows non-stale L5 row |
| W2 | W2.1 | Retro outcome rebinder (git-walk classifier) | 8k | Done | `outcome_label='undecided'` count drops on existing rows |
| W3 | W3.1, W3.2 | `exit_criteria_json` extractor in capture writer + marker contract update | 6k | Done | New markers carrying `exit_criteria=` populate column |
| W4 | W4.1, W4.2 | HMAC signing — generate key, document, retro-sign all 63 rows | 5k | Done | All 63 rows have `sig_alg='hmac-sha256'` and non-NULL signature |
| W5 | W5.1 | Forward CI gate `check_author_gate_v2_completeness.py` | 5k | Done | Gate fails on missing v2 fields in rows newer than 7d |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---:|---|
| W1.1 | Verify L5/hitl bootstrap | (read-only) `artifacts/ledgers/router_l5_hitl.sqlite` | None — already populated | 0.5k | Done |
| W1.2 | Regen W18 calibration report | `docs/reports/calibration/2026-W18.md` | Existing report is W17, stale | 1.5k | Done |
| W2.1 | Retro git-walk rebinder | `tools/refactor_decisions/rebind_outcomes_from_git.py`, tests | Heuristics may misclassify; idempotent guard | 8k | Done |
| W3.1 | exit_criteria parser | `.windsurf/scripts/post_cascade_author_gate_capture.py` | Regex must tolerate JSON or simple list values | 4k | Done |
| W3.2 | Marker contract docs | `.windsurf/rules/author-gate-enforcement.md` | Backward compat with v2 markers | 2k | Done |
| W4.1 | Key generation + .env.example | `.env.example`, key file | Key must be gitignored; doc placement | 1k | Done |
| W4.2 | Retro --resign 63 rows | (run existing) `author_gate_ledger_integrity.py --resign` | Must commit signature column updates | 4k | Done |
| W5.1 | v2 completeness CI gate | `ops_scripts/ci/check_author_gate_v2_completeness.py`, tests | Sentinel for silent-marker rows | 5k | Done |

## ADG_GRAPH_LAYER_EVIDENCE

- **Layer**: harness (`.windsurf/scripts/`, `ops_scripts/ci/`, `tools/refactor_decisions/`) — does not touch L0–L6 of `agentic_core/`
- **MV evidence**: not applicable — this is harness/governance code, not subject to `mv_*` hotspot ranking. Constitutional §22 graph-layer requirement applies to `agentic_core/`/`apps_*/` refactoring; harness exemption per ADR-031.
- **Semantic edges**: N/A (no production data flow)
- **P-views**: not applicable to harness layer

## ADG_HOTSPOT_REPORT

Not applicable — pure harness work. No fan-in from `agentic_core/`/`apps_*/`.

## Out of Scope (deferred)

- Wiring `agentic_core/L5_safety/runtime_gates/g06_hitl_approval.py` to emit ROUTER_DECISION markers (separate engineering task; tracked as NEXT_STEP)
- Schema migration to make `confidence_top NOT NULL` (cannot retro-fix existing 59 NULL rows; CI gate is the practical equivalent)
- Per-decision `exit_criteria` AG-10 shape change in `ask_user_question` packet (forward-only, no retro)
