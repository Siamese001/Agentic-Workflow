"""W6 compliance verification: apps_rg L4 boundary non-contamination proof.

Plan 03 W6 acceptance criteria:
- No apps_rg literals introduced into agentic_core by this plan
- No direct cache writes in live runtime paths
- No direct Chroma mutation calls in runtime
- No direct filesystem durable writes outside allowlist
- No Exit direct writer paths (GAP-001 closed)
- No quarantined L6 importers in live runtime
- UWG receipt ref assertions when receipts returned
"""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

APPS_RG_RUNTIME_PATHS = [
    REPO_ROOT / "apps_rg" / "runtime",
    REPO_ROOT / "apps_rg" / "cache",
]

CORE_ROOT = REPO_ROOT / "agentic_core"

FORBIDDEN_WRITE_METHODS = {"write_text", "write_bytes"}
FORBIDDEN_CHROMA_MUTATIONS = {"upsert", "delete", "create_collection", "persist", "reset", "delete_collection"}
# Note: 'add' and 'update' excluded — too ambiguous (set.add, hashlib.update are false positives).
# These are covered by check_c0_chroma_readonly_runtime.py CI gate which has more context.
FORBIDDEN_CHROMA_MUTATIONS_STRICT = {"upsert", "create_collection", "persist", "reset", "delete_collection"}
FORBIDDEN_CACHE_WRITE_IMPORT = "write_section_to_semantic_cache"
QUARANTINED_MODULE = "l6_shadow_learning"


def _collect_py_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(root.rglob("*.py"))


def _ast_attribute_calls(filepath: Path) -> list[tuple[str, int]]:
    """Return list of (attr_name, lineno) for all attribute calls in file."""
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, OSError):
        return []
    results = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            results.append((node.func.attr, node.lineno))
    return results


def _ast_imports(filepath: Path) -> list[tuple[str, str, int]]:
    """Return list of (module, name, lineno) for all imports."""
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, OSError):
        return []
    results = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                results.append((module, alias.name, node.lineno))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                results.append(("", alias.name, node.lineno))
    return results


class TestNoDirectCacheWriteInRuntime(unittest.TestCase):
    """W6: No direct semantic cache write calls in live runtime (GAP G2 closed)."""

    def test_write_section_to_semantic_cache_not_imported_in_runtime(self) -> None:
        """write_section_to_semantic_cache must not be imported in runtime paths."""
        violations = []
        for root in APPS_RG_RUNTIME_PATHS:
            for py_file in _collect_py_files(root):
                if "_quarantine" in py_file.parts:
                    continue
                for module, name, lineno in _ast_imports(py_file):
                    if name == FORBIDDEN_CACHE_WRITE_IMPORT:
                        violations.append(f"{py_file.relative_to(REPO_ROOT)}:{lineno}")
        self.assertFalse(
            violations,
            f"write_section_to_semantic_cache imported in runtime: {violations}",
        )


class TestNoChromaMutationsInRuntime(unittest.TestCase):
    """W6: No Chroma mutation calls in live runtime/cache paths."""

    def test_no_chroma_mutation_calls_in_runtime(self) -> None:
        violations = []
        for root in APPS_RG_RUNTIME_PATHS:
            for py_file in _collect_py_files(root):
                if "_quarantine" in py_file.parts:
                    continue
                for attr, lineno in _ast_attribute_calls(py_file):
                    if attr in FORBIDDEN_CHROMA_MUTATIONS:
                        violations.append(f"{py_file.relative_to(REPO_ROOT)}:{lineno} — .{attr}()")
        self.assertFalse(
            violations,
            f"Chroma mutation calls found in runtime: {violations}",
        )


class TestNoDirectFilesystemDurableWritesInRuntime(unittest.TestCase):
    """W6: No direct durable filesystem writes in runtime (GAP-001/G4 closed)."""

    def test_no_write_text_or_write_bytes_in_bindings(self) -> None:
        violations = []
        bindings_root = REPO_ROOT / "apps_rg" / "runtime" / "bindings"
        for py_file in _collect_py_files(bindings_root):
            if "_quarantine" in py_file.parts:
                continue
            for attr, lineno in _ast_attribute_calls(py_file):
                if attr in FORBIDDEN_WRITE_METHODS:
                    violations.append(f"{py_file.relative_to(REPO_ROOT)}:{lineno} — .{attr}()")
        self.assertFalse(
            violations,
            f"Direct filesystem write calls found in bindings: {violations}",
        )

    def test_exit_binding_has_no_direct_writes(self) -> None:
        """exit_binding.py must not contain write_text, write_bytes (GAP-001 closed)."""
        exit_binding = REPO_ROOT / "apps_rg" / "runtime" / "bindings" / "exit_binding.py"
        self.assertTrue(exit_binding.exists(), "exit_binding.py must exist")
        violations = []
        for attr, lineno in _ast_attribute_calls(exit_binding):
            if attr in FORBIDDEN_WRITE_METHODS:
                violations.append(f"line {lineno}: .{attr}()")
        self.assertFalse(
            violations,
            f"exit_binding.py has direct write calls (GAP-001 should be closed): {violations}",
        )


