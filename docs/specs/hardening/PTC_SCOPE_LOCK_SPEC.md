# PTC Scope Lock Specification

## SCOPE
Governs: **L2 Execution Layer** (Prompt-Tool Contract, Tool Invocation Control)

Defines static tool contract enforcement with no dynamic registration or side-channel invocations.

---

Static tool contract enforcement with no dynamic registration or side-channel invocations.

---

## PTC (Prompt-Tool Contract) Scope Lock

```python
@dataclass
class ToolContract:
    tool_name: str
    allowed_operations: List[str]
    parameter_schema: Dict[str, Any]
    max_invocations: int
    session_locked: bool = True

class PTCScopeLock:
    """Enforce static tool contracts for session"""

    def __init__(self, instruction_packet: InstructionPacket):
        """
        Initialize PTC scope lock from instruction packet.

        REQUIREMENTS:
        - Tool allowlist from InstructionPacket
        - No dynamic tool registration
        - No tool invocation outside allowlist
        - No streaming side-channel calls
        - Tool contracts static for session
        """

        self.allowed_tools = self._extract_tool_allowlist(instruction_packet)
        self.tool_contracts = self._build_tool_contracts(instruction_packet)
        self.invocation_counts = {tool: 0 for tool in self.allowed_tools}
        self.session_locked = True

    def _extract_tool_allowlist(self, instruction_packet: InstructionPacket) -> Set[str]:
        """Extract tool allowlist from instruction packet"""

        if 'tool_allowlist' not in instruction_packet.constraints:
            raise ValueError("InstructionPacket missing tool_allowlist")

        return set(instruction_packet.constraints['tool_allowlist'])

    def _build_tool_contracts(self, instruction_packet: InstructionPacket) -> Dict[str, ToolContract]:
        """Build tool contracts from instruction packet"""

        contracts = {}

        for tool_spec in instruction_packet.constraints.get('tool_contracts', []):
            contract = ToolContract(
                tool_name=tool_spec['name'],
                allowed_operations=tool_spec['operations'],
                parameter_schema=tool_spec['schema'],
                max_invocations=tool_spec.get('max_invocations', 1000),
                session_locked=True
            )
            contracts[tool_spec['name']] = contract

        return contracts

    def validate_tool_invocation(self, tool_name: str,
                                 operation: str,
                                 parameters: Dict[str, Any]) -> bool:
        """
        Validate tool invocation against contract.

        REQUIREMENTS:
        - Tool must be in allowlist
        - Operation must be allowed
        - Parameters must match schema
        - Invocation count must not exceed max
        """

        # Check allowlist
        if tool_name not in self.allowed_tools:
            raise ToolNotAllowedError(
                f"Tool {tool_name} not in allowlist: {self.allowed_tools}"
            )

        # Check contract exists
        if tool_name not in self.tool_contracts:
            raise ToolContractMissingError(
                f"No contract for tool: {tool_name}"
            )

        contract = self.tool_contracts[tool_name]

        # Check operation allowed
        if operation not in contract.allowed_operations:
            raise OperationNotAllowedError(
                f"Operation {operation} not allowed for tool {tool_name}. "
                f"Allowed: {contract.allowed_operations}"
            )

        # Validate parameters
        if not self._validate_parameters(parameters, contract.parameter_schema):
            raise InvalidParametersError(
                f"Parameters do not match schema for {tool_name}"
            )

        # Check invocation count
        if self.invocation_counts[tool_name] >= contract.max_invocations:
            raise MaxInvocationsExceededError(
                f"Max invocations exceeded for {tool_name}: "
                f"{contract.max_invocations}"
            )

        return True

    def record_invocation(self, tool_name: str):
        """Record tool invocation"""
        self.invocation_counts[tool_name] += 1

    def _validate_parameters(self, parameters: Dict[str, Any],
                            schema: Dict[str, Any]) -> bool:
        """Validate parameters against schema"""

        # Check required parameters
        for param_name, param_spec in schema.items():
            if param_spec.get('required', False):
                if param_name not in parameters:
                    return False

            # Check type
            if param_name in parameters:
                expected_type = param_spec.get('type')
                actual_value = parameters[param_name]

                if not self._check_type(actual_value, expected_type):
                    return False

        return True

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check value matches expected type"""

        type_map = {
            'string': str,
            'integer': int,
            'float': float,
            'boolean': bool,
            'array': list,
            'object': dict
        }

        if expected_type not in type_map:
            return True  # Unknown type, allow

        return isinstance(value, type_map[expected_type])

    def prevent_dynamic_registration(self, tool_name: str):
        """Prevent dynamic tool registration mid-run"""

        if self.session_locked:
            raise DynamicRegistrationError(
                f"Cannot register tool {tool_name} - session locked"
            )

    def prevent_streaming_side_channel(self, tool_name: str):
        """Prevent streaming side-channel tool calls"""

        # Check if tool supports streaming
        if tool_name in self.tool_contracts:
            contract = self.tool_contracts[tool_name]

            if 'streaming' in contract.allowed_operations:
                raise StreamingSideChannelError(
                    f"Streaming side-channel detected for {tool_name}"
                )
```

