# Agent Hardening Architecture

## Overview

This document describes the agentic hardening system that transforms "stupid" agents (those that hallucinate, break formats, or fail instructions) into "hard-constrained" agents that physically cannot misbehave.

Instead of relying on prompts that agents "choose" to follow, we enforce constraints at the system level.

## The Four Hardening Layers

```text
┌─────────────────────────────────────────────────────────────┐
│                    HARDENED AGENT                           │
├─────────────────────────────────────────────────────────────┤
│  1. Constrained Decoding (Grammar-Based)                    │
│     ├─ Enforces valid JSON/Schema at network layer         │
│     └─ Uses Instructor + Pydantic for structure enforcement │
├─────────────────────────────────────────────────────────────┤
│  2. DSPy Optimization (Prompt Engineering)                  │
│     ├─ Mathematically optimizes prompts offline            │
│     └─ Treats prompts as trainable weights                 │
├─────────────────────────────────────────────────────────────┤
│  3. Enhanced Sandbox (Execution Safety)                     │
│     ├─ Docker containers with security hardening           │
│     └─ Pattern detection for dangerous commands            │
├─────────────────────────────────────────────────────────────┤
│  4. Tool Verification (Pre-execution Check)                 │
│     ├─ Validates tool calls before execution               │
│     └─ Detects hallucinated tools/code                     │
└─────────────────────────────────────────────────────────────┘
```

## 1. Constrained Decoding - Fixing "Format Stupidity"

### Problem
Agents return malformed JSON that crashes parsers:
```json
{
  "action": "search",
  "query": "find data",  // Trailing comma breaks parser
}
```

### Solution

Force the LLM's token probability distribution to ONLY allow valid tokens.

```python
from agentic_core.L2_execution.structured_engine import StructuredEngine, AgentThoughtProcess

# The agent PHYSICALLY cannot output invalid structure
engine = StructuredEngine(api_key="your-key")

result = await engine.think_structured(
    system_prompt="You are a helpful assistant",
    user_prompt="What should you do next?",
    max_retries=3  # Automatically retries on validation errors
)

# result is GUARANTEED to be a valid AgentThoughtProcess
print(result.tool_choice)  # Always valid enum value
print(result.confidence_score)  # Always 0.0-1.0 float
```

### How It Works

1. **Network Layer Enforcement**: Instructor patches the OpenAI client
2. **Schema Validation**: Pydantic validates each token as it's generated
3. **Auto-retry**: Invalid tokens are automatically rejected and regenerated

### Key Benefits

- **Zero Parse Errors**: Impossible to receive malformed JSON
- **Type Safety**: All fields have correct types
- **Validation**: Built-in field validation (e.g., confidence scores in range)

## 2. DSPy Optimization - Fixing "Instruction Stupidity"

### Problem

Agents work for 3 turns, then "forget" their role and produce lazy code.

### Solution

Mathematically optimize prompts instead of hand-writing them.

```python
from agentic_core.L1_cognition.dspy_optimizer import DSPyOptimizer, OptimizationExample

# Define what "good" looks like
examples = [
    OptimizationExample(
        inputs={"requirements": "Create a fast API"},
        ideal_output={"code": "from fastapi import FastAPI\n..."},
        metadata={"score": 0.9}
    )
]

# Optimize the prompt
optimizer = DSPyOptimizer()
result = await optimizer.optimize_prompt(
    base_prompt="Generate code for: {requirements}",
    signature_class=CodeGenSignature,
    training_examples=examples,
    metric_func=code_compilation_metric
)

# result.optimized_prompt is mathematically optimal
```

### How It Works

1. **Define Metrics**: What makes a "good" response (e.g., code compiles)
2. **Generate Variants**: Create prompt variations
3. **Evaluate**: Score each variant on test cases
4. **Select Best**: Choose highest-scoring prompt formulation

### Key Benefits

- **Data-Driven**: Prompts optimized on actual performance
- **Continuous**: Can re-optimize as new data comes in
- **Measurable**: Clear metrics for prompt quality

