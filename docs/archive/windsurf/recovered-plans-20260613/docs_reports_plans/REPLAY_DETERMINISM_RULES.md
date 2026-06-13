# Replay Determinism Rules

## SCOPE
Governs: **L2 Execution Layer** (Deterministic Execution, Replay Validation)

Defines L2 determinism canonicalization rules for guaranteed replay integrity.

---

L2 determinism canonicalization for guaranteed replay integrity.

---

## Determinism Requirements

All L2 execution must be deterministic and replay-capable with identical outputs given identical inputs.

---

## Fixed Random Seed Injection

```python
class DeterministicRandomSource:
    """Deterministic random number generator for replay"""

    def __init__(self, trace_id: str):
        """
        Initialize deterministic RNG from trace ID.

        REQUIREMENTS:
        - Seed derived from trace_id (deterministic)
        - Same trace_id → same random sequence
        - No system entropy allowed
        """
        import hashlib

        # Derive seed from trace_id
        seed_bytes = hashlib.sha256(trace_id.encode()).digest()
        self.seed = int.from_bytes(seed_bytes[:8], byteorder='big')

        # Initialize RNG
        import random
        self.rng = random.Random(self.seed)

    def random(self) -> float:
        """Generate deterministic random float [0.0, 1.0)"""
        return self.rng.random()

    def randint(self, a: int, b: int) -> int:
        """Generate deterministic random integer [a, b]"""
        return self.rng.randint(a, b)

    def choice(self, seq):
        """Choose deterministic random element from sequence"""
        return self.rng.choice(seq)

    def shuffle(self, seq):
        """Shuffle sequence deterministically (in-place)"""
        self.rng.shuffle(seq)
        return seq

# Usage in L2 execution
class L2ExecutionSandbox:
    def __init__(self, trace_id: str):
        self.trace_id = trace_id
        self.random_source = DeterministicRandomSource(trace_id)

    def execute_with_determinism(self, code: str):
        """Execute code with deterministic random source"""

        # Inject deterministic random into execution context
        exec_globals = {
            'random': self.random_source.random,
            'randint': self.random_source.randint,
            'choice': self.random_source.choice,
        }

        exec(code, exec_globals)
```

### Invariant
**No system entropy allowed. All randomness must be derived from trace_id.**

---

## Virtualized Clock Source

```python
class VirtualizedClock:
    """Virtualized clock for deterministic time operations"""

    def __init__(self, base_timestamp: str):
        """
        Initialize virtual clock from base timestamp.

        REQUIREMENTS:
        - Base timestamp from sealed dispatch
        - Clock advances deterministically
        - No system time allowed
        """
        from datetime import datetime

        self.base_time = datetime.fromisoformat(base_timestamp)
        self.elapsed_seconds = 0

    def now(self) -> datetime:
        """Get current virtual time"""
        from datetime import timedelta
        return self.base_time + timedelta(seconds=self.elapsed_seconds)

    def advance(self, seconds: float):
        """Advance virtual clock by N seconds"""
        self.elapsed_seconds += seconds

    def sleep(self, seconds: float):
        """Virtual sleep (advances clock without blocking)"""
        self.advance(seconds)

# Usage in L2 execution
class L2ExecutionSandbox:
    def __init__(self, trace_id: str, base_timestamp: str):
        self.trace_id = trace_id
        self.virtual_clock = VirtualizedClock(base_timestamp)

    def execute_with_virtual_time(self, code: str):
        """Execute code with virtualized clock"""

        # Inject virtual clock into execution context
        exec_globals = {
            'datetime': type('datetime', (), {
                'now': lambda: self.virtual_clock.now(),
            }),
            'time': type('time', (), {
                'time': lambda: self.virtual_clock.now().timestamp(),
                'sleep': self.virtual_clock.sleep,
            }),
        }

        exec(code, exec_globals)
```

### Invariant
**No system time calls allowed. All time operations must use virtual clock.**

---

## Float Normalization Before Hashing

