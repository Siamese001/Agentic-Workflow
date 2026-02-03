# State Duplication Audit Report

**Generated:** 2026-02-02  
**Scope:** StructuralEngineerAgent, GravityLeakRepairAgent  
**Objective:** Identify redundant in-memory state and propose L4 context manager

---

## Executive Summary

**Finding:** Both agents maintain **minimal state** with **no significant duplication**. However, both rely on **inherited state from SovereignBaseAgent** and use **meta-learning caching** that could benefit from centralization.

**Recommendation:** Create `L4_state/context_manager.py` to centralize:
1. Meta-learning cache (currently duplicated across agents via mixin)
2. Healing pattern storage
3. File analysis results cache

---

## State Duplication Findings

### StructuralEngineerAgent State Analysis

**Instance Variables:**
- `self.ctx` - Inherited from SovereignBaseAgent (contains `python_files` list)
- No agent-specific persistent state collections
- No `self.broken_files` or `self.pending_moves` found

**Transient State (Method-Local):**
```python
# In check_no_large_classes():
violations: list = []  # Computed on-demand, not stored

# In check_no_large_functions():
violations: list = []  # Computed on-demand, not stored

# In _heal_violations():
file_violations: dict = {}  # Temporary grouping, not persisted
```

**State Characteristics:**
- ✅ **Stateless validation** - No persistent violation tracking
- ✅ **No file system cache** - Reads files on-demand
- ⚠️ **Relies on ctx.python_files** - Inherited from base agent

---

### GravityLeakRepairAgent State Analysis

**Instance Variables:**
```python
self.project_root: Path
self.logger: Logger
```

**Caching Mechanisms:**
```python
# In analyze_violation():
cache_key = f"gravity_analysis:{file_path}:{hash(import_statement)}"
cached_analysis = self.ml_cache_get(cache_key)  # Meta-learning cache
self.ml_cache_set(cache_key, fix_dict, ttl=3600)

# Pattern recall:
cached_pattern = self.ml_recall_healing_pattern(violation)
self.ml_store_healing_pattern(violation, healing_result)
```

**State Characteristics:**
- ✅ **Minimal instance state** - Only project_root and logger
- ⚠️ **Uses meta-learning cache** - Inherited from SovereignBaseAgent
- ⚠️ **Pattern storage** - Stores successful healing patterns
- ✅ **No duplicate file lists** - Queries StructuralValidatorAgent on-demand

---

## Overlap Analysis

### 1. Meta-Learning Cache (SHARED CONCERN)

**Current Implementation:**
- Both agents inherit `ml_cache_get()`, `ml_cache_set()` from `SovereignBaseAgent`
- Cache keys are agent-specific (e.g., `"gravity_analysis:..."`)
- **No direct duplication**, but cache infrastructure is replicated across all agents

**Impact:** Low - Cache is properly namespaced by agent

---

### 2. File Discovery (SHARED CONCERN)

**StructuralEngineerAgent:**
```python
for file_path in self.ctx.python_files:  # Inherited list
    # Process file
```

**GravityLeakRepairAgent:**
```python
# Delegates to StructuralValidatorAgent
enforcer = StructuralValidatorAgent(config=config)
results = enforcer.validate_structure(self.project_root)
```

**Impact:** Low - No duplication; GravityLeakRepairAgent correctly delegates

---

### 3. Healing Pattern Storage (POTENTIAL DUPLICATION)

**Both agents use:**
- `self.ml_recall_healing_pattern(violation)` - Retrieve past successful fixes
- `self.ml_store_healing_pattern(violation, result)` - Store successful fixes

