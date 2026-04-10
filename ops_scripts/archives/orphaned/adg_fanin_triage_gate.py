import argparse
import subprocess
import sys
from pathlib import Path


def get_staged_files():
    """Gets the list of staged files from git."""
    cmd = ["git", "diff", "--name-only", "--cached"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return [Path(p) for p in result.stdout.strip().split('\n') if p]

def main():
    """Main function to run the ADG fan-in triage gate."""
    parser = argparse.ArgumentParser(description="ADG Fan-In Test Triage Gate")
    parser.add_argument("--staged", action="store_true", help="Run on staged files")
    parser.add_argument("files", nargs='*', help="Specific files to check")
    args = parser.parse_args()

    if args.staged:
        files_to_check = get_staged_files()
    elif args.files:
        files_to_check = [Path(f) for f in args.files]
    else:
        print("Usage: python adg_fanin_triage_gate.py [--staged | file1 file2 ...]")
        sys.exit(1)

    adg_test_files = [f for f in files_to_check if f.name.endswith("_adg.py")]

    if not adg_test_files:
        print("No `_adg.py` files to check. Gate passed.")
        sys.exit(0)

    print(f"Checking {len(adg_test_files)} `_adg.py` file(s)...")
    all_passed = True
    for f in adg_test_files:
        print(f"-- Verifying {f}...")
        cmd = ["python", "tools/adg/adg_test_triage.py", "classify", "--pattern", str(f)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            print(f"❌ ERROR: Triage script failed for {f}")
            print(result.stderr)
            all_passed = False
        else:
            # A more robust check could validate the output classification here
            print(f"✅ SUCCESS: Triage script passed for {f}")
            print(result.stdout)

    if not all_passed:
        print("\nADG Fan-In Triage Gate FAILED.")
        sys.exit(1)

    print("\nADG Fan-In Triage Gate PASSED.")

if __name__ == "__main__":
    main()
