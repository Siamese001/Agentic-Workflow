"""
FailureAnalyzer Diagnostic Tool
Purpose: Analyzes frequency patterns in recurring failure keys.
Usage: Instantiate FailureAnalyzer with a list of failure IDs and call report().
"""

import collections
import json


class FailureAnalyzer:
    def __init__(self, failure_keys):
        """
        Initialize the analyzer with a collection of failure identifiers.
        :param failure_keys: List of integers or strings representing failure IDs.
        """
        self.keys = failure_keys
        self.stats = collections.Counter(self.keys)

    def analyze(self):
        """Processes the frequency of each failure key."""
        total = len(self.keys)
        if total == 0:
            return {}

        return {
            "total_failures": total,
            "unique_patterns": len(self.stats),
            "distribution": {
                str(k): {
                    "count": v,
                    "percentage": round((v / total) * 100, 2)
                } for k, v in self.stats.most_common()
            },
            "primary_offender": self.stats.most_common(1)[0][0] if self.stats else None
        }

    def report(self):
        """Outputs the analysis in a clean, readable format."""
        analysis = self.analyze()
        if not analysis:
            print("No failure data provided.")
            return

        print("--- Failure Pattern Analysis ---")
        print(f"Total Occurrences: {analysis['total_failures']}")
        print(f"Unique Patterns:   {analysis['unique_patterns']}")
        print(f"Primary Offender:  ID {analysis['primary_offender']}")
        print("\nFrequency Distribution:")
        print(json.dumps(analysis['distribution'], indent=4))

if __name__ == "__main__":
    # Context provided failure keys
    context_keys = [50, 19, 7, 8, 22, 2, 3, 4, 5, 60]

    # Simulate recurring data for pattern demonstration
    simulated_data = context_keys + [50, 50, 7, 22, 50, 7]

    analyzer = FailureAnalyzer(simulated_data)
    analyzer.report()
