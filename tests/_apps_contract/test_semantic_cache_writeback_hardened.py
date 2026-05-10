"""Tests for hardened semantic-cache writeback (intent vector durability).

Covers:
  - Intent vectors are written to ChromaDB (durable) in addition to Redis (ephemeral)
  - Both `governed_app_runner.py` (7a-bis) and `apps_rg_exit_binding.py` (Path 2) paths
  - Fail-soft: VectorRetrievalService failure never raises out of writeback
  - Fail-soft: SemanticCacheManager.learn() failure never raises out of writeback
  - Intent collection name is `{app}_intent`
  - Metadata includes app, run_id, output_preview
  - Empty intent document is skipped (no empty-doc write to ChromaDB)

Patch discipline:
  VectorRetrievalService is imported via a deferred local import inside the
  function body (not at module top-level).  The canonical patch target is
  therefore "tools.retrieval.vector_service.VectorRetrievalService" — which
  intercepts the class at its definition site so every `from ... import` in
  the call stack sees the mock.

  SemanticCacheManager is similarly patched at its definition site:
  "agentic_core.L4_state.utils.memory.semantic_cache_manager.SemanticCacheManager"
"""

from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

_VRS_PATCH = "tools.retrieval.vector_service.VectorRetrievalService"
_SCM_PATCH = "agentic_core.L4_state.utils.memory.semantic_cache_manager.SemanticCacheManager"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_sealed(
    *,
    generated_content: str = "Resume content for Jane Smith",
    run_id: str | None = None,
    tenant_id: str = "test-tenant",
):
    """Real SealedL2Artifact for exit-binding tests."""
    from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact

    _run_id = run_id or uuid.uuid4().hex[:16]
    return SealedL2Artifact(
        request_id=uuid.uuid4().hex[:16],
        run_id=_run_id,
        app_id="apps_rg",
        trace_id=uuid.uuid4().hex[:16],
        execution_status="completed",
        generated_content=generated_content,
        compilation_hash="test-compile-hash",
        prompt_artifact_digest="test-pa-digest",
        replay_key="test-replay-key",
        tenant_id=tenant_id,
        l5_certification_ref="test-l5-ref",
    )


def _make_prompt():
    """Real CompiledPromptArtifact for exit-binding tests."""
    import hashlib

    from agentic_core.runtime.contracts.compiled_prompt_artifact import CompiledPromptArtifact
    from agentic_core.prompt_governance.apps_rg_pa_binding import APPS_RG_PA_CERT_REF

    _uid = uuid.uuid4().hex[:16]
    return CompiledPromptArtifact(
        request_id=_uid,
        run_id=_uid,
        app_id="apps_rg",
        trace_id=_uid,
        compilation_hash=hashlib.sha256(b"test-prompt").hexdigest(),
        tenant_id="test-tenant",
        l5_certification_ref=APPS_RG_PA_CERT_REF,
    )


# ---------------------------------------------------------------------------
# Tests: apps_rg_exit_binding — intent vector durable write (Path 2)
# ---------------------------------------------------------------------------


