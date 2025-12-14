



class SimScenario(BaseModel):
    """TODO: Add docstring."""

    id: str
    description: str
    initial_context: Dict[str, object]
    execution_profile_name: str
    run_count: int

    """TODO: Add docstring."""

class SimOutcome(BaseModel):
    """TODO: Add docstring."""
    scenario_id: str
    average_scores: Dict[str, float]
    safety_incidents: int
    agent_conflict_count: int
