"""EQ-12 — apply-patch validator tests."""

from __future__ import annotations

import pytest

from agentic_core.prompt_governance.validation.apply_patch_validator import (
    ApplyPatchReport,
    validate_apply_patch,
)


_CANONICAL = """Some preamble prose the model may add.

*** Begin Patch
*** Update File: agentic_core/foo.py
@@ def bar():
-    return 1
+    return 2
*** End Patch
"""


class TestCanonicalAccept:
    def test_canonical_envelope_is_ok(self) -> None:
        report = validate_apply_patch(_CANONICAL)
        assert report.ok is True
        assert report.reasons == []
        assert report.files == [("Update File", "agentic_core/foo.py")]

    def test_add_file_action_accepted(self) -> None:
        patch = "*** Begin Patch\n*** Add File: agentic_core/new.py\n@@\n+print('hi')\n*** End Patch\n"
        report = validate_apply_patch(patch)
        assert report.ok
        assert report.files == [("Add File", "agentic_core/new.py")]

    def test_delete_file_action_accepted(self) -> None:
        patch = "*** Begin Patch\n*** Delete File: agentic_core/old.py\n*** End Patch\n"
        report = validate_apply_patch(patch)
        assert report.ok
        assert report.files == [("Delete File", "agentic_core/old.py")]

    def test_multiple_files_accepted(self) -> None:
        patch = (
            "*** Begin Patch\n"
            "*** Update File: a.py\n"
            "@@\n-1\n+2\n"
            "*** Update File: b.py\n"
            "@@\n-3\n+4\n"
            "*** End Patch\n"
        )
        report = validate_apply_patch(patch)
        assert report.ok
        assert len(report.files) == 2


class TestRejectMalformed:
    def test_missing_begin_fence(self) -> None:
        report = validate_apply_patch("*** Update File: x.py\n*** End Patch")
        assert report.ok is False
        assert any("Begin Patch" in r for r in report.reasons)

    def test_missing_end_fence(self) -> None:
        report = validate_apply_patch("*** Begin Patch\n*** Update File: x.py")
        assert report.ok is False
        assert any("End Patch" in r for r in report.reasons)

    def test_empty_input(self) -> None:
        assert validate_apply_patch("").ok is False

    def test_non_string_input(self) -> None:
        # Defensive: callers sometimes pass None on error paths.
        assert validate_apply_patch(None).ok is False  # type: ignore[arg-type]

    def test_end_before_begin(self) -> None:
        report = validate_apply_patch("*** End Patch\n*** Update File: x.py\n*** Begin Patch")
        assert report.ok is False

    def test_envelope_with_no_file_action(self) -> None:
        report = validate_apply_patch("*** Begin Patch\nno file header here\n*** End Patch")
        assert report.ok is False
        assert any("no file action" in r for r in report.reasons)


class TestPathScopeEnforcement:
    def test_in_scope_path_accepted(self) -> None:
        report = validate_apply_patch(_CANONICAL, allowed_path_prefixes=("agentic_core/",))
        assert report.ok

    def test_out_of_scope_path_rejected(self) -> None:
        patch = "*** Begin Patch\n*** Update File: outside/evil.py\n*** End Patch"
        report = validate_apply_patch(patch, allowed_path_prefixes=("agentic_core/",))
        assert report.ok is False
        assert any("outside allowed prefixes" in r for r in report.reasons)

    def test_multiple_prefixes_any_match_accepts(self) -> None:
        patch = (
            "*** Begin Patch\n*** Update File: agentic_core/a.py\n*** Update File: tests/b.py\n*** End Patch"
        )
        report = validate_apply_patch(patch, allowed_path_prefixes=("agentic_core/", "tests/"))
        assert report.ok

    def test_empty_prefix_tuple_disables_scope_check(self) -> None:
        patch = "*** Begin Patch\n*** Update File: anything/goes.py\n*** End Patch"
        report = validate_apply_patch(patch, allowed_path_prefixes=())
        assert report.ok


class TestReportShape:
    def test_report_is_frozen_ish(self) -> None:
        report = ApplyPatchReport(ok=True)
        # Dataclass is mutable by default but tests hold the reference;
        # we verify list defaults are isolated between instances.
        r2 = ApplyPatchReport(ok=False)
        report.reasons.append("x")
        assert r2.reasons == []
