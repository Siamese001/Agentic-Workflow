"""
Failure Analyzer Tool
Purpose: Analyze frequency patterns in recurring failure keys to identify systemic issues.
Usage: Instantiate FailureAnalyzer with a list of failure keys and execute .analyze()
"""
import collections


class FailureAnalyzer:
    def __init__(self, keys):
        """Initialize with a list of failure event identifiers."""
        self.keys = keys

    def analyze(self):
        """Computes and prints the distribution and frequency of failure keys."""
        if not self.keys:
            print("No failure data provided for analysis.")
            return

        total_events = len(self.keys)
        counts = collections.Counter(self.keys)

        # Sort results by frequency in descending order
        sorted_patterns = counts.most_common()

        print("--- Failure Pattern Analysis Report ---")
        print(f"Total Events Scanned: {total_events}")
        print(f"{'Failure Key':<15} | {'Occurrences':<12} | {'Distribution %':<15}")
        print("-" * 50)

        for key, count in sorted_patterns:
            percentage = (count / total_events) * 100
            print(f"{str(key):<15} | {count:<12} | {percentage:>14.2f}%")
        print("-" * 50)

if __name__ == "__main__":
    # Context-specific keys for diagnostic evaluation
    context_keys = [50, 19, 7, 8, 22, 2, 3, 4, 5, 60]

    analyzer = FailureAnalyzer(context_keys)
    analyzer.analyze()
