"""
agentic_core/agents/infrastructure.py
Depth: 3
Role: Manages environment, version control, logging, and file monitoring.
"""
import asyncio
import datetime
import os
import sys
import time
from typing import Optional

from agentic_core.agents.base import SubAtomicAgent
from apps_shared.domain.constants import EXCLUDED_DIRS

# Optional dependencies
try:
    from git import Repo, GitCommandError
    GITPYTHON_AVAILABLE = True
except ImportError:
    GITPYTHON_AVAILABLE = False

try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False


class Historian(SubAtomicAgent):
    """
    ROLE: Records all validation events to a Markdown log file.
    """
    def __init__(self, ctx):
        super().__init__(ctx)
        self.log_file = f"validation_log_{datetime.date.today()}.md"

    async def execute(self):
        # The Historian is usually called directly via record_event, 
        # but can run as an agent to flush/summary logs.
        pass

    def record_event(self, agent: str, status: str, details: str):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"| {timestamp} | {agent:<20} | {status:<10} | {details} |\n"
        
        # Atomic append
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                if f.tell() == 0:
                    f.write("| Time | Agent | Status | Details |\n|---|---|---|---|\n")
                f.write(entry)
        except Exception as e:
            print(f"   ⚠️ Historian failed to write: {e}")


class GitAgent(SubAtomicAgent):
    """
    ROLE: Manages Version Control (Branching, Commits).
    """
    def __init__(self, ctx):
        super().__init__(ctx)
        self.repo = None
        if GITPYTHON_AVAILABLE:
            try:
                self.repo = Repo('.')
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
            if self.repo.is_dirty(untracked_files=True):
                self.repo.git.add(A=True)
                self.repo.index.commit(f"Auto-fix by {self.ctx._current_agent}")
                print("   💾 Changes committed to git.")
        except Exception as e:
            print(f"   ⚠️ Git operation failed: {e}")


class BenchmarkingAgent(SubAtomicAgent):
    """
    ROLE: Measures execution time and ensures tools aren't too slow.
    """
    async def execute(self):
        # In a real run, this might aggregate stats from the Context
        # For now, it's a placeholder for Key 62 (Time Budgets)
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

            # Debounce
            now = time.time()
            if now - self.cooldown < 2.0: return
            self.cooldown = now

            print(f"\n   👀 WATCHMAN: Detected change in {event.src_path}")
            
            # Signal the loop to re-scan
            # Note: Thread-safe signaling needed here in full async app
            self.ctx.modified_files.add(event.src_path)
else:
    # Stub class when watchdog is not available
    class WatchmanHandler:
        """Stub WatchmanHandler when watchdog is not installed."""
        def __init__(self, context, loop):
            self.ctx = context
            self.loop = loop
        
        def on_modified(self, event):
            pass
