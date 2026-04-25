"""Direct trace of why scanner does not match a guardian on route_gates.py:237."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agentic_core.adg.artifact.multi_writer import (
    has_guardian_for_violation,
    _resolve_except_anchor_lines,
    _extract_guardian_tokens,
    _read_lines_cached,
    _GUARDIAN_MAP,
)

fp = "agentic_core/L0_routing/reasoning/route_gates.py"
for line_no, kind in [
    (237, "return_none_swallow"),
    (255, "return_none_swallow"),
    (127, "broad_exception_catch"),
    (303, "silent_exception_swallow"),
    (347, "silent_exception_swallow"),
    (349, "log_and_swallow"),
    (28, "hardcoded_secret"),
    (146, "return_none_swallow"),
    (144, "return_none_swallow"),
]:
    path_map = {
        237: fp,
        255: fp,
        127: "agentic_core/L2_execution/reasoning/programmatic_tool_runner.py",
        303: "agentic_core/L5_safety/enforcement/exit_control_gate.py",
        347: "agentic_core/L5_safety/enforcement/exit_control_gate.py",
        349: "agentic_core/L5_safety/enforcement/exit_control_gate.py",
        28: "agentic_core/L5_safety/eval_spine/judge_backends/anthropic_stub.py",
        146: "agentic_core/L5_safety/eval_spine/shadow_observer.py",
        144: "agentic_core/runtime/config/routing_thresholds.py",
    }
    p = path_map.get(line_no, fp)
    result = has_guardian_for_violation(p, line_no, kind)
    lines = _read_lines_cached(p)
    anchors = _resolve_except_anchor_lines(lines, line_no)
    tokens_at_anchors = {a: _extract_guardian_tokens(lines[a - 1]) for a in anchors if 1 <= a <= len(lines)}
    print(f"{p}:{line_no} ({kind}) matched={result}")
    print(f"  anchors={anchors}")
    for a, toks in tokens_at_anchors.items():
        snippet = lines[a - 1].strip()[:100]
        print(f"    line {a}: tokens={toks}  <<< {snippet}")
    print()
