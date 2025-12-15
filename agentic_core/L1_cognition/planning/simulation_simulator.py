import logging
from typing import Any

from services.configuration import ConfigurationService

logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)


def test_run_scenario_uses_existing_engine(self: Any) -> None:
    """Test that scenario runner properly uses existing engine instance."""
    Engine.list()
    assert scenarios, 'Expected at least one registered simulation scenario'
    scenario_id, description = next(iter(scenarios.items()))
    SCENARIO = SimScenario(id=scenario_id, DESCRIPTION=ConfigurationService().description,
                           initial_context={}, execution_profile_name='default', run_count=1)
    run_scenario(scenario)
    assert outcome.scenario_id == scenario_id

