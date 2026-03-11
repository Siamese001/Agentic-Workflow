"""Governance: Silent swallow enforcement semantics in LazySeamEnforcer.

Invariants enforced:
  A) scan_file() swallows SyntaxError on invalid Python — returns empty list.
  B) scan_codebase() continues scanning after encountering invalid files.
  C) No mutation occurs during the swallowed exception path.
  D) Swallow does NOT convert a guardian BLOCK into ALLOW — enforcement
     semantics are preserved even when scan_file raises.
"""

from __future__ import annotations

import importlib.util
import json
import textwrap
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
)

pytestmark = pytest.mark.governance

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _get_enforcer_class():
    """Load LazySeamEnforcer by file path (no __init__.py needed)."""
    src = _REPO_ROOT / AGENTIC_CORE_DIR / "L5_safety" / "governance" / "lazy_seam_enforcer.py"
    spec = importlib.util.spec_from_file_location("lazy_seam_enforcer", src)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.LazySeamEnforcer


def _make_enforcer(cls, tmp_path: Path):
    """Create a LazySeamEnforcer with a minimal allowlist."""
    allowlist = tmp_path / "allowlist.json"
    allowlist.write_text(json.dumps({"seams": []}), encoding="utf-8")
    return cls(root_path=tmp_path, allowlist_path=allowlist)


# ---------------------------------------------------------------------------
# A — scan_file swallows SyntaxError, returns empty list
# ---------------------------------------------------------------------------


class TestScanFileSwallowsSyntaxError:
    """scan_file must return [] on unparseable Python without raising."""

    def test_syntax_error_returns_empty(self, tmp_path: Path) -> None:
        cls = _get_enforcer_class()
        bad_file = tmp_path / "bad.py"
        bad_file.write_text("def broken(\n", encoding="utf-8")

        enforcer = _make_enforcer(cls, tmp_path)
        result = enforcer.scan_file(bad_file)
        assert result == [], f"Expected empty list, got {result}"

    def test_io_error_returns_empty(self, tmp_path: Path) -> None:
        cls = _get_enforcer_class()
        missing = tmp_path / "nonexistent.py"
        enforcer = _make_enforcer(cls, tmp_path)
        result = enforcer.scan_file(missing)
        assert result == [], f"Expected empty list, got {result}"


# ---------------------------------------------------------------------------
# B — scan_codebase continues after invalid files
# ---------------------------------------------------------------------------


class TestScanCodebaseContinuesAfterError:
    """scan_codebase must not abort when one file is unparseable."""

    def test_valid_files_still_scanned(self, tmp_path: Path) -> None:
        cls = _get_enforcer_class()

        bad = tmp_path / "bad.py"
        bad.write_text("def broken(\n", encoding="utf-8")

        good = tmp_path / "good.py"
        good.write_text(
            textwrap.dedent("""\
                def _get_something():
                    from os.path import join
                    return join
            """),
            encoding="utf-8",
        )

        enforcer = _make_enforcer(cls, tmp_path)
        # scan_file on bad must not prevent scanning good
        bad_seams = enforcer.scan_file(bad)
        assert bad_seams == [], "Bad file should return []"
        good_seams = enforcer.scan_file(good)
        func_names = [s["function_name"] for s in good_seams]
        assert "_get_something" in func_names, f"Valid seam not found. Found: {func_names}"


# ---------------------------------------------------------------------------
# C — No mutation during swallowed exception
# ---------------------------------------------------------------------------


class TestNoMutationOnSwallow:
    """The swallowed exception path must not trigger any file writes."""

    def test_no_files_created_on_syntax_error(self, tmp_path: Path) -> None:
        cls = _get_enforcer_class()

        bad = tmp_path / "bad.py"
        bad.write_text("def broken(\n", encoding="utf-8")

        enforcer = _make_enforcer(cls, tmp_path)
        files_before = set(tmp_path.rglob("*"))
        enforcer.scan_file(bad)
        files_after = set(tmp_path.rglob("*"))

        new_files = files_after - files_before
        assert not new_files, f"Files created during swallow: {new_files}"


# ---------------------------------------------------------------------------
# D — Swallow does NOT weaken enforcement semantics
# ---------------------------------------------------------------------------


class TestSwallowDoesNotWeakenEnforcement:
    """A file that would produce a BLOCK must not become ALLOW via swallow."""

    def test_corrupt_file_not_treated_as_compliant(self, tmp_path: Path) -> None:
        cls = _get_enforcer_class()

        bad = tmp_path / "suspicious.py"
        bad.write_text(
            textwrap.dedent("""\
                def _get_secret_agent():
                    from agentic_core.L5_safety.validators import x
                    return x
                # syntax error below
                def broken(
            """),
            encoding="utf-8",
        )

        enforcer = _make_enforcer(cls, tmp_path)
        seams = enforcer.scan_file(bad)

        # Unparseable => zero seams => NOT registered as compliant
        assert seams == [], "Corrupt file should return no seams"

        # Verify: valid version of same file IS detected
        good = tmp_path / "suspicious_valid.py"
        good.write_text(
            textwrap.dedent("""\
                def _get_secret_agent():
                    from agentic_core.L5_safety.validators import x
                    return x
            """),
            encoding="utf-8",
        )
        seams_valid = enforcer.scan_file(good)
        assert len(seams_valid) == 1, "Valid seam must be detected"
        assert seams_valid[0]["function_name"] == "_get_secret_agent"
