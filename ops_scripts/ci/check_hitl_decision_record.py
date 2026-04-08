import sys
from pathlib import Path


def check_hitl_record(file_path: Path) -> bool:
    """Checks if a markdown file contains a HITL_DECISION_RECORD section."""
    content = file_path.read_text(encoding="utf-8")

    # Simple check for the presence of the HITL record section
    if "## HITL_DECISION_RECORD" in content:
        print(f"SUCCESS: HITL_DECISION_RECORD found in {file_path}")
        return True

    # A more complex rule could be to check if a HITL was expected
    # For now, we'll just warn if it's not found in a plan.
    if file_path.parent.name == "plans":
        print(f"WARNING: No HITL_DECISION_RECORD found in plan {file_path}. This may be acceptable.")

    return True # For now, we don't fail the build, just warn

def main():
    """Main function to check files for HITL records.

    Supports:
    - No args: scan markdown files under current working directory
    - One dir arg: scan markdown files in that directory
    - File args (pre-commit): scan provided markdown files only
    """
    args = sys.argv[1:]

    if not args:
        files_to_check = list(Path.cwd().rglob("*.md"))
    elif len(args) == 1 and Path(args[0]).is_dir():
        files_to_check = list(Path(args[0]).glob("*.md"))
    else:
        files_to_check = [Path(p) for p in args if Path(p).suffix.lower() == ".md" and Path(p).is_file()]

    all_passed = True

    for file_path in files_to_check:
        if not check_hitl_record(file_path):
            all_passed = False

    if not all_passed:
        sys.exit(1)

if __name__ == "__main__":
    main()
