from typing import Any, Optional, Protocol, Dict, List
import re

import asyncio
import datetime
import os
import time

from agentic_core.L2_execution.tool_registry.base import SubAtomicAgent
# Domain constants not available, using fallback
EXCLUDED_DIRS = {'.git', '__pycache__', '.venv', 'venv', 'data', 'archives'}

# Optional dependencies
try:
    from git import Repo
    GITPYTHON_AVAILABLE = True
except ImportError:
    GITPYTHON_AVAILABLE = False

try:
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False


class Historian(SubAtomicAgent):
    """
    ROLE: Records all validation events to a Markdown log file.
    """
    def __init__(self, ctx):
        super().__init__(ctx)
        # Use env var for log path for better environment isolation
        self.log_file = os.getenv("HISTORIAN_LOG_PATH", f"validation_log_{datetime.date.today()}.md")

    async def execute(self):
        # The Historian is usually called directly via record_event,
        # but can run as an agent to flush/summary logs.
        pass

    def record_event(self, agent: str, status: str, details: str):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"| {timestamp} | {agent:<20} | {status:<10} | {details} |\n"

        # Atomic append - Note: Consider migrating to async file I/O for high-scale environments
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                if f.tell() == 0:
                    f.write("| Time | Agent | Status | Details |\n|---|---|---|---|\n")
                f.write(entry)
        except (IOError, OSError) as e:
            print(f"   [!] Historian failed to write: {e}")


class GitAgent(SubAtomicAgent):
    """
    ROLE: Manages Version Control (Branching, Commits).
    """
    def __init__(self, ctx):
        super().__init__(ctx)
        self.repo = None
        if GITPYTHON_AVAILABLE:
            try:
                # Use environment variable for repository path to avoid hardcoded relative paths
                repo_path = os.getenv("GIT_REPO_PATH", ".")
                self.repo = Repo(repo_path)
            except Exception:
                pass

    async def execute(self):
        if not GITPYTHON_AVAILABLE or not self.repo:
            return

        # Simple auto-commit logic if requested
        if "COMMIT_CHANGES" in self.ctx.signals:
            await self._commit_changes()

    async def _commit_changes(self):
        try:
            # git operations are blocking calls; use to_thread to keep the event loop responsive
            is_dirty = await asyncio.to_thread(self.repo.is_dirty, untracked_files=True)
            if is_dirty:
                await asyncio.to_thread(self.repo.git.add, A=True)
                commit_msg = f"Auto-fix by {self.ctx._current_agent}"
                await asyncio.to_thread(self.repo.index.commit, commit_msg)
                print("   [SAVE] Changes committed to git.")
        except Exception as e:
            print(f"   [!] Git operation failed: {e}")


class BenchmarkingAgent(SubAtomicAgent):
    """
    ROLE: Measures execution time and ensures tools aren't too slow.
    """
    async def execute(self):
        # Placeholder for Time Budget logic
        pass


if WATCHDOG_AVAILABLE:
    class WatchmanHandler(FileSystemEventHandler):
        """
        L5 Component: Reacts to file system changes in real-time.
        """
        def __init__(self, context, loop):
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
        def __init__(self, context, loop):
            self.ctx = context
            self.loop = loop

        def on_modified(self, event):
            pass