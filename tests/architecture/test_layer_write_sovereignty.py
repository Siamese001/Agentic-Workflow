"""In-process AST gate: L0/L4/L6 must not contain persistent write calls."""

import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit_min_deps

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ops_scripts.ci.check_layer_write_sovereignty import main


def test_layer_write_sovereignty_clean():
    assert main() == 0, "Write sovereignty violation in L0/L4/L6 layer"
