"""Pact-style verifier for REQ Coverage Contracts.

Walks ``docs/requirements/contracts/<REQ_ID>.contract.yaml`` and asserts that
each contract is satisfied by recent ledger evidence within its
``freshness_sla_days`` window.

This is the consumer-driven contract pattern (Pact). The contract YAML
declares "this REQ expects spans of shape X within N days." The verifier
queries the runtime evidence ledger and confirms the expectation is met.

Industry references
-------------------
* Pact docs — *"Contract by example: a collection of test cases describing
  concrete request/response pairs."* The contract YAMLs ARE the examples.
* OTel SemConv lifecycle — `experimental → stable → deprecated`. A REQ
  in `experimental` status MUST satisfy its contract for N consecutive
  weekly runs before promotion (enforced by the closure-lifecycle gate,
  not this verifier).

Failure semantics
-----------------
For each contract:
  * **PASS**  — ledger has matching spans within the freshness window.
  * **FAIL**  — contract expectations were violated (e.g. zero matches).
  * **STALE** — ledger has older matches but none within the window.
  * **EMPTY** — ledger has no matches at all (cold contract — typical for
    brand-new ``experimental``-status REQs that haven't run yet).

Exit codes
----------
0 — all non-deprecated contracts PASS, or are EMPTY+experimental.
1 — at least one contract FAIL or STALE.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from contextlib import closing
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:  # pyyaml is in requirements; fail-soft just in case
    import yaml as _yaml
except ImportError:  # guardian: allow-yaml-optional -- declared dep, but fail closed early with a clear message
    _yaml = None

from tools.runtime_evidence.ledger_writer import DEFAULT_LEDGER_PATH

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTRACTS_DIR = REPO_ROOT / "docs" / "requirements" / "contracts"


@dataclass
class ContractResult:
    req_id: str
    status: str  # PASS | FAIL | STALE | EMPTY
    contract_status: str  # experimental | stable | deprecated
    matches_in_window: int
    latest_observed_at: int | None
    expected_layers: set[str] = field(default_factory=set)
    expected_apps: set[str] = field(default_factory=set)
    expected_edge_kinds: set[str] = field(default_factory=set)
    observed_layers: set[str] = field(default_factory=set)
    observed_apps: set[str] = field(default_factory=set)
    observed_edge_kinds: set[str] = field(default_factory=set)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "req_id": self.req_id,
            "status": self.status,
            "contract_status": self.contract_status,
            "matches_in_window": self.matches_in_window,
            "latest_observed_at": self.latest_observed_at,
            "expected_layers": sorted(self.expected_layers),
            "expected_apps": sorted(self.expected_apps),
            "expected_edge_kinds": sorted(self.expected_edge_kinds),
            "observed_layers": sorted(self.observed_layers),
            "observed_apps": sorted(self.observed_apps),
            "observed_edge_kinds": sorted(self.observed_edge_kinds),
            "notes": list(self.notes),
        }


def load_contracts(contracts_dir: Path = DEFAULT_CONTRACTS_DIR) -> list[dict[str, Any]]:
    """Load every ``*.contract.yaml`` in the directory."""
    if _yaml is None:
        raise ImportError(
            "PyYAML is required for contract verification. "
            "Install with: pip install pyyaml"
        )
    if not contracts_dir.exists():
        return []
    contracts: list[dict[str, Any]] = []
    for path in sorted(contracts_dir.glob("*.contract.yaml")):
        with path.open(encoding="utf-8") as fh:
            data = _yaml.safe_load(fh)
        if isinstance(data, dict):
            data["__path__"] = str(path)
            contracts.append(data)
    return contracts


def verify_one(
    contract: dict[str, Any],
    *,
    ledger_path: Path = DEFAULT_LEDGER_PATH,
    now: int | None = None,
) -> ContractResult:
    """Verify a single contract against the ledger."""
    req_id = contract["req_id"]
    contract_status = contract.get("status", "experimental")
    expects = contract.get("expects_spans", {}) or {}
    expected_layers = set(expects.get("layers") or [])
    expected_apps = set(expects.get("apps") or [])
    expected_edge_kinds = set(expects.get("edge_kinds") or [])
    min_count = int(expects.get("min_count_per_run", 1))
    sla_days = int(contract.get("freshness_sla_days", 7))
    must_carry_trace_id = bool(expects.get("must_carry_trace_id", False))

    result = ContractResult(
        req_id=req_id,
        status="EMPTY",
        contract_status=contract_status,
        matches_in_window=0,
        latest_observed_at=None,
        expected_layers=expected_layers,
        expected_apps=expected_apps,
        expected_edge_kinds=expected_edge_kinds,
    )

    if not ledger_path.exists():
        result.notes.append(f"ledger not found at {ledger_path}")
        return result

    now_ts = now or int(time.time())
    cutoff = now_ts - sla_days * 24 * 3600

    with closing(sqlite3.connect(ledger_path)) as con:
        # Total matches (any layer/app) for this req
        total_row = con.execute(
            "SELECT COUNT(*), MAX(observed_at) FROM req_emission WHERE req_id = ?",
            (req_id,),
        ).fetchone()
        total_count, total_latest = (total_row or (0, None))

        if total_count == 0:
            result.notes.append("no rows for this REQ_ID anywhere in the ledger")
            # EMPTY status — acceptable for `experimental` contracts that haven't
            # run yet, but FAIL for `stable`.
            result.status = "EMPTY"
            return result
        result.latest_observed_at = total_latest

        # Matches inside the freshness window
        window_rows = con.execute(
            """
            SELECT layer, app_id, edge_kind, trace_id
            FROM req_emission
            WHERE req_id = ? AND observed_at >= ?
            """,
            (req_id, cutoff),
        ).fetchall()

    if not window_rows:
        result.status = "STALE"
        result.notes.append(
            f"latest observation at {total_latest} is older than "
            f"{sla_days} days (cutoff={cutoff})"
        )
        return result

    result.matches_in_window = len(window_rows)
    result.observed_layers = {r[0] for r in window_rows}
    result.observed_apps = {r[1] for r in window_rows}
    result.observed_edge_kinds = {r[2] for r in window_rows}

    # Predicate checks
    failures: list[str] = []
    if expected_layers and not (expected_layers & result.observed_layers):
        failures.append(
            f"expected layers {sorted(expected_layers)} but observed "
            f"{sorted(result.observed_layers)}"
        )
    if expected_apps and not (expected_apps & result.observed_apps):
        failures.append(
            f"expected apps {sorted(expected_apps)} but observed "
            f"{sorted(result.observed_apps)}"
        )
    if expected_edge_kinds and not (expected_edge_kinds & result.observed_edge_kinds):
        failures.append(
            f"expected edge_kinds {sorted(expected_edge_kinds)} but observed "
            f"{sorted(result.observed_edge_kinds)}"
        )
    if result.matches_in_window < min_count:
        failures.append(
            f"min_count_per_run={min_count} not met (got {result.matches_in_window})"
        )
    if must_carry_trace_id and any(not r[3] for r in window_rows):
        failures.append("at least one matching span has empty trace_id")

    if failures:
        result.status = "FAIL"
        result.notes.extend(failures)
    else:
        result.status = "PASS"
    return result


def verify_all(
    contracts_dir: Path = DEFAULT_CONTRACTS_DIR,
    ledger_path: Path = DEFAULT_LEDGER_PATH,
) -> dict[str, Any]:
    """Verify every contract; return summary dict suitable for CI."""
    contracts = load_contracts(contracts_dir)
    results = [verify_one(c, ledger_path=ledger_path) for c in contracts]
    by_status: dict[str, int] = {}
    for r in results:
        by_status[r.status] = by_status.get(r.status, 0) + 1

    # Hard failures: FAIL on any contract; STALE on a `stable`/`deprecated`
    # contract; FAIL on a `stable` contract that's EMPTY.
    failures = [
        r for r in results
        if r.status == "FAIL"
        or (r.status == "STALE" and r.contract_status != "experimental")
        or (r.status == "EMPTY" and r.contract_status == "stable")
    ]
    return {
        "ok": not failures,
        "total": len(results),
        "by_status": by_status,
        "results": [r.to_dict() for r in results],
        "failures": [r.to_dict() for r in failures],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contracts-dir", type=Path, default=DEFAULT_CONTRACTS_DIR)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER_PATH)
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args(argv)

    summary = verify_all(args.contracts_dir, args.ledger)
    print(
        f"[contract_verifier] {summary['total']} contracts checked: "
        f"{summary['by_status']}"
    )
    for r in summary["results"]:
        marker = {
            "PASS": "[OK]  ",
            "FAIL": "[FAIL]",
            "STALE": "[STALE]",
            "EMPTY": "[EMPTY]",
        }.get(r["status"], "[?]")
        print(
            f"  {marker} {r['req_id']:<46} status={r['contract_status']:<13} "
            f"matches={r['matches_in_window']}"
        )
        for note in r.get("notes", []):
            print(f"         {note}")
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"[contract_verifier] wrote {args.json_out}")
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
