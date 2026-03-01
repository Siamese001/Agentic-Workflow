"""
L2 Qwen 14B vLLM inference worker.

Runs inside the WSL vLLM Python environment. Called as a subprocess by the
Windows-side healing pipeline via _get_qwen_vllm_arbiter() in execute_ssot.py.

Usage (invoked by the lazy seam, not directly):
    /home/amita/venvs/vllm/bin/python qwen_vllm_inference.py \
        --agent_name arch_governor \
        --confidence 0.62 \
        --violation_types NAMING HIERARCHY \
        --territory agentic_core \
        --model_path /home/amita/models/Qwen2.5-14B-Instruct-AWQ

Exits 0 on success, prints JSON to stdout:
    {"decision": true, "reason": "...", "model": "Qwen2.5-14B-Instruct-AWQ"}
"""

from __future__ import annotations

import argparse
import json


def _build_prompt(agent_name: str, confidence: float, violation_types: list[str], territory: str) -> str:
    violations_str = ", ".join(violation_types) if violation_types else "UNKNOWN"
    return (
        f"You are a governance arbitration engine for an agentic codebase healing pipeline.\n"
        f"Agent: {agent_name}\n"
        f"Territory: {territory}\n"
        f"Confidence score: {confidence:.2f} (medium confidence band 0.40-0.75)\n"
        f"Violation types: {violations_str}\n\n"
        f"Should this agent proceed with healing? "
        f"Reply with exactly one word: YES or NO, followed by a single sentence of reasoning."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Qwen 14B vLLM governance arbiter")
    parser.add_argument("--agent_name", required=True)
    parser.add_argument("--confidence", type=float, required=True)
    parser.add_argument("--violation_types", nargs="*", default=[])
    parser.add_argument("--territory", required=True)
    parser.add_argument("--model_path", default="/home/amita/models/Qwen2.5-14B-Instruct-AWQ")
    args = parser.parse_args()

    from vllm import LLM, SamplingParams

    llm = LLM(
        model=args.model_path,
        quantization="awq",
        dtype="float16",
        max_model_len=512,
        gpu_memory_utilization=0.7,
    )

    prompt = _build_prompt(args.agent_name, args.confidence, args.violation_types, args.territory)
    sampling_params = SamplingParams(temperature=0.0, max_tokens=80)
    outputs = llm.generate([prompt], sampling_params)
    response = outputs[0].outputs[0].text.strip()

    decision = response.upper().startswith("YES")
    result = {
        "decision": decision,
        "reason": response,
        "model": "Qwen2.5-14B-Instruct-AWQ",
        "agent_name": args.agent_name,
        "confidence_in": args.confidence,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
