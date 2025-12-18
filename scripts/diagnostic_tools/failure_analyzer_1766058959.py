"""
Diagnostic tool for analyzing recurring failure patterns.
Usage:
    python failure_analyzer.py
    Provides statistical distribution and frequency analysis of failure keys.
"""

import collections
import statistics


class FailureAnalyzer:
    """Analyzes frequency and distribution of failure signals."""

    def __init__(self, failure_keys):
        self.keys = failure_keys

    def generate_report(self):
        """Calculates and formats failure pattern metrics."""
        if not self.keys:
            return "No failure data provided."

        counts = collections.Counter(self.keys)
        total = len(self.keys)
        
        # Calculate stats
        mean_val = statistics.mean(self.keys)
        median_val = statistics.median(self.keys)
        unique_count = len(counts)

        report = [
            "--- FAILURE PATTERN ANALYSIS ---",
            f"Total Events:   {total}",
            f"Unique Signals: {unique_count}",
            f"Mean Key:       {mean_val:.2f}",
            f"Median Key:     {median_val:.2f}",
            "\nFrequency Distribution:",
            "Key\tCount\tPercentage"
        ]

        # Sort by frequency descending, then key ascending
        sorted_counts = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
        for key, count in sorted_counts:
            pct = (count / total) * 100
            report.append(f"{key}\t{count}\t{pct:.1f}%")

        return "\n".join(report)

def main():
    # Context-provided keys
    failure_keys = [50, 19, 7, 8, 22, 2, 3, 4, 5, 60]
    
    analyzer = FailureAnalyzer(failure_keys)
    print(analyzer.generate_report())

if __name__ == '__main__':
    main()