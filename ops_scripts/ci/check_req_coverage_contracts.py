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

from tools.runtime_evidence.contract_verifier import main as verifier_main


def main(argv: list[str] | None = None) -> int:
    return verifier_main(argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
