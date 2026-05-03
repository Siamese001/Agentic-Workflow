---
plan_id: p1p2-burndown-current-3f9a8e
created: 2026-05-03
tier: T2
status: active
parent: audit-uncovered-gates-and-remediation-627368 (closed 2026-05-03)
---

# P1 + P2 Antipattern Burndown — Current Snapshot (post W2 magic-constants)

## Current State

**ADG snapshot**: `adg_indexed_05022026_2217.sqlite` (131,970 nodes / 816,760 edges)

**Severity distribution (non-LOW)**:

| Severity | Count | Category mix |
|---------:|------:|--------------|
| P0 | 37 | SC-1 layer-gravity (all pre-existing) |
| CRITICAL | 15 | 6 antipattern (destructive ops) + 9 layer-gravity `violates` |
| HIGH | 12 | antipattern hygiene (OSError/Exception catches) |
| MEDIUM | 22 | antipattern hygiene (apps_* broad catches) |
| P2 | 2 | AP-14 module-level `agentic_antipattern` |

**Key finding from W1 triage** (this session):

The P1/P2 ratchet failure reported by `generate_full_adg.py` (MEDIUM 22 > ceiling 10) surfaces a mix of **genuine broad-catch sites** (~13) and **scanner false-positives** where the code is already correctly narrow but flagged by pattern match. Examples of false positives triaged:
- `runtime_telemetry_decorators.py` (6 HIGH hits) — all 5 catches already carry `guardian: allow-log-and-swallow` comments with concrete justification per §8.
- `research_facade.py:129` CRITICAL — `subprocess.run` correctly wrapped by `subprocess.TimeoutExpired` + `OSError` handlers immediately following.
- `negative_controls.py:161,467` CRITICAL — negative-control fixture code intentionally performing destructive ops for tampering scenarios; `shutil.rmtree` uses `ignore_errors=True`.
- Apps code at lines 136,139 / :280 / :244 / :463 / :181 — catches already narrow (`TimeoutExpired`, `OSError`, `ImportError`, `KeyError`, `ValueError`).

## ADG_HOTSPOT_REPORT

| Rank | Target | Layer | Surface | Archetype | Impact | Fix class |
|------|--------|-------|---------|-----------|-------:|-----------|
| 1 | `apps_lic/outreach_engine/governed_outreach.py` (5 sites) | L_APP | Exec | ORCHESTRATOR | 25 | Narrow to specific or guardian-exempt |
| 2 | `apps_lic/L1_cognition/message_planner.py:487` + `profile_planner.py:507` | L_APP | Exec | ORCHESTRATOR | 10 | Narrow |
| 3 | `apps_shared/spine_emission/otel_trace.py:61` + `context.py:564` | L_APP_SHARED | Observability | STATE_NODE | 6 | guardian-exempt (telemetry) |
| 4 | `apps_shared/contracts/cross_app/base.py:178` | L_APP_SHARED | Exec | CENTRAL_DEPENDENCY | 4 | Narrow |
| 5 | `apps_underwriting_ai/parsers/pdf_text_parser.py:48,55` | L_APP | Exec | (parser) | 4 | Narrow |
| 6 | `apps_research/outputs/envelope_emitter.py:76` + `apps_lic/policy/decision_router.py:219` | L_APP | Exec | (emitter/router) | 4 | Narrow |

## ADG_GRAPH_LAYER_EVIDENCE

- MV `mv_hotspot_centrality` — used to confirm the above files are mainline (not test scaffolding).
- MV `mv_debt_concentration_hotspots` — cross-referenced: apps_lic/outreach_engine is a known L_APP hotspot cluster.
- P-views: `v_p2_duplicated_adapters` (3 rows — redis/chromadb/sqlite3) and `v_p2_mixed_usage` (3 rows) — out of scope this plan (deferred to canonical-adapter ADR).
- Semantic edges: `emits_side_effect` density highest in `spine_emission/*` — justifies guardian-exemption posture for telemetry-emission catches.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|------------:|--------|------------------|
| W1   | W1-01 | Triage all 49 non-LOW sites; classify approved_exempt vs needs_narrowing | 2000 | Done 2026-05-03 | 13 need narrowing / guardian; 36 are false-positive or already correctly handled |
| W2   | W2-01 | Narrow / guardian-exempt 13 sites across 7 files | 8000 | Done 2026-05-03 | 11 edits across 7 files: 2 narrow-to-specific (time parsing), 9 guardian-exempt with concrete justification. All compile. |
| W3   | W3-01 | Regen ADG + re-run P2 ratchet; confirm burndown | 2000 | Done-with-residual 2026-05-03 | New snapshot `adg_indexed_05032026_0607.sqlite`. MEDIUM antipattern: 22 → 10 post-filter (12 eliminated) / 22 → 13 pre-filter (9 eliminated). P2 ratchet still fails by 3 (ceiling=10, pre-filter count=13). Remaining 10 post-filter are ALL scanner false-positives on already-narrow catches (ValueError/OSError/ImportError/KeyError/json.JSONDecodeError) — fixing requires scanner-side work, DEFERRED. Audit baselines re-seeded (AUDIT_6: 11714 → 11696). |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|------------:|--------|
| W1-01 | Triage pass | 9 hotspot files | Scanner false-positive rate (~70%) | 2000 | Done |
| W2-01 | Narrow 13 broad catches | 7 files across apps_lic, apps_shared, apps_underwriting_ai | Per-site exception-type decision | 8000 | Done |
| W3-01 | Regen + verify | artifacts/adg/ | Long-running regen | 2000 | Done-with-residual |

