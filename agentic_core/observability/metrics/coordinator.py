"""
Observability Coordinator - Manages periodic execution of observability agents
Coordinates metrics collection, benchmarking, and coverage monitoring
PHASE 8: Integrated MetaCoverageOptimizerAgent for autonomous self-optimization
"""

from .CoverageAgent import CoverageAgent
from .MetaCoverageOptimizerAgent import MetaCoverageOptimizerAgent
from .MetricsAgent import MetricsAgent  # Assuming this exists
from .BenchmarkingAgent import BenchmarkingAgent  # Assuming this exists
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ObservabilityCoordinator:
    def __init__(self, tick_interval: int = 60):
        """
        Initialize the observability coordinator
        
        Args:
            tick_interval: Seconds between periodic ticks (default: 60)
        """
        self.tick_interval = tick_interval
        self.coverage_agent = CoverageAgent(
            threshold_entropy=2.4, 
            intervention_mode="report"
        )
        self.meta_optimizer = MetaCoverageOptimizerAgent()
        self.agents = [
            MetricsAgent(),
            BenchmarkingAgent(),
            self.coverage_agent,
        ]
        self.running = False
        self.cycle_count = 0
        self.optimizer_interval = 100  # Run optimizer every 100 cycles

    def periodic_tick(self):
        """Execute one tick of all observability agents"""
        self.cycle_count += 1
        
        for agent in self.agents:
            try:
                result = agent.act()
                logger.info(f"Observability tick - {result}")
            except Exception as e:
                logger.error(f"Error in {agent.__class__.__name__}: {e}")
        
        # Run meta-optimizer periodically (Phase 8)
        if self.cycle_count % self.optimizer_interval == 0:
            try:
                optimizer_result = self.meta_optimizer.act()
                logger.info(f"Meta-Optimizer tick - {optimizer_result}")
            except Exception as e:
                logger.error(f"Error in MetaCoverageOptimizerAgent: {e}")

    def start_periodic_execution(self):
        """Start the periodic execution loop"""
        self.running = True
        logger.info("Starting observability coordinator...")
        
        while self.running:
            try:
                self.periodic_tick()
                time.sleep(self.tick_interval)
            except KeyboardInterrupt:
                logger.info("Observability coordinator stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in coordinator loop: {e}")
                time.sleep(self.tick_interval)

    def stop(self):
        """Stop the periodic execution"""
        self.running = False
        logger.info("Stopping observability coordinator...")

    def add_agent(self, agent):
        """Add a new observability agent"""
        self.agents.append(agent)
        logger.info(f"Added agent: {agent.__class__.__name__}")

    def remove_agent(self, agent_type):
        """Remove an observability agent by type"""
        self.agents = [agent for agent in self.agents if not isinstance(agent, agent_type)]
        logger.info(f"Removed agents of type: {agent_type.__name__}")

# Example usage
if __name__ == "__main__":
    coordinator = ObservabilityCoordinator(tick_interval=30)
    
    try:
        coordinator.start_periodic_execution()
    except KeyboardInterrupt:
        coordinator.stop()
