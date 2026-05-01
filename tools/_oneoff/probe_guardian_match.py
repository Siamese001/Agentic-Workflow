"""Probe has_guardian_for_violation for the stubborn retrieval_benchmark site."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agentic_core.adg.artifact.multi_writer import (
    has_guardian_for_violation,
    _resolve_except_anchor_lines,
    _extract_guardian_tokens,
    _GUARDIAN_MAP,
)

fp = "agentic_core/L3_orchestration/reasoning/engines/retrieval_benchmark.py"
line_no = 143
edge_kind = "default_fallback_masking"

print(f"edge_kind: {edge_kind}")
print(f"guardians for edge_kind: {_GUARDIAN_MAP.get(edge_kind)}")
print(f"line_no: {line_no}")

lines = Path(fp).read_text(encoding="utf-8").splitlines()
print(f"line {line_no}: {lines[line_no - 1]!r}")
print(f"line {line_no + 6}: {lines[line_no + 5]!r}")

anchors = _resolve_except_anchor_lines(lines, line_no)
print(f"anchor_lines: {anchors}")
for a in sorted(anchors):
    if 1 <= a <= len(lines):
        ln_text = lines[a - 1]
        tokens = _extract_guardian_tokens(ln_text)
        print(f"  anchor {a}: tokens={tokens}  line={ln_text!r}")

result = has_guardian_for_violation(fp, line_no, edge_kind)
print(f"has_guardian_for_violation: {result}")
