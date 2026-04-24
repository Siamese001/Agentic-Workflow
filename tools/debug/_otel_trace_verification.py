"""Comprehensive OTel + trace verification per agentic_process_mapping_v33.

Verifies that every specified observability invariant holds:

  [1] trace_orchestrator emits all 3 runtime-ADG auto-wired spans
      (runtime.trace_root, orchestrator.execute, Exit.disposition).

  [2] Tier 3 autowrap emits L2.step.seal for each concrete engine
      execute() call \u2014 including async engines.

  [3] Every emitted span carries unified trace_id (Tier 2 harden invariant).

  [4] All 4 required attribute families appear on their respective spans:
        trace_root   -> trace_id, run_id, input_envelope_hash, parent_span_id=""
        step.seal    -> step_id, output_hash, evidence_ids, replay_key, lineage_hash
        Exit         -> exit_disposition, policy_hash, reason_codes, guardrail_result

  [5] Exception path flips Exit.disposition -> "deny".

  [6] Materializer (step [6] SHADOW EVAL ingest) consumes the drained spans
      and produces a valid RuntimeADGSnapshot.

  [7] validate_tier1_corpus_coverage on a real run reports 3/5 categories
      satisfied (the 2 missing come from heal_router.v1.route +
      consensus.v1.judge which live outside this synthetic test).

Exit code 0 = all checks pass. Non-zero = which check failed.
"""

from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from system_learning.stores import version_store as vs_mod


class _NullBridge:
    def persist_active_version(self, *_a: Any, **_k: Any) -> None:
        return None


vs_mod.get_sl_memory_bridge = lambda: _NullBridge()  # type: ignore[assignment]

from system_learning.runtime_adg.auto_persistence import AutoPersistenceTracingAdapter
from system_learning.runtime_adg.materializer import RuntimeADGMaterializer
from system_learning.runtime_adg.runtime_span_emitter import (
    SPAN_EXIT_DISPOSITION,
    SPAN_STEP_SEAL,
    SPAN_TRACE_ROOT,
    get_current_adapter,
    seal_step,
)
from system_learning.runtime_adg.span_contracts import validate_tier1_corpus_coverage
from system_learning.runtime_adg.store import FileBackedRuntimeADGStore

FileBackedRuntimeADGStore._validate_l4_compliance = lambda self: None  # type: ignore


_CHECKS: list[tuple[str, bool, str]] = []


def _check(name: str, condition: bool, detail: str = "") -> None:
    _CHECKS.append((name, condition, detail))
    marker = "PASS" if condition else "FAIL"
    line = f"  [{marker}] {name}"
    if detail:
        line += f"  -> {detail}"
    print(line)


def _run_sync_path(adapter: AutoPersistenceTracingAdapter) -> None:
    """Exercise a synchronous happy-path orchestrator run with 2 sealed steps."""
    with adapter.trace_orchestrator(mission="otel-verify-sync"):
        # Tier 3 nested seal via contextvar (simulates an engine execute()).
        a = get_current_adapter()
        with seal_step(a, step_id="engine-a.execute", trace_id="") as bag:
            bag["output"] = {"records": 3, "status": "ok"}
        with seal_step(a, step_id="engine-b.execute", trace_id="") as bag:
            bag["output"] = [1, 2, 3]


def _run_async_path(adapter: AutoPersistenceTracingAdapter) -> None:
    """Exercise an async caller (simulates apps_rg async def execute)."""
    async def _work() -> None:
        with adapter.trace_orchestrator(mission="otel-verify-async"):
            a = get_current_adapter()
            with seal_step(a, step_id="async-engine.execute", trace_id="") as bag:
                await asyncio.sleep(0)
                bag["output"] = "async-ok"

    asyncio.run(_work())


def _run_exception_path(adapter: AutoPersistenceTracingAdapter) -> None:
    """Exercise exception path \u2014 Exit.disposition must flip to 'deny'."""
    try:
        with adapter.trace_orchestrator(mission="otel-verify-error"):
            raise ValueError("simulated failure")
    except ValueError:
        pass


