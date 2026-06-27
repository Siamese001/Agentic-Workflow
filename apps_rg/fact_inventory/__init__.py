"""Candidate fact ledger loading and selection policy helpers (ingress-only utilities)."""

from .candidate_fact_ledger import (
    ConfidenceBand,
    fact_usage_band,
    jd_briefing_cannot_create_facts_note,
    load_master_candidate_fact_ledger,
    load_master_role_family_taxonomy,
    normalize_role_family_id,
    validate_fact_shape,
)

# Reachability anchors for the hardening and validation modules that must stay on the live ADG path.
from .apply_c03_graph_full_zero_loss_overwrite import (
    apply_overwrite as _apply_c03_graph_full_zero_loss_overwrite,
)
from .apply_c03_graph_skill_granularity_hardening import (
    apply_hardening as _apply_c03_graph_skill_granularity_hardening,
)
from .apply_graphdb_capability_sqlite_hardening import (
    apply_graphdb_capability_sqlite_hardening as _apply_graphdb_capability_sqlite_hardening,
)
from .c03_graph_skill_hardening import (
    harden_augmented_skills_graph_payload as _harden_augmented_skills_graph_payload,
)
from .graph_metric_heterogeneity_policy import (
    validate_metric_heterogeneity as _validate_metric_heterogeneity,
)
from .graph_sqlite_path_index import (
    materialize_graphdb_capability_indexes as _materialize_graphdb_capability_indexes,
)
from .validate_c03_graph_hardening import (
    validate_c03_graph_hardening_payload as _validate_c03_graph_hardening_payload,
)
from .validate_c03_graph_skill_granularity import (
    validate_graph as _validate_c03_graph_skill_granularity,
)
from .validate_graph_sqlite_path_index import (
    validate_graph_sqlite_path_index as _validate_graph_sqlite_path_index,
)

_REACHABILITY_ANCHORS = (
    _apply_c03_graph_full_zero_loss_overwrite,
    _apply_c03_graph_skill_granularity_hardening,
    _apply_graphdb_capability_sqlite_hardening,
    _harden_augmented_skills_graph_payload,
    _materialize_graphdb_capability_indexes,
    _validate_c03_graph_hardening_payload,
    _validate_c03_graph_skill_granularity,
    _validate_graph_sqlite_path_index,
    _validate_metric_heterogeneity,
)

__all__ = [
    "ConfidenceBand",
    "fact_usage_band",
    "jd_briefing_cannot_create_facts_note",
    "load_master_candidate_fact_ledger",
    "load_master_role_family_taxonomy",
    "normalize_role_family_id",
    "validate_fact_shape",
]
