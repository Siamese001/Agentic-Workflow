"""Zip archive creation and file compression for ADG artifact retention."""

from __future__ import annotations

import gzip
import shutil
import zipfile
from pathlib import Path


def _archive_zip_files(zip_files: list[Path], archive_month_dir: Path) -> tuple[int, int, int]:
    """Archive zip files with compression.

    Returns:
        Tuple of (archived_count, bytes_original, bytes_archived)
    """
    archived_count = 0
    bytes_original = 0
    bytes_archived = 0

    for zip_file in zip_files:
        if not zip_file.exists():
            continue

        try:
            original_size = zip_file.stat().st_size
            bytes_original += original_size

            archive_path = archive_month_dir / f"{zip_file.name}.gz"

            with open(zip_file, "rb") as f_in:
                with gzip.open(archive_path, "wb", compresslevel=9) as f_out:
                    shutil.copyfileobj(f_in, f_out)

            if archive_path.exists() and archive_path.stat().st_size > 0:
                bytes_archived += archive_path.stat().st_size
                zip_file.unlink()
                archived_count += 1
            else:
                if archive_path.exists():
                    archive_path.unlink()

        except OSError as e:
            print(f"[ADG] Archive: error archiving {zip_file.name}: {e}")
            continue

    return archived_count, bytes_original, bytes_archived


def _archive_individual_files(files: list[Path], archive_month_dir: Path) -> tuple[int, int, int]:
    """Archive individual files (legacy fallback for orphaned runs).

    Returns:
        Tuple of (archived_count, bytes_original, bytes_archived)
    """
    archived_count = 0
    bytes_original = 0
    bytes_archived = 0

    for file_path in files:
        if not file_path.exists():
            continue

        try:
            original_size = file_path.stat().st_size
            bytes_original += original_size

            archive_path = archive_month_dir / f"{file_path.name}.gz"

            with open(file_path, "rb") as f_in:
                with gzip.open(archive_path, "wb", compresslevel=9) as f_out:
                    shutil.copyfileobj(f_in, f_out)

            if archive_path.exists() and archive_path.stat().st_size > 0:
                bytes_archived += archive_path.stat().st_size
                file_path.unlink()
                archived_count += 1
            else:
                if archive_path.exists():
                    archive_path.unlink()

        except OSError as e:
            print(f"[ADG] Archive: error archiving {file_path.name}: {e}")
            continue

    return archived_count, bytes_original, bytes_archived


def _create_zip_archive(adg_dir: Path, ts: str, artifact_paths: list[Path]) -> Path:
    """Create a zip archive of all static ADG artifacts for the current run.

    Args:
        adg_dir: ADG artifacts directory
        ts: Timestamp string for naming
        artifact_paths: List of artifact file paths to include

    Returns:
        Path to the created zip file

    Raises:
        RuntimeError: If zip creation fails
    """
    zip_path = adg_dir / f"adg_run_{ts}.zip"

    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
            missing_artifacts = []
            for artifact_path in artifact_paths:
                if artifact_path.exists():
                    zf.write(artifact_path, f"adg/{artifact_path.name}")
                else:
                    missing_artifacts.append(artifact_path.name)
                    print(f"[ADG] WARNING: Missing artifact {artifact_path.name}")

            if missing_artifacts:
                print(f"[ADG] WARNING: Zip created with missing artifacts: {missing_artifacts}")

    except (ValueError, TypeError, RuntimeError) as e:
        print(f"[ADG] CRITICAL: Zip creation failed: {e}")
        if zip_path.exists():
            zip_path.unlink()
        raise RuntimeError(f"Zip creation failed for {ts}: {e}") from e

    if not zip_path.exists():
        raise RuntimeError(f"Zip file not created after successful completion for {ts}")

    zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
    report_count = len([p for p in artifact_paths if "report" in p.name.lower()])
    adg_count = len(artifact_paths) - report_count
    print(
        f"[ADG] Zip archive created: {zip_path.name} ({zip_size_mb:.1f} MB, {adg_count} ADG + {report_count} reports)",
    )

    return zip_path
