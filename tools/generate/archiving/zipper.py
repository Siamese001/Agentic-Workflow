"""Zip archive creation and file compression for ADG artifact retention."""

from __future__ import annotations

import gzip
import os
import shutil
import zipfile
from pathlib import Path

from tqdm import tqdm


def _safe_unlink(path: Path) -> None:
    """Best-effort unlink for temp files and archived sources."""
    try:
        if path.exists():
            path.unlink()
    except OSError:
        pass


def _replace_atomically(temp_path: Path, final_path: Path) -> None:
    """Atomically replace final_path with temp_path on the same filesystem."""
    os.replace(temp_path, final_path)


def _archive_zip_files(zip_files: list[Path], archive_month_dir: Path) -> tuple[int, int, int]:
    """Archive zip files with compression.

    Returns:
        Tuple of (archived_count, bytes_original, bytes_archived)
    """
    archived_count = 0
    bytes_original = 0
    bytes_archived = 0

    for zip_file in tqdm(zip_files, desc="[ADG] Compressing zip archives", unit="file"):
        if not zip_file.exists():
            continue

        try:
            original_size = zip_file.stat().st_size
            bytes_original += original_size

            archive_path = archive_month_dir / f"{zip_file.name}.gz"
            temp_archive_path = archive_path.with_suffix(f"{archive_path.suffix}.tmp")

            with zip_file.open("rb") as f_in, gzip.open(temp_archive_path, "wb", compresslevel=9) as f_out:
                shutil.copyfileobj(f_in, f_out)

            if temp_archive_path.exists() and temp_archive_path.stat().st_size > 0:
                _replace_atomically(temp_archive_path, archive_path)
                bytes_archived += archive_path.stat().st_size
                _safe_unlink(zip_file)
                archived_count += 1
            elif temp_archive_path.exists():
                _safe_unlink(temp_archive_path)

        except OSError as e:
            if temp_archive_path.exists():
                _safe_unlink(temp_archive_path)
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

    for file_path in tqdm(files, desc="[ADG] Compressing individual files", unit="file"):
        if not file_path.exists():
            continue

        try:
            original_size = file_path.stat().st_size
            bytes_original += original_size

            archive_path = archive_month_dir / f"{file_path.name}.gz"
            temp_archive_path = archive_path.with_suffix(f"{archive_path.suffix}.tmp")

            with file_path.open("rb") as f_in, gzip.open(temp_archive_path, "wb", compresslevel=9) as f_out:
                shutil.copyfileobj(f_in, f_out)

            if temp_archive_path.exists() and temp_archive_path.stat().st_size > 0:
                _replace_atomically(temp_archive_path, archive_path)
                bytes_archived += archive_path.stat().st_size
                _safe_unlink(file_path)
                archived_count += 1
            elif temp_archive_path.exists():
                _safe_unlink(temp_archive_path)

        except OSError as e:
            if temp_archive_path.exists():
                _safe_unlink(temp_archive_path)
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

    temp_zip_path = zip_path.with_suffix(".zip.tmp")

    try:
        unique_artifact_paths = list(dict.fromkeys(artifact_paths))
        with zipfile.ZipFile(temp_zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
            missing_artifacts = []
            for artifact_path in unique_artifact_paths:
                if artifact_path.exists():
                    zf.write(artifact_path, f"adg/{artifact_path.name}")
                else:
                    missing_artifacts.append(artifact_path.name)
                    print(f"[ADG] WARNING: Missing artifact {artifact_path.name}")

            if missing_artifacts:
                print(f"[ADG] WARNING: Zip created with missing artifacts: {missing_artifacts}")

        _replace_atomically(temp_zip_path, zip_path)

    except (OSError, ValueError, zipfile.BadZipFile) as e:
        print(f"[ADG] CRITICAL: Zip creation failed: {e}")
        if temp_zip_path.exists():
            _safe_unlink(temp_zip_path)
        if zip_path.exists():
            _safe_unlink(zip_path)
        raise RuntimeError(f"Zip creation failed for {ts}: {e}") from e

    if not zip_path.exists():
        raise RuntimeError(f"Zip file not created after successful completion for {ts}")

    zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
    report_count = len([p for p in unique_artifact_paths if "report" in p.name.lower()])
    adg_count = len(unique_artifact_paths) - report_count
    print(
        f"[ADG] Zip archive created: {zip_path.name} ({zip_size_mb:.1f} MB, {adg_count} ADG + {report_count} reports)",
    )

    return zip_path