---

## No Dynamic Tool Registration

```python
class ToolRegistry:
    """Static tool registry - no dynamic registration"""

    def __init__(self, static_tools: Dict[str, ToolContract]):
        """
        Initialize with static tool set.

        REQUIREMENTS:
        - Tools defined at session start
        - No runtime registration
        - No tool modification
        - Registry immutable
        """

        self.tools = static_tools
        self._locked = True

    def register_tool(self, tool_name: str, contract: ToolContract):
        """Attempt to register tool (should fail if locked)"""

        if self._locked:
            raise RuntimeError(
                f"Tool registry locked - cannot register {tool_name}"
            )

        self.tools[tool_name] = contract

    def get_tool(self, tool_name: str) -> ToolContract:
        """Get tool contract"""

        if tool_name not in self.tools:
            raise ToolNotFoundError(f"Tool not found: {tool_name}")

        return self.tools[tool_name]

    def list_tools(self) -> List[str]:
        """List available tools"""
        return list(self.tools.keys())

    def is_locked(self) -> bool:
        """Check if registry is locked"""
        return self._locked

# Usage in L2 execution
class L2ExecutionSandbox:
    def __init__(self, instruction_packet: InstructionPacket):
        # Build static tool registry from instruction packet
        static_tools = self._build_static_tools(instruction_packet)
        self.tool_registry = ToolRegistry(static_tools)

        # Initialize PTC scope lock
        self.ptc_lock = PTCScopeLock(instruction_packet)

    def invoke_tool(self, tool_name: str, operation: str,
                   parameters: Dict[str, Any]):
        """Invoke tool with PTC validation"""

        # Validate against PTC scope lock
        self.ptc_lock.validate_tool_invocation(tool_name, operation, parameters)

        # Get tool from registry
        tool = self.tool_registry.get_tool(tool_name)

        # Execute tool
        result = self._execute_tool(tool, operation, parameters)

        # Record invocation
        self.ptc_lock.record_invocation(tool_name)

        return result
```

---

## No Tool Invocation Outside Allowlist

```python
class ToolInvocationGuard:
    """Guard against tool invocations outside allowlist"""

    def __init__(self, allowlist: Set[str]):
        self.allowlist = allowlist
        self.violations = []

    def check_invocation(self, tool_name: str) -> bool:
        """Check if tool invocation is allowed"""

        if tool_name not in self.allowlist:
            self._record_violation(tool_name)
            return False

        return True

    def _record_violation(self, tool_name: str):
        """Record allowlist violation"""

        violation = {
            'tool_name': tool_name,
            'timestamp': datetime.now().isoformat(),
            'allowlist': list(self.allowlist)
        }

        self.violations.append(violation)

        # Emit security event
        self._emit_security_event(violation)

    def _emit_security_event(self, violation: Dict[str, Any]):
        """Emit security event for violation"""

        print(f"SECURITY: Tool invocation outside allowlist: {violation}")

    def get_violations(self) -> List[Dict[str, Any]]:
        """Get all recorded violations"""
        return self.violations

    def abort_on_violation(self, tool_name: str):
        """Abort execution on allowlist violation"""

        raise ToolAllowlistViolationError(
            f"Tool {tool_name} not in allowlist. "
            f"Allowed tools: {self.allowlist}"
        )
```

