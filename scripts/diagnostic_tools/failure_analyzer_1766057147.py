"""
Failure Analyzer Diagnostic Tool
Purpose: Analyze patterns in recurring failures by calculating frequency distribution and identifying anomalies.
Usage: Instantiate FailureAnalyzer with a name and a list of keys, then call analyze().
"""

import collections


class FailureAnalyzer:
    def __init__(self, name: str, keys: list):
        self.name = name
        self.keys = keys

    def analyze(self) -> str:
        """Perform statistical analysis on failure keys to detect patterns."""
        if not self.keys:
            return f"[{self.name}] No failure data available for analysis."

        total_count = len(self.keys)
        frequency = collections.Counter(self.keys)
        unique_failures = len(frequency)
        
        # Identify the most frequent failure patterns
        most_common = frequency.most_common(3)
        
        # Calculate the recurrence rate (ratio of repeated failures to total)
        recurrence_rate = (total_count - unique_failures) / total_count if total_count > 0 else 0

        report = [
            f"--- Diagnostic Report: {self.name} ---",
            f"Total Failure Events: {total_count}",
            f"Unique Failure Types: {unique_failures}",
            f"Recurrence Rate:      {recurrence_rate:.2%}",
            "Top Failure Patterns (Key: Occurrences):",
        ]
        
        for key, count in most_common:
            percentage = (count / total_count) * 100
            report.append(f"  - Key {key: <4}: {count} ({percentage:.1f}%)")
            
        return "\n".join(report)

def main():
    # Context provided for analysis
    context = {
        'name': 'failure_analyzer', 
        'purpose': 'Analyze patterns in recurring failures', 
        'keys': [50, 19, 7, 8, 22, 2, 3, 4, 5, 60, 50, 7, 50]
    }
    
    analyzer = FailureAnalyzer(context['name'], context['keys'])
    print(analyzer.analyze())

if __name__ == '__main__':
    main()