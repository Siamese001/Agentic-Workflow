#!/usr/bin/env python3
"""
Test suite for pre-commit integration of purge_cache.py

Validates that the purge cache script integrates correctly with pre-commit hooks
and respects command-line arguments for quiet and extended operations.
"""

import pytest
import subprocess
import pathlib
import shutil
import sys
import os

# Add the project root to the path to import the script
project_root = pathlib.Path(__file__).parents[4]
sys.path.insert(0, str(project_root))

def test_quiet_mode_output():
    """Verify that --quiet flag suppresses stdout for clean pre-commit logs."""
    # Setup mock cache
    mock_dir = pathlib.Path("temp_quiet_test/__pycache__")
    mock_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Execute script via subprocess to capture output
        result = subprocess.run(
            ["python", "ops_scripts/maintenance/purge_cache.py", "--quiet"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        assert result.stdout.strip() == "", f"FAILED: Quiet mode produced output: '{result.stdout.strip()}'"
        assert not mock_dir.exists(), "FAILED: Cache was not deleted in quiet mode."
        print("Test Case 1: Quiet Mode Suppression - 100% PASS")
    finally:
        # Cleanup
        if mock_dir.exists():
            shutil.rmtree("temp_quiet_test", ignore_errors=True)

def test_extended_purge_coverage():
    """Verify that --all flag targets additional cache types like pytest."""
    pytest_cache = pathlib.Path(".pytest_cache")
    pytest_cache.mkdir(exist_ok=True)
    
    try:
        # Run with --all
        result = subprocess.run(
            ["python", "ops_scripts/maintenance/purge_cache.py", "--all", "--quiet"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        assert not pytest_cache.exists(), "FAILED: Extended cache (.pytest_cache) was not removed."
        print("Test Case 2: Extended Purge Coverage - 100% PASS")
    finally:
        # Cleanup if test failed
        if pytest_cache.exists():
            shutil.rmtree(".pytest_cache", ignore_errors=True)

def test_pre_commit_config_syntax():
    """Verify .pre-commit-config.yaml contains the new local hook."""
    config_path = project_root / ".pre-commit-config.yaml"
    assert config_path.exists(), "FAILED: Config file missing."
    
    content = config_path.read_text()
    assert "id: purge-cache" in content, "FAILED: purge-cache hook not found in config."
    assert "always_run: true" in content, "FAILED: always_run not set to true."
    assert "pass_filenames: false" in content, "FAILED: pass_filenames not set to false."
    assert "--quiet" in content, "FAILED: --quiet flag not found in hook entry."
    assert "stages: [commit]" in content, "FAILED: stages not set to [commit]."
    print("Test Case 3: Config Integration Validation - 100% PASS")

def test_selective_exclusion_persistence():
    """Ensure that .venv directories are NEVER touched even with --all."""
    venv_cache = pathlib.Path(".venv/__pycache__")
    venv_cache.mkdir(parents=True, exist_ok=True)
    
    try:
        result = subprocess.run(
            ["python", "ops_scripts/maintenance/purge_cache.py", "--all", "--quiet"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        exists = venv_cache.exists()
        assert exists, "FAILED: Script purged protected .venv directory!"
        print("Test Case 4: Protected Directory Isolation - 100% PASS")
    finally:
        # Clean up for real
        if pathlib.Path(".venv").exists():
            shutil.rmtree(".venv", ignore_errors=True)

def test_argparse_help_functionality():
    """Verify that argparse help works correctly."""
    result = subprocess.run(
        ["python", "ops_scripts/maintenance/purge_cache.py", "--help"],
        capture_output=True,
        text=True,
        cwd=project_root
    )
    
    assert result.returncode == 0, "FAILED: Help command should exit with code 0."
    assert "--quiet" in result.stdout, "FAILED: --quiet option not in help output."
    assert "--all" in result.stdout, "FAILED: --all option not in help output."
    assert "Hardened Cache Purge Utility" in result.stdout, "FAILED: Description not in help output."
    print("Test Case 5: Argparse Help Functionality - 100% PASS")

def test_verbose_mode_functionality():
    """Verify that without --quiet flag, the script produces output."""
    # Setup mock cache
    mock_dir = pathlib.Path("temp_verbose_test/__pycache__")
    mock_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Execute script without --quiet to capture output
        result = subprocess.run(
            ["python", "ops_scripts/maintenance/purge_cache.py"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        assert result.stdout.strip() != "", "FAILED: Verbose mode should produce output."
        assert "Purged" in result.stdout, "FAILED: Expected 'Purged' in output."
        assert not mock_dir.exists(), "FAILED: Cache was not deleted in verbose mode."
        print("Test Case 6: Verbose Mode Functionality - 100% PASS")
    finally:
        # Cleanup
        if mock_dir.exists():
            shutil.rmtree("temp_verbose_test", ignore_errors=True)

def test_extended_flag_with_quiet():
    """Verify that --all and --quiet flags work together correctly."""
    # Setup multiple cache types
    pytest_cache = pathlib.Path("temp_extended_test/.pytest_cache")
    mypy_cache = pathlib.Path("temp_extended_test/.mypy_cache")
    pycache = pathlib.Path("temp_extended_test/__pycache__")
    
    pytest_cache.mkdir(parents=True, exist_ok=True)
    mypy_cache.mkdir(parents=True, exist_ok=True)
    pycache.mkdir(parents=True, exist_ok=True)
    
    try:
        # Run with both --all and --quiet
        result = subprocess.run(
            ["python", "ops_scripts/maintenance/purge_cache.py", "--all", "--quiet"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        assert result.stdout.strip() == "", "FAILED: --quiet should suppress output even with --all."
        assert not pytest_cache.exists(), "FAILED: .pytest_cache was not removed with --all flag."
        assert not mypy_cache.exists(), "FAILED: .mypy_cache was not removed with --all flag."
        assert not pycache.exists(), "FAILED: __pycache__ was not removed with --all flag."
        print("Test Case 7: Extended + Quiet Flag Integration - 100% PASS")
    finally:
        # Cleanup
        if pathlib.Path("temp_extended_test").exists():
            shutil.rmtree("temp_extended_test", ignore_errors=True)

if __name__ == "__main__":
    # Run all test cases
    test_functions = [
        test_quiet_mode_output,
        test_extended_purge_coverage,
        test_pre_commit_config_syntax,
        test_selective_exclusion_persistence,
        test_argparse_help_functionality,
        test_verbose_mode_functionality,
        test_extended_flag_with_quiet
    ]
    
    print("Running Pre-commit Integration Test Suite...")
    print("=" * 60)
    
    failed_tests = []
    for test_func in test_functions:
        try:
            test_func()
        except Exception as e:
            print(f"FAILED: {test_func.__name__} - {e}")
            failed_tests.append(test_func.__name__)
    
    print("=" * 60)
    if failed_tests:
        print(f"FAILED: {len(failed_tests)} test(s) failed: {', '.join(failed_tests)}")
        sys.exit(1)
    else:
        print("SUCCESS: All test cases passed - 100% PRE-COMMIT INTEGRATION VALIDATION")
