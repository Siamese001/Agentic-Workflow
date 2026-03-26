# API Documentation: providers

**Target Audience**: developers, api_users

# providers API Documentation

**File**: `providers.py`
**Classes**: 7
**Functions**: 32

## Classes

- **ClockProvider** (inherits from ABC)
- **RandomProvider** (inherits from ABC)
- **WallClock** (inherits from ClockProvider)
- **OsRandom** (inherits from RandomProvider)
- **FrozenClock** (inherits from ClockProvider)
- **SeededRandom** (inherits from RandomProvider)
- **MonotonicSequenceClock** (inherits from ClockProvider)

## Functions

- **get_clock** -> ClockProvider
- **get_random** -> RandomProvider
- **set_clock** -> None
- **set_random** -> None
- **reset_providers** -> None
- **now** -> datetime
- **now_iso** -> str
- **now_epoch** -> float
- **emit_replay_key** -> str
- **emit_determinism_digest** -> str
- **randint** -> int
- **random** -> float
- **choice** -> Any
- **seed_value** -> int | str | None
- **emit_seeds_rng** -> None
- **__init__** -> None
- **now** -> datetime
- **__init__** -> None
- **randint** -> int
- **random** -> float
- **choice** -> Any
- **seed_value** -> None
- **__init__** -> None
- **now** -> datetime
- **frozen** -> datetime
- **__init__** -> None
- **randint** -> int
- **random** -> float
- **choice** -> Any
- **seed_value** -> int
- **__init__** -> None
- **now** -> datetime


## Class: ClockProvider

**Description**: Abstract injectable clock replacing datetime.now() / time.time().

**Inherits from**: ABC

### Methods

#### now
**Parameters**: self
**Returns**: datetime
**Description**: Return current datetime (timezone-aware UTC).

#### now_iso
**Parameters**: self
**Returns**: str
**Description**: Return ISO-8601 string of current time.

#### now_epoch
**Parameters**: self
**Returns**: float
**Description**: Return POSIX timestamp.

#### emit_replay_key
**Parameters**: self, context
**Returns**: str
**Description**: Emit a deterministic replay key covering this clock value.

        ADG edge: ``emits_replay_key``.
        

#### emit_determinism_digest
**Parameters**: self, inputs
**Returns**: str
**Description**: Emit a determinism digest covering inputs + current clock value.

        ADG edge: ``emits_determinism_digest``.
        



## Class: RandomProvider

**Description**: Abstract injectable random source replacing random.* / os.urandom calls.

**Inherits from**: ABC

### Methods

#### randint
**Parameters**: self, a, b
**Returns**: int
**Description**: Return random integer N such that a <= N <= b.

#### random
**Parameters**: self
**Returns**: float
**Description**: Return random float in [0.0, 1.0).

#### choice
**Parameters**: self, seq
**Returns**: Any
**Description**: Return random element from seq.

#### seed_value
**Parameters**: self
**Returns**: int | str | None
**Description**: Return the seed used, or None if non-deterministic.

#### emit_seeds_rng
**Parameters**: self, context
**Returns**: None
**Description**: Log that RNG was seeded for this context.

        ADG edge: ``seeds_rng``.
        



## Class: WallClock

**Description**: Production clock: returns real wall-clock time.

    Records values into trace_context if provided so they can be replayed.
    ADG edge: ``patches_time`` (any caller using WallClock instead of datetime.now).
    

**Inherits from**: ClockProvider

### Methods

#### __init__
**Parameters**: self, trace_context
**Returns**: None

#### now
**Parameters**: self
**Returns**: datetime



## Class: OsRandom

**Description**: Production random: uses Python stdlib random (non-deterministic by default).

    Records seed into trace_context if provided.
    

**Inherits from**: RandomProvider

### Methods

#### __init__
**Parameters**: self, trace_context
**Returns**: None

#### randint
**Parameters**: self, a, b
**Returns**: int

#### random
**Parameters**: self
**Returns**: float

#### choice
**Parameters**: self, seq
**Returns**: Any

#### seed_value
**Parameters**: self
**Returns**: None



## Class: FrozenClock

**Description**: Test clock: always returns the same instant.

    ADG edge: ``patches_time``.

    Args:
        frozen_time: ISO-8601 string, datetime, or POSIX float. Defaults to epoch.
    

**Inherits from**: ClockProvider

### Methods

#### __init__
**Parameters**: self, frozen_time
**Returns**: None

#### now
**Parameters**: self
**Returns**: datetime

#### frozen
**Parameters**: self
**Returns**: datetime



## Class: SeededRandom

