"""CI gate: REQ Coverage Contracts (Pact-style verifier).

Wraps ``tools.runtime_evidence.contract_verifier`` for invocation by
``ops_scripts/ci/run_contract_gates.py``.

Exit codes
----------
0 — all non-deprecated contracts PASS, or are EMPTY+experimental.
1 — at least one contract FAIL or STALE (or EMPTY-stable).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow direct script invocation (`python ops_scripts/ci/check_req_coverage_contracts.py`)
# in addition to module invocation. Mirrors the sys.path shim used in
# tools/requirements/emit_proof_bundles.py and update_pilot_ledger.py.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.runtime_evidence.contract_verifier import main as verifier_main


def main(argv: list[str] | None = None) -> int:
    return verifier_main(argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
