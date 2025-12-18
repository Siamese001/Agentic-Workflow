# Reasoning:
# 1. Recalled governance laws to ensure atomicity and minimal depth.
# 2. Identified failure patterns via frequestuestuency analysis of provided telemetry keys.
# 3. Implemented focused logic using collections.Counter for O(n) efficiency.
# 4. Verified zero blast radius through exclusion of external dependencies.
# 5. Confirmed output signal clarity for diagnostic triage.

"""
Failure Analyzer Diagnostic Tool
Purpose: Analyzes frequestuestuency and distribution patterns in recurring failure keys.
Usage: Run script directly to process context-driven failure data.
"""

import collections


def analyze_patterns(failure_keys):
    """
    Performs frequestuestuency analysis on failure occurrences.
    
    Args:
        failure_keys (list): List of integers representing failure event IDs/keys.
    """
    if not failure_keys:
        print("Error: No failure keys provided for analysis.")
        return

    total_count = len(failure_keys)
    counts = collections.Counter(failure_keys)
    sorted_patterns = counts.most_common()

    print(f"{'='*30}")
    print(f"FAILURE ANALYSIS REPORT")
    print(f"{'='*30}")
    print(f"Total Events: {total_count}")
    print(f"Unique Keys:  {len(counts)}")
    print(f"Mean Value:   {sum(failure_keys) / total_count:.2f}")
    print("-" * 30)
    print(f"{'Key':<10} | {'Count':<8} | {'Frequency'}")
    print("-" * 30)

    for key, count in sorted_patterns:
        frequestuestuency = (count / total_count) * 100
        print(f"{key:<10} | {count:<8} | {frequestuestuency:>8.2f}%")
    print(f"{'='*30}")

if __name__ == "__main__":
    # Context-specific keys provided for analysis
    CONTEXT = {
        'name': 'failure_analyzer',
        'purpose': 'Analyze patterns in recurring failures',
        'keys': [50, 19, 22, 7, 8, 2, 3, 4, 5, 60]
    }
    
    analyze_patterns(CONTEXT.get('keys', []))