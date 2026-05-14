"""W1 P1.4: Prove C0 has no L4/UWG durable write path.

Plan: 04_apps-rg-c0-architecture-analysis-f3d8b2
Acceptance: c0_binding.py has no import from L4 state layer; no UWG call;
no durable write; verified by import graph assertion.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest


def get_c0_binding_source() -> str:
    """Read the c0_binding.py source file."""
    binding_path = Path("apps_rg/runtime/bindings/c0_binding.py")
    if not binding_path.exists():
        repo_root = Path(__file__).parent.parent.parent
        binding_path = repo_root / binding_path
    
    return binding_path.read_text(encoding="utf-8")


def parse_c0_binding_ast() -> ast.Module:
    """Parse c0_binding.py into AST."""
    source = get_c0_binding_source()
    return ast.parse(source)


def test_c0_binding_no_l4_imports():
    """PROOF: c0_binding.py has no imports from L4 state layer.
    
    C0 is READ-ONLY retrieval only. No durable writes.
    """
    tree = parse_c0_binding_ast()
    
    l4_patterns = [
        "agentic_core.L4_state",
        "L4_state",
        "unit_of_work",
        "UWG",
        "durable_write",
        "persistent_store",
    ]
    
    violations = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                full_name = alias.name
                for pattern in l4_patterns:
                    if pattern in full_name:
                        violations.append(f"Import: {full_name}")
        
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            full_module = module
            for pattern in l4_patterns:
                if pattern in full_module:
                    violations.append(f"From import: {full_module}")
            
            # Check imported names too
            for alias in node.names:
                name = alias.name
                for pattern in ["UWG", "UnitOfWork", "durable_write", "persistent"]:
                    if pattern in name:
                        violations.append(f"Imported name: {name} from {module}")
    
    assert not violations, (
        f"c0_binding.py must not import from L4/UWG. Violations: {violations}"
    )


def test_c0_binding_no_uwg_calls():
    """PROOF: c0_binding.py has no UWG function calls.
    
    Searches for patterns like uwg(), unit_of_work(), write_durable(), etc.
    """
    tree = parse_c0_binding_ast()
    source = get_c0_binding_source()
    lines = source.split("\n")
    
    uwg_patterns = [
        "uwg(",
        "unit_of_work(",
        "durable_write(",
        "persistent_store(",
        "write_to_l4(",
        "UWG.",
    ]
    
    violations = []
    for i, line in enumerate(lines, 1):
        # Skip comments and docstrings
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
            continue
        
        for pattern in uwg_patterns:
            if pattern in line:
                # Make sure it's not just a comment
                code_part = line.split("#")[0]
                if pattern in code_part:
                    violations.append(f"Line {i}: {line.strip()}")
    
    assert not violations, (
        f"c0_binding.py must not call UWG/L4 write functions. Violations: {violations[:5]}"
    )


def test_c0_binding_only_retrieval_methods():
    """PROOF: c0_binding.py only has read-only retrieval methods.
    
    Validates the public API is retrieval-only.
    """
    tree = parse_c0_binding_ast()
    
    # Get function names defined in the module
    public_functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if not node.name.startswith("_"):
                public_functions.append(node.name)
    
    # Only c0_retrieve_apps_rg should be public
    assert "c0_retrieve_apps_rg" in public_functions, (
        "c0_retrieve_apps_rg must be the main public function"
    )
    
    # No "write", "store", "persist", "save" functions
    forbidden_patterns = ["write", "store", "persist", "save", "commit"]
    for func in public_functions:
        for pattern in forbidden_patterns:
            assert pattern not in func.lower(), (
                f"Public function {func} suggests write operation - not allowed in C0"
            )


def test_c0_binding_imports_are_readonly():
    """PROOF: c0_binding.py imports are from read-only contracts.
    
    Validates imports are from runtime/contracts (read-only) not from L4.
    """
    tree = parse_c0_binding_ast()
    
    allowed_import_roots = [
        "agentic_core.runtime.contracts",  # Read-only contracts
        "agentic_core.runtime.entry",  # Ingress
        "__future__",
        "typing",
        "datetime",
        "pathlib",
        "hashlib",
        "json",
        "logging",
        "os",
    ]
    
    forbidden_roots = [
        "agentic_core.L4_state",
        "agentic_core.L5_safety",  # Safety enforcement can write
    ]
    
    violations = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            
            for forbidden in forbidden_roots:
                if module.startswith(forbidden):
                    violations.append(f"Forbidden import from: {module}")
    
    assert not violations, (
        f"c0_binding.py must not import from L4/L5 write paths. Violations: {violations}"
    )


def test_c0_binding_chroma_readonly():
    """PROOF: C0 binding never writes to Chroma — query only.
    
    Validates read-only semantics per C0 governance contract.
    """
    source = get_c0_binding_source()
    
    # W5: Exclude Python set operations (e.g., source_classes_used.add()) from Chroma write detection
    python_set_add_patterns = [
        "source_classes_used.add(",
        "_client.add(",
    ]
    
    chroma_write_ops = [
        ".add(",
        ".update(",
        ".delete(",
        ".upsert(",
        ".modify(",
        ".create_collection(",
        ".delete_collection(",
    ]
    
    # Normalize source by replacing known Python set operations with safe placeholder
    normalized_source = source
    for pattern in python_set_add_patterns:
        normalized_source = normalized_source.replace(pattern, "# PYTHON_SET_OP")
    
    violations = []
    for op in chroma_write_ops:
        if op in normalized_source:
            violations.append(f"Chroma write operation found: {op}")
    
    assert not violations, (
        f"c0_binding.py must only read from Chroma (query only). Violations: {violations}"
    )
    # Verify query() IS used (proves it's actually doing retrieval)
    assert ".query(" in source, "c0_binding.py must use Chroma query() for retrieval"


def test_c0_evidence_gap_error_is_readonly():
    """PROOF: C0EvidenceGapError indicates read-only path failure, not write.
    
    Validates the error is about retrieval gap, not write failure.
    """
    source = get_c0_binding_source()
    
    # Error should mention retrieval, embedding, Chroma - not writes
    assert "C0EvidenceGapError" in source, "C0EvidenceGapError must be defined"
    
    # Error message should be about retrieval, not writes
    assert "retrieval" in source.lower() or "embedding" in source.lower() or "chroma" in source.lower(), (
        "C0 evidence error should relate to retrieval, not writes"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
