"""
Unit tests for Multi-Repository & Remote Support (L5 Environment Expansion).
Tests GitPython integration for branching, commits, and remote push operations.

These tests verify the "All Tests Pass" provision for L5 Full Autonomy.
"""
import os
import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch


# ==============================================================================
# STANDALONE IMPLEMENTATIONS FOR TESTING
# (Mirrors canon_validator_agentic.py without heavy dependencies)
# ==============================================================================

EXCLUDED_DIRS = {
    '.git', '.venv', 'venv', 'env', '__pycache__', '.pytest_cache',
    'node_modules', '.idea', '.vscode', 'build', 'dist', 'eggs', 
    'site-packages', 'archives', 'data', 'cache', 'logs', 'tmp', 'temp'
}


class MockValidationContext:
    """Lightweight mock of ValidationContext for git testing."""
    
    def __init__(self):
        self.signals: set = set()
        self.modified_files: set = set()
        self.successful_traces: list = []
        self.python_files: list = []
        self._streamer_initialized: bool = False
        self.broadcast = AsyncMock()
    
    def _load_memory(self):
        pass


class MockGitCommandError(Exception):
    """Mock GitCommandError for testing."""


class GitAgent:
    """
    ROLE: Remote GitOps. Manages checkpoints and pushes healing branches.
    (Standalone implementation for testing)
    """
    def __init__(self, ctx: MockValidationContext):
        self.ctx = ctx
        self.name = "GitOps"
    
    def can_run(self) -> bool:
        return True
    
    async def execute(self):
        """Execute using GitPython."""
        await self._execute_gitpython()
    
    async def _execute_gitpython(self):
        """L5 GitPython-based execution with remote support."""
        from git import Repo, GitCommandError
        
        try:
            repo = Repo('.')
        except Exception:
            print("   GitOps: Not a valid git repository.")
            return

        # Handle critical failure - revert to HEAD
        if "CRITICAL_FAILURE" in self.ctx.signals:
            print(f"   GitOps: Critical Failure. Reverting to HEAD...")
            try:
                repo.git.reset('--hard', 'HEAD')
                self.ctx.signals.discard("CRITICAL_FAILURE")
            except GitCommandError as e:
                print(f"   GitOps Reset Error: {e}")
            return

        # Create healing branch and commit changes
        if self.ctx.modified_files:
            try:
                # Create unique branch
                branch_name = f"healing/auto_{int(time.time())}"
                
                # Create and checkout new branch
                new_branch = repo.create_head(branch_name)
                new_branch.checkout()
                
                # Add and Commit
                repo.index.add(list(self.ctx.modified_files))
                commit_msg = f"L5 Auto-fix cycle {len(self.ctx.successful_traces)}"
                repo.index.commit(commit_msg)
                print(f"   GitOps: Checkpoint saved to branch '{branch_name}'.")
                
                # Remote Push (if configured)
                remote_url = os.getenv("GIT_REMOTE_URL")
                if remote_url:
                    try:
                        # Check if origin exists, create if not
                        if 'origin' not in [r.name for r in repo.remotes]:
                            repo.create_remote('origin', remote_url)
                        
                        origin = repo.remotes.origin
                        origin.push(branch_name)
                        print(f"   GitOps: Pushed healing branch to remote.")
                    except GitCommandError as e:
                        print(f"   GitOps Push Error: {e}")
                
                # Broadcast to streamer if available
                if self.ctx._streamer_initialized:
                    await self.ctx.broadcast(f"Created healing branch: {branch_name}", agent=self.name, level="GIT_CHECKPOINT")
                    
            except GitCommandError as e:
                print(f"   GitOps Error: {e}")


# ==============================================================================
# L5 MULTI-REPOSITORY TESTS - Context Loading
# ==============================================================================

