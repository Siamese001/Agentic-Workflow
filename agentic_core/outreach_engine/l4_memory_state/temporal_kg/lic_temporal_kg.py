# LIC Temporal Knowledge Graph for L4 memory state
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TemporalNode:
    """Temporal knowledge graph node"""
    node_id: str = ""
    data: Dict[str, Any] = None
    timestamp: datetime = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}

class LICTemporalKG:
    """Temporal knowledge graph for outreach memory"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.nodes = {}

    def add_node(self, node_id: str, data: Dict[str, Any], timestamp: datetime = None) -> TemporalNode:
        """Add temporal node to knowledge graph"""
        node = TemporalNode(
            node_id=node_id,
            data=data,
            timestamp=timestamp or datetime.now()
        )
        self.nodes[node_id] = node
        return node

    def get_node(self, node_id: str) -> Optional[TemporalNode]:
        """Get temporal node by ID"""
        return self.nodes.get(node_id)

    def query_temporal_range(self, start_time: datetime, end_time: datetime) -> List[TemporalNode]:
        """Query nodes within temporal range"""
        return [
            node for node in self.nodes.values()
            if start_time <= node.timestamp <= end_time
        ]
