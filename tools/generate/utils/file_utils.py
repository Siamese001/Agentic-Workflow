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

    Tests DELETE access rather than GENERIC_WRITE. SQLite WAL-mode opens the
    main database without FILE_SHARE_DELETE, so any opener lacking that flag
    blocks the DELETE-access request that unlink() needs.
    """

    if os.name != "nt":
        return False
    try:
        import ctypes

        delete_access = 0x00010000
        file_share_read = 0x00000001
        file_share_write = 0x00000002
        open_existing = 3
        handle = ctypes.windll.kernel32.CreateFileW(
            str(filepath),
            delete_access,
            file_share_read | file_share_write,
            None,
            open_existing,
            0,
            None,
        )
        if handle == ctypes.c_void_p(-1).value:
            return True
        ctypes.windll.kernel32.CloseHandle(handle)
        return False
    except (
        ImportError,
        AttributeError,
        OSError,
    ):  # guardian: allow-broad-exception -- Windows API best-effort; treat uncertainty as locked
        return True


def _perform_wal_checkpoint(target: Path | None = None) -> None:
    """Perform best-effort WAL checkpoints for one SQLite file or a directory.

    Historically this helper accepted a directory but the MV retry path passed
    the concrete ``adg_indexed_*.sqlite`` file. The old implementation called
    ``is_dir()`` implicitly via ``glob`` and checkpointed nothing. Supporting
    both shapes makes lock recovery deterministic.
    """

    print("[ADG] Pre-flight: attempting best-effort SQLite WAL checkpoint...")
    try:
        target = target if target is not None else ROOT / "artifacts" / "adg"
        target = target.expanduser().resolve()
        if target.is_file():
            sqlite_files = [target] if target.suffix.lower() in {".sqlite", ".db"} else []
        elif target.is_dir():
            sqlite_files = sorted(
                {
                    *target.glob("adg_indexed_*.sqlite"),
                    *target.glob("adg_graph_*.sqlite"),
                }
            )
        else:
            return

        for sqlite_file in sqlite_files:
            try:
                with sqlite3.connect(str(sqlite_file), timeout=5.0) as temp_conn:
                    temp_conn.execute("PRAGMA busy_timeout = 5000")
                    result = temp_conn.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
                busy, log_frames, checkpointed_frames = result or (0, 0, 0)
                if busy:
                    print(
                        "[ADG] WAL checkpoint busy for "
                        f"{sqlite_file.name}: log={log_frames}, checkpointed={checkpointed_frames}"
                    )
                else:
                    print(
                        "[ADG] WAL checkpoint complete for "
                        f"{sqlite_file.name}: frames={checkpointed_frames}"
                    )
            except sqlite3.Error as exc:  # guardian: allow-broad-exception -- best-effort cleanup before bounded retry
                print(f"[ADG] WAL checkpoint skipped for {sqlite_file.name}: {exc}")

        gc.collect()
        time.sleep(0.5)
    except OSError as exc:  # guardian: allow-silent-swallow -- subsequent lock check remains authoritative
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
    except Exception as exc:  # guardian: allow-broad-exception -- non-critical lock probe
        print(f"[WARNING] Could not check for locked SQLite files: {exc}")
        print("[WARNING]   Proceeding with ADG generation...")
