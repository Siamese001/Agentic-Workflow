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

Not a refactoring plan (pure enforcement-tier additions). No `mv_*` queries are in the critical path — this plan ships new enforcement scripts, does not refactor existing ADG-consuming code.

## ADG_HOTSPOT_REPORT

| File | Archetype | Layer | Fan-in | Surface | Rationale |
|---|---|---|---:|---|---|
| `.windsurf/scripts/post_cascade_adg_audit.py` | SAFETY_GATEKEEPER | L_HOOKS | 0 (hook) | Security | Enforcement point for ADG-first rule |
| `.windsurf/scripts/pre_write_gate.py` | SAFETY_GATEKEEPER | L_HOOKS | 0 | Security+Write | Enforcement point for write-class violations |

## References

- `.windsurf/rules/adg-graph-layer-enforcement.md`
- `.windsurf/rules/constitutional.md` §22 §28
- `ops_scripts/ci/check_graph_layer_evidence.py`
- `artifacts/windsurf/adg_first_violations.jsonl` (51 entries — basis for P1 promotion)
- `artifacts/windsurf/graph_layer_violations.jsonl` (416 entries — basis for P3 baseline)
