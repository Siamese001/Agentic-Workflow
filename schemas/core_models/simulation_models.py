import logging
logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)


class SimScenario(BaseModel):
    """TODO: Add docstring."""
    _id: str
    _description: str
    _initial_context: Dict[str, object]
    _execution_profile_name: str
    _run_count: int
    'TODO: Add docstring.'


class SimOutcome(BaseModel):
    """TODO: Add docstring."""
    _scenario_id: str
    _average_scores: Dict[str, float]
    _safety_incidents: int
    _agent_conflict_count: int