---

## No Streaming Side-Channel Calls

```python
class StreamingSideChannelDetector:
    """Detect and prevent streaming side-channel tool calls"""

    def __init__(self):
        self.streaming_calls = []

    def detect_streaming_call(self, tool_name: str,
                             call_context: Dict[str, Any]) -> bool:
        """
        Detect if tool call is streaming side-channel.

        INDICATORS:
        - Call outside main execution flow
        - No trace ID binding
        - Async/streaming response type
        - Bypasses PTC validation
        """

        # Check for trace ID
        if 'trace_id' not in call_context:
            return True  # Side-channel detected

        # Check for streaming response
        if call_context.get('response_type') == 'streaming':
            return True  # Streaming detected

        # Check for async call
        if call_context.get('async', False):
            return True  # Async detected

        return False

    def prevent_streaming_call(self, tool_name: str,
                               call_context: Dict[str, Any]):
        """Prevent streaming side-channel call"""

        if self.detect_streaming_call(tool_name, call_context):
            self._record_streaming_call(tool_name, call_context)

            raise StreamingSideChannelError(
                f"Streaming side-channel detected for {tool_name}"
            )

    def _record_streaming_call(self, tool_name: str,
                              call_context: Dict[str, Any]):
        """Record streaming call attempt"""

        self.streaming_calls.append({
            'tool_name': tool_name,
            'context': call_context,
            'timestamp': datetime.now().isoformat()
        })
```

---

## Static Tool Contracts

```python
class StaticToolContractBuilder:
    """Build static tool contracts at session start"""

    @staticmethod
    def build_contracts_from_instruction_packet(
        instruction_packet: InstructionPacket
    ) -> Dict[str, ToolContract]:
        """
        Build tool contracts from instruction packet.

        REQUIREMENTS:
        - All tools defined upfront
        - Contracts immutable for session
        - No runtime modifications
        """

        contracts = {}

        # Extract tool specifications
        tool_specs = instruction_packet.constraints.get('tool_contracts', [])

        for spec in tool_specs:
            contract = ToolContract(
                tool_name=spec['name'],
                allowed_operations=spec['operations'],
                parameter_schema=spec['schema'],
                max_invocations=spec.get('max_invocations', 1000),
                session_locked=True
            )

            contracts[spec['name']] = contract

        return contracts

    @staticmethod
    def validate_contract_completeness(
        contracts: Dict[str, ToolContract]
    ) -> bool:
        """Validate all contracts are complete"""

        for tool_name, contract in contracts.items():
            # Check required fields
            if not contract.tool_name:
                return False

            if not contract.allowed_operations:
                return False

            if not contract.parameter_schema:
                return False

        return True

# Example tool contracts
STANDARD_TOOL_CONTRACTS = {
    'file_read': ToolContract(
        tool_name='file_read',
        allowed_operations=['read', 'stat'],
        parameter_schema={
            'file_path': {'type': 'string', 'required': True},
            'encoding': {'type': 'string', 'required': False}
        },
        max_invocations=1000,
        session_locked=True
    ),
    'file_write': ToolContract(
        tool_name='file_write',
        allowed_operations=['write', 'append'],
        parameter_schema={
            'file_path': {'type': 'string', 'required': True},
            'content': {'type': 'string', 'required': True},
            'mode': {'type': 'string', 'required': False}
        },
        max_invocations=100,
        session_locked=True
    ),
    'git_operations': ToolContract(
        tool_name='git_operations',
        allowed_operations=['status', 'diff', 'commit'],
        parameter_schema={
            'operation': {'type': 'string', 'required': True},
            'args': {'type': 'array', 'required': False}
        },
        max_invocations=50,
        session_locked=True
    )
}
```

---

## Violation Detection and Abort

