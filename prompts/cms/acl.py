from __future__ import annotations

from typing import Dict, Set


# Simple role → allowed actions mapping for prompt governance.
# Actions are generic strings like "create", "update", "approve".


_ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    "engineer": {"create", "update"},
    "designer": {"create", "update"},
    "reviewer": {"approve", "view"},
    "admin": {"create", "update", "approve", "view", "delete"},
}


def check_access(role: str, action: str) -> bool:
    """Return True if the given role is allowed to perform action.

    Unknown roles default to no access.
    """

    actions = _ROLE_PERMISSIONS.get(role.lower())
    if not actions:
        return False
    return action in actions
