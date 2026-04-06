"""
State Snapshot Script for V10 Zero-Loss Refactoring.

Implements the State Snapshot Rule from the V10 Implementation Plan.
Creates backups of databases, vector stores, and memory files before
modifying agents in L2 (Execution), L3 (Orchestration), or L4 (State).

Usage:
    python scripts/state_snapshot.py --wave 2 --agent DomainPlannerAgent
    python scripts/state_snapshot.py --wave 3 --agent CodeHealerAgent
    python scripts/state_snapshot.py --restore --wave 2  # Restore from snapshot

v3.1: Created as part of Wave 2 Pre-Flight Checks.
"""
import argparse
import json
import shutil
import sys
from datetime import datetime
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
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
VECTOR_STORE_DIR = PROJECT_ROOT / 'vector_store'
WINDSURF_DIR = PROJECT_ROOT / '.windsurf'
SNAPSHOTS_DIR = DATA_DIR / 'snapshots'
VECTOR_SNAPSHOTS_DIR = PROJECT_ROOT / 'vector_store_snapshots'
STATE_SENSITIVE_LAYERS = ['L2', 'L3', 'L4']

def create_snapshot_dirs(wave: int) -> tuple[Path, Path, Path]:
    """Create snapshot directories for a wave."""
    wave_data_dir = SNAPSHOTS_DIR / f'wave{wave}'
    wave_vector_dir = VECTOR_SNAPSHOTS_DIR / f'wave{wave}'
    wave_memory_backup = WINDSURF_DIR / f'memory_wave{wave}_backup.jsonl'
    wave_data_dir.mkdir(parents=True, exist_ok=True)
    wave_vector_dir.mkdir(parents=True, exist_ok=True)
    return (wave_data_dir, wave_vector_dir, wave_memory_backup)

def backup_databases(wave_data_dir: Path) -> list[str]:
    """Backup all .db files from data directory."""
    backed_up = []
    if not DATA_DIR.exists():
        print(f'  [SKIP] Data directory does not exist: {DATA_DIR}')
        return backed_up
    for db_file in DATA_DIR.glob('*.db'):
        dest = wave_data_dir / db_file.name
        shutil.copy2(db_file, dest)
        backed_up.append(str(db_file.name))
        print(f'  [OK] Backed up: {db_file.name}')
    if not backed_up:
        print('  [INFO] No .db files found to backup')
    return backed_up

def backup_vector_store(wave_vector_dir: Path) -> bool:
    """Backup vector store directory."""
    if not VECTOR_STORE_DIR.exists():
        print(f'  [SKIP] Vector store does not exist: {VECTOR_STORE_DIR}')
        return False
    if wave_vector_dir.exists():
        shutil.rmtree(wave_vector_dir)
    shutil.copytree(VECTOR_STORE_DIR, wave_vector_dir)
    print(f'  [OK] Backed up vector store to: {wave_vector_dir}')
    return True

def backup_memory(wave_memory_backup: Path) -> bool:
    """Backup Windsurf memory file."""
    memory_file = WINDSURF_DIR / 'memory.jsonl'
    if not memory_file.exists():
        print(f'  [SKIP] Memory file does not exist: {memory_file}')
        return False
    shutil.copy2(memory_file, wave_memory_backup)
    print(f'  [OK] Backed up memory to: {wave_memory_backup}')
    return True

def create_manifest(wave: int, agent: str, wave_data_dir: Path, backed_up_dbs: list[str], vector_backed_up: bool, memory_backed_up: bool) -> None:
    """Create a manifest file documenting the snapshot."""
    manifest = {'wave': wave, 'agent': agent, 'timestamp': datetime.utcnow().isoformat() + 'Z', 'backups': {'databases': backed_up_dbs, 'vector_store': vector_backed_up, 'memory': memory_backed_up}, 'restore_command': f'python scripts/state_snapshot.py --restore --wave {wave}'}
    manifest_path = wave_data_dir / 'snapshot_manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f'  [OK] Created manifest: {manifest_path}')

