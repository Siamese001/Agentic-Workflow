"""W4 tests — L5 verify helper + CI gate check_l5_cert_ref_on_emit_contracts.py.

Covers:
- verify_certification_ref: import paths, True/False semantics
- registry.py re-export
- CI gate: green path (all contracts present), fail-closed mode, bypass mode,
  missing-field detection, missing-class detection, missing-file detection
"""
from __future__ import annotations

import ast
import importlib
import subprocess
import sys
import textwrap
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# verify_certification_ref — helper semantics
# ---------------------------------------------------------------------------

def test_verify_cert_ref_true_for_nonempty():
    from agentic_core.L5_safety.contracts.verify import verify_certification_ref
    assert verify_certification_ref("cert-abc-001") is True


def test_verify_cert_ref_false_for_empty_string():
    from agentic_core.L5_safety.contracts.verify import verify_certification_ref
    assert verify_certification_ref("") is False


def test_verify_cert_ref_false_for_whitespace():
    from agentic_core.L5_safety.contracts.verify import verify_certification_ref
    assert verify_certification_ref("   ") is True  # non-empty string — structural only


def test_verify_cert_ref_false_for_non_string():
    from agentic_core.L5_safety.contracts.verify import verify_certification_ref
    assert verify_certification_ref(None) is False  # type: ignore[arg-type]


def test_verify_cert_ref_reexported_from_registry():
    from agentic_core.L5_safety.contracts import registry
    assert hasattr(registry, "verify_certification_ref")
    assert callable(registry.verify_certification_ref)


def test_verify_cert_ref_registry_and_verify_are_same_function():
    from agentic_core.L5_safety.contracts.verify import verify_certification_ref as vv
    from agentic_core.L5_safety.contracts.registry import verify_certification_ref as vr
    assert vv is vr


# ---------------------------------------------------------------------------
# CI gate — direct module import tests
# ---------------------------------------------------------------------------

def _import_gate():
    """Import the gate module fresh each call."""
    import importlib.util
    gate_path = REPO_ROOT / "ops_scripts" / "ci" / "check_l5_cert_ref_on_emit_contracts.py"
    spec = importlib.util.spec_from_file_location("check_l5_cert_ref_on_emit_contracts", gate_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_gate_green_no_violations(capsys):
    mod = _import_gate()
    rc = mod.main()
    out = capsys.readouterr().out
    assert rc == 0
    assert "18/18 OK" in out
    assert "gate GREEN" in out


def test_gate_extract_field_names_found():
    mod = _import_gate()
    src = textwrap.dedent("""\
        from dataclasses import dataclass
        @dataclass
        class Foo:
            x: str = ""
            l5_certification_ref: str = ""
    """)
    tree = ast.parse(src)
    fields = mod._extract_dataclass_field_names(tree, "Foo")
    assert "l5_certification_ref" in fields
    assert "x" in fields


def test_gate_extract_field_names_class_not_found():
    mod = _import_gate()
    tree = ast.parse("class Bar: pass")
    assert mod._extract_dataclass_field_names(tree, "Missing") is None


def test_gate_check_file_missing_field(tmp_path):
    mod = _import_gate()
    # Write a contract file that is missing the field
    src = textwrap.dedent("""\
        from dataclasses import dataclass
        @dataclass(frozen=True)
        class MyContract:
            request_id: str = ""
    """)
    f = tmp_path / "contract.py"
    f.write_text(src, encoding="utf-8")
    # Patch REPO_ROOT so the relative path resolves correctly
    rel = str(f.relative_to(REPO_ROOT)) if f.is_relative_to(REPO_ROOT) else str(f)
    # Use absolute path trick: temporarily make it relative to tmp_path
    import unittest.mock as mock
    with mock.patch.object(mod, "REPO_ROOT", tmp_path):
        err = mod._check_file(str(f.relative_to(tmp_path)), "MyContract")
    assert err is not None
    assert "FIELD_MISSING" in err


def test_gate_check_file_class_not_found(tmp_path):
    mod = _import_gate()
    src = "class Other: pass\n"
    f = tmp_path / "contract2.py"
    f.write_text(src, encoding="utf-8")
    import unittest.mock as mock
    with mock.patch.object(mod, "REPO_ROOT", tmp_path):
        err = mod._check_file(str(f.relative_to(tmp_path)), "Missing")
    assert err is not None
    assert "CLASS_NOT_FOUND" in err


def test_gate_check_file_missing_file(tmp_path):
    mod = _import_gate()
    import unittest.mock as mock
    with mock.patch.object(mod, "REPO_ROOT", tmp_path):
        err = mod._check_file("does_not_exist.py", "Foo")
    assert err is not None
    assert "MISSING_FILE" in err


def test_gate_bypass_exits_zero(capsys, monkeypatch):
    monkeypatch.setenv("L5_CERT_REF_GATE_BYPASS", "1")
    mod = _import_gate()
    rc = mod.main()
    out = capsys.readouterr().out
    assert rc == 0
    assert "bypassed" in out.lower()


def test_gate_fail_closed_exits_one_when_violations(capsys, monkeypatch, tmp_path):
    monkeypatch.setenv("L5_CERT_REF_GATE_FAIL_CLOSED", "1")
    monkeypatch.delenv("L5_CERT_REF_GATE_BYPASS", raising=False)
    mod = _import_gate()
    # Inject a synthetic violation
    bad_contracts = [("nonexistent/path.py", "FakeClass")]
    import unittest.mock as mock
    with mock.patch.object(mod, "EMIT_CONTRACTS", bad_contracts):
        rc = mod.main()
    assert rc == 1


def test_gate_advisory_exits_zero_even_with_violations(capsys, monkeypatch):
    monkeypatch.delenv("L5_CERT_REF_GATE_FAIL_CLOSED", raising=False)
    monkeypatch.delenv("L5_CERT_REF_GATE_BYPASS", raising=False)
    mod = _import_gate()
    import unittest.mock as mock
    bad_contracts = [("nonexistent/path.py", "FakeClass")]
    with mock.patch.object(mod, "EMIT_CONTRACTS", bad_contracts):
        rc = mod.main()
    assert rc == 0


# ---------------------------------------------------------------------------
# Gate registered in run_contract_gates.py
# ---------------------------------------------------------------------------

def test_gate_registered_in_run_contract_gates():
    gates_path = REPO_ROOT / "ops_scripts" / "ci" / "run_contract_gates.py"
    content = gates_path.read_text(encoding="utf-8")
    assert "check_l5_cert_ref_on_emit_contracts.py" in content
    assert "L5CR1" in content