## 3. Enhanced Sandbox - Fixing "Dangerous Stupidity"

### Problem

Agent tries to run `rm -rf /` or hallucinates dangerous commands.

### Solution

Execute ALL code in hardened Docker containers that cannot harm the host.

```python
from runtime.core.sandbox import create_sandbox

# Create hardened sandbox
sandbox = await create_sandbox(
    image="python:3.10-slim",
    network_disabled=True
)

# Enable security hardening
sandbox.security_hardening = True

# Execute dangerous code safely
code = "import os; os.system('rm -rf /')"  # Dangerous!
result = await sandbox.run_code(code, allow_dangerous=False)

# Result: Error - "Code rejected due to security violations"
# Host system: Completely safe
```

### Security Features

- **Pattern Detection**: Blocks dangerous commands before execution
- **Container Hardening**:
  - Runs as non-root user
  - Read-only filesystem
  - No network access
  - Limited CPU/memory
- **Automatic Cleanup**: Containers destroyed after use

### Key Benefits

- **Isolation**: Code cannot escape container
- **Prevention**: Dangerous patterns blocked upfront
- **Resource Limits**: Cannot exhaust host resources

## 4. Tool Verification - Fixing "Hallucination Stupidity"

### Problem

Agent invents tools that don't exist:

```python
# Agent hallucinates
result = magic_library.solve_problem()  # magic_library doesn't exist!
```

### Solution

Verify every tool call before execution.

```python
from agentic_core.L3_orchestration.tool_verification import ToolVerifier

verifier = ToolVerifier(strict_mode=True)

# Verify tool call
report = await verifier.verify_tool_call(
    tool_name="magic_library.solve",
    tool_args={"problem": "hard"},
    context={"available_tools": ["pandas", "numpy"]}
)

# Result: FAILED
# Issues: ["Hallucinated tool detected: magic_library"]
```

### Verification Checks

1. **Syntax Validation**: Code must parse correctly
2. **Import Validation**: All imports must exist
3. **Tool Existence**: Tool must be in registry
4. **Argument Validation**: Required arguments present
5. **Dry Run**: Execute in sandbox to check runtime errors

### Key Benefits

- **Prevention**: Hallucinations caught before execution
- **Feedback**: Clear error messages guide corrections
- **Learning**: Agents learn what tools are available

## Integration: HardenedAutonomousHop

All four hardening layers integrate into a single hardened agent:

```python
from runtime.core.hardened_autonomous_hop import (
    HardenedAutonomousHop,
    HardenedAutonomousHopConfig,
    HardeningConfig,
    AutonomyConfig
)

# Configure all hardening features
hardening = HardeningConfig(
    enable_constrained_decoding=True,
    enable_enhanced_sandbox=True,
    enable_tool_verification=True,
    sandbox_security_hardening=True
)

autonomy = AutonomyConfig(
    enable_episodic_memory=True,
    enable_reasoning_kernel=True
)

config = HardenedAutonomousHopConfig(
    hardening=hardening,
    autonomy=autonomy
)

# Create hardened agent
agent = HardenedAutonomousHop(
    hop_function=my_task,
    config=config
)

# Execute with full hardening
result = await agent.run(
    goal="Build a data pipeline",
    constraints=["Must be secure", "Should be efficient"]
)
```

## Execution Flow with Hardening

```
THINK Stage:
1. Recall relevant experiences (Episodic Memory)
2. Generate with constrained decoding (StructuredEngine)
3. Verify output format (Pydantic validation)

ACT Stage:
1. Discover tools dynamically (ToolRegistry)
2. Verify tool call (ToolVerifier)
3. Execute in sandbox (DockerSandbox)

CRITIQUE Stage:
1. Check quality criteria
2. Analyze failure patterns (Episodic Memory)
3. Commit to memory (Learning)
```

## Hardening vs Standard Agents

