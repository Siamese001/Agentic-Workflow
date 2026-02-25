# vLLM Model Configuration and Windsurf Routing Report

**Version:** REV 5
**routing_invariants_version:** 1
**Status:** Architectural Invariants Enforced

---

## Section 1 — Architectural Invariants

The vLLM integration operates under strict architectural invariants. Any deviation from this list is a test failure.

### Invariant 1: L0 Isolation Mandate
L0 performs deterministic path selection only and contains zero model imports. No `vllm`, `transformers`, or `torch` imports are permitted in L0–L6 layer directories.

### Invariant 2: Single Routing Algorithm
Routing uses an ordered predicate list with first-match-wins semantics. No decision tables or heuristic routing rubrics are permitted.

### Invariant 3: Predicate Purity
Routing predicates are pure functions with no side effects. They accept only deterministic inputs and produce deterministic outputs. Each evaluation includes a `predicate_evaluation_hash`.

### Invariant 4: Mutation Envelope
vLLM outputs are proposals only. L2.2 is the sole authority for mutations. All vLLM interactions flow through the boundary client as proposals.

### Invariant 5: Hash Chain
All mutations follow a distinct hash chain: `proposal_hash → validation_hash → execution_hash`. These hashes must be cryptographically distinct and auditable.

### Invariant 6: Canonical Hash
All hashing uses canonical serialization: `json.dumps(sort_keys=True, separators=(',', ':'))`, SHA-256, UTF-8 encoding. No timestamps, UUIDs, or non-deterministic data are included.

### Invariant 7: Structural Escalation
Only L3 and L5 may perform structural escalation. No other layers may escalate or modify structural components.

### Invariant 8: routing_version Immutability
The `routing_version` is frozen at run start and cannot be mutated during execution. All routing decisions reference the same version.

### Invariant 9: CI Static Import Scan
Continuous integration must scan L0–L6 for `import vllm`, `from vllm`, `import transformers`, `import torch` and return ZERO MATCHES.

### Invariant 10: No Dynamic Imports
Dynamic imports via `importlib.import_module` are forbidden in L0–L6 layers.

### Invariant 11: No Global State in Predicates
Routing predicates cannot access or modify global state. All predicate inputs must be explicit parameters.

### Invariant 12: No Dynamic Bypass
Dynamic attribute access (`getattr`), built-in imports (`__import__`), and `sys.modules` mutations are forbidden in L0–L6.

---

## Section 2 — Canonical Normalization Rules

All payloads must be normalized before hashing:

1. **Tuples to Lists:** Convert all tuples to lists
2. **Dict Key Sorting:** Sort dictionary keys recursively
3. **Float Precision:** Round floats to 12 decimal places
4. **Set Handling:** Convert sets to sorted lists
5. **Decimal Handling:** Convert `Decimal` objects to strings
6. **Enum Handling:** Convert `Enum` objects to their `.name` property
7. **Dataclass Handling:** Convert nested dataclasses via `asdict()`
8. **Rejection Criteria:** Reject `datetime`, `bytes`, `complex`, and custom objects without explicit serializers

**Idempotent Requirement:** `normalize_payload(normalize_payload(x)) == normalize_payload(x)`

---

## Section 3 — Boundary Client Contract

The boundary client (`tools/vllm_boundary_client.py`) is the sole permitted location for model imports.

### Required Functions

```python
def normalize_payload(payload: Any) -> Any:
    """Idempotent canonical normalization."""

def canonical_hash(payload: dict) -> str:
    """Cryptographic hash with strict normalization."""

def generate_proposal(prompt: str, config: dict) -> dict:
    """Generate proposal with full audit trail."""
    return {
        "text": str,
        "proposal_hash": str,
        "routing_version": str,
        "config_hash": str,
    }
```

### Required Constants

- `_DEFAULT_TIMEOUT_SECONDS = 30` (no magic numbers)

### Required Behaviors

- No retries (deterministic behavior)
- Explicit exception on timeout
- All model imports isolated to this file only

---

## Section 4 — Scenario Matrix

| Scenario | Context | Predicate | Route | Rationale |
|----------|---------|-----------|-------|-----------|
| Policy Read Required | `requires_policy_read=True` | Policy read check | Opus | Privacy/security boundary |
| High Iteration Count | `iteration_count > 3` | Resource guard | Opus | Cost control |
| Invalid AST | `invalid_ast=True` | Syntax validation | Opus | Safety fallback |
| Default | All other cases | Default routing | LOCAL_VLLM | Standard processing |

---

## Section 5 — Provider Enumeration

Routing uses strict enum-based providers:

```python
class Provider(Enum):
    OPUS = "opus"
    LOCAL_VLLM = "local_vllm"
```

No string literals are permitted for routing decisions.

---

## Section 6 — Testing Requirements

### Isolation Tests
- Static AST import scan for model libraries (ZERO MATCHES)
- Dynamic import detection
- Attribute-based import detection
- Transitive dependency graph verification
- Boundary client isolation verification

### Determinism Tests
- Canonical hash stability across multiple calls
- Cross-process determinism (3 interpreter instances)
- Idempotent normalization verification
- Predicate purity verification (no side effects)
- Context immutability verification

### Evidence Requirements
- Full audit trail with commit hash
- Environment specification (Python version, OS)
- File hashes for all predicate files
- Module dependency graph
- Determinism validation across process boundaries

---

## Compliance Declaration

This integration complies with all architectural invariants listed in Section 1. Any deviation constitutes a test failure and must be immediately addressed.

**Last Updated:** REV 5 Implementation
**Compliance Status:** Enforced