```python
class FloatNormalizer:
    """Normalize floats for deterministic hashing"""

    @staticmethod
    def normalize_float(value: float, precision: int = 6) -> float:
        """
        Normalize float to fixed precision.

        REQUIREMENTS:
        - Round to fixed decimal places
        - Handle special values (inf, -inf, nan)
        - Consistent across platforms
        """
        import math

        # Handle special values
        if math.isnan(value):
            return 0.0  # Normalize NaN to 0
        elif math.isinf(value):
            return 1e308 if value > 0 else -1e308  # Normalize inf

        # Round to fixed precision
        return round(value, precision)

    @staticmethod
    def normalize_dict(data: dict, precision: int = 6) -> dict:
        """Recursively normalize all floats in dict"""

        normalized = {}
        for key, value in data.items():
            if isinstance(value, float):
                normalized[key] = FloatNormalizer.normalize_float(value, precision)
            elif isinstance(value, dict):
                normalized[key] = FloatNormalizer.normalize_dict(value, precision)
            elif isinstance(value, list):
                normalized[key] = FloatNormalizer.normalize_list(value, precision)
            else:
                normalized[key] = value

        return normalized

    @staticmethod
    def normalize_list(data: list, precision: int = 6) -> list:
        """Recursively normalize all floats in list"""

        normalized = []
        for item in data:
            if isinstance(item, float):
                normalized.append(FloatNormalizer.normalize_float(item, precision))
            elif isinstance(item, dict):
                normalized.append(FloatNormalizer.normalize_dict(item, precision))
            elif isinstance(item, list):
                normalized.append(FloatNormalizer.normalize_list(item, precision))
            else:
                normalized.append(item)

        return normalized

# Usage before HMAC generation
class HMACGenerator:
    def generate_hmac(self, data: dict) -> str:
        """Generate HMAC with float normalization"""
        import hmac
        import hashlib
        import json

        # Normalize floats
        normalized_data = FloatNormalizer.normalize_dict(data)

        # Canonical JSON serialization
        canonical_json = json.dumps(normalized_data, sort_keys=True)

        # Generate HMAC
        return hmac.new(
            key=self.secret.encode(),
            msg=canonical_json.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
```

### Invariant
**All floats must be normalized to 6 decimal places before hashing.**

---

## Sorted JSON Canonicalization

```python
class JSONCanonicalizer:
    """Canonical JSON serialization for deterministic hashing"""

    @staticmethod
    def canonicalize(data: Any) -> str:
        """
        Serialize data to canonical JSON.

        REQUIREMENTS:
        - Keys sorted alphabetically
        - No whitespace
        - Consistent number formatting
        - UTF-8 encoding
        """
        import json

        # Normalize floats first
        normalized = FloatNormalizer.normalize_dict(data) if isinstance(data, dict) else data

        # Canonical serialization
        return json.dumps(
            normalized,
            sort_keys=True,      # Sort keys alphabetically
            separators=(',', ':'),  # No whitespace
            ensure_ascii=False   # UTF-8 encoding
        )

    @staticmethod
    def hash_canonical(data: Any) -> str:
        """Hash data using canonical serialization"""
        import hashlib

        canonical_json = JSONCanonicalizer.canonicalize(data)
        return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()

# Usage in all HMAC operations
class L2ExecutionSandbox:
    def seal_execution_result(self, result: dict) -> str:
        """Seal execution result with canonical HMAC"""
        import hmac
        import hashlib

        # Canonical serialization
        canonical_json = JSONCanonicalizer.canonicalize(result)

        # Generate HMAC
        return hmac.new(
            key=self.seal_secret.encode(),
            msg=canonical_json.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
```

### Invariant
**All JSON serialization must use sorted keys and no whitespace.**

---

## Replay Mode Enforcement

