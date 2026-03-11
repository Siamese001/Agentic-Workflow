"""V15 P10.4 — Incident Bundle Generator Tests.

Validates deterministic bundle creation, idempotency, safety checks,
force mode, and sentinel-based user content preservation.
"""

from __future__ import annotations

from ops_scripts.incident.create_v15_incident_bundle import (
    BUNDLE_FILES,
    SENTINEL,
    create_bundle,
)

INCIDENT_ID = "INC-TEST-001"


# ===========================================================================
# A) First Run — Creates Exact Tree
# ===========================================================================


class TestFirstRun:
    """First run on empty dir creates the full bundle."""

    def test_exit_zero(self, tmp_path):
        out = tmp_path / "bundle"
        code, msgs = create_bundle(out, INCIDENT_ID)
        assert code == 0

    def test_readme_created(self, tmp_path):
        out = tmp_path / "bundle"
        create_bundle(out, INCIDENT_ID)
        readme = out / "README.md"
        assert readme.is_file()
        text = readme.read_text(encoding="utf-8")
        assert INCIDENT_ID in text
        assert SENTINEL in text

    def test_all_dirs_created(self, tmp_path):
        out = tmp_path / "bundle"
        create_bundle(out, INCIDENT_ID)
        for subdir in ["inputs", "artifacts", "analysis"]:
            assert (out / subdir).is_dir()

    def test_all_files_created(self, tmp_path):
        out = tmp_path / "bundle"
        create_bundle(out, INCIDENT_ID)
        for rel_path in BUNDLE_FILES:
            assert (out / rel_path).is_file(), f"Missing: {rel_path}"

    def test_all_files_have_sentinel(self, tmp_path):
        out = tmp_path / "bundle"
        create_bundle(out, INCIDENT_ID)
        for rel_path in BUNDLE_FILES:
            text = (out / rel_path).read_text(encoding="utf-8")
            assert SENTINEL in text, f"Missing sentinel in {rel_path}"

    def test_readme_contains_checklist(self, tmp_path):
        out = tmp_path / "bundle"
        create_bundle(out, INCIDENT_ID)
        text = (out / "README.md").read_text(encoding="utf-8")
        assert "test_v15_p1_compliance" in text
        assert "test_v15_p6_refinement" in text

    def test_incident_id_in_readme(self, tmp_path):
        out = tmp_path / "bundle"
        create_bundle(out, INCIDENT_ID)
        text = (out / "README.md").read_text(encoding="utf-8")
        assert f"`{INCIDENT_ID}`" in text

    def test_analysis_files_present(self, tmp_path):
        out = tmp_path / "bundle"
        create_bundle(out, INCIDENT_ID)
        for name in ["triage.md", "root_cause.md", "remediation.md"]:
            assert (out / "analysis" / name).is_file()


# ===========================================================================
# B) Idempotency — Second Run No Changes
# ===========================================================================


class TestIdempotency:
    """Second run on existing bundle makes no changes."""

    def test_second_run_exit_zero(self, tmp_path):
        out = tmp_path / "bundle"
        create_bundle(out, INCIDENT_ID)
        code, msgs = create_bundle(out, INCIDENT_ID)
        assert code == 0
        assert any("idempotent" in m.lower() for m in msgs)

    def test_file_bytes_unchanged(self, tmp_path):
        out = tmp_path / "bundle"
        create_bundle(out, INCIDENT_ID)

        # Capture all file bytes
        before = {}
        for rel_path in BUNDLE_FILES:
            before[rel_path] = (out / rel_path).read_bytes()
        before["README.md"] = (out / "README.md").read_bytes()

        # Second run
        create_bundle(out, INCIDENT_ID)

        # Compare
        for rel_path, data in before.items():
            assert (out / rel_path).read_bytes() == data, f"Changed: {rel_path}"


# ===========================================================================
# C) Non-Empty Dir Without --force Exits 2
# ===========================================================================


