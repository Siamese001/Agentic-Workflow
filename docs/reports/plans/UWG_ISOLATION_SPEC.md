# UWG Isolation Enforcement Specification

## SCOPE
Governs: **UWG (Universal Write Gateway)** (Independent Daemon, Mutation Control, Trace Validation)

Defines UWG isolation as independent host-level daemon with strict mutation controls.

---

Universal Write Gateway isolation as independent host-level daemon with strict mutation controls.

---

## UWG Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    HOST SYSTEM                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ UWG Daemon (Independent Process)                     │  │
│  │ • Port: 9000                                          │  │
│  │ • PID file: /var/run/uwg.pid                         │  │
│  │ • Config: /etc/uwg/config.json                       │  │
│  │ • Version: Independent from L2                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↑                                  │
│                          │ IPC (Unix socket)                │
│                          ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ L2 Execution Sandbox                                 │  │
│  │ • Cannot bypass UWG                                   │  │
│  │ • Must provide signed ExecutionTrace                 │  │
│  │ • Cannot mutate without UWG approval                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘

INVARIANT: No mutation without signed ExecutionTrace
```

---

## Independent Daemon Requirements

```python
class UWGDaemon:
    """UWG as independent host-level daemon"""

    def __init__(self, config_path: str = "/etc/uwg/config.json"):
        """
        Initialize UWG daemon.

        REQUIREMENTS:
        - Runs as independent process
        - Independent versioning from L2
        - Listens on Unix socket
        - Maintains own PID file
        - Logs to separate file
        """

        self.config = self._load_config(config_path)
        self.version = self._get_daemon_version()
        self.pid_file = "/var/run/uwg.pid"
        self.socket_path = "/var/run/uwg.sock"

        # Verify not already running
        if self._is_running():
            raise RuntimeError("UWG daemon already running")

        # Create PID file
        self._create_pid_file()

        # Initialize components
        self.policy_store = PolicyStore(self.config['policy_path'])
        self.trace_validator = TraceValidator()
        self.mutation_log = MutationLog(self.config['log_path'])

        # Start listening
        self._start_socket_server()

    def _get_daemon_version(self) -> str:
        """Get UWG daemon version (independent from L2)"""
        return "2.1.0"  # UWG version, not L2 version

    def _is_running(self) -> bool:
        """Check if UWG daemon is already running"""
        import os

        if not os.path.exists(self.pid_file):
            return False

        # Read PID
        with open(self.pid_file, 'r') as f:
            pid = int(f.read().strip())

        # Check if process exists
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            # Stale PID file
            os.remove(self.pid_file)
            return False

    def _create_pid_file(self):
        """Create PID file"""
        import os

        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))

    def _start_socket_server(self):
        """Start Unix socket server for IPC"""
        import socket
        import os

        # Remove stale socket
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)

        # Create socket
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.bind(self.socket_path)
        self.socket.listen(5)

        print(f"UWG daemon listening on {self.socket_path}")
```

---

## Independent Versioning

```python
@dataclass
class UWGVersion:
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def is_compatible_with(self, client_version: str) -> bool:
        """Check if client version is compatible"""

        client_parts = client_version.split('.')
        client_major = int(client_parts[0])

        # Major version must match
        if client_major != self.major:
            return False

        return True

class UWGVersionManager:
    """Manage UWG versioning independent from L2"""

    CURRENT_VERSION = UWGVersion(major=2, minor=1, patch=0)

    @staticmethod
    def validate_client_version(client_version: str) -> bool:
        """Validate client version compatibility"""

        return UWGVersionManager.CURRENT_VERSION.is_compatible_with(client_version)

    @staticmethod
    def get_version_string() -> str:
        """Get current UWG version"""
        return str(UWGVersionManager.CURRENT_VERSION)
```

---

## Stale Policy Hash Rejection

```python
class PolicyHashValidator:
    """Validate policy hash freshness"""

    def __init__(self, policy_store: PolicyStore):
        self.policy_store = policy_store

    def validate_policy_hash(self, provided_hash: str) -> Tuple[bool, str]:
        """
        Validate policy hash is current.

        REQUIREMENTS:
        - Hash must match current epoch
        - Stale hashes rejected
        - Rejection logged
        """

        current_hash = self.policy_store.get_current_epoch_hash()

        if provided_hash != current_hash:
            return False, f"Stale policy hash: provided={provided_hash}, current={current_hash}"

        return True, "OK"

    def reject_stale_hash(self, provided_hash: str, trace_id: str):
        """Reject mutation with stale policy hash"""

        self.mutation_log.log_rejection({
            'trace_id': trace_id,
            'reason': 'STALE_POLICY_HASH',
            'provided_hash': provided_hash,
            'current_hash': self.policy_store.get_current_epoch_hash(),
            'timestamp': datetime.now().isoformat()
        })

        raise PolicyHashMismatchError(
            f"Stale policy hash rejected: {provided_hash}"
        )
