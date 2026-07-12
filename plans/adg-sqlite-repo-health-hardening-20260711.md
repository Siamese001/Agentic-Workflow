# ADG SQLite Repository-Health Hardening Plan

Plan ID: `adg-sqlite-repo-health-hardening-20260711`  
Status: Implementation in progress  
Repository: `Siamese001/Agentic-Workflow`  
Authoritative branch: `main`  
Base commit: `6486b1fd838a724ed4d8822d2b63f7c23069021b`

## Executive Assessment

The ADG has broad extraction, authority, runtime-witness, materialized-view, graph-analysis, gating, and reporting capabilities, but it is not yet a trustworthy repository-health system. The primary problem is not missing metrics; it is competing implementations, inconsistent graph semantics, unstable identity, misleading temporal calculations, fail-open consumer behavior, and artifact lineage that allows reports to describe different stages of the same run as if they were one snapshot.

The latest published audit run, `07112026_1937`, is explicitly `repair_ready`, not certified:

- Generator exit code: `1`
- Certification: `failed`
- Enforcement rollup: `NOT_CERTIFIED`
- Snapshot size: `714,641,408` bytes
- Meta node count: `189,542`; final observed count: `189,543`
- Meta edge count: `1,037,575`; final observed count: `1,037,677`
- Graph/report mismatch: `+1` node and `+102` edges
- Additional reports use materially different edge populations: `1,038,249` authority rows versus `511,522` three-bucket classified rows
- Required failing gates include `adg_gate_dispatcher`, `config-ref`, `lifecycle`, and `test-coverage`

No new repository-health metric should become merge-blocking until snapshot consistency, metric definitions, projection semantics, and certification selection are corrected.

## Implementation Status

Implementation began directly at user instruction; no design-approval package is required.

Landed on `agent/adg-sqlite-repo-health-hardening`:

- SQLite foreign-key enforcement and certification-time `foreign_key_check`
- Lossless canonical graph digests with isolated-node and edge-occurrence identity
- Directed `MultiDiGraph` projections with conservation accounting and exact SCC/reachability
- Explicit certified, repair, and candidate snapshot pointers with atomic promotion
- MCP certified-only selection, digest verification, fail-closed health, and complete materialization checks
- Exact Phase D membership deltas with `NO_BASELINE` semantics
- P0 write-sovereignty baseline failure closure
- Versioned metric registry and CI validation

Remaining waves continue incrementally behind compatibility surfaces and the draft PR.

## Source-of-Truth and Provenance

ADG Provenance: `backend=GitHub main report artifacts`, `snapshot=adg_indexed_07112026_1937.sqlite`, `source_sha256=a061c440a43f632c8c23466358ce2d7189d61e542005f540ee4bd7649b3b1d78`.

`DEGRADED_FALLBACK: reason=GitHub exposes the source and committed audit reports but not direct SQL access to the 714 MB SQLite snapshot.`

Consequences:

- Code findings are confirmed against `main`.
- Snapshot counts come from committed reports.
- Runtime query plans and latency must be measured in Wave 0.
- Current health values remain diagnostic because the snapshot failed certification and report consistency.

## Current-State Architecture

1. `ADGStaticScanner` extracts static nodes, relations, blind spots, and resolution data.
2. `ADGArtifactBuilder` creates schema `3.0.0` entities and relations.
3. `ArtifactNormalizer` creates normalized schema `4.0.0` and assigns integer IDs.
4. `agentic_core/adg/artifact/ArtifactPaths.py` writes the canonical SQLite candidate.
5. `generate_full_adg.py` subsequently enriches that SQLite with authority, runtime, registry, coverage, infra, materialized-view, and other rows.
6. Phases A–F create physical `mv_*` tables.
7. Two separate graph stacks create derived projections:
   - `tools/generate/graph_projection.py`
   - `tools/graphdb/**`
8. P0/P1 gates, ratchets, three-bucket checks, analyst reports, watchlists, and BCG reports consume different subsets and stages.
9. `SQLiteBackend` selects the newest timestamped SQLite by modification time.
10. `ADGService` exposes canonical and projection data through MCP, with optional Redis read-through.

## Confirmed Findings

### P0: Snapshot and report authority are inconsistent

- `AUDIT_PIPELINE_RECEIPT.json` marks the latest run failed and `repair_ready`.
- `adg_bcg_executive_summary_latest.json` reports node, edge, timestamp, and certification inconsistencies.
- `ArtifactPaths._write_sqlite()` stores `meta.total_nodes` and `meta.total_edges` before later generator stages mutate the graph.
- Validation occurs both before and after different enrichment stages, so a check can pass before final counts drift.
- `latest_sqlite()` selects by modification time and required-table presence, not certification status. A failed repair candidate can therefore become the MCP source.

### P0: Canonical writer authority is forked

`ArtifactPaths.py` is the generator’s current writer, but it imports behavior from `multi_writer.py`; both files contain large, divergent writer implementations.

Confirmed schema divergence includes:

- `ArtifactPaths.edges.confidence_score` versus `multi_writer.edges.confidence`
- Precision tables exist in `multi_writer` but not `ArtifactPaths`
- Different null/default rules
- Different severity-classification SQL
- Different precision metrics
- Both implementations exceed 1,100 lines
- Their tests only validate importability and public surfaces, not schema or behavioral equivalence

### P0: Graph projection semantics can produce incorrect answers

`tools/generate/graph_projection.py`:

