# Unified Sovereign Protocol Guide

## Overview

The **Unified Sovereign Protocol** (`execute_ssot.py`) represents the culmination of Phase 4 Deep Integration, merging the capabilities of the legacy `Canon Validator` and `SSOT Compliance Protocol` into a single, hardened, intelligent system.

## Architecture

### Core Components

1. **Ultra-Hardened Security Layer**
   - Atomic write patterns for state persistence
   - NonInteractiveGuard prevents CI/CD hangs
   - Retry logic with exponential backoff
   - Emergency cleanup prevents zombie states

2. **L3 Orchestration Integration**
   - Smart delegation to ConsolidatedOrchestratorAgent
   - Graceful fallback to L5 iteration
   - Mission context propagation

3. **Meta-Learning State Management**
   - Strategy weight tracking (`cot`, `tot`, `react`)
   - Experience history (last 5 experiences)
   - Pattern extraction metrics
   - Dashboard observability

4. **Autonomous Decision Engine**
   - Confidence-based healing decisions
   - Multi-factor confidence scoring
   - LLM override capability for low-confidence scenarios

## Usage

### Basic Commands

```bash
# Single territory scan (autonomous)
python agentic_core/L0_maintenance/scripts/execute_ssot.py --territory prompt_governance

# Multi-domain sweep with L3 orchestration attempt
python agentic_core/L0_maintenance/scripts/execute_ssot.py --domains

# With LLM assistance for low-confidence decisions
python agentic_core/L0_maintenance/scripts/execute_ssot.py --territory L5_safety --enable-llm

# List all discoverable agents
python agentic_core/L0_maintenance/scripts/execute_ssot.py --list-agents

# Run specific agent directly
python agentic_core/L0_maintenance/scripts/execute_ssot.py --agent NamingAgent
```

### Advanced Usage

```bash
# Manual mode (disables autonomous decisions)
python agentic_core/L0_maintenance/scripts/execute_ssot.py --territory prompt_governance --manual

# Multi-domain with full execution
python agentic_core/L0_maintenance/scripts/execute_ssot.py --domains --enable-llm
```

## Migration Guide

### From Canon Validator

**Old Command:**

```bash
python agentic_core/L0_maintenance/scripts/canon_validator_agentic_v2_thin.py --scan-mode comprehensive
```

**New Command (Equivalent):**

```bash
python agentic_core/L0_maintenance/scripts/execute_ssot.py --territory prompt_governance
```

**New Command (Enhanced - L3 Orchestration):**

```bash
python agentic_core/L0_maintenance/scripts/execute_ssot.py --domains
```

### From SSOT Compliance Protocol

**Old Command:**

```bash
python agentic_core/L0_maintenance/scripts/execute_ssot_compliance_protocol.py --territory prompt_governance
```

**New Command (Equivalent):**

```bash
python agentic_core/L0_maintenance/scripts/execute_ssot.py --territory prompt_governance
```

## Feature Parity Matrix

| Feature | Canon Validator | SSOT Protocol | Unified Protocol |
|---------|----------------|---------------|------------------|
| Agent Discovery | ✅ | ✅ | ✅ |
| Dashboard Integration | ✅ | ❌ | ✅ |
| Meta-Learning | ✅ | ❌ | ✅ |
| L3 Orchestration | ✅ | ❌ | ✅ |
| Atomic Writes | ❌ | ✅ | ✅ |
| Retry Logic | ❌ | ✅ | ✅ |
| NonInteractiveGuard | ❌ | ✅ | ✅ |
| Confidence Scoring | ❌ | ✅ | ✅ |
| Emergency Cleanup | ❌ | ✅ | ✅ |

## Execution Phases

### Phase 1: Territorial Discovery

- **Agent**: FilesystemSSOTReconcilerAgent + LocationAgent
- **Purpose**: Detect root drift and location violations
- **Output**: Drift report, location violations, confidence score

### Phase 2: Structural Alignment

- **Agent**: HierarchyAgent
- **Purpose**: Heal hierarchy violations
- **Output**: Structure healing results

### Phase 3: Architectural Validation

- **Agent**: ArchitectureGovernorAgent + SystemArchitectAgent
- **Purpose**: Validate architecture and imports
- **Output**: Governance report, architecture validation

