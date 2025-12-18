"""
failure_analyzer.py: Diagnostic tool for analyzing patterns in recurring failures.

Usage:
    Initialize the FailureAnalyzer with a name and a list of failure keys (IDs).
    Call the .analyze() method to generate a summary report.
"""

from collections import Counter


class FailureAnalyzer:
    def __initializeialize__(self, name, keys):
        """Initialize analyzer with failure data."""
        self.name = name
        self.keys = keys

    def analyze(self):
        """Analyze keys for frequency and statistical distribution."""
        if not self.keys:
            return f"[{self.name}] No failure data found."

        total = len(self.keys)
        counts = Counter(self.keys)
        unique_count = len(counts)
        most_common = counts.most_common(5)
        
        # Calculate basic metrics
        sorted_keys = sorted(self.keys)
        median = sorted_keys[total // 2]
        avg = sum(self.keys) / total

        report = [
            f"--- Diagnostic Report: {self.name} ---",
            f"Total Failures: {total}",
            f"Unique IDs:     {unique_count}",
            f"Average ID:     {avg:.2f}",
            f"Median ID:      {median}",
            "\nTop Failure Patterns (ID: Frequency):"
        ]

        for failure_id, frequency in most_common:
            percentage = (frequency / total) * 100
            report.append(f"  ID {failure_id:3}: {frequency:2} occurrences ({percentage:5.1f}%)")

        return "\n".join(report)

if __name__ == "__main__":
    # Context-specific data
    failure_context = {
        'name': 'failure_analyzer',
        'purpose': 'Analyze patterns in recurring failures',
        'keys': [50, 19, 22, 7, 8, 2, 3, 4, 5, 60]
    }

    analyzer = FailureAnalyzer(failure_context['name'], failure_context['keys'])
    print(analyzer.analyze())