# API Documentation: oscillation_firewall_gate

**Target Audience**: developers, api_users

# oscillation_firewall_gate API Documentation

**File**: `oscillation_firewall_gate.py`
**Classes**: 3
**Functions**: 8

## Classes

- **OscillationFirewallTripped** (inherits from RuntimeError)
- **OscillationFirewallConfig**
- **OscillationFirewall**

## Functions

- **validate_threshold** -> bool
- **__post_init__** -> None
- **__init__** -> None
- **record_tier_decision** -> None
- **assert_no_oscillation** -> None
- **is_tier_frozen** -> bool
- **get_frozen_tiers** -> set[str]
- **reset_for_testing** -> None


## Class: OscillationFirewallTripped

**Description**: Raised when routing-tier oscillation is detected and firewall fires.

**Inherits from**: RuntimeError



## Class: OscillationFirewallConfig

**Description**: Configuration for the oscillation firewall.

    Fields:
        cooldown_window: Number of recent tier decisions to inspect.
        freeze_cycles:   Number of cycles a tier is frozen after oscillation.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: OscillationFirewall

**Description**: Routing-tier oscillation firewall.

    Wraps system_learning.enforcement.oscillation_detector.OscillationDetector
    with routing-tier semantics.  Each tier is tracked independently; an
    oscillation in *any* tier triggers a freeze for that tier.

    Args:
        config: OscillationFirewallConfig (defaults are conservative).
    

### Methods

#### __init__
**Parameters**: self, config
**Returns**: None

#### record_tier_decision
**Parameters**: self, tier, cycle
**Returns**: None
**Description**: Record that *tier* was chosen at *cycle*.

        This is the non-raising variant — use for observation only.
        

#### assert_no_oscillation
**Parameters**: self, tier, cycle
**Returns**: None
**Description**: Assert that accepting *tier* at *cycle* does not complete oscillation.

        Tracks a single "routing_tier" parameter whose value is the tier name.
        DETERMINISTIC->QWEN->DETERMINISTIC is two value-flips = oscillation.

        Raises:
            OscillationFirewallTripped: if oscillation pattern is detected.
        

#### is_tier_frozen
**Parameters**: self, tier, cycle
**Returns**: bool
**Description**: Return True if routing_tier parameter is frozen at *cycle*.

#### get_frozen_tiers
**Parameters**: self, cycle
**Returns**: set[str]
**Description**: Return set of tier names currently frozen at *cycle*.

#### reset_for_testing
**Parameters**: self
**Returns**: None
**Description**: Clear all state for test isolation.



## Function: validate_threshold

**Parameters**: tier_sequence, config
**Returns**: bool
**Description**: Return True if *tier_sequence* does NOT contain an oscillation pattern.

    Stateless alternative to OscillationFirewall.  Used in invariant tests
    to assert that a recorded sequence is stable.

    An oscillation is defined as: the same tier appearing at least twice
    with a different tier interspersed, within the cooldown_window.
    



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __init__

**Parameters**: self, config
**Returns**: None


## Function: record_tier_decision

**Parameters**: self, tier, cycle
**Returns**: None
**Description**: Record that *tier* was chosen at *cycle*.

        This is the non-raising variant — use for observation only.
        



## Function: assert_no_oscillation

**Parameters**: self, tier, cycle
**Returns**: None
**Description**: Assert that accepting *tier* at *cycle* does not complete oscillation.

        Tracks a single "routing_tier" parameter whose value is the tier name.
        DETERMINISTIC->QWEN->DETERMINISTIC is two value-flips = oscillation.

        Raises:
            OscillationFirewallTripped: if oscillation pattern is detected.
        



## Function: is_tier_frozen

**Parameters**: self, tier, cycle
**Returns**: bool
**Description**: Return True if routing_tier parameter is frozen at *cycle*.



## Function: get_frozen_tiers

**Parameters**: self, cycle
**Returns**: set[str]
**Description**: Return set of tier names currently frozen at *cycle*.



## Function: reset_for_testing

**Parameters**: self
**Returns**: None
**Description**: Clear all state for test isolation.



## Usage Examples

### Class Usage

```python
# Using OscillationFirewallTripped
oscillationfirewalltripped = OscillationFirewallTripped()
```

```python
# Using OscillationFirewallConfig
oscillationfirewallconfig = OscillationFirewallConfig()
```

```python
# Using OscillationFirewall
oscillationfirewall = OscillationFirewall()
oscillationfirewall.record_tier_decision()
oscillationfirewall.assert_no_oscillation()
```

### Function Usage

```python
# Using validate_threshold
result = validate_threshold(tier_sequence, config)
```

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using __init__
result = __init__(config)
```



---
**Generated**: 2026-03-26T09:39:04.888148
**Type**: api_reference
**Quality**: comprehensive
