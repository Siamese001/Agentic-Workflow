"""
FailureAnalyzer Diagnostic Tool
Purpose: Analyzes frequency patterns and statistical distribution of failure codes 
to identify recurring system bottlenecks.
Usage: Instantiate FailureAnalyzer with a list of failure keys and call analyze().
"""
import collections
import math


class FailureAnalyzer:
    def __init__(self, failure_keys):
        self.keys = sorted(failure_keys)
        self.total = len(self.keys)

    def _calculate_metrics(self):
        """Calculates frequency distribution and variance."""
        counts = collections.Counter(self.keys)
        mean = sum(self.keys) / self.total if self.total > 0 else 0
        variance = sum((x - mean) ** 2 for x in self.keys) / self.total if self.total > 0 else 0
        return counts, mean, math.sqrt(variance)

    def analyze(self):
        """Outputs a structured diagnostic report of failure patterns."""
        if not self.keys:
            print("Status: No data available.")
            return

        counts, mean, std_dev = self._calculate_metrics()
        
        print(f"{'='*40}")
        print(f"FAILURE PATTERN DIAGNOSTIC")
        print(f"{'='*40}")
        print(f"Total Events:  {self.total}")
        print(f"Unique Keys:   {len(counts)}")
        print(f"Mean Key ID:   {mean:.2f}")
        print(f"Std Deviation: {std_dev:.2f}")
        print(f"{'-'*40}")
        print(f"{'Key ID':<10} | {'Frequency':<10} | {'Impact %'}")
        print(f"{'-'*40}")
        
        for key, count in counts.most_common():
            percentage = (count / self.total) * 100
            print(f"{key:<10} | {count:<10} | {percentage:>8.1f}%")
        print(f"{'='*40}")

if __name__ == "__main__":
    # Contextual data injection
    CONTEXT_KEYS = [50, 19, 7, 8, 22, 2, 3, 4, 5, 60]
    
    analyzer = FailureAnalyzer(CONTEXT_KEYS)
    analyzer.analyze()