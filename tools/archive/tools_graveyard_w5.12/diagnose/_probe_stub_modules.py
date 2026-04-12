"""Probe which modules the stub test files are supposed to test."""

import importlib

CANDIDATES = [
    "agentic_core.config.core.config_loader",
    "agentic_core.config.core.sovereign_config",
    "agentic_core.L3_orchestration.protocols.IOrchestratorProtocol",
    "agentic_core.L3_orchestration.protocols.IValidatorProtocol",
    "agentic_core.L1_cognition.base.L1CognitionBase",
    "agentic_core.L2_execution.base.L2ExecutionBase",
    "agentic_core.L3_orchestration.base.L3OrchestrationBase",
    "agentic_core.L4_state.base.L4StateBase",
    "agentic_core.L5_safety.base.L5SafetyBase",
    "agentic_core.L6_observability.base.L6ObservabilityBase",
    "system_learning.engines.classification_kernel",
    "system_learning.engines.meta_learning_engine",
    "system_learning.engines.structural_healing_engine",
    # HOPPipelineExecutor / FileClassificationAgent / RGStrategyExecutor / RGValidationExecutor
    "agentic_core.L3_orchestration.pipelines.HOPPipelineExecutor",
    "agentic_core.L0_routing.agents.FileClassificationAgent",
    "agentic_core.L3_orchestration.executors.RGStrategyExecutor",
    "agentic_core.L3_orchestration.executors.RGValidationExecutor",
    "agentic_core.L2_execution.executors.RGStrategyExecutor",
    "agentic_core.L2_execution.executors.RGValidationExecutor",
]

for mod in CANDIDATES:
    try:
        m = importlib.import_module(mod)
        print(f"OK  {mod}")
    except ImportError as e:
        print(f"ERR {mod}: {e}")
    # guardian: allow-silent-swallow
    except Exception as e:
        print(f"EXC {mod}: {e}")
