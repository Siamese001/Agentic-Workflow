"""Run the fail-closed apps_rg Anthropic live cache probe and write its receipt."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from apps_rg.runtime.providers.anthropic_cache_live_probe import run_live_cache_probe


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="Receipt JSON path")
    parser.add_argument(
        "--model",
        default=os.environ.get("APPS_RG_ANTHROPIC_LIVE_CACHE_MODEL", "claude-sonnet-5"),
    )
    parser.add_argument("--timeout-seconds", type=float, default=90.0)
    return parser


def main() -> int:
    args = _parser().parse_args()
    api_key = str(os.environ.get("ANTHROPIC_API_KEY") or "").strip()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if not api_key:
        receipt = {
            "schema": "apps_rg_anthropic_cache_live_probe_v1",
            "status": "SKIPPED_SECRET_UNAVAILABLE",
            "pass": False,
            "model": args.model,
            "promotion_reasons": ["ANTHROPIC_API_KEY unavailable"],
        }
        output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(receipt, indent=2))
        return 3

    price_raw = str(os.environ.get("APPS_RG_ANTHROPIC_INPUT_USD_PER_MILLION") or "").strip()
    try:
        price = float(price_raw) if price_raw else None
    except ValueError:
        price = None
    receipt = run_live_cache_probe(
        api_key=api_key,
        model=args.model,
        timeout_seconds=args.timeout_seconds,
        input_usd_per_million=price,
    )
    output.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in receipt.items() if key != "calls"}, indent=2))
    return 0 if receipt.get("pass") else 2


if __name__ == "__main__":
    raise SystemExit(main())
