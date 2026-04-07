"""Reporting subpackage for ADG generation."""

from tools.generate.reporting.analysis import (
    _artifact_determinism_probe,
    _audit_semantic_surfaces,
    _cleanup_validation_files,
    _semantic_precision_stats,
    _violation_propagation_stats,
    _violation_surface_stats,
)
from tools.generate.reporting.reports import (
    _generate_standardized_reports,
    _print_defect_table,
)

__all__ = [
    "_audit_semantic_surfaces",
    "_semantic_precision_stats",
    "_violation_surface_stats",
    "_violation_propagation_stats",
    "_artifact_determinism_probe",
    "_cleanup_validation_files",
    "_print_defect_table",
    "_generate_standardized_reports",
]
