"""Operator CLI for fact_vectors staging promotion and drain workflows."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from apps_rg.runtime.c0.fact_vector_write_back import (
    drain_held_staged_fact_vectors,
    list_staged_fact_vectors,
    promote_staged_fact_vectors,
    reject_staged_fact_vectors,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chroma-path", default=os.environ.get("CHROMA_PERSIST_DIR", "").strip())
    parser.add_argument("--artifact-dir", type=Path, default=None)
    parser.add_argument("--sparse-dir", type=Path, default=None)
    parser.add_argument("--ids", nargs="*", default=[])
    parser.add_argument("--reason", default="")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--x3-code", default="")
    parser.add_argument("--require-x3-allow", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--list", action="store_true")
    action.add_argument("--promote", action="store_true")
    action.add_argument("--reject", action="store_true")
    action.add_argument("--drain-held", action="store_true")
    return parser


def _emit(doc: dict[str, Any]) -> int:
    print(json.dumps(doc, indent=2, ensure_ascii=False), flush=True)
    return 1 if doc.get("status") == "FAIL" else 0


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.list:
        return _emit(
            list_staged_fact_vectors(
                chroma_path=args.chroma_path,
                limit=args.limit,
            )
        )
    if args.promote:
        return _emit(
            promote_staged_fact_vectors(
                chroma_path=args.chroma_path,
                artifact_dir=args.artifact_dir,
                sparse_dir=args.sparse_dir,
                ids=args.ids,
                run_id=args.run_id,
                x3_code=args.x3_code,
                require_x3_allow=bool(args.require_x3_allow),
                limit=args.limit,
            )
        )
    if args.reject:
        return _emit(
            reject_staged_fact_vectors(
                chroma_path=args.chroma_path,
                ids=args.ids,
                reason=args.reason,
            )
        )
    return _emit(
        drain_held_staged_fact_vectors(
            chroma_path=args.chroma_path,
            reason=args.reason or "drain_held",
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
