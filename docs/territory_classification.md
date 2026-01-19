# Territory Classification Rules (Single Source of Truth)

**Date**: January 05, 2026  
**Status**: Active — All L1-L5 Base Class consistency achieved

## Universal Rules

- **Base Class**: Any agent with class name ending in "BaseAgent" → dedicated "Base Class" subterritory.
  - Applies uniformly to **L1-L5**.
  - Detection: `AutonomyGuardianAgent._classify_subterritory()`
  - Targets: invocation="N/A", observability="N/A" (via `autonomy_targets.py` pattern)
  - Rationale: Abstract bases require separate tracking and relaxed metrics.

## Layer-Specific Rules

### L0-L4

- Standard subterritories:
  - Infrastructure: path/name heuristics (e.g., observability, config, storage, caching)
  - Specialized: sovereign clients, RL agents, meta-agents (high-specificity naming)
  - Default: Core

### L5 Safety — Intentional Exception

- Domain-specific categories (no Core/Infrastructure/Specialized):
  - `guardrails/` → Guardrails
  - `validators/` → Validators
  - `gravity/` → Gravity
  - `red_teaming/` → Red Teaming
- Base Class: handled universally above
- Rationale: Safety domain decomposition provides clearer compliance visibility than generic categories.

## Display Rules

- Always use full subterritory names (no abbreviations like "Base Cl", "Infrast").

## References

- Discovery: `scripts/full_agent_discovery.py`
- Classification: `agentic_core/L5_safety/validators/AutonomyGuardianAgent.py` (`_classify_subterritory`, `_get_territory_agents`)
- Targets: `agentic_core/config/autonomy_targets.py`
- Tests: `scripts/comprehensive_dashboard_tests.py` (territory structure consistency tests)