**Description**: Deterministic random with a fixed seed.

    ADG edge: ``seeds_rng``.

    Args:
        seed: Integer seed for reproducible sequences.
    

**Inherits from**: RandomProvider

### Methods

#### __init__
**Parameters**: self, seed
**Returns**: None

#### randint
**Parameters**: self, a, b
**Returns**: int

#### random
**Parameters**: self
**Returns**: float

#### choice
**Parameters**: self, seq
**Returns**: Any

#### seed_value
**Parameters**: self
**Returns**: int



## Class: MonotonicSequenceClock

**Description**: Test clock that advances by a fixed delta on each call.

    Useful for testing time-ordered sequences without relying on wall clock.
    

**Inherits from**: ClockProvider

### Methods

#### __init__
**Parameters**: self, start, step_seconds
**Returns**: None

#### now
**Parameters**: self
**Returns**: datetime



## Function: get_clock

**Returns**: ClockProvider
**Description**: Return the process-level ClockProvider.



## Function: get_random

**Returns**: RandomProvider
**Description**: Return the process-level RandomProvider.



## Function: set_clock

**Parameters**: provider
**Returns**: None
**Description**: Replace the process-level ClockProvider (test injection).



## Function: set_random

**Parameters**: provider
**Returns**: None
**Description**: Replace the process-level RandomProvider (test injection).



## Function: reset_providers

**Returns**: None
**Description**: Reset both providers to production defaults (test teardown).



## Function: now

**Parameters**: self
**Returns**: datetime
**Description**: Return current datetime (timezone-aware UTC).



## Function: now_iso

**Parameters**: self
**Returns**: str
**Description**: Return ISO-8601 string of current time.



## Function: now_epoch

**Parameters**: self
**Returns**: float
**Description**: Return POSIX timestamp.



## Function: emit_replay_key

**Parameters**: self, context
**Returns**: str
**Description**: Emit a deterministic replay key covering this clock value.

        ADG edge: ``emits_replay_key``.
        



## Function: emit_determinism_digest

**Parameters**: self, inputs
**Returns**: str
**Description**: Emit a determinism digest covering inputs + current clock value.

        ADG edge: ``emits_determinism_digest``.
        



## Function: randint

**Parameters**: self, a, b
**Returns**: int
**Description**: Return random integer N such that a <= N <= b.



## Function: random

**Parameters**: self
**Returns**: float
**Description**: Return random float in [0.0, 1.0).



## Function: choice

**Parameters**: self, seq
**Returns**: Any
**Description**: Return random element from seq.



## Function: seed_value

**Parameters**: self
**Returns**: int | str | None
**Description**: Return the seed used, or None if non-deterministic.



## Function: emit_seeds_rng

**Parameters**: self, context
**Returns**: None
**Description**: Log that RNG was seeded for this context.

        ADG edge: ``seeds_rng``.
        



## Function: __init__

**Parameters**: self, trace_context
**Returns**: None


## Function: now

**Parameters**: self
**Returns**: datetime


## Function: __init__

**Parameters**: self, trace_context
**Returns**: None


## Function: randint

**Parameters**: self, a, b
**Returns**: int


## Function: random

**Parameters**: self
**Returns**: float


## Function: choice

**Parameters**: self, seq
**Returns**: Any


## Function: seed_value

**Parameters**: self
**Returns**: None


## Function: __init__

**Parameters**: self, frozen_time
**Returns**: None


## Function: now

**Parameters**: self
**Returns**: datetime


## Function: frozen

**Parameters**: self
**Returns**: datetime


## Function: __init__

**Parameters**: self, seed
**Returns**: None


## Function: randint

**Parameters**: self, a, b
**Returns**: int


## Function: random

**Parameters**: self
**Returns**: float


## Function: choice

**Parameters**: self, seq
**Returns**: Any


## Function: seed_value

**Parameters**: self
**Returns**: int


## Function: __init__

**Parameters**: self, start, step_seconds
**Returns**: None


## Function: now

**Parameters**: self
**Returns**: datetime


## Usage Examples

### Class Usage

```python
# Using ClockProvider
clockprovider = ClockProvider()
clockprovider.now()
clockprovider.now_iso()
```

```python
# Using RandomProvider
randomprovider = RandomProvider()
randomprovider.randint()
randomprovider.random()
```

```python
# Using WallClock
wallclock = WallClock()
wallclock.now()
```

### Function Usage

```python
# Using get_clock
result = get_clock()
```

```python
# Using get_random
result = get_random()
```

```python
# Using set_clock
result = set_clock(provider)
```



---
**Generated**: 2026-03-26T09:39:03.581842
**Type**: api_reference
**Quality**: comprehensive
