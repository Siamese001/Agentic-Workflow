"""
Integration hook for layer activation tracking
This module provides decorators and utilities to automatically track layer activations
"""

from functools import wraps
from agentic_core.observability.metrics.shared_counters import increment_layer_activation

def track_layer_activation(layer_name: str):
    """
    Decorator to automatically track layer activations
    
    Args:
        layer_name: Name of the layer to track
    
    Usage:
        @track_layer_activation("L3_orchestration")
        def orchestrate_workflow():
            # Your orchestration logic here
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Increment activation counter before execution
            increment_layer_activation(layer_name)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def manual_track(layer_name: str):
    """
    Manually track a layer activation (for cases where decorator isn't suitable)
    
    Args:
        layer_name: Name of the layer to track
    """
    increment_layer_activation(layer_name)

# Layer mapping helper
LAYER_MAPPING = {
    "maintenance": "L0_maintenance",
    "cognition": "L1_cognition", 
    "execution": "L2_execution",
    "orchestration": "L3_orchestration",
    "state": "L4_state",
    "safety": "L5_safety",
    "validator": "L5_safety",
    "guardrail": "L5_safety",
    "config": "config",
    "schema": "schemas",
    "prompt": "prompt_governance",
    "observability": "observability",
    "metric": "observability",
    "util": "utils",
    "app_rg": "apps_rg",
    "app_lic": "apps_lic",
    "app_shared": "apps_shared"
}

def infer_layer_from_agent_name(agent_name: str) -> str:
    """
    Infer layer name from agent class name or file path
    
    Args:
        agent_name: Agent class name or file path
        
    Returns:
        Layer name or "unknown" if no match found
    """
    agent_lower = agent_name.lower()
    
    for keyword, layer in LAYER_MAPPING.items():
        if keyword in agent_lower:
            return layer
    
    return "unknown"

def track_agent_activation(agent_class_name: str):
    """
    Track activation based on agent class name
    
    Args:
        agent_class_name: Name of the agent class
    """
    layer = infer_layer_from_agent_name(agent_class_name)
    if layer != "unknown":
        increment_layer_activation(layer)
    else:
        # Log unknown agent for tracking purposes
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Unknown layer for agent: {agent_class_name}")