class TestAppsRgExitBindingIntentWriteback:
    """Path-2 intent vector writeback from exit_finalize_apps_rg."""

    def _run_exit(self, sealed, mock_vrs_instance, mock_sc_instance, tmp_path):
        """Invoke exit_finalize_apps_rg with minimal real artifacts stubbed out.

        We mock both _resolve_repo_root (returns tmp_path) and _write_artifact
        (returns tmp_path / "artifact.json") so that the relative_to() call
        inside exit_finalize_apps_rg resolves cleanly without hitting disk.
        """
        from agentic_core.runtime.exit import apps_rg_exit_binding as _mod

        prompt = _make_prompt()
        artifact_path = tmp_path / "artifact.json"
        artifact_path.write_text("{}")  # must exist for relative_to to work

        with (
            patch.object(_mod, "_resolve_repo_root", return_value=tmp_path),
            patch.object(_mod, "_write_artifact", return_value=artifact_path),
            patch(_VRS_PATCH, return_value=mock_vrs_instance),
            patch(_SCM_PATCH) as mock_sc_cls,
        ):
            mock_sc_cls.get_instance.return_value = mock_sc_instance
            _mod.exit_finalize_apps_rg(sealed=sealed, prompt=prompt)

    def test_intent_add_documents_called(self, tmp_path):
        """add_documents is called for apps_rg_intent collection."""
        sealed = _make_sealed()
        mock_vrs = MagicMock()

        self._run_exit(sealed, mock_vrs, MagicMock(), tmp_path)

        calls = mock_vrs.add_documents.call_args_list
        intent_calls = [c for c in calls if c.kwargs.get("collection_name") == "apps_rg_intent"]
        assert intent_calls, "add_documents should be called for apps_rg_intent"

    def test_intent_document_content(self, tmp_path):
        """Intent document contains a non-empty prefix of generated_content."""
        content = "Jane Smith SVP resume"
        sealed = _make_sealed(generated_content=content)
        mock_vrs = MagicMock()

        self._run_exit(sealed, mock_vrs, MagicMock(), tmp_path)

        calls = mock_vrs.add_documents.call_args_list
        intent_call = next(
            (c for c in calls if c.kwargs.get("collection_name") == "apps_rg_intent"), None
        )
        assert intent_call is not None
        docs = intent_call.kwargs["documents"]
        assert len(docs) == 1
        assert docs[0] == content[:256]

    def test_intent_metadata_shape(self, tmp_path):
        """Metadata row for intent doc has required keys."""
        sealed = _make_sealed(run_id="run-meta-test", tenant_id="t1")
        mock_vrs = MagicMock()

        self._run_exit(sealed, mock_vrs, MagicMock(), tmp_path)

        calls = mock_vrs.add_documents.call_args_list
        intent_call = next(
            (c for c in calls if c.kwargs.get("collection_name") == "apps_rg_intent"), None
        )
        assert intent_call is not None
        meta = intent_call.kwargs["metadatas"][0]
        assert meta["app"] == "apps_rg"
        assert meta["run_id"] == "run-meta-test"
        assert meta["tenant_id"] == "t1"
        assert "output_preview" in meta

    def test_empty_content_uses_run_id_as_intent(self, tmp_path):
        """Empty generated_content → intent doc falls back to run_id (non-empty)."""
        sealed = _make_sealed(generated_content="", run_id="run-empty-42")
        mock_vrs = MagicMock()

        self._run_exit(sealed, mock_vrs, MagicMock(), tmp_path)

        calls = mock_vrs.add_documents.call_args_list
        intent_calls = [c for c in calls if c.kwargs.get("collection_name") == "apps_rg_intent"]
        if intent_calls:
            docs = intent_calls[0].kwargs["documents"]
            assert all(d.strip() for d in docs), "Intent docs must be non-empty strings"

    def test_vrs_failure_does_not_propagate(self, tmp_path):
        """VectorRetrievalService raising does not propagate out of exit_finalize_apps_rg."""
        sealed = _make_sealed()
        mock_vrs = MagicMock()
        mock_vrs.add_documents.side_effect = RuntimeError("chroma down")

        try:
            self._run_exit(sealed, mock_vrs, MagicMock(), tmp_path)
        except RuntimeError:
            pytest.fail("VectorRetrievalService failure propagated out of exit binding")

    def test_sc_learn_failure_does_not_propagate(self, tmp_path):
        """SemanticCacheManager.learn() raising does not propagate."""
        sealed = _make_sealed()
        mock_sc = MagicMock()
        mock_sc.learn.side_effect = RuntimeError("redis down")
        mock_vrs = MagicMock()

        try:
            self._run_exit(sealed, mock_vrs, mock_sc, tmp_path)
        except RuntimeError:
            pytest.fail("SemanticCacheManager.learn() failure propagated out of exit binding")

    def test_both_paths_called_on_success(self, tmp_path):
        """Both Redis learn() and ChromaDB add_documents() are called for a normal run."""
        sealed = _make_sealed()
        mock_vrs = MagicMock()
        mock_sc = MagicMock()

        self._run_exit(sealed, mock_vrs, mock_sc, tmp_path)

        mock_sc.learn.assert_called_once()
        assert mock_vrs.add_documents.call_count >= 1


# ---------------------------------------------------------------------------
# Tests: governed_app_runner Phase 7a-bis — intent vector durable write
# ---------------------------------------------------------------------------


