"""Test that _ArchitectureHandoffVisitor correctly extracts gates_promotion edges."""

import ast
import sys

sys.path.insert(0, ".")

from agentic_core.adg.extraction.visitors import VisitorContext
from agentic_core.adg.extraction.visitors.orchestration import _ArchitectureHandoffVisitor
import agentic_core.adg.contracts.schema_util as _su

print("HANDOFF_GATES_SYMBOLS:", getattr(_su, "HANDOFF_GATES_SYMBOLS", "MISSING"))
print("HANDOFF_PROMOTE_SYMBOLS:", getattr(_su, "HANDOFF_PROMOTE_SYMBOLS", "MISSING"))

code = """
import uuid
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_gates_promotion,
    _emit_promotes_future_run_change,
)

def stage_proposal(self):
    _emit_gates_promotion(str(uuid.uuid4()), "EvalSpine.stage_proposal", "x")

def commit_optimization(self):
    _emit_promotes_future_run_change(str(uuid.uuid4()), "EvalSpine.commit_optimization", "y")
"""

tree = ast.parse(code)
ctx = VisitorContext(
    module_adg_name="ADG::Module::agentic_core/runtime/engine/eval_spine.py",
    source_file="agentic_core/runtime/engine/eval_spine.py",
)
v = _ArchitectureHandoffVisitor(ctx)
v.visit(tree)
edges = v.extract_edges()
print(f"\nExtracted {len(edges)} edges:")
for e in edges:
    print(f"  relation_type={e.relation_type}  symbol={e.symbol}  line={e.line_no}")