- Loads a mixed module/symbol graph into `nx.DiGraph`.
- Collapses parallel relations between the same node pair.
- Mixes `imports`, `exports`, `reads_from`, `resolves_callsite`, and `emits_side_effect` in one dependency projection.
- Calculates centrality over modules and symbols but creates `proj_nodes` from modules only.
- Does not enable foreign-key enforcement while inserting projection rows.
- Uses the same `2.0` criticality weight for every recognized layer.
- Labels sampled betweenness correctly as approximate, but downstream consumers do not consistently preserve that caveat.
- Leaves `curr_snapshot_id` empty in projection-diff rows.
- Treats every numeric increase as “worsened,” regardless of metric semantics.
- Intentionally serves stale projection results.

`tools/graphdb/projection.py`:

- Projects into an undirected, simple `nx.Graph`.
- Collapses direction and parallel edge types.
- Silently skips unmapped node and edge types.
- Hardcodes scanner and schema versions.
- Feeds architecture and blast-radius queries that require directed semantics.

### P0: Temporal “new” metrics are not true row-level deltas

`phase_d_snapshot_regression.py` does not compare stable prior and current finding keys:

- `mv_new_provider_surfaces` sets `is_new=1` in both branches.
- `mv_new_cross_layer_dependencies` marks any current dependency as new after the first run.
- `mv_newly_introduced_critical_paths` compares only to a fixed score threshold.
- `mv_new_write_bypass_paths` uses aggregate count changes or critical severity rather than exact prior-row membership.
- Snapshot identity is the commit SHA, which cannot distinguish dirty-tree runs or multiple artifacts for the same commit.

### P1: Materialized-view authority is duplicated and undocumented

The orchestrator documentation claims 42 tables across four phases, while the implementation invokes six phases producing approximately 52 physical tables.

Overlapping implementations include:

| Concept | Competing implementations |
|---|---|
| Centrality | `mv_hotspot_centrality`, `mv_node_centrality`, `mv_symbol_level_centrality`, `proj_centrality` |
| Blast radius | `mv_graph_critical_path_blast_radius`, `mv_critical_path_blast_radius`, `mv_multi_hop_dependency_analysis`, `proj_reachability`, `structural_outputs.blast_radius` |
| Chokepoints | `mv_graph_chokepoint_bridges`, `mv_chokepoints`, `proj_centrality.bridge_score` |
| SCC/cycles | approximate two-hop `mv_graph_scc_clusters` and exact NetworkX SCC |
| Debt risk | `mv_high_fan_in_out_with_defects`, `mv_risk_weighted_impact_scores`, `mv_debt_concentration_hotspots`, refactor score |
| Health | artifact health reporter, infrastructure health utility, MCP health, BCG reports |

`tools/graph/materialized_views/enhanced_graph_views.py` is not part of the canonical orchestrator, while `tools/adg/analysis/materialized_views.py` has separate consumers and tests.

### P1: Health surfaces disagree and fail open

- `health_reporter.py` uses fixed absolute thresholds such as 2,000 unresolved imports and 500 layer violations.
- `infrastructure/utils/adg_health.py` reports mostly raw counts.
- `ADGService.health()` hardcodes schema version `1.0` although canonical SQLite reports schema `4.x`.
- MCP quick health checks SQLite/Redis availability but not certification, finalization, graph integrity, required materializations, or projection freshness.
- `HealthDiagnostics._safe_projection_status()` converts projection errors into `available=false`, `stale=false`.
- Missing projections return zero blast radius, empty violations, empty diffs, or `None`, conflating “no finding” with “not evaluated.”
- `get_views_materialized_at()` detects any qualifying view, not the complete required physical-table/view manifest.

### P1: Identity and evidence are unstable

- Integer node IDs derive from sorted names and shift when earlier names are added.
- Edge IDs are autoincremented and have no stable occurrence key.
- Current reports expose samples such as `<id=77>`, which cannot be reliably compared across snapshots.
- `CanonicalSnapshot.graph_hash` hashes a set of `(from, relation, to)` triples, discarding edge multiplicity, kind, source location, symbol, evidence, and confidence.
- Several distinct graph changes can therefore share the same canonical graph hash.

### P1: Confidence is heuristic, not calibrated

`EdgeConfidence.py` assigns fixed scores by relation type and edge kind. There is no labeled calibration corpus, precision/recall measurement, expected calibration error, versioned model, or minimum sample requirement. Current confidence values should be described as heuristic evidence strength, not probability.

### P1: SQLite integrity controls are incomplete

- DDL declares foreign keys but writer and MV connections do not enable `PRAGMA foreign_keys=ON`.
- Integrity validation runs `PRAGMA integrity_check` but not `foreign_key_check`.
- Core enums and confidence ranges lack CHECK constraints.
- Core tables are not `STRICT`.
- Edges lack a uniqueness or occurrence-identity contract.
- Query plans are not governed through a canonical query catalog.
- `INSERT OR REPLACE` may hide identity or uniqueness defects.
- Candidate publication occurs before the complete final validation and certification sequence.

### P2: Current repository-health signals have useful but untrusted evidence

Latest diagnostic values include:

- 466 unresolved imports
- 1.49% first-party low-confidence ratio
- 17,970 inferred symbols, or 10.12%
- 935 resolved dead-import candidates
- 3,867 runtime-attested edges
- 222 runtime traces but zero traces with topology checks
- 455 synthetic runtime rows
- 256 registry-drift rows
- 275 dead-path rows
- 22 config-bloat rows
- zero triplet-attested rows

These signals should be retained as diagnostic inputs, but their denominators, eligibility rules, evidence confidence, and certification status must be made explicit.

## Duplication and Semantic-Conflict Matrix

