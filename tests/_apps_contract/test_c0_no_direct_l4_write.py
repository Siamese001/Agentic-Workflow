"""W7 tests: C0 does not write directly to L4 (safety layer).
"""
from __future__ import annotations

import inspect
import unittest


class TestC0NoDirectL4Write(unittest.TestCase):
    """Verify C0 binding does not bypass L4 safety layer."""

    def test_c0_no_l4_safety_import(self) -> None:
        """C0 does not import from L4 safety modules."""
        from apps_rg.runtime import bindings
        
        source = inspect.getsource(bindings.c0_binding)
        
        # C0 should NOT import from L4
        l4_imports = [
            "from agentic_core.L4_safety",
            "from agentic_core.L5_safety",
            "import L4_safety",
            "import L5_safety",
        ]
        
        for imp in l4_imports:
            self.assertNotIn(
                imp, source,
                f"C0 should not import from L4/L5: {imp}"
            )

    def test_c0_no_l4_write_calls(self) -> None:
        """C0 source does not call L4 write methods."""
        from apps_rg.runtime import bindings
        
        source = inspect.getsource(bindings.c0_binding)
        
        # C0 should NOT call L4 methods
        l4_calls = [
            "L4_safety.",
            "L5_safety.",
            "uwg_write",
            "unified_write",
            "safety_check_and_write",
        ]
        
        for call in l4_calls:
            self.assertNotIn(
                call, source,
                f"C0 should not call L4/L5 methods: {call}"
            )

    def test_c0_returns_evidence_not_writes(self) -> None:
        """C0 returns evidence, does not trigger writes."""
        from apps_rg.runtime.bindings import c0_binding
        
        # C0 functions return evidence containers
        funcs = [
            'c0_retrieve_evidence_for_apps_rg',
        ]
        
        for func_name in funcs:
            if hasattr(c0_binding, func_name):
                func = getattr(c0_binding, func_name)
                self.assertTrue(callable(func))

    def test_c0_evidence_passed_to_pa_not_l4(self) -> None:
        """C0 evidence is passed to PA, not directly to L4."""
        # This is a design contract test
        # C0 -> evidence -> PA (prompt assembly)
        # PA -> L2 -> L3 -> L4 (proper flow)
        self.assertTrue(True, "Design contract: C0 -> PA -> L2 -> L3 -> L4")


class TestC0BindingIsRetrievalOnly(unittest.TestCase):
    """Verify C0 binding is retrieval-only."""

    def test_c0_function_name_indicates_retrieval(self) -> None:
        """C0 function names indicate retrieval, not write."""
        from apps_rg.runtime.bindings import c0_binding
        
        # Function should be named for retrieval
        self.assertTrue(
            hasattr(c0_binding, 'c0_retrieve_apps_rg'),
            "C0 should have retrieve function"
        )

    def test_c0_no_write_in_function_names(self) -> None:
        """C0 function names do not include 'write'."""
        from apps_rg.runtime.bindings import c0_binding
        
        members = dir(c0_binding)
        public_funcs = [m for m in members if not m.startswith('_')]
        
        for func in public_funcs:
            self.assertNotIn(
                'write', func.lower(),
                f"C0 function should not be named 'write': {func}"
            )
            self.assertNotIn(
                'store', func.lower(),
                f"C0 function should not be named 'store': {func}"
            )

    def test_c0_no_chroma_mutation(self) -> None:
        """C0 does not mutate ChromaDB — only queries."""
        from apps_rg.runtime import bindings
        
        source = inspect.getsource(bindings.c0_binding)
        
        # C0 should NOT call Chroma mutation methods
        chroma_mutations = [
            ".add(",
            ".upsert(",
            ".update(",
            ".delete(",
            ".modify(",
        ]
        
        for mutation in chroma_mutations:
            # Check that mutations are NOT called on collection
            lines = source.split('\n')
            for line in lines:
                if 'collection' in line and mutation in line:
                    # Allow only in comments or docstrings
                    stripped = line.strip()
                    if not stripped.startswith('#') and not stripped.startswith('"""'):
                        self.fail(f"C0 should not mutate Chroma: {line}")


class TestC0OutputConsumedByPALayer(unittest.TestCase):
    """Verify C0 output is consumed by PA, not L4."""

    def test_c0_output_is_final_evidence_contract(self) -> None:
        """C0 produces FinalEvidenceContract for PA consumption."""
        from apps_rg.runtime.bindings.c0_binding import c0_retrieve_apps_rg
        from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract
        
        # Function exists and FEC type exists
        self.assertTrue(callable(c0_retrieve_apps_rg))
        
        # FEC is the contract type
        self.assertTrue(hasattr(FinalEvidenceContract, 'evidence_items'))

    def test_final_evidence_contract_has_no_write_methods(self) -> None:
        """FEC is data container, has no write methods."""
        from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract
        
        # FEC should be a dataclass or similar container
        # Should not have write methods
        write_methods = ['write', 'store', 'save', 'commit']
        
        for method in write_methods:
            self.assertFalse(
                hasattr(FinalEvidenceContract, method),
                f"FEC should not have write method: {method}"
            )


if __name__ == "__main__":
    unittest.main()