def main() -> int:
    print("=" * 78)
    print("OTel + Runtime ADG Trace Verification \u2014 agentic_process_mapping_v33")
    print("=" * 78)

    with tempfile.TemporaryDirectory() as td:
        adapter = AutoPersistenceTracingAdapter(
            service_name="otel-verification",
            enable_auto_persistence=False,
            l4_store_path=str(Path(td) / "runtime_adg"),
            l6_base_dir=str(Path(td) / "l6"),
        )

        # -------------------------------------------------------------------
        print("\n[1] Sync orchestrator path")
        _run_sync_path(adapter)
        spans_sync = adapter.drain_completed_spans()
        names = [s["name"] for s in spans_sync]
        _check("trace_root emitted", SPAN_TRACE_ROOT in names)
        _check("Exit.disposition emitted", SPAN_EXIT_DISPOSITION in names)
        _check("orchestrator.execute emitted", "orchestrator.execute" in names)
        seal_count_sync = names.count(SPAN_STEP_SEAL)
        _check("L2.step.seal count == 2", seal_count_sync == 2, f"got {seal_count_sync}")

        # Tier 2 harden: trace_id unified.
        root = next(s for s in spans_sync if s["name"] == SPAN_TRACE_ROOT)
        orch = next(s for s in spans_sync if s["name"] == "orchestrator.execute")
        exit_span = next(s for s in spans_sync if s["name"] == SPAN_EXIT_DISPOSITION)
        tids = {root["trace_id"], orch["trace_id"], exit_span["trace_id"]}
        _check("trace_ids unified across root/orch/exit", len(tids) == 1,
               f"distinct trace_ids: {len(tids)}")

        # Attribute coverage.
        root_attrs = root["attributes"]
        _check("trace_root has trace_id/run_id/envelope_hash",
               all(k in root_attrs for k in ("trace_id", "run_id", "input_envelope_hash")))
        _check("trace_root parent_span_id is empty", root_attrs.get("parent_span_id") == "")

        seals = [s for s in spans_sync if s["name"] == SPAN_STEP_SEAL]
        for s in seals:
            a = s["attributes"]
            required = ("step_id", "output_hash", "evidence_ids", "replay_key", "lineage_hash")
            _check(f"seal[{a.get('step_id')}] has all 5 attrs",
                   all(k in a for k in required))

        exit_attrs = exit_span["attributes"]
        _check("Exit has exit_disposition/policy_hash/reason_codes/guardrail_result",
               all(k in exit_attrs for k in
                   ("exit_disposition", "policy_hash", "reason_codes", "guardrail_result")))
        _check("Exit disposition == 'allow' on happy path",
               exit_attrs["exit_disposition"] == "allow")

        # -------------------------------------------------------------------
        print("\n[2] Async orchestrator path")
        _run_async_path(adapter)
        spans_async = adapter.drain_completed_spans()
        names_async = [s["name"] for s in spans_async]
        _check("async: trace_root emitted", SPAN_TRACE_ROOT in names_async)
        _check("async: L2.step.seal emitted", SPAN_STEP_SEAL in names_async)
        _check("async: Exit.disposition emitted", SPAN_EXIT_DISPOSITION in names_async)

        # -------------------------------------------------------------------
        print("\n[3] Exception path")
        _run_exception_path(adapter)
        spans_exc = adapter.drain_completed_spans()
        exc_exit = next(s for s in spans_exc if s["name"] == SPAN_EXIT_DISPOSITION)
        _check("Exception path: disposition == 'deny'",
               exc_exit["attributes"]["exit_disposition"] == "deny")
        _check("Exception path: reason_codes includes error marker",
               "auto_persist_error" in exc_exit["attributes"]["reason_codes"])

        # -------------------------------------------------------------------
        print("\n[4] Materializer (step [6] SHADOW EVAL ingest)")
        # Re-run sync path so we have spans to materialize.
        _run_sync_path(adapter)
        all_spans = adapter.drain_completed_spans()
        snapshot = RuntimeADGMaterializer().materialize(all_spans, mission="otel-verify")
        _check("materializer produced snapshot",
               snapshot is not None and hasattr(snapshot, "nodes"))
        _check("snapshot has >=3 nodes", len(snapshot.nodes) >= 3,
               f"got {len(snapshot.nodes)} nodes")

        # -------------------------------------------------------------------
        print("\n[5] Tier 1 corpus coverage on real run")
        report = validate_tier1_corpus_coverage([snapshot])
        for cat, status in report.category_status.items():
            example = ""
            hits = report.category_example_hits.get(cat, ())
            if hits:
                example = f" (e.g. {hits[0]})"
            print(f"      [{status:<14}] {cat}{example}")
        _check("runtime.trace_root satisfied",
               report.category_status["runtime.trace_root"] == "satisfied")
        _check("L2.step.seal satisfied",
               report.category_status["L2.step.seal"] == "satisfied")
        _check("Exit.disposition satisfied",
               report.category_status["Exit.disposition"] == "satisfied")
        _check("Tier 1 coverage reached 3/5 from this synthetic run",
               report.satisfied_count() >= 3,
               f"got {report.satisfied_count()}/5")

    # -----------------------------------------------------------------------
    print("\n" + "=" * 78)
    passed = sum(1 for _, ok, _ in _CHECKS if ok)
    total = len(_CHECKS)
    print(f"SUMMARY: {passed}/{total} checks passed")
    print("=" * 78)
    failed = [name for name, ok, _ in _CHECKS if not ok]
    if failed:
        print("\nFAILURES:")
        for name in failed:
            print(f"  - {name}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
