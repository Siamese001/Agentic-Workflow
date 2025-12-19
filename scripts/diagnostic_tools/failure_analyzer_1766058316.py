import collections
import json


class FailureAnalyzer:
    """
    Diagnostic tool to analyze patterns in recurring failures via frequency distribution.

    Usage:
        analyzer = FailureAnalyzer(failure_keys=[50, 19, 7, ...])
        report = analyzer.generate_report()
        print(report)
    """
    def __init__(self, failure_keys):
        self.keys = failure_keys
        self.stats = collections.Counter(self.keys)

    def calculate_distribution(self):
        """Calculates percentage of total for each failure key."""
        total = sum(self.stats.values())
        if total == 0:
            return {}
        return {str(k): round((v / total) * 100, 2) for k, v in self.stats.items()}

    def find_anomalies(self, threshold_multiplier=1.5):
        """Identifies keys appearing significantly more often than the average frequency."""
        if not self.stats:
            return []
        avg_freq = sum(self.stats.values()) / len(self.stats)
        return [k for k, v in self.stats.items() if v > avg_freq * threshold_multiplier]

    def generate_report(self):
        """Generates a structured JSON report of failure patterns."""
        report = {
            "metadata": {
                "total_samples": len(self.keys),
                "unique_keys": len(self.stats)
            },
            "top_recurring_failures": self.stats.most_common(5),
            "frequency_distribution_pct": self.calculate_distribution(),
            "detected_anomalies": self.find_anomalies()
        }
        return json.dumps(report, indent=4)

if __name__ == "__main__":
    # Contextual failure keys provided for analysis
    context_keys = [50, 19, 7, 8, 22, 2, 3, 4, 5, 60]

    # Example usage with simulated recurring patterns
    simulation_data = context_keys + [50, 50, 19, 50, 7, 50, 19]

    analyzer = FailureAnalyzer(simulation_data)
    print("FAILURE ANALYZER OUTPUT")
    print("=======================")
    print(analyzer.generate_report())
