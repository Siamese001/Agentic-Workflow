# Outreach planner
from .base import BasePlanner

class OutreachPlanner(BasePlanner):
    def plan_outreach(self, target):
        return self.plan("execute_outreach")
