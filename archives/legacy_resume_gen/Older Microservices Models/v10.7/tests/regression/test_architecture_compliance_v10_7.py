import subprocess
import pytest


@pytest.mark.architecture
def test_no_global_config_usage() -> None:
    r = subprocess.run(["grep", "-R", "GLOBAL_CONFIG", "agentic_workflow/"], capture_output=True, text=True)
    assert "GLOBAL_CONFIG" not in r.stdout


@pytest.mark.architecture
def test_dependency_injection_exists() -> None:
    from agentic_core.L1_cognition.P2_inspect.detect_anomalies_update.inspect import signature
#     from archives.legacy_resume_gen.Agentic-Workflow-10_7_main.agents import StrategyAgent  # INVALID: Cannot import from path with hyphens

    assert "context" in signature(StrategyAgent.__init__).parameters


@pytest.mark.xfail(reason="Add 13 architecture compliance tests", strict=False)
def test_placeholder() -> None:
    pytest.xfail("Add 13 architecture compliance tests")