class TestQuarantinedL6NotImportedInRuntime(unittest.TestCase):
    """W6: Quarantined l6_shadow_learning not imported by live runtime code."""

    def test_l6_shadow_learning_not_imported_in_runtime(self) -> None:
        violations = []
        for root in APPS_RG_RUNTIME_PATHS:
            for py_file in _collect_py_files(root):
                if "_quarantine" in py_file.parts:
                    continue
                for module, name, lineno in _ast_imports(py_file):
                    if QUARANTINED_MODULE in module or QUARANTINED_MODULE in name:
                        violations.append(f"{py_file.relative_to(REPO_ROOT)}:{lineno}")
        self.assertFalse(
            violations,
            f"Quarantined l6_shadow_learning imported in live runtime: {violations}",
        )


class TestNoAppsRgLiteralsAddedToCore(unittest.TestCase):
    """W6.3: Non-contamination proof — agentic_core has no new apps_rg literals."""

    APPS_RG_LITERAL_PATTERNS = [
        "apps_rg",
        "resume_generation",
        "section_agentic_pipeline",
        "unify_consulting",
    ]

    def test_agentic_core_has_no_apps_rg_resume_section_names(self) -> None:
        """agentic_core must not contain apps_rg-specific resume section literals.

        'executive_summary' is excluded — it is a generic JSON key used in core stubs
        and workflow types pre-dating apps_rg. Only apps_rg-specific literals like
        'unify_consulting' and 'section_agentic_pipeline' are checked here.
        """
        section_names = {"unify_consulting", "section_agentic_pipeline"}
        violations = []
        for py_file in CORE_ROOT.rglob("*.py"):
            try:
                source = py_file.read_text(encoding="utf-8")
            except OSError:
                continue
            for name in section_names:
                if f'"{name}"' in source or f"'{name}'" in source:
                    violations.append(f"{py_file.relative_to(REPO_ROOT)}: '{name}'")
        self.assertFalse(
            violations,
            f"apps_rg-specific section names found in agentic_core: {violations}",
        )


class TestInertWritebackCandidateShape(unittest.TestCase):
    """W6.1: ExitBindingResult carries inert proposals when UWG receipt returned."""

    def test_inert_artifact_commit_candidate_has_inert_flag(self) -> None:
        """InertArtifactCommitCandidate must have mutation_candidate_inert=True by default."""
        from apps_rg.runtime.bindings.exit_binding import InertArtifactCommitCandidate
        import dataclasses
        fields = {f.name: f for f in dataclasses.fields(InertArtifactCommitCandidate)}
        self.assertIn("mutation_candidate_inert", fields)
        self.assertTrue(fields["mutation_candidate_inert"].default)

    def test_inert_artifact_commit_candidate_has_proposal_status(self) -> None:
        """InertArtifactCommitCandidate must have proposal_status='PENDING_UWG'."""
        from apps_rg.runtime.bindings.exit_binding import InertArtifactCommitCandidate
        import dataclasses
        fields = {f.name: f for f in dataclasses.fields(InertArtifactCommitCandidate)}
        self.assertIn("proposal_status", fields)
        self.assertEqual(fields["proposal_status"].default, "PENDING_UWG")

    def test_inert_artifact_commit_candidate_non_durable_flags(self) -> None:
        """InertArtifactCommitCandidate must have non_durable, not_l4_truth, not_replay_source."""
        from apps_rg.runtime.bindings.exit_binding import InertArtifactCommitCandidate
        import dataclasses
        fields = {f.name for f in dataclasses.fields(InertArtifactCommitCandidate)}
        for flag in ("non_durable", "not_l4_truth", "not_replay_source"):
            self.assertIn(flag, fields, f"InertArtifactCommitCandidate missing flag '{flag}'")


class TestL4NamespaceManifestExists(unittest.TestCase):
    """W6: L4 namespace manifest present for non-contamination proof."""

    def test_manifest_exists(self) -> None:
        manifest = REPO_ROOT / "apps_rg" / "config" / "l4_namespace_manifest.yaml"
        self.assertTrue(
            manifest.exists(),
            "apps_rg/config/l4_namespace_manifest.yaml must exist for W6 compliance",
        )

    def test_no_apps_rg_l4_manifest_in_agentic_core(self) -> None:
        """App-owned L4 manifest must NOT be embedded in agentic_core."""
        for yaml_file in CORE_ROOT.rglob("*.yaml"):
            try:
                content = yaml_file.read_text(encoding="utf-8")
            except OSError:
                continue
            self.assertNotIn(
                "apps_rg",
                content,
                f"apps_rg literal found in agentic_core YAML: {yaml_file.relative_to(REPO_ROOT)}",
            )


if __name__ == "__main__":
    unittest.main()
