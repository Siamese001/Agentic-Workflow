"""
Reasoning:
1. Recalled Laws of Subatomic Governance to maintain codebase integrity and isolation.
2. Identified failure patterns through statistical distribution and frequency analysis.
3. Developed an atomic diagnostic tool within prescribed file size and depth constraints.
4. Confirmed zero blast radius using standard library containment.
5. Verified the tool generates idempotent results to prevent signal duplication.
"""

import collections
import statistics

"""
Failure Analyzer Diagnostic Tool
Purpose: Analyze patterns in recurring failures by calculating frequency
and statistical distribution of failure keys.
Usage: Run script directly to analyze provided keys or import analyze_failures.
"""

def analyze_failures(keys):
    """
    Performs frequency analysis and identifies statistical outliers in keys.
    """
    if not keys:
        print("Error: No failure keys provided for analysis.")
        return

    # Frequency and Statistics Analysis
    counts = collections.Counter(keys)
    mean_val = statistics.mean(keys)
    median_val = statistics.median(keys)
    stdev_val = statistics.stdev(keys) if len(keys) > 1 else 0.0

    # Gap analysis for clustering detection
    sorted_keys = sorted(keys)
    gaps = [sorted_keys[i+1] - sorted_keys[i] for i in range(len(sorted_keys)-1)]
    avg_gap = statistics.mean(gaps) if gaps else 0

    # Output generation
    print(f"{' FAILURE METRICS ':*^40}")
    print(f"Total Events processed:   {len(keys)}")
    print(f"Unique Failure Signatures: {len(counts)}")
    print(f"Arithmetic Mean:           {mean_val:.2f}")
    print(f"Standard Deviation:        {stdev_val:.2f}")
    print(f"Median Key ID:             {median_val}")
    print(f"Average Signature Gap:     {avg_gap:.2f}")

    print(f"\n{' TOP RECURRING PATTERNS ':*^40}")
    for key, freq in counts.most_common(3):
        print(f"Key ID: {key: <15} | Frequency: {freq}")

    # Heuristic Signal Detection
    print(f"\n{' SIGNAL ANALYSIS ':*^40}")
    if stdev_val > mean_val:
        print("[ALERT] High variance: Failures are likely non-homogeneous.")
    elif len(counts) <= len(keys) * 0.5:
        print("[ALERT] High recurrence: Potential root cause bottleneck detected.")
    else:
        print("[INFO] Normal distribution: No immediate clustering detected.")

if __name__ == "__main__":
    # Context data from ToolsmithAgent
    FAILURE_DATA = [50, 19, 7, 8, 22, 2, 3, 4, 5, 60]
    analyze_failures(FAILURE_DATA)
