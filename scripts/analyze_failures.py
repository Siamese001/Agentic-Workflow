#!/usr/bin/env python3
"""
Analyze validation failure patterns to identify root causes
"""

import json
from collections import Counter, defaultdict

def analyze_failures():
    """Load and analyze validation failures"""
    results_path = r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11\scripts\windsurf_validation_keys_results.json"
    
    with open(results_path, 'r') as f:
        data = json.load(f)
    
    print("=== VALIDATION FAILURE ANALYSIS ===")
    print(f"Total Keys: {data['summary']['total_keys']}")
    print(f"Passed: {data['summary']['passed']} ({data['summary']['pass_rate']:.1%})")
    print(f"Failed: {data['summary']['failed']}")
    print()
    
    # Analyze failure reasons
    failure_reasons = []
    category_failures = defaultdict(list)
    
    for key, info in data['failed_keys'].items():
        reason = info['reason']
        failure_reasons.append(reason)
        
        # Extract category from key
        parts = key.split('_', 2)
        if len(parts) >= 2:
            category = parts[0] + "_" + parts[1]
            category_failures[category].append(reason)
    
    # Top failure reasons
    reason_counts = Counter(failure_reasons)
    print("=== TOP 10 FAILURE REASONS ===")
    for i, (reason, count) in enumerate(reason_counts.most_common(10), 1):
        print(f"{i:2d}. {count:4d}: {reason}")
    
    print()
    print("=== FAILURES BY CATEGORY ===")
    for category, failures in category_failures.items():
        unique_reasons = set(failures)
        print(f"{category:20s}: {len(failures):4d} failures, {len(unique_reasons):2d} unique reasons")
        if len(unique_reasons) <= 3:
            for reason in unique_reasons:
                print(f"                      - {reason}")
    
    print()
    print("=== SAMPLE FAILED KEYS ===")
    sample_keys = list(data['failed_keys'].keys())[:10]
    for key in sample_keys:
        reason = data['failed_keys'][key]['reason']
        print(f"{key:50s} -> {reason}")

if __name__ == "__main__":
    analyze_failures()
