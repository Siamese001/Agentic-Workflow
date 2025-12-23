# Reasoning Summary:
# 1. Recalled governance laws to ensure atomic diagnostic logic.
# 2. Identified key-value clustering as the primary pattern for failure analysis.
# 3. Implemented a minimal, focused analyzer class to maintain depth limits.
# 4. Verified zero external dependencies to prevent blast radius expansion.
# 5. Confirmed deterministic output to ensure signal stability.

import collections


class FailureAnalyzer:
    """
    Diagnostic tool for analyzing recurring failure patterns.

    Usage:
        Initialize with a list of failure keys.
        Call `analyze()` to get statistical breakdown.
        Call `report()` for a formatted console output.
    """
    def __init__(self, failure_keys):
        self.keys = failure_keys

    def analyze(self):
        """Calculates frequency distribution and impact metrics."""
        if not self.keys:
            return {"error": "No failure keys provided."}

        counts = collections.Counter(self.keys)
        total = len(self.keys)

        return {
            "metrics": {
                "total_failures": total,
                "unique_patterns": len(counts),
                "high_frequency_key": counts.most_common(1)[0][0] if total > 0 else None
            },
            "distribution": {
                str(k): {"count": v, "percentage": round((v / total) * 100, 2)}
                for k, v in counts.items()
            }
        }

    def report(self):
        """Outputs the analysis in a clear, readable format."""
        results = self.analyze()
        print(f"--- FAILURE ANALYSIS REPORT ---")
        print(f"Scope: {results['metrics']['total_failures']} events")
        print(f"Uniqueness: {results['metrics']['unique_patterns']} patterns identified")
        print("-" * 31)
        print(f"{'Key':<10} | {'Count':<7} | {'Impact'}")

        # Sort by count descending then key ascending
        sorted_dist = sorted(results['distribution'].items(), key=lambda x: (-x[1]['count'], x[0]))
        for key, data in sorted_dist:
            print(f"{key:<10} | {data['count']:<7} | {data['percentage']}%")

if __name__ == "__main__":
    # Contextual failure data for analysis
    CONTEXT_KEYS = [50, 19, 7, 8, 22, 2, 3, 4, 5, 60]

    analyzer = FailureAnalyzer(CONTEXT_KEYS)
    analyzer.report()
