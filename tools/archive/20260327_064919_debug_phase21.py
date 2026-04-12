#!/usr/bin/env python3
"""Debug Phase 2.1 test setup."""

import json

# Import the module we're testing
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent / "tools"))

from fix_high_severity_silent_swallowers import HighSeveritySilentSwallowerFixer


def debug_phase21():
    """Debug Phase 2.1 setup."""

    with tempfile.TemporaryDirectory() as temp_dir:
        workspace = Path(temp_dir)

        # Create test files
        test_file = workspace / "test_file.py"
        content = """try:
    import missing_dependency
except ImportError:
    pass"""
        test_file.write_text(content)
        print(f"Created test_file: {test_file}")
        print(f"Content:\n{test_file.read_text()}")

        optional_file = workspace / "optional_file.py"
        content = """try:
    import optional_module
except ImportError:
    pass"""
        optional_file.write_text(content)
        print(f"Created optional_file: {optional_file}")

        test_dir = workspace / "tests"
        test_dir.mkdir()
        required_test = test_dir / "test_required.py"
        content = """try:
    import test_dependency
except ImportError:
    pass"""
        required_test.write_text(content)
        print(f"Created test_required: {required_test}")

        # Create violations
        violations = {
            "scan_timestamp": "2026-03-24T19:30:00Z",
            "total_violations": 3,
            "violations": [
                {
                    "file_path": str(test_file),
                    "line_number": 2,
                    "exception_type": "ImportError",
                    "handler_body": ["pass"],
                    "context": "import missing_dependency",
                    "severity": "HIGH",
                },
                {
                    "file_path": str(optional_file),
                    "line_number": 2,
                    "exception_type": "ImportError",
                    "handler_body": ["pass"],
                    "context": "optional import fallback",
                    "severity": "HIGH",
                },
                {
                    "file_path": str(required_test),
                    "line_number": 2,
                    "exception_type": "ImportError",
                    "handler_body": ["pass"],
                    "context": "import test_dependency",
                    "severity": "HIGH",
                },
            ],
        }

        # Create tools directory and violations file
        tools_dir = workspace / "tools"
        tools_dir.mkdir()
        violations_file = tools_dir / "silent_swallower_report.json"
        with open(violations_file, "w") as f:
            json.dump(violations, f)

        print(f"Created violations file: {violations_file}")
        print(f"Violations: {len(violations['violations'])}")

        # Test the fixer
        with patch("fix_high_severity_silent_swallowers.PROJECT_ROOT", workspace):
            fixer = HighSeveritySilentSwallowerFixer()
            print(f"Loaded {len(fixer.violations)} violations")

            # Check first violation
            if fixer.violations:
                v = fixer.violations[0]
                print(f"First violation: {v}")
                file_path = Path(v["file_path"])
                print(f"File exists: {file_path.exists()}")
                if file_path.exists():
                    lines = file_path.read_text().splitlines()
                    print(f"File has {len(lines)} lines")
                    if v["line_number"] <= len(lines):
                        print(f"Line {v['line_number']}: {lines[v['line_number'] - 1]}")
                    else:
                        print(f"Line {v['line_number']} not found")

            # Try applying fixes
            result = fixer.apply_fixes_to_all_remaining_violations()
            print(f"Result: {result}")


if __name__ == "__main__":
    debug_phase21()
