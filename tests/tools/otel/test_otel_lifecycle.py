import time

import tools.otel.otel_lifecycle as lifecycle_module


LIFECYCLE_FN_NAMES = [
    "emit_determinism_digest",
    "record_execution_trace",
    "_emit_applies_guardrail",
    "_emit_reads_policy_state",
    "_emit_snapshots_state",
    "_emit_authorize_and_execute",
    "_emit_validates_capability",
    "_emit_routes_to_capability",
    "_emit_writes_via_uwg",
    "_emit_blocks_direct_write",
    "_emit_records_tool_invocation",
    "_emit_captures_execution_output",
    "_emit_dispatches_agent",
    "_emit_coordinates_agents",
    "_emit_records_workflow_lineage",
    "_emit_records_healing_outcome",
    "_emit_escalates_failure",
    "_emit_orchestrates_workflow",
    "_emit_dispatches_healing_run",
    "_emit_invokes_evaluation",
    "_emit_records_telemetry_event",
    "_emit_captures_evaluation_metric",
    "_emit_stores_embedding",
    "_emit_updates_meta_learning_state",
    "_emit_links_execution_to_snapshot",
]


def test_lifecycle_background_registration_completes(monkeypatch):
    calls = []
    monkeypatch.setattr(lifecycle_module, "_LIFECYCLE_AVAILABLE", True)
    for name in LIFECYCLE_FN_NAMES:
        monkeypatch.setattr(
            lifecycle_module, name, lambda *args, _name=name: calls.append(_name), raising=False
        )

    registrar = lifecycle_module.LifecycleRegistrar()
    registrar.start_background()

    deadline = time.time() + 1.0
    while not registrar.registered and time.time() < deadline:
        time.sleep(0.01)

    assert registrar.started is True
    assert registrar.registered is True
    assert registrar.last_error is None
    assert "record_execution_trace" in calls