| Surface | Decision |
|---|---|
| `tools/adg/generate_full_adg.py` | KEEP as compatibility shim |
| `tools/generate/generate_full_adg.py` | HARDEN and reduce to orchestration |
| `ArtifactPaths.py` + `multi_writer.py` | CONSOLIDATE into one writer and one schema |
| `normalizer.py` + `normalizer_config.py` | CONSOLIDATE after behavioral parity inventory |
| Phase A/B/C obligation MVs | KEEP, contract, and consolidate overlapping calculations |
| Phase D regression MVs | REPLACE with stable-key set diffs |
| Phase E graph intelligence | REPLACE approximate SCC/bridge/blast calculations |
| Phase F hotspot/coverage | HARDEN missing-data semantics and metric lineage |
| `enhanced_graph_views.py` | RETIRE or merge unique value into canonical metrics |
| `MaterializedViewManager` | RETIRE after consumer migration unless unique consumers are proven |
| `graph_projection.py` | HARDEN as the single offline graph-algorithm implementation |
| `tools/graphdb/project_graph.py` stack | CONSOLIDATE behind the canonical projection specification |
| `structural_outputs.py` | KEEP as a presentation/query adapter, not metric authority |
| `refactor_accelerator.py` | KEEP as a ranking consumer; externalize and version weights |
| `health_reporter.py` | REPLACE internals with unified health contracts |
| `infrastructure/utils/adg_health.py` | Convert to compatibility presentation adapter |
| MCP health | HARDEN to expose certification, completeness, and uncertainty |
| Pickle snapshots | Already removed; KEEP JSON-only prohibition |

## Target Architecture

`generate_full_adg.py` becomes a thin deterministic coordinator:

1. Discover source and configuration.
2. Create a unique candidate run directory.
3. Extract and normalize into an in-memory canonical contract.
4. Write one temporary SQLite candidate through one writer.
5. Add authority/runtime/registry evidence through governed writer modules.
6. Materialize canonical derived tables from registered metric/projection definitions.
7. Execute final integrity, conservation, determinism, and metric-contract checks.
8. Freeze final counts and digests.
9. Generate all reports from that frozen database only.
10. Run required gates.
11. Retain failed candidates as `repair_ready`.
12. Update the certified pointer only after all required gates pass.
13. Refresh Redis from the certified snapshot digest.
14. Serve all consumers from certified SQLite unless explicitly requesting a repair candidate.

No report may mutate canonical SQLite after finalization.

## Proposed Canonical Schema

### Core schema v5

| Object | Purpose |
|---|---|
| `adg_snapshot` | One authoritative row containing snapshot ID, commit, tree hash, source/config/scanner digests, timestamps, status and certification |
| `adg_schema_manifest` | Schema, metric-registry, relation-taxonomy and projection-spec versions |
| `node_types` | Controlled node vocabulary |
| `relation_types` | Direction, inverse rule, allowed endpoints, multiplicity and projection eligibility |
| `nodes` | Surrogate integer ID plus stable `node_key`, canonical name, type, layer, path and span |
| `edges` | Surrogate ID plus stable `edge_key`, stable endpoints, relation, kind and occurrence fields |
| `edge_evidence` | One-to-many extractor/runtime/registry evidence with provenance, confidence method and evidence reference |
| `extractor_runs` | Extractor identity, version, configuration, duration, counts and digest |
| `scan_units` | Every eligible file/unit with parsed, excluded, failed or unsupported disposition |
| `violations` | Existing compatibility surface backed by stable finding keys |
| `stage_receipts` | Stage status, input/output digests, duration, counts, errors and requiredness |
| `projection_specs` | Named graph population, node level, relation set, direction, aggregation and weighting |
| `algorithm_runs` | Algorithm, exact/approximate flag, parameters, seed, version, duration and projection digest |
| `metric_definitions` | Stable metric contracts and versions |
| `metric_observations` | Current values, numerator, denominator, unit, confidence and status |
| `finding_instances` | Stable actionable findings with lifecycle state |
| `finding_evidence` | Node, edge, path, source and test evidence |
| `snapshot_deltas` | Stable-key added, resolved, reopened and changed findings |
| `gate_results` | PASS/FAIL/WARN/UNKNOWN/SKIPPED/NOT_APPLICABLE with policy version |

### Required constraints

- New tables use `STRICT` when supported.
- `PRAGMA foreign_keys=ON` on every writer connection.
- `node_key` and `edge_key` are unique and immutable within a snapshot.
- Confidence is constrained to `[0,1]`.
- Enum fields use FK or CHECK constraints.
- `source_file`, line/span and evidence rules depend on relation type.
- Synthetic rows require explicit `origin_kind`, producer and evidence.
- JSON fields are validated with `json_valid`.
- Finalization prevents later canonical writes.
- Compatibility views preserve old column names during migration.

### Stable identity

- `snapshot_id = sha256(commit_sha + repo_state_hash + scanner_digest + config_digest + canonical_content_digest)`.
- `node_key = sha256(namespace + entity_type + canonical_path + canonical_symbol + stable_span_identity)`.
- `edge_key = sha256(src_node_key + relation_type + dst_node_key + edge_kind + occurrence_identity)`.
- Integer IDs remain local surrogates only.
- Reports and MCP return stable keys and names; integer IDs are optional diagnostics.

## High-Value Metric Portfolio

Every observation must carry `metric_id`, version, snapshot, numerator, denominator, population, exclusions, confidence, status and evidence query.

