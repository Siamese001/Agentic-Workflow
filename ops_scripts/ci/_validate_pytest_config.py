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
    content = path.read_text()

    # Extract addopts
    addopts_match = re.search(r'addopts\s*=\s*(.+?)(?:\n\w|\Z)', content, re.DOTALL)
    addopts = addopts_match.group(1).strip() if addopts_match else ""

    # Extract testpaths
    testpaths_match = re.search(r'testpaths\s*=\s*(.+)', content)
    testpaths = testpaths_match.group(1).strip().split() if testpaths_match else []

    # Extract markers
    markers_section = re.search(r'markers\s*=\s*\n((?:\s+.+\n)+)', content)
    markers = []
    if markers_section:
        for line in markers_section.group(1).strip().split('\n'):
            if ':' in line:
                marker_name = line.strip().split(':')[0].strip()
                markers.append(marker_name)

    # Parse xdist options
    n_workers = "auto" if "-n auto" in addopts else None
    if not n_workers:
        n_match = re.search(r'-n\s+(\d+)', addopts)
        if n_match:
            n_workers = n_match.group(1)

    dist_match = re.search(r'--dist=(\w+)', addopts)
    dist_mode = dist_match.group(1) if dist_match else None

    # Parse timeout
    timeout_match = re.search(r'--timeout=(\d+)', addopts)
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
    content = path.read_bytes()
    data = tomllib.loads(content.decode('utf-8'))

    pytest_options = data.get('tool', {}).get('pytest', {}).get('ini_options', {})

    addopts = pytest_options.get('addopts', '')
    testpaths = pytest_options.get('testpaths', [])
    markers_raw = pytest_options.get('markers', [])

    # Parse markers from list format
    markers = []
    for marker in markers_raw:
        if ':' in marker:
            markers.append(marker.split(':')[0].strip())

    # Parse xdist options
    n_workers = "auto" if "-n auto" in addopts else None
    if not n_workers:
        n_match = re.search(r'-n\s+(\d+)', addopts)
        if n_match:
            n_workers = n_match.group(1)

    dist_match = re.search(r'--dist=(\w+)', addopts)
    dist_mode = dist_match.group(1) if dist_match else None

    timeout_match = re.search(r'--timeout=(\d+)', addopts)
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

    # Critical: xdist parallel execution
    if not pytest_ini.n_workers:
        errors.append("CRITICAL: pytest.ini missing -n auto (parallel execution)")
    elif pytest_ini.n_workers != pyproject.n_workers:
        warnings.append(f"WORKERS MISMATCH: pytest.ini={pytest_ini.n_workers}, pyproject.toml={pyproject.n_workers}")

    # Critical: dist mode
    if not pytest_ini.dist_mode:
        errors.append("CRITICAL: pytest.ini missing --dist=loadfile (distribution mode)")
    elif pytest_ini.dist_mode != pyproject.dist_mode:
        warnings.append(f"DIST MISMATCH: pytest.ini={pytest_ini.dist_mode}, pyproject.toml={pyproject.dist_mode}")

    # High: timeout
    if not pytest_ini.timeout:
        errors.append("CRITICAL: pytest.ini missing --timeout (test timeout protection)")
    elif pyproject.timeout and pytest_ini.timeout < pyproject.timeout:
        errors.append(f"TIMEOUT ERROR: pytest.ini timeout ({pytest_ini.timeout}) < pyproject.toml ({pyproject.timeout})")

    # High: serial marker (required for stateful tests)
    if 'serial' not in pytest_ini.markers:
        errors.append("CRITICAL: pytest.ini missing 'serial' marker (required for Redis state tests)")

    # Medium: marker superset check
    pyproject_marker_set = set(pyproject.markers)
    pytest_marker_set = set(pytest_ini.markers)
    missing_in_pytest = pyproject_marker_set - pytest_marker_set
    if missing_in_pytest:
        warnings.append(f"MARKERS: pyproject.toml has extra markers not in pytest.ini: {missing_in_pytest}")

    # Medium: testpaths
    if set(pytest_ini.testpaths) != set(pyproject.testpaths):
        warnings.append(f"TESTPATHS MISMATCH: pytest.ini={pytest_ini.testpaths}, pyproject.toml={pyproject.testpaths}")

    # Report results
    print("=" * 60)
    print("PYTEST CONFIG SSOT VALIDATION")
    print("=" * 60)

    print("\n📄 pytest.ini:")
    print("   Workers: " + (pytest_ini.n_workers or 'NOT SET') + " | Dist: " + (pytest_ini.dist_mode or 'NOT SET') + " | Timeout: " + str(pytest_ini.timeout or 'NOT SET'))
    print("   Markers: " + str(len(pytest_ini.markers)) + " defined")

    print("\n📄 pyproject.toml:")
    print("   Workers: " + (pyproject.n_workers or 'NOT SET') + " | Dist: " + (pyproject.dist_mode or 'NOT SET') + " | Timeout: " + str(pyproject.timeout or 'NOT SET'))
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
    content = pytest_ini_path.read_text()
    changes_made = False

    # Fix missing -n auto
    if '-n auto' not in content and '-n ' not in content:
        content = re.sub(
            r'(addopts\s*=\s*)',
            r'\1-n auto --dist=loadfile --timeout=180 ',
            content,
        )
        changes_made = True
        print("🔧 AUTO-FIX: Added -n auto --dist=loadfile --timeout=180 to addopts")

    # Fix missing serial marker
    if 'serial:' not in content:
        # Find markers section and append
        content = re.sub(
            r'(markers\s*=\s*\n)',
            r'\1    serial: Tests that must run serially (shared Redis state, not xdist-safe)\n',
            content,
        )
        changes_made = True
        print("🔧 AUTO-FIX: Added 'serial' marker definition")

    if changes_made:
        pytest_ini_path.write_text(content)
        print(f"✅ Written fixes to {pytest_ini_path}")

    return changes_made


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validate pytest config SSOT")
    parser.add_argument('--strict', action='store_true', help='Treat warnings as errors')
    parser.add_argument('--fix', action='store_true', help='Auto-fix critical drift')
    args = parser.parse_args()

    root = Path.cwd()
    pytest_ini_path = root / 'pytest.ini'
    pyproject_path = root / 'pyproject.toml'

    if not pytest_ini_path.exists():
        print(f"❌ File not found: {pytest_ini_path}")
        return 1

    if not pyproject_path.exists():
        print(f"❌ File not found: {pyproject_path}")
        return 1

    # Parse configs
    pytest_ini = parse_pytest_ini(pytest_ini_path)
    pyproject = parse_pyproject_toml(pyproject_path)

    # Auto-fix if requested
    if args.fix:
        if fix_configs(pytest_ini_path, pyproject_path):
            # Re-parse after fixes
            pytest_ini = parse_pytest_ini(pytest_ini_path)

    # Validate
    return validate_configs(pytest_ini, pyproject, strict=args.strict)


if __name__ == '__main__':
    sys.exit(main())