class TestNonEmptyDirSafety:
    """Non-empty dir without --force must exit 2."""

    def test_non_bundle_dir_exits_2(self, tmp_path):
        out = tmp_path / "existing"
        out.mkdir()
        (out / "user_file.txt").write_text("user content", encoding="utf-8")

        code, msgs = create_bundle(out, INCIDENT_ID)
        assert code == 2
        assert any("--force" in m for m in msgs)

    def test_non_bundle_dir_files_untouched(self, tmp_path):
        out = tmp_path / "existing"
        out.mkdir()
        user_file = out / "user_file.txt"
        user_file.write_text("user content", encoding="utf-8")

        create_bundle(out, INCIDENT_ID)
        assert user_file.read_text(encoding="utf-8") == "user content"


# ===========================================================================
# D) --force Mode
# ===========================================================================


class TestForceMode:
    """--force overwrites placeholders in non-bundle dirs."""

    def test_force_on_non_bundle_dir(self, tmp_path):
        out = tmp_path / "existing"
        out.mkdir()
        (out / "user_file.txt").write_text("user content", encoding="utf-8")

        code, msgs = create_bundle(out, INCIDENT_ID, force=True)
        assert code == 0
        assert (out / "README.md").is_file()

    def test_force_preserves_existing_user_file(self, tmp_path):
        out = tmp_path / "existing"
        out.mkdir()
        user_file = out / "user_file.txt"
        user_file.write_text("user content", encoding="utf-8")

        create_bundle(out, INCIDENT_ID, force=True)
        assert user_file.read_text(encoding="utf-8") == "user content"


# ===========================================================================
# E) Sentinel-Based Content Preservation
# ===========================================================================


class TestSentinelPreservation:
    """User-edited files (sentinel removed) must not be overwritten."""

    def test_user_edited_triage_preserved(self, tmp_path):
        out = tmp_path / "bundle"
        create_bundle(out, INCIDENT_ID)

        # Simulate user editing triage.md (removing sentinel)
        triage = out / "analysis" / "triage.md"
        triage.write_text("# My custom triage\nReal analysis here.", encoding="utf-8")

        # Re-run (idempotent path won't even enter file-writing)
        # But test with force=True to prove sentinel protection
        create_bundle(out, INCIDENT_ID, force=True)

        # force=True overwrites files WITH sentinel but _write_if_placeholder
        # checks: sentinel in existing => overwrite; else keep
        text = triage.read_text(encoding="utf-8")
        assert "My custom triage" in text
        assert SENTINEL not in text

    def test_placeholder_file_overwritten_by_force(self, tmp_path):
        out = tmp_path / "bundle"
        create_bundle(out, INCIDENT_ID)

        # File still has sentinel — force should overwrite
        triage = out / "analysis" / "triage.md"
        assert SENTINEL in triage.read_text(encoding="utf-8")

        create_bundle(out, INCIDENT_ID, force=True)
        assert SENTINEL in triage.read_text(encoding="utf-8")


# ===========================================================================
# F) Determinism
# ===========================================================================


class TestDeterminism:
    """Same inputs produce identical bundle bytes."""

    def test_two_bundles_identical(self, tmp_path):
        out1 = tmp_path / "b1"
        out2 = tmp_path / "b2"
        create_bundle(out1, INCIDENT_ID)
        create_bundle(out2, INCIDENT_ID)

        all_files = ["README.md"] + sorted(BUNDLE_FILES.keys())
        for rel_path in all_files:
            b1 = (out1 / rel_path).read_bytes()
            b2 = (out2 / rel_path).read_bytes()
            assert b1 == b2, f"Non-deterministic: {rel_path}"

    def test_different_incident_id_different_readme(self, tmp_path):
        out1 = tmp_path / "b1"
        out2 = tmp_path / "b2"
        create_bundle(out1, "INC-A")
        create_bundle(out2, "INC-B")

        r1 = (out1 / "README.md").read_text(encoding="utf-8")
        r2 = (out2 / "README.md").read_text(encoding="utf-8")
        assert r1 != r2
        assert "INC-A" in r1
        assert "INC-B" in r2
