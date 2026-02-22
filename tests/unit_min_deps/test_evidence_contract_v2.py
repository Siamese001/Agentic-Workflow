"""Tests for Evidence Contract v2 helper."""

from unittest.mock import MagicMock, patch
import pytest
import sys
from pathlib import Path

# Add tools/evidence to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "evidence"))

from evidence_contract_v2 import EvidenceContractV2


@pytest.mark.unit_min_deps
def test_rejects_missing_code_commit():
    """EvidenceContractV2.parse_args rejects missing --code-commit."""
    with patch.object(sys, 'argv', ['test_evidence_contract_v2.py']):
        with pytest.raises(SystemExit):
            EvidenceContractV2.parse_args("test")


@pytest.mark.unit_min_deps
def test_accepts_valid_code_commit():
    """EvidenceContractV2.parse_args accepts valid --code-commit."""
    with patch.object(sys, 'argv', [
        'test_evidence_contract_v2.py', 
        '--code-commit', 
        'a' * 40
    ]):
        args = EvidenceContractV2.parse_args("test")
        assert args.code_commit == 'a' * 40
        assert args.evidence_commit is None


@pytest.mark.unit_min_deps
def test_validate_commit_hash_invalid_length():
    """validate_commit_hash rejects non-40-character hashes."""
    contract = EvidenceContractV2(Path.cwd())
    
    with pytest.raises(ValueError, match="must be 40 characters"):
        contract.validate_commit_hash("short")
    
    with pytest.raises(ValueError, match="must be 40 characters"):
        contract.validate_commit_hash("a" * 39)


@pytest.mark.unit_min_deps
def test_validate_commit_hash_invalid_chars():
    """validate_commit_hash rejects non-hex characters."""
    contract = EvidenceContractV2(Path.cwd())
    
    with pytest.raises(ValueError, match="must be hex"):
        contract.validate_commit_hash("g" * 40)
    
    with pytest.raises(ValueError, match="must be hex"):
        contract.validate_commit_hash("a" * 20 + "xyz" + "a" * 17)


@pytest.mark.unit_min_deps
def test_validate_commit_hash_valid():
    """validate_commit_hash accepts valid 40-hex strings."""
    contract = EvidenceContractV2(Path.cwd())
    
    # Should not raise
    contract.validate_commit_hash("a" * 40)
    contract.validate_commit_hash("0123456789abcdef0123456789abcdef01234567")  # 40 chars
    contract.validate_commit_hash("ABCDEF0123456789ABCDEF0123456789ABCDEF01")  # 40 chars


@pytest.mark.unit_min_deps
def test_run_cmd_detects_powershell():
    """run_cmd rejects PowerShell commands."""
    contract = EvidenceContractV2(Path.cwd())
    
    with pytest.raises(ValueError, match="PowerShell usage detected"):
        contract.run_cmd(["powershell", "-Command", "echo test"])
    
    with pytest.raises(ValueError, match="PowerShell usage detected"):
        contract.run_cmd(["pwsh", "-Command", "echo test"])
    
    with pytest.raises(ValueError, match="PowerShell usage detected"):
        contract.run_cmd(["PowerShell.exe", "-Command", "echo test"])


@pytest.mark.unit_min_deps
def test_run_cmd_accepts_python():
    """run_cmd accepts Python commands."""
    contract = EvidenceContractV2(Path.cwd())
    
    # Mock subprocess.run to avoid actual execution
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        # Should not raise
        rc, out, err = contract.run_cmd(["python", "--version"])
        assert rc == 0


@pytest.mark.unit_min_deps
def test_hash_loop_prevention():
    """validate_hash_loop_prevention rejects CODE_COMMIT == current HEAD."""
    contract = EvidenceContractV2(Path.cwd())
    
    with patch.object(contract, 'get_current_head', return_value='a' * 40):
        with pytest.raises(ValueError, match="hash loop"):
            contract.validate_hash_loop_prevention('a' * 40)


@pytest.mark.unit_min_deps
def test_hash_loop_prevention_allows_different():
    """validate_hash_loop_prevention allows different commits."""
    contract = EvidenceContractV2(Path.cwd())
    
    with patch.object(contract, 'get_current_head', return_value='a' * 40):
        # Should not raise
        contract.validate_hash_loop_prevention('b' * 40)


@pytest.mark.unit_min_deps
def test_validate_scope_containment_violations():
    """validate_scope_containment rejects files outside allowed prefixes."""
    contract = EvidenceContractV2(Path.cwd(), {"apps_lic/", "apps_rg/"})
    
    files_out_of_scope = [
        "docs/technical/drill-down.md",
        "scripts/deploy.sh",
        "temp/file.txt"
    ]
    
    with pytest.raises(ValueError, match="Scope violation"):
        contract.validate_scope_containment(files_out_of_scope, "TEST")


