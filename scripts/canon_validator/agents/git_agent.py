"""
GitAgent - Remote GitOps Manager.
Manages checkpoints and pushes healing branches.
"""

import asyncio
import os
import subprocess
import time
from datetime import datetime
from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import ValidationContext

from ..base import SubAtomicAgent


class GitAgent(SubAtomicAgent):
    """
    ROLE: Remote GitOps. Manages checkpoints and pushes healing branches.
    """

    def run_cmd(self, cmd: list) -> bool:
        """Fallback subprocess command runner."""
        try:
            subprocess.run(cmd, check=True, capture_output=True, cwd=os.getcwd())
            return True
        except subprocess.CalledProcessError:
            return False

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Managing Git Operations...")

        # Try GitPython first, fallback to subprocess
        try:
            from git import Repo, GitCommandError
            await self._execute_gitpython(Repo, GitCommandError)
        except ImportError:
            await self._execute_subprocess()

    async def _execute_gitpython(self, Repo, GitCommandError):
        """GitPython-based execution with remote support."""
        try:
            repo = Repo('.')
        except Exception:
            print("   ⚠️  GitOps: Not a valid git repository.")
            return

        # Handle critical failure - revert to HEAD
        if "CRITICAL_FAILURE" in self.ctx.signals:
            print(f"   ⏪ GitOps: Critical Failure. Reverting to HEAD...")
            try:
                repo.git.reset('--hard', 'HEAD')
                self.ctx.signals.discard("CRITICAL_FAILURE")
            except GitCommandError as e:
                print(f"   ⚠️  GitOps Reset Error: {e}")
            return

        # Create healing branch and commit changes
        if self.ctx.modified_files:
            try:
                branch_name, commit_msg = await self._generate_git_metadata()
                if not branch_name:
                    branch_name = f"healing/auto_{int(time.time())}"

                # Create and checkout new branch
                new_branch = repo.create_head(branch_name)
                new_branch.checkout()

                # Add and Commit
                repo.index.add(list(self.ctx.modified_files))
                if not commit_msg:
                    commit_msg = f"[HEALING] fix: auto-fix cycle {len(self.ctx.successful_traces)}"
                repo.index.commit(commit_msg)
                print(f"   💾 GitOps: Checkpoint saved to branch '{branch_name}'.")

                # Remote Push (if configured)
                remote_url = os.getenv("GIT_REMOTE_URL")
                if remote_url:
                    try:
                        if 'origin' not in [r.name for r in repo.remotes]:
                            repo.create_remote('origin', remote_url)
                        origin = repo.remotes.origin
                        origin.push(branch_name)
                        print(f"   🌐 GitOps: Pushed healing branch to remote.")
                    except GitCommandError as e:
                        print(f"   ⚠️  GitOps Push Error: {e}")

            except GitCommandError as e:
                print(f"   ⚠️  GitOps Error: {e}")

    async def _execute_subprocess(self):
        """Fallback subprocess-based execution."""
        if "CRITICAL_FAILURE" in self.ctx.signals:
            print(f"   ⏪ GitOps: Critical Failure. REVERTING to last safe commit...")
            self.run_cmd(["git", "reset", "--hard", "HEAD"])
            self.ctx.signals.discard("CRITICAL_FAILURE")
        elif self.ctx.modified_files:
            print(f"   💾 GitOps: Committing {len(self.ctx.modified_files)} changes...")
            self.run_cmd(["git", "add"] + list(self.ctx.modified_files))
            cycle = len(self.ctx.successful_traces)
            self.run_cmd(["git", "commit", "-m", f"[HEALING] fix: auto-fix cycle {cycle}"])
            print(f"   ✅ GitOps: Checkpoint saved.")

    async def _generate_git_metadata(self) -> Tuple[str, str]:
        """Generate intelligent branch name and commit message."""
        if not self.ctx.intelligence_enabled:
            return None, None

        date_str = datetime.now().strftime("%Y%m%d")
        signals_summary = list(self.ctx.signals)[:5]
        modified_summary = [os.path.basename(f) for f in list(self.ctx.modified_files)[:5]]

        prompt = f"""
Current healing state:
Modified files: {modified_summary}
Signals resolved: {signals_summary}
Date: {date_str}

Propose:
- Branch name (healing/<type>-<desc>-YYYYMMDD)
- Commit title (conventional: fix/refactor/security/chore)

RESPONSE FORMAT:
BRANCH: healing/<type>-<short-desc>-{date_str}
COMMIT: <type>: <description>
"""

        try:
            response = await self.ctx.resilient_mutation(self.name, prompt, max_attempts=1)
            if response:
                branch_name = None
                commit_msg = None
                for line in response.strip().split('\n'):
                    if line.startswith('BRANCH:'):
                        branch_name = line.replace('BRANCH:', '').strip()
                    elif line.startswith('COMMIT:'):
                        commit_msg = f"[HEALING] {line.replace('COMMIT:', '').strip()}"

                if branch_name and not branch_name.startswith("healing/"):
                    branch_name = None

                return branch_name, commit_msg
        except Exception:
            pass
        return None, None
