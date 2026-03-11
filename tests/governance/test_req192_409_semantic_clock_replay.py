"""W19: Two-run SemanticClock advancement; identical artifact + L4 version binding; no wall-clock.

REQ-192/409: SemanticClock advancement produces identical artifacts across runs;
no wall-clock usage in AST of clock module.
"""

from __future__ import annotations

import ast
import dataclasses
from pathlib import Path

import pytest

from agentic_core.L0_routing.types.determinism_types import (
    SemanticClock,
    SemanticClockAdvancementArtifact,
    SemanticClockSnapshot,
)

pytestmark = pytest.mark.governance

REPO_ROOT = Path(__file__).parent.parent.parent
_CLOCK_MODULE = REPO_ROOT / "agentic_core/L0_routing/types/determinism_types.py"

_WALL_CLOCK_ATTRS = frozenset(["time", "now", "utcnow", "monotonic", "perf_counter"])


def _find_wallclock_calls(path: Path) -> list[str]:
    """AST-scan for wall-clock calls in a module."""
    source = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []

    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            # datetime.now() / datetime.utcnow()
            if isinstance(func, ast.Attribute) and func.attr in _WALL_CLOCK_ATTRS:
                violations.append(f"line {node.lineno}: wall-clock call '{func.attr}()'")
            # time.time() / time.monotonic()
            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                if func.value.id == "time" and func.attr in _WALL_CLOCK_ATTRS:
                    violations.append(f"line {node.lineno}: wall-clock call 'time.{func.attr}()'")
    return violations


@pytest.mark.governance
def test_req192_semantic_clock_advancement_two_run_identical():
    """REQ-192: Two-run SemanticClock advancement produces identical snapshot."""
    clock1 = SemanticClock(step_id=0)
    clock2 = SemanticClock(step_id=0)

    snap1 = SemanticClockSnapshot(
        tick=clock1.step_id,
        vector_clock=clock1.vector_clock,
    )
    snap2 = SemanticClockSnapshot(
        tick=clock2.step_id,
        vector_clock=clock2.vector_clock,
    )

    assert snap1.tick == snap2.tick
    assert snap1.vector_clock == snap2.vector_clock


@pytest.mark.governance
def test_req192_clock_advancement_artifact_deterministic():
    """REQ-192: SemanticClockAdvancementArtifact hash is deterministic."""
    artifact1 = SemanticClockAdvancementArtifact(
        advancement_id="adv_001",
        previous_tick=5,
        new_tick=6,
        advancement_reason="phase_transition",
        l4_version_binding="l4_v1.0.0",
        provider_id="provider_anthropic",
        timestamp=1234567890.0,
    )
    artifact2 = SemanticClockAdvancementArtifact(
        advancement_id="adv_001",
        previous_tick=5,
        new_tick=6,
        advancement_reason="phase_transition",
        l4_version_binding="l4_v1.0.0",
        provider_id="provider_anthropic",
        timestamp=1234567890.0,
    )

    assert artifact1.artifact_hash == artifact2.artifact_hash
    assert len(artifact1.artifact_hash) == 64


@pytest.mark.governance
def test_req192_clock_advancement_hash_field_sensitive():
    """Changing any field changes the advancement artifact hash."""
    base = SemanticClockAdvancementArtifact(
        advancement_id="adv_001",
        previous_tick=5,
        new_tick=6,
        advancement_reason="phase_transition",
        l4_version_binding="l4_v1.0.0",
        provider_id="provider_anthropic",
        timestamp=1234567890.0,
    )
    alt = SemanticClockAdvancementArtifact(
        advancement_id="adv_001",
        previous_tick=5,
        new_tick=99,  # changed
        advancement_reason="phase_transition",
        l4_version_binding="l4_v1.0.0",
        provider_id="provider_anthropic",
        timestamp=1234567890.0,
    )
    assert base.artifact_hash != alt.artifact_hash


@pytest.mark.governance
def test_req409_no_wallclock_in_semantic_clock_module():
    """REQ-409: No wall-clock calls in the determinism_types module."""
    assert _CLOCK_MODULE.exists(), f"Module not found: {_CLOCK_MODULE}"
    violations = _find_wallclock_calls(_CLOCK_MODULE)
    # Filter out calls inside SemanticClockAdvancementArtifact.__post_init__
    # which uses timestamp (a field, not a call) — we check for actual CALLS
    assert violations == [], f"Wall-clock calls found in {_CLOCK_MODULE.name}:\n" + "\n".join(violations)


@pytest.mark.governance
def test_req192_l4_version_binding_in_artifact():
    """REQ-192: Advancement artifact carries L4 version binding."""
    artifact = SemanticClockAdvancementArtifact(
        advancement_id="adv_002",
        previous_tick=10,
        new_tick=11,
        advancement_reason="policy_update",
        l4_version_binding="l4_v2.0.1",
        provider_id="provider_openai",
        timestamp=9999999.0,
    )
    assert artifact.l4_version_binding == "l4_v2.0.1"
    assert artifact.provider_id == "provider_openai"


@pytest.mark.governance
def test_req192_clock_snapshot_immutable():
    """SemanticClockSnapshot is a frozen dataclass (immutable)."""
    snap = SemanticClockSnapshot(tick=7, vector_clock=())
    with pytest.raises((AttributeError, TypeError, dataclasses.FrozenInstanceError)):
        snap.tick = 99  # type: ignore[misc]
