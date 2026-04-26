"""Reference-pack test-contract drift gate (constitutional follow-up to §22).

Walks every ``docs/reference/**/*.md`` file looking for ``TEST REQUIREMENTS``
(or ``PTC V2 TEST REQUIREMENTS``) blocks. Each ``- test_<name>`` bullet is a
declared, normative test contract that the architecture pack promises will be
enforced at runtime.

For every declared contract, this gate searches ``tests/`` for a matching
``def test_<name>`` definition. Contracts without an implementation are
violations.

A baseline JSON at ``ops_scripts/ci/baselines/reference_test_contract_baseline.json``
grandfathers contracts that are **known missing as of baseline date**. The
baseline must shrink, never grow — any NEW contract added to a doc MUST land
with a matching test in the same commit, or be added to the baseline with
a justification (will fail review).

Exit codes:
  0  PASS  every declared contract has either an implementation or a baseline entry
  1  FAIL  one or more contracts are missing implementation AND not baselined
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from tqdm import tqdm

REPO = Path(__file__).resolve().parents[2]
REF_DIR = REPO / "docs" / "reference"
TESTS_DIR = REPO / "tests"
BASELINE = REPO / "ops_scripts" / "ci" / "baselines" / "reference_test_contract_baseline.json"

TEST_REQ_HEADER = re.compile(r"^(?:PTC V2 )?TEST REQUIREMENTS\s*$")
TEST_BULLET = re.compile(r"^-\s+(test_[a-zA-Z0-9_]+)\s*$")
DEF_PATTERN = re.compile(r"^\s*(?:async\s+)?def\s+(test_[a-zA-Z0-9_]+)\s*\(", re.MULTILINE)


def parse_test_contracts(md_path: Path) -> list[str]:
    """Extract test_* names from TEST REQUIREMENTS blocks in a markdown file."""
    contracts: list[str] = []
    in_block = False
    seen_dashes_after_header = False
    lines = md_path.read_text(encoding="utf-8", errors="replace").splitlines()
    # Wrapped with tqdm at line granularity for §16; disabled in non-TTY (CI)
    for raw in tqdm(lines, desc=f"parse:{md_path.name}", unit="ln", leave=False, disable=True):
        line = raw.rstrip()
        if TEST_REQ_HEADER.match(line):
            in_block = True
            seen_dashes_after_header = False
            continue
        if not in_block:
            continue
        # The header is followed by a dashes line, then bullets, ending at next header or blank gap
        if line.startswith("---"):
            seen_dashes_after_header = True
            continue
        if not seen_dashes_after_header:
            # Allow up to one non-dashes line before bailing
            if line.strip() == "":
                continue
            in_block = False
            continue
        m = TEST_BULLET.match(line)
        if m:
            contracts.append(m.group(1))
            continue
        # End block on next ALL-CAPS section header or non-bullet, non-blank line
        if line.strip() == "":
            continue
        if line.isupper() or re.match(r"^[A-Z][A-Z0-9 _/-]+$", line):
            in_block = False
            continue
        # Other prose ends the block
        in_block = False
    return contracts


def collect_implemented_tests() -> set[str]:
    """Scan tests/ directory for every defined test_* function name."""
    impl: set[str] = set()
    if not TESTS_DIR.exists():
        return impl
    for py in TESTS_DIR.rglob("*.py"):
        try:
            text = py.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for match in DEF_PATTERN.finditer(text):
            impl.add(match.group(1))
    return impl


def load_baseline() -> dict:
    if not BASELINE.exists():
        return {
            "_comment": (
                "Test contracts declared in docs/reference/**/TEST REQUIREMENTS blocks "
                "but not yet implemented in tests/. Must shrink monotonically."
            ),
            "baseline_date": "",
            "missing_contracts": {},
        }
    data: dict = json.loads(BASELINE.read_text(encoding="utf-8"))
    return data


def main() -> int:
    declared: dict[str, list[str]] = {}  # test_name -> [source_doc, ...]
    md_files = sorted(REF_DIR.rglob("*.md"))
    for md in tqdm(md_files, desc="Scanning reference docs", unit="file", disable=not sys.stdout.isatty()):
        try:
            rel = md.relative_to(REPO)
        except ValueError:
            rel = md.relative_to(REF_DIR)
        for name in parse_test_contracts(md):
            declared.setdefault(name, []).append(str(rel).replace("\\", "/"))

    implemented = collect_implemented_tests()
    missing = {name: docs for name, docs in declared.items() if name not in implemented}

    baseline = load_baseline()
    baselined: set[str] = set(baseline.get("missing_contracts", {}).keys())

    new_violations = sorted(set(missing.keys()) - baselined)
    resolved = sorted(baselined - set(missing.keys()))

    total_declared = len(declared)
    total_implemented = sum(1 for n in declared if n in implemented)
    total_missing = len(missing)

    print("[check_reference_test_contracts]")
    print(f"  Declared contracts:    {total_declared}")
    print(f"  Implemented:           {total_implemented}")
    print(f"  Missing (any):         {total_missing}")
    print(f"  Baselined (allowed):   {len(baselined)}")
    print(f"  NEW violations:        {len(new_violations)}")
    print(f"  Resolved since baseline: {len(resolved)}")

    if resolved:
        print()
        print("Note: the following contracts are now implemented and should be removed from baseline:")
        for r in resolved[:20]:
            print(f"  + {r}")
        if len(resolved) > 20:
            print(f"  ...and {len(resolved) - 20} more")

    if new_violations:
        print()
        print("FAIL: NEW test contracts declared without implementation:")
        for name in new_violations[:50]:
            docs = ", ".join(declared[name])
            print(f"  - {name}  (declared in: {docs})")
        if len(new_violations) > 50:
            print(f"  ...and {len(new_violations) - 50} more")
        print()
        print("Resolution options:")
        print("  1. Implement the test in tests/ matching the exact name")
        print("  2. Add to ops_scripts/ci/baselines/reference_test_contract_baseline.json")
        print("     with a justification + ETA (must be approved by reviewer)")
        return 1

    print()
    print("[check_reference_test_contracts] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
