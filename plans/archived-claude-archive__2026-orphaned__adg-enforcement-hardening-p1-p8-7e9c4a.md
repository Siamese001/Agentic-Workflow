---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-orphaned\\adg-enforcement-hardening-p1-p8-7e9c4a.md'
original_relative_path: '_archive\\2026-orphaned\\adg-enforcement-hardening-p1-p8-7e9c4a.md'
source_sha256: 63bf4b05beee88051a49f0231895b1b6b568174fd523ae77cf7d9b2beba3cb75
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG Enforcement Hardening — P1..P8

Status: In Progress (2026-04-28)
Source: Web-research improvement review (Kumar hooks article, Windsurf Wave 13/14 changelog, MS Entra Authorization Fabric).

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| W1 | P1, P3, P8 | Critical blocking enforcement + secret scan verification | 3000 | Hook schema unchanged | In Progress | `exit 2` fires on critical ADG violations; PR-delta gate blocks new violations |
| W2 | P2, P4 | Stop-gate + pre-prompt grep detector | 3000 | pre_user_prompt chain accepts new hook | Todo | Plan-evidence gate fires end-of-turn; user prompt injection works |
| W3 | P5, P6, P7 | Telemetry + PEP/PDP scaffold + test coverage | 4000 | Heartbeat is first in chain | Todo | Chain-latency captured; PDP module importable; smoke tests for new hooks |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| P1 | Promote ADG audit critical→exit 2 | `post_cascade_adg_audit.py` | Environment bypass must still exit 0 | 400 | Done |
| P2 | Plan-evidence Stop-equivalent hook | new hook + `hooks.json` | Must scan response for `plans/*.md` edits | 1200 | Todo |
| P3 | PR-delta CI gate on violation logs | new gate + workflow patch | Baseline file lookup | 1000 | Todo |
| P4 | Pre-prompt grep-for-deps warning | new pre_user_prompt hook + `hooks.json` | Must inject into prompt, not block | 800 | Todo |
| P5 | Hook chain latency telemetry | `post_cascade_heartbeat.py` + calibration | Read previous heartbeat timestamp | 800 | Todo |
| P6 | PEP/PDP scaffold (minimal) | new `tools/policy/decisions/adg_first.py` | Only one decision extracted | 600 | Todo |
| P7 | Smoke-test coverage for new hooks | `tests/unit/ops_scripts/hooks/windsurf/` | Synthetic stdin fixtures | 1200 | Todo |
| P8 | Secret detection in pre_write_gate | (already wired — verify + document) | Existing `_secret_patterns.py` | 200 | Done (pre-existing) |

## ADG_GRAPH_LAYER_EVIDENCE

Although this plan ships new enforcement-tier hooks (not a refactor of existing
modules), the constitutional §22 evidence requirement is satisfied by the MVs
this work consumes and protects:

- **`mv_observability_interference_breaches`** — the post-Cascade hook chain
  emits structured JSONL records; a regression here is a Security Surface
  failure mode this plan's `post_cascade_adg_audit.py` is designed to detect.
- **`mv_replay_surface_gaps`** — `post_cascade_heartbeat.py`'s new
  `chain_latency_ms` field plugs a replay-coverage gap previously listed in
  this MV's report.
- **`mv_exit_disposition_coverage`** — exit-2 promotion in
  `post_cascade_adg_audit.py` improves disposition coverage for the
  `grep_for_deps_critical` violation class.

Semantic edge: **`emits_side_effect`** (every hook in this plan writes to
`artifacts/windsurf/*.jsonl` audit logs).

P-view check: this plan is `L_HOOKS`, not production code, so `v_p0_*` /
`v_p1_*` / `v_p2_*` / `v_p3_*` are not expected to match.

## ADG_HOTSPOT_REPORT

| File | Archetype | Layer | Fan-in | Surface | Rationale |
|---|---|---|---:|---|---|
| `.windsurf/scripts/post_cascade_adg_audit.py` | SAFETY_GATEKEEPER | L_HOOKS | 0 (hook) | Security Surface | Enforcement point for ADG-first rule (§28) |
| `.windsurf/scripts/post_cascade_plan_evidence_gate.py` | SAFETY_GATEKEEPER | L_HOOKS | 0 (hook) | Security Surface | Enforcement point for §22 plan-evidence requirement |
| `ops_scripts/ci/check_adg_violation_log_delta.py` | SAFETY_GATEKEEPER | L_TOOLS | 0 (CI) | Observability Surface | PR-delta enforcement on append-only audit logs |

## References

- `.windsurf/rules/adg-graph-layer-enforcement.md`
- `.windsurf/rules/constitutional.md` §22 §28
- `ops_scripts/ci/check_graph_layer_evidence.py`
- `artifacts/windsurf/adg_first_violations.jsonl` (51 entries — basis for P1 promotion)
- `artifacts/windsurf/graph_layer_violations.jsonl` (416 entries — basis for P3 baseline)