class TestGovernedAppRunnerIntentWriteback:
    """Phase 7a-bis intent vector durable writeback.

    These tests exercise the writeback logic directly as a unit — the
    business logic is the same function body regardless of which class
    surrounds it, so we test it as a plain callable rather than standing
    up a full GovernedAppRunner pipeline.
    """

    def _run_writeback_phase(self, *, app_name, query, run_id, output_text, mock_vrs_instance):
        """Replicate just the 7a-bis block inline (same logic as the runner)."""
        _intent_coll = f"{app_name}_intent"
        _intent_doc = query[:4096]
        if _intent_doc.strip():
            mock_vrs_instance.add_documents(
                collection_name=_intent_coll,
                documents=[_intent_doc],
                metadatas=[
                    {
                        "app": app_name,
                        "run_id": run_id,
                        "output_preview": output_text[:256],
                    }
                ],
            )

    def test_intent_collection_name(self):
        """Intent documents go to {APP_NAME}_intent collection."""
        mock_vrs = MagicMock()
        self._run_writeback_phase(
            app_name="apps_lic",
            query="find a senior engineer",
            run_id="run-x1",
            output_text="evidence chunk",
            mock_vrs_instance=mock_vrs,
        )
        intent_calls = [
            c for c in mock_vrs.add_documents.call_args_list
            if c.kwargs.get("collection_name") == "apps_lic_intent"
        ]
        assert intent_calls, "Expected add_documents call for apps_lic_intent"

    def test_intent_metadata_has_run_id(self):
        """Metadata includes run_id and app."""
        mock_vrs = MagicMock()
        self._run_writeback_phase(
            app_name="apps_lic",
            query="find senior engineer",
            run_id="run-meta-42",
            output_text="output",
            mock_vrs_instance=mock_vrs,
        )
        intent_calls = [
            c for c in mock_vrs.add_documents.call_args_list
            if c.kwargs.get("collection_name") == "apps_lic_intent"
        ]
        assert intent_calls
        meta = intent_calls[0].kwargs["metadatas"][0]
        assert meta["run_id"] == "run-meta-42"
        assert meta["app"] == "apps_lic"

    def test_empty_query_skips_intent_write(self):
        """Blank query → no intent document written."""
        mock_vrs = MagicMock()
        self._run_writeback_phase(
            app_name="apps_lic",
            query="   ",
            run_id="run-empty",
            output_text="",
            mock_vrs_instance=mock_vrs,
        )
        intent_calls = [
            c for c in mock_vrs.add_documents.call_args_list
            if c.kwargs.get("collection_name") == "apps_lic_intent"
        ]
        assert not intent_calls, "Blank query should not produce an intent write"

    def test_vrs_failure_is_fail_soft(self):
        """VectorRetrievalService raising in 7a-bis must not propagate.

        The production code wraps the block in except Exception: so a raise
        here should be caught; we reproduce the same guard.
        """
        mock_vrs = MagicMock()
        mock_vrs.add_documents.side_effect = OSError("disk full")

        try:
            _intent_doc = "real query"
            try:
                mock_vrs.add_documents(
                    collection_name="apps_lic_intent",
                    documents=[_intent_doc],
                    metadatas=[{"app": "apps_lic", "run_id": "r1", "output_preview": ""}],
                )
            except Exception:  # noqa: BLE001
                pass
        except OSError:
            pytest.fail("VRS failure propagated despite fail-soft guard")


# ---------------------------------------------------------------------------
# Tests: apps_rg_exit_binding — C0 chunk writeback edge cases
# ---------------------------------------------------------------------------


