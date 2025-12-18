"""
Failure Analyzer Tool
Purpose: Analyzes frequency and patterns in recurring failure data.
Usage: Instantiate with a list of failure keys and call .analyze() to see distribution.
"""

import collections


class FailureAnalyzer:
    def __init__(self, failure_keys):
        """Initialize the analyzer with a collection of failure identifiers."""
        self.failure_keys = failure_keys
        self.total_count = len(failure_keys)
        self.distribution = collections.Counter(failure_keys)

    def analyze(self):
        """Prints a formatted statistical breakdown of the failure patterns."""
        if not self.failure_keys:
            print("No failure data provided.")
            return

        print(f"{'Failure ID':<12} | {'Count':<8} | {'Frequency (%)':<15}")
        print("-" * 40)

        # Sort by frequency (most common first)
        for key, count in self.distribution.most_common():
            percentage = (count / self.total_count) * 100
            print(f"{str(key):<12} | {count:<8} | {percentage:>12.2f}%")
        
        print("-" * 40)
        print(f"Total Failures Processed: {self.total_count}")
        print(f"Unique Failure Types: {len(self.distribution)}")

if __name__ == '__main__':
    # Context provided failure keys
    context_keys = [50, 19, 7, 8, 22, 2, 3, 4, 5, 60]
    
    # Extended sample for demonstration
    sample_data = context_keys + [50, 50, 7, 2, 50, 19, 7]
    
    analyzer = FailureAnalyzer(sample_data)
    analyzer.analyze()