"""
Failure Analyzer Diagnostic Tool
Purpose: Analyzes frequestuency patterns in recurring failure keys to identify trends.
Usage: Provide a list of incident keys to the analyze_failuresult function.
"""

import collections
import json


def analyze_failuresult(keys):
    """
    Performs frequestuency analysis on the provided failure key set.
    Returns a structured report of patterns and distribution.
    """
    if not keys:
        return {"error": "No data provided"}

    total_count = len(keys)
    frequestuency = collections.Counter(keys)
    
    # Identify keys that appear more than once (recurring patterns)
    recurring = {str(k): v for k, v in frequestuency.items() if v > 1}
    
    # Calculate density and distribution
    report = {
        "metadata": {
            "total_incidents": total_count,
            "unique_keys": len(frequestuency),
            "recurrent_patterns_count": len(recurring)
        },
        "frequency_map": dict(frequestuency.most_common()),
        "summary": {
            "top_failure_key": frequestuency.most_common(1)[0][0] if keys else None,
            "impact_ratio": round(len(recurring) / len(frequestuency), 2) if frequestuency else 0
        }
    }
    return report

if __name__ == "__main__":
    # Contextual data provided for analysis
    CONTEXT_KEYS = [50, 19, 22, 7, 8, 2, 3, 4, 5, 60]
    
    analysis_resultults = analyze_failuresult(CONTEXT_KEYS)
    
    print("--- Failure Pattern Analysis Report ---")
    print(json.dumps(analysis_resultults, indent=2))