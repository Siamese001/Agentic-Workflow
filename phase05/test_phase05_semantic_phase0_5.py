#!/usr/bin/env python3
"""Phase 0.5 — semantic cache rebuild tests (semantic extraction, artifacts, pointers).

These tests exercise the core Phase 0.5 machinery in `phase05_execute` without
needing to run the full archive scan pipeline. They operate against a temporary
`CACHE_ROOT` so that no real semantic cache state is modified.

Covered scenarios (from Phase 0.5 spec):

- 0.5-PY-01: Python component extraction (classes, functions, constants).
- 0.5-PY-02: Syntax error fallback → blob component spanning full file.
- 0.5-PY-03: Multi-class file → `co_defined` edge in component graph.
- 0.5-NP-01: JSON config → single `kind: config` component, bucket 05_config.
- 0.5-NP-02: Markdown document → single `kind: document` component.
- 0.5-ART-01: Required global + semantic artifacts exist for hash H.
- 0.5-ART-02: Deterministic ordering / idempotent semantic + graph output.
- 0.5-PTR-01: Pointer validity via Phase05Validator K11 passes.
- 0.5-PTR-02: Corrupted pointer causes Phase05Validator K11 to fail.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Tuple


# Ensure repository root is on sys.path so that the `phase05` package can be
# imported when tests are invoked from within the 10_tests tree.
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from phase05 import phase05_execute as p5
from phase05 import phase05_validate as p5v
from phase05.phase05_validate import Phase05Validator, ValidationStep


def _setup_tmp_roots(tmp_path: Path) -> Tuple[Path, Path]:
    """Create an isolated PROJECT_ROOT and CACHE_ROOT under tmp_path.

    Returns (project_root, cache_root).
    """
    project_root = tmp_path / "project_root"
    cache_root = project_root / "06_data" / "semantic_cache"
    cache_root.mkdir(parents=True, exist_ok=True)

    # Patch roots in Phase 0.5 modules so all artifacts land under tmp.
    p5.PROJECT_ROOT = project_root
    p5.CACHE_ROOT = cache_root
    p5v.CACHE_ROOT = cache_root

    return project_root, cache_root


def _make_archive_record(project_root: Path, filename: str, content: str) -> p5.ArchiveFileRecord:
    """Create a single CURRENT-engine ArchiveFileRecord for a synthetic file."""
    file_path = project_root / filename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")

    size_bytes = file_path.stat().st_size
    loc = p5.count_loc(file_path)

    return p5.ArchiveFileRecord(
        path=file_path,
        engine="CURRENT",
        archive_name="TEST_DOMAIN",
        rel_posix=filename.replace("\\", "/"),
        version_tag="test",
        size_bytes=size_bytes,
        loc=loc,
    )


# ---------------------------------------------------------------------------
# 0.5-PY-01 — Extract classes, functions, constants
# ---------------------------------------------------------------------------


def test_05_py_01_extract_python_components(tmp_path: Path) -> None:
    project_root, cache_root = _setup_tmp_roots(tmp_path)

    src = """class Planner:
    def plan(self):
        pass


def helper():
    pass

