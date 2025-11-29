#!/usr/bin/env python3
"""
Analyze semantic validation failures to identify improvement areas
"""

import json
from collections import Counter, defaultdict

def analyze_semantic_failures():
    """Load and analyze semantic validation failures"""
    results_path = r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11\scripts\windsurf_validation_keys_semantic_results.json"
    
    with open(results_path, 'r') as f:
        data = json.load(f)
    
    print("=== SEMANTIC VALIDATION FAILURE ANALYSIS ===")
    print(f"Total Keys: {data['summary']['total_keys']}")
    print(f"Passed: {data['summary']['passed']} ({data['summary']['pass_rate']:.1%})")
    print(f"Failed: {data['summary']['failed']}")
    print()
    
    # Analyze failure reasons by namespace
    namespace_failures = defaultdict(list)
    category_failures = defaultdict(list)
    
    for key, info in data['failed_keys'].items():
        reason = info['reason']
        
        # Extract namespace from key
        if '::' in key:
            rule_part = key.split('::')[0]
            parts = rule_part.split('.')
            if len(parts) >= 2:
                namespace = parts[0]
                category = parts[1] if len(parts) > 1 else "unknown"
                namespace_failures[namespace].append(reason)
                category_failures[f"{namespace}.{category}"].append(reason)
    
    # Top failure reasons
    failure_reasons = [info['reason'] for info in data['failed_keys'].values()]
    reason_counts = Counter(failure_reasons)
    print("=== TOP 10 FAILURE REASONS ===")
    for i, (reason, count) in enumerate(reason_counts.most_common(10), 1):
        print(f"{i:2d}. {count:4d}: {reason}")
    
    print()
    print("=== FAILURES BY NAMESPACE ===")
    for namespace, failures in namespace_failures.items():
        unique_reasons = set(failures)
        print(f"{namespace:15s}: {len(failures):4d} failures, {len(unique_reasons):2d} unique reasons")
        if len(unique_reasons) <= 3:
            for reason in unique_reasons:
                print(f"{'':17s}- {reason}")
    
    print()
    print("=== FAILURES BY CATEGORY ===")
    for category, failures in category_failures.items():
        unique_reasons = set(failures)
        print(f"{category:25s}: {len(failures):4d} failures, {len(unique_reasons):2d} unique reasons")
        if len(unique_reasons) <= 3:
            for reason in unique_reasons:
                print(f"{'':27s}- {reason}")
    
    print()
    print("=== SAMPLE FAILED KEYS ===")
    sample_keys = list(data['failed_keys'].keys())[:10]
    for key in sample_keys:
        reason = data['failed_keys'][key]['reason']
        print(f"{key:60s} -> {reason}")

if __name__ == "__main__":
    analyze_semantic_failures()
