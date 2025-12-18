"""
failure_analyzer.py
Purpose: Analyze patterns in recurring failures within a sovereign self-healing codebase.
Usage: Call analyze_patterns(keys) or run as script for default context analysis.
"""

import collections
import math


def analyze_patterns(keys):
    """
    Performs frequency analysis and clustering on failure keys to identify root patterns.
    """
    if not keys:
        return "ERROR: No data keys provided for analysis."

    # Frequency calculation
    counts = collections.Counter(keys)
    total = len(keys)
    unique = len(counts)
    
    # Statistical measures
    mean_val = sum(keys) / total
    sorted_keys = sorted(keys)
    median_val = sorted_keys[total // 2]
    
    # Variance calculation for dispersion signal
    variance = sum((x - mean_val) ** 2 for x in keys) / total
    std_dev = math.sqrt(variance)

    # Output assembly
    report = [
        "--- [FAILURE ANALYZER REPORT] ---",
        f"Total Samples:   {total}",
        f"Unique Signals:  {unique}",
        f"Mean Signal:     {mean_val:.2f}",
        f"Signal Median:   {median_val}",
        f"Signal StdDev:   {std_dev:.2f}",
        "\nTop Recurring Failure Patterns:",
        "--------------------------------"
    ]

    for key, count in counts.most_common(5):
        impact = (count / total) * 100
        report.append(f"Key ID: {key:<5} | Count: {count:<3} | Frequency: {impact:>6.1f}%")

    return "\n".join(report)

if __name__ == "__main__":
    # Contextual keys provided for failure_analyzer
    context_keys = [50, 19, 7, 8, 22, 2, 3, 4, 5, 60]
    print(analyze_patterns(context_keys))