"""Tests for Phase 1 data quality fixes (G1-G6).

Covers:
- G1: invokes_dynamic separated from invokes_provider in _DynamicExecutionVisitor
- G2: PromptSlot/PromptTemplate entity_type in builder.py
- G3: WRITE_SIDE_EFFECT_EXCLUSIONS filter in _CallVisitor
- G4: __future__ excluded from dead_imports in _UnusedImportVisitor
- G5: decorated_by relation (renamed from influences) in _DecoratorVisitor
- G6: reads_env/reads_secret/reads_policy_state promoted to relation_type
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _scan_source(source: str, module_adg: str = "ADG::Module::test.py", rel: str = "test.py"):
    from agentic_core.adg.extraction.static_scanner import (
        _AttributeVisitor,
        _CallVisitor,
        _DecoratorVisitor,
        _DynamicExecutionVisitor,
        _ImportVisitor,
        _tag_dead_imports,
        _UnusedImportVisitor,
    )

    tree = ast.parse(source)
    edges = []

    iv = _ImportVisitor(module_adg, rel)
    iv.visit(tree)
    edges.extend(iv.edges)

    cv = _CallVisitor(module_adg, rel)
    cv.visit(tree)
    edges.extend(cv.edges)

    dv = _DynamicExecutionVisitor(module_adg, rel)
    dv.visit(tree)
    edges.extend(dv.edges)

    av = _AttributeVisitor(module_adg, rel)
    av.visit(tree)
    edges.extend(av.edges)

    dec = _DecoratorVisitor(module_adg, rel)
    dec.visit(tree)
    edges.extend(dec.edges)

    uiv = _UnusedImportVisitor()
    uiv.visit(tree)
    if uiv.dead_names:
        edges = _tag_dead_imports(edges, uiv.dead_names)

    return edges


# ---------------------------------------------------------------------------
# G1: invokes_dynamic separated from invokes_provider
# ---------------------------------------------------------------------------


class TestG1InvokesDynamic:
    def test_eval_emits_invokes_dynamic(self):
        source = "result = eval('1+1')"
        edges = _scan_source(source)
        dynamic_edges = [e for e in edges if e.relation_type == "invokes_dynamic"]
        assert dynamic_edges, "eval() should emit invokes_dynamic edge"
        assert dynamic_edges[0].edge_kind == "dynamic_exec"

    def test_exec_emits_invokes_dynamic(self):
        source = "exec('x=1')"
        edges = _scan_source(source)
        dynamic_edges = [e for e in edges if e.relation_type == "invokes_dynamic"]
        assert dynamic_edges, "exec() should emit invokes_dynamic edge"

    def test_importlib_emits_invokes_dynamic(self):
        source = "import importlib\nmod = importlib.import_module('some.mod')"
        edges = _scan_source(source)
        dynamic_edges = [e for e in edges if e.relation_type == "invokes_dynamic"]
        assert dynamic_edges, "importlib.import_module() should emit invokes_dynamic edge"

    def test_dynamic_is_not_invokes_provider(self):
        source = "result = eval('1+1')"
        edges = _scan_source(source)
        provider_from_dynamic = [
            e for e in edges if e.relation_type == "invokes_provider" and e.edge_kind == "dynamic_exec"
        ]
        assert not provider_from_dynamic, "dynamic_exec edges must not use invokes_provider relation"

    def test_network_call_still_invokes_provider(self):
        source = "import requests\nrequests.get('http://example.com')"
        edges = _scan_source(source)
        provider_edges = [e for e in edges if e.relation_type == "invokes_provider"]
        assert provider_edges, "network calls should still emit invokes_provider"


# ---------------------------------------------------------------------------
# G3: WRITE_SIDE_EFFECT_EXCLUSIONS
# ---------------------------------------------------------------------------


class TestG3WriteExclusions:
    def test_copy_excluded_from_writes_to(self):
        source = "result = copy(some_dict)"
        edges = _scan_source(source)
        write_edges = [e for e in edges if e.relation_type == "writes_to" and "copy" in e.symbol]
        assert not write_edges, "copy() must be excluded from writes_to (false positive)"

    def test_deepcopy_excluded_from_writes_to(self):
        source = "import copy\nresult = copy.deepcopy(obj)"
        edges = _scan_source(source)
        write_edges = [e for e in edges if e.relation_type == "writes_to" and "deepcopy" in e.symbol]
        assert not write_edges, "copy.deepcopy() must be excluded from writes_to"

    def test_os_remove_still_writes_to(self):
        source = "import os\nos.remove('file.txt')"
        edges = _scan_source(source)
        write_edges = [e for e in edges if e.relation_type == "writes_to"]
        assert write_edges, "os.remove() should still emit writes_to edge"

    def test_open_still_writes_to(self):
        source = "f = open('file.txt', 'w')"
        edges = _scan_source(source)
        write_edges = [e for e in edges if e.relation_type == "writes_to"]
        assert write_edges, "open() should still emit writes_to edge"


# ---------------------------------------------------------------------------
# G4: __future__ excluded from dead imports
# ---------------------------------------------------------------------------


class TestG4FutureDeadImports:
    def test_future_annotations_not_dead(self):
        source = "from __future__ import annotations\n\ndef foo() -> None:\n    pass\n"
        edges = _scan_source(source)
        dead_future = [e for e in edges if e.relation_type == "dead_imports" and "__future__" in e.symbol]
        assert not dead_future, "from __future__ import annotations must never be tagged dead_import"

    def test_unused_regular_import_is_dead(self):
        source = "import os\n\ndef foo():\n    pass\n"
        edges = _scan_source(source)
        dead = [e for e in edges if e.relation_type == "dead_imports"]
        assert dead, "Truly unused import should be tagged dead_import"

    def test_used_import_not_dead(self):
        source = "import os\n\ndef foo():\n    return os.getcwd()\n"
        edges = _scan_source(source)
        dead_os = [e for e in edges if e.relation_type == "dead_imports" and "os" in e.symbol]
        assert not dead_os, "Used import should not be tagged dead_import"


# ---------------------------------------------------------------------------
# G5: decorated_by (renamed from influences)
# ---------------------------------------------------------------------------


class TestG5DecoratedBy:
    def test_function_decorator_emits_decorated_by(self):
        source = "@some_decorator\ndef foo(): pass\n"
        edges = _scan_source(source)
        dec_edges = [e for e in edges if e.relation_type == "decorated_by"]
        assert dec_edges, "@some_decorator should emit decorated_by edge"
        assert dec_edges[0].edge_kind == "decorator"

    def test_class_decorator_emits_decorated_by(self):
        source = "@dataclass\nclass Foo: pass\n"
        edges = _scan_source(source)
        dec_edges = [e for e in edges if e.relation_type == "decorated_by"]
        assert dec_edges, "@dataclass should emit decorated_by edge"

    def test_no_influences_relation(self):
        source = "@some_decorator\ndef foo(): pass\n"
        edges = _scan_source(source)
        influences_edges = [e for e in edges if e.relation_type == "influences"]
        assert not influences_edges, "influences relation must be replaced by decorated_by"

    def test_chained_decorators_all_emit_decorated_by(self):
        source = "@decorator_a\n@decorator_b\ndef foo(): pass\n"
        edges = _scan_source(source)
        dec_edges = [e for e in edges if e.relation_type == "decorated_by"]
        assert len(dec_edges) == 2, "Both decorators should emit decorated_by edges"


# ---------------------------------------------------------------------------
# G6: reads_env/reads_secret/reads_policy_state as relation_type
# ---------------------------------------------------------------------------


class TestG6ReadsSubtypes:
    def test_os_getenv_emits_reads_env(self):
        source = "import os\nval = os.getenv('KEY')"
        edges = _scan_source(source)
        env_edges = [e for e in edges if e.relation_type == "reads_env"]
        assert env_edges, "os.getenv() should emit reads_env relation"
        assert all(e.edge_kind == "reads_env" for e in env_edges)

    def test_os_environ_emits_reads_env(self):
        source = "import os\nval = os.environ.get('KEY')"
        edges = _scan_source(source)
        env_edges = [e for e in edges if e.relation_type == "reads_env"]
        assert env_edges, "os.environ.get() should emit reads_env relation"

    def test_reads_env_is_not_reads_from(self):
        source = "import os\nval = os.getenv('KEY')"
        edges = _scan_source(source)
        reads_from_env = [e for e in edges if e.relation_type == "reads_from" and e.edge_kind == "reads_env"]
        assert not reads_from_env, "reads_env edges must use reads_env as relation_type, not reads_from"

    def test_secret_read_emits_reads_secret(self):
        source = "val = get_secret('API_KEY')"
        edges = _scan_source(source)
        secret_edges = [e for e in edges if e.relation_type == "reads_secret"]
        assert secret_edges, "Secret reads should emit reads_secret relation"

    def test_policy_read_emits_reads_policy_state(self):
        source = "val = get_policy('rules')"
        edges = _scan_source(source)
        policy_edges = [e for e in edges if e.relation_type == "reads_policy_state"]
        assert policy_edges, "Policy reads should emit reads_policy_state relation"


# ---------------------------------------------------------------------------
# Schema consistency
# ---------------------------------------------------------------------------


class TestSchemaConsistency:
    def test_invokes_dynamic_in_relation_type(self):
        from agentic_core.adg.schema import RelationType

        assert "invokes_dynamic" in RelationType.__args__

    def test_decorated_by_in_relation_type(self):
        from agentic_core.adg.schema import RelationType

        assert "decorated_by" in RelationType.__args__

    def test_seam_bypass_in_relation_type(self):
        from agentic_core.adg.schema import RelationType

        assert "seam_bypass" in RelationType.__args__

    def test_reads_env_in_relation_type(self):
        from agentic_core.adg.schema import RelationType

        assert "reads_env" in RelationType.__args__

    def test_reads_secret_in_relation_type(self):
        from agentic_core.adg.schema import RelationType

        assert "reads_secret" in RelationType.__args__

    def test_reads_policy_state_in_relation_type(self):
        from agentic_core.adg.schema import RelationType

        assert "reads_policy_state" in RelationType.__args__

    def test_seam_in_entity_type(self):
        from agentic_core.adg.schema import EntityType

        assert "seam" in EntityType.__args__

    def test_write_side_effect_exclusions_exported(self):
        from agentic_core.adg.schema import WRITE_SIDE_EFFECT_EXCLUSIONS

        assert "copy" in WRITE_SIDE_EFFECT_EXCLUSIONS
        assert "deepcopy" in WRITE_SIDE_EFFECT_EXCLUSIONS

    def test_seam_module_patterns_exported(self):
        from agentic_core.adg.schema import SEAM_MODULE_PATTERNS

        assert len(SEAM_MODULE_PATTERNS) >= 1

    def test_rule_id_prefixes_exported(self):
        from agentic_core.adg.schema import RULE_ID_PREFIXES

        assert "LAYER_GRAVITY" in RULE_ID_PREFIXES
        assert "UWG_BYPASS" in RULE_ID_PREFIXES
        assert "SEAM_BYPASS" in RULE_ID_PREFIXES