```python
class PTCViolationDetector:
    """Detect PTC violations and abort execution"""

    def __init__(self, ptc_lock: PTCScopeLock):
        self.ptc_lock = ptc_lock
        self.violations = []

    def detect_violation(self, tool_name: str, operation: str,
                        parameters: Dict[str, Any]) -> Optional[str]:
        """
        Detect PTC violation.

        VIOLATIONS:
        - Tool not in allowlist
        - Operation not allowed
        - Invalid parameters
        - Max invocations exceeded
        - Dynamic registration attempt
        - Streaming side-channel
        """

        try:
            self.ptc_lock.validate_tool_invocation(tool_name, operation, parameters)
            return None  # No violation

        except ToolNotAllowedError as e:
            return f"TOOL_NOT_ALLOWED: {str(e)}"

        except OperationNotAllowedError as e:
            return f"OPERATION_NOT_ALLOWED: {str(e)}"

        except InvalidParametersError as e:
            return f"INVALID_PARAMETERS: {str(e)}"

        except MaxInvocationsExceededError as e:
            return f"MAX_INVOCATIONS_EXCEEDED: {str(e)}"

        except DynamicRegistrationError as e:
            return f"DYNAMIC_REGISTRATION: {str(e)}"

        except StreamingSideChannelError as e:
            return f"STREAMING_SIDE_CHANNEL: {str(e)}"

    def abort_on_violation(self, violation_type: str):
        """Abort execution on PTC violation"""

        self.violations.append({
            'type': violation_type,
            'timestamp': datetime.now().isoformat()
        })

        # Emit abort event
        self._emit_abort_event(violation_type)

        # Hard abort
        raise PTCViolationAbortError(
            f"PTC violation detected: {violation_type}. Execution aborted."
        )

    def _emit_abort_event(self, violation_type: str):
        """Emit abort event for monitoring"""

        print(f"ABORT: PTC violation - {violation_type}")

# Usage in L2 execution
class L2ExecutionSandbox:
    def execute_with_ptc_enforcement(self, instruction_packet: InstructionPacket):
        """Execute with PTC enforcement"""

        # Initialize PTC components
        ptc_lock = PTCScopeLock(instruction_packet)
        violation_detector = PTCViolationDetector(ptc_lock)

        # Execute with monitoring
        try:
            result = self._execute_instruction(instruction_packet)

        except Exception as e:
            # Check if PTC violation
            if isinstance(e, (ToolNotAllowedError, OperationNotAllowedError,
                            InvalidParametersError, MaxInvocationsExceededError,
                            DynamicRegistrationError, StreamingSideChannelError)):
                violation_detector.abort_on_violation(str(e))

            raise

        return result
```

---

## Invariants

1. **No dynamic tool registration mid-run**
2. **No tool invocation outside InstructionPacket allowlist**
3. **No streaming side-channel tool calls**
4. **Tool contracts static for session**
5. **All tool invocations validated against contract**
6. **Violation → hard abort**

---

## Monitoring Requirements

All PTC operations must emit:
- Tool name
- Operation
- Parameters (sanitized)
- Validation result
- Invocation count
- Violation type (if any)
- Abort reason (if aborted)

All violations must be logged:
- Violation type
- Tool name
- Timestamp
- Stack trace
- Instruction packet ID

---

## Failure Modes

| Violation | Action | Recovery |
|-----------|--------|----------|
| Tool not in allowlist | Hard abort | Update allowlist |
| Operation not allowed | Hard abort | Update contract |
| Invalid parameters | Hard abort | Fix parameters |
| Max invocations exceeded | Hard abort | Increase limit |
| Dynamic registration | Hard abort | Remove registration |
| Streaming side-channel | Hard abort | Remove streaming |

---

## Example InstructionPacket with Tool Contracts

```json
{
  "path": "A",
  "violation": {...},
  "capabilities": ["L5_SAFETY", "L2_EXECUTION"],
  "constraints": {
    "tool_allowlist": [
      "file_read",
      "file_write",
      "git_operations"
    ],
    "tool_contracts": [
      {
        "name": "file_read",
        "operations": ["read", "stat"],
        "schema": {
          "file_path": {"type": "string", "required": true},
          "encoding": {"type": "string", "required": false}
        },
        "max_invocations": 1000
      },
      {
        "name": "file_write",
        "operations": ["write"],
        "schema": {
          "file_path": {"type": "string", "required": true},
          "content": {"type": "string", "required": true}
        },
        "max_invocations": 100
      }
    ]
  }
}
```
