---
plan_id: p1p2-burndown-followup-a2e4c7
created: 2026-05-03
tier: T3
status: active
parent: p1p2-burndown-current-3f9a8e (Completed 2026-05-03)
---

# P1/P2 Burndown — Deferred Follow-up

Captures the three `DEFERRED_SCOPE:` items emitted by the parent plan `p1p2-burndown-current-3f9a8e` (Completed 2026-05-03, commits `bd79cdf9ea` + `0d35441ba8`). Each of the three items is tracked as an independent wave — they have distinct blast-radii, risk profiles, and ADR footprints, and do not share a critical path.

## Parent Outcome Recap

- **W1–W3 complete**: 22 → 13 MEDIUM antipattern pre-filter (9 genuine broad catches eliminated via 11 edits across 7 files in W2).
- **P2 ratchet**: settled 10 → 13 to match post-W2 floor. ADG regen exits 0.
- **Residual**: 13 pre-filter / 10 post-filter are all scanner false-positives on already-narrow catches (`ValueError`, `OSError`, `ImportError`, `KeyError`, `json.JSONDecodeError`, `subprocess.TimeoutExpired`). Guardian exemptions landed with concrete §8 justification where needed.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|------------:|--------|------------------|
| W1 | W1-01 | ADG scanner: recognize narrow-type exception catches | 8000 | Pending | Scanner no longer classifies `except ValueError:` / `except OSError:` / `except json.JSONDecodeError:` / `except subprocess.TimeoutExpired:` as MEDIUM `antipattern` category. P2 ratchet auto-reduces 13 → ≤2. Unit-test suite added for scanner classification boundary. |
| W2 | W2-01..W2-09 | 9 CRITICAL layer-gravity `violates` — ADR per module-pair or refactor | 20000 | Pending | Each of the 9 `L_RUNTIME→L6`, `L_OPS→L6`, `L_TOOLS→L6`, `L_TOOLS→L_OPS` crossings carries an ADR in `docs/architecture/adr/` or the violating import is moved to a gravity-respecting location. `adg_violations` severity=CRITICAL category=violates count drops from 9 → 0. |
| W3 | W3-01 | Canonical adapter ADR — `redis`, `chromadb`, `sqlite3` | 12000 | Pending | ADR authored naming the canonical adapter module for each of the three infra primitives. `v_p2_duplicated_adapters` (3 rows) + `v_p2_mixed_usage` (3 rows) plus the 2 AP-14 sites (`agentic_core/L4_state/utils/memory/canonical_store.py`, `apps_rg/enforcement/HardenedanthropicexecutorStrategy.py`) are reclassified or the wrapped-usage count exceeds direct-usage count. |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|------------:|--------|
| W1-01 | Scanner narrow-catch recognition | `tools/adg/...` scanner + `tools/generate/validation/gates.py` call-site + unit tests | Scanner classifier logic is deep in the ADG stack; needs to distinguish `except Exception` from `except <NarrowType>` at AST-node level; must not regress existing broad-catch detection | 8000 | Pending |
| W2-01..W2-09 | 9 CRITICAL layer-gravity crossings | `agentic_core/runtime/entrypoints/integrated_managed_workflow_run.py:68`, `integrated_safe_reuse_run.py:76,119`, `ops_scripts/ci/check_otel_genai_semconv_coverage.py:59`, `check_synthetic_trace_flag.py:33`, `ops_scripts/reports/desk_d_governed_board.py:29`, `governed_handoff.py:45`, `tools/maintenance/backfill_adg_graph_layer_sections.py:261`, `tools/otel/exercise_real_otel_pipeline.py:221`, `tools/proof/composition_proof_provenance_chain.py:61` | Each crossing requires Author-Gate: ADR vs refactor. Most are ops/runtime → L6 observability — likely ADR-approved (observability is universal) but must be deliberate. | 20000 | Pending |
| W3-01 | Canonical-adapter ADR for redis/chromadb/sqlite3 | `agentic_core/L4_state/cache/gptcache_client.py`, `agentic_core/L4_state/utils/client/chroma_client.py`, `agentic_core/L3_orchestration/reasoning/engines/sovereign_redis_orchestrator.py`, `agentic_core/L4_state/utils/memory/semantic_cache_manager.py`, `agentic_core/cache/redis_cache_client.py`, `apps_shared/data_adapters/repo_signal_adapter.py`, `tools/memory/sqlite_memory_store.py`, `agentic_core/L4_state/utils/memory/canonical_store.py`, `apps_rg/enforcement/HardenedanthropicexecutorStrategy.py` | sqlite3 has 276 direct uses vs 4 wrapped — reversing that is a migration campaign, not a single refactor. Needs ADR + phased rollout plan. | 12000 | Pending |

