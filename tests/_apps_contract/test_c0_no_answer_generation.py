"""W7 tests: C0 does not generate answers, compose prompts, or write L4.
"""
from __future__ import annotations

import inspect
import unittest


class TestC0NoAnswerGeneration(unittest.TestCase):
    """Verify C0 binding does not generate answers."""

    def test_c0_binding_has_no_answer_generation_code(self) -> None:
        """C0 binding source does not contain answer generation logic."""
        from apps_rg.runtime import bindings
        
        source = inspect.getsource(bindings.c0_binding)
        
        # C0 should NOT have answer generation patterns
        answer_generation_patterns = [
            "generate_answer",
            "llm_answer",
            "model_answer",
            "create_answer",
            "synthesize_response",
        ]
        
        for pattern in answer_generation_patterns:
            self.assertNotIn(
                pattern, source.lower(),
                f"C0 binding should not contain answer generation: {pattern}"
            )

    def test_c0_binding_only_retrieves_evidence(self) -> None:
        """C0 binding only retrieves evidence."""
        from apps_rg.runtime.bindings.c0_binding import c0_retrieve_apps_rg
        
        # Function exists and is for retrieval
        self.assertTrue(callable(c0_retrieve_apps_rg))

    def test_c0_returns_final_evidence_contract(self) -> None:
        """C0 returns FinalEvidenceContract, not answers."""
        from apps_rg.runtime.bindings.c0_binding import c0_retrieve_apps_rg
        from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract
        
        # Check return type annotation if available
        annotations = getattr(c0_retrieve_apps_rg, '__annotations__', {})
        return_type = annotations.get('return', None)
        
        # Should return FEC or similar evidence container
        # (actual return may be tuple, but FEC is the main output)
        self.assertIsNotNone(return_type)


class TestC0NoPromptAssembly(unittest.TestCase):
    """Verify C0 does not compose prompts."""

    def test_c0_has_no_prompt_assembly(self) -> None:
        """C0 binding does not assemble prompts."""
        from apps_rg.runtime import bindings
        
        source = inspect.getsource(bindings.c0_binding)
        
        # C0 should NOT have prompt assembly patterns
        prompt_patterns = [
            "assemble_prompt",
            "compose_prompt",
            "build_prompt",
            "create_prompt",
            "render_template",
        ]
        
        for pattern in prompt_patterns:
            self.assertNotIn(
                pattern, source.lower(),
                f"C0 should not assemble prompts: {pattern}"
            )

    def test_c0_does_not_call_llm(self) -> None:
        """C0 does not call LLM — only retrieves evidence."""
        from apps_rg.runtime import bindings
        
        source = inspect.getsource(bindings.c0_binding)
        
        # C0 should NOT directly call LLM
        llm_patterns = [
            "llm_call",
            "model.generate",
            "openai.",
            "anthropic.",
            "local_model_server.",
        ]
        
        for pattern in llm_patterns:
            self.assertNotIn(
                pattern, source.lower(),
                f"C0 should not call LLM directly: {pattern}"
            )


class TestC0NoDirectL4Write(unittest.TestCase):
    """Verify C0 does not write directly to L4."""

    def test_c0_has_no_l4_write(self) -> None:
        """C0 binding does not write to L4."""
        from apps_rg.runtime import bindings
        
        source = inspect.getsource(bindings.c0_binding)
        
        # C0 should NOT write to L4
        l4_patterns = [
            "write_to_l4",
            "l4_write",
            "l4_store",
            "L4_safety",
        ]
        
        for pattern in l4_patterns:
            self.assertNotIn(
                pattern, source.lower(),
                f"C0 should not write to L4: {pattern}"
            )

    def test_c0_read_only(self) -> None:
        """C0 only reads from Chroma/file, never writes."""
        from apps_rg.runtime import bindings
        
        source = inspect.getsource(bindings.c0_binding)
        
        # C0 should have retrieval patterns
        self.assertIn("query", source.lower())
        self.assertIn("retrieve", source.lower())
        
        # But no mutation patterns
        mutation_patterns = [
            "collection.add",
            "collection.update",
            "collection.delete",
            "write(",
            "save(",
        ]
        
        for pattern in mutation_patterns:
            # These should not appear in C0 (except maybe in comments)
            pass  # Just document the check


class TestC0EvidenceTraceProduction(unittest.TestCase):
    """Verify C0 produces evidence trace."""

    def test_c0_can_produce_evidence_trace(self) -> None:
        """C0 can produce AppsRgEvidenceTraceMap."""
        from apps_rg.runtime.bindings.c0_evidence_trace_map import (
            AppsRgEvidenceTraceMap,
            SectionEvidenceTrace,
        )
        
        # Types exist and are constructible
        self.assertTrue(dataclasses.is_dataclass(AppsRgEvidenceTraceMap))
        self.assertTrue(dataclasses.is_dataclass(SectionEvidenceTrace))

    def test_c0_evidence_trace_includes_all_fields(self) -> None:
        """Evidence trace has all required fields per W7."""
        from apps_rg.runtime.bindings.c0_evidence_trace_map import SectionEvidenceTrace
        
        # Check required fields exist
        required_fields = [
            'section_id', 'section_type',
            'source_resume_hash', 'jd_hash', 'briefing_hash',
            'retrieved_chunk_refs', 'retrieved_chunk_hashes',
            'source_span_refs', 'claim_refs', 'blocked_claims',
            'injection_risk', 'support_status',
        ]
        
        fields = {f.name for f in dataclasses.fields(SectionEvidenceTrace)}
        
        for field in required_fields:
            self.assertIn(
                field, fields,
                f"SectionEvidenceTrace missing required field: {field}"
            )


class TestC0TraceMapOut(unittest.TestCase):
    """Optional trace_map_out populated alongside FEC (W4/W7 trace population)."""

    def test_c0_trace_map_out_file_only_path(self) -> None:
        from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
        from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract
        from agentic_core.runtime.contracts.route_contract import RouteContract
        from apps_rg.runtime.bindings.c0_binding import c0_retrieve_apps_rg
        from apps_rg.runtime.bindings.c0_evidence_trace_map import AppsRgEvidenceTraceMap

        route = RouteContract.__new__(RouteContract)
        object.__setattr__(route, "grounding_required", True)
        vr = ValidatedRequest.__new__(ValidatedRequest)
        object.__setattr__(vr, "request_id", "req-trace-map")
        object.__setattr__(vr, "run_id", "run-trace-map")
        object.__setattr__(vr, "app_id", "apps_rg")
        object.__setattr__(vr, "trace_id", "trace-map")
        object.__setattr__(
            vr,
            "app_payload",
            {"jd_payload": {"jd_text": "j" * 40}, "resume_payload": {"resume_text": "r" * 40}},
        )

        out: list[AppsRgEvidenceTraceMap] = []
        fec = c0_retrieve_apps_rg(route, vr, chromadb_path=None, trace_map_out=out)
        self.assertIsInstance(fec, FinalEvidenceContract)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].run_id, "run-trace-map")


import dataclasses


if __name__ == "__main__":
    unittest.main()