| Feature | Standard Agent | Hardened Agent |
|---------|----------------|----------------|
| **JSON Output** | "Please output JSON" (optional) | Enforced at network layer |
| **Prompt Quality** | Hand-written | Mathematically optimized |
| **Code Execution** | On localhost | In hardened container |
| **Tool Usage** | Whatever agent wants | Verified before execution |
| **Error Rate** | High (hallucinations) | Near zero (blocked) |
| **Safety** | Trust-based | Constraint-based |

## Configuration Options

### HardeningConfig

```python
@dataclass
class HardeningConfig:
    enable_constrained_decoding: bool = True
    enable_dspy_optimization: bool = False
    enable_enhanced_sandbox: bool = True
    enable_tool_verification: bool = True

    # Constrained decoding
    max_retries: int = 3

    # Sandbox settings
    sandbox_image: str = "python:3.10-slim"
    sandbox_network_disabled: bool = True
    sandbox_security_hardening: bool = True

    # Tool verification
    verification_strict_mode: bool = True
```

### Best Practices

1. **Enable All Hardening**: Use all 4 layers for maximum safety
2. **Configure Strictly**: Set strict_mode=True for production
3. **Monitor Logs**: Watch for verification failures
4. **Update Patterns**: Regularly update dangerous patterns
5. **Test Thoroughly**: Verify hardening works with test cases

## Migration Guide

### From Standard to Hardened

```python
# Before (Standard)
from runtime.core.autonomous_subatomic_hop import AutonomousSubatomicHop

agent = AutonomousSubatomicHop(
    hop_function=my_function,
    config=AutonomousHopConfig()
)

# After (Hardened)
from runtime.core.hardened_autonomous_hop import HardenedAutonomousHop

agent = HardenedAutonomousHop(
    hop_function=my_function,
    config=HardenedAutonomousHopConfig(
        hardening=HardeningConfig(
            enable_constrained_decoding=True,
            enable_enhanced_sandbox=True,
            enable_tool_verification=True
        )
    )
)
```

## Testing Hardening

### Test Constrained Decoding

```python
# Try to break the schema - should fail
bad_input = "This is not JSON"
result = await engine.think_structured(bad_input)
# Result: Automatically retries until valid
```

### Test Sandbox Security

```python
# Try dangerous code
dangerous_code = "import subprocess; subprocess.call(['rm', '-rf', '/'])"
result = await sandbox.run_code(dangerous_code)
# Result: Rejected with security violation
```

### Test Tool Verification

```python
# Try hallucinated tool
await verifier.verify_tool_call(
    tool_name="fake_tool",
    tool_args={}
)
# Result: FAILED with clear error message
```

## Monitoring and Observability

Hardening components emit telemetry for monitoring:

```python
# Constrained decoding retries
telemetry.record_event({
    "event_type": "CONSTRAINED_DECODING_RETRY",
    "payload": {"retries": 2, "validation_errors": ["missing_field"]}
})

# Security violations
telemetry.record_event({
    "event_type": "SECURITY_VIOLATION",
    "payload": {"pattern": "rm -rf", "blocked": True}
})

# Tool verification failures
telemetry.record_event({
    "event_type": "TOOL_VERIFICATION_FAILED",
    "payload": {"tool": "fake_tool", "reason": "hallucinated"}
})
```

## Future Enhancements

1. **Formal Verification**: Use theorem provers to verify code
2. **Type Checking**: Static type analysis before execution
3. **Resource Accounting**: Track and limit resource usage
4. **Adaptive Hardening**: Adjust constraints based on context
5. **Distributed Verification**: Cross-check with other agents

## Conclusion

The hardening architecture transforms agents from "soft-constrained" (follow rules if they want) to "hard-constrained" (physically cannot misbehave). This eliminates entire classes of agent failures:

- **No more parse errors** (constrained decoding)
- **No more lazy responses** (optimized prompts)
- **No more dangerous actions** (sandboxed execution)
- **No more hallucinated tools** (verification loop)

The result is agents that are reliable, safe, and predictable - essential for production use.
