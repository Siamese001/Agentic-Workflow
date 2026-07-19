"""Build the pinned C0.3 assertion corpus and BGE-M3 vector generation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps_rg.fact_inventory.c03_skill_embedding_builder import (
    build_assertion_embedding_generation,
)


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--candidate-facts", type=Path, required=True)
    parser.add_argument("--base-resume", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    manifest = build_assertion_embedding_generation(
        repository_root=ROOT,
        graph_path=args.graph.resolve(),
        candidate_fact_path=args.candidate_facts.resolve(),
        base_resume_path=args.base_resume.resolve(),
        model_path=args.model_path.resolve(),
        output_dir=args.output_dir.resolve(),
        device=str(args.device),
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "manifest_sha256": manifest["manifest_sha256"],
                "assertion_count": manifest["assertion_corpus"]["assertion_count"],
                "projection": manifest["projection"],
                "runtime_proof": manifest["runtime_proof"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
