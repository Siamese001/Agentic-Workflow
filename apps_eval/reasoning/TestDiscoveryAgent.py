"""
Test Discovery Agent — apps_eval/reasoning

Agent for discovering and cataloging tests from ADG.
Aligned with apps_lic agent patterns with lifecycle trace integration.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_agent,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
    _emit_routes_to_agent,
    _emit_snapshots_state,
    emit_determinism_digest,
    emit_replay_key,
)
from apps_eval.services.test_discovery_service import TestDiscoveryService

_log = logging.getLogger(__name__)


class TestDiscoveryAgent:
    """Agent for discovering tests from ADG and codebase."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize the test discovery agent."""
        self.config = config or {}
        self._discovery_service = TestDiscoveryService(config)

        # Lifecycle trace emission
        emit_replay_key("test_discovery", "agent_init")
        emit_determinism_digest("test_discovery", "agent_init")
        _emit_applies_guardrail("p0", "test_discovery_agent", "agent_init")
        _emit_reads_policy_state("p0", "test_discovery_agent", "policy_binding")
        _emit_snapshots_state("p0", "test_discovery_agent", "agent_state")

    async def discover_tests(
        self,
        target_modules: list[str],
        discovery_mode: str = "adg",
    ) -> dict[str, Any]:
        """Execute test discovery workflow.

        Args:
            target_modules: List of module patterns to discover
            discovery_mode: Discovery mode (adg, codebase, or both)

        Returns:
            Discovery results with test catalog
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "TestDiscoveryAgent.discover_tests",
        )
        _emit_orchestrates_workflow("p3", "test_discovery_agent", "discovery_workflow")
        _emit_dispatches_agent("p3", "test_discovery_agent", "discovery_dispatch")
        _emit_routes_to_agent("p1", "test_discovery_agent", "discovery_route")
        _emit_records_telemetry_event("p4", "test_discovery_agent", "discovery_start")

        try:
            discovered_tests: list[dict[str, Any]] = []

            if discovery_mode in ("adg", "both"):
                for module in target_modules:
                    tests = self._discovery_service.discover_from_adg(module)
                    discovered_tests.extend(tests)

            if discovery_mode in ("codebase", "both"):
                tests = self._discovery_service.discover_from_codebase(target_modules)
                discovered_tests.extend(tests)

            result = {
                "success": True,
                "trace_id": _trace_id,
                "tests_discovered": len(discovered_tests),
                "tests": discovered_tests,
                "mode": discovery_mode,
            }

            _log.info("Test discovery complete: %d tests found", len(discovered_tests))
            _emit_records_telemetry_event(
                "p4", "test_discovery_agent", f"discovery_complete:{len(discovered_tests)}",
            )

            return result

        except Exception as exc:
            _log.error("Test discovery failed: %s", exc)
            _emit_records_telemetry_event("p4", "test_discovery_agent", "discovery_error")
            return {
                "success": False,
                "trace_id": _trace_id,
                "error": str(exc),
                "tests_discovered": 0,
                "tests": [],
            }

    @staticmethod
    def _make_trace_id(target_modules: list[str]) -> str:
        """Generate a deterministic trace ID."""
        raw = f"discover:{','.join(sorted(target_modules))}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
