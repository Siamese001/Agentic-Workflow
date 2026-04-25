"""AppHealResult contract — parallel to agentic_core.L2_execution.types.heal_contract_types.

Defines the shared result envelope for all apps_* guardian/healer pairs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AppHealStatus(str, Enum):
    HEALED = "HEALED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass(frozen=True)
class AppHealResult:
    """Immutable result produced by one guardian→healer execution."""

    check_id: str
    app: str
    status: AppHealStatus
    changes_made: tuple[str, ...] = field(default_factory=tuple)
    rollback_info: dict[str, Any] = field(default_factory=dict)
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "app": self.app,
            "status": str(self.status),
            "changes_made": list(self.changes_made),
            "rollback_info": self.rollback_info,
            "detail": self.detail,
        }

    @classmethod
    def skipped(cls, check_id: str, app: str, reason: str) -> AppHealResult:
        return cls(check_id=check_id, app=app, status=AppHealStatus.SKIPPED, detail=reason)

    @classmethod
    def failed(cls, check_id: str, app: str, reason: str) -> AppHealResult:
        return cls(check_id=check_id, app=app, status=AppHealStatus.FAILED, detail=reason)


__all__ = ["AppHealStatus", "AppHealResult"]
