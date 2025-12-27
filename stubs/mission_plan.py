"""Stub for MissionPlan class used across test files."""

class MissionPlan:
    """Stub for mission planning and execution."""
    def __init__(self, mission_id: str = "stub_mission", **kwargs):
        self.mission_id = mission_id
        self.config = kwargs
        self.status = "ready"
    
    def execute(self):
        return {"status": "success", "mission_id": self.mission_id}
    
    def validate(self):
        return True

class Missing:
    """Stub for Missing sentinel class."""
    pass
