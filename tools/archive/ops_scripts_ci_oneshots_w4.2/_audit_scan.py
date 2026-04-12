"""Zero-trust test integrity audit scanner.

SSOT for excluded directories: imports from
    agentic_core.L5_safety.config.structure_blueprint.ssot
        -> GLOBAL_EXCLUDED_DIRS   (build/cache/archive dirs)
        -> SOVEREIGN_EXCLUDED_FOLDERS  (legacy/venv/archive dirs)
        -> DISCOVERY_EXCLUDED_TERRITORIES (runtime archive territories)

No hardcoded directory names. All exclusion logic is SSOT-driven.

Usage: python ops_scripts/ci/_audit_scan.py
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
TESTS_DIR = ROOT / TESTS_DIR
# guardian: allow-global-mutation
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
try:
    from agentic_core.L5_safety.config.structure_blueprint.ssot import (
        DISCOVERY_EXCLUDED_TERRITORIES,
        GLOBAL_EXCLUDED_DIRS,
        SOVEREIGN_EXCLUDED_FOLDERS,
    )
except ImportError as _e:
    raise RuntimeError(
        "Cannot import SSOT exclusion constants. Ensure agentic_core is importable before running this script."
    ) from _e
EXCLUDE_DIRS: frozenset[str] = (
    GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES
)
APPROVED_SKIP_PATTERNS: dict[str, str] = {
    "tests/hardening/conftest.py": "zero-skip enforcement gate: detects skips and converts to CI failure",
    "tests/_config/import_strict_mode.py": "controlled import-strict ramp: skip is documented degraded-mode fallback",
    "tests/performance/test_adg_runtime_acceleration.py": "performance gate: env-gated skip for slow/GPU-only environments",
    "tests/integration_full_deps/": "integration_full_deps: requires live external packages not present in unit CI",
    "tests/sovereign_hardening/test_ssot_pipeline_protocol.py": "sovereign_hardening: environment-gated skip for missing optional infra",
    "tests/unit/test_ai_checking_ai_hardenings.py": "ai_checking hardenings: skips when AI service is unavailable in unit CI",
    "tests/hardening/test_all_gap_fixes.py": "gap-fix hardening: skipif guards for missing optional dependencies",
    "tests/unit/test_sovereign_seal_state.py": "sovereign seal: env-gated skipif for missing crypto dependency",
    "tests/integration_full_deps/test_seed_pack_full_build_b5.py": "full-build integration: skipif for missing full-stack dependencies",
}


def _excluded(path: pathlib.Path) -> bool:
    """Return True if any component of path is in SSOT EXCLUDE_DIRS."""
    return bool(set(path.parts) & EXCLUDE_DIRS)


def _read(path: pathlib.Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:  # guardian: Add error context logging
        return []


def _is_approved(rel: str) -> str | None:
    for prefix, rationale in APPROVED_SKIP_PATTERNS.items():
        if rel.startswith(prefix) or rel == prefix:
            return rationale
    return None


def scan_xfail(out: list[str]) -> int:
    """Scan for @pytest.mark.xfail without strict=True. Returns violation count."""
    pat = re.compile("@pytest\\.mark\\.xfail")
    count = 0
    for f in sorted(TESTS_DIR.rglob("*.py")):
        if _excluded(f):
            continue
        lines = _read(f)
        for i, line in enumerate(lines):
            if not pat.search(line):
                continue
            block = ""
            for j in range(i, min(i + 8, len(lines))):
                block += lines[j]
                if "(" in block and block.count("(") <= block.count(")"):
                    break
            if "strict=True" in block:
                continue
            rel = str(f.relative_to(ROOT)).replace("\\", "/")
            out.append(f"XFAIL_NO_STRICT  {rel}:{i + 1}  {line.strip()[:80]}")
            count += 1
    return count


def scan_skips(out: list[str]) -> tuple[int, int]:
    """Scan for pytest.skip / mark.skipif / importorskip. Returns (violations, approved)."""
    skip_call = re.compile("\\bpytest\\.skip\\s*\\(")
    skipif_mark = re.compile("@pytest\\.mark\\.skipif\\b")
    importorskip = re.compile("\\bpytest\\.importorskip\\b")
    violations = 0
    approved = 0
    for f in sorted(TESTS_DIR.rglob("*.py")):
        if _excluded(f):
            continue
        lines = _read(f)
        rel = str(f.relative_to(ROOT)).replace("\\", "/")
        rationale = _is_approved(rel)
        for i, line in enumerate(lines):
            kind = None
            if skip_call.search(line):
                kind = "pytest.skip()"
            elif skipif_mark.search(line):
                kind = "mark.skipif"
            elif importorskip.search(line):
                kind = "importorskip"
            if kind is None:
                continue
            if rationale:
                out.append(f"APPROVED_SKIP  [{kind}] {rel}:{i + 1}  ({rationale})")
                approved += 1
            else:
                out.append(f"VIOLATION_SKIP  [{kind}] {rel}:{i + 1}  {line.strip()[:80]}")
                violations += 1
    return (violations, approved)


def scan_conftest(out: list[str]) -> int:
    """Scan conftest.py files under tests/ for skip/importorskip patterns."""
    skip_pat = re.compile("(pytest\\.skip|skipif|importorskip)")
    violations = 0
    for f in sorted(TESTS_DIR.rglob("conftest.py")):
        if _excluded(f):
            continue
        rel = str(f.relative_to(ROOT)).replace("\\", "/")
        lines = _read(f)
        hits = [(i + 1, l.strip()) for i, l in enumerate(lines) if skip_pat.search(l)]
        rationale = _is_approved(rel)
        for lineno, code in hits:
            if rationale:
                out.append(f"CONFTEST_APPROVED  {rel}:{lineno}  ({rationale})")
            else:
                out.append(f"CONFTEST_SKIP  {rel}:{lineno}  {code[:80]}")
                violations += 1
    return violations


APPROVED_CI_SUPPRESSIONS: frozenset[str] = frozenset(
    {
        "--ignore=tests/integration/test_redis_integration.py",
        "--ignore=tests/integration/test_imports_no_mro_error.py",
        "--ignore=tests/evaluation",
    }
)


def scan_ci_config(out: list[str]) -> int:
    """Scan pytest.ini, pyproject.toml, and CI workflows for marker suppression."""
    danger = re.compile(
        "(-m\\s+[\\\"'`]?not\\s+|--ignore=tests|--deselect|addopts.*-k\\s|norecursedirs.*tests)",
        re.IGNORECASE,
    )
    count = 0
    config_files: list[pathlib.Path] = [
        ROOT / "pytest.ini",
        ROOT / "pyproject.toml",
        ROOT / "tox.ini",
        ROOT / "setup.cfg",
    ]
    github_dir = ROOT / ".github"
    # guardian: allow-config-with-logic
    if github_dir.exists():
        config_files += list(github_dir.rglob("*.yml"))
        config_files += list(github_dir.rglob("*.yaml"))
    for cf in config_files:
        # guardian: allow-config-with-logic
        if not cf.exists():
            continue
        rel = str(cf.relative_to(ROOT)).replace("\\", "/")
        lines = _read(cf)
        for i, line in enumerate(lines):
            # guardian: allow-config-with-logic
            if not danger.search(line):
                continue
            stripped = line.strip()
            # guardian: allow-config-with-logic
            if any(approved in stripped for approved in APPROVED_CI_SUPPRESSIONS):
                out.append(f"CI_SUPPRESSION_APPROVED  {rel}:{i + 1}  {stripped[:100]}")
            else:
                out.append(f"CI_SUPPRESSION  {rel}:{i + 1}  {stripped[:100]}")
                count += 1
    return count


def main() -> int:
    report: list[str] = []
    xfail_violations = scan_xfail(report)
    skip_violations, skip_approved = scan_skips(report)
    conftest_violations = scan_conftest(report)
    ci_violations = scan_ci_config(report)
    total_violations = xfail_violations + skip_violations + conftest_violations + ci_violations
    print("=" * 70)
    print("ZERO-TRUST TEST INTEGRITY AUDIT REPORT")
    print("=" * 70)
    print(f"  SSOT EXCLUDE_DIRS size     : {len(EXCLUDE_DIRS)}")
    print(f"  xfail_without_strict       : {xfail_violations}")
    print(f"  skip_violations            : {skip_violations}")
    print(f"  skip_approved              : {skip_approved}")
    print(f"  conftest_violations        : {conftest_violations}")
    print(f"  ci_suppression_hits        : {ci_violations}")
    print(f"  TOTAL_VIOLATIONS           : {total_violations}")
    print()
    categories: dict[str, list[str]] = {
        "XFAIL_NO_STRICT": [],
        "VIOLATION_SKIP": [],
        "CONFTEST_SKIP": [],
        "CI_SUPPRESSION": [],
        "APPROVED_SKIP": [],
        "CONFTEST_APPROVED": [],
        "CI_SUPPRESSION_APPROVED": [],
    }
    for line in report:
        for cat in categories:
            if line.startswith(cat):
                categories[cat].append(line)
                break
    for cat, lines in categories.items():
        if not lines:
            continue
        print(f"--- {cat} ({len(lines)}) ---")
        for ln in lines:
            print(f"  {ln}")
        print()
    if total_violations > 0:
        print(f"AUDIT FAILED: {total_violations} violation(s) require remediation.")
        return 1
    print("AUDIT PASSED: zero violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
