# Phase 2: Folder Purity Remediation

## Wave 1: agentic_core Remediation

### Pre-Wave Baseline

```text
git rev-parse HEAD: 624948408a34a443a773daeeda5ed23774c97429
```

### Violation Analysis

Based on Phase 1 test output, the violations fall into categories:

#### reasoning/ violations (need rule expansion)
- `*Executor.py` - legitimate reasoning executors
- `*Strategy.py` - legitimate strategies in reasoning
- `*Orchestrator.py` - legitimate orchestrators

#### validators/ violations
- `structure_drift_manifest.py` - not a validator, should be in config/

#### config/ violations
- `mcp_registry.py` - registry pattern, needs rule
- `blueprint_compiler.py` - compiler pattern, needs rule

#### types/ violations
- `*_contract.py` - contract pattern, needs rule
- `*_registry.py` - registry pattern, needs rule
- `*_validate.py` - validation helpers, needs rule
- `*_spec.py` - spec pattern, needs rule
- `*_result.py` - result pattern, needs rule
- `*_map.py` - map pattern, needs rule
- `*_seam.py` - seam pattern, needs rule
- PascalCase types (ImmutableStagingBuffer, etc.) - needs rule

#### utils/ violations
- snake_case utilities without _util suffix - needs rule expansion

### Remediation Strategy

**Approach: Extend FOLDER_PURITY_RULES to accommodate legitimate patterns rather than mass file moves.**

This is the correct approach because:
1. The existing files are in semantically correct locations
2. Mass moves would break imports across the codebase
3. The rules were too restrictive, not the file placements

---

## Wave 2: apps_lic Remediation

(To be appended)

---

## Wave 3: apps_rg + apps_shared Remediation

(To be appended)
