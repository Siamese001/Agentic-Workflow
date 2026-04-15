"""Unit tests for _is_canonical in tools/eval/retrieval_eval_curated.py.

Phase 4: validates that chunks with invalid_for_normative_use=True are never
canonical, regardless of the ``canonical`` metadata field value.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_spec = importlib.util.spec_from_file_location(
    "retrieval_eval_curated",
    _REPO_ROOT / "tools" / "eval" / "retrieval_eval_curated.py",
)
_eval_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
sys.modules["retrieval_eval_curated"] = _eval_mod
_spec.loader.exec_module(_eval_mod)  # type: ignore[union-attr]
_is_canonical = _eval_mod._is_canonical


class TestIsCanonical:
    """Unit tests for _is_canonical helper (tools/eval/retrieval_eval_curated.py)."""

    def test_canonical_true_no_invalid_flag_is_canonical(self) -> None:
        assert _is_canonical({"canonical": True}) is True

    def test_canonical_false_is_not_canonical(self) -> None:
        assert _is_canonical({"canonical": False}) is False

    def test_phase4_guard_invalid_flag_overrides_canonical_true(self) -> None:
        """Phase 4: invalid_for_normative_use=True must return False even when canonical=True."""
        assert _is_canonical({"canonical": True, "invalid_for_normative_use": True}) is False

    def test_invalid_flag_false_does_not_suppress_canonical(self) -> None:
        """invalid_for_normative_use=False must NOT trigger the Phase 4 guard."""
        assert _is_canonical({"canonical": True, "invalid_for_normative_use": False}) is True

    def test_legacy_arch_doc_adr_is_canonical_without_canonical_field(self) -> None:
        meta = {
            "artifact_type": "arch_doc",
            "file_path": "docs/adr/adr-018-chromadb.md",
        }
        assert _is_canonical(meta) is True

    def test_legacy_arch_doc_non_adr_is_not_canonical(self) -> None:
        meta = {
            "artifact_type": "arch_doc",
            "file_path": "docs/design/overview.md",
        }
        assert _is_canonical(meta) is False

    def test_empty_metadata_is_not_canonical(self) -> None:
        assert _is_canonical({}) is False

    def test_phase4_guard_fires_before_legacy_adr_inference(self) -> None:
        """Phase 4 guard must short-circuit before legacy inference — ADR with invalid=True is rejected."""
        meta = {
            "artifact_type": "arch_doc",
            "file_path": "docs/adr/adr-018-chromadb.md",
            "invalid_for_normative_use": True,
        }
        assert _is_canonical(meta) is False
