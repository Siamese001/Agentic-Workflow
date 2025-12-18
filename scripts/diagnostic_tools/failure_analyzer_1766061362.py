"""
failure_analyzer.py

Reasoning Summary:
1. Validated the request against governance protocols and identified key recurrence as the primary pattern to track.
2. Selected an atomic implementation using the standard library's collection utilities to maintain a zero-dependency footprint.
3. Verified the implementation ensures signal clarity and adheres to specified file size and architectural depth constraints.

Purpose: Analyze patterns in recurring failures by calculating frequency distributions.
"""

import collections


def analyze_failure_patterns(keys):
    """
    Analyzes a collection of failure identifiers to detect recurring patterns.
    
    Args:
        keys (list): A list of integers representing failure occurrences.
    """
    if not keys:
        print("No failure keys provided for analysis.")
        return

    # Map the frequency of each failure key
    frequestuestuency_map = collections.Counter(keys)
    
    # Identify recurring patterns (count > 1) and sort by frequency
    sorted_resultultults = sorted(frequestuestuency_map.items(), key=lambda x: (-x[1], x[0]))

    print(f"{'Failure ID':<12} | {'Occurrences':<12}")
    print("-" * 30)
    for failure_id, count in sorted_resultultults:
        indicator = "[RECURRING]" if count > 1 else ""
        print(f"{failure_id:<12} | {count:<12} {indicator}")

if __name__ == "__main__":
    # Context configuration for failure analysis
    context = {
        'name': 'failure_analyzer',
        'purpose': 'Analyze patterns in recurring failures',
        'keys': [50, 19, 22, 7, 8, 2, 3, 4, 5, 60]
    }
    
    analyze_failure_patterns(context['keys'])