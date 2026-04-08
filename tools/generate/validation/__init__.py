"""Validation gates for ADG generation: artifact integrity, P0/P1/P2/SC/AP checks."""

from tools.generate.validation.gates import (
    CLASS_AGENTIC,
    CLASS_HYGIENE,
    CLASS_STRUCTURAL,
    VALID_VIOLATION_CLASSES,
    _check_agentic_antipatterns,
    _check_dead_production_imports,
    _check_p0_violations,
    _check_p1_ratchet,
    _check_p2_ratchet,
    _check_structural_conformance,
    _insert_sc_ap_violation,
    _load_sc_ap_config,
    _save_sc_ap_config,
)
from tools.generate.validation.integrity import (
    _check_artifact_consistency,
    _check_artifact_validity,
    _check_sqlite_integrity,
)

__all__ = [
    "_check_artifact_validity",
    "_check_sqlite_integrity",
    "_check_artifact_consistency",
    "_check_p0_violations",
    "_check_p1_ratchet",
    "_check_p2_ratchet",
    "_check_dead_production_imports",
    "_check_structural_conformance",
    "_check_agentic_antipatterns",
    "_load_sc_ap_config",
    "_save_sc_ap_config",
    "_insert_sc_ap_violation",
    "CLASS_HYGIENE",
    "CLASS_STRUCTURAL",
    "CLASS_AGENTIC",
    "VALID_VIOLATION_CLASSES",
]
