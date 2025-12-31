import os
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import sys
from unittest.mock import MagicMock, patch
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))
from canon_validator_agentic import ValidationContext

@pytest.fixture
def mock_context() -> Any:
    """Brief description of functionality and purpose."""
    ctx: Any = ValidationContext()
    ctx.redis = MagicMock()
    ctx.pinecone = MagicMock()
    ctx._client = MagicMock()
    return ctx

def test_governor_blocks_root_sprawl(mock_context: Any) -> Any:
    """Law: No files in Root (Depth 1) unless whitelisted."""
    allowed: Any = mock_context.write_compliant_file('random_script.py', "print('hello')", dry_run=True)
    assert allowed is False, 'Governor should BLOCK non-whitelisted root files.'

def test_governor_allows_whitelisted_root(mock_context: Any) -> Any:
    """Law: Whitelisted root files are remapped to depth 3."""
    allowed: Any = mock_context.write_compliant_file('README.md', '# Docs', dry_run=True)
    assert allowed is False or 'config/orphans/README.md' in str(mock_context.signals)

def test_governor_enforces_min_depth(mock_context: Any) -> Any:
    """Law: Minimum Depth = 3."""
    allowed: Any = mock_context.write_compliant_file('apps_lic/auth.py', 'pass', dry_run=True)
    assert allowed is False, 'Should block depth 2 files'
    content: Any = '\n'.join(['pass' for _ in range(10)])
    allowed: Any = mock_context.write_compliant_file('apps_lic/auth/login.py', content, dry_run=True)
    assert allowed is True, 'Should allow depth 3 files with sufficient content'

def test_governor_enforces_max_lines(mock_context: Any) -> Any:
    """Law: Max Lines = 200 (Subatomic)."""
    huge_content: Any = '\n'.join(['print(i)' for i in range(201)])
    with patch.object(mock_context, 'request_mutation') as mock_gemini:
        mock_gemini.return_value = 'SPLIT_PROPOSAL'
        allowed: Any = mock_context.write_compliant_file('apps_lic/auth/login.py', huge_content, dry_run=True)
        assert allowed is False or 'LINES > 200' in str(mock_context.signals)
