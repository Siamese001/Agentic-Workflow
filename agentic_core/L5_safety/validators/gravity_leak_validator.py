"""
agentic_core/L5_safety/validators/gravity_leak_validator.py

GravityLeakValidatorAgent — certify-only validator pair for GravityLeakHealerAgent.

ADG fix: A-13 (no certify-only validator pair existed for GravityLeakHealerAgent).

Contract:
- ZERO mutations — read-only scan only
- Delegates to GravityLeakRepairAgent.heal_repository(dry_run=True, execute=False)
- Returns check_dict with check_id="gravity_leak" for HEALER_REGISTRY dispatch
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "gravity_leak_validator", "L5")
_emit_routes_through("p1", "gravity_leak_validator", "L5")
_emit_escalates_to_human("p1", "gravity_leak_validator", "L5")
_emit_reads_policy_state("p1", "gravity_leak_validator", "L5")

_emit_applies_guardrail("p0", "gravity_leak_validator", "p0_governance")
_emit_snapshots_state("p0", "gravity_leak_validator", "state_snapshot")

Logger = logging.getLogger(__name__)


class GravityLeakValidatorAgent:
    """Certify-only validator that detects gravity-leak violations without fixing them.

    Mirrors the domain of GravityLeakHealerAgent (GravityLeakRepairAgent) but
    performs NO mutations — suitable for validators/ territory.

    Usage::

        agent = GravityLeakValidatorAgent(project_root=Path("."))
        result = agent.certify()
        assert result["check_id"] == "gravity_leak"
    """

    CHECK_ID = "gravity_leak"

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = Path(project_root) if project_root else Path.cwd()

    def certify(self) -> dict[str, Any]:
        """Run a dry-run gravity-leak scan and return a check_dict.

        Returns:
            check_dict compatible with HEALER_REGISTRY dispatch:
                check_id, passed, violations_found, summary
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "GravityLeakValidatorAgent.certify")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:GravityLeakValidatorAgent.certify".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        try:
            from agentic_core.L5_safety.reasoning.GravityLeakRepairAgent import (
                GravityLeakRepairAgent,
            )

            agent = GravityLeakRepairAgent(project_root=self._project_root)
            result = agent.heal_repository(dry_run=True, execute=False)  # guardian: allow-silent-swallower
        except Exception as exc:
            Logger.warning("[GravityLeakValidator] scan failed: %s", exc)
            return {
                "check_id": self.CHECK_ID,
                "passed": False,
                "violations_found": -1,
                "summary": f"scan_error: {type(exc).__name__}: {exc}",
            }

        violations_found: int = result.get("violations_found", 0)
        passed = violations_found == 0
        Logger.info(
            "[GravityLeakValidator] check_id=%s passed=%s violations=%d",
            self.CHECK_ID,
            passed,
            violations_found,
        )
        return {
            "check_id": self.CHECK_ID,
            "passed": passed,
            "violations_found": violations_found,
            "summary": result.get("summary", ""),
        }

    def validate(self) -> dict[str, Any]:
        """Alias for certify() — standard validator interface."""
        return self.certify()


__all__ = ["GravityLeakValidatorAgent"]
