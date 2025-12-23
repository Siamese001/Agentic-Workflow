"""
failure_analyzer.py: A diagnostic tool for identifying recurring patterns in failure IDs.
This tool analyzes frequency and distribution of failure keys using the standard library.
Usage: Instantiate FailureAnalyzer with a list of keys and call .report().
"""

import collections


class FailureAnalyzer:
    """Analyzes a sequence of failure keys to detect statistical patterns."""

    def __init__(self, keys):
        """Initialize with a list of failure event identifiers."""
        self.keys = keys

    def analyze(self):
        """Calculates frequency distributions and impact metrics."""
        if not self.keys:
            return None

        total_count = len(self.keys)
        counts = collections.Counter(self.keys)

        # Sort patterns by frequency (descending)
        patterns = sorted(counts.items(), key=lambda x: x[1], reverse=True)

        return {
            "metrics": {
                "total_events": total_count,
                "unique_signatures": len(counts),
            },
            "patterns": patterns
        }

    def report(self):
        """Outputs a formatted diagnostic summary to the console."""
        results = self.analyze()
        if not results:
            print("No data available for analysis.")
            return

        metrics = results["metrics"]
        print(f"{'='*35}")
        print(f"FAILURE PATTERN DIAGNOSTIC")
        print(f"{'='*35}")
        print(f"Total Events:      {metrics['total_events']}")
        print(f"Unique Signatures: {metrics['unique_signatures']}")
        print(f"\nTop Recurring Signatures:")
        print(f"{'-'*35}")
        print(f"{'Key':<10} | {'Count':<8} | {'Impact':<8}")

        for key, count in results["patterns"]:
            impact = (count / metrics['total_events']) * 100
            print(f"{str(key):<10} | {count:<8} | {impact:>6.1f}%")
        print(f"{'='*35}")

if __name__ == "__main__":
    # Contextual keys provided for analysis
    context_keys = [50, 19, 7, 8, 22, 2, 3, 4, 5, 60]

    # Simulated historical stream for pattern detection
    historical_stream = context_keys + [50, 50, 22, 8, 50, 19, 50, 22, 7]

    analyzer = FailureAnalyzer(historical_stream)
    analyzer.report()
