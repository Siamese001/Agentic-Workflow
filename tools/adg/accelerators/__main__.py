"""Unified ADG Accelerators Entry Point

Orchestrates all ADG accelerator tools for testing, hardening, and incremental updates.

Usage:
    # Testing accelerators
    python -m tools.adg.accelerators testing gap [--top 20] [--layer L5]
    python -m tools.adg.accelerators testing scope --changed file.py
    python -m tools.adg.accelerators testing groups --workers 4
    python -m tools.adg.accelerators testing collection-safety [--json out.json]

    # Hardening accelerators
    python -m tools.adg.accelerators hardening p0 --layer L3 --dim evidence --apply
    python -m tools.adg.accelerators hardening p1 --apply
    python -m tools.adg.accelerators hardening p2 --apply

    # Incremental accelerators
    python -m tools.adg.accelerators incremental update --changed file1.py file2.py
    python -m tools.adg.accelerators incremental scan --cache

    # Fast test runner
    python -m tools.adg.accelerators fast [--adg] [--dry-run]

Each subcommand delegates to the appropriate accelerator module.
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
_logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent.parent.parent


def run_testing_accelerator(args: argparse.Namespace) -> int:
    """Delegate to the testing accelerator (adg_test_accelerator.py)."""
    from tools.adg import adg_test_accelerator as testing

    # Map our unified commands to the existing accelerator commands
    if args.testing_command == "gap":
        return testing.main([
            "gap",
            "--top", str(args.top),
            *([
