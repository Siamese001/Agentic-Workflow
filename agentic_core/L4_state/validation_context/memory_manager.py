"""
Memory Manager - JSON Persistence for Canon Validator State

Handles loading and saving of validation state, conversation history,
and other persistent data structures.
"""
from typing import Any, Optional, Protocol, Dict, List
import time
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

class MemoryManager:
    """
    Manages JSON-based persistence for validation state.
    
    Features:
    - Load/save conversation history
    - Load/save validation results
    - Load/save agent state
    - Atomic writes with backup
    - Automatic directory creation
    """
    
    def __init__(self, base_dir: str = None):
        """
        Initialize memory manager.
        
        Args:
            base_dir: Base directory for memory files (default: .canon_memory/)
        """
        if base_dir is None:
            base_dir = os.path.join(os.getcwd(), '.canon_memory')
        
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Subdirectories
        self.conversations_dir = self.base_dir / 'conversations'
        self.results_dir = self.base_dir / 'results'
        self.state_dir = self.base_dir / 'state'
        
        # Create subdirectories
        self.conversations_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)
        self.state_dir.mkdir(exist_ok=True)
    
    # ============================================================================
    # CONVERSATION HISTORY
    # ============================================================================
    
    def load_conversation_history(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load conversation history for a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            List of conversation turns
        """
        safe_name = self._sanitize_filename(file_path)
        history_file = self.conversations_dir / f"{safe_name}.json"
        
        if not history_file.exists():
            return []
        
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Failed to load conversation history for {file_path}: {e}")
            return []
    
    def save_conversation_history(self, file_path: str, history: List[Dict[str, Any]]):
        """
        Save conversation history for a file.
        
        Args:
            file_path: Path to file
            history: List of conversation turns
        """
        safe_name = self._sanitize_filename(file_path)
        history_file = self.conversations_dir / f"{safe_name}.json"
        
        try:
            self._atomic_write(history_file, history)
        except Exception as e:
            print(f"[!] Failed to save conversation history for {file_path}: {e}")
    
    def clear_conversation_history(self, file_path: str):
        """
        Clear conversation history for a file.
        
        Args:
            file_path: Path to file
        """
        safe_name = self._sanitize_filename(file_path)
        history_file = self.conversations_dir / f"{safe_name}.json"
        
        if history_file.exists():
            try:
                history_file.unlink()
            except Exception as e:
                print(f"[!] Failed to clear conversation history for {file_path}: {e}")
    
    # ============================================================================
    # VALIDATION RESULTS
    # ============================================================================
    
    def load_validation_results(self, session_id: str = None) -> Dict[str, Any]:
        """
        Load validation results.
        
        Args:
            session_id: Optional session ID (default: latest)
            
        Returns:
            Dictionary of validation results
        """
        if session_id is None:
            # Find latest results file
            results_files = sorted(self.results_dir.glob('results_*.json'))
            if not results_files:
                return {}
            results_file = results_files[-1]
        else:
            results_file = self.results_dir / f"results_{session_id}.json"
        
        if not results_file.exists():
            return {}
        
        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Failed to load validation results: {e}")
            return {}
    
    def save_validation_results(self, results: Dict[str, Any], session_id: str = None):
        """
        Save validation results.
        
        Args:
            results: Dictionary of validation results
            session_id: Optional session ID (default: timestamp)
        """
        if session_id is None:
            session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        results_file = self.results_dir / f"results_{session_id}.json"
        
        try:
            self._atomic_write(results_file, results)
        except Exception as e:
            print(f"[!] Failed to save validation results: {e}")
    
    # ============================================================================
    # AGENT STATE
    # ============================================================================
    
    def load_agent_state(self, agent_name: str) -> Dict[str, Any]:
        """
        Load state for a specific agent.
        
        Args:
            agent_name: Name of agent
            
        Returns:
            Dictionary of agent state
        """
        state_file = self.state_dir / f"{agent_name.lower()}.json"
        
        if not state_file.exists():
            return {}
        
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Failed to load state for {agent_name}: {e}")
            return {}
    
    def save_agent_state(self, agent_name: str, state: Dict[str, Any]):
        """
        Save state for a specific agent.
        
        Args:
            agent_name: Name of agent
            state: Dictionary of agent state
        """
        state_file = self.state_dir / f"{agent_name.lower()}.json"
        
        try:
            self._atomic_write(state_file, state)
        except Exception as e:
            print(f"[!] Failed to save state for {agent_name}: {e}")
    
    # ============================================================================
    # GENERIC MEMORY OPERATIONS
    # ============================================================================
    
    def load_memory(self, key: str, category: str = 'general') -> Optional[Any]:
        """
        Load arbitrary memory by key.
        
        Args:
            key: Memory key
            category: Memory category (subdirectory)
            
        Returns:
            Memory value or None
        """
        category_dir = self.base_dir / category
        category_dir.mkdir(exist_ok=True)
        
        safe_key = self._sanitize_filename(key)
        memory_file = category_dir / f"{safe_key}.json"
        
        if not memory_file.exists():
            return None
        
        try:
            with open(memory_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('value')
        except Exception as e:
            print(f"[!] Failed to load memory {key}: {e}")
            return None
    
    def save_memory(self, key: str, value: Any, category: str = 'general'):
        """
        Save arbitrary memory by key.
        
        Args:
            key: Memory key
            value: Memory value (must be JSON-serializable)
            category: Memory category (subdirectory)
        """
        category_dir = self.base_dir / category
        category_dir.mkdir(exist_ok=True)
        
        safe_key = self._sanitize_filename(key)
        memory_file = category_dir / f"{safe_key}.json"
        
        try:
            data = {
                'key': key,
                'value': value,
                'timestamp': datetime.now().isoformat(),
                'category': category
            }
            self._atomic_write(memory_file, data)
        except Exception as e:
            print(f"[!] Failed to save memory {key}: {e}")
    
    def delete_memory(self, key: str, category: str = 'general'):
        """
        Delete memory by key.
        
        Args:
            key: Memory key
            category: Memory category
        """
        category_dir = self.base_dir / category
        safe_key = self._sanitize_filename(key)
        memory_file = category_dir / f"{safe_key}.json"
        
        if memory_file.exists():
            try:
                memory_file.unlink()
            except Exception as e:
                print(f"[!] Failed to delete memory {key}: {e}")
    
    # ============================================================================
    # CLEANUP OPERATIONS
    # ============================================================================
    
    def cleanup_old_memories(self, days: int = 7):
        """
        Clean up memories older than specified days.
        
        Args:
            days: Number of days to keep
        """
        cutoff_time = datetime.now().timestamp() - (days * 86400)
        
        for category_dir in [self.conversations_dir, self.results_dir, self.state_dir]:
            for memory_file in category_dir.glob('*.json'):
                try:
                    if memory_file.stat().st_mtime < cutoff_time:
                        memory_file.unlink()
                        print(f"🗑️  Cleaned up old memory: {memory_file.name}")
                except Exception as e:
                    print(f"[!] Failed to cleanup {memory_file}: {e}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored memories.
        
        Returns:
            Dictionary of memory statistics
        """
        stats = {
            'base_dir': str(self.base_dir),
            'conversations': len(list(self.conversations_dir.glob('*.json'))),
            'results': len(list(self.results_dir.glob('*.json'))),
            'agent_states': len(list(self.state_dir.glob('*.json'))),
            'total_size_mb': 0
        }
        
        # Calculate total size
        total_size = 0
        for file in self.base_dir.rglob('*.json'):
            try:
                total_size += file.stat().st_size
            except:
                pass
        
        stats['total_size_mb'] = round(total_size / (1024 * 1024), 2)
        
        return stats
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def _sanitize_filename(self, name: str) -> str:
        """
        Sanitize a string to be safe for use as filename.
        
        Args:
            name: Original name
            
        Returns:
            Sanitized name
        """
        # Replace path separators and special characters
        safe = name.replace('/', '_').replace('\\', '_')
        safe = safe.replace(':', '_').replace('*', '_')
        safe = safe.replace('?', '_').replace('"', '_')
        safe = safe.replace('<', '_').replace('>', '_')
        safe = safe.replace('|', '_')
        
        # Limit length
        if len(safe) > 200:
            safe = safe[:200]
        
        return safe
    
    def _atomic_write(self, file_path: Path, data: Any):
        """
        Atomically write data to file with backup.
        
        Args:
            file_path: Path to file
            data: Data to write (will be JSON-serialized)
        """
        # Write to temporary file first
        temp_file = file_path.with_suffix('.tmp')
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Create backup if original exists
        if file_path.exists():
            backup_file = file_path.with_suffix('.bak')
            if backup_file.exists():
                backup_file.unlink()
            file_path.rename(backup_file)
        
        # Move temp to final location
        temp_file.rename(file_path)
        
        # Remove backup on success
        backup_file = file_path.with_suffix('.bak')
        if backup_file.exists():
            backup_file.unlink()


# Global instance for easy access
_memory_manager = None

def get_memory_manager(base_dir: str = None) -> MemoryManager:
    """
    Get or create global memory manager instance.
    
    Args:
        base_dir: Base directory for memory files
        
    Returns:
        MemoryManager instance
    """
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager(base_dir)
    return _memory_manager
