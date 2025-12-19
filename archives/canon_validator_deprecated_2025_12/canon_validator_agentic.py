#!/usr/bin/env python3
"""
Canon Validator v2.1 - Entry Point

Minimal entry point for the Canon Validator system.
All logic has been extracted to agentic_core/L3_orchestration/.

Usage:
  Standard (L4):  python canon_validator_agentic.py
  Daemon (L5):    python canon_validator_agentic.py --daemon
  Surgical:       python canon_validator_agentic.py --target <file>
"""

import argparse
import sys
from pathlib import Path

# Fix Windows console encoding FIRST
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Add repo root to path for imports
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("CRITICAL: Missing python-dotenv. Install with: pip install python-dotenv")
    sys.exit(1)

# Import mission runners from agentic_core
from agentic_core.L3_orchestration import (
    run_daemon_mode,
    run_standard_mode,
    run_surgical_mode,
)


def main():
    """Main entry point for Canon Validator."""
    parser = argparse.ArgumentParser(
        description="Canon Validator v2.1 - Modular Agentic Architecture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  Standard (L4):  python canon_validator_agentic.py
  Daemon (L5):    python canon_validator_agentic.py --daemon
  Surgical:       python canon_validator_agentic.py --target <file>

The Watchman (L5 Daemon Mode):
  Monitors the repository for file changes and automatically triggers
  surgical validation missions using blast radius analysis.
        """
    )
    parser.add_argument(
        "--daemon", 
        action="store_true", 
        help="Run in L5 Autonomous Mode (The Watchman)"
    )
    parser.add_argument(
        "--target",
        type=str,
        default=None,
        help="Target a specific file for surgical validation"
    )
    args = parser.parse_args()

    if args.daemon:
        run_daemon_mode()
    elif args.target:
        run_surgical_mode(args.target)
    else:
        run_standard_mode()


if __name__ == "__main__":
    main()
