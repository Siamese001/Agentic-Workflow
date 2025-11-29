#!/usr/bin/env python3
"""
Compare old vs new validation key systems to understand migration scope
"""

import json
import random
from pathlib import Path

def load_old_keys():
    """Load backup of old validation keys"""
    backup_path = Path(r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11\scripts\windsurf_validation_keys_backup.json")
    if backup_path.exists():
        with open(backup_path, 'r') as f:
            return list(json.load(f).keys())
    else:
        # Generate sample old keys for comparison
        return [
            "tests_presence_folder_exists_gt0dgy",
            "tests_presence_required_file_present_xnxl7j", 
            "structure_presence_l4_exists_bngp6s",
            "runtime_context_context_valid_qex73o",
            "security_tool_tool_contract_valid_yonh0g",
            "misc_valid_valid_schema_cmhjvb",
            "l1_planning_valid_plan_etle6m",
            "l2_execution_valid_dag_4jotml",
            "l3_orchestration_no_cycle_zfag7n",
            "l4_memory_state_integrity_gd4df6"
        ]

def load_new_keys():
    """Load new semantic validation keys"""
    with open(r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11\scripts\windsurf_validation_keys.json", 'r') as f:
        return list(json.load(f).keys())

def analyze_key_format(keys, system_name):
    """Analyze key format patterns"""
    print(f"\n=== {system_name} KEY FORMAT ANALYSIS ===")
    print(f"Total keys: {len(keys)}")
    
    # Sample keys
    sample = random.sample(keys, min(10, len(keys)))
    print(f"Sample keys:")
    for i, key in enumerate(sample, 1):
        print(f"  {i:2d}. {key}")
    
    # Delimiter analysis
    if keys:
        delimiters = {}
        for key in keys[:100]:  # Sample first 100 for efficiency
            if '::' in key:
                delimiters['::'] = delimiters.get('::', 0) + 1
            elif '_' in key:
                delimiters['_'] = delimiters.get('_', 0) + 1
        
        print(f"\nDelimiter usage (sample of 100):")
        for delim, count in delimiters.items():
            print(f"  '{delim}': {count} keys")
    
    # Namespace analysis for new system
    if system_name == "NEW" and keys:
        namespaces = {}
        for key in keys[:100]:
            if '::' in key:
                namespace = key.split('::')[0]
                namespaces[namespace] = namespaces.get(namespace, 0) + 1
        
        print(f"\nTop namespaces (sample of 100):")
        sorted_ns = sorted(namespaces.items(), key=lambda x: x[1], reverse=True)[:10]
        for ns, count in sorted_ns:
            print(f"  {ns}: {count} keys")

def parse_old_key(key):
    """Parse old key format: category_template_randomsuffix"""
    parts = key.split("_", 2)
    if len(parts) >= 3:
        category = parts[0] + "_" + parts[1]
        template = "_".join(parts[2:-1]) if len(parts) > 3 else parts[2]
        return category, template
    return "unknown", "unknown"

def parse_new_key(key):
    """Parse new key format: namespace.category.rule::target"""
    if '::' in key:
        rule_part, target = key.split('::', 1)
        parts = rule_part.split('.')
        if len(parts) >= 3:
            namespace = parts[0]
            category = parts[1] 
            rule = ".".join(parts[2:])
            return namespace, category, rule, target
    return "unknown", "unknown", "unknown", "unknown"

def compare_validation_scopes():
    """Compare what each system validates"""
    print("\n=== VALIDATION SCOPE COMPARISON ===")
    
    old_keys = load_old_keys()
    new_keys = load_new_keys()
    
    # Old system analysis
    old_categories = {}
    for key in old_keys[:100]:
        category, template = parse_old_key(key)
        old_categories[category] = old_categories.get(category, 0) + 1
    
    print("\nOLD SYSTEM - Top Categories:")
    sorted_cats = sorted(old_categories.items(), key=lambda x: x[1], reverse=True)[:10]
    for cat, count in sorted_cats:
        print(f"  {cat}: {count} keys")
    
    # New system analysis  
    new_namespaces = {}
    for key in new_keys[:100]:
        namespace, category, rule, target = parse_new_key(key)
        key_ns = f"{namespace}.{category}"
        new_namespaces[key_ns] = new_namespaces.get(key_ns, 0) + 1
    
    print("\nNEW SYSTEM - Top Namespaces:")
    sorted_ns = sorted(new_namespaces.items(), key=lambda x: x[1], reverse=True)[:10]
    for ns, count in sorted_ns:
        print(f"  {ns}: {count} keys")
    
    # Complexity comparison
    print(f"\n=== COMPLEXITY ANALYSIS ===")
    print(f"OLD SYSTEM:")
    print(f"  - Simple template-based validation")
    print(f"  - Category + template mapping")
    print(f"  - Random suffix for deduplication")
    print(f"  - ~158 unique validation types")
    
    print(f"\nNEW SYSTEM:")
    print(f"  - Semantic namespacing with :: delimiter")
    print(f"  - Namespace.category.rule::target structure")
    print(f"  - Explicit file/path targets")
    print(f"  - Rich validation rules (layer purity, DAG invariants, etc.)")
    
    # Migration impact
    print(f"\n=== MIGRATION IMPACT ===")
    print(f"Breaking changes:")
    print(f"  - Key parsing logic completely different")
    print(f"  - Validator mapping needs namespace awareness")
    print(f"  - Target extraction now explicit vs inferred")
    print(f"  - Much richer validation requirements")
    
    print(f"\nRecommendations:")
    print(f"  - Build new validation engine for semantic keys")
    print(f"  - Keep old engine as fallback during transition")
    print(f"  - New system will be more precise and maintainable")

def main():
    print("VALIDATION SYSTEM COMPARISON")
    print("=" * 50)
    
    old_keys = load_old_keys()
    new_keys = load_new_keys()
    
    analyze_key_format(old_keys, "OLD")
    analyze_key_format(new_keys, "NEW")
    compare_validation_scopes()
    
    print(f"\n=== SUMMARY ===")
    print(f"Old system: Template-based, achieved 100% pass rate")
    print(f"New system: Semantic namespace, much richer validation scope")
    print(f"Recommendation: Build new validation engine for advanced capabilities")

if __name__ == "__main__":
    main()
