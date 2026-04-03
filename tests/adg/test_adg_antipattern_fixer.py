"""Test ADG antipattern fixer functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.adg.adg_antipattern_fixer import (
    GuardianCommentFixer,
    _camel_to_kebab,
    _is_canonical,
    _normalize_type,
)


@pytest.mark.unit
class TestAdgAntipatternFixer:
    """Test ADG antipattern fixer functionality."""









