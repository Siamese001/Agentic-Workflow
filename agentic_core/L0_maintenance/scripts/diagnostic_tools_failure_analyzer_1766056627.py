# 1. Three Laws of Subatomic Governance: Prioritized governance integrity, atomic locality, and signal-less diagnostics.
# 2. Root Cause Pattern: Identified the need for centralized frequency mapping to resolve sparse failure key distributions.
# 3. Atomic Fix: Implemented a discrete analyzer tool utilizing focused pattern recognition for high-frequency signal detection.
# 4. Blast Radius: Verified zero impact on existing dependency graphs; tool functions as a standalone diagnostic unit.
# 5. Signal Verification: Validated that execution flow is purely observational to prevent introduction of state-mutation signals.

"""
Failure Analyzer Diagnostic Tool
Purpose: Analyze patterns in recurring failures to identify root cause signals.
Usage: python failure_analyzer.py
"""

import collections
import json


def analyze_failure_patterns(keys):
    """
    Analyzes frequency of failure keys and returns statistical summary.

    Args:
        keys (list): List of failure identifiers provided in the context.
    Returns:
        dict: Analysis report including distribution and occurrence metadata.
    """
    if not keys:
        return {"status": "error", "message": "No data points available for analysis."}

    total_events = len(keys)
    counts = collections.Counter(keys)

    # Identify recurring patterns (keys appearing more than once)
    recurring = {k: v for k, v in counts.items() if v > 1}

    report = {
        "metadata": {
            "total_captured_events": total_events,
            "unique_signatures": len(counts),
            "reoccurrence_detected": len(recurring) > 0
        },
        "frequency_distribution": [
            {
                "key": k,
                "count": v,
                "weight": round(v / total_events, 4),
                "percentage": f"{(v / total_events):.1%}"
            }
            for k, v in counts.most_common()
        ]
    }
    return report

def main():
    # Context: Failure keys from diagnostic environment
    # Note: These values represent the provided sample [50, 19, 7, 8, 22, 2, 3, 4, 5, 60]
    failure_keys = [50, 19, 7, 8, 22, 2, 3, 4, 5, 60]

    # Execute diagnostic analysis
    results = analyze_failure_patterns(failure_keys)

    # Output results in structured format
    print("--- SUBATOMIC GOVERNANCE: FAILURE PATTERN REPORT ---")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
