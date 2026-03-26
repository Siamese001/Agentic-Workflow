"""Fixture-file round-trip tests — end-to-end scan through _scan_file.

Methods used:
1. Real .py fixture files written to tmp_path, scanned via _scan_file()
2. _classify_call() boundary tests (all branches + edge-case suffixes)
3. _classify_config_read() full-branch coverage (all subtypes)
4. Regression lock: influences / invokes_provider(dynamic_exec) MUST NOT appear
5. verify_layer_graph_consistency error branch (schema.py 391-395)
6. _populate_module_entities seam path (builder.py)
7. Property-based: multi-decorator / chained calls / mixed fixture
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest




ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _scan(source: str, tmp_path: Path, filename: str = "fixture.py"):

    def test_exec_round_trip(self, tmp_path):
        edges = _scan("exec('x=1')\n", tmp_path)
        assert "invokes_dynamic" in _rel_types(edges)

    def test_importlib_import_module_round_trip(self, tmp_path):
        edges = _scan("import importlib\nmod = importlib.import_module('pkg')\n", tmp_path)
        assert "invokes_dynamic" in _rel_types(edges)

    def test_compile_round_trip(self, tmp_path):
        edges = _scan("code = compile('x=1', '<str>', 'exec')\n", tmp_path)
        assert "invokes_dynamic" in _rel_types(edges)


class TestRoundTripG3WriteExclusions:
    """G3: WRITE_SIDE_EFFECT_EXCLUSIONS via _scan_file."""

    def test_copy_deepcopy_not_writes_to(self, tmp_path):
        edges = _scan("import copy\nresult = copy.deepcopy(obj)\n", tmp_path)
        write_deepcopy = [e for e in edges if e.relation_type == "writes_to" and "deepcopy" in e.symbol]
        assert not write_deepcopy

    def test_asyncio_run_not_writes_to(self, tmp_path):
        edges = _scan("import asyncio\nasyncio.run(main())\n", tmp_path)
        write_asyncio = [e for e in edges if e.relation_type == "writes_to" and "asyncio" in e.symbol]
        assert not write_asyncio

    def test_os_remove_is_writes_to(self, tmp_path):
        edges = _scan("import os\nos.remove('file.txt')\n", tmp_path)
        assert "writes_to" in _rel_types(edges)

    def test_open_write_mode_is_writes_to(self, tmp_path):
        edges = _scan("f = open('out.txt', 'w')\n", tmp_path)
        assert "writes_to" in _rel_types(edges)

    def test_shutil_copy_is_writes_to(self, tmp_path):
        edges = _scan("import shutil\nshutil.copy('src', 'dst')\n", tmp_path)
        assert "writes_to" in _rel_types(edges)


class TestRoundTripG4FutureImports:
    """G4: __future__ not tagged dead via _scan_file."""

    def test_future_annotations_not_dead(self, tmp_path):
        edges = _scan(
            "from __future__ import annotations\n\ndef foo() -> None:\n    pass\n",
            tmp_path,
        )
        dead_future = [
            e for e in edges if e.relation_type == "dead_imports" and "__future__" in (e.symbol or "")
        ]
        assert not dead_future

    def test_future_generators_not_dead(self, tmp_path):
        edges = _scan(
            "from __future__ import generators\n\ndef foo():\n    yield 1\n",
            tmp_path,
        )
        dead_future = [
            e for e in edges if e.relation_type == "dead_imports" and "__future__" in (e.symbol or "")
        ]
        assert not dead_future

    def test_future_plus_unused_import(self, tmp_path):
        """__future__ stays live; the other unused import becomes dead."""
        edges = _scan(
            "from __future__ import annotations\nimport unused_mod\n\ndef foo(): pass\n",
            tmp_path,
        )
        dead = [e for e in edges if e.relation_type == "dead_imports"]
        dead_symbols = {e.symbol for e in dead}
        assert not any("__future__" in (s or "") for s in dead_symbols)
        assert any("unused_mod" in (s or "") for s in dead_symbols)


class TestRoundTripG5DecoratedBy:
    """G5: decorated_by via _scan_file."""

    def test_function_decorator_round_trip(self, tmp_path):
        edges = _scan("@my_decorator\ndef foo(): pass\n", tmp_path)
        assert "decorated_by" in _rel_types(edges)
        assert "influences" not in _rel_types(edges)

    def test_class_decorator_round_trip(self, tmp_path):
        edges = _scan(
            "from dataclasses import dataclass\n@dataclass\nclass Foo: x: int = 0\n",
            tmp_path,
        )
        dec_edges = [e for e in edges if e.relation_type == "decorated_by"]
        assert dec_edges
        assert all(e.edge_kind == "decorator" for e in dec_edges)

    def test_chained_decorators_round_trip(self, tmp_path):
        edges = _scan("@dec_a\n@dec_b\n@dec_c\ndef foo(): pass\n", tmp_path)
        dec_edges = [e for e in edges if e.relation_type == "decorated_by"]
        assert len(dec_edges) == 3

    def test_method_decorator_round_trip(self, tmp_path):
        edges = _scan("class Foo:\n    @staticmethod\n    def bar(): pass\n", tmp_path)
        dec_edges = [e for e in edges if e.relation_type == "decorated_by"]
        assert dec_edges


class TestRoundTripG6ReadsSubtypes:
    """G6: reads_env/reads_secret/reads_config as relation_type via _scan_file."""

    def test_os_getenv_round_trip(self, tmp_path):
        edges = _scan("import os\nval = os.getenv('KEY')\n", tmp_path)
        env_edges = [e for e in edges if e.relation_type == "reads_env"]
        assert env_edges
        assert all(e.edge_kind == "reads_env" for e in env_edges)

    def test_os_environ_attribute_round_trip(self, tmp_path):
        edges = _scan("import os\nval = os.environ.get('KEY', 'default')\n", tmp_path)
        env_edges = [e for e in edges if e.relation_type == "reads_env"]
        assert env_edges

    def test_reads_env_not_reads_from_round_trip(self, tmp_path):
        edges = _scan("import os\nval = os.getenv('KEY')\n", tmp_path)
        bad = [e for e in edges if e.relation_type == "reads_from" and e.edge_kind == "reads_env"]
        assert not bad, "reads_env must use reads_env as relation_type, not reads_from"

    def test_config_get_round_trip(self, tmp_path):
        edges = _scan("val = config.get('key')\n", tmp_path)
        cfg_edges = [e for e in edges if e.relation_type == "reads_config"]
        assert cfg_edges

    def test_secret_call_round_trip(self, tmp_path):
        edges = _scan("val = get_secret('API_KEY')\n", tmp_path)
        secret_edges = [e for e in edges if e.relation_type == "reads_secret"]
        assert secret_edges

    def test_policy_call_round_trip(self, tmp_path):
        edges = _scan("val = get_policy('rules')\n", tmp_path)
        policy_edges = [e for e in edges if e.relation_type == "reads_policy_state"]
        assert policy_edges


# ===========================================================================
# 2. _classify_call() boundary tests — all branches
# ===========================================================================


class TestClassifyCallBoundary:
    """Full branch coverage of _CallVisitor._classify_call."""

    def setup_method(self):
        pass

    def test_network_symbol_direct(self):
        # Use requests.get — a pure network symbol with no write-suffix collision
        kind, rel = self._classify("requests.get")
        assert kind == "network"
        assert rel == "invokes_provider"

    def test_provider_sdk_base_match(self):
            dead = [
                e for e in edges if e.relation_type == "dead_imports" and "__future__" in (e.symbol or "")
            ]
            assert not dead, f"from __future__ import {fut} must not be tagged dead_import"


# ===========================================================================
# 5. verify_layer_graph_consistency error branch (schema.py 391-395)
# ===========================================================================


class TestVerifyLayerGraphConsistency:
    def test_clean_map_returns_empty(self):
        assert len(errors) == 2

    def test_empty_map_returns_empty(self):
        artifact = self._build(modules=[rel_path], edges=[edge])
        agent_entities = [e for e in artifact.entities if rel_path in e.adg_name]
        assert len(agent_entities) == 1, (
            "Module should not be duplicated between modules list and edge from_name"
        )

    def test_module_entity_has_correct_layer(self):
        artifact = self._build(modules=["agentic_core/L2_execution/SomeAgent.py"])
        ent = next(e for e in artifact.entities if "SomeAgent.py" in e.adg_name)
        assert ent.layer == "L2"

    def test_unknown_path_gets_l_unknown(self):
        artifact = self._build(modules=["totally/unknown/path/mod.py"])
        ent = next(e for e in artifact.entities if "mod.py" in e.adg_name)
        assert ent.layer == "L_UNKNOWN"


# ===========================================================================
# 7. Property-based: complex mixed-fixture sources
# ===========================================================================


class TestMixedFixtureScans:
    """Multi-feature fixture files that exercise many visitors simultaneously."""

    def test_mixed_dynamic_decorator_env(self, tmp_path):
        source = """\
