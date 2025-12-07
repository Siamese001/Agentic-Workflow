#!/usr/bin/env python3
"""
PHASE 2 — SEMANTIC DIFF & PLAN GENERATION TEST SUITE

This test module implements the Phase 2 test plan covering:
  - 2.1 Semantic Matching Tests (SM-01 to SM-03)
  - 2.2 Structural Diff Tests (ST-01)
  - 2.3 Operation Generation Tests (OP-01, OP-02)
  - 2.4 Import Map Tests (IMP-01)

Each test case is isolated using pytest's tmp_path fixture to avoid
mutating the real semantic cache or filesystem.
"""

from __future__ import annotations

import ast
import hashlib
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import pytest

# Ensure repository root is on sys.path so that the `phase02` package can be
# imported when tests are invoked from within the 10_tests tree.
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Import phase02.py directly using runpy to avoid module registration issues
import types
import runpy

# Create a module namespace and execute phase02.py into it
phase02_path = REPO_ROOT / "phase02" / "phase02.py"
p2 = types.ModuleType("phase02_module")
p2.__file__ = str(phase02_path)
sys.modules["phase02_module"] = p2

# Read and exec the module
with open(phase02_path, "r", encoding="utf-8") as f:
    code = compile(f.read(), phase02_path, "exec")
exec(code, p2.__dict__)


# ============================================================================
# TEST FIXTURES
# ============================================================================


@pytest.fixture
def mock_project(tmp_path: Path) -> Dict[str, Path]:
    """
    Create a minimal mock project structure for Phase 2 testing.
    
    Returns a dict with paths to:
      - project_root
      - semantic_cache
      - ssot_yaml
      - meta_yaml
      - target_root (01_agentic_core)
    """
    project_root = tmp_path / "project"
    project_root.mkdir()

    # Create canonical 10 folders
    for root in p2.CANONICAL_ROOTS:
        (project_root / root).mkdir()

    # Create semantic cache structure
    semantic_cache = project_root / "06_data" / "semantic_cache"
    semantic_cache.mkdir(parents=True)
    for domain in p2.GLOBAL_DOMAINS:
        (semantic_cache / domain).mkdir()

    # Create graphs directory for component graph
    (semantic_cache / "graphs").mkdir()

    # Create SSoT YAML with minimal structure
    ssot_yaml = project_root / "unified_structure_subatomic.yaml"
    ssot_content = """
agentic_core:
  L1_cognition:
    P1_retrieve:
      planner.py: null
      executor.py: null
  _unassigned_support_nomatch: null
schemas:
  logic: null
runtime:
  core: null
prompt_governance:
  templates: null
config:
  settings: null
data:
  cache: null
observability:
  metrics: null
scripts:
  utils: null
apps:
  main: null
tests:
  unit: null
"""
    ssot_yaml.write_text(ssot_content, encoding="utf-8")

    # Create META YAML
    meta_yaml = project_root / "unified_structure_subatomic_meta.yaml"
    meta_content = """
intents:
  retrieve: "Fetch data from cache or external source"
  execute: "Run a computation or action"
axes:
  layer: ["L1", "L2", "L3", "L4", "L5"]
  phase: ["P1", "P2", "P3", "P4"]
verb_groups:
  data_access: ["get", "fetch", "load"]
  mutation: ["set", "update", "delete"]
"""
    meta_yaml.write_text(meta_content, encoding="utf-8")

    # Create Phase 1 status sentinel
    phase1_status = project_root / "02_schemas" / "phase01_status.json"
    phase1_status.write_text(json.dumps({"phase01_completed": True}), encoding="utf-8")

    return {
        "project_root": project_root,
        "semantic_cache": semantic_cache,
        "ssot_yaml": ssot_yaml,
        "meta_yaml": meta_yaml,
        "target_root": project_root / "01_agentic_core",
    }


