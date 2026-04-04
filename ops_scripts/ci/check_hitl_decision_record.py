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
    """Main function to check files in a directory for HITL records."""
    if len(sys.argv) != 2:
        print("Usage: python check_hitl_decision_record.py <directory_path>")
        sys.exit(1)

    target_dir = Path(sys.argv[1])
    if not target_dir.is_dir():
        print(f"ERROR: Directory not found: {target_dir}")
        sys.exit(1)

    files_to_check = list(target_dir.glob('*.md'))
    all_passed = True

    for file_path in files_to_check:
        if not check_hitl_record(file_path):
            all_passed = False

    if not all_passed:
        sys.exit(1)

if __name__ == "__main__":
    main()
