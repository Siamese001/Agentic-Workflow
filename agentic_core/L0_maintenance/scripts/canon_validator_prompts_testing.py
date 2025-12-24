"""
Testing few-shot patterns.
Used by TestPilot and property-based testing agents.
"""
import json

FEW_SHOT_PROPERTY_TESTS = """
FEW-SHOT HYPOTHESIS PROPERTY TESTS (Valid syntax only):

EXAMPLE 1: List reversal idempotency
from hypothesis import given, strategies as st
@given(st.lists(st.integers()))
def test_reverse_twice(lst):
    assert lst[::-1][::-1] == lst

EXAMPLE 2: JSON serialization roundtrip
@given(st.dictionaries(st.text(), st.integers()))
def test_json_roundtrip(data):
    assert json.loads(json.dumps(data)) == data

EXAMPLE 3: Sorting is idempotent
@given(st.lists(st.integers()))
def test_sorted_idempotent(numbers):
    assert sorted(sorted(numbers)) == sorted(numbers)
"""

FEW_SHOT_TESTPILOT = """
FEW-SHOT TEST GENERATION (TestPilot):

EXAMPLE 1: Unit Test Structure
GOOD:
def test_process_valid_order():
    order = OrderFactory(status="pending")
    result = process_order(order)
    assert result.status == "processed"

Use pytest style.
Cover happy path + one error case.
Never use real external calls.
"""