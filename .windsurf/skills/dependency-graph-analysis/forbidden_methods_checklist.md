# Forbidden Methods Checklist

**Verify compliance with §0 and §2.3 — low-signal search is FORBIDDEN as primary analysis.**

## Forbidden as Primary Analysis

These MUST NOT be used to determine blast radius, architecture, ownership, call flow, dependency direction, dead code, test coverage, or file authority:

| Method | Why Forbidden |
|--------|---------------|
| `grep` / `rg` | Cannot distinguish imports from comments/strings; misses dynamic resolution |
| Regex repo sweeps | Cannot parse Python AST; misses nested/multi-line structures |
| Filename guesses | Proximity ≠ dependency; misses cross-directory and dynamic imports |
| Substring hunts | Finds comments/docstrings; cannot determine call direction |
| IDE reference counts | May miss dynamic resolution, registry, factory patterns |

## Permitted Secondary Usage

Text search MAY be used ONLY:
- **After** AST graph has identified a bounded candidate set
- **Only** as secondary confirmation for literal strings or exact constants
- **Example**: Graph shows file1.py imports utils.py → grep confirms exact import statement

## Graph Wins Disagreements

If graph and text search disagree → **graph wins** unless you prove the graph extractor is incomplete and record the limitation explicitly.

## Quick Decision

```
Need dependency/impact info?
  → Built AST graph? NO → STOP, build graph first
  → Built AST graph? YES → Use graph results
  → Need literal string confirmation? → Text search OK (secondary only)
```
