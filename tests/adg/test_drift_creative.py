"""Drift detection property tests using hypothesis for ADG graph invariants."""

from __future__ import annotations

import pytest

pytest.importorskip("hypothesis", reason="hypothesis not installed")
from hypothesis import given, settings  # noqa: E402
from hypothesis import strategies as st


@given(st.lists(st.text(min_size=1, max_size=50), min_size=2, max_size=20))
@settings(max_examples=10, deadline=2000)


@given(
    st.lists(
        st.tuples(st.integers(min_value=0, max_value=99), st.integers(min_value=0, max_value=99)),
        min_size=1,
        max_size=50,
    )
)
@settings(max_examples=10, deadline=2000)