```

---

## Monotonic Trace ID Chaining

```python
class TraceIDChainValidator:
    """Validate trace ID monotonic chaining"""

    def __init__(self):
        self.last_trace_id = None
        self.trace_chain = []

    def validate_trace_id(self, trace_id: str) -> Tuple[bool, str]:
        """
        Validate trace ID is monotonically increasing.

        REQUIREMENTS:
        - Trace IDs must be monotonic
        - No gaps allowed
        - No duplicates allowed
        - Chain must be continuous
        """

        # First trace ID
        if self.last_trace_id is None:
            self.last_trace_id = trace_id
            self.trace_chain.append(trace_id)
            return True, "OK"

        # Check monotonic increase
        if trace_id <= self.last_trace_id:
            return False, f"Non-monotonic trace ID: {trace_id} <= {self.last_trace_id}"

        # Update chain
        self.last_trace_id = trace_id
        self.trace_chain.append(trace_id)

        return True, "OK"

    def detect_replay_attack(self, trace_id: str) -> bool:
        """Detect potential replay attack"""

        # Check if trace ID already seen
        if trace_id in self.trace_chain[:-1]:  # Exclude current
            return True

        return False

    def get_chain_integrity(self) -> Dict[str, Any]:
        """Get trace chain integrity status"""

        return {
            'chain_length': len(self.trace_chain),
            'last_trace_id': self.last_trace_id,
            'gaps_detected': self._detect_gaps(),
            'duplicates_detected': self._detect_duplicates()
        }

    def _detect_gaps(self) -> List[Tuple[str, str]]:
        """Detect gaps in trace chain"""

        gaps = []

        for i in range(1, len(self.trace_chain)):
            prev_id = self.trace_chain[i-1]
            curr_id = self.trace_chain[i]

            # Check for expected increment
            # (Implementation depends on trace ID format)

        return gaps

    def _detect_duplicates(self) -> List[str]:
        """Detect duplicate trace IDs"""

        seen = set()
        duplicates = []

        for trace_id in self.trace_chain:
            if trace_id in seen:
                duplicates.append(trace_id)
            seen.add(trace_id)

        return duplicates
```

---

## Replay Mode Bypass Prevention

```python
class ReplayModeGuard:
    """Prevent UWG bypass in replay mode"""

    def __init__(self):
        self.replay_mode_active = False

    def enter_replay_mode(self, original_trace: ExecutionTrace):
        """Enter replay mode with original trace"""

        self.replay_mode_active = True
        self.original_trace = original_trace

    def validate_mutation_in_replay(self, mutation_request: MutationRequest) -> bool:
        """
        Validate mutation is allowed in replay mode.

        REQUIREMENTS:
        - Mutation must match original trace
        - No new mutations allowed
        - UWG cannot be bypassed
        """

        if not self.replay_mode_active:
            return True  # Not in replay mode

        # Find matching mutation in original trace
        matching_mutation = self._find_matching_mutation(mutation_request)

        if not matching_mutation:
            raise ReplayModeViolationError(
                f"Mutation not in original trace: {mutation_request}"
            )

        # Validate mutation matches exactly
        if not self._mutations_match(mutation_request, matching_mutation):
            raise ReplayModeViolationError(
                f"Mutation differs from original: {mutation_request}"
            )

        return True

    def _find_matching_mutation(self, mutation_request: MutationRequest):
        """Find matching mutation in original trace"""

        for mutation in self.original_trace.mutations:
            if mutation.trace_id == mutation_request.trace_id:
                return mutation

        return None

    def _mutations_match(self, request: MutationRequest,
                        original: Mutation) -> bool:
        """Check if mutations match exactly"""

        # Compare file paths
        if request.file_path != original.file_path:
            return False

        # Compare content hashes
        if request.content_hash != original.content_hash:
            return False

        # Compare operation types
        if request.operation != original.operation:
            return False

        return True
