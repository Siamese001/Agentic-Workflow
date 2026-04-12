import re
import sys
from pathlib import Path


def add_status_if_missing(file_path: Path):
    """Adds 'Status: RESOLVED' to an RCA file if it's missing."""
    content = file_path.read_text(encoding="utf-8")
    if not re.search(r"^Status:", content, re.MULTILINE):
        # Add status after the Date line, or at the top if Date is not found
        if re.search(r"^Date:", content, re.MULTILINE):
            new_content = re.sub(r"(Date:.*)", r"\1\nStatus: RESOLVED", content, 1, re.MULTILINE)
        else:
            new_content = "Status: RESOLVED\n" + content

        file_path.write_text(new_content, encoding="utf-8")
        print(f"Patched {file_path}")
        return True
    else:
        print(f"Skipped {file_path} (status already present)")
        return False


def main():
    """Main function to patch all RCA files in the plans directory."""
    plans_dir = Path("docs/reports/plans")
    if not plans_dir.is_dir():
        print(f"ERROR: Directory not found: {plans_dir}")
        sys.exit(1)

    rca_files = list(plans_dir.glob("RCA_*.md"))
    patched_count = 0
    for file_path in rca_files:
        if add_status_if_missing(file_path):
            patched_count += 1

    print(f"\nPatching complete. {patched_count} of {len(rca_files)} files were updated.")


if __name__ == "__main__":
    main()
