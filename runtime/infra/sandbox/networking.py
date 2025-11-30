# Network isolation and policy management for sandbox
from typing import Dict, Any, List

def default_network_policy() -> Dict[str, Any]:
    """Create a default network policy that denies all external access"""
    return {
        "allow_outbound": False,
        "allow_inbound": False,
        "allowed_domains": [],
        "allowed_ports": [],
        "blocked_domains": ["*"],
        "dns_servers": ["8.8.8.8", "8.8.4.4"],
        "proxy": None
    }

def is_destination_allowed(policy: Dict[str, Any], destination: str) -> bool:
    """Check if a destination is allowed under the given network policy"""
    # Check allowlist first (highest priority - overrides allow_outbound)
    allowlist = policy.get("allowlist", [])
    if allowlist and destination in allowlist:
        return True
    
    # Then check outbound permission
    if not policy.get("allow_outbound", False):
        return False
    
    allowed_domains = policy.get("allowed_domains", [])
    if allowed_domains and destination in allowed_domains:
        return True
    
    blocked_domains = policy.get("blocked_domains", [])
    if "*" in blocked_domains:
        return False
    
    return destination not in blocked_domains
