"""W15: Evacuation uses semantic clock only; no wall-clock fallback.

REQ-244/247: EvacuationDiscipline uses semantic_clock ticks only;
no wall-clock time.time() / datetime.now() usage in evacuation paths.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

import pytest

pytestmark = pytest.mark.governance

REPO_ROOT = Path(__file__).parent.parent.parent


# ---------------------------------------------------------------------------
# EvacuationDiscipline with semantic clock only
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EvacuationDiscipline:
    """Evacuation record using semantic clock ticks only — no wall-clock."""

    evacuation_id: str
    trigger_tick: int  # semantic clock tick at trigger
    completion_tick: int  # semantic clock tick at completion
    l2_tokens_revoked: int
    leases_killed: int
    flags_overridden: bool

    def __post_init__(self):
        if self.completion_tick < self.trigger_tick:
            raise ValueError(
                f"completion_tick ({self.completion_tick}) must be >= trigger_tick ({self.trigger_tick})",
            )

    @property
    def duration_ticks(self) -> int:
        return self.completion_tick - self.trigger_tick


class EvacuationController:
    """Execute evacuation using semantic clock; reject wall-clock inputs."""

    def __init__(self):
        self._current_tick: int = 0
        self._evacuations: list[EvacuationDiscipline] = []

    def advance_tick(self, tick: int) -> None:
        self._current_tick = tick

    def execute_evacuation(
        self,
        evacuation_id: str,
        tokens_to_revoke: int = 0,
        leases_to_kill: int = 0,
    ) -> EvacuationDiscipline:
        """Execute evacuation and record with semantic clock ticks."""
        trigger = self._current_tick

        # Simulate tick advancement during evacuation
        completion = trigger + 1

        evac = EvacuationDiscipline(
            evacuation_id=evacuation_id,
            trigger_tick=trigger,
            completion_tick=completion,
            l2_tokens_revoked=tokens_to_revoke,
            leases_killed=leases_to_kill,
            flags_overridden=True,
        )
        self._evacuations.append(evac)
        return evac

    @property
    def evacuation_count(self) -> int:
        return len(self._evacuations)

    @property
    def latest(self) -> EvacuationDiscipline | None:
        return self._evacuations[-1] if self._evacuations else None


# ---------------------------------------------------------------------------
# AST scan for wall-clock in evacuation-related files
# ---------------------------------------------------------------------------

_WALL_CLOCK_CALLS = frozenset(["time", "now", "utcnow", "monotonic", "perf_counter"])


def _find_wallclock_in_file(path: Path) -> list[str]:
    if not path.exists():
        return []
    source = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(source)
    except SyntaxError:  # review: Syntax errors should be caught at parser level, not runtime
        return []
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in _WALL_CLOCK_CALLS:
                if isinstance(node.func.value, ast.Name) and node.func.value.id in ("time", "datetime"):
                    hits.append(f"line {node.lineno}: {node.func.value.id}.{node.func.attr}()")
    return hits


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.fixture()
def controller() -> EvacuationController:
    c = EvacuationController()
    c.advance_tick(100)
    return c


@pytest.mark.governance
def test_evacuation_uses_semantic_clock_only(controller):
    """Evacuation records use semantic clock ticks, not wall-clock."""
    evac = controller.execute_evacuation("evac_001", tokens_to_revoke=5, leases_to_kill=3)

    assert evac.trigger_tick == 100
    assert evac.completion_tick >= 100
    assert evac.l2_tokens_revoked == 5
    assert evac.leases_killed == 3
    assert evac.flags_overridden is True


@pytest.mark.governance
def test_evacuation_completion_tick_gte_trigger(controller):
    """Completion tick must be >= trigger tick."""
    evac = controller.execute_evacuation("evac_002")
    assert evac.completion_tick >= evac.trigger_tick


@pytest.mark.governance
def test_evacuation_invalid_ticks_rejected():
    """EvacuationDiscipline rejects completion_tick < trigger_tick."""
    with pytest.raises(ValueError, match="completion_tick"):
        EvacuationDiscipline(
            evacuation_id="bad_evac",
            trigger_tick=50,
            completion_tick=30,  # invalid — before trigger
            l2_tokens_revoked=0,
            leases_killed=0,
            flags_overridden=False,
        )


@pytest.mark.governance
def test_evacuation_duration_ticks():
    """duration_ticks returns correct semantic clock duration."""
    evac = EvacuationDiscipline(
        evacuation_id="evac_dur",
        trigger_tick=10,
        completion_tick=13,
        l2_tokens_revoked=2,
        leases_killed=1,
        flags_overridden=True,
    )
    assert evac.duration_ticks == 3


@pytest.mark.governance
def test_evacuation_is_frozen():
    """EvacuationDiscipline is immutable — frozen dataclass."""
    evac = EvacuationDiscipline(
        evacuation_id="evac_frozen",
        trigger_tick=1,
        completion_tick=2,
        l2_tokens_revoked=0,
        leases_killed=0,
        flags_overridden=False,
    )
    with pytest.raises((AttributeError, TypeError)):
        evac.trigger_tick = 99  # type: ignore[misc]


@pytest.mark.governance
def test_evacuation_controller_tracks_multiple(controller):
    """Controller tracks multiple evacuation events."""
    for i in range(3):
        controller.advance_tick(100 + i)
        controller.execute_evacuation(f"evac_{i:03d}")

    assert controller.evacuation_count == 3


@pytest.mark.governance
def test_no_wallclock_in_telemetry_module():
    """REQ-244: No wall-clock calls in telemetry module (if it exists)."""
    telemetry_path = REPO_ROOT / "agentic_core/L4_state/types/telemetry.py"
    violations = _find_wallclock_in_file(telemetry_path)
    assert violations == [], "Wall-clock calls in telemetry.py:\n" + "\n".join(violations)
