#!/usr/bin/env python3
"""
Windsurf Log Append Utility

Appends new batch entries to windsurf_log.json for real-time dashboard updates.

Usage:
    # After completing a batch:
    python scripts/append_windsurf_log.py --healing 74 --healed 178 --total 241 --commits 5 --mcp 17

    # Or import and use programmatically:
    from append_windsurf_log import append_batch
    append_batch(healing_pct=74, healed=178, total_core=241, commits=5, mcp_hardened=17)
"""
import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

# Path to log file (project root)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = PROJECT_ROOT / 'windsurf_log.json'


def load_log() -> list:
    """Load existing log entries."""
    if LOG_PATH.exists():
        try:
            with open(LOG_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading log: {e}")
            return []
    return []


def save_log(log: list) -> None:
    """Save log entries to file."""
    with open(LOG_PATH, 'w') as f:
        json.dump(log, f, indent=2)
    print(f"[OK] Log saved to {LOG_PATH}")


def append_batch(
    healing_pct: float,
    healed: int,
    total_core: int,
    commits: int,
    batch_name: Optional[str] = None,
    mcp_hardened: int = 0,
    regressions: int = 0
) -> dict:
    """
    Append a new batch entry to the windsurf log.
    
    Args:
        healing_pct: Core healing percentage
        healed: Number of healed agents
        total_core: Total core agents
        commits: Number of commits in this batch
        batch_name: Optional batch name (auto-generated if None)
        mcp_hardened: Number of MCP hardened agents
        regressions: Number of regressions detected
    
    Returns:
        The new entry that was appended
    """
    log = load_log()
    
    # Auto-generate batch name if not provided
    if batch_name is None:
        batch_num = len(log) + 1
        batch_name = f"Batch {batch_num}"
    
    new_entry = {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "batch": batch_name,
        "healing_core_pct": healing_pct,
        "healed_agents": healed,
        "total_core": total_core,
        "commits": commits,
        "mcp_hardened": mcp_hardened,
        "regressions": regressions
    }
    
    log.append(new_entry)
    save_log(log)
    
    print(f"\n[NEW ENTRY]")
    print(f"  Batch: {batch_name}")
    print(f"  Healing: {healing_pct}% ({healed}/{total_core})")
    print(f"  MCP Hardened: {mcp_hardened}")
    print(f"  Commits: {commits}")
    print(f"  Regressions: {regressions}")
    
    return new_entry


def get_current_stats() -> dict:
    """Get current statistics from the log."""
    log = load_log()
    if not log:
        return {}
    
    latest = log[-1]
    total_commits = sum(entry.get('commits', 0) for entry in log)
    
    return {
        'latest_batch': latest.get('batch', 'Unknown'),
        'healing_pct': latest.get('healing_core_pct', 0),
        'healed': latest.get('healed_agents', 0),
        'total': latest.get('total_core', 0),
        'mcp_hardened': latest.get('mcp_hardened', 0),
        'total_commits': total_commits,
        'entry_count': len(log)
    }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description='Append batch to Windsurf log')
    parser.add_argument('--healing', type=float, required=True, help='Healing percentage')
    parser.add_argument('--healed', type=int, required=True, help='Number of healed agents')
    parser.add_argument('--total', type=int, required=True, help='Total core agents')
    parser.add_argument('--commits', type=int, required=True, help='Number of commits')
    parser.add_argument('--batch', type=str, default=None, help='Batch name (optional)')
    parser.add_argument('--mcp', type=int, default=0, help='MCP hardened agents')
    parser.add_argument('--regressions', type=int, default=0, help='Regressions detected')
    parser.add_argument('--stats', action='store_true', help='Show current stats only')
    
    args = parser.parse_args()
    
    if args.stats:
        stats = get_current_stats()
        print("\n[CURRENT STATS]")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        return
    
    append_batch(
        healing_pct=args.healing,
        healed=args.healed,
        total_core=args.total,
        commits=args.commits,
        batch_name=args.batch,
        mcp_hardened=args.mcp,
        regressions=args.regressions
    )


if __name__ == '__main__':
    main()
