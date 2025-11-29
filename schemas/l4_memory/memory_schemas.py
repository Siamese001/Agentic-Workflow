#!/usr/bin/env python3
"""
Memory Schemas
Section 10: Schema Layer - Schemas for L4 memory/state operations
"""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

from .base_schemas import BaseRequest, BaseResponse, ProcessingStatus

class MemoryType(str, Enum):
    """Memory type enumeration"""
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    WORKING = "working"
    LONG_TERM = "long_term"
    TEMPORAL = "temporal"

class StorageType(str, Enum):
    """Storage type enumeration"""
    MEMORY = "memory"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    KNOWLEDGE_GRAPH = "knowledge_graph"

class MemoryRequest(BaseRequest):
    """Request schema for memory operations"""
    memory_type: MemoryType = Field(..., description="Type of memory operation")
    operation: str = Field(..., description="Memory operation (store/retrieve/update/delete)")
    data: Optional[Dict[str, Any]] = Field(None, description="Data to store")
    query: Optional[str] = Field(None, description="Query for retrieval")
    storage_type: StorageType = Field(StorageType.MEMORY, description="Storage type")
    ttl_seconds: Optional[int] = Field(None, description="Time to live in seconds")

class MemoryResponse(BaseResponse):
    """Response schema for memory operations"""
    memory_id: str = Field(..., description="Memory identifier")
    memory_type: MemoryType = Field(..., description="Type of memory operation")
    operation: str = Field(..., description="Memory operation performed")
    result_data: Optional[Dict[str, Any]] = Field(None, description="Retrieved data")
    storage_location: str = Field(..., description="Storage location")
    timestamp: datetime = Field(default_factory=datetime.now, description="Operation timestamp")

class StateSnapshot(BaseModel):
    """State snapshot schema"""
    snapshot_id: str = Field(..., description="Snapshot identifier")
    workflow_id: str = Field(..., description="Workflow identifier")
    state_data: Dict[str, Any] = Field(..., description="State data")
    created_at: datetime = Field(default_factory=datetime.now, description="Snapshot creation time")
    version: str = Field(..., description="State version")
    checksum: str = Field(..., description="Data checksum")

class TemporalState(BaseModel):
    """Temporal state schema"""
    state_id: str = Field(..., description="State identifier")
    temporal_data: Dict[str, Any] = Field(..., description="Temporal data")
    valid_from: datetime = Field(..., description="Validity start time")
    valid_to: Optional[datetime] = Field(None, description="Validity end time")
    timeline_position: str = Field(..., description="Position in timeline")

class MemoryEntry(BaseModel):
    """Memory entry schema"""
    entry_id: str = Field(..., description="Entry identifier")
    memory_type: MemoryType = Field(..., description="Memory type")
    content: Dict[str, Any] = Field(..., description="Memory content")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Entry metadata")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation time")
    last_accessed: Optional[datetime] = Field(None, description="Last access time")
    access_count: int = Field(0, description="Access count")

class KnowledgeGraphEntry(BaseModel):
    """Knowledge graph entry schema"""
    node_id: str = Field(..., description="Node identifier")
    node_type: str = Field(..., description="Node type")
    properties: Dict[str, Any] = Field(..., description="Node properties")
    relationships: List[Dict[str, Any]] = Field(default_factory=list, description="Node relationships")
    embedding: Optional[List[float]] = Field(None, description="Node embedding vector")

class MemoryQuery(BaseModel):
    """Memory query schema"""
    query_id: str = Field(..., description="Query identifier")
    query_text: str = Field(..., description="Query text")
    memory_type: MemoryType = Field(..., description="Memory type to query")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Query filters")
    limit: int = Field(10, description="Maximum results to return")
    similarity_threshold: float = Field(0.7, description="Similarity threshold for vector search")

# Re-export memory schemas
__all__ = [
    'MemoryRequest', 'MemoryResponse', 'StateSnapshot', 'TemporalState',
    'MemoryEntry', 'KnowledgeGraphEntry', 'MemoryQuery',
    'MemoryType', 'StorageType'
]





