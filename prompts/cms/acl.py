from __future__ import annotations

from enum import Enum
from typing import Dict, Set


# Simple role → allowed actions mapping for prompt governance.
# Actions are generic strings like "create", "update", "approve".


_ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    "engineer": {"create", "update"},
    "designer": {"create", "update"},
    "reviewer": {"approve", "view"},
    "admin": {"create", "update", "approve", "view", "delete"},
}


class Role(str, Enum):
    ENGINEER = "engineer"
    DESIGNER = "designer"
    REVIEWER = "reviewer"
    ADMIN = "admin"


def check_access(role: str, action: str) -> bool:
    """Return True if the given role is allowed to perform action.

    Unknown roles default to no access.
    """

    key = role.value if isinstance(role, Role) else str(role)
    actions = _ROLE_PERMISSIONS.get(key.lower())
    if not actions:
        return False
    return action in actions


def can_edit(role: Role, prompt: object) -> bool:  # pragma: no cover - thin wrapper
    return check_access(role, "update") or check_access(role, "create")


def can_approve(role: Role, prompt: object) -> bool:  # pragma: no cover - thin wrapper
    return check_access(role, "approve")
