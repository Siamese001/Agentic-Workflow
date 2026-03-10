"""Unit tests for static analysis scanners."""

import tempfile
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    TOOLS_DIR,
)
from agentic_core.L5_safety.static_checks.determinism_serialization_check import (
    scan_file_for_determinism,
)
from agentic_core.L5_safety.static_checks.powershell_ban import (
    scan_file_for_powershell,
)
from agentic_core.L5_safety.static_checks.write_gateway_enforcer import (
    scan_file_for_writes,
)


@pytest.mark.unit_min_deps
def test_powershell_scanner_detects_subprocess_calls():
    """Test PowerShell scanner detects subprocess calls with PowerShell."""
    code = """
import subprocess
subprocess.run(["pwsh", "-c", "echo test"])
subprocess.call(["powershell", "-Command", "Get-Process"])
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        violations = scan_file_for_powershell(Path(f.name))

        assert len(violations) == 2
        assert violations[0][1] == "PS_SUBPROCESS_ARGV0"
        assert "pwsh" in violations[0][2]
        assert violations[1][1] == "PS_SUBPROCESS_ARGV0"
        assert "powershell" in violations[1][2]


@pytest.mark.unit_min_deps
def test_powershell_scanner_detects_shell_true():
    """Test PowerShell scanner detects shell=True in tools directory."""
    code = """
import subprocess
subprocess.run(["echo", "test"], shell=True)
"""

    with tempfile.TemporaryDirectory() as temp_dir:
        tools_dir = Path(temp_dir) / TOOLS_DIR
        tools_dir.mkdir()

        test_file = tools_dir / "test.py"
        test_file.write_text(code)

        violations = scan_file_for_powershell(test_file)

        assert len(violations) == 1
        assert violations[0][1] == "PS_SUBPROCESS_SHELL"
        assert "shell=True" in violations[0][2]


@pytest.mark.unit_min_deps
def test_powershell_scanner_detects_string_literals():
    """Test PowerShell scanner detects string literals."""
    code = """
# This is a comment about pwsh usage
command = "powershell -Command Get-Process"
"""

    with tempfile.TemporaryDirectory() as temp_dir:
        evidence_dir = Path(temp_dir) / "docs" / "evidence"
        evidence_dir.mkdir(parents=True)

        test_file = evidence_dir / "test.py"
        test_file.write_text(code)

        violations = scan_file_for_powershell(test_file)

        assert len(violations) == 2
        assert violations[0][1] == "PS_STRING_LITERAL"
        assert violations[1][1] == "PS_STRING_LITERAL"


@pytest.mark.unit_min_deps
def test_write_gateway_scanner_detects_direct_writes():
    """Test write gateway scanner detects direct file writes."""
    code = """
# Direct write violations
open("file.txt", "w")
open("data.bin", "wb")
Path("output.txt").write_text("content")
Path("output.bin").write_bytes(b"binary")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        violations = scan_file_for_writes(Path(f.name))

        assert len(violations) == 4
        rule_ids = [v[1] for v in violations]
        assert "DIRECT_OPEN_WRITE" in rule_ids
        assert "DIRECT_PATH_WRITE" in rule_ids


@pytest.mark.unit_min_deps
def test_write_gateway_scanner_respects_allowlist():
    """Test write gateway scanner respects allowlist comments."""
    code = """
# This should be flagged
open("file1.txt", "w")

# This should be allowed
open("file2.txt", "w")  # guardian: allow-direct-write

# This should be flagged again
open("file3.txt", "w")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        violations = scan_file_for_writes(Path(f.name))

        assert len(violations) == 2
        # Should only flag file1.txt and file3.txt, not file2.txt


@pytest.mark.unit_min_deps
def test_write_gateway_scanner_detects_with_statement():
    """Test write gateway scanner detects with open() patterns."""
    code = """
with open("output.txt", "w") as f:
    f.write("content")

with open("data.bin", "wb") as f:
    f.write(b"binary")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        violations = scan_file_for_writes(Path(f.name))

        assert len(violations) == 2
        assert all(v[1] == "DIRECT_WITH_WRITE" for v in violations)


@pytest.mark.unit_min_deps
def test_determinism_scanner_detects_json_without_sort_keys():
    """Test determinism scanner detects json.dumps without sort_keys."""
    code = """
def serialize_data(data):
    # This should be flagged
    json.dumps(data)

    # This should be flagged too
    json.dumps(data, indent=2)

    # This should be allowed
    json.dumps(data, sort_keys=True)
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        violations = scan_file_for_determinism(Path(f.name))

        assert len(violations) == 2
        assert all(v[1] == "JSON_NO_SORT_KEYS" for v in violations)


@pytest.mark.unit_min_deps
def test_determinism_scanner_detects_datetime_now():
    """Test determinism scanner detects datetime.now() in serialization functions."""
    code = """
import datetime

def record_to_json(record):
    # This should be flagged
    timestamp = datetime.now()
    return json.dumps({"timestamp": timestamp.isoformat()}, sort_keys=True)

def other_function():
    # This should not be flagged (not in serialization context)
    timestamp = datetime.now()
    return timestamp
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        violations = scan_file_for_determinism(Path(f.name))

        assert len(violations) == 1
        assert violations[0][1] == "DATETIME_NOW"


@pytest.mark.unit_min_deps
def test_determinism_scanner_detects_time_time():
    """Test determinism scanner detects time.time() in serialization functions."""
    code = """
import time

def serialize_with_timestamp(data):
    # This should be flagged
    timestamp = time.time()
    return json.dumps({"timestamp": timestamp}, sort_keys=True)
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        violations = scan_file_for_determinism(Path(f.name))

        assert len(violations) == 1
        assert violations[0][1] == "TIME_TIME"


@pytest.mark.unit_min_deps
def test_scanner_deterministic_ordering():
    """Test that scanner findings are returned in deterministic order."""
    code = """
import subprocess

from agentic_core.L0_routing.config.path_constants import (
    TOOLS_DIR,
)
subprocess.run(["pwsh", "-c", "echo test"])
subprocess.call(["powershell", "-Command", "Get-Process"])
open("file.txt", "w")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        # Run scan twice
        violations1 = scan_file_for_powershell(Path(f.name))
        violations2 = scan_file_for_powershell(Path(f.name))

        # Should be identical and in same order
        assert violations1 == violations2

        # Should be sorted by line number
        line_numbers = [v[0] for v in violations1]
        assert line_numbers == sorted(line_numbers)
