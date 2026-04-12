"""Debug: Run G11 _DeterminismControlVisitor directly on a blocker module."""

import ast
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agentic_core.adg.extraction.static_scanner import _DeterminismControlVisitor

TEST_FILES = [
    "agentic_core/L0_routing/enforcement/trace_id_generator.py",
    "agentic_core/L0_routing/enforcement/traceability_contracts.py",
    "agentic_core/runtime/trace_emitter.py",
]

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

for rel in TEST_FILES:
    fpath = os.path.join(ROOT, rel)
    with open(fpath, encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source, filename=rel)
    module_adg = f"Module::{rel}"

    visitor = _DeterminismControlVisitor(module_adg, rel)
    visitor.visit(tree)

    print(f"\n{rel}")
    print(f"  Total G11 edges: {len(visitor.edges)}")
    for e in visitor.edges:
        print(f"    {e.relation_type:30s} symbol={e.symbol:40s} L{e.line_no}")

    # Check specifically for emits_determinism_digest
    digest_edges = [e for e in visitor.edges if e.relation_type == "emits_determinism_digest"]
    print(f"  emits_determinism_digest edges: {len(digest_edges)}")