@pytest.mark.unit_min_deps
def test_validate_scope_containment_allowed():
    """validate_scope_containment allows files within allowed prefixes."""
    contract = EvidenceContractV2(Path.cwd(), {"apps_lic/", "apps_rg/"})
    
    files_in_scope = [
        "apps_lic/engines/test.py",
        "apps_rg/engines/test.py",
        "apps_lic/subdir/file.py"
    ]
    
    # Should not raise
    contract.validate_scope_containment(files_in_scope, "TEST")


@pytest.mark.unit_min_deps
def test_build_evidence_sections():
    """build_evidence_sections returns properly structured sections."""
    contract = EvidenceContractV2(Path.cwd())
    
    with patch.object(contract, 'get_changed_files') as mock_get_files, \
         patch.object(contract, 'validate_scope_containment'):
        
        mock_get_files.return_value = ["file1.py", "file2.py"]
        
        sections = contract.build_evidence_sections(
            "a" * 40, 
            evidence_commit="b" * 40,
            inspected_files=["inspected.py"]
        )
        
        assert sections["CODE_COMMIT"] == "a" * 40
        assert sections["EVIDENCE_COMMIT"] == "b" * 40
        assert sections["FILES_CHANGED_CODE"] == ["file1.py", "file2.py"]
        assert sections["FILES_CHANGED_EVIDENCE"] == ["file1.py", "file2.py"]
        assert sections["INSPECTED_FILES"] == ["inspected.py"]


@pytest.mark.unit_min_deps
def test_format_evidence_sections():
    """format_evidence_sections produces proper markdown structure."""
    contract = EvidenceContractV2(Path.cwd())
    
    sections = {
        "CODE_COMMIT": "a" * 40,
        "EVIDENCE_COMMIT": "PENDING",
        "FILES_CHANGED_CODE": ["file1.py", "file2.py"],
        "FILES_CHANGED_EVIDENCE": [],
        "INSPECTED_FILES": ["inspected.py"]
    }
    
    lines = contract.format_evidence_sections(sections)
    
    # Check that all required sections are present
    assert "## CODE_COMMIT" in lines
    assert "## EVIDENCE_COMMIT" in lines
    assert "## FILES_CHANGED_CODE" in lines
    assert "## FILES_CHANGED_EVIDENCE" in lines
    assert "## INSPECTED_FILES" in lines
    
    # Check that values are present
    assert "a" * 40 in lines
    assert "PENDING" in lines
    assert "file1.py" in lines
    assert "file2.py" in lines
    assert "inspected.py" in lines


@pytest.mark.unit_min_deps
def test_validate_evidence_contract_structure():
    """validate_evidence_contract_structure performs all validations."""
    contract = EvidenceContractV2(Path.cwd())
    
    with patch.object(contract, 'validate_commit_hash') as mock_hash, \
         patch.object(contract, 'validate_commit_exists') as mock_exists, \
         patch.object(contract, 'validate_hash_loop_prevention') as mock_loop:
        
        # Test without evidence_commit (draft mode - no hash-loop check)
        contract.validate_evidence_contract_structure("a" * 40, require_evidence_commit=False)
        
        mock_hash.assert_called_once_with("a" * 40)
        mock_exists.assert_called_once_with("a" * 40)
        mock_loop.assert_not_called()  # Not called in draft mode
        
        # Test with evidence_commit (hash-loop check enabled)
        mock_hash.reset_mock()
        mock_exists.reset_mock()
        mock_loop.reset_mock()
        
        contract.validate_evidence_contract_structure("a" * 40, "b" * 40, require_evidence_commit=True)
        
        assert mock_hash.call_count == 2
        assert mock_exists.call_count == 2
        mock_loop.assert_called_once_with("a" * 40)  # Called when evidence_commit provided


@pytest.mark.unit_min_deps
def test_validate_evidence_contract_structure_requires_evidence_commit():
    """validate_evidence_contract_structure requires evidence_commit when required."""
    contract = EvidenceContractV2(Path.cwd())
    
    with patch.object(contract, 'validate_commit_hash') as mock_hash, \
         patch.object(contract, 'validate_commit_exists') as mock_exists, \
         patch.object(contract, 'validate_hash_loop_prevention') as mock_loop:
        
        # Make validate_commit_exists raise an error to simulate non-existent commit
        mock_exists.side_effect = ValueError("Commit does not exist: test")
        
        with pytest.raises(ValueError, match="Commit does not exist"):
            contract.validate_evidence_contract_structure("a" * 40, require_evidence_commit=True)
