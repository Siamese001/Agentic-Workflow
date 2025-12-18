import collections
import json


class FailureAnalyzer:
    """
    Diagnostic tool to analyze patterns in recurring failures.
    
    Usage:
        Initialize with a list of failure keys/codes.
        Call analyze_patterns() to retrieve frequency distribution and metrics.
    """
    def __init__(self, failure_keys):
        self.failure_keys = failure_keys

    def analyze_patterns(self):
        """Extracts frequency counts and recurrence metrics from the dataset."""
        if not self.failure_keys:
            return {"error": "No data provided"}

        counts = collections.Counter(self.failure_keys)
        total_failures = len(self.failure_keys)
        unique_count = len(counts)
        
        # Calculate recurrence ratio to determine the severity of pattern repetition
        recurrence_ratio = (total_failures - unique_count) / total_failures if total_failures > 0 else 0

        return {
            "summary": {
                "total_events": total_failures,
                "unique_keys": unique_count,
                "recurrence_ratio": round(recurrence_ratio, 4)
            },
            "frequency_map": dict(counts.most_common()),
            "top_offenders": [key for key, count in counts.most_common() if count > 1]
        }

def run_diagnostic():
    """Main execution block for standalone diagnostic analysis."""
    # Context provided by governance agent
    context_keys = [50, 19, 7, 8, 22, 2, 3, 4, 5, 60]
    
    analyzer = FailureAnalyzer(context_keys)
    report = analyzer.analyze_patterns()
    
    print("--- Failure Pattern Analysis Report ---")
    print(json.dumps(report, indent=4))

if __name__ == "__main__":
    run_diagnostic()