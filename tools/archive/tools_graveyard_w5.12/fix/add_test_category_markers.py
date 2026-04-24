#!/usr/bin/env python3
"""
Add category markers to all tests.
Target: Add @pytest.mark.* markers to all test functions.
"""

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestCategoryMarkerAdder:
    """Add category markers to all tests."""

    def __init__(self):
        self.test_files = []
        self.markers_added = 0
        self.errors = 0

        # Load test inventory
        with open(PROJECT_ROOT / "tools" / "test_enforcement" / "test_inventory.json") as f:
            inventory = json.load(f)
            self.test_files = inventory.get("test_files", [])

    def add_category_markers_to_all_tests(self):
        """Add category markers to all test functions."""
        print("🔧 Adding category markers to all tests...")

        for test_file_info in self.test_files[:500]:  # Process first 500 files as demo
            file_path = Path(test_file_info["file_path"])

            if not file_path.exists():
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
                lines = content.splitlines()
                modified = False

                # Find all test functions and add markers if missing
                for i, line in enumerate(lines):
                    if re.match(r"^\s*def test_", line):
                        # Check if marker already exists above
                        has_marker = False
                        for j in range(max(0, i - 3), i):
                            if "@pytest.mark." in lines[j]:
                                has_marker = True
                                break

                        if not has_marker:
                            # Determine appropriate category
                            category = self._determine_test_category(file_path, line)
                            indent = len(line) - len(line.lstrip())
                            marker_line = " " * indent + category
                            lines.insert(i, marker_line)
                            modified = True
                            self.markers_added += 1

                if modified:
                    file_path.write_text("\n".join(lines), encoding="utf-8")

                    if self.markers_added % 50 == 0:
                        print(f"    Added {self.markers_added} category markers...")

            except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
                self.errors += 1
                print(f"    Error processing {file_path}: {e}")

        print(f"  ✅ Added {self.markers_added} category markers")

    def _determine_test_category(self, file_path, test_line):
        """Determine appropriate test category marker."""
        path_str = str(file_path)

        # Determine category based on file path
        if "/unit_min_deps/" in path_str:
            return "@pytest.mark.unit_min_deps"
        elif "/unit/" in path_str:
            return "@pytest.mark.unit"
        elif "/integration/" in path_str:
            return "@pytest.mark.integration"
        elif "/e2e/" in path_str:
            return "@pytest.mark.e2e"
        elif "performance" in path_str.lower():
            return "@pytest.mark.performance"
        elif "security" in path_str.lower():
            return "@pytest.mark.security"
        elif "adg" in path_str.lower():
            return "@pytest.mark.adg"
        elif "sovereign" in path_str.lower():
            return "@pytest.mark.sovereign"
        elif "guardian" in path_str.lower():
            return "@pytest.mark.guardian"
        else:
            return "@pytest.mark.unit"  # Default to unit

    def generate_marker_report(self):
        """Generate a report of markers added."""
        print("📋 Generating category marker report...")

        report = {
            "marker_timestamp": "2026-03-24T19:45:00Z",
            "total_test_files": len(self.test_files),
            "markers_added": self.markers_added,
            "errors": self.errors,
            "files_processed": min(500, len(self.test_files)),
        }

        report_file = PROJECT_ROOT / "tools" / "test_category_markers_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"✅ Marker report written to: {report_file}")

        return report


def main():
    """Main entry point."""
    print("=" * 80)
    print("TEST CATEGORY MARKER ADDER")
    print("=" * 80)
    print("Adding category markers to all test functions...")
    print("=" * 80)

    adder = TestCategoryMarkerAdder()

    print(f"📊 Processing {len(adder.test_files)} test files:")

    # Add category markers
    adder.add_category_markers_to_all_tests()

    # Generate report
    report = adder.generate_marker_report()

    print("\n" + "=" * 80)
    print("🎉 TEST CATEGORY MARKERS ADDED!")
    print(f"✅ Markers added: {report['markers_added']}")
    print(f"📁 Files processed: {report['files_processed']}")
    print(f"❌ Errors: {report['errors']}")

    if report["files_processed"] < len(adder.test_files):
        print("\n📝 REMAINING:")
        print(f"   {len(adder.test_files) - report['files_processed']} files to process")
    else:
        print("\n🎉 ALL TEST CATEGORY MARKERS ADDED!")

    print("=" * 80)


if __name__ == "__main__":
    main()
