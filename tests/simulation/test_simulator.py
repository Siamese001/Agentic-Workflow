from simulation import Engine

from eval.simulation.models import SimScenario
from eval.simulation.simulator import run_scenario


def test_run_scenario_uses_existing_engine():
    scenarios = Engine.list()
    assert scenarios, "Expected at least one registered simulation scenario"

    scenario_id, description = next(iter(scenarios.items()))

    scenario = SimScenario(
        id=scenario_id,
        description=description,
        initial_context={},
        execution_profile_name="default",
        run_count=1,
    )

    outcome = run_scenario(scenario)
    assert outcome.scenario_id == scenario_id