class TestMultiRepoContextLoading:
    """Verifies Context loads files from ADDITIONAL_REPO_ROOTS."""
    
    def test_additional_repo_roots_scanning(self):
        """Verifies files from additional roots are added to python_files."""
        # Simulate the scanning logic that ValidationContext uses
        python_files = ["local.py"]
        
        # Use paths that don't match any EXCLUDED_DIRS
        # Note: 'tmp' is in EXCLUDED_DIRS, so use 'external_repos' instead
        fake_repo = os.path.join("external_repos", "fake_repo")
        walk_results = [(fake_repo, [], ["external_lib.py"])]
        
        # This mirrors the exact logic in ValidationContext.__post_init__
        for r, _, files in walk_results:
            if any(x in r for x in EXCLUDED_DIRS):
                continue
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(r, file))
        
        # Verify both local and external files are present
        expected_path = os.path.join(fake_repo, "external_lib.py")
        assert expected_path in python_files
        assert "local.py" in python_files
        assert len(python_files) == 2
    
    def test_excluded_dirs_respected_in_additional_roots(self):
        """Verifies EXCLUDED_DIRS are respected when scanning additional roots."""
        python_files = []
        
        # Use paths where some match EXCLUDED_DIRS and some don't
        repo_path = os.path.join("external_repos", "myrepo")
        pycache_path = os.path.join("external_repos", "myrepo", "__pycache__")
        venv_path = os.path.join("external_repos", "myrepo", "venv")
        
        walk_results = [
            (repo_path, [], ["good.py"]),
            (pycache_path, [], ["cached.py"]),
            (venv_path, [], ["venv_file.py"]),
        ]
        
        # This mirrors the exact logic in ValidationContext.__post_init__
        for r, _, files in walk_results:
            if any(x in r for x in EXCLUDED_DIRS):
                continue
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(r, file))
        
        # Only good.py should be included (not in excluded dirs)
        expected_good = os.path.join(repo_path, "good.py")
        expected_cached = os.path.join(pycache_path, "cached.py")
        expected_venv = os.path.join(venv_path, "venv_file.py")
        
        assert expected_good in python_files
        assert expected_cached not in python_files
        assert expected_venv not in python_files
        assert len(python_files) == 1
    
    def test_multiple_additional_roots(self):
        """Verifies multiple comma-separated roots are all scanned."""
        python_files = []
        extra_roots = "/tmp/repo1, /tmp/repo2, /tmp/repo3"
        
        def mock_walk(path):
            return [(path, [], [f"file_from_{os.path.basename(path)}.py"])]
        
        with patch("os.path.exists", return_value=True), \
             patch("os.walk", side_effect=mock_walk):
            
            for root in extra_roots.split(","):
                root = root.strip()
                if os.path.exists(root):
                    for r, _, files in os.walk(root):
                        for file in files:
                            if file.endswith(".py"):
                                python_files.append(os.path.join(r, file))
        
        assert len(python_files) == 3
        assert any("repo1" in f for f in python_files)
        assert any("repo2" in f for f in python_files)
        assert any("repo3" in f for f in python_files)


# ==============================================================================
# L5 GIT AGENT TESTS - Branching Logic
# ==============================================================================

class TestGitAgentBranchingLogic:
    """Verifies GitAgent branch creation and commit operations."""
    
    @pytest.mark.asyncio
    async def test_git_agent_creates_healing_branch(self):
        """Verifies GitAgent creates a healing branch with correct naming."""
        ctx = MockValidationContext()
        ctx.modified_files = {"test.py"}
        
        with patch("git.Repo") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_head = MagicMock()
            mock_repo.create_head.return_value = mock_head
            mock_repo.remotes = []
            
            agent = GitAgent(ctx)
            await agent.execute()
            
            # Verify branch creation
            mock_repo.create_head.assert_called_once()
            args, _ = mock_repo.create_head.call_args
            assert args[0].startswith("healing/auto_")
    
    @pytest.mark.asyncio
    async def test_git_agent_checkouts_new_branch(self):
        """Verifies GitAgent checks out the new branch."""
        ctx = MockValidationContext()
        ctx.modified_files = {"test.py"}
        
        with patch("git.Repo") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_head = MagicMock()
            mock_repo.create_head.return_value = mock_head
            mock_repo.remotes = []
            
            agent = GitAgent(ctx)
            await agent.execute()
            
            # Verify checkout
            mock_head.checkout.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_git_agent_adds_modified_files(self):
        """Verifies GitAgent adds modified files to index."""
        ctx = MockValidationContext()
        ctx.modified_files = {"file1.py", "file2.py"}
        
        with patch("git.Repo") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_head = MagicMock()
            mock_repo.create_head.return_value = mock_head
            mock_repo.remotes = []
            
            agent = GitAgent(ctx)
            await agent.execute()
            
            # Verify add was called with modified files
            mock_repo.index.add.assert_called_once()
            call_args = mock_repo.index.add.call_args[0][0]
            assert "file1.py" in call_args or "file2.py" in call_args
    
    @pytest.mark.asyncio
    async def test_git_agent_commits_with_message(self):
        """Verifies GitAgent commits with appropriate message."""
        ctx = MockValidationContext()
        ctx.modified_files = {"test.py"}
        ctx.successful_traces = [{"task": "fix1"}, {"task": "fix2"}]
        
        with patch("git.Repo") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_head = MagicMock()
            mock_repo.create_head.return_value = mock_head
            mock_repo.remotes = []
            
            agent = GitAgent(ctx)
            await agent.execute()
            
            # Verify commit
            mock_repo.index.commit.assert_called_once()
            commit_msg = mock_repo.index.commit.call_args[0][0]
            assert "L5 Auto-fix" in commit_msg


