"""
L4 Memory Unit Tests
Tests for individual memory components
"""

import pytest
from agentic_core.l4_memory import (
    ShortTermMemory, LongTermMemory, StateManager
)


class TestMemoryComponents:
    """Test memory functionality"""
    
    def test_short_term_memory_init(self):
        """Test ShortTermMemory initialization"""
        memory = ShortTermMemory()
        assert memory is not None
    
    def test_long_term_memory_init(self):
        """Test LongTermMemory initialization"""
        memory = LongTermMemory()
        assert memory is not None
    
    def test_state_manager_init(self):
        """Test StateManager initialization"""
        manager = StateManager()
        assert manager is not None
