# Shared Module — Instructional Injection Patterns

> **Source:** `06_data/prompt_libraries/injections/Instructional_Injection_Enhanced_v5.md`
> **Module Focus:** Cross-cutting patterns for shared utilities and operations

---

## Applicable Patterns for Shared Module

The shared module provides utilities used across all layers.

### Context Layer (Patterns 6-8)

| # | Instruction Type | Shared Application |
|---|------------------|-------------------|
| **6** | Untrusted Block Wrapping | Utility for wrapping external content |
| **7** | Canonicalization | Text normalization utilities |
| **8** | Context Pruning | Token budget management |

### Output Layer (Patterns 26-30)

| # | Instruction Type | Shared Application |
|---|------------------|-------------------|
| **26** | Strict JSON-Only | JSON serialization utilities |
| **27** | Schema Enforcement | Schema validation utilities |
| **28** | Stability Contracts | Consistent serialization |
| **29** | Error Envelope | Standardized error classes |
| **30** | Minimality | Output size utilities |

---

## Shared Utilities Implementation

### Text Utilities (utils.py)

Implement patterns: 6, 7, 8

```python
# Pattern 6: Untrusted Block Wrapping
def wrap_untrusted(content: str) -> str:
    return f"<UNTRUSTED_DATA>{content}</UNTRUSTED_DATA>"

# Pattern 7: Canonicalization
def canonicalize(text: str) -> str:
    return text.strip().lower()

# Pattern 8: Context Pruning
def prune_to_budget(text: str, max_tokens: int) -> str:
    # Truncate to token budget
    pass
```

### Exception Hierarchy (exceptions.py)

Implement pattern: 29

```python
# Pattern 29: Error Envelope Normalization
class AgenticWorkflowError(Exception):
    def to_envelope(self) -> dict:
        return {
            "error": {
                "code": self.code,
                "message": str(self),
                "details": self.details
            }
        }
```

### Models (models.py)

Implement patterns: 26, 27, 28

```python
# Pattern 26, 27, 28: Schema compliance
@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    # Stable field ordering via dataclass
```

---

## Dependency Injection in Shared

From `Dependency & Prompt Injection Patterns.md`:

| Pattern | Shared Application |
|---------|-------------------|
| **Constructor Injection** | Inject config at utility creation |
| **Ambient Context** | Share CONFIG singleton |

---

## Cross-Reference

- Full patterns: `06_data/prompt_libraries/injections/Instructional_Injection_Enhanced_v5.md`
- DI patterns: `06_data/prompt_libraries/injections/Dependency & Prompt Injection Patterns.md`
- Master index: `INSTRUCTIONAL_INJECTION_PATTERNS_INDEX.md`
