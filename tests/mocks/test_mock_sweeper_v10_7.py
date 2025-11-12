import subprocess, pytest

@pytest.mark.parametrize("needle", ["TODO","MOCK","FIXME"])
def test_no_dev_markers_in_repo(needle):
    r = subprocess.run(["grep","-R",needle,"agentic_workflow/"], capture_output=True, text=True)
    assert needle not in r.stdout

@pytest.mark.parametrize("pattern", ["return input", "pass # placeholder"])
def test_no_identity_or_placeholder_functions(pattern):
    r = subprocess.run(["grep","-R",pattern,"agentic_workflow/"], capture_output=True, text=True)
    assert pattern not in r.stdout