```python
class ReplayValidator:
    """Validate replay integrity"""

    def __init__(self, original_trace: ExecutionTrace):
        self.original_trace = original_trace
        self.replay_events = []

    def record_event(self, event: dict):
        """Record event during replay"""
        self.replay_events.append(event)

    def validate_replay(self) -> bool:
        """
        Validate replay matches original execution.

        REQUIREMENTS:
        - Same number of events
        - Same event types in same order
        - Same event payloads (after normalization)
        - No untranscripted randomness
        - No time-dependent external calls
        - No non-deterministic ordering
        """

        # Check event count
        if len(self.replay_events) != len(self.original_trace.events):
            return False

        # Check each event
        for i, (replay_event, original_event) in enumerate(
            zip(self.replay_events, self.original_trace.events)
        ):
            # Check event type
            if replay_event['type'] != original_event['type']:
                return False

            # Normalize payloads
            replay_payload = FloatNormalizer.normalize_dict(replay_event['payload'])
            original_payload = FloatNormalizer.normalize_dict(original_event['payload'])

            # Check payload equality
            if replay_payload != original_payload:
                return False

        return True

    def reject_untranscripted_randomness(self, operation: str):
        """Reject operations that introduce randomness"""

        forbidden_operations = [
            'random.random',
            'random.randint',
            'random.choice',
            'random.shuffle',
            'uuid.uuid4',
            'os.urandom',
            'secrets.token_bytes',
        ]

        if operation in forbidden_operations:
            raise RuntimeError(
                f"Untranscripted randomness detected: {operation}. "
                "Use DeterministicRandomSource instead."
            )

    def reject_time_dependent_calls(self, operation: str):
        """Reject time-dependent external calls"""

        forbidden_operations = [
            'datetime.now',
            'datetime.utcnow',
            'time.time',
            'time.monotonic',
        ]

        if operation in forbidden_operations:
            raise RuntimeError(
                f"Time-dependent call detected: {operation}. "
                "Use VirtualizedClock instead."
            )

    def reject_non_deterministic_ordering(self, operation: str):
        """Reject non-deterministic ordering operations"""

        forbidden_operations = [
            'set',  # Set iteration order is non-deterministic
            'dict',  # Dict iteration order (Python <3.7)
            'hash',  # Hash values are randomized
        ]

        if operation in forbidden_operations:
            raise RuntimeError(
                f"Non-deterministic ordering detected: {operation}. "
                "Use sorted() or OrderedDict instead."
            )
```

### Invariants
1. **Replay must produce identical event sequence**
2. **No untranscripted randomness allowed**
3. **No time-dependent external calls allowed**
4. **No non-deterministic ordering allowed**

---

## Determinism Checklist

Before execution, verify:
- [ ] Random seed injected from trace_id
- [ ] Virtual clock initialized from base_timestamp
- [ ] Float normalization enabled
- [ ] JSON canonicalization enabled
- [ ] Replay validator active
- [ ] Forbidden operations blocked

During execution, reject:
- [ ] System random calls
- [ ] System time calls
- [ ] External network calls (unless transcripted)
- [ ] File I/O (unless transcripted)
- [ ] Non-deterministic data structures

After execution, validate:
- [ ] All events match original trace
- [ ] All HMACs match
- [ ] No untranscripted operations
- [ ] Replay produces identical output

---

## Execution Sandbox Configuration

```python
class DeterministicExecutionSandbox:
    """L2 execution sandbox with full determinism enforcement"""

    def __init__(self, sealed_dispatch: SealedDispatch):
        self.trace_id = sealed_dispatch.trace_id
        self.base_timestamp = sealed_dispatch.timestamp

        # Initialize deterministic components
        self.random_source = DeterministicRandomSource(self.trace_id)
        self.virtual_clock = VirtualizedClock(self.base_timestamp)
        self.replay_validator = ReplayValidator(sealed_dispatch.original_trace)

        # Forbidden operations
        self.forbidden_modules = {
            'random': 'Use DeterministicRandomSource',
            'time': 'Use VirtualizedClock',
            'datetime': 'Use VirtualizedClock',
            'uuid': 'Use deterministic ID generation',
            'secrets': 'Use DeterministicRandomSource',
            'os.urandom': 'Use DeterministicRandomSource',
        }

    def execute(self, instruction_packet: InstructionPacket) -> ExecutionResult:
        """
        Execute instruction packet with determinism enforcement.

        REQUIREMENTS:
        - All randomness from deterministic source
        - All time from virtual clock
        - All floats normalized before hashing
        - All JSON canonicalized
        - All operations transcripted
        """

        # Build execution context
        exec_context = self._build_deterministic_context()

        # Execute with monitoring
        result = self._execute_with_monitoring(instruction_packet, exec_context)

        # Validate determinism
        if not self.replay_validator.validate_replay():
            raise RuntimeError("Replay validation failed - execution not deterministic")

        return result

    def _build_deterministic_context(self) -> dict:
        """Build execution context with deterministic replacements"""

        return {
            # Deterministic random
            'random': self.random_source.random,
            'randint': self.random_source.randint,
            'choice': self.random_source.choice,
            'shuffle': self.random_source.shuffle,

            # Virtual clock
            'datetime': type('datetime', (), {
                'now': lambda: self.virtual_clock.now(),
            }),
            'time': type('time', (), {
                'time': lambda: self.virtual_clock.now().timestamp(),
                'sleep': self.virtual_clock.sleep,
            }),

            # Deterministic ID generation
            'uuid4': lambda: self._deterministic_uuid(),

            # Float normalization
            'normalize_float': FloatNormalizer.normalize_float,

            # JSON canonicalization
            'json_dumps': JSONCanonicalizer.canonicalize,
        }

    def _deterministic_uuid(self) -> str:
        """Generate deterministic UUID from trace_id and counter"""
        import hashlib

        # Increment counter
        if not hasattr(self, '_uuid_counter'):
            self._uuid_counter = 0
        self._uuid_counter += 1

        # Generate deterministic UUID
        uuid_input = f"{self.trace_id}:{self._uuid_counter}"
        uuid_hash = hashlib.sha256(uuid_input.encode()).hexdigest()

        # Format as UUID
        return f"{uuid_hash[:8]}-{uuid_hash[8:12]}-{uuid_hash[12:16]}-{uuid_hash[16:20]}-{uuid_hash[20:32]}"

    def _execute_with_monitoring(self, instruction_packet: InstructionPacket,
                                 exec_context: dict) -> ExecutionResult:
        """Execute with operation monitoring"""

        # Monitor for forbidden operations
        import sys

        class ForbiddenOperationMonitor:
            def __init__(self, validator):
                self.validator = validator

            def __call__(self, frame, event, arg):
                if event == 'call':
                    # Check for forbidden operations
                    func_name = frame.f_code.co_name

                    if func_name in ['random', 'randint', 'choice']:
                        self.validator.reject_untranscripted_randomness(func_name)

                    if func_name in ['now', 'time', 'sleep']:
                        self.validator.reject_time_dependent_calls(func_name)

                return None

        # Set trace function
        monitor = ForbiddenOperationMonitor(self.replay_validator)
        sys.settrace(monitor)

        try:
            # Execute instruction packet
            result = self._execute_instruction(instruction_packet, exec_context)
        finally:
            # Remove trace function
            sys.settrace(None)

        return result
```

