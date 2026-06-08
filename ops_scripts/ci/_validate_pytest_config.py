#!/usr/bin/env python3
"""
Pytest Config SSOT Validation Gate
Checks consistency between pytest.ini and pyproject.toml

Usage:
    python _validate_pytest_config.py [--strict] [--fix]

Exit codes:
    0: Configs synchronized
    1: Critical drift (blocks CI in --strict mode)
    2: Warning drift (logs only, allows CI)
"""

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import tomllib


@dataclass
class PytestConfig:
    source: str
    addopts: str
    testpaths: list
    markers: list
    timeout: int | None = None
    n_workers: str | None = None
    dist_mode: str | None = None


def parse_pytest_ini(path: Path) -> PytestConfig:
    """Parse pytest.ini file."""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"could not read {path}: {exc}") from exc

    # Extract addopts
    addopts_match = re.search(r"addopts\s*=\s*(.+?)(?:\n\w|\Z)", content, re.DOTALL)
    addopts = addopts_match.group(1).strip() if addopts_match else ""

    # Extract testpaths
    testpaths_match = re.search(r"testpaths\s*=\s*(.+)", content)
    testpaths = testpaths_match.group(1).strip().split() if testpaths_match else []

    # Extract markers
    markers_section = re.search(r"markers\s*=\s*\n((?:\s+.+\n)+)", content)
    markers = []
    if markers_section:
        for line in markers_section.group(1).strip().split("\n"):
            if ":" in line:
                marker_name = line.strip().split(":")[0].strip()
                markers.append(marker_name)

    # Parse xdist options
    n_workers = "auto" if "-n auto" in addopts else None
    if not n_workers:
        n_match = re.search(r"-n\s+(\d+)", addopts)
        if n_match:
            n_workers = n_match.group(1)

    dist_match = re.search(r"--dist=(\w+)", addopts)
    dist_mode = dist_match.group(1) if dist_match else None

    # Parse timeout
    timeout_match = re.search(r"--timeout=(\d+)", addopts)
    timeout = int(timeout_match.group(1)) if timeout_match else None

    return PytestConfig(
        source="pytest.ini",
        addopts=addopts,
        testpaths=testpaths,
        markers=markers,
        timeout=timeout,
        n_workers=n_workers,
        dist_mode=dist_mode,
    )


