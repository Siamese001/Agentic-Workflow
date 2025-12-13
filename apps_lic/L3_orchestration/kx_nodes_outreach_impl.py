"""Implementation for kx_nodes_outreach."""

from typing import Any, Dict, List, Optional
from .kx_nodes_outreach_types import *

def get_outreach_kx_dag(connection_request: bool=False) -> Dict[str, OutreachKNode]:
    """Get the complete outreach K.X node DAG.
    
    Args:
        connection_request: Use connection request variants if True
        
    Returns:
        Dictionary of outreach K.X nodes with dependencies
    """
    dag = OUTREACH_KX_DAG.copy()
    if connection_request:
        dag['K.3_Message_Body'] = CONNECTION_REQUEST_VARIANTS['CONNECTION_REQ_K.3_COMPRESSED']
        dag['K.5_CTA_Generation'] = CONNECTION_REQUEST_VARIANTS['CONNECTION_REQ_K.5_MICRO']
    return dag

def get_outreach_execution_order(connection_request: bool=False) -> List[str]:
    """Get topological execution order for outreach K.X nodes.
    
    Args:
        connection_request: Use connection request variants if True
        
    Returns:
        List of node keys in execution order
    """
    dag = get_outreach_kx_dag(connection_request)
    in_degree = {node_key: 0 for node_key in dag}
    adjacency = {node_key: [] for node_key in dag}
    for node_key, node in dag.items():
        for dep in node.dependencies:
            if dep in dag:
                adjacency[dep].append(node_key)
                in_degree[node_key] += 1
    queue = [node for node, degree in in_degree.items() if degree == 0]
    order = []
    while queue:
        queue.sort(key=lambda k: dag[k].metadata.get('priority', 999))
        node = queue.pop(0)
        order.append(node)
        for neighbor in adjacency[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    if len(order) != len(dag):
        raise ValueError('Outreach K.X DAG contains cycles')
    return order

def get_outreach_kx_node(node_key: str, connection_request: bool=False) -> Optional[OutreachKNode]:
    """Get outreach K.X node by key.
    
    Args:
        node_key: Node key (e.g., "K.3_Message_Body")
        connection_request: Use connection request variant if True
        
    Returns:
        OutreachKNode or None if not found
    """
    dag = get_outreach_kx_dag(connection_request)
    return dag.get(node_key)

