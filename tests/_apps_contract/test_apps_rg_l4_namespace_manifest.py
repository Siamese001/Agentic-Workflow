"""W3 tests: apps_rg L4 namespace manifest — shape, ACL, surface definitions.

Plan 03 W3.3 acceptance criteria:
- manifest exists at apps_rg/config/l4_namespace_manifest.yaml
- optional JSON schema validates manifest shape
- 10 required surfaces present
- All surfaces have required fields
- mutation_requires_uwg=True for durable surfaces
- Surfaces typed correctly
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

try:
    import yaml  # type: ignore[import]
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "apps_rg" / "config" / "l4_namespace_manifest.yaml"
SCHEMA_PATH = REPO_ROOT / "apps_rg" / "config" / "l4_namespace_manifest.schema.json"

REQUIRED_SURFACE_FIELDS = {
    "surface_id",
    "surface_type",
    "schema_version",
    "acl_profile",
    "replay_key_pattern",
    "retention_policy",
    "mutation_requires_uwg",
    "read_allowed",
    "write_allowed",
}

VALID_SURFACE_TYPES = {"cache", "vector_index", "filesystem", "in_memory", "telemetry"}

DURABLE_SURFACE_TYPES = {"cache", "vector_index", "filesystem"}


def _load_manifest() -> dict:
    if not _YAML_AVAILABLE:
        raise unittest.SkipTest("pyyaml not available")
    with MANIFEST_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


class TestL4NamespaceManifestExists(unittest.TestCase):
    """Manifest file exists and is parseable."""

    def test_manifest_file_exists(self) -> None:
        """l4_namespace_manifest.yaml must exist at apps_rg/config/."""
        self.assertTrue(
            MANIFEST_PATH.exists(),
            f"L4 namespace manifest not found at {MANIFEST_PATH.relative_to(REPO_ROOT)}",
        )

    def test_schema_file_exists(self) -> None:
        """Optional JSON schema must exist alongside the manifest."""
        self.assertTrue(
            SCHEMA_PATH.exists(),
            f"L4 namespace schema not found at {SCHEMA_PATH.relative_to(REPO_ROOT)}",
        )

    @unittest.skipUnless(_YAML_AVAILABLE, "pyyaml not available")
    def test_manifest_parseable(self) -> None:
        """Manifest must be valid YAML."""
        data = _load_manifest()
        self.assertIsInstance(data, dict)
        self.assertIn("l4_namespace", data)

    def test_schema_parseable(self) -> None:
        """JSON schema must be valid JSON."""
        with SCHEMA_PATH.open(encoding="utf-8") as f:
            schema = json.load(f)
        self.assertIn("$schema", schema)
        self.assertIn("properties", schema)


class TestL4NamespaceManifestShape(unittest.TestCase):
    """Manifest has required root structure."""

    def setUp(self) -> None:
        self.data = _load_manifest()
        self.ns = self.data["l4_namespace"]

    def test_app_id_is_apps_rg(self) -> None:
        self.assertEqual(self.ns["app_id"], "apps_rg")

    def test_version_present(self) -> None:
        self.assertIn("version", self.ns)
        self.assertRegex(self.ns["version"], r"^\d{4}-\d{2}-\d{2}$")

    def test_surfaces_is_list(self) -> None:
        self.assertIsInstance(self.ns.get("surfaces"), list)

    def test_surfaces_count_at_least_10(self) -> None:
        surfaces = self.ns.get("surfaces", [])
        self.assertGreaterEqual(
            len(surfaces), 10,
            f"Expected >= 10 surfaces, found {len(surfaces)}",
        )

    def test_surface_ids_unique(self) -> None:
        surfaces = self.ns.get("surfaces", [])
        ids = [s.get("surface_id") for s in surfaces]
        self.assertEqual(len(ids), len(set(ids)), "Duplicate surface_id found")


class TestL4SurfaceRequiredFields(unittest.TestCase):
    """Each surface has all required fields with correct types."""

    def setUp(self) -> None:
        data = _load_manifest()
        self.surfaces = data["l4_namespace"]["surfaces"]

    def test_all_surfaces_have_required_fields(self) -> None:
        for surface in self.surfaces:
            sid = surface.get("surface_id", "<unknown>")
            for field in REQUIRED_SURFACE_FIELDS:
                self.assertIn(
                    field, surface,
                    f"Surface '{sid}' missing required field '{field}'",
                )

    def test_surface_types_valid(self) -> None:
        for surface in self.surfaces:
            sid = surface.get("surface_id", "<unknown>")
            stype = surface.get("surface_type", "")
            self.assertIn(
                stype, VALID_SURFACE_TYPES,
                f"Surface '{sid}' has invalid surface_type '{stype}'",
            )

    def test_mutation_requires_uwg_is_bool(self) -> None:
        for surface in self.surfaces:
            sid = surface.get("surface_id", "<unknown>")
            val = surface.get("mutation_requires_uwg")
            self.assertIsInstance(val, bool, f"Surface '{sid}' mutation_requires_uwg must be bool")

    def test_read_write_allowed_are_bools(self) -> None:
        for surface in self.surfaces:
            sid = surface.get("surface_id", "<unknown>")
            self.assertIsInstance(surface.get("read_allowed"), bool, f"Surface '{sid}' read_allowed must be bool")
            self.assertIsInstance(surface.get("write_allowed"), bool, f"Surface '{sid}' write_allowed must be bool")


class TestL4DurableSurfacePolicy(unittest.TestCase):
    """Durable surfaces (cache/vector_index/filesystem) require UWG mediation."""

    def setUp(self) -> None:
        data = _load_manifest()
        self.surfaces = data["l4_namespace"]["surfaces"]

    def test_durable_surfaces_require_uwg(self) -> None:
        """cache, vector_index, filesystem surfaces must have mutation_requires_uwg=True.

        Exception: surfaces with retention_policy='build_time' are written at build/authoring
        time (not runtime) and are read-only during execution, so mutation_requires_uwg=False
        is correct for them.
        """
        for surface in self.surfaces:
            sid = surface.get("surface_id", "<unknown>")
            stype = surface.get("surface_type", "")
            retention = surface.get("retention_policy", "")
            if stype in DURABLE_SURFACE_TYPES and retention != "build_time":
                self.assertTrue(
                    surface.get("mutation_requires_uwg"),
                    f"Durable surface '{sid}' (type={stype}) must have mutation_requires_uwg=True",
                )

    def test_durable_surfaces_write_not_allowed_directly(self) -> None:
        """Durable surfaces should not be directly writable by runtime — UWG mediates."""
        for surface in self.surfaces:
            sid = surface.get("surface_id", "<unknown>")
            stype = surface.get("surface_type", "")
            if stype in DURABLE_SURFACE_TYPES:
                self.assertFalse(
                    surface.get("write_allowed"),
                    f"Durable surface '{sid}' write_allowed must be False (UWG-mediated only)",
                )

    def test_in_memory_surfaces_no_uwg_required(self) -> None:
        """in_memory surfaces are session-scoped and do not require UWG."""
        for surface in self.surfaces:
            stype = surface.get("surface_type", "")
            if stype == "in_memory":
                self.assertFalse(
                    surface.get("mutation_requires_uwg"),
                    f"in_memory surface '{surface.get('surface_id')}' should not require UWG",
                )

    def test_known_surfaces_present(self) -> None:
        """Known required surface IDs from plan are present."""
        required_ids = {
            "semantic_cache",
            "chroma_retrieval",
            "artifact_resume_json",
            "artifact_run_metadata",
            "c0_evidence_store",
            "exit_commit_candidates",
            "cache_write_proposals",
        }
        surface_ids = {s.get("surface_id") for s in self.surfaces}
        missing = required_ids - surface_ids
        self.assertFalse(missing, f"Required surface IDs missing: {missing}")


if __name__ == "__main__":
    unittest.main()