```

---

## Signed ExecutionTrace Requirement

```python
class ExecutionTraceValidator:
    """Validate signed execution traces"""

    def __init__(self, public_key: str):
        self.public_key = public_key

    def validate_trace_signature(self, trace: ExecutionTrace) -> bool:
        """
        Validate execution trace signature.

        REQUIREMENTS:
        - Trace must be signed by L0c
        - Signature must be valid
        - Trace must not be tampered
        """

        # Verify signature
        if not self._verify_signature(trace):
            return False

        # Verify trace integrity
        if not self._verify_trace_integrity(trace):
            return False

        return True

    def _verify_signature(self, trace: ExecutionTrace) -> bool:
        """Verify trace signature using public key"""

        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives.serialization import load_pem_public_key

        # Load public key
        public_key = load_pem_public_key(self.public_key.encode())

        # Verify signature
        try:
            public_key.verify(
                trace.signature.encode(),
                trace.payload.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

    def _verify_trace_integrity(self, trace: ExecutionTrace) -> bool:
        """Verify trace has not been tampered"""

        import hashlib

        # Recalculate trace hash
        calculated_hash = hashlib.sha256(trace.payload.encode()).hexdigest()

        # Compare with stored hash
        return calculated_hash == trace.payload_hash

class UWGMutationGate:
    """Gate all mutations through UWG with trace validation"""

    def __init__(self, trace_validator: ExecutionTraceValidator):
        self.trace_validator = trace_validator

    def authorize_mutation(self, mutation_request: MutationRequest,
                          execution_trace: ExecutionTrace) -> bool:
        """
        Authorize mutation with signed execution trace.

        REQUIREMENTS:
        - Execution trace must be provided
        - Trace must be signed and valid
        - Mutation must be in trace
        - No mutation without trace
        """

        # Validate trace signature
        if not self.trace_validator.validate_trace_signature(execution_trace):
            raise InvalidTraceSignatureError("Execution trace signature invalid")

        # Validate mutation is in trace
        if not self._mutation_in_trace(mutation_request, execution_trace):
            raise UnauthorizedMutationError(
                f"Mutation not authorized in trace: {mutation_request}"
            )

        return True

    def _mutation_in_trace(self, mutation_request: MutationRequest,
                          execution_trace: ExecutionTrace) -> bool:
        """Check if mutation is authorized in trace"""

        for mutation in execution_trace.mutations:
            if (mutation.file_path == mutation_request.file_path and
                mutation.operation == mutation_request.operation):
                return True

        return False
```

---

## IPC Protocol

```python
@dataclass
class UWGRequest:
    version: str
    trace_id: str
    policy_hash: str
    execution_trace: ExecutionTrace
    mutation_request: MutationRequest
    timestamp: str

@dataclass
class UWGResponse:
    success: bool
    error: Optional[str]
    mutation_id: Optional[str]
    timestamp: str

class UWGIPCHandler:
    """Handle IPC requests from L2"""

    def handle_request(self, request_data: bytes) -> bytes:
        """
        Handle mutation request from L2.

        PROTOCOL:
        1. Deserialize request
        2. Validate version compatibility
        3. Validate policy hash
        4. Validate trace ID chain
        5. Validate execution trace signature
        6. Authorize mutation
        7. Execute mutation
        8. Return response
        """

        # Deserialize request
        request = self._deserialize_request(request_data)

        # Validate version
        if not UWGVersionManager.validate_client_version(request.version):
            return self._error_response("Version incompatible")

        # Validate policy hash
        valid, error = self.policy_validator.validate_policy_hash(request.policy_hash)
        if not valid:
            return self._error_response(error)

        # Validate trace ID
        valid, error = self.trace_chain_validator.validate_trace_id(request.trace_id)
        if not valid:
            return self._error_response(error)

        # Validate execution trace
        if not self.trace_validator.validate_trace_signature(request.execution_trace):
            return self._error_response("Invalid execution trace signature")

        # Authorize mutation
        try:
            self.mutation_gate.authorize_mutation(
                request.mutation_request,
                request.execution_trace
            )
        except Exception as e:
            return self._error_response(str(e))

        # Execute mutation
        mutation_id = self._execute_mutation(request.mutation_request)

        # Return success response
        return self._success_response(mutation_id)

    def _deserialize_request(self, data: bytes) -> UWGRequest:
        """Deserialize request from bytes"""
        import json

        request_dict = json.loads(data.decode('utf-8'))
        return UWGRequest(**request_dict)

    def _error_response(self, error: str) -> bytes:
        """Create error response"""
        import json

        response = UWGResponse(
            success=False,
            error=error,
            mutation_id=None,
            timestamp=datetime.now().isoformat()
        )

        return json.dumps(response.__dict__).encode('utf-8')

    def _success_response(self, mutation_id: str) -> bytes:
        """Create success response"""
        import json

        response = UWGResponse(
            success=True,
            error=None,
            mutation_id=mutation_id,
            timestamp=datetime.now().isoformat()
        )

        return json.dumps(response.__dict__).encode('utf-8')
```

---

## Invariants

1. **No mutation without signed ExecutionTrace**
2. **UWG runs as independent daemon**
3. **Independent versioning from L2**
4. **Stale policy hash rejected**
5. **Trace IDs must be monotonic**
6. **UWG cannot be bypassed in replay mode**
7. **All mutations logged**

---

## Deployment Configuration

```bash
# UWG daemon systemd service
[Unit]
Description=Universal Write Gateway Daemon
After=network.target

[Service]
Type=forking
PIDFile=/var/run/uwg.pid
ExecStart=/usr/local/bin/uwg-daemon start
ExecStop=/usr/local/bin/uwg-daemon stop
ExecReload=/usr/local/bin/uwg-daemon reload
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

---

## Monitoring Requirements

UWG daemon must emit:
- Daemon version
- Uptime
- Request count
- Mutation count
- Rejection count
- Policy hash changes
- Trace ID chain integrity
- Replay mode status

All mutations must be logged:
- Trace ID
- Policy hash
- File path
- Operation type
- Timestamp
- Success/failure
- Rejection reason (if rejected)

---

## Failure Modes

| Failure | Action | Recovery |
|---------|--------|----------|
| Daemon crash | Auto-restart via systemd | Restore from checkpoint |
| Stale policy hash | Reject mutation | Client updates policy |
| Invalid trace signature | Reject mutation | Client re-signs trace |
| Trace ID collision | Reject mutation | Investigate replay attack |
| IPC socket failure | Restart daemon | Reconnect clients |
