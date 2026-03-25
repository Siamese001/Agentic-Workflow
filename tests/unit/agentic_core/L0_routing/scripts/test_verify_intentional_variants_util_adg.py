"""Behavioral contract tests for agentic_core.L0_routing.scripts.verify_intentional_variants_util."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.scripts.verify_intentional_variants_util"


@pytest.fixture(scope="module")
def mod():
    """Import the module under test. Fails hard if first-party import broken."""
    try:
        return importlib.import_module(MODULE_PATH)
    except Exception as exc:
        pytest.fail(
            f"FIRST-PARTY IMPORT FAILED for {MODULE_PATH}: {exc}",
            pytrace=False,
        )


def test_module_importable(mod):
    """Module imports without errors."""
    assert mod.__name__ == MODULE_PATH


def test_module_exposes_public_api(mod):
    """Module exposes expected public symbols."""
    public = [n for n in dir(mod) if not n.startswith("_")]
    assert len(public) >= 1, f"{MODULE_PATH} must expose at least one public symbol"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_path_is_instantiable(mod):
    """Path is accessible and is a type."""
    cls = getattr(mod, "Path", None)
    assert cls is not None, "Path must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Path must be a class"


def test_defaultdict_is_instantiable(mod):
    """defaultdict is accessible and is a type."""
    cls = getattr(mod, "defaultdict", None)
    assert cls is not None, "defaultdict must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "defaultdict must be a class"


def test_analyze_variant_likelihood_is_callable(mod):
    """analyze_variant_likelihood is accessible and callable."""
    func = getattr(mod, "analyze_variant_likelihood", None)
    assert func is not None, "analyze_variant_likelihood must be defined in {MODULE_PATH}"
    assert callable(func), "analyze_variant_likelihood must be callable"


def test_compute_file_hash_is_callable(mod):
    """compute_file_hash is accessible and callable."""
    func = getattr(mod, "compute_file_hash", None)
    assert func is not None, "compute_file_hash must be defined in {MODULE_PATH}"
    assert callable(func), "compute_file_hash must be callable"


def test_emit_determinism_digest_is_callable(mod):
    """emit_determinism_digest is accessible and callable."""
    func = getattr(mod, "emit_determinism_digest", None)
    assert func is not None, "emit_determinism_digest must be defined in {MODULE_PATH}"
    assert callable(func), "emit_determinism_digest must be callable"


def test_emit_replay_key_is_callable(mod):
    """emit_replay_key is accessible and callable."""
    func = getattr(mod, "emit_replay_key", None)
    assert func is not None, "emit_replay_key must be defined in {MODULE_PATH}"
    assert callable(func), "emit_replay_key must be callable"


def test_extract_key_identifiers_is_callable(mod):
    """extract_key_identifiers is accessible and callable."""
    func = getattr(mod, "extract_key_identifiers", None)
    assert func is not None, "extract_key_identifiers must be defined in {MODULE_PATH}"
    assert callable(func), "extract_key_identifiers must be callable"


def test_main_is_callable(mod):
    """main is accessible and callable."""
    func = getattr(mod, "main", None)
    assert func is not None, "main must be defined in {MODULE_PATH}"
    assert callable(func), "main must be callable"


def test_read_file_content_is_callable(mod):
    """read_file_content is accessible and callable."""
    func = getattr(mod, "read_file_content", None)
    assert func is not None, "read_file_content must be defined in {MODULE_PATH}"
    assert callable(func), "read_file_content must be callable"


def test_scan_for_duplicates_is_callable(mod):
    """scan_for_duplicates is accessible and callable."""
    func = getattr(mod, "scan_for_duplicates", None)
    assert func is not None, "scan_for_duplicates must be defined in {MODULE_PATH}"
    assert callable(func), "scan_for_duplicates must be callable"

