"""Candidate fact ledger loading and selection policy helpers (ingress-only utilities)."""

from importlib import import_module

from .candidate_fact_ledger import (
    ConfidenceBand,
    fact_usage_band,
    jd_briefing_cannot_create_facts_note,
    load_master_candidate_fact_ledger,
    load_master_role_family_taxonomy,
    normalize_role_family_id,
    validate_fact_shape,
)

# Lazy reachability anchors for hardening and validation modules that must stay
# on the live ADG path without forcing package-import side effects.
_REACHABILITY_ANCHOR_SPECS = {
    "_apply_c03_graph_full_zero_loss_overwrite": (
        "apps_rg.fact_inventory.apply_c03_graph_full_zero_loss_overwrite",
        "apply_overwrite",
    ),
    "_apply_c03_graph_skill_granularity_hardening": (
        "apps_rg.fact_inventory.apply_c03_graph_skill_granularity_hardening",
        "apply_hardening",
    ),
    "_apply_graphdb_capability_sqlite_hardening": (
        "apps_rg.fact_inventory.apply_graphdb_capability_sqlite_hardening",
        "apply_graphdb_capability_sqlite_hardening",
    ),
    "_harden_augmented_skills_graph_payload": (
        "apps_rg.fact_inventory.c03_graph_skill_hardening",
        "harden_augmented_skills_graph_payload",
    ),
    "_validate_metric_heterogeneity": (
        "apps_rg.fact_inventory.graph_metric_heterogeneity_policy",
        "validate_metric_heterogeneity",
    ),
    "_materialize_graphdb_capability_indexes": (
        "apps_rg.fact_inventory.graph_sqlite_path_index",
        "materialize_graphdb_capability_indexes",
    ),
    "_validate_c03_graph_hardening_payload": (
        "apps_rg.fact_inventory.validate_c03_graph_hardening",
        "validate_c03_graph_hardening_payload",
    ),
    "_validate_c03_graph_skill_granularity": (
        "apps_rg.fact_inventory.validate_c03_graph_skill_granularity",
        "validate_graph",
    ),
    "_validate_graph_sqlite_path_index": (
        "apps_rg.fact_inventory.validate_graph_sqlite_path_index",
        "validate_graph_sqlite_path_index",
    ),
}


def _load_reachability_anchor(name: str) -> object:
    module_name, attr_name = _REACHABILITY_ANCHOR_SPECS[name]
    anchor = getattr(import_module(module_name), attr_name)
    globals()[name] = anchor
    return anchor


def __getattr__(name: str) -> object:
    if name == "_REACHABILITY_ANCHORS":
        anchors = tuple(_load_reachability_anchor(n) for n in _REACHABILITY_ANCHOR_SPECS)
        globals()[name] = anchors
        return anchors
    if name in _REACHABILITY_ANCHOR_SPECS:
        return _load_reachability_anchor(name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "ConfidenceBand",
    "fact_usage_band",
    "jd_briefing_cannot_create_facts_note",
    "load_master_candidate_fact_ledger",
    "load_master_role_family_taxonomy",
    "normalize_role_family_id",
    "validate_fact_shape",
]
