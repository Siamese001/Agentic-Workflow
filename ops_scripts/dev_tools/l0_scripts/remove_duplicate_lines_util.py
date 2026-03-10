#!/usr/bin/env python3
"""
Remove duplicate const realAgentData declarations by line numbers.
"""

# Import SSOT for dashboard directory - NO HARDCODING
from agentic_core.L5_safety.config.structure_blueprint import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    DASHBOARD_DIR,
    get_validated_project_root,
)


def remove_duplicates():
    """Remove duplicate realAgentData declarations at specific line numbers."""
    dashboard_path = get_validated_project_root() / DASHBOARD_DIR / "autonomy_dashboard.html"

    print("Reading dashboard HTML...")
    lines = dashboard_path.read_text(encoding="utf-8").splitlines(keepends=True)

    # Line numbers to remove (keep first at 1427, remove others)
    # Convert to 0-indexed
    lines_to_remove_start = [10187 - 1, 18947 - 1, 27567 - 1, 36187 - 1]

    print(f"Total lines: {len(lines)}")
    print(f"Removing duplicate realAgentData declarations at lines: {[l + 1 for l in lines_to_remove_start]}")

    # For each duplicate, find the end of the declaration (the closing };)
    ranges_to_remove = []

    for start_line in lines_to_remove_start:
        # Find the comment line before it
        comment_line = start_line - 1
        if comment_line >= 0 and "Real per-agent data" in lines[comment_line]:
            # Find the closing }; after the declaration
            end_line = start_line
            brace_count = 0
            found_start = False

            for i in range(start_line, min(start_line + 10000, len(lines))):
                line = lines[i]
                if "{" in line:
                    brace_count += line.count("{")
                    found_start = True
                if "}" in line:
                    brace_count -= line.count("}")
                    if found_start and brace_count == 0 and "};" in line:
                        end_line = i
                        break

            ranges_to_remove.append((comment_line, end_line))
            print(f"  Range: lines {comment_line + 1} to {end_line + 1}")

    # Remove ranges in reverse order to preserve indices
    for start, end in reversed(ranges_to_remove):
        del lines[start : end + 1]

    # Write back
    dashboard_path.write_text("".join(lines), encoding="utf-8")
    print(f"✅ Removed {len(ranges_to_remove)} duplicate declarations")
    print(f"   New file has {len(lines)} lines")


if __name__ == "__main__":
    remove_duplicates()
