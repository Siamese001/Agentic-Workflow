"""Test IhealerprotocolAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestIhealerprotocolAdg:
    """Test IhealerprotocolAdg functionality."""

    def test_IHealerProtocol_adg_imports(self):
        """Test IHealerProtocol_adg module imports."""
        from agentic_core import IHealerProtocol_adg

        assert IHealerProtocol_adg is not None

    def test_IHealerProtocol_adg_class(self):
        """Test IhealerprotocolAdg class exists."""
        from agentic_core import IhealerprotocolAdg

        assert IhealerprotocolAdg is not None

    def test_IHealerProtocol_adg_callable(self):
        """Test IHealerProtocol_adg functions are callable."""
        from agentic_core import validate_IHealerProtocol_adg

        assert callable(validate_IHealerProtocol_adg)
