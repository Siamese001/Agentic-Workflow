"""Unit tests for the apps_shared stub classifier.

Plan: apps-shared-stub-audit-7dfe16 W1 verification.

Exercises every branch of the classifier against synthetic source files
so the pattern library (Protocol / ABC / ImplicitABC / TypedDict /
TemplateMethodHook / ContextManagerStub / NullObject / DeprecationShim /
HealerConvention / RealGap) stays honest as new cases are added.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tools.analysis.audit_apps_shared_stubs import (
    CensusReport,
    audit,
    emit_json,
)


def _write(root: Path, relpath: str, body: str) -> Path:
    p = root / relpath
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    return p


# -- Registry contract ------------------------------------------------------


def test_audit_returns_census_report(tmp_path: Path) -> None:
    _write(tmp_path, "x.py", "def f():\n    pass\n")
    report = audit(tmp_path)
    assert isinstance(report, CensusReport)
    assert report.scanned_files == 1


def test_emit_json_roundtrip(tmp_path: Path) -> None:
    _write(tmp_path, "x.py", "def f():\n    pass\n")
    report = audit(tmp_path)
    out = tmp_path / "census.json"
    emit_json(report, out)
    assert out.exists()
    import json

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert "stubs" in payload
    assert "category_counts" in payload


# -- Category recognition ---------------------------------------------------


def test_protocol_class_recognised(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "p.py",
        "from typing import Protocol\n"
        "class FooProto(Protocol):\n"
        "    def m(self) -> None: ...\n",
    )
    report = audit(tmp_path)
    cats = {s.category for s in report.stubs}
    assert "Protocol" in cats


def test_abc_class_recognised(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "a.py",
        "from abc import ABC\n"
        "class FooABC(ABC):\n"
        "    def m(self) -> None:\n"
        "        raise NotImplementedError\n",
    )
    report = audit(tmp_path)
    cats = {s.category for s in report.stubs}
    assert "ABC" in cats


def test_abstractmethod_recognised(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "am.py",
        "from abc import abstractmethod\n"
        "class Foo:\n"
        "    @abstractmethod\n"
        "    def m(self) -> None:\n"
        "        raise NotImplementedError\n",
    )
    report = audit(tmp_path)
    cats = {s.category for s in report.stubs}
    assert "ABC" in cats


def test_implicit_abc_on_base_class(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "i.py",
        "class BaseThing:\n"
        "    def m(self) -> None:\n"
        "        raise NotImplementedError\n",
    )
    report = audit(tmp_path)
    cats = {s.category for s in report.stubs}
    assert "ImplicitABC" in cats


def test_implicit_abc_on_client_class(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "c.py",
        "class LLMClient:\n"
        "    def generate(self, p) -> str:\n"
        "        raise NotImplementedError\n",
    )
    report = audit(tmp_path)
    cats = {s.category for s in report.stubs}
    assert "ImplicitABC" in cats


def test_context_manager_stub_recognised(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "cm.py",
        "class Ctx:\n"
        "    async def __aexit__(self, *a):\n"
        "        pass\n",
    )
    report = audit(tmp_path)
    cats = {s.category for s in report.stubs}
    assert "ContextManagerStub" in cats


def test_template_method_hook_recognised(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "t.py",
        "class BaseAgent:\n"
        "    def _post_hook(self) -> None:\n"
        '        """Subclasses may override."""\n',
    )
    report = audit(tmp_path)
    cats = {s.category for s in report.stubs}
    assert "TemplateMethodHook" in cats


def test_null_object_recognised(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "utils/n.py",
        "def create_span(name: str):\n"
        '    """Create a tracing span (null-object fallback when OTel unwired)."""\n'
        "    return None\n",
    )
    report = audit(tmp_path)
    cats = {s.category for s in report.stubs}
    assert "NullObject" in cats


def test_null_object_NOT_claimed_for_scripts(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "scripts/fix.py",
        "def fix_it():\n"
        '    """Fix the thing that needs fixing with a meaningful description."""\n'
        "    pass\n",
    )
    report = audit(tmp_path)
    cats = [s.category for s in report.stubs]
    assert "NullObject" not in cats
    assert "RealGap" in cats


def test_compat_shim_recognised(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "_compat/s.py",
        "def old_api():\n"
        "    pass\n",
    )
    report = audit(tmp_path)
    cats = {s.category for s in report.stubs}
    assert "DeprecationShim" in cats


def test_real_gap_fallthrough(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "plain.py",
        "def helper():\n    pass\n",
    )
    report = audit(tmp_path)
    cats = [s.category for s in report.stubs]
    assert "RealGap" in cats


# -- Stub-kind recognition --------------------------------------------------


@pytest.mark.parametrize(
    "body, expected_kind",
    [
        ("    pass\n", "Pass"),
        ("    ...\n", "Ellipsis"),
        ("    return None\n", "RetNone"),
        ("    return\n", "RetNone"),
        ('    """doc only"""\n', "DocOnly"),
        ("    raise NotImplementedError\n", "NotImpl"),
        ("    raise NotImplementedError('x')\n", "NotImpl"),
    ],
)
def test_stub_kinds(tmp_path: Path, body: str, expected_kind: str) -> None:
    _write(tmp_path, "k.py", f"def f():\n{body}")
    report = audit(tmp_path)
    assert any(s.stub_kind == expected_kind for s in report.stubs), (
        f"expected {expected_kind} in {[s.stub_kind for s in report.stubs]}"
    )


# -- Non-stub bodies ignored ------------------------------------------------


def test_non_stub_body_ignored(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "real.py",
        "def f(x):\n    return x + 1\n",
    )
    report = audit(tmp_path)
    assert len(report.stubs) == 0


def test_multi_statement_body_ignored(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "multi.py",
        "def f():\n    a = 1\n    return a\n",
    )
    report = audit(tmp_path)
    assert len(report.stubs) == 0


# -- Live apps_shared regression -------------------------------------------


def test_live_apps_shared_has_zero_real_gaps() -> None:
    """After plan 7dfe16 W3, apps_shared should carry zero RealGap stubs."""
    root = Path("apps_shared")
    if not root.exists():
        pytest.skip("apps_shared package not present")
    report = audit(root)
    real_gaps = [s for s in report.stubs if s.category == "RealGap"]
    assert len(real_gaps) == 0, (
        f"RealGap regression: {[(s.file_path, s.line_number, s.qualified_name) for s in real_gaps]}"
    )
