#!/usr/bin/env python3
"""Profile individual visitor costs per file to find the bottleneck."""
import ast
import time
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# suppress hard_fails noise
import logging
logging.disable(logging.CRITICAL)

from agentic_core.adg.extraction.static_scanner import (
    _ImportVisitor, _CallVisitor, _InheritanceVisitor, _AttributeVisitor,
    _CompositionVisitor, _DynamicExecutionVisitor, _InternalCallGraphVisitor,
    _TestTraceabilityVisitor, _GovernancePlaneVisitor, _CriticalEdgeVisitor,
    _SymbolInventoryVisitor, _DecoratorVisitor, _TypeAnnotationVisitor,
    _UnusedImportVisitor, _AntipatternVisitor, _PromptSlotVisitor,
    _ExecutionTraceVisitor, _HealerValidatorVisitor, _EmbeddingPipelineVisitor,
    _HITLVisitor, _SafetyEnforcementVisitor, _SandboxAirlockVisitor,
    _CapabilityBudgetVisitor, _JITContextVisitor, _BoundaryVerifierVisitor,
    _DeterminismControlVisitor, _IOInterceptionVisitor, _MutationTransportVisitor,
    _ExecutionProofVisitor, _PathControlVisitor, _EvalSpineVisitor,
    _DuplicateMethodVisitor, _UnreachableCodeAfterRaiseVisitor, _SecretAccessVisitor,
    _AgentDispatchVisitor, _DynamicInvocationVisitor, _NondeterminismVisitor,
    _L5ValidationProofVisitor, _LearningProvenanceVisitor,
    _P1OrchestrationGovernanceVisitor, _P2ExecutionCapabilityVisitor,
    _P3OrchestrationHealingVisitor, _P3LearningMaturityVisitor,
    _P4ObservabilityGovernanceVisitor, _P4StateTelemetryVisitor,
    _AntipatternRegistryVisitor, _ConfigGovernanceVisitor,
    _PolicyStateObserverVisitor, _HealingOrchestratorVisitor,
    canonical_name, _repo_relative,
)
from agentic_core.adg.identity.normalizer import IdentityNormalizer

# Use a complex real file as test subject
test_files = [
    ROOT / "agentic_core" / "adg" / "extraction" / "static_scanner.py",
    ROOT / "agentic_core" / "runtime" / "lifecycle_trace_contract.py",
    ROOT / "tests" / "adg" / "test_surface_linking_example.py",
]

