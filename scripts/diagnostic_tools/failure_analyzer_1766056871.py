"""
Failure Analyzer Tool
Purpose: Analyzes recurring failure patterns from a list of identifiers.
Usage: Run directly to see sample analysis or import into a service.
"""

import collections


def analyze_patterns(keys):
    """
    Identifies recurring failure keys and calculates frequency distributions.

    Args:
        keys (list): List of integers representing failure occurrences.

    Returns:
        dict: Analysis results containing total, unique, and recurring patterns.
    """
    if not keys:
        return {"error": "Empty dataset"}

    count_map = collections.Counter(keys)
    recurring = {k: v for k, v in count_map.items() if v > 1}

    # Sort by frequency descending
    sorted_patterns = sorted(recurring.items(), key=lambda x: x[1], reverse=True)

    analysis = {
        "summary": {
            "total_failures": len(keys),
            "unique_signatures": len(count_map),
            "recurring_count": len(recurring)
        },
        "top_recurring": sorted_patterns[:5],
        "distribution": {
            "mean_recurrence": sum(count_map.values()) / len(count_map)
        }
    }
    return analysis

def display_results(results):
    """Formatted output for console feedback."""
    print("--- Failure Pattern Analysis ---")
    if "error" in results:
        print(f"Error: {results['error']}")
        return

    s = results["summary"]
    print(f"Total Events: {s['total_failures']}")
    print(f"Unique Sigs:  {s['unique_signatures']}")
    print(f"Recurrences:  {s['recurring_count']}")

    print("\nTop Patterns (ID: Count):")
    for key, freq in results["top_recurring"]:
        print(f" - {key}: {freq}")

if __name__ == "__main__":
    # Contextual data provided
    failure_keys = [50, 19, 7, 8, 22, 2, 3, 4, 5, 60]

    # Adding synthetic recurrences for demonstration
    sample_data = failure_keys + [50, 19, 50, 7]

    report = analyze_patterns(sample_data)
    display_results(report)
