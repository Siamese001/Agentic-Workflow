"""
L2 Qwen 14B vLLM inference worker.

Runs inside the WSL vLLM Python environment. Called as a subprocess by the
Windows-side healing pipeline via _get_qwen_vllm_arbiter() in execute_ssot.py.

Usage (invoked by the lazy seam, not directly):
    /home/amita/venvs/vllm/bin/python qwen_vllm_inference.py         --agent_name arch_governor         --confidence 0.62         --violation_types NAMING HIERARCHY         --territory agentic_core         --model_path /home/amita/models/Qwen2.5-14B-Instruct-AWQ

Exits 0 on success, prints JSON to stdout:
    {"decision": true, "reason": "...", "model": "Qwen2.5-14B-Instruct-AWQ"}
"""

from __future__ import annotations

import argparse
import json

from agentic_core.L2_execution.healers.healing_tier_config import QWEN_GPU_MEM_UTIL
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


def _build_prompt(agent_name: str, violation_types: list[str], territory: str, score: int, gate: str) -> str:
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_build_prompt", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_build_prompt", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "_build_prompt")
    violations_str = ", ".join(violation_types) if violation_types else "UNKNOWN"
    band = (
        "low (agent-native)" if score <= 13 else "medium (Qwen-advised)" if score <= 26 else "high (Gemini)"
    )
    return f"You are a healing-plan advisor for an agentic codebase pipeline.\nScore-based routing has already dispatched this to you: score={score} ({band}), gate={gate}.\nHealing WILL proceed. Your role is to describe what the agent should do and confirm it is safe.\n\nAgent: {agent_name}\nTerritory: {territory}\nViolations detected: {violations_str}\n\nIn one sentence, describe the specific healing action {agent_name} should take for these violations.\nThen reply YES to confirm it is safe.\nOnly reply NO if the action would cause irreversible data loss or break a production invariant.\nFormat: YES <healing action description> OR NO <specific reason>."


def main() -> None:
    parser = argparse.ArgumentParser(description="Qwen 14B vLLM governance arbiter")
    parser.add_argument("--agent_name", required=True)
    parser.add_argument("--violation_types", nargs="*", default=[])
    parser.add_argument("--territory", required=True)
    parser.add_argument("--score", type=int, default=0)
    parser.add_argument("--gate", default="")
    parser.add_argument("--model_path", default="/home/amita/models/Qwen2.5-14B-Instruct-AWQ")
    args = parser.parse_args()
    from vllm import LLM, SamplingParams

    # guardian: allow-magic-config
    llm = LLM(
        model=args.model_path,
        quantization="awq",
        dtype="float16",
        max_model_len=512,
        gpu_memory_utilization=QWEN_GPU_MEM_UTIL,
    )
    prompt = _build_prompt(args.agent_name, args.violation_types, args.territory, args.score, args.gate)
    # guardian: allow-magic-config
    sampling_params = SamplingParams(temperature=0.0, max_tokens=80)
    outputs = llm.generate([prompt], sampling_params)
    response = outputs[0].outputs[0].text.strip()
    decision = response.upper().startswith("YES")
    result = {
        "decision": decision,
        "reason": response,
        "model": "Qwen2.5-14B-Instruct-AWQ",
        "agent_name": args.agent_name,
        "score": args.score,
        "gate": args.gate,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
