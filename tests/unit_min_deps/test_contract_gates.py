"""Tests for contract gates runner."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add ops_scripts/ci to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ops_scripts" / "ci"))

from run_contract_gates import run_cmd


@pytest.mark.unit_min_deps
def test_run_cmd_detects_powershell():
    """run_cmd rejects PowerShell commands."""
    with pytest.raises(ValueError, match="PowerShell usage detected"):
        run_cmd(["powershell", "-Command", "echo test"])
    
    with pytest.raises(ValueError, match="PowerShell usage detected"):
        run_cmd(["pwsh", "-Command", "echo test"])
    
    with pytest.raises(ValueError, match="PowerShell usage detected"):
        run_cmd(["PowerShell.exe", "-Command", "echo test"])


@pytest.mark.unit_min_deps
def test_run_cmd_accepts_python():
    """run_cmd accepts Python commands."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        # Should not raise
        rc, out, err = run_cmd(["python", "--version"])
        assert rc == 0


@pytest.mark.unit_min_deps
def test_run_cmd_uses_argv_arrays():
    """run_cmd uses subprocess with argv arrays and shell=False."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="output", stderr="")
        
        run_cmd(["python", "-m", "pytest", "-q"])
        
        # Verify subprocess.run was called with correct parameters
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        
        # Check that args is a list (argv array)
        assert isinstance(call_args[0][0], list)
        assert call_args[0][0] == ["python", "-m", "pytest", "-q"]
        
        # Check that shell=False
        assert call_args[1]["shell"] is False


@pytest.mark.unit_min_deps
def test_run_cmd_returns_output():
    """run_cmd returns return code, stdout, and stderr."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(
            returncode=42,
            stdout="test output",
            stderr="test error"
        )
        
        rc, out, err = run_cmd(["python", "--version"])
        
        assert rc == 42
        assert out == "test output"
        assert err == "test error"


@pytest.mark.unit_min_deps
def test_run_cmd_encoding_safe():
    """run_cmd uses UTF-8 encoding with error replacement."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        run_cmd(["python", "--version"])
        
        call_args = mock_run.call_args
        assert call_args[1]["encoding"] == "utf-8"
        assert call_args[1]["errors"] == "replace"
