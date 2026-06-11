---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\author-gate-rename-and-meta-learning-a7c3f1.md'
original_relative_path: 'author-gate-rename-and-meta-learning-a7c3f1.md'
source_sha256: 532247e560167325d735cfa078ddbbd4e6bdd8b63ace7c5e6f9a6336575208e8
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-23'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Author-Gate Rename Residue + Meta-Learning Enrichment

Status: Executed 2026-04-23 — W1-W6 complete (W5.2 memory tag cleanup deferred on MCP transport error)
Tier: T3 (cross-layer: hooks, scripts, schema, Notion, tests)
Owner: Cascade
ADG Snapshot: latest on disk
Created: 2026-04-23

## Goal

Two interlocking objectives:

1. **Finish the `hitl-*` → `author-gate-*` rename** for all artifacts that actually represent
   developer-loop Author-Gate decisions (not runtime HITL). Preserve `agentic_core/L5_safety/`
   and `agentic_core/adg/contracts/` runtime HITL naming — those are correct per ADR-023.
2. **Close the meta-learning gaps** discovered in the audit: persist `confidence_top`,
   `confidence_dominance_gap`, `override_vs_recommendation`, `selection_latency_ms`,
   `principle_at_stake`, write `decision_scope` rows, add pattern promotion, backfill
   the 9 stale `outcome_label` NULLs, and install the Windsurf 2.0.67 inline-capture bypass
   so capture doesn't go dark.

## Scope Boundaries

IN scope:
- `.windsurf/scripts/*.py` (Author-Gate hooks only)
- `.windsurf/schemas/decision_ledger.schema.sql`, `author_gate_triggers.yaml`
- `.windsurf/skills/author-gate-packet-builder/`
- `.windsurf/skills/refactor-decision-memory/`
- `artifacts/windsurf/hitl_*.{json,jsonl}` + `.windsurf/state/refactor_decisions/hitl_capture.log`
- Tests under `tests/unit/windsurf/scripts/` whose subject is Author-Gate
- Notion DB title for `5b60fdde-7259-491e-9f2d-e088f1f741ef`
- Memory entity tags that conflate `hitl` with author-gate events

OUT of scope (DO NOT TOUCH):
- `agentic_core/L5_safety/enforcement/exit_control_hitl.py` — legitimate runtime HITL
- `agentic_core/adg/contracts/schema.py`, `schema_util.py` — runtime HITL contract
- `agentic_core/runtime/contracts/lifecycle_trace_contract.py` — runtime HITL lifecycle
- `docs/contracts/L5_exit_control_hitl.md` — runtime HITL contract doc
- ADR-023 and any doc explicitly about runtime exit-control
- Deprecated shim rules already in place (`hitl-enforcement.md`, etc.) — leave until 2026-07-21 TTL
- Historical plan `.windsurf/plans/harness-enforcement-rename-a8f21c.md` — frozen record

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1   | P1.1–P1.3 | Author-Gate rename residue (file + string renames, back-compat aliases) | 9k | No runtime HITL files touched | Todo | grep `hitl_session\|hitl_violations\|hitl_capture` returns 0 hits in `.windsurf/scripts/`; legacy paths read-compat preserved for 1 version |
| W2   | P2.1–P2.2 | `DECISION_CAPTURED:` marker v2 — extend format + capture regex to carry confidence/gap/override/latency/principle | 7k | Marker remains single-line plain text | Todo | New marker parses; old marker still parses (back-compat); all 5 columns populate on fresh capture |
| W3   | P3.1–P3.3 | Capture hook enrichment — write `decision_scope` row; inline `defer.py`-style bypass for 2.0.67 hook-dark window; options_json capture full option set | 9k | psutil not needed here | Todo | Every new decision produces ≥1 scope row; bypass path works when `post_cascade_response` dark |
| W4   | P4.1–P4.2 | Pattern promotion + backfill `outcome_label` on 9 stale rows | 5k | Binder schema unchanged | Todo | `promote_to_pattern=1` set on ≥1 qualifying decision; 9 stale rows get labels |
| W5   | P5.1–P5.2 | Notion DB rename + memory entity tag cleanup | 3k | User has Notion write perm | Todo | Notion DB title = "Author-Gate Decision Ledger"; memory tags updated |
| W6   | P6.1–P6.2 | Verification + CI gate + smoke tests | 4k | pytest_mcp healthy | Todo | All touched unit tests green; end-to-end capture+lookup smoke passes; no gate regressions |

