from __future__ import annotations
from dataclasses import dataclass
"""
Memory Manager - JSON Persistence for Canon Validator State

Handles loading and saving of validation state, conversation history,
and other persistent data structures.
"""
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin

@dataclass
class MemoryManagerAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """
    Manages JSON-based persistence for validation state.
    
    Features:
    - Load/save conversation history
    - Load/save validation results
    - Load/save agent state
    - Atomic writes with backup
    - Automatic directory creation
    """

    def __init__(self, base_dir: str=None) -> None:
        """
        Initialize memory manager.
        
        Args:
            base_dir: Base directory for memory files (default: .canon_memory/)
        """
        if base_dir is None:
            base_dir = os.path.join(os.getcwd(), '.canon_memory')
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.conversations_dir = self.base_dir / 'conversations'
        self.results_dir = self.base_dir / 'results'
        self.state_dir = self.base_dir / 'state'
        self.conversations_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)
        self.state_dir.mkdir(exist_ok=True)

    def load_conversation_history(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load conversation history for a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            List of conversation turns
        """
        safe_name: Any = self._sanitize_filename(file_path)
        history_file: Any = self.conversations_dir / f'{safe_name}.json'
        if not history_file.exists():
            return []
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f'[!] Failed to load conversation history for {file_path}: {e}')
            return []

    def save_conversation_history(self, file_path: str, history: List[Dict[str, Any]]) -> Any:
        """
        Save conversation history for a file.
        
        Args:
            file_path: Path to file
            history: List of conversation turns
        """
        safe_name: Any = self._sanitize_filename(file_path)
        history_file: Any = self.conversations_dir / f'{safe_name}.json'
        try:
            self._atomic_write(history_file, history)
        except Exception as e:
            print(f'[!] Failed to save conversation history for {file_path}: {e}')

    def clear_conversation_history(self, file_path: str) -> Any:
        """
        Clear conversation history for a file.
        
        Args:
            file_path: Path to file
        """
        safe_name: Any = self._sanitize_filename(file_path)
        history_file: Any = self.conversations_dir / f'{safe_name}.json'
        if history_file.exists():
            try:
                history_file.unlink()
            except Exception as e:
                print(f'[!] Failed to clear conversation history for {file_path}: {e}')

    def load_validation_results(self, session_id: str=None) -> Dict[str, Any]:
        """
        Load validation results.
        
        Args:
            session_id: Optional session ID (default: latest)
            
        Returns:
            Dictionary of validation results
        """
        if session_id is None:
            results_files: Any = sorted(self.results_dir.glob('results_*.json'))
            if not results_files:
                return {}
            results_file: Any = results_files[-1]
        else:
            results_file: Any = self.results_dir / f'results_{session_id}.json'
        if not results_file.exists():
            return {}
        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f'[!] Failed to load validation results: {e}')
            return {}

    def save_validation_results(self, results: Dict[str, Any], session_id: str=None) -> Any:
        """
        Save validation results.
        
        Args:
            results: Dictionary of validation results
            session_id: Optional session ID (default: timestamp)
        """
        if session_id is None:
            session_id: Any = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file: Any = self.results_dir / f'results_{session_id}.json'
        try:
            self._atomic_write(results_file, results)
        except Exception as e:
            print(f'[!] Failed to save validation results: {e}')

    def load_agent_state(self, agent_name: str) -> Dict[str, Any]:
        """
        Load state for a specific agent.
        
        Args:
            agent_name: Name of agent
            
        Returns:
            Dictionary of agent state
        """
        state_file: Any = self.state_dir / f'{agent_name.lower()}.json'
        if not state_file.exists():
            return {}
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f'[!] Failed to load state for {agent_name}: {e}')
            return {}

    def save_agent_state(self, agent_name: str, state: Dict[str, Any]) -> Any:
        """
        Save state for a specific agent.
        
        Args:
            agent_name: Name of agent
            state: Dictionary of agent state
        """
        state_file: Any = self.state_dir / f'{agent_name.lower()}.json'
        try:
            self._atomic_write(state_file, state)
        except Exception as e:
            print(f'[!] Failed to save state for {agent_name}: {e}')

    def load_memory(self, key: str, category: str='general') -> Optional[Any]:
        """
        Load arbitrary memory by key.
        
        Args:
            key: Memory key
            category: Memory category (subdirectory)
            
        Returns:
            Memory value or None
        """
        category_dir: Any = self.base_dir / category
        category_dir.mkdir(exist_ok=True)
        safe_key: Any = self._sanitize_filename(key)
        memory_file: Any = category_dir / f'{safe_key}.json'
        if not memory_file.exists():
            return None
        try:
            with open(memory_file, 'r', encoding='utf-8') as f:
                data: Any = json.load(f)
                return data.get('value')
        except Exception as e:
            print(f'[!] Failed to load memory {key}: {e}')
            return None

    def save_memory(self, key: str, value: Any, category: str='general') -> Any:
        """
        Save arbitrary memory by key.
        
        Args:
            key: Memory key
            value: Memory value (must be JSON-serializable)
            category: Memory category (subdirectory)
        """
        category_dir: Any = self.base_dir / category
        category_dir.mkdir(exist_ok=True)
        safe_key: Any = self._sanitize_filename(key)
        memory_file: Any = category_dir / f'{safe_key}.json'
        try:
            data: Any = {'key': key, 'value': value, 'timestamp': datetime.now().isoformat(), 'category': category}
            self._atomic_write(memory_file, data)
        except Exception as e:
            print(f'[!] Failed to save memory {key}: {e}')

    def delete_memory(self, key: str, category: str='general') -> Any:
        """
        Delete memory by key.
        
        Args:
            key: Memory key
            category: Memory category
        """
        category_dir: Any = self.base_dir / category
        safe_key: Any = self._sanitize_filename(key)
        memory_file: Any = category_dir / f'{safe_key}.json'
        if memory_file.exists():
            try:
                memory_file.unlink()
            except Exception as e:
                print(f'[!] Failed to delete memory {key}: {e}')

    def cleanup_old_memories(self, days: int=7) -> Any:
        """
        Clean up memories older than specified days.
        
        Args:
            days: Number of days to keep
        """
        cutoff_time: Any = datetime.now().timestamp() - days * 86400
        for category_dir in [self.conversations_dir, self.results_dir, self.state_dir]:
            for memory_file in category_dir.glob('*.json'):
                try:
                    if memory_file.stat().st_mtime < cutoff_time:
                        memory_file.unlink()
                        print(f'🗑️  Cleaned up old memory: {memory_file.name}')
                except Exception as e:
                    print(f'[!] Failed to cleanup {memory_file}: {e}')

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored memories.
        
        Returns:
            Dictionary of memory statistics
        """
        stats: Any = {'base_dir': str(self.base_dir), 'conversations': len(list(self.conversations_dir.glob('*.json'))), 'results': len(list(self.results_dir.glob('*.json'))), 'agent_states': len(list(self.state_dir.glob('*.json'))), 'total_size_mb': 0}
        total_size: Any = 0
        for file in self.base_dir.rglob('*.json'):
            try:
                total_size += file.stat().st_size
            except:
                pass
        stats['total_size_mb'] = round(total_size / (1024 * 1024), 2)
        return stats

    def _sanitize_filename(self, name: str) -> str:
        """
        Sanitize a string to be safe for use as filename.
        
        Args:
            name: Original name
            
        Returns:
            Sanitized name
        """
        safe = name.replace('/', '_').replace('\\', '_')
        safe = safe.replace(':', '_').replace('*', '_')
        safe = safe.replace('?', '_').replace('"', '_')
        safe = safe.replace('<', '_').replace('>', '_')
        safe = safe.replace('|', '_')
        if len(safe) > 200:
            safe = safe[:200]
        return safe

    def _atomic_write(self, file_path: Path, data: Any) -> Any:
        """
        Atomically write data to file with backup.
        
        Args:
            file_path: Path to file
            data: Data to write (will be JSON-serialized)
        """
        temp_file = file_path.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        if file_path.exists():
            backup_file = file_path.with_suffix('.bak')
            if backup_file.exists():
                backup_file.unlink()
            file_path.rename(backup_file)
        temp_file.rename(file_path)
        backup_file = file_path.with_suffix('.bak')
        if backup_file.exists():
            backup_file.unlink()

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L4 state agent - operational only."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L4 state - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

_memory_manager = None

def get_memory_manager(base_dir: str=None) -> MemoryManagerAgent:
    """
    # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
    super().heal_repository()

    Get or create global memory manager instance.
    
    Args:
        base_dir: Base directory for memory storage
        
    Returns:
        MemoryManagerAgent instance
    """
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManagerAgent(base_dir)
    return _memory_manager