for test_file in test_files:
    if not test_file.exists():
        continue
    print(f"\n{'='*60}")
    print(f"FILE: {test_file.relative_to(ROOT)}")
    print(f"Size: {test_file.stat().st_size / 1024:.1f} KB")

    source = test_file.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(source)
    rel = str(test_file.relative_to(ROOT)).replace("\\", "/")
    module_adg = canonical_name("Module", rel)
    identity_normalizer = IdentityNormalizer(repo_root=ROOT)

    VISITORS = [
        ("_ImportVisitor",               lambda: _ImportVisitor(module_adg, rel, identity_normalizer=identity_normalizer)),
        ("_CallVisitor",                 lambda: _CallVisitor(module_adg, rel)),
        ("_InheritanceVisitor",          lambda: _InheritanceVisitor(module_adg, rel)),
        ("_AttributeVisitor",            lambda: _AttributeVisitor(module_adg, rel)),
        ("_CompositionVisitor",          lambda: _CompositionVisitor(module_adg, rel)),
        ("_DynamicExecutionVisitor",     lambda: _DynamicExecutionVisitor(module_adg, rel)),
        ("_InternalCallGraphVisitor",    lambda: _InternalCallGraphVisitor(module_adg, rel)),
        ("_TestTraceabilityVisitor",     lambda: _TestTraceabilityVisitor(module_adg, rel)),
        ("_GovernancePlaneVisitor",      lambda: _GovernancePlaneVisitor(module_adg, rel)),
        ("_CriticalEdgeVisitor",         lambda: _CriticalEdgeVisitor(module_adg, rel)),
        ("_SymbolInventoryVisitor",      lambda: _SymbolInventoryVisitor(module_adg, rel)),
        ("_DecoratorVisitor",            lambda: _DecoratorVisitor(module_adg, rel)),
        ("_TypeAnnotationVisitor",       lambda: _TypeAnnotationVisitor(module_adg, rel)),
        ("_UnusedImportVisitor",         lambda: _UnusedImportVisitor()),
        ("_AntipatternVisitor",          lambda: _AntipatternVisitor(module_adg, rel)),
        ("_PromptSlotVisitor",           lambda: _PromptSlotVisitor(module_adg, rel)),
        ("_ExecutionTraceVisitor",       lambda: _ExecutionTraceVisitor(module_adg, rel)),
        ("_HealerValidatorVisitor",      lambda: _HealerValidatorVisitor(module_adg, rel)),
        ("_EmbeddingPipelineVisitor",    lambda: _EmbeddingPipelineVisitor(module_adg, rel)),
        ("_HITLVisitor",                 lambda: _HITLVisitor(module_adg, rel)),
        ("_SafetyEnforcementVisitor",    lambda: _SafetyEnforcementVisitor(module_adg, rel)),
        ("_SandboxAirlockVisitor",       lambda: _SandboxAirlockVisitor(module_adg, rel)),
        ("_CapabilityBudgetVisitor",     lambda: _CapabilityBudgetVisitor(module_adg, rel)),
        ("_JITContextVisitor",           lambda: _JITContextVisitor(module_adg, rel)),
        ("_BoundaryVerifierVisitor",     lambda: _BoundaryVerifierVisitor(module_adg, rel)),
        ("_DeterminismControlVisitor",   lambda: _DeterminismControlVisitor(module_adg, rel)),
        ("_IOInterceptionVisitor",       lambda: _IOInterceptionVisitor(module_adg, rel)),
        ("_MutationTransportVisitor",    lambda: _MutationTransportVisitor(module_adg, rel)),
        ("_ExecutionProofVisitor",       lambda: _ExecutionProofVisitor(module_adg, rel)),
        ("_PathControlVisitor",          lambda: _PathControlVisitor(module_adg, rel)),
        ("_EvalSpineVisitor",            lambda: _EvalSpineVisitor(module_adg, rel)),
        ("_DuplicateMethodVisitor",      lambda: _DuplicateMethodVisitor(module_adg, rel)),
        ("_UnreachableCodeAfterRaise",   lambda: _UnreachableCodeAfterRaiseVisitor(module_adg, rel)),
        ("_SecretAccessVisitor",         lambda: _SecretAccessVisitor(module_adg, rel)),
        ("_AgentDispatchVisitor",        lambda: _AgentDispatchVisitor(module_adg, rel)),
        ("_DynamicInvocationVisitor",    lambda: _DynamicInvocationVisitor(module_adg, rel)),
        ("_NondeterminismVisitor",       lambda: _NondeterminismVisitor(module_adg, rel)),
        ("_L5ValidationProofVisitor",    lambda: _L5ValidationProofVisitor(module_adg, rel)),
        ("_LearningProvenanceVisitor",   lambda: _LearningProvenanceVisitor(module_adg, rel)),
        ("_P1OrchGovernanceVisitor",     lambda: _P1OrchestrationGovernanceVisitor(module_adg, rel)),
        ("_P2ExecutionCapability",       lambda: _P2ExecutionCapabilityVisitor(module_adg, rel)),
        ("_P3OrchHealingVisitor",        lambda: _P3OrchestrationHealingVisitor(module_adg, rel)),
        ("_P3LearningMaturity",          lambda: _P3LearningMaturityVisitor(module_adg, rel)),
        ("_P4ObservabilityGov",          lambda: _P4ObservabilityGovernanceVisitor(module_adg, rel)),
        ("_P4StateTelemetry",            lambda: _P4StateTelemetryVisitor(module_adg, rel)),
        ("_AntipatternRegistry",         lambda: _AntipatternRegistryVisitor(module_adg, rel)),
        ("_ConfigGovernanceVisitor",     lambda: _ConfigGovernanceVisitor(module_adg, rel)),
        ("_PolicyStateObserver",         lambda: _PolicyStateObserverVisitor(module_adg, rel)),
        ("_HealingOrchestrator",         lambda: _HealingOrchestratorVisitor(module_adg, rel)),
    ]

    timings = []
    for name, factory in VISITORS:
        v = factory()
        t0 = time.perf_counter()
        v.visit(tree)
        elapsed = time.perf_counter() - t0
        timings.append((elapsed, name))

    timings.sort(reverse=True)
    total = sum(t for t, _ in timings)
    print(f"{'Visitor':<35} {'ms':>8}  {'%':>6}")
    print("-" * 55)
    for elapsed, name in timings:
        pct = elapsed / total * 100 if total else 0
        print(f"{name:<35} {elapsed*1000:>8.1f}  {pct:>5.1f}%")
    print(f"{'TOTAL':<35} {total*1000:>8.1f}")

print("\nDone.")
