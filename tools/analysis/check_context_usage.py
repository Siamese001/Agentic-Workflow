"""Check context usage for test reconstruction batches."""

import json
from pathlib import Path
from typing import Any


class ContextChecker:
    """Monitor and report context usage during test reconstruction."""

    def __init__(self):
        self.max_context_kb = 128
        self.tracking_file = Path("tools/context_usage.json")
        self.usage_data = self._load_tracking_data()

    def _load_tracking_data(self) -> dict[str, Any]:
        """Load existing tracking data."""
        if self.tracking_file.exists():
            with open(self.tracking_file) as f:
                return json.load(f)
        return {"batches": [], "current_session": {}, "warnings": []}

    def _save_tracking_data(self):
        """Save tracking data."""
        with open(self.tracking_file, "w") as f:
            json.dump(self.usage_data, f, indent=2)

    def estimate_batch_usage(self, batch_name: str, file_count: int, layer: str) -> dict[str, Any]:
        """Estimate context usage for a batch."""
        # Base context for shared fixtures and layer structure
        base_context_kb = {
            "runtime": 45,
            "l0_routing": 40,
            "l2_execution": 50,
            "l5_safety": 35,
            "governance": 30,
            "integration": 45,
            "e2e": 40,
        }.get(layer, 40)

        # Context per file (source + test code)
        per_file_kb = {
            "runtime": 1.8,
            "l0_routing": 1.5,
            "l2_execution": 2.0,
            "l5_safety": 1.2,
            "governance": 1.0,
            "integration": 1.8,
            "e2e": 1.5,
        }.get(layer, 1.5)

        total_kb = base_context_kb + (file_count * per_file_kb)
        percentage = (total_kb / self.max_context_kb) * 100

        result = {
            "batch_name": batch_name,
            "layer": layer,
            "file_count": file_count,
            "estimated_usage_kb": total_kb,
            "percentage_of_limit": percentage,
            "status": "OK" if percentage < 80 else "WARNING" if percentage < 95 else "CRITICAL",
            "base_context_kb": base_context_kb,
            "per_file_kb": per_file_kb,
        }

        # Track this batch
        self.usage_data["batches"].append(
            {
                **result,
                "timestamp": str(Path().cwd()),
                "actual_usage_kb": None,  # Would be filled by actual measurement
            },
        )

        self._save_tracking_data()

        return result

    def check_batch(self, batch_name: str) -> dict[str, Any]:
        """Check context usage for a specific batch."""
        # Find batch in tracking data
        for batch in self.usage_data["batches"]:
            if batch["batch_name"] == batch_name:
                return batch

        # Return default if not found
        return {
            "batch_name": batch_name,
            "estimated_usage_kb": 75,
            "percentage_of_limit": 58.6,
            "status": "OK",
            "message": "Batch not found in tracking data",
        }

    def get_session_summary(self) -> dict[str, Any]:
        """Get summary of current session."""
        total_batches = len(self.usage_data["batches"])
        if total_batches == 0:
            return {"message": "No batches processed yet"}

        avg_usage = sum(b.get("estimated_usage_kb", 0) for b in self.usage_data["batches"]) / total_batches
        max_usage = max(b.get("percentage_of_limit", 0) for b in self.usage_data["batches"])

        return {
            "total_batches": total_batches,
            "average_usage_kb": avg_usage,
            "average_percentage": (avg_usage / self.max_context_kb) * 100,
            "max_percentage": max_usage,
            "status": "OK" if max_usage < 80 else "WARNING" if max_usage < 95 else "CRITICAL",
        }


def main():
    """Command line interface."""
    import argparse

    parser = argparse.ArgumentParser(description="Check context usage")
    parser.add_argument("--batch", required=True, help="Batch name to check")
    parser.add_argument("--files", type=int, help="Number of files in batch")
    parser.add_argument("--layer", help="Layer being processed")
    parser.add_argument("--summary", action="store_true", help="Show session summary")

    args = parser.parse_args()

    checker = ContextChecker()

    if args.summary:
        summary = checker.get_session_summary()
        print("\n=== Session Summary ===")
        for key, value in summary.items():
            print(f"{key}: {value}")
    else:
        if args.files and args.layer:
            # Estimate new batch
            result = checker.estimate_batch_usage(args.batch, args.files, args.layer)
        else:
            # Check existing batch
            result = checker.check_batch(args.batch)

        print(f"\n=== Context Usage for {args.batch} ===")
        print(f"Estimated usage: {result['estimated_usage_kb']:.1f} KB")
        print(f"Percentage of limit: {result['percentage_of_limit']:.1f}%")
        print(f"Status: {result['status']}")

        if result["percentage_of_limit"] > 80:
            print("\n⚠️  WARNING: High context usage detected!")
            print("Consider reducing batch size or optimizing imports.")


if __name__ == "__main__":
    main()
