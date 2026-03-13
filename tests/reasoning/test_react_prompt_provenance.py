"""CI tests — ReAct prompt provenance recording.

Verifies:
  - PromptProvenanceRecord is built correctly from inputs.
  - prompt_hash is deterministic for identical prompt text.
  - record_hash is stable across replay runs.
  - Different prompt texts produce different prompt_hash values.
  - rag_context_ids are captured correctly.

CI failure condition:
  - Prompt hash differs between replay runs for identical input.
  - Provenance record missing required fields.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.types.react_trace_types import PromptProvenanceRecord


class TestPromptProvenanceRecord:
    def _make(
        self,
        prompt_text: str = "What is the capital?",
        prompt_template_id: str = "react_v1",
        rag_context_ids: tuple[str, ...] = ("ctx1", "ctx2"),
        policy_hash: str = "pol1",
        model_id: str = "gpt-4",
    ) -> PromptProvenanceRecord:
        return PromptProvenanceRecord.build(
            prompt_text=prompt_text,
            prompt_template_id=prompt_template_id,
            rag_context_ids=rag_context_ids,
            policy_hash=policy_hash,
            model_id=model_id,
        )

    def test_build_sets_prompt_hash(self):
        rec = self._make()
        assert rec.prompt_hash != ""
        assert len(rec.prompt_hash) == 64

    def test_prompt_hash_deterministic(self):
        rec1 = self._make(prompt_text="Hello world")
        rec2 = self._make(prompt_text="Hello world")
        assert rec1.prompt_hash == rec2.prompt_hash

    def test_different_prompt_different_hash(self):
        rec1 = self._make(prompt_text="Question A")
        rec2 = self._make(prompt_text="Question B")
        assert rec1.prompt_hash != rec2.prompt_hash

    def test_record_hash_stable(self):
        rec1 = self._make()
        rec2 = self._make()
        assert rec1.record_hash() == rec2.record_hash()

    def test_rag_context_ids_captured(self):
        rec = self._make(rag_context_ids=("id_x", "id_y", "id_z"))
        assert rec.rag_context_ids == ("id_x", "id_y", "id_z")

    def test_empty_rag_context_ids(self):
        rec = self._make(rag_context_ids=())
        assert rec.rag_context_ids == ()
        assert len(rec.prompt_hash) == 64

    def test_policy_hash_stored(self):
        rec = self._make(policy_hash="pol_xyz")
        assert rec.policy_hash == "pol_xyz"

    def test_model_id_stored(self):
        rec = self._make(model_id="claude-3")
        assert rec.model_id == "claude-3"

    def test_prompt_template_id_stored(self):
        rec = self._make(prompt_template_id="tmpl_99")
        assert rec.prompt_template_id == "tmpl_99"

    def test_record_is_immutable(self):
        rec = self._make()
        with pytest.raises((AttributeError, TypeError)):
            rec.prompt_hash = "mutated"  # type: ignore[misc]

    def test_different_policy_different_record_hash(self):
        rec1 = self._make(policy_hash="pol_a")
        rec2 = self._make(policy_hash="pol_b")
        assert rec1.record_hash() != rec2.record_hash()

    def test_different_rag_ids_different_record_hash(self):
        rec1 = self._make(rag_context_ids=("c1",))
        rec2 = self._make(rag_context_ids=("c2",))
        assert rec1.record_hash() != rec2.record_hash()

    def test_canonical_bytes_deterministic(self):
        rec = self._make()
        assert rec.canonical_bytes() == rec.canonical_bytes()
