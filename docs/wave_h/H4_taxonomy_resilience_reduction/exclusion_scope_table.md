# H4 — Exclusion Scope Table

wave: H4
adg_snapshot: artifacts/adg/adg_indexed_04182026_1558.sqlite
adg_snapshot_timestamp: "04182026_1558"

Required enum:

- production_safe_included
- pilot_only
- production_excluded
- unresolved

## Taxonomy residual area classification

| residual_area | basis | classification | boundary_rule | card_family_impact |
|---|---|---|---|---|
| ADG internals stable subset (`agentic_core/adg/*` stable graph-analysis/support paths) | clustered in `unclassified_modules.md`; snapshot-bound structures | production_safe_included | include only snapshot-bound deterministic symbol/path/hotspot facts | symbol/path/hotspot mostly includable |
| Evaluation internals subset (`evaluation/*` non-partial stable surfaces) | large residual cluster with known semantics | pilot_only | include under explicit residual tags until full decomposition metrics are complete | hotspot/symbol/path constrained; violation remains pilot-only |
| Knowledge internals subset (`knowledge/*` broad mixed certainty) | residual cluster with mixed certainty and storage sensitivity | production_excluded | exclude from production packaging unless promoted to stable classified subset | path/symbol/pipeline constrained |
| Prompt-governance internals (`prompt_governance/*` mixed role certainty) | residual cluster; governance-critical semantics | production_excluded | exclude from production-safe packaging until decomposition closure evidence exists | violation/pipeline/state-machine constrained |
| Runtime utility + singleton mixed cluster (`utils/*` + singleton `other` modules) | high heterogeneity and low role certainty | unresolved | hold out of production-safe packaging pending explicit role decomposition | broad family uncertainty; keep out of production scope |
| Replay-deep and system_learning-deep residual spans (context-linked exclusions) | H0/H1/H3 carry-forward policy | production_excluded | remain explicitly excluded from production claims in H4 | pipeline/state-machine/replay/system-learning families excluded |