def parse_pyproject_toml(path: Path) -> PytestConfig:
    """Parse pyproject.toml file."""
    try:
        content = path.read_bytes()
        data = tomllib.loads(content.decode("utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise RuntimeError(f"could not parse {path}: {exc}") from exc

    pytest_options = data.get("tool", {}).get("pytest", {}).get("ini_options", {})

    addopts = pytest_options.get("addopts", "")
    testpaths = pytest_options.get("testpaths", [])
    markers_raw = pytest_options.get("markers", [])

    # Parse markers from list format
    markers = []
    for marker in markers_raw:
        if ":" in marker:
            markers.append(marker.split(":")[0].strip())

    # Parse xdist options
    n_workers = "auto" if "-n auto" in addopts else None
    if not n_workers:
        n_match = re.search(r"-n\s+(\d+)", addopts)
        if n_match:
            n_workers = n_match.group(1)

    dist_match = re.search(r"--dist=(\w+)", addopts)
    dist_mode = dist_match.group(1) if dist_match else None

    timeout_match = re.search(r"--timeout=(\d+)", addopts)
    timeout = int(timeout_match.group(1)) if timeout_match else None

    return PytestConfig(
        source="pyproject.toml",
        addopts=addopts,
        testpaths=testpaths,
        markers=markers,
        timeout=timeout,
        n_workers=n_workers,
        dist_mode=dist_mode,
    )


def validate_configs(pytest_ini: PytestConfig, pyproject: PytestConfig, strict: bool = False) -> int:
    """Validate config consistency. Returns exit code."""
    errors = []
    warnings = []

    # Critical: xdist parallel execution + dist mode.
    # xdist is INTENTIONALLY kept out of pytest.ini (it breaks IDE test
    # explorers — see the pytest.ini header comment). pyproject.toml is the
    # canonical CI source for parallelism, so validate it there. If pytest.ini
    # *does* pin these, they must not conflict with pyproject.
    if not pyproject.n_workers:
        errors.append("CRITICAL: pyproject.toml missing -n <workers> (CI parallel execution)")
    elif pytest_ini.n_workers and pytest_ini.n_workers != pyproject.n_workers:
        warnings.append(
            f"WORKERS MISMATCH: pytest.ini={pytest_ini.n_workers}, pyproject.toml={pyproject.n_workers}"
        )

    if not pyproject.dist_mode:
        errors.append("CRITICAL: pyproject.toml missing --dist=<mode> (distribution mode)")
    elif pytest_ini.dist_mode and pytest_ini.dist_mode != pyproject.dist_mode:
        warnings.append(
            f"DIST MISMATCH: pytest.ini={pytest_ini.dist_mode}, pyproject.toml={pyproject.dist_mode}"
        )

    # High: timeout
    if not pytest_ini.timeout:
        errors.append("CRITICAL: pytest.ini missing --timeout (test timeout protection)")
    elif pyproject.timeout and pytest_ini.timeout < pyproject.timeout:
        errors.append(
            f"TIMEOUT ERROR: pytest.ini timeout ({pytest_ini.timeout}) < pyproject.toml ({pyproject.timeout})"
        )

    # High: serial marker (required for stateful tests)
    if "serial" not in pytest_ini.markers:
        errors.append("CRITICAL: pytest.ini missing 'serial' marker (required for Redis state tests)")

    # Medium: marker superset check
    pyproject_marker_set = set(pyproject.markers)
    pytest_marker_set = set(pytest_ini.markers)
    missing_in_pytest = pyproject_marker_set - pytest_marker_set
    if missing_in_pytest:
        warnings.append(f"MARKERS: pyproject.toml has extra markers not in pytest.ini: {missing_in_pytest}")

    # Medium: testpaths
    if set(pytest_ini.testpaths) != set(pyproject.testpaths):
        warnings.append(
            f"TESTPATHS MISMATCH: pytest.ini={pytest_ini.testpaths}, pyproject.toml={pyproject.testpaths}"
        )

    # Report results
    print("=" * 60)
    print("PYTEST CONFIG SSOT VALIDATION")
    print("=" * 60)

    print("\n📄 pytest.ini:")
    print(
        "   Workers: "
        + (pytest_ini.n_workers or "NOT SET")
        + " | Dist: "
        + (pytest_ini.dist_mode or "NOT SET")
        + " | Timeout: "
        + str(pytest_ini.timeout or "NOT SET")
    )
    print("   Markers: " + str(len(pytest_ini.markers)) + " defined")

    print("\n📄 pyproject.toml:")
    print(
        "   Workers: "
        + (pyproject.n_workers or "NOT SET")
        + " | Dist: "
        + (pyproject.dist_mode or "NOT SET")
        + " | Timeout: "
        + str(pyproject.timeout or "NOT SET")
    )
    print("   Markers: " + str(len(pyproject.markers)) + " defined")

    if errors:
        print("\n❌ ERRORS (" + str(len(errors)) + "):")
        for err in errors:
            print("   " + err)

    if warnings:
        print("\n⚠️ WARNINGS (" + str(len(warnings)) + "):")
        for warn in warnings:
            print("   " + warn)

    if not errors and not warnings:
        print("\n✅ Configs synchronized - no drift detected")
        return 0

    if errors:
        print("\n⛔ CRITICAL DRIFT DETECTED - CI BLOCKED")
        return 1

    if warnings and strict:
        print("\n⛔ WARNINGS IN STRICT MODE - CI BLOCKED")
        return 1

    print("\n⚠️ WARNINGS ONLY - CI ALLOWED")
    return 2


def fix_configs(pytest_ini_path: Path, _pyproject_path: Path) -> bool:
    """Auto-fix critical config drift. Returns True if changes made."""
    try:
        content = pytest_ini_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"could not read {pytest_ini_path}: {exc}") from exc
    changes_made = False

    # NOTE: xdist (-n / --dist) is INTENTIONALLY not auto-added to pytest.ini —
    # it breaks IDE test explorers (see pytest.ini header). The canonical CI
    # parallelism lives in pyproject.toml; validate_configs checks it there. We
    # still auto-add a missing --timeout and the serial marker.
    if "--timeout" not in content:
        content = re.sub(r"(addopts\s*=\s*)", r"\1--timeout=180 ", content)
        changes_made = True
        print("🔧 AUTO-FIX: Added --timeout=180 to addopts")

    # Fix missing serial marker
    if "serial:" not in content:
        # Find markers section and append
        content = re.sub(
            r"(markers\s*=\s*\n)",
            r"\1    serial: Tests that must run serially (shared Redis state, not xdist-safe)\n",
            content,
        )
        changes_made = True
        print("🔧 AUTO-FIX: Added 'serial' marker definition")

    if changes_made:
        try:
            pytest_ini_path.write_text(content, encoding="utf-8")
        except OSError as exc:
            raise RuntimeError(f"could not write {pytest_ini_path}: {exc}") from exc
        print(f"✅ Written fixes to {pytest_ini_path}")

    return changes_made


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Validate pytest config SSOT")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--fix", action="store_true", help="Auto-fix critical drift")
    args = parser.parse_args()

    root = Path.cwd()
    pytest_ini_path = root / "pytest.ini"
    pyproject_path = root / "pyproject.toml"

    if not pytest_ini_path.exists() or not pyproject_path.exists():
        repo_root = Path(__file__).resolve().parents[2]
        repo_pytest = repo_root / "pytest.ini"
        repo_pyproject = repo_root / "pyproject.toml"
        if repo_pytest.exists() and repo_pyproject.exists():
            root = repo_root
            pytest_ini_path = repo_pytest
            pyproject_path = repo_pyproject

    if not pytest_ini_path.exists():
        print(f"❌ File not found: {pytest_ini_path}")
        return 1

    if not pyproject_path.exists():
        print(f"❌ File not found: {pyproject_path}")
        return 1

    try:
        pytest_ini = parse_pytest_ini(pytest_ini_path)
        pyproject = parse_pyproject_toml(pyproject_path)

        if args.fix:
            if fix_configs(pytest_ini_path, pyproject_path):
                pytest_ini = parse_pytest_ini(pytest_ini_path)
    except RuntimeError as exc:
        print(f"❌ {exc}")
        return 1

    return validate_configs(pytest_ini, pyproject, strict=args.strict)


if __name__ == "__main__":
    sys.exit(main())
