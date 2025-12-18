"""
failure_analyzer.py

Purpose:
    Analyzes patterns in recurring failures by calculating frequency distribution
    and identifying hotspots within a given set of failure keys.

Reasoning Summary:
    1. Identified frequency distribution as the root cause pattern for recurring failures.
    2. Implemented an atomic analyzer to process discrete failure signals.
    3. Verified the script's dependency graph is empty (stdlib only) to ensure zero blast radius.
"""

import collections


def analyze_patterns(keys):
    """
    Analyzes the frequency of failure keys and returns a report.
    
    Args:
        keys (list): A list of integers or strings representing failure IDs.
    """
    if not keys:
        print("No failure data provided.")
        return

    # Count occurrences of each failure key
    counts = collections.Counter(keys)
    total = len(keys)
    
    # Sort by frequency descending
    sorted_patterns = counts.most_common()

    print(f"{'='*30}")
    print(f"FAILURE PATTERN ANALYSIS")
    print(f"{'='*30}")
    print(f"Total Samples: {total}")
    print(f"Unique Keys:   {len(counts)}")
    print(f"{'-'*30}")
    print(f"{'Key':<10} | {'Count':<7} | {'Frequency %'}")
    print(f"{'-'*30}")

    for key, count in sorted_patterns:
        percentage = (count / total) * 100
        print(f"{str(key):<10} | {count:<7} | {percentage:>10.2f}%")
    
    print(f"{'='*30}")

if __name__ == "__main__":
    # Context-provided failure keys
    context_keys = [50, 19, 7, 8, 22, 2, 3, 4, 5, 60]
    
    # Example execution
    analyze_patterns(context_keys)