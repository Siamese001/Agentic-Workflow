#!/usr/bin/env python3
"""
Analyze the final 8 semantic validation failures
"""

import json

def analyze_final_failures():
    """Load and analyze the final failures"""
    results_path = r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11\scripts\windsurf_validation_keys_semantic_results.json"
    
    with open(results_path, 'r') as f:
        data = json.load(f)
    
    print("=== FINAL 8 FAILURES ANALYSIS ===")
    print(f"Total Keys: {data['summary']['total_keys']}")
    print(f"Passed: {data['summary']['passed']} ({data['summary']['pass_rate']:.1%})")
    print(f"Failed: {data['summary']['failed']}")
    print()
    
    print("FAILURES:")
    for i, (key, info) in enumerate(data['failed_keys'].items(), 1):
        print(f"{i:2d}. {key:70s} -> {info['reason']}")
    
    print()
    print("FAILURE PATTERNS:")
    reasons = [info['reason'] for info in data['failed_keys'].values()]
    from collections import Counter
    reason_counts = Counter(reasons)
    
    for reason, count in reason_counts.items():
        print(f"  {count}x: {reason}")

if __name__ == "__main__":
    analyze_final_failures()