---

## Transcription Protocol

All non-deterministic operations must be transcripted:

```python
class OperationTranscript:
    """Transcript non-deterministic operations for replay"""

    def __init__(self):
        self.operations = []

    def record_operation(self, operation_type: str, inputs: dict,
                        outputs: dict):
        """Record operation for replay"""

        self.operations.append({
            'type': operation_type,
            'inputs': FloatNormalizer.normalize_dict(inputs),
            'outputs': FloatNormalizer.normalize_dict(outputs),
            'timestamp': self.virtual_clock.now().isoformat()
        })

    def replay_operation(self, operation_type: str, inputs: dict) -> dict:
        """Replay transcripted operation"""

        # Find matching operation in transcript
        for op in self.operations:
            if op['type'] == operation_type:
                # Normalize inputs for comparison
                normalized_inputs = FloatNormalizer.normalize_dict(inputs)

                if op['inputs'] == normalized_inputs:
                    return op['outputs']

        raise RuntimeError(
            f"No transcript found for operation: {operation_type} with inputs: {inputs}"
        )

# Usage for external calls
class L2ExecutionSandbox:
    def call_external_api(self, api_name: str, params: dict) -> dict:
        """Call external API with transcription"""

        if self.replay_mode:
            # Replay from transcript
            return self.transcript.replay_operation('external_api', {
                'api_name': api_name,
                'params': params
            })
        else:
            # Execute and record
            result = self._actual_api_call(api_name, params)

            self.transcript.record_operation('external_api', {
                'api_name': api_name,
                'params': params
            }, result)

            return result
```

---

## Failure Modes

| Violation | Action | Recovery |
|-----------|--------|----------|
| Untranscripted randomness | Abort execution | Add deterministic source |
| Time-dependent call | Abort execution | Use virtual clock |
| Non-deterministic ordering | Abort execution | Use sorted structures |
| Replay mismatch | Abort replay | Investigate divergence |
| Float precision loss | Normalize and continue | Log precision warning |

---

## Monitoring Requirements

All determinism violations must emit:
- Violation type
- Operation attempted
- Stack trace
- Trace ID
- Timestamp
- Suggested fix

All replay operations must emit:
- Event count
- Match status
- Divergence point (if any)
- Original vs replay diff

---

## Invariant Enforcement

All L2 execution must satisfy:
1. **Deterministic random source only**
2. **Virtual clock only**
3. **Float normalization before hashing**
4. **JSON canonicalization everywhere**
5. **No untranscripted operations**
6. **Replay produces identical output**

**Violation of any invariant = immediate execution abort.**
