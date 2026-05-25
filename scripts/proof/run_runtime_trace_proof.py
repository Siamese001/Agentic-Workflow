"""Runtime trace proof — emit a canary trace, ingest, validate against contract.

This script is the W1.2 deliverable of plan
``.windsurf/plans/assurance-p1-gates-ab4758.md``. It:

1. Builds a synthetic LIC canary span graph (U0 -> L0 -> C0 -> PA -> L2 ->
   Exit -> UWG).
2. Ingests the spans via
   :func:`agentic_core.L6_observability.otel_runtime_ingest.emit_spans_to_runtime_adg`.
3. Reads the persisted snapshot back from the runtime ADG store.
4. Adapts the snapshot into validate_trace input.
5. Validates against ``canary.lic.v1``.

Exit code:
    0  pass — span DAG matches contract.
    1  fail — one or more contract violations (printed to stdout).
    2  infrastructure error — ingest, persistence, or contract load failed.

Usage::

    python scripts/proof/run_runtime_trace_proof.py
    python scripts/proof/run_runtime_trace_proof.py --contract canary.lic.v1
    python scripts/proof/run_runtime_trace_proof.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any

# Bootstrap sys.path so this script is invokable as
# ``python scripts/proof/run_runtime_trace_proof.py`` AND as
# ``python -m scripts.proof.run_runtime_trace_proof``. Must precede any
# imports of ``agentic_core`` / ``system_learning``.
_REPO_ROOT = str(Path(__file__).resolve().parents[2])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)


def _emit(message: str) -> None:
    """Stderr-safe progress emit (stdout is reserved for --json result)."""
    print(message, file=sys.stderr)


def run_proof(
    *,
    contract_id: str = "canary.lic.v1",
    trace_id: str | None = None,
) -> dict[str, Any]:
    """Run the canary proof end-to-end and return a structured result.

    Returns a dict with at least::

        {
          "ok": bool,
          "contract_id": str,
          "trace_id": str,
          "spans_emitted": int,
          "spans_ingested": int,
          "snapshot_id": str | None,
          "violations": [ {kind, detail, span_name}, ... ],
          "error": str | None,
        }
    """
    # Local imports keep this script importable without paying the cost
    # of pulling in the runtime ADG stack at module-load time. We use the
    # materializer directly (in-process) rather than the file-backed store
    # so the canary is hermetic — no filesystem side effects, no
    # pollution of real runtime ADG storage with synthetic test data.
    from agentic_core.L6_observability.runtime_trace import (
        build_canary_lic_spans,
        load_contract,
        snapshot_to_spans,
        validate_trace,
    )
    from agentic_core.L6_system_learning.materializer import RuntimeADGMaterializer

    resolved_trace_id = trace_id or f"canary-{uuid.uuid4().hex[:12]}"
    result: dict[str, Any] = {
        "ok": False,
        "contract_id": contract_id,
        "trace_id": resolved_trace_id,
        "spans_emitted": 0,
        "spans_ingested": 0,
        "snapshot_id": None,
        "violations": [],
        "error": None,
    }

    # 1. Build canary spans.
    _emit(f"[1/5] Building canary spans (trace_id={resolved_trace_id})")
    spans = build_canary_lic_spans(trace_id=resolved_trace_id)
    result["spans_emitted"] = len(spans)

    # 2. Load contract first so a missing contract fails fast.
    _emit(f"[2/5] Loading contract {contract_id}")
    try:
        contract = load_contract(contract_id)
    except (FileNotFoundError, OSError) as exc:
        result["error"] = f"contract_load_failed: {exc}"
        return result

    # 3. Materialize spans into a runtime ADG snapshot (in-process, hermetic).
    _emit(f"[3/5] Materializing {len(spans)} spans")
    try:
        snapshot = RuntimeADGMaterializer().materialize(spans, mission="lic.canary")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        result["error"] = f"materialize_failed: {exc}"
        return result
    result["spans_ingested"] = len(snapshot.nodes)
    result["snapshot_id"] = snapshot.snapshot_id

    # 4. Adapt snapshot into validate_trace shape.
    _emit("[4/5] Adapting snapshot to validator input")
    span_dicts = snapshot_to_spans(snapshot)

    # 5. Validate against contract.
    _emit(f"[5/5] Validating {len(span_dicts)} spans against {contract_id}")
    validation = validate_trace(contract, span_dicts)
    result["ok"] = validation.ok
    result["violations"] = [asdict(v) for v in validation.violations]
    return result


def _format_human(result: dict[str, Any]) -> str:
    lines: list[str] = []
    status = "PASS" if result["ok"] else "FAIL"
    lines.append(f"runtime_trace_proof: {status}")
    lines.append(f"  contract:    {result['contract_id']}")
    lines.append(f"  trace_id:    {result['trace_id']}")
    lines.append(f"  spans_in:    {result['spans_emitted']}")
    lines.append(f"  spans_out:   {result['spans_ingested']}")
    lines.append(f"  snapshot:    {result['snapshot_id']}")
    if result["error"]:
        lines.append(f"  error:       {result['error']}")
    if result["violations"]:
        lines.append(f"  violations:  {len(result['violations'])}")
        for v in result["violations"]:
            span = v.get("span_name") or "-"
            lines.append(f"    - [{v['kind']}] {span}: {v['detail']}")
    return "\n".join(lines)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Runtime trace proof — canary end-to-end validator.",
    )
    parser.add_argument(
        "--contract",
        default="canary.lic.v1",
        help="contract id to load (default: canary.lic.v1)",
    )
    parser.add_argument(
        "--trace-id",
        default=None,
        help="explicit trace id (default: random canary-XXXXXXXXXXXX)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit JSON result to stdout (machine-readable)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    try:
        result = run_proof(contract_id=args.contract, trace_id=args.trace_id)
    except (ImportError, AttributeError) as exc:
        # Hard infrastructure errors at import-time → exit 2.
        print(f"runtime_trace_proof: infrastructure error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(_format_human(result))

    if result["error"]:
        return 2
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
