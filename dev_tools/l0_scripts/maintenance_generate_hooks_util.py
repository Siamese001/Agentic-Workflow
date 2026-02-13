"""
dev_tools/l0_scripts/maintenance_generate_hooks_util.py
-----------------------------------------------------------------
DEPRECATED: Redirects to the unified 'generate_hooks.py' script.
This file is retained as a stub to prevent breaking existing automation
that calls this specific path.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Redirect execution to the SSOT generator
project_root = Path(__file__).resolve().parent.parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))

from agentic_core.L0_routing.scripts.generate_hooks import (
    generate_sovereign_list,
    sync_pre_commit,
)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sync pre-commit config with SSOT (Redirect)")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--list", action="store_true", help="List current sovereign roots")

    args = parser.parse_args()

    print("[*] maintenance_generate_hooks_util.py is DEPRECATED. Redirecting to generate_hooks.py...")

    if args.list:
        generate_sovereign_list()
    else:
        success = sync_pre_commit(dry_run=args.dry_run)
        sys.exit(0 if success else 1)
