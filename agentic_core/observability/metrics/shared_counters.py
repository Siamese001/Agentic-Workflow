# Shared counters for layer activation tracking
# This module provides a global counter for tracking layer activations across the system

layer_activation_counts = {
    "L0_maintenance": 0,
    "L1_cognition": 0,
    "L2_execution": 0,
    "L3_orchestration": 0,
    "L4_state": 0,
    "L5_safety": 0,
    "config": 0,
    "schemas": 0,
    "prompt_governance": 0,
    "observability": 0,
    "utils": 0,
    "apps_rg": 0,
    "apps_lic": 0,
    "apps_shared": 0
}

def increment_layer_activation(layer: str):
    """Increment activation count for a given layer"""
    if layer in layer_activation_counts:
        layer_activation_counts[layer] += 1
    else:
        layer_activation_counts[layer] = 1

def get_layer_counts() -> dict:
    """Get current layer activation counts"""
    return layer_activation_counts.copy()

def reset_layer_counts():
    """Reset all layer activation counts to zero"""
    for layer in layer_activation_counts:
        layer_activation_counts[layer] = 0
