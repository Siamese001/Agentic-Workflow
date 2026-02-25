"""Cross-Layer Import Allowlist - Architectural Closure

Explicit allowlist of cross-layer import violations that are tolerated
but tracked for future remediation. Any violation not in this list
will cause CI to fail.

Generated from hardening sweep results.
"""

from typing import Set

# Explicit allowlist of cross-layer import violations
# Format: "relative/path/from/repo:description"
CROSS_LAYER_ALLOWLIST: Set[str] = {
    # L2 configuration modules importing L0 (technical debt)
    "agentic_core/L2_execution/config/hybrid_retriever_config.py:Direct L0 import in L2",
    "agentic_core/L2_execution/config/unified_workflow_config.py:Direct L0 import in L2",
    
    # Validation orchestrator importing across layers (technical debt)
    "agentic_core/L2_execution/engines/validation_orchestrator.py:Direct L0 import in L2",
    "agentic_core/L2_execution/engines/validation_orchestrator.py:Direct L1 import in L2",
    
    # Classification compliance healer importing L0 (technical debt)
    "agentic_core/L2_execution/healers/classification_compliance_healer.py:Direct L0 import in L2",
}

# SHA256 hash of sorted allowlist for drift detection
def compute_allowlist_hash() -> str:
    """Compute SHA256 hash of sorted allowlist for deterministic digest."""
    import hashlib
    
    sorted_items = sorted(CROSS_LAYER_ALLOWLIST)
    content = "\n".join(sorted_items)
    return hashlib.sha256(content.encode()).hexdigest()

# Allowlist hash for inclusion in W34-HARDENING-DIGEST
CROSS_LAYER_ALLOWLIST_HASH = compute_allowlist_hash()

# Validation function
def is_cross_layer_violation_allowed(file_path: str, description: str) -> bool:
    """Check if cross-layer violation is in allowlist."""
    key = f"{file_path}:{description}"
    return key in CROSS_LAYER_ALLOWLIST

if __name__ == "__main__":
    # Print allowlist info for debugging
    print(f"Cross-Layer Allowlist: {len(CROSS_LAYER_ALLOWLIST)} violations")
    print(f"Allowlist Hash: {CROSS_LAYER_ALLOWLIST_HASH}")
    for item in sorted(CROSS_LAYER_ALLOWLIST):
        print(f"  {item}")
