import sys
from pathlib import Path

SENTINEL_FILE = Path(__file__).resolve().parents[2] / "artifacts" / "adg" / "adg_ingested.sentinel"

def check_adg_ingestion() -> bool:
    """Checks if the ADG ingestion sentinel file exists."""
    if not SENTINEL_FILE.exists():
        print("ERROR: ADG artifacts have not been ingested. Run ingestion script first.")
        print(f"Expected sentinel file at: {SENTINEL_FILE.resolve()}")
        return False

    print("SUCCESS: ADG ingestion is verified.")
    return True

def main():
    """Main function to check for ADG ingestion."""
    if not check_adg_ingestion():
        sys.exit(1)

if __name__ == "__main__":
    main()
