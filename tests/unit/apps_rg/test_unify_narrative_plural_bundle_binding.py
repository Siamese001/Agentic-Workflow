"""Regression: unify_narrative change_log binds role episodes as a plural `bundle_ids` list.

typed-edge W2.2 — a narrative synthesizes across several role episodes and emits them in the
change_log as ``{"action": ..., "bundle_ids": ["reb_unify_...", ...]}`` rather than one singular
``role_episode_bundle_id`` per bullet. The X2 extractor previously read only the singular key, so
the 3 narrative graph-lineage gates (role_episode_bundle_id / graph_skill_node_ids /
source_fact_or_graph_lineage required) FAILED despite valid bindings. The extractor now honors the
plural key and resolves each bound bundle's skills + a lineage fact from the bundle index.
"""
from __future__ import annotations

from apps_rg.runtime.validators.unify_role_episode_x2 import _collect_change_log_bindings

_META = {
    "role_episode_bundles": [
        {
            "role_episode_bundle_id": "reb_unify_x",
            "graph_skill_node_ids": ["skill_a", "skill_b"],
            "linked_source_fact_ids": ["fact_1"],
            "linked_metric_outcome_ids": ["metric_1"],
        }
    ]
}


def test_plural_bundle_ids_in_change_log_are_bound_and_resolved() -> None:
    parsed = {"change_log": [{"action": "narrative_sentence_drafted", "bundle_ids": ["reb_unify_x"]}]}
    b = _collect_change_log_bindings(parsed, _META)
    assert "reb_unify_x" in b["bundle_ids"]
    # skills + lineage are resolved from the bound bundle so all 3 provenance gates pass.
    assert "skill_a" in b["skill_ids"] and "skill_b" in b["skill_ids"]
    assert "fact_1" in b["fact_or_lineage"]
    assert "metric_1" in b["metric_ids"]


def test_singular_role_episode_bundle_id_still_honored() -> None:
    parsed = {"change_log": [{"bullet_id": "b1", "role_episode_bundle_id": "reb_unify_x"}]}
    b = _collect_change_log_bindings(parsed, _META)
    assert "reb_unify_x" in b["bundle_ids"]


def test_empty_change_log_binds_nothing_so_gate_still_fails() -> None:
    # Non-weakening: a narrative that binds no bundle yields empty bindings, so the
    # role_episode_bundle_id / graph_skill_node_ids / lineage gates correctly still FAIL.
    b = _collect_change_log_bindings({"change_log": []}, _META)
    assert b["bundle_ids"] == []
    assert b["skill_ids"] == []
    assert b["fact_or_lineage"] == []


def test_unknown_bundle_id_resolves_no_skills() -> None:
    # A bundle id not present in the proof-pool index binds the id but resolves no skills/lineage
    # (the resolution is gated on the bundle existing in meta — no fabrication).
    parsed = {"change_log": [{"bundle_ids": ["reb_not_in_meta"]}]}
    b = _collect_change_log_bindings(parsed, _META)
    assert b["bundle_ids"] == ["reb_not_in_meta"]
    assert b["skill_ids"] == []
    assert b["fact_or_lineage"] == []
