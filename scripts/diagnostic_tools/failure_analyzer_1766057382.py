"""
FailureAnalyzer Diagnostic Tool
Purpose: Analyzes recurring failure patterns using frequency distribution and statistical thresholds.
Usage: Instantiate FailureAnalyzer with a list of failure keys and call analyze() to generate a report.
"""

import collections
import statistics


class FailureAnalyzer:
    def __init__(self, failure_keys):
        """
        Initialize with a sequence of failure identifiers (e.g., error codes or hash signatures).
        """
        self.keys = failure_keys
        self.stats = {}

    def analyze(self):
        """
        Performs frequency analysis and identifies anomalies based on standard deviation.
        """
        if not self.keys:
            return "No data provided for analysis."

        counts = collections.Counter(self.keys)
        total = sum(counts.values())
        freq_list = list(counts.values())
        
        mean_freq = statistics.mean(freq_list)
        std_dev = statistics.stdev(freq_list) if len(freq_list) > 1 else 0

        report = [
            f"{'FAILURE_ID':<15} | {'COUNT':<10} | {'PERCENTAGE':<10} | {'SIGNAL'}",
            "-" * 60
        ]

        for key, count in counts.most_common():
            percentage = (count / total) * 100
            # Identify high-intensity signals (recurring failures > 1 std dev from mean)
            signal = "CRITICAL" if count > (mean_freq + std_dev) else "STABLE"
            report.append(f"{str(key):<15} | {count:<10} | {percentage:>9.2f}% | {signal}")

        summary = (
            f"\nTotal Events: {total}\n"
            f"Unique Patterns: {len(counts)}\n"
            f"Avg Frequency: {mean_freq:.2f}"
        )
        
        return "\n".join(report) + "\n" + summary

def run_diagnostic():
    # Contextual data injection
    context_keys = [50, 19, 7, 8, 22, 2, 3, 4, 5, 60]
    # Simulated expansion for pattern recognition
    sample_data = context_keys + [50, 50, 19, 7, 50, 22, 19]
    
    analyzer = FailureAnalyzer(sample_data)
    print("--- Failure Pattern Analysis Report ---")
    print(analyzer.analyze())

if __name__ == "__main__":
    run_diagnostic()