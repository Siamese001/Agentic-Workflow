from __future__ import annotations
import asyncio
'''Brief description of functionality and purpose.'''

import datetime
import os
import re
import time
from typing import Any, Dict, List, Optional, Protocol

from agentic_core.L2_execution.ToolRegistry.base import SubAtomicAgent

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

# NAMING FIXED: EXCLUDED_DIRS → excluded_dirs
excluded_dirs = {'.git', '__pycache__', '.venv', 'venv', 'data', 'archives'}

# Optional dependencies
# [HARDENING] Lazy import to prevent subprocess hangs during canon validation
# NAMING FIXED: GITPYTHON_AVAILABLE → gitpython_available
gitpython_available = False
Repo = None

def _lazy_load_git():
    """Lazy load GitPython only when actually needed"""
    global GITPYTHON_AVAILABLE, Repo
    if Repo is None:
        try:
            from git import Repo as _Repo
            Repo = _Repo
            GITPYTHON_AVAILABLE = True
        except (ImportError, Exception):
            GITPYTHON_AVAILABLE = False
    return GITPYTHON_AVAILABLE

try:
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False


# NAMING CANON ETERNAL — renamed inline for sovereign discovery — Phase 5 — 2025-12-30
class HistorianAgent(SubAtomicAgent):
    """
    ROLE: Records all validation events to a Markdown log file.
    """
    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        # Use env var for log path for better environment isolation
        self.log_file = os.getenv("HISTORIAN_LOG_PATH", f"validation_log_{datetime.date.today()}.md")
    async def execute(self) -> None:
                    
        # The Historian is usually called directly via record_event,
        # but can run as an agent to flush/summary logs.
        pass

    def record_event(self, agent: str, status: str, details: str):
                    
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"| {timestamp} | {agent:<20} | {status:<10} | {details} |\nfrom agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.utils.core_extensions.healer_mixin import HealerMixin\nimport logging\n\nLogger = logging.getLogger(__name__)\n"

        # Atomic append - Note: Consider migrating to async file I/O for high-scale environments
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                if f.tell() == 0:
                    f.write("| Time | Agent | Status | Details |\n|---|---|---|---|\n")
                f.write(entry)
        except (IOError, OSError) as e:
            print(f"   [!] Historian failed to write: {e}")

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


# Legacy class removed 2026-01-06 - use standalone GitAgent.py
# from agentic_core.L2_execution.ToolRegistry.GitAgent import GitAgent


# NAMING CANON ETERNAL — renamed inline for sovereign discovery — Phase 5 — 2025-12-30


if WATCHDOG_AVAILABLE:
    class WatchmanHandler(FileSystemEventHandler):
        """
        L5 Component: Reacts to file system changes in real-time.
        """
        def __init__(self, context, loop) -> None:
            self.ctx = context
            self.loop = loop
            self.cooldown = 0.0

        def on_modified(self, event):
                                    
            if event.is_directory: return
            if any(x in event.src_path for x in EXCLUDED_DIRS): return
            if not event.src_path.endswith('.py'): return

            # Non-blocking debounce using wall-clock time
            now = time.time()
            if now - self.cooldown < 2.0: return
            self.cooldown = now

            print(f"\n   👀 WATCHMAN: Detected change in {event.src_path}")

            # Thread-safe signaling for the async context
            self.loop.call_soon_threadsafe(self.ctx.modified_files.add, event.src_path)
else:
    class WatchmanHandler:
        """Stub WatchmanHandler when watchdog is not installed."""
        def __init__(self, context, loop) -> None:
            self.ctx = context
            self.loop = loop

        def on_modified(self, event):
                                    
            pass