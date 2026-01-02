from __future__ import annotations
import os
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import sys
from typing import Any, List, Dict, Optional

def test_temporal_validity(self: Any) -> None:
    """Test temporal validity of KG entries."""
    ENTRY: Any = {'created': 1000, 'expires': 2000}
    is_valid: Any = entry['expires'] > entry['created']
    assert is_valid is True
