"""Executive summary demo harness — non-product; requires ``APPS_RG_ALLOW_DEMO_HARNESS=1``."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from apps_rg.runtime.non_product_proof_stamp import (
    DEMO_HARNESS_ENV,
    demo_harness_non_product_stamp,
)

DEMO_PROOF_ARTIFACT = "demo_harness_proof.json"


def run_demo_harness(*, output_dir: Path) -> dict[str, Any]:
    if __import__("os").environ.get(DEMO_HARNESS_ENV, "").strip() not in ("1", "true", "yes"):
        raise RuntimeError(
            f"{DEMO_HARNESS_ENV}=1 required for demo harness (test-only / explicit operator enable)"
        )
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    stamp = demo_harness_non_product_stamp()
    (out / DEMO_PROOF_ARTIFACT).write_text(
        json.dumps(stamp, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return stamp


def main() -> int:
    if __import__("os").environ.get(DEMO_HARNESS_ENV, "").strip() not in ("1", "true", "yes"):
        sys.stderr.write(
            f"BLOCKED: set {DEMO_HARNESS_ENV}=1 to run demo harness (non-product)\n"
        )
        return 2
    run_demo_harness(output_dir=Path.cwd())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