## ADG_HOTSPOT_REPORT

| Rank | Target | Layer | Surface | Archetype | Impact | Fix class |
|------|--------|-------|---------|-----------|-------:|-----------|
| 1 | W1 scanner narrow-catch recognition | L_TOOLS | Observability | CENTRAL_DEPENDENCY | 26 (13 FP × 2.0 tooling weight) | Scanner classifier refactor + tests |
| 2 | W3 sqlite3 canonical adapter | L4 state | State | STATE_NODE | 21 (276 direct uses × L4 weight 1.75 / normalized) | ADR + phased migration |
| 3 | W2 9 CRITICAL layer-gravity | L_RUNTIME / L_OPS / L_TOOLS | Execution | ORCHESTRATOR | 18 (9 crossings × L6 targets × 2.0) | ADR-per-pair OR refactor |
| 4 | W3 redis canonical adapter | L3/L4 | State | STATE_NODE | 10 (3 adapter files, 10 direct vs 3 wrapped) | ADR |
| 5 | W3 chromadb canonical adapter | L4 | State | STATE_NODE | 8 (2 adapter files, 10 direct vs 2 wrapped) | ADR |

## ADG_GRAPH_LAYER_EVIDENCE

- MV `mv_graph_reverse_dependency_hotspots` — W1 scanner is cross-cutting (high rdscore via tool count); W3 sqlite3 touches 276 direct-use sites.
- MV `mv_hotspot_centrality` — `canonical_store.py` and `semantic_cache_manager.py` surface with high betweenness (they bridge L3 orchestration to L4 state).
- P-views: `v_p2_duplicated_adapters` (3 rows: redis, chromadb, sqlite3), `v_p2_mixed_usage` (3 rows: same keys with direct-vs-wrapped counts), `v_p0_*` (14 rows — unaffected by this plan), `v_p2_*` AP-14 category (2 module-level rows).
- Semantic edges: `writes_to` density confirms `canonical_store.py` is a write authority — W3 ADR must preserve write-path invariants.
- `emits_side_effect` — the 9 CRITICAL crossings are overwhelmingly observability-bound (L6 targets), suggesting ADR (not refactor) is the right posture for most.

## Author-Gate Decision Points (expected)

Each wave surfaces at least one Author-Gate. Seeding for the queue helper:

AG_QUEUE_SEED: plan=p1p2-burndown-followup-a2e4c7 id=w1-scanner-approach depends_on= title=Scanner classifier refactor vs per-site annotation
AG_QUEUE_SEED: plan=p1p2-burndown-followup-a2e4c7 id=w2-adr-vs-refactor depends_on= title=Per-pair ADR approval vs bulk refactor to gravity-respecting location
AG_QUEUE_SEED: plan=p1p2-burndown-followup-a2e4c7 id=w3-canonical-adapter depends_on= title=Canonical-adapter ADR authorship and migration scope (sqlite3 has 276 direct uses)

## Execution Protocol

Each wave follows the standard:

1. Open Author-Gate packet (score ≥ 0.72, dominance ≥ 0.85 / gap ≥ 0.12 → recommend).
2. Execute the approved option; all edits compile; targeted tests added.
3. `generate_full_adg.py` regen; P-view / ratchet count confirms fix class.
4. Commit with plan slug reference.
5. Update this plan row status + Notion row.

Rollback: any wave that fails `py_compile` or drops non-skip test count is reverted via git.

## References

- Parent plan: `.windsurf/plans/p1p2-burndown-current-3f9a8e.md` (Completed)
- Constitutional §6 (Author-Gate), §8 (guardian exemption), §22 (graph-layer primary), §24 (DEFERRED_SCOPE marker), §35 (AG queue drain)
- ADG primers: `docs/reference/_primers/AST Dependency Graphs (ADG)/`
- Parent commits: `bd79cdf9ea` (W2 edits), `0d35441ba8` (W3 ratchet settle)

## Status

Active 2026-05-03. Awaiting Author-Gate for W1 scope.
