# CoverageAgent - Layer Activation Entropy Monitoring

## Overview
CoverageAgent monitors the distribution of layer activations across the autonomous system using Shannon entropy to detect imbalances in system coverage.

## Files Created
- `CoverageAgent.py` - Main agent implementation
- `shared_counters.py` - Global layer activation tracking
- `dashboard_api.py` - REST API endpoint for metrics
- `coordinator.py` - Periodic execution coordinator
- `activation_hooks.py` - Integration utilities and decorators
- `integration_examples.py` - Complete integration examples

## Key Features
- **Entropy-based monitoring**: Uses Shannon entropy to measure distribution balance
- **Configurable threshold**: Default 2.4 (tunable based on system needs)
- **Multiple intervention modes**: report, bias_routing, inject_tasks
- **Real-time alerts**: Detects underrepresented layers
- **Compliance logging**: Tracks violations for audit trails

## Integration Steps

### 1. Add activation tracking to your agents
```python
from agentic_core.observability.metrics.activation_hooks import track_agent_activation

# In your agent base class
class SubAtomicAgent:
    def __init__(self):
        track_agent_activation(self.__class__.__name__)
```

### 2. Start the metrics API
```python
from agentic_core.observability.metrics.dashboard_api import app
import uvicorn

uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 3. Run the coordinator
```python
from agentic_core.observability.metrics.coordinator import ObservabilityCoordinator

coordinator = ObservabilityCoordinator(tick_interval=60)
coordinator.start_periodic_execution()
```

## Configuration Options

### Conservative (Development)
```python
CoverageAgent(
    threshold_entropy=2.4,
    intervention_mode="report"
)
```

### Sensitive (Production)
```python
CoverageAgent(
    threshold_entropy=2.0,
    intervention_mode="bias_routing"
)
```

## Monitoring Output Example
```
CoverageAgent: Current entropy = 1.47 / 3.81 (threshold 2.40). 
Proportions: {'L3_orchestration': '62.5%', 'L2_execution': '31.2%', 'L5_safety': '6.2%'} 
IMBALANCE DETECTED — Underrepresented: L5_safety (6.2%). Recommend corrective action.
```

## Dependencies
- numpy
- requests
- fastapi (for API server)
- uvicorn (for API server)

Install with:
```bash
pip install numpy requests fastapi uvicorn
```

## Next Steps
1. Integrate activation hooks into your agent base classes
2. Deploy the metrics API alongside your dashboard
3. Configure the coordinator with appropriate thresholds
4. Monitor alerts and adjust intervention modes as needed
