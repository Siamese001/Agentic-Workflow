"""
Create and restore state snapshots for wave-based refactoring work.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "state_snapshot", "uwg_governed_write")
_emit_writes_through("p1", "state_snapshot", "uwg_governed_write_2")
_emit_pulls_context("p1", "state_snapshot", "context_retrieval")
_emit_pulls_context("p1", "state_snapshot", "context_retrieval_2")
emit_determinism_digest("trace_state_snapshot", "state_snapshot_dispatch")
emit_determinism_digest("trace_state_snapshot", "state_snapshot_complete")
_emit_validated_by_safety_plane("p1", "state_snapshot", "safety_validation")

STATE_SENSITIVE_LAYERS = ["L2", "L3", "L4"]


def _resolve_repo_root(explicit_root: str | None = None) -> Path:
    if explicit_root:
        return Path(explicit_root).expanduser().resolve()
    env_root = os.getenv("AGENTIC_WORKFLOW_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists():
            return candidate
    return Path.cwd().resolve()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.replace(path)


def create_snapshot_dirs(repo_root: Path, wave: int) -> tuple[Path, Path, Path]:
    data_dir = repo_root / "data"
    windsurf_dir = repo_root / ".windsurf"
    snapshots_dir = data_dir / "snapshots"
    vector_snapshots_dir = repo_root / "vector_store_snapshots"

    wave_data_dir = snapshots_dir / f"wave{wave}"
    wave_vector_dir = vector_snapshots_dir / f"wave{wave}"
    wave_memory_backup = windsurf_dir / f"memory_wave{wave}_backup.jsonl"
    wave_data_dir.mkdir(parents=True, exist_ok=True)
    wave_vector_dir.mkdir(parents=True, exist_ok=True)
    return (wave_data_dir, wave_vector_dir, wave_memory_backup)


def backup_databases(repo_root: Path, wave_data_dir: Path) -> list[str]:
    backed_up: list[str] = []
    data_dir = repo_root / "data"
    if not data_dir.exists():
        print(f"  [SKIP] Data directory does not exist: {data_dir}")
        return backed_up

    for db_file in sorted(data_dir.glob("*.db")):
        shutil.copy2(db_file, wave_data_dir / db_file.name)
        backed_up.append(db_file.name)
        print(f"  [OK] Backed up: {db_file.name}")

    if not backed_up:
        print("  [INFO] No .db files found to backup")
    return backed_up


def backup_vector_store(repo_root: Path, wave_vector_dir: Path) -> bool:
    vector_store_dir = repo_root / "vector_store"
    if not vector_store_dir.exists():
        print(f"  [SKIP] Vector store does not exist: {vector_store_dir}")
        return False
    if wave_vector_dir.exists():
        shutil.rmtree(wave_vector_dir)
    shutil.copytree(vector_store_dir, wave_vector_dir)
    print(f"  [OK] Backed up vector store to: {wave_vector_dir}")
    return True


def backup_memory(repo_root: Path, wave_memory_backup: Path) -> bool:
    memory_file = repo_root / ".windsurf" / "memory.jsonl"
    if not memory_file.exists():
        print(f"  [SKIP] Memory file does not exist: {memory_file}")
        return False
    shutil.copy2(memory_file, wave_memory_backup)
    print(f"  [OK] Backed up memory to: {wave_memory_backup}")
    return True


def create_manifest(
    repo_root: Path,
    wave: int,
    agent: str,
    wave_data_dir: Path,
    backed_up_dbs: list[str],
    vector_backed_up: bool,
    memory_backed_up: bool,
) -> Path:
    manifest = {
        "wave": wave,
        "agent": agent,
        "timestamp": _utc_now_iso(),
        "backups": {
            "databases": backed_up_dbs,
            "vector_store": vector_backed_up,
            "memory": memory_backed_up,
        },
        "restore_command": f"python scripts/state_snapshot.py --restore --wave {wave} --execute-restore",
        "repo_root": str(repo_root),
    }
    manifest_path = wave_data_dir / "snapshot_manifest.json"
    _atomic_write(manifest_path, json.dumps(manifest, indent=2) + "\n")
    print(f"  [OK] Created manifest: {manifest_path}")
    return manifest_path


def take_snapshot(repo_root: Path, wave: int, agent: str) -> bool:
    print(f"\n{'=' * 60}")
    print(f"STATE SNAPSHOT - Wave {wave} - {agent}")
    print(f"{'=' * 60}")
    print(f"Timestamp: {_utc_now_iso()}\n")

    wave_data_dir, wave_vector_dir, wave_memory_backup = create_snapshot_dirs(repo_root, wave)

    print("[1/4] Backing up databases...")
    backed_up_dbs = backup_databases(repo_root, wave_data_dir)

    print("\n[2/4] Backing up vector store...")
    vector_backed_up = backup_vector_store(repo_root, wave_vector_dir)

    print("\n[3/4] Backing up Windsurf memory...")
    memory_backed_up = backup_memory(repo_root, wave_memory_backup)

    print("\n[4/4] Creating manifest...")
    create_manifest(repo_root, wave, agent, wave_data_dir, backed_up_dbs, vector_backed_up, memory_backed_up)

    print(f"\n{'=' * 60}")
    print("SNAPSHOT COMPLETE")
    print(f"{'=' * 60}")
    print(f"  Data snapshots:   {wave_data_dir}")
    print(f"  Vector snapshots: {wave_vector_dir}")
    print(f"  Memory backup:    {wave_memory_backup}")
    return True


def restore_snapshot(repo_root: Path, wave: int, execute_restore: bool = False) -> bool:
    data_dir = repo_root / "data"
    vector_store_dir = repo_root / "vector_store"
    windsurf_dir = repo_root / ".windsurf"

    wave_data_dir = data_dir / "snapshots" / f"wave{wave}"
    wave_vector_dir = repo_root / "vector_store_snapshots" / f"wave{wave}"
    wave_memory_backup = windsurf_dir / f"memory_wave{wave}_backup.jsonl"
    manifest_path = wave_data_dir / "snapshot_manifest.json"

    print(f"\n{'=' * 60}")
    print(f"STATE RESTORE - Wave {wave}")
    print(f"{'=' * 60}")
    print(f"Timestamp: {_utc_now_iso()}\n")

    if not manifest_path.exists():
        print(f"[ERROR] No snapshot found for Wave {wave}")
        print(f"  Expected manifest at: {manifest_path}")
        return False

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    print(f"Restoring snapshot from: {manifest['timestamp']}")
    print(f"Original agent: {manifest['agent']}")
    if not execute_restore:
        print("[DRY RUN] Restore plan only. Re-run with --execute-restore to apply changes.\n")

    print("[1/3] Restoring databases...")
    for db_name in manifest["backups"]["databases"]:
        src = wave_data_dir / db_name
        dest = data_dir / db_name
        if src.exists():
            print(f"  [{'OK' if execute_restore else 'PLAN'}] Restore {db_name}")
            if execute_restore:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
        else:
            print(f"  [WARN] Backup not found: {db_name}")

    print("\n[2/3] Restoring vector store...")
    if manifest["backups"]["vector_store"] and wave_vector_dir.exists():
        print(f"  [{'OK' if execute_restore else 'PLAN'}] Restore vector store from {wave_vector_dir}")
        if execute_restore:
            if vector_store_dir.exists():
                shutil.rmtree(vector_store_dir)
            shutil.copytree(wave_vector_dir, vector_store_dir)
    else:
        print("  [SKIP] No vector store backup to restore")

    print("\n[3/3] Restoring Windsurf memory...")
    memory_file = windsurf_dir / "memory.jsonl"
    if manifest["backups"]["memory"] and wave_memory_backup.exists():
        print(f"  [{'OK' if execute_restore else 'PLAN'}] Restore memory from {wave_memory_backup}")
        if execute_restore:
            if memory_file.exists():
                memory_file.unlink()
            shutil.copy2(wave_memory_backup, memory_file)
    else:
        print("  [SKIP] No memory backup to restore")

    print(f"\n{'=' * 60}")
    print("RESTORE COMPLETE" if execute_restore else "RESTORE PLAN COMPLETE")
    print(f"{'=' * 60}")
    return True


def verify_snapshot(repo_root: Path, wave: int) -> bool:
    manifest_path = repo_root / "data" / "snapshots" / f"wave{wave}" / "snapshot_manifest.json"
    if not manifest_path.exists():
        return False
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return "wave" in manifest and "timestamp" in manifest and "backups" in manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="State Snapshot Tool for zero-loss refactoring.")
    parser.add_argument("--repo-root", help="Override automatic repository root detection.")
    parser.add_argument("--wave", type=int, required=True, help="Wave number (for example 2, 3, or 4).")
    parser.add_argument(
        "--agent", type=str, default="Unknown", help="Agent being modified (for the manifest)."
    )
    parser.add_argument(
        "--restore", action="store_true", help="Restore from snapshot instead of creating one."
    )
    parser.add_argument("--execute-restore", action="store_true", help="Actually apply restore operations.")
    parser.add_argument(
        "--verify", action="store_true", help="Verify snapshot exists without modifying anything."
    )
    args = parser.parse_args(argv)

    repo_root = _resolve_repo_root(args.repo_root)

    if args.verify:
        exists = verify_snapshot(repo_root, args.wave)
        print(f"Snapshot for wave {args.wave}: {'FOUND' if exists else 'MISSING'}")
        return 0 if exists else 1

    if args.restore:
        success = restore_snapshot(repo_root, args.wave, execute_restore=args.execute_restore)
        return 0 if success else 1

    success = take_snapshot(repo_root, args.wave, args.agent)
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
