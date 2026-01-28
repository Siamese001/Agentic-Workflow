"""
file: tests/conftest.py
description: Global test anchor. Wires up the relocated fixtures.
"""
# Point pytest to the moved root conftest (formerly tests/conftest.py)
pytest_plugins = ["tests.fixtures.root_conftest"]
