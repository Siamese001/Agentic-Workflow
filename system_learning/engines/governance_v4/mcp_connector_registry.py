"""L5 Governance v4 — MCP Connector Registry (G-12).

Enterprise allowlist for MCP connectors with one-time vs permanent grant
tracking and data-sensitivity tagging. Tracks allowlist violations.

Reference
---------
``docs/reference/00_L5_Policy_Plane/Governance & Safety v4.md`` G-12.

KPI surface
-----------
``MCP_CONNECTOR_ALLOWLIST_VIOLATIONS`` — count of unallowed MCP calls
(must be 0).
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class GrantType(str, Enum):
    ONE_TIME = "ONE_TIME"
    PERMANENT = "PERMANENT"


class DataSensitivity(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    REGULATED = "REGULATED"


@dataclass(frozen=True)
class ConnectorEntry:
    connector_id: str
    grant_type: GrantType
    data_sensitivity: DataSensitivity
    notes: str = ""


class McpConnectorRegistry:
    """Allowlist + grant tracker for MCP connectors."""

    def __init__(self) -> None:
        self._entries: dict[str, ConnectorEntry] = {}
        self._consumed_one_time: set[str] = set()
        self._violations: int = 0

    def register(
        self,
        *,
        connector_id: str,
        grant_type: GrantType,
        data_sensitivity: DataSensitivity,
        notes: str = "",
    ) -> ConnectorEntry:
        entry = ConnectorEntry(
            connector_id=connector_id,
            grant_type=grant_type,
            data_sensitivity=data_sensitivity,
            notes=notes,
        )
        self._entries[connector_id] = entry
        return entry

    def authorize(self, connector_id: str) -> tuple[bool, str]:
        """Check if a connector call is authorized.

        Returns ``(authorized, reason)``. Counts violations on rejection.
        """
        entry = self._entries.get(connector_id)
        if entry is None:
            self._violations += 1
            return False, f"connector {connector_id} not in allowlist"
        if entry.grant_type is GrantType.ONE_TIME:
            if connector_id in self._consumed_one_time:
                self._violations += 1
                return False, f"one-time grant for {connector_id} already consumed"
            self._consumed_one_time.add(connector_id)
        return True, "authorized"

    @property
    def violation_count(self) -> int:
        return self._violations

    def reset_violations(self) -> None:
        self._violations = 0

    def reset(self) -> None:
        self._entries.clear()
        self._consumed_one_time.clear()
        self._violations = 0

    def publish_kpi_sample(self, board: Any) -> None:
        try:
            from system_learning.engines.v7_kpi_board import (  # noqa: PLC0415
                V7KPIName,
                V7KPISample,
            )

            board.record(V7KPISample(
                name=V7KPIName.MCP_CONNECTOR_ALLOWLIST_VIOLATIONS,
                value=float(self._violations),
                timestamp=time.time(),
                source="mcp_connector_registry",
                metadata={"count": self._violations},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-specific -- KPI must not break authorization
            logger.warning(
                "v7_kpi_mcp_connector_allowlist_violations_failed: %s", exc
            )


__all__ = [
    "GrantType",
    "DataSensitivity",
    "ConnectorEntry",
    "McpConnectorRegistry",
]
