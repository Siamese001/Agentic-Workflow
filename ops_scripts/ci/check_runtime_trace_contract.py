#!/usr/bin/env python3
"""Runtime trace contract CI gate.

Invokes ``scripts/proof/run_runtime_trace_proof.py`` for one or more canary
contracts and surfaces violations in the standard CI gate format.

Exit codes:
    0  All canary contracts passed.
    1  One or more canary contracts produced violations (fail-closed).
    2  Infrastructure error (contract load failed, materialization failed,
       missing artefact, etc).

Usage::

    python ops_scripts/ci/check_runtime_trace_contract.py
    python ops_scripts/ci/check_runtime_trace_contract.py --contract canary.lic.v1
    python ops_scripts/ci/check_runtime_trace_contract.py --json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

PROOF_SCRIPT = REPO_ROOT / "scripts" / "proof" / "run_runtime_trace_proof.py"

# Default contracts the gate must validate. Add new canary contracts here as
# they ship under ``config/runtime_trace/contracts/``.
DEFAULT_CONTRACTS: tuple[str, ...] = ("canary.lic.v1",)

DEFAULT_TIMEOUT_S = 60


def run_proof_for_contract(
    contract_id: str, *, timeout: int = DEFAULT_TIMEOUT_S
) -> dict[str, Any]:
    """Invoke the proof script for ``contract_id`` and return the parsed result.

    Returns a dict with at minimum::

        {
            "contract_id": str,
            "ok": bool,
            "exit_code": int,
            "violations": [...],
            "error": str | None,
        }
    """
    cmd = [
        sys.executable,
        str(PROOF_SCRIPT),
        "--contract",
        contract_id,
        "--json",
    ]
    try:
        proc = subprocess.run(  # noqa: S603 — fixed argv, shell=False
            cmd,
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "contract_id": contract_id,
            "ok": False,
            "exit_code": 124,
            "violations": [],
            "error": f"timeout after {timeout}s",
        }
    except (OSError, ValueError) as exc:
        return {
            "contract_id": contract_id,
            "ok": False,
            "exit_code": 2,
            "violations": [],
            "error": f"subprocess_failed: {type(exc).__name__}: {exc}",
        }

    out = proc.stdout.strip()
    if not out:
        return {
            "contract_id": contract_id,
            "ok": False,
            "exit_code": proc.returncode,
            "violations": [],
            "error": f"empty_proof_output stderr={proc.stderr.strip()[:240]!r}",
        }
    try:
        parsed = json.loads(out)
    except json.JSONDecodeError as exc:
        return {
            "contract_id": contract_id,
            "ok": False,
            "exit_code": proc.returncode,
            "violations": [],
            "error": f"proof_output_not_json: {exc}; stdout={out[:240]!r}",
        }

    parsed["exit_code"] = proc.returncode
    return parsed


def _print_human(results: list[dict[str, Any]]) -> None:
    print("🔍 Runtime trace contract gate")
    for r in results:
        cid = r["contract_id"]
        if r.get("error"):
            print(f"  ⚠️  {cid}: INFRA-ERROR — {r['error']}")
        elif r["ok"]:
            print(f"  ✅ {cid}: PASS")
        else:
            n = len(r.get("violations", []))
            print(f"  ❌ {cid}: FAIL ({n} violation{'s' if n != 1 else ''})")
            for v in r.get("violations", [])[:10]:
                span = v.get("span_name") or "-"
                print(f"      [{v['kind']}] {span}: {v['detail']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--contract",
        action="append",
        help="Canary contract id (may be repeated). Default: all known contracts.",
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON to stdout."
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT_S,
        help=f"Per-contract timeout in seconds (default: {DEFAULT_TIMEOUT_S}).",
    )
    args = parser.parse_args(argv)

    if not PROOF_SCRIPT.is_file():
        print(f"❌ proof script missing: {PROOF_SCRIPT}", file=sys.stderr)
        return 2

    contracts = tuple(args.contract) if args.contract else DEFAULT_CONTRACTS
    results = [
        run_proof_for_contract(c, timeout=args.timeout) for c in contracts
    ]

    if args.json:
        print(json.dumps({"results": results}, indent=2, sort_keys=True))
    else:
        _print_human(results)

    if any(r.get("error") for r in results):
        return 2
    return 0 if all(r["ok"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
