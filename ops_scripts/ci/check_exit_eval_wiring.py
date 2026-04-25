"""CI gate: exit_eval wiring completeness.

Enforces that the evaluation framework stays internally consistent:

1. Every YAML rubric under ``config/exit_eval_rubrics/`` loads cleanly
   through ``agentic_core.L3_orchestration.exit_eval.rubric.load_rubric``.
2. Every rubric with gate id ``X1[A-G]`` has a corresponding ADR under
   ``docs/architecture/adr/`` (pattern ``ADR-NNN-x1<letter>-*.md``).
3. Every category declared in ``tools.exit_eval.run_x1f_probes.CATEGORY_DETECTORS``
   has a probe file at ``data/eval/golden/adversarial/<category>/probes.jsonl``
   with ≥20 entries (H4.2).
4. Every rubric gate has a test file at
   ``tests/agentic_core/L3_orchestration/exit_eval/test_*.py``
   that at least references the gate id as a string literal.

Exit codes:
    0 — all wiring valid (or the checked directories are absent).
    1 — one or more violations.
    2 — infrastructure error (e.g., rubric load fails with a bug in the
        loader itself, separate from a bad YAML).

Run:
    python ops_scripts/ci/check_exit_eval_wiring.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
RUBRIC_DIR = REPO_ROOT / "config" / "exit_eval_rubrics"
ADR_DIR = REPO_ROOT / "docs" / "architecture" / "adr"
PROBE_DIR = REPO_ROOT / "data" / "eval" / "golden" / "adversarial"
TEST_DIR = REPO_ROOT / "tests" / "agentic_core" / "L3_orchestration" / "exit_eval"


def _load_rubrics() -> tuple[dict[str, Path], list[str]]:
    from agentic_core.L3_orchestration.exit_eval.rubric import (  # local import to isolate infra errors
        RubricError,
        load_rubric,
    )

    errors: list[str] = []
    gate_to_path: dict[str, Path] = {}
    if not RUBRIC_DIR.exists():
        return gate_to_path, errors
    for path in sorted(RUBRIC_DIR.glob("*.yaml")):
        # Leading-underscore files are SSOT/config artifacts that live alongside
        # the rubrics but do not themselves describe a gate (e.g. _versions.yaml
        # added 2026-04-25 per runtime-gate-coverage-hardening-7e3f1a). Skip them
        # so the wiring check only operates on real rubric files.
        if path.name.startswith("_"):
            continue
        try:
            rubric = load_rubric(path)
        except RubricError as exc:
            errors.append(f"{path.name}: failed to load — {exc}")
            continue
        gate_to_path[rubric.gate] = path
    return gate_to_path, errors


def _check_adr_for_gate(gate: str) -> str | None:
    """Return None if an ADR for the gate exists; error string otherwise."""
    suffix = gate[-1].lower()  # X1E → e
    # Structural gates X1A/X1B/X1C/X1D are covered by the runtime HITL family
    # (ADR-023) rather than dedicated ADRs; only X1E, X1F, X1G require one.
    if gate not in {"X1E", "X1F", "X1G"}:
        return None
    pattern = re.compile(rf"ADR-\d+-x1{suffix}-.*\.md$", re.IGNORECASE)
    if not ADR_DIR.exists():
        return f"{gate}: ADR dir missing at {ADR_DIR}"
    for candidate in ADR_DIR.iterdir():
        if pattern.search(candidate.name):
            return None
    return f"{gate}: no ADR matching ADR-NNN-x1{suffix}-*.md under {ADR_DIR}"


def _check_probe_coverage() -> list[str]:
    """Each category routed in run_x1f_probes has ≥20 probe lines."""
    errors: list[str] = []
    # Avoid importing run_x1f_probes at module import time so wiring-check
    # failures don't cascade into harness-side unavailability.
    try:
        from tools.exit_eval.run_x1f_probes import CATEGORY_DETECTORS  # noqa: WPS433 (local import)
    except ImportError as exc:
        errors.append(f"cannot import run_x1f_probes: {exc}")
        return errors

    if not PROBE_DIR.exists():
        errors.append(f"probe dir missing: {PROBE_DIR}")
        return errors

    for category in CATEGORY_DETECTORS:
        probe_file = PROBE_DIR / category / "probes.jsonl"
        if not probe_file.exists():
            errors.append(f"{category}: missing {probe_file}")
            continue
        # Count non-blank lines; probe harness skips blanks too.
        try:
            text = probe_file.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{category}: {exc}")
            continue
        count = sum(1 for line in text.splitlines() if line.strip())
        if count < 20:
            errors.append(f"{category}: {count} probes (<20 per ADR-053 H4.2)")
        # Sanity: each line must be a JSON object with the expected_verdict key.
        for line_no, raw in enumerate(text.splitlines(), 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except ValueError:
                errors.append(f"{category}: {probe_file.name}:{line_no}: invalid JSON")
                continue
            if not isinstance(obj, dict) or "expected_verdict" not in obj:
                errors.append(f"{category}: {probe_file.name}:{line_no}: missing expected_verdict")
    return errors


def _check_tests_for_gates(gate_ids: set[str]) -> list[str]:
    errors: list[str] = []
    if not TEST_DIR.exists():
        errors.append(f"test dir missing: {TEST_DIR}")
        return errors
    hay: list[str] = []
    for path in TEST_DIR.rglob("*.py"):
        try:
            hay.append(path.read_text(encoding="utf-8"))
        except OSError:
            continue
    combined = "\n".join(hay)
    for gate in sorted(gate_ids):
        if gate not in combined:
            errors.append(f"{gate}: no test file mentions gate id")
    return errors


def main() -> int:
    gate_to_path, rubric_errors = _load_rubrics()
    if rubric_errors:
        for err in rubric_errors:
            print(f"RUBRIC ERROR: {err}", file=sys.stderr)
        return 1

    errors: list[str] = []

    for gate in gate_to_path:
        adr_err = _check_adr_for_gate(gate)
        if adr_err:
            errors.append(adr_err)

    errors.extend(_check_probe_coverage())
    errors.extend(_check_tests_for_gates(set(gate_to_path)))

    if errors:
        print("exit_eval wiring violations:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"exit_eval wiring OK — {len(gate_to_path)} rubrics, all ADRs / probes / tests in place.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
