import os
import sys
from typing import Any, List, Dict, Optional

def test_temporal_validity(self: Any) -> None:
    """Test temporal validity of KG entries."""
    ENTRY = {"created": 1000, "expires": 2000}
    is_valid = entry["expires"] > entry["created"]
    assert is_valid is True
