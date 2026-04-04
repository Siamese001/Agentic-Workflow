import re
import sys
from pathlib import Path


def check_rca_status(file_path: Path) -> bool:
    """Checks if an RCA markdown file has the status 'RESOLVED'."""
    content = file_path.read_text(encoding="utf-8")
    status_match = re.search(r"^Status:\s*(?P<status>.*)$", content, re.MULTILINE)

    if not status_match:
        print(f"ERROR: No 'Status:' line found in {file_path}")
        return False

    status = status_match.group("status").strip()
    if status != "RESOLVED":
        print(f"ERROR: RCA {file_path} has status '{status}'. Must be 'RESOLVED'.")
        return False

    print(f"SUCCESS: RCA {file_path} is RESOLVED.")
    return True

def main():
    """Main function to check RCA files in a given directory."""
    if len(sys.argv) != 2:
        print("Usage: python check_rca_closure.py <directory_path>")
        sys.exit(1)

    rca_dir = Path(sys.argv[1])
    if not rca_dir.is_dir():
        print(f"ERROR: Directory not found: {rca_dir}")
        sys.exit(1)

    files_to_check = list(rca_dir.glob('RCA_*.md'))
    all_passed = True

    for file_path in files_to_check:
        if not check_rca_status(file_path):
            all_passed = False

    if not all_passed:
        sys.exit(1)

if __name__ == "__main__":
    main()
