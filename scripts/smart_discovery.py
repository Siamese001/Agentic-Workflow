"""
Smart Discovery Runner - Optimal execution model for agent discovery.

Features:
- Staleness detection (compare JSON mtime vs source file mtimes)
- Incremental mode detection (only flag when full scan needed)
- Pre-report freshness check for AutonomyGuardianAgent

Usage:
    python scripts/smart_discovery.py              # Auto-detect mode
    python scripts/smart_discovery.py --check      # Just check if stale
    python scripts/smart_discovery.py --force      # Force full scan
"""
import hashlib
import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DISCOVERY_JSON = PROJECT_ROOT / "agent_discovery_full.json"
MANIFEST_JSON = PROJECT_ROOT / "agent_discovery_full.manifest.json"

# Configuration
STALENESS_THRESHOLD_HOURS = 1  # Max age before auto-refresh
INCREMENTAL_THRESHOLD = 50    # Files changed threshold for incremental vs full


def get_json_mtime() -> Optional[datetime]:
    """Get modification time of discovery JSON."""
    if not DISCOVERY_JSON.exists():
        return None
    return datetime.fromtimestamp(DISCOVERY_JSON.stat().st_mtime)


def get_latest_source_mtime() -> datetime:
    """Get the most recent modification time of any source file."""
    latest = datetime.min
    for folder in ['agentic_core', 'apps_lic', 'apps_rg', 'apps_shared']:
        folder_path = PROJECT_ROOT / folder
        if folder_path.exists():
            for py_file in folder_path.rglob("*.py"):
                if '__pycache__' in str(py_file):
                    continue
                mtime = datetime.fromtimestamp(py_file.stat().st_mtime)
                if mtime > latest:
                    latest = mtime
    return latest


def is_discovery_stale() -> Tuple[bool, str]:
    """
    Check if discovery JSON needs refresh.
    
    Returns:
        (is_stale, reason)
    """
    if not DISCOVERY_JSON.exists():
        return True, "JSON file does not exist"
    
    json_mtime = get_json_mtime()
    
    # Check JSON age
    age = datetime.now() - json_mtime
    if age > timedelta(hours=STALENESS_THRESHOLD_HOURS):
        return True, f"JSON is {age.total_seconds()/3600:.1f}h old (threshold: {STALENESS_THRESHOLD_HOURS}h)"
    
    # Check if any source files are newer than JSON
    latest_source = get_latest_source_mtime()
    if latest_source > json_mtime:
        return True, f"Source files modified after JSON ({latest_source} > {json_mtime})"
    
    return False, "JSON is fresh"


def get_changed_files() -> List[Path]:
    """Get files changed since last discovery based on manifest hashes."""
    if not MANIFEST_JSON.exists():
        return []  # No manifest = can't determine changes
    
    try:
        manifest = json.loads(MANIFEST_JSON.read_text(encoding='utf-8'))
        file_hashes = manifest.get("file_hashes", {})
    except Exception:
        return []
    
    changed = []
    for folder in ['agentic_core', 'apps_lic', 'apps_rg', 'apps_shared']:
        folder_path = PROJECT_ROOT / folder
        if folder_path.exists():
            for py_file in folder_path.rglob("*.py"):
                if '__pycache__' in str(py_file):
                    continue
                rel_path = str(py_file.relative_to(PROJECT_ROOT)).replace("\\", "/")
                try:
                    current_hash = hashlib.md5(py_file.read_bytes()).hexdigest()
                    if file_hashes.get(rel_path) != current_hash:
                        changed.append(py_file)
                except Exception:
                    changed.append(py_file)  # Can't read = assume changed
    
    return changed


def run_discovery(force: bool = False) -> int:
    """
    Run discovery with smart mode selection.
    
    Returns exit code (0 = success)
    """
    import subprocess
    
    is_stale, reason = is_discovery_stale()
    
    if not force and not is_stale:
        print(f"[SMART_DISCOVERY] JSON is fresh, skipping scan")
        print(f"  Reason: {reason}")
        return 0
    
    print(f"[SMART_DISCOVERY] Running discovery...")
    print(f"  Reason: {reason}")
    
    changed = get_changed_files()
    if changed:
        print(f"  Changed files: {len(changed)}")
    
    # Always run full scan for now (incremental not yet implemented)
    cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "full_agent_discovery.py")]
    if force:
        cmd.append("--force")
    
    start = time.time()
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    elapsed = time.time() - start
    
    print(f"[SMART_DISCOVERY] Completed in {elapsed:.1f}s")
    return result.returncode


def ensure_fresh_discovery() -> None:
    """
    Called by AutonomyGuardianAgent before report generation.
    Auto-refreshes if stale.
    """
    is_stale, reason = is_discovery_stale()
    if is_stale:
        print(f"[DISCOVERY] JSON is stale ({reason}), refreshing...")
        run_discovery()
    else:
        print(f"[DISCOVERY] JSON is fresh, skipping scan")


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart Agent Discovery Runner")
    parser.add_argument("--check", action="store_true", help="Just check if stale, don't run")
    parser.add_argument("--force", action="store_true", help="Force full scan")
    parser.add_argument("--ensure", action="store_true", help="Ensure fresh (for pre-report)")
    args = parser.parse_args()
    
    if args.check:
        is_stale, reason = is_discovery_stale()
        print(f"Stale: {is_stale}")
        print(f"Reason: {reason}")
        sys.exit(1 if is_stale else 0)
    
    if args.ensure:
        ensure_fresh_discovery()
        sys.exit(0)
    
    exit_code = run_discovery(force=args.force)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
