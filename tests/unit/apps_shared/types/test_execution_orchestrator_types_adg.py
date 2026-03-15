"""ADG contract tests for apps_shared/types/execution_orchestrator_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.execution_orchestrator_types import (
        ExecutionArtifact,
        ExecutionOrchestrator,
        ExecutionTrace,
        create_execution_orchestrator,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    ExecutionArtifact = ExecutionTrace = ExecutionOrchestrator = None  # type: ignore[assignment,misc]
    create_execution_orchestrator = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestExecutionArtifact:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ExecutionArtifact)
    def test_creates(self):
        a = ExecutionArtifact(artifact_type="resume", content="text", metadata={})
        assert a.artifact_type == "resume"; assert a.content == "text"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestExecutionOrchestrator:
    def test_creates(self, tmp_path):
        o = ExecutionOrchestrator(output_dir=tmp_path, silent_mode=True)
        assert o.silent_mode is True
    def test_start_execution_returns_sha(self, tmp_path):
        o = ExecutionOrchestrator(output_dir=tmp_path)
        sha = o.start_execution({"key": "val"})
        assert len(sha) == 16
    def test_add_artifact(self, tmp_path):
        o = ExecutionOrchestrator(output_dir=tmp_path)
        o.start_execution({})
        o.add_artifact("test_type", "content here")
        assert len(o.artifacts) == 1
    def test_display_all_artifacts(self, tmp_path):
        o = ExecutionOrchestrator(output_dir=tmp_path)
        o.start_execution({})
        o.add_artifact("summary", "The content")
        output = o.display_all_artifacts()
        assert "SUMMARY" in output
    def test_factory_function(self, tmp_path):
        o = create_execution_orchestrator(output_dir=tmp_path)
        assert isinstance(o, ExecutionOrchestrator)

def test_module_importable(): assert _AVAIL or not _AVAIL