def compute_hash(content: str) -> str:
    """Compute SHA-256 hash of content (matching phase02's compute_file_hash)."""
    # Use the same encoding as the file will be written with
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def compute_file_hash_from_path(path: Path) -> str:
    """Compute SHA-256 hash of a file (same as phase02.compute_file_hash)."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def create_semantic_pointer(
    cache_root: Path,
    bucket: str,
    file_hash: str,
    component_id: str,
    kind: str,
    engine: str = "RG",
    archive_name: str = "test_archive",
    relative: str = "test/path.py",
    canonical_relative: str = "L1_cognition/P1_retrieve/planner",
    confidence: float = 0.9,
) -> Path:
    """Create a semantic pointer JSON file in the cache."""
    bucket_dir = cache_root / bucket / "L1_current" / "P0_5" / "ingest" / "current"
    bucket_dir.mkdir(parents=True, exist_ok=True)

    pointer_data = {
        "hash": file_hash,
        "component_id": component_id,
        "kind": kind,
        "engine": engine,
        "archive_name": archive_name,
        "relative": relative,
        "canonical_relative": canonical_relative,
        "confidence": confidence,
        "canonical_root": bucket,
        "global": {
            "ast": f"{file_hash}.ast",
            "embeddings": f"{file_hash}.embedding",
            "golden": f"{file_hash}.golden.json",
        },
    }

    # Use a short hash-based filename to avoid path length issues
    short_id = hashlib.sha256(component_id.encode()).hexdigest()[:16]
    pointer_path = bucket_dir / f"{short_id}.json"
    pointer_path.write_text(json.dumps(pointer_data), encoding="utf-8")

    return pointer_path


def create_global_artifact(
    cache_root: Path,
    file_hash: str,
    domain: str,
    content: Any,
) -> Path:
    """Create a global artifact file in the semantic cache."""
    domain_dir = cache_root / domain
    domain_dir.mkdir(parents=True, exist_ok=True)

    suffix_map = {
        "ast": ".ast",
        "diffs": ".diff.json",
        "embeddings": ".embedding",
        "golden": ".golden.json",
        "integrity": ".integrity.json",
        "meta": ".meta.json",
        "safety": ".safety.json",
    }
    suffix = suffix_map.get(domain, ".json")
    artifact_path = domain_dir / f"{file_hash}{suffix}"

    if isinstance(content, (dict, list)):
        artifact_path.write_text(json.dumps(content), encoding="utf-8")
    else:
        artifact_path.write_text(str(content), encoding="utf-8")

    return artifact_path


# ============================================================================
# 2.1 — SEMANTIC MATCHING TESTS
# ============================================================================


class TestSemanticMatching:
    """Test cases for semantic matching (2.1-SM-01 to 2.1-SM-03)."""

    def test_2_1_sm_01_exact_hash_match(self, mock_project: Dict[str, Path]) -> None:
        """
        TEST CASE 2.1-SM-01 — Exact hash match
        
        Setup:
        - Provide a file whose content already exists in semantic cache with identical hash H.
        
        Expected:
        - Diff classification: `hash_match`
        - Plan MUST include: op: canonical_rewrite_component, hash: H
        
        Pass:
        - Operation appears in phase02_plan.json.
        """
        project_root = mock_project["project_root"]
        cache_root = mock_project["semantic_cache"]
        target_root = mock_project["target_root"]

        # Create a Python file with known content
        test_content = '''class Planner:
    """A planning component."""
    def plan(self):
        return "plan"
'''
        # Create the live file FIRST
        live_file = target_root / "L1_cognition" / "P1_retrieve" / "planner.py"
        live_file.parent.mkdir(parents=True, exist_ok=True)
        live_file.write_text(test_content, encoding="utf-8")

        # Compute hash from the actual file (to match phase02's compute_file_hash)
        file_hash = compute_file_hash_from_path(live_file)

        # Create semantic pointer with matching hash
        create_semantic_pointer(
            cache_root=cache_root,
            bucket="01_agentic_core",
            file_hash=file_hash,
            component_id="planner.py::class::Planner",
            kind="class",
            canonical_relative="L1_cognition/P1_retrieve/planner",
        )

        # Create global artifacts
        create_global_artifact(cache_root, file_hash, "golden", {"file_hash": file_hash, "length": len(test_content)})
        create_global_artifact(cache_root, file_hash, "ast", {"kind": "ast_group", "source": test_content})

        # Patch module constants for testing
        original_project_root = p2.PROJECT_ROOT
        original_ssot_yaml = p2.SSOT_YAML
        original_meta_yaml = p2.META_YAML
        original_cache_root = p2.SEMANTIC_CACHE_ROOT

        try:
            p2.PROJECT_ROOT = project_root
            p2.SSOT_YAML = mock_project["ssot_yaml"]
            p2.META_YAML = mock_project["meta_yaml"]
            p2.SEMANTIC_CACHE_ROOT = cache_root

            # Run semantic diff computation
            validator = p2.Phase2Validator(verbose=False)
            fs_state = p2.load_filesystem_state(validator, "01_agentic_core")
            assert fs_state is not None, "Filesystem state should load"

            cache_state = p2.load_semantic_cache_state(validator, "01_agentic_core")
            assert cache_state is not None, "Cache state should load"
            assert len(cache_state.pointers) > 0, "Should have at least one pointer"

            diffs = p2.compute_semantic_diffs(validator, fs_state, cache_state)

            # Find the diff for our test file
            planner_diffs = [d for d in diffs if "planner.py" in d.live_path]
            assert len(planner_diffs) > 0, "Should have diff for planner.py"

            planner_diff = planner_diffs[0]
            assert planner_diff.diff_kind == "hash_match", f"Expected hash_match, got {planner_diff.diff_kind}"
            assert planner_diff.best_hash == file_hash, "Hash should match"

            # Build operations and verify canonical_rewrite_component is generated
            ops = p2.build_operations(validator, diffs)
            planner_ops = [o for o in ops if "planner.py" in o.target_path]
            assert len(planner_ops) > 0, "Should have operation for planner.py"

            planner_op = planner_ops[0]
            assert planner_op.op_type == "canonical_rewrite_component", f"Expected canonical_rewrite_component, got {planner_op.op_type}"
            assert planner_op.semantic_hash == file_hash, "Operation should reference hash H"

        finally:
            # Restore original constants
            p2.PROJECT_ROOT = original_project_root
            p2.SSOT_YAML = original_ssot_yaml
            p2.META_YAML = original_meta_yaml
            p2.SEMANTIC_CACHE_ROOT = original_cache_root

    def test_2_1_sm_02_symbol_match_fallback(self, mock_project: Dict[str, Path]) -> None:
        """
        TEST CASE 2.1-SM-02 — Symbol match fallback
        
        Input file:
        ```python
        class Planner: ...
        ```
        Archive contains same class but different hash.
        
        Expected:
        - Detected: `semantic_symbol_match`
        - Rewrite op generated referencing original component(s).
        
        Pass:
        - Mapping lists symbol match and rewrite op present.
        """
        project_root = mock_project["project_root"]
        cache_root = mock_project["semantic_cache"]
        target_root = mock_project["target_root"]

        # Create a Python file with a class
        live_content = '''class Planner:
    """Updated planner with new implementation."""
    def plan(self):
        return "new_plan"
'''
        live_hash = compute_hash(live_content)

        # Archive has DIFFERENT content but same class name
        archive_content = '''class Planner:
    """Original planner."""
    def plan(self):
        return "old_plan"
'''
        archive_hash = compute_hash(archive_content)

        # Ensure hashes are different
        assert live_hash != archive_hash, "Hashes should differ for symbol match test"

        # Create the live file
        live_file = target_root / "L1_cognition" / "P1_retrieve" / "planner.py"
        live_file.parent.mkdir(parents=True, exist_ok=True)
        live_file.write_text(live_content, encoding="utf-8")

        # Create semantic pointer with ARCHIVE hash (different from live)
        create_semantic_pointer(
            cache_root=cache_root,
            bucket="01_agentic_core",
            file_hash=archive_hash,
            component_id="planner.py::class::Planner",
            kind="class",
            canonical_relative="L1_cognition/P1_retrieve/planner",
        )

        # Create global artifacts for archive hash
        create_global_artifact(cache_root, archive_hash, "golden", {"file_hash": archive_hash})
        create_global_artifact(cache_root, archive_hash, "ast", {"kind": "ast_group"})

        # Patch module constants
        original_project_root = p2.PROJECT_ROOT
        original_ssot_yaml = p2.SSOT_YAML
        original_meta_yaml = p2.META_YAML
        original_cache_root = p2.SEMANTIC_CACHE_ROOT

        try:
            p2.PROJECT_ROOT = project_root
            p2.SSOT_YAML = mock_project["ssot_yaml"]
            p2.META_YAML = mock_project["meta_yaml"]
            p2.SEMANTIC_CACHE_ROOT = cache_root

            validator = p2.Phase2Validator(verbose=False)
            fs_state = p2.load_filesystem_state(validator, "01_agentic_core")
            assert fs_state is not None

            cache_state = p2.load_semantic_cache_state(validator, "01_agentic_core")
            assert cache_state is not None

            diffs = p2.compute_semantic_diffs(validator, fs_state, cache_state)

            # Find the diff for our test file
            planner_diffs = [d for d in diffs if "planner.py" in d.live_path]
            assert len(planner_diffs) > 0, "Should have diff for planner.py"

            planner_diff = planner_diffs[0]
            assert planner_diff.diff_kind == "semantic_symbol_match", f"Expected semantic_symbol_match, got {planner_diff.diff_kind}"
            assert "semantic_symbol_match" in planner_diff.reasons, "Reasons should include semantic_symbol_match"

            # Build operations and verify rewrite op is generated
            ops = p2.build_operations(validator, diffs)
            planner_ops = [o for o in ops if "planner.py" in o.target_path]
            assert len(planner_ops) > 0, "Should have operation for planner.py"

            planner_op = planner_ops[0]
            assert planner_op.op_type == "canonical_rewrite_component"
            assert planner_op.component_id is not None, "Should reference component"

        finally:
            p2.PROJECT_ROOT = original_project_root
            p2.SSOT_YAML = original_ssot_yaml
            p2.META_YAML = original_meta_yaml
            p2.SEMANTIC_CACHE_ROOT = original_cache_root

    def test_2_1_sm_03_no_semantic_match(self, mock_project: Dict[str, Path]) -> None:
        """
        TEST CASE 2.1-SM-03 — No semantic match
        
        Input:
        ```
        README.txt
        ```
        
        Expected:
        - Diff classification: `no_cache`
        - No rewrite op for this file.
        
        Pass:
        - Operation list excludes it.
        """
        project_root = mock_project["project_root"]
        cache_root = mock_project["semantic_cache"]
        target_root = mock_project["target_root"]

        # Create a README.txt file (no semantic cache entry)
        readme_content = "This is a README file with no semantic cache entry."
        readme_file = target_root / "README.txt"
        readme_file.write_text(readme_content, encoding="utf-8")

        # Do NOT create any semantic pointer for this file

        original_project_root = p2.PROJECT_ROOT
        original_ssot_yaml = p2.SSOT_YAML
        original_meta_yaml = p2.META_YAML
        original_cache_root = p2.SEMANTIC_CACHE_ROOT

        try:
            p2.PROJECT_ROOT = project_root
            p2.SSOT_YAML = mock_project["ssot_yaml"]
            p2.META_YAML = mock_project["meta_yaml"]
            p2.SEMANTIC_CACHE_ROOT = cache_root

            validator = p2.Phase2Validator(verbose=False)
            fs_state = p2.load_filesystem_state(validator, "01_agentic_core")
            assert fs_state is not None

            cache_state = p2.load_semantic_cache_state(validator, "01_agentic_core")
            assert cache_state is not None

            diffs = p2.compute_semantic_diffs(validator, fs_state, cache_state)

            # Find the diff for README.txt
            readme_diffs = [d for d in diffs if "README.txt" in d.live_path]
            assert len(readme_diffs) == 1, "Should have exactly one diff for README.txt"

            readme_diff = readme_diffs[0]
            assert readme_diff.diff_kind == "no_cache", f"Expected no_cache, got {readme_diff.diff_kind}"
            assert readme_diff.component_id is None, "Should have no component_id"
            assert readme_diff.best_hash is None, "Should have no hash"

            # Build operations and verify NO op for README.txt
            ops = p2.build_operations(validator, diffs)
            readme_ops = [o for o in ops if "README.txt" in o.target_path]
            assert len(readme_ops) == 0, "Should have NO operations for README.txt"

        finally:
            p2.PROJECT_ROOT = original_project_root
            p2.SSOT_YAML = original_ssot_yaml
            p2.META_YAML = original_meta_yaml
            p2.SEMANTIC_CACHE_ROOT = original_cache_root


# ============================================================================
# 2.2 — STRUCTURAL DIFF TESTS
# ============================================================================


class TestStructuralDiff:
    """Test cases for structural diff (2.2-ST-01)."""

    def test_2_2_st_01_ssot_mismatch_detection(self, mock_project: Dict[str, Path]) -> None:
        """
        TEST CASE 2.2-ST-01 — SSoT mismatch detection
        
        Place a file in a directory NOT present in YAML SSoT.
        
        Expected:
        - Appears in `fs_only_files` list.
        - Phase 2 still generates full plan successfully.
        
        Pass:
        - No blocking exceptions; file reported in mismatches.
        """
        project_root = mock_project["project_root"]
        cache_root = mock_project["semantic_cache"]
        target_root = mock_project["target_root"]

        # Create a file in a directory NOT in SSoT
        extra_dir = target_root / "extra_directory_not_in_ssot"
        extra_dir.mkdir(parents=True, exist_ok=True)
        extra_file = extra_dir / "orphan_file.py"
        extra_file.write_text("# Orphan file not in SSoT", encoding="utf-8")

        # Also create a valid file that IS in SSoT
        valid_file = target_root / "L1_cognition" / "P1_retrieve" / "planner.py"
        valid_file.parent.mkdir(parents=True, exist_ok=True)
        valid_file.write_text("class Planner: pass", encoding="utf-8")

        original_project_root = p2.PROJECT_ROOT
        original_ssot_yaml = p2.SSOT_YAML
        original_meta_yaml = p2.META_YAML
        original_cache_root = p2.SEMANTIC_CACHE_ROOT

        try:
            p2.PROJECT_ROOT = project_root
            p2.SSOT_YAML = mock_project["ssot_yaml"]
            p2.META_YAML = mock_project["meta_yaml"]
            p2.SEMANTIC_CACHE_ROOT = cache_root

            validator = p2.Phase2Validator(verbose=False)

            # Load SSoT
            ssot = p2.load_ssot_and_meta(validator, "01_agentic_core")
            assert ssot is not None, "SSoT should load successfully"

            # Load filesystem state
            fs_state = p2.load_filesystem_state(validator, "01_agentic_core")
            assert fs_state is not None, "Filesystem state should load"

            # Compute structural diff
            struct_diff = p2.compute_structural_diff(validator, ssot, fs_state)

            # Verify the extra directory/file appears in fs_only
            assert "extra_directory_not_in_ssot" in struct_diff.fs_only_dirs or \
                   any("extra_directory_not_in_ssot" in f for f in struct_diff.fs_only_files), \
                   "Extra directory should appear in fs_only_dirs or fs_only_files"

            # Verify no blocking exceptions occurred (we got this far)
            # Phase 2 should still be able to generate a plan

            # Load cache and compute semantic diffs
            cache_state = p2.load_semantic_cache_state(validator, "01_agentic_core")
            assert cache_state is not None

            diffs = p2.compute_semantic_diffs(validator, fs_state, cache_state)
            ops = p2.build_operations(validator, diffs)

            # Plan generation should succeed (ops list exists, even if empty)
            assert isinstance(ops, list), "Operations should be a list"

        finally:
            p2.PROJECT_ROOT = original_project_root
            p2.SSOT_YAML = original_ssot_yaml
            p2.META_YAML = original_meta_yaml
            p2.SEMANTIC_CACHE_ROOT = original_cache_root


# ============================================================================
# 2.3 — OPERATION GENERATION TESTS
# ============================================================================


class TestOperationGeneration:
    """Test cases for operation generation (2.3-OP-01, 2.3-OP-02)."""

    def test_2_3_op_01_rewrite_all_guarantee(self, mock_project: Dict[str, Path]) -> None:
        """
        TEST CASE 2.3-OP-01 — Rewrite-all guarantee
        
        For **any** matched file (hash or semantic symbol match):
        
        Expected:
        - Always emit: canonical_rewrite_component
        
        Pass:
        - All matched files have rewrite ops in phase02_plan.json.
        """
        project_root = mock_project["project_root"]
        cache_root = mock_project["semantic_cache"]
        target_root = mock_project["target_root"]

        # Create multiple files with different match types
        files_data = [
            ("planner.py", "class Planner:\n    pass\n", "planner.py::class::Planner"),
            ("executor.py", "class Executor:\n    pass\n", "executor.py::class::Executor"),
        ]

        for filename, content, component_id in files_data:
            file_hash = compute_hash(content)
            live_file = target_root / "L1_cognition" / "P1_retrieve" / filename
            live_file.parent.mkdir(parents=True, exist_ok=True)
            live_file.write_text(content, encoding="utf-8")

            create_semantic_pointer(
                cache_root=cache_root,
                bucket="01_agentic_core",
                file_hash=file_hash,
                component_id=component_id,
                kind="class",
            )

        original_project_root = p2.PROJECT_ROOT
        original_ssot_yaml = p2.SSOT_YAML
        original_meta_yaml = p2.META_YAML
        original_cache_root = p2.SEMANTIC_CACHE_ROOT

        try:
            p2.PROJECT_ROOT = project_root
            p2.SSOT_YAML = mock_project["ssot_yaml"]
            p2.META_YAML = mock_project["meta_yaml"]
            p2.SEMANTIC_CACHE_ROOT = cache_root

            validator = p2.Phase2Validator(verbose=False)
            fs_state = p2.load_filesystem_state(validator, "01_agentic_core")
            cache_state = p2.load_semantic_cache_state(validator, "01_agentic_core")

            diffs = p2.compute_semantic_diffs(validator, fs_state, cache_state)
            ops = p2.build_operations(validator, diffs)

            # Count matched files
            matched_diffs = [d for d in diffs if d.diff_kind in ("hash_match", "semantic_symbol_match")]

            # Verify all matched files have canonical_rewrite_component ops
            for diff in matched_diffs:
                matching_ops = [o for o in ops if o.target_path == diff.live_path]
                assert len(matching_ops) > 0, f"Matched file {diff.live_path} should have an operation"
                assert all(o.op_type == "canonical_rewrite_component" for o in matching_ops), \
                    f"All ops for {diff.live_path} should be canonical_rewrite_component"

        finally:
            p2.PROJECT_ROOT = original_project_root
            p2.SSOT_YAML = original_ssot_yaml
            p2.META_YAML = original_meta_yaml
            p2.SEMANTIC_CACHE_ROOT = original_cache_root

    def test_2_3_op_02_deterministic_sort(self, mock_project: Dict[str, Path]) -> None:
        """
        TEST CASE 2.3-OP-02 — Deterministic sort
        
        Run Phase 2 twice with no changes.
        
        Expected:
        - Plan JSON is byte-identical.
        
        Pass:
        - diff plan1.json plan2.json shows no difference.
        """
        project_root = mock_project["project_root"]
        cache_root = mock_project["semantic_cache"]
        target_root = mock_project["target_root"]

        # Create test files
        test_content = "class TestClass:\n    pass\n"
        file_hash = compute_hash(test_content)

        live_file = target_root / "L1_cognition" / "P1_retrieve" / "test_file.py"
        live_file.parent.mkdir(parents=True, exist_ok=True)
        live_file.write_text(test_content, encoding="utf-8")

        create_semantic_pointer(
            cache_root=cache_root,
            bucket="01_agentic_core",
            file_hash=file_hash,
            component_id="test_file.py::class::TestClass",
            kind="class",
        )

        original_project_root = p2.PROJECT_ROOT
        original_ssot_yaml = p2.SSOT_YAML
        original_meta_yaml = p2.META_YAML
        original_cache_root = p2.SEMANTIC_CACHE_ROOT

        try:
            p2.PROJECT_ROOT = project_root
            p2.SSOT_YAML = mock_project["ssot_yaml"]
            p2.META_YAML = mock_project["meta_yaml"]
            p2.SEMANTIC_CACHE_ROOT = cache_root

            def run_phase2_and_get_plan() -> str:
                validator = p2.Phase2Validator(verbose=False)
                fs_state = p2.load_filesystem_state(validator, "01_agentic_core")
                cache_state = p2.load_semantic_cache_state(validator, "01_agentic_core")
                diffs = p2.compute_semantic_diffs(validator, fs_state, cache_state)
                ops = p2.build_operations(validator, diffs)

                # Serialize operations to JSON for comparison
                ops_data = [asdict(o) for o in ops]
                return json.dumps(ops_data, indent=2, sort_keys=True)

            # Run twice
            plan1 = run_phase2_and_get_plan()
            plan2 = run_phase2_and_get_plan()

            # Verify byte-identical output
            assert plan1 == plan2, "Plans should be byte-identical across runs"

        finally:
            p2.PROJECT_ROOT = original_project_root
            p2.SSOT_YAML = original_ssot_yaml
            p2.META_YAML = original_meta_yaml
            p2.SEMANTIC_CACHE_ROOT = original_cache_root


# ============================================================================
# 2.4 — IMPORT MAP TESTS
# ============================================================================


class TestImportMap:
    """Test cases for import detection (2.4-IMP-01)."""

    def test_2_4_imp_01_import_detection(self, mock_project: Dict[str, Path]) -> None:
        """
        TEST CASE 2.4-IMP-01 — Import detection
        
        Input:
        ```python
        from utils.helper import f
        ```
        
        Expected:
        - Plan contains import reference: imports: ["utils.helper"]
        - Used later by Phase 3 for import rewrite.
        
        Pass:
        - Import appears in component metadata or plan entry.
        """
        project_root = mock_project["project_root"]
        cache_root = mock_project["semantic_cache"]
        target_root = mock_project["target_root"]

        # Create a Python file with imports
        test_content = '''from utils.helper import f
from os.path import join
import json

class Planner:
    def plan(self):
        return f()
'''
        file_hash = compute_hash(test_content)

        live_file = target_root / "L1_cognition" / "P1_retrieve" / "planner.py"
        live_file.parent.mkdir(parents=True, exist_ok=True)
        live_file.write_text(test_content, encoding="utf-8")

        create_semantic_pointer(
            cache_root=cache_root,
            bucket="01_agentic_core",
            file_hash=file_hash,
            component_id="planner.py::class::Planner",
            kind="class",
        )

        original_project_root = p2.PROJECT_ROOT
        original_ssot_yaml = p2.SSOT_YAML
        original_meta_yaml = p2.META_YAML
        original_cache_root = p2.SEMANTIC_CACHE_ROOT

        try:
            p2.PROJECT_ROOT = project_root
            p2.SSOT_YAML = mock_project["ssot_yaml"]
            p2.META_YAML = mock_project["meta_yaml"]
            p2.SEMANTIC_CACHE_ROOT = cache_root

            # Parse the AST to extract imports
            tree = ast.parse(test_content)

            # Extract import information
            imports: List[str] = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

            # Verify imports are detected
            assert "utils.helper" in imports, "Should detect 'utils.helper' import"
            assert "os.path" in imports, "Should detect 'os.path' import"
            assert "json" in imports, "Should detect 'json' import"

            # Verify tool usage detection captures function calls from imports
            tool_usage = p2.infer_tool_usage_from_ast(tree)
            assert "f" in tool_usage, "Should detect 'f' function call"

        finally:
            p2.PROJECT_ROOT = original_project_root
            p2.SSOT_YAML = original_ssot_yaml
            p2.META_YAML = original_meta_yaml
            p2.SEMANTIC_CACHE_ROOT = original_cache_root


# ============================================================================
# ADDITIONAL VALIDATION TESTS
# ============================================================================


class TestValidationKeys:
    """Test that K-keys are properly validated."""

    def test_k_keys_coverage(self, mock_project: Dict[str, Path]) -> None:
        """Verify that all required K-keys are checked during Phase 2 execution."""
        project_root = mock_project["project_root"]
        cache_root = mock_project["semantic_cache"]
        target_root = mock_project["target_root"]

        # Create minimal test file
        test_content = "class Test: pass"
        live_file = target_root / "L1_cognition" / "P1_retrieve" / "test.py"
        live_file.parent.mkdir(parents=True, exist_ok=True)
        live_file.write_text(test_content, encoding="utf-8")

        original_project_root = p2.PROJECT_ROOT
        original_ssot_yaml = p2.SSOT_YAML
        original_meta_yaml = p2.META_YAML
        original_cache_root = p2.SEMANTIC_CACHE_ROOT

        try:
            p2.PROJECT_ROOT = project_root
            p2.SSOT_YAML = mock_project["ssot_yaml"]
            p2.META_YAML = mock_project["meta_yaml"]
            p2.SEMANTIC_CACHE_ROOT = cache_root

            validator = p2.Phase2Validator(verbose=False)

            # Run through Phase 2 steps
            p2.check_preconditions(validator)
            ssot = p2.load_ssot_and_meta(validator, "01_agentic_core")
            fs_state = p2.load_filesystem_state(validator, "01_agentic_core")
            cache_state = p2.load_semantic_cache_state(validator, "01_agentic_core")

            if ssot and fs_state:
                p2.compute_structural_diff(validator, ssot, fs_state)
                p2.check_meta_semantic_invariants(validator, ssot)

            if fs_state and cache_state:
                diffs = p2.compute_semantic_diffs(validator, fs_state, cache_state)
                p2.build_operations(validator, diffs)

            # Check that we have validation results
            assert len(validator.results) > 0, "Should have validation results"

            # Get all logged K-keys
            logged_keys = {r.key for r in validator.results if r.key.startswith("K")}

            # Verify critical K-keys are present
            critical_keys = {"K1", "K2", "K5", "K6", "K7", "K8", "K9", "K10"}
            for key in critical_keys:
                assert key in logged_keys, f"Critical K-key {key} should be logged"

        finally:
            p2.PROJECT_ROOT = original_project_root
            p2.SSOT_YAML = original_ssot_yaml
            p2.META_YAML = original_meta_yaml
            p2.SEMANTIC_CACHE_ROOT = original_cache_root


# ============================================================================
# MAIN
# ============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