from __future__ import annotations
import os

@some_decorator
def my_func():
    val = os.getenv("KEY")
    result = eval("1+1")
    return val
"""
        edges = _scan(source, tmp_path)
        rels = _rel_types(edges)
        assert "decorated_by" in rels
        assert "reads_env" in rels
        assert "invokes_dynamic" in rels
        assert "influences" not in rels

    def test_mixed_write_exclusion_and_real_write(self, tmp_path):
        source = """\
import copy
import os

def process(data):
    snapshot = copy.deepcopy(data)
    os.remove("/tmp/old_file")
    return snapshot
"""
        edges = _scan(source, tmp_path)
        deepcopy_writes = [
            e for e in edges if e.relation_type == "writes_to" and "deepcopy" in (e.symbol or "")
        ]
        real_writes = [e for e in edges if e.relation_type == "writes_to"]
        assert not deepcopy_writes, "copy.deepcopy must not appear as writes_to"
        assert real_writes, "os.remove must appear as writes_to"

    def test_mixed_future_and_unused_imports(self, tmp_path):
        source = """\
from __future__ import annotations
import unused_module
import os

def foo():
    return os.getcwd()
"""
        edges = _scan(source, tmp_path)
        dead = [e for e in edges if e.relation_type == "dead_imports"]
        dead_symbols = {e.symbol for e in dead}
        assert not any("__future__" in (s or "") for s in dead_symbols)
        assert any("unused_module" in (s or "") for s in dead_symbols)

    def test_all_new_relation_types_never_coexist_with_banned(self, tmp_path):
        source = """\