def take_snapshot(wave: int, agent: str) -> bool:
    """
    Take a complete state snapshot for a wave.

    Returns True if snapshot was successful.
    """
    print(f"\n{'=' * 60}")
    print(f'STATE SNAPSHOT - Wave {wave} - {agent}')
    print(f"{'=' * 60}")
    print(f'Timestamp: {datetime.utcnow().isoformat()}Z')
    print()
    wave_data_dir, wave_vector_dir, wave_memory_backup = create_snapshot_dirs(wave)
    print('[1/3] Backing up databases...')
    backed_up_dbs = backup_databases(wave_data_dir)
    print('\n[2/3] Backing up vector store...')
    vector_backed_up = backup_vector_store(wave_vector_dir)
    print('\n[3/3] Backing up Windsurf memory...')
    memory_backed_up = backup_memory(wave_memory_backup)
    print('\n[4/4] Creating manifest...')
    create_manifest(wave, agent, wave_data_dir, backed_up_dbs, vector_backed_up, memory_backed_up)
    print(f"\n{'=' * 60}")
    print('SNAPSHOT COMPLETE')
    print(f"{'=' * 60}")
    print(f'  Data snapshots: {wave_data_dir}')
    print(f'  Vector snapshots: {wave_vector_dir}')
    print(f'  Memory backup: {wave_memory_backup}')
    print()
    print('To restore this snapshot:')
    print(f'  python scripts/state_snapshot.py --restore --wave {wave}')
    print()
    return True

def restore_snapshot(wave: int) -> bool:
    """
    Restore state from a wave snapshot.

    Returns True if restore was successful.
    """
    print(f"\n{'=' * 60}")
    print(f'STATE RESTORE - Wave {wave}')
    print(f"{'=' * 60}")
    print(f'Timestamp: {datetime.utcnow().isoformat()}Z')
    print()
    wave_data_dir = SNAPSHOTS_DIR / f'wave{wave}'
    wave_vector_dir = VECTOR_SNAPSHOTS_DIR / f'wave{wave}'
    wave_memory_backup = WINDSURF_DIR / f'memory_wave{wave}_backup.jsonl'
    manifest_path = wave_data_dir / 'snapshot_manifest.json'
    if not manifest_path.exists():
        print(f'[ERROR] No snapshot found for Wave {wave}')
        print(f'  Expected manifest at: {manifest_path}')
        return False
    manifest = json.loads(manifest_path.read_text())
    print(f"Restoring snapshot from: {manifest['timestamp']}")
    print(f"Original agent: {manifest['agent']}")
    print()
    print('[1/3] Restoring databases...')
    for db_name in manifest['backups']['databases']:
        src = wave_data_dir / db_name
        dest = DATA_DIR / db_name
        if src.exists():
            shutil.copy2(src, dest)
            print(f'  [OK] Restored: {db_name}')
        else:
            print(f'  [WARN] Backup not found: {db_name}')
    print('\n[2/3] Restoring vector store...')
    if manifest['backups']['vector_store'] and wave_vector_dir.exists():
        if VECTOR_STORE_DIR.exists():
            shutil.rmtree(VECTOR_STORE_DIR)
        shutil.copytree(wave_vector_dir, VECTOR_STORE_DIR)
        print('  [OK] Restored vector store')
    else:
        print('  [SKIP] No vector store backup to restore')
    print('\n[3/3] Restoring Windsurf memory...')
    memory_file = WINDSURF_DIR / 'memory.jsonl'
    if manifest['backups']['memory'] and wave_memory_backup.exists():
        if memory_file.exists():
            memory_file.unlink()
        shutil.copy2(wave_memory_backup, memory_file)
        print('  [OK] Restored memory')
    else:
        print('  [SKIP] No memory backup to restore')
    print(f"\n{'=' * 60}")
    print('RESTORE COMPLETE')
    print(f"{'=' * 60}")
    print()
    return True

def verify_snapshot(wave: int) -> bool:
    """Verify that a snapshot exists and is valid."""
    wave_data_dir = SNAPSHOTS_DIR / f'wave{wave}'
    manifest_path = wave_data_dir / 'snapshot_manifest.json'
    if not manifest_path.exists():
        return False
    try:
        manifest = json.loads(manifest_path.read_text())
        return 'wave' in manifest and 'timestamp' in manifest
    except (json.JSONDecodeError, KeyError):
        return False

def main():
    parser = argparse.ArgumentParser(description='State Snapshot Tool for V10 Zero-Loss Refactoring')
    parser.add_argument('--wave', type=int, required=True, help='Wave number (e.g., 2, 3, 4)')
    parser.add_argument('--agent', type=str, default='Unknown', help='Agent being modified (for manifest)')
    parser.add_argument('--restore', action='store_true', help='Restore from snapshot instead of creating one')
    parser.add_argument('--verify', action='store_true', help='Verify snapshot exists without modifying anything')
    args = parser.parse_args()
    if args.verify:
        exists = verify_snapshot(args.wave)
        if exists:
            print(f'[OK] Snapshot exists for Wave {args.wave}')
            sys.exit(0)
        else:
            print(f'[ERROR] No valid snapshot for Wave {args.wave}')
            sys.exit(1)
    if args.restore:
        success = restore_snapshot(args.wave)
    else:
        success = take_snapshot(args.wave, args.agent)
    sys.exit(0 if success else 1)
if __name__ == '__main__':
    main()
