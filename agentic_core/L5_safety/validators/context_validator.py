"""
L4 State Context Manager - Single Source of Truth for Agent State

Centralizes:
1. Meta-learning cache (cross-agent)
2. Healing pattern storage (cross-agent learning)
3. File analysis results cache (performance optimization)

Replaces:
- Distributed ml_cache_* methods in SovereignBaseAgent
- Agent-specific pattern storage
- Redundant file scanning

Usage:
    from agentic_core.L4_state.utils.context_manager import get_context_manager

    ctx = get_context_manager(project_root)

    # Cache analysis results
    ctx.cache_set("complexity:file.py", result, agent="GovernanceAgent")
    cached = ctx.cache_get("complexity:file.py", agent="GovernanceAgent")

    # Store/recall healing patterns
    ctx.store_healing_pattern(violation, result, agent="GravityLeakRepairAgent")
    pattern = ctx.recall_healing_pattern(violation, agent="StructuralEngineerAgent")
"""
from __future__ import annotations
import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

@dataclass
class CacheEntry:
    """Represents a cached analysis result."""
    key: str
    value: Any
    timestamp: float
    ttl: int
    agent: str

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return time.time() - self.timestamp > self.ttl

@dataclass
class HealingPattern:
    """Represents a successful healing pattern."""
    violation_signature: str
    healing_strategy: str
    success_count: int
    last_used: float
    agent: str
    metadata: dict[str, Any]

class L4ContextManager:
    """
    Centralized state management for L5 agents.

    Singleton pattern ensures all agents share the same context.
    Enables cross-agent learning and eliminates redundant state.
    """
    _instance: L4ContextManager | None = None
    _lock: bool = False

    def __init__(self, project_root: Path):
        if L4ContextManager._instance is not None:
            raise RuntimeError('Use get_context_manager() to get singleton instance')
        self.project_root = project_root
        self._cache: dict[str, CacheEntry] = {}
        self._patterns: dict[str, HealingPattern] = {}
        self._file_cache: dict[str, dict[str, Any]] = {}
        self._python_files: list[Path] | None = None
        self._python_files_timestamp: float = 0

    @classmethod
    def get_instance(cls, project_root: Path) -> L4ContextManager:
        """Get or create singleton instance."""
        if cls._instance is None:
            cls._instance = cls(project_root)
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Reset singleton (for testing only)."""
        cls._instance = None

    def cache_get(self, key: str, agent: str) -> Any | None:
        """
        Retrieve cached value.

        Args:
            key: Cache key
            agent: Agent requesting the value

        Returns:
            Cached value or None if not found/expired
        """
        entry = self._cache.get(key)
        if entry is None:
            return None
        if entry.is_expired():
            del self._cache[key]
            return None
        return entry.value

    def cache_set(self, key: str, value: Any, agent: str, ttl: int=3600):
        """
        Store value in cache.

        Args:
            key: Cache key
            value: Value to cache
            agent: Agent storing the value
            ttl: Time-to-live in seconds (default 1 hour)
        """
        self._cache[key] = CacheEntry(key=key, value=value, timestamp=time.time(), ttl=ttl, agent=agent)

    def cache_clear(self, agent: str | None=None):
        """
        Clear cache entries.

        Args:
            agent: If specified, only clear entries from this agent
        """
        if agent is None:
            self._cache.clear()
        else:
            self._cache = {k: v for k, v in self._cache.items() if v.agent != agent}

    def recall_healing_pattern(self, violation: dict[str, Any], agent: str) -> dict[str, Any] | None:
        """
        Recall a successful healing pattern.

        Enables cross-agent learning: If GravityLeakRepairAgent successfully
        fixed a similar violation, StructuralEngineerAgent can reuse that pattern.

        Args:
            violation: Violation characteristics
            agent: Agent requesting the pattern

        Returns:
            Healing pattern metadata or None
        """
        signature = self._compute_violation_signature(violation)
        pattern = self._patterns.get(signature)
        if pattern is None:
            return None
        pattern.last_used = time.time()
        return {'healing_strategy': pattern.healing_strategy, 'success_count': pattern.success_count, 'discovered_by': pattern.agent, 'metadata': pattern.metadata}

    def store_healing_pattern(self, violation: dict[str, Any], result: dict[str, Any], agent: str):
        """
        Store a successful healing pattern.

        Args:
            violation: Violation that was healed
            result: Healing result
            agent: Agent that performed the healing
        """
        signature = self._compute_violation_signature(violation)
        if signature in self._patterns:
            self._patterns[signature].success_count += 1
            self._patterns[signature].last_used = time.time()
        else:
            self._patterns[signature] = HealingPattern(violation_signature=signature, healing_strategy=result.get('strategy', result.get('fix_type', 'unknown')), success_count=1, last_used=time.time(), agent=agent, metadata=result)

    def _compute_violation_signature(self, violation: dict[str, Any]) -> str:
        """
        Compute a unique signature for a violation.

        Similar violations should have the same signature to enable pattern reuse.
        """
        characteristics = {'type': violation.get('type', ''), 'layer': violation.get('file_layer', violation.get('layer', '')), 'target_layer': violation.get('import_layer', violation.get('target_layer', ''))}
        signature_str = json.dumps(characteristics, sort_keys=True)
        return hashlib.sha256(signature_str.encode()).hexdigest()[:16]

    def get_file_analysis(self, file_path: Path, analysis_type: str) -> dict[str, Any] | None:
        """
        Get cached file analysis result.

        Args:
            file_path: Path to file
            analysis_type: Type of analysis (e.g., "complexity", "gravity")

        Returns:
            Cached analysis or None
        """
        cache_key = f'{file_path}:{analysis_type}'
        if cache_key in self._file_cache:
            cached_mtime = self._file_cache[cache_key].get('mtime', 0)
            current_mtime = file_path.stat().st_mtime if file_path.exists() else 0
            if current_mtime <= cached_mtime:
                return self._file_cache[cache_key].get('result')
        return None

    def set_file_analysis(self, file_path: Path, analysis_type: str, result: dict[str, Any]):
        """
        Cache file analysis result.

        Args:
            file_path: Path to file
            analysis_type: Type of analysis
            result: Analysis result
        """
        cache_key = f'{file_path}:{analysis_type}'
        self._file_cache[cache_key] = {'result': result, 'mtime': file_path.stat().st_mtime if file_path.exists() else 0}

    # guardian: allow-magic-config
    def get_python_files(self, max_age: int=300) -> list[Path]:
        """
        Get list of Python files in project.

        Cached for performance - all agents share the same list.

        Args:
            max_age: Maximum age of cache in seconds (default 5 minutes)

        Returns:
            List of Python file paths
        """
        current_time = time.time()
        if self._python_files is None or current_time - self._python_files_timestamp > max_age:
            from agentic_core.utils.ssot_discovery_validator import get_python_files
            self._python_files = get_python_files(self.project_root)
            self._python_files_timestamp = current_time
        return self._python_files

    def invalidate_python_files_cache(self):
        """Force refresh of Python files list on next access."""
        self._python_files = None
        self._python_files_timestamp = 0

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about context manager usage."""
        return {'cache_entries': len(self._cache), 'healing_patterns': len(self._patterns), 'file_analyses': len(self._file_cache), 'python_files_cached': self._python_files is not None}

def get_context_manager(project_root: Path | str) -> L4ContextManager:
    """
    Factory function for L4ContextManager.

    Args:
        project_root: Path to project root

    Returns:
        Singleton L4ContextManager instance
    """
    if isinstance(project_root, str):
        project_root = Path(project_root)
    return L4ContextManager.get_instance(project_root)
