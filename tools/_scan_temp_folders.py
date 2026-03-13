"""Scan for unused backup/temp folders that should be deleted."""

from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent

# Temp/cache folders that should be deleted if unused
TEMP_FOLDER_PATTERNS = {
    ".nox",
    ".pytest_tmp",
    ".pytest_cache",
    ".tox",
    ".backup",
    ".healing_backups",
    ".mypy_cache",
    ".ruff_cache",
    "__pycache__",
    ".coverage_html",
    "htmlcov",
}

print("=== SCANNING FOR UNUSED TEMP/BACKUP FOLDERS ===\n")

temp_dirs = []
total_size = 0

for entry in ROOT.iterdir():
    if not entry.is_dir():
        continue

    if entry.name in TEMP_FOLDER_PATTERNS or entry.name.startswith("tmp"):
        try:
            size = sum(f.stat().st_size for f in entry.rglob("*") if f.is_file())
            mtime = entry.stat().st_mtime
            age_days = (datetime.now().timestamp() - mtime) / 86400

            temp_dirs.append(
                {
                    "name": entry.name,
                    "size": size,
                    "size_mb": size / (1024 * 1024),
                    "age_days": age_days,
                    "last_modified": datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
            total_size += size
        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"  [ERROR] Could not scan {entry.name}: {e}")

print(f"Found {len(temp_dirs)} temp/backup folders:\n")
print(f"{'Folder':<25} {'Size (MB)':>12} {'Age (days)':>12} {'Last Modified':<20} {'Action'}")
print("-" * 90)

for d in sorted(temp_dirs, key=lambda x: x["size"], reverse=True):
    # Determine action based on age and type
    if d["age_days"] > 30:
        action = "DELETE (>30 days old)"
    elif d["name"] in {".nox", ".pytest_tmp", ".pytest_cache", ".mypy_cache", ".ruff_cache"}:
        action = "DELETE (cache)"
    elif d["name"] == ".healing_backups" and d["age_days"] > 7:
        action = "DELETE (old backups)"
    elif d["name"] == ".backup" and d["age_days"] > 7:
        action = "DELETE (old backups)"
    else:
        action = "KEEP (recent)"

    print(f"{d['name']:<25} {d['size_mb']:>12.2f} {d['age_days']:>12.1f} {d['last_modified']:<20} {action}")

print("-" * 90)
print(f"{'TOTAL':<25} {total_size / (1024 * 1024):>12.2f} MB")

print("\n=== RECOMMENDATION ===")
deletable = [
    d
    for d in temp_dirs
    if d["age_days"] > 7 or d["name"] in {".nox", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
]
if deletable:
    deletable_size = sum(d["size"] for d in deletable)
    print(f"Can safely delete {len(deletable)} folders to reclaim {deletable_size / (1024 * 1024):.2f} MB:")
    for d in deletable:
        print(f"  • {d['name']}")
else:
    print("No folders recommended for deletion.")
