import subprocess
import pytest


@pytest.mark.architecture
def test_no_global_config_usage():
    r = subprocess.run(["grep", "-R", "GLOBAL_CONFIG", "agentic_workflow/"], capture_output=True, text=True)
    assert "GLOBAL_CONFIG" not in r.stdout


@pytest.mark.architecture
def test_dependency_injection_exists():
    from inspect import signature
    from agents import StrategyAgent

    assert "context" in signature(StrategyAgent.__init__).parameters


@pytest.mark.xfail(reason="Add 13 architecture compliance tests", strict=False)
def test_placeholder():
    pytest.xfail("Add 13 architecture compliance tests")
