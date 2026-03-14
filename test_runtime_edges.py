"""
Test script to verify runtime ADG edges are emitted correctly.

Tests:
1. TraceContext.run_frame() emits records_execution_trace
2. RunStateAuthority.read() emits observes_runtime_state
3. RunStateAuthority.snapshot() emits snapshots_state
"""

import logging
import sys
from pathlib import Path

# Configure logging to capture ADG edge emissions
logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

# Test 1: TraceContext.run_frame() emits records_execution_trace
print("=" * 80)
print("TEST 1: TraceContext.run_frame() - records_execution_trace edge")
print("=" * 80)

from agentic_core.runtime.trace_context import get_trace_context

trace_ctx = get_trace_context()
with trace_ctx.run_frame(layer="L3", module="test_module", operation="test_op"):
    print("  Inside trace frame - should emit records_execution_trace")

print("\n")

# Test 2: RunStateAuthority.read() emits observes_runtime_state
print("=" * 80)
print("TEST 2: RunStateAuthority.read() - observes_runtime_state edge")
print("=" * 80)

from agentic_core.L4_state.authority.run_state_authority import get_run_state_authority

rsa = get_run_state_authority()
rsa.commit("test_key", "test_value", run_id="test-run-001")
value, version = rsa.read("test_key")
print(f"  Read value: {value}, version: {version}")

print("\n")

# Test 3: RunStateAuthority.snapshot() emits snapshots_state
print("=" * 80)
print("TEST 3: RunStateAuthority.snapshot() - snapshots_state edge")
print("=" * 80)

snapshot = rsa.snapshot("test_checkpoint", run_id="test-run-001")
print(f"  Snapshot created: {snapshot.label}, hash: {snapshot.content_hash}")

print("\n")

# Test 4: DeterministicOrchestrator with RSA integration
print("=" * 80)
print("TEST 4: DeterministicOrchestrator - integrated runtime edges")
print("=" * 80)

from agentic_core.L3_orchestration.engines.deterministic_orchestrator import DeterministicOrchestrator
from agentic_core.L0_routing.types.governance_types import GovernedPayload

orch = DeterministicOrchestrator(run_id="test-orch-001")
print(f"  Orchestrator initialized with run_id: {orch.run_id}")

# Read agent_registry_hash from RSA (should emit observes_runtime_state)
agent_hash, version = orch._rsa.read("agent_registry_hash")
print(f"  Agent registry hash read from RSA: {agent_hash[:16]}..., version: {version}")

print("\n")
print("=" * 80)
print("ALL TESTS COMPLETE")
print("=" * 80)
print("\nCheck logs above for ADG edge emissions:")
print("  - 'records_execution_trace' from TraceContext")
print("  - 'observes_runtime_state' from RunStateAuthority.read()")
print("  - 'snapshots_state' from RunStateAuthority.snapshot()")
