"""Implementation for kx_nodes_resume."""

# from .kx_nodes_resume_types import *  # Star import removed

def get_resume_kx_dag() -> Dict[str, ResumeKNode]:
    """Get the complete resume K.X node DAG.

    Returns:
        Dictionary of resume K.X nodes with dependencies
    """
    return RESUME_KX_DAG.copy()

def get_resume_execution_order() -> List[str]:
    """Get topological execution order for resume K.X nodes.

    Returns:
        List of node keys in execution order
    """
    in_degree = {node_key: 0 for node_key in RESUME_KX_DAG}
    adjacency = {node_key: [] for node_key in RESUME_KX_DAG}
    for node_key, node in RESUME_KX_DAG.items():
        for dep in node.dependencies:
            if dep in RESUME_KX_DAG:
                adjacency[dep].append(node_key)
                in_degree[node_key] += 1
    queue = [node for node, degree in in_degree.items() if degree == 0]
    order = []
    while queue:
        queue.sort(key=lambda k: RESUME_KX_DAG[k].metadata.get('priority', 999))
        node = queue.pop(0)
        order.append(node)
        for neighbor in adjacency[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    if len(order) != len(RESUME_KX_DAG):
        raise ValueError('Resume K.X DAG contains cycles')
    return order

def get_resume_kx_node(node_key: str) -> Optional[ResumeKNode]:
    """Get resume K.X node by key.

    Args:
        node_key: Node key (e.g., "K.1_Executive_Summary")

    Returns:
        ResumeKNode or None if not found
    """
    return RESUME_KX_DAG.get(node_key)
