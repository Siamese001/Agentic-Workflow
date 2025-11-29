# Resume planner
from .base import BasePlanner

class ResumePlanner(BasePlanner):
    def plan_resume_processing(self, resume):
        return self.plan("process_resume")
