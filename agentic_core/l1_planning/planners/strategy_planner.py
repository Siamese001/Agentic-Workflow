# strategy_planner
from abc import ABC, abstractmethod

class Strategy_Planner:
    def __init__(self):
        pass
    
    def plan(self, goal, context):
        return {"steps": [], "status": "planned"}
