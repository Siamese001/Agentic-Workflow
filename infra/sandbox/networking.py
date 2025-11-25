from __future__ import annotations

from typing import Dict, List


def default_network_policy() -> Dict[str, object]:
    """Return the default network policy for sandboxed execution.

    By default all outbound network access is disabled.
    """

    return {
        "allow_network": False,
        "allowlist": [],
    }


def is_destination_allowed(policy: Dict[str, object], host: str) -> bool:
    if not policy.get("allow_network"):
        return False
    allowlist: List[str] = list(policy.get("allowlist", []) or [])
    return host in allowlist



