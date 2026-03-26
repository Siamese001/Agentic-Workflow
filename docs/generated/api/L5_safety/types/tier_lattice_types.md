# API Documentation: tier_lattice_types

**Target Audience**: developers, api_users

# tier_lattice_types API Documentation

**File**: `tier_lattice_types.py`
**Classes**: 4
**Functions**: 5

## Classes

- **LearningTier** (inherits from <ast.Attribute object at 0x000001CBFB8E1350>)
- **DropPolicy** (inherits from <ast.Attribute object at 0x000001CBFCBA4710>)
- **TierLattice**
- **BackpressurePolicy**

## Functions

- **validate_escalation_sequence** -> bool
- **dominates** -> bool
- **drop_policy** -> DropPolicy
- **can_drop** -> bool
- **should_drop** -> bool


## Class: LearningTier

**Description**: Canonical learning tier enumeration.

**Inherits from**: enum.IntEnum



## Class: DropPolicy

**Description**: Backpressure drop policy per tier.

**Inherits from**: enum.Enum



## Class: TierLattice

**Description**: Formal partial order over LearningTier.

    Uses the natural integer ordering of IntEnum values.
    ``dominates(a, b)`` means ``a`` is strictly higher than
    ``b`` in the lattice (a > b).
    

### Methods

#### dominates
**Parameters**: self, a, b
**Returns**: bool
**Description**: Return True if ``a`` strictly dominates ``b``.

        Strict dominance: a.value > b.value.
        

#### drop_policy
**Parameters**: self, tier
**Returns**: DropPolicy
**Description**: Return the backpressure drop policy for a tier.

#### can_drop
**Parameters**: self, tier, under_pressure
**Returns**: bool
**Description**: Whether a signal at this tier may be dropped.



## Class: BackpressurePolicy

**Description**: Policy engine that references TierLattice for drops.

### Methods

#### should_drop
**Parameters**: self, tier, under_pressure
**Returns**: bool
**Description**: Decide whether to drop a signal at this tier.



## Function: validate_escalation_sequence

**Parameters**: sequence
**Returns**: bool
**Description**: Validate that a rollout sequence is monotonically
    non-decreasing (escalation monotonicity).

    Returns True if valid, False if any tier decreases.
    



## Function: dominates

**Parameters**: self, a, b
**Returns**: bool
**Description**: Return True if ``a`` strictly dominates ``b``.

        Strict dominance: a.value > b.value.
        



## Function: drop_policy

**Parameters**: self, tier
**Returns**: DropPolicy
**Description**: Return the backpressure drop policy for a tier.



## Function: can_drop

**Parameters**: self, tier, under_pressure
**Returns**: bool
**Description**: Whether a signal at this tier may be dropped.



## Function: should_drop

**Parameters**: self, tier, under_pressure
**Returns**: bool
**Description**: Decide whether to drop a signal at this tier.



## Usage Examples

### Class Usage

```python
# Using LearningTier
learningtier = LearningTier()
```

```python
# Using DropPolicy
droppolicy = DropPolicy()
```

```python
# Using TierLattice
tierlattice = TierLattice()
tierlattice.dominates()
tierlattice.drop_policy()
```

### Function Usage

```python
# Using validate_escalation_sequence
result = validate_escalation_sequence(sequence)
```

```python
# Using dominates
result = dominates(a, b)
```

```python
# Using drop_policy
result = drop_policy(tier)
```



---
**Generated**: 2026-03-26T09:39:05.588374
**Type**: api_reference
**Quality**: comprehensive
