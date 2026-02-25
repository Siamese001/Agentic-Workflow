# Circuit Breaker and Line-Count Guard Implementation

## Overview

This document summarizes the implementation of circuit breaker and line-count guard protection for the Shared Alignment Intelligence in `LocationAgent`. These safeguards prevent mass-migration to `apps_shared` and ensure only significant files are considered for shared upgrades.

## Implementation Details

### 1. Configuration Updates (`structure_blueprint.py`)

Added circuit breaker configuration to `HEALING_CONFIG`:

```python
HEALING_CONFIG: Final[Mapping[str, int]] = {
    "max_rounds": int(os.getenv("MAX_HEALING_ROUNDS", "10")),
    "max_per_file": int(os.getenv("MAX_HEALING_PER_FILE", "8")),
    "global_budget": int(
        os.getenv("GLOBAL_HEALING_BUDGET", "500")
    ),  # [TEMP BOOST] Unblock 10k Violation backlog
    "max_moves_per_run": 250,
    "max_shared_upgrades_per_run": 10,  # [CIRCUIT BREAKER] Prevent mass-migration to apps_shared
    "max_fissions_per_run": 50,
    "dust_threshold": 40,  # Minimum lines for a module to exist (Span-of-Two)
}
```

**Key Parameters:**
- `max_shared_upgrades_per_run`: 10 - Maximum shared upgrades per run
- `dust_threshold`: 40 - Minimum lines for a file to be considered significant

### 2. Circuit Breaker Logic (`LocationAgent.py`)

Enhanced the global candidate detection logic in `deep_import_validation_and_heal`:

```python
# [HARDENING] GLOBAL CANDIDATE DETECTION logic
# If scores for BOTH apps are low but the file is in an app folder
shared_upgrade_count = getattr(self, "_shared_upgrade_count", 0)
from agentic_core.L5_safety.validators.structure_blueprint import HEALING_CONFIG

# 1. Check if file is significant enough to score (Dust Threshold)
with open(path, 'r') as f:
    if len(f.readlines()) < HEALING_CONFIG["dust_threshold"]:
        return # Skip boilerplate/noise

# 2. Check Circuit Breaker before shared upgrade
if (app_rg + app_lic) < AST_DOMAIN_HIT_THRESHOLD * 0.5:
    if shared_upgrade_count >= HEALING_CONFIG["max_shared_upgrades_per_run"]:
        Logger.error(f"CIRCUIT BREAKER TRIPPED: Shared upgrade limit reached at {path}")
        return

    target = self.project_root / "apps_shared" / "utils" / path.name
    move_result = self.safe_move(path, target, dry_run=False)
    self._shared_upgrade_count = shared_upgrade_count + 1
    additional_moves.append(move_result)
```

**Key Features:**
- **Dust Threshold Guard**: Files with fewer than 40 lines are skipped
- **Circuit Breaker**: Stops shared upgrades after 10 upgrades per run
- **Error Logging**: Logs when circuit breaker is tripped
- **Counter Tracking**: Tracks shared upgrades via `_shared_upgrade_count`

### 3. Comprehensive Test Suite (`test_shared_upgrade_circuit_breaker.py`)

Created 7 comprehensive tests to verify circuit breaker functionality:

#### Test Coverage:
1. **`test_shared_upgrade_circuit_breaker`** - Verifies circuit breaker prevents upgrades when limit exceeded
2. **`test_dust_threshold_prevents_upgrade`** - Ensures tiny files are skipped
3. **`test_circuit_breaker_allows_under_limit`** - Confirms upgrades work normally under limit
4. **`test_circuit_breaker_logs_error_when_tripped`** - Validates error logging when tripped
5. **`test_circuit_breaker_resets_on_new_instance`** - Ensures counter resets for new instances
6. **`test_dust_threshold_configuration`** - Verifies dust threshold is properly configured
7. **`test_max_shared_upgrades_configuration`** - Validates max shared upgrades limit

#### Test Results:
```
================================================================================= 7 passed, 7 warnings in 9.77s ==================================================================================
```

## Protection Mechanisms

### 1. Mass-Migration Prevention
- **Problem**: Without safeguards, the shared upgrade logic could move hundreds of files to `apps_shared` in a single run
- **Solution**: Circuit breaker limits upgrades to 10 per run
- **Benefit**: Prevents repository structure disruption

### 2. Noise Filtering
- **Problem**: Boilerplate files, tests, or tiny utility files could be incorrectly upgraded
- **Solution**: Dust threshold requires minimum 40 lines
- **Benefit**: Only significant modules are considered

### 3. Error Visibility
- **Problem**: Silent failures when limits are reached
- **Solution**: Clear error logging when circuit breaker trips
- **Benefit**: Operators can identify when limits are hit

## Integration with Existing Logic

The circuit breaker integrates seamlessly with existing Shared Alignment Intelligence:

1. **Score-Based Detection**: Still uses AST domain scores for upgrade decisions
2. **Threshold Logic**: Maintains existing low/high threshold boundaries
3. **Target Path Construction**: Preserves `apps_shared/utils/` targeting
4. **Move Operations**: Uses existing `safe_move` infrastructure

## Configuration Values

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `max_shared_upgrades_per_run` | 10 | Conservative limit to prevent mass migration |
| `dust_threshold` | 40 | "Span-of-Two" principle - ensures meaningful modules |
| `AST_DOMAIN_HIT_THRESHOLD` | 2.0 | Existing threshold for domain specificity |
| Low threshold | 1.0 (0.5 × 2.0) | Triggers shared upgrade consideration |
| High threshold | 1.6 (0.8 × 2.0) | Triggers domain retention |

## Backward Compatibility

- **No Breaking Changes**: Existing functionality preserved
- **Optional Safeguards**: Circuit breaker only activates when limits reached
- **Configuration Driven**: Values can be adjusted via `HEALING_CONFIG`
- **Graceful Degradation**: System continues functioning when limits hit

## Testing Strategy

### Mock Strategy
- **Import Agent Mocking**: Prevents CodeHealerAgent initialization issues
- **AST Score Mocking**: Provides controlled test scenarios
- **File I/O Mocking**: Simulates various file sizes and contents
- **Logger Mocking**: Captures error messages for validation

### Test Scenarios
- **Edge Cases**: Files at threshold boundaries
- **Error Conditions**: Circuit breaker tripped scenarios
- **Normal Operation**: Under-limit upgrade scenarios
- **Configuration Validation**: Ensuring proper setup

## Performance Impact

- **Minimal Overhead**: Simple counter increment and comparison
- **File I/O**: One additional read for line count check
- **Memory**: Single integer counter per agent instance
- **Logging**: Only when limits exceeded

## Future Enhancements

### Potential Improvements
1. **Configurable Thresholds**: Per-project customization
2. **Adaptive Limits**: Dynamic adjustment based on repository size
3. **Selective Reset**: Manual counter reset capabilities
4. **Metrics Collection**: Track upgrade patterns over time
5. **Whitelist Support**: Exception handling for specific files

### Monitoring Considerations
- **Circuit Breaker Events**: Log when limits are reached
- **Upgrade Patterns**: Track which types of files get upgraded
- **Threshold Effectiveness**: Monitor if dust threshold is appropriate
- **Repository Health**: Assess impact on code organization

## Conclusion

The circuit breaker and line-count guard implementation provides robust protection against mass-migration while preserving the intelligent shared upgrade capabilities of the LocationAgent. The comprehensive test suite ensures reliability and the configuration-driven approach allows for easy adjustment as needs evolve.

**Status**: ✅ **IMPLEMENTATION COMPLETE** - All tests passing, safeguards active
