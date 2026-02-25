"""Embedding Surface Allowlist - Architectural Closure

Explicit allowlist of embedding surface violations that are tolerated
but tracked for future remediation. Any violation not in this list
will cause CI to fail.

Generated from hardening sweep results.
"""

from typing import Set

# Explicit allowlist of embedding surface violations
# Format: "relative/path/from/repo:line:type:details"
EMBEDDING_ALLOWLIST: Set[str] = {
    # Meta-learning embedding service (known technical debt)
    "system_learning/engines/meta_learning_embedding_service.py:58:EMBEDDING_ACCESS:Access to EmbeddingServiceFactory.get_or_disabled outside factory",
    "system_learning/pipelines/meta_learning_pipeline.py:523:EMBEDDING_ACCESS:Access to EmbeddingServiceFactory.get_or_disabled outside factory", 
    "system_learning/pipelines/meta_learning_pipeline.py:650:EMBEDDING_ACCESS:Access to EmbeddingServiceFactory.get_or_disabled outside factory",
    
    # Late interaction reranker utility (external dependency)
    "apps_shared/utils/late_interaction_reranker_util.py:44:EMBEDDING_IMPORT:From import from sentence_transformers outside factory",
    "apps_shared/utils/late_interaction_reranker_util.py:63:EMBEDDING_IMPORT:From import from sentence_transformers outside factory",
}

# SHA256 hash of sorted allowlist for drift detection
def compute_allowlist_hash() -> str:
    """Compute SHA256 hash of sorted allowlist for deterministic digest."""
    import hashlib
    
    sorted_items = sorted(EMBEDDING_ALLOWLIST)
    content = "\n".join(sorted_items)
    return hashlib.sha256(content.encode()).hexdigest()

# Allowlist hash for inclusion in W34-HARDENING-DIGEST
EMBEDDING_ALLOWLIST_HASH = compute_allowlist_hash()

# Validation function
def is_embedding_violation_allowed(file_path: str, line: int, violation_type: str, details: str) -> bool:
    """Check if embedding violation is in allowlist."""
    key = f"{file_path}:{line}:{violation_type}:{details}"
    return key in EMBEDDING_ALLOWLIST

if __name__ == "__main__":
    # Print allowlist info for debugging
    print(f"Embedding Allowlist: {len(EMBEDDING_ALLOWLIST)} violations")
    print(f"Allowlist Hash: {EMBEDDING_ALLOWLIST_HASH}")
    for item in sorted(EMBEDDING_ALLOWLIST):
        print(f"  {item}")
