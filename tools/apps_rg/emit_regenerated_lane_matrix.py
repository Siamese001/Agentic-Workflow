"""Emit W9 regenerated_lane_matrix.json from runtime proof dirs."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root

REGEN_RUNS = (
    ("headline", "headline_20260518_233123"),
    ("ibm_bullets", "ibm_bullets_20260518_233233"),
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    repo = find_repo_root()
    rows: list[dict] = []
    for lane, run_id in REGEN_RUNS:
        rd = repo / "artifacts/apps_rg/runtime_proofs" / lane / "real" / run_id
        x3 = json.loads((rd / "x3_disposition.json").read_text(encoding="utf-8")) if rd.is_dir() else {}
        x2 = json.loads((rd / "x2_gate_outputs.json").read_text(encoding="utf-8")) if (rd / "x2_gate_outputs.json").is_file() else {}
        rows.append(
            {
                "lane": lane,
                "run_id": run_id,
                "artifact_dir": rd.relative_to(repo).as_posix() if rd.is_dir() else None,
                "command": (
                    f"python -m apps_rg --section {lane} --provider qwen_vllm "
                    "--x1d-judges gemini_pro,openai_chatgpt,anthropic_claude --allow-non-allow-exit-zero"
                ),
                "runtime_generation_status": x3.get("runtime_generation_status"),
                "x3_code": x3.get("x3_code"),
                "x2_failed": x2.get("x2_failed"),
                "product_quality_status": x3.get("product_quality_status"),
                "real_llm_confirmed": x3.get("runtime_generation_status") == "REAL_LLM",
                "offline_stub": x3.get("runtime_generation_status") == "OFFLINE_CONTRACT_STUB",
                "mocked_judges": x3.get("mocked_judges") or [],
                "rollup_selected": False,
                "decisive_note": "Regenerated REAL_LLM run; not selected for rollup (X3_BLOCK or score below pinned run).",
            },
        )
    blob = {
        "schema": "apps_rg.regenerated_lane_matrix.v1",
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
        "regenerations": rows,
    }
    out = repo / "artifacts/apps_rg/runtime_proofs/final_resume_assembly/regenerated_lane_matrix.json"
    if args.write:
        out.write_text(json.dumps(blob, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {out.relative_to(repo)}")
    else:
        print(json.dumps(blob, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
