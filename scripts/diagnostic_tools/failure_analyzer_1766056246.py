import collections
import json


class FailureAnalyzer:
    """
    Diagnostic tool for analyzing recurring failure patterns.
    Usage: Instantiate with a list of failure keys/signatures and call display_report().
    """
    def __init__(self, failure_keys):
        self.failure_keys = failure_keys

    def calculate_metrics(self):
        """Performs frequency analysis on failure data."""
        if not self.failure_keys:
            return None

        total = len(self.failure_keys)
        counts = collections.Counter(self.failure_keys)
        
        return {
            "total_samples": total,
            "unique_signatures": len(counts),
            "top_recurring": counts.most_common(3),
            "distribution": {str(k): f"{(v / total) * 100:.1f}%" for k, v in counts.items()}
        }

    def display_report(self):
        """Formats and prints the diagnostic findings."""
        metrics = self.calculate_metrics()
        if not metrics:
            print("Error: No diagnostic data available.")
            return

        print("--- FAILURE PATTERN ANALYSIS REPORT ---")
        print(f"Total Events: {metrics['total_samples']}")
        print(f"Unique Keys:  {metrics['unique_signatures']}")
        print("\nPrimary Failure Drivers:")
        for key, count in metrics['top_recurring']:
            print(f" - Key [{key}]: {count} occurrences")
        
        print("\nPattern Distribution:")
        print(json.dumps(metrics['distribution'], indent=4))
        print("---------------------------------------")

if __name__ == "__main__":
    # Context provided: [50, 19, 7, 8, 22, 2, 3, 4, 5, 60]
    # Adding synthetic recurrences to demonstrate pattern analysis
    context_keys = [50, 19, 7, 8, 22, 2, 3, 4, 5, 60, 50, 7, 50, 22, 50]
    
    analyzer = FailureAnalyzer(context_keys)
    analyzer.display_report()