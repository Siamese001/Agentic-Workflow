# models - Simulation models for runtime evaluation
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class SimulationType(Enum):
    """Types of simulation scenarios"""
    PERFORMANCE = "performance"
    STRESS = "stress"
    CONCURRENCY = "concurrency"
    BUDGET = "budget"
    SAFETY = "safety"

@dataclass
class SimulationConfig:
    """Configuration for simulation scenarios"""
    simulation_type: SimulationType
    duration: float = 60.0
    concurrent_users: int = 1
    token_budget: int = 1000
    cost_limit: float = 1.0
    
    def __post_init__(self):
        if isinstance(self.simulation_type, str):
            self.simulation_type = SimulationType(self.simulation_type)

@dataclass
class SimulationMetrics:
    """Metrics collected during simulation"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    tokens_consumed: int = 0
    cost_incurred: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    def reset(self) -> None:
        """Reset all metrics"""
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.average_response_time = 0.0
        self.tokens_consumed = 0
        self.cost_incurred = 0.0

@dataclass
class SimScenario:
    """Simulation scenario definition"""
    name: str
    config: SimulationConfig
    description: str = ""
    enabled: bool = True
    
    def __post_init__(self):
        if not self.description:
            self.description = f"Simulation scenario for {self.config.simulation_type.value}"

class SimulationRunner:
    """Runs simulation scenarios and collects metrics"""
    
    def __init__(self):
        self.scenarios: List[SimScenario] = []
        self.metrics = SimulationMetrics()
        self.running = False
    
    def add_scenario(self, scenario: SimScenario) -> None:
        """Add a simulation scenario"""
        self.scenarios.append(scenario)
    
    def remove_scenario(self, scenario_name: str) -> bool:
        """Remove a simulation scenario by name"""
        for i, scenario in enumerate(self.scenarios):
            if scenario.name == scenario_name:
                del self.scenarios[i]
                return True
        return False
    
    def run_scenario(self, scenario_name: str) -> SimulationMetrics:
        """Run a specific simulation scenario"""
        scenario = next((s for s in self.scenarios if s.name == scenario_name), None)
        if not scenario:
            raise ValueError(f"Scenario '{scenario_name}' not found")
        
        if not scenario.enabled:
            raise ValueError(f"Scenario '{scenario_name}' is disabled")
        
        # Mock simulation execution
        self.running = True
        self.metrics.reset()
        
        # Simulate some activity based on scenario type
        if scenario.config.simulation_type == SimulationType.PERFORMANCE:
            self.metrics.total_requests = 100
            self.metrics.successful_requests = 95
            self.metrics.average_response_time = 0.5
            self.metrics.tokens_consumed = 500
            self.metrics.cost_incurred = 0.5
        elif scenario.config.simulation_type == SimulationType.STRESS:
            self.metrics.total_requests = 1000
            self.metrics.successful_requests = 900
            self.metrics.average_response_time = 1.2
            self.metrics.tokens_consumed = 5000
            self.metrics.cost_incurred = 2.5
        elif scenario.config.simulation_type == SimulationType.CONCURRENCY:
            self.metrics.total_requests = 200
            self.metrics.successful_requests = 180
            self.metrics.average_response_time = 0.8
            self.metrics.tokens_consumed = 1000
            self.metrics.cost_incurred = 1.0
        else:
            # Default simulation
            self.metrics.total_requests = 50
            self.metrics.successful_requests = 48
            self.metrics.average_response_time = 0.3
            self.metrics.tokens_consumed = 250
            self.metrics.cost_incurred = 0.25
        
        self.metrics.failed_requests = self.metrics.total_requests - self.metrics.successful_requests
        self.running = False
        
        return self.metrics
    
    def get_scenario_status(self) -> Dict[str, Any]:
        """Get status of all scenarios"""
        return {
            "total_scenarios": len(self.scenarios),
            "enabled_scenarios": len([s for s in self.scenarios if s.enabled]),
            "running": self.running,
            "scenarios": [
                {
                    "name": s.name,
                    "type": s.config.simulation_type.value,
                    "enabled": s.enabled,
                    "description": s.description
                }
                for s in self.scenarios
            ]
        }

# Global simulation runner instance
_global_simulation_runner: Optional[SimulationRunner] = None

def get_simulation_runner() -> SimulationRunner:
    """Get the global simulation runner instance"""
    global _global_simulation_runner
    if _global_simulation_runner is None:
        _global_simulation_runner = SimulationRunner()
    return _global_simulation_runner

def reset_simulation_runner() -> None:
    """Reset the global simulation runner (for testing)"""
    global _global_simulation_runner
    _global_simulation_runner = None
