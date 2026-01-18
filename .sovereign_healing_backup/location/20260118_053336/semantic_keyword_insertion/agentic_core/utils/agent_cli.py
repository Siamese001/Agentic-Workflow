
# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, healer, memory, orchestrator, workflow
# This boosts alignment detection — review and integrate appropriately

import sys
from pathlib import Path

# === ENABLE DIRECT EXECUTION: Dynamically add project root to sys.path ===
def _add_project_root_to_sys_path() -> None:
    current = Path(__file__).resolve()
    while current.parent != current:
        if (current / AGENTIC_CORE_DIR).exists():
            root_str = str(current)
            if root_str not in sys.path:
                sys.path.insert(0, root_str)
            return
        current = current.parent
    raise RuntimeError("Could not locate project root")

_add_project_root_to_sys_path()
# === END PATH FIX ===

"""Shared CLI runner for L2 batch agents.
Provides standardized argument parsing and execution context.
"""

import argparse
import random
from typing import Any, List
from tqdm import tqdm
import shutil  # For terminal width detection in formatting

from agentic_core.L5_safety.validators.structure_blueprint_1 import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)


def create_agent_parser(description: str) -> argparse.ArgumentParser:
    """Create standardized argument parser for L2 agents."""
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--heal",
        action="store_true",
        help="Enable surgery/healing: perform file modifications (creates backups)"
    )
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Auto-confirm healing prompt (non-interactive; use with --heal for scripted runs)"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Scan all Python files (ignore limit for large repositories)"
    )
    
    return parser


def setup_execution_context(args: argparse.Namespace, project_root: Path) -> Any:
    """Create execution context with file collection and surgery flags."""
    # === BEST-IN-CLASS FILE COLLECTION WITH COLORED PROGRESS BAR ===
    print("\n🔍 Collecting Python files from project...")
    files_gen = project_root.rglob("*.py")
    
    # Manual tqdm for accurate total + rate + dynamic description
    pbar = tqdm(
        desc="Collecting files",
        unit="file",
        colour="#88ffff",  # Cyan for collection phase
        bar_format="{l_bar}{bar:30}| {n_fmt} files [{elapsed}, {rate_fmt}{postfix}]",
        leave=False,  # Clears after completion
        dynamic_ncols=True,
    )
    
    python_files: List[str] = []
    for f in files_gen:
        if f.is_file() and ARCHIVES_DIR not in str(f) and ".venv" not in str(f) and "__pycache__" not in str(f):
            python_files.append(str(f))
        pbar.update(1)
    
    total_found = len(python_files)
    pbar.close()
    print(f"✅ Found {total_found} Python files\n")
    # === END COLLECTION ===

    # Apply file limit for large repositories
    if not args.full and len(python_files) > 300:
        print(f"⚠️  Large repository ({len(python_files)} files). Limiting to 300 random files for faster daily runs.")
        random.seed(42)
        random.shuffle(python_files)
        python_files = python_files[:300]
        print("   Use --full to scan all files.")

    # Handle healing confirmation
    surgery = False
    if args.heal:
        if not args.yes:
            confirm = input("\n\033[91m⚠️  HEALING MODE ENABLED\033[0m: This will MODIFY files (backups created). Type 'yes' to continue: ")
            if confirm.lower() != "yes":
                print("Aborted by user.")
                return None
        else:
            print("\n\033[91m⚠️  HEALING MODE enabled\033[0m (auto-confirmed with -y/--yes)")
        surgery = True
        print("\033[93m🛠️  Running in HEALING mode\033[0m")
    else:
        print("\033[92m🔍 Running in SAFE validation mode (dry-run)\033[0m")

    print(f"\033[1mScanning {len(python_files)} Python files...\033[0m\n")

    # Create context object
    class Context:
        def __init__(self):
            self.project_root = str(project_root)
            self.python_files = python_files
            self.RUN_SPRAWL_SURGERY = surgery

    return Context()


def run_agent_cli(agent_class: Any, description: str) -> None:
    """Standard CLI runner for L2 agents."""
    parser = create_agent_parser(description)
    args = parser.parse_args()
    
    project_root = Path.cwd()
    ctx = setup_execution_context(args, project_root)
    
    if ctx is None:
        return
    
    # Initialize and execute agent
    agent = agent_class()
    
    import asyncio
    asyncio.run(agent.execute(ctx))
    
    terminal_width = shutil.get_terminal_size(fallback=(80, 24)).columns
    line = "=" * terminal_width
    print(f"\n\033[92m{line}\033[0m")
    print("\033[1;92mEXECUTION COMPLETE\033[0m")
    print(f"\033[92m{line}\033[0m")