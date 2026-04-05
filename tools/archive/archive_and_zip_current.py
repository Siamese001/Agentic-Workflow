#!/usr/bin/env python3
"""Archive current ADG artifacts and create new zip file."""

import gzip
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADG_DIR = ROOT / "artifacts" / "adg"
ARCHIVE_DIR = ADG_DIR / "_archive"


def archive_current_artifacts():
    """Archive all current _2008 artifacts."""
    timestamp = datetime.now().strftime("%m%d%Y_%H%M")
    current_month = datetime.now().strftime("%Y-%m")

    # Create archive directory for current month
    month_archive_dir = ARCHIVE_DIR / current_month
    month_archive_dir.mkdir(parents=True, exist_ok=True)

    print(f"Archiving _2008 artifacts to {month_archive_dir}")

    # Find all _2008 files
    artifact_files = list(ADG_DIR.glob("*_03222026_2008.*"))

    archived_count = 0
    for file_path in artifact_files:
        if file_path.is_file():
            # Create gzipped archive
            archive_path = month_archive_dir / f"{file_path.name}.gz"

            with open(file_path, 'rb') as f_in:
                with gzip.open(archive_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            print(f"  Archived: {file_path.name} -> {archive_path.name}")
            archived_count += 1

    print(f"✅ Archived {archived_count} files")
    return archived_count


def create_current_zip():
    """Create new zip file with current artifacts."""
    timestamp = datetime.now().strftime("%m%d%Y_%H%M")
    zip_path = ADG_DIR / f"adg_run_{timestamp}.zip"

    print(f"Creating new zip file: {zip_path.name}")

    # Get all current files (excluding archive and old zips)
    files_to_zip = []
    for file_path in ADG_DIR.iterdir():
        if (file_path.is_file() and
            not file_path.name.startswith('.') and
            not file_path.name.endswith('.zip') and
            file_path.name != 'README.md' and
            '_archive' not in file_path.name):
            files_to_zip.append(file_path)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files_to_zip:
            # Add file to zip with just the filename (no directory structure)
            zipf.write(file_path, file_path.name)
            print(f"  Added: {file_path.name}")

    zip_size = zip_path.stat().st_size / (1024 * 1024)  # MB
    print(f"✅ Created zip: {zip_path.name} ({zip_size:.1f} MB)")

    return zip_path


def cleanup_old_files():
    """Remove archived files from main directory."""
    print("Cleaning up archived files from main directory...")

    # Remove _2008 files
    artifact_files = list(ADG_DIR.glob("*_03222026_2008.*"))
    removed_count = 0

    for file_path in artifact_files:
        if file_path.is_file():
            file_path.unlink()
            print(f"  Removed: {file_path.name}")
            removed_count += 1

    print(f"✅ Removed {removed_count} files from main directory")
    return removed_count


def main():
    """Main archive and zip process."""
    print("=" * 80)
    print("ARCHIVE CURRENT ARTIFACTS AND CREATE NEW ZIP")
    print("=" * 80)

    # 1. Archive current artifacts
    archived = archive_current_artifacts()

    # 2. Create new zip
    zip_file = create_current_zip()

    # 3. Clean up old files
    removed = cleanup_old_files()

    print("\n" + "=" * 80)
    print("ARCHIVE AND ZIP COMPLETE")
    print("=" * 80)
    print(f"Files archived: {archived}")
    print(f"Files removed: {removed}")
    print(f"New zip: {zip_file.name}")
    print("\n✅ Archive and zip process completed successfully!")


if __name__ == "__main__":
    main()
