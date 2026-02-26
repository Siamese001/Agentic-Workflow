"""In-process AST gate: zero direct LLM SDK usage outside allowed boundary."""

import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit_min_deps

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ops_scripts.ci.check_sovereign_llm_gateway import main


def test_sovereign_gateway_boundary_clean():
    assert main() == 0, "Direct LLM SDK usage detected outside SovereignLLMGateway"
