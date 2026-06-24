"""Prove apps_rg fact-vector readiness without launching U0/C0.

This is an operator-facing wrapper around the import-light readiness gate. It
checks the existing Chroma ``fact_vectors`` collection and bootstrap manifest,
writes a receipt, and exits non-zero when generation would be blocked.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps_rg.runtime.fact_vector_readiness import (
    BLOCKED_PRE_U0_FACT_VECTOR_READINESS,
    PRE_U0_GATE_ID,
    STATUS_PASS,
    build_fact_vector_readiness_receipt,
    write_fact_vector_readiness_receipt,
)


def _default_out_dir() -> Path:
    stamp = time.strftime("%Y%m%d_%H%M%S")
    return (
        REPO_ROOT
        / "artifacts"
        / "apps_rg"
        / "sufficiency_proofs"
        / f"fact_vector_readiness_{stamp}_{time.time_ns()}"
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", default="", help="Directory for the readiness receipt.")
    parser.add_argument("--chroma-path", default="", help="Chroma directory or chroma.sqlite3 path.")
    parser.add_argument(
        "--no-require-manifest-alignment",
        action="store_true",
        help="Diagnostic mode only: prove live Chroma coverage without blocking on stale manifest.",
    )
    parser.add_argument("--json", action="store_true", help="Print compact JSON summary.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    out_dir = Path(args.artifact_dir).resolve() if args.artifact_dir else _default_out_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    receipt = build_fact_vector_readiness_receipt(
        repo_root=REPO_ROOT,
        chroma_path=str(args.chroma_path or ""),
        gate_id=PRE_U0_GATE_ID,
        block_code=BLOCKED_PRE_U0_FACT_VECTOR_READINESS,
        target_context={"source": "tools/apps_rg/prove_fact_vector_readiness.py"},
        require_manifest_alignment=not bool(args.no_require_manifest_alignment),
    )
    receipt_path = out_dir / "fact_vector_readiness.json"
    receipt["receipt_path"] = str(receipt_path)
    write_fact_vector_readiness_receipt(receipt_path, receipt)
    summary: dict[str, Any] = {
        "status": receipt.get("status"),
        "receipt_path": str(receipt_path),
        "block_code": receipt.get("block_code"),
        "reasons": receipt.get("reasons") or [],
        "collection_doc_count": (receipt.get("summary") or {}).get("collection_doc_count"),
        "failed_sections": receipt.get("failed_sections") or [],
        "require_manifest_alignment": not bool(args.no_require_manifest_alignment),
    }
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(
            f"fact_vector_readiness status={summary['status']} "
            f"docs={summary['collection_doc_count']} "
            f"failed_sections={len(summary['failed_sections'])} "
            f"receipt={receipt_path}"
        )
        if summary["reasons"]:
            print("reasons=" + ", ".join(str(r) for r in summary["reasons"]))
    return 0 if receipt.get("status") == STATUS_PASS else 2


if __name__ == "__main__":
    raise SystemExit(main())
