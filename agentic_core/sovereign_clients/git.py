"""
SovereignGitClient - Audited Git Operations

Routes all Git operations through controlled plane with:
- Audit logging
- Safe subprocess execution
- Error handling with rollback support
"""
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L5_safety.healer_mixin import HealerMixin

Logger = logging.getLogger(__name__)


class SovereignGitClient(MCPHardenedMixin, HealerMixin):
    """Sovereign Git client - audit + safe exec for all Git operations."""
    
    def __init__(self, repo_root: Optional[Path] = None):
        """
        Initialize Git client.
        
        Args:
            repo_root: Repository root directory (defaults to cwd)
        """
        super().__init__()
        self.repo_root = repo_root or Path.cwd()
        self.audit_log: List[Dict[str, Any]] = []
        self._mcp_audit('init')
    
    def _audit(self, operation: str, payload: Dict[str, Any], result: Any) -> None:
        """Record operation to audit log."""
        self.audit_log.append({
            'operation': operation,
            'payload': {k: str(v)[:100] for k, v in payload.items()},
            'success': result.get('success', False) if isinstance(result, dict) else True
        })
    
    def _run_git(self, args: List[str]) -> Dict[str, Any]:
        """Execute git command safely."""
        cmd = ['git', '-C', str(self.repo_root)] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            return {
                'success': True,
                'stdout': result.stdout.strip(),
                'stderr': result.stderr.strip()
            }
        except subprocess.CalledProcessError as e:
            Logger.error(f"Git command failed: {' '.join(cmd)}")
            return {
                'success': False,
                'error': e.stderr,
                'returncode': e.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Git command timed out'
            }
    
    def execute(self, operation: str, **payload) -> Dict[str, Any]:
        """
        Route Git operations safely.
        
        Args:
            operation: Git operation (commit, push, pull, status, etc.)
            **payload: Operation-specific parameters
        
        Returns:
            Result dictionary with success status and output
        """
        Logger.debug(f"[SOVEREIGN GIT] {operation}: {payload}")
        
        if operation == 'commit':
            message = payload.get('message', 'Sovereign commit')
            files = payload.get('files', [])
            if files:
                for f in files:
                    self._run_git(['add', str(f)])
            result = self._run_git(['commit', '-m', message])
        
        elif operation == 'push':
            branch = payload.get('branch', 'HEAD')
            remote = payload.get('remote', 'origin')
            result = self._run_git(['push', remote, branch])
        
        elif operation == 'pull':
            remote = payload.get('remote', 'origin')
            branch = payload.get('branch', '')
            args = ['pull', remote]
            if branch:
                args.append(branch)
            result = self._run_git(args)
        
        elif operation == 'status':
            result = self._run_git(['status', '--porcelain'])
        
        elif operation == 'diff':
            file_path = payload.get('file', '')
            args = ['diff']
            if file_path:
                args.append(str(file_path))
            result = self._run_git(args)
        
        elif operation == 'log':
            count = payload.get('count', 10)
            result = self._run_git(['log', f'-{count}', '--oneline'])
        
        elif operation == 'checkout':
            branch = payload.get('branch', '')
            if not branch:
                return {'success': False, 'error': 'Branch required for checkout'}
            result = self._run_git(['checkout', branch])
        
        elif operation == 'branch':
            action = payload.get('action', 'list')
            if action == 'list':
                result = self._run_git(['branch', '-a'])
            elif action == 'create':
                name = payload.get('name', '')
                if not name:
                    return {'success': False, 'error': 'Branch name required'}
                result = self._run_git(['branch', name])
            else:
                return {'success': False, 'error': f'Unknown branch action: {action}'}
        
        else:
            result = {'success': False, 'error': f'Unsupported Git operation: {operation}'}
        
        self._audit(operation, payload, result)
        return result
