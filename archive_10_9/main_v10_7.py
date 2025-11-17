"""Entry point for v10_7 orchestration workflow."""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from agent_orchestration_v10_7 import (
    OrchestrationContext,
    get_graph_app,
    unwrap_node_result,
)
from agent_stacks_v10_8.state_adapter_stack import MainGraphState
from core_v10_7.config import ConfigV10_7, load_config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def run_workflow_async(
    job_path: str,
    master_path: str,
    checkpointer: Optional[Any] = None,
    allow_hil: bool = True,
) -> Dict[str, Any]:
    """Run the LangGraph workflow and stream events to stdout."""

    with open(master_path, "r", encoding="utf-8") as f:
        master_data = json.load(f)
    with open(job_path, "r", encoding="utf-8") as f:
        job_data = json.load(f)

    config: ConfigV10_7 = load_config(master_data)
    context = OrchestrationContext(config)
    initial_state = MainGraphState.from_dict({"job": job_data, "hil": {"enabled": allow_hil}}).to_dict()

    app = get_graph_app(checkpointer, config, context)

    final_state: Dict[str, Any] = {}
    async for event in app.astream_events(initial_state, version="v1"):
        event_type = event.get("event")
        if event_type == "on_graph_start":
            logger.info("Graph start: %s", event)
        elif event_type == "on_node_start":
            logger.info("Node start: %s", event.get("name"))
        elif event_type == "on_chat_model_stream":
            token = event.get("data", {}).get("chunk", "")
            print(token, end="", flush=True)
        elif event_type == "on_graph_end":
            payload = event.get("data") or {}
            final_state = unwrap_node_result(payload)
            logger.info("Graph end")

    return final_state


def main() -> None:
    parser = argparse.ArgumentParser(description="Run v10_7 workflow")
    parser.add_argument("-j", "--job", required=True, help="Path to job JSON")
    parser.add_argument("-m", "--master", required=True, help="Path to master JSON")
    parser.add_argument("--no-hil", action="store_true", help="Disable HIL pause")
    args = parser.parse_args()

    try:
        final_state = asyncio.run(
            run_workflow_async(
                job_path=args.job,
                master_path=args.master,
                checkpointer=None,
                allow_hil=not args.no_hil,
            )
        )
    except Exception as exc:  # pragma: no cover - CLI guard
        logger.error("Workflow failed: %s", exc)
        raise SystemExit(1) from exc

    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)
    output_path = outputs_dir / "final_state.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_state, f, indent=2)

    logger.info("Workflow complete. Output saved to %s", output_path)
    raise SystemExit(0)


if __name__ == "__main__":
    main()
