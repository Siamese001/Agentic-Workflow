"""Test SignatureInvalidatorAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSignatureInvalidatorAdg:
    """Test SignatureInvalidatorAdg functionality."""

    def test_signature_invalidator_adg_imports(self):
        """Test signature_invalidator_adg module imports."""
        from agentic_core import signature_invalidator_adg
        assert signature_invalidator_adg is not None

    def test_signature_invalidator_adg_class(self):
        """Test SignatureInvalidatorAdg class exists."""
        from agentic_core import SignatureInvalidatorAdg
        assert SignatureInvalidatorAdg is not None

    def test_signature_invalidator_adg_callable(self):
        """Test signature_invalidator_adg functions are callable."""
        from agentic_core import validate_signature_invalidator_adg
        assert callable(validate_signature_invalidator_adg)
