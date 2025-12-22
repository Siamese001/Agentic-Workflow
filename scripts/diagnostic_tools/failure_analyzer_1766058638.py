"""
FailureAnalyzer Diagnostic Tool
Usage:
    analyzer = FailureAnalyzer(failure_keys=[50, 19, 7, 8, 22, 2, 3, 4, 5, 60])
    analyzer.report()

Reasoning Summary:
The agent identifies failure patterns by calculating frequency distribution and clustering anomalies.
A minimal standalone utility is constructed to provide diagnostic visibility while maintaining
zero external dependencies and a low architectural blast radius.
"""

import collections
import statistics


class FailureAnalyzer:
    """Analyzes recurring failure keys to identify patterns and clusters."""

    def __init__(self, failure_keys):
        self.keys = sorted(failure_keys)
        self.count = len(self.keys)

    def get_stats(self):
        """Calculate basic statistical indicators for the failure set."""
        if not self.keys:
            return {}

        return {
            "total_occurrences": self.count,
            "min_id": self.keys[0],
            "max_id": self.keys[-1],
            "mean_id": statistics.mean(self.keys),
            "median_id": statistics.median(self.keys),
            "unique_count": len(set(self.keys))
        }

    def identify_clusters(self, threshold=5):
        """Identify groups of failures that occur within a specific proximity."""
        clusters = []
        if not self.keys:
            return clusters

        current_cluster = [self.keys[0]]
        for i in range(1, self.count):
            if self.keys[i] - self.keys[i-1] <= threshold:
                current_cluster.append(self.keys[i])
            else:
                if len(current_cluster) > 1:
                    clusters.append(current_cluster)
                current_cluster = [self.keys[i]]

        if len(current_cluster) > 1:
            clusters.append(current_cluster)
        return clusters

    def report(self):
        """Print a formatted diagnostic report to the console."""
        stats = self.get_stats()
        clusters = self.identify_clusters()

        print("-" * 30)
        print("FAILURE PATTERN DIAGNOSTIC")
        print("-" * 30)
        for key, value in stats.items():
            print(f"{key.replace('_', ' ').title():<20}: {value}")

        print(f"\nIdentified Clusters (Threshold=5):")
        if not clusters:
            print("  No significant clusters detected.")
        for idx, cluster in enumerate(clusters):
            print(f"  Cluster {idx+1}: {cluster}")

        # Frequency analysis
        freq = collections.Counter(self.keys)
        duplicates = {k: v for k, v in freq.items() if v > 1}
        if duplicates:
            print(f"\nRecurring IDs:")
            for k, v in duplicates.items():
                print(f"  ID {k}: {v} times")

        print("-" * 30)

if __name__ == "__main__":
    # Context keys provided for analysis
    context_keys = [50, 19, 7, 8, 22, 2, 3, 4, 5, 60]

    analyzer = FailureAnalyzer(context_keys)
    analyzer.report()
