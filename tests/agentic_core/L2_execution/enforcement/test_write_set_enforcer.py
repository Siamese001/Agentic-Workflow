"""Tests for WriteSetEnforcer - write set boundary enforcement."""
import pytest
from unittest.mock import Mock
from agentic_core.L2_execution.enforcement.write_set_enforcer import WriteSetEnforcer


class TestWriteSetEnforcer:
    def test_init_with_write_set(self):
        e = WriteSetEnforcer(write_set={"/src/main.py"})
        assert "/src/main.py" in e.write_set

    def test_validate_write_in_set(self):
        e = WriteSetEnforcer(write_set={"/src/main.py"})
        assert e.validate("/src/main.py") is True

    def test_validate_write_outside_set(self):
        e = WriteSetEnforcer(write_set={"/src/main.py"})
        assert e.validate("/src/other.py") is False

    def test_enforce_in_set(self):
        e = WriteSetEnforcer(write_set={"/src/main.py"})
        e.enforce("/src/main.py")

    def test_enforce_outside_set(self):
        e = WriteSetEnforcer(write_set={"/src/main.py"})
        with pytest.raises(PermissionError):
            e.enforce("/src/other.py")

    def test_add_to_write_set(self):
        e = WriteSetEnforcer(write_set=set())
        e.add_path("/src/new.py")
        assert "/src/new.py" in e.write_set

    def test_remove_from_write_set(self):
        e = WriteSetEnforcer(write_set={"/src/main.py"})
        e.remove_path("/src/main.py")
        assert "/src/main.py" not in e.write_set

    def test_freeze_write_set(self):
        e = WriteSetEnforcer(write_set={"/src/main.py"})
        e.freeze()
        with pytest.raises(RuntimeError):
            e.add_path("/src/other.py")
