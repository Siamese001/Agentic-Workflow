"""Classify each ``ops_scripts/ci/check_*.py`` gate by where it is wired.

Read-only audit for the enforcement-surface consolidation plan
(``plans/enforcement-surface-consolidation-d8b3f6.md``, W1.2). For every gate it records whether the
basename is referenced in:

- the contract-gate registry (``run_contract_gates.py`` + sibling registry helpers),
- ``.pre-commit-config.yaml``,
- ``.github/workflows/*``,
- ``tests/``,

and assigns a classification: ``REGISTRY`` / ``PRECOMMIT`` / ``WORKFLOW`` / ``TEST_ONLY`` / ``ORPHANED``.

``ORPHANED`` (referenced by none of registry/pre-commit/workflow/tests) is the **only** set the
consolidation plan's W4 may retire — and only after this report proves it. This makes the
"175 uncalled-by-registry overcounts dead" guardrail concrete: a gate uncalled by the registry but
present in pre-commit or a workflow is NOT dead.

Usage:
    python tools/governance/classify_gate_wiring.py [--out docs/reports/governance/gate_wiring_classification.json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CI_DIR = REPO_ROOT / "ops_scripts" / "ci"

# Make ``tools.progress_display`` importable when run as a script (sys.path[0] is this file's dir).
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from tools.progress_display import ProgressReporter
except ImportError:  # optional progress dep absent -> degrade to no-op bar (precise, no broad-except)
    ProgressReporter = None  # type: ignore[assignment]

_GATE_RE = re.compile(r"check_[a-z0-9_]+\.py")


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except (OSError, ValueError):
        return ""


def _basenames(text: str) -> set[str]:
    return set(_GATE_RE.findall(text))


def _registry_refs() -> set[str]:
    corpus = "\n".join(
        _read(CI_DIR / name)
        for name in ("run_contract_gates.py", "_adg_ci_gates.py", "_governance_paths.py")
    )
    return _basenames(corpus)


def _workflow_refs() -> set[str]:
    wf = REPO_ROOT / ".github" / "workflows"
    if not wf.is_dir():
        return set()
    return _basenames("\n".join(_read(p) for p in sorted(wf.glob("*.y*ml"))))


def _test_refs() -> set[str]:
    """Scan tests/ for gate-basename references (progress-reported, may iterate >10 files)."""
    refs: set[str] = set()
    tdir = REPO_ROOT / "tests"
    if not tdir.is_dir():
        return refs
    files = sorted(tdir.rglob("*.py"))
    reporter = ProgressReporter(total=len(files), label="Scanning tests") if ProgressReporter else None
    for path in files:
        refs |= _basenames(_read(path))
        if reporter:
            reporter.update()
    if reporter:
        reporter.done()
    return refs


def classify() -> dict:
    gates = sorted(p.name for p in CI_DIR.glob("check_*.py"))
    registry = _registry_refs()
    precommit = _basenames(_read(REPO_ROOT / ".pre-commit-config.yaml"))
    workflow = _workflow_refs()
    tests = _test_refs()

    result: dict[str, dict] = {}
    counts = {"REGISTRY": 0, "PRECOMMIT": 0, "WORKFLOW": 0, "TEST_ONLY": 0, "ORPHANED": 0}
    reporter = ProgressReporter(total=len(gates), label="Classifying gates") if ProgressReporter else None
    for name in gates:
        flags = {
            "registry": name in registry,
            "precommit": name in precommit,
            "workflow": name in workflow,
            "tests": name in tests,
        }
        if flags["registry"]:
            cls = "REGISTRY"
        elif flags["precommit"]:
            cls = "PRECOMMIT"
        elif flags["workflow"]:
            cls = "WORKFLOW"
        elif flags["tests"]:
            cls = "TEST_ONLY"
        else:
            cls = "ORPHANED"
        counts[cls] += 1
        result[name] = {**flags, "classification": cls}
        if reporter:
            reporter.update()
    if reporter:
        reporter.done()

    return {"total_gates": len(gates), "counts": counts, "gates": result}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Classify CI gate wiring (read-only audit)")
    parser.add_argument(
        "--out",
        default="docs/reports/governance/gate_wiring_classification.json",
        help="Output JSON path (repo-relative)",
    )
    args = parser.parse_args(argv)

    payload = classify()

    out = (REPO_ROOT / args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print(f"[classify_gate_wiring] {payload['total_gates']} gates -> {args.out}")
    for key, val in payload["counts"].items():
        print(f"  {key:<10} {val}")
    print(
        "  (ORPHANED = retirable by W4 after review; PRECOMMIT/WORKFLOW prove "
        "'uncalled-by-registry' != dead)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