Total estimate: **~37k tokens**. Green 🟢.

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | Rename author-gate state paths | `@.windsurf/scripts/pre_author_gate.py`, `@.windsurf/scripts/post_cascade_author_gate_capture.py`, `@.windsurf/scripts/post_cascade_author_gate_miss_detector.py`, `@.windsurf/scripts/generate_calibration_report.py`, `@.windsurf/scripts/author_gate_ledger_integrity.py` | Back-compat: `artifacts/windsurf/hitl_session_state.json` read-fallback | 4k | Todo |
| P1.2 | Rename log files + in-place migration | `hitl_capture.log` → `author_gate_capture.log`; `hitl_violations.jsonl` → `author_gate_violations.jsonl`; `hitl_session_state.json` → `author_gate_session_state.json`; add one-shot migration that copies old → new on first invocation | Windows file-in-use during migration; fail-open if copy fails | 3k | Todo |
| P1.3 | Rename Author-Gate test files + string contents | `tests/unit/windsurf/scripts/test_post_cascade_author_gate_capture.py` (10 hits), `test_post_cascade_author_gate_miss_detector.py` (3 hits) | Must preserve test intent — rename symbols `hitl_packet` → `author_gate_packet` only where they describe Author-Gate | 2k | Todo |
| P2.1 | Extend `DECISION_CAPTURED:` marker schema | `@.windsurf/rules/author-gate-enforcement.md` line ~80 (Pipeline step 9 marker format) | Backwards compatibility — old marker must still parse | 3k | Todo |
| P2.2 | Update capture regex + INSERT to populate confidence columns | `@.windsurf/scripts/post_cascade_author_gate_capture.py` `_capture_marker_re` + `_capture_from_marker` | Regex must tolerate missing optional fields (old format) | 4k | Todo |
| P3.1 | Insert `decision_scope` row at capture time | `@.windsurf/scripts/post_cascade_author_gate_capture.py` `_capture_from_marker` | Infer `layer` from `repo_area` path prefix (L0–L6) | 3k | Todo |
| P3.2 | Capture full `options_json` from packet header | Same file; extend `_extract_options()` to parse option labels + confidences | Heuristic parsing — fail-soft to list of just the selected | 3k | Todo |
| P3.3 | Inline `defer.py`-style Author-Gate capture bypass for 2.0.67 | New `@.windsurf/scripts/capture_author_gate.py` that takes a marker as argv; Cascade invokes it inline via `run_command` (same pattern as `defer.py`) | Detection rule: when hook-dark (heartbeat stale >1h) | 3k | Todo |
| P4.1 | Pattern promotion script | New `@.windsurf/scripts/promote_author_gate_patterns.py` — flips `promote_to_pattern=1` for decisions with ≥2 matching precedents + clean outcomes | Wired as weekly cron or post-commit tail; dry-run mode | 3k | Todo |
| P4.2 | Backfill `outcome_label` on 9 stale rows | Same script in `--backfill` mode — re-runs `classify_outcome()` against each bound commit subject | Idempotent — only touches NULL labels | 2k | Todo |
| P5.1 | Rename Notion "HITL Decision Ledger" → "Author-Gate Decision Ledger" | Notion `API-patch-page` on parent db + row label; update `@AGENTS.md` Notion Workspace Map | DB ID stays the same — only title changes | 2k | Todo |
| P5.2 | Memory entity tag cleanup | `memory` MCP `search_nodes("hitl")` → update observations/tags that describe author-gate events; keep runtime HITL entries | Identify by entity content, not tag string alone | 1k | Todo |
| P6.1 | Unit tests for new marker + scope row + pattern promotion | Extend `test_post_cascade_author_gate_capture.py` with v2 marker tests; new `test_promote_author_gate_patterns.py` | Fixtures need a pre-populated ledger | 3k | Todo |
| P6.2 | End-to-end smoke + CI gate regression | `python -m py_compile` on all touched files; run `pytest tests/unit/windsurf/scripts/` + `pytest tests/unit/.windsurf/skills/`; run `python ops_scripts/ci/run_contract_gates.py` | Must not regress existing gates | 1k | Todo |

