"""
FailureAnalyzer Diagnostic Tool
Purpose: Analyzes frequency patterns in recurring failure keys to identify hotspots.
Usage: Instantiate FailureAnalyzer with failure data and call analyze().
"""

import collections
import json


class FailureAnalyzer:
    def __init__(self, context):
        self.name = context.get('name', 'unknown_analyzer')
        self.keys = context.get('keys', [])
        self.purpose = context.get('purpose', 'General Analysis')

    def analyze(self):
        """Perform frequency analysis on the provided keys."""
        if not self.keys:
            return "No data points provided for analysis."

        counts = collections.Counter(self.keys)
        total = len(self.keys)
        unique = len(counts)

        # Sort by frequency descending
        sorted_patterns = counts.most_common()

        report = {
            "metadata": {
                "agent": "ToolsmithAgent",
                "target": self.name,
                "total_events": total,
                "unique_keys": unique
            },
            "frequency_distribution": [
                {"key": k, "count": v, "percentage": f"{(v/total)*100:.2f}%"}
                for k, v in sorted_patterns
            ],
            "recommendation": "Address high-frequency keys first to optimize healing."
        }
        return report

    def display(self):
        """Print the analysis in a clean format."""
        result = self.analyze()
        print(f"--- {self.name.upper()} REPORT ---")
        print(f"Purpose: {self.purpose}")
        print(json.dumps(result, indent=2))
        print("-" * (len(self.name) + 15))

if __name__ == "__main__":
    # Context provided by sovereign governance layer
    context = {
        'name': 'failure_analyzer',
        'purpose': 'Analyze patterns in recurring failures',
        'keys': [50, 19, 7, 8, 22, 2, 3, 4, 5, 60, 50, 7, 50, 22]
    }

    analyzer = FailureAnalyzer(context)
    analyzer.display()
