from __future__ import annotations

import logging

'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
from typing import Any

_logger = logging.getLogger(__name__)

def test_run_scenario_uses_existing_engine(self: Any) -> None:
    """Test that scenario runner properly uses existing engine instance."""
    Engine.list()
    assert scenarios, 'Expected at least one registered simulation scenario'
    scenario_id, description = next(iter(scenarios.items()))
    SimScenario(id=scenario_id, description=description, initial_context={}, execution_profile_name='default', run_count=1)
    run_scenario(scenario)
    assert outcome.scenario_id == scenario_id
