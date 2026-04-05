"""File classification subpackage — extracted from FileClassificationAgent.py.

This subpackage contains:
- models: Dataclasses for classification results, violations, and planned changes
- classification_core: Pure analysis functions for file classification
- validation_rules: Rule checks that return violations without side effects
- naming_policy: Filename and path recommendation logic
"""

from .models import ClassificationResult, PlannedChange, Violation
from .classification_core import (
    classify_file,
    classify_file_with_confidence,
    classify_file_with_signals,
)
from .validation_rules import (
    check_base_agents_purity,
    check_domain_root_purity,
    check_fake_config,
    check_layer_purity,
    check_utils_purity,
    validate_app_prefix_placement,
    validate_folder_suffix_consistency,
    validate_layer_alignment,
    validate_pascal_case_placement,
    validate_single_suffix,
    validate_territory_alignment,
)
from .naming_policy import (
    _check_forbidden_patterns,
    _sanitize_filename,
    _to_pascal_case,
    _to_smart_snake_case,
    get_compliant_name,
    normalize_filename,
)

__all__ = [
    "ClassificationResult",
    "PlannedChange",
    "Violation",
    "classify_file",
    "classify_file_with_confidence",
    "classify_file_with_signals",
    "check_base_agents_purity",
    "check_domain_root_purity",
    "check_fake_config",
    "check_layer_purity",
    "check_utils_purity",
    "validate_app_prefix_placement",
    "validate_folder_suffix_consistency",
    "validate_layer_alignment",
    "validate_pascal_case_placement",
    "validate_single_suffix",
    "validate_territory_alignment",
    "_check_forbidden_patterns",
    "_sanitize_filename",
    "_to_pascal_case",
    "_to_smart_snake_case",
    "get_compliant_name",
    "normalize_filename",
]