## Gap Register

| Gap | Resolution |
|-----|------------|
| Confidence scores not carried by marker | W2 — extend marker format + regex |
| No `decision_scope` row on capture | W3 P3.1 |
| Only selected option kept in `options_json` | W3 P3.2 |
| Windsurf 2.0.67 post_cascade hook silently dark | W3 P3.3 inline bypass |
| No pattern promotion → lookup can only return `suggestive` | W4 P4.1 |
| 9 `outcome_label=NULL` rows from pre-label era | W4 P4.2 |
| Notion DB title misnomer | W5 P5.1 |
| Memory tags conflating hitl/author-gate | W5 P5.2 |

## ADG_HOTSPOT_REPORT

Not applicable — no P0/P1/P2 violations are being modified; this is harness-side hook/schema work,
not `agentic_core` code. ADG fan-in on the Author-Gate scripts: `post_cascade_author_gate_capture.py`
is invoked by the Windsurf hook dispatcher only (no in-repo imports); `pre_author_gate.py` is likewise
invoked by the hook dispatcher. Impact score: **N/A — infrastructure-only change**.

## ADG_GRAPH_LAYER_EVIDENCE

Not applicable — see above. The ADG materialized views (`mv_graph_reverse_dependency_hotspots`, etc.)
and semantic edges (`flows_to`, `writes_to`) are not relevant because no node in `agentic_core/`,
`apps_*/`, or `system_learning/` is being modified. All changes live under `.windsurf/` and `tests/`.

## Rollback Checkpoints

- After W1: verify old log paths still readable via back-compat shims
- After W2: verify old `DECISION_CAPTURED:` marker format still parses (regression guard)
- After W3: verify capture still produces rows when run manually
- After W4: verify binder + lookup still functional
- After W5: verify Notion DB still addressable by ID (title rename only)
- After W6: all gates green; memory recall still works

## Verification

```powershell
# Rename completeness (should return 0 hits after W1)
python -c "import subprocess,sys; r=subprocess.run(['git','grep','-l','hitl_session_state\\|hitl_violations\\|hitl_capture\\|HITL_PACKET','.windsurf/scripts/','.windsurf/schemas/','.windsurf/skills/author-gate-packet-builder/'],capture_output=True,text=True,timeout=10); print(r.stdout); sys.exit(1 if r.stdout.strip() else 0)"

# Meta-learning fields populated (should show non-NULL counts > 0 after W3)
python -c "import sqlite3; c=sqlite3.connect('.windsurf/state/refactor_decisions/refactor_decision_ledger.sqlite'); print('with_confidence:',c.execute('SELECT COUNT(*) FROM decisions WHERE confidence_top IS NOT NULL').fetchone()[0]); print('with_scope:',c.execute('SELECT COUNT(DISTINCT decision_id) FROM decision_scope').fetchone()[0]); print('promoted:',c.execute('SELECT COUNT(*) FROM decision_outcomes WHERE promote_to_pattern=1').fetchone()[0])"

# Targeted tests
python -m pytest tests/unit/windsurf/scripts/test_post_cascade_author_gate_capture.py -v
python -m pytest tests/unit/windsurf/scripts/test_post_cascade_author_gate_miss_detector.py -v
```

## Out-of-Band Considerations

- **`post_cascade_author_gate_capture.py` is currently dark** (Windsurf 2.0.67 bug). W3 P3.3 inline
  bypass partially mitigates; full recovery waits for Windsurf 2.0.68+.
- **The deprecated rule shims** (`hitl-enforcement.md` etc.) have a 2026-07-21 TTL per the
  harness-enforcement-rename plan — do NOT touch them in this plan.
- **Notion database ID** (`5b60fdde-…`) is stable; only the display title changes. Existing queries
  using the ID continue to work.

## Approval

Reply with `SR_APPROVAL: APPROVED` to begin W1. Reply `SR_APPROVAL: REVISE <note>` to iterate.
