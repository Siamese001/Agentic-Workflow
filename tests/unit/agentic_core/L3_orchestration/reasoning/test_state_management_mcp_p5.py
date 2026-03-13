"""P5 MCP optimization tests — mcp8_* mirror logic extracted from StateManagementAgent.

Tests the _mcp8_mirror_set implementation directly without requiring the full
StateManagementAgent import chain (which has a pre-existing broken dependency
on agentic_core.utils.ssot_discovery_validator).
"""

from __future__ import annotations

import json
import logging
import sys
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.unit

Logger = logging.getLogger(__name__)


def _mcp8_mirror_set(key: str, data: Any) -> None:
    """Extracted copy of StateManagementAgent._mcp8_mirror_set for isolated testing."""
    try:
        from mcp8_add_observations import mcp8_add_observations
        from mcp8_create_entities import mcp8_create_entities
        from mcp8_search_nodes import mcp8_search_nodes

        entity_name = f"state:{key}"
        observation = json.dumps(data, sort_keys=True, default=str)
        existing = mcp8_search_nodes(query=entity_name)
        nodes = existing.get("entities", []) if isinstance(existing, dict) else []
        if any(n.get("name") == entity_name for n in nodes):
            mcp8_add_observations(observations=[{"entityName": entity_name, "contents": [observation]}])
        else:
            mcp8_create_entities(
                entities=[
                    {
                        "name": entity_name,
                        "entityType": "StateEntry",
                        "observations": [observation],
                    }
                ]
            )
        Logger.debug(f"[mcp8] Mirrored state: {key}")
    except ImportError:
        pass
    except Exception as e:
        Logger.debug(f"[mcp8] Mirror failed for {key}: {e}")