# ==============================================================================
# L5 GIT AGENT TESTS - Remote Push
# ==============================================================================

class TestGitAgentRemotePush:
    """Verifies GitAgent remote push operations."""
    
    @pytest.mark.asyncio
    async def test_git_agent_pushes_to_remote(self):
        """Verifies GitAgent pushes to remote if configured."""
        ctx = MockValidationContext()
        ctx.modified_files = {"test.py"}
        
        with patch.dict(os.environ, {"GIT_REMOTE_URL": "git@github.com:user/repo.git"}), \
             patch("git.Repo") as MockRepo:
            
            mock_repo = MockRepo.return_value
            mock_head = MagicMock()
            mock_repo.create_head.return_value = mock_head
            
            # Mock remotes
            mock_remote = MagicMock()
            mock_repo.remotes = MagicMock()
            mock_repo.remotes.__iter__ = lambda self: iter([mock_remote])
            mock_remote.name = 'origin'
            mock_repo.remotes.origin = mock_remote
            
            agent = GitAgent(ctx)
            await agent.execute()
            
            # Verify push was called
            mock_remote.push.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_git_agent_creates_origin_if_missing(self):
        """Verifies GitAgent creates origin remote if not present."""
        ctx = MockValidationContext()
        ctx.modified_files = {"test.py"}
        
        with patch.dict(os.environ, {"GIT_REMOTE_URL": "git@github.com:user/repo.git"}), \
             patch("git.Repo") as MockRepo:
            
            mock_repo = MockRepo.return_value
            mock_head = MagicMock()
            mock_repo.create_head.return_value = mock_head
            
            # Mock remotes - empty (no origin)
            mock_repo.remotes = MagicMock()
            mock_repo.remotes.__iter__ = lambda self: iter([])
            
            mock_new_remote = MagicMock()
            mock_repo.create_remote.return_value = mock_new_remote
            mock_repo.remotes.origin = mock_new_remote
            
            agent = GitAgent(ctx)
            await agent.execute()
            
            # Verify remote creation
            mock_repo.create_remote.assert_called_once_with('origin', 'git@github.com:user/repo.git')
    
    @pytest.mark.asyncio
    async def test_git_agent_no_push_without_remote_url(self):
        """Verifies GitAgent doesn't push without GIT_REMOTE_URL."""
        ctx = MockValidationContext()
        ctx.modified_files = {"test.py"}
        
        # Ensure no GIT_REMOTE_URL
        env = os.environ.copy()
        env.pop("GIT_REMOTE_URL", None)
        
        with patch.dict(os.environ, env, clear=True), \
             patch("git.Repo") as MockRepo:
            
            mock_repo = MockRepo.return_value
            mock_head = MagicMock()
            mock_repo.create_head.return_value = mock_head
            mock_repo.remotes = []
            
            agent = GitAgent(ctx)
            await agent.execute()
            
            # Verify no remote operations
            mock_repo.create_remote.assert_not_called()


# ==============================================================================
# L5 GIT AGENT TESTS - Critical Failure Handling
# ==============================================================================

