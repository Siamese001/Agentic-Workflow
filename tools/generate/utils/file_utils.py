"""File locking utilities for ADG generation (Windows-aware)."""

from __future__ import annotations

import gc
import os
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _is_file_locked(filepath: Path) -> bool:
    """Check if file is locked (Windows only).

    Returns True if file cannot be opened exclusively.
    """
    if os.name != "nt":
        return False
    try:
        import ctypes

        GENERIC_WRITE = 0x40000000
        FILE_SHARE_READ = 0x00000001
        FILE_SHARE_WRITE = 0x00000002
        OPEN_EXISTING = 3
        handle = ctypes.windll.kernel32.CreateFileW(
            str(filepath),
            GENERIC_WRITE,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            None,
            OPEN_EXISTING,
            0,
            None,
        )
        if handle == ctypes.c_void_p(-1).value:
            return True  # Another process holds an exclusive write lock
        ctypes.windll.kernel32.CloseHandle(handle)
        return False
    except Exception:  # guardian: allow-broad-exception -- Windows API best-effort: file lock check may fail unpredictably, treat failure as locked
        return True


def _perform_wal_checkpoint(adg_dir: Path | None = None) -> None:
    """Perform best-effort WAL checkpoint on prior SQLite files."""
    print("[ADG] Pre-flight: attempting best-effort SQLite WAL checkpoint...")
    try:
        adg_dir = adg_dir if adg_dir is not None else ROOT / "artifacts" / "adg"
        sqlite_files = list(adg_dir.glob("adg_indexed_*.sqlite"))

        for sqlite_file in sqlite_files:
            try:
                temp_conn = sqlite3.connect(str(sqlite_file))
                temp_conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                temp_conn.close()
                del temp_conn
                print(f"[ADG] WAL checkpoint attempted for: {sqlite_file.name}")
            except Exception:  # guardian: allow-broad-exception -- best-effort cleanup: WAL checkpoint failure during lock check
                pass

        gc.collect()
        time.sleep(0.5)
    except Exception:  # guardian: allow-silent-swallow -- best-effort lock check: failure caught by subsequent pre-generation check
        pass


def _check_locked_files(adg_dir: Path | None = None) -> None:
    """Check for locked SQLite files and abort if found."""
    print("[ADG] Checking for remaining locked SQLite files...")
    try:
        adg_dir = adg_dir if adg_dir is not None else ROOT / "artifacts" / "adg"
        sqlite_files = list(adg_dir.glob("adg_indexed_*.sqlite"))
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
            print("[ERROR] Fallback: restart Windsurf if MCP close tool unavailable")
            print("[ERROR]")
            print("[ERROR] ADG generation aborted - file locks prevent archive cleanup")
            sys.exit(1)
        else:
            print("[ADG] No locked SQLite files found - proceeding with generation")
    except Exception as e:  # guardian: allow-broad-exception -- non-critical: locked file check failure should not block ADG generation
        print(f"[WARNING] Could not check for locked SQLite files: {e}")
        print("[WARNING]   Proceeding with ADG generation...")
