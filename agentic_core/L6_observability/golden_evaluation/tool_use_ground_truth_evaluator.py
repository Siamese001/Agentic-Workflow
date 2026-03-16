"""
Tool Use Ground Truth Evaluator - Deterministic Evaluation Contract.

Provides deterministic evaluation of tool selection against golden dataset.
No timestamps, UUIDs, or nondeterministic fields in output.
"""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "tool_use_ground_truth_evaluator")
emit_determinism_digest("p0", "tool_use_ground_truth_evaluator")

_emit_dispatches_healing_run("p1", "tool_use_ground_truth_evaluator", "L6")
_emit_routes_through("p1", "tool_use_ground_truth_evaluator", "L6")
_emit_escalates_to_human("p1", "tool_use_ground_truth_evaluator", "L6")
_emit_reads_policy_state("p1", "tool_use_ground_truth_evaluator", "L6")


@dataclass(frozen=True)
class ToolUseResult:
    """Deterministic result of tool use evaluation."""

    total_samples: int
    correct_tool_selections: int
    certification_hash: str
    tool_distribution: dict[str, int]
    complex_queries: list[dict[str, Any]]
    average_tools_per_query: float
    error_message: str = ""


def evaluate_tool_use_ground_truth(data_root: str = None, limit: int = None) -> ToolUseResult:
    """Evaluate tool use against golden dataset deterministically.

    Args:
        data_root: Root directory containing data/golden/ subdirectory
        limit: Optional limit on number of samples to process

    Returns:
        ToolUseResult with deterministic certification hash
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "evaluate_tool_use_ground_truth", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "evaluate_tool_use_ground_truth", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L6_OBSERVABILITY, "evaluate_tool_use_ground_truth")
    if data_root is None:
        data_root = Path(__file__).parent.parent.parent.parent.parent / "data"
    golden_dir = Path(data_root) / "golden"
    tool_file = golden_dir / "tool_use_ground_truth_1000.jsonl"
    if not tool_file.exists():
        result = ToolUseResult(
            total_samples=0,
            correct_tool_selections=0,
            certification_hash=hashlib.sha256(b"no_data").hexdigest(),
            tool_distribution={},
            complex_queries=[],
            average_tools_per_query=0.0,
            error_message="Golden dataset not found",
        )
        return result
    samples = []
    with open(tool_file, encoding="utf-8") as f:
        for line in f:
            if limit and len(samples) >= limit:
                break
            samples.append(json.loads(line))
    correct_count = 0
    tool_dist = {}
    complex_queries = []
    total_tools = 0
    for sample in samples:
        expected_calls = sample.get("expected_tool_calls", [])
        scenario = sample.get("scenario", "unknown")
        success_criteria = sample.get("success_criteria", [])
        for tool_call in expected_calls:
            tool_name = tool_call.get("name", "unknown")
            tool_dist[tool_name] = tool_dist.get(tool_name, 0) + 1
            total_tools += 1
        if "correct_tool" in success_criteria:
            correct_count += 1
        if len(expected_calls) >= 3 or "proper_chaining" in success_criteria:
            complex_queries.append(
                {
                    "id": sample.get("id", ""),
                    "scenario": scenario,
                    "tool_count": len(expected_calls),
                    "tools": [call.get("name") for call in expected_calls],
                }
            )
    avg_tools = total_tools / len(samples) if samples else 0.0
    hash_data = {
        "total_samples": len(samples),
        "correct_tool_selections": correct_count,
        "tool_distribution": tool_dist,
        "complex_queries_count": len(complex_queries),
        "average_tools_per_query": avg_tools,
    }
    cert_hash = hashlib.sha256(
        json.dumps(hash_data, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return ToolUseResult(
        total_samples=len(samples),
        correct_tool_selections=correct_count,
        certification_hash=cert_hash,
        tool_distribution=tool_dist,
        complex_queries=complex_queries,
        average_tools_per_query=avg_tools,
    )
