"""File locking utilities for ADG generation (Windows-aware)."""

from __future__ import annotations

import gc
import os
import sqlite3
import sys
import time
from pathlib import Path


def _discover_repo_root(start: Path) -> Path:
    """Best-effort repository root discovery for direct script and package execution."""
    for candidate in (start, *start.parents):
        if (candidate / "agentic_core").exists() or (candidate / ".git").exists():
            return candidate
        if candidate.name == "tools" and (candidate / "generate").exists():
            return candidate.parent
    return start.parents[3] if len(start.parents) > 3 else start.parent


ROOT = _discover_repo_root(Path(__file__).resolve().parent)


def _is_file_locked(filepath: Path) -> bool:
    """Check if a file can be deleted (Windows only).

    Tests DELETE access rather than GENERIC_WRITE.  SQLite WAL-mode opens the
    main database without FILE_SHARE_DELETE, so any opener lacking that flag
    will block a DELETE-access request — which is exactly what unlink() needs.
    GENERIC_WRITE + FILE_SHARE_READ|WRITE succeeds even on an open SQLite file
    because share modes are compatible; DELETE access correctly fails.
    Returns True if the file cannot be deleted (locked or inaccessible).
    """
    if os.name != "nt":
        return False
    try:
        import ctypes

        DELETE_ACCESS = 0x00010000
        FILE_SHARE_READ = 0x00000001
        FILE_SHARE_WRITE = 0x00000002
        OPEN_EXISTING = 3
        handle = ctypes.windll.kernel32.CreateFileW(
            str(filepath),
            DELETE_ACCESS,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            None,
            OPEN_EXISTING,
            0,
            None,
        )
        if handle == ctypes.c_void_p(-1).value:
            return True  # Delete access denied — another opener lacks FILE_SHARE_DELETE
        ctypes.windll.kernel32.CloseHandle(handle)
        return False
    except (
        ImportError,
        AttributeError,
        OSError,
    ):  # guardian: allow-broad-exception -- Windows API best-effort: file lock check may fail unpredictably, treat failure as locked
        return True


def _perform_wal_checkpoint(adg_dir: Path | None = None) -> None:
    """Perform best-effort WAL checkpoint on prior SQLite files."""
    print("[ADG] Pre-flight: attempting best-effort SQLite WAL checkpoint...")
    try:
        adg_dir = adg_dir if adg_dir is not None else ROOT / "artifacts" / "adg"
        if not adg_dir.exists():
            return
        sqlite_files = list(adg_dir.glob("adg_indexed_*.sqlite"))

        for sqlite_file in sqlite_files:
            try:
                with sqlite3.connect(str(sqlite_file)) as temp_conn:
                    temp_conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                print(f"[ADG] WAL checkpoint attempted for: {sqlite_file.name}")
            except sqlite3.Error as exc:  # guardian: allow-broad-exception -- best-effort cleanup: WAL checkpoint failure during lock check
                print(f"[ADG] WAL checkpoint skipped for {sqlite_file.name}: {exc}")

        gc.collect()
        time.sleep(0.5)
    except OSError as exc:  # guardian: allow-silent-swallow -- best-effort lock check: failure caught by subsequent pre-generation check
        print(f"[ADG] Warning: unable to enumerate SQLite artifacts for WAL checkpoint: {exc}")


def _check_locked_files(adg_dir: Path | None = None) -> None:
    """Check for locked SQLite files and abort if found."""
    print("[ADG] Checking for remaining locked SQLite files...")
    try:
        adg_dir = adg_dir if adg_dir is not None else ROOT / "artifacts" / "adg"
        if not adg_dir.exists():
            print("[ADG] No ADG artifact directory found; skipping lock check")
            return
        sqlite_files = list(adg_dir.glob("adg_indexed_*.sqlite")) + list(adg_dir.glob("adg_graph_*.sqlite"))
        locked_count = 0
        locked_files_list = []

        for sqlite_file in sqlite_files:
            if _is_file_locked(sqlite_file):
                locked_count += 1
                locked_files_list.append(sqlite_file.name)
                print(f"[ADG] Found locked SQLite file: {sqlite_file.name}")

        if locked_count > 0:
            print(f"\n[ERROR] {locked_count} SQLite file(s) are locked by MCP server process")
            print(f"[ERROR] Locked files: {', '.join(locked_files_list)}")
            print("[ERROR]")
            print("[ERROR] The MCP server (adg_sqlite) has these files open.")
            print("[ERROR] Automatic lock release cannot close connections from another process.")
            print("[ERROR]")
            print("[ERROR] REQUIRED ACTION: call adg_close_connections() MCP tool")
            print("[ERROR] Fallback: restart legacy editor if MCP close tool unavailable")
            print("[ERROR]")
            print("[ERROR] ADG generation aborted - file locks prevent archive cleanup")
            sys.exit(1)
        else:
            print("[ADG] No locked SQLite files found - proceeding with generation")
    except Exception as e:  # guardian: allow-broad-exception -- non-critical: locked file check failure should not block ADG generation
        print(f"[WARNING] Could not check for locked SQLite files: {e}")
        print("[WARNING]   Proceeding with ADG generation...")
