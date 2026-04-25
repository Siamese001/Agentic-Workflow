"""RAGBench TechQA loader.

Provides two loader paths:

  1. ``load_local(path)`` — read an existing JSONL fixture (offline, no
     network). This is the default code path and is used by
     ``ragbench_runner.py`` and the CI tests.
  2. ``download_techqa(out_path, *, n=50)`` — fetch the RAGBench TechQA
     subset from HuggingFace (``rungalileo/ragbench``) and serialise the
     first ``n`` queries into the JSONL schema shared with
     ``data/eval/golden/ragbench_techqa_synthetic.jsonl``.

The download path requires ``datasets`` (``pip install datasets``) and
network access. It is **not** invoked by tests or by ``ragbench_runner``;
it must be run explicitly by an operator who has reviewed the RAGBench
license terms.

License note: RAGBench is published by Galileo Labs under the
``rungalileo/ragbench`` namespace on HuggingFace. The TechQA subset is
derived from the IBM TechQA dataset (CDLA-Sharing-1.0). Verify the
current upstream license before redistributing the downloaded fixture.

Usage:

    # Offline (default — uses the synthetic fixture committed to the repo)
    python tools/eval/ragbench_runner.py

    # Download real RAGBench TechQA (50 queries) one-time:
    python tools/eval/ragbench_loader.py download \\
        --output data/eval/golden/ragbench_techqa.jsonl --n 50
    python tools/eval/ragbench_runner.py \\
        --fixture data/eval/golden/ragbench_techqa.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class _Row:
    query_id: str
    query: str
    relevant_passage_ids: list[str]
    passages: list[dict[str, str]]


def load_local(path: Path) -> list[_Row]:
    """Read JSONL fixture in the schema produced by ``download_techqa``."""
    rows: list[_Row] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            rows.append(
                _Row(
                    query_id=str(obj["query_id"]),
                    query=str(obj["query"]),
                    relevant_passage_ids=[str(x) for x in obj["relevant_passage_ids"]],
                    passages=[{"id": str(p["id"]), "text": str(p["text"])} for p in obj["passages"]],
                )
            )
    return rows


def download_techqa(out_path: Path, *, n: int = 50) -> int:
    """Download RAGBench TechQA from HuggingFace and write JSONL.

    Returns the number of rows written. Raises ``RuntimeError`` if
    ``datasets`` is not installed — never silently falls back so the
    operator gets a clear remediation step.
    """
    try:
        from datasets import load_dataset  # noqa: PLC0415
    except ImportError as exc:
        raise RuntimeError(
            "The datasets package is required to download RAGBench. "
            "Install it with `pip install datasets`, or use the "
            "synthetic fixture at "
            "data/eval/golden/ragbench_techqa_synthetic.jsonl."
        ) from exc

    # RAGBench publishes per-domain configs; ``techqa`` is the customer-support
    # subset Sarkar's blog evaluates. ``test`` split is the canonical eval
    # partition.
    ds = load_dataset("rungalileo/ragbench", "techqa", split="test")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    written = 0
    with out_path.open("w", encoding="utf-8") as f:
        for i, row in enumerate(ds):
            if written >= n:
                break
            # RAGBench schema fields (verified against arxiv 2407.11005):
            #   ``id``, ``question``, ``documents`` (list[str]),
            #   ``relevant_doc_ids`` or ``ground_truth_doc_ids`` (list[int]).
            # Schema can drift between HF dataset revisions; we defensively
            # check both common field names.
            documents = row.get("documents") or row.get("passages") or []
            if not documents:
                continue
            gold = (
                row.get("relevant_doc_ids")
                or row.get("ground_truth_doc_ids")
                or row.get("relevant_passage_ids")
                or []
            )
            if not gold:
                continue
            # Synthesise stable passage ids per row.
            passage_ids = [f"p{i:03d}_{j:02d}" for j in range(len(documents))]
            relevant_ids = [passage_ids[idx] for idx in gold if 0 <= idx < len(documents)]
            if not relevant_ids:
                continue
            payload = {
                "query_id": str(row.get("id") or f"q{i:03d}"),
                "query": str(row.get("question") or ""),
                "relevant_passage_ids": relevant_ids,
                "passages": [
                    {"id": pid, "text": str(text)} for pid, text in zip(passage_ids, documents, strict=False)
                ],
            }
            f.write(json.dumps(payload, ensure_ascii=False))
            f.write("\n")
            written += 1
    return written


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_dl = sub.add_parser("download", help="Download RAGBench TechQA from HuggingFace")
    p_dl.add_argument("--output", type=Path, required=True)
    p_dl.add_argument("--n", type=int, default=50)

    p_ck = sub.add_parser("check", help="Validate a local JSONL fixture")
    p_ck.add_argument("--path", type=Path, required=True)

    args = parser.parse_args(argv)

    if args.cmd == "download":
        n = download_techqa(args.output, n=args.n)
        print(f"Wrote {n} rows to {args.output.as_posix()}")
        return 0

    if args.cmd == "check":
        rows = load_local(args.path)
        print(f"Loaded {len(rows)} rows from {args.path.as_posix()}")
        bad = [r for r in rows if not r.relevant_passage_ids]
        if bad:
            print(f"WARNING: {len(bad)} rows have no relevant_passage_ids", file=sys.stderr)
            return 1
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(_main())
