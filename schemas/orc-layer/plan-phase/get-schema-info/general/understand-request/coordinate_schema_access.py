"""
Schema definitions for schema access coordination and management.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class AccessMode(Enum):
    """Schema access coordination modes."""
    EXCLUSIVE = "exclusive"
    SHARED_READ = "shared_read"
    SHARED_WRITE = "shared_write"
    OPTIMISTIC = "optimistic"


class CoordinationStrategy(Enum):
    """Access coordination strategies."""
    LOCK_BASED = "lock_based"
    VERSION_BASED = "version_based"
    QUEUE_BASED = "queue_based"
    TOKEN_BASED = "token_based"


@dataclass
class AccessRequest:
    """Schema for individual access request."""
    request_id: str
    requester_id: str
    schema_id: str
    access_mode: AccessMode
    duration_seconds: int
    priority: str


@dataclass
class CoordinationPolicy:
    """Schema for access coordination policy."""
    policy_id: str
    strategy: CoordinationStrategy
    max_concurrent_access: int
    timeout_seconds: int
    conflict_resolution: str


@dataclass
class CoordinationResult:
    """Schema for coordination operation results."""
    coordination_id: str
    access_granted: bool
    granted_requests: List[str]
    denied_requests: List[str]
    coordination_metadata: Dict[str, Any]