| Metric contract | Definition and decision | Exactness, threshold and action |
|---|---|---|
| `RH.TRUST.001 certification_state` | Whether the frozen snapshot passed every required stage and gate | Exact; PASS only when all required receipts PASS; any missing receipt = UNKNOWN; controls certified promotion |
| `RH.TRUST.002 snapshot_consistency` | Count/hash differences among finalized SQLite, meta, reports and manifests | Exact; threshold zero; any mismatch blocks certification |
| `RH.TRUST.003 extraction_coverage_rate` | Successfully parsed eligible units / all eligible units, dimensioned by language, domain and first-party/test/generated status | Exact; compare with certified baseline; missing denominator = UNKNOWN; directs scanner remediation |
| `RH.TRUST.004 internal_resolution_rate` | Authoritative resolved internal candidates / resolvable internal candidates by relation and extractor | Exact classification; external/test-only excluded from first-party rate; regressions block only after stable baseline |
| `RH.TRUST.005 confidence_calibration` | Precision, recall, Brier score and expected calibration error against versioned labeled fixtures | Statistical; minimum 30 labeled cases per extractor/tier or UNKNOWN; prevents probabilistic claims from heuristics |
| `RH.TRUST.006 reproducibility` | Equality of canonical content digests from repeated identical inputs | Exact; three consecutive builds must match before release |
| `RH.GRAPH.001 production_orphan_rate` | Eligible production modules not reachable from approved roots on the named module-dependency projection / eligible production modules | Exact bounded reachability; replaces raw fan-in-zero; evidence includes shortest attempted root path |
| `RH.GRAPH.002 illegal_layer_path_rate` | Unauthorized layer transitions or reachable forbidden paths / eligible cross-layer paths | Exact against versioned layer policy; zero-tolerance only for explicitly P0 rules |
| `RH.GRAPH.003 cycle_burden` | Non-trivial SCC count, nodes in SCCs, maximum SCC, and criticality-weighted SCC burden | Exact SCC on directed module projection; components remain separately visible; new critical-layer SCC blocks |
| `RH.GRAPH.004 blast_radius_distribution` | Distinct dependent production modules at hops 1–4 by relation-specific projection | Exact bounded BFS; emit raw counts and percentiles; rank changes and impacted tests |
| `RH.GRAPH.005 chokepoint_risk` | Exact articulation/bridge status on an explicitly undirected resilience projection plus sampled directed betweenness | Mixed; exact and approximate components never merged without labels; report-only until validated |
| `RH.GRAPH.006 dependency_concentration` | HHI and top-1% share of inbound production dependencies by layer/domain | Exact; trend signal; identifies architectural concentration without arbitrary degree thresholds |
| `RH.COVER.001 critical_surface_test_gap` | High-impact changed modules lacking fresh coverage or valid `covers`/impacted-test evidence / high-impact changed modules | Exact eligibility; NOT_COLLECTED differs from ZERO; drives test creation |
| `RH.RUNTIME.001 obligation_witness_coverage` | Eligible architectural obligations with required static/test/runtime witnesses / eligible obligations, by obligation family | Exact contract evaluation; runtime evidence required only where the obligation declares it |
| `RH.SURFACE.001 governed_surface_gap` | Missing required control evidence, dimensioned by Execution, Write, Security, State and Observability | Exact per surface contract; critical gaps cannot be averaged away |
| `RH.CHANGE.001 decomposed_change_risk` | Versioned rank using churn percentile, complexity percentile, blast-radius percentile and test gap | Deterministic ranking, not a merge verdict; all components remain visible; weights live in metric registry |
| `RH.OWN.001 ownership_concentration` | Contributor concentration and minimum contributor set covering 50%/80% of recent changes | Exact over declared Git window; minimum 20 relevant commits or UNKNOWN; informs review/ownership action |
| `RH.TREND.001 finding_lifecycle` | Stable-key counts of added, resolved, reopened and persistent findings | Exact set diff between certified snapshots; replaces current Phase D “new” fields |
| `RH.SQL.001 sqlite_operational_health` | Integrity, FK violations, query p50/p95, slow-query count, page count, freelist ratio and snapshot size | Exact measurements; integrity/FK nonzero blocks; performance uses Wave 0 baselines |
| `RH.FRESH.001 snapshot_freshness` | Active snapshot commit/tree/config match, age and projection digest parity | Exact; stale or mismatched inputs produce DEGRADED/UNKNOWN, never healthy |

## Rejected or Deferred Metrics

- Global graph density across heterogeneous module/symbol/runtime/registry nodes: reject as non-actionable.
- Average clustering over the current mixed projection: reject.
- Two-hop mutual reachability labeled as SCC: retire.
- Raw degree across mixed relation types: replace with named projections.
- A single opaque repository-health score: reject.
- Triplet-attested fraction across every static edge: replace with obligation-eligible witness coverage.
- “Unobserved code” as a defect without runtime eligibility: reject.
- Fixed fan-in/fan-out thresholds as universal health gates: replace with percentiles and policy exceptions.
- All-layer weight `2.0`: retire.
- Raw node and edge growth as health: retain only as inventory and normalization denominators.
- Approximate centrality as a merge gate: defer permanently unless a validated decision contract is established.
- Community detection/modularity: defer until module-boundary alignment has a named consumer and reliable projection.

## Wave-Based Implementation Plan

## Wave 0: Baseline, inventory and executable contracts

### Objective

Freeze definitions and measure current behavior before changing authority.

### Files

- New `docs/architecture/adg_sqlite_repo_health_target.md`
- New `tools/adg/contracts/metric_registry.py`
- New `tools/adg/contracts/metric_registry.json`
- New `tools/adg/audit/surface_inventory.py`
- New `ops_scripts/ci/check_adg_metric_registry.py`
- New `tests/unit/tools/adg/contracts/test_metric_registry.py`
- Update `plans/adg-sqlite-repo-health-hardening-20260711.md`

