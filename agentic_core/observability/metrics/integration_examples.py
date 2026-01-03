"""
Integration script for CoverageAgent
Demonstrates how to integrate CoverageAgent into the existing autonomy system
"""

# Example 1: Integration into existing agent base classes
# Add to your agent base class (e.g., SubAtomicAgent, CanonBaseAgent)

def track_activation_in_agent_base(self):
    """Add this method to your agent base class"""
    from agentic_core.observability.metrics.activation_hooks import track_agent_activation
    
    # Track activation when agent is instantiated or executed
    track_agent_activation(self.__class__.__name__)

# Example 2: Integration into orchestrator
# Add to your orchestrator's execute_agent method

def execute_agent_with_tracking(self, agent):
    """Execute agent with activation tracking"""
    from agentic_core.observability.metrics.activation_hooks import track_agent_activation
    
    # Track before execution
    track_agent_activation(agent.__class__.__name__)
    
    # Execute the agent
    return agent.execute()

# Example 3: Integration into workflow/pipeline systems
# Add tracking at key pipeline stages

def track_workflow_stage(stage_name: str):
    """Decorator for workflow stage tracking"""
    from agentic_core.observability.metrics.activation_hooks import track_layer_activation
    
    return track_layer_activation(stage_name)

# Example usage:
# @track_workflow_stage("L3_orchestration")
# def orchestrate_agents():
#     # Your orchestration logic
#     pass

# Example 4: Manual integration points
# Add manual tracking in key locations

# In agent discovery/registration
from agentic_core.observability.metrics.activation_hooks import manual_track

def register_agent(agent_class):
    """Register agent with tracking"""
    # Track when agent is discovered/registered
    manual_track("discovery")
    
    # Your registration logic here
    pass

# In compliance checks
def run_compliance_check():
    """Run compliance with tracking"""
    manual_track("L5_safety")
    
    # Your compliance logic here
    pass

# Example 5: Dashboard server integration
# Add to your dashboard startup script

def start_dashboard_with_api():
    """Start dashboard with metrics API"""
    from agentic_core.observability.metrics.dashboard_api import app
    import uvicorn
    
    # Start the API server alongside your dashboard
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

# Example 6: Production deployment configuration
# Configuration for production use

COVERAGE_AGENT_CONFIG = {
    "threshold_entropy": 2.4,  # Conservative threshold
    "intervention_mode": "report",  # Start with reporting only
    "dashboard_api_url": "http://localhost:8000/api/metrics",
    "tick_interval": 60,  # Check every minute
}

# For production, you might want:
PRODUCTION_CONFIG = {
    "threshold_entropy": 2.0,  # More sensitive threshold
    "intervention_mode": "bias_routing",  # Enable automatic interventions
    "dashboard_api_url": "http://dashboard-service:8000/api/metrics",
    "tick_interval": 30,  # Check every 30 seconds
}

# Example 7: Testing CoverageAgent
def test_coverage_agent():
    """Test CoverageAgent with mock data"""
    from agentic_core.observability.metrics.CoverageAgent import CoverageAgent
    from agentic_core.observability.metrics.shared_counters import increment_layer_activation
    
    # Create agent
    agent = CoverageAgent(threshold_entropy=2.4)
    
    # Simulate some activations
    for _ in range(100):
        increment_layer_activation("L3_orchestration")
    for _ in range(50):
        increment_layer_activation("L2_execution")
    for _ in range(10):
        increment_layer_activation("L5_safety")
    
    # Test the agent
    result = agent.act()
    print(result)
    
    # Expected output: CoverageAgent: Current entropy = 1.47 / 3.81 (threshold 2.40). 
    # Proportions: {'L3_orchestration': '62.5%', 'L2_execution': '31.2%', 'L5_safety': '6.2%'} 
    # IMBALANCE DETECTED — Underrepresented: L5_safety (6.2%). Recommend corrective action. Coverage balanced.

if __name__ == "__main__":
    test_coverage_agent()
