"""Collection policy for retired apps_eval legacy tests.

Active apps_eval coverage lives under ``apps_eval/tests``. The files ignored
here target the pre-reset agent/orchestrator/service implementation that was
quarantined by the RG/LIC hard reset plan.
"""

collect_ignore = [
    "engines/test_narrative_judge_scorer.py",
    "test_apps_eval_integration.py",
    "test_base_eval_engine.py",
    "test_contract.py",
    "test_eval_orchestrator.py",
    "test_eval_to_bus_roundtrip.py",
    "test_eval_to_bus_roundtrip_micro.py",
    "test_eval_types.py",
    "test_evaluation_engines.py",
    "test_promotion_loop.py",
    "test_properties.py",
    "test_quality_services.py",
    "test_validators.py",
]