### Work

1. Inventory every producer, table, view, report, gate, MCP method and Redis projection.
2. Record all current schema variants and metric formulas.
3. Benchmark full generation, each stage, MV materialization, DB size and the top 20 consumer queries.
4. Capture `EXPLAIN QUERY PLAN` output.
5. Establish the named graph projections and relation semantics.
6. Record executable contracts and migration boundaries directly in the implementation branch.
7. Execute Waves 1–9 without a design-approval package gate; pause only for a material scope or authority blocker.

### Acceptance

- 100% of current `mv_*`, `v_p*`, `proj_*`, report and gate surfaces inventoried.
- Every current metric receives KEEP/HARDEN/CONSOLIDATE/REPLACE/RETIRE.
- Baseline includes p50/p95 and row counts for the top 20 queries.
- No production behavior changes.

### Rollback

Delete only the new diagnostic files; no runtime rollback required.

## Wave 1: One schema, one writer, atomic candidate finalization

### Objective

Eliminate writer/schema forks and prevent inconsistent snapshots from becoming active.

### Files

- New `agentic_core/adg/artifact/schema_v5.py`
- New `agentic_core/adg/artifact/sqlite_writer.py`
- New `agentic_core/adg/artifact/finalization.py`
- Update `ArtifactPaths.py`
- Update `multi_writer.py`
- Update `normalizer.py`
- Update `normalizer_config.py`
- Update `tools/generate/generate_full_adg.py`
- Update `tools/generate/validation/integrity.py`
- Update `tools/adg/shared_modules/path_resolver.py`
- New `tests/agentic_core/adg/artifact/test_sqlite_writer_contract.py`
- New `tests/agentic_core/adg/artifact/test_snapshot_finalization.py`

### Work

1. Make `sqlite_writer.py` the only writer.
2. Convert `ArtifactPaths.py` and `multi_writer.py` to thin compatibility adapters.
3. Introduce schema v5 stable keys and constraints.
4. Build candidate SQLite entirely in a temporary run directory.
5. Run every canonical mutation before final counts and digests.
6. Enable FK enforcement and run `integrity_check` plus `foreign_key_check`.
7. Generate reports only after finalization.
8. Emit separate candidate and certification manifests.
9. Maintain a portable `certified_snapshot.json` pointer.
10. Never update the certified pointer for failed runs.

### Acceptance

- Exactly one DDL and writer authority.
- Zero FK, count, hash or manifest inconsistencies.
- Identical inputs produce identical canonical content digests.
- A forced failure retains a repair candidate but leaves the certified pointer unchanged.
- Existing compatibility imports remain green.

### Rollback

Repoint `certified_snapshot.json` to the last certified v4 snapshot; no in-place database rollback.

## Wave 2: Extraction completeness, identity and calibrated confidence

### Objective

Make extraction quality measurable and every confidence claim defensible.

### Files

- `agentic_core/adg/extraction/static_scanner.py`
- `agentic_core/adg/artifact/builder_types.py`
- `agentic_core/adg/identity/normalizer.py`
- `agentic_core/adg/analysis/EdgeConfidence.py`
- `agentic_core/adg/artifact/edge_authority.py`
- New `data/adg/golden/extraction_calibration.jsonl`
- New `tests/unit/agentic_core/adg/test_identity_stability.py`
- New `tests/unit/agentic_core/adg/test_edge_confidence_calibration.py`

### Work

1. Emit one `scan_units` row for every eligible input.
2. Separate parsed, excluded, unsupported and failed states.
3. Generate stable node and edge keys.
4. Preserve multiple evidence records instead of collapsing them into one edge score.
5. Rename existing fixed scores to `heuristic_evidence_strength`.
6. Build calibration fixtures from confirmed historical defects.
7. Report precision, recall and calibration only when sample sufficiency is met.
8. Dimension resolution by relation, extractor, layer and first-party status.

### Acceptance

- 100% of eligible inputs have a terminal scan disposition.
- Stable fixtures retain identical node/edge keys across unrelated insertions.
- No confidence value is presented as calibrated without a valid calibration receipt.
- Existing extraction counts are conserved or differences are fully dispositioned.

### Rollback

Compatibility views retain v4 node/edge columns; revert the scanner/builder while preserving the v5 candidate behind the inactive pointer.

## Wave 3: SQLite query, index and traversal hardening

### Objective

Make canonical SQLite fast, bounded and correct for graph retrieval.

### Files

- `tools/adg/core/sqlite_backend.py`
- New `tools/adg/core/query_catalog.py`
- New `tools/adg/core/traversal.py`
- `tools/generate/materialized_views/sqlite_helpers.py`
- `tools/generate/validation/integrity.py`
- New `ops_scripts/ci/check_adg_query_plans.py`
- New `tests/unit/tools/adg/test_traversal_contract.py`
- New `tests/performance/test_adg_query_budgets.py`

### Work

1. Register every supported query and required index.
2. Add composite/covering/partial indexes based on measured plans.
3. Fix SQL traversal to return complete node and edge paths.
4. Add direction, relation, authority, population and depth to traversal contracts.
5. Enforce cycle safety, deterministic ordering, result caps and timeout budgets.
6. Distinguish EMPTY, UNAVAILABLE, STALE and TRUNCATED.
7. Run `ANALYZE` and `PRAGMA optimize` before final freeze.
8. Prevent consumers from issuing arbitrary unbounded recursive queries.

### Acceptance

- Traversal fixtures match expected paths exactly.
- Top 20 query p95 is no worse than 1.10× the Wave 0 baseline.
- No unexpected full scan appears in governed query plans.
- Every truncated traversal reports frontier size, visited count, depth and truncation reason.

