"""Compatibility shim that re-exports the v10.8 RAG execution stack."""

# from archives.legacy_resume_gen.Agentic-Workflow-10_7_main.stacks_v10_8.rag_execution import RAGExecutionStack  # INVALID: Cannot import from path with hyphens

__all__ = ["RAGExecutionStack"]
