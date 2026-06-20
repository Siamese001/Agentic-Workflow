---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\scorer-otel-autosource-layer-b-c5e4d1.md'
original_relative_path: '_archive\\2026-05\\scorer-otel-autosource-layer-b-c5e4d1.md'
source_sha256: daacc198ee48e3ad09c3bc486f808c4ed8001d44111a16b207eef398b576d635
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Scorer OTel Auto-Source — Layer B

- **Status**: Todo
- **Tier**: T2 (3 scoped files, single-layer L6 observability + follow-up wiring to L0/tools)
- **Parent ADR**: `docs/architecture/adr/ADR-031-priority-scoring-operational-signals.md`
- **Created**: 2026-04-23
- **ADG snapshot used for fan-in**: `artifacts/adg/adg_indexed_04222026_2106.sqlite`
- **Context**: ADR-031 shipped the scorer math (v1→v2) and layer A (marker grammar + hook passthrough). The scorer now accepts 5 operational signals and the hook forwards them — but **nothing populates those signal values automatically**. Until this plan lands, v2 is a feature the marker author has to manually opt into, which defeats the ADR-031 goal of letting production telemetry drive backlog prioritization.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| **B1** | B1.1 | Plan-slug → agent-class resolver (pure Python, no new deps) | 6000 | ADG has `resolved_path` on every node; plan slug correlates to a file path | Todo | Given a plan slug + layer, resolver returns a ranked list of `agent_class` candidates drawn from ADG nodes whose `resolved_path` matches the plan's scope. |
| **B2** | B2.1 | Rolling-window OTel query fabric | 9000 | `otel_mcp.spans_by_agent` + `otel_anomalies` work against the existing runtime-ADG store; 30-day window is adequate | Todo | `OtelSignalFabric.fetch(plan=..., agent_class=..., window_days=30)` returns `(prod_invocations:int, trajectory_defect_rate:float)` with bounded timeout and fail-open `(0, 0.0)` on MCP failure. |
| **B3** | B3.1 | Reversibility inference from ADG semantic edges | 5000 | ADG snapshot exposes `writes_to`, `emits_side_effect`, `controls_flow` semantic edge kinds | Todo | `infer_reversibility(adg_node_id)` returns `"write"` if any `writes_to`/`emits_side_effect` edge exists from the node, `"action"` if `controls_flow`/`calls` to side-effecting targets, else `"read"`. |
| **B4** | B4.1 | Wire resolver + fabric + inference into the capture hook | 4000 | Layer A (this commit) already forwards v2 kwargs to scorer; hook gets a new `_enrich()` step between parse and score | Todo | Markers missing v2 fields get auto-enriched before scoring; hook log records both raw and enriched field sets for audit; bypass env var `DEFERRED_SCOPE_NO_AUTOSOURCE=1` short-circuits. |
| **B5** | B5.1 | Validation — telemetry on/off A/B + calibration report | 3000 | At least 10 real deferred items in last 30 days to score | Todo | Side-by-side report: v1 band, v2-manual band, v2-auto band. If auto-source moves >20% of items >1 band from manual, threshold recalibration ADR is opened. |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| B1.1 | Plan→agent-class resolver | `tools/priority/plan_agent_resolver.py` (new), `tests/unit/tools/priority/test_plan_agent_resolver.py` (new) | Plan slugs are free-form; need tolerant fuzzy match against `nodes.resolved_path`; must not hit the network | 6000 | Todo |
| B2.1 | OTel signal fabric | `tools/priority/otel_signal_fabric.py` (new), `tests/unit/tools/priority/test_otel_signal_fabric.py` (new) | MCP serialization rule — fabric must make at most 1 MCP call per fetch; SDK race (ADR-????) means batching is forbidden; fail-open on any MCP error | 9000 | Todo |
| B3.1 | Reversibility inference | `tools/priority/reversibility_inference.py` (new), `tests/unit/tools/priority/test_reversibility_inference.py` (new) | Semantic edge coverage is uneven pre-ADG-regen; function falls back to `"read"` when node has zero semantic edges | 5000 | Todo |
| B4.1 | Hook wiring + bypass | `.cursor/scripts/post_cursor_agent_deferred_scope_capture.py` (edit), `tests/unit/windsurf/scripts/test_deferred_scope_capture_autosource.py` (new) | Hook runs on every response — enrichment must be bounded (<500ms total) or timeout; ALL enrichment failures fail-open to v1 scoring | 4000 | Todo |
| B5.1 | Calibration A/B report | `tools/reports/priority_calibration_report.py` (new), `docs/reports/priority/calibration_<date>.md` (artifact) | Need a stable corpus — uses `artifacts/cursor/deferred_scope_capture.jsonl` tail; threshold recalibration is a follow-up ADR, not a code change here | 3000 | Todo |

Total estimate: **~27,000 tokens** — fits a single session.

---

## Gap Register

- **Plan-slug ambiguity**: some plans are named `something-6hex` where `6hex` is not a file path component. Resolver needs a heuristic that strips `-<6hex>` suffix and matches on the stem.
- **agent-class attribute**: `otel_mcp.spans_by_agent` expects an `agent_class` string. If ADG nodes in the plan scope don't map 1:1 to agent classes (e.g. utility modules), return an empty list — fabric returns neutral defaults.
- **Rolling window skew**: 30-day window is naive for repos with bursty traffic. Deferred to a follow-up if B5 calibration shows skew.
- **Reversibility false negatives**: if ADG is stale (pre-regen after a refactor), inference may miss newly-added write edges. B3 doc must tell callers to regenerate ADG before relying on inference for high-stakes decisions.

---

## Non-Goals (explicitly deferred)

- Recalibrating band thresholds (`P1≥300`, etc.) — that's an ADR on its own if B5 proves drift.
- Rewriting existing historical Notion rows — out of scope; auto-source kicks in on new markers only.
- Extending the scorer to consume runtime cost metrics (CPU/memory) — future v3.
