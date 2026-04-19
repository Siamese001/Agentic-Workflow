# H4 — Taxonomy Reduction Assessment

wave: H4
adg_snapshot: artifacts/adg/adg_indexed_04182026_1558.sqlite
adg_snapshot_timestamp: "04182026_1558"

## Scope

- `B7-G6-04` (337-module `role=other` taxonomy residual)

## H1 closure tests applied

1. taxonomy decomposition reaches production-safe threshold
2. unresolved remainder is bounded and excluded
3. card family scope reflects new taxonomy certainty

## Direct evidence basis

- `docs/wave_g/G1_core_runtime_inventory/unclassified_modules.md`:
  - `role=other` count = 337 modules across 99 subsystem clusters.
- `docs/wave_g/G6_taxonomy_cleanup/normalization_matrix.md`:
  - `G6-S013` keeps this bucket as `ambiguous_needing_followup` and blocker-class.
- `docs/wave_g/G7_integrated_runtime_map/*`:
  - `B7-G6-04` still open and production-blocking in G7/H0/H1/H3 lineage.
- `docs/wave_h/H0_readiness_and_pilot/go_no_go_matrix.md`:
  - production-safe vs pilot-only card-family boundaries already defined.

## Stable subcluster partition (inside residual bucket)

Derived from the largest, repeatedly-identified cluster families in `unclassified_modules.md` and cross-cutting table:

1. **ADG internals cluster** (`agentic_core/adg/*`, including extraction/analysis/applications/artifact/client/processing)
2. **Evaluation internals cluster** (`agentic_core/evaluation/*`, especially retrieval/metrics/judges/monitoring/feedback)
3. **Knowledge pipeline internals cluster** (`agentic_core/knowledge/*`, loaders/chunking/retrieval/lifecycle/observability/query)
4. **Runtime utility cluster** (`agentic_core/utils/*`, plus isolated cross-cutting singletons)
5. **Prompt-governance internals cluster** (`agentic_core/prompt_governance/*` subtrees)
6. **Mixed special-surface small clusters** (single-digit module groups and singleton files)

## Production packaging disposition by subcluster

### Production-safe included (bounded)

- **Subset inclusion only** of clusters that already map to `safe_now` card families without unresolved authority/control-plane dependence:
  - ADG internals subset for snapshot-bound **symbol/path/hotspot** packaging,
  - evaluation subset for snapshot-bound **hotspot/limited symbol-path** packaging,
  - failure-domain-supporting subset where lineage is already stable.

### Production excluded or unresolved

- Full-bucket broad inclusion of all 337 modules remains disallowed.
- Mixed/special singleton cluster remains excluded where role certainty is still narrative-only.
- Any subcluster that would emit production canonical claims in unresolved governance/authority areas remains excluded.

## Card families directly affected

From H0 card-family matrix and H1 blocker impact:

- directly constrained by taxonomy certainty:
  - `symbol cards`
  - `path cards`
  - `hotspot cards`
  - `pipeline cards`
  - `state-machine cards`
- boundary effect:
  - `violation cards` remain pilot-only under residual labeling discipline.

## H1 closure-test outcomes

- Test 1 (decomposition reaches production-safe threshold): **partial pass**
  - subclusters are now explicit and bounded, but full production-safe threshold for the whole residual bucket is not evidenced.
- Test 2 (remainder bounded and excluded): **pass (bounded exclusion posture)**
  - exclusion boundaries are explicit in H4 scope table.
- Test 3 (card family scope reflects certainty): **pass (bounded)**
  - family-level impacts and production inclusion/exclusion are explicitly scoped.

## Net result

`B7-G6-04` is **narrowed but not fully closed**:

- H4 establishes a production-safe **subset** posture with explicit exclusions,
- but does not prove full taxonomy closure for the entire 337-module residual bucket.
