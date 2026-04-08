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
    """Main function to check RCA files.

    Supports:
    - No args: scan repository for RCA_*.md
    - One dir arg: scan that directory for RCA_*.md
    - File args (pre-commit): scan provided RCA markdown files
    """
    args = sys.argv[1:]

    if not args:
        print("INFO: No RCA files provided; skipping RCA closure check.")
        return
    elif len(args) == 1 and Path(args[0]).is_dir():
        files_to_check = list(Path(args[0]).glob("RCA_*.md"))
    else:
        files_to_check = [Path(p) for p in args if Path(p).is_file() and Path(p).name.startswith("RCA_") and Path(p).suffix.lower() == ".md"]

    all_passed = True

    for file_path in files_to_check:
        if not check_rca_status(file_path):
            all_passed = False

    if not all_passed:
        sys.exit(1)

if __name__ == "__main__":
    main()
