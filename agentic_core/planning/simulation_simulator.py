# from archives.legacy_resume_gen.Agentic-Workflow-10_7_main.draft_simulation import Engine  # INVALID: Cannot import from path with hyphens

# from archives.legacy_root_folders.eval.simulation.models import SimScenario  # DEPRECATED: Archive import removed to protect archives from validation edits
# from archives.legacy_root_folders.eval.simulation.simulator import run_scenario  # DEPRECATED: Archive import removed to protect archives from validation edits


def test_run_scenario_uses_existing_engine(self) -> None:
    """Test that scenario runner properly uses existing engine instance."""
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






