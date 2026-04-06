# ADR-002: Interface Layer Protocol-First Architecture

**Status**: Accepted
**Date**: 2026-04-06
**Context**: agentic_core/interfaces/ directory
**Decision**: Adopt protocol-first architecture for agentic_core interfaces/

---

## Context

The `agentic_core/interfaces/` directory had a split-brain architecture problem:
- Two competing patterns with no documented rationale
- Protocol files (`I*Protocol.py`) using `typing.Protocol` for type-safe contracts
- Re-export shims (e.g., `gateway.py`, `spine.py`) that directly imported from L0-L6 implementations
- 8 protocol files were archived as dead code (zero production usage)
- No naming convention for non-protocol files
- FileClassificationAgent had no rules for `interfaces/` directory

This created architectural ambiguity and violated the single-source-of-truth principle.

---

## Decision

Adopt **protocol-first architecture** for the interfaces layer:

1. **Protocol Files (`I*Protocol.py`)**: Define runtime-checkable contracts using `typing.Protocol`
   - These are the canonical source of truth for layer boundaries
   - All new cross-layer contracts must be defined as protocols
   - Protocols are re-exported via `agentic_core/interfaces/__init__.py`

2. **Shim Files (`*_shim.py`)**: Re-export concrete implementations from L0-L6
   - Provide backward compatibility for existing code
   - Clearly marked with `_shim.py` suffix for honest naming
   - May be deprecated over time as code migrates to protocol-first pattern

3. **Type Files (`*_types.py`)**: Contain type definitions and dataclasses
   - Not protocols, but reusable type definitions
   - Follow existing FileClassificationAgent naming rules

4. **Naming Convention** (added to FileClassificationAgent):
   - Protocol files: `I[A-Z].*Protocol.py` → `agentic_core/interfaces/`
   - Shim files: `*_shim.py` → `agentic_core/interfaces/`
   - Type files: `*_types.py` → `agentic_core/interfaces/`

---

## Implementation

### Wave 1: Restore & Consolidate IHealerProtocol
- Restored `IHealerProtocol.py` from archive to `agentic_core/interfaces/`
- Deleted duplicate from `agentic_core/L3_orchestration/types/healer_types.py`
- Added deprecation comment pointing to canonical location

### Wave 2: Implement Missing Protocols
- Created `IOrchestratorProtocol.py` - contract for orchestration operations
- Created `IValidatorProtocol.py` - contract for validation operations
- Created `IMemoryStoreProtocol.py` - contract for memory/storage operations
- All protocols use `@runtime_checkable` decorator

### Wave 3: Rename Shims to Honest Names
- Renamed 11 shim files: `gateway.py` → `gateway_shim.py`, etc.
- Updated `__init__.py` to export new protocols
- Removed outdated deletion comments

### Wave 4: Update Production Imports
- Updated all production code to use new shim names
- Updated shim docstrings to reflect new import paths
- Verified imports work: `from agentic_core.interfaces import *`

### Wave 5: Documentation & Enforcement
- Created this ADR documenting the decision
- Updated FileClassificationAgent with interfaces/ naming rules (pending)

---

## Consequences

### Positive
- **Architectural Clarity**: Single coherent pattern for interfaces layer
- **Type Safety**: Protocols provide runtime-checkable contracts
- **Layer Decoupling**: Protocols define boundaries without coupling to implementations
- **Honest Naming**: `_shim.py` suffix clearly indicates re-export purpose
- **Extensibility**: New implementations can be added without breaking contracts

### Negative
- **Migration Cost**: Existing code must be updated to use new shim names (done)
- **Indirection**: Additional layer of abstraction for shims (temporary)
- **Learning Curve**: Developers must understand protocol vs shim distinction

### Risks
- **Incomplete Migration**: Some code may still use old import paths (mitigated by batch replacement)
- **Protocol Drift**: Protocols may diverge from implementations (mitigated by runtime checks)

---

## Migration Path

1. **Phase 1 (Complete)**: Establish pattern with 4 strategic protocols
   - IHealerProtocol (restored)
   - IOrchestratorProtocol (new)
   - IValidatorProtocol (new)
   - IMemoryStoreProtocol (new)

2. **Phase 2 (Future)**: Gradually migrate production code to depend on protocols
   - New code: Use protocols directly
   - Old code: Continue using shims (tech debt tracked)

3. **Phase 3 (Future)**: Deprecate and remove shims
   - Once all code uses protocols, shims can be removed
   - Timeline: Determined by adoption rate

---

## Alternatives Considered

### Option A: Protocol-First (Chosen)
- Define protocols for all layer boundaries
- Keep shims for backward compatibility
- **Pros**: Type-safe, extensible, clear contracts
- **Cons**: Higher upfront cost, more files

### Option B: Shim-Only
- Remove all protocols, keep only shims
- Rename shims to honest names
- **Pros**: Simple, minimal changes
- **Cons**: No type safety, tight coupling to implementations

### Option C: Hybrid (Rejected)
- Keep both patterns without consolidation
- **Pros**: No migration needed
- **Cons**: Architectural ambiguity, split-brain problem persists

---

## References

- FileClassificationAgent naming conventions
- Python typing.Protocol documentation
- OpenAI SVP Engineering architectural standards (layer decoupling, type safety)
