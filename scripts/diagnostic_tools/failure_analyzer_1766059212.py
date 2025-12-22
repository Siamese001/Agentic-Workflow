import collections


class FailureAnalyzer:
    """
    Diagnostic tool to analyze recurring failure patterns.
    Usage: Initialize with a list of failure keys and call analyze().
    """
    def __init__(self, keys):
        self.keys = keys

    def analyze(self):
        """Performs frequency analysis and identifies primary failure modes."""
        if not self.keys:
            return "Analysis Complete: No failure data present."

        counts = collections.Counter(self.keys)
        total_events = len(self.keys)
        most_common = counts.most_common(5)

        report = [
            "=== RECURRING FAILURE PATTERN REPORT ===",
            f"Total Failure Events: {total_events}",
            f"Unique Failure Keys:  {len(counts)}",
            "----------------------------------------",
            "Top Failure Modes (Key: Count [Frequency]):"
        ]

        for key, count in most_common:
            freq = (count / total_events) * 100
            report.append(f"  Key {key:<3}: {count:>2} hits ({freq:>5.1f}%)")

        report.append("========================================")
        return "\n".join(report)

def main():
    # Context-provided keys for diagnostic execution
    data = [50, 19, 7, 8, 22, 2, 3, 4, 5, 60]
    analyzer = FailureAnalyzer(data)
    print(analyzer.analyze())

if __name__ == "__main__":
    main()
