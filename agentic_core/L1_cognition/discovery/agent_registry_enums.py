"""Enum types for agent_registry."""

from enum import Enum

class AgentCapability(Enum):
    """Standard agent capabilities."""
    PLANNING = 'planning'
    REASONING = 'reasoning'
    TOOL_EXECUTION = 'tool_execution'
    CODE_GENERATION = 'code_generation'
    DATA_ANALYSIS = 'data_analysis'
    SEARCH = 'search'
    RETRIEVAL = 'retrieval'
    SUMMARIZATION = 'summarization'
    TRANSLATION = 'translation'
    ORCHESTRATION = 'orchestration'

class AgentStatus(Enum):
    """Agent operational status."""
    ACTIVE = 'active'
    IDLE = 'idle'
    BUSY = 'busy'
    OFFLINE = 'offline'
    MAINTENANCE = 'maintenance'