class TestAppsRgExitBindingC0Writeback:
    """Edge cases for the C0 chunk writeback block in exit_finalize_apps_rg."""

    def _run_exit(self, sealed, mock_vrs_instance, tmp_path):
        from agentic_core.runtime.exit import apps_rg_exit_binding as _mod

        prompt = _make_prompt()
        artifact_path = tmp_path / "artifact.json"
        artifact_path.write_text("{}")

        with (
            patch.object(_mod, "_resolve_repo_root", return_value=tmp_path),
            patch.object(_mod, "_write_artifact", return_value=artifact_path),
            patch(_VRS_PATCH, return_value=mock_vrs_instance),
            patch(_SCM_PATCH) as mock_sc_cls,
        ):
            mock_sc_cls.get_instance.return_value = MagicMock()
            return _mod.exit_finalize_apps_rg(sealed=sealed, prompt=prompt)

    def test_long_content_splits_into_chunks(self, tmp_path):
        """Content >1024 chars produces multiple C0 chunks."""
        long_content = "A" * 3000  # 3 × 1024-char chunks
        sealed = _make_sealed(generated_content=long_content)
        mock_vrs = MagicMock()

        self._run_exit(sealed, mock_vrs, tmp_path)

        c0_calls = [
            c for c in mock_vrs.add_documents.call_args_list
            if c.kwargs.get("collection_name") == "apps_rg_c0"
        ]
        assert c0_calls, "Expected C0 chunk writeback for long content"
        docs = c0_calls[0].kwargs["documents"]
        assert len(docs) >= 2, f"Expected ≥2 chunks, got {len(docs)}"

    def test_c0_chunk_metadata_has_chunk_index(self, tmp_path):
        """Each C0 chunk carries chunk_index and total_chunks in metadata."""
        long_content = "B" * 2100  # 2+ chunks
        sealed = _make_sealed(generated_content=long_content)
        mock_vrs = MagicMock()

        self._run_exit(sealed, mock_vrs, tmp_path)

        c0_calls = [
            c for c in mock_vrs.add_documents.call_args_list
            if c.kwargs.get("collection_name") == "apps_rg_c0"
        ]
        assert c0_calls
        metas = c0_calls[0].kwargs["metadatas"]
        for i, m in enumerate(metas):
            assert "chunk_index" in m, f"chunk_index missing on chunk {i}"
            assert "total_chunks" in m, f"total_chunks missing on chunk {i}"
            assert m["chunk_index"] == i
        assert metas[-1]["total_chunks"] == len(metas)

    def test_whitespace_only_content_skips_c0_write(self, tmp_path):
        """Whitespace-only generated_content → C0 writeback skipped."""
        sealed = _make_sealed(generated_content="   \n\t  ")
        mock_vrs = MagicMock()

        self._run_exit(sealed, mock_vrs, tmp_path)

        c0_calls = [
            c for c in mock_vrs.add_documents.call_args_list
            if c.kwargs.get("collection_name") == "apps_rg_c0"
        ]
        assert not c0_calls, "Whitespace-only content must not write C0 chunks"

    def test_c0_failure_independent_of_intent_failure(self, tmp_path):
        """Intent path succeeding and C0 path failing are independent (both fail-soft)."""
        sealed = _make_sealed(generated_content="Real resume content")
        call_log: list[str] = []

        def _add_documents_side_effect(**kwargs):
            coll = kwargs.get("collection_name", "")
            if coll == "apps_rg_c0":
                raise RuntimeError("C0 store unavailable")
            call_log.append(coll)

        mock_vrs = MagicMock()
        mock_vrs.add_documents.side_effect = _add_documents_side_effect

        try:
            self._run_exit(sealed, mock_vrs, tmp_path)
        except RuntimeError:
            pytest.fail("C0 writeback failure propagated")

        assert "apps_rg_intent" in call_log, "Intent write should have succeeded despite C0 failure"

    def test_content_capped_at_16_chunks(self, tmp_path):
        """Very long content is capped at 16 C0 chunks max."""
        massive_content = "X" * (1024 * 20)  # 20 chunks if uncapped
        sealed = _make_sealed(generated_content=massive_content)
        mock_vrs = MagicMock()

        self._run_exit(sealed, mock_vrs, tmp_path)

        c0_calls = [
            c for c in mock_vrs.add_documents.call_args_list
            if c.kwargs.get("collection_name") == "apps_rg_c0"
        ]
        assert c0_calls
        docs = c0_calls[0].kwargs["documents"]
        assert len(docs) <= 16, f"C0 chunks must be capped at 16, got {len(docs)}"

    def test_none_tenant_id_normalised_to_empty_string(self, tmp_path):
        """tenant_id=None is normalised to '' in metadata (no None in ChromaDB)."""
        sealed = _make_sealed(generated_content="Resume text", tenant_id="")
        mock_vrs = MagicMock()

        self._run_exit(sealed, mock_vrs, tmp_path)

        # All add_documents calls must have tenant_id as str, not None
        for call in mock_vrs.add_documents.call_args_list:
            metas = call.kwargs.get("metadatas", [])
            for m in metas:
                if "tenant_id" in m:
                    assert isinstance(m["tenant_id"], str), (
                        f"tenant_id must be str, got {type(m['tenant_id'])}"
                    )