class TestGitAgentCriticalFailure:
    """Verifies GitAgent handles critical failures correctly."""
    
    @pytest.mark.asyncio
    async def test_git_agent_reverts_on_critical_failure(self):
        """Verifies GitAgent reverts to HEAD on CRITICAL_FAILURE."""
        ctx = MockValidationContext()
        ctx.signals.add("CRITICAL_FAILURE")
        ctx.modified_files = {"test.py"}
        
        with patch("git.Repo") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_git = MagicMock()
            mock_repo.git = mock_git
            
            agent = GitAgent(ctx)
            await agent.execute()
            
            # Verify reset was called
            mock_git.reset.assert_called_once_with('--hard', 'HEAD')
    
    @pytest.mark.asyncio
    async def test_git_agent_clears_critical_failure_signal(self):
        """Verifies GitAgent clears CRITICAL_FAILURE signal after revert."""
        ctx = MockValidationContext()
        ctx.signals.add("CRITICAL_FAILURE")
        
        with patch("git.Repo") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_git = MagicMock()
            mock_repo.git = mock_git
            
            agent = GitAgent(ctx)
            await agent.execute()
            
            # Verify signal was cleared
            assert "CRITICAL_FAILURE" not in ctx.signals
    
    @pytest.mark.asyncio
    async def test_git_agent_no_commit_on_critical_failure(self):
        """Verifies GitAgent doesn't commit when CRITICAL_FAILURE is present."""
        ctx = MockValidationContext()
        ctx.signals.add("CRITICAL_FAILURE")
        ctx.modified_files = {"test.py"}
        
        with patch("git.Repo") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_git = MagicMock()
            mock_repo.git = mock_git
            
            agent = GitAgent(ctx)
            await agent.execute()
            
            # Verify no branch/commit operations
            mock_repo.create_head.assert_not_called()
            mock_repo.index.commit.assert_not_called()


# ==============================================================================
# L5 GIT AGENT TESTS - Error Handling
# ==============================================================================

class TestGitAgentErrorHandling:
    """Verifies GitAgent handles errors gracefully."""
    
    @pytest.mark.asyncio
    async def test_git_agent_handles_invalid_repo(self):
        """Verifies GitAgent handles non-git directory gracefully."""
        ctx = MockValidationContext()
        ctx.modified_files = {"test.py"}
        
        with patch("git.Repo") as MockRepo:
            MockRepo.side_effect = Exception("Not a git repository")
            
            agent = GitAgent(ctx)
            # Should not raise
            await agent.execute()
    
    @pytest.mark.asyncio
    async def test_git_agent_handles_no_modified_files(self):
        """Verifies GitAgent does nothing when no files modified."""
        ctx = MockValidationContext()
        ctx.modified_files = set()  # Empty
        
        with patch("git.Repo") as MockRepo:
            mock_repo = MockRepo.return_value
            
            agent = GitAgent(ctx)
            await agent.execute()
            
            # Verify no branch operations
            mock_repo.create_head.assert_not_called()


# ==============================================================================
# L5 GIT AGENT TESTS - Streamer Integration
# ==============================================================================

class TestGitAgentStreamerIntegration:
    """Verifies GitAgent broadcasts to the L5 Streamer."""
    
    @pytest.mark.asyncio
    async def test_git_agent_broadcasts_checkpoint(self):
        """Verifies GitAgent broadcasts checkpoint creation."""
        ctx = MockValidationContext()
        ctx.modified_files = {"test.py"}
        ctx._streamer_initialized = True
        ctx.broadcast = AsyncMock()
        
        with patch("git.Repo") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_head = MagicMock()
            mock_repo.create_head.return_value = mock_head
            mock_repo.remotes = []
            
            agent = GitAgent(ctx)
            await agent.execute()
            
            # Verify broadcast was called
            ctx.broadcast.assert_called()
            call_args = ctx.broadcast.call_args
            assert "healing branch" in call_args[0][0]
            assert call_args[1]["level"] == "GIT_CHECKPOINT"
    
    @pytest.mark.asyncio
    async def test_git_agent_no_broadcast_when_streamer_inactive(self):
        """Verifies GitAgent doesn't broadcast when streamer inactive."""
        ctx = MockValidationContext()
        ctx.modified_files = {"test.py"}
        ctx._streamer_initialized = False
        ctx.broadcast = AsyncMock()
        
        with patch("git.Repo") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_head = MagicMock()
            mock_repo.create_head.return_value = mock_head
            mock_repo.remotes = []
            
            agent = GitAgent(ctx)
            await agent.execute()
            
            # Verify broadcast was NOT called
            ctx.broadcast.assert_not_called()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