### Phase 4: Healing

- **Agent**: ArchitectureGovernorAgent (healing mode)
- **Purpose**: Execute healing plan
- **Output**: Healing execution results

### Phase 5: Certification

- **Agent**: SovereignCertifier
- **Purpose**: Issue compliance certificate
- **Output**: Compliance certificate

## L3 Orchestration Flow

When using `--domains`, the protocol attempts L3 orchestration:

```text
1. Try to load ConsolidatedOrchestratorAgent
   ├── Success → Delegate mission to L3
   │   ├── Assemble active roster
   │   ├── Create mission context
   │   └── Execute via orchestrator.run_mission()
   └── Failure → Fall back to L5 iteration
       └── Execute standard 5-phase protocol
```

## Meta-Learning State

The protocol tracks cognitive metrics for dashboard observability:

```json
{
  "meta_learning": {
    "enabled": true,
    "total_experiences": 42,
    "patterns_extracted": 15,
    "strategy_weights": {
      "cot": 1.5,
      "tot": 0.8,
      "react": 1.7
    },
    "recent_experiences": [
      "L3 Mission Complete",
      "Healing Applied: 3 violations",
      "Architecture Validated"
    ]
  }
}
```

## Security Hardening

### Atomic Write Pattern

- Writes to temporary file first
- Sets strict permissions (600)
- Atomic replacement with `os.replace()`
- Prevents JSON corruption on crashes

### NonInteractiveGuard

- Monkey-patches `builtins.input`
- Blocks interactive prompts in autonomous mode
- Prevents CI/CD pipeline hangs
- Resource exhaustion protection

### Retry Logic

- Exponential backoff: `delay * (2^attempt)`
- Configurable max retries (default: 3)
- Preserves function metadata
- Comprehensive logging

### Emergency Cleanup

- `atexit.register()` guarantees cleanup
- Prevents zombie "running" states
- Works for SIGTERM, KeyboardInterrupt, etc.

## Dashboard Integration

Real-time state is persisted to `runtime_state.json`:

```json
{
  "status": "running",
  "start_time": "2026-01-27T20:37:00",
  "current_agent": "LocationAgent",
  "current_layer": "L5 - Safety",
  "agents_order": ["prompt_governance"],
  "completed_agents": [...],
  "events": [...],
  "meta_learning": {...},
  "compliance_scores": {...}
}
```

## Testing

### Integration Tests

```bash
# Run Phase 4 integration tests
python -m pytest tests/L0_maintenance/test_integration_parity.py -v

# Test specific features
python -m pytest tests/L0_maintenance/test_integration_parity.py::TestIntegrationParity::test_l3_orchestrator_success_delegation -v
```

### Test Coverage

- ✅ Meta-learning state updates
- ✅ L3 orchestration delegation
- ✅ Graceful fallback handling
- ✅ Confidence scoring integration
- ✅ Emergency cleanup mechanisms
- ✅ Atomic write simulation

## Troubleshooting

### L3 Orchestration Not Available

**Warning**: `L3 Orchestrator not found. Falling back to L5 iteration.`

**Solution**: This is normal behavior when L3 orchestration is not installed. The protocol will continue with L5 iteration.

### Interactive Prompt Blocked

**Warning**: `BLOCKED PROMPT: Agent attempted input(...)`

**Solution**: This indicates the NonInteractiveGuard is working correctly. The agent attempted to request user input in autonomous mode.

### Low Confidence Decisions

**Info**: `LOW CONFIDENCE (0.3) - LLM Disabled`

**Solution**: Use `--enable-llm` flag to allow LLM override for low-confidence scenarios, or use `--manual` mode for interactive decisions.

## Deprecation Timeline

- **January 27, 2026**: Legacy files deprecated and moved to `archives/deprecated/`
- **February 27, 2026**: Safe to remove deprecated files completely
- **March 27, 2026**: Documentation updates and training materials finalized

## Support

For migration assistance or questions:

- Review deprecation notices in `archives/deprecated/`
- Check integration test results
- Contact the Architecture Team

---

**Version**: 4.0 (Unified Sovereign Protocol)
**Last Updated**: January 27, 2026
**Status**: Production Ready ✅
