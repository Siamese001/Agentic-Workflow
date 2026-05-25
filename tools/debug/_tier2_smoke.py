"""Exercise the Tier 2-wired AutoPersistenceTracingAdapter end-to-end."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agentic_core.L6_system_learning.stores import version_store as vs_mod


class _Null:
    def persist_active_version(self, *_a, **_k) -> None:
        return None


vs_mod.get_sl_memory_bridge = lambda: _Null()  # type: ignore[assignment]

from agentic_core.L6_system_learning.auto_persistence import AutoPersistenceTracingAdapter
from agentic_core.L6_system_learning.materializer import RuntimeADGMaterializer
from agentic_core.L6_system_learning.span_contracts import validate_tier1_corpus_coverage
from agentic_core.L6_system_learning.store import FileBackedRuntimeADGStore

FileBackedRuntimeADGStore._validate_l4_compliance = lambda self: None  # type: ignore


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        adapter = AutoPersistenceTracingAdapter(
            service_name="test-service",
            enable_auto_persistence=False,  # don't need L4 persist for smoke
            l4_store_path=os.path.join(td, "runtime_adg"),
            l6_base_dir=os.path.join(td, "l6"),
        )
        with adapter.trace_orchestrator(mission="tier2-smoke") as _span:
            pass

        spans = adapter.drain_completed_spans()
        print(f"Spans drained: {len(spans)}")
        for s in spans:
            name = s["name"]
            layer = s["layer"]
            kind = s["kind"]
            print(f"  {name:30s} layer={layer:15s} kind={kind}")

        snap = RuntimeADGMaterializer().materialize(spans, mission="tier2-smoke")
        rep = validate_tier1_corpus_coverage([snap])
        pct = rep.satisfied_pct * 100
        print(f"\nTier 1 satisfied: {rep.satisfied_count()}/5 ({pct:.0f}%)")
        for c, status in rep.category_status.items():
            hits = rep.category_example_hits.get(c, ())
            example = f"  (e.g. {hits[0]})" if hits else ""
            print(f"  [{status:<14}] {c}{example}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
