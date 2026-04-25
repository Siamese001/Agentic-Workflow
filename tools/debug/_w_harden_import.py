"""Import-smoke test every authorized agent + shim we edited.

py_compile only checks syntax; this executes the module-level code path that
runs on actual import (top-level imports, __all__ evaluation, class body,
module-level calls).
"""

from __future__ import annotations

import importlib
import sys
import traceback

MODULES = [
    # 31 agents authorized (canonical list from cooling artifacts)
    "apps_lic.reasoning.IntelligenceLibrarianAgent",
    "agentic_core.L5_safety.validators.CodeJanitorAgent",
    "agentic_core.L5_safety.validators.GovernanceAgent",
    "agentic_core.L5_safety.validators.PascalSovereigntyAgent",
    "agentic_core.L1_cognition.reasoning.StrategicRecommendationAgent",
    "agentic_core.L2_execution.reasoning.ToolsmithAgent",
    "agentic_core.L3_orchestration.reasoning.CoverageAgent",
    "agentic_core.L3_orchestration.reasoning.OrchestrationHandshakeAgent",
    "agentic_core.L3_orchestration.reasoning.SubatomicHopAgent",
    "agentic_core.L5_safety.reasoning.ArchitectureGovernorValidatorAgent",
    "agentic_core.L5_safety.reasoning.BenchmarkingAgent",
    "agentic_core.L5_safety.reasoning.BootstrapAgent",
    "agentic_core.L5_safety.reasoning.CodeDeduplicationAgent",
    "agentic_core.L5_safety.reasoning.CodeFormatterAgent",
    "agentic_core.L5_safety.reasoning.ComplexityAnalyzerAgent",
    "agentic_core.L5_safety.reasoning.CredentialScannerAgent",
    "agentic_core.L5_safety.reasoning.DependencyPruningAgent",
    "agentic_core.L3_orchestration.reasoning.GravityStateAgent",
    "agentic_core.L5_safety.reasoning.CostGovernorAgent",
    "agentic_core.L0_routing.reasoning.SSOTFolderCleanupAgent",
    "agentic_core.L3_orchestration.reasoning.SubAtomicAgent",
    "agentic_core.L5_safety.reasoning.CodeDetectorAgent",
    "agentic_core.L5_safety.reasoning.CodeEnforcerAgent",
    "agentic_core.L5_safety.reasoning.CodeJanitorAgent",
    "agentic_core.L5_safety.reasoning.CodeValidatorAgent",
    "agentic_core.L5_safety.reasoning.AutonomyGuardianAgent",
    "agentic_core.L5_safety.reasoning.RedSentinelAgent",
    "agentic_core.L5_safety.reasoning.StructureHealerAgent",
    "agentic_core.L0_routing.reasoning.RootCustomsAgent",
    "agentic_core.L5_safety.reasoning.GovernanceAgent",
    "agentic_core.L5_safety.reasoning.LocationHealerAgent",
    # 2 shims we edited
    "agentic_core._compat.core.l5_safety_aliases",
    "agentic_core.interfaces.state_agents",
]

ok = 0
fail: list[tuple[str, str]] = []
for m in MODULES:
    try:
        importlib.import_module(m)
        ok += 1
    except (ImportError, AttributeError, TypeError, ValueError, OSError, RuntimeError) as e:
        fail.append((m, f"{type(e).__name__}: {e}"))
    except Exception as e:  # noqa: BLE001 — harness wants any failure surfaced
        fail.append((m, f"{type(e).__name__}: {e}"))

print(f"[{ok}/{len(MODULES)}] import OK")
for m, err in fail:
    print(f"  FAIL {m}")
    print(f"       {err[:300]}")

sys.exit(1 if fail else 0)