CONFIG = {"mode": "test"}
"""
    rec = _make_archive_record(project_root, "py01_sample.py", src)

    hash_map, components_by_hash, _ = p5.generate_global_and_semantic_artifacts([rec])

    # Exactly one hash for this single file
    assert len(hash_map) == 1
    (h,) = tuple(hash_map.keys())

    sem_path = cache_root / "semantic" / f"{h}.semantic.json"
    assert sem_path.exists()

    sem_data = json.loads(sem_path.read_text(encoding="utf-8"))
    components = sem_data["components"]

    # Expect exactly 3 top-level components: class, function, constant assignment
    assert len(components) == 3

    names = {c["name"] for c in components}
    assert "Planner" in names
    assert "helper" in names
    assert "CONFIG" in names

    # All components must have valid, strictly positive spans
    spans = []
    for c in components:
        start = c["span_start"]
        end = c["span_end"]
        assert isinstance(start, int) and isinstance(end, int)
        assert start > 0 and end >= start
        spans.append((start, end))

    # Components should not overlap by line range
    spans.sort()
    prev_end = None
    for start, end in spans:
        if prev_end is not None:
            assert start > prev_end
        prev_end = end


# ---------------------------------------------------------------------------
# 0.5-PY-02 — Syntax error fallback
# ---------------------------------------------------------------------------


def test_05_py_02_syntax_error_fallback(tmp_path: Path) -> None:
    project_root, cache_root = _setup_tmp_roots(tmp_path)

    # Intentionally invalid Python
    src = """def broken(
    print("x")
"""
    rec = _make_archive_record(project_root, "py02_broken.py", src)

    hash_map, components_by_hash, _ = p5.generate_global_and_semantic_artifacts([rec])
    assert len(hash_map) == 1
    (h,) = tuple(hash_map.keys())

    sem_path = cache_root / "semantic" / f"{h}.semantic.json"
    assert sem_path.exists()

    data = json.loads(sem_path.read_text(encoding="utf-8"))
    comps = data["components"]

    # Fallback should yield exactly one blob/document component spanning whole file
    assert len(comps) == 1
    comp = comps[0]

    assert comp["span_start"] == 1
    assert comp["span_end"] == rec.loc


# ---------------------------------------------------------------------------
# 0.5-PY-03 — Multi-class file co_defined edge
# ---------------------------------------------------------------------------


def test_05_py_03_multi_class_co_defined_edge(tmp_path: Path) -> None:
    project_root, cache_root = _setup_tmp_roots(tmp_path)

    src = """class A:
    ...


class B:
    ...
"""
    rec = _make_archive_record(project_root, "py03_multi_class.py", src)

    hash_map, components_by_hash, _ = p5.generate_global_and_semantic_artifacts([rec])
    (h,) = tuple(hash_map.keys())

    sem_path = cache_root / "semantic" / f"{h}.semantic.json"
    sem = json.loads(sem_path.read_text(encoding="utf-8"))
    comps = sem["components"]

    names_to_id = {c["name"]: c["component_id"] for c in comps}
    assert "A" in names_to_id and "B" in names_to_id

    graph_path = cache_root / "graphs" / "component_graph.json"
    assert graph_path.exists()

    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    edges = graph.get("edges", [])

    a_id = names_to_id["A"]
    b_id = names_to_id["B"]
    has_co_defined = any(
        e.get("kind") == "co_defined"
        and {e.get("from"), e.get("to")} == {a_id, b_id}
        for e in edges
    )
    assert has_co_defined


# ---------------------------------------------------------------------------
# 0.5-NP-01 — JSON configuration
# ---------------------------------------------------------------------------


def test_05_np_01_json_config(tmp_path: Path) -> None:
    project_root, cache_root = _setup_tmp_roots(tmp_path)

    src = """{"mode": "test", "level": 1}
"""
    rec = _make_archive_record(project_root, "config.json", src)

    hash_map, components_by_hash, _ = p5.generate_global_and_semantic_artifacts([rec])
    (h,) = tuple(hash_map.keys())

    sem_path = cache_root / "semantic" / f"{h}.semantic.json"
    data = json.loads(sem_path.read_text(encoding="utf-8"))
    comps = data["components"]

    assert len(comps) == 1
    comp = comps[0]

    assert comp["kind"] == "config"
    assert comp["bucket"] == "05_config"
    assert comp["span_start"] == 1
    assert comp["span_end"] == rec.loc


# ---------------------------------------------------------------------------
# 0.5-NP-02 — Markdown document
# ---------------------------------------------------------------------------


def test_05_np_02_markdown_document(tmp_path: Path) -> None:
    project_root, cache_root = _setup_tmp_roots(tmp_path)

    src = """# Title
Some text here.
Another line.
"""
    rec = _make_archive_record(project_root, "doc.md", src)

    hash_map, components_by_hash, _ = p5.generate_global_and_semantic_artifacts([rec])
    (h,) = tuple(hash_map.keys())

    sem_path = cache_root / "semantic" / f"{h}.semantic.json"
    data = json.loads(sem_path.read_text(encoding="utf-8"))
    comps = data["components"]

    assert len(comps) == 1
    comp = comps[0]

    assert comp["kind"] == "document"
    # Bucket may be None for documents; only require full-span coverage.
    assert comp["span_start"] == 1
    assert comp["span_end"] == rec.loc


# ---------------------------------------------------------------------------
# 0.5-ART-01 — Required artifacts exist for hash H
# ---------------------------------------------------------------------------


def test_05_art_01_required_artifacts_exist(tmp_path: Path) -> None:
    project_root, cache_root = _setup_tmp_roots(tmp_path)

    src = """def f():
    return 42
"""
    rec = _make_archive_record(project_root, "art01_sample.py", src)

    hash_map, components_by_hash, _ = p5.generate_global_and_semantic_artifacts([rec])
    (h,) = tuple(hash_map.keys())

    # Check required global + semantic artifacts
    assert (cache_root / "ast" / f"{h}.ast").exists()
    assert (cache_root / "golden" / f"{h}.golden.json").exists()
    assert (cache_root / "embeddings" / f"{h}.embedding").exists()
    assert (cache_root / "integrity" / f"{h}.integrity.json").exists()
    assert (cache_root / "meta" / f"{h}.meta.json").exists()
    assert (cache_root / "semantic" / f"{h}.semantic.json").exists()


# ---------------------------------------------------------------------------
# 0.5-ART-02 — Deterministic ordering / idempotent output
# ---------------------------------------------------------------------------


def test_05_art_02_deterministic_semantic_and_graph(tmp_path: Path) -> None:
    project_root, cache_root = _setup_tmp_roots(tmp_path)

    src = """class Alpha:
    def a(self):
        return 1


class Beta:
    def b(self):
        return 2
"""
    rec = _make_archive_record(project_root, "art02_sample.py", src)

    # First run
    hash_map_1, _, _ = p5.generate_global_and_semantic_artifacts([rec])
    (h1,) = tuple(hash_map_1.keys())

    sem_path = cache_root / "semantic" / f"{h1}.semantic.json"
    graph_path = cache_root / "graphs" / "component_graph.json"

    sem_1 = sem_path.read_text(encoding="utf-8")
    graph_1 = graph_path.read_text(encoding="utf-8")

    # Second run with identical inputs
    hash_map_2, _, _ = p5.generate_global_and_semantic_artifacts([rec])
    (h2,) = tuple(hash_map_2.keys())
    assert h1 == h2

    sem_2 = sem_path.read_text(encoding="utf-8")
    graph_2 = graph_path.read_text(encoding="utf-8")

    # Idempotent outputs
    assert sem_1 == sem_2
    assert graph_1 == graph_2


# ---------------------------------------------------------------------------
# 0.5-PTR-01/02 — Pointer validity and corruption detection via K11
# ---------------------------------------------------------------------------


def test_05_ptr_01_pointer_validity(tmp_path: Path) -> None:
    project_root, cache_root = _setup_tmp_roots(tmp_path)

    # Ensure full cache directory structure exists (buckets, global domains).
    p5.create_semantic_cache_structure()

    src = """class Planner:
    pass
"""
    rec = _make_archive_record(project_root, "ptr01_sample.py", src)

    hash_map, components_by_hash, _ = p5.generate_global_and_semantic_artifacts([rec])

    # Generate canonical pointers for these components
    bucket_counts, move_plan = p5.generate_canonical_component_pointers(hash_map, components_by_hash)
    assert sum(bucket_counts.values()) > 0

    # Validate pointers and their linkage to semantic components using the validator
    v = Phase05Validator(strict_mode=True)
    step_global = ValidationStep("GLOBAL", "global", "PENDING")
    step_sem = ValidationStep("SEMANTIC", "semantic", "PENDING")
    step_ptr = ValidationStep("CANONICAL", "canonical", "PENDING")

    assert v._validate_global_artifacts(step_global)
    assert v._validate_semantic_artifacts(step_sem)
    assert v._validate_canonical_pointers(step_ptr)
    assert v.K.get("K11", False)

    # Additionally, check that each pointer's global references resolve.
    for bucket in p5v.SEMANTIC_BUCKETS:
        bucket_root = cache_root / bucket
        if not bucket_root.exists():
            continue
        for ptr_file in bucket_root.rglob("*.json"):
            data = json.loads(ptr_file.read_text(encoding="utf-8"))
            h = data.get("hash")
            cid = data.get("component_id")

            # Hash and component id must resolve into the validator's tables
            assert h in v.global_hashes
            assert cid in v.components_by_hash.get(h, set())

            # Canonical root and relative must be internally consistent
            canonical_root = data.get("canonical_root")
            canonical_relative = data.get("canonical_relative")
            assert canonical_root == bucket
            pointer_rel = ptr_file.relative_to(bucket_root)
            pointer_rel_no_suffix = str(pointer_rel.with_suffix("")).replace("\\", "/")
            assert canonical_relative == pointer_rel_no_suffix

            # Global artifact references must exist
            global_refs = data.get("global", {})
            for rel_path in global_refs.values():
                assert (cache_root / rel_path).exists()


def test_05_ptr_02_invalid_pointer_detection(tmp_path: Path) -> None:
    project_root, cache_root = _setup_tmp_roots(tmp_path)

    p5.create_semantic_cache_structure()

    src = """def f():
    return 1
"""
    rec = _make_archive_record(project_root, "ptr02_sample.py", src)

    hash_map, components_by_hash, _ = p5.generate_global_and_semantic_artifacts([rec])
    p5.generate_canonical_component_pointers(hash_map, components_by_hash)

    # Corrupt a single pointer by giving it an invalid component_id
    corrupted = False
    for bucket in p5v.SEMANTIC_BUCKETS:
        bucket_root = cache_root / bucket
        if not bucket_root.exists():
            continue
        for ptr_file in bucket_root.rglob("*.json"):
            data = json.loads(ptr_file.read_text(encoding="utf-8"))
            data["component_id"] = "INVALID_COMPONENT_ID_FOR_TEST"
            ptr_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
            corrupted = True
            break
        if corrupted:
            break

    assert corrupted, "Expected to corrupt at least one pointer file"

    # Run validator semantic + pointer steps; K11 should fail
    v = Phase05Validator(strict_mode=True)
    step_global = ValidationStep("GLOBAL", "global", "PENDING")
    step_sem = ValidationStep("SEMANTIC", "semantic", "PENDING")
    step_ptr = ValidationStep("CANONICAL", "canonical", "PENDING")

    assert v._validate_global_artifacts(step_global)
    assert v._validate_semantic_artifacts(step_sem)
    ok_ptr = v._validate_canonical_pointers(step_ptr)

    assert not ok_ptr
    assert not v.K.get("K11", True)