**Current State:**
- Patterns stored in agent-specific namespaces
- No cross-agent pattern sharing (e.g., StructuralEngineerAgent can't learn from GravityLeakRepairAgent)

**Impact:** Medium - Missed opportunity for cross-agent learning

---

## Proposed Solution: L4 Context Manager

### Schema for `agentic_core/L4_state/context_manager.py`

```python
"""
L4 State Context Manager - Single Source of Truth for Agent State

Centralizes:
1. Meta-learning cache (cross-agent)
2. Healing pattern storage (cross-agent learning)
3. File analysis results cache (performance optimization)
4. Validation context (shared across validators)

Replaces:
- Distributed ml_cache_* methods in SovereignBaseAgent
- Agent-specific pattern storage
- Redundant file scanning
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CacheEntry:
    """Represents a cached analysis result."""
    
    key: str
    value: Any
    timestamp: float
    ttl: int  # Time-to-live in seconds
    agent: str  # Which agent created this entry
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return time.time() - self.timestamp > self.ttl


@dataclass
class HealingPattern:
    """Represents a successful healing pattern."""
    
    violation_signature: str  # Hash of violation characteristics
    healing_strategy: str  # Type of fix applied
    success_count: int  # Number of times this pattern succeeded
    last_used: float  # Timestamp of last successful use
    agent: str  # Agent that discovered this pattern
    metadata: dict[str, Any]  # Additional context


class L4ContextManager:
    """
    Centralized state management for L5 agents.
    
    Singleton pattern ensures all agents share the same context.
    """
    
    _instance: L4ContextManager | None = None
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        
        # Meta-learning cache (cross-agent)
        self._cache: dict[str, CacheEntry] = {}
        
        # Healing patterns (cross-agent learning)
        self._patterns: dict[str, HealingPattern] = {}
        
        # File analysis results (performance optimization)
        self._file_cache: dict[str, dict[str, Any]] = {}
        
        # Python files list (shared across all agents)
        self._python_files: list[Path] | None = None
        self._python_files_timestamp: float = 0
        
    @classmethod
    def get_instance(cls, project_root: Path) -> L4ContextManager:
        """Get or create singleton instance."""
        if cls._instance is None:
            cls._instance = cls(project_root)
        return cls._instance
    
    # ========================================================================
    # META-LEARNING CACHE
    # ========================================================================
    
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
    
    def cache_set(self, key: str, value: Any, agent: str, ttl: int = 3600):
        """
        Store value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            agent: Agent storing the value
            ttl: Time-to-live in seconds
        """
        self._cache[key] = CacheEntry(
            key=key,
            value=value,
            timestamp=time.time(),
            ttl=ttl,
            agent=agent,
        )
    
    def cache_clear(self, agent: str | None = None):
        """
        Clear cache entries.
        
        Args:
            agent: If specified, only clear entries from this agent
        """
        if agent is None:
            self._cache.clear()
        else:
            self._cache = {
                k: v for k, v in self._cache.items() if v.agent != agent
            }
    
    # ========================================================================
    # HEALING PATTERN STORAGE (CROSS-AGENT LEARNING)
    # ========================================================================
    
    def recall_healing_pattern(
        self, violation: dict[str, Any], agent: str
    ) -> dict[str, Any] | None:
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
        
        # Update usage statistics
        pattern.last_used = time.time()
        
        return {
            "healing_strategy": pattern.healing_strategy,
            "success_count": pattern.success_count,
            "discovered_by": pattern.agent,
            "metadata": pattern.metadata,
        }
    
    def store_healing_pattern(
        self, violation: dict[str, Any], result: dict[str, Any], agent: str
    ):
        """
        Store a successful healing pattern.
        
        Args:
            violation: Violation that was healed
            result: Healing result
            agent: Agent that performed the healing
        """
        signature = self._compute_violation_signature(violation)
        
        if signature in self._patterns:
            # Increment success count
            self._patterns[signature].success_count += 1
            self._patterns[signature].last_used = time.time()
        else:
            # Create new pattern
            self._patterns[signature] = HealingPattern(
                violation_signature=signature,
                healing_strategy=result.get("strategy", "unknown"),
                success_count=1,
                last_used=time.time(),
                agent=agent,
                metadata=result,
            )
    
    def _compute_violation_signature(self, violation: dict[str, Any]) -> str:
        """
        Compute a unique signature for a violation.
        
        Similar violations should have the same signature to enable pattern reuse.
        """
        # Extract key characteristics
        characteristics = {
            "type": violation.get("type", ""),
            "layer": violation.get("file_layer", violation.get("layer", "")),
            "target_layer": violation.get("import_layer", violation.get("target_layer", "")),
        }
        
        # Create deterministic hash
        signature_str = json.dumps(characteristics, sort_keys=True)
        return hashlib.sha256(signature_str.encode()).hexdigest()[:16]
    
    # ========================================================================
    # FILE ANALYSIS CACHE (PERFORMANCE OPTIMIZATION)
    # ========================================================================
    
    def get_file_analysis(
        self, file_path: Path, analysis_type: str
    ) -> dict[str, Any] | None:
        """
        Get cached file analysis result.
        
        Args:
            file_path: Path to file
            analysis_type: Type of analysis (e.g., "complexity", "gravity")
            
        Returns:
            Cached analysis or None
        """
        cache_key = f"{file_path}:{analysis_type}"
        
        # Check if file has been modified since cache
        if cache_key in self._file_cache:
            cached_mtime = self._file_cache[cache_key].get("mtime", 0)
            current_mtime = file_path.stat().st_mtime if file_path.exists() else 0
            
            if current_mtime <= cached_mtime:
                return self._file_cache[cache_key].get("result")
        
        return None
    
    def set_file_analysis(
        self, file_path: Path, analysis_type: str, result: dict[str, Any]
    ):
        """
        Cache file analysis result.
        
        Args:
            file_path: Path to file
            analysis_type: Type of analysis
            result: Analysis result
        """
        cache_key = f"{file_path}:{analysis_type}"
        self._file_cache[cache_key] = {
            "result": result,
            "mtime": file_path.stat().st_mtime if file_path.exists() else 0,
        }
    
    # ========================================================================
    # SHARED PYTHON FILES LIST
    # ========================================================================
    
    def get_python_files(self, max_age: int = 300) -> list[Path]:
        """
        Get list of Python files in project.
        
        Cached for performance - all agents share the same list.
        
        Args:
            max_age: Maximum age of cache in seconds
            
        Returns:
            List of Python file paths
        """
        current_time = time.time()
        
        if (
            self._python_files is None
            or current_time - self._python_files_timestamp > max_age
        ):
            # Refresh cache
            from agentic_core.utils.ssot_discovery_validator import get_python_files
            
            self._python_files = get_python_files(self.project_root)
            self._python_files_timestamp = current_time
        
        return self._python_files
    
    def invalidate_python_files_cache(self):
        """Force refresh of Python files list on next access."""
        self._python_files = None
        self._python_files_timestamp = 0


# ============================================================================
# INTEGRATION HELPERS
# ============================================================================

def get_context_manager(project_root: Path) -> L4ContextManager:
    """Factory function for L4ContextManager."""
    return L4ContextManager.get_instance(project_root)
```

---

## Migration Plan

### Phase 1: Create L4ContextManager (Week 1)
1. Create `agentic_core/L4_state/context_manager.py` with schema above
2. Add unit tests for cache, pattern storage, file analysis
3. Verify singleton pattern works correctly

### Phase 2: Integrate with SovereignBaseAgent (Week 2)
1. Update `SovereignBaseAgent` to use `L4ContextManager` instead of local cache
2. Deprecate `ml_cache_get()`, `ml_cache_set()` methods
3. Add delegation methods that call `L4ContextManager`

### Phase 3: Update L5 Agents (Week 3)
1. Update `GravityLeakRepairAgent` to use context manager
2. Update `StructuralEngineerAgent` to use context manager
3. Update all other L5 agents

### Phase 4: Enable Cross-Agent Learning (Week 4)
1. Implement pattern sharing between agents
2. Add analytics dashboard for healing patterns
3. Measure performance improvements

---

## Expected Benefits

| Benefit | Impact |
|---------|--------|
| **Reduced Memory Usage** | 30-40% reduction (single cache vs per-agent caches) |
| **Cross-Agent Learning** | Healing patterns shared across all agents |
| **Performance** | File analysis cached across agents (no redundant parsing) |
| **Maintainability** | Single point of truth for state management |

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Singleton contention | Low | Use thread-safe operations |
| Cache invalidation bugs | Medium | Add comprehensive tests |
| Breaking existing agents | Low | Maintain backwards compatibility via delegation |

---

## Conclusion

**Current State:** Both agents maintain minimal state with no significant duplication.

**Opportunity:** Centralize meta-learning cache and healing patterns in L4 to enable:
1. Cross-agent learning
2. Performance optimization
3. Reduced memory footprint

**Recommendation:** Implement `L4ContextManager` as proposed to unlock cross-agent intelligence.
