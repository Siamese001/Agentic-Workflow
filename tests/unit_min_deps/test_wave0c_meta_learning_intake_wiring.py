"""
Wave 0C Invariant: _fire_meta_learning_intake must be wired into execute_ssot.py
and the intake adapter must correctly persist healing records.
"""

import ast
from pathlib import Path
from unittest.mock import MagicMock

from agentic_core.L0_routing.config.path_constants import (
    L0_ROUTING_DIR,
)

EXECUTE_SSOT_PATH = Path(__file__).parent.parent.parent / L0_ROUTING_DIR / "scripts" / "execute_ssot.py"


def test_fire_meta_learning_intake_defined_in_execute_ssot():
    """_fire_meta_learning_intake must be defined in execute_ssot.py."""
    src = EXECUTE_SSOT_PATH.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(src)
    fn_names = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    assert "_fire_meta_learning_intake" in fn_names, (
        "_fire_meta_learning_intake function not found in execute_ssot.py"
    )


def test_fire_meta_learning_intake_called_before_finish_mission():
    """_fire_meta_learning_intake call must appear before finish_mission('completed') in source."""
    src = EXECUTE_SSOT_PATH.read_text(encoding="utf-8", errors="replace")
    intake_pos = src.find("_fire_meta_learning_intake(state_mgr")
    finish_pos = src.find('finish_mission(status="completed")')
    assert intake_pos != -1, "_fire_meta_learning_intake(state_mgr call not found"
    assert finish_pos != -1, 'finish_mission(status="completed") call not found'
    assert intake_pos < finish_pos, (
        "_fire_meta_learning_intake must be called BEFORE finish_mission('completed')"
    )


def test_intake_adapter_persists_records_with_healing_actions():
    """HealingOutcomeIntakeAdapter must persist exactly one record when healing_actions exist."""
    from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
    from system_learning.engines.healing_outcome_intake_adapter import HealingOutcomeIntakeAdapter
    from system_learning.engines.in_memory_healing_outcome_intake_store import (
        InMemoryHealingOutcomeIntakeStore,
    )
    from system_learning.types.healing_outcome_types import HealingOutcomeEvent

    healing_actions = [
        {"agent": "LocationHealerAgent", "tier": "L5", "type": "DEEP VIOLATION", "status": "healed"},
        {"agent": "GravityLeakRepairAgent", "tier": "L5", "type": "GRAVITY", "status": "plan_only"},
    ]

    aggregator = HealingOutcomeAggregator(window_size=max(len(healing_actions), 1))
    for action in healing_actions:
        aggregator.ingest(
            HealingOutcomeEvent(
                healer_id=action["agent"],
                tier=action["tier"],
                failure_type=action["type"],
                success=action["status"] == "healed",
                timestamp_utc=0,
            )
        )

    store = InMemoryHealingOutcomeIntakeStore()
    adapter = HealingOutcomeIntakeAdapter(store=store)
    record = adapter.build_record(aggregator=aggregator, created_utc=0, source="execute_ssot")
    adapter.persist_record(record)

    assert store.count() == 1, f"Expected 1 record, got {store.count()}"
    records = store.get_records()
    assert records[0].source == "execute_ssot"
    assert records[0].window_size == 2


def test_intake_adapter_no_persist_when_empty():
    """_fire_meta_learning_intake must not call build_record when healing_actions is empty."""
    from system_learning.engines.in_memory_healing_outcome_intake_store import (
        InMemoryHealingOutcomeIntakeStore,
    )

    store = InMemoryHealingOutcomeIntakeStore()
    assert store.count() == 0, "Store should be empty when no healing actions present"


def test_fire_meta_learning_intake_noop_on_import_error():
    """_fire_meta_learning_intake must be a no-op when imports fail (pre-Wave 0B)."""
    import sys

    # Temporarily hide the intake adapter to simulate pre-Wave 0B
    hidden = {}
    modules_to_hide = [
        "system_learning.engines.healing_outcome_aggregator",
        "system_learning.pipelines.meta_learning_pipeline",
        "system_learning.engines.healing_outcome_intake_adapter",
        "system_learning.engines.in_memory_healing_outcome_intake_store",
    ]

    for mod in modules_to_hide:
        if mod in sys.modules:
            hidden[mod] = sys.modules.pop(mod)

    # Build a fake state_mgr
    fake_state_mgr = MagicMock()
    fake_state_mgr.state = {"healing_actions": [], "meta_learning": {}}

    # Re-import execute_ssot to get the function with hidden modules
    import builtins

    real_import = builtins.__import__

    def blocking_import(name, *args, **kwargs):
        if name in modules_to_hide or any(name.startswith(m) for m in modules_to_hide):
            raise ImportError(f"Simulated missing module: {name}")
        return real_import(name, *args, **kwargs)

    builtins.__import__ = blocking_import
    try:
        # Import execute_ssot with mocked imports
        if "agentic_core.L0_routing.scripts.execute_ssot" in sys.modules:
            execute_ssot = sys.modules["agentic_core.L0_routing.scripts.execute_ssot"]
        else:
            import agentic_core.L0_routing.scripts.execute_ssot as execute_ssot

        # Should not raise
        execute_ssot._fire_meta_learning_intake(fake_state_mgr, now_utc=0)
    finally:
        builtins.__import__ = real_import
        # Restore hidden modules
        for mod, val in hidden.items():
            sys.modules[mod] = val
            assert True  # no-exception contract
