# Heal Capability % - Final Definition

**Last Updated:** 2026-01-14
**Status:** CANONICAL (SSOT)

## Definition

**Heal Capability %** = Percentage of agents that have healing capability through any of the following:

### 1. Direct Implementation
Agent defines one of these methods:
- `heal()` - General healing method
- `apply_fix()` - Fix application method
- `heal_violation()` - Violation-specific healing
- `heal_repository()` - Repository-level healing

### 2. Inheritance (MRO-Aware)
Agent inherits healing capability through the Method Resolution Order (MRO) chain:
- Inherits from `HealerMixin`
- Inherits from any class that has healing capability

## Factory Analogy

> **Workers who have access to repair tools** — either their own personal toolkit at their station (direct implementation) OR access to the factory's shared repair equipment through their department (inheritance). They CAN fix issues.

## Related Metric: Heal Invocation %

**Heal Invocation %** = Percentage of agents that **actively call** `super().heal_repository()` in their `heal_repository()` method.

> **Workers who actually USE the repair tools** — they not only have access to tools but actively invoke the repair chain when issues occur.

### Key Distinction

| Metric | Question Answered |
|--------|-------------------|
| **Heal Cap %** | "Can this agent heal?" (Has capability) |
| **Heal Invocation %** | "Does this agent properly invoke the healing chain?" (Uses capability correctly) |

## Implementation (SSOT)

From `scripts/full_agent_discovery.py`:

```python
# Line 1400-1402
has_heal = has_method(node, 'heal') or has_method(node, 'apply_fix') or has_method(node, 'heal_violation') or has_method(node, 'heal_repository')
inherits_healing = has_healing_in_chain(node.name, bases)
has_healing = has_heal or inherits_healing
```

## Current Status

- **Heal Cap %**: 100.0% (all 265 agents have healing capability)
- **Heal Invocation %**: 96.2% (255/265 agents properly invoke super().heal_repository())

## Why This Matters

1. **Heal Cap % at 100%** means every agent CAN participate in healing
2. **Heal Invocation % < 100%** means some agents with `heal_repository()` overrides don't call `super()`, breaking the MRO healing chain
3. The gap between these metrics identifies agents that need `super().heal_repository()` calls added

## Files Involved

- `scripts/full_agent_discovery.py` - Detection logic (SSOT)
- `scripts/regenerate_dashboard_full.py` - Dashboard calculation
- `agentic_core/common/healing/healer_mixin.py` - HealerMixin implementation
