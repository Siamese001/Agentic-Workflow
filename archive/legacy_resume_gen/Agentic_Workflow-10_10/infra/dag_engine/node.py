"""
DAG node model for résumé processing workflow orchestration.

Provides agent-aware node definitions for comprehensive résumé improvement operations.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DAGNode(BaseModel):
    """
    Represents agent-aware DAG node for résumé processing workflows.

    Defines declarative node structure for optimal résumé enhancement orchestration.
    """

    id: str
    type: str
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    config: Dict[str, Any] = Field(default_factory=dict)
    agent_type: Optional[str] = None
    required_capabilities: List[str] = Field(default_factory=list)
    preferred_agent_ids: List[str] = Field(default_factory=list)