### Rollback

Retain old methods behind compatibility wrappers and switch the certified pointer back if query parity fails.

## Wave 4: Canonical graph projections and exact algorithms

### Objective

Replace misleading graph calculations with named, conserved projections.

### Files

- `tools/generate/graph_projection.py`
- `tools/adg/core/graph_projection_backend.py`
- `tools/graphdb/projection.py`
- `tools/graphdb/project_graph.py`
- `tools/graphdb/schema.py`
- `tools/generate/materialized_views/phase_e_graph_intelligence.py`
- `tools/graph/materialized_views/enhanced_graph_views.py`
- `tools/adg/analysis/materialized_views.py`
- `tools/adg/structural_outputs.py`
- New `tools/adg/graph/projection_specs.py`
- New `tools/adg/graph/algorithms.py`
- New `tests/unit/tools/adg/graph/test_algorithm_parity.py`

### Work

1. Define separate projections for module dependencies, call dependencies, data flow, governance, runtime and registry evidence.
2. Use `MultiDiGraph` for lossless projection.
3. Collapse to algorithm-specific graphs only through registered aggregation rules.
4. Enforce conservation: included plus explicitly excluded rows must equal canonical eligible rows.
5. Use exact directed SCCs.
6. Use exact bounded BFS for blast radius.
7. Use exact articulation/bridge calculations only on the named undirected resilience projection.
8. Keep sampled betweenness report-only and preserve seed/sample metadata.
9. Remove silent type drops.
10. Read actual scanner/schema versions.
11. Remove stale-result serving from authoritative MCP methods.
12. Retire approximate Phase E SCC and duplicate centrality/blast tables after compatibility validation.

### Acceptance

- 100% conservation accounting for nodes and eligible edges.
- Exact algorithm output matches golden graphs.
- No approximate result is labeled exact.
- Identical snapshots generate identical algorithm outputs and digests.
- Stale projections return STALE/UNKNOWN, never an authoritative value.

### Rollback

Keep current projection tables readable for one compatibility window; do not use them for new health decisions.

## Wave 5: Unified repository-health metrics and findings

### Objective

Create one high-value metric and finding authority.

### Files

- New `tools/adg/health/metric_engine.py`
- New `tools/adg/health/finding_engine.py`
- New `tools/adg/health/contracts.py`
- `agentic_core/adg/applications/health_reporter.py`
- `infrastructure/utils/adg_health.py`
- `tools/adg/refactor_accelerator.py`
- `tools/generate/materialized_views/phase_a_path_authority.py`
- `phase_b_capability_tool_task.py`
- `phase_c_trace_drift_debt.py`
- `phase_f_hotspot_coverage.py`
- New `tests/unit/tools/adg/health/test_metric_contracts.py`
- New `tests/unit/tools/adg/health/test_finding_evidence.py`

### Work

1. Implement the approved metric portfolio.
2. Persist definition version with every observation.
3. Emit stable finding keys and evidence paths.
4. Separate inventory, risk, breach and blocker semantics.
5. Preserve the five governed surfaces independently.
6. Make missing coverage `NOT_COLLECTED`, not zero.
7. Externalize refactor-ranking weights.
8. Prohibit a global score from hiding any critical failure.
9. Replace fixed absolute health thresholds with normalized rates, approved zero-tolerance rules and certified baselines.

### Acceptance

- Every metric observation validates against its registry contract.
- Every blocker has evidence and a smallest-safe remediation.
- Required UNKNOWN/SKIPPED metrics prevent a healthy verdict.
- No metric has more than one calculation authority.
- Existing reports can be regenerated from metric/finding rows.

### Rollback

Presentation adapters can read legacy MVs while the new metric engine remains non-authoritative until parity is proven.

## Wave 6: Exact temporal history and regression detection

### Objective

Replace pseudo-deltas with stable finding lifecycle intelligence.

### Files

- `tools/generate/materialized_views/phase_d_snapshot_regression.py`
- `agentic_core/adg/analysis/CanonicalSnapshot.py`
- `agentic_core/adg/analysis/GraphDiff.py`
- `tools/generate/graph_projection.py`
- New `tools/adg/history/certified_history.py`
- New `tests/unit/tools/adg/history/test_exact_snapshot_diff.py`
- New `tests/unit/tools/adg/history/test_finding_lifecycle.py`

### Work

1. Compare only certified snapshots.
2. Diff stable node, edge and finding keys.
3. Track added, resolved, reopened, persistent and changed.
4. Use artifact digest identity, not commit alone.
5. Preserve metric-definition versions and block invalid cross-version comparisons.
6. Add baseline windows, minimum samples and hysteresis.
7. Make the history catalog a rebuildable projection over immutable certified snapshots, never a second graph authority.
8. Replace all current `is_new` implementations.

### Acceptance

- Identical consecutive snapshots yield zero added/resolved findings.
- Fixture changes produce exact expected deltas.
- Current snapshot IDs are never empty.
- No current row is marked new solely because it exists.
- Definition changes produce `NOT_COMPARABLE`, not false regression.

### Rollback

Retain prior certified snapshots and rebuild the derived history catalog from them.

## Wave 7: MCP, CI, report and Redis consumer unification

### Objective

Make every consumer receive consistent certification, provenance and uncertainty.

### Files

- `tools/adg/core/service.py`
- `tools/adg/core/sqlite_backend.py`
- `tools/adg/mcp/health.py`
- `tools/adg/mcp/runtime.py`
- `tools/adg/shared_modules/path_resolver.py`
- `tools/adg/core/redis_cache.py`
- `tools/generate/reporting/**`
- `ops_scripts/ci/adg_gates/**`
- `ops_scripts/ci/check_pipeline_skips.py`
- New `ops_scripts/ci/check_adg_consumer_contract.py`
- New `tests/unit/tools/adg/test_adg_consumer_contract.py`