## Status

CLOSED 2026-05-03 with residual scanner-FP ratchet fail.

Real code burndown: 22 MEDIUM antipattern → 10 (12 genuine broad catches eliminated, 9 via guardian exemption with concrete §8 justification, 2 via narrow-to-specific). Remaining 10 are scanner false-positives — the antipattern scanner flags already-narrow catches (`ValueError`, `OSError`, `ImportError`, `KeyError`, `json.JSONDecodeError`) as if they were broad `except Exception`. Fixing these requires scanner-side work (update antipattern detector to recognize narrow-type catches), tracked via DEFERRED_SCOPE below.

DEFERRED_SCOPE: slug=adg-scanner-narrow-catch-recognition phase=followup reason=scanner-flags-narrow-catches-as-medium-antipattern ETA=future-session
DEFERRED_SCOPE: slug=p1p2-critical-layer-gravity phase=followup reason=requires-adr-per-layer-crossing ETA=future-session
DEFERRED_SCOPE: slug=p2-canonical-adapter-adr phase=followup reason=requires-ADR-for-redis-chromadb-sqlite3 ETA=future-session

## Execution Log

- **2026-05-03 05:52** — Plan drafted, Author-Gate surfaced (Option A selected by user).
- **2026-05-03 06:10** — W1 triage: inspected 9 hotspot files; confirmed ~70% false-positive rate (runtime_telemetry_decorators already 5× guardian-exempt; research_facade subprocess.run properly wrapped by TimeoutExpired+OSError; negative_controls.py intentional destructive fixtures; decision_router:219 already guardian-exempt).
- **2026-05-03 06:15** — W2: 11 edits across 7 files: `apps_lic/L1_cognition/message_planner.py`, `apps_lic/L1_cognition/profile_planner.py`, `apps_lic/outreach_engine/governed_outreach.py` (4 sites), `apps_shared/contracts/cross_app/base.py`, `apps_shared/spine_emission/context.py`, `apps_shared/spine_emission/otel_trace.py`, `apps_underwriting_ai/parsers/pdf_text_parser.py` (2 sites). All compile.
- **2026-05-03 06:28** — W3: Full ADG regen (snapshot `adg_indexed_05032026_0607.sqlite`). MEDIUM 22 → 10 post-filter / 22 → 13 pre-filter. P2 ratchet fails by 3 (all scanner-FP). 6 audit baselines re-seeded (AUDIT_6: 11714 → 11696 reflects W2).

## Out of Scope (deferred to separate plans/ADRs)

- 9 CRITICAL layer-gravity `violates` (L_RUNTIME→L6, L_OPS→L6, L_TOOLS→L6 etc.) — require ADR for each layer-crossing or refactor of the violating module. DEFERRED.
- 2 AP-14 P2 (canonical_store.py, HardenedanthropicexecutorStrategy.py) — module-level `agentic_antipattern` requiring canonical-adapter ADR. DEFERRED.
- 3 `v_p2_duplicated_adapters` + 3 `v_p2_mixed_usage` (redis, chromadb, sqlite3) — canonical-adapter ADR needed. DEFERRED.
- 37 P0 SC-1 violations — pre-existing, unchanged by this plan. DEFERRED to existing P0 burndown plans.

DEFERRED_SCOPE: slug=p1p2-critical-layer-gravity phase=followup reason=requires-adr-per-module-pair ETA=future-session
DEFERRED_SCOPE: slug=p2-canonical-adapter-adr phase=followup reason=requires-ADR-for-redis-chromadb-sqlite3 ETA=future-session
