"""Entry point for the consolidated workflow."""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any, Dict

from .config import ConfigLoader
from .context import create_workflow_context
from .orchestration import get_graph_app


async def run_workflow_async(config_path: str | None = None, job_input_path: str | None = None, master_resume_path: str | None = None) -> Dict[str, Any]:
    cfg = ConfigLoader.load(config_path)
    ctx = create_workflow_context(cfg.model, cfg.temperature, cfg.max_tokens)
    app = get_graph_app(ctx)
    job_input: Dict[str, Any] = {}
    if job_input_path:
        job_input = json.loads(Path(job_input_path).read_text())
    async for event in app.astream_events(job_input):
        if event.get("event") == "final":
            final = event["data"]
            out_dir = Path("outputs")
            out_dir.mkdir(exist_ok=True)
            (out_dir / "final_resume.json").write_text(json.dumps(final.__dict__, indent=2))
            return final.__dict__
    return {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run consolidated v10_9 workflow")
    parser.add_argument("-c", "--config", help="Path to config json", default=None)
    parser.add_argument("-j", "--job", help="Path to job input json", default=None)
    parser.add_argument("-m", "--master", help="Path to master resume json", default=None)
    args = parser.parse_args()
    asyncio.run(run_workflow_async(args.config, args.job, args.master))


if __name__ == "__main__":
    main()