### Work

1. Resolve certified versus repair snapshots explicitly.
2. Return real schema, snapshot, content and certification versions.
3. Add status enums: PASS, FAIL, WARN, UNKNOWN, SKIPPED and NOT_APPLICABLE.
4. Eliminate unavailable-to-zero fallbacks.
5. Require a complete materialization manifest, not “any view exists.”
6. Re-key Redis by certified snapshot digest and metric version.
7. Make projection staleness and missing required stages visible in every affected response.
8. Generate reports from persisted metric/finding rows.
9. Permit diagnostic access to repair candidates only through an explicit request and provenance marker.

### Acceptance

- Failed candidates never become default MCP snapshots.
- Redis and SQLite responses identify the same certified digest.
- MCP health cannot report healthy when certification or required metrics are unavailable.
- Empty findings and unavailable evaluation are distinguishable.
- Consumer contract tests cover every MCP method.

### Rollback

Disable v5 consumer routing and repoint to the last certified v4 snapshot.

## Wave 8: Deterministic testing, performance and release gates

### Objective

Prove correctness, determinism, resilience and cost.

### Evaluation alignment

- ADG formulas and checkers use deterministic micro-evals/unit tests aligned to X2.
- Full deterministic pipeline runs are integration/regression tests, not mislabeled model suite evals.
- No LLM writer or judge is required for graph correctness.
- If a downstream model-generated report is later evaluated, it uses the separate lane/suite/meta ladder and never waives ADG runtime gates.

### Files

- Expand all new tests above
- `tests/unit/tools/generate/test_generate_full_adg_failfast.py`
- `tests/unit/tools/generate/test_graph_projection.py`
- `tests/unit/tools/generate/test_adg_graph_intelligence.py`
- `tests/unit/tools/adg/test_adg_mcp_fixes.py`
- New `tests/property/adg/**`
- New `tests/performance/adg/**`
- New `ops_scripts/ci/check_adg_release_readiness.py`

### Required verification

    python -m pytest tests/agentic_core/adg/artifact -q
    python -m pytest tests/unit/agentic_core/adg -q
    python -m pytest tests/unit/tools/generate/test_graph_projection.py -q
    python -m pytest tests/unit/tools/generate/test_adg_graph_intelligence.py -q
    python -m pytest tests/unit/tools/adg -q
    python -m pytest tests/property/adg -q
    python -m pytest tests/performance/adg -q
    python ops_scripts/ci/check_adg_metric_registry.py
    python ops_scripts/ci/check_adg_query_plans.py
    python ops_scripts/ci/check_pipeline_skips.py
    python ops_scripts/ci/check_snapshot_has_mvs.py
    python ops_scripts/ci/check_graph_layer_evidence.py
    python ops_scripts/ci/check_adg_consumer_contract.py
    python ops_scripts/ci/check_adg_release_readiness.py
    python -m tools.generate.generate_full_adg

### Acceptance

- Three identical full builds produce identical canonical digests.
- Zero integrity, FK, conservation, lineage or report-consistency defects.
- All exact algorithms match golden fixtures.
- Full-generation duration is no worse than 1.10× the approved Wave 0 baseline unless separately approved.
- Snapshot size is no worse than 1.15× baseline without a documented value-bearing schema increase.
- Top-query p95 remains within the Wave 3 budget.
- Crash-injection tests never replace the certified pointer.
- No mock, UNKNOWN or SKIPPED result can satisfy a required gate.

## Wave 9: Documentation, deprecation and closeout

### Objective

Remove obsolete authority and make operation unambiguous.

### Files

- `.codex/rules/adg-canonical-invariants.md`
- `.codex/skills/adg-sqlite/SKILL.md`
- `.codex/skills/graph-analysis/SKILL.md`
- `docs/tools/adg_persistence_guide.md`
- `docs/technical/graphdb_ci_hardening.md`
- `tools/adg/mcp/OPERATIONS.md`
- New `docs/runbooks/adg_candidate_recovery.md`
- New `docs/runbooks/adg_certification_and_rollback.md`
- Deprecate or remove superseded writer, MV and projection modules

### Work

1. Correct phase/table counts and source-of-truth diagrams.
2. Document every metric and projection.
3. Publish operator recovery, rollback, retention and performance runbooks.
4. Remove deprecated code after zero live consumers are proven.
5. Archive old baselines with semantic-version provenance.
6. Produce final before/after evidence.

### Acceptance

- Zero non-test imports of retired modules.
- Documentation matches generated schema and metric manifests automatically.
- One command identifies active certified and latest repair snapshots.
- Final full ADG run is certified and all release gates pass.

## ADG_HOTSPOT_REPORT

| Rank | Hotspot | Evidence | Surfaces |
|---:|---|---|---|
| 1 | `ArtifactPaths.py` / `multi_writer.py` | Divergent DDL, confidence columns, precision tables and severity SQL | Write, State, Security, Observability |
| 2 | `tools/generate/generate_full_adg.py` | Approximately 2,966 lines coordinating writes, enrichment, projections, gates, repair and reporting | Execution, Write, State, Observability |
| 3 | Dual graph projection stacks | Directed mixed simple graph versus undirected simple graph; silent loss and overlapping algorithms | Execution, State, Security, Observability |
| 4 | Phase D regression tables | Current rows labeled “new” without exact prior-row comparison | State, Observability |
| 5 | Health/MCP stack | Hardcoded schema, fixed thresholds and unavailable-to-empty fallback | Execution, State, Observability |
| 6 | Snapshot resolution | Newest-by-mtime selection can activate failed repair candidates | Execution, State, Security |
| 7 | MV registry/documentation | Six phases and approximately 52 tables described as four phases and 42 tables | State, Observability |
| 8 | Current report consistency | +1 node, +102 edges, timestamp mismatch and multiple edge populations | All five surfaces |

