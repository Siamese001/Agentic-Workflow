# ADR-029: ADG Pipeline Ordering Contract

- **Status**: Accepted
- **Date**: 2026-04-22
- **Deciders**: Cascade (paired with user)
- **Related**:
  - Constitutional §22 (graph-layer evidence)
  - `@c:/Git/Agentic-Workflow/.windsurf/rules/adg-graph-layer-enforcement.md`
  - `@c:/Git/Agentic-Workflow/.windsurf/rules/adg-canonical-invariants.md`
- **Plan**: `@c:/Git/Agentic-Workflow/.windsurf/plans/adg-pipeline-e2e-5287a1.md`
- **Implementation commits**: `9fb93f698c` (W1), `7c3addc712` + `252f7dd1a3` + `4875fa1a3c` (W2), `dbef291670` + `11ee7a8644` + `21bfe4db8e` (W3), `8509bf0dd3` + `7b129ddf08` (W4)

## Context

The ADG generation pipeline (`@c:/Git/Agentic-Workflow/tools/generate/generate_full_adg.py`) sequences ~20 discrete stages that land either in the canonical snapshot (`adg_indexed_<ts>.sqlite`) or alongside it (`adg_graph_<ts>.sqlite`, P7 reports, watchlists). Prior to this ADR, four ordering and observability defects existed:

1. **Enrichment stranded after blocking gates.** `_enrich_infra_views()` and `_materialize_adg_views()` ran AFTER the Tier-2 code-quality gates (`_run_p0_two_pass_runner`, `_check_p0_violations`, `_check_p1_ratchet`, `_check_dead_production_imports`, `_check_structural_conformance`, `_check_agentic_antipatterns`). Any `sys.exit(1)` from those gates — common in practice, since the baseline has 3000+ P0 violations across 5 gate families — left the committed snapshot with zero materialized views. Observed: `adg_indexed_04222026_1939.sqlite` shipped with 5 base tables only.
2. **Projection stranded similarly.** P6 (`graph_projection.build_graph_projection`) and P6b (`_build_graphdb_network_projection`) ran AFTER the same blocking gates. When P0 blocked, P6/P6b never ran, so `adg_graph_<ts>.sqlite` stayed stale indefinitely. Observed: `adg_graph_04222026_1218.sqlite` survived past `adg_indexed_04222026_2052.sqlite` (14-hour gap).
3. **Silent projection swallowing.** The P6/P6b callers caught a broad specific tuple `(ImportError, OSError, RuntimeError, TypeError, ValueError)` and masked real defects as "skipped." The helper contract documented only `ImportError` as an acceptable skip reason.
4. **Silent pipeline skips.** Five `print("[ADG] P* skipped: {e}")` call sites in the P4/P5/P6/P6b/P7 stages emitted no forensic trail — impossible to distinguish a healthy skip (optional dep missing) from a latent defect (schema drift, helper bug).

The root constitutional rule: **§22 requires every T2/T3 plan to cite `mv_*` / `v_p*` / semantic-edge primitives.** When snapshots shipped without those primitives, plans became uncitable — every downstream refactor was either blocked or used stale evidence.

## Decision

Adopt a **Pipeline Ordering Contract** with four invariants, enforced by CI gates:

### Invariant 1 — Enrichment Precedes Blocking Gates
`_enrich_infra_views(paths.sqlite)` and `_materialize_adg_views(paths.sqlite)` MUST run immediately after `_resolve_post_commit_sqlite(...)` and BEFORE any Tier-2 gate that may `sys.exit(1)`. Materialization is a pure derivation over `nodes`, `edges`, `violations` — zero coupling to gate outcomes — so moving it ahead of gates is always safe.

**Enforced by**: `ops_scripts/ci/check_snapshot_has_mvs.py` (T7j pre-commit; `run_contract_gates.py`).

### Invariant 2 — Projection Precedes Blocking Gates
`build_graph_projection(...)` (P6) and `_build_graphdb_network_projection(...)` (P6b) MUST run immediately after enrichment and BEFORE `_emit_p0_remediation_wave_plan(...)`. Per `@c:/Git/Agentic-Workflow/tools/generate/graph_projection.py:22`, the projection reads ONLY canonical `nodes`, `edges`, `violations`, `meta` — never `mv_*` — so it has zero coupling to gate outcomes.

**Enforced by**: `check_snapshot_has_mvs.py` projection-freshness check (`proj_meta.source_artifact_digest == meta.artifact_digest`). Modes: `strict` (default), `warn` (`ADG_SNAPSHOT_PROJECTION_CHECK=warn`), `off`.

### Invariant 3 — Precise Exception Discipline at Non-Blocking Callers
Non-blocking pipeline stages (P6, P6b) MUST catch `ImportError` and only `ImportError`. Helpers' documented failure contracts are final: non-ImportError failures MUST propagate, not be masked as "skipped."

P4/P5/P7 callers retain a broader specific-tuple catch (they aggregate multiple helpers with genuinely heterogeneous failure modes) but MUST emit ledger entries (invariant 4).

