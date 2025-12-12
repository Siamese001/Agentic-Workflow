#!/usr/bin/env python3
"""Analyze violations to identify patterns and prioritize fixes."""

from pathlib import Path
from collections import defaultdict

# Key 29 violations (39 total)
key29_violations = [
    ("apps_rg/L1_cognition/P2_inspect/rg_validation_gates.py", 77, "_register_default_gates", 154),
    ("schemas/pipeline/synthesis/use_schema_invoke/invoke_schema_pipeline_service.py", 144, "call_api", 115),
    ("schemas/pipeline/data_access/get_schema_request/manage_schema_context.py", 448, "create_workflow_context", 145),
    ("schemas/logic/synthesis/use_schema_invoke/invoke_schema_logic_service.py", 144, "call_api", 115),
    ("schemas/logic/data_access/convert/convert_to_internal_schema.py", 83, "convert_to_internal", 126),
    ("schemas/logic/data_access/get_schema_request/load_schema_context.py", 450, "create_workflow_context", 148),
    ("schemas/logic/data_access/get_schema_request/retrieve_schema_context.py", 450, "create_workflow_context", 145),
    ("schemas/logic/data_access/get_schema_utility/format_schema_context.py", 448, "create_workflow_context", 145),
    ("schemas/cache/data_access/get_schema_embedding/find_schema_context.py", 448, "create_workflow_context", 145),
]

# Key 30 violations (25 total)
key30_violations = [
    ("schemas/logic/data_access/convert/convert_to_internal_schema.py", 83, "convert_to_internal", 7),
    ("schemas/logic/data_access/get_schema_embedding/retrieve_schema_similarity.py", 245, "_extract_fields_with_types", 7),
    ("observability/runtime/synthesis/use_tools/perform_observability_operation.py", 345, "_aggregate_by_method", 7),
    ("apps_lic/L1_cognition/profile_planner.py", 353, "_infer_archetype", 6),
    ("apps_lic/planning/profile_planner.py", 353, "_infer_archetype", 6),
    ("apps_lic/L1_cognition/P2_inspect/lic_validator_rules.py", 284, "calculate_signal_score", 6),
    ("config/policy/l5___init__.py", 63, "arbitrate_safety", 6),
]

def analyze_patterns():
    """Analyze violation patterns."""
    print("="*70)
    print("VIOLATION PATTERN ANALYSIS")
    print("="*70)
    
    # Group by directory pattern
    key29_by_dir = defaultdict(list)
    for file, line, func, lines in key29_violations:
        dir_pattern = "/".join(Path(file).parts[:2])
        key29_by_dir[dir_pattern].append((file, func, lines))
    
    print("\n[KEY 29] Function Length by Directory:")
    for dir_pattern, violations in sorted(key29_by_dir.items()):
        print(f"\n  {dir_pattern}/ ({len(violations)} violations):")
        for file, func, lines in violations[:3]:
            print(f"    - {func} ({lines} lines)")
        if len(violations) > 3:
            print(f"    ... and {len(violations) - 3} more")
    
    # Group by function name pattern
    func_patterns = defaultdict(int)
    for file, line, func, lines in key29_violations:
        if "create_workflow_context" in func:
            func_patterns["create_workflow_context"] += 1
        elif "call_api" in func:
            func_patterns["call_api"] += 1
        else:
            func_patterns[func] += 1
    
    print("\n[KEY 29] By Function Pattern:")
    for pattern, count in sorted(func_patterns.items(), key=lambda x: -x[1]):
        print(f"  {pattern}: {count} instances")
    
    # Depth 7 violations (most severe)
    print("\n[KEY 30] Depth 7 Violations (CRITICAL):")
    depth7 = [v for v in key30_violations if v[3] == 7]
    for file, line, func, depth in depth7:
        print(f"  - {file}:{line} – {func}")
    
    # Depth 6 violations
    print(f"\n[KEY 30] Depth 6 Violations: {len([v for v in key30_violations if v[3] == 6])} functions")
    
    print("\n" + "="*70)
    print("RECOMMENDATION:")
    print("="*70)
    print("1. Fix depth 7 violations first (3 functions) - most critical")
    print("2. Fix unique large functions (_register_default_gates, convert_to_internal)")
    print("3. Create template fix for create_workflow_context pattern (13+ instances)")
    print("4. Create template fix for call_api pattern (8+ instances)")
    print("5. Fix remaining depth 6 violations")
    print("="*70)

if __name__ == "__main__":
    analyze_patterns()