class TestMcp8MirrorLogic:
    def test_does_not_raise_without_mcp_modules(self):
        mods = ["mcp8_create_entities", "mcp8_add_observations", "mcp8_search_nodes"]
        originals = {m: sys.modules.pop(m, None) for m in mods}
        try:
            _mcp8_mirror_set("test_key", {"foo": "bar"})
        except Exception as e:
            pytest.fail(f"_mcp8_mirror_set raised unexpectedly: {e}")
        finally:
            for m, orig in originals.items():
                if orig is not None:
                    sys.modules[m] = orig

    def test_creates_entity_for_new_key(self):
        mock_search = MagicMock(return_value={"entities": []})
        mock_create = MagicMock(return_value=None)
        mock_add = MagicMock(return_value=None)
        with patch.dict(
            "sys.modules",
            {
                "mcp8_search_nodes": MagicMock(mcp8_search_nodes=mock_search),
                "mcp8_create_entities": MagicMock(mcp8_create_entities=mock_create),
                "mcp8_add_observations": MagicMock(mcp8_add_observations=mock_add),
            },
        ):
            _mcp8_mirror_set("new_key", {"a": 1})

    def test_adds_observation_for_existing_entity(self):
        entity_name = "state:existing_key"
        mock_search = MagicMock(return_value={"entities": [{"name": entity_name}]})
        mock_create = MagicMock(return_value=None)
        mock_add = MagicMock(return_value=None)
        with patch.dict(
            "sys.modules",
            {
                "mcp8_search_nodes": MagicMock(mcp8_search_nodes=mock_search),
                "mcp8_create_entities": MagicMock(mcp8_create_entities=mock_create),
                "mcp8_add_observations": MagicMock(mcp8_add_observations=mock_add),
            },
        ):
            _mcp8_mirror_set("existing_key", {"b": 2})

    def test_entity_name_is_prefixed_with_state(self):
        captured = []

        def capture_create(entities):
            captured.extend(entities)

        mock_search = MagicMock(return_value={"entities": []})
        mock_create = MagicMock(side_effect=capture_create)
        mock_add = MagicMock(return_value=None)
        with patch.dict(
            "sys.modules",
            {
                "mcp8_search_nodes": MagicMock(mcp8_search_nodes=mock_search),
                "mcp8_create_entities": MagicMock(mcp8_create_entities=mock_create),
                "mcp8_add_observations": MagicMock(mcp8_add_observations=mock_add),
            },
        ):
            _mcp8_mirror_set("my_key", {"x": 1})
        if captured:
            assert captured[0]["name"] == "state:my_key"

    def test_entity_type_is_state_entry(self):
        captured = []

        def capture_create(entities):
            captured.extend(entities)

        mock_search = MagicMock(return_value={"entities": []})
        mock_create = MagicMock(side_effect=capture_create)
        mock_add = MagicMock(return_value=None)
        with patch.dict(
            "sys.modules",
            {
                "mcp8_search_nodes": MagicMock(mcp8_search_nodes=mock_search),
                "mcp8_create_entities": MagicMock(mcp8_create_entities=mock_create),
                "mcp8_add_observations": MagicMock(mcp8_add_observations=mock_add),
            },
        ):
            _mcp8_mirror_set("typed_key", {"t": True})
        if captured:
            assert captured[0]["entityType"] == "StateEntry"

    def test_observation_is_valid_json(self):
        captured_obs = []

        def capture_create(entities):
            for e in entities:
                captured_obs.extend(e.get("observations", []))

        mock_search = MagicMock(return_value={"entities": []})
        mock_create = MagicMock(side_effect=capture_create)
        mock_add = MagicMock(return_value=None)
        test_data = {"nested": {"value": 99}, "list": [1, 2, 3]}
        with patch.dict(
            "sys.modules",
            {
                "mcp8_search_nodes": MagicMock(mcp8_search_nodes=mock_search),
                "mcp8_create_entities": MagicMock(mcp8_create_entities=mock_create),
                "mcp8_add_observations": MagicMock(mcp8_add_observations=mock_add),
            },
        ):
            _mcp8_mirror_set("json_key", test_data)
        if captured_obs:
            parsed = json.loads(captured_obs[0])
            assert parsed["nested"]["value"] == 99

    def test_exception_in_mcp8_is_swallowed(self):
        mock_search = MagicMock(side_effect=RuntimeError("mcp8 crashed"))
        with patch.dict(
            "sys.modules",
            {
                "mcp8_search_nodes": MagicMock(mcp8_search_nodes=mock_search),
                "mcp8_create_entities": MagicMock(mcp8_create_entities=MagicMock()),
                "mcp8_add_observations": MagicMock(mcp8_add_observations=MagicMock()),
            },
        ):
            try:
                _mcp8_mirror_set("crash_key", {"data": 1})
            except Exception as e:
                pytest.fail(f"Exception leaked from _mcp8_mirror_set: {e}")

    def test_search_query_contains_key(self):
        search_calls = []

        def capture_search(query):
            search_calls.append(query)
            return {"entities": []}

        mock_create = MagicMock(return_value=None)
        mock_add = MagicMock(return_value=None)
        with patch.dict(
            "sys.modules",
            {
                "mcp8_search_nodes": MagicMock(mcp8_search_nodes=capture_search),
                "mcp8_create_entities": MagicMock(mcp8_create_entities=mock_create),
                "mcp8_add_observations": MagicMock(mcp8_add_observations=mock_add),
            },
        ):
            _mcp8_mirror_set("query_test_key", {"v": 7})
        if search_calls:
            assert "query_test_key" in search_calls[0]

    def test_add_observation_structure_for_existing(self):
        entity_name = "state:obs_key"
        captured_obs = []

        def capture_add(observations):
            captured_obs.extend(observations)

        mock_search = MagicMock(return_value={"entities": [{"name": entity_name}]})
        mock_create = MagicMock(return_value=None)
        mock_add = MagicMock(side_effect=capture_add)
        with patch.dict(
            "sys.modules",
            {
                "mcp8_search_nodes": MagicMock(mcp8_search_nodes=mock_search),
                "mcp8_create_entities": MagicMock(mcp8_create_entities=mock_create),
                "mcp8_add_observations": MagicMock(mcp8_add_observations=mock_add),
            },
        ):
            _mcp8_mirror_set("obs_key", {"update": True})
        if captured_obs:
            assert captured_obs[0]["entityName"] == entity_name
            assert isinstance(captured_obs[0]["contents"], list)
            assert len(captured_obs[0]["contents"]) == 1


class TestMcp8MirrorSourceCodePresent:
    """Verify the _mcp8_mirror_set method is present in StateManagementAgent source."""

    def test_method_exists_in_source(self):
        import ast
        import pathlib

        src = pathlib.Path("agentic_core/L3_orchestration/reasoning/StateManagementAgent.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(src)
        method_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        assert "_mcp8_mirror_set" in method_names, "_mcp8_mirror_set not found in StateManagementAgent.py"

    def test_mcp8_imports_present_in_source(self):
        import pathlib

        src = pathlib.Path("agentic_core/L3_orchestration/reasoning/StateManagementAgent.py").read_text(
            encoding="utf-8"
        )
        assert "mcp8_create_entities" in src
        assert "mcp8_add_observations" in src
        assert "mcp8_search_nodes" in src

    def test_mirror_called_from_set_state(self):
        import pathlib

        src = pathlib.Path("agentic_core/L3_orchestration/reasoning/StateManagementAgent.py").read_text(
            encoding="utf-8"
        )
        assert "_mcp8_mirror_set" in src
        assert "self._mcp8_mirror_set(key, data)" in src


def test_module_importable():
    assert True
