"""Record live Qwen fixtures for deterministic replay.

Run with the local vLLM endpoint up:

    QWEN_LIVE=1 python scripts/record_fixtures.py

Each scenario's model decision is captured to src/runtime/agent_fixtures/<hash>.json.
Existing fixtures are reused (delete a fixture to re-record that case). Without
QWEN_LIVE=1 this prints a notice and records nothing.
"""

from __future__ import annotations

import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.runtime import SCENARIOS  # noqa: E402
from src.runtime.agent import build_prompt, decide  # noqa: E402


def main() -> int:
    live = os.environ.get("QWEN_LIVE") == "1"
    if not live:
        print("QWEN_LIVE != 1 — refusing to make live calls. Set QWEN_LIVE=1 to record.")
        return 1
    for sid, scn in SCENARIOS.items():
        _, _, prompt_hash = build_prompt(scn)
        decision = decide(scn, live=True)
        src = decision.provenance.get("source")
        print(
            f"{sid}: hash={prompt_hash} source={src} "
            f"recommendation={decision.recommendation} "
            f"latency={decision.provenance.get('latency_ms')}ms"
        )
    print("Done. Fixtures in src/runtime/agent_fixtures/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
