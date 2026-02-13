"""V15 CC-1 Critique Catch-Up — Hardening Tests for Phases 7.0–7.2.

Fix #1: Gateway resets _pipe_violations/_policy_violations per execute().
Fix #3: Spy test forwards **kwargs (covered by existing test passing).
Fix #4: P3 gate SemanticClock check uses _clock.tick( not generic tick(.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from agentic_core.L0_routing.enforcement.v15_execution_gateway import (
    V15ExecutionGateway,
)
from agentic_core.L0_routing.types.v15_p2_types import (
    FixConstraint,
    SurgicalManifest,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _make_manifest(trace_id: str = "CC3AL1-00000001") -> SurgicalManifest:
    ast_snippet = "heal(test)"
    return SurgicalManifest(
        schema_version="1.0.0",
        correlation_id=trace_id,
        node_id="TestNode",
        target_layer="L2",
        ast_snippet=ast_snippet,
        serialization_canon="test",
        fix_constraint=FixConstraint.RELAXED,
        manifest_hash=hashlib.sha256(ast_snippet.encode()).hexdigest(),
        change_history=(),
        provenance_chain=(trace_id,),
    )


def _noop_heal(manifest):
    return {"status": "completed", "errors": 0}


def _noop_state_hash():
    return ("aaa", "bbb", "ccc")


# ---------------------------------------------------------------------------
# Fix #1: Violation lists reset per execute()
# ---------------------------------------------------------------------------


class TestGatewayViolationListReset:
    """Singleton gateway must not leak violations across execute() calls."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_pipe_violations_reset_between_executions(self):
        """_pipe_violations must be empty after a clean second execution,
        even if the first execution recorded violations."""
        from agentic_core.L0_routing.types.v15_contracts import PipeOrderEnforcer

        gw = V15ExecutionGateway()

        # Force a pipe violation via internal helper
        pipe = PipeOrderEnforcer()
        gw._pipe_advance(pipe, "schema_validation", "trace-1")
        gw._pipe_advance(pipe, "commit", "trace-1")  # out of order → violation
        assert len(gw._pipe_violations) == 1, "Expected 1 violation from first wave"

        # Now run a clean execute() — violations must be reset
        manifest = _make_manifest(trace_id="CC3AL1-AAAAAAAA")
        result = gw.execute(manifest, _noop_heal, _noop_state_hash, trace_id="CC3AL1-AAAAAAAA")
        assert result.success
        assert len(gw._pipe_violations) == 0, (
            "Violation list must be empty after clean execute() — Fix #1 (per-execute reset) is missing"
        )

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_policy_violations_reset_between_executions(self):
        """_policy_violations must be empty after a clean second execution."""
        from agentic_core.L0_routing.types.v15_contracts import PolicyConfigGuard

        gw = V15ExecutionGateway()

        # Force a policy violation via internal helper
        guard = PolicyConfigGuard(policy_config={"k": "v"}, wave_id="w1")
        gw._policy_check(guard, {"k": "MUTATED"}, "trace-1")
        assert len(gw._policy_violations) == 1, "Expected 1 policy violation"

        # Clean execute resets
        manifest = _make_manifest(trace_id="CC3AL1-BBBBBBBB")
        result = gw.execute(manifest, _noop_heal, _noop_state_hash, trace_id="CC3AL1-BBBBBBBB")
        assert result.success
        assert len(gw._policy_violations) == 0, (
            "Policy violation list must be empty after clean execute() — "
            "Fix #1 (per-execute reset) is missing"
        )

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_consecutive_clean_executions_no_accumulation(self):
        """Two consecutive clean executions must never accumulate violations."""
        gw = V15ExecutionGateway()
        for i in range(3):
            tid = f"CC3AL1-{i:08X}"
            m = _make_manifest(trace_id=tid)
            gw.execute(m, _noop_heal, _noop_state_hash, trace_id=tid)

        assert len(gw._pipe_violations) == 0
        assert len(gw._policy_violations) == 0


# ---------------------------------------------------------------------------
# Fix #4: P3 gate uses _clock.tick( not generic tick(
# ---------------------------------------------------------------------------


class TestP3GateSemanticClockCheck:
    """P3 gate must use _clock.tick( to avoid false positives."""

    def test_p3_gate_checks_clock_tick_specifically(self):
        """The P3 gate source must match _clock.tick( not bare tick(."""
        p3_src = (PROJECT_ROOT / "ops_scripts/ci/run_v15_p3_gate.py").read_text(encoding="utf-8")
        assert "_clock.tick(" in p3_src, (
            "P3 gate must check for _clock.tick( specifically — "
            "Fix #4 (tighten SemanticClock match) is missing"
        )
        # Must NOT use the old generic match
        assert 'has_tick = "tick(" in content' not in p3_src, (
            "P3 gate still uses generic 'tick(' match — Fix #4 not applied"
        )

    def test_p3_gate_still_passes(self):
        """P3 gate must still exit 0 with the tightened check."""
        result = subprocess.run(
            [sys.executable, "ops_scripts/ci/run_v15_p3_gate.py"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"P3 gate failed: {result.stderr}"

    def test_p3_evidence_has_semantic_clock_pass(self):
        """P3 evidence JSON must contain a passed semantic_clock_wiring check."""
        evidence_path = PROJECT_ROOT / "docs/reports/plans/v15_p3_evidence.json"
        if evidence_path.exists():
            data = json.loads(evidence_path.read_text(encoding="utf-8"))
            clock_checks = [
                c for c in data.get("passed_details", []) if c.get("check") == "semantic_clock_wiring"
            ]
            assert len(clock_checks) >= 1, "semantic_clock_wiring check must be in passed_details"
            detail = clock_checks[0].get("detail", "")
            assert "_clock.tick()" in detail, "Evidence detail must reference _clock.tick() specifically"
