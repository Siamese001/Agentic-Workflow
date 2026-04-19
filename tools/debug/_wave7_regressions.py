import sqlite3
from pathlib import Path

c = sqlite3.connect(r"artifacts/adg/adg_indexed_04192026_1251.sqlite")
# All wave 1-6 files that should be at 0 P1
WAVE_FILES = [
    # Wave 1
    "agentic_core/L5_safety/reasoning/FileClassificationAgent.py",
    "agentic_core/L5_safety/reasoning/location_validator.py",
    "agentic_core/L5_safety/reasoning/SystemArchitectAgent.py",
    "agentic_core/L5_safety/reasoning/L5SafetyExerciserAgent.py",
    "agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py",
    "agentic_core/mixins/tracing_mixin.py",
    "agentic_core/utils/workflow_engines/drift_monitor.py",
    # Wave 2
    "agentic_core/mixins/meta_learning_client_mixin.py",
    "agentic_core/knowledge/reasoning/SovereignRAGManagerAgent.py",
    "agentic_core/L3_orchestration/enforcement/mission_runner.py",
    "agentic_core/agents/types/adg_backed_registry.py",
    "agentic_core/L1_cognition/reasoning/ml_decision_support/inference/shadow_logger.py",
    "agentic_core/cache/discovery_cache.py",
    "agentic_core/gateway/api_gateway_integration.py",
    # Wave 3
    "system_learning/stores/telemetry_store.py",
    "system_learning/ml_integration/training_pipeline.py",
    "agentic_core/utils/meta_learning_storage_util.py",
    "agentic_core/agents/types/agent_registry.py",
    "agentic_core/L5_safety/validators/mission_preflight_validator.py",
    "agentic_core/L5_safety/validators/base_detector_validator.py",
    "agentic_core/L5_safety/reasoning/filesystem_ssot_reconciler.py",
    # Wave 4
    "agentic_core/L5_safety/reasoning/GovernanceAgent.py",
    "agentic_core/L5_safety/enforcement/pytest_config_guardrail.py",
    "agentic_core/L5_safety/enforcement/governance/cache_guard.py",
    "agentic_core/L5_safety/enforcement/HealingStrategy.py",
    "agentic_core/L4_state/utils/memory/canonical_store.py",
    "agentic_core/L4_state/cache/gptcache_client.py",
    "agentic_core/L4_state/cache/discovery_cache.py",
    # Wave 5
    "agentic_core/L3_orchestration/reasoning/engines/adg_integration.py",
    "agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py",
    "agentic_core/L0_routing/reasoning/intent_embedding_classifier.py",
    "system_learning/stores/version_store.py",
    "system_learning/state/system_learning_state_manager.py",
    "system_learning/ports/outcome_write_back_hook.py",
    "system_learning/pipelines/meta_learning_pipeline.py",
    # Wave 6
    "system_learning/ml_integration/anomaly_detection.py",
    "system_learning/engines/signal_grouping_engine.py",
    "system_learning/engines/shadow_drift_analyzer.py",
    "system_learning/engines/policy_recommendation_engine.py",
    "system_learning/engines/meta_learning_bus.py",
    "system_learning/engines/l0_threshold_tuner.py",
    "system_learning/engines/l0_routing_confidence_monitor.py",
]
print("Regressed wave files (post-ruff-reformat):")
total = 0
for p in WAVE_FILES:
    n = c.execute(
        "SELECT COUNT(*) FROM violations WHERE severity='HIGH' AND file_path=?",
        (p,),
    ).fetchone()[0]
    if n > 0:
        print(f"  {n:3d}  {p}")
        total += n
print(f"\n  Total regressions: {total}")
