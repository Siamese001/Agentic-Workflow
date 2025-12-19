"""
GitAgent - L6 GitOps & Remote Synchronization

Manages git operations for self-healing commits and remote pushes.
Ensures changes are committed and pushed to remote repository.
"""

import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

LOGGER = logging.getLogger(__name__)


class GitAgent:
    """
    Agent for managing git operations and remote synchronization.
    
    Features:
    - Atomic commits of modified files
    - Branch management for healing cycles
    - Remote push capabilities
    - Safety checks for secrets
    """
    
    def __init__(self, repo_root: Path = None):
        """
        Initialize the GitAgent.
        
        Args:
            repo_root: Root directory of the git repository
        """
        self.repo_root = repo_root or Path.cwd()
        self.remote_repo = os.getenv("CANON_REMOTE_REPO")
        
        # Git command helper
        self.git_cmd = ["git", "-C", str(self.repo_root)]
        
        # Check if we're in a git repo
        if not self._is_git_repo():
            LOGGER.warning(f"Not in a git repository: {self.repo_root}")
            self.enabled = False
        else:
            self.enabled = True
            LOGGER.info(f"GitAgent initialized for {self.repo_root}")
    
    def _is_git_repo(self) -> bool:
        """Check if current directory is a git repository."""
        git_dir = self.repo_root / ".git"
        return git_dir.exists()
    
    def _run_git(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """
        Run a git command.
        
        Args:
            args: Git command arguments
            check: Whether to check return code
            
        Returns:
            Completed process
        """
        cmd = self.git_cmd + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            LOGGER.error(f"Git command failed: {' '.join(cmd)}")
            LOGGER.error(f"Error: {e.stderr}")
            raise
    
    def _generate_git_metadata(self, cycle_id: int) -> Dict[str, str]:
        """
        Generate git metadata for a healing cycle.
        
        Args:
            cycle_id: ID of the current cycle
            
        Returns:
            Dictionary with branch name and commit info
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        branch_name = f"healing/cycle-{cycle_id}-{timestamp}"
        
        commit_message = f"""Self-healing cycle {cycle_id}

Automated fixes applied at {timestamp}
Modified files: {len(self._get_modified_files())} files
Status: COMPLETED
"""
        
        return {
            "branch_name": branch_name,
            "commit_message": commit_message,
            "timestamp": timestamp,
            "cycle_id": cycle_id
        }
    
    def _get_modified_files(self) -> List[Path]:
        """Get list of modified files in the repository."""
        try:
            result = self._run_git(["status", "--porcelain"])
            modified = []
            
            for line in result.stdout.strip().split('\n'):
                if line:
                    # Parse git status output
                    status = line[:2]
                    file_path = line[3:]
                    
                    # Only include modified files (not untracked)
                    if status.strip() and status[0] in ['M', 'A', 'R']:
                        modified.append(Path(file_path))
            
            return modified
        except Exception as e:
            LOGGER.error(f"Failed to get modified files: {e}")
            return []
    
    def _check_for_secrets(self, file_paths: List[Path]) -> List[str]:
        """
        Check files for potential secrets.
        
        Args:
            file_paths: List of files to check
            
        Returns:
            List of suspicious files
        """
        suspicious = []
        secret_patterns = [
            "password", "secret", "token", "key", "credential",
            "api_key", "private_key", "auth_token"
        ]
        
        for file_path in file_paths:
            if not file_path.exists():
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    
                for pattern in secret_patterns:
                    if pattern in content:
                        suspicious.append(str(file_path))
                        break
            except Exception:
                # Skip binary files or read errors
                pass
        
        return suspicious
    
    def stage_files(self, file_paths: List[Path]) -> bool:
        """
        Stage specific files for commit.
        
        Args:
            file_paths: List of files to stage
            
        Returns:
            True if successful
        """
        if not self.enabled:
            LOGGER.warning("Git not enabled")
            return False
        
        try:
            # Stage each file
            for file_path in file_paths:
                self._run_git(["add", str(file_path)])
            
            LOGGER.info(f"Staged {len(file_paths)} files")
            return True
        except Exception as e:
            LOGGER.error(f"Failed to stage files: {e}")
            return False
    
    def create_branch(self, branch_name: str) -> bool:
        """
        Create and checkout a new branch.
        
        Args:
            branch_name: Name of the branch to create
            
        Returns:
            True if successful
        """
        if not self.enabled:
            return False
        
        try:
            # Create and checkout branch
            self._run_git(["checkout", "-b", branch_name])
            LOGGER.info(f"Created branch: {branch_name}")
            return True
        except Exception as e:
            LOGGER.error(f"Failed to create branch: {e}")
            return False
    
    def commit_changes(self, message: str) -> bool:
        """
        Commit staged changes.
        
        Args:
            message: Commit message
            
        Returns:
            True if successful
        """
        if not self.enabled:
            return False
        
        try:
            # Configure git user if not set
            try:
                self._run_git(["config", "user.name", "AgenticWorkflow"])
                self._run_git(["config", "user.email", "workflow@agentic.system"])
            except:
                pass
            
            # Commit changes
            self._run_git(["commit", "-m", message])
            LOGGER.info("Changes committed")
            return True
        except Exception as e:
            LOGGER.error(f"Failed to commit: {e}")
            return False
    
    def push_to_remote(self, branch_name: str = None) -> bool:
        """
        Push changes to remote repository.
        
        Args:
            branch_name: Branch to push (current branch if None)
            
        Returns:
            True if successful
        """
        if not self.enabled or not self.remote_repo:
            LOGGER.warning("Remote repository not configured")
            return False
        
        try:
            # Add remote if not exists
            try:
                self._run_git(["remote", "add", "origin", self.remote_repo], check=False)
            except:
                pass
            
            # Push to remote
            if branch_name:
                self._run_git(["push", "-u", "origin", branch_name])
            else:
                self._run_git(["push", "-u", "origin", "HEAD"])
            
            LOGGER.info(f"Pushed to remote: {self.remote_repo}")
            return True
        except Exception as e:
            LOGGER.error(f"Failed to push to remote: {e}")
            return False
    
    def commit_healing_cycle(self, cycle_id: int, modified_files: List[Path]) -> bool:
        """
        Commit changes from a healing cycle.
        
        Args:
            cycle_id: ID of the healing cycle
            modified_files: List of modified files to commit
            
        Returns:
            True if successful
        """
        if not modified_files:
            LOGGER.info("No files to commit")
            return True
        
        # Generate metadata
        metadata = self._generate_git_metadata(cycle_id)
        
        # Safety check for secrets
        suspicious = self._check_for_secrets(modified_files)
        if suspicious:
            LOGGER.warning(f"Found potential secrets in: {suspicious}")
            # Don't commit files with secrets
            modified_files = [f for f in modified_files if str(f) not in suspicious]
        
        if not modified_files:
            LOGGER.error("No safe files to commit")
            return False
        
        try:
            # Create branch
            if not self.create_branch(metadata["branch_name"]):
                return False
            
            # Stage files
            if not self.stage_files(modified_files):
                return False
            
            # Commit changes
            if not self.commit_changes(metadata["commit_message"]):
                return False
            
            # Push to remote
            if self.remote_repo:
                self.push_to_remote(metadata["branch_name"])
            
            LOGGER.info(f"Successfully committed healing cycle {cycle_id}")
            return True
            
        except Exception as e:
            LOGGER.error(f"Failed to commit healing cycle: {e}")
            return False
    
    def get_repo_status(self) -> Dict[str, Any]:
        """
        Get current repository status.
        
        Returns:
            Status dictionary
        """
        if not self.enabled:
            return {"status": "not_a_git_repo"}
        
        try:
            # Get current branch
            branch_result = self._run_git(["branch", "--show-current"])
            current_branch = branch_result.stdout.strip()
            
            # Get status
            status_result = self._run_git(["status", "--porcelain"])
            modified_files = []
            for line in status_result.stdout.strip().split('\n'):
                if line:
                    modified_files.append(line[3:])
            
            # Get remote info
            remote_result = self._run_git(["remote", "-v"], check=False)
            remotes = remote_result.stdout.strip() if remote_result.returncode == 0 else ""
            
            return {
                "enabled": True,
                "current_branch": current_branch,
                "modified_files": modified_files,
                "remotes": remotes,
                "remote_configured": bool(self.remote_repo)
            }
        except Exception as e:
            LOGGER.error(f"Failed to get repo status: {e}")
            return {"status": "error", "error": str(e)}


# Global instance
_git_agent: Optional[GitAgent] = None


def get_git_agent() -> GitAgent:
    """Get or create the global GitAgent instance."""
    global _git_agent
    if _git_agent is None:
        _git_agent = GitAgent()
    return _git_agent


def initialize_git_agent(repo_root: Path = None):
    """
    Initialize the GitAgent system.
    
    Args:
        repo_root: Root directory of the git repository
    """
    global _git_agent
    _git_agent = GitAgent(repo_root)
    
    if _git_agent.enabled:
        LOGGER.info("GitAgent initialized successfully")
    else:
        LOGGER.warning("GitAgent disabled - not in a git repository")


# Convenience functions
def commit_healing_cycle(cycle_id: int, modified_files: List[Path]) -> bool:
    """
    Commit a healing cycle.
    
    Args:
        cycle_id: Cycle ID
        modified_files: List of modified files
        
    Returns:
        True if successful
    """
    agent = get_git_agent()
    return agent.commit_healing_cycle(cycle_id, modified_files)
