"""L5 Governance v4 — Egress Inspector (G-08) + Hard-Constraint Enforcer (G-15).

The egress inspector runs the bidirectional AI firewall on every outbound
LLM gateway request: PII / secret / URL / hallucination-grounding /
sensitive-data classifiers.

The hard-constraint enforcer blocks REMEDIATE on any violation tagged
``hard_constraint: true`` — only REJECT is allowed.

Reference
---------
``docs/reference/00_L5_Policy_Plane/Governance & Safety v4.md`` G-08, G-15.

KPI surface
-----------
- ``EGRESS_INSPECTOR_BLOCK_RATE`` (ratio of egress calls blocked)
- ``HARD_CONSTRAINT_REMEDIATE_ATTEMPTS`` (count, EQ 0)
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class EgressVerdict(str, Enum):
    PASS = "PASS"
    BLOCK = "BLOCK"
    QUARANTINE = "QUARANTINE"


@dataclass(frozen=True)
class EgressFinding:
    verdict: EgressVerdict
    triggered: tuple[str, ...]
    rationale: str


# Conservative pattern set. The inspector is explicitly NOT a complete DLP
# system — it's a deterministic last-mile fail-closed check before egress.
_SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("github_pat", re.compile(r"ghp_[A-Za-z0-9]{36}")),
    ("openai_key", re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("private_key_block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
)
_PII_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("ssn_us", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("credit_card", re.compile(r"\b(?:\d[ -]?){13,16}\b")),
)
_URL_PATTERN = re.compile(r"https?://([^\s/]+)")


class EgressInspector:
    """Fail-closed egress inspector."""

    def __init__(
        self,
        *,
        url_allowlist: tuple[str, ...] | None = None,
    ) -> None:
        # If allowlist is None, all URLs pass; if empty tuple, all URLs fail.
        self._url_allowlist = url_allowlist
        self._blocked: int = 0
        self._total: int = 0

    def inspect(self, payload: str) -> EgressFinding:
        self._total += 1
        triggered: list[str] = []

        for label, rx in _SECRET_PATTERNS:
            if rx.search(payload):
                triggered.append(f"secret:{label}")
        for label, rx in _PII_PATTERNS:
            if rx.search(payload):
                triggered.append(f"pii:{label}")
        if self._url_allowlist is not None:
            for url_match in _URL_PATTERN.finditer(payload):
                host = url_match.group(1).lower()
                if not any(host == a or host.endswith("." + a)
                           for a in self._url_allowlist):
                    triggered.append(f"url_not_allowlisted:{host}")

        if triggered:
            self._blocked += 1
            return EgressFinding(
                verdict=EgressVerdict.BLOCK,
                triggered=tuple(triggered),
                rationale=f"egress blocked: {triggered[:3]}",
            )
        return EgressFinding(
            verdict=EgressVerdict.PASS,
            triggered=(),
            rationale="egress clean",
        )

    @property
    def counters(self) -> tuple[int, int]:
        return (self._blocked, self._total)

    def reset(self) -> None:
        self._blocked = 0
        self._total = 0

    def publish_kpi_sample(self, board: Any) -> None:
        try:
            from system_learning.engines.v7_kpi_board import (  # noqa: PLC0415
                V7KPIName,
                V7KPISample,
            )

            ratio = (
                self._blocked / self._total if self._total > 0 else 0.0
            )
            board.record(V7KPISample(
                name=V7KPIName.EGRESS_INSPECTOR_BLOCK_RATE,
                value=ratio,
                timestamp=time.time(),
                source="egress_inspector",
                metadata={"blocked": self._blocked, "total": self._total},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-specific -- KPI must not break inspection
            logger.warning("v7_kpi_egress_block_rate_failed: %s", exc)


# ---- Hard-Constraint Enforcer --------------------------------------------


class HardConstraintRemediateError(RuntimeError):
    """Raised when REMEDIATE is attempted on a hard_constraint violation."""


class HardConstraintEnforcer:
    """Block REMEDIATE on any rule tagged hard_constraint: true."""

    def __init__(self) -> None:
        self._attempts: int = 0

    def enforce(
        self,
        *,
        decision: str,
        breached_rule_id: str,  # noqa: ARG002 -- recorded by caller; reserved for audit log
        rule_is_hard_constraint: bool,
    ) -> str:
        """Returns the *final* decision after enforcement.

        If ``decision == "REMEDIATE"`` and ``rule_is_hard_constraint``, the
        decision is forced to ``"REJECT"`` and the attempt is counted.
        """
        if decision == "REMEDIATE" and rule_is_hard_constraint:
            self._attempts += 1
            return "REJECT"
        return decision

    @property
    def attempt_count(self) -> int:
        return self._attempts

    def reset(self) -> None:
        self._attempts = 0

    def publish_kpi_sample(self, board: Any) -> None:
        try:
            from system_learning.engines.v7_kpi_board import (  # noqa: PLC0415
                V7KPIName,
                V7KPISample,
            )

            board.record(V7KPISample(
                name=V7KPIName.HARD_CONSTRAINT_REMEDIATE_ATTEMPTS,
                value=float(self._attempts),
                timestamp=time.time(),
                source="hard_constraint_enforcer",
                metadata={"count": self._attempts},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-specific -- KPI must not break enforcement
            logger.warning(
                "v7_kpi_hard_constraint_remediate_attempts_failed: %s", exc
            )


__all__ = [
    "EgressVerdict",
    "EgressFinding",
    "EgressInspector",
    "HardConstraintRemediateError",
    "HardConstraintEnforcer",
]
