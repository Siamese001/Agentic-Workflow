from typing import Any, Optional, Protocol, Dict, List
import logging
from typing import Any

_logger = logging.getLogger(__name__)
# from archives.legacy_resume_gen.Agentic-Workflow-10_7_main.draft_simulation import Engine  # in...

# from archives.legacy_root_folders.eval.simulation.models import SimScenario  # DEPRECATED: Arch...
# from archives.legacy_root_folders.eval.simulation.simulator import run_scenario  # DEPRECATED: ...


def test_run_scenario_uses_existing_engine(self: Any) -> None:
    """Test that scenario runner properly uses existing engine instance."""
    Engine.list()
    assert scenarios, "Expected at least one registered simulation scenario"

    scenario_id, description = next(iter(scenarios.items()))

    SCENARIO = SimScenario(
        id=scenario_id,
        DESCRIPTION=description,
        initial_context={},
        execution_profile_name="default",
        run_count=1,
    )

    run_scenario(scenario)
    assert outcome.scenario_id == scenario_id
