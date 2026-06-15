from __future__ import annotations

import json
from pathlib import Path

from agentic_core.L6_observability.shadow_eval import L6PipelineState, run_6a, run_observer
from agentic_core.L6_observability.shadow_eval.span_export import write_span_artifacts

from tests.l6_observability.test_g28_g29_learning_firewall import _raw_exhaust


def test_span_export_writes_g28_g29_artifact_refs(tmp_path: Path) -> None:
    state = L6PipelineState()
    run_6a(state, _raw_exhaust())
    run_observer(state)

    paths = write_span_artifacts(state.recorder.records, tmp_path)
    exported = json.loads(paths["span_export_json"].read_text(encoding="utf-8"))

    names = [span["name"] for span in exported["spans"]]
    assert "l6.g28.audit_completeness" in names
    assert "l6.g29.learning_firewall" in names
    assert exported["observer_law"]["current_run_mutation_allowed"] is False
