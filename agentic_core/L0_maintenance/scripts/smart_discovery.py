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
import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    SCRIPTS_DIR,
)
from agentic_core.utils.security import safe_execute

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DISCOVERY_JSON = PROJECT_ROOT / AGENT_DISCOVERY_JSON
MANIFEST_JSON = PROJECT_ROOT / AGENT_DISCOVERY_MANIFEST_JSON

# configuration
STALENESS_THRESHOLD = timedelta(hours=1)

# Shared exclude logic with discovery
ARCHIVES_DIR = "archives"
EXCLUDED_DIRS = {
    "__pycache__",
    ".git",
    ARCHIVES_DIR,
    ".sovereign_healing_backup",
    "node_modules",
    ".venv",
}


def should_exclude_path(path: Path) -> bool:
    """Return True if path should be excluded from scanning/hashing."""
    return any(excluded in path.parts for excluded in EXCLUDED_DIRS)


# Proper logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("smart_discovery")


def _scan_python_files() -> list[Path]:
    """Return list of all non-excluded .py files."""
    # Phase 6.7: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_python_files

    return list(get_python_files(PROJECT_ROOT))


def get_json_mtime() -> datetime | None:
    """Get modification time of discovery JSON."""
    if not DISCOVERY_JSON.exists():
        return None
    try:
        return datetime.fromtimestamp(DISCOVERY_JSON.stat().st_mtime)
    except OSError as e:
        log.error(f"Failed to read JSON mtime: {e}")
        return None


def get_latest_source_mtime() -> datetime:
    """Get the most recent mtime of scanned Python files."""
    files = _scan_python_files()
    latest = datetime.min
    for py_file in files:
        try:
            mtime = datetime.fromtimestamp(py_file.stat().st_mtime)
            if mtime > latest:
                latest = mtime
        except OSError:
            return datetime.now()  # Unreadable → assume changed
    return latest if latest != datetime.min else datetime.now()


def is_discovery_stale() -> tuple[bool, str]:
    """
    Check if discovery JSON needs refresh.

    Returns:
        (is_stale, reason)
    """
    if not DISCOVERY_JSON.exists():
        return True, "JSON file does not exist"

    json_mtime = get_json_mtime()
    if json_mtime is None:
        return True, "JSON mtime unreadable"

    # Check JSON age
    age = datetime.now() - json_mtime
    if age > STALENESS_THRESHOLD:
        return True, f"JSON too old ({age.total_seconds() / 3600:.1f}h > 1h)"

    # Check if any source files are newer than JSON
    latest_source = get_latest_source_mtime()
    if latest_source > json_mtime:
        return True, f"Source files modified after JSON ({latest_source} > {json_mtime})"

    return False, "JSON is fresh"


def get_changed_files() -> list[Path]:
    """Return list of changed files since last manifest (for logging only)."""
    if not MANIFEST_JSON.exists():
        return _scan_python_files()  # Force full if no manifest

    try:
        manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        file_hashes: dict = manifest.get("file_hashes", {})
    except Exception as e:
        log.warning(f"Manifest invalid ({e}) → assuming all changed")
        return _scan_python_files()

    files = _scan_python_files()
    changed = []
    for py_file in files:
        rel_path = str(py_file.relative_to(PROJECT_ROOT)).replace("\\", "/")
        try:
            current_hash = hashlib.md5(py_file.read_bytes()).hexdigest()
            if file_hashes.get(rel_path) != current_hash:
                changed.append(py_file)
        except Exception:
            changed.append(py_file)
    return changed


def run_discovery(force: bool = False) -> int:
    """
    Run discovery with smart mode selection.

    Returns exit code (0 = success)
    """
    import subprocess

    is_stale, reason = is_discovery_stale()

    if not force and not is_stale:
        log.info("JSON is fresh, skipping scan")
        log.info(f"Reason: {reason}")
        return 0

    log.info("Discovery needed")
    log.info(f"Reason: {reason}")

    changed = get_changed_files()
    log.info(f"Detected {len(changed)} changed files (informational)")

    # INCREMENTAL TRIGGER: Use incremental mode for small change sets
    use_incremental = 0 < len(changed) <= 30
    if use_incremental:
        log.info(f"Small change set ({len(changed)} files) → using --incremental mode")
    elif len(changed) > 30:
        log.info(f"Large change set ({len(changed)} files) → full scan")

    cmd = [sys.executable, str(PROJECT_ROOT / SCRIPTS_DIR / "full_agent_discovery.py")]
    if force:
        cmd.append("--force")
    if use_incremental:
        cmd.append("--incremental")

    # Robust subprocess with timeout, output capture, logging
    log.info("Launching full_agent_discovery.py...")
    start = time.time()
    try:
        result = safe_execute(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=300,  # 5 min max
            check=False,
        )
        elapsed = time.time() - start
        if result.returncode == 0:
            log.info(f"Discovery succeeded in {elapsed:.1f}s")
            return 0
        else:
            log.error(f"Discovery failed (code {result.returncode})")
            log.error(f"STDOUT: {result.stdout}")
            log.error(f"STDERR: {result.stderr}")
            return result.returncode
    except subprocess.TimeoutExpired:
        log.error("Discovery timed out after 300s")
        return 1
    except Exception as e:
        log.error(f"Failed to launch discovery: {e}")
        return 1


def ensure_fresh_discovery() -> None:
    """
    Called by AutonomyGuardianAgent before report generation.
    Auto-refreshes if stale.
    """
    is_stale, reason = is_discovery_stale()
    if is_stale:
        log.info(f"JSON stale ({reason}) → triggering discovery")
        run_discovery()
    else:
        log.info("JSON fresh → skipping discovery")


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