## ADG_GRAPH_LAYER_EVIDENCE

| Evidence surface | Current evidence | Planned treatment |
|---|---|---|
| `mv_graph_vs_report_mismatches` | Current committed report shows count and timestamp mismatches | Make zero rows a certification prerequisite |
| `mv_hotspot_centrality` | Canonical Phase A hotspot source, but overlaps other centrality stores | Retain one named projection and metric authority |
| `mv_write_sovereignty_paths` | Current inventory reports 99 non-UWG paths | Preserve as Write-surface evidence with exact eligibility |
| `mv_snapshot_regression_summary` | Aggregate deltas exist but row-level “new” semantics are invalid | Replace in Wave 6 |
| `mv_handoff_witness_tiers` | Consumed by runtime-spine reporting | Preserve and bind to obligation contracts |
| `mv_cross_cutting_witness_tiers` | Covers 13 architectural obligation families | Preserve and normalize denominators |
| `v_p0_write_bypass_uwg` | P0 write-bypass evidence | Preserve compatibility; route through unified finding engine |
| `v_p1_not_on_spine` | Spine reachability evidence | Preserve with stable root/projection definition |
| `v_p0_l6_mutation` | Observability mutation evidence | Preserve as zero-tolerance L6 breach |
| Semantic edges | `imports`, `calls`, `writes_to`, `reads_from`, `emits_side_effect`, `resolves_callsite`, `covers` | Assign each to named projections; never mix by convenience |
| Runtime evidence | 3,867 attested rows, 222 traces, zero topology-checked traces | Keep separate from static evidence and report eligibility |

## Schema and Data Migration Plan

1. Build v5 snapshots from source; do not alter old SQLite files in place.
2. Add compatibility views for old node, edge, violation and MV consumers.
3. Run v4 and v5 generation against the same commit for parity.
4. Map legacy integer evidence to stable keys using canonical name, path, symbol, span and relation occurrence.
5. Do not dual-write through two writer implementations.
6. Approve a single cutover after conservation and consumer parity pass.
7. Re-key Redis using the v5 certified digest.
8. Preserve old ratchet baselines as archived v4 evidence.
9. Seed v5 baselines only after metric-definition approval and two comparable certified runs.
10. Rollback by changing the certified pointer, not by mutating a snapshot.
11. Retire v4 compatibility only after repository search and ADG reachability prove zero consumers.

## Performance and Resource Budgets

Wave 0 must measure actual budgets. Do not invent absolute limits.

Release budgets:

- Full generation: no more than 10% slower than the approved comparable baseline.
- MV refresh: no more than 10% slower unless replacing approximate algorithms with approved exact work.
- Snapshot size: no more than 15% larger without approved schema-value justification.
- Top 20 query p95: no more than 10% slower than the indexed Wave 3 baseline.
- Traversal: bounded by declared depth, frontier and row caps.
- Approximate algorithms: deterministic seed, recorded sample size and bounded duration.
- CI-light checks must not require loading the full NetworkX graph.
- Offline exact graph computations remain generation-time work, not MCP runtime work.

## Risk Register

| Risk | Mitigation |
|---|---|
| Schema migration breaks consumers | Compatibility views, consumer inventory and certified-pointer rollback |
| Exact algorithms increase runtime | Named projections, conservation filters, profiling and offline-only computation |
| Stable-key formula changes identity | Version key derivation and preserve old key mapping |
| Historical comparison crosses metric versions | Emit NOT_COMPARABLE |
| Metric thresholds create false blockers | Baseline first, minimum samples, hysteresis and separate inventory from breach |
| Approximate values are mistaken for proof | Persist exactness, algorithm and parameter metadata |
| Failed snapshot is served | Certified pointer and explicit repair-candidate access |
| Missing data becomes zero | Typed UNKNOWN/NOT_COLLECTED states |
| Redis diverges | Digest-keyed cache with SQLite hydration/fallback |
| Report generation mutates or races snapshot | Freeze before report generation; immutable read-only access |
| Graph projection loses relations | MultiDiGraph plus conservation accounting |
| Health score hides critical defects | No opaque aggregate; surface-level fail-closed verdicts |
| Baseline gaming | Versioned approval record, reviewer, rationale and no P0 rebaseline shortcut |

## Final Definition of Done

The hardening is complete only when:

1. One schema and one writer produce canonical SQLite.
2. The latest full run is certified.
3. Failed candidates cannot become active.
4. Final SQLite, metadata, manifests and every report agree exactly.
5. Stable node, edge, metric and finding identities support exact history.
6. Every projection declares population, direction, relation set and aggregation.
7. Exact and approximate algorithms are never conflated.
8. Duplicate centrality, SCC, blast-radius, regression and health authorities are retired.
9. Every metric has a registered decision, formula, denominator, confidence and remediation.
10. Static, runtime and registry evidence remain separately attributable.
11. MCP distinguishes empty, stale, unavailable, skipped and unknown.
12. Redis remains a non-authoritative projection.
13. Deterministic micro-evals and tests cover every checker.
14. All integrity, FK, conservation, query-plan, consumer and performance gates pass.
15. Documentation and runbooks are generated or verified against the live schema and metric manifests.