### Invariant 4 — Skip-Ledger Forensic Trail
Every non-blocking pipeline skip MUST emit a JSONL record via `_record_pipeline_skip(adg_artifacts_dir, ts, layer=, name=, exc=)` to `artifacts/adg/adg_pipeline_skips_<ts>.jsonl`. Each record: `{ts, layer, name, exc_type, exc_message}`.

**Enforced by**: `ops_scripts/ci/check_pipeline_skips.py` (T7k pre-commit; `run_contract_gates.py`). Default allow-list: `ImportError` only. Modes: `strict` (default), `warn` (`ADG_PIPELINE_SKIPS_WARN=1`), `off` (`ADG_PIPELINE_SKIP_ACCEPT_IMPORT_ERROR=0` disables even the import-error allow-list).

## Canonical Ordering Reference

```
[Tier 0] snapshot extraction + canonical build
  ↓
_resolve_post_commit_sqlite(paths, ...)                 # → prod_sqlite_path
  ↓
[W1] _enrich_infra_views(paths.sqlite)
[W1] _materialize_adg_views(paths.sqlite)               # 51 mv_* tables + v_p* views
  ↓
[W3] build_graph_projection(paths.sqlite, ...)          # → adg_graph_<ts>.sqlite (P6)
[W3] _build_graphdb_network_projection(paths.sqlite, ...) # P6b GraphDB artifacts
  ↓
[Tier 2 blocking] _emit_p0_remediation_wave_plan(...)
[Tier 2 blocking] _run_p0_two_pass_runner(...)
[Tier 2 blocking] _check_p0_violations(...)             # may sys.exit(1)
[Tier 2 blocking] _check_p1_ratchet(...)
[Tier 2 blocking] _check_dead_production_imports(...)
[Tier 2 blocking] _check_structural_conformance(...)
[Tier 2 blocking] _check_agentic_antipatterns(...)
  ↓
[Non-blocking — all use _record_pipeline_skip on failure]
  P7 report emitters (×4: structural-outputs, refactor-accelerator, graphdb-queries, runtime-spine)
  _check_witness_tier_gates(...)
  P4 build_and_emit_watchlist(...)
  P5 ADGGraphWatchlistBuilder(...)
  ↓
[Repair + size report + auto-commit]
```

## Consequences

**Positive:**
- Every committed `adg_indexed_<ts>.sqlite` now ships with 51+ materialized views, 15+ P-views, 6+ infra-wiring views, AND a matching-digest `adg_graph_<ts>.sqlite`. Constitutional §22 plan citations are always valid against the latest snapshot.
- P0 violations are now surfaced correctly (they previously fail-opened on empty MV queries).
- Silent pipeline skips are no longer possible — every skip produces a JSONL record inspected at pre-commit time.
- Institutional memory preserved: four CI gates (`check_snapshot_has_mvs.py`, `check_pipeline_skips.py` + existing `check_graph_layer_evidence.py`) will fail future refactors that re-introduce the defect.

**Negative / trade-offs:**
- Running P6/P6b projection work even when P0 will later block adds ~20–30 seconds to pipelines that would previously short-circuit. Judged acceptable because the projection is indispensable for the next developer loop.
- Four new CI gates slightly increase pre-commit wall time. Mitigated by narrow file triggers (pre-commit only runs them when pipeline-related files are staged).

**Deferred scope (tracked separately):**
- Four pre-existing `§16` progress-bar gaps in `@c:/Git/Agentic-Workflow/tools/generate/generate_full_adg.py` (lines 160, 300, 372, 669) — captured as `DEFERRED_SCOPE` marker in this session.
- P0 baseline violations surfaced by enrichment fix (write_sovereignty 1887, authority_boundary 642, capability_egress 499, critical_path_integrity 64, infra_wiring 1) — these existed before and were masked; they are not a W1–W4 regression.

## Alternatives Considered

1. **Retry + rollback on gate failure**: catch P0 `sys.exit(1)`, run enrichment/projection, then re-raise. Rejected: brittle (exception catching of `SystemExit` is an anti-pattern), and the ordering fix is strictly better.
2. **Post-commit enrichment hook**: run enrichment after the pipeline exits, from a separate script invoked by `auto_commit_artifacts`. Rejected: introduces partial-state snapshots into git history (every push window would show a snapshot without MVs).
3. **Soft-fail MV gate**: accept snapshots without MVs and flag them via a warning. Rejected: constitutional §22 requires citable primitives — a missing-MV snapshot is a structural defect, not a warning.

## References

- `@c:/Git/Agentic-Workflow/tools/generate/generate_full_adg.py` (pipeline ordering — lines 598–670)
- `@c:/Git/Agentic-Workflow/tools/generate/graph_projection.py` (projection freshness contract — lines 8–21)
- `@c:/Git/Agentic-Workflow/ops_scripts/ci/check_snapshot_has_mvs.py` (T7j gate)
- `@c:/Git/Agentic-Workflow/ops_scripts/ci/check_pipeline_skips.py` (T7k gate)
- `@c:/Git/Agentic-Workflow/.pre-commit-config.yaml` (T7j + T7k hooks)
- `@c:/Git/Agentic-Workflow/ops_scripts/ci/run_contract_gates.py` (local gate runner)
