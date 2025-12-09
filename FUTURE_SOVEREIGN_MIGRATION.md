# FUTURE SOVEREIGN DIRECTORY MIGRATION PLAN
## Canon 2025 - Expansion Roadmap

### Current State ✅
- **SOVEREIGN_DIRS**: `{agentic_core, apps_lic, apps_rg, apps_shared}`
- **40/40 Validation**: PASSING
- **Pre-commit hooks**: Functional
- **Zombie extermination**: Active

### Target Expansion 🎯
**FUTURE_SOVEREIGN** directories to be added after cleanup:
- `schemas/` - Pydantic/JSON schemas for structured output
- `prompt_governance/` - Safety rails, refusal patterns, jailbreak filters  
- `observability/` - Tracing, metrics, audit logs
- `config/` - Runtime config + feature flags

---

## VIOLATIONS BY DIRECTORY

### 🔥 CRITICAL (Block Sovereign Status)

#### Key 11: Forbidden 'Any' Types
**Impact**: Safety violations - one bug = jailbreak
**Affected**: `prompt_governance/` safety files
- `apply_safety_policy.py: sanitize_node()` uses 'Any'
- `enforce_safety_filters.py: _calculate_depth()` uses 'Any'
- `validate_safety_ethics.py: _calculate_depth()` uses 'Any'
- `enforce_safety_budget.py: _calculate_depth()` uses 'Any'
- `track_safety_cost.py: _calculate_depth()` uses 'Any'
- `update_safety_usage.py: _calculate_depth()` uses 'Any'
- `apply_execution_safety.py: _calculate_depth()` uses 'Any'
- `validate_execution_ethics.py: _calculate_depth()` uses 'Any'

**Fix**: Replace `Any` with proper Union types or specific protocols

#### Key 24: Stub Files (<350 bytes)
**Impact**: Incomplete implementations
**Affected**: `prompt_governance/` 
- `guard_base.py` - stub implementation
- `policy_base.py` - stub implementation  
- `base.py` - stub implementation

**Fix**: Implement full functionality or move to utilities

---

### ⚠️ HIGH PRIORITY

#### Key 15: Retrieval Verbs Outside L4
**Impact**: Architectural violations
**Affected**: `observability/`, `schemas/`, `prompt_governance/`
- Files using `retrieve_*()` and `fetch_*()` outside L4 layer
- 17+ files need verb reclassification

**Fix**: Move retrieval logic to proper L4 layer or rename verbs

#### Key 22: Banned Tokens
**Impact**: Naming convention violations
**Affected**: All future sovereign directories
- `guard_base.py`, `policy_base.py`, `base.py` - "base" forbidden
- `sampling_processor.py` - "processor" forbidden

**Fix**: Rename to domain-specific names

---

### 📋 MEDIUM PRIORITY

#### Key 21: Bad File Names
**Affected**: `observability/`
- `w3c_trace_context.py` - naming convention issue

#### Key 23: Comment Violations
**Affected**: Multiple directories
- TODO/FIXME comments in production code

#### Key 28: Duplicate Files
**Affected**: `prompt_governance/`
- 6+ files with identical content
- Should move to `shared/` utilities

---

## MIGRATION STRATEGY

### Phase 1: Critical Safety Fixes
1. Fix Key 11 'Any' types in safety code
2. Implement Key 24 stub files or move to utilities
3. **Result**: Safety compliance achieved

### Phase 2: Architectural Cleanup
1. Fix Key 15 retrieval verb placement
2. Rename Key 22 banned token files
3. **Result**: Architectural compliance achieved

### Phase 3: Final Polish
1. Fix Key 21-28 remaining violations
2. Remove duplicates and cleanup comments
3. **Result**: Full 40/40 compliance

### Phase 4: Sovereign Expansion
1. Update `SOVEREIGN_DIRS` in `canon_validator.py`
2. Update pre-commit file patterns
3. Test 40/40 validation
4. **Result**: Full sovereign coverage achieved

---

## IMPLEMENTATION COMMANDS

### After Phase 3 Complete:
```bash
# Update canon_validator.py
SOVEREIGN_DIRS = {
    "agentic_core", "apps_lic", "apps_rg", "apps_shared",
    "schemas", "prompt_governance", "observability", "config"
}

# Update .pre-commit-config.yaml
files: ^(agentic_core|apps_lic|apps_rg|apps_shared|schemas|prompt_governance|observability|config)/.*\.py$

# Test expansion
python canon_validator.py  # Should pass 40/40
git commit -m "canon: expand sovereign directories to full production coverage"
```

---

## WHY THIS MATTERS

- `schemas/` - Defines contract with world (structured output) → must be perfect
- `prompt_governance/` - Safety layer → one bug = jailbreak  
- `observability/` - Audit compliance → one missing span = compliance failure
- `config/` - Live behavior control → one typo = catastrophe

These are **not utilities**. These are **core production code**.

*Canon 2025 - Migration Ready*