from __future__ import annotations
import os
import copy

@my_decorator
def func():
    val = os.getenv("K")
    snap = copy.deepcopy(val)
    exec("pass")
    return snap
"""
        edges = _scan(source, tmp_path)
        assert "influences" not in _rel_types(edges), "influences must never appear"
        for e in edges:
            if e.relation_type == "invokes_provider":
                assert e.edge_kind != "dynamic_exec", "invokes_provider must not use dynamic_exec edge_kind"
            if e.relation_type == "reads_from":
                assert e.edge_kind not in (
                    "reads_env",
                    "reads_secret",
                    "reads_policy_state",
                    "reads_runtime_state",
                    "reads_config",
                ), f"reads_from must not carry reads_* edge_kind, got {e.edge_kind}"

    def test_multiple_env_reads_all_reads_env(self, tmp_path):
        source = """\
import os

A = os.getenv("A")
B = os.environ.get("B")
C = os.getenv("C", "default")
"""
        edges = _scan(source, tmp_path)
        env_edges = [e for e in edges if e.relation_type == "reads_env"]
        assert len(env_edges) >= 2, "Multiple getenv/environ calls should all emit reads_env"

    def test_chained_dynamic_and_provider(self, tmp_path):
        source = """\
import importlib
import requests

mod = importlib.import_module("pkg")
resp = requests.get("http://example.com")
"""
        edges = _scan(source, tmp_path)
        assert "invokes_dynamic" in _rel_types(edges)
        assert "invokes_provider" in _rel_types(edges)
        # dynamic must use invokes_dynamic, network must use invokes_provider
        dynamic_edges = [e for e in edges if e.edge_kind == "dynamic_exec"]
        for de in dynamic_edges:
            assert de.relation_type == "invokes_dynamic"


# ===========================================================================
# 8. _tag_dead_imports edge-case coverage
# ===========================================================================


class TestTagDeadImports:
    def _make_import_edge(self, symbol: str):
        pass

    def test_dead_name_retagged(self):
        result = _tag_dead_imports([call_edge], {"foo"})
        assert result[0].relation_type == "calls", "Non-import edges must not be retagged"