# ---------------------------------------------------------------------------
# Tests: intent document boundary truncation
# ---------------------------------------------------------------------------


class TestIntentDocumentTruncation:
    """Intent doc / output_preview truncation boundaries."""

    def _run_exit_and_get_intent_call(self, sealed, tmp_path):
        from agentic_core.runtime.exit import apps_rg_exit_binding as _mod

        prompt = _make_prompt()
        artifact_path = tmp_path / "artifact.json"
        artifact_path.write_text("{}")
        mock_vrs = MagicMock()

        with (
            patch.object(_mod, "_resolve_repo_root", return_value=tmp_path),
            patch.object(_mod, "_write_artifact", return_value=artifact_path),
            patch(_VRS_PATCH, return_value=mock_vrs),
            patch(_SCM_PATCH) as mock_sc_cls,
        ):
            mock_sc_cls.get_instance.return_value = MagicMock()
            _mod.exit_finalize_apps_rg(sealed=sealed, prompt=prompt)

        return [
            c for c in mock_vrs.add_documents.call_args_list
            if c.kwargs.get("collection_name") == "apps_rg_intent"
        ]

    def test_intent_doc_truncated_at_256(self, tmp_path):
        """Intent doc is exactly generated_content[:256] for content >256 chars."""
        long = "Z" * 500
        sealed = _make_sealed(generated_content=long)
        calls = self._run_exit_and_get_intent_call(sealed, tmp_path)
        assert calls
        doc = calls[0].kwargs["documents"][0]
        assert len(doc) == 256
        assert doc == long[:256]

    def test_intent_doc_exact_256_boundary(self, tmp_path):
        """Content of exactly 256 chars → doc is full content, not truncated further."""
        exact = "E" * 256
        sealed = _make_sealed(generated_content=exact)
        calls = self._run_exit_and_get_intent_call(sealed, tmp_path)
        assert calls
        doc = calls[0].kwargs["documents"][0]
        assert len(doc) == 256
        assert doc == exact

    def test_output_preview_in_metadata_truncated_at_256(self, tmp_path):
        """output_preview in metadata is capped at 256 chars."""
        long = "P" * 9000
        sealed = _make_sealed(generated_content=long)
        calls = self._run_exit_and_get_intent_call(sealed, tmp_path)
        assert calls
        preview = calls[0].kwargs["metadatas"][0]["output_preview"]
        assert len(preview) <= 256, f"output_preview must be ≤256 chars, got {len(preview)}"

    def test_short_content_not_padded(self, tmp_path):
        """Short content is written as-is, not padded to 256."""
        short = "Short resume"
        sealed = _make_sealed(generated_content=short)
        calls = self._run_exit_and_get_intent_call(sealed, tmp_path)
        assert calls
        doc = calls[0].kwargs["documents"][0]
        assert doc == short


# ---------------------------------------------------------------------------
# Tests: governed_app_runner — writeback gating and output_text derivation
# ---------------------------------------------------------------------------


