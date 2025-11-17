import asyncio
import json
from pathlib import Path

from core_v10_7.config import ConfigV10_7
from run_learning_v10_7 import run_meta_learning


def test_meta_learning_runs_and_writes_summary(tmp_path: Path):
    feedback_path = tmp_path / "feedback.log"
    with open(feedback_path, "w", encoding="utf-8") as f:
        f.write(json.dumps({"workflow_id": "wf-1", "score": 0.9}) + "\n")
        f.write(json.dumps({"workflow_id": "wf-2", "score": 0.8}) + "\n")

    config = ConfigV10_7(
        telemetry={"feedback_log_path": str(feedback_path), "meta_learning_output": str(tmp_path / "out.json")},
        meta_loop_config={"enable_meta_learning": True},
    )

    summary = asyncio.get_event_loop().run_until_complete(run_meta_learning(config))
    assert summary["meta_learning_enabled"] is True
    assert summary["metrics"]["total_entries"] == 2
    assert Path(summary["output_path"]).exists()
