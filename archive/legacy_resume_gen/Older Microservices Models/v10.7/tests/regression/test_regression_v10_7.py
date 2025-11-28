import json
import pytest


@pytest.mark.regression
def test_output_backward_compatibility():
    prev = json.load(open("tests/baseline_outputs_previous.json"))
    new = json.load(open("tests/baseline_outputs_v10_7.json"))
    for k in prev.keys():
        assert set(prev[k].keys()).issubset(new[k].keys())


@pytest.mark.xfail(reason="Add additional regression tests for model drift and scoring consistency", strict=False)
def test_placeholder():
    pytest.xfail("Add additional regression tests for model drift and scoring consistency")
