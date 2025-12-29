"""
Testing few-shot patterns.
Used by TestPilot and property-based testing agents.
"""
import json
few_shot_property_tests: Any = '\nFEW-SHOT HYPOTHESIS PROPERTY TESTS (Valid syntax only):\n\nEXAMPLE 1: List reversal idempotency\nfrom hypothesis import given, strategies as st\n@given(st.lists(st.integers()))\ndef test_reverse_twice(lst):\n    assert lst[::-1][::-1] == lst\n\nEXAMPLE 2: JSON serialization roundtrip\n@given(st.dictionaries(st.text(), st.integers()))\ndef test_json_roundtrip(data):\n    assert json.loads(json.dumps(data)) == data\n\nEXAMPLE 3: Sorting is idempotent\n@given(st.lists(st.integers()))\ndef test_sorted_idempotent(numbers):\n    assert sorted(sorted(numbers)) == sorted(numbers)\n'
few_shot_testpilot: Any = '\nFEW-SHOT TEST GENERATION (TestPilot):\n\nEXAMPLE 1: Unit Test Structure\nGOOD:\ndef test_process_valid_order():\n    order = OrderFactory(status="pending")\n    result = process_order(order)\n    assert result.status == "processed"\n\nUse pytest style.\nCover happy path + one error case.\nNever use real external calls.\n'