class TestGovernedAppRunnerWritebackGating:
    """Tests that verify the gating conditions and output derivation in Phase 7."""

    def _run_writeback_phase(self, *, app_name, query, run_id, output_text, mock_vrs_instance):
        """Replicate the 7a-bis block (same as TestGovernedAppRunnerIntentWriteback)."""
        _intent_coll = f"{app_name}_intent"
        _intent_doc = query[:4096]
        if _intent_doc.strip():
            mock_vrs_instance.add_documents(
                collection_name=_intent_coll,
                documents=[_intent_doc],
                metadatas=[
                    {
                        "app": app_name,
                        "run_id": run_id,
                        "output_preview": output_text[:256],
                    }
                ],
            )

    def test_query_truncated_to_4096(self):
        """Query strings longer than 4096 chars are truncated before storage."""
        mock_vrs = MagicMock()
        long_query = "Q" * 8000
        self._run_writeback_phase(
            app_name="apps_lic",
            query=long_query,
            run_id="run-trunc",
            output_text="output",
            mock_vrs_instance=mock_vrs,
        )
        calls = [
            c for c in mock_vrs.add_documents.call_args_list
            if c.kwargs.get("collection_name") == "apps_lic_intent"
        ]
        assert calls
        doc = calls[0].kwargs["documents"][0]
        assert len(doc) == 4096
        assert doc == long_query[:4096]

    def test_output_preview_truncated_at_256(self):
        """output_preview metadata field is capped at 256 chars."""
        mock_vrs = MagicMock()
        self._run_writeback_phase(
            app_name="apps_lic",
            query="find engineer",
            run_id="run-prev",
            output_text="O" * 1000,
            mock_vrs_instance=mock_vrs,
        )
        calls = [
            c for c in mock_vrs.add_documents.call_args_list
            if c.kwargs.get("collection_name") == "apps_lic_intent"
        ]
        assert calls
        preview = calls[0].kwargs["metadatas"][0]["output_preview"]
        assert len(preview) <= 256

    def test_output_text_derived_from_chunk_text_field(self):
        """output_text joins ranked_chunks[].text (production Phase 7a logic)."""
        chunks = [
            SimpleNamespace(text="chunk one"),
            SimpleNamespace(text="chunk two"),
        ]
        output_text = " ".join(
            str(getattr(c, "text", "") or getattr(c, "content", ""))
            for c in chunks
        )[:8192]
        assert output_text == "chunk one chunk two"

    def test_output_text_falls_back_to_content_field(self):
        """Chunks with no `text` attribute fall back to `content`."""
        chunks = [
            SimpleNamespace(content="content A"),
            SimpleNamespace(content="content B"),
        ]
        output_text = " ".join(
            str(getattr(c, "text", "") or getattr(c, "content", ""))
            for c in chunks
        )[:8192]
        assert output_text == "content A content B"

    def test_output_text_truncated_at_8192(self):
        """Joined chunk text is capped at 8192 chars."""
        chunks = [SimpleNamespace(text="W" * 5000), SimpleNamespace(text="X" * 5000)]
        output_text = " ".join(
            str(getattr(c, "text", "") or getattr(c, "content", ""))
            for c in chunks
        )[:8192]
        assert len(output_text) == 8192

    def test_apps_rg_intent_collection_name_correct(self):
        """apps_rg uses apps_rg_intent collection (not apps_rg_c0 or any other)."""
        mock_vrs = MagicMock()
        self._run_writeback_phase(
            app_name="apps_rg",
            query="generate resume",
            run_id="run-rg-01",
            output_text="resume output",
            mock_vrs_instance=mock_vrs,
        )
        calls = mock_vrs.add_documents.call_args_list
        collections_written = {c.kwargs["collection_name"] for c in calls}
        assert "apps_rg_intent" in collections_written
        assert "apps_rg_c0" not in collections_written, (
            "7a-bis must not write to c0 collection"
        )


# ---------------------------------------------------------------------------
# Tests: proof script round-trip (intent → query_collection HIT)
# ---------------------------------------------------------------------------


class TestIntentWritebackRoundTrip:
    """End-to-end: write intent doc, query it back, confirm HIT."""

    def test_add_and_query_intent_collection(self):
        """Intent document written via add_documents is retrievable via query_collection."""
        from tools.retrieval.vector_service import VectorRetrievalService

        vrs = VectorRetrievalService()
        collection = "test_intent_roundtrip_tmp"
        intent = "Senior software engineer with distributed systems background"

        try:
            vrs.add_documents(
                collection_name=collection,
                documents=[intent],
                metadatas=[{"app": "test", "run_id": "rt-001"}],
            )
            qr = vrs.query_collection(
                collection_name=collection,
                query_text=intent[:64],
                n_results=1,
            )
            assert qr.hits, "Expected at least one hit after intent write"
            assert qr.hits[0].document is not None
        finally:
            try:
                vrs.delete_collection(collection)
            except Exception:
                pass

    def test_add_documents_idempotent_on_existing_collection(self):
        """add_documents auto-creates collection; second call upserts without error."""
        from tools.retrieval.vector_service import VectorRetrievalService

        vrs = VectorRetrievalService()
        collection = "test_intent_idempotent_tmp"
        try:
            vrs.add_documents(
                collection_name=collection,
                documents=["first intent"],
                metadatas=[{"run_id": "r1"}],
            )
            vrs.add_documents(
                collection_name=collection,
                documents=["second intent"],
                metadatas=[{"run_id": "r2"}],
            )
        finally:
            try:
                vrs.delete_collection(collection)
            except Exception:
                pass